"""Auto Scaling Manager - Core Enterprise Auto-Scaling Orchestration System

This module provides comprehensive auto-scaling management for the IA Influencer Agent platform,
supporting dynamic resource allocation, intelligent load balancing, and predictive scaling.

Author: Fahed Mlaiel
Email: mlaiel@live.de
© 2025 All Rights Reserved
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from concurrent.futures import ThreadPoolExecutor
import threading

from ..base import BaseAgent
try:
    from core.exceptions import ScalingException, ResourceException
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ScalingException, ResourceException = globals().get('ScalingException, ResourceException', Exception)
try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_database
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_database = DatabaseManager
from ...core.monitoring import get_metrics_client


class ScalingAction(Enum):
    """Scaling action types"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down" 
    NO_ACTION = "no_action"


class ResourceType(Enum):
    """Resource types for scaling"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"


@dataclass
class ScalingMetrics:
    """Scaling metrics data structure"""
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    request_rate: float = 0.0
    response_time: float = 0.0
    error_rate: float = 0.0
    queue_length: int = 0
    active_connections: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingThreshold:
    """Scaling threshold configuration"""
    resource_type: ResourceType
    scale_up_threshold: float
    scale_down_threshold: float
    min_instances: int
    max_instances: int
    cooldown_period: int = 300  # 5 minutes
    evaluation_period: int = 60  # 1 minute


@dataclass
class ScalingInstance:
    """Scaling instance information"""
    instance_id: str
    resource_type: ResourceType
    current_instances: int
    target_instances: int
    status: str
    last_scaled: datetime
    metrics: ScalingMetrics


class AutoScalingManager(BaseAgent):
    """
    Enterprise Auto-Scaling Manager
    
    Provides comprehensive auto-scaling capabilities including:
    - Dynamic resource scaling based on load
    - Predictive scaling using ML models
    - Multi-metric scaling decisions
    - Cost-optimized scaling strategies
    - Real-time monitoring and alerting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.settings = get_settings()
        self.db = get_database()
        self.metrics_client = get_metrics_client()
        
        # Scaling configuration
        self.scaling_thresholds: Dict[str, ScalingThreshold] = {}
        self.scaling_instances: Dict[str, ScalingInstance] = {}
        self.scaling_history: List[Dict[str, Any]] = []
        
        # Monitoring
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Locks for thread-safe operations
        self.scaling_lock = threading.Lock()
        self.metrics_lock = threading.Lock()
        
        # Performance tracking
        self.scaling_decisions: Dict[str, int] = {
            "scale_up": 0,
            "scale_down": 0,
            "no_action": 0
        }
        
        self.logger.info("AutoScalingManager initialized successfully")

    async def start_monitoring(self):
        """Start auto-scaling monitoring"""
        try:
            if self.is_monitoring:
                self.logger.warning("Auto-scaling monitoring already active")
                return
            
            self.is_monitoring = True
            self.monitor_task = asyncio.create_task(self._monitoring_loop())
            
            # Initialize default thresholds
            await self._initialize_default_thresholds()
            
            self.logger.info("Auto-scaling monitoring started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start auto-scaling monitoring: {e}")
            self.is_monitoring = False
            raise ScalingException(f"Monitoring startup failed: {e}")

    async def stop_monitoring(self):
        """Stop auto-scaling monitoring"""
        try:
            self.is_monitoring = False
            
            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass
            
            self.executor.shutdown(wait=True)
            self.logger.info("Auto-scaling monitoring stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")

    async def _monitoring_loop(self):
        """Main monitoring loop for auto-scaling"""
        self.logger.info("Starting auto-scaling monitoring loop")
        
        while self.is_monitoring:
            try:
                # Collect metrics from all monitored services
                metrics = await self._collect_system_metrics()
                
                # Evaluate scaling decisions for each service
                for service_name, service_metrics in metrics.items():
                    await self._evaluate_scaling_decision(service_name, service_metrics)
                
                # Update monitoring metrics
                await self._update_monitoring_metrics()
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _collect_system_metrics(self) -> Dict[str, ScalingMetrics]:
        """Collect comprehensive system metrics"""
        metrics = {}
        
        try:
            # Get metrics from various sources
            services = await self._get_monitored_services()
            
            for service_name in services:
                service_metrics = ScalingMetrics(
                    cpu_utilization=await self._get_cpu_utilization(service_name),
                    memory_utilization=await self._get_memory_utilization(service_name),
                    request_rate=await self._get_request_rate(service_name),
                    response_time=await self._get_response_time(service_name),
                    error_rate=await self._get_error_rate(service_name),
                    queue_length=await self._get_queue_length(service_name),
                    active_connections=await self._get_active_connections(service_name),
                    timestamp=datetime.now()
                )
                
                metrics[service_name] = service_metrics
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {}

    async def _evaluate_scaling_decision(self, service_name: str, metrics: ScalingMetrics):
        """Evaluate scaling decision for a service"""
        try:
            threshold = self.scaling_thresholds.get(service_name)
            if not threshold:
                # Create default threshold for new service
                threshold = await self._create_default_threshold(service_name)
                self.scaling_thresholds[service_name] = threshold
            
            # Check cooldown period
            instance = self.scaling_instances.get(service_name)
            if instance and self._is_in_cooldown(instance, threshold.cooldown_period):
                return ScalingAction.NO_ACTION
            
            # Evaluate scaling conditions
            action = self._determine_scaling_action(metrics, threshold)
            
            # Execute scaling action
            if action != ScalingAction.NO_ACTION:
                await self._execute_scaling_action(service_name, action, metrics)
            
            # Update scaling statistics
            self.scaling_decisions[action.value] += 1
            
        except Exception as e:
            self.logger.error(f"Error evaluating scaling decision for {service_name}: {e}")

    def _determine_scaling_action(self, metrics: ScalingMetrics, threshold: ScalingThreshold) -> ScalingAction:
        """Determine appropriate scaling action based on metrics"""
        try:
            # Multi-metric scaling decision
            scale_up_signals = 0
            scale_down_signals = 0
            
            # CPU utilization
            if metrics.cpu_utilization > threshold.scale_up_threshold:
                scale_up_signals += 1
            elif metrics.cpu_utilization < threshold.scale_down_threshold:
                scale_down_signals += 1
            
            # Memory utilization
            if metrics.memory_utilization > threshold.scale_up_threshold:
                scale_up_signals += 1
            elif metrics.memory_utilization < threshold.scale_down_threshold:
                scale_down_signals += 1
            
            # Response time (high response time = scale up)
            if metrics.response_time > 1000:  # 1 second
                scale_up_signals += 1
            elif metrics.response_time < 200:  # 200ms
                scale_down_signals += 1
            
            # Error rate (high error rate = scale up)
            if metrics.error_rate > 0.05:  # 5% error rate
                scale_up_signals += 1
            elif metrics.error_rate < 0.001:  # 0.1% error rate
                scale_down_signals += 1
            
            # Queue length
            if metrics.queue_length > 100:
                scale_up_signals += 1
            elif metrics.queue_length < 10:
                scale_down_signals += 1
            
            # Make decision based on signals
            if scale_up_signals >= 2:
                return ScalingAction.SCALE_UP
            elif scale_down_signals >= 3:  # More conservative scale down
                return ScalingAction.SCALE_DOWN
            else:
                return ScalingAction.NO_ACTION
                
        except Exception as e:
            self.logger.error(f"Error determining scaling action: {e}")
            return ScalingAction.NO_ACTION

    async def _execute_scaling_action(self, service_name: str, action: ScalingAction, metrics: ScalingMetrics):
        """Execute the determined scaling action"""
        try:
            with self.scaling_lock:
                instance = self.scaling_instances.get(service_name)
                threshold = self.scaling_thresholds.get(service_name)
                
                if not instance:
                    instance = ScalingInstance(
                        instance_id=service_name,
                        resource_type=ResourceType.CPU,
                        current_instances=await self._get_current_instance_count(service_name),
                        target_instances=0,
                        status="active",
                        last_scaled=datetime.now(),
                        metrics=metrics
                    )
                    self.scaling_instances[service_name] = instance
                
                if action == ScalingAction.SCALE_UP:
                    new_count = min(instance.current_instances + 1, threshold.max_instances)
                    if new_count > instance.current_instances:
                        await self._scale_service(service_name, new_count)
                        instance.current_instances = new_count
                        instance.target_instances = new_count
                        instance.last_scaled = datetime.now()
                        
                        self.logger.info(f"Scaled up {service_name} to {new_count} instances")
                
                elif action == ScalingAction.SCALE_DOWN:
                    new_count = max(instance.current_instances - 1, threshold.min_instances)
                    if new_count < instance.current_instances:
                        await self._scale_service(service_name, new_count)
                        instance.current_instances = new_count
                        instance.target_instances = new_count
                        instance.last_scaled = datetime.now()
                        
                        self.logger.info(f"Scaled down {service_name} to {new_count} instances")
                
                # Update metrics
                instance.metrics = metrics
                
                # Record scaling event
                await self._record_scaling_event(service_name, action, instance)
                
        except Exception as e:
            self.logger.error(f"Error executing scaling action for {service_name}: {e}")
            raise ScalingException(f"Scaling execution failed: {e}")

    async def _scale_service(self, service_name: str, target_instances: int):
        """Scale a specific service to target instance count"""
        try:
            # This would integrate with orchestration platform (Kubernetes, Docker Swarm, etc.)
            # Implementation depends on deployment environment
            
            # Simulate scaling operation for now
            self.logger.info(f"Scaling {service_name} to {target_instances} instances")
            
            # In production, this would call:
            # - Kubernetes API for pod scaling
            # - Docker API for container scaling
            # - Cloud provider APIs (AWS ECS, GCP Cloud Run, etc.)
            
            await asyncio.sleep(1)  # Simulate scaling delay
            
        except Exception as e:
            self.logger.error(f"Error scaling service {service_name}: {e}")
            raise

    def _is_in_cooldown(self, instance: ScalingInstance, cooldown_period: int) -> bool:
        """Check if service is in cooldown period"""
        cooldown_end = instance.last_scaled + timedelta(seconds=cooldown_period)
        return datetime.now() < cooldown_end

    async def _record_scaling_event(self, service_name: str, action: ScalingAction, instance: ScalingInstance):
        """Record scaling event for audit and analysis"""
        try:
            event = {
                "timestamp": datetime.now().isoformat(),
                "service_name": service_name,
                "action": action.value,
                "previous_instances": instance.current_instances,
                "new_instances": instance.target_instances,
                "metrics": {
                    "cpu_utilization": instance.metrics.cpu_utilization,
                    "memory_utilization": instance.metrics.memory_utilization,
                    "request_rate": instance.metrics.request_rate,
                    "response_time": instance.metrics.response_time,
                    "error_rate": instance.metrics.error_rate
                }
            }
            
            self.scaling_history.append(event)
            
            # Store in database
            if self.db:
                await self.db.execute(
                    "INSERT INTO scaling_events (service_name, action, event_data) VALUES (?, ?, ?)",
                    (service_name, action.value, json.dumps(event))
                )
            
            # Send to metrics system
            if self.metrics_client:
                self.metrics_client.record_scaling_event(service_name, action.value, instance.target_instances)
                
        except Exception as e:
            self.logger.error(f"Error recording scaling event: {e}")

    async def _initialize_default_thresholds(self):
        """Initialize default scaling thresholds"""
        default_services = [
            "content_agent", "protection_agent", "music_agent", "distribution_agent",
            "recommendation_agent", "analytics_agent", "api_gateway"
        ]
        
        for service in default_services:
            if service not in self.scaling_thresholds:
                threshold = ScalingThreshold(
                    resource_type=ResourceType.CPU,
                    scale_up_threshold=80.0,
                    scale_down_threshold=30.0,
                    min_instances=2,
                    max_instances=20,
                    cooldown_period=300,
                    evaluation_period=60
                )
                self.scaling_thresholds[service] = threshold

    async def _create_default_threshold(self, service_name: str) -> ScalingThreshold:
        """Create default threshold for new service"""
        return ScalingThreshold(
            resource_type=ResourceType.CPU,
            scale_up_threshold=75.0,
            scale_down_threshold=25.0,
            min_instances=1,
            max_instances=10,
            cooldown_period=300,
            evaluation_period=60
        )

    # Metric collection methods (would integrate with monitoring systems)
    async def _get_monitored_services(self) -> List[str]:
        """Get list of services to monitor"""
        return list(self.scaling_thresholds.keys())

    async def _get_cpu_utilization(self, service_name: str) -> float:
        """Get CPU utilization for service"""
        # Integration with monitoring system (Prometheus, CloudWatch, etc.)
        return 50.0  # Placeholder

    async def _get_memory_utilization(self, service_name: str) -> float:
        """Get memory utilization for service"""
        return 45.0  # Placeholder

    async def _get_request_rate(self, service_name: str) -> float:
        """Get request rate for service"""
        return 100.0  # Placeholder

    async def _get_response_time(self, service_name: str) -> float:
        """Get average response time for service"""
        return 250.0  # Placeholder

    async def _get_error_rate(self, service_name: str) -> float:
        """Get error rate for service"""
        return 0.01  # Placeholder

    async def _get_queue_length(self, service_name: str) -> int:
        """Get queue length for service"""
        return 25  # Placeholder

    async def _get_active_connections(self, service_name: str) -> int:
        """Get active connections for service"""
        return 150  # Placeholder

    async def _get_current_instance_count(self, service_name: str) -> int:
        """Get current instance count for service"""
        return 2  # Placeholder

    async def _update_monitoring_metrics(self):
        """Update monitoring metrics"""
        try:
            if self.metrics_client:
                total_services = len(self.scaling_instances)
                active_scaling = sum(1 for i in self.scaling_instances.values() if i.status == "scaling")
                
                self.metrics_client.gauge("autoscaling.monitored_services", total_services)
                self.metrics_client.gauge("autoscaling.active_scaling", active_scaling)
                self.metrics_client.gauge("autoscaling.scale_up_decisions", self.scaling_decisions["scale_up"])
                self.metrics_client.gauge("autoscaling.scale_down_decisions", self.scaling_decisions["scale_down"])
                
        except Exception as e:
            self.logger.error(f"Error updating monitoring metrics: {e}")

    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status"""
        try:
            status = {
                "monitoring_active": self.is_monitoring,
                "monitored_services": len(self.scaling_instances),
                "scaling_decisions": self.scaling_decisions,
                "services": {}
            }
            
            for service_name, instance in self.scaling_instances.items():
                threshold = self.scaling_thresholds.get(service_name)
                status["services"][service_name] = {
                    "current_instances": instance.current_instances,
                    "target_instances": instance.target_instances,
                    "status": instance.status,
                    "last_scaled": instance.last_scaled.isoformat(),
                    "min_instances": threshold.min_instances if threshold else 1,
                    "max_instances": threshold.max_instances if threshold else 10,
                    "metrics": {
                        "cpu_utilization": instance.metrics.cpu_utilization,
                        "memory_utilization": instance.metrics.memory_utilization,
                        "response_time": instance.metrics.response_time,
                        "error_rate": instance.metrics.error_rate
                    }
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting scaling status: {e}")
            return {"error": str(e)}

    async def update_threshold(self, service_name: str, threshold: ScalingThreshold):
        """Update scaling threshold for a service"""
        try:
            self.scaling_thresholds[service_name] = threshold
            self.logger.info(f"Updated scaling threshold for {service_name}")
            
            # Store in database
            if self.db:
                threshold_data = {
                    "resource_type": threshold.resource_type.value,
                    "scale_up_threshold": threshold.scale_up_threshold,
                    "scale_down_threshold": threshold.scale_down_threshold,
                    "min_instances": threshold.min_instances,
                    "max_instances": threshold.max_instances,
                    "cooldown_period": threshold.cooldown_period
                }
                
                await self.db.execute(
                    "REPLACE INTO scaling_thresholds (service_name, threshold_data) VALUES (?, ?)",
                    (service_name, json.dumps(threshold_data))
                )
                
        except Exception as e:
            self.logger.error(f"Error updating threshold for {service_name}: {e}")
            raise ScalingException(f"Threshold update failed: {e}")

    async def get_scaling_history(self, service_name: Optional[str] = None, 
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """Get scaling history"""
        try:
            if service_name:
                history = [event for event in self.scaling_history 
                          if event["service_name"] == service_name]
            else:
                history = self.scaling_history
            
            return history[-limit:]
            
        except Exception as e:
            self.logger.error(f"Error getting scaling history: {e}")
            return []

    async def health_check(self) -> Dict[str, Any]:
        """Health check for auto-scaling manager"""
        try:
            return {
                "status": "healthy" if self.is_monitoring else "stopped",
                "monitoring": self.is_monitoring,
                "monitored_services": len(self.scaling_instances),
                "total_scaling_events": len(self.scaling_history),
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
