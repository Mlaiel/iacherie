"""Intelligent Model Retraining Triggers - Advanced ML automation

Extends the existing trigger management system with intelligent model retraining
capabilities, performance degradation detection, and automated training workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class RetrainingTriggerType(Enum):
    """Types of model retraining triggers"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    NEW_DATA_THRESHOLD = "new_data_threshold"
    ERROR_RATE_SPIKE = "error_rate_spike"
    FEEDBACK_SCORE_DROP = "feedback_score_drop"


class TriggerPriority(Enum):
    """Retraining trigger priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class RetrainingCondition:
    """Condition for triggering model retraining"""
    condition_id: str
    condition_type: str
    metric_name: str
    threshold_value: float
    comparison_operator: str  # >, <, >=, <=, ==, !=
    window_size: int = 24  # hours
    min_samples: int = 100
    description: str = ""


@dataclass
class RetrainingAction:
    """Action to take when retraining is triggered"""
    action_id: str
    action_type: str
    model_id: str
    training_config: Dict[str, Any] = field(default_factory=dict)
    notification_config: Dict[str, Any] = field(default_factory=dict)
    validation_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrainingTrigger:
    """Intelligent model retraining trigger definition"""
    trigger_id: str
    name: str
    model_id: str
    trigger_type: RetrainingTriggerType
    conditions: List[RetrainingCondition]
    actions: List[RetrainingAction]
    priority: TriggerPriority = TriggerPriority.MEDIUM
    enabled: bool = True
    cooldown_hours: int = 6  # Minimum time between triggers
    max_retrains_per_day: int = 3
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None


@dataclass
class RetrainingExecution:
    """Model retraining execution record"""
    execution_id: str
    trigger_id: str
    model_id: str
    trigger_type: RetrainingTriggerType
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, cancelled
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""


class IntelligentRetrainingManager:
    """Advanced model retraining automation manager"""
    
    def __init__(self):
        self.triggers: Dict[str, RetrainingTrigger] = {}
        self.executions: List[RetrainingExecution] = []
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = {}
        self.condition_evaluators: Dict[str, Callable] = {}
        self.action_executors: Dict[str, Callable] = {}
        
        # Initialize built-in evaluators and executors
        self._initialize_builtin_components()
        
        # Performance tracking
        self.performance_metrics = {
            "total_triggers": 0,
            "successful_retrains": 0,
            "failed_retrains": 0,
            "average_retrain_time": 0.0,
            "models_monitored": 0
        }
        
        logger.info("Intelligent retraining manager initialized")
    
    
    async def register_retraining_trigger(self, trigger: RetrainingTrigger) -> bool:
        """Register a new retraining trigger"""
        try:
            # Validate trigger configuration
            if not await self._validate_trigger(trigger):
                return False
            
            self.triggers[trigger.trigger_id] = trigger
            
            # Initialize metrics tracking for the model
            if trigger.model_id not in self.metrics_history:
                self.metrics_history[trigger.model_id] = []
            
            logger.info(f"Retraining trigger registered: {trigger.trigger_id} for model {trigger.model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Trigger registration failed: {e}")
            return False
    
    
    async def update_model_metrics(self, model_id: str, metrics: Dict[str, Any]) -> bool:
        """Update metrics for a model and check triggers"""
        try:
            # Add timestamp to metrics
            metrics["timestamp"] = datetime.now()
            
            # Store in history
            if model_id not in self.metrics_history:
                self.metrics_history[model_id] = []
            
            self.metrics_history[model_id].append(metrics)
            
            # Keep only recent metrics (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            self.metrics_history[model_id] = [
                m for m in self.metrics_history[model_id] 
                if m["timestamp"] >= cutoff_date
            ]
            
            # Check all triggers for this model
            await self._check_triggers_for_model(model_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Metrics update failed: {e}")
            return False
    
    
    async def check_all_triggers(self) -> Dict[str, Any]:
        """Check all active triggers and execute retraining if needed"""
        try:
            results = {
                "checked_triggers": 0,
                "triggered_retrains": 0,
                "skipped_cooldown": 0,
                "errors": []
            }
            
            for trigger_id, trigger in self.triggers.items():
                if not trigger.enabled:
                    continue
                
                results["checked_triggers"] += 1
                
                try:
                    # Check cooldown
                    if not await self._check_cooldown(trigger):
                        results["skipped_cooldown"] += 1
                        continue
                    
                    # Check daily limit
                    if not await self._check_daily_limit(trigger):
                        logger.info(f"Daily retrain limit reached for {trigger_id}")
                        continue
                    
                    # Evaluate trigger conditions
                    should_trigger = await self._evaluate_trigger_conditions(trigger)
                    
                    if should_trigger:
                        execution_id = await self._execute_retraining(trigger)
                        if execution_id:
                            results["triggered_retrains"] += 1
                            logger.info(f"Retraining triggered: {trigger_id} -> {execution_id}")
                        else:
                            results["errors"].append(f"Failed to execute retraining for {trigger_id}")
                    
                except Exception as e:
                    error_msg = f"Error checking trigger {trigger_id}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
            
            return results
            
        except Exception as e:
            logger.error(f"Trigger checking failed: {e}")
            return {"error": str(e)}
    
    
    async def get_retraining_status(self, model_id: str = None) -> Dict[str, Any]:
        """Get retraining status and history"""
        try:
            if model_id:
                executions = [e for e in self.executions if e.model_id == model_id]
                triggers = [t for t in self.triggers.values() if t.model_id == model_id]
            else:
                executions = self.executions
                triggers = list(self.triggers.values())
            
            # Calculate statistics
            total_executions = len(executions)
            successful_executions = sum(1 for e in executions if e.status == "completed")
            failed_executions = sum(1 for e in executions if e.status == "failed")
            running_executions = sum(1 for e in executions if e.status == "running")
            
            # Recent executions (last 7 days)
            recent_cutoff = datetime.now() - timedelta(days=7)
            recent_executions = [e for e in executions if e.started_at >= recent_cutoff]
            
            return {
                "summary": {
                    "total_executions": total_executions,
                    "successful_executions": successful_executions,
                    "failed_executions": failed_executions,
                    "running_executions": running_executions,
                    "success_rate": successful_executions / total_executions if total_executions > 0 else 0
                },
                "recent_activity": {
                    "last_7_days": len(recent_executions),
                    "recent_executions": [
                        {
                            "execution_id": e.execution_id,
                            "model_id": e.model_id,
                            "trigger_type": e.trigger_type.value,
                            "status": e.status,
                            "started_at": e.started_at.isoformat(),
                            "completed_at": e.completed_at.isoformat() if e.completed_at else None
                        } for e in recent_executions[-10:]  # Last 10 recent
                    ]
                },
                "active_triggers": len([t for t in triggers if t.enabled]),
                "models_monitored": len(set(t.model_id for t in triggers)),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Status retrieval failed: {e}")
            return {"error": str(e)}
    
    
    async def cancel_retraining(self, execution_id: str) -> bool:
        """Cancel a running retraining execution"""
        try:
            execution = next((e for e in self.executions if e.execution_id == execution_id), None)
            
            if not execution:
                logger.error(f"Execution not found: {execution_id}")
                return False
            
            if execution.status != "running":
                logger.warning(f"Cannot cancel execution {execution_id}: status is {execution.status}")
                return False
            
            # Update execution status
            execution.status = "cancelled"
            execution.completed_at = datetime.now()
            execution.error_message = "Cancelled by user"
            
            logger.info(f"Retraining execution cancelled: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Retraining cancellation failed: {e}")
            return False
    
    
    async def _check_triggers_for_model(self, model_id: str):
        """Check all triggers for a specific model"""
        model_triggers = [t for t in self.triggers.values() if t.model_id == model_id and t.enabled]
        
        for trigger in model_triggers:
            try:
                # Check cooldown and limits
                if not await self._check_cooldown(trigger) or not await self._check_daily_limit(trigger):
                    continue
                
                # Evaluate conditions
                should_trigger = await self._evaluate_trigger_conditions(trigger)
                
                if should_trigger:
                    await self._execute_retraining(trigger)
                    
            except Exception as e:
                logger.error(f"Error checking trigger {trigger.trigger_id}: {e}")
    
    
    async def _validate_trigger(self, trigger: RetrainingTrigger) -> bool:
        """Validate trigger configuration"""
        if not trigger.trigger_id or not trigger.model_id:
            logger.error("Trigger must have trigger_id and model_id")
            return False
        
        if not trigger.conditions:
            logger.error("Trigger must have at least one condition")
            return False
        
        if not trigger.actions:
            logger.error("Trigger must have at least one action")
            return False
        
        # Validate conditions
        for condition in trigger.conditions:
            if condition.condition_type not in self.condition_evaluators:
                logger.error(f"Unknown condition type: {condition.condition_type}")
                return False
        
        return True
    
    
    async def _check_cooldown(self, trigger: RetrainingTrigger) -> bool:
        """Check if trigger is in cooldown period"""
        if trigger.last_triggered is None:
            return True
        
        cooldown_end = trigger.last_triggered + timedelta(hours=trigger.cooldown_hours)
        return datetime.now() >= cooldown_end
    
    
    async def _check_daily_limit(self, trigger: RetrainingTrigger) -> bool:
        """Check if daily retraining limit has been reached"""
        today = datetime.now().date()
        today_executions = [
            e for e in self.executions 
            if e.trigger_id == trigger.trigger_id and e.started_at.date() == today
        ]
        
        return len(today_executions) < trigger.max_retrains_per_day
    
    
    async def _evaluate_trigger_conditions(self, trigger: RetrainingTrigger) -> bool:
        """Evaluate all conditions for a trigger"""
        try:
            model_metrics = self.metrics_history.get(trigger.model_id, [])
            
            if not model_metrics:
                logger.warning(f"No metrics available for model {trigger.model_id}")
                return False
            
            # All conditions must be met (AND logic)
            for condition in trigger.conditions:
                if not await self._evaluate_condition(condition, model_metrics):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    
    async def _evaluate_condition(self, condition: RetrainingCondition, 
                                  model_metrics: List[Dict[str, Any]]) -> bool:
        """Evaluate a single condition"""
        try:
            evaluator = self.condition_evaluators.get(condition.condition_type)
            
            if not evaluator:
                logger.error(f"No evaluator for condition type: {condition.condition_type}")
                return False
            
            return await evaluator(condition, model_metrics)
            
        except Exception as e:
            logger.error(f"Individual condition evaluation failed: {e}")
            return False
    
    
    async def _execute_retraining(self, trigger: RetrainingTrigger) -> Optional[str]:
        """Execute retraining actions for a trigger"""
        try:
            execution_id = f"retrain_{int(datetime.now().timestamp())}"
            
            # Create execution record
            execution = RetrainingExecution(
                execution_id=execution_id,
                trigger_id=trigger.trigger_id,
                model_id=trigger.model_id,
                trigger_type=trigger.trigger_type,
                started_at=datetime.now()
            )
            
            self.executions.append(execution)
            
            # Update trigger last triggered time
            trigger.last_triggered = datetime.now()
            
            # Execute all actions
            for action in trigger.actions:
                try:
                    executor = self.action_executors.get(action.action_type)
                    if executor:
                        await executor(action, execution)
                    else:
                        logger.warning(f"No executor for action type: {action.action_type}")
                        
                except Exception as e:
                    logger.error(f"Action execution failed: {e}")
                    execution.error_message = str(e)
                    execution.status = "failed"
            
            # Update performance metrics
            self.performance_metrics["total_triggers"] += 1
            
            logger.info(f"Retraining execution started: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Retraining execution failed: {e}")
            return None
    
    
    def _initialize_builtin_components(self):
        """Initialize built-in condition evaluators and action executors"""
        # Condition evaluators
        self.condition_evaluators.update({
            "performance_threshold": self._evaluate_performance_threshold,
            "drift_detection": self._evaluate_drift_detection,
            "error_rate": self._evaluate_error_rate,
            "data_volume": self._evaluate_data_volume,
            "feedback_score": self._evaluate_feedback_score
        })
        
        # Action executors
        self.action_executors.update({
            "start_training": self._execute_start_training,
            "send_notification": self._execute_send_notification,
            "create_backup": self._execute_create_backup,
            "update_config": self._execute_update_config
        })
    
    
    async def _evaluate_performance_threshold(self, condition: RetrainingCondition, 
                                              metrics: List[Dict[str, Any]]) -> bool:
        """Evaluate performance threshold condition"""
        try:
            # Get recent metrics within window
            window_start = datetime.now() - timedelta(hours=condition.window_size)
            recent_metrics = [
                m for m in metrics 
                if m["timestamp"] >= window_start and condition.metric_name in m
            ]
            
            if len(recent_metrics) < condition.min_samples:
                return False
            
            # Get metric values
            values = [m[condition.metric_name] for m in recent_metrics]
            avg_value = sum(values) / len(values)
            
            # Compare with threshold
            if condition.comparison_operator == ">":
                return avg_value > condition.threshold_value
            elif condition.comparison_operator == "<":
                return avg_value < condition.threshold_value
            elif condition.comparison_operator == ">=":
                return avg_value >= condition.threshold_value
            elif condition.comparison_operator == "<=":
                return avg_value <= condition.threshold_value
            elif condition.comparison_operator == "==":
                return abs(avg_value - condition.threshold_value) < 0.001
            elif condition.comparison_operator == "!=":
                return abs(avg_value - condition.threshold_value) >= 0.001
            
            return False
            
        except Exception as e:
            logger.error(f"Performance threshold evaluation failed: {e}")
            return False
    
    
    async def _evaluate_drift_detection(self, condition: RetrainingCondition,
                                        metrics: List[Dict[str, Any]]) -> bool:
        """Evaluate drift detection condition"""
        try:
            # Simplified drift detection - check for drift_score metric
            recent_metrics = [
                m for m in metrics[-condition.min_samples:]
                if "drift_score" in m
            ]
            
            if not recent_metrics:
                return False
            
            latest_drift_score = recent_metrics[-1]["drift_score"]
            return latest_drift_score > condition.threshold_value
            
        except Exception as e:
            logger.error(f"Drift detection evaluation failed: {e}")
            return False
    
    
    async def _evaluate_error_rate(self, condition: RetrainingCondition,
                                   metrics: List[Dict[str, Any]]) -> bool:
        """Evaluate error rate condition"""
        try:
            window_start = datetime.now() - timedelta(hours=condition.window_size)
            recent_metrics = [
                m for m in metrics 
                if m["timestamp"] >= window_start and "error_rate" in m
            ]
            
            if len(recent_metrics) < condition.min_samples:
                return False
            
            avg_error_rate = sum(m["error_rate"] for m in recent_metrics) / len(recent_metrics)
            return avg_error_rate > condition.threshold_value
            
        except Exception as e:
            logger.error(f"Error rate evaluation failed: {e}")
            return False
    
    
    async def _evaluate_data_volume(self, condition: RetrainingCondition,
                                    metrics: List[Dict[str, Any]]) -> bool:
        """Evaluate data volume condition"""
        try:
            recent_metrics = [m for m in metrics if "data_volume" in m]
            
            if not recent_metrics:
                return False
            
            total_volume = sum(m["data_volume"] for m in recent_metrics)
            return total_volume >= condition.threshold_value
            
        except Exception as e:
            logger.error(f"Data volume evaluation failed: {e}")
            return False
    
    
    async def _evaluate_feedback_score(self, condition: RetrainingCondition,
                                       metrics: List[Dict[str, Any]]) -> bool:
        """Evaluate feedback score condition"""
        try:
            window_start = datetime.now() - timedelta(hours=condition.window_size)
            recent_metrics = [
                m for m in metrics 
                if m["timestamp"] >= window_start and "feedback_score" in m
            ]
            
            if len(recent_metrics) < condition.min_samples:
                return False
            
            avg_score = sum(m["feedback_score"] for m in recent_metrics) / len(recent_metrics)
            return avg_score < condition.threshold_value  # Low score triggers retraining
            
        except Exception as e:
            logger.error(f"Feedback score evaluation failed: {e}")
            return False
    
    
    async def _execute_start_training(self, action: RetrainingAction, 
                                      execution: RetrainingExecution):
        """Execute model training action"""
        try:
            # In a real implementation, this would interface with the training system
            logger.info(f"Starting training for model {action.model_id}")
            
            # Simulate training process
            await asyncio.sleep(1)  # Placeholder for actual training
            
            execution.status = "completed"
            execution.completed_at = datetime.now()
            execution.metrics = {"training_started": True}
            
            self.performance_metrics["successful_retrains"] += 1
            
        except Exception as e:
            logger.error(f"Training execution failed: {e}")
            execution.status = "failed"
            execution.error_message = str(e)
            self.performance_metrics["failed_retrains"] += 1
    
    
    async def _execute_send_notification(self, action: RetrainingAction,
                                         execution: RetrainingExecution):
        """Execute notification action"""
        try:
            # Send notification about retraining
            logger.info(f"Sending retraining notification for model {action.model_id}")
            
            # In a real implementation, this would send actual notifications
            # via email, Slack, etc.
            
        except Exception as e:
            logger.error(f"Notification execution failed: {e}")
    
    
    async def _execute_create_backup(self, action: RetrainingAction,
                                     execution: RetrainingExecution):
        """Execute model backup action"""
        try:
            logger.info(f"Creating backup for model {action.model_id}")
            
            # In a real implementation, this would create model backups
            
        except Exception as e:
            logger.error(f"Backup execution failed: {e}")
    
    
    async def _execute_update_config(self, action: RetrainingAction,
                                     execution: RetrainingExecution):
        """Execute configuration update action"""
        try:
            logger.info(f"Updating configuration for model {action.model_id}")
            
            # In a real implementation, this would update model configurations
            
        except Exception as e:
            logger.error(f"Config update execution failed: {e}")