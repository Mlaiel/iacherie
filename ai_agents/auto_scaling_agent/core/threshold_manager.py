"""Threshold Manager - Enterprise Threshold Management & Alert Configuration System

This module provides comprehensive threshold management, alert configuration,
and dynamic threshold optimization for the auto-scaling system.

Author: Fahed Mlaiel
Email: mlaiel@live.de
© 2025 All Rights Reserved
"""
import asyncio
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
import statistics

from ..base import BaseAgent
try:
    from core.exceptions import ThresholdException
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ThresholdException = globals().get('ThresholdException', Exception)
try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...core.monitoring import get_metrics_client


class ThresholdType(Enum):
    """Types of thresholds"""    STATIC = "static"
    DYNAMIC = "dynamic"
    ADAPTIVE = "adaptive"
    PERCENTAGE = "percentage"
    ABSOLUTE = "absolute"


class ComparisonOperator(Enum):
    """Comparison operators for thresholds"""    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "ge"
    LESS_EQUAL = "le"
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    BETWEEN = "between"
    OUTSIDE = "outside"


class AlertSeverity(Enum):
    """Alert severity levels"""    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Threshold:
    """Threshold configuration"""    threshold_id: str
    name: str
    metric_name: str
    threshold_type: ThresholdType
    operator: ComparisonOperator
    value: float
    secondary_value: Optional[float] = None  # For BETWEEN/OUTSIDE operators
    severity: AlertSeverity = AlertSeverity.WARNING
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DynamicThresholdConfig:
    """Configuration for dynamic threshold calculation"""    metric_name: str
    calculation_method: str  # "percentile", "standard_deviation", "moving_average"
    lookback_period: int = 3600  # seconds
    update_interval: int = 300   # seconds
    sensitivity: float = 1.0     # multiplier for threshold calculation
    min_data_points: int = 10
    percentile: Optional[float] = None  # for percentile method
    std_dev_multiplier: Optional[float] = None  # for std dev method


@dataclass
class ThresholdViolation:
    """Threshold violation record"""    violation_id: str
    threshold_id: str
    metric_name: str
    current_value: float
    threshold_value: float
    operator: ComparisonOperator
    severity: AlertSeverity
    timestamp: datetime
    duration: Optional[timedelta] = None
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThresholdGroup:
    """Group of related thresholds"""    group_id: str
    name: str
    description: str
    thresholds: List[str] = field(default_factory=list)  # threshold IDs
    group_logic: str = "any"  # "any", "all", "majority"
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)


class ThresholdManager(BaseAgent):
    """    Enterprise Threshold Manager
    
    Features:
    - Static and dynamic thresholds
    - Adaptive threshold optimization
    - Complex threshold conditions
    - Threshold groups and dependencies
    - Historical analysis
    - Alert suppression and escalation
    - Performance optimization
    - Configuration management
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.settings = get_settings()
        self.metrics_client = get_metrics_client()
        
        # Threshold storage
        self.thresholds: Dict[str, Threshold] = {}
        self.threshold_groups: Dict[str, ThresholdGroup] = {}
        self.dynamic_configs: Dict[str, DynamicThresholdConfig] = {}
        
        # Violation tracking
        self.active_violations: Dict[str, ThresholdViolation] = {}
        self.violation_history: deque = deque(maxlen=10000)
        
        # Dynamic threshold state
        self.calculated_thresholds: Dict[str, float] = {}
        self.threshold_calculations: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_tasks: List[asyncio.Task] = []
        
        # Configuration
        self.evaluation_interval = 30  # seconds
        self.dynamic_update_interval = 300  # seconds
        self.violation_timeout = 3600  # seconds
        
        # Thread safety
        self.threshold_lock = threading.RLock()
        self.violation_lock = threading.RLock()
        
        # Performance tracking
        self.manager_stats = {
            "threshold_evaluations": 0,
            "violations_detected": 0,
            "violations_resolved": 0,
            "dynamic_updates": 0,
            "false_positives": 0,
            "average_evaluation_time": 0.0
        }
        
        # Alert suppression
        self.suppression_rules: Dict[str, Dict[str, Any]] = {}
        self.notification_cooldowns: Dict[str, datetime] = {}
        
        # Historical data for analysis
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5000))
        
        self.logger.info("ThresholdManager initialized successfully")

    async def start_monitoring(self):
        """Start threshold monitoring"""        try:
            if self.is_monitoring:
                self.logger.warning("Threshold monitoring already active")
                return
            
            self.is_monitoring = True
            
            # Initialize default thresholds
            await self._initialize_default_thresholds()
            
            # Initialize dynamic threshold configurations
            await self._initialize_dynamic_configs()
            
            # Start monitoring tasks
            self.monitor_tasks = [
                asyncio.create_task(self._threshold_evaluation_loop()),
                asyncio.create_task(self._dynamic_threshold_update_loop()),
                asyncio.create_task(self._violation_cleanup_loop()),
                asyncio.create_task(self._analytics_loop())
            ]
            
            self.logger.info("Threshold monitoring started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start threshold monitoring: {e}")
            self.is_monitoring = False
            raise ThresholdException(f"Monitoring startup failed: {e}")

    async def stop_monitoring(self):
        """Stop threshold monitoring"""        try:
            self.is_monitoring = False
            
            # Cancel all monitoring tasks
            for task in self.monitor_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self.monitor_tasks:
                await asyncio.gather(*self.monitor_tasks, return_exceptions=True)
            
            self.monitor_tasks.clear()
            self.logger.info("Threshold monitoring stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping threshold monitoring: {e}")

    async def _threshold_evaluation_loop(self):
        """Main threshold evaluation loop"""        self.logger.info("Starting threshold evaluation loop")
        
        while self.is_monitoring:
            try:
                start_time = time.time()
                
                # Evaluate all active thresholds
                await self._evaluate_all_thresholds()
                
                # Update performance stats
                evaluation_time = (time.time() - start_time) * 1000
                self.manager_stats["threshold_evaluations"] += 1
                self.manager_stats["average_evaluation_time"] = (
                    (self.manager_stats["average_evaluation_time"] * 
                     (self.manager_stats["threshold_evaluations"] - 1) + evaluation_time) /
                    self.manager_stats["threshold_evaluations"]
                )
                
                # Sleep for evaluation interval
                await asyncio.sleep(self.evaluation_interval)
                
            except Exception as e:
                self.logger.error(f"Error in threshold evaluation loop: {e}")
                await asyncio.sleep(self.evaluation_interval)

    async def _dynamic_threshold_update_loop(self):
        """Dynamic threshold update loop"""        while self.is_monitoring:
            try:
                # Update dynamic thresholds
                await self._update_dynamic_thresholds()
                
                # Update stats
                self.manager_stats["dynamic_updates"] += 1
                
                # Sleep for update interval
                await asyncio.sleep(self.dynamic_update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in dynamic threshold update loop: {e}")
                await asyncio.sleep(self.dynamic_update_interval)

    async def _violation_cleanup_loop(self):
        """Violation cleanup loop"""        while self.is_monitoring:
            try:
                # Clean up old violations
                await self._cleanup_old_violations()
                
                # Sleep for cleanup interval
                await asyncio.sleep(600)  # Run every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error in violation cleanup loop: {e}")
                await asyncio.sleep(600)

    async def _analytics_loop(self):
        """Analytics and optimization loop"""        while self.is_monitoring:
            try:
                # Analyze threshold performance
                await self._analyze_threshold_performance()
                
                # Optimize thresholds
                await self._optimize_thresholds()
                
                # Sleep for analytics interval
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                self.logger.error(f"Error in analytics loop: {e}")
                await asyncio.sleep(3600)

    async def _evaluate_all_thresholds(self):
        """Evaluate all active thresholds"""        try:
            with self.threshold_lock:
                # Get current metric values (this would integrate with metrics collector)
                current_metrics = await self._get_current_metrics()
                
                # Evaluate individual thresholds
                for threshold_id, threshold in self.thresholds.items():
                    if threshold.enabled:
                        await self._evaluate_threshold(threshold, current_metrics)
                
                # Evaluate threshold groups
                for group_id, group in self.threshold_groups.items():
                    if group.enabled:
                        await self._evaluate_threshold_group(group, current_metrics)
                        
        except Exception as e:
            self.logger.error(f"Error evaluating all thresholds: {e}")

    async def _evaluate_threshold(self, threshold: Threshold, 
                                 current_metrics: Dict[str, float]):
        """Evaluate a single threshold"""        try:
            metric_value = current_metrics.get(threshold.metric_name)
            if metric_value is None:
                return
            
            # Store metric for historical analysis
            self.metric_history[threshold.metric_name].append({
                "value": metric_value,
                "timestamp": datetime.now()
            })
            
            # Get threshold value (static or dynamic)
            threshold_value = await self._get_threshold_value(threshold)
            
            # Evaluate condition
            violated = self._evaluate_condition(
                metric_value, threshold.operator, threshold_value, threshold.secondary_value
            )
            
            if violated:
                await self._handle_threshold_violation(threshold, metric_value, threshold_value)
            else:
                await self._handle_threshold_recovery(threshold)
                
        except Exception as e:
            self.logger.error(f"Error evaluating threshold {threshold.threshold_id}: {e}")

    async def _evaluate_threshold_group(self, group: ThresholdGroup,
                                       current_metrics: Dict[str, float]):
        """Evaluate a threshold group"""        try:
            violation_count = 0
            total_thresholds = len(group.thresholds)
            
            if total_thresholds == 0:
                return
            
            # Check each threshold in the group
            for threshold_id in group.thresholds:
                threshold = self.thresholds.get(threshold_id)
                if not threshold or not threshold.enabled:
                    continue
                
                metric_value = current_metrics.get(threshold.metric_name)
                if metric_value is None:
                    continue
                
                threshold_value = await self._get_threshold_value(threshold)
                
                if self._evaluate_condition(
                    metric_value, threshold.operator, threshold_value, threshold.secondary_value
                ):
                    violation_count += 1
            
            # Apply group logic
            group_violated = False
            if group.group_logic == "any":
                group_violated = violation_count > 0
            elif group.group_logic == "all":
                group_violated = violation_count == total_thresholds
            elif group.group_logic == "majority":
                group_violated = violation_count > (total_thresholds / 2)
            
            if group_violated:
                await self._handle_group_violation(group, violation_count, total_thresholds)
            else:
                await self._handle_group_recovery(group)
                
        except Exception as e:
            self.logger.error(f"Error evaluating threshold group {group.group_id}: {e}")

    def _evaluate_condition(self, value: float, operator: ComparisonOperator,
                           threshold: float, secondary_threshold: Optional[float] = None) -> bool:
        """Evaluate threshold condition"""        try:
            if operator == ComparisonOperator.GREATER_THAN:
                return value > threshold
            elif operator == ComparisonOperator.LESS_THAN:
                return value < threshold
            elif operator == ComparisonOperator.GREATER_EQUAL:
                return value >= threshold
            elif operator == ComparisonOperator.LESS_EQUAL:
                return value <= threshold
            elif operator == ComparisonOperator.EQUAL:
                return abs(value - threshold) < 0.001
            elif operator == ComparisonOperator.NOT_EQUAL:
                return abs(value - threshold) >= 0.001
            elif operator == ComparisonOperator.BETWEEN:
                if secondary_threshold is None:
                    return False
                return min(threshold, secondary_threshold) <= value <= max(threshold, secondary_threshold)
            elif operator == ComparisonOperator.OUTSIDE:
                if secondary_threshold is None:
                    return False
                return value < min(threshold, secondary_threshold) or value > max(threshold, secondary_threshold)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            return False

    async def _get_threshold_value(self, threshold: Threshold) -> float:
        """Get threshold value (static or calculated)"""        try:
            if threshold.threshold_type == ThresholdType.STATIC:
                return threshold.value
            elif threshold.threshold_type == ThresholdType.DYNAMIC:
                return self.calculated_thresholds.get(threshold.threshold_id, threshold.value)
            elif threshold.threshold_type == ThresholdType.ADAPTIVE:
                return await self._calculate_adaptive_threshold(threshold)
            else:
                return threshold.value
                
        except Exception as e:
            self.logger.error(f"Error getting threshold value: {e}")
            return threshold.value

    async def _calculate_adaptive_threshold(self, threshold: Threshold) -> float:
        """Calculate adaptive threshold based on historical data"""        try:
            metric_history = self.metric_history.get(threshold.metric_name, deque())
            
            if len(metric_history) < 10:
                return threshold.value
            
            # Get recent values (last hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            recent_values = [
                record["value"] for record in metric_history
                if record["timestamp"] >= cutoff_time
            ]
            
            if not recent_values:
                return threshold.value
            
            # Calculate adaptive threshold based on percentiles
            if threshold.operator in [ComparisonOperator.GREATER_THAN, ComparisonOperator.GREATER_EQUAL]:
                # For upper thresholds, use 95th percentile
                return statistics.quantiles(recent_values, n=20)[18]  # 95th percentile
            else:
                # For lower thresholds, use 5th percentile
                return statistics.quantiles(recent_values, n=20)[0]   # 5th percentile
                
        except Exception as e:
            self.logger.error(f"Error calculating adaptive threshold: {e}")
            return threshold.value

    async def _handle_threshold_violation(self, threshold: Threshold,
                                         current_value: float, threshold_value: float):
        """Handle threshold violation"""        try:
            violation_key = f"{threshold.threshold_id}_{threshold.metric_name}"
            
            # Check if violation already exists
            if violation_key in self.active_violations:
                # Update existing violation
                violation = self.active_violations[violation_key]
                violation.current_value = current_value
                violation.duration = datetime.now() - violation.timestamp
                return
            
            # Create new violation
            violation = ThresholdViolation(
                violation_id=f"v_{int(time.time())}_{threshold.threshold_id}",
                threshold_id=threshold.threshold_id,
                metric_name=threshold.metric_name,
                current_value=current_value,
                threshold_value=threshold_value,
                operator=threshold.operator,
                severity=threshold.severity,
                timestamp=datetime.now(),
                metadata={
                    "threshold_name": threshold.name,
                    "threshold_type": threshold.threshold_type.value,
                    "tags": threshold.tags
                }
            )
            
            with self.violation_lock:
                self.active_violations[violation_key] = violation
                self.violation_history.append(violation)
            
            # Update stats
            self.manager_stats["violations_detected"] += 1
            
            # Send notifications
            await self._send_violation_notification(violation)
            
            self.logger.warning(
                f"Threshold violation: {threshold.name} - "
                f"{current_value} {threshold.operator.value} {threshold_value}"
            )
            
        except Exception as e:
            self.logger.error(f"Error handling threshold violation: {e}")

    async def _handle_threshold_recovery(self, threshold: Threshold):
        """Handle threshold recovery"""        try:
            violation_key = f"{threshold.threshold_id}_{threshold.metric_name}"
            
            if violation_key in self.active_violations:
                with self.violation_lock:
                    violation = self.active_violations[violation_key]
                    violation.resolved = True
                    violation.resolution_time = datetime.now()
                    violation.duration = violation.resolution_time - violation.timestamp
                    
                    del self.active_violations[violation_key]
                
                # Update stats
                self.manager_stats["violations_resolved"] += 1
                
                # Send recovery notification
                await self._send_recovery_notification(violation)
                
                self.logger.info(f"Threshold recovered: {threshold.name}")
                
        except Exception as e:
            self.logger.error(f"Error handling threshold recovery: {e}")

    async def _handle_group_violation(self, group: ThresholdGroup,
                                     violation_count: int, total_thresholds: int):
        """Handle threshold group violation"""        try:
            # Group violation handling logic
            self.logger.warning(
                f"Threshold group violation: {group.name} - "
                f"{violation_count}/{total_thresholds} thresholds violated"
            )
            
        except Exception as e:
            self.logger.error(f"Error handling group violation: {e}")

    async def _handle_group_recovery(self, group: ThresholdGroup):
        """Handle threshold group recovery"""        try:
            # Group recovery handling logic
            self.logger.info(f"Threshold group recovered: {group.name}")
            
        except Exception as e:
            self.logger.error(f"Error handling group recovery: {e}")

    async def _send_violation_notification(self, violation: ThresholdViolation):
        """Send violation notification"""        try:
            # Check notification cooldown
            cooldown_key = f"{violation.threshold_id}_{violation.severity.value}"
            if cooldown_key in self.notification_cooldowns:
                last_notification = self.notification_cooldowns[cooldown_key]
                cooldown_period = self._get_notification_cooldown(violation.severity)
                
                if datetime.now() - last_notification < timedelta(seconds=cooldown_period):
                    return  # Skip notification due to cooldown
            
            # Send notification (integration point for alerting systems)
            notification_data = {
                "type": "threshold_violation",
                "violation_id": violation.violation_id,
                "threshold_id": violation.threshold_id,
                "metric_name": violation.metric_name,
                "current_value": violation.current_value,
                "threshold_value": violation.threshold_value,
                "severity": violation.severity.value,
                "timestamp": violation.timestamp.isoformat(),
                "metadata": violation.metadata
            }
            
            # Log notification (in production, send to alerting system)
            self.logger.info(f"Sending violation notification: {json.dumps(notification_data, indent=2)}")
            
            # Update cooldown
            self.notification_cooldowns[cooldown_key] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error sending violation notification: {e}")

    async def _send_recovery_notification(self, violation: ThresholdViolation):
        """Send recovery notification"""        try:
            notification_data = {
                "type": "threshold_recovery",
                "violation_id": violation.violation_id,
                "threshold_id": violation.threshold_id,
                "metric_name": violation.metric_name,
                "duration": violation.duration.total_seconds() if violation.duration else 0,
                "timestamp": violation.resolution_time.isoformat() if violation.resolution_time else None
            }
            
            self.logger.info(f"Sending recovery notification: {json.dumps(notification_data, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"Error sending recovery notification: {e}")

    def _get_notification_cooldown(self, severity: AlertSeverity) -> int:
        """Get notification cooldown period based on severity"""        cooldown_periods = {
            AlertSeverity.INFO: 3600,       # 1 hour
            AlertSeverity.WARNING: 1800,    # 30 minutes
            AlertSeverity.CRITICAL: 600,    # 10 minutes
            AlertSeverity.EMERGENCY: 300    # 5 minutes
        }
        return cooldown_periods.get(severity, 1800)

    async def _update_dynamic_thresholds(self):
        """Update dynamic thresholds based on configuration"""        try:
            for metric_name, config in self.dynamic_configs.items():
                try:
                    new_threshold = await self._calculate_dynamic_threshold(config)
                    
                    # Update all dynamic thresholds for this metric
                    for threshold_id, threshold in self.thresholds.items():
                        if (threshold.metric_name == metric_name and 
                            threshold.threshold_type == ThresholdType.DYNAMIC):
                            self.calculated_thresholds[threshold_id] = new_threshold
                    
                except Exception as e:
                    self.logger.error(f"Error updating dynamic threshold for {metric_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error updating dynamic thresholds: {e}")

    async def _calculate_dynamic_threshold(self, config: DynamicThresholdConfig) -> float:
        """Calculate dynamic threshold based on configuration"""        try:
            metric_history = self.metric_history.get(config.metric_name, deque())
            
            if len(metric_history) < config.min_data_points:
                return 0.0  # Not enough data
            
            # Get data within lookback period
            cutoff_time = datetime.now() - timedelta(seconds=config.lookback_period)
            recent_values = [
                record["value"] for record in metric_history
                if record["timestamp"] >= cutoff_time
            ]
            
            if len(recent_values) < config.min_data_points:
                return 0.0
            
            if config.calculation_method == "percentile":
                percentile = config.percentile or 95.0
                threshold = statistics.quantiles(recent_values, n=100)[int(percentile)-1]
                
            elif config.calculation_method == "standard_deviation":
                mean = statistics.mean(recent_values)
                std_dev = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
                multiplier = config.std_dev_multiplier or 2.0
                threshold = mean + (std_dev * multiplier)
                
            elif config.calculation_method == "moving_average":
                threshold = statistics.mean(recent_values)
                
            else:
                threshold = statistics.mean(recent_values)
            
            # Apply sensitivity multiplier
            threshold *= config.sensitivity
            
            return threshold
            
        except Exception as e:
            self.logger.error(f"Error calculating dynamic threshold: {e}")
            return 0.0

    async def _get_current_metrics(self) -> Dict[str, float]:
        """Get current metric values (integration point)"""        try:
            # This would integrate with the metrics collector
            # For now, return simulated values
            return {
                "cpu_utilization": 65.0,
                "memory_utilization": 72.0,
                "response_time": 280.0,
                "error_rate": 0.015,
                "request_rate": 145.0,
                "queue_length": 18.0,
                "disk_usage": 78.0,
                "network_io": 1250000.0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting current metrics: {e}")
            return {}

    async def _cleanup_old_violations(self):
        """Clean up old and resolved violations"""        try:
            current_time = datetime.now()
            violations_to_remove = []
            
            with self.violation_lock:
                for violation_key, violation in self.active_violations.items():
                    # Remove violations older than timeout
                    if (current_time - violation.timestamp).total_seconds() > self.violation_timeout:
                        violations_to_remove.append(violation_key)
                
                for violation_key in violations_to_remove:
                    del self.active_violations[violation_key]
                    
            # Clean up violation history
            cutoff_time = current_time - timedelta(days=30)
            while (self.violation_history and 
                   self.violation_history[0].timestamp < cutoff_time):
                self.violation_history.popleft()
                
        except Exception as e:
            self.logger.error(f"Error cleaning up violations: {e}")

    async def _analyze_threshold_performance(self):
        """Analyze threshold performance and detect issues"""        try:
            # Analyze false positive rate
            recent_violations = [
                v for v in self.violation_history
                if (datetime.now() - v.timestamp).total_seconds() < 86400  # Last 24 hours
            ]
            
            if recent_violations:
                # Calculate metrics
                total_violations = len(recent_violations)
                resolved_violations = sum(1 for v in recent_violations if v.resolved)
                
                if resolved_violations > 0:
                    avg_resolution_time = statistics.mean([
                        v.duration.total_seconds() for v in recent_violations
                        if v.resolved and v.duration
                    ])
                else:
                    avg_resolution_time = 0
                
                # Log performance metrics
                self.logger.info(
                    f"Threshold performance - Total: {total_violations}, "
                    f"Resolved: {resolved_violations}, Avg resolution: {avg_resolution_time:.1f}s"
                )
                
        except Exception as e:
            self.logger.error(f"Error analyzing threshold performance: {e}")

    async def _optimize_thresholds(self):
        """Optimize thresholds based on performance analysis"""        try:
            # Simple optimization logic
            # In production, this would use more sophisticated ML algorithms
            
            for threshold_id, threshold in self.thresholds.items():
                if threshold.threshold_type == ThresholdType.ADAPTIVE:
                    # Analyze violation patterns and adjust sensitivity
                    recent_violations = [
                        v for v in self.violation_history
                        if (v.threshold_id == threshold_id and 
                            (datetime.now() - v.timestamp).total_seconds() < 86400)
                    ]
                    
                    if len(recent_violations) > 10:  # Too many violations
                        # Consider increasing threshold to reduce false positives
                        pass
                    elif len(recent_violations) == 0:  # No violations
                        # Consider decreasing threshold for better sensitivity
                        pass
                        
        except Exception as e:
            self.logger.error(f"Error optimizing thresholds: {e}")

    async def _initialize_default_thresholds(self):
        """Initialize default thresholds"""        try:
            default_thresholds = [
                Threshold(
                    threshold_id="cpu_high",
                    name="High CPU Utilization",
                    metric_name="cpu_utilization",
                    threshold_type=ThresholdType.STATIC,
                    operator=ComparisonOperator.GREATER_THAN,
                    value=80.0,
                    severity=AlertSeverity.WARNING,
                    tags={"category": "system", "resource": "cpu"}
                ),
                Threshold(
                    threshold_id="cpu_critical",
                    name="Critical CPU Utilization",
                    metric_name="cpu_utilization",
                    threshold_type=ThresholdType.STATIC,
                    operator=ComparisonOperator.GREATER_THAN,
                    value=95.0,
                    severity=AlertSeverity.CRITICAL,
                    tags={"category": "system", "resource": "cpu"}
                ),
                Threshold(
                    threshold_id="memory_high",
                    name="High Memory Utilization",
                    metric_name="memory_utilization",
                    threshold_type=ThresholdType.STATIC,
                    operator=ComparisonOperator.GREATER_THAN,
                    value=85.0,
                    severity=AlertSeverity.WARNING,
                    tags={"category": "system", "resource": "memory"}
                ),
                Threshold(
                    threshold_id="response_time_high",
                    name="High Response Time",
                    metric_name="response_time",
                    threshold_type=ThresholdType.ADAPTIVE,
                    operator=ComparisonOperator.GREATER_THAN,
                    value=1000.0,
                    severity=AlertSeverity.WARNING,
                    tags={"category": "performance", "resource": "application"}
                ),
                Threshold(
                    threshold_id="error_rate_high",
                    name="High Error Rate",
                    metric_name="error_rate",
                    threshold_type=ThresholdType.STATIC,
                    operator=ComparisonOperator.GREATER_THAN,
                    value=0.05,  # 5%
                    severity=AlertSeverity.CRITICAL,
                    tags={"category": "reliability", "resource": "application"}
                )
            ]
            
            for threshold in default_thresholds:
                self.thresholds[threshold.threshold_id] = threshold
                
        except Exception as e:
            self.logger.error(f"Error initializing default thresholds: {e}")

    async def _initialize_dynamic_configs(self):
        """Initialize dynamic threshold configurations"""        try:
            default_configs = [
                DynamicThresholdConfig(
                    metric_name="response_time",
                    calculation_method="percentile",
                    lookback_period=3600,
                    percentile=95.0,
                    sensitivity=1.2
                ),
                DynamicThresholdConfig(
                    metric_name="cpu_utilization",
                    calculation_method="standard_deviation",
                    lookback_period=1800,
                    std_dev_multiplier=2.0,
                    sensitivity=1.1
                )
            ]
            
            for config in default_configs:
                self.dynamic_configs[config.metric_name] = config
                
        except Exception as e:
            self.logger.error(f"Error initializing dynamic configs: {e}")

    async def add_threshold(self, threshold: Threshold):
        """Add a new threshold"""        try:
            with self.threshold_lock:
                self.thresholds[threshold.threshold_id] = threshold
                threshold.updated_at = datetime.now()
                
            self.logger.info(f"Added threshold: {threshold.name}")
            
        except Exception as e:
            self.logger.error(f"Error adding threshold: {e}")
            raise ThresholdException(f"Failed to add threshold: {e}")

    async def update_threshold(self, threshold_id: str, updates: Dict[str, Any]):
        """Update an existing threshold"""        try:
            with self.threshold_lock:
                if threshold_id not in self.thresholds:
                    raise ThresholdException(f"Threshold {threshold_id} not found")
                
                threshold = self.thresholds[threshold_id]
                
                # Apply updates
                for key, value in updates.items():
                    if hasattr(threshold, key):
                        setattr(threshold, key, value)
                
                threshold.updated_at = datetime.now()
                
            self.logger.info(f"Updated threshold: {threshold_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating threshold: {e}")
            raise ThresholdException(f"Failed to update threshold: {e}")

    async def remove_threshold(self, threshold_id: str):
        """Remove a threshold"""        try:
            with self.threshold_lock:
                if threshold_id in self.thresholds:
                    del self.thresholds[threshold_id]
                    
                # Clean up related violations
                violations_to_remove = [
                    k for k, v in self.active_violations.items()
                    if v.threshold_id == threshold_id
                ]
                
                for violation_key in violations_to_remove:
                    del self.active_violations[violation_key]
                    
            self.logger.info(f"Removed threshold: {threshold_id}")
            
        except Exception as e:
            self.logger.error(f"Error removing threshold: {e}")
            raise ThresholdException(f"Failed to remove threshold: {e}")

    async def get_threshold_status(self) -> Dict[str, Any]:
        """Get comprehensive threshold status"""        try:
            return {
                "total_thresholds": len(self.thresholds),
                "enabled_thresholds": len([t for t in self.thresholds.values() if t.enabled]),
                "active_violations": len(self.active_violations),
                "threshold_groups": len(self.threshold_groups),
                "dynamic_configs": len(self.dynamic_configs),
                "monitoring": self.is_monitoring,
                "manager_stats": self.manager_stats,
                "recent_violations": [
                    {
                        "threshold_id": v.threshold_id,
                        "metric_name": v.metric_name,
                        "severity": v.severity.value,
                        "timestamp": v.timestamp.isoformat(),
                        "current_value": v.current_value,
                        "threshold_value": v.threshold_value
                    }
                    for v in list(self.active_violations.values())[-10:]
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting threshold status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for threshold manager"""        try:
            active_tasks = len([task for task in self.monitor_tasks if not task.done()])
            
            # Calculate recent violation rate
            recent_time = datetime.now() - timedelta(hours=1)
            recent_violations = len([
                v for v in self.violation_history
                if v.timestamp >= recent_time
            ])
            
            return {
                "status": "healthy" if self.is_monitoring and active_tasks > 0 else "unhealthy",
                "monitoring": self.is_monitoring,
                "active_tasks": active_tasks,
                "total_tasks": len(self.monitor_tasks),
                "total_thresholds": len(self.thresholds),
                "active_violations": len(self.active_violations),
                "recent_violations_per_hour": recent_violations,
                "average_evaluation_time": self.manager_stats["average_evaluation_time"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
