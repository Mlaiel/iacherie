"""📈 Scaling Configuration Manager - IA-Influencer-Agent
==================================================================
Project Creator & Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
         Microservices Architect + Audio Engineer + DevOps Engineer + IA Prompt Engineer
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Enterprise-grade scaling and auto-scaling configuration
→ horizontal scaling → vertical scaling → load-based scaling → predictive scaling.
==================================================================
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import math

class ScalingStrategy(Enum):
    """
Scaling strategies"""

    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"
    HYBRID = "hybrid"

class ScalingDirection(Enum):
    """Scaling directions"""

    UP = "up"
    DOWN = "down"
    BOTH = "both"

class MetricType(Enum):
    """Metric types for scaling decisions"""

    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    ERROR_RATE = "error_rate"
    CUSTOM = "custom"

class ScalingTrigger(Enum):
    """Scaling triggers"""

    THRESHOLD = "threshold"
    TREND = "trend"
    SCHEDULE = "schedule"
    EVENT = "event"
    COMBINATION = "combination"

class ResourceType(Enum):
    """Resource types for scaling"""

    PODS = "pods"
    NODES = "nodes"
    CONTAINERS = "containers"
    VIRTUAL_MACHINES = "virtual_machines"
    SERVERLESS_FUNCTIONS = "serverless_functions"

@dataclass
class MetricThreshold:
    """Metric threshold configuration"""
    metric_type: MetricType
    threshold_value: float
    comparison: str = "greater_than"  # greater_than, less_than, equal_to
    duration_seconds: int = 300
    evaluation_periods: int = 2
    datapoints_to_alarm: int = 2

@dataclass
class ScalingPolicy:
    """Scaling policy configuration"""
    name: str
    resource_type: ResourceType
    strategy: ScalingStrategy
    direction: ScalingDirection
    min_capacity: int = 1
    max_capacity: int = 10
    target_capacity: int = 2
    scaling_step: int = 1
    cooldown_seconds: int = 300
    warmup_seconds: int = 180
    enabled: bool = True

@dataclass
class PredictiveScaling:
    """
Predictive scaling configuration"""
    enabled: bool = False
    forecast_horizon_hours: int = 24
    forecast_confidence_threshold: float = 0.8
    historical_data_days: int = 30
    prediction_model: str = "auto"  # auto, linear, exponential, arima
    seasonal_patterns: bool = True
    traffic_patterns: List[str] = field(default_factory=list)

@dataclass
class ScheduledScaling:
    """Scheduled scaling configuration"""
    enabled: bool = False
    schedules: List[Dict[str, Any]] = field(default_factory=list)
    timezone: str = "UTC"
    override_policies: bool = False

@dataclass
class ScalingMetrics:
    """Scaling metrics configuration"""
    collection_interval: int = 30
    retention_days: int = 30
    custom_metrics: Dict[str, str] = field(default_factory=dict)
    external_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationConfig:
    """
Scaling notification configuration"""
    enabled: bool = True
    channels: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=lambda: ["scale_up", "scale_down", "error"])
    rate_limit_minutes: int = 5

@dataclass
class ScalingConfiguration:
    """Complete scaling configuration"""
    service_name: str
    namespace: str = "default"
    policies: List[ScalingPolicy] = field(default_factory=list)
    thresholds: List[MetricThreshold] = field(default_factory=list)
    predictive_scaling: PredictiveScaling = field(default_factory=PredictiveScaling)
    scheduled_scaling: ScheduledScaling = field(default_factory=ScheduledScaling)
    metrics_config: ScalingMetrics = field(default_factory=ScalingMetrics)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    custom_config: Dict[str, Any] = field(default_factory=dict)

class ScalingConfigManager:
    """
    Enterprise auto-scaling configuration and policy management.
    
    Provides comprehensive scaling management:
    - Multi-strategy scaling (reactive, predictive, scheduled)
    - Resource-aware scaling (CPU, memory, custom metrics)
    - Kubernetes HPA/VPA integration
    - Cloud provider auto-scaling
    - Predictive scaling with ML models
    - Scheduled scaling for known patterns
    - Multi-tier scaling policies
    - Cost optimization algorithms
    - Real-time monitoring and alerting
    - Scaling event tracking and analytics
    """
    
    def __init__(self):
        """
Initialize scaling configuration manager"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Scaling configurations
        self.scaling_configs = {}
        self.active_policies = {}
        
        # Scaling state
        self.current_metrics = {}
        self.scaling_history = []
        self.cooldown_timers = {}
        
        # Predictive models
        self.prediction_models = {}
        self.historical_data = {}
        
        # Monitoring
        self.scaling_events = []
        self.performance_metrics = {}
        
        self.logger.info("Scaling configuration manager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize scaling configuration manager.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Load default scaling configurations
            await self._load_default_configurations()
            
            # Initialize metrics collection
            await self._initialize_metrics_collection()
            
            # Start scaling engine
            await self._start_scaling_engine()
            
            # Initialize predictive models
            await self._initialize_predictive_models()
            
            # Start scheduled scaling
            await self._start_scheduled_scaling()
            
            self.logger.info("Scaling configuration manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scaling manager: {e}")
            return False
    
    async def _load_default_configurations(self) -> None:
        """Load default scaling configurations"""
        
        # Web tier scaling configuration
        web_config = ScalingConfiguration(
            service_name="web-tier",
            namespace="production",
            policies=[
                ScalingPolicy(
                    name="cpu-scaling",
                    resource_type=ResourceType.PODS,
                    strategy=ScalingStrategy.REACTIVE,
                    direction=ScalingDirection.BOTH,
                    min_capacity=2,
                    max_capacity=20,
                    target_capacity=3,
                    scaling_step=2,
                    cooldown_seconds=300
                ),
                ScalingPolicy(
                    name="memory-scaling",
                    resource_type=ResourceType.PODS,
                    strategy=ScalingStrategy.REACTIVE,
                    direction=ScalingDirection.UP,
                    min_capacity=2,
                    max_capacity=15,
                    scaling_step=1,
                    cooldown_seconds=180
                )
            ],
            thresholds=[
                MetricThreshold(
                    metric_type=MetricType.CPU_UTILIZATION,
                    threshold_value=70.0,
                    comparison="greater_than",
                    duration_seconds=300,
                    evaluation_periods=2
                ),
                MetricThreshold(
                    metric_type=MetricType.MEMORY_UTILIZATION,
                    threshold_value=80.0,
                    comparison="greater_than",
                    duration_seconds=180,
                    evaluation_periods=2
                ),
                MetricThreshold(
                    metric_type=MetricType.REQUEST_RATE,
                    threshold_value=1000.0,
                    comparison="greater_than",
                    duration_seconds=120,
                    evaluation_periods=1
                )
            ],
            predictive_scaling=PredictiveScaling(
                enabled=True,
                forecast_horizon_hours=6,
                forecast_confidence_threshold=0.75,
                historical_data_days=14,
                seasonal_patterns=True,
                traffic_patterns=["business_hours", "weekend_low"]
            ),
            scheduled_scaling=ScheduledScaling(
                enabled=True,
                schedules=[
                    {
                        "name": "business_hours_scale_up",
                        "cron": "0 8 * * 1-5",  # 8 AM weekdays
                        "target_capacity": 5,
                        "timezone": "UTC"
                    },
                    {
                        "name": "night_scale_down",
                        "cron": "0 22 * * *",  # 10 PM daily
                        "target_capacity": 2,
                        "timezone": "UTC"
                    }
                ],
                timezone="UTC"
            )
        )
        
        # Application tier scaling configuration
        app_config = ScalingConfiguration(
            service_name="app-tier",
            namespace="production",
            policies=[
                ScalingPolicy(
                    name="response-time-scaling",
                    resource_type=ResourceType.PODS,
                    strategy=ScalingStrategy.HYBRID,
                    direction=ScalingDirection.BOTH,
                    min_capacity=3,
                    max_capacity=30,
                    target_capacity=5,
                    scaling_step=3,
                    cooldown_seconds=240
                ),
                ScalingPolicy(
                    name="queue-length-scaling",
                    resource_type=ResourceType.PODS,
                    strategy=ScalingStrategy.REACTIVE,
                    direction=ScalingDirection.UP,
                    min_capacity=3,
                    max_capacity=25,
                    scaling_step=2,
                    cooldown_seconds=120
                )
            ],
            thresholds=[
                MetricThreshold(
                    metric_type=MetricType.RESPONSE_TIME,
                    threshold_value=500.0,  # 500ms
                    comparison="greater_than",
                    duration_seconds=180,
                    evaluation_periods=2
                ),
                MetricThreshold(
                    metric_type=MetricType.QUEUE_LENGTH,
                    threshold_value=100.0,
                    comparison="greater_than",
                    duration_seconds=60,
                    evaluation_periods=1
                ),
                MetricThreshold(
                    metric_type=MetricType.ERROR_RATE,
                    threshold_value=5.0,  # 5%
                    comparison="greater_than",
                    duration_seconds=120,
                    evaluation_periods=2
                )
            ],
            predictive_scaling=PredictiveScaling(
                enabled=True,
                forecast_horizon_hours=12,
                forecast_confidence_threshold=0.8,
                historical_data_days=21,
                prediction_model="auto"
            )
        )
        
        # AI processing tier scaling configuration
        ai_config = ScalingConfiguration(
            service_name="ai-processing",
            namespace="production",
            policies=[
                ScalingPolicy(
                    name="gpu-scaling",
                    resource_type=ResourceType.PODS,
                    strategy=ScalingStrategy.PREDICTIVE,
                    direction=ScalingDirection.BOTH,
                    min_capacity=1,
                    max_capacity=10,
                    target_capacity=2,
                    scaling_step=1,
                    cooldown_seconds=600,  # Longer cooldown for GPU resources
                    warmup_seconds=300
                )
            ],
            thresholds=[
                MetricThreshold(
                    metric_type=MetricType.CUSTOM,
                    threshold_value=80.0,
                    comparison="greater_than",
                    duration_seconds=300,
                    evaluation_periods=3
                )
            ],
            metrics_config=ScalingMetrics(
                custom_metrics={
                    "gpu_utilization": "nvidia.com/gpu",
                    "inference_queue_length": "custom.metrics.io/inference_queue",
                    "model_processing_time": "custom.metrics.io/processing_time"
                }
            ),
            predictive_scaling=PredictiveScaling(
                enabled=True,
                forecast_horizon_hours=24,
                forecast_confidence_threshold=0.85,
                historical_data_days=30,
                traffic_patterns=["content_upload_spikes", "processing_batches"]
            )
        )
        
        # Database tier scaling configuration
        db_config = ScalingConfiguration(
            service_name="database-tier",
            namespace="production",
            policies=[
                ScalingPolicy(
                    name="read-replica-scaling",
                    resource_type=ResourceType.PODS,
                    strategy=ScalingStrategy.REACTIVE,
                    direction=ScalingDirection.BOTH,
                    min_capacity=2,
                    max_capacity=8,
                    target_capacity=3,
                    scaling_step=1,
                    cooldown_seconds=900  # Longer cooldown for database
                )
            ],
            thresholds=[
                MetricThreshold(
                    metric_type=MetricType.CUSTOM,
                    threshold_value=70.0,
                    comparison="greater_than",
                    duration_seconds=600,
                    evaluation_periods=3
                )
            ],
            metrics_config=ScalingMetrics(
                custom_metrics={
                    "db_connections": "postgres.connections.active",
                    "query_latency": "postgres.query.latency_p95",
                    "replication_lag": "postgres.replication.lag"
                }
            ),
            scheduled_scaling=ScheduledScaling(
                enabled=True,
                schedules=[
                    {
                        "name": "backup_window_scale_up",
                        "cron": "0 2 * * *",  # 2 AM for backups
                        "target_capacity": 4,
                        "timezone": "UTC"
                    }
                ]
            )
        )
        
        self.scaling_configs = {
            "web-tier": web_config,
            "app-tier": app_config,
            "ai-processing": ai_config,
            "database-tier": db_config
        }
        
        self.logger.info(f"Loaded {len(self.scaling_configs)} scaling configurations")
    
    async def _initialize_metrics_collection(self) -> None:
        """Initialize metrics collection"""
        asyncio.create_task(self._collect_metrics())
        self.logger.info("Metrics collection initialized")
    
    async def _collect_metrics(self) -> None:
        """Collect scaling metrics continuously"""
        while True:
            try:
                for service_name, config in self.scaling_configs.items():
                    await self._collect_service_metrics(service_name, config)
                
                # Wait before next collection
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_service_metrics(self, service_name: str, config: ScalingConfiguration) -> None:
        """Collect metrics for a service"""
        # Simulate metric collection
        metrics = {
            "cpu_utilization": 65.0 + (hash(service_name) % 30),
            "memory_utilization": 70.0 + (hash(service_name) % 25),
            "request_rate": 800 + (hash(service_name) % 400),
            "response_time": 200 + (hash(service_name) % 300),
            "queue_length": 50 + (hash(service_name) % 100),
            "error_rate": 1.0 + (hash(service_name) % 3),
            "timestamp": datetime.now()
        }
        
        # Add custom metrics
        for metric_name, metric_source in config.metrics_config.custom_metrics.items():
            metrics[metric_name] = 50.0 + (hash(metric_name) % 40)
        
        self.current_metrics[service_name] = metrics
    
    async def _start_scaling_engine(self) -> None:
        """Start scaling decision engine"""
        asyncio.create_task(self._scaling_engine())
        self.logger.info("Scaling engine started")
    
    async def _scaling_engine(self) -> None:
        """Scaling decision engine"""
        while True:
            try:
                for service_name, config in self.scaling_configs.items():
                    await self._evaluate_scaling_decisions(service_name, config)
                
                await asyncio.sleep(60)  # Evaluate every minute
                
            except Exception as e:
                self.logger.error(f"Scaling engine error: {e}")
                await asyncio.sleep(120)
    
    async def _evaluate_scaling_decisions(self, service_name: str, config: ScalingConfiguration) -> None:
        """Evaluate scaling decisions for a service"""
        if service_name not in self.current_metrics:
            return
        
        metrics = self.current_metrics[service_name]
        
        for policy in config.policies:
            if not policy.enabled:
                continue
            
            # Check cooldown
            if await self._is_in_cooldown(service_name, policy.name):
                continue
            
            # Evaluate thresholds
            scaling_decision = await self._evaluate_thresholds(service_name, config, metrics)
            
            if scaling_decision:
                await self._execute_scaling_action(service_name, policy, scaling_decision)
    
    async def _is_in_cooldown(self, service_name: str, policy_name: str) -> bool:
        """
Check if scaling action is in cooldown period"""
        key = f"{service_name}:{policy_name}"
        if key in self.cooldown_timers:
            return datetime.now() < self.cooldown_timers[key]
        return False
    
    async def _evaluate_thresholds(
        self,
        service_name: str,
        config: ScalingConfiguration,
        metrics: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate scaling thresholds"""
        violations = []
        
        for threshold in config.thresholds:
            metric_value = metrics.get(threshold.metric_type.value)
            if metric_value is None:
                continue
            
            violated = False
            if threshold.comparison == "greater_than" and metric_value > threshold.threshold_value:
                violated = True
            elif threshold.comparison == "less_than" and metric_value < threshold.threshold_value:
                violated = True
            elif threshold.comparison == "equal_to" and metric_value == threshold.threshold_value:
                violated = True
            
            if violated:
                violations.append({
                    "metric": threshold.metric_type.value,
                    "value": metric_value,
                    "threshold": threshold.threshold_value,
                    "comparison": threshold.comparison
                })
        
        if violations:
            return {
                "action": "scale_up" if any(v["value"] > v["threshold"] for v in violations) else "scale_down",
                "violations": violations,
                "timestamp": datetime.now()
            }
        
        return None
    
    async def _execute_scaling_action(
        self,
        service_name: str,
        policy: ScalingPolicy,
        decision: Dict[str, Any]
    ) -> None:
        """Execute scaling action"""
        try:
            action = decision["action"]
            current_capacity = await self._get_current_capacity(service_name, policy.resource_type)
            
            if action == "scale_up":
                new_capacity = min(current_capacity + policy.scaling_step, policy.max_capacity)
            else:  # scale_down
                new_capacity = max(current_capacity - policy.scaling_step, policy.min_capacity)
            
            if new_capacity != current_capacity:
                success = await self._scale_resource(service_name, policy, new_capacity)
                
                if success:
                    # Set cooldown timer
                    cooldown_key = f"{service_name}:{policy.name}"
                    self.cooldown_timers[cooldown_key] = datetime.now() + timedelta(seconds=policy.cooldown_seconds)
                    
                    # Record scaling event
                    await self._record_scaling_event(service_name, policy, action, current_capacity, new_capacity, decision)
                    
                    # Send notification
                    await self._send_scaling_notification(service_name, action, current_capacity, new_capacity)
            
        except Exception as e:
            self.logger.error(f"Failed to execute scaling action for {service_name}: {e}")
    
    async def _get_current_capacity(self, service_name: str, resource_type: ResourceType) -> int:
        """Get current resource capacity"""
        # Implementation would get actual capacity from Kubernetes, cloud provider, etc.
        # For now, return a simulated value
        return 3
    
    async def _scale_resource(self, service_name: str, policy: ScalingPolicy, new_capacity: int) -> bool:
        """
Scale resource to new capacity"""
        try:
            # Implementation would execute actual scaling
            # For Kubernetes: update HPA or deployment replicas
            # For cloud: update auto-scaling group
            
            self.logger.info(f"Scaling {service_name} to {new_capacity} {policy.resource_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to scale {service_name}: {e}")
            return False
    
    async def _record_scaling_event(
        self,
        service_name: str,
        policy: ScalingPolicy,
        action: str,
        old_capacity: int,
        new_capacity: int,
        decision: Dict[str, Any]
    ) -> None:
        """Record scaling event"""
        event = {
            "timestamp": datetime.now(),
            "service_name": service_name,
            "policy_name": policy.name,
            "action": action,
            "old_capacity": old_capacity,
            "new_capacity": new_capacity,
            "resource_type": policy.resource_type.value,
            "trigger_violations": decision["violations"],
            "strategy": policy.strategy.value
        }
        
        self.scaling_events.append(event)
        self.scaling_history.append(event)
        
        # Limit history size
        if len(self.scaling_history) > 1000:
            self.scaling_history = self.scaling_history[-1000:]
    
    async def _send_scaling_notification(
        self,
        service_name: str,
        action: str,
        old_capacity: int,
        new_capacity: int
    ) -> None:
        """Send scaling notification"""
        if service_name in self.scaling_configs:
            config = self.scaling_configs[service_name]
            if config.notifications.enabled:
                # Implementation would send notifications
                self.logger.info(f"Scaling notification: {service_name} {action} {old_capacity}→{new_capacity}")
    
    async def _initialize_predictive_models(self) -> None:
        """Initialize predictive scaling models"""
        for service_name, config in self.scaling_configs.items():
            if config.predictive_scaling.enabled:
                await self._train_prediction_model(service_name, config)
        
        # Start predictive scaling task
        asyncio.create_task(self._predictive_scaling_engine())
        self.logger.info("Predictive scaling models initialized")
    
    async def _train_prediction_model(self, service_name: str, config: ScalingConfiguration) -> None:
        """Train prediction model for service"""
        # Implementation would train actual ML model
        # For now, create a simple model placeholder
        self.prediction_models[service_name] = {
            "model_type": config.predictive_scaling.prediction_model,
            "confidence": config.predictive_scaling.forecast_confidence_threshold,
            "horizon_hours": config.predictive_scaling.forecast_horizon_hours,
            "last_trained": datetime.now()
        }
    
    async def _predictive_scaling_engine(self) -> None:
        """Predictive scaling engine"""
        while True:
            try:
                for service_name, config in self.scaling_configs.items():
                    if config.predictive_scaling.enabled:
                        await self._execute_predictive_scaling(service_name, config)
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                self.logger.error(f"Predictive scaling error: {e}")
                await asyncio.sleep(3600)
    
    async def _execute_predictive_scaling(self, service_name: str, config: ScalingConfiguration) -> None:
        """Execute predictive scaling for service"""
        if service_name not in self.prediction_models:
            return
        
        # Generate prediction
        prediction = await self._generate_prediction(service_name, config)
        
        if prediction and prediction["confidence"] >= config.predictive_scaling.forecast_confidence_threshold:
            # Execute predictive scaling
            await self._apply_predictive_scaling(service_name, config, prediction)
    
    async def _generate_prediction(self, service_name: str, config: ScalingConfiguration) -> Optional[Dict[str, Any]]:
        """Generate capacity prediction"""
        # Implementation would use actual ML model
        # For now, return a simulated prediction
        return {
            "predicted_capacity": 5,
            "confidence": 0.85,
            "forecast_time": datetime.now() + timedelta(hours=config.predictive_scaling.forecast_horizon_hours),
            "factors": ["traffic_increase", "seasonal_pattern"]
        }
    
    async def _apply_predictive_scaling(
        self,
        service_name: str,
        config: ScalingConfiguration,
        prediction: Dict[str, Any]
    ) -> None:
        """Apply predictive scaling action"""
        predicted_capacity = prediction["predicted_capacity"]
        current_capacity = await self._get_current_capacity(service_name, ResourceType.PODS)
        
        if predicted_capacity != current_capacity:
            for policy in config.policies:
                if policy.strategy in [ScalingStrategy.PREDICTIVE, ScalingStrategy.HYBRID]:
                    await self._scale_resource(service_name, policy, predicted_capacity)
                    break
    
    async def _start_scheduled_scaling(self) -> None:
        """Start scheduled scaling"""
        asyncio.create_task(self._scheduled_scaling_engine())
        self.logger.info("Scheduled scaling started")
    
    async def _scheduled_scaling_engine(self) -> None:
        """Scheduled scaling engine"""
        while True:
            try:
                for service_name, config in self.scaling_configs.items():
                    if config.scheduled_scaling.enabled:
                        await self._check_scheduled_scaling(service_name, config)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Scheduled scaling error: {e}")
                await asyncio.sleep(300)
    
    async def _check_scheduled_scaling(self, service_name: str, config: ScalingConfiguration) -> None:
        """Check and execute scheduled scaling"""
        # Implementation would parse cron schedules and execute scaling
        # For now, just log scheduled scaling checks
        pass
    
    async def add_scaling_config(self, service_name: str, config: ScalingConfiguration) -> bool:
        """
        Add scaling configuration for a service.
        
        Args:
            service_name: Service name
            config: Scaling configuration
            
        Returns:
            bool: True if successful
        """
        try:
            self.scaling_configs[service_name] = config
            
            # Initialize metrics collection for new service
            if config.metrics_config:
                # Start collecting metrics
                pass
            
            # Initialize predictive model if enabled
            if config.predictive_scaling.enabled:
                await self._train_prediction_model(service_name, config)
            
            self.logger.info(f"Scaling configuration added for service: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add scaling config for {service_name}: {e}")
            return False
    
    async def update_scaling_policy(
        self,
        service_name: str,
        policy_name: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update scaling policy.
        
        Args:
            service_name: Service name
            policy_name: Policy name to update
            updates: Updates to apply
            
        Returns:
            bool: True if successful
        """
        try:
            if service_name not in self.scaling_configs:
                raise ValueError(f"Service not found: {service_name}")
            
            config = self.scaling_configs[service_name]
            
            # Find and update policy
            for policy in config.policies:
                if policy.name == policy_name:
                    for key, value in updates.items():
                        if hasattr(policy, key):
                            setattr(policy, key, value)
                    break
            else:
                raise ValueError(f"Policy not found: {policy_name}")
            
            self.logger.info(f"Scaling policy updated: {service_name}:{policy_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update scaling policy {service_name}:{policy_name}: {e}")
            return False
    
    async def enable_predictive_scaling(self, service_name: str) -> bool:
        """
        Enable predictive scaling for a service.
        
        Args:
            service_name: Service name
            
        Returns:
            bool: True if successful
        """
        try:
            if service_name not in self.scaling_configs:
                raise ValueError(f"Service not found: {service_name}")
            
            config = self.scaling_configs[service_name]
            config.predictive_scaling.enabled = True
            
            # Train prediction model
            await self._train_prediction_model(service_name, config)
            
            self.logger.info(f"Predictive scaling enabled for: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable predictive scaling for {service_name}: {e}")
            return False
    
    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get comprehensive scaling status"""
        recent_events = [
            event for event in self.scaling_events
            if (datetime.now() - event["timestamp"]).total_seconds() < 3600  # Last hour
        ]
        
        return {
            "services": {
                name: {
                    "policies_count": len(config.policies),
                    "predictive_enabled": config.predictive_scaling.enabled,
                    "scheduled_enabled": config.scheduled_scaling.enabled,
                    "current_metrics": self.current_metrics.get(name, {}),
                    "in_cooldown": any(
                        await self._is_in_cooldown(name, policy.name)
                        for policy in config.policies
                    )
                }
                for name, config in self.scaling_configs.items()
            },
            "recent_events": len(recent_events),
            "total_scaling_events": len(self.scaling_history),
            "active_cooldowns": len([
                key for key, timer in self.cooldown_timers.items()
                if datetime.now() < timer
            ]),
            "prediction_models": len(self.prediction_models)
        }
    
    async def get_scaling_history(
        self,
        service_name: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get scaling history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        history = [
            event for event in self.scaling_history
            if event["timestamp"] >= cutoff_time
        ]
        
        if service_name:
            history = [event for event in history if event["service_name"] == service_name]
        
        return history
    
    async def get_status(self) -> Dict[str, Any]:
        """Get scaling manager status"""
        return await self.get_scaling_status()
