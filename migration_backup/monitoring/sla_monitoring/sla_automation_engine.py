"""SLA Automation Engine
Advanced automated SLA monitoring, self-healing, predictive alerting, and intelligent optimization system.

⚠️ PROPRIETARY CODE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use, distribution, or modification is strictly prohibited.
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from collections import deque, defaultdict
import json
import time
from enum import Enum

class AutomationAction(Enum):
    """Types of automated actions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    OPTIMIZE_DATABASE = "optimize_database"
    REDIRECT_TRAFFIC = "redirect_traffic"
    ALERT_ESCALATION = "alert_escalation"
    SELF_HEALING = "self_healing"
    PREDICTIVE_SCALING = "predictive_scaling"
    LOAD_BALANCING = "load_balancing"

class AutomationTrigger(Enum):
    """Automation trigger types"""
    SLA_VIOLATION = "sla_violation"
    THRESHOLD_BREACH = "threshold_breach"
    PREDICTIVE_ALERT = "predictive_alert"
    PATTERN_DETECTION = "pattern_detection"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    CASCADE_FAILURE = "cascade_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"

class AutomationPriority(Enum):
    """Priority levels for automation actions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    PREVENTIVE = "preventive"

@dataclass
class AutomationRule:
    """Automation rule configuration"""
    rule_id: str
    name: str
    description: str
    trigger: AutomationTrigger
    conditions: Dict[str, Any]
    actions: List[AutomationAction]
    priority: AutomationPriority
    enabled: bool = True
    cooldown_minutes: int = 15
    max_executions_per_hour: int = 10
    requires_approval: bool = False
    success_threshold: float = 95.0
    created_at: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None
    execution_count: int = 0

@dataclass
class AutomationExecution:
    """Automation execution tracking"""
    execution_id: str
    rule_id: str
    trigger_event: str
    actions_executed: List[AutomationAction]
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    impact_metrics: Dict[str, float] = field(default_factory=dict)
    rollback_performed: bool = False

@dataclass
class SLAAutomationTargets:
    """SLA Automation Engine targets"""
    # Automation Response SLA
    automation_response_seconds: float = 30.0  # <30s automation response
    self_healing_success_rate: float = 95.0  # 95% self-healing success
    false_positive_rate: float = 1.0  # <1% false positive rate
    automation_availability: float = 99.99  # 99.99% automation availability
    
    # Predictive Accuracy SLA
    prediction_accuracy: float = 80.0  # 80% prediction accuracy
    prediction_lead_time_minutes: float = 15.0  # 15min prediction lead time
    alert_precision: float = 85.0  # 85% alert precision
    alert_recall: float = 90.0  # 90% alert recall
    
    # Performance Impact SLA
    automation_overhead_percentage: float = 2.0  # <2% performance overhead
    rollback_success_rate: float = 99.0  # 99% rollback success rate
    recovery_time_minutes: float = 5.0  # <5min recovery time
    cascade_prevention_rate: float = 95.0  # 95% cascade failure prevention

class SLAAutomationEngine:
    """
    Advanced SLA Automation Engine
    Provides automated monitoring, self-healing, predictive alerting, and intelligent optimization
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.targets = SLAAutomationTargets()
        
        # Automation state
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.executions: Dict[str, AutomationExecution] = {}
        self.active_automations: Dict[str, datetime] = {}
        self.cooldown_tracking: Dict[str, datetime] = {}
        
        # Monitoring and metrics
        self.sla_violations: deque = deque(maxlen=1000)
        self.performance_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.prediction_model: Dict[str, Any] = {}
        self.pattern_detection: Dict[str, List[Any]] = defaultdict(list)
        
        # Alert and notification system
        self.alerts: List[Dict[str, Any]] = []
        self.notification_handlers: Dict[str, Callable] = {}
        
        # Action handlers
        self.action_handlers: Dict[AutomationAction, Callable] = {}
        
        self._setup_default_rules()
        self._setup_action_handlers()
        
    def _setup_default_rules(self):
        """Initialize default automation rules"""
        default_rules = [
            AutomationRule(
                rule_id="api_response_time_scaling",
                name="API Response Time Auto-Scaling",
                description="Auto-scale when API response times exceed threshold",
                trigger=AutomationTrigger.THRESHOLD_BREACH,
                conditions={
                    "metric": "api_response_time",
                    "threshold": 500.0,
                    "duration_minutes": 5,
                    "comparison": "greater_than"
                },
                actions=[AutomationAction.SCALE_UP, AutomationAction.LOAD_BALANCING],
                priority=AutomationPriority.HIGH,
                cooldown_minutes=10
            ),
            AutomationRule(
                rule_id="database_performance_optimization",
                name="Database Performance Self-Healing",
                description="Optimize database when performance degrades",
                trigger=AutomationTrigger.SLA_VIOLATION,
                conditions={
                    "component": "database",
                    "metric": "query_response_time",
                    "threshold": 200.0
                },
                actions=[AutomationAction.OPTIMIZE_DATABASE, AutomationAction.CLEAR_CACHE],
                priority=AutomationPriority.HIGH,
                cooldown_minutes=30
            ),
            AutomationRule(
                rule_id="content_processing_recovery",
                name="Content Processing Pipeline Recovery",
                description="Restart content processing services on failure",
                trigger=AutomationTrigger.SLA_VIOLATION,
                conditions={
                    "component": "content_processing",
                    "error_rate": ">5%"
                },
                actions=[AutomationAction.RESTART_SERVICE, AutomationAction.SELF_HEALING],
                priority=AutomationPriority.CRITICAL,
                cooldown_minutes=5
            ),
            AutomationRule(
                rule_id="predictive_scaling",
                name="Predictive Capacity Scaling",
                description="Scale resources based on predicted demand",
                trigger=AutomationTrigger.PREDICTIVE_ALERT,
                conditions={
                    "prediction_confidence": ">80%",
                    "expected_load_increase": ">50%"
                },
                actions=[AutomationAction.PREDICTIVE_SCALING],
                priority=AutomationPriority.PREVENTIVE,
                cooldown_minutes=60
            )
        ]
        
        for rule in default_rules:
            self.automation_rules[rule.rule_id] = rule
    
    def _setup_action_handlers(self):
        """Setup action handlers for different automation actions"""
        self.action_handlers = {
            AutomationAction.SCALE_UP: self._handle_scale_up,
            AutomationAction.SCALE_DOWN: self._handle_scale_down,
            AutomationAction.RESTART_SERVICE: self._handle_restart_service,
            AutomationAction.CLEAR_CACHE: self._handle_clear_cache,
            AutomationAction.OPTIMIZE_DATABASE: self._handle_optimize_database,
            AutomationAction.REDIRECT_TRAFFIC: self._handle_redirect_traffic,
            AutomationAction.ALERT_ESCALATION: self._handle_alert_escalation,
            AutomationAction.SELF_HEALING: self._handle_self_healing,
            AutomationAction.PREDICTIVE_SCALING: self._handle_predictive_scaling,
            AutomationAction.LOAD_BALANCING: self._handle_load_balancing
        }
    
    async def process_sla_violation(self, violation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process SLA violation and trigger appropriate automation"""
        try:
            violation_id = violation_data.get("violation_id", f"violation_{int(time.time())}")
            component = violation_data.get("component", "unknown")
            metric = violation_data.get("metric", "unknown")
            severity = violation_data.get("severity", "medium")
            
            self.logger.info(f"Processing SLA violation: {violation_id} for {component}:{metric}")
            
            # Record violation
            self.sla_violations.append({
                "timestamp": datetime.now(),
                "violation_id": violation_id,
                "component": component,
                "metric": metric,
                "severity": severity,
                "data": violation_data
            })
            
            # Find matching automation rules
            matching_rules = self._find_matching_rules(violation_data, AutomationTrigger.SLA_VIOLATION)
            
            executed_actions = []
            for rule in matching_rules:
                if self._can_execute_rule(rule):
                    execution_result = await self._execute_automation_rule(rule, violation_data)
                    executed_actions.append(execution_result)
            
            # Generate predictive alerts based on violation pattern
            await self._analyze_violation_patterns(violation_data)
            
            return {
                "violation_id": violation_id,
                "executed_actions": executed_actions,
                "automation_response_time": (datetime.now() - datetime.fromisoformat(violation_data.get("timestamp", datetime.now().isoformat()))).total_seconds()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing SLA violation: {e}")
            raise
    
    async def process_threshold_breach(self, metric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process metric threshold breach and trigger automation"""
        try:
            metric_name = metric_data.get("metric_name", "unknown")
            current_value = metric_data.get("current_value", 0)
            threshold = metric_data.get("threshold", 0)
            component = metric_data.get("component", "unknown")
            
            self.logger.info(f"Processing threshold breach: {metric_name} = {current_value} (threshold: {threshold})")
            
            # Find matching automation rules
            matching_rules = self._find_matching_rules(metric_data, AutomationTrigger.THRESHOLD_BREACH)
            
            executed_actions = []
            for rule in matching_rules:
                if self._can_execute_rule(rule):
                    execution_result = await self._execute_automation_rule(rule, metric_data)
                    executed_actions.append(execution_result)
            
            return {
                "metric_name": metric_name,
                "current_value": current_value,
                "threshold": threshold,
                "executed_actions": executed_actions
            }
            
        except Exception as e:
            self.logger.error(f"Error processing threshold breach: {e}")
            raise
    
    async def predict_sla_violations(self, time_horizon_minutes: int = 30) -> List[Dict[str, Any]]:
        """Predict potential SLA violations using historical data and patterns"""
        try:
            current_time = datetime.now()
            predictions = []
            
            # Analyze performance metrics for predictive patterns
            for metric_name, values in self.performance_metrics.items():
                if len(values) < 10:  # Need minimum data points
                    continue
                
                # Simple trend analysis for prediction
                recent_values = list(values)[-10:]
                trend = self._calculate_trend(recent_values)
                
                if abs(trend) > 0.1:  # Significant trend detected
                    predicted_value = recent_values[-1] + (trend * time_horizon_minutes)
                    
                    # Check if predicted value would violate SLA
                    sla_threshold = self._get_sla_threshold(metric_name)
                    if sla_threshold and predicted_value > sla_threshold:
                        prediction = {
                            "metric_name": metric_name,
                            "current_value": recent_values[-1],
                            "predicted_value": predicted_value,
                            "sla_threshold": sla_threshold,
                            "confidence": self._calculate_prediction_confidence(recent_values, trend),
                            "time_to_violation_minutes": self._calculate_time_to_violation(recent_values[-1], sla_threshold, trend),
                            "prediction_time": current_time.isoformat(),
                            "horizon_minutes": time_horizon_minutes
                        }
                        
                        predictions.append(prediction)
                        
                        # Trigger predictive automation if confidence is high
                        if prediction["confidence"] > 80.0:
                            await self._trigger_predictive_automation(prediction)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting SLA violations: {e}")
            raise
    
    def _find_matching_rules(self, event_data: Dict[str, Any], trigger_type: AutomationTrigger) -> List[AutomationRule]:
        """Find automation rules that match the given event"""
        matching_rules = []
        
        for rule in self.automation_rules.values():
            if not rule.enabled or rule.trigger != trigger_type:
                continue
            
            if self._evaluate_rule_conditions(rule, event_data):
                matching_rules.append(rule)
        
        # Sort by priority
        priority_order = {
            AutomationPriority.CRITICAL: 0,
            AutomationPriority.HIGH: 1,
            AutomationPriority.MEDIUM: 2,
            AutomationPriority.LOW: 3,
            AutomationPriority.PREVENTIVE: 4
        }
        
        matching_rules.sort(key=lambda r: priority_order.get(r.priority, 5))
        return matching_rules
    
    def _evaluate_rule_conditions(self, rule: AutomationRule, event_data: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met"""
        try:
            conditions = rule.conditions
            
            # Check component match
            if "component" in conditions and conditions["component"] != event_data.get("component", ""):
                return False
            
            # Check metric match
            if "metric" in conditions and conditions["metric"] != event_data.get("metric", ""):
                return False
            
            # Check threshold conditions
            if "threshold" in conditions:
                threshold = conditions["threshold"]
                current_value = event_data.get("current_value", 0)
                comparison = conditions.get("comparison", "greater_than")
                
                if comparison == "greater_than" and current_value <= threshold:
                    return False
                elif comparison == "less_than" and current_value >= threshold:
                    return False
                elif comparison == "equals" and current_value != threshold:
                    return False
            
            # Check duration conditions
            if "duration_minutes" in conditions:
                # This would require historical tracking - simplified for now
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating rule conditions: {e}")
            return False
    
    def _can_execute_rule(self, rule: AutomationRule) -> bool:
        """Check if rule can be executed based on cooldown and limits"""
        current_time = datetime.now()
        
        # Check cooldown
        if rule.rule_id in self.cooldown_tracking:
            last_execution = self.cooldown_tracking[rule.rule_id]
            if (current_time - last_execution).total_seconds() < (rule.cooldown_minutes * 60):
                return False
        
        # Check execution limits per hour
        one_hour_ago = current_time - timedelta(hours=1)
        recent_executions = [
            exec for exec in self.executions.values()
            if exec.rule_id == rule.rule_id and exec.start_time >= one_hour_ago
        ]
        
        if len(recent_executions) >= rule.max_executions_per_hour:
            return False
        
        return True
    
    async def _execute_automation_rule(self, rule: AutomationRule, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an automation rule"""
        try:
            execution_id = f"exec_{rule.rule_id}_{int(time.time())}"
            execution = AutomationExecution(
                execution_id=execution_id,
                rule_id=rule.rule_id,
                trigger_event=json.dumps(event_data),
                actions_executed=[],
                start_time=datetime.now()
            )
            
            self.logger.info(f"Executing automation rule: {rule.name} (ID: {rule.rule_id})")
            
            # Execute actions
            for action in rule.actions:
                try:
                    if action in self.action_handlers:
                        action_result = await self.action_handlers[action](event_data, rule)
                        execution.actions_executed.append(action)
                        
                        if not action_result.get("success", False):
                            execution.error_message = action_result.get("error", "Action failed")
                            break
                    else:
                        self.logger.warning(f"No handler for action: {action}")
                
                except Exception as e:
                    execution.error_message = str(e)
                    self.logger.error(f"Error executing action {action}: {e}")
                    break
            
            execution.end_time = datetime.now()
            execution.success = len(execution.actions_executed) == len(rule.actions) and not execution.error_message
            
            # Update tracking
            self.executions[execution_id] = execution
            self.cooldown_tracking[rule.rule_id] = execution.end_time
            rule.last_executed = execution.end_time
            rule.execution_count += 1
            
            # Generate alert
            await self._generate_automation_alert(rule, execution, event_data)
            
            return {
                "execution_id": execution_id,
                "rule_id": rule.rule_id,
                "success": execution.success,
                "actions_executed": [action.value for action in execution.actions_executed],
                "execution_time_seconds": (execution.end_time - execution.start_time).total_seconds(),
                "error_message": execution.error_message
            }
            
        except Exception as e:
            self.logger.error(f"Error executing automation rule: {e}")
            raise
    
    # Action handlers
    async def _handle_scale_up(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle scale up action"""
        try:
            component = event_data.get("component", "unknown")
            current_instances = event_data.get("current_instances", 1)
            target_instances = min(current_instances + 2, 10)  # Scale up by 2, max 10
            
            self.logger.info(f"Scaling up {component} from {current_instances} to {target_instances} instances")
            
            # Simulate scaling operation
            await asyncio.sleep(1)  # Simulate API call delay
            
            return {
                "success": True,
                "action": "scale_up",
                "component": component,
                "from_instances": current_instances,
                "to_instances": target_instances
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_scale_down(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle scale down action"""
        try:
            component = event_data.get("component", "unknown")
            current_instances = event_data.get("current_instances", 1)
            target_instances = max(current_instances - 1, 1)  # Scale down by 1, min 1
            
            self.logger.info(f"Scaling down {component} from {current_instances} to {target_instances} instances")
            
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "action": "scale_down",
                "component": component,
                "from_instances": current_instances,
                "to_instances": target_instances
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_restart_service(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle service restart action"""
        try:
            component = event_data.get("component", "unknown")
            service_name = event_data.get("service_name", component)
            
            self.logger.info(f"Restarting service: {service_name}")
            
            await asyncio.sleep(2)  # Simulate restart time
            
            return {
                "success": True,
                "action": "restart_service",
                "service_name": service_name,
                "restart_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_clear_cache(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle cache clearing action"""
        try:
            cache_type = event_data.get("cache_type", "redis")
            
            self.logger.info(f"Clearing {cache_type} cache")
            
            await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "action": "clear_cache",
                "cache_type": cache_type,
                "cleared_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_optimize_database(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle database optimization action"""
        try:
            database_name = event_data.get("database_name", "main")
            
            self.logger.info(f"Optimizing database: {database_name}")
            
            await asyncio.sleep(3)  # Simulate optimization time
            
            return {
                "success": True,
                "action": "optimize_database",
                "database_name": database_name,
                "optimized_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_redirect_traffic(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle traffic redirection action"""
        try:
            from_endpoint = event_data.get("endpoint", "unknown")
            to_endpoint = event_data.get("backup_endpoint", "backup")
            
            self.logger.info(f"Redirecting traffic from {from_endpoint} to {to_endpoint}")
            
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "action": "redirect_traffic",
                "from_endpoint": from_endpoint,
                "to_endpoint": to_endpoint,
                "redirected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_alert_escalation(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle alert escalation action"""
        try:
            severity = event_data.get("severity", "medium")
            escalation_level = "manager" if severity == "high" else "senior"
            
            self.logger.info(f"Escalating alert to {escalation_level}")
            
            return {
                "success": True,
                "action": "alert_escalation",
                "escalation_level": escalation_level,
                "escalated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_self_healing(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle self-healing action"""
        try:
            component = event_data.get("component", "unknown")
            
            self.logger.info(f"Initiating self-healing for {component}")
            
            # Simulate self-healing process
            healing_actions = ["restart_service", "clear_cache", "reset_connections"]
            
            await asyncio.sleep(2)
            
            return {
                "success": True,
                "action": "self_healing",
                "component": component,
                "healing_actions": healing_actions,
                "healed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_predictive_scaling(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle predictive scaling action"""
        try:
            predicted_load = event_data.get("predicted_load", 1.0)
            current_capacity = event_data.get("current_capacity", 100)
            target_capacity = int(current_capacity * predicted_load * 1.2)  # 20% buffer
            
            self.logger.info(f"Predictive scaling to {target_capacity}% capacity based on predicted load {predicted_load}")
            
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "action": "predictive_scaling",
                "predicted_load": predicted_load,
                "target_capacity": target_capacity,
                "scaled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_load_balancing(self, event_data: Dict[str, Any], rule: AutomationRule) -> Dict[str, Any]:
        """Handle load balancing action"""
        try:
            self.logger.info("Optimizing load balancing configuration")
            
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "action": "load_balancing",
                "optimized_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend from time series data"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear regression slope calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x_squared_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x_squared_sum - x_sum * x_sum)
        return slope
    
    def _calculate_prediction_confidence(self, values: List[float], trend: float) -> float:
        """Calculate confidence level for prediction"""
        if len(values) < 3:
            return 50.0
        
        # Calculate R-squared for trend line
        mean_y = statistics.mean(values)
        ss_tot = sum((y - mean_y) ** 2 for y in values)
        
        predicted_values = [values[0] + trend * i for i in range(len(values))]
        ss_res = sum((values[i] - predicted_values[i]) ** 2 for i in range(len(values)))
        
        if ss_tot == 0:
            return 50.0
        
        r_squared = 1 - (ss_res / ss_tot)
        confidence = max(0, min(100, r_squared * 100))
        
        return confidence
    
    def _calculate_time_to_violation(self, current_value: float, threshold: float, trend: float) -> float:
        """Calculate estimated time to SLA violation"""
        if trend <= 0:
            return float('inf')
        
        time_to_violation = (threshold - current_value) / trend
        return max(0, time_to_violation)
    
    def _get_sla_threshold(self, metric_name: str) -> Optional[float]:
        """Get SLA threshold for a given metric"""
        # This would typically fetch from SLA configuration
        thresholds = {
            "api_response_time": 200.0,
            "database_query_time": 100.0,
            "cpu_utilization": 80.0,
            "memory_utilization": 85.0,
            "error_rate": 1.0
        }
        return thresholds.get(metric_name)
    
    async def _trigger_predictive_automation(self, prediction: Dict[str, Any]):
        """Trigger automation based on prediction"""
        event_data = {
            "trigger": "predictive_alert",
            "metric_name": prediction["metric_name"],
            "predicted_value": prediction["predicted_value"],
            "confidence": prediction["confidence"],
            "time_to_violation_minutes": prediction["time_to_violation_minutes"]
        }
        
        matching_rules = self._find_matching_rules(event_data, AutomationTrigger.PREDICTIVE_ALERT)
        
        for rule in matching_rules:
            if self._can_execute_rule(rule):
                await self._execute_automation_rule(rule, event_data)
    
    async def _analyze_violation_patterns(self, violation_data: Dict[str, Any]):
        """Analyze patterns in SLA violations for future prediction"""
        component = violation_data.get("component", "unknown")
        metric = violation_data.get("metric", "unknown")
        
        pattern_key = f"{component}:{metric}"
        self.pattern_detection[pattern_key].append({
            "timestamp": datetime.now(),
            "severity": violation_data.get("severity", "medium"),
            "value": violation_data.get("current_value", 0)
        })
        
        # Keep only recent patterns (last 100)
        if len(self.pattern_detection[pattern_key]) > 100:
            self.pattern_detection[pattern_key] = self.pattern_detection[pattern_key][-100:]
    
    async def _generate_automation_alert(self, rule: AutomationRule, execution: AutomationExecution, event_data: Dict[str, Any]):
        """Generate alert for automation execution"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "title": f"Automation Executed: {rule.name}",
            "message": f"Rule '{rule.name}' executed {len(execution.actions_executed)} actions",
            "severity": "info" if execution.success else "warning",
            "component": "sla_automation_engine",
            "metadata": {
                "rule_id": rule.rule_id,
                "execution_id": execution.execution_id,
                "success": execution.success,
                "actions": [action.value for action in execution.actions_executed],
                "trigger_event": event_data
            }
        }
        
        self.alerts.append(alert)
        self.logger.info(f"Automation Alert - {alert['title']}: {alert['message']}")
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
    
    async def get_automation_summary(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive automation engine summary"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            
            # Filter recent executions
            recent_executions = [
                exec for exec in self.executions.values()
                if exec.start_time >= cutoff_time
            ]
            
            # Calculate metrics
            total_executions = len(recent_executions)
            successful_executions = len([exec for exec in recent_executions if exec.success])
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 100
            
            # Calculate average response time
            response_times = [
                (exec.end_time - exec.start_time).total_seconds()
                for exec in recent_executions if exec.end_time
            ]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            # Rule execution statistics
            rule_stats = defaultdict(int)
            for exec in recent_executions:
                rule_stats[exec.rule_id] += 1
            
            return {
                "time_window_hours": time_window_hours,
                "automation_summary": {
                    "total_executions": total_executions,
                    "successful_executions": successful_executions,
                    "success_rate": success_rate,
                    "avg_response_time_seconds": avg_response_time,
                    "active_rules": len([r for r in self.automation_rules.values() if r.enabled]),
                    "total_rules": len(self.automation_rules)
                },
                "rule_execution_stats": dict(rule_stats),
                "sla_compliance": {
                    "automation_response_compliant": avg_response_time <= self.targets.automation_response_seconds,
                    "self_healing_success_compliant": success_rate >= self.targets.self_healing_success_rate,
                    "automation_availability_compliant": True  # Simplified
                },
                "recent_violations": len(self.sla_violations),
                "active_automations": len(self.active_automations),
                "cooldown_rules": len(self.cooldown_tracking)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating automation summary: {e}")
            raise

# Global instance for easy access
sla_automation_engine = SLAAutomationEngine()