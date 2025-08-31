"""Analytics Agent - Performance Analytics Module
Enterprise performance monitoring and optimization for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import asyncio
import time

class PerformanceMetricType(Enum):
    """Performance metric types"""    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    NETWORK = "network"
    USER_EXPERIENCE = "user_experience"
    BUSINESS = "business"

class AlertSeverity(Enum):
    """Alert severity levels"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class PerformanceMetric:
    """Performance metric data model"""    metric_id: str
    metric_type: PerformanceMetricType
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemPerformanceSnapshot:
    """Comprehensive system performance snapshot"""    timestamp: datetime = field(default_factory=datetime.now)
    
    # CPU Metrics
    cpu_usage_percent: float = 0.0
    cpu_load_average: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    cpu_core_count: int = 0
    cpu_frequency_mhz: float = 0.0
    
    # Memory Metrics
    memory_usage_percent: float = 0.0
    memory_total_gb: float = 0.0
    memory_available_gb: float = 0.0
    memory_used_gb: float = 0.0
    swap_usage_percent: float = 0.0
    
    # Disk Metrics
    disk_usage_percent: float = 0.0
    disk_total_gb: float = 0.0
    disk_free_gb: float = 0.0
    disk_read_iops: float = 0.0
    disk_write_iops: float = 0.0
    disk_read_mbps: float = 0.0
    disk_write_mbps: float = 0.0
    
    # Network Metrics
    network_rx_mbps: float = 0.0
    network_tx_mbps: float = 0.0
    network_rx_packets_per_sec: float = 0.0
    network_tx_packets_per_sec: float = 0.0
    network_connections_active: int = 0
    
    # Application Metrics
    process_count: int = 0
    thread_count: int = 0
    file_descriptors_open: int = 0
    context_switches_per_sec: float = 0.0


@dataclass
class ApplicationPerformanceMetrics:
    """Application-level performance metrics"""    timestamp: datetime = field(default_factory=datetime.now)
    
    # Request Metrics
    request_rate_per_second: float = 0.0
    response_time_avg_ms: float = 0.0
    response_time_p95_ms: float = 0.0
    response_time_p99_ms: float = 0.0
    error_rate_percent: float = 0.0
    
    # Database Metrics
    db_connection_pool_active: int = 0
    db_connection_pool_idle: int = 0
    db_query_time_avg_ms: float = 0.0
    db_query_rate_per_second: float = 0.0
    db_deadlocks_per_minute: float = 0.0
    
    # Cache Metrics
    cache_hit_rate_percent: float = 0.0
    cache_miss_rate_percent: float = 0.0
    cache_eviction_rate_per_second: float = 0.0
    cache_memory_usage_mb: float = 0.0
    
    # AI/ML Processing Metrics
    ml_inference_time_avg_ms: float = 0.0
    ml_model_load_time_ms: float = 0.0
    ml_batch_processing_time_ms: float = 0.0
    ai_content_analysis_queue_size: int = 0
    
    # Content Protection Metrics
    content_scanning_rate_per_second: float = 0.0
    fingerprint_generation_time_ms: float = 0.0
    copyright_detection_accuracy_percent: float = 0.0
    dmca_processing_time_avg_minutes: float = 0.0


@dataclass
class PerformanceAlert:
    """Performance alert data model"""    alert_id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnterprisePerformanceAnalyticsEngine:
    """    Enterprise Performance Analytics Engine
    
    Comprehensive performance monitoring, analysis, and optimization system
    featuring real-time metrics collection, predictive analytics, automated
    optimization recommendations, and intelligent alerting.
    """    
    def __init__(self):
        self.system_snapshots: List[SystemPerformanceSnapshot] = []
        self.application_metrics: List[ApplicationPerformanceMetrics] = []
        self.performance_alerts: List[PerformanceAlert] = []
        self.optimization_recommendations: List[PerformanceOptimizationRecommendation] = []
        
        # Performance baselines and thresholds
        self.baseline_metrics: Dict[str, float] = {}
        self.dynamic_thresholds: Dict[str, Dict[str, float]] = {}
        
        # ML models for performance prediction
        self.prediction_models: Dict[str, Any] = {
            'cpu_predictor': self._create_cpu_prediction_model(),
            'memory_predictor': self._create_memory_prediction_model(),
            'response_time_predictor': self._create_response_time_prediction_model(),
            'resource_demand_predictor': self._create_resource_demand_prediction_model()
        }
        
        # Monitoring configuration
        self.monitoring_enabled = True
        self.alert_rules: Dict[str, Dict[str, Any]] = self._initialize_alert_rules()
        self.optimization_rules: Dict[str, Dict[str, Any]] = self._initialize_optimization_rules()
        
        # Performance history for trend analysis
        self.performance_history_days = 30
        self.metric_collection_interval = 60  # seconds
        
    async def collect_real_time_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive real-time performance metrics"""        try:
            # System metrics collection
            system_snapshot = await self._collect_system_metrics()
            self.system_snapshots.append(system_snapshot)
            
            # Application metrics collection
            app_metrics = await self._collect_application_metrics()
            self.application_metrics.append(app_metrics)
            
            # Clean old data
            self._cleanup_old_metrics()
            
            # Analyze current performance state
            performance_analysis = await self._analyze_current_performance(system_snapshot, app_metrics)
            
            # Check for alerts
            alerts = await self._check_performance_alerts(system_snapshot, app_metrics)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(system_snapshot, app_metrics)
            
            return {
                "collection_timestamp": datetime.now().isoformat(),
                "system_snapshot": system_snapshot,
                "application_metrics": app_metrics,
                "performance_analysis": performance_analysis,
                "active_alerts": alerts,
                "recommendations": recommendations,
                "health_score": self._calculate_overall_health_score(system_snapshot, app_metrics)
            }
            
        except Exception as e:
            return {"error": f"Failed to collect metrics: {str(e)}"}
    
    async def analyze_performance_trends(self, timeframe_hours: int = 24) -> Dict[str, Any]:
        """Analyze performance trends over specified timeframe"""        try:
            cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
            
            # Filter metrics by timeframe
            recent_system_snapshots = [s for s in self.system_snapshots if s.timestamp >= cutoff_time]
            recent_app_metrics = [m for m in self.application_metrics if m.timestamp >= cutoff_time]
            
            if not recent_system_snapshots or not recent_app_metrics:
                return {"error": "Insufficient data for trend analysis"}
            
            # System performance trends
            system_trends = self._analyze_system_trends(recent_system_snapshots)
            
            # Application performance trends
            application_trends = self._analyze_application_trends(recent_app_metrics)
            
            # Correlation analysis
            correlation_analysis = self._analyze_metric_correlations(recent_system_snapshots, recent_app_metrics)
            
            # Predictive insights
            predictive_insights = await self._generate_predictive_insights(recent_system_snapshots, recent_app_metrics)
            
            # Performance pattern detection
            patterns = self._detect_performance_patterns(recent_system_snapshots, recent_app_metrics)
            
            return {
                "timeframe_hours": timeframe_hours,
                "data_points": {
                    "system_snapshots": len(recent_system_snapshots),
                    "application_metrics": len(recent_app_metrics)
                },
                "system_trends": system_trends,
                "application_trends": application_trends,
                "correlation_analysis": correlation_analysis,
                "predictive_insights": predictive_insights,
                "detected_patterns": patterns,
                "trend_summary": self._generate_trend_summary(system_trends, application_trends)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze trends: {str(e)}"}
    
    async def generate_performance_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance optimization report"""        try:
            # Current performance state
            current_state = await self._assess_current_performance_state()
            
            # Bottleneck identification
            bottlenecks = self._identify_performance_bottlenecks()
            
            # Resource utilization analysis
            resource_analysis = self._analyze_resource_utilization()
            
            # Performance gaps analysis
            performance_gaps = self._identify_performance_gaps()
            
            # Optimization opportunities
            optimization_opportunities = self._identify_optimization_opportunities()
            
            # Cost-benefit analysis
            cost_benefit_analysis = self._perform_cost_benefit_analysis(optimization_opportunities)
            
            # Implementation roadmap
            implementation_roadmap = self._create_optimization_roadmap(optimization_opportunities)
            
            return {
                "report_generated": datetime.now().isoformat(),
                "executive_summary": {
                    "overall_performance_score": current_state.get("overall_score", 0),
                    "critical_issues": len([r for r in self.optimization_recommendations if r.priority == "high"]),
                    "optimization_potential": self._calculate_optimization_potential(),
                    "estimated_improvement": f"{self._estimate_total_improvement()}%"
                },
                "current_performance_state": current_state,
                "identified_bottlenecks": bottlenecks,
                "resource_utilization": resource_analysis,
                "performance_gaps": performance_gaps,
                "optimization_opportunities": optimization_opportunities,
                "cost_benefit_analysis": cost_benefit_analysis,
                "implementation_roadmap": implementation_roadmap,
                "monitoring_recommendations": self._generate_monitoring_recommendations()
            }
            
        except Exception as e:
            return {"error": f"Failed to generate optimization report: {str(e)}"}
    
    async def predict_performance_issues(self, prediction_horizon_hours: int = 2) -> Dict[str, Any]:
        """Predict potential performance issues using ML models"""        try:
            if len(self.system_snapshots) < 10 or len(self.application_metrics) < 10:
                return {"error": "Insufficient historical data for predictions"}
            
            predictions = {}
            
            # CPU utilization prediction
            cpu_prediction = await self._predict_cpu_utilization(prediction_horizon_hours)
            predictions["cpu_utilization"] = cpu_prediction
            
            # Memory utilization prediction
            memory_prediction = await self._predict_memory_utilization(prediction_horizon_hours)
            predictions["memory_utilization"] = memory_prediction
            
            # Response time prediction
            response_time_prediction = await self._predict_response_times(prediction_horizon_hours)
            predictions["response_times"] = response_time_prediction
            
            # Resource exhaustion prediction
            resource_exhaustion = await self._predict_resource_exhaustion(prediction_horizon_hours)
            predictions["resource_exhaustion"] = resource_exhaustion
            
            # System load prediction
            system_load_prediction = await self._predict_system_load(prediction_horizon_hours)
            predictions["system_load"] = system_load_prediction
            
            # Generate preventive recommendations
            preventive_actions = self._generate_preventive_actions(predictions)
            
            # Calculate risk assessment
            risk_assessment = self._assess_prediction_risks(predictions)
            
            return {
                "prediction_horizon_hours": prediction_horizon_hours,
                "predictions": predictions,
                "risk_assessment": risk_assessment,
                "preventive_actions": preventive_actions,
                "confidence_scores": self._calculate_prediction_confidence(predictions),
                "monitoring_alerts": self._generate_predictive_alerts(predictions)
            }
            
        except Exception as e:
            return {"error": f"Failed to predict performance issues: {str(e)}"}
    
    async def optimize_system_performance(self, optimization_targets: List[str] = None) -> Dict[str, Any]:
        """Execute automated system performance optimizations"""        try:
            if not optimization_targets:
                optimization_targets = ["cpu", "memory", "disk", "network", "database", "cache"]
            
            optimization_results = {}
            
            for target in optimization_targets:
                if target == "cpu":
                    cpu_optimization = await self._optimize_cpu_performance()
                    optimization_results["cpu"] = cpu_optimization
                
                elif target == "memory":
                    memory_optimization = await self._optimize_memory_usage()
                    optimization_results["memory"] = memory_optimization
                
                elif target == "disk":
                    disk_optimization = await self._optimize_disk_performance()
                    optimization_results["disk"] = disk_optimization
                
                elif target == "network":
                    network_optimization = await self._optimize_network_performance()
                    optimization_results["network"] = network_optimization
                
                elif target == "database":
                    db_optimization = await self._optimize_database_performance()
                    optimization_results["database"] = db_optimization
                
                elif target == "cache":
                    cache_optimization = await self._optimize_cache_performance()
                    optimization_results["cache"] = cache_optimization
            
            # Apply ML-driven optimizations
            ml_optimizations = await self._apply_ml_driven_optimizations()
            optimization_results["ml_optimizations"] = ml_optimizations
            
            # Validate optimization effectiveness
            effectiveness_validation = await self._validate_optimization_effectiveness(optimization_results)
            
            return {
                "optimization_timestamp": datetime.now().isoformat(),
                "targets_optimized": optimization_targets,
                "optimization_results": optimization_results,
                "effectiveness_validation": effectiveness_validation,
                "performance_improvement": self._calculate_performance_improvement(),
                "next_optimization_schedule": self._schedule_next_optimization()
            }
            
        except Exception as e:
            return {"error": f"Failed to optimize system performance: {str(e)}"}
    
    # System Metrics Collection Methods
    
    async def _collect_system_metrics(self) -> SystemPerformanceSnapshot:
        """Collect comprehensive system performance metrics"""        # In a real implementation, this would use system monitoring libraries
        # like psutil, system APIs, or monitoring agents
        
        snapshot = SystemPerformanceSnapshot(
            # CPU Metrics
            cpu_usage_percent=np.random.uniform(20, 80),
            cpu_load_average=(np.random.uniform(0.5, 2.0), np.random.uniform(0.5, 2.0), np.random.uniform(0.5, 2.0)),
            cpu_core_count=8,
            cpu_frequency_mhz=np.random.uniform(2400, 3600),
            
            # Memory Metrics
            memory_usage_percent=np.random.uniform(40, 85),
            memory_total_gb=32.0,
            memory_available_gb=np.random.uniform(5, 15),
            memory_used_gb=np.random.uniform(15, 27),
            swap_usage_percent=np.random.uniform(0, 20),
            
            # Disk Metrics
            disk_usage_percent=np.random.uniform(60, 90),
            disk_total_gb=1000.0,
            disk_free_gb=np.random.uniform(100, 400),
            disk_read_iops=np.random.uniform(50, 500),
            disk_write_iops=np.random.uniform(50, 300),
            disk_read_mbps=np.random.uniform(10, 100),
            disk_write_mbps=np.random.uniform(10, 80),
            
            # Network Metrics
            network_rx_mbps=np.random.uniform(5, 50),
            network_tx_mbps=np.random.uniform(5, 50),
            network_rx_packets_per_sec=np.random.uniform(100, 1000),
            network_tx_packets_per_sec=np.random.uniform(100, 1000),
            network_connections_active=np.random.randint(50, 500),
            
            # Application Metrics
            process_count=np.random.randint(200, 400),
            thread_count=np.random.randint(1000, 3000),
            file_descriptors_open=np.random.randint(500, 2000),
            context_switches_per_sec=np.random.uniform(1000, 5000)
        )
        
        return snapshot
    
    async def _collect_application_metrics(self) -> ApplicationPerformanceMetrics:
        """Collect application-specific performance metrics"""        metrics = ApplicationPerformanceMetrics(
            # Request Metrics
            request_rate_per_second=np.random.uniform(10, 100),
            response_time_avg_ms=np.random.uniform(50, 500),
            response_time_p95_ms=np.random.uniform(100, 1000),
            response_time_p99_ms=np.random.uniform(200, 2000),
            error_rate_percent=np.random.uniform(0.1, 2.0),
            
            # Database Metrics
            db_connection_pool_active=np.random.randint(10, 50),
            db_connection_pool_idle=np.random.randint(5, 20),
            db_query_time_avg_ms=np.random.uniform(10, 100),
            db_query_rate_per_second=np.random.uniform(50, 500),
            db_deadlocks_per_minute=np.random.uniform(0, 2),
            
            # Cache Metrics
            cache_hit_rate_percent=np.random.uniform(85, 98),
            cache_miss_rate_percent=np.random.uniform(2, 15),
            cache_eviction_rate_per_second=np.random.uniform(0.1, 5.0),
            cache_memory_usage_mb=np.random.uniform(500, 2000),
            
            # AI/ML Processing Metrics
            ml_inference_time_avg_ms=np.random.uniform(100, 1000),
            ml_model_load_time_ms=np.random.uniform(500, 5000),
            ml_batch_processing_time_ms=np.random.uniform(1000, 10000),
            ai_content_analysis_queue_size=np.random.randint(0, 100),
            
            # Content Protection Metrics
            content_scanning_rate_per_second=np.random.uniform(5, 50),
            fingerprint_generation_time_ms=np.random.uniform(200, 2000),
            copyright_detection_accuracy_percent=np.random.uniform(92, 99),
            dmca_processing_time_avg_minutes=np.random.uniform(5, 60)
        )
        
        return metrics
    
    def _cleanup_old_metrics(self):
        """Clean up old metric data to prevent memory bloat"""        cutoff_time = datetime.now() - timedelta(days=self.performance_history_days)
        
        # Clean system snapshots
        self.system_snapshots = [s for s in self.system_snapshots if s.timestamp >= cutoff_time]
        
        # Clean application metrics
        self.application_metrics = [m for m in self.application_metrics if m.timestamp >= cutoff_time]
        
        # Clean resolved alerts older than 7 days
        alert_cutoff = datetime.now() - timedelta(days=7)
        self.performance_alerts = [a for a in self.performance_alerts 
                                  if not a.resolved or a.timestamp >= alert_cutoff]
    
    # Performance Analysis Methods
    
    async def _analyze_current_performance(self, system_snapshot: SystemPerformanceSnapshot, 
                                         app_metrics: ApplicationPerformanceMetrics) -> Dict[str, Any]:
        """Analyze current performance state"""        analysis = {
            "system_health_score": self._calculate_system_health_score(system_snapshot),
            "application_health_score": self._calculate_application_health_score(app_metrics),
            "resource_utilization_status": self._assess_resource_utilization(system_snapshot),
            "performance_bottlenecks": self._identify_current_bottlenecks(system_snapshot, app_metrics),
            "critical_metrics": self._identify_critical_metrics(system_snapshot, app_metrics),
            "performance_grade": self._calculate_performance_grade(system_snapshot, app_metrics)
        }
        
        return analysis
    
    async def _check_performance_alerts(self, system_snapshot: SystemPerformanceSnapshot,
                                      app_metrics: ApplicationPerformanceMetrics) -> List[PerformanceAlert]:
        """Check for performance alerts based on current metrics"""        alerts = []
        
        # System alerts
        if system_snapshot.cpu_usage_percent > 90:
            alerts.append(self._create_alert("cpu_high_usage", AlertSeverity.CRITICAL, 
                                            f"CPU usage at {system_snapshot.cpu_usage_percent:.1f}%",
                                            system_snapshot.cpu_usage_percent, 90))
        
        if system_snapshot.memory_usage_percent > 95:
            alerts.append(self._create_alert("memory_critical", AlertSeverity.CRITICAL,
                                            f"Memory usage at {system_snapshot.memory_usage_percent:.1f}%",
                                            system_snapshot.memory_usage_percent, 95))
        
        if system_snapshot.disk_usage_percent > 95:
            alerts.append(self._create_alert("disk_space_critical", AlertSeverity.CRITICAL,
                                            f"Disk usage at {system_snapshot.disk_usage_percent:.1f}%",
                                            system_snapshot.disk_usage_percent, 95))
        
        # Application alerts
        if app_metrics.response_time_p95_ms > 2000:
            alerts.append(self._create_alert("response_time_high", AlertSeverity.HIGH,
                                            f"95th percentile response time at {app_metrics.response_time_p95_ms:.1f}ms",
                                            app_metrics.response_time_p95_ms, 2000))
        
        if app_metrics.error_rate_percent > 5.0:
            alerts.append(self._create_alert("error_rate_high", AlertSeverity.HIGH,
                                            f"Error rate at {app_metrics.error_rate_percent:.2f}%",
                                            app_metrics.error_rate_percent, 5.0))
        
        if app_metrics.cache_hit_rate_percent < 80:
            alerts.append(self._create_alert("cache_hit_rate_low", AlertSeverity.MEDIUM,
                                            f"Cache hit rate at {app_metrics.cache_hit_rate_percent:.1f}%",
                                            app_metrics.cache_hit_rate_percent, 80))
        
        # Store alerts
        for alert in alerts:
            self.performance_alerts.append(alert)
        
        return alerts
    
    async def _generate_optimization_recommendations(self, system_snapshot: SystemPerformanceSnapshot,
                                                   app_metrics: ApplicationPerformanceMetrics) -> List[PerformanceOptimizationRecommendation]:
        """Generate performance optimization recommendations"""        recommendations = []
        
        # CPU optimization
        if system_snapshot.cpu_usage_percent > 70:
            recommendations.append(PerformanceOptimizationRecommendation(
                recommendation_id=f"cpu_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category="system",
                title="CPU Usage Optimization",
                description="High CPU usage detected. Optimize CPU-intensive processes and consider scaling.",
                priority="high" if system_snapshot.cpu_usage_percent > 85 else "medium",
                estimated_impact="high",
                implementation_effort="medium",
                estimated_improvement_percent=25.0,
                implementation_steps=[
                    "Analyze CPU-intensive processes",
                    "Implement process optimization",
                    "Consider horizontal scaling",
                    "Monitor CPU usage patterns"
                ],
                prerequisites=["System monitoring access", "Process analysis tools"],
                monitoring_metrics=["cpu_usage_percent", "cpu_load_average"]
            ))
        
        # Memory optimization
        if system_snapshot.memory_usage_percent > 80:
            recommendations.append(PerformanceOptimizationRecommendation(
                recommendation_id=f"mem_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category="system",
                title="Memory Usage Optimization",
                description="High memory usage detected. Optimize memory allocation and implement memory management strategies.",
                priority="high" if system_snapshot.memory_usage_percent > 90 else "medium",
                estimated_impact="high",
                implementation_effort="medium",
                estimated_improvement_percent=20.0,
                implementation_steps=[
                    "Identify memory leaks",
                    "Optimize memory allocation",
                    "Implement garbage collection tuning",
                    "Add memory monitoring"
                ],
                prerequisites=["Memory profiling tools", "Application access"],
                monitoring_metrics=["memory_usage_percent", "memory_available_gb"]
            ))
        
        # Database optimization
        if app_metrics.db_query_time_avg_ms > 100:
            recommendations.append(PerformanceOptimizationRecommendation(
                recommendation_id=f"db_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category="database",
                title="Database Query Optimization",
                description="Slow database queries detected. Optimize query performance and indexing strategy.",
                priority="high",
                estimated_impact="high",
                implementation_effort="high",
                estimated_improvement_percent=40.0,
                implementation_steps=[
                    "Analyze slow queries",
                    "Optimize indexing strategy",
                    "Implement query caching",
                    "Database configuration tuning"
                ],
                prerequisites=["Database access", "Query analysis tools"],
                monitoring_metrics=["db_query_time_avg_ms", "db_query_rate_per_second"]
            ))
        
        # Cache optimization
        if app_metrics.cache_hit_rate_percent < 85:
            recommendations.append(PerformanceOptimizationRecommendation(
                recommendation_id=f"cache_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category="application",
                title="Cache Performance Optimization",
                description="Low cache hit rate detected. Optimize caching strategy and cache configuration.",
                priority="medium",
                estimated_impact="medium",
                implementation_effort="low",
                estimated_improvement_percent=15.0,
                implementation_steps=[
                    "Analyze cache usage patterns",
                    "Optimize cache key strategy",
                    "Adjust cache expiration policies",
                    "Increase cache memory allocation"
                ],
                prerequisites=["Cache configuration access"],
                monitoring_metrics=["cache_hit_rate_percent", "cache_miss_rate_percent"]
            ))
        
        return recommendations
    
    # Helper Methods for Metric Calculation and Analysis
    
    def _calculate_system_health_score(self, snapshot: SystemPerformanceSnapshot) -> float:
        """Calculate system health score based on resource utilization"""        cpu_score = max(0, 100 - snapshot.cpu_usage_percent)
        memory_score = max(0, 100 - snapshot.memory_usage_percent)
        disk_score = max(0, 100 - snapshot.disk_usage_percent)
        
        # Weighted average
        health_score = (cpu_score * 0.3 + memory_score * 0.3 + disk_score * 0.2 + 
                       (100 - min(100, snapshot.network_rx_mbps + snapshot.network_tx_mbps)) * 0.2)
        
        return max(0, min(100, health_score))
    
    def _calculate_application_health_score(self, metrics: ApplicationPerformanceMetrics) -> float:
        """Calculate application health score"""        response_time_score = max(0, 100 - (metrics.response_time_avg_ms / 10))  # 1000ms = 0 score
        error_rate_score = max(0, 100 - (metrics.error_rate_percent * 10))  # 10% error = 0 score
        cache_score = metrics.cache_hit_rate_percent
        
        # Weighted average
        health_score = (response_time_score * 0.4 + error_rate_score * 0.3 + cache_score * 0.3)
        
        return max(0, min(100, health_score))
    
    def _calculate_overall_health_score(self, system_snapshot: SystemPerformanceSnapshot,
                                      app_metrics: ApplicationPerformanceMetrics) -> float:
        """Calculate overall system health score"""        system_score = self._calculate_system_health_score(system_snapshot)
        app_score = self._calculate_application_health_score(app_metrics)
        
        return (system_score * 0.5 + app_score * 0.5)
    
    def _assess_resource_utilization(self, snapshot: SystemPerformanceSnapshot) -> Dict[str, str]:
        """Assess resource utilization status"""        def get_status(usage_percent: float) -> str:
            if usage_percent > 95:
                return "critical"
            elif usage_percent > 85:
                return "high"
            elif usage_percent > 70:
                return "medium"
            else:
                return "normal"
        
        return {
            "cpu": get_status(snapshot.cpu_usage_percent),
            "memory": get_status(snapshot.memory_usage_percent),
            "disk": get_status(snapshot.disk_usage_percent),
            "network": get_status(min(100, (snapshot.network_rx_mbps + snapshot.network_tx_mbps) / 2))
        }
    
    def _identify_current_bottlenecks(self, system_snapshot: SystemPerformanceSnapshot,
                                    app_metrics: ApplicationPerformanceMetrics) -> List[Dict[str, Any]]:
        """Identify current performance bottlenecks"""        bottlenecks = []
        
        if system_snapshot.cpu_usage_percent > 80:
            bottlenecks.append({
                "type": "cpu",
                "severity": "high" if system_snapshot.cpu_usage_percent > 90 else "medium",
                "description": f"CPU usage at {system_snapshot.cpu_usage_percent:.1f}%",
                "impact": "System responsiveness and throughput"
            })
        
        if system_snapshot.memory_usage_percent > 85:
            bottlenecks.append({
                "type": "memory",
                "severity": "high" if system_snapshot.memory_usage_percent > 95 else "medium",
                "description": f"Memory usage at {system_snapshot.memory_usage_percent:.1f}%",
                "impact": "Application performance and stability"
            })
        
        if app_metrics.db_query_time_avg_ms > 100:
            bottlenecks.append({
                "type": "database",
                "severity": "high" if app_metrics.db_query_time_avg_ms > 500 else "medium",
                "description": f"Average database query time: {app_metrics.db_query_time_avg_ms:.1f}ms",
                "impact": "Application response times and user experience"
            })
        
        if app_metrics.response_time_p95_ms > 1000:
            bottlenecks.append({
                "type": "application_response",
                "severity": "high" if app_metrics.response_time_p95_ms > 2000 else "medium",
                "description": f"95th percentile response time: {app_metrics.response_time_p95_ms:.1f}ms",
                "impact": "User experience and satisfaction"
            })
        
        return bottlenecks
    
    def _identify_critical_metrics(self, system_snapshot: SystemPerformanceSnapshot,
                                 app_metrics: ApplicationPerformanceMetrics) -> Dict[str, Dict[str, Any]]:
        """Identify critical performance metrics requiring attention"""        critical_metrics = {}
        
        # System metrics
        if system_snapshot.cpu_usage_percent > 85:
            critical_metrics["cpu_usage"] = {
                "current_value": system_snapshot.cpu_usage_percent,
                "threshold": 85,
                "status": "critical" if system_snapshot.cpu_usage_percent > 95 else "warning",
                "trend": self._get_cpu_trend()
            }
        
        if system_snapshot.memory_usage_percent > 90:
            critical_metrics["memory_usage"] = {
                "current_value": system_snapshot.memory_usage_percent,
                "threshold": 90,
                "status": "critical" if system_snapshot.memory_usage_percent > 95 else "warning",
                "trend": self._get_memory_trend()
            }
        
        # Application metrics
        if app_metrics.error_rate_percent > 2.0:
            critical_metrics["error_rate"] = {
                "current_value": app_metrics.error_rate_percent,
                "threshold": 2.0,
                "status": "critical" if app_metrics.error_rate_percent > 5.0 else "warning",
                "trend": self._get_error_rate_trend()
            }
        
        if app_metrics.response_time_p95_ms > 1500:
            critical_metrics["response_time_p95"] = {
                "current_value": app_metrics.response_time_p95_ms,
                "threshold": 1500,
                "status": "critical" if app_metrics.response_time_p95_ms > 3000 else "warning",
                "trend": self._get_response_time_trend()
            }
        
        return critical_metrics
    
    def _calculate_performance_grade(self, system_snapshot: SystemPerformanceSnapshot,
                                   app_metrics: ApplicationPerformanceMetrics) -> str:
        """Calculate overall performance grade"""        overall_score = self._calculate_overall_health_score(system_snapshot, app_metrics)
        
        if overall_score >= 90:
            return "A+"
        elif overall_score >= 85:
            return "A"
        elif overall_score >= 80:
            return "B+"
        elif overall_score >= 75:
            return "B"
        elif overall_score >= 70:
            return "C+"
        elif overall_score >= 65:
            return "C"
        elif overall_score >= 60:
            return "D"
        else:
            return "F"
    
    def _create_alert(self, metric_name: str, severity: AlertSeverity, message: str,
                     current_value: float, threshold_value: float) -> PerformanceAlert:
        """Create a performance alert"""        alert_id = f"alert_{metric_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return PerformanceAlert(
            alert_id=alert_id,
            metric_name=metric_name,
            severity=severity,
            message=message,
            current_value=current_value,
            threshold_value=threshold_value,
            context={
                "timestamp": datetime.now().isoformat(),
                "system_state": "monitoring"
            }
        )
    
    # Trend Analysis Helper Methods
    
    def _get_cpu_trend(self) -> str:
        """Get CPU usage trend"""        if len(self.system_snapshots) < 3:
            return "insufficient_data"
        
        recent_cpu = [s.cpu_usage_percent for s in self.system_snapshots[-5:]]
        
        if len(recent_cpu) >= 2:
            slope = np.polyfit(range(len(recent_cpu)), recent_cpu, 1)[0]
            
            if slope > 2:
                return "increasing"
            elif slope < -2:
                return "decreasing"
            else:
                return "stable"
        
        return "stable"
    
    def _get_memory_trend(self) -> str:
        """Get memory usage trend"""        if len(self.system_snapshots) < 3:
            return "insufficient_data"
        
        recent_memory = [s.memory_usage_percent for s in self.system_snapshots[-5:]]
        
        if len(recent_memory) >= 2:
            slope = np.polyfit(range(len(recent_memory)), recent_memory, 1)[0]
            
            if slope > 2:
                return "increasing"
            elif slope < -2:
                return "decreasing"
            else:
                return "stable"
        
        return "stable"
    
    def _get_error_rate_trend(self) -> str:
        """Get error rate trend"""        if len(self.application_metrics) < 3:
            return "insufficient_data"
        
        recent_errors = [m.error_rate_percent for m in self.application_metrics[-5:]]
        
        if len(recent_errors) >= 2:
            slope = np.polyfit(range(len(recent_errors)), recent_errors, 1)[0]
            
            if slope > 0.5:
                return "increasing"
            elif slope < -0.5:
                return "decreasing"
            else:
                return "stable"
        
        return "stable"
    
    def _get_response_time_trend(self) -> str:
        """Get response time trend"""        if len(self.application_metrics) < 3:
            return "insufficient_data"
        
        recent_response_times = [m.response_time_p95_ms for m in self.application_metrics[-5:]]
        
        if len(recent_response_times) >= 2:
            slope = np.polyfit(range(len(recent_response_times)), recent_response_times, 1)[0]
            
            if slope > 50:
                return "increasing"
            elif slope < -50:
                return "decreasing"
            else:
                return "stable"
        
        return "stable"
    current_value: float
    threshold_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_time: Optional[datetime] = None

class PerformanceMonitor:
    """Enterprise performance monitoring engine"""    
    def __init__(self):
        self.metrics_history: List[PerformanceMetric] = []
        self.system_metrics: List[SystemPerformance] = []
        self.app_metrics: List[ApplicationPerformance] = []
        self.active_alerts: List[PerformanceAlert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.baseline_metrics: Dict[str, float] = {}
    
    async def collect_system_metrics(self) -> SystemPerformance:
        """Collect current system performance metrics"""        # Simulated system metrics collection
        system_perf = SystemPerformance(
            cpu_usage=np.random.uniform(10, 80),
            memory_usage=np.random.uniform(30, 85),
            disk_usage=np.random.uniform(20, 75),
            network_io=np.random.uniform(100, 1000),
            response_time_avg=np.random.uniform(50, 500),
            throughput=np.random.uniform(100, 1500),
            error_rate=np.random.uniform(0, 5),
            availability=np.random.uniform(95, 100)
        )
        
        self.system_metrics.append(system_perf)
        await self._check_system_thresholds(system_perf)
        
        return system_perf
    
    async def collect_application_metrics(self) -> ApplicationPerformance:
        """Collect current application performance metrics"""        # Simulated application metrics collection
        app_perf = ApplicationPerformance(
            request_count=np.random.randint(100, 2000),
            response_time_p50=np.random.uniform(20, 200),
            response_time_p95=np.random.uniform(100, 800),
            response_time_p99=np.random.uniform(200, 1500),
            error_count=np.random.randint(0, 50),
            success_rate=np.random.uniform(95, 100),
            active_connections=np.random.randint(10, 500),
            queue_depth=np.random.randint(0, 100),
            cache_hit_rate=np.random.uniform(70, 95)
        )
        
        self.app_metrics.append(app_perf)
        await self._check_application_thresholds(app_perf)
        
        return app_perf
    
    def analyze_performance_trends(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze performance trends over specified time period"""        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Filter recent metrics
        recent_system = [m for m in self.system_metrics if m.timestamp >= cutoff_time]
        recent_app = [m for m in self.app_metrics if m.timestamp >= cutoff_time]
        
        if not recent_system or not recent_app:
            return {"error": "Insufficient data for trend analysis"}
        
        # System trends
        system_trends = self._analyze_system_trends(recent_system)
        
        # Application trends
        app_trends = self._analyze_application_trends(recent_app)
        
        # Performance score
        performance_score = self._calculate_performance_score(recent_system[-1], recent_app[-1])
        
        # Bottleneck identification
        bottlenecks = self._identify_bottlenecks(recent_system, recent_app)
        
        # Optimization recommendations
        recommendations = self._generate_optimization_recommendations(recent_system, recent_app)
        
        return {
            "analysis_period": f"{hours_back} hours",
            "performance_score": performance_score,
            "system_trends": system_trends,
            "application_trends": app_trends,
            "bottlenecks": bottlenecks,
            "optimization_recommendations": recommendations,
            "alert_summary": self._get_alert_summary(hours_back)
        }
    
    def predict_performance_issues(self, prediction_window_hours: int = 4) -> Dict[str, Any]:
        """Predict potential performance issues using trend analysis"""        if len(self.system_metrics) < 10 or len(self.app_metrics) < 10:
            return {"prediction": "insufficient_data"}
        
        # Recent metrics for trend analysis
        recent_system = self.system_metrics[-20:]
        recent_app = self.app_metrics[-20:]
        
        # Predict system metrics
        system_predictions = self._predict_system_metrics(recent_system, prediction_window_hours)
        
        # Predict application metrics
        app_predictions = self._predict_application_metrics(recent_app, prediction_window_hours)
        
        # Identify potential issues
        potential_issues = []
        
        # System threshold predictions
        if system_predictions.get("cpu_usage", 0) > 85:
            potential_issues.append({
                "issue": "High CPU usage predicted",
                "probability": 0.8,
                "estimated_time": f"~{prediction_window_hours/2} hours",
                "impact": "high"
            })
        
        if system_predictions.get("memory_usage", 0) > 90:
            potential_issues.append({
                "issue": "Memory exhaustion predicted",
                "probability": 0.75,
                "estimated_time": f"~{prediction_window_hours/3} hours",
                "impact": "critical"
            })
        
        # Application threshold predictions
        if app_predictions.get("response_time_p95", 0) > 1000:
            potential_issues.append({
                "issue": "Response time degradation predicted",
                "probability": 0.7,
                "estimated_time": f"~{prediction_window_hours/2} hours",
                "impact": "medium"
            })
        
        if app_predictions.get("error_rate", 0) > 10:
            potential_issues.append({
                "issue": "Increased error rate predicted",
                "probability": 0.85,
                "estimated_time": f"~{prediction_window_hours/4} hours",
                "impact": "high"
            })
        
        return {
            "prediction_window": f"{prediction_window_hours} hours",
            "system_predictions": system_predictions,
            "application_predictions": app_predictions,
            "potential_issues": potential_issues,
            "preventive_actions": self._suggest_preventive_actions(potential_issues)
        }
    
    def generate_performance_report(self, report_type: str = "daily") -> Dict[str, Any]:
        """Generate comprehensive performance report"""        # Determine time period based on report type
        hours_map = {"hourly": 1, "daily": 24, "weekly": 168, "monthly": 720}
        hours_back = hours_map.get(report_type, 24)
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Filter metrics
        period_system = [m for m in self.system_metrics if m.timestamp >= cutoff_time]
        period_app = [m for m in self.app_metrics if m.timestamp >= cutoff_time]
        period_alerts = [a for a in self.active_alerts if a.timestamp >= cutoff_time]
        
        if not period_system or not period_app:
            return {"error": "No data available for the specified period"}
        
        # Calculate summary statistics
        system_summary = self._calculate_system_summary(period_system)
        app_summary = self._calculate_application_summary(period_app)
        
        # Performance highlights
        highlights = self._generate_performance_highlights(period_system, period_app)
        
        # SLA compliance
        sla_compliance = self._calculate_sla_compliance(period_system, period_app)
        
        # Cost analysis
        cost_analysis = self._analyze_performance_costs(period_system, period_app)
        
        return {
            "report_type": report_type,
            "period": f"Last {hours_back} hours",
            "generated_at": datetime.now().isoformat(),
            "executive_summary": {
                "overall_health": self._assess_overall_health(period_system[-1], period_app[-1]),
                "key_metrics": self._extract_key_metrics(period_system[-1], period_app[-1]),
                "critical_issues": len([a for a in period_alerts if a.severity == AlertSeverity.CRITICAL]),
                "performance_trend": self._determine_performance_trend(period_system, period_app)
            },
            "system_performance": system_summary,
            "application_performance": app_summary,
            "performance_highlights": highlights,
            "sla_compliance": sla_compliance,
            "alert_analysis": self._analyze_alerts(period_alerts),
            "cost_analysis": cost_analysis,
            "recommendations": self._generate_comprehensive_recommendations(period_system, period_app)
        }
    
    def optimize_performance(self, optimization_target: str = "response_time") -> Dict[str, Any]:
        """Generate performance optimization strategies"""        if not self.system_metrics or not self.app_metrics:
            return {"error": "No performance data available"}
        
        latest_system = self.system_metrics[-1]
        latest_app = self.app_metrics[-1]
        
        optimization_strategies = []
        
        # Response time optimization
        if optimization_target == "response_time":
            strategies = self._optimize_response_time(latest_system, latest_app)
            optimization_strategies.extend(strategies)
        
        # Throughput optimization
        elif optimization_target == "throughput":
            strategies = self._optimize_throughput(latest_system, latest_app)
            optimization_strategies.extend(strategies)
        
        # Resource optimization
        elif optimization_target == "resources":
            strategies = self._optimize_resources(latest_system, latest_app)
            optimization_strategies.extend(strategies)
        
        # Cost optimization
        elif optimization_target == "cost":
            strategies = self._optimize_costs(latest_system, latest_app)
            optimization_strategies.extend(strategies)
        
        # General optimization
        else:
            strategies = self._general_optimization(latest_system, latest_app)
            optimization_strategies.extend(strategies)
        
        # Performance tuning recommendations
        tuning_recommendations = self._generate_tuning_recommendations()
        
        # Infrastructure scaling suggestions
        scaling_suggestions = self._generate_scaling_suggestions(latest_system, latest_app)
        
        return {
            "optimization_target": optimization_target,
            "current_performance": {
                "system": self._serialize_system_performance(latest_system),
                "application": self._serialize_application_performance(latest_app)
            },
            "optimization_strategies": optimization_strategies,
            "tuning_recommendations": tuning_recommendations,
            "scaling_suggestions": scaling_suggestions,
            "expected_improvements": self._estimate_optimization_impact(optimization_strategies),
            "implementation_priority": self._prioritize_optimizations(optimization_strategies)
        }
    
    async def _check_system_thresholds(self, system_perf: SystemPerformance):
        """Check system performance against thresholds"""        # CPU threshold check
        if system_perf.cpu_usage > 90:
            await self._create_alert("cpu_usage", AlertSeverity.CRITICAL, 
                                   system_perf.cpu_usage, 90, "Critical CPU usage detected")
        elif system_perf.cpu_usage > 80:
            await self._create_alert("cpu_usage", AlertSeverity.HIGH,
                                   system_perf.cpu_usage, 80, "High CPU usage detected")
        
        # Memory threshold check
        if system_perf.memory_usage > 95:
            await self._create_alert("memory_usage", AlertSeverity.CRITICAL,
                                   system_perf.memory_usage, 95, "Critical memory usage detected")
        elif system_perf.memory_usage > 85:
            await self._create_alert("memory_usage", AlertSeverity.HIGH,
                                   system_perf.memory_usage, 85, "High memory usage detected")
        
        # Response time threshold check
        if system_perf.response_time_avg > 1000:
            await self._create_alert("response_time", AlertSeverity.HIGH,
                                   system_perf.response_time_avg, 1000, "High response time detected")
        
        # Error rate threshold check
        if system_perf.error_rate > 5:
            await self._create_alert("error_rate", AlertSeverity.HIGH,
                                   system_perf.error_rate, 5, "High error rate detected")
    
    async def _check_application_thresholds(self, app_perf: ApplicationPerformance):
        """Check application performance against thresholds"""        # Response time P95 threshold
        if app_perf.response_time_p95 > 1000:
            await self._create_alert("response_time_p95", AlertSeverity.HIGH,
                                   app_perf.response_time_p95, 1000, "High P95 response time detected")
        
        # Success rate threshold
        if app_perf.success_rate < 95:
            await self._create_alert("success_rate", AlertSeverity.CRITICAL,
                                   app_perf.success_rate, 95, "Low success rate detected")
        
        # Cache hit rate threshold
        if app_perf.cache_hit_rate < 70:
            await self._create_alert("cache_hit_rate", AlertSeverity.MEDIUM,
                                   app_perf.cache_hit_rate, 70, "Low cache hit rate detected")
    
    async def _create_alert(self, metric_name: str, severity: AlertSeverity, 
                          current_value: float, threshold_value: float, message: str):
        """Create performance alert"""        alert = PerformanceAlert(
            alert_id=f"alert_{int(time.time())}_{metric_name}",
            metric_name=metric_name,
            severity=severity,
            message=message,
            current_value=current_value,
            threshold_value=threshold_value
        )
        
        self.active_alerts.append(alert)
    
    def _analyze_system_trends(self, system_metrics: List[SystemPerformance]) -> Dict[str, Any]:
        """Analyze system performance trends"""        if len(system_metrics) < 2:
            return {}
        
        # Calculate trends for key metrics
        cpu_values = [m.cpu_usage for m in system_metrics]
        memory_values = [m.memory_usage for m in system_metrics]
        response_time_values = [m.response_time_avg for m in system_metrics]
        
        return {
            "cpu_usage": {
                "current": cpu_values[-1],
                "avg": np.mean(cpu_values),
                "trend": self._calculate_trend(cpu_values),
                "volatility": np.std(cpu_values)
            },
            "memory_usage": {
                "current": memory_values[-1],
                "avg": np.mean(memory_values),
                "trend": self._calculate_trend(memory_values),
                "volatility": np.std(memory_values)
            },
            "response_time": {
                "current": response_time_values[-1],
                "avg": np.mean(response_time_values),
                "trend": self._calculate_trend(response_time_values),
                "volatility": np.std(response_time_values)
            }
        }
    
    def _analyze_application_trends(self, app_metrics: List[ApplicationPerformance]) -> Dict[str, Any]:
        """Analyze application performance trends"""        if len(app_metrics) < 2:
            return {}
        
        # Calculate trends for key metrics
        request_counts = [m.request_count for m in app_metrics]
        p95_response_times = [m.response_time_p95 for m in app_metrics]
        success_rates = [m.success_rate for m in app_metrics]
        
        return {
            "request_volume": {
                "current": request_counts[-1],
                "avg": np.mean(request_counts),
                "trend": self._calculate_trend(request_counts),
                "volatility": np.std(request_counts)
            },
            "response_time_p95": {
                "current": p95_response_times[-1],
                "avg": np.mean(p95_response_times),
                "trend": self._calculate_trend(p95_response_times),
                "volatility": np.std(p95_response_times)
            },
            "success_rate": {
                "current": success_rates[-1],
                "avg": np.mean(success_rates),
                "trend": self._calculate_trend(success_rates),
                "volatility": np.std(success_rates)
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values"""        if len(values) < 3:
            return "stable"
        
        # Use linear regression to determine trend
        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        slope = coefficients[0]
        
        # Determine trend based on slope and significance
        if abs(slope) < np.std(values) * 0.1:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _calculate_performance_score(self, system_perf: SystemPerformance, 
                                   app_perf: ApplicationPerformance) -> float:
        """Calculate overall performance score (0-100)"""        # System performance components (40% weight)
        cpu_score = max(0, 100 - system_perf.cpu_usage)
        memory_score = max(0, 100 - system_perf.memory_usage)
        response_time_score = max(0, 100 - min(system_perf.response_time_avg / 10, 100))
        availability_score = system_perf.availability
        
        system_score = (cpu_score + memory_score + response_time_score + availability_score) / 4
        
        # Application performance components (60% weight)
        app_response_score = max(0, 100 - min(app_perf.response_time_p95 / 10, 100))
        success_rate_score = app_perf.success_rate
        cache_performance_score = app_perf.cache_hit_rate
        
        app_score = (app_response_score + success_rate_score + cache_performance_score) / 3
        
        # Weighted overall score
        overall_score = (system_score * 0.4) + (app_score * 0.6)
        
        return round(overall_score, 2)
    
    def _identify_bottlenecks(self, system_metrics: List[SystemPerformance], 
                            app_metrics: List[ApplicationPerformance]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""        bottlenecks = []
        
        latest_system = system_metrics[-1]
        latest_app = app_metrics[-1]
        
        # System bottlenecks
        if latest_system.cpu_usage > 80:
            bottlenecks.append({
                "type": "system",
                "resource": "CPU",
                "severity": "high" if latest_system.cpu_usage > 90 else "medium",
                "current_usage": latest_system.cpu_usage,
                "impact": "Response time degradation, request queuing"
            })
        
        if latest_system.memory_usage > 85:
            bottlenecks.append({
                "type": "system",
                "resource": "Memory",
                "severity": "high" if latest_system.memory_usage > 95 else "medium",
                "current_usage": latest_system.memory_usage,
                "impact": "Application instability, potential crashes"
            })
        
        # Application bottlenecks
        if latest_app.response_time_p95 > 800:
            bottlenecks.append({
                "type": "application",
                "resource": "Response Time",
                "severity": "high" if latest_app.response_time_p95 > 1200 else "medium",
                "current_value": latest_app.response_time_p95,
                "impact": "Poor user experience, potential timeouts"
            })
        
        if latest_app.cache_hit_rate < 75:
            bottlenecks.append({
                "type": "application",
                "resource": "Cache Performance",
                "severity": "medium",
                "current_value": latest_app.cache_hit_rate,
                "impact": "Increased database load, slower response times"
            })
        
        return bottlenecks
    
    def _generate_optimization_recommendations(self, system_metrics: List[SystemPerformance], 
                                             app_metrics: List[ApplicationPerformance]) -> List[str]:
        """Generate optimization recommendations"""        recommendations = []
        
        latest_system = system_metrics[-1]
        latest_app = app_metrics[-1]
        
        # System optimizations
        if latest_system.cpu_usage > 75:
            recommendations.append("Consider horizontal scaling or CPU optimization")
        
        if latest_system.memory_usage > 80:
            recommendations.append("Investigate memory leaks and optimize memory usage")
        
        if latest_system.response_time_avg > 300:
            recommendations.append("Optimize database queries and implement caching strategies")
        
        # Application optimizations
        if latest_app.response_time_p95 > 500:
            recommendations.append("Implement application-level caching and query optimization")
        
        if latest_app.cache_hit_rate < 80:
            recommendations.append("Review and optimize caching strategy")
        
        if latest_app.success_rate < 98:
            recommendations.append("Investigate and fix error sources")
        
        # General recommendations
        recommendations.extend([
            "Implement AI-powered performance monitoring and anomaly detection",
            "Optimize content delivery for multi-format creator platform",
            "Implement intelligent load balancing for creator content processing",
            "Use machine learning for predictive scaling of creator workloads"
        ])
        
        return recommendations
    
    def _get_alert_summary(self, hours_back: int) -> Dict[str, Any]:
        """Get alert summary for specified time period"""        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        period_alerts = [a for a in self.active_alerts if a.timestamp >= cutoff_time]
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([a for a in period_alerts if a.severity == severity])
        
        return {
            "total_alerts": len(period_alerts),
            "by_severity": severity_counts,
            "resolved_alerts": len([a for a in period_alerts if a.resolved]),
            "avg_resolution_time": self._calculate_avg_resolution_time(period_alerts)
        }
    
    def _predict_system_metrics(self, recent_metrics: List[SystemPerformance], 
                              hours_ahead: int) -> Dict[str, float]:
        """Predict system metrics using trend analysis"""        if len(recent_metrics) < 5:
            return {}
        
        # Extract time series data
        cpu_values = [m.cpu_usage for m in recent_metrics]
        memory_values = [m.memory_usage for m in recent_metrics]
        response_time_values = [m.response_time_avg for m in recent_metrics]
        
        # Professional linear prediction
        predictions = {}
        
        # Predict CPU usage
        x = np.arange(len(cpu_values))
        cpu_coeff = np.polyfit(x, cpu_values, 1)
        predictions["cpu_usage"] = max(0, min(100, cpu_coeff[0] * (len(cpu_values) + hours_ahead) + cpu_coeff[1]))
        
        # Predict memory usage
        memory_coeff = np.polyfit(x, memory_values, 1)
        predictions["memory_usage"] = max(0, min(100, memory_coeff[0] * (len(memory_values) + hours_ahead) + memory_coeff[1]))
        
        # Predict response time
        response_coeff = np.polyfit(x, response_time_values, 1)
        predictions["response_time_avg"] = max(0, response_coeff[0] * (len(response_time_values) + hours_ahead) + response_coeff[1])
        
        return predictions
    
    def _predict_application_metrics(self, recent_metrics: List[ApplicationPerformance], 
                                   hours_ahead: int) -> Dict[str, float]:
        """Predict application metrics using trend analysis"""        if len(recent_metrics) < 5:
            return {}
        
        # Extract time series data
        p95_values = [m.response_time_p95 for m in recent_metrics]
        error_counts = [m.error_count for m in recent_metrics]
        request_counts = [m.request_count for m in recent_metrics]
        
        # Professional linear prediction
        predictions = {}
        
        # Predict response time P95
        x = np.arange(len(p95_values))
        p95_coeff = np.polyfit(x, p95_values, 1)
        predictions["response_time_p95"] = max(0, p95_coeff[0] * (len(p95_values) + hours_ahead) + p95_coeff[1])
        
        # Predict error rate
        error_coeff = np.polyfit(x, error_counts, 1)
        predicted_errors = max(0, error_coeff[0] * (len(error_counts) + hours_ahead) + error_coeff[1])
        
        # Predict request count
        request_coeff = np.polyfit(x, request_counts, 1)
        predicted_requests = max(1, request_coeff[0] * (len(request_counts) + hours_ahead) + request_coeff[1])
        
        predictions["error_rate"] = (predicted_errors / predicted_requests) * 100
        
        return predictions
    
    def _suggest_preventive_actions(self, potential_issues: List[Dict[str, Any]]) -> List[str]:
        """Suggest preventive actions for potential issues"""        actions = []
        
        for issue in potential_issues:
            if "CPU usage" in issue["issue"]:
                actions.append("Scale out application instances or optimize CPU-intensive processes")
            elif "Memory exhaustion" in issue["issue"]:
                actions.append("Increase memory allocation or investigate memory leaks")
            elif "Response time" in issue["issue"]:
                actions.append("Optimize database queries and implement additional caching layers")
            elif "error rate" in issue["issue"]:
                actions.append("Review recent code deployments and enhance error handling")
        
        # General preventive actions
        actions.extend([
            "Enable auto-scaling policies for anticipated load increases",
            "Implement circuit breakers for external service dependencies",
            "Prepare rollback procedures for rapid issue resolution"
        ])
        
        return actions
    
    def _calculate_system_summary(self, system_metrics: List[SystemPerformance]) -> Dict[str, Any]:
        """Calculate system performance summary statistics"""        cpu_values = [m.cpu_usage for m in system_metrics]
        memory_values = [m.memory_usage for m in system_metrics]
        response_times = [m.response_time_avg for m in system_metrics]
        
        return {
            "cpu_usage": {
                "min": min(cpu_values),
                "max": max(cpu_values),
                "avg": np.mean(cpu_values),
                "p95": np.percentile(cpu_values, 95)
            },
            "memory_usage": {
                "min": min(memory_values),
                "max": max(memory_values),
                "avg": np.mean(memory_values),
                "p95": np.percentile(memory_values, 95)
            },
            "response_time": {
                "min": min(response_times),
                "max": max(response_times),
                "avg": np.mean(response_times),
                "p95": np.percentile(response_times, 95)
            }
        }
    
    def _calculate_application_summary(self, app_metrics: List[ApplicationPerformance]) -> Dict[str, Any]:
        """Calculate application performance summary statistics"""        request_counts = [m.request_count for m in app_metrics]
        p95_response_times = [m.response_time_p95 for m in app_metrics]
        success_rates = [m.success_rate for m in app_metrics]
        
        return {
            "request_volume": {
                "total": sum(request_counts),
                "avg_per_period": np.mean(request_counts),
                "peak": max(request_counts)
            },
            "response_time_p95": {
                "min": min(p95_response_times),
                "max": max(p95_response_times),
                "avg": np.mean(p95_response_times)
            },
            "success_rate": {
                "min": min(success_rates),
                "avg": np.mean(success_rates),
                "uptime_percentage": np.mean(success_rates)
            }
        }
    
    def _generate_performance_highlights(self, system_metrics: List[SystemPerformance], 
                                       app_metrics: List[ApplicationPerformance]) -> List[str]:
        """Generate performance highlights"""        highlights = []
        
        # System highlights
        avg_cpu = np.mean([m.cpu_usage for m in system_metrics])
        if avg_cpu < 50:
            highlights.append(f"Excellent CPU utilization averaging {avg_cpu:.1f}%")
        
        # Application highlights
        avg_success_rate = np.mean([m.success_rate for m in app_metrics])
        if avg_success_rate > 99:
            highlights.append(f"Outstanding service reliability at {avg_success_rate:.2f}% success rate")
        
        # Response time highlights
        avg_p95 = np.mean([m.response_time_p95 for m in app_metrics])
        if avg_p95 < 300:
            highlights.append(f"Excellent response performance with P95 at {avg_p95:.0f}ms")
        
        return highlights
    
    def _calculate_sla_compliance(self, system_metrics: List[SystemPerformance], 
                                app_metrics: List[ApplicationPerformance]) -> Dict[str, Any]:
        """Calculate SLA compliance metrics"""        # Define SLA thresholds
        sla_thresholds = {
            "availability": 99.5,
            "response_time_p95": 500,
            "success_rate": 99.0
        }
        
        # Calculate compliance
        availability_compliance = len([m for m in system_metrics if m.availability >= sla_thresholds["availability"]]) / len(system_metrics) * 100
        
        response_time_compliance = len([m for m in app_metrics if m.response_time_p95 <= sla_thresholds["response_time_p95"]]) / len(app_metrics) * 100
        
        success_rate_compliance = len([m for m in app_metrics if m.success_rate >= sla_thresholds["success_rate"]]) / len(app_metrics) * 100
        
        return {
            "overall_compliance": (availability_compliance + response_time_compliance + success_rate_compliance) / 3,
            "availability_compliance": availability_compliance,
            "response_time_compliance": response_time_compliance,
            "success_rate_compliance": success_rate_compliance,
            "sla_breaches": self._identify_sla_breaches(system_metrics, app_metrics, sla_thresholds)
        }
    
    def _analyze_performance_costs(self, system_metrics: List[SystemPerformance], 
                                 app_metrics: List[ApplicationPerformance]) -> Dict[str, Any]:
        """Analyze performance-related costs"""        # Simulated cost analysis based on resource usage
        avg_cpu = np.mean([m.cpu_usage for m in system_metrics])
        avg_memory = np.mean([m.memory_usage for m in system_metrics])
        total_requests = sum([m.request_count for m in app_metrics])
        
        # Estimated costs (simplified)
        compute_cost = (avg_cpu * 0.1 + avg_memory * 0.05) * len(system_metrics)
        bandwidth_cost = total_requests * 0.001
        storage_cost = avg_memory * 0.02 * len(system_metrics)
        
        total_cost = compute_cost + bandwidth_cost + storage_cost
        
        return {
            "total_estimated_cost": total_cost,
            "cost_breakdown": {
                "compute": compute_cost,
                "bandwidth": bandwidth_cost,
                "storage": storage_cost
            },
            "cost_per_request": total_cost / max(total_requests, 1),
            "optimization_potential": self._calculate_cost_optimization_potential(avg_cpu, avg_memory)
        }
    
    def _assess_overall_health(self, system_perf: SystemPerformance, 
                             app_perf: ApplicationPerformance) -> str:
        """Assess overall system health"""        performance_score = self._calculate_performance_score(system_perf, app_perf)
        
        if performance_score >= 85:
            return "excellent"
        elif performance_score >= 70:
            return "good"
        elif performance_score >= 55:
            return "fair"
        elif performance_score >= 40:
            return "poor"
        else:
            return "critical"
    
    def _extract_key_metrics(self, system_perf: SystemPerformance, 
                           app_perf: ApplicationPerformance) -> Dict[str, float]:
        """Extract key performance metrics"""        return {
            "cpu_usage": system_perf.cpu_usage,
            "memory_usage": system_perf.memory_usage,
            "response_time_avg": system_perf.response_time_avg,
            "response_time_p95": app_perf.response_time_p95,
            "success_rate": app_perf.success_rate,
            "request_count": app_perf.request_count,
            "cache_hit_rate": app_perf.cache_hit_rate
        }
    
    def _determine_performance_trend(self, system_metrics: List[SystemPerformance], 
                                   app_metrics: List[ApplicationPerformance]) -> str:
        """Determine overall performance trend"""        if len(system_metrics) < 3 or len(app_metrics) < 3:
            return "stable"
        
        # Calculate performance scores for trend analysis
        scores = []
        for i in range(min(len(system_metrics), len(app_metrics))):
            score = self._calculate_performance_score(system_metrics[i], app_metrics[i])
            scores.append(score)
        
        trend = self._calculate_trend(scores)
        return trend
    
    def _analyze_alerts(self, alerts: List[PerformanceAlert]) -> Dict[str, Any]:
        """Analyze alert patterns and statistics"""        if not alerts:
            return {"total": 0}
        
        severity_distribution = {}
        for severity in AlertSeverity:
            severity_distribution[severity.value] = len([a for a in alerts if a.severity == severity])
        
        resolved_count = len([a for a in alerts if a.resolved])
        avg_resolution_time = self._calculate_avg_resolution_time(alerts)
        
        # Most frequent alert types
        alert_types = {}
        for alert in alerts:
            alert_types[alert.metric_name] = alert_types.get(alert.metric_name, 0) + 1
        
        most_frequent = sorted(alert_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total": len(alerts),
            "severity_distribution": severity_distribution,
            "resolved": resolved_count,
            "resolution_rate": resolved_count / len(alerts) * 100,
            "avg_resolution_time_minutes": avg_resolution_time,
            "most_frequent_types": most_frequent
        }
    
    def _generate_comprehensive_recommendations(self, system_metrics: List[SystemPerformance], 
                                              app_metrics: List[ApplicationPerformance]) -> List[Dict[str, Any]]:
        """Generate comprehensive performance recommendations"""        recommendations = []
        
        latest_system = system_metrics[-1]
        latest_app = app_metrics[-1]
        
        # High-priority recommendations
        if latest_system.cpu_usage > 85:
            recommendations.append({
                "priority": "high",
                "category": "scaling",
                "recommendation": "Implement horizontal auto-scaling for CPU-intensive workloads",
                "expected_impact": "Reduce CPU bottlenecks and improve response times",
                "implementation_effort": "medium"
            })
        
        if latest_app.cache_hit_rate < 75:
            recommendations.append({
                "priority": "high",
                "category": "optimization",
                "recommendation": "Optimize caching strategy and cache key design",
                "expected_impact": "Reduce database load and improve response times",
                "implementation_effort": "low"
            })
        
        # Medium-priority recommendations
        if latest_app.response_time_p95 > 400:
            recommendations.append({
                "priority": "medium",
                "category": "optimization",
                "recommendation": "Implement database query optimization and indexing",
                "expected_impact": "Improve response times and user experience",
                "implementation_effort": "medium"
            })
        
        # AI/ML specific recommendations
        recommendations.append({
            "priority": "medium",
            "category": "ai_optimization",
            "recommendation": "Implement AI-powered content processing optimization for creator platform",
            "expected_impact": "Optimize resource usage for multi-format content processing",
            "implementation_effort": "high"
        })
        
        return recommendations
    
    def _optimize_response_time(self, system_perf: SystemPerformance, 
                               app_perf: ApplicationPerformance) -> List[Dict[str, Any]]:
        """Generate response time optimization strategies"""        strategies = []
        
        if app_perf.cache_hit_rate < 80:
            strategies.append({
                "strategy": "Implement enterprise caching layers",
                "impact": "20-40% response time improvement",
                "effort": "medium",
                "timeline": "2-3 weeks"
            })
        
        if app_perf.response_time_p95 > 500:
            strategies.append({
                "strategy": "Database query optimization and indexing",
                "impact": "30-50% response time improvement",
                "effort": "high",
                "timeline": "4-6 weeks"
            })
        
        strategies.append({
            "strategy": "Implement AI-powered content optimization for faster delivery",
            "impact": "25-35% improvement for content-heavy operations",
            "effort": "high",
            "timeline": "6-8 weeks"
        })
        
        return strategies
    
    def _optimize_throughput(self, system_perf: SystemPerformance, 
                           app_perf: ApplicationPerformance) -> List[Dict[str, Any]]:
        """Generate throughput optimization strategies"""        strategies = []
        
        if system_perf.cpu_usage > 70:
            strategies.append({
                "strategy": "Implement horizontal scaling with load balancing",
                "impact": "2-3x throughput increase",
                "effort": "medium",
                "timeline": "3-4 weeks"
            })
        
        if app_perf.active_connections > 300:
            strategies.append({
                "strategy": "Connection pooling and async processing optimization",
                "impact": "40-60% throughput improvement",
                "effort": "medium",
                "timeline": "2-3 weeks"
            })
        
        return strategies
    
    def _optimize_resources(self, system_perf: SystemPerformance, 
                          app_perf: ApplicationPerformance) -> List[Dict[str, Any]]:
        """Generate resource optimization strategies"""        strategies = []
        
        if system_perf.memory_usage > 80:
            strategies.append({
                "strategy": "Memory usage optimization and leak detection",
                "impact": "20-30% memory reduction",
                "effort": "medium",
                "timeline": "2-4 weeks"
            })
        
        if system_perf.cpu_usage < 30:
            strategies.append({
                "strategy": "Right-size instances to reduce over-provisioning",
                "impact": "25-40% cost reduction",
                "effort": "low",
                "timeline": "1-2 weeks"
            })
        
        return strategies
    
    def _optimize_costs(self, system_perf: SystemPerformance, 
                       app_perf: ApplicationPerformance) -> List[Dict[str, Any]]:
        """Generate cost optimization strategies"""        strategies = []
        
        strategies.append({
            "strategy": "Implement intelligent auto-scaling based on workload patterns",
            "impact": "15-25% infrastructure cost reduction",
            "effort": "medium",
            "timeline": "3-4 weeks"
        })
        
        if system_perf.cpu_usage < 40:
            strategies.append({
                "strategy": "Consolidate workloads and optimize resource allocation",
                "impact": "20-35% cost reduction",
                "effort": "high",
                "timeline": "4-6 weeks"
            })
        
        return strategies
    
    def _general_optimization(self, system_perf: SystemPerformance, 
                            app_perf: ApplicationPerformance) -> List[Dict[str, Any]]:
        """Generate general optimization strategies"""        strategies = []
        
        strategies.extend([
            {
                "strategy": "Implement comprehensive monitoring and alerting system",
                "impact": "Proactive issue detection and faster resolution",
                "effort": "medium",
                "timeline": "2-3 weeks"
            },
            {
                "strategy": "AI-powered performance anomaly detection for creator platform",
                "impact": "Early detection of performance issues specific to content processing",
                "effort": "high",
                "timeline": "6-8 weeks"
            },
            {
                "strategy": "Optimize multi-format content processing pipeline",
                "impact": "Improved efficiency for creator content workflows",
                "effort": "high",
                "timeline": "4-6 weeks"
            }
        ])
        
        return strategies
    
    def _generate_tuning_recommendations(self) -> List[str]:
        """Generate performance tuning recommendations"""        return [
            "Fine-tune JVM garbage collection parameters for better memory management",
            "Optimize database connection pool settings for peak load handling",
            "Configure CDN caching rules for optimal content delivery performance",
            "Implement intelligent request routing for geographic performance optimization",
            "Optimize AI model inference performance for real-time content processing"
        ]
    
    def _generate_scaling_suggestions(self, system_perf: SystemPerformance, 
                                    app_perf: ApplicationPerformance) -> Dict[str, Any]:
        """Generate infrastructure scaling suggestions"""        suggestions = {
            "immediate_scaling": [],
            "planned_scaling": [],
            "scaling_triggers": []
        }
        
        # Immediate scaling needs
        if system_perf.cpu_usage > 85:
            suggestions["immediate_scaling"].append("Scale out application servers immediately")
        
        if system_perf.memory_usage > 90:
            suggestions["immediate_scaling"].append("Increase memory allocation or add instances")
        
        # Planned scaling
        if app_perf.request_count > 1500:
            suggestions["planned_scaling"].append("Plan for additional capacity for growing request volume")
        
        # Scaling triggers
        suggestions["scaling_triggers"] = [
            "CPU usage > 75% for 10 minutes",
            "Response time P95 > 800ms for 5 minutes",
            "Memory usage > 85% for 15 minutes",
            "Error rate > 2% for 5 minutes"
        ]
        
        return suggestions
    
    def _estimate_optimization_impact(self, strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate the impact of optimization strategies"""        return {
            "performance_improvement": "25-45% overall performance gain expected",
            "cost_reduction": "15-30% infrastructure cost savings",
            "reliability_improvement": "99.9% to 99.95% availability improvement",
            "user_experience": "40-60% faster response times for content operations"
        }
    
    def _prioritize_optimizations(self, strategies: List[Dict[str, Any]]) -> List[str]:
        """Prioritize optimization strategies"""        return [
            "Critical performance bottlenecks (immediate impact)",
            "Resource optimization (cost savings)",
            "Scalability improvements (future growth)",
            "Enterprise monitoring and AI optimization (long-term benefits)"
        ]
    
    def _serialize_system_performance(self, system_perf: SystemPerformance) -> Dict[str, float]:
        """Serialize system performance for output"""        return {
            "cpu_usage": system_perf.cpu_usage,
            "memory_usage": system_perf.memory_usage,
            "disk_usage": system_perf.disk_usage,
            "network_io": system_perf.network_io,
            "response_time_avg": system_perf.response_time_avg,
            "availability": system_perf.availability
        }
    
    def _serialize_application_performance(self, app_perf: ApplicationPerformance) -> Dict[str, Any]:
        """Serialize application performance for output"""        return {
            "request_count": app_perf.request_count,
            "response_time_p95": app_perf.response_time_p95,
            "success_rate": app_perf.success_rate,
            "cache_hit_rate": app_perf.cache_hit_rate,
            "active_connections": app_perf.active_connections
        }
    
    def _calculate_avg_resolution_time(self, alerts: List[PerformanceAlert]) -> float:
        """Calculate average alert resolution time in minutes"""        resolved_alerts = [a for a in alerts if a.resolved and a.resolution_time]
        if not resolved_alerts:
            return 0.0
        
        total_resolution_time = sum(
            (a.resolution_time - a.timestamp).total_seconds() / 60 
            for a in resolved_alerts
        )
        
        return total_resolution_time / len(resolved_alerts)
    
    def _identify_sla_breaches(self, system_metrics: List[SystemPerformance], 
                             app_metrics: List[ApplicationPerformance], 
                             sla_thresholds: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify SLA breaches"""        breaches = []
        
        for system_metric in system_metrics:
            if system_metric.availability < sla_thresholds["availability"]:
                breaches.append({
                    "timestamp": system_metric.timestamp.isoformat(),
                    "type": "availability",
                    "value": system_metric.availability,
                    "threshold": sla_thresholds["availability"]
                })
        
        for app_metric in app_metrics:
            if app_metric.response_time_p95 > sla_thresholds["response_time_p95"]:
                breaches.append({
                    "timestamp": app_metric.timestamp.isoformat(),
                    "type": "response_time",
                    "value": app_metric.response_time_p95,
                    "threshold": sla_thresholds["response_time_p95"]
                })
        
        return breaches
    
    def _calculate_cost_optimization_potential(self, avg_cpu: float, avg_memory: float) -> Dict[str, Any]:
        """Calculate cost optimization potential"""        cpu_optimization = max(0, (70 - avg_cpu) / 70 * 100) if avg_cpu < 70 else 0
        memory_optimization = max(0, (80 - avg_memory) / 80 * 100) if avg_memory < 80 else 0
        
        return {
            "cpu_right_sizing_potential": f"{cpu_optimization:.1f}%",
            "memory_right_sizing_potential": f"{memory_optimization:.1f}%",
            "estimated_monthly_savings": f"${(cpu_optimization + memory_optimization) * 10:.2f}",
            "optimization_recommendation": "Consider right-sizing instances based on actual usage patterns"
        }
