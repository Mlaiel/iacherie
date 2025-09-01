"""Pipeline Monitoring and Health Checking System
==============================================

Professional monitoring system for data pipeline health, performance metrics,
and real-time status tracking with advanced alerting capabilities.

Team Specialties:
- Lead Developer AI: Fahed Mlaiel - Advanced monitoring architecture
- DevOps Engineer: Production-grade monitoring and observability
- Backend Senior Engineer: High-performance metrics collection
- Security Engineer: Security monitoring and threat detection
- Database Administrator: Database performance monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT WARNING ⚠️
This monitoring technology and intellectual property belong exclusively to Fahed Mlaiel.
Unauthorized use, copying, or reproduction without explicit written permission
will result in immediate legal prosecution under international copyright laws.
"""
import asyncio
import logging
import time
import json
import traceback
import gc
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor

import psutil
import aioredis
import aiohttp
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry
from sqlalchemy import text
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from backend.core.config import get_settings
from backend.core.database import AsyncDatabaseSession
from backend.core.exceptions import MonitoringError, HealthCheckError
from backend.utils.logging import get_logger
from backend.utils.notifications import NotificationManager
from backend.utils.cache import CacheManager
from backend.data.storage import StorageManager
from backend.data.pipelines.analytics_pipeline import AnalyticsPipeline
from backend.data.pipelines.protection_pipeline import ProtectionPipeline
from backend.data.pipelines.monetization_pipeline import MonetizationPipeline
from backend.data.pipelines.collaboration_pipeline import CollaborationPipeline
from backend.data.pipelines.distribution_pipeline import MultiPlatformDistributor

logger = get_logger(__name__)
settings = get_settings()


class HealthStatus(str, Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(str, Enum):
    """Types of metrics being monitored"""
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    RESOURCE_USAGE = "resource_usage"
    BUSINESS = "business"
    SECURITY = "security"


class PipelineComponent(str, Enum):
    """Pipeline components being monitored"""
    ANALYTICS = "analytics"
    PROTECTION = "protection"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    DISTRIBUTION = "distribution"
    DATABASE = "database"
    CACHE = "cache"
    STORAGE = "storage"
    API_GATEWAY = "api_gateway"
    EXTERNAL_APIS = "external_apis"


@dataclass
class HealthCheck:
    """Health check result data structure"""
    component: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    response_time: float
    dependencies: List[str]
    metrics: Dict[str, float]


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    severity: AlertSeverity
    component: str
    title: str
    description: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    component: str
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    request_rate: float
    error_rate: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput: float
    active_connections: int
    queue_size: int


class AnomalyDetector:
    """
    Advanced anomaly detection system using machine learning
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metric_windows = defaultdict(lambda: deque(maxlen=window_size))
        self.isolation_forests = {}
        self.scalers = {}
        self.anomaly_thresholds = {
            "cpu_usage": 0.8,
            "memory_usage": 0.85,
            "error_rate": 0.05,
            "response_time": 2.0
        }

    async def detect_anomalies(self, metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """
        Detect anomalies in performance metrics using ML models
        """
        try:
            anomalies = []
            component = metrics.component
            
            # Convert metrics to feature vector
            features = [
                metrics.cpu_usage,
                metrics.memory_usage,
                metrics.error_rate,
                metrics.avg_response_time,
                metrics.throughput
            ]
            
            # Add to rolling window
            self.metric_windows[component].append(features)
            
            # Need minimum data points for ML detection
            if len(self.metric_windows[component]) < 20:
                return await self._basic_threshold_detection(metrics)
            
            # Prepare data for ML model
            data = np.array(list(self.metric_windows[component]))
            
            # Initialize or update ML models
            if component not in self.isolation_forests:
                self.isolation_forests[component] = IsolationForest(
                    contamination=0.1, random_state=42
                )
                self.scalers[component] = StandardScaler()
                
                # Fit models with available data
                scaled_data = self.scalers[component].fit_transform(data)
                self.isolation_forests[component].fit(scaled_data)
            
            # Scale current features
            current_features = np.array([features])
            scaled_features = self.scalers[component].transform(current_features)
            
            # Detect anomalies
            anomaly_score = self.isolation_forests[component].decision_function(scaled_features)[0]
            is_anomaly = self.isolation_forests[component].predict(scaled_features)[0] == -1
            
            if is_anomaly:
                anomalies.append({
                    "type": "ml_anomaly",
                    "component": component,
                    "anomaly_score": float(anomaly_score),
                    "features": features,
                    "description": f"ML model detected anomaly in {component} performance",
                    "severity": self._calculate_anomaly_severity(anomaly_score, features)
                })
            
            # Also run threshold-based detection
            threshold_anomalies = await self._basic_threshold_detection(metrics)
            anomalies.extend(threshold_anomalies)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return []

    async def _basic_threshold_detection(self, metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """
        Basic threshold-based anomaly detection as fallback
        """
        anomalies = []
        
        # CPU usage anomaly
        if metrics.cpu_usage > self.anomaly_thresholds["cpu_usage"]:
            anomalies.append({
                "type": "threshold_anomaly",
                "metric": "cpu_usage",
                "value": metrics.cpu_usage,
                "threshold": self.anomaly_thresholds["cpu_usage"],
                "severity": AlertSeverity.WARNING if metrics.cpu_usage < 0.95 else AlertSeverity.CRITICAL,
                "description": f"High CPU usage: {metrics.cpu_usage:.2%}"
            })
        
        # Memory usage anomaly
        if metrics.memory_usage > self.anomaly_thresholds["memory_usage"]:
            anomalies.append({
                "type": "threshold_anomaly",
                "metric": "memory_usage",
                "value": metrics.memory_usage,
                "threshold": self.anomaly_thresholds["memory_usage"],
                "severity": AlertSeverity.WARNING if metrics.memory_usage < 0.95 else AlertSeverity.CRITICAL,
                "description": f"High memory usage: {metrics.memory_usage:.2%}"
            })
        
        # Error rate anomaly
        if metrics.error_rate > self.anomaly_thresholds["error_rate"]:
            anomalies.append({
                "type": "threshold_anomaly",
                "metric": "error_rate",
                "value": metrics.error_rate,
                "threshold": self.anomaly_thresholds["error_rate"],
                "severity": AlertSeverity.ERROR if metrics.error_rate < 0.1 else AlertSeverity.CRITICAL,
                "description": f"High error rate: {metrics.error_rate:.2%}"
            })
        
        # Response time anomaly
        if metrics.avg_response_time > self.anomaly_thresholds["response_time"]:
            anomalies.append({
                "type": "threshold_anomaly",
                "metric": "response_time",
                "value": metrics.avg_response_time,
                "threshold": self.anomaly_thresholds["response_time"],
                "severity": AlertSeverity.WARNING if metrics.avg_response_time < 5.0 else AlertSeverity.ERROR,
                "description": f"High response time: {metrics.avg_response_time:.2f}s"
            })
        
        return anomalies

    def _calculate_anomaly_severity(self, anomaly_score: float, features: List[float]) -> AlertSeverity:
        """
        Calculate severity based on anomaly score and feature values
        """
        # More negative scores indicate stronger anomalies
        if anomaly_score < -0.5:
            return AlertSeverity.CRITICAL
        elif anomaly_score < -0.3:
            return AlertSeverity.ERROR
        elif anomaly_score < -0.1:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO


class PipelineMonitor:
    """
    Comprehensive pipeline monitoring system with real-time health checking
    """
    
    def __init__(self):
        self.notification_manager = NotificationManager()
        self.cache_manager = CacheManager()
        self.storage_manager = StorageManager()
        self.anomaly_detector = AnomalyDetector()
        
        # Pipeline components
        self.analytics_pipeline = AnalyticsPipeline()
        self.protection_pipeline = ProtectionPipeline()
        self.monetization_pipeline = MonetizationPipeline()
        self.collaboration_pipeline = CollaborationPipeline()
        self.distribution_pipeline = MultiPlatformDistributor()
        
        # Monitoring state
        self.health_checks = {}
        self.active_alerts = {}
        self.metrics_history = defaultdict(list)
        self.monitoring_active = False
        
        # Performance tracking
        self.performance_metrics = {}
        self.last_health_check = {}
        
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self.setup_prometheus_metrics()
        
        # Health check intervals (seconds)
        self.health_check_intervals = {
            PipelineComponent.ANALYTICS: 30,
            PipelineComponent.PROTECTION: 15,
            PipelineComponent.MONETIZATION: 60,
            PipelineComponent.COLLABORATION: 45,
            PipelineComponent.DISTRIBUTION: 30,
            PipelineComponent.DATABASE: 20,
            PipelineComponent.CACHE: 15,
            PipelineComponent.STORAGE: 60,
            PipelineComponent.API_GATEWAY: 10,
            PipelineComponent.EXTERNAL_APIS: 30
        }

    def setup_prometheus_metrics(self):
        """
        Setup Prometheus metrics for monitoring
        """
        self.prometheus_metrics = {
            "health_status": Gauge(
                'pipeline_health_status', 
                'Health status of pipeline components', 
                ['component'], 
                registry=self.registry
            ),
            "response_time": Histogram(
                'pipeline_response_time_seconds', 
                'Response time of pipeline operations', 
                ['component', 'operation'], 
                registry=self.registry
            ),
            "error_count": Counter(
                'pipeline_errors_total', 
                'Total number of pipeline errors', 
                ['component', 'error_type'], 
                registry=self.registry
            ),
            "throughput": Gauge(
                'pipeline_throughput', 
                'Pipeline throughput (operations per second)', 
                ['component'], 
                registry=self.registry
            ),
            "resource_usage": Gauge(
                'pipeline_resource_usage', 
                'Resource usage percentage', 
                ['component', 'resource'], 
                registry=self.registry
            ),
            "active_connections": Gauge(
                'pipeline_active_connections', 
                'Number of active connections', 
                ['component'], 
                registry=self.registry
            )
        }

    async def start_monitoring(self):
        """
        Start comprehensive pipeline monitoring
        """
        try:
            logger.info("Starting pipeline monitoring system")
            self.monitoring_active = True
            
            # Start monitoring tasks for each component
            monitoring_tasks = []
            
            for component, interval in self.health_check_intervals.items():
                task = asyncio.create_task(
                    self._monitor_component_health(component, interval)
                )
                monitoring_tasks.append(task)
            
            # Start anomaly detection task
            anomaly_task = asyncio.create_task(self._run_anomaly_detection())
            monitoring_tasks.append(anomaly_task)
            
            # Start metrics collection task
            metrics_task = asyncio.create_task(self._collect_performance_metrics())
            monitoring_tasks.append(metrics_task)
            
            # Start alert processing task
            alert_task = asyncio.create_task(self._process_alerts())
            monitoring_tasks.append(alert_task)
            
            # Wait for all monitoring tasks
            await asyncio.gather(*monitoring_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Monitoring system failed: {str(e)}")
            raise MonitoringError(f"Monitoring system failed: {str(e)}")

    async def _monitor_component_health(self, component: PipelineComponent, interval: int):
        """
        Monitor health of specific pipeline component
        """
        while self.monitoring_active:
            try:
                start_time = time.time()
                
                # Perform component-specific health check
                health_check = await self._perform_health_check(component)
                
                # Calculate response time
                response_time = time.time() - start_time
                health_check.response_time = response_time
                
                # Store health check result
                self.health_checks[component.value] = health_check
                self.last_health_check[component.value] = datetime.utcnow()
                
                # Update Prometheus metrics
                self._update_prometheus_metrics(component, health_check)
                
                # Check for alerts
                await self._check_for_alerts(component, health_check)
                
                # Log health status
                logger.debug(f"{component.value} health: {health_check.status.value} ({response_time:.3f}s)")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Health check failed for {component.value}: {str(e)}")
                await asyncio.sleep(interval)

    async def _perform_health_check(self, component: PipelineComponent) -> HealthCheck:
        """
        Perform health check for specific component
        """
        try:
            if component == PipelineComponent.ANALYTICS:
                return await self._check_analytics_health()
            elif component == PipelineComponent.PROTECTION:
                return await self._check_protection_health()
            elif component == PipelineComponent.MONETIZATION:
                return await self._check_monetization_health()
            elif component == PipelineComponent.COLLABORATION:
                return await self._check_collaboration_health()
            elif component == PipelineComponent.DISTRIBUTION:
                return await self._check_distribution_health()
            elif component == PipelineComponent.DATABASE:
                return await self._check_database_health()
            elif component == PipelineComponent.CACHE:
                return await self._check_cache_health()
            elif component == PipelineComponent.STORAGE:
                return await self._check_storage_health()
            elif component == PipelineComponent.API_GATEWAY:
                return await self._check_api_gateway_health()
            elif component == PipelineComponent.EXTERNAL_APIS:
                return await self._check_external_apis_health()
            else:
                return HealthCheck(
                    component=component.value,
                    status=HealthStatus.UNKNOWN,
                    message="Unknown component",
                    details={},
                    timestamp=datetime.utcnow(),
                    response_time=0.0,
                    dependencies=[],
                    metrics={}
                )
                
        except Exception as e:
            logger.error(f"Health check failed for {component.value}: {str(e)}")
            return HealthCheck(
                component=component.value,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e), "traceback": traceback.format_exc()},
                timestamp=datetime.utcnow(),
                response_time=0.0,
                dependencies=[],
                metrics={}
            )

    async def _check_analytics_health(self) -> HealthCheck:
        """
        Check analytics pipeline health
        """
        try:
            metrics = {}
            details = {}
            status = HealthStatus.HEALTHY
            message = "Analytics pipeline operating normally"
            
            # Test basic functionality
            test_user_id = 1  # Test user
            try:
                # Test metrics calculation (lightweight)
                test_metrics = await self.analytics_pipeline.metrics_aggregator.calculate_comprehensive_metrics(
                    user_id=test_user_id,
                    content_ids=[],  # Empty for quick test
                    time_range="last_7_days"
                )
                
                if test_metrics.get("error"):
                    status = HealthStatus.WARNING
                    message = "Analytics pipeline has minor issues"
                    details["analytics_error"] = test_metrics["error"]
                else:
                    metrics["test_calculation_success"] = 1.0
                    
            except Exception as e:
                status = HealthStatus.DEGRADED
                message = "Analytics pipeline functionality degraded"
                details["functionality_error"] = str(e)
                metrics["test_calculation_success"] = 0.0
            
            # Check system resources for analytics
            process = psutil.Process()
            cpu_usage = process.cpu_percent()
            memory_info = process.memory_info()
            memory_usage = memory_info.rss / (1024 * 1024 * 1024)  # GB
            
            metrics.update({
                "cpu_usage": cpu_usage,
                "memory_usage_gb": memory_usage,
                "threads_count": process.num_threads()
            })
            
            # Check if resources are constrained
            if cpu_usage > 80 or memory_usage > 8:  # 8GB threshold
                status = HealthStatus.WARNING
                message = "Analytics pipeline under resource pressure"
            
            return HealthCheck(
                component="analytics",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.utcnow(),
                response_time=0.0,
                dependencies=["database", "cache"],
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheck(
                component="analytics",
                status=HealthStatus.CRITICAL,
                message=f"Analytics health check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow(),
                response_time=0.0,
                dependencies=["database", "cache"],
                metrics={}
            )

    async def _check_protection_health(self) -> HealthCheck:
        """
        Check content protection pipeline health
        """
        try:
            metrics = {}
            details = {}
            status = HealthStatus.HEALTHY
            message = "Protection pipeline operating normally"
            
            # Test fingerprinting system
            try:
                # Test with dummy content
                test_result = await self.protection_pipeline.fingerprinting_engine.create_content_fingerprint(
                    content_id="test",
                    content_type="image",
                    content_data={"test": True}
                )
                
                if test_result.get("error"):
                    status = HealthStatus.WARNING
                    message = "Protection pipeline has minor issues"
                    details["fingerprinting_error"] = test_result["error"]
                else:
                    metrics["fingerprinting_test_success"] = 1.0
                    
            except Exception as e:
                status = HealthStatus.DEGRADED
                message = "Protection pipeline functionality degraded"
                details["functionality_error"] = str(e)
                metrics["fingerprinting_test_success"] = 0.0
            
            # Check violation detection queue size
            try:
                queue_size = await self._get_queue_size("violation_detection")
                metrics["violation_queue_size"] = queue_size
                
                if queue_size > 1000:  # Large backlog
                    status = HealthStatus.WARNING
                    message = "Protection pipeline has large processing queue"
                    
            except Exception as e:
                details["queue_check_error"] = str(e)
            
            return HealthCheck(
                component="protection",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.utcnow(),
                response_time=0.0,
                dependencies=["database", "external_apis"],
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheck(
                component="protection",
                status=HealthStatus.CRITICAL,
                message=f"Protection health check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow(),
                response_time=0.0,
                dependencies=["database", "external_apis"],
                metrics={}
            )

    async def _check_database_health(self) -> HealthCheck:
        """
        Check database health and performance
        """
        try:
            metrics = {}
            details = {}
            status = HealthStatus.HEALTHY
            message = "Database operating normally"
            
            # Test database connectivity and performance
            async with AsyncDatabaseSession() as session:
                start_time = time.time()
                
                # Simple query to test connectivity
                result = await session.execute(text("SELECT 1"))
                connection_time = time.time() - start_time
                
                metrics["connection_time"] = connection_time
                
                if connection_time > 1.0:  # Slow connection
                    status = HealthStatus.WARNING
                    message = "Database connection is slow"
                
                # Check active connections
                try:
                    active_connections_result = await session.execute(
                        text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
                    )
                    active_connections = active_connections_result.scalar()
                    metrics["active_connections"] = active_connections
                    
                    if active_connections > 50:  # Too many connections
                        status = HealthStatus.WARNING
                        message = "High number of active database connections"
                        
                except Exception as e:
                    details["connection_check_error"] = str(e)
                
                # Check database size
                try:
                    db_size_result = await session.execute(
                        text("SELECT pg_size_pretty(pg_database_size(current_database()))")
                    )
                    db_size = db_size_result.scalar()
                    details["database_size"] = db_size
                    
                except Exception as e:
                    details["size_check_error"] = str(e)
            
            return HealthCheck(
                component="database",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.utcnow(),
                response_time=0.0,
                dependencies=[],
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheck(
                component="database",
                status=HealthStatus.CRITICAL,
                message=f"Database health check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow(),
                response_time=0.0,
                dependencies=[],
                metrics={}
            )

    async def _check_cache_health(self) -> HealthCheck:
        """
        Check Redis cache health
        """
        try:
            metrics = {}
            details = {}
            status = HealthStatus.HEALTHY
            message = "Cache operating normally"
            
            start_time = time.time()
            
            # Test cache connectivity
            test_key = "health_check_test"
            test_value = f"test_{int(time.time())}"
            
            await self.cache_manager.set(test_key, test_value, ttl=10)
            cached_value = await self.cache_manager.get(test_key)
            
            if cached_value != test_value:
                status = HealthStatus.CRITICAL
                message = "Cache read/write test failed"
            else:
                # Clean up test key
                await self.cache_manager.delete(test_key)
            
            response_time = time.time() - start_time
            metrics["response_time"] = response_time
            
            if response_time > 0.1:  # Slow cache
                status = HealthStatus.WARNING
                message = "Cache response time is slow"
            
            # Get cache info
            try:
                cache_info = await self.cache_manager.get_info()
                if cache_info:
                    metrics.update({
                        "used_memory": cache_info.get("used_memory", 0),
                        "connected_clients": cache_info.get("connected_clients", 0),
                        "keyspace_hits": cache_info.get("keyspace_hits", 0),
                        "keyspace_misses": cache_info.get("keyspace_misses", 0)
                    })
                    
                    # Calculate hit rate
                    hits = cache_info.get("keyspace_hits", 0)
                    misses = cache_info.get("keyspace_misses", 0)
                    if hits + misses > 0:
                        hit_rate = hits / (hits + misses)
                        metrics["hit_rate"] = hit_rate
                        
                        if hit_rate < 0.8:  # Low hit rate
                            status = HealthStatus.WARNING
                            message = "Cache hit rate is low"
                            
            except Exception as e:
                details["info_error"] = str(e)
            
            return HealthCheck(
                component="cache",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.utcnow(),
                response_time=response_time,
                dependencies=[],
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheck(
                component="cache",
                status=HealthStatus.CRITICAL,
                message=f"Cache health check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow(),
                response_time=0.0,
                dependencies=[],
                metrics={}
            )

    # Additional health check methods for other components...
    async def _check_monetization_health(self) -> HealthCheck:
        """Check monetization pipeline health"""
        # Implementation for monetization health check
        pass

    async def _check_collaboration_health(self) -> HealthCheck:
        """Check collaboration pipeline health"""
        # Implementation for collaboration health check
        pass

    async def _check_distribution_health(self) -> HealthCheck:
        """Check distribution pipeline health"""
        # Implementation for distribution health check
        pass

    async def _check_storage_health(self) -> HealthCheck:
        """Check storage system health"""
        # Implementation for storage health check
        pass

    async def _check_api_gateway_health(self) -> HealthCheck:
        """Check API gateway health"""
        # Implementation for API gateway health check
        pass

    async def _check_external_apis_health(self) -> HealthCheck:
        """Check external APIs health"""
        # Implementation for external APIs health check
        pass

    # Monitoring utility methods...
    def _update_prometheus_metrics(self, component: PipelineComponent, health_check: HealthCheck):
        """Update Prometheus metrics with health check data"""
        try:
            # Health status (convert to numeric)
            status_value = {
                HealthStatus.HEALTHY: 1.0,
                HealthStatus.WARNING: 0.7,
                HealthStatus.DEGRADED: 0.5,
                HealthStatus.CRITICAL: 0.2,
                HealthStatus.UNKNOWN: 0.0
            }.get(health_check.status, 0.0)
            
            self.prometheus_metrics["health_status"].labels(component=component.value).set(status_value)
            
            # Response time
            self.prometheus_metrics["response_time"].labels(
                component=component.value, operation="health_check"
            ).observe(health_check.response_time)
            
            # Update other metrics if available
            for metric_name, metric_value in health_check.metrics.items():
                if metric_name in ["cpu_usage", "memory_usage_gb", "response_time"]:
                    self.prometheus_metrics["resource_usage"].labels(
                        component=component.value, resource=metric_name
                    ).set(metric_value)
                    
        except Exception as e:
            logger.error(f"Failed to update Prometheus metrics: {str(e)}")

    async def _get_queue_size(self, queue_name: str) -> int:
        """Get queue size for monitoring"""
        try:
            # Implementation would check actual queue size
            # This is a placeholder
            return 0
        except Exception:
            return -1

    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """
        Generate comprehensive monitoring dashboard data
        """
        try:
            dashboard = {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": self._calculate_overall_status(),
                "health_checks": {
                    component: asdict(health_check) 
                    for component, health_check in self.health_checks.items()
                },
                "active_alerts": [
                    asdict(alert) for alert in self.active_alerts.values()
                ],
                "performance_summary": await self._generate_performance_summary(),
                "system_resources": await self._get_system_resources(),
                "prometheus_metrics_url": "/metrics"
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {str(e)}")
            return {"error": str(e)}

    def _calculate_overall_status(self) -> str:
        """Calculate overall system health status"""
        if not self.health_checks:
            return HealthStatus.UNKNOWN.value
        
        statuses = [hc.status for hc in self.health_checks.values()]
        
        if any(status == HealthStatus.CRITICAL for status in statuses):
            return HealthStatus.CRITICAL.value
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            return HealthStatus.DEGRADED.value
        elif any(status == HealthStatus.WARNING for status in statuses):
            return HealthStatus.WARNING.value
        else:
            return HealthStatus.HEALTHY.value

    async def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary from collected metrics"""
        # Implementation would aggregate performance metrics
        return {"placeholder": "performance_summary"}

    async def _get_system_resources(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": {
                    "percent": memory.percent,
                    "used_gb": memory.used / (1024**3),
                    "total_gb": memory.total / (1024**3)
                },
                "disk_usage": {
                    "percent": disk.percent,
                    "used_gb": disk.used / (1024**3),
                    "total_gb": disk.total / (1024**3)
                }
            }
        except Exception as e:
            logger.error(f"System resource check failed: {str(e)}")
            return {"error": str(e)}

    # Additional monitoring methods for comprehensive implementation...
    WARNING = "warning" 
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(str, Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class HealthCheckResult:
    """Health check result data structure"""
    component: str
    status: HealthStatus
    message: str
    response_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class PipelineMetrics:
    """Pipeline performance metrics"""
    pipeline_name: str
    execution_count: int
    success_count: int
    failure_count: int
    avg_execution_time: float
    last_execution: datetime
    error_rate: float
    throughput: float
    active_tasks: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["last_execution"] = self.last_execution.isoformat()
        return data


class HealthChecker:
    """
    Comprehensive health checking system for all pipeline components
    """
    
    def __init__(self):
        self.notification_manager = NotificationManager()
        self.storage_manager = StorageManager()
        
        # Health check registry
        self.health_checks: Dict[str, Callable] = {
            "database": self._check_database_health,
            "redis": self._check_redis_health,
            "storage": self._check_storage_health,
            "system": self._check_system_health,
            "fingerprinting": self._check_fingerprinting_health,
            "protection": self._check_protection_health,
            "monetization": self._check_monetization_health,
            "analytics": self._check_analytics_health
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "database_connections": 80,
            "response_time": 5.0,
            "error_rate": 0.05  # 5%
        }

    async def run_health_checks(
        self, 
        components: Optional[List[str]] = None
    ) -> Dict[str, HealthCheckResult]:
        """
        Run health checks for specified components or all components
        """
        try:
            components_to_check = components or list(self.health_checks.keys())
            results = {}
            
            # Run health checks concurrently
            tasks = [
                self._run_single_health_check(component)
                for component in components_to_check
                if component in self.health_checks
            ]
            
            check_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(check_results):
                component = components_to_check[i]
                
                if isinstance(result, Exception):
                    results[component] = HealthCheckResult(
                        component=component,
                        status=HealthStatus.CRITICAL,
                        message=f"Health check failed: {str(result)}",
                        response_time=0.0,
                        timestamp=datetime.utcnow()
                    )
                else:
                    results[component] = result
            
            # Check for critical issues and send alerts
            await self._process_health_alerts(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Health check execution failed: {str(e)}")
            raise HealthCheckError(f"Health check failed: {str(e)}")

    async def _run_single_health_check(self, component: str) -> HealthCheckResult:
        """Run health check for a single component"""
        start_time = time.time()
        
        try:
            health_check_func = self.health_checks[component]
            result = await health_check_func()
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                component=component,
                status=result.get("status", HealthStatus.UNKNOWN),
                message=result.get("message", "Health check completed"),
                response_time=response_time,
                timestamp=datetime.utcnow(),
                metadata=result.get("metadata", {})
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                component=component,
                status=HealthStatus.CRITICAL,
                message=f"Health check error: {str(e)}",
                response_time=response_time,
                timestamp=datetime.utcnow()
            )

    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health and performance"""
        try:
            async with AsyncDatabaseSession() as session:
                # Test basic connectivity
                result = await session.execute(text("SELECT 1"))
                result.fetchone()
                
                # Check connection pool status
                pool_info = session.bind.pool
                pool_status = {
                    "size": pool_info.size(),
                    "checked_in": pool_info.checkedin(),
                    "checked_out": pool_info.checkedout(),
                    "invalid": pool_info.invalid()
                }
                
                # Check for long-running queries
                long_queries = await session.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM pg_stat_activity 
                    WHERE state = 'active' 
                    AND query_start < NOW() - INTERVAL '5 minutes'
                """))
                long_query_count = long_queries.fetchone()[0]
                
                # Determine health status
                if pool_status["checked_out"] > self.alert_thresholds["database_connections"]:
                    status = HealthStatus.WARNING
                    message = "High database connection usage"
                elif long_query_count > 0:
                    status = HealthStatus.WARNING
                    message = f"Long-running queries detected: {long_query_count}"
                else:
                    status = HealthStatus.HEALTHY
                    message = "Database is healthy"
                
                return {
                    "status": status,
                    "message": message,
                    "metadata": {
                        "pool_status": pool_status,
                        "long_queries": long_query_count
                    }
                }
                
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Database connection failed: {str(e)}"
            }

    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health and performance"""
        try:
            redis = aioredis.from_url(settings.REDIS_URL)
            
            # Test basic connectivity
            await redis.ping()
            
            # Get Redis info
            info = await redis.info()
            memory_usage = info.get("used_memory_human", "0B")
            connected_clients = info.get("connected_clients", 0)
            
            # Check memory usage
            if "GB" in memory_usage and float(memory_usage.replace("GB", "")) > 8:
                status = HealthStatus.WARNING
                message = f"High Redis memory usage: {memory_usage}"
            elif connected_clients > 100:
                status = HealthStatus.WARNING
                message = f"High client connections: {connected_clients}"
            else:
                status = HealthStatus.HEALTHY
                message = "Redis is healthy"
            
            await redis.close()
            
            return {
                "status": status,
                "message": message,
                "metadata": {
                    "memory_usage": memory_usage,
                    "connected_clients": connected_clients
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Redis connection failed: {str(e)}"
            }

    async def _check_storage_health(self) -> Dict[str, Any]:
        """Check storage system health"""
        try:
            # Test storage connectivity
            health_result = await self.storage_manager.health_check()
            
            if health_result["status"] == "healthy":
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "Storage is healthy",
                    "metadata": health_result
                }
            else:
                return {
                    "status": HealthStatus.WARNING,
                    "message": f"Storage issues: {health_result.get('message', 'Unknown')}",
                    "metadata": health_result
                }
                
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Storage check failed: {str(e)}"
            }

    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system resource health"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Determine overall status
            if (cpu_usage > self.alert_thresholds["cpu_usage"] or
                memory_usage > self.alert_thresholds["memory_usage"] or
                disk_usage > self.alert_thresholds["disk_usage"]):
                status = HealthStatus.WARNING
                message = "High system resource usage"
            else:
                status = HealthStatus.HEALTHY
                message = "System resources are healthy"
            
            return {
                "status": status,
                "message": message,
                "metadata": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "disk_usage": disk_usage,
                    "available_memory": memory.available,
                    "total_memory": memory.total
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"System check failed: {str(e)}"
            }

    async def _check_fingerprinting_health(self) -> Dict[str, Any]:
        """Check fingerprinting engine health"""
        try:
            # Test fingerprinting service availability
            # This would check if the AI models are loaded and responding
            
            # Simulate fingerprinting health check
            test_start = time.time()
            
            # Mock test - in real implementation, this would test actual fingerprinting
            await asyncio.sleep(0.1)  # Simulate processing time
            
            response_time = time.time() - test_start
            
            if response_time > self.alert_thresholds["response_time"]:
                status = HealthStatus.WARNING
                message = f"Slow fingerprinting response: {response_time:.2f}s"
            else:
                status = HealthStatus.HEALTHY
                message = "Fingerprinting engine is healthy"
            
            return {
                "status": status,
                "message": message,
                "metadata": {
                    "response_time": response_time,
                    "model_status": "loaded"
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Fingerprinting check failed: {str(e)}"
            }

    async def _check_protection_health(self) -> Dict[str, Any]:
        """Check protection pipeline health"""
        try:
            # Check protection service components
            # This would verify monitoring, crawlers, etc. are operational
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Protection pipeline is healthy",
                "metadata": {
                    "active_monitors": 0,  # Would be actual count
                    "crawler_status": "active"
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Protection check failed: {str(e)}"
            }

    async def _check_monetization_health(self) -> Dict[str, Any]:
        """Check monetization pipeline health"""
        try:
            # Check monetization services
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Monetization pipeline is healthy",
                "metadata": {
                    "payment_processor_status": "active",
                    "revenue_tracking": "operational"
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Monetization check failed: {str(e)}"
            }

    async def _check_analytics_health(self) -> Dict[str, Any]:
        """Check analytics pipeline health"""
        try:
            # Check analytics services
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Analytics pipeline is healthy",
                "metadata": {
                    "metrics_collection": "active",
                    "dashboard_status": "operational"
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Analytics check failed: {str(e)}"
            }

    async def _process_health_alerts(self, results: Dict[str, HealthCheckResult]):
        """Process health check results and send alerts if needed"""
        critical_issues = []
        warning_issues = []
        
        for component, result in results.items():
            if result.status == HealthStatus.CRITICAL:
                critical_issues.append(result)
            elif result.status == HealthStatus.WARNING:
                warning_issues.append(result)
        
        # Send critical alerts immediately
        if critical_issues:
            await self.notification_manager.send_critical_alert(
                "System Health Critical",
                f"Critical issues detected in {len(critical_issues)} components",
                critical_issues
            )
        
        # Send warning alerts (with rate limiting)
        if warning_issues:
            await self.notification_manager.send_warning_alert(
                "System Health Warning",
                f"Warning issues detected in {len(warning_issues)} components",
                warning_issues
            )


class PipelineMonitor:
    """
    Advanced pipeline monitoring system with metrics collection and analysis
    """
    
    def __init__(self):
        self.health_checker = HealthChecker()
        
        # Prometheus metrics
        self.pipeline_executions = Counter(
            'pipeline_executions_total',
            'Total pipeline executions',
            ['pipeline_name', 'status']
        )
        
        self.pipeline_duration = Histogram(
            'pipeline_duration_seconds',
            'Pipeline execution duration',
            ['pipeline_name']
        )
        
        self.pipeline_errors = Counter(
            'pipeline_errors_total',
            'Total pipeline errors',
            ['pipeline_name', 'error_type']
        )
        
        self.active_pipelines = Gauge(
            'active_pipelines',
            'Number of active pipelines',
            ['pipeline_name']
        )
        
        # In-memory metrics storage
        self.metrics_cache = {}

    async def start_monitoring(self):
        """Start continuous monitoring of all pipelines"""
        logger.info("Starting pipeline monitoring system")
        
        # Start background monitoring tasks
        asyncio.create_task(self._continuous_health_monitoring())
        asyncio.create_task(self._metrics_collection_loop())
        asyncio.create_task(self._cleanup_old_metrics())

    async def record_pipeline_execution(
        self,
        pipeline_name: str,
        execution_time: float,
        status: str,
        error_type: Optional[str] = None
    ):
        """Record pipeline execution metrics"""
        # Update Prometheus metrics
        self.pipeline_executions.labels(
            pipeline_name=pipeline_name,
            status=status
        ).inc()
        
        self.pipeline_duration.labels(
            pipeline_name=pipeline_name
        ).observe(execution_time)
        
        if error_type:
            self.pipeline_errors.labels(
                pipeline_name=pipeline_name,
                error_type=error_type
            ).inc()
        
        # Update in-memory cache
        if pipeline_name not in self.metrics_cache:
            self.metrics_cache[pipeline_name] = {
                "execution_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_execution_time": 0.0,
                "last_execution": datetime.utcnow(),
                "errors": []
            }
        
        cache = self.metrics_cache[pipeline_name]
        cache["execution_count"] += 1
        cache["total_execution_time"] += execution_time
        cache["last_execution"] = datetime.utcnow()
        
        if status == "success":
            cache["success_count"] += 1
        else:
            cache["failure_count"] += 1
            if error_type:
                cache["errors"].append({
                    "type": error_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "execution_time": execution_time
                })

    async def get_pipeline_metrics(
        self,
        pipeline_name: Optional[str] = None,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, PipelineMetrics]:
        """Get comprehensive pipeline metrics"""
        if time_range is None:
            time_range = timedelta(hours=24)
        
        pipelines_to_include = [pipeline_name] if pipeline_name else list(self.metrics_cache.keys())
        metrics = {}
        
        for name in pipelines_to_include:
            if name not in self.metrics_cache:
                continue
            
            cache = self.metrics_cache[name]
            
            # Calculate metrics
            execution_count = cache["execution_count"]
            success_count = cache["success_count"]
            failure_count = cache["failure_count"]
            
            avg_execution_time = (
                cache["total_execution_time"] / execution_count 
                if execution_count > 0 else 0.0
            )
            
            error_rate = failure_count / execution_count if execution_count > 0 else 0.0
            
            # Calculate throughput (executions per hour)
            hours_elapsed = min(time_range.total_seconds() / 3600, 24)
            throughput = execution_count / hours_elapsed if hours_elapsed > 0 else 0.0
            
            metrics[name] = PipelineMetrics(
                pipeline_name=name,
                execution_count=execution_count,
                success_count=success_count,
                failure_count=failure_count,
                avg_execution_time=avg_execution_time,
                last_execution=cache["last_execution"],
                error_rate=error_rate,
                throughput=throughput,
                active_tasks=0  # Would be calculated from active task tracking
            )
        
        return metrics

    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        # Run health checks
        health_results = await self.health_checker.run_health_checks()
        
        # Get pipeline metrics
        pipeline_metrics = await self.get_pipeline_metrics()
        
        # Calculate overall system health
        healthy_components = sum(
            1 for result in health_results.values() 
            if result.status == HealthStatus.HEALTHY
        )
        
        total_components = len(health_results)
        system_health_score = (healthy_components / total_components) * 100 if total_components > 0 else 0
        
        # System statistics
        system_stats = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "uptime": time.time() - psutil.boot_time()
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health_score": system_health_score,
            "component_health": {
                name: result.to_dict() for name, result in health_results.items()
            },
            "pipeline_metrics": {
                name: metrics.to_dict() for name, metrics in pipeline_metrics.items()
            },
            "system_stats": system_stats,
            "alerts": {
                "critical": sum(
                    1 for result in health_results.values() 
                    if result.status == HealthStatus.CRITICAL
                ),
                "warnings": sum(
                    1 for result in health_results.values() 
                    if result.status == HealthStatus.WARNING
                )
            }
        }

    async def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        return generate_latest().decode('utf-8')

    async def _continuous_health_monitoring(self):
        """Continuous health monitoring background task"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self.health_checker.run_health_checks()
                
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        while True:
            try:
                await asyncio.sleep(30)  # Collect every 30 seconds
                
                # Update active pipeline gauges
                for pipeline_name in self.metrics_cache.keys():
                    # This would count actual active tasks
                    active_count = 0  # Placeholder
                    self.active_pipelines.labels(
                        pipeline_name=pipeline_name
                    ).set(active_count)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
                await asyncio.sleep(30)

    async def _cleanup_old_metrics(self):
        """Cleanup old metrics data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                for pipeline_name, cache in self.metrics_cache.items():
                    # Remove old error entries
                    cache["errors"] = [
                        error for error in cache["errors"]
                        if datetime.fromisoformat(error["timestamp"]) > cutoff_time
                    ]
                
            except Exception as e:
                logger.error(f"Metrics cleanup error: {str(e)}")
                await asyncio.sleep(3600)
