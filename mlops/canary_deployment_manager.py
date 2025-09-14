"""
Enterprise Canary Deployment Manager for MLOps
DevOps + Lead Dev IA implementation with intelligent traffic splitting and rollback
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import time
import numpy as np
import uuid
from pathlib import Path
import yaml
from abc import ABC, abstractmethod
import statistics
import warnings

logger = logging.getLogger(__name__)


class DeploymentPhase(Enum):
    """Canary deployment phases"""
    PREPARATION = "preparation"
    INITIAL_DEPLOYMENT = "initial_deployment"
    TRAFFIC_SPLITTING = "traffic_splitting"
    MONITORING = "monitoring"
    SCALING = "scaling"
    COMPLETION = "completion"
    ROLLBACK = "rollback"
    CLEANUP = "cleanup"


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    PREPARING = "preparing"
    DEPLOYING = "deploying"
    MONITORING = "monitoring"
    SCALING = "scaling"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


class TrafficSplitStrategy(Enum):
    """Traffic splitting strategies"""
    PERCENTAGE_BASED = "percentage_based"
    USER_BASED = "user_based"
    GEOGRAPHIC = "geographic"
    FEATURE_FLAG = "feature_flag"
    TIME_BASED = "time_based"
    GRADUAL_RAMP = "gradual_ramp"


class HealthCheckType(Enum):
    """Types of health checks"""
    HTTP_ENDPOINT = "http_endpoint"
    TCP_SOCKET = "tcp_socket"
    COMMAND_EXEC = "command_exec"
    CUSTOM_FUNCTION = "custom_function"
    MODEL_PREDICTION = "model_prediction"


@dataclass
class TrafficSplitConfig:
    """Traffic splitting configuration"""
    strategy: TrafficSplitStrategy = TrafficSplitStrategy.PERCENTAGE_BASED
    initial_percentage: float = 5.0
    target_percentage: float = 100.0
    increment_percentage: float = 10.0
    increment_interval_minutes: int = 10
    max_error_rate_percent: float = 5.0
    min_success_rate_percent: float = 95.0
    evaluation_window_minutes: int = 5
    rollback_threshold_percent: float = 10.0


@dataclass
class HealthCheck:
    """Health check configuration"""
    name: str
    check_type: HealthCheckType
    endpoint: Optional[str] = None
    timeout_seconds: int = 30
    interval_seconds: int = 60
    success_threshold: int = 1
    failure_threshold: int = 3
    custom_function: Optional[Callable] = None
    expected_response_code: int = 200
    expected_response_pattern: Optional[str] = None


@dataclass
class DeploymentTarget:
    """Deployment target configuration"""
    name: str
    environment: str = "production"
    namespace: Optional[str] = None
    cluster: Optional[str] = None
    region: Optional[str] = None
    
    # Service configuration
    service_name: str = ""
    service_port: int = 8080
    service_protocol: str = "HTTP"
    
    # Resource configuration
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"
    replicas: int = 2
    max_replicas: int = 10
    
    # Health checks
    health_checks: List[HealthCheck] = field(default_factory=list)
    
    # Labels and metadata
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class CanaryDeployment:
    """Canary deployment configuration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Model/Application information
    model_name: str = ""
    model_version: str = ""
    baseline_version: str = ""
    canary_version: str = ""
    
    # Deployment configuration
    target: DeploymentTarget = field(default_factory=DeploymentTarget)
    traffic_config: TrafficSplitConfig = field(default_factory=TrafficSplitConfig)
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timeout_minutes: int = 120
    
    # Monitoring and validation
    success_criteria: Dict[str, float] = field(default_factory=dict)
    monitoring_config: Dict[str, Any] = field(default_factory=dict)
    
    # Rollback configuration
    auto_rollback_enabled: bool = True
    rollback_triggers: List[str] = field(default_factory=list)
    
    # Metadata
    created_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentMetrics:
    """Deployment metrics and monitoring data"""
    timestamp: datetime
    
    # Traffic metrics
    total_requests: int = 0
    canary_requests: int = 0
    baseline_requests: int = 0
    traffic_split_percentage: float = 0.0
    
    # Performance metrics
    canary_latency_p50: float = 0.0
    canary_latency_p95: float = 0.0
    canary_latency_p99: float = 0.0
    baseline_latency_p50: float = 0.0
    baseline_latency_p95: float = 0.0
    baseline_latency_p99: float = 0.0
    
    # Error metrics
    canary_error_rate: float = 0.0
    baseline_error_rate: float = 0.0
    canary_success_rate: float = 100.0
    baseline_success_rate: float = 100.0
    
    # Resource metrics
    canary_cpu_usage: float = 0.0
    canary_memory_usage: float = 0.0
    baseline_cpu_usage: float = 0.0
    baseline_memory_usage: float = 0.0
    
    # Business metrics
    canary_throughput: float = 0.0
    baseline_throughput: float = 0.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class DeploymentResult:
    """Canary deployment result"""
    deployment_id: str
    deployment_name: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: float = 0.0
    
    # Final traffic split
    final_traffic_percentage: float = 0.0
    rollback_triggered: bool = False
    rollback_reason: Optional[str] = None
    
    # Performance summary
    performance_improvement: float = 0.0
    error_rate_change: float = 0.0
    success_criteria_met: Dict[str, bool] = field(default_factory=dict)
    
    # Detailed metrics
    metrics_history: List[DeploymentMetrics] = field(default_factory=list)
    
    # Recommendations and artifacts
    recommendations: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)


class TrafficSplitter:
    """Handles traffic splitting for canary deployments"""
    
    def __init__(self) -> None:
        self.active_splits: Dict[str, Dict[str, Any]] = {}
        
    async def configure_traffic_split(
        self,
        deployment_id: str,
        config: TrafficSplitConfig,
        target: DeploymentTarget
    ) -> bool:
        """Configure traffic splitting"""
        try:
            logger.info(f"Configuring traffic split for deployment {deployment_id}")
            
            split_config = {
                "deployment_id": deployment_id,
                "strategy": config.strategy,
                "current_percentage": config.initial_percentage,
                "target_percentage": config.target_percentage,
                "target": target,
                "created_at": datetime.utcnow(),
                "last_updated": datetime.utcnow()
            }
            
            # Configure based on strategy
            if config.strategy == TrafficSplitStrategy.PERCENTAGE_BASED:
                success = await self._configure_percentage_split(split_config, config)
            elif config.strategy == TrafficSplitStrategy.USER_BASED:
                success = await self._configure_user_split(split_config, config)
            elif config.strategy == TrafficSplitStrategy.GEOGRAPHIC:
                success = await self._configure_geo_split(split_config, config)
            elif config.strategy == TrafficSplitStrategy.FEATURE_FLAG:
                success = await self._configure_feature_flag_split(split_config, config)
            else:
                success = await self._configure_percentage_split(split_config, config)
            
            if success:
                self.active_splits[deployment_id] = split_config
                logger.info(f"Traffic split configured successfully for {deployment_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to configure traffic split: {e}")
            return False

    async def _configure_percentage_split(
        self,
        split_config: Dict[str, Any],
        config: TrafficSplitConfig
    ) -> bool:
        """Configure percentage-based traffic splitting"""
        try:
            # In a real implementation, this would configure load balancer
            # For now, we'll simulate the configuration
            
            deployment_id = split_config["deployment_id"]
            percentage = split_config["current_percentage"]
            
            logger.info(f"Setting traffic split to {percentage}% for canary {deployment_id}")
            
            # Simulate load balancer configuration
            await asyncio.sleep(0.1)  # Simulate API call delay
            
            split_config.update({
                "load_balancer_config": {
                    "canary_weight": int(percentage),
                    "baseline_weight": int(100 - percentage),
                    "algorithm": "weighted_round_robin"
                },
                "status": "configured"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Percentage split configuration failed: {e}")
            return False

    async def _configure_user_split(
        self,
        split_config: Dict[str, Any],
        config: TrafficSplitConfig
    ) -> bool:
        """Configure user-based traffic splitting"""
        try:
            # User-based splitting using user ID hashing
            split_config.update({
                "user_split_config": {
                    "hash_algorithm": "md5",
                    "split_field": "user_id",
                    "canary_percentage": config.initial_percentage
                },
                "status": "configured"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"User split configuration failed: {e}")
            return False

    async def _configure_geo_split(
        self,
        split_config: Dict[str, Any],
        config: TrafficSplitConfig
    ) -> bool:
        """Configure geographic traffic splitting"""
        try:
            # Geographic splitting by region/country
            split_config.update({
                "geo_split_config": {
                    "split_by": "region",
                    "canary_regions": ["us-west-1", "eu-west-1"],
                    "baseline_regions": ["us-east-1", "eu-central-1"]
                },
                "status": "configured"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Geographic split configuration failed: {e}")
            return False

    async def _configure_feature_flag_split(
        self,
        split_config: Dict[str, Any],
        config: TrafficSplitConfig
    ) -> bool:
        """Configure feature flag-based traffic splitting"""
        try:
            # Feature flag-based splitting
            split_config.update({
                "feature_flag_config": {
                    "flag_name": f"canary_{split_config['deployment_id']}",
                    "enabled_percentage": config.initial_percentage,
                    "targeting_rules": []
                },
                "status": "configured"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Feature flag split configuration failed: {e}")
            return False

    async def update_traffic_percentage(
        self,
        deployment_id: str,
        new_percentage: float
    ) -> bool:
        """Update traffic split percentage"""
        try:
            if deployment_id not in self.active_splits:
                raise ValueError(f"No active split found for deployment {deployment_id}")
            
            split_config = self.active_splits[deployment_id]
            old_percentage = split_config["current_percentage"]
            
            logger.info(f"Updating traffic split from {old_percentage}% to {new_percentage}% for {deployment_id}")
            
            # Update configuration based on strategy
            if split_config["strategy"] == TrafficSplitStrategy.PERCENTAGE_BASED:
                split_config["load_balancer_config"]["canary_weight"] = int(new_percentage)
                split_config["load_balancer_config"]["baseline_weight"] = int(100 - new_percentage)
            elif split_config["strategy"] == TrafficSplitStrategy.USER_BASED:
                split_config["user_split_config"]["canary_percentage"] = new_percentage
            elif split_config["strategy"] == TrafficSplitStrategy.FEATURE_FLAG:
                split_config["feature_flag_config"]["enabled_percentage"] = new_percentage
            
            split_config["current_percentage"] = new_percentage
            split_config["last_updated"] = datetime.utcnow()
            
            # Simulate configuration update
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update traffic percentage: {e}")
            return False

    async def remove_traffic_split(self, deployment_id: str) -> bool:
        """Remove traffic split configuration"""
        try:
            if deployment_id in self.active_splits:
                logger.info(f"Removing traffic split for deployment {deployment_id}")
                
                # Clean up configuration
                split_config = self.active_splits[deployment_id]
                
                # Reset to 100% baseline traffic
                await self.update_traffic_percentage(deployment_id, 0.0)
                
                # Remove from active splits
                del self.active_splits[deployment_id]
                
                logger.info(f"Traffic split removed for {deployment_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove traffic split: {e}")
            return False


class HealthMonitor:
    """Monitors health of canary and baseline deployments"""
    
    def __init__(self) -> None:
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
    async def start_monitoring(
        self,
        deployment_id: str,
        health_checks: List[HealthCheck],
        callback: Optional[Callable] = None
    ) -> bool:
        """Start health monitoring"""
        try:
            logger.info(f"Starting health monitoring for deployment {deployment_id}")
            
            # Create monitoring task
            monitor_task = asyncio.create_task(
                self._monitor_health(deployment_id, health_checks, callback)
            )
            
            self.monitoring_tasks[deployment_id] = monitor_task
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start health monitoring: {e}")
            return False

    async def _monitor_health(
        self,
        deployment_id -> None: str,
        health_checks -> None: List[HealthCheck],
        callback -> None: Optional[Callable]
    ) -> None:
        """Monitor health continuously"""
        try:
            consecutive_failures = {check.name: 0 for check in health_checks}
            consecutive_successes = {check.name: 0 for check in health_checks}
            
            while True:
                health_results = {}
                
                for check in health_checks:
                    try:
                        # Perform health check
                        result = await self._perform_health_check(check)
                        health_results[check.name] = result
                        
                        if result["healthy"]:
                            consecutive_successes[check.name] += 1
                            consecutive_failures[check.name] = 0
                        else:
                            consecutive_failures[check.name] += 1
                            consecutive_successes[check.name] = 0
                        
                        # Check if failure threshold reached
                        if consecutive_failures[check.name] >= check.failure_threshold:
                            logger.warning(f"Health check {check.name} failed {check.failure_threshold} times")
                            
                            if callback:
                                await callback(deployment_id, "health_check_failed", {
                                    "check_name": check.name,
                                    "failure_count": consecutive_failures[check.name]
                                })
                        
                    except Exception as e:
                        logger.error(f"Health check {check.name} error: {e}")
                        health_results[check.name] = {"healthy": False, "error": str(e)}
                
                # Overall health assessment
                overall_healthy = all(result.get("healthy", False) for result in health_results.values())
                
                if not overall_healthy and callback:
                    await callback(deployment_id, "unhealthy", health_results)
                
                # Wait for next check interval
                min_interval = min(check.interval_seconds for check in health_checks)
                await asyncio.sleep(min_interval)
                
        except asyncio.CancelledError:
            logger.info(f"Health monitoring cancelled for {deployment_id}")
        except Exception as e:
            logger.error(f"Health monitoring error for {deployment_id}: {e}")

    async def _perform_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Perform a single health check"""
        try:
            if check.check_type == HealthCheckType.HTTP_ENDPOINT:
                return await self._http_health_check(check)
            elif check.check_type == HealthCheckType.TCP_SOCKET:
                return await self._tcp_health_check(check)
            elif check.check_type == HealthCheckType.CUSTOM_FUNCTION:
                return await self._custom_health_check(check)
            elif check.check_type == HealthCheckType.MODEL_PREDICTION:
                return await self._model_prediction_check(check)
            else:
                return {"healthy": True, "message": "Check type not implemented"}
                
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _http_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Perform HTTP health check"""
        try:
            # Simulate HTTP health check
            # In real implementation, would use aiohttp or similar
            await asyncio.sleep(0.1)  # Simulate network call
            
            # Mock response
            response_code = 200
            response_time = 0.05
            
            healthy = response_code == check.expected_response_code
            
            return {
                "healthy": healthy,
                "response_code": response_code,
                "response_time": response_time,
                "endpoint": check.endpoint
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _tcp_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Perform TCP socket health check"""
        try:
            # Simulate TCP connection check
            await asyncio.sleep(0.05)
            
            return {
                "healthy": True,
                "connection_time": 0.02,
                "endpoint": check.endpoint
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _custom_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Perform custom function health check"""
        try:
            if check.custom_function:
                if asyncio.iscoroutinefunction(check.custom_function):
                    result = await check.custom_function()
                else:
                    result = check.custom_function()
                
                return {
                    "healthy": bool(result),
                    "result": result
                }
            else:
                return {"healthy": False, "error": "No custom function provided"}
                
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _model_prediction_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Perform model prediction health check"""
        try:
            # Simulate model prediction check
            await asyncio.sleep(0.1)
            
            # Mock prediction test
            prediction_latency = 0.08
            prediction_successful = True
            
            return {
                "healthy": prediction_successful,
                "prediction_latency": prediction_latency,
                "test_successful": prediction_successful
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def stop_monitoring(self, deployment_id -> None: str) -> None:
        """Stop health monitoring"""
        try:
            if deployment_id in self.monitoring_tasks:
                task = self.monitoring_tasks[deployment_id]
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                del self.monitoring_tasks[deployment_id]
                logger.info(f"Health monitoring stopped for {deployment_id}")
                
        except Exception as e:
            logger.error(f"Error stopping health monitoring: {e}")


class MetricsCollector:
    """Collects deployment metrics for analysis"""
    
    def __init__(self) -> None:
        self.metrics_storage: Dict[str, List[DeploymentMetrics]] = {}
        
    async def collect_metrics(
        self,
        deployment_id: str,
        target: DeploymentTarget
    ) -> DeploymentMetrics:
        """Collect current deployment metrics"""
        try:
            # Simulate metrics collection
            # In real implementation, would query monitoring systems like Prometheus
            
            current_time = datetime.utcnow()
            
            # Generate mock metrics
            metrics = DeploymentMetrics(
                timestamp=current_time,
                total_requests=np.random.randint(100, 1000),
                traffic_split_percentage=np.random.uniform(5, 50),
                
                # Latency metrics (mock with some variation)
                canary_latency_p50=np.random.uniform(0.05, 0.15),
                canary_latency_p95=np.random.uniform(0.15, 0.30),
                canary_latency_p99=np.random.uniform(0.30, 0.50),
                baseline_latency_p50=np.random.uniform(0.08, 0.18),
                baseline_latency_p95=np.random.uniform(0.18, 0.35),
                baseline_latency_p99=np.random.uniform(0.35, 0.55),
                
                # Error rates
                canary_error_rate=np.random.uniform(0, 5),
                baseline_error_rate=np.random.uniform(0, 3),
                
                # Resource usage
                canary_cpu_usage=np.random.uniform(20, 80),
                canary_memory_usage=np.random.uniform(30, 70),
                baseline_cpu_usage=np.random.uniform(25, 85),
                baseline_memory_usage=np.random.uniform(35, 75),
                
                # Throughput
                canary_throughput=np.random.uniform(50, 200),
                baseline_throughput=np.random.uniform(100, 300)
            )
            
            # Calculate derived metrics
            metrics.canary_requests = int(metrics.total_requests * metrics.traffic_split_percentage / 100)
            metrics.baseline_requests = metrics.total_requests - metrics.canary_requests
            metrics.canary_success_rate = 100 - metrics.canary_error_rate
            metrics.baseline_success_rate = 100 - metrics.baseline_error_rate
            
            # Store metrics
            if deployment_id not in self.metrics_storage:
                self.metrics_storage[deployment_id] = []
            
            self.metrics_storage[deployment_id].append(metrics)
            
            # Keep only last 1000 metrics points
            if len(self.metrics_storage[deployment_id]) > 1000:
                self.metrics_storage[deployment_id] = self.metrics_storage[deployment_id][-1000:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            raise

    def get_metrics_history(
        self,
        deployment_id: str,
        minutes: Optional[int] = None
    ) -> List[DeploymentMetrics]:
        """Get metrics history for deployment"""
        try:
            if deployment_id not in self.metrics_storage:
                return []
            
            metrics = self.metrics_storage[deployment_id]
            
            if minutes is not None:
                # Filter by time window
                cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
                metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics history: {e}")
            return []

    def analyze_metrics(
        self,
        deployment_id: str,
        window_minutes: int = 10
    ) -> Dict[str, Any]:
        """Analyze metrics for decision making"""
        try:
            metrics = self.get_metrics_history(deployment_id, window_minutes)
            
            if not metrics:
                return {}
            
            # Calculate statistics
            analysis = {
                "window_minutes": window_minutes,
                "sample_count": len(metrics),
                "latest_metrics": metrics[-1] if metrics else None,
                
                # Performance analysis
                "canary_performance": {
                    "avg_latency_p95": statistics.mean([m.canary_latency_p95 for m in metrics]),
                    "avg_error_rate": statistics.mean([m.canary_error_rate for m in metrics]),
                    "avg_success_rate": statistics.mean([m.canary_success_rate for m in metrics]),
                    "avg_throughput": statistics.mean([m.canary_throughput for m in metrics])
                },
                
                "baseline_performance": {
                    "avg_latency_p95": statistics.mean([m.baseline_latency_p95 for m in metrics]),
                    "avg_error_rate": statistics.mean([m.baseline_error_rate for m in metrics]),
                    "avg_success_rate": statistics.mean([m.baseline_success_rate for m in metrics]),
                    "avg_throughput": statistics.mean([m.baseline_throughput for m in metrics])
                }
            }
            
            # Performance comparison
            canary_perf = analysis["canary_performance"]
            baseline_perf = analysis["baseline_performance"]
            
            analysis["comparison"] = {
                "latency_improvement": ((baseline_perf["avg_latency_p95"] - canary_perf["avg_latency_p95"]) / baseline_perf["avg_latency_p95"] * 100) if baseline_perf["avg_latency_p95"] > 0 else 0,
                "error_rate_change": canary_perf["avg_error_rate"] - baseline_perf["avg_error_rate"],
                "throughput_improvement": ((canary_perf["avg_throughput"] - baseline_perf["avg_throughput"]) / baseline_perf["avg_throughput"] * 100) if baseline_perf["avg_throughput"] > 0 else 0
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze metrics: {e}")
            return {}


class CanaryDeploymentManager:
    """
    Enterprise canary deployment manager for MLOps
    """
    
    def __init__(self) -> None:
        self.traffic_splitter = TrafficSplitter()
        self.health_monitor = HealthMonitor()
        self.metrics_collector = MetricsCollector()
        self.active_deployments: Dict[str, CanaryDeployment] = {}
        self.deployment_results: Dict[str, DeploymentResult] = {}
        
    async def start_canary_deployment(
        self,
        deployment: CanaryDeployment
    ) -> DeploymentResult:
        """Start a canary deployment"""
        result = DeploymentResult(
            deployment_id=deployment.id,
            deployment_name=deployment.name,
            status=DeploymentStatus.PREPARING,
            start_time=datetime.utcnow()
        )
        
        try:
            logger.info(f"Starting canary deployment: {deployment.name}")
            
            # Store deployment
            self.active_deployments[deployment.id] = deployment
            deployment.start_time = result.start_time
            
            # Execute deployment phases
            await self._execute_deployment_phases(deployment, result)
            
            # Store final result
            self.deployment_results[deployment.id] = result
            
            logger.info(f"Canary deployment completed: {deployment.name} - {result.status.value}")
            return result
            
        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.rollback_triggered = True
            result.rollback_reason = str(e)
            logger.error(f"Canary deployment failed: {deployment.name} - {e}")
            
            # Attempt rollback
            await self._rollback_deployment(deployment, result)
            
            return result
        
        finally:
            result.end_time = datetime.utcnow()
            result.duration_minutes = (result.end_time - result.start_time).total_seconds() / 60
            
            # Cleanup
            if deployment.id in self.active_deployments:
                del self.active_deployments[deployment.id]

    async def _execute_deployment_phases(
        self,
        deployment -> None: CanaryDeployment,
        result -> None: DeploymentResult
    ) -> None:
        """Execute all deployment phases"""
        try:
            # Phase 1: Preparation
            result.status = DeploymentStatus.PREPARING
            await self._phase_preparation(deployment, result)
            
            # Phase 2: Initial deployment
            result.status = DeploymentStatus.DEPLOYING
            await self._phase_initial_deployment(deployment, result)
            
            # Phase 3: Start monitoring
            result.status = DeploymentStatus.MONITORING
            await self._phase_start_monitoring(deployment, result)
            
            # Phase 4: Gradual traffic increase
            result.status = DeploymentStatus.SCALING
            await self._phase_gradual_scaling(deployment, result)
            
            # Phase 5: Final validation and completion
            result.status = DeploymentStatus.COMPLETED
            await self._phase_completion(deployment, result)
            
        except Exception as e:
            logger.error(f"Deployment phase execution failed: {e}")
            raise

    async def _phase_preparation(
        self,
        deployment -> None: CanaryDeployment,
        result -> None: DeploymentResult
    ) -> None:
        """Preparation phase"""
        try:
            logger.info(f"Phase 1: Preparation for {deployment.name}")
            
            # Validate deployment configuration
            await self._validate_deployment_config(deployment)
            
            # Prepare deployment environment
            await self._prepare_deployment_environment(deployment)
            
            # Initialize metrics collection
            await self.metrics_collector.collect_metrics(deployment.id, deployment.target)
            
            logger.info(f"Preparation phase completed for {deployment.name}")
            
        except Exception as e:
            logger.error(f"Preparation phase failed: {e}")
            raise

    async def _phase_initial_deployment(
        self,
        deployment -> None: CanaryDeployment,
        result -> None: DeploymentResult
    ) -> None:
        """Initial deployment phase"""
        try:
            logger.info(f"Phase 2: Initial deployment for {deployment.name}")
            
            # Deploy canary version
            await self._deploy_canary_version(deployment)
            
            # Configure initial traffic split
            success = await self.traffic_splitter.configure_traffic_split(
                deployment.id,
                deployment.traffic_config,
                deployment.target
            )
            
            if not success:
                raise Exception("Failed to configure initial traffic split")
            
            # Wait for initial stabilization
            await asyncio.sleep(30)  # 30 seconds stabilization
            
            result.final_traffic_percentage = deployment.traffic_config.initial_percentage
            
            logger.info(f"Initial deployment completed for {deployment.name}")
            
        except Exception as e:
            logger.error(f"Initial deployment phase failed: {e}")
            raise

    async def _phase_start_monitoring(
        self,
        deployment -> None: CanaryDeployment,
        result -> None: DeploymentResult
    ) -> None:
        """Start monitoring phase"""
        try:
            logger.info(f"Phase 3: Starting monitoring for {deployment.name}")
            
            # Start health monitoring
            await self.health_monitor.start_monitoring(
                deployment.id,
                deployment.target.health_checks,
                self._health_check_callback
            )
            
            # Initial metrics collection
            initial_metrics = await self.metrics_collector.collect_metrics(
                deployment.id, deployment.target
            )
            result.metrics_history.append(initial_metrics)
            
            logger.info(f"Monitoring started for {deployment.name}")
            
        except Exception as e:
            logger.error(f"Monitoring phase failed: {e}")
            raise

    async def _phase_gradual_scaling(
        self,
        deployment -> None: CanaryDeployment,
        result -> None: DeploymentResult
    ) -> None:
        """Gradual scaling phase"""
        try:
            logger.info(f"Phase 4: Gradual scaling for {deployment.name}")
            
            config = deployment.traffic_config
            current_percentage = config.initial_percentage
            
            while current_percentage < config.target_percentage:
                # Collect and analyze metrics
                metrics = await self.metrics_collector.collect_metrics(
                    deployment.id, deployment.target
                )
                result.metrics_history.append(metrics)
                
                # Analyze performance
                analysis = self.metrics_collector.analyze_metrics(
                    deployment.id, config.evaluation_window_minutes
                )
                
                # Check if we should continue scaling
                should_continue, reason = await self._evaluate_scaling_decision(
                    deployment, analysis
                )
                
                if not should_continue:
                    logger.warning(f"Scaling stopped for {deployment.name}: {reason}")
                    if "error" in reason.lower() or "failure" in reason.lower():
                        result.rollback_triggered = True
                        result.rollback_reason = reason
                        raise Exception(f"Scaling failed: {reason}")
                    break
                
                # Increase traffic percentage
                next_percentage = min(
                    current_percentage + config.increment_percentage,
                    config.target_percentage
                )
                
                success = await self.traffic_splitter.update_traffic_percentage(
                    deployment.id, next_percentage
                )
                
                if not success:
                    raise Exception("Failed to update traffic percentage")
                
                current_percentage = next_percentage
                result.final_traffic_percentage = current_percentage
                
                logger.info(f"Traffic increased to {current_percentage}% for {deployment.name}")
                
                # Wait before next increment
                if current_percentage < config.target_percentage:
                    await asyncio.sleep(config.increment_interval_minutes * 60)
            
            logger.info(f"Gradual scaling completed for {deployment.name}")
            
        except Exception as e:
            logger.error(f"Gradual scaling phase failed: {e}")
            raise

    async def _phase_completion(
        self,
        deployment -> None: CanaryDeployment,
        result -> None: DeploymentResult
    ) -> None:
        """Completion phase"""
        try:
            logger.info(f"Phase 5: Completion for {deployment.name}")
            
            # Final metrics collection
            final_metrics = await self.metrics_collector.collect_metrics(
                deployment.id, deployment.target
            )
            result.metrics_history.append(final_metrics)
            
            # Final analysis
            final_analysis = self.metrics_collector.analyze_metrics(
                deployment.id, deployment.traffic_config.evaluation_window_minutes
            )
            
            # Check success criteria
            result.success_criteria_met = await self._evaluate_success_criteria(
                deployment, final_analysis
            )
            
            # Calculate performance improvement
            if final_analysis.get("comparison"):
                result.performance_improvement = final_analysis["comparison"].get("latency_improvement", 0)
                result.error_rate_change = final_analysis["comparison"].get("error_rate_change", 0)
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(
                deployment, result, final_analysis
            )
            
            # Clean up traffic split if fully migrated
            if result.final_traffic_percentage >= 100:
                await self.traffic_splitter.remove_traffic_split(deployment.id)
            
            logger.info(f"Completion phase finished for {deployment.name}")
            
        except Exception as e:
            logger.error(f"Completion phase failed: {e}")
            raise

    async def _validate_deployment_config(self, deployment -> None: CanaryDeployment) -> None:
        """Validate deployment configuration"""
        try:
            # Basic validation
            if not deployment.name:
                raise ValueError("Deployment name is required")
            
            if not deployment.model_name:
                raise ValueError("Model name is required")
            
            if not deployment.canary_version:
                raise ValueError("Canary version is required")
            
            # Traffic config validation
            config = deployment.traffic_config
            if config.initial_percentage <= 0 or config.initial_percentage > 100:
                raise ValueError("Initial percentage must be between 0 and 100")
            
            if config.target_percentage <= config.initial_percentage:
                raise ValueError("Target percentage must be greater than initial percentage")
            
            # Health checks validation
            if not deployment.target.health_checks:
                logger.warning("No health checks configured for deployment")
            
        except Exception as e:
            logger.error(f"Deployment configuration validation failed: {e}")
            raise

    async def _prepare_deployment_environment(self, deployment -> None: CanaryDeployment) -> None:
        """Prepare deployment environment"""
        try:
            # Simulate environment preparation
            await asyncio.sleep(1)  # Simulate preparation time
            
            logger.info(f"Environment prepared for {deployment.name}")
            
        except Exception as e:
            logger.error(f"Environment preparation failed: {e}")
            raise

    async def _deploy_canary_version(self, deployment -> None: CanaryDeployment) -> None:
        """Deploy canary version"""
        try:
            # Simulate canary deployment
            await asyncio.sleep(2)  # Simulate deployment time
            
            logger.info(f"Canary version {deployment.canary_version} deployed for {deployment.name}")
            
        except Exception as e:
            logger.error(f"Canary deployment failed: {e}")
            raise

    async def _health_check_callback(
        self,
        deployment_id -> None: str,
        event_type -> None: str,
        data -> None: Dict[str, Any]
    ) -> None:
        """Handle health check events"""
        try:
            if event_type == "health_check_failed":
                logger.warning(f"Health check failed for {deployment_id}: {data}")
                
                # Could trigger rollback based on severity
                if deployment_id in self.active_deployments:
                    deployment = self.active_deployments[deployment_id]
                    if deployment.auto_rollback_enabled:
                        logger.warning(f"Consider rollback for {deployment_id} due to health check failure")
            
        except Exception as e:
            logger.error(f"Health check callback error: {e}")

    async def _evaluate_scaling_decision(
        self,
        deployment: CanaryDeployment,
        analysis: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Evaluate whether to continue scaling"""
        try:
            if not analysis:
                return False, "No metrics available for analysis"
            
            config = deployment.traffic_config
            canary_perf = analysis.get("canary_performance", {})
            
            # Check error rate
            avg_error_rate = canary_perf.get("avg_error_rate", 0)
            if avg_error_rate > config.max_error_rate_percent:
                return False, f"Error rate too high: {avg_error_rate:.2f}%"
            
            # Check success rate
            avg_success_rate = canary_perf.get("avg_success_rate", 100)
            if avg_success_rate < config.min_success_rate_percent:
                return False, f"Success rate too low: {avg_success_rate:.2f}%"
            
            # Check success criteria
            for criteria_name, target_value in deployment.success_criteria.items():
                actual_value = canary_perf.get(criteria_name, 0)
                if actual_value < target_value:
                    return False, f"Success criteria not met: {criteria_name} = {actual_value:.2f} < {target_value}"
            
            return True, "All criteria met, continue scaling"
            
        except Exception as e:
            logger.error(f"Scaling decision evaluation failed: {e}")
            return False, f"Evaluation error: {e}"

    async def _evaluate_success_criteria(
        self,
        deployment: CanaryDeployment,
        analysis: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Evaluate success criteria"""
        try:
            criteria_met = {}
            
            if not analysis:
                return criteria_met
            
            canary_perf = analysis.get("canary_performance", {})
            comparison = analysis.get("comparison", {})
            
            # Evaluate each success criteria
            for criteria_name, target_value in deployment.success_criteria.items():
                if criteria_name in canary_perf:
                    actual_value = canary_perf[criteria_name]
                    criteria_met[criteria_name] = actual_value >= target_value
                elif criteria_name in comparison:
                    actual_value = comparison[criteria_name]
                    criteria_met[criteria_name] = actual_value >= target_value
                else:
                    criteria_met[criteria_name] = False
            
            return criteria_met
            
        except Exception as e:
            logger.error(f"Success criteria evaluation failed: {e}")
            return {}

    async def _generate_recommendations(
        self,
        deployment: CanaryDeployment,
        result: DeploymentResult,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate deployment recommendations"""
        recommendations = []
        
        try:
            # Performance recommendations
            if analysis.get("comparison"):
                comparison = analysis["comparison"]
                
                latency_improvement = comparison.get("latency_improvement", 0)
                if latency_improvement > 10:
                    recommendations.append(f"Excellent latency improvement: {latency_improvement:.1f}% faster")
                elif latency_improvement < -10:
                    recommendations.append(f"Performance regression detected: {abs(latency_improvement):.1f}% slower")
                
                error_rate_change = comparison.get("error_rate_change", 0)
                if error_rate_change > 2:
                    recommendations.append(f"Error rate increased by {error_rate_change:.1f}% - investigate issues")
                elif error_rate_change < -1:
                    recommendations.append(f"Error rate improved by {abs(error_rate_change):.1f}%")
            
            # Success criteria recommendations
            unmet_criteria = [name for name, met in result.success_criteria_met.items() if not met]
            if unmet_criteria:
                recommendations.append(f"Unmet success criteria: {', '.join(unmet_criteria)}")
            
            # Traffic recommendations
            if result.final_traffic_percentage < 100:
                recommendations.append(f"Deployment stopped at {result.final_traffic_percentage:.1f}% traffic")
                if result.rollback_triggered:
                    recommendations.append("Consider investigating rollback cause before retry")
                else:
                    recommendations.append("Consider gradual completion to 100% traffic")
            
            # Rollback recommendations
            if result.rollback_triggered:
                recommendations.append(f"Rollback triggered: {result.rollback_reason}")
                recommendations.append("Review metrics and logs before attempting redeployment")
            
            # General recommendations
            if not recommendations:
                recommendations.append("Deployment completed successfully with no issues detected")
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
        
        return recommendations

    async def _rollback_deployment(
        self,
        deployment -> None: CanaryDeployment,
        result -> None: DeploymentResult
    ) -> None:
        """Rollback deployment"""
        try:
            logger.info(f"Starting rollback for deployment {deployment.name}")
            result.status = DeploymentStatus.ROLLING_BACK
            
            # Remove traffic split (route all traffic to baseline)
            await self.traffic_splitter.remove_traffic_split(deployment.id)
            
            # Stop health monitoring
            await self.health_monitor.stop_monitoring(deployment.id)
            
            # Cleanup canary deployment
            # In real implementation, would remove canary pods/containers
            await asyncio.sleep(1)  # Simulate cleanup time
            
            result.status = DeploymentStatus.ROLLED_BACK
            logger.info(f"Rollback completed for deployment {deployment.name}")
            
        except Exception as e:
            logger.error(f"Rollback failed for deployment {deployment.name}: {e}")

    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get current deployment status"""
        try:
            if deployment_id in self.active_deployments:
                deployment = self.active_deployments[deployment_id]
                
                # Get latest metrics
                latest_metrics = await self.metrics_collector.collect_metrics(
                    deployment_id, deployment.target
                )
                
                # Get metrics analysis
                analysis = self.metrics_collector.analyze_metrics(deployment_id)
                
                return {
                    "deployment_id": deployment_id,
                    "name": deployment.name,
                    "status": "active",
                    "current_traffic_percentage": latest_metrics.traffic_split_percentage,
                    "latest_metrics": latest_metrics,
                    "analysis": analysis
                }
            
            elif deployment_id in self.deployment_results:
                result = self.deployment_results[deployment_id]
                return {
                    "deployment_id": deployment_id,
                    "name": result.deployment_name,
                    "status": result.status.value,
                    "final_traffic_percentage": result.final_traffic_percentage,
                    "duration_minutes": result.duration_minutes,
                    "rollback_triggered": result.rollback_triggered
                }
            
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return None

    async def stop_deployment(self, deployment_id: str) -> bool:
        """Stop an active deployment"""
        try:
            if deployment_id in self.active_deployments:
                deployment = self.active_deployments[deployment_id]
                
                # Create result for stopped deployment
                result = DeploymentResult(
                    deployment_id=deployment_id,
                    deployment_name=deployment.name,
                    status=DeploymentStatus.ROLLING_BACK,
                    start_time=deployment.start_time or datetime.utcnow()
                )
                
                # Perform rollback
                await self._rollback_deployment(deployment, result)
                
                # Store result
                self.deployment_results[deployment_id] = result
                
                # Remove from active deployments
                del self.active_deployments[deployment_id]
                
                logger.info(f"Deployment {deployment_id} stopped and rolled back")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop deployment: {e}")
            return False


# Factory functions
def create_canary_deployment_manager() -> CanaryDeploymentManager:
    """Create a new canary deployment manager instance"""
    return CanaryDeploymentManager()


def create_canary_deployment(
    name: str,
    model_name: str,
    canary_version: str,
    baseline_version: str = "stable"
) -> CanaryDeployment:
    """Create a canary deployment configuration"""
    return CanaryDeployment(
        name=name,
        model_name=model_name,
        canary_version=canary_version,
        baseline_version=baseline_version
    )


def create_traffic_split_config(
    initial_percentage: float = 5.0,
    target_percentage: float = 100.0,
    increment_percentage: float = 10.0
) -> TrafficSplitConfig:
    """Create traffic split configuration"""
    return TrafficSplitConfig(
        initial_percentage=initial_percentage,
        target_percentage=target_percentage,
        increment_percentage=increment_percentage
    )


def create_health_check(
    name: str,
    check_type: HealthCheckType = HealthCheckType.HTTP_ENDPOINT,
    endpoint: str = "/health"
) -> HealthCheck:
    """Create a health check configuration"""
    return HealthCheck(
        name=name,
        check_type=check_type,
        endpoint=endpoint
    )


# Example usage
if __name__ == "__main__":
    async def main() -> None:
        # Create canary deployment manager
        manager = create_canary_deployment_manager()
        
        # Create deployment configuration
        deployment = create_canary_deployment(
            name="ml-model-v2-canary",
            model_name="recommendation-engine",
            canary_version="v2.1.0",
            baseline_version="v2.0.0"
        )
        
        # Configure traffic splitting
        deployment.traffic_config = create_traffic_split_config(
            initial_percentage=10.0,
            target_percentage=100.0,
            increment_percentage=20.0
        )
        
        # Add health checks
        deployment.target.health_checks = [
            create_health_check("health", HealthCheckType.HTTP_ENDPOINT, "/health"),
            create_health_check("readiness", HealthCheckType.HTTP_ENDPOINT, "/ready"),
            create_health_check("model_prediction", HealthCheckType.MODEL_PREDICTION)
        ]
        
        # Set success criteria
        deployment.success_criteria = {
            "avg_success_rate": 95.0,
            "avg_latency_p95": 0.2
        }
        
        # Set metadata
        deployment.created_by = "mlops-team"
        deployment.description = "Canary deployment for recommendation engine v2.1.0"
        
        print(f"Starting canary deployment: {deployment.name}")
        
        # Start deployment
        result = await manager.start_canary_deployment(deployment)
        
        print(f"Canary deployment completed:")
        print(f"- Status: {result.status.value}")
        print(f"- Duration: {result.duration_minutes:.1f} minutes")
        print(f"- Final traffic: {result.final_traffic_percentage:.1f}%")
        print(f"- Rollback triggered: {result.rollback_triggered}")
        
        if result.rollback_triggered:
            print(f"- Rollback reason: {result.rollback_reason}")
        
        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"- {rec}")
        
        print(f"\nPerformance summary:")
        print(f"- Performance improvement: {result.performance_improvement:.1f}%")
        print(f"- Error rate change: {result.error_rate_change:+.2f}%")
        print(f"- Success criteria met: {sum(result.success_criteria_met.values())}/{len(result.success_criteria_met)}")
    
    asyncio.run(main())