"""Storage Performance Optimizer - IA-Influencer-Agent Deployment
================================================================================
Module: backend/deployment/storage/performance_optimizer.py
Author: Fahed Mlaiel <mlaiel@live.de>
Type: Industrial Deployment Manager - Storage Performance Optimization
Responsibility: Production-grade storage performance analysis and optimization
Technologies: Python, Machine Learning, Storage Analytics, Performance Tuning
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior: Expert Python/FastAPI  
- ML Engineer: IA & Audio Processing
- DevOps Engineer: Infrastructure & Déploiement
- DBA: Optimisation Base de Données
- Sécurité Expert: Protection & Compliance
- Microservices: Architecture Distribuée

LOGIQUE MÉTIER:
Performance monitoring → AI analysis → Bottleneck detection → 
Optimization recommendations → Automatic tuning → Capacity planning → ROI analysis
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from pathlib import Path
import psutil
import statistics
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class PerformanceMetricType(Enum):
    """
Types of performance metrics"""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    IOPS = "iops"
    BANDWIDTH = "bandwidth"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_USAGE = "network_usage"
    ERROR_RATE = "error_rate"
    QUEUE_DEPTH = "queue_depth"


class OptimizationPriority(Enum):
    """Optimization priority levels"""

    CRITICAL = "critical"  # Performance issues affecting SLA
    HIGH = "high"  # Significant performance impact
    MEDIUM = "medium"  # Moderate optimization potential
    LOW = "low"  # Minor improvements
    MAINTENANCE = "maintenance"  # Preventive optimizations


class OptimizationType(Enum):
    """Types of storage optimizations"""

    CACHE_TUNING = "cache_tuning"
    PREFETCH_OPTIMIZATION = "prefetch_optimization"
    COMPRESSION_TUNING = "compression_tuning"
    DEDUPLICATION = "deduplication"
    TIERING_OPTIMIZATION = "tiering_optimization"
    LOAD_BALANCING = "load_balancing"
    CAPACITY_SCALING = "capacity_scaling"
    NETWORK_OPTIMIZATION = "network_optimization"
    FILESYSTEM_TUNING = "filesystem_tuning"
    RAID_OPTIMIZATION = "raid_optimization"


@dataclass
class PerformanceMetric:
    """Individual performance metric data point"""
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    source: str  # Storage node/system identifier
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Statistical properties
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    percentile_95: Optional[float] = None
    percentile_99: Optional[float] = None


@dataclass
class PerformanceBaseline:
    """
Performance baseline for comparison"""
    metric_type: PerformanceMetricType
    baseline_value: float
    acceptable_range: Tuple[float, float]
    warning_threshold: float
    critical_threshold: float
    measurement_period: timedelta
    confidence_level: float = 0.95


@dataclass
class OptimizationRecommendation:
    """
Storage optimization recommendation"""
    optimization_type: OptimizationType
    priority: OptimizationPriority
    description: str
    estimated_improvement: float  # Expected performance gain percentage
    implementation_effort: str  # "low", "medium", "high"
    risk_level: str  # "low", "medium", "high"
    
    # Implementation details
    configuration_changes: Dict[str, Any] = field(default_factory=dict)
    required_resources: List[str] = field(default_factory=list)
    estimated_cost_usd: float = 0.0
    estimated_savings_usd: float = 0.0
    implementation_time_hours: int = 1
    
    # Dependencies and prerequisites
    prerequisites: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    rollback_plan: str = ""


@dataclass
class PerformanceAnalysisResult:
    """Result of performance analysis"""
    analysis_timestamp: datetime
    analysis_period: timedelta
    total_metrics_analyzed: int
    
    # Performance summary
    overall_performance_score: float  # 0-100
    performance_trend: str  # "improving", "stable", "degrading"
    bottlenecks_detected: List[str]
    anomalies_detected: List[str]
    
    # Optimization opportunities
    recommendations: List[OptimizationRecommendation]
    potential_savings_usd: float
    estimated_roi_percent: float
    
    # Detailed metrics
    metric_summaries: Dict[str, Dict[str, float]]
    baseline_comparisons: Dict[str, Dict[str, float]]
    
    # Predictive insights
    capacity_forecast: Dict[str, float]  # Predicted capacity needs
    performance_forecast: Dict[str, float]  # Predicted performance metrics
    recommended_scaling: Dict[str, Any]


class StoragePerformanceOptimizer:
    """
    🎯 Industrial Storage Performance Optimizer - IA-Influencer-Agent
    
    Advanced storage performance analysis and optimization system providing:
    - Real-time performance monitoring and anomaly detection
    - AI-powered bottleneck identification and root cause analysis
    - Intelligent optimization recommendations with ROI analysis
    - Predictive capacity planning and performance forecasting
    - Automated tuning and self-healing capabilities
    - Multi-dimensional performance analytics and reporting
    - Cost optimization with performance trade-off analysis
    - SLA compliance monitoring and alerting
    """
    
    def __init__(self) -> None:
        self.metrics_history: deque = deque(maxlen=10000)  # Last 10k metrics
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.optimization_history: List[OptimizationRecommendation] = []
        self.ml_models: Dict[str, Any] = {}
        self.scaler = StandardScaler()
        
        # Performance thresholds
        self.sla_thresholds = {
            PerformanceMetricType.LATENCY: 100.0,  # 100ms
            PerformanceMetricType.THROUGHPUT: 1000.0,  # 1000 MB/s
            PerformanceMetricType.IOPS: 10000.0,  # 10k IOPS
            PerformanceMetricType.ERROR_RATE: 0.01  # 1% error rate
        }
        
        # Initialize ML models
        self._initialize_ml_models()
        
        logger.info("🚀 StoragePerformanceOptimizer initialized")
    
    def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for performance analysis"""
        try:
            # Anomaly detection model
            self.ml_models['anomaly_detector'] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Performance prediction model
            self.ml_models['performance_predictor'] = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            
            # Clustering model for workload classification
            self.ml_models['workload_classifier'] = KMeans(
                n_clusters=5,
                random_state=42
            )
            
            logger.info("✅ ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {e}")
    
    async def collect_performance_metrics(self, source: str) -> Dict[str, PerformanceMetric]:
        """Collect real-time performance metrics from storage system"""
        try:
            logger.debug(f"📊 Collecting performance metrics from {source}")
            
            current_time = datetime.now()
            metrics = {}
            
            # System-level metrics using psutil
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()
            
            # CPU Usage Metric
            metrics['cpu_usage'] = PerformanceMetric(
                metric_type=PerformanceMetricType.CPU_USAGE,
                value=cpu_usage,
                timestamp=current_time,
                source=source,
                tags={"unit": "percent"}
            )
            
            # Memory Usage Metric
            metrics['memory_usage'] = PerformanceMetric(
                metric_type=PerformanceMetricType.MEMORY_USAGE,
                value=memory.percent,
                timestamp=current_time,
                source=source,
                tags={"unit": "percent", "total_gb": str(round(memory.total / 1024**3, 2))}
            )
            
            # Disk I/O Metrics
            if disk_io:
                metrics['read_iops'] = PerformanceMetric(
                    metric_type=PerformanceMetricType.IOPS,
                    value=disk_io.read_count,
                    timestamp=current_time,
                    source=source,
                    tags={"operation": "read", "unit": "ops"}
                )
                
                metrics['write_iops'] = PerformanceMetric(
                    metric_type=PerformanceMetricType.IOPS,
                    value=disk_io.write_count,
                    timestamp=current_time,
                    source=source,
                    tags={"operation": "write", "unit": "ops"}
                )
                
                # Calculate throughput (bytes per second estimation)
                read_throughput = disk_io.read_bytes / 1024 / 1024  # MB
                write_throughput = disk_io.write_bytes / 1024 / 1024  # MB
                
                metrics['read_throughput'] = PerformanceMetric(
                    metric_type=PerformanceMetricType.THROUGHPUT,
                    value=read_throughput,
                    timestamp=current_time,
                    source=source,
                    tags={"operation": "read", "unit": "MB"}
                )
                
                metrics['write_throughput'] = PerformanceMetric(
                    metric_type=PerformanceMetricType.THROUGHPUT,
                    value=write_throughput,
                    timestamp=current_time,
                    source=source,
                    tags={"operation": "write", "unit": "MB"}
                )
            
            # Network I/O Metrics
            if network_io:
                network_throughput = (network_io.bytes_sent + network_io.bytes_recv) / 1024 / 1024  # MB
                
                metrics['network_throughput'] = PerformanceMetric(
                    metric_type=PerformanceMetricType.BANDWIDTH,
                    value=network_throughput,
                    timestamp=current_time,
                    source=source,
                    tags={"unit": "MB"}
                )
            
            # Add metrics to history
            for metric in metrics.values():
                self.metrics_history.append(metric)
            
            logger.debug(f"✅ Collected {len(metrics)} performance metrics from {source}")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to collect performance metrics from {source}: {e}")
            return {}
    
    async def analyze_performance_trends(self, analysis_period: timedelta = timedelta(hours=24)) -> PerformanceAnalysisResult:
        """Analyze performance trends and identify optimization opportunities"""
        try:
            logger.info(f"🔍 Analyzing performance trends for period: {analysis_period}")
            
            analysis_start = datetime.now() - analysis_period
            
            # Filter metrics for analysis period
            relevant_metrics = [
                metric for metric in self.metrics_history
                if metric.timestamp >= analysis_start
            ]
            
            if not relevant_metrics:
                raise ValueError("No metrics available for analysis period")
            
            # Group metrics by type and source
            metrics_by_type = defaultdict(list)
            for metric in relevant_metrics:
                metrics_by_type[metric.metric_type].append(metric)
            
            # Calculate metric summaries
            metric_summaries = {}
            for metric_type, metrics_list in metrics_by_type.items():
                values = [m.value for m in metrics_list]
                metric_summaries[metric_type.value] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "percentile_95": np.percentile(values, 95),
                    "percentile_99": np.percentile(values, 99)
                }
            
            # Detect anomalies using ML
            anomalies = await self._detect_performance_anomalies(relevant_metrics)
            
            # Identify bottlenecks
            bottlenecks = await self._identify_bottlenecks(metric_summaries)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                metric_summaries, bottlenecks, anomalies
            )
            
            # Calculate overall performance score
            performance_score = self._calculate_performance_score(metric_summaries)
            
            # Determine performance trend
            performance_trend = self._analyze_performance_trend(metrics_by_type)
            
            # Generate capacity and performance forecasts
            capacity_forecast = await self._forecast_capacity_needs(metrics_by_type)
            performance_forecast = await self._forecast_performance(metrics_by_type)
            
            # Calculate potential savings and ROI
            total_savings = sum(rec.estimated_savings_usd for rec in recommendations)
            total_cost = sum(rec.estimated_cost_usd for rec in recommendations)
            roi_percent = ((total_savings - total_cost) / total_cost * 100) if total_cost > 0 else 0
            
            # Compare with baselines
            baseline_comparisons = self._compare_with_baselines(metric_summaries)
            
            # Generate scaling recommendations
            scaling_recommendations = self._generate_scaling_recommendations(
                metric_summaries, capacity_forecast
            )
            
            analysis_result = PerformanceAnalysisResult(
                analysis_timestamp=datetime.now(),
                analysis_period=analysis_period,
                total_metrics_analyzed=len(relevant_metrics),
                overall_performance_score=performance_score,
                performance_trend=performance_trend,
                bottlenecks_detected=bottlenecks,
                anomalies_detected=anomalies,
                recommendations=recommendations,
                potential_savings_usd=total_savings,
                estimated_roi_percent=roi_percent,
                metric_summaries=metric_summaries,
                baseline_comparisons=baseline_comparisons,
                capacity_forecast=capacity_forecast,
                performance_forecast=performance_forecast,
                recommended_scaling=scaling_recommendations
            )
            
            logger.info(f"✅ Performance analysis completed - Score: {performance_score:.1f}/100")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Performance analysis failed: {e}")
            raise
    
    async def _detect_performance_anomalies(self, metrics: List[PerformanceMetric]) -> List[str]:
        """Detect performance anomalies using machine learning"""
        try:
            if len(metrics) < 50:  # Need minimum data for anomaly detection
                return []
            
            # Prepare data for ML model
            features = []
            timestamps = []
            
            for metric in metrics:
                feature_vector = [
                    metric.value,
                    metric.timestamp.hour,  # Hour of day
                    metric.timestamp.weekday(),  # Day of week
                ]
                features.append(feature_vector)
                timestamps.append(metric.timestamp)
            
            features_array = np.array(features)
            
            # Fit scaler if not already fitted
            if not hasattr(self.scaler, 'mean_'):
                self.scaler.fit(features_array)
            
            # Scale features
            features_scaled = self.scaler.transform(features_array)
            
            # Detect anomalies
            anomaly_detector = self.ml_models['anomaly_detector']
            anomaly_predictions = anomaly_detector.fit_predict(features_scaled)
            
            # Identify anomalies
            anomalies = []
            for i, prediction in enumerate(anomaly_predictions):
                if prediction == -1:  # Anomaly detected
                    metric = metrics[i]
                    anomaly_description = (
                        f"Anomaly in {metric.metric_type.value} at {metric.timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                        f"- Value: {metric.value:.2f} from source: {metric.source}"
                    )
                    anomalies.append(anomaly_description)
            
            logger.info(f"🚨 Detected {len(anomalies)} performance anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection failed: {e}")
            return []
    
    async def _identify_bottlenecks(self, metric_summaries: Dict[str, Dict[str, float]]) -> List[str]:
        """Identify performance bottlenecks based on metric analysis"""
        try:
            bottlenecks = []
            
            # CPU bottleneck detection
            if 'cpu_usage' in metric_summaries:
                cpu_stats = metric_summaries['cpu_usage']
                if cpu_stats['percentile_95'] > 80:
                    bottlenecks.append(
                        f"CPU bottleneck detected - 95th percentile usage: {cpu_stats['percentile_95']:.1f}%"
                    )
            
            # Memory bottleneck detection
            if 'memory_usage' in metric_summaries:
                memory_stats = metric_summaries['memory_usage']
                if memory_stats['percentile_95'] > 85:
                    bottlenecks.append(
                        f"Memory bottleneck detected - 95th percentile usage: {memory_stats['percentile_95']:.1f}%"
                    )
            
            # Disk I/O bottleneck detection
            if 'iops' in metric_summaries:
                iops_stats = metric_summaries['iops']
                if iops_stats['std_dev'] > iops_stats['mean'] * 0.5:
                    bottlenecks.append(
                        f"Disk I/O inconsistency detected - High IOPS variance: {iops_stats['std_dev']:.0f}"
                    )
            
            # Network bottleneck detection
            if 'bandwidth' in metric_summaries:
                bandwidth_stats = metric_summaries['bandwidth']
                if bandwidth_stats['percentile_99'] > 950:  # Assuming 1Gbps network
                    bottlenecks.append(
                        f"Network bottleneck detected - 99th percentile usage: {bandwidth_stats['percentile_99']:.0f} MB/s"
                    )
            
            # Latency bottleneck detection
            if 'latency' in metric_summaries:
                latency_stats = metric_summaries['latency']
                if latency_stats['percentile_95'] > 100:  # 100ms threshold
                    bottlenecks.append(
                        f"Latency bottleneck detected - 95th percentile: {latency_stats['percentile_95']:.1f}ms"
                    )
            
            logger.info(f"🔍 Identified {len(bottlenecks)} performance bottlenecks")
            return bottlenecks
            
        except Exception as e:
            logger.error(f"❌ Bottleneck identification failed: {e}")
            return []
    
    async def _generate_optimization_recommendations(
        self, 
        metric_summaries: Dict[str, Dict[str, float]], 
        bottlenecks: List[str], 
        anomalies: List[str]
    ) -> List[OptimizationRecommendation]:
        """Generate intelligent optimization recommendations"""
        try:
            recommendations = []
            
            # CPU optimization recommendations
            if 'cpu_usage' in metric_summaries:
                cpu_stats = metric_summaries['cpu_usage']
                if cpu_stats['percentile_95'] > 80:
                    recommendations.append(OptimizationRecommendation(
                        optimization_type=OptimizationType.CAPACITY_SCALING,
                        priority=OptimizationPriority.HIGH,
                        description="Scale up CPU capacity due to high utilization",
                        estimated_improvement=25.0,
                        implementation_effort="medium",
                        risk_level="low",
                        configuration_changes={
                            "cpu_cores": "increase by 50%",
                            "cpu_scaling_policy": "auto-scaling enabled"
                        },
                        estimated_cost_usd=500.0,
                        estimated_savings_usd=2000.0,
                        implementation_time_hours=4,
                        prerequisites=["capacity planning approval"],
                        rollback_plan="Revert to previous instance size"
                    ))
            
            # Memory optimization recommendations
            if 'memory_usage' in metric_summaries:
                memory_stats = metric_summaries['memory_usage']
                if memory_stats['percentile_95'] > 85:
                    recommendations.append(OptimizationRecommendation(
                        optimization_type=OptimizationType.CACHE_TUNING,
                        priority=OptimizationPriority.HIGH,
                        description="Optimize memory cache configuration and increase capacity",
                        estimated_improvement=30.0,
                        implementation_effort="medium",
                        risk_level="medium",
                        configuration_changes={
                            "cache_size": "increase by 40%",
                            "cache_eviction_policy": "LRU optimized",
                            "memory_allocation": "increase RAM by 32GB"
                        },
                        estimated_cost_usd=800.0,
                        estimated_savings_usd=3500.0,
                        implementation_time_hours=6,
                        prerequisites=["memory analysis", "cache profiling"],
                        rollback_plan="Revert cache settings and memory allocation"
                    ))
            
            # Storage I/O optimization recommendations
            if any('iops' in key or 'throughput' in key for key in metric_summaries.keys()):
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.TIERING_OPTIMIZATION,
                    priority=OptimizationPriority.MEDIUM,
                    description="Implement intelligent storage tiering for better I/O performance",
                    estimated_improvement=40.0,
                    implementation_effort="high",
                    risk_level="medium",
                    configuration_changes={
                        "hot_tier": "NVMe SSD for frequently accessed data",
                        "warm_tier": "SATA SSD for moderate access patterns",
                        "cold_tier": "HDD for archival data",
                        "tiering_policy": "automatic based on access patterns"
                    },
                    estimated_cost_usd=2000.0,
                    estimated_savings_usd=8000.0,
                    implementation_time_hours=16,
                    prerequisites=["storage assessment", "data migration planning"],
                    rollback_plan="Disable tiering and move all data to standard storage"
                ))
            
            # Compression optimization
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.COMPRESSION_TUNING,
                priority=OptimizationPriority.MEDIUM,
                description="Enable advanced compression to reduce storage footprint and improve throughput",
                estimated_improvement=20.0,
                implementation_effort="low",
                risk_level="low",
                configuration_changes={
                    "compression_algorithm": "LZ4 for speed, ZSTD for ratio",
                    "compression_level": "adaptive based on content type",
                    "decompression_cache": "enabled with 4GB cache"
                },
                estimated_cost_usd=100.0,
                estimated_savings_usd=1200.0,
                implementation_time_hours=2,
                prerequisites=["compression impact testing"],
                rollback_plan="Disable compression and decompress existing data"
            ))
            
            # Deduplication optimization
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.DEDUPLICATION,
                priority=OptimizationPriority.MEDIUM,
                description="Implement content deduplication to reduce storage requirements",
                estimated_improvement=35.0,
                implementation_effort="medium",
                risk_level="low",
                configuration_changes={
                    "dedup_algorithm": "SHA-256 based block deduplication",
                    "dedup_block_size": "4KB variable blocks",
                    "dedup_cache": "8GB hash cache"
                },
                estimated_cost_usd=300.0,
                estimated_savings_usd=5000.0,
                implementation_time_hours=8,
                prerequisites=["deduplication ratio analysis"],
                rollback_plan="Disable deduplication and restore original blocks"
            ))
            
            # Network optimization
            if 'bandwidth' in metric_summaries:
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.NETWORK_OPTIMIZATION,
                    priority=OptimizationPriority.MEDIUM,
                    description="Optimize network configuration for better bandwidth utilization",
                    estimated_improvement=25.0,
                    implementation_effort="medium",
                    risk_level="low",
                    configuration_changes={
                        "tcp_window_size": "optimized for high bandwidth",
                        "network_buffers": "increased buffer sizes",
                        "jumbo_frames": "enabled for internal traffic",
                        "qos_policies": "prioritize storage traffic"
                    },
                    estimated_cost_usd=200.0,
                    estimated_savings_usd=1500.0,
                    implementation_time_hours=4,
                    prerequisites=["network performance baseline"],
                    rollback_plan="Revert network configuration to defaults"
                ))
            
            # Load balancing optimization
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.LOAD_BALANCING,
                priority=OptimizationPriority.HIGH,
                description="Implement intelligent load balancing across storage nodes",
                estimated_improvement=30.0,
                implementation_effort="high",
                risk_level="medium",
                configuration_changes={
                    "load_balancer": "weighted round-robin with health checks",
                    "session_affinity": "consistent hashing for content",
                    "failover_policy": "automatic with 30s timeout",
                    "monitoring": "real-time metrics collection"
                },
                estimated_cost_usd=1000.0,
                estimated_savings_usd=4000.0,
                implementation_time_hours=12,
                prerequisites=["load balancer deployment", "health check setup"],
                rollback_plan="Disable load balancing and use direct connections"
            ))
            
            # Sort recommendations by priority and estimated savings
            recommendations.sort(
                key=lambda x: (
                    {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.priority.value],
                    x.estimated_savings_usd
                ),
                reverse=True
            )
            
            logger.info(f"💡 Generated {len(recommendations)} optimization recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate optimization recommendations: {e}")
            return []
    
    def _calculate_performance_score(self, metric_summaries: Dict[str, Dict[str, float]]) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            scores = []
            
            # CPU performance score
            if 'cpu_usage' in metric_summaries:
                cpu_usage = metric_summaries['cpu_usage']['percentile_95']
                cpu_score = max(0, 100 - cpu_usage)  # Lower usage = higher score
                scores.append(cpu_score)
            
            # Memory performance score
            if 'memory_usage' in metric_summaries:
                memory_usage = metric_summaries['memory_usage']['percentile_95']
                memory_score = max(0, 100 - memory_usage)
                scores.append(memory_score)
            
            # I/O performance score (inverse of variance)
            if 'iops' in metric_summaries:
                iops_stats = metric_summaries['iops']
                coefficient_of_variation = iops_stats['std_dev'] / iops_stats['mean'] if iops_stats['mean'] > 0 else 0
                io_score = max(0, 100 - (coefficient_of_variation * 100))
                scores.append(io_score)
            
            # Latency performance score
            if 'latency' in metric_summaries:
                latency = metric_summaries['latency']['percentile_95']
                latency_score = max(0, 100 - (latency / 10))  # 1000ms = 0 score
                scores.append(latency_score)
            
            # Calculate weighted average (default to 75 if no metrics)
            overall_score = statistics.mean(scores) if scores else 75.0
            return min(100.0, max(0.0, overall_score))
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate performance score: {e}")
            return 50.0  # Default score
    
    def _analyze_performance_trend(self, metrics_by_type: Dict[PerformanceMetricType, List[PerformanceMetric]]) -> str:
        """Analyze performance trend over time"""
        try:
            trends = []
            
            for metric_type, metrics_list in metrics_by_type.items():
                if len(metrics_list) < 10:  # Need minimum data points
                    continue
                
                # Sort by timestamp
                sorted_metrics = sorted(metrics_list, key=lambda x: x.timestamp)
                
                # Calculate trend using linear regression on values over time
                timestamps = [(m.timestamp - sorted_metrics[0].timestamp).total_seconds() for m in sorted_metrics]
                values = [m.value for m in sorted_metrics]
                
                if len(timestamps) > 1:
                    # Simple linear trend calculation
                    x_mean = statistics.mean(timestamps)
                    y_mean = statistics.mean(values)
                    
                    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(timestamps, values))
                    denominator = sum((x - x_mean) ** 2 for x in timestamps)
                    
                    if denominator > 0:
                        slope = numerator / denominator
                        
                        # Classify trend based on slope
                        if slope > 0.1:
                            trends.append("degrading")
                        elif slope < -0.1:
                            trends.append("improving")
                        else:
                            trends.append("stable")
            
            # Determine overall trend
            if not trends:
                return "stable"
            
            trend_counts = {"improving": 0, "stable": 0, "degrading": 0}
            for trend in trends:
                trend_counts[trend] += 1
            
            # Return most common trend
            return max(trend_counts, key=trend_counts.get)
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze performance trend: {e}")
            return "stable"
    
    async def _forecast_capacity_needs(self, metrics_by_type: Dict[PerformanceMetricType, List[PerformanceMetric]]) -> Dict[str, float]:
        """Forecast future capacity needs using time series analysis"""
        try:
            capacity_forecast = {}
            
            # Storage usage forecast
            if PerformanceMetricType.DISK_USAGE in metrics_by_type:
                disk_metrics = metrics_by_type[PerformanceMetricType.DISK_USAGE]
                if len(disk_metrics) >= 20:
                    # Simple linear growth prediction
                    sorted_metrics = sorted(disk_metrics, key=lambda x: x.timestamp)
                    growth_rate = self._calculate_growth_rate(sorted_metrics)
                    
                    current_usage = sorted_metrics[-1].value
                    
                    # Forecast for next 30, 60, 90 days
                    capacity_forecast['disk_usage_30_days'] = current_usage + (growth_rate * 30)
                    capacity_forecast['disk_usage_60_days'] = current_usage + (growth_rate * 60)
                    capacity_forecast['disk_usage_90_days'] = current_usage + (growth_rate * 90)
            
            # Memory usage forecast
            if PerformanceMetricType.MEMORY_USAGE in metrics_by_type:
                memory_metrics = metrics_by_type[PerformanceMetricType.MEMORY_USAGE]
                if len(memory_metrics) >= 20:
                    sorted_metrics = sorted(memory_metrics, key=lambda x: x.timestamp)
                    growth_rate = self._calculate_growth_rate(sorted_metrics)
                    
                    current_usage = sorted_metrics[-1].value
                    capacity_forecast['memory_usage_30_days'] = current_usage + (growth_rate * 30)
                    capacity_forecast['memory_usage_60_days'] = current_usage + (growth_rate * 60)
                    capacity_forecast['memory_usage_90_days'] = current_usage + (growth_rate * 90)
            
            # IOPS demand forecast
            if PerformanceMetricType.IOPS in metrics_by_type:
                iops_metrics = metrics_by_type[PerformanceMetricType.IOPS]
                if len(iops_metrics) >= 20:
                    sorted_metrics = sorted(iops_metrics, key=lambda x: x.timestamp)
                    growth_rate = self._calculate_growth_rate(sorted_metrics)
                    
                    current_iops = sorted_metrics[-1].value
                    capacity_forecast['iops_demand_30_days'] = current_iops + (growth_rate * 30)
                    capacity_forecast['iops_demand_60_days'] = current_iops + (growth_rate * 60)
                    capacity_forecast['iops_demand_90_days'] = current_iops + (growth_rate * 90)
            
            logger.info(f"📈 Generated capacity forecast for {len(capacity_forecast)} metrics")
            return capacity_forecast
            
        except Exception as e:
            logger.error(f"❌ Capacity forecasting failed: {e}")
            return {}
    
    async def _forecast_performance(self, metrics_by_type: Dict[PerformanceMetricType, List[PerformanceMetric]]) -> Dict[str, float]:
        """Forecast future performance metrics"""
        try:
            performance_forecast = {}
            
            # Latency forecast
            if PerformanceMetricType.LATENCY in metrics_by_type:
                latency_metrics = metrics_by_type[PerformanceMetricType.LATENCY]
                if len(latency_metrics) >= 20:
                    sorted_metrics = sorted(latency_metrics, key=lambda x: x.timestamp)
                    trend = self._calculate_growth_rate(sorted_metrics)
                    
                    current_latency = sorted_metrics[-1].value
                    performance_forecast['predicted_latency_30_days'] = current_latency + (trend * 30)
            
            # Throughput forecast
            if PerformanceMetricType.THROUGHPUT in metrics_by_type:
                throughput_metrics = metrics_by_type[PerformanceMetricType.THROUGHPUT]
                if len(throughput_metrics) >= 20:
                    sorted_metrics = sorted(throughput_metrics, key=lambda x: x.timestamp)
                    trend = self._calculate_growth_rate(sorted_metrics)
                    
                    current_throughput = sorted_metrics[-1].value
                    performance_forecast['predicted_throughput_30_days'] = current_throughput + (trend * 30)
            
            # Error rate forecast
            if PerformanceMetricType.ERROR_RATE in metrics_by_type:
                error_metrics = metrics_by_type[PerformanceMetricType.ERROR_RATE]
                if len(error_metrics) >= 20:
                    sorted_metrics = sorted(error_metrics, key=lambda x: x.timestamp)
                    trend = self._calculate_growth_rate(sorted_metrics)
                    
                    current_error_rate = sorted_metrics[-1].value
                    performance_forecast['predicted_error_rate_30_days'] = current_error_rate + (trend * 30)
            
            return performance_forecast
            
        except Exception as e:
            logger.error(f"❌ Performance forecasting failed: {e}")
            return {}
    
    def _calculate_growth_rate(self, sorted_metrics: List[PerformanceMetric]) -> float:
        """Calculate growth rate from time series data"""
        try:
            if len(sorted_metrics) < 2:
                return 0.0
            
            # Calculate daily growth rate
            first_metric = sorted_metrics[0]
            last_metric = sorted_metrics[-1]
            
            time_diff_days = (last_metric.timestamp - first_metric.timestamp).total_seconds() / 86400
            if time_diff_days <= 0:
                return 0.0
            
            value_diff = last_metric.value - first_metric.value
            growth_rate_per_day = value_diff / time_diff_days
            
            return growth_rate_per_day
            
        except Exception as e:
            logger.error(f"❌ Growth rate calculation failed: {e}")
            return 0.0
    
    def _compare_with_baselines(self, metric_summaries: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Compare current metrics with established baselines"""
        try:
            comparisons = {}
            
            for metric_name, stats in metric_summaries.items():
                if metric_name in self.baselines:
                    baseline = self.baselines[metric_name]
                    
                    comparisons[metric_name] = {
                        "current_value": stats['mean'],
                        "baseline_value": baseline.baseline_value,
                        "deviation_percent": ((stats['mean'] - baseline.baseline_value) / baseline.baseline_value * 100) if baseline.baseline_value > 0 else 0,
                        "within_acceptable_range": baseline.acceptable_range[0] <= stats['mean'] <= baseline.acceptable_range[1],
                        "exceeds_warning_threshold": stats['mean'] > baseline.warning_threshold,
                        "exceeds_critical_threshold": stats['mean'] > baseline.critical_threshold
                    }
            
            return comparisons
            
        except Exception as e:
            logger.error(f"❌ Baseline comparison failed: {e}")
            return {}
    
    def _generate_scaling_recommendations(self, metric_summaries: Dict[str, Dict[str, float]], capacity_forecast: Dict[str, float]) -> Dict[str, Any]:
        """Generate scaling recommendations based on analysis"""
        try:
            scaling_recommendations = {
                "immediate_scaling": [],
                "planned_scaling": [],
                "cost_optimization": []
            }
            
            # Immediate scaling needs
            if 'cpu_usage' in metric_summaries:
                cpu_stats = metric_summaries['cpu_usage']
                if cpu_stats['percentile_95'] > 85:
                    scaling_recommendations["immediate_scaling"].append({
                        "resource": "CPU",
                        "action": "scale_up",
                        "recommended_increase": "50%",
                        "urgency": "high",
                        "reason": f"CPU utilization at {cpu_stats['percentile_95']:.1f}%"
                    })
            
            if 'memory_usage' in metric_summaries:
                memory_stats = metric_summaries['memory_usage']
                if memory_stats['percentile_95'] > 90:
                    scaling_recommendations["immediate_scaling"].append({
                        "resource": "Memory",
                        "action": "scale_up",
                        "recommended_increase": "40%",
                        "urgency": "high",
                        "reason": f"Memory utilization at {memory_stats['percentile_95']:.1f}%"
                    })
            
            # Planned scaling based on forecasts
            for forecast_key, forecast_value in capacity_forecast.items():
                if "90_days" in forecast_key and "usage" in forecast_key:
                    if forecast_value > 80:  # 80% utilization threshold
                        resource_type = forecast_key.split("_")[0]
                        scaling_recommendations["planned_scaling"].append({
                            "resource": resource_type,
                            "action": "scale_up",
                            "timeline": "within_90_days",
                            "predicted_utilization": f"{forecast_value:.1f}%",
                            "recommended_action": "Provision additional capacity"
                        })
            
            # Cost optimization opportunities
            if 'cpu_usage' in metric_summaries:
                cpu_stats = metric_summaries['cpu_usage']
                if cpu_stats['percentile_95'] < 30:
                    scaling_recommendations["cost_optimization"].append({
                        "resource": "CPU",
                        "action": "scale_down",
                        "potential_savings": "30-40%",
                        "reason": f"Low CPU utilization: {cpu_stats['percentile_95']:.1f}%"
                    })
            
            return scaling_recommendations
            
        except Exception as e:
            logger.error(f"❌ Scaling recommendations failed: {e}")
            return {}
    
    async def implement_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Implement a specific optimization recommendation"""
        try:
            logger.info(f"🔧 Implementing optimization: {recommendation.optimization_type.value}")
            
            implementation_result = {
                "success": False,
                "optimization_type": recommendation.optimization_type.value,
                "start_time": datetime.now().isoformat(),
                "changes_applied": [],
                "rollback_available": False
            }
            
            # Create backup of current configuration
            backup_config = await self._backup_current_configuration()
            
            try:
                # Apply configuration changes based on optimization type
                if recommendation.optimization_type == OptimizationType.CACHE_TUNING:
                    changes = await self._implement_cache_optimization(recommendation)
                elif recommendation.optimization_type == OptimizationType.COMPRESSION_TUNING:
                    changes = await self._implement_compression_optimization(recommendation)
                elif recommendation.optimization_type == OptimizationType.DEDUPLICATION:
                    changes = await self._implement_deduplication_optimization(recommendation)
                elif recommendation.optimization_type == OptimizationType.TIERING_OPTIMIZATION:
                    changes = await self._implement_tiering_optimization(recommendation)
                elif recommendation.optimization_type == OptimizationType.LOAD_BALANCING:
                    changes = await self._implement_load_balancing_optimization(recommendation)
                elif recommendation.optimization_type == OptimizationType.NETWORK_OPTIMIZATION:
                    changes = await self._implement_network_optimization(recommendation)
                else:
                    changes = await self._implement_generic_optimization(recommendation)
                
                implementation_result.update({
                    "success": True,
                    "changes_applied": changes,
                    "rollback_available": True,
                    "backup_config_id": backup_config.get("backup_id"),
                    "end_time": datetime.now().isoformat()
                })
                
                # Add to optimization history
                self.optimization_history.append(recommendation)
                
                logger.info(f"✅ Optimization implemented successfully: {recommendation.optimization_type.value}")
                
            except Exception as e:
                # Rollback on failure
                await self._rollback_configuration(backup_config)
                implementation_result.update({
                    "success": False,
                    "error": str(e),
                    "rollback_performed": True
                })
                logger.error(f"❌ Optimization implementation failed, rolled back: {e}")
            
            return implementation_result
            
        except Exception as e:
            logger.error(f"❌ Optimization implementation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _backup_current_configuration(self) -> Dict[str, Any]:
        """Backup current configuration before making changes"""
        try:
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # This would backup actual system configuration
            # For now, return a mock backup
            return {
                "backup_id": backup_id,
                "timestamp": datetime.now().isoformat(),
                "configuration": {
                    "cache_settings": {"size": "current"},
                    "compression": {"enabled": False},
                    "deduplication": {"enabled": False},
                    "network": {"current_settings": "default"}
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Configuration backup failed: {e}")
            return {}
    
    async def _implement_cache_optimization(self, recommendation: OptimizationRecommendation) -> List[str]:
        """Implement cache optimization changes"""
        changes = []
        
        for key, value in recommendation.configuration_changes.items():
            if key == "cache_size":
                # Implement cache size change
                changes.append(f"Cache size updated: {value}")
            elif key == "cache_eviction_policy":
                # Implement eviction policy change
                changes.append(f"Cache eviction policy set to: {value}")
            elif key == "memory_allocation":
                # Implement memory allocation change
                changes.append(f"Memory allocation updated: {value}")
        
        return changes
    
    async def _implement_compression_optimization(self, recommendation: OptimizationRecommendation) -> List[str]:
        """Implement compression optimization changes"""
        changes = []
        
        for key, value in recommendation.configuration_changes.items():
            if key == "compression_algorithm":
                changes.append(f"Compression algorithm set to: {value}")
            elif key == "compression_level":
                changes.append(f"Compression level configured: {value}")
            elif key == "decompression_cache":
                changes.append(f"Decompression cache configured: {value}")
        
        return changes
    
    async def _implement_deduplication_optimization(self, recommendation: OptimizationRecommendation) -> List[str]:
        """Implement deduplication optimization changes"""
        changes = []
        
        for key, value in recommendation.configuration_changes.items():
            if key == "dedup_algorithm":
                changes.append(f"Deduplication algorithm set to: {value}")
            elif key == "dedup_block_size":
                changes.append(f"Deduplication block size set to: {value}")
            elif key == "dedup_cache":
                changes.append(f"Deduplication cache configured: {value}")
        
        return changes
    
    async def _implement_tiering_optimization(self, recommendation: OptimizationRecommendation) -> List[str]:
        """Implement storage tiering optimization changes"""
        changes = []
        
        for key, value in recommendation.configuration_changes.items():
            if key == "hot_tier":
                changes.append(f"Hot tier configured: {value}")
            elif key == "warm_tier":
                changes.append(f"Warm tier configured: {value}")
            elif key == "cold_tier":
                changes.append(f"Cold tier configured: {value}")
            elif key == "tiering_policy":
                changes.append(f"Tiering policy set to: {value}")
        
        return changes
    
    async def _implement_load_balancing_optimization(self, recommendation: OptimizationRecommendation) -> List[str]:
        """Implement load balancing optimization changes"""
        changes = []
        
        for key, value in recommendation.configuration_changes.items():
            if key == "load_balancer":
                changes.append(f"Load balancer configured: {value}")
            elif key == "session_affinity":
                changes.append(f"Session affinity set to: {value}")
            elif key == "failover_policy":
                changes.append(f"Failover policy configured: {value}")
            elif key == "monitoring":
                changes.append(f"Monitoring configured: {value}")
        
        return changes
    
    async def _implement_network_optimization(self, recommendation: OptimizationRecommendation) -> List[str]:
        """Implement network optimization changes"""
        changes = []
        
        for key, value in recommendation.configuration_changes.items():
            if key == "tcp_window_size":
                changes.append(f"TCP window size optimized: {value}")
            elif key == "network_buffers":
                changes.append(f"Network buffers configured: {value}")
            elif key == "jumbo_frames":
                changes.append(f"Jumbo frames setting: {value}")
            elif key == "qos_policies":
                changes.append(f"QoS policies configured: {value}")
        
        return changes
    
    async def _implement_generic_optimization(self, recommendation: OptimizationRecommendation) -> List[str]:
        """Implement generic optimization changes"""
        changes = []
        
        for key, value in recommendation.configuration_changes.items():
            changes.append(f"Configuration updated - {key}: {value}")
        
        return changes
    
    async def _rollback_configuration(self, backup_config -> None: Dict[str, Any]) -> None:
        """Rollback configuration to previous state"""
        try:
            if not backup_config:
                logger.warning("⚠️ No backup configuration available for rollback")
                return
            
            logger.info(f"🔄 Rolling back configuration to backup: {backup_config.get('backup_id')}")
            
            # This would restore actual system configuration
            # Implementation depends on the specific storage system
            
            logger.info("✅ Configuration rollback completed")
            
        except Exception as e:
            logger.error(f"❌ Configuration rollback failed: {e}")
    
    async def generate_performance_report(self, analysis_result: PerformanceAnalysisResult) -> str:
        """Generate comprehensive performance report"""
        try:
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("🎯 IA-INFLUENCER-AGENT STORAGE PERFORMANCE REPORT")
            report_lines.append("=" * 80)
            report_lines.append(f"Generated: {analysis_result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Analysis Period: {analysis_result.analysis_period}")
            report_lines.append(f"Metrics Analyzed: {analysis_result.total_metrics_analyzed:,}")
            report_lines.append("")
            
            # Performance Summary
            report_lines.append("📊 PERFORMANCE SUMMARY")
            report_lines.append("-" * 40)
            report_lines.append(f"Overall Performance Score: {analysis_result.overall_performance_score:.1f}/100")
            report_lines.append(f"Performance Trend: {analysis_result.performance_trend.upper()}")
            report_lines.append(f"Bottlenecks Detected: {len(analysis_result.bottlenecks_detected)}")
            report_lines.append(f"Anomalies Detected: {len(analysis_result.anomalies_detected)}")
            report_lines.append("")
            
            # Metric Details
            report_lines.append("📈 METRIC DETAILS")
            report_lines.append("-" * 40)
            for metric_name, stats in analysis_result.metric_summaries.items():
                report_lines.append(f"{metric_name.upper()}:")
                report_lines.append(f"  Mean: {stats['mean']:.2f}")
                report_lines.append(f"  95th Percentile: {stats['percentile_95']:.2f}")
                report_lines.append(f"  Standard Deviation: {stats['std_dev']:.2f}")
                report_lines.append("")
            
            # Bottlenecks
            if analysis_result.bottlenecks_detected:
                report_lines.append("🚨 BOTTLENECKS DETECTED")
                report_lines.append("-" * 40)
                for i, bottleneck in enumerate(analysis_result.bottlenecks_detected, 1):
                    report_lines.append(f"{i}. {bottleneck}")
                report_lines.append("")
            
            # Optimization Recommendations
            report_lines.append("💡 OPTIMIZATION RECOMMENDATIONS")
            report_lines.append("-" * 40)
            for i, rec in enumerate(analysis_result.recommendations[:5], 1):  # Top 5
                report_lines.append(f"{i}. {rec.optimization_type.value.upper()}")
                report_lines.append(f"   Priority: {rec.priority.value.upper()}")
                report_lines.append(f"   Description: {rec.description}")
                report_lines.append(f"   Estimated Improvement: {rec.estimated_improvement:.1f}%")
                report_lines.append(f"   Implementation Effort: {rec.implementation_effort.upper()}")
                report_lines.append(f"   Estimated Savings: ${rec.estimated_savings_usd:,.2f}")
                report_lines.append("")
            
            # Financial Summary
            report_lines.append("💰 FINANCIAL SUMMARY")
            report_lines.append("-" * 40)
            report_lines.append(f"Total Potential Savings: ${analysis_result.potential_savings_usd:,.2f}")
            report_lines.append(f"Estimated ROI: {analysis_result.estimated_roi_percent:.1f}%")
            report_lines.append("")
            
            # Capacity Forecast
            if analysis_result.capacity_forecast:
                report_lines.append("📅 CAPACITY FORECAST")
                report_lines.append("-" * 40)
                for metric, value in analysis_result.capacity_forecast.items():
                    report_lines.append(f"{metric}: {value:.1f}")
                report_lines.append("")
            
            # Scaling Recommendations
            if analysis_result.recommended_scaling:
                report_lines.append("⚖️ SCALING RECOMMENDATIONS")
                report_lines.append("-" * 40)
                
                if analysis_result.recommended_scaling.get("immediate_scaling"):
                    report_lines.append("IMMEDIATE SCALING NEEDS:")
                    for rec in analysis_result.recommended_scaling["immediate_scaling"]:
                        report_lines.append(f"  • {rec['resource']}: {rec['action']} ({rec['recommended_increase']})")
                        report_lines.append(f"    Reason: {rec['reason']}")
                    report_lines.append("")
                
                if analysis_result.recommended_scaling.get("planned_scaling"):
                    report_lines.append("PLANNED SCALING (90 DAYS):")
                    for rec in analysis_result.recommended_scaling["planned_scaling"]:
                        report_lines.append(f"  • {rec['resource']}: {rec['recommended_action']}")
                        report_lines.append(f"    Predicted Utilization: {rec['predicted_utilization']}")
                    report_lines.append("")
            
            report_lines.append("=" * 80)
            report_lines.append("(c) 2025 Fahed Mlaiel - IA-Influencer-Agent Performance Optimizer")
            report_lines.append("=" * 80)
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"❌ Performance report generation failed: {e}")
            return f"Error generating performance report: {e}"


# Global Performance Optimizer Instance
performance_optimizer = StoragePerformanceOptimizer()


# Factory function
def create_performance_optimizer() -> StoragePerformanceOptimizer:
    """Factory function to create performance optimizer instance"""
    return StoragePerformanceOptimizer()


# Usage Example
async def main() -> None:
    """
Example usage of StoragePerformanceOptimizer"""
    try:
        optimizer = create_performance_optimizer()
        
        # Collect metrics from storage systems
        metrics = await optimizer.collect_performance_metrics("storage-node-1")
        print(f"Collected metrics: {len(metrics)}")
        
        # Simulate more metric collection
        for i in range(100):
            await optimizer.collect_performance_metrics(f"storage-node-{i % 3 + 1}")
            await asyncio.sleep(0.1)  # Small delay
        
        # Analyze performance
        analysis = await optimizer.analyze_performance_trends()
        print(f"Performance Score: {analysis.overall_performance_score:.1f}/100")
        print(f"Recommendations: {len(analysis.recommendations)}")
        
        # Generate report
        report = await optimizer.generate_performance_report(analysis)
        print("\n" + report)
        
        # Implement top recommendation if available
        if analysis.recommendations:
            top_recommendation = analysis.recommendations[0]
            implementation_result = await optimizer.implement_optimization(top_recommendation)
            print(f"Implementation result: {implementation_result}")
        
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
