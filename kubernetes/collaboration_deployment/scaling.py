"""Advanced Collaboration Scaling Management for IA Influencer Agent
================================================================

This module provides intelligent auto-scaling capabilities for collaboration services,
handling horizontal, vertical, and cluster-level scaling based on ML-driven metrics
and performance indicators for the complete creator collaboration ecosystem.

Business Logic Flow:
Multi-format creators → Dynamic load management → AI-driven scaling decisions 
→ Resource optimization → Cost efficiency → Performance optimization

Features:
- Intelligent horizontal/vertical scaling
- ML-based predictive scaling
- Multi-cloud resource management
- Cost-aware scaling decisions
- Creator collaboration load optimization
- Real-time performance monitoring
- Automated capacity planning

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any reproduction, modification, distribution or use without explicit 
written authorization is STRICTLY PROHIBITED and will be subject to 
legal proceedings under German and international law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import math
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class ScalingType(Enum):
    """
Types of scaling operations for IA Influencer Agent services."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical" 
    CLUSTER = "cluster"
    CUSTOM_METRICS = "custom_metrics"
    PREDICTIVE_ML = "predictive_ml"
    COST_AWARE = "cost_aware"
    COLLABORATIVE_LOAD = "collaborative_load"
    CREATOR_DEMAND = "creator_demand"
    CONTENT_PROCESSING = "content_processing"
    AI_WORKLOAD = "ai_workload"


class ScalingDirection(Enum):
    """Direction of scaling operation with advanced states."""

    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    EMERGENCY_SCALE = "emergency_scale"
    PREDICTIVE_SCALE = "predictive_scale"
    COST_OPTIMIZE = "cost_optimize"


class ScalingTrigger(Enum):
    """Advanced triggers for scaling operations."""

    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    CUSTOM_METRIC = "custom_metric"
    PREDICTIVE = "predictive"
    CREATOR_ACTIVITY = "creator_activity"
    CONTENT_UPLOAD_RATE = "content_upload_rate"
    AI_PROCESSING_LOAD = "ai_processing_load"
    COLLABORATION_REQUESTS = "collaboration_requests"
    PROTECTION_ANALYSIS_LOAD = "protection_analysis_load"
    MONETIZATION_EVENTS = "monetization_events"
    PLATFORM_DISTRIBUTION_LOAD = "platform_distribution_load"
    REAL_TIME_ANALYTICS = "real_time_analytics"
    COST_THRESHOLD = "cost_threshold"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class ScalingStrategy(Enum):
    """Scaling strategies for different scenarios."""

    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_FIRST = "performance_first"
    BALANCED = "balanced"


@dataclass
class ScalingPolicy:
    """Comprehensive configuration for scaling policies."""
    name: str
    service_name: str
    scaling_type: ScalingType
    trigger: ScalingTrigger
    strategy: ScalingStrategy = ScalingStrategy.HYBRID
    threshold_up: float = 80.0
    threshold_down: float = 30.0
    min_replicas: int = 1
    max_replicas: int = 100
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    scale_factor: float = 1.5
    evaluation_periods: int = 3
    enabled: bool = True
    cost_aware: bool = True
    performance_priority: float = 0.7  # 0-1 balance between cost and performance
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    ml_model_config: Dict[str, Any] = field(default_factory=dict)
    creator_behavior_weights: Dict[str, float] = field(default_factory=dict)
    time_based_rules: List[Dict[str, Any]] = field(default_factory=list)
    emergency_thresholds: Dict[str, float] = field(default_factory=dict)


@dataclass
class ScalingEvent:
    """
Comprehensive record of a scaling event."""
    event_id: str
    service_name: str
    scaling_type: ScalingType
    direction: ScalingDirection
    trigger: ScalingTrigger
    strategy: ScalingStrategy
    metric_value: float
    threshold: float
    old_replicas: int
    new_replicas: int
    old_resources: Dict[str, Any] = field(default_factory=dict)
    new_resources: Dict[str, Any] = field(default_factory=dict)
    cost_impact: float = 0.0
    performance_impact: float = 0.0
    prediction_accuracy: Optional[float] = None
    creator_impact: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    rollback_available: bool = True


@dataclass
class ResourceMetrics:
    """
Comprehensive resource utilization metrics."""
    cpu_utilization: float
    memory_utilization: float
    network_io: float
    disk_io: float
    request_rate: float
    response_time: float
    error_rate: float
    queue_length: int
    active_connections: int
    gpu_utilization: float = 0.0
    ai_processing_load: float = 0.0
    creator_active_sessions: int = 0
    content_processing_queue: int = 0
    collaboration_requests_pending: int = 0
    protection_analysis_queue: int = 0
    monetization_events_rate: float = 0.0
    platform_distribution_load: float = 0.0
    cost_per_hour: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PredictiveModel:
    """
Configuration for ML-based predictive scaling."""
    model_type: str = "time_series"
    prediction_horizon: int = 3600  # seconds
    confidence_threshold: float = 0.8
    seasonal_patterns: bool = True
    creator_behavior_patterns: bool = True
    content_upload_patterns: bool = True
    collaboration_patterns: bool = True
    training_data_window: int = 604800  # 1 week in seconds
    retrain_interval: int = 86400  # 24 hours in seconds
    features: List[str] = field(default_factory=list)
    model_params: Dict[str, Any] = field(default_factory=dict)


class CollaborationScalingManager:
    """
    Advanced scaling management for IA Influencer Agent collaboration services.
    
    Provides comprehensive auto-scaling capabilities:
    - Intelligent horizontal and vertical scaling
    - ML-based predictive scaling for creator behavior patterns
    - Cost-aware scaling decisions and optimization
    - Multi-cloud resource management
    - Creator collaboration load optimization
    - Real-time performance monitoring and adjustment
    - Emergency scaling for high-demand scenarios
    - Seasonal and pattern-based scaling predictions
    - Content processing workload optimization
    - AI processing resource allocation
    """
    def __init__(self, config: Any):
        """
Initialize the collaboration scaling manager."""
        self.config = config
        
        # Scaling policies and events
        self.scaling_policies: Dict[str, ScalingPolicy] = {}
        self.scaling_events: List[ScalingEvent] = []
        self.active_scaling_operations: Dict[str, asyncio.Task] = {}
        
        # Metrics and monitoring
        self.metrics_history: Dict[str, List[ResourceMetrics]] = {}
        self.service_metrics: Dict[str, ResourceMetrics] = {}
        
        # ML and prediction
        self.predictive_models: Dict[str, PredictiveModel] = {}
        self.predictions_cache: Dict[str, Dict[str, Any]] = {}
        
        # Cost and resource tracking
        self.cost_history: List[Dict[str, Any]] = []
        self.resource_pools: Dict[str, Any] = {}
        
        # Threading for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.metrics_lock = threading.RLock()
        
        # Monitoring task
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_interval = 30  # seconds
        
        logger.info("Collaboration scaling manager initialized")

    async def start_monitoring(self) -> None:
        """Start continuous monitoring and scaling."""
        if self.monitoring_task and not self.monitoring_task.done():
            logger.warning("Monitoring already running")
            return
        
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started scaling monitoring")

    async def stop_monitoring(self) -> None:
        """Stop monitoring and scaling operations."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Cancel active scaling operations
        for operation in self.active_scaling_operations.values():
            operation.cancel()
        
        logger.info("Stopped scaling monitoring")

    async def add_scaling_policy(self, policy: ScalingPolicy) -> None:
        """Add a new scaling policy for a service."""
        self.scaling_policies[policy.service_name] = policy
        
        # Initialize metrics history
        if policy.service_name not in self.metrics_history:
            self.metrics_history[policy.service_name] = []
        
        # Setup predictive model if enabled
        if policy.strategy in [ScalingStrategy.PREDICTIVE, ScalingStrategy.HYBRID]:
            await self._setup_predictive_model(policy)
        
        logger.info(f"Added scaling policy for service: {policy.service_name}")

    async def remove_scaling_policy(self, service_name: str) -> bool:
        """Remove scaling policy for a service."""
        if service_name not in self.scaling_policies:
            return False
        
        # Cancel active scaling operations
        if service_name in self.active_scaling_operations:
            self.active_scaling_operations[service_name].cancel()
            del self.active_scaling_operations[service_name]
        
        del self.scaling_policies[service_name]
        logger.info(f"Removed scaling policy for service: {service_name}")
        return True

    async def update_service_metrics(
        self, 
        service_name: str, 
        metrics: ResourceMetrics
    ) -> None:
        """Update metrics for a service."""
        with self.metrics_lock:
            self.service_metrics[service_name] = metrics
            
            # Add to history
            if service_name not in self.metrics_history:
                self.metrics_history[service_name] = []
            
            self.metrics_history[service_name].append(metrics)
            
            # Keep only recent history (24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.metrics_history[service_name] = [
                m for m in self.metrics_history[service_name] 
                if m.timestamp > cutoff_time
            ]

    async def scale_service(
        self, 
        service_name: str, 
        target_replicas: int,
        reason: str = "manual"
    ) -> bool:
        """Manually scale a service to target replicas."""
        if service_name not in self.scaling_policies:
            logger.error(f"No scaling policy found for service: {service_name}")
            return False
        
        policy = self.scaling_policies[service_name]
        
        # Validate target replicas
        if target_replicas < policy.min_replicas or target_replicas > policy.max_replicas:
            logger.error(f"Target replicas {target_replicas} outside allowed range [{policy.min_replicas}, {policy.max_replicas}]")
            return False
        
        # Get current replicas
        current_replicas = await self._get_current_replicas(service_name)
        
        if current_replicas == target_replicas:
            logger.info(f"Service {service_name} already at target replicas: {target_replicas}")
            return True
        
        # Create scaling event
        scaling_event = ScalingEvent(
            event_id=f"manual-{service_name}-{int(datetime.utcnow().timestamp())}",
            service_name=service_name,
            scaling_type=ScalingType.HORIZONTAL,
            direction=ScalingDirection.SCALE_UP if target_replicas > current_replicas else ScalingDirection.SCALE_DOWN,
            trigger=ScalingTrigger.CUSTOM_METRIC,
            strategy=ScalingStrategy.REACTIVE,
            metric_value=float(current_replicas),
            threshold=float(target_replicas),
            old_replicas=current_replicas,
            new_replicas=target_replicas
        )
        
        # Perform scaling
        success = await self._execute_scaling(scaling_event, reason)
        
        # Record event
        self.scaling_events.append(scaling_event)
        
        return success

    async def get_scaling_recommendations(
        self, 
        service_name: str
    ) -> Dict[str, Any]:
        """Get scaling recommendations for a service."""
        if service_name not in self.scaling_policies:
            return {"error": "No scaling policy found"}
        
        policy = self.scaling_policies[service_name]
        current_metrics = self.service_metrics.get(service_name)
        
        if not current_metrics:
            return {"error": "No metrics available"}
        
        recommendations = {
            "service_name": service_name,
            "current_state": await self._get_current_service_state(service_name),
            "recommendations": [],
            "cost_analysis": {},
            "performance_analysis": {},
            "predictions": {}
        }
        
        # Analyze current metrics
        analysis = await self._analyze_metrics(service_name, current_metrics, policy)
        
        # Generate recommendations
        if analysis["scaling_needed"]:
            rec = {
                "action": analysis["direction"].value,
                "target_replicas": analysis["recommended_replicas"],
                "reason": analysis["reason"],
                "confidence": analysis["confidence"],
                "estimated_cost_impact": analysis["cost_impact"],
                "estimated_performance_impact": analysis["performance_impact"]
            }
            recommendations["recommendations"].append(rec)
        
        # Add predictive recommendations
        if policy.strategy in [ScalingStrategy.PREDICTIVE, ScalingStrategy.HYBRID]:
            predictive_rec = await self._get_predictive_recommendations(service_name)
            if predictive_rec:
                recommendations["predictions"] = predictive_rec
        
        # Cost analysis
        recommendations["cost_analysis"] = await self._analyze_cost_impact(service_name)
        
        # Performance analysis
        recommendations["performance_analysis"] = await self._analyze_performance_impact(service_name)
        
        return recommendations

    async def get_scaling_history(
        self, 
        service_name: Optional[str] = None,
        days: int = 7
    ) -> List[ScalingEvent]:
        """Get scaling history for services."""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        events = [
            event for event in self.scaling_events
            if event.timestamp > cutoff_time
        ]
        
        if service_name:
            events = [e for e in events if e.service_name == service_name]
        
        return sorted(events, key=lambda x: x.timestamp, reverse=True)

    async def get_metrics_summary(self, service_name: str) -> Dict[str, Any]:
        """
Get comprehensive metrics summary for a service."""
        if service_name not in self.metrics_history:
            return {"error": "No metrics history found"}
        
        history = self.metrics_history[service_name]
        if not history:
            return {"error": "No metrics data available"}
        
        current = self.service_metrics.get(service_name)
        
        # Calculate statistics
        cpu_values = [m.cpu_utilization for m in history]
        memory_values = [m.memory_utilization for m in history]
        response_time_values = [m.response_time for m in history]
        request_rate_values = [m.request_rate for m in history]
        
        summary = {
            "service_name": service_name,
            "current_metrics": current.__dict__ if current else None,
            "statistics": {
                "cpu_utilization": {
                    "avg": statistics.mean(cpu_values),
                    "min": min(cpu_values),
                    "max": max(cpu_values),
                    "std": statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
                },
                "memory_utilization": {
                    "avg": statistics.mean(memory_values),
                    "min": min(memory_values),
                    "max": max(memory_values),
                    "std": statistics.stdev(memory_values) if len(memory_values) > 1 else 0
                },
                "response_time": {
                    "avg": statistics.mean(response_time_values),
                    "min": min(response_time_values),
                    "max": max(response_time_values),
                    "std": statistics.stdev(response_time_values) if len(response_time_values) > 1 else 0
                },
                "request_rate": {
                    "avg": statistics.mean(request_rate_values),
                    "min": min(request_rate_values),
                    "max": max(request_rate_values),
                    "std": statistics.stdev(request_rate_values) if len(request_rate_values) > 1 else 0
                }
            },
            "data_points": len(history),
            "time_range": {
                "start": min(m.timestamp for m in history).isoformat(),
                "end": max(m.timestamp for m in history).isoformat()
            }
        }
        
        return summary

    async def configure_predictive_scaling(
        self, 
        service_name: str, 
        model_config: PredictiveModel
    ) -> bool:
        """Configure predictive scaling for a service."""
        try:
            self.predictive_models[service_name] = model_config
            
            # Train initial model if enough data
            if await self._has_sufficient_training_data(service_name):
                await self._train_predictive_model(service_name)
            
            logger.info(f"Configured predictive scaling for service: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure predictive scaling for {service_name}: {e}")
            return False

    # Private implementation methods

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for scaling decisions."""
        while True:
            try:
                await self._evaluate_all_services()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _evaluate_all_services(self) -> None:
        """Evaluate scaling needs for all services."""
        for service_name, policy in self.scaling_policies.items():
            if not policy.enabled:
                continue
            
            # Skip if scaling operation is already active
            if service_name in self.active_scaling_operations:
                continue
            
            try:
                current_metrics = self.service_metrics.get(service_name)
                if not current_metrics:
                    continue
                
                # Analyze metrics and determine scaling need
                analysis = await self._analyze_metrics(service_name, current_metrics, policy)
                
                if analysis["scaling_needed"]:
                    # Check cooldown period
                    if await self._is_in_cooldown(service_name, analysis["direction"]):
                        continue
                    
                    # Create scaling event
                    scaling_event = ScalingEvent(
                        event_id=f"auto-{service_name}-{int(datetime.utcnow().timestamp())}",
                        service_name=service_name,
                        scaling_type=policy.scaling_type,
                        direction=analysis["direction"],
                        trigger=policy.trigger,
                        strategy=policy.strategy,
                        metric_value=analysis["metric_value"],
                        threshold=analysis["threshold"],
                        old_replicas=analysis["current_replicas"],
                        new_replicas=analysis["recommended_replicas"]
                    )
                    
                    # Execute scaling asynchronously
                    task = asyncio.create_task(
                        self._execute_scaling(scaling_event, "automatic")
                    )
                    self.active_scaling_operations[service_name] = task
                    
                    # Record event
                    self.scaling_events.append(scaling_event)
                    
            except Exception as e:
                logger.error(f"Error evaluating service {service_name}: {e}")

    async def _analyze_metrics(
        self, 
        service_name: str, 
        metrics: ResourceMetrics, 
        policy: ScalingPolicy
    ) -> Dict[str, Any]:
        """Analyze metrics and determine scaling needs."""
        current_replicas = await self._get_current_replicas(service_name)
        
        analysis = {
            "scaling_needed": False,
            "direction": ScalingDirection.MAINTAIN,
            "current_replicas": current_replicas,
            "recommended_replicas": current_replicas,
            "metric_value": 0.0,
            "threshold": 0.0,
            "reason": "",
            "confidence": 0.0,
            "cost_impact": 0.0,
            "performance_impact": 0.0
        }
        
        # Get metric value based on trigger
        if policy.trigger == ScalingTrigger.CPU_UTILIZATION:
            metric_value = metrics.cpu_utilization
            threshold_up = policy.threshold_up
            threshold_down = policy.threshold_down
        elif policy.trigger == ScalingTrigger.MEMORY_UTILIZATION:
            metric_value = metrics.memory_utilization
            threshold_up = policy.threshold_up
            threshold_down = policy.threshold_down
        elif policy.trigger == ScalingTrigger.REQUEST_RATE:
            metric_value = metrics.request_rate
            threshold_up = policy.threshold_up
            threshold_down = policy.threshold_down
        elif policy.trigger == ScalingTrigger.RESPONSE_TIME:
            metric_value = metrics.response_time
            threshold_up = policy.threshold_up
            threshold_down = policy.threshold_down
        elif policy.trigger == ScalingTrigger.CREATOR_ACTIVITY:
            metric_value = metrics.creator_active_sessions
            threshold_up = policy.threshold_up
            threshold_down = policy.threshold_down
        elif policy.trigger == ScalingTrigger.AI_PROCESSING_LOAD:
            metric_value = metrics.ai_processing_load
            threshold_up = policy.threshold_up
            threshold_down = policy.threshold_down
        else:
            # Use CPU as default
            metric_value = metrics.cpu_utilization
            threshold_up = policy.threshold_up
            threshold_down = policy.threshold_down
        
        analysis["metric_value"] = metric_value
        
        # Determine scaling direction
        if metric_value > threshold_up and current_replicas < policy.max_replicas:
            analysis["scaling_needed"] = True
            analysis["direction"] = ScalingDirection.SCALE_UP
            analysis["threshold"] = threshold_up
            analysis["recommended_replicas"] = min(
                math.ceil(current_replicas * policy.scale_factor),
                policy.max_replicas
            )
            analysis["reason"] = f"{policy.trigger.value} ({metric_value:.1f}%) above threshold ({threshold_up:.1f}%)"
            analysis["confidence"] = min((metric_value - threshold_up) / threshold_up, 1.0)
            
        elif metric_value < threshold_down and current_replicas > policy.min_replicas:
            analysis["scaling_needed"] = True
            analysis["direction"] = ScalingDirection.SCALE_DOWN
            analysis["threshold"] = threshold_down
            analysis["recommended_replicas"] = max(
                math.floor(current_replicas / policy.scale_factor),
                policy.min_replicas
            )
            analysis["reason"] = f"{policy.trigger.value} ({metric_value:.1f}%) below threshold ({threshold_down:.1f}%)"
            analysis["confidence"] = min((threshold_down - metric_value) / threshold_down, 1.0)
        
        # Calculate cost and performance impact
        if analysis["scaling_needed"]:
            replica_change = analysis["recommended_replicas"] - current_replicas
            analysis["cost_impact"] = replica_change * metrics.cost_per_hour
            analysis["performance_impact"] = replica_change * 0.2  # Estimated performance improvement per replica
        
        return analysis

    async def _execute_scaling(self, event: ScalingEvent, reason: str) -> bool:
        """Execute the scaling operation."""
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Executing scaling for {event.service_name}: {event.old_replicas} -> {event.new_replicas} ({reason})")
            
            # Perform the actual scaling operation
            success = await self._perform_scaling_operation(event)
            
            if success:
                # Validate scaling result
                await asyncio.sleep(10)  # Wait for scaling to take effect
                actual_replicas = await self._get_current_replicas(event.service_name)
                
                if actual_replicas == event.new_replicas:
                    event.success = True
                    logger.info(f"Scaling completed successfully for {event.service_name}")
                else:
                    event.success = False
                    event.error_message = f"Expected {event.new_replicas} replicas, got {actual_replicas}"
                    logger.error(f"Scaling validation failed for {event.service_name}: {event.error_message}")
            else:
                event.success = False
                event.error_message = "Scaling operation failed"
                logger.error(f"Scaling operation failed for {event.service_name}")
            
        except Exception as e:
            event.success = False
            event.error_message = str(e)
            logger.error(f"Error executing scaling for {event.service_name}: {e}")
        
        finally:
            # Calculate duration
            event.duration_seconds = (datetime.utcnow() - start_time).total_seconds()
            
            # Remove from active operations
            if event.service_name in self.active_scaling_operations:
                del self.active_scaling_operations[event.service_name]
        
        return event.success

    async def _perform_scaling_operation(self, event: ScalingEvent) -> bool:
        """Perform the actual scaling operation."""
        # This would integrate with the actual orchestration platform
        # For now, we simulate the operation
        await asyncio.sleep(5)  # Simulate scaling time
        return True

    async def _get_current_replicas(self, service_name: str) -> int:
        """
Get current number of replicas for a service."""
        # This would query the actual orchestration platform
        # For now, return a default value
        return 3

    async def _get_current_service_state(self, service_name: str) -> Dict[str, Any]:
        """
Get current state of a service."""
        current_replicas = await self._get_current_replicas(service_name)
        current_metrics = self.service_metrics.get(service_name)
        
        return {
            "replicas": current_replicas,
            "metrics": current_metrics.__dict__ if current_metrics else None,
            "status": "running"  # Would query actual status
        }

    async def _is_in_cooldown(self, service_name: str, direction: ScalingDirection) -> bool:
        """Check if service is in cooldown period."""
        policy = self.scaling_policies[service_name]
        
        # Get last scaling event for this service
        recent_events = [
            e for e in self.scaling_events 
            if e.service_name == service_name and e.success
        ]
        
        if not recent_events:
            return False
        
        last_event = max(recent_events, key=lambda x: x.timestamp)
        
        # Determine cooldown period
        if direction == ScalingDirection.SCALE_UP:
            cooldown = policy.scale_up_cooldown
        else:
            cooldown = policy.scale_down_cooldown
        
        # Check if in cooldown
        time_since_last = (datetime.utcnow() - last_event.timestamp).total_seconds()
        return time_since_last < cooldown

    async def _setup_predictive_model(self, policy: ScalingPolicy) -> None:
        """
Setup predictive model for a service."""
        if policy.service_name not in self.predictive_models:
            self.predictive_models[policy.service_name] = PredictiveModel()
        
        logger.info(f"Setup predictive model for service: {policy.service_name}")

    async def _get_predictive_recommendations(self, service_name: str) -> Dict[str, Any]:
        """Get predictive scaling recommendations."""
        if service_name not in self.predictive_models:
            return {}
        
        # This would use actual ML models for prediction
        # For now, return mock data
        return {
            "next_hour_prediction": {
                "expected_load_increase": 25.0,
                "recommended_action": "scale_up",
                "confidence": 0.85
            },
            "daily_pattern": {
                "peak_hours": [9, 10, 11, 14, 15, 16],
                "low_hours": [2, 3, 4, 5, 6]
            }
        }

    async def _analyze_cost_impact(self, service_name: str) -> Dict[str, Any]:
        """Analyze cost impact of scaling decisions."""
        current_metrics = self.service_metrics.get(service_name)
        current_replicas = await self._get_current_replicas(service_name)
        
        if not current_metrics:
            return {}
        
        hourly_cost = current_metrics.cost_per_hour
        
        return {
            "current_hourly_cost": hourly_cost,
            "daily_cost": hourly_cost * 24,
            "monthly_cost": hourly_cost * 24 * 30,
            "cost_per_replica": hourly_cost / current_replicas if current_replicas > 0 else 0,
            "scaling_up_cost": (hourly_cost / current_replicas) if current_replicas > 0 else 0,
            "scaling_down_savings": (hourly_cost / current_replicas) if current_replicas > 1 else 0
        }

    async def _analyze_performance_impact(self, service_name: str) -> Dict[str, Any]:
        """Analyze performance impact of scaling decisions."""
        current_metrics = self.service_metrics.get(service_name)
        
        if not current_metrics:
            return {}
        
        return {
            "current_response_time": current_metrics.response_time,
            "current_throughput": current_metrics.request_rate,
            "current_error_rate": current_metrics.error_rate,
            "estimated_improvement_scale_up": {
                "response_time_reduction": "15-25%",
                "throughput_increase": "20-30%",
                "error_rate_reduction": "10-20%"
            },
            "estimated_impact_scale_down": {
                "response_time_increase": "10-20%",
                "throughput_decrease": "15-25%",
                "error_rate_increase": "5-15%"
            }
        }

    async def _has_sufficient_training_data(self, service_name: str) -> bool:
        """Check if there's sufficient data for ML model training."""
        if service_name not in self.metrics_history:
            return False
        
        history = self.metrics_history[service_name]
        
        # Need at least 24 hours of data with 1-minute intervals
        return len(history) >= 1440

    async def _train_predictive_model(self, service_name: str) -> None:
        """
Train predictive model for a service."""
        logger.info(f"Training predictive model for service: {service_name}")
        
        # This would implement actual ML model training
        # For now, just log the action
        pass


class CollaborationScalingManager:
    """
    Advanced scaling manager for collaboration services.
    
    Provides intelligent auto-scaling capabilities including:
    - Horizontal Pod Autoscaling (HPA)
    - Vertical Pod Autoscaling (VPA)
    - Cluster Autoscaling
    - Custom metrics-based scaling
    - Predictive scaling using ML
    """
    
    def __init__(self, deployment_config):
        """
Initialize scaling manager."""
        self.deployment_config = deployment_config
        self.scaling_policies: Dict[str, ScalingPolicy] = {}
        self.scaling_events: List[ScalingEvent] = []
        self.current_metrics: Dict[str, ResourceMetrics] = {}
        self.ml_predictor = None
        
        # Initialize default scaling policies
        self._initialize_default_policies()
        
        logger.info("CollaborationScalingManager initialized")
    
    def _initialize_default_policies(self) -> None:
        """Initialize default scaling policies for collaboration services."""
        default_policies = {
            "collaboration_api_gateway_cpu": ScalingPolicy(
                name="api_gateway_cpu_scaling",
                service_name="collaboration-api-gateway",
                scaling_type=ScalingType.HORIZONTAL,
                trigger=ScalingTrigger.CPU_UTILIZATION,
                threshold_up=70.0,
                threshold_down=30.0,
                min_replicas=3,
                max_replicas=20,
                scale_up_cooldown=180,
                scale_down_cooldown=300
            ),
            
            "collaboration_api_gateway_rps": ScalingPolicy(
                name="api_gateway_rps_scaling",
                service_name="collaboration-api-gateway",
                scaling_type=ScalingType.HORIZONTAL,
                trigger=ScalingTrigger.REQUEST_RATE,
                threshold_up=1000.0,  # requests per second
                threshold_down=200.0,
                min_replicas=3,
                max_replicas=25,
                scale_factor=2.0
            ),
            
            "matching_engine_memory": ScalingPolicy(
                name="matching_engine_memory_scaling",
                service_name="collaboration-matching-service",
                scaling_type=ScalingType.VERTICAL,
                trigger=ScalingTrigger.MEMORY_UTILIZATION,
                threshold_up=80.0,
                threshold_down=40.0,
                min_replicas=2,
                max_replicas=10
            ),
            
            "content_processing_queue": ScalingPolicy(
                name="content_processing_queue_scaling",
                service_name="content-processing-service",
                scaling_type=ScalingType.HORIZONTAL,
                trigger=ScalingTrigger.QUEUE_LENGTH,
                threshold_up=100.0,  # queue items
                threshold_down=10.0,
                min_replicas=2,
                max_replicas=15,
                scale_factor=1.8
            ),
            
            "notification_response_time": ScalingPolicy(
                name="notification_response_time_scaling",
                service_name="notification-orchestrator",
                scaling_type=ScalingType.HORIZONTAL,
                trigger=ScalingTrigger.RESPONSE_TIME,
                threshold_up=500.0,  # milliseconds
                threshold_down=100.0,
                min_replicas=2,
                max_replicas=12
            ),
            
            "analytics_custom_metrics": ScalingPolicy(
                name="analytics_custom_scaling",
                service_name="collaboration-analytics",
                scaling_type=ScalingType.CUSTOM_METRICS,
                trigger=ScalingTrigger.CUSTOM_METRIC,
                threshold_up=1000.0,  # events per minute
                threshold_down=100.0,
                min_replicas=2,
                max_replicas=8,
                custom_metrics={
                    "metric_name": "collaboration_events_per_minute",
                    "aggregation": "average",
                    "window": "5m"
                }
            )
        }
        
        self.scaling_policies.update(default_policies)
    
    async def configure_horizontal_scaling(self) -> Dict[str, Any]:
        """Configure Horizontal Pod Autoscaling (HPA) for services."""
        logger.info("Configuring horizontal pod autoscaling")
        
        hpa_configs = {}
        
        for policy_name, policy in self.scaling_policies.items():
            if policy.scaling_type == ScalingType.HORIZONTAL:
                hpa_config = await self._create_hpa_config(policy)
                hpa_configs[policy.service_name] = hpa_config
                
                # Apply HPA configuration
                await self._apply_hpa_config(policy.service_name, hpa_config)
        
        logger.info(f"Configured HPA for {len(hpa_configs)} services")
        return {"hpa_configs": hpa_configs, "status": "configured"}
    
    async def configure_vertical_scaling(self) -> Dict[str, Any]:
        """Configure Vertical Pod Autoscaling (VPA) for services."""
        logger.info("Configuring vertical pod autoscaling")
        
        vpa_configs = {}
        
        for policy_name, policy in self.scaling_policies.items():
            if policy.scaling_type == ScalingType.VERTICAL:
                vpa_config = await self._create_vpa_config(policy)
                vpa_configs[policy.service_name] = vpa_config
                
                # Apply VPA configuration
                await self._apply_vpa_config(policy.service_name, vpa_config)
        
        logger.info(f"Configured VPA for {len(vpa_configs)} services")
        return {"vpa_configs": vpa_configs, "status": "configured"}
    
    async def configure_cluster_scaling(self) -> Dict[str, Any]:
        """Configure cluster-level autoscaling."""
        logger.info("Configuring cluster autoscaling")
        
        cluster_config = {
            "enabled": True,
            "min_nodes": 3,
            "max_nodes": 50,
            "target_cpu_utilization": 70,
            "target_memory_utilization": 80,
            "scale_down_delay": "10m",
            "scale_up_delay": "30s",
            "node_pools": [
                {
                    "name": "collaboration-pool",
                    "machine_type": "n1-standard-4",
                    "min_nodes": 2,
                    "max_nodes": 20,
                    "labels": {
                        "workload": "collaboration"
                    }
                },
                {
                    "name": "ml-processing-pool",
                    "machine_type": "n1-standard-8",
                    "min_nodes": 1,
                    "max_nodes": 10,
                    "labels": {
                        "workload": "ml-processing"
                    }
                }
            ]
        }
        
        # Apply cluster autoscaling configuration
        await self._apply_cluster_autoscaling(cluster_config)
        
        logger.info("Cluster autoscaling configured")
        return {"cluster_config": cluster_config, "status": "configured"}
    
    async def configure_custom_metrics_scaling(self) -> Dict[str, Any]:
        """Configure custom metrics-based scaling."""
        logger.info("Configuring custom metrics scaling")
        
        custom_metrics_configs = {}
        
        for policy_name, policy in self.scaling_policies.items():
            if policy.scaling_type == ScalingType.CUSTOM_METRICS:
                custom_config = await self._create_custom_metrics_config(policy)
                custom_metrics_configs[policy.service_name] = custom_config
                
                # Apply custom metrics configuration
                await self._apply_custom_metrics_config(policy.service_name, custom_config)
        
        logger.info(f"Configured custom metrics scaling for {len(custom_metrics_configs)} services")
        return {"custom_configs": custom_metrics_configs, "status": "configured"}
    
    async def _create_hpa_config(self, policy: ScalingPolicy) -> Dict[str, Any]:
        """Create HPA configuration for a scaling policy."""
        metrics = []
        
        if policy.trigger == ScalingTrigger.CPU_UTILIZATION:
            metrics.append({
                "type": "Resource",
                "resource": {
                    "name": "cpu",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": int(policy.threshold_up)
                    }
                }
            })
        
        elif policy.trigger == ScalingTrigger.MEMORY_UTILIZATION:
            metrics.append({
                "type": "Resource",
                "resource": {
                    "name": "memory",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": int(policy.threshold_up)
                    }
                }
            })
        
        elif policy.trigger == ScalingTrigger.REQUEST_RATE:
            metrics.append({
                "type": "Pods",
                "pods": {
                    "metric": {
                        "name": "http_requests_per_second"
                    },
                    "target": {
                        "type": "AverageValue",
                        "averageValue": str(policy.threshold_up)
                    }
                }
            })
        
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{policy.service_name}-hpa",
                "namespace": "collaboration"
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": policy.service_name
                },
                "minReplicas": policy.min_replicas,
                "maxReplicas": policy.max_replicas,
                "metrics": metrics,
                "behavior": {
                    "scaleUp": {
                        "stabilizationWindowSeconds": policy.scale_up_cooldown,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": int((policy.scale_factor - 1) * 100),
                                "periodSeconds": 60
                            }
                        ]
                    },
                    "scaleDown": {
                        "stabilizationWindowSeconds": policy.scale_down_cooldown,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 10,
                                "periodSeconds": 60
                            }
                        ]
                    }
                }
            }
        }
    
    async def _create_vpa_config(self, policy: ScalingPolicy) -> Dict[str, Any]:
        """Create VPA configuration for a scaling policy."""
        return {
            "apiVersion": "autoscaling.k8s.io/v1",
            "kind": "VerticalPodAutoscaler",
            "metadata": {
                "name": f"{policy.service_name}-vpa",
                "namespace": "collaboration"
            },
            "spec": {
                "targetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": policy.service_name
                },
                "updatePolicy": {
                    "updateMode": "Auto"
                },
                "resourcePolicy": {
                    "containerPolicies": [
                        {
                            "containerName": policy.service_name,
                            "minAllowed": {
                                "cpu": "100m",
                                "memory": "256Mi"
                            },
                            "maxAllowed": {
                                "cpu": "8",
                                "memory": "16Gi"
                            },
                            "controlledResources": ["cpu", "memory"]
                        }
                    ]
                }
            }
        }
    
    async def _create_custom_metrics_config(self, policy: ScalingPolicy) -> Dict[str, Any]:
        """Create custom metrics configuration."""
        return {
            "name": policy.custom_metrics.get("metric_name"),
            "query": f'avg_over_time({policy.custom_metrics.get("metric_name")}[{policy.custom_metrics.get("window", "5m")}])',
            "threshold": policy.threshold_up,
            "service": policy.service_name,
            "scaling_factor": policy.scale_factor
        }
    
    async def _apply_hpa_config(self, service_name: str, config: Dict[str, Any]) -> None:
        """Apply HPA configuration to Kubernetes."""
        logger.info(f"Applying HPA configuration for {service_name}")
        # Simulate applying HPA config
        await asyncio.sleep(1)
        logger.info(f"HPA applied for {service_name}")
    
    async def _apply_vpa_config(self, service_name: str, config: Dict[str, Any]) -> None:
        """Apply VPA configuration to Kubernetes."""
        logger.info(f"Applying VPA configuration for {service_name}")
        # Simulate applying VPA config
        await asyncio.sleep(1)
        logger.info(f"VPA applied for {service_name}")
    
    async def _apply_cluster_autoscaling(self, config: Dict[str, Any]) -> None:
        """Apply cluster autoscaling configuration."""
        logger.info("Applying cluster autoscaling configuration")
        # Simulate applying cluster config
        await asyncio.sleep(2)
        logger.info("Cluster autoscaling applied")
    
    async def _apply_custom_metrics_config(self, service_name: str, config: Dict[str, Any]) -> None:
        """Apply custom metrics configuration."""
        logger.info(f"Applying custom metrics configuration for {service_name}")
        # Simulate applying custom metrics config
        await asyncio.sleep(1)
        logger.info(f"Custom metrics applied for {service_name}")
    
    async def scale_services(self, scale_config: Dict[str, Any]) -> Dict[str, Any]:
        """Manually scale services based on configuration."""
        logger.info("Manually scaling services")
        
        scaling_results = {}
        
        for service_name, target_replicas in scale_config.get("services", {}).items():
            try:
                # Get current replica count
                current_replicas = await self._get_current_replicas(service_name)
                
                # Perform scaling
                scaling_result = await self._scale_service(
                    service_name, 
                    current_replicas, 
                    target_replicas
                )
                
                scaling_results[service_name] = scaling_result
                
                # Record scaling event
                event = ScalingEvent(
                    event_id=f"manual-{service_name}-{int(datetime.utcnow().timestamp())}",
                    service_name=service_name,
                    scaling_type=ScalingType.HORIZONTAL,
                    direction=ScalingDirection.SCALE_UP if target_replicas > current_replicas else ScalingDirection.SCALE_DOWN,
                    trigger=ScalingTrigger.CUSTOM_METRIC,
                    metric_value=target_replicas,
                    threshold=current_replicas,
                    old_replicas=current_replicas,
                    new_replicas=target_replicas,
                    success=scaling_result["success"]
                )
                
                self.scaling_events.append(event)
                
            except Exception as e:
                scaling_results[service_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return scaling_results
    
    async def _get_current_replicas(self, service_name: str) -> int:
        """Get current replica count for a service."""
        # Simulate getting current replicas
        return 3  # Default replica count
    
    async def _scale_service(self, service_name: str, current_replicas: int, target_replicas: int) -> Dict[str, Any]:
        """
Scale a service to target replica count."""
        logger.info(f"Scaling {service_name} from {current_replicas} to {target_replicas} replicas")
        
        try:
            # Simulate scaling operation
            await asyncio.sleep(2)
            
            return {
                "success": True,
                "service_name": service_name,
                "old_replicas": current_replicas,
                "new_replicas": target_replicas,
                "scaling_time_seconds": 2.0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def monitor_and_scale(self) -> None:
        """Continuously monitor metrics and trigger scaling actions."""
        logger.info("Starting automatic scaling monitoring")
        
        while True:
            try:
                # Collect current metrics
                await self._collect_service_metrics()
                
                # Evaluate scaling policies
                scaling_decisions = await self._evaluate_scaling_policies()
                
                # Execute scaling actions
                for decision in scaling_decisions:
                    await self._execute_scaling_decision(decision)
                
                # Wait before next evaluation
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in scaling monitoring: {e}")
                await asyncio.sleep(30)  # Shorter wait on error
    
    async def _collect_service_metrics(self) -> None:
        """Collect current metrics for all services."""
        # Simulate metric collection
        services = [
            "collaboration-api-gateway",
            "collaboration-matching-service",
            "content-processing-service",
            "notification-orchestrator",
            "collaboration-analytics"
        ]
        
        for service in services:
            # Simulate realistic metrics
            metrics = ResourceMetrics(
                cpu_utilization=40.0 + (hash(service) % 40),  # 40-80%
                memory_utilization=30.0 + (hash(service) % 50),  # 30-80%
                network_io=100.0 + (hash(service) % 900),  # 100-1000 MB/s
                disk_io=50.0 + (hash(service) % 200),  # 50-250 MB/s
                request_rate=500.0 + (hash(service) % 1000),  # 500-1500 rps
                response_time=50.0 + (hash(service) % 200),  # 50-250 ms
                error_rate=0.1 + (hash(service) % 10) / 100,  # 0.1-0.2%
                queue_length=10 + (hash(service) % 90),  # 10-100 items
                active_connections=100 + (hash(service) % 400)  # 100-500 connections
            )
            
            self.current_metrics[service] = metrics
    
    async def _evaluate_scaling_policies(self) -> List[Dict[str, Any]]:
        """Evaluate all scaling policies against current metrics."""
        scaling_decisions = []
        
        for policy_name, policy in self.scaling_policies.items():
            if not policy.enabled:
                continue
            
            service_metrics = self.current_metrics.get(policy.service_name)
            if not service_metrics:
                continue
            
            decision = await self._evaluate_single_policy(policy, service_metrics)
            if decision:
                scaling_decisions.append(decision)
        
        return scaling_decisions
    
    async def _evaluate_single_policy(self, policy: ScalingPolicy, metrics: ResourceMetrics) -> Optional[Dict[str, Any]]:
        """
Evaluate a single scaling policy."""
        # Get metric value based on trigger type
        metric_value = self._get_metric_value(policy.trigger, metrics)
        
        # Determine scaling direction
        if metric_value > policy.threshold_up:
            direction = ScalingDirection.SCALE_UP
        elif metric_value < policy.threshold_down:
            direction = ScalingDirection.SCALE_DOWN
        else:
            return None  # No scaling needed
        
        # Check cooldown period
        if not await self._check_cooldown(policy, direction):
            return None
        
        return {
            "policy": policy,
            "direction": direction,
            "metric_value": metric_value,
            "threshold": policy.threshold_up if direction == ScalingDirection.SCALE_UP else policy.threshold_down
        }
    
    def _get_metric_value(self, trigger: ScalingTrigger, metrics: ResourceMetrics) -> float:
        """Get metric value based on trigger type."""
        metric_map = {
            ScalingTrigger.CPU_UTILIZATION: metrics.cpu_utilization,
            ScalingTrigger.MEMORY_UTILIZATION: metrics.memory_utilization,
            ScalingTrigger.REQUEST_RATE: metrics.request_rate,
            ScalingTrigger.RESPONSE_TIME: metrics.response_time,
            ScalingTrigger.QUEUE_LENGTH: float(metrics.queue_length)
        }
        
        return metric_map.get(trigger, 0.0)
    
    async def _check_cooldown(self, policy: ScalingPolicy, direction: ScalingDirection) -> bool:
        """
Check if scaling action is allowed based on cooldown period."""
        cooldown_seconds = (
            policy.scale_up_cooldown if direction == ScalingDirection.SCALE_UP 
            else policy.scale_down_cooldown
        )
        
        # Find last scaling event for this service and direction
        cutoff_time = datetime.utcnow() - timedelta(seconds=cooldown_seconds)
        
        for event in reversed(self.scaling_events):
            if (event.service_name == policy.service_name and 
                event.direction == direction and 
                event.timestamp > cutoff_time):
                return False
        
        return True
    
    async def _execute_scaling_decision(self, decision: Dict[str, Any]) -> None:
        """
Execute a scaling decision."""
        policy = decision["policy"]
        direction = decision["direction"]
        
        logger.info(f"Executing scaling decision for {policy.service_name}: {direction.value}")
        
        try:
            # Get current replica count
            current_replicas = await self._get_current_replicas(policy.service_name)
            
            # Calculate target replicas
            if direction == ScalingDirection.SCALE_UP:
                target_replicas = min(
                    int(current_replicas * policy.scale_factor),
                    policy.max_replicas
                )
            else:
                target_replicas = max(
                    int(current_replicas / policy.scale_factor),
                    policy.min_replicas
                )
            
            # Perform scaling
            if target_replicas != current_replicas:
                scaling_result = await self._scale_service(
                    policy.service_name,
                    current_replicas,
                    target_replicas
                )
                
                # Record scaling event
                event = ScalingEvent(
                    event_id=f"auto-{policy.service_name}-{int(datetime.utcnow().timestamp())}",
                    service_name=policy.service_name,
                    scaling_type=policy.scaling_type,
                    direction=direction,
                    trigger=policy.trigger,
                    metric_value=decision["metric_value"],
                    threshold=decision["threshold"],
                    old_replicas=current_replicas,
                    new_replicas=target_replicas,
                    success=scaling_result["success"],
                    duration_seconds=scaling_result.get("scaling_time_seconds")
                )
                
                self.scaling_events.append(event)
        
        except Exception as e:
            logger.error(f"Failed to execute scaling decision: {e}")
    
    async def get_scaling_history(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get scaling history for services."""
        events = self.scaling_events
        
        if service_name:
            events = [e for e in events if e.service_name == service_name]
        
        return [
            {
                "event_id": e.event_id,
                "service_name": e.service_name,
                "scaling_type": e.scaling_type.value,
                "direction": e.direction.value,
                "trigger": e.trigger.value,
                "metric_value": e.metric_value,
                "threshold": e.threshold,
                "old_replicas": e.old_replicas,
                "new_replicas": e.new_replicas,
                "timestamp": e.timestamp.isoformat(),
                "duration_seconds": e.duration_seconds,
                "success": e.success,
                "error_message": e.error_message
            }
            for e in events
        ]
    
    async def get_current_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status for all services."""
        status = {}
        
        for service_name, metrics in self.current_metrics.items():
            # Get active policies for this service
            active_policies = [
                p for p in self.scaling_policies.values() 
                if p.service_name == service_name and p.enabled
            ]
            
            status[service_name] = {
                "current_metrics": {
                    "cpu_utilization": metrics.cpu_utilization,
                    "memory_utilization": metrics.memory_utilization,
                    "request_rate": metrics.request_rate,
                    "response_time": metrics.response_time,
                    "queue_length": metrics.queue_length
                },
                "active_policies": len(active_policies),
                "policy_names": [p.name for p in active_policies],
                "last_scaling_event": self._get_last_scaling_event(service_name)
            }
        
        return status
    
    def _get_last_scaling_event(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get the last scaling event for a service."""
        for event in reversed(self.scaling_events):
            if event.service_name == service_name:
                return {
                    "timestamp": event.timestamp.isoformat(),
                    "direction": event.direction.value,
                    "trigger": event.trigger.value,
                    "success": event.success
                }
        return None
    
    def add_scaling_policy(self, policy: ScalingPolicy) -> None:
        """Add a new scaling policy."""
        self.scaling_policies[policy.name] = policy
        logger.info(f"Added scaling policy: {policy.name}")
    
    def remove_scaling_policy(self, policy_name: str) -> bool:
        """Remove a scaling policy."""
        if policy_name in self.scaling_policies:
            del self.scaling_policies[policy_name]
            logger.info(f"Removed scaling policy: {policy_name}")
            return True
        return False
    
    def update_scaling_policy(self, policy_name: str, updates: Dict[str, Any]) -> bool:
        """Update an existing scaling policy."""
        if policy_name in self.scaling_policies:
            policy = self.scaling_policies[policy_name]
            
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            logger.info(f"Updated scaling policy: {policy_name}")
            return True
        return False
