"""
Enterprise workflow automation with intelligent triggers and actions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
from typing import Dict, List, Callable, Optional, Any, Set, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import logging
from collections import defaultdict

from ..core.events import EventBus, Event
from ..core.exceptions import AutomationException
from ..models.content import ContentItem
from ..services.ai.content_analyzer import ContentAnalyzer
from ..services.protection.fingerprinting import FingerprintService
from ..services.notification.manager import NotificationManager
from ..utils.pattern_matching import PatternMatcher
from ..utils.metrics import MetricsCollector


class TriggerType(Enum):
    """Enhanced trigger types for automation."""
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    CONTENT_BASED = "content_based"
    THRESHOLD_BASED = "threshold_based"
    PATTERN_BASED = "pattern_based"
    MANUAL = "manual"
    CONDITIONAL = "conditional"
    COMPOSITE = "composite"


class ActionType(Enum):
    """Types of automation actions."""
    WORKFLOW_START = "workflow_start"
    NOTIFICATION_SEND = "notification_send"
    CONTENT_ANALYSIS = "content_analysis"
    PROTECTION_SCAN = "protection_scan"
    REPORT_GENERATION = "report_generation"
    DATA_EXPORT = "data_export"
    SYSTEM_MAINTENANCE = "system_maintenance"
    CUSTOM_SCRIPT = "custom_script"


class AutomationStatus(Enum):
    """Enhanced automation status."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    FAILED = "failed"
    TESTING = "testing"
    SCHEDULED = "scheduled"


class ExecutionMode(Enum):
    """Automation execution modes."""
    IMMEDIATE = "immediate"
    QUEUED = "queued"
    BATCH = "batch"
    PARALLEL = "parallel"


@dataclass
class TriggerCondition:
    """Complex trigger condition with evaluation logic."""
    name: str
    condition_type: str  # comparison, regex, function, composite
    field_path: str  # dot notation path to field
    operator: str  # eq, ne, gt, lt, gte, lte, in, not_in, contains, regex, custom
    expected_value: Any
    weight: float = 1.0
    required: bool = True
    
    def evaluate(self, context: Dict[str, Any]) -> tuple[bool, float]:
        """Evaluate condition and return (matches, confidence_score)."""
        try:
            # Get field value using dot notation
            field_value = self._get_field_value(context, self.field_path)
            
            # Evaluate based on operator
            matches = self._evaluate_operator(field_value, self.operator, self.expected_value)
            confidence = self.weight if matches else 0.0
            
            return matches, confidence
            
        except Exception as e:
            logging.error(f"Error evaluating condition {self.name}: {e}")
            return False, 0.0
    
    def _get_field_value(self, context: Dict, field_path: str) -> Any:
        """Get nested field value using dot notation."""
        keys = field_path.split('.')
        value = context
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif hasattr(value, key):
                value = getattr(value, key)
            else:
                return None
        
        return value
    
    def _evaluate_operator(self, field_value: Any, operator: str, expected: Any) -> bool:
        """Evaluate operator-based comparison."""
        operators = {
            "eq": lambda a, b: a == b,
            "ne": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
            "in": lambda a, b: a in b,
            "not_in": lambda a, b: a not in b,
            "contains": lambda a, b: b in str(a),
            "startswith": lambda a, b: str(a).startswith(str(b)),
            "endswith": lambda a, b: str(a).endswith(str(b))
        }
        
        if operator in operators:
            return operators[operator](field_value, expected)
        
        return False


@dataclass
class AutomationRule:
    """Enhanced automation rule with complex conditions and actions."""
    id: str
    name: str
    description: str
    trigger_type: TriggerType
    action_type: ActionType
    conditions: List[TriggerCondition] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.IMMEDIATE
    priority: int = 5  # 1-10, higher is more important
    enabled: bool = True
    status: AutomationStatus = AutomationStatus.ACTIVE
    
    # Scheduling and limits
    schedule_expression: Optional[str] = None  # Cron expression
    rate_limit_per_hour: Optional[int] = None
    max_executions_per_day: Optional[int] = None
    
    # Execution tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_execution_time: float = 0.0
    
    # Context and metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    owner_id: Optional[str] = None
    
    def evaluate_conditions(self, context: Dict[str, Any]) -> tuple[bool, float]:
        """Evaluate all conditions and return overall match and confidence."""
        if not self.conditions:
            return True, 1.0
        
        total_weight = sum(condition.weight for condition in self.conditions)
        if total_weight == 0:
            return True, 1.0
        
        matched_weight = 0.0
        required_conditions_met = True
        
        for condition in self.conditions:
            matches, confidence = condition.evaluate(context)
            
            if condition.required and not matches:
                required_conditions_met = False
                break
            
            if matches:
                matched_weight += confidence
        
        if not required_conditions_met:
            return False, 0.0
        
        overall_confidence = matched_weight / total_weight
        overall_match = overall_confidence >= 0.7  # 70% threshold
        
        return overall_match, overall_confidence
    
    def can_execute(self) -> tuple[bool, str]:
        """Check if rule can be executed considering limits."""
        if not self.enabled or self.status != AutomationStatus.ACTIVE:
            return False, f"Rule is {self.status.value}"
        
        now = datetime.utcnow()
        
        # Check rate limiting
        if self.rate_limit_per_hour:
            hour_ago = now - timedelta(hours=1)
            recent_executions = self.execution_count  # Simplified, would need actual tracking
            if recent_executions >= self.rate_limit_per_hour:
                return False, "Rate limit exceeded"
        
        # Check daily limits
        if self.max_executions_per_day:
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_executions = self.execution_count  # Simplified
            if daily_executions >= self.max_executions_per_day:
                return False, "Daily execution limit reached"
        
        return True, "Can execute"
    
    def record_execution(self, success: bool, duration: float):
        """Record execution statistics."""
        self.last_executed = datetime.utcnow()
        self.execution_count += 1
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        # Update average execution time
        if self.execution_count > 1:
            self.avg_execution_time = (
                (self.avg_execution_time * (self.execution_count - 1) + duration) / 
                self.execution_count
            )
        else:
            self.avg_execution_time = duration


class AutomationActionHandler:
    """Base handler for automation actions."""
    
    def __init__(self, action_type: ActionType):
        self.action_type = action_type
        self.logger = logging.getLogger(f"automation.handler.{action_type.value}")
    
    async def execute(
        self, 
        action_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute automation action."""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Executing action {self.action_type.value}")
            
            result = await self._execute_action(action_config, context)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": result,
                "duration": duration,
                "action_type": self.action_type.value,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.logger.error(f"Action {self.action_type.value} failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "duration": duration,
                "action_type": self.action_type.value,
                "failed_at": datetime.utcnow().isoformat()
            }
    
    async def _execute_action(
        self, 
        action_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the specific action - to be overridden."""
        raise NotImplementedError


class WorkflowStartActionHandler(AutomationActionHandler):
    """Handler for starting workflows."""
    
    def __init__(self):
        super().__init__(ActionType.WORKFLOW_START)
        # Would inject workflow orchestrator
        # self.workflow_orchestrator = WorkflowOrchestrator()
    
    async def _execute_action(self, action_config: Dict, context: Dict) -> Dict:
        """Start a workflow."""
        template_id = action_config.get("template_id")
        input_data = action_config.get("input_data", {})
        
        # Merge context data
        input_data.update(context)
        
        # Placeholder for actual workflow starting
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        
        return {
            "workflow_id": workflow_id,
            "template_id": template_id,
            "started_at": datetime.utcnow().isoformat()
        }


class NotificationActionHandler(AutomationActionHandler):
    """Handler for sending notifications."""
    
    def __init__(self):
        super().__init__(ActionType.NOTIFICATION_SEND)
        self.notification_manager = NotificationManager()
    
    async def _execute_action(self, action_config: Dict, context: Dict) -> Dict:
        """Send notification."""
        message = action_config.get("message", "Automation trigger activated")
        channels = action_config.get("channels", ["email"])
        recipients = action_config.get("recipients", [])
        urgent = action_config.get("urgent", False)
        
        # Template message with context variables
        templated_message = self._template_message(message, context)
        
        notification_id = await self.notification_manager.send_notification(
            type="automation_trigger",
            message=templated_message,
            channels=channels,
            recipients=recipients,
            urgent=urgent
        )
        
        return {
            "notification_id": notification_id,
            "message": templated_message,
            "channels": channels,
            "recipients_count": len(recipients)
        }
    
    def _template_message(self, message: str, context: Dict) -> str:
        """Template message with context variables."""
        try:
            return message.format(**context)
        except (KeyError, ValueError):
            return message


class ContentAnalysisActionHandler(AutomationActionHandler):
    """Handler for content analysis actions."""
    
    def __init__(self):
        super().__init__(ActionType.CONTENT_ANALYSIS)
        self.content_analyzer = ContentAnalyzer()
    
    async def _execute_action(self, action_config: Dict, context: Dict) -> Dict:
        """Execute content analysis."""
        content_items = action_config.get("content_items", [])
        analysis_type = action_config.get("analysis_type", "quick")
        
        # Get content from context if not provided
        if not content_items and "content_item" in context:
            content_items = [context["content_item"]]
        
        analysis_results = []
        
        for content_item in content_items:
            if analysis_type == "comprehensive":
                result = await self.content_analyzer.analyze_comprehensive(content_item)
            else:
                result = await self.content_analyzer.analyze_quick(content_item)
            
            analysis_results.append({
                "content_id": content_item.get("id"),
                "analysis": result
            })
        
        return {
            "analyzed_items": len(content_items),
            "analysis_results": analysis_results,
            "analysis_type": analysis_type
        }


class ProtectionScanActionHandler(AutomationActionHandler):
    """Handler for protection scanning actions."""
    
    def __init__(self):
        super().__init__(ActionType.PROTECTION_SCAN)
        self.fingerprint_service = FingerprintService()
    
    async def _execute_action(self, action_config: Dict, context: Dict) -> Dict:
        """Execute protection scan."""
        scan_type = action_config.get("scan_type", "fingerprint")
        platforms = action_config.get("platforms", ["youtube", "instagram"])
        content_ids = action_config.get("content_ids", [])
        
        scan_results = []
        
        if scan_type == "fingerprint":
            for content_id in content_ids:
                result = await self.fingerprint_service.scan_for_violations(
                    content_id, platforms
                )
                scan_results.append({
                    "content_id": content_id,
                    "violations": result.get("violations", []),
                    "scan_platforms": platforms
                })
        
        return {
            "scan_type": scan_type,
            "scanned_content_items": len(content_ids),
            "platforms_scanned": len(platforms),
            "total_violations": sum(len(r.get("violations", [])) for r in scan_results),
            "scan_results": scan_results
        }


class EnterpriseWorkflowAutomation:
    """Enterprise-grade workflow automation engine."""
    
    def __init__(self):
        self.logger = logging.getLogger("workflow.automation")
        self.event_bus = EventBus()
        self.metrics = MetricsCollector()
        self.pattern_matcher = PatternMatcher()
        
        # Automation state
        self.automation_rules = {}
        self.execution_queue = asyncio.Queue()
        self.event_queue = asyncio.Queue()
        
        # Action handlers
        self.action_handlers = {
            ActionType.WORKFLOW_START: WorkflowStartActionHandler(),
            ActionType.NOTIFICATION_SEND: NotificationActionHandler(),
            ActionType.CONTENT_ANALYSIS: ContentAnalysisActionHandler(),
            ActionType.PROTECTION_SCAN: ProtectionScanActionHandler()
        }
        
        # Configuration
        self.max_concurrent_executions = 10
        self.event_processing_batch_size = 50
        self.rule_evaluation_timeout = 30
        
        # Runtime state
        self.running = False
        self.active_executions = set()
        self.execution_stats = defaultdict(int)
    
    async def initialize(self):
        """Initialize automation engine."""
        self.logger.info("Initializing workflow automation engine")
        
        # Set up event subscriptions
        await self._setup_event_subscriptions()
        
        # Start background tasks
        asyncio.create_task(self._event_processing_loop())
        asyncio.create_task(self._execution_loop())
        asyncio.create_task(self._monitoring_loop())
        
        self.running = True
    
    async def _setup_event_subscriptions(self):
        """Set up subscriptions to relevant events."""
        # Subscribe to content events
        self.event_bus.subscribe("content.uploaded", self._handle_content_event)
        self.event_bus.subscribe("content.analyzed", self._handle_content_event)
        self.event_bus.subscribe("content.published", self._handle_content_event)
        
        # Subscribe to protection events
        self.event_bus.subscribe("protection.violation_detected", self._handle_protection_event)
        self.event_bus.subscribe("protection.scan_completed", self._handle_protection_event)
        
        # Subscribe to system events
        self.event_bus.subscribe("system.threshold_exceeded", self._handle_system_event)
        self.event_bus.subscribe("system.error_occurred", self._handle_system_event)
        
        # Subscribe to workflow events
        self.event_bus.subscribe("workflow.completed", self._handle_workflow_event)
        self.event_bus.subscribe("workflow.failed", self._handle_workflow_event)
    
    async def register_automation_rule(self, rule: AutomationRule) -> str:
        """Register a new automation rule."""
        rule_id = rule.id
        self.automation_rules[rule_id] = rule
        
        self.logger.info(f"Registered automation rule: {rule.name} ({rule_id})")
        
        return rule_id
    
    async def create_content_upload_automation(
        self,
        user_id: str,
        trigger_conditions: Dict[str, Any]
    ) -> str:
        """Create automation for content upload events."""
        rule_id = f"content_upload_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Define conditions
        conditions = [
            TriggerCondition(
                name="user_match",
                condition_type="comparison",
                field_path="user_id",
                operator="eq",
                expected_value=user_id,
                weight=1.0,
                required=True
            ),
            TriggerCondition(
                name="content_type_filter",
                condition_type="comparison",
                field_path="content_item.content_type",
                operator="in",
                expected_value=trigger_conditions.get("content_types", ["audio", "video", "image"]),
                weight=0.8
            )
        ]
        
        # Define actions
        actions = [
            {
                "type": ActionType.CONTENT_ANALYSIS.value,
                "config": {
                    "analysis_type": "comprehensive",
                    "include_ai_insights": True
                }
            },
            {
                "type": ActionType.WORKFLOW_START.value,
                "config": {
                    "template_id": "content_processing",
                    "input_data": {
                        "user_id": user_id,
                        "processing_options": trigger_conditions.get("processing_options", {})
                    }
                }
            }
        ]
        
        rule = AutomationRule(
            id=rule_id,
            name=f"Content Upload Automation - {user_id}",
            description="Automatically process uploaded content",
            trigger_type=TriggerType.EVENT_BASED,
            action_type=ActionType.WORKFLOW_START,
            conditions=conditions,
            actions=actions,
            execution_mode=ExecutionMode.IMMEDIATE,
            priority=7,
            owner_id=user_id,
            metadata={
                "automation_type": "content_upload",
                "user_id": user_id,
                "trigger_conditions": trigger_conditions
            }
        )
        
        await self.register_automation_rule(rule)
        return rule_id
    
    async def create_protection_monitoring_automation(
        self,
        user_id: str,
        content_ids: List[str],
        monitoring_config: Dict[str, Any]
    ) -> str:
        """Create automation for protection monitoring."""
        rule_id = f"protection_monitor_{user_id}_{uuid.uuid4().hex[:8]}"
        
        conditions = [
            TriggerCondition(
                name="violation_detected",
                condition_type="comparison",
                field_path="event_type",
                operator="eq",
                expected_value="protection.violation_detected",
                weight=1.0,
                required=True
            ),
            TriggerCondition(
                name="content_match",
                condition_type="comparison",
                field_path="content_id",
                operator="in",
                expected_value=content_ids,
                weight=1.0,
                required=True
            ),
            TriggerCondition(
                name="confidence_threshold",
                condition_type="comparison",
                field_path="violation.confidence",
                operator="gte",
                expected_value=monitoring_config.get("confidence_threshold", 0.8),
                weight=0.9
            )
        ]
        
        actions = [
            {
                "type": ActionType.NOTIFICATION_SEND.value,
                "config": {
                    "message": "Content protection violation detected for content {content_id}. Confidence: {violation.confidence}",
                    "channels": monitoring_config.get("notification_channels", ["email"]),
                    "recipients": [user_id],
                    "urgent": True
                }
            }
        ]
        
        if monitoring_config.get("auto_takedown", False):
            actions.append({
                "type": ActionType.CUSTOM_SCRIPT.value,
                "config": {
                    "script": "initiate_takedown_process",
                    "parameters": {
                        "content_id": "{content_id}",
                        "violation_url": "{violation.url}"
                    }
                }
            })
        
        rule = AutomationRule(
            id=rule_id,
            name=f"Protection Monitoring - {user_id}",
            description="Monitor and respond to content protection violations",
            trigger_type=TriggerType.EVENT_BASED,
            action_type=ActionType.NOTIFICATION_SEND,
            conditions=conditions,
            actions=actions,
            execution_mode=ExecutionMode.IMMEDIATE,
            priority=9,  # High priority for protection
            owner_id=user_id,
            rate_limit_per_hour=100,  # Prevent spam
            metadata={
                "automation_type": "protection_monitoring",
                "user_id": user_id,
                "content_ids": content_ids,
                "monitoring_config": monitoring_config
            }
        )
        
        await self.register_automation_rule(rule)
        return rule_id
    
    async def create_performance_threshold_automation(
        self,
        threshold_config: Dict[str, Any]
    ) -> str:
        """Create automation for performance threshold monitoring."""
        rule_id = f"performance_threshold_{uuid.uuid4().hex[:8]}"
        
        conditions = [
            TriggerCondition(
                name="threshold_exceeded",
                condition_type="comparison",
                field_path="metric_value",
                operator="gte",
                expected_value=threshold_config.get("threshold", 0.8),
                weight=1.0,
                required=True
            ),
            TriggerCondition(
                name="metric_type",
                condition_type="comparison",
                field_path="metric_type",
                operator="eq",
                expected_value=threshold_config.get("metric_type"),
                weight=1.0,
                required=True
            )
        ]
        
        actions = [
            {
                "type": ActionType.NOTIFICATION_SEND.value,
                "config": {
                    "message": "Performance threshold exceeded: {metric_type} = {metric_value}",
                    "channels": ["email", "slack"],
                    "recipients": threshold_config.get("alert_recipients", []),
                    "urgent": threshold_config.get("critical", False)
                }
            }
        ]
        
        if threshold_config.get("auto_scale", False):
            actions.append({
                "type": ActionType.SYSTEM_MAINTENANCE.value,
                "config": {
                    "action": "auto_scale",
                    "parameters": threshold_config.get("scaling_params", {})
                }
            })
        
        rule = AutomationRule(
            id=rule_id,
            name=f"Performance Threshold - {threshold_config.get('metric_type')}",
            description="Monitor and respond to performance threshold breaches",
            trigger_type=TriggerType.THRESHOLD_BASED,
            action_type=ActionType.NOTIFICATION_SEND,
            conditions=conditions,
            actions=actions,
            execution_mode=ExecutionMode.IMMEDIATE,
            priority=8,
            rate_limit_per_hour=10,  # Prevent alert storms
            metadata={
                "automation_type": "performance_threshold",
                "threshold_config": threshold_config
            }
        )
        
        await self.register_automation_rule(rule)
        return rule_id
    
    async def trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger event for automation processing."""
        event = {
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.utcnow().isoformat(),
            "event_id": uuid.uuid4().hex
        }
        
        await self.event_queue.put(event)
        self.logger.debug(f"Queued event: {event_type}")
    
    async def _event_processing_loop(self):
        """Main event processing loop."""
        while self.running:
            try:
                # Process events in batches
                events_batch = []
                
                # Collect batch of events
                for _ in range(self.event_processing_batch_size):
                    try:
                        event = await asyncio.wait_for(
                            self.event_queue.get(),
                            timeout=1.0
                        )
                        events_batch.append(event)
                    except asyncio.TimeoutError:
                        break
                
                # Process each event
                for event in events_batch:
                    await self._process_event(event)
                
                if not events_batch:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Error in event processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_event(self, event: Dict[str, Any]):
        """Process individual event against automation rules."""
        event_type = event["event_type"]
        event_data = event["event_data"]
        
        # Find matching rules
        matching_rules = []
        
        for rule in self.automation_rules.values():
            if not rule.enabled or rule.status != AutomationStatus.ACTIVE:
                continue
            
            if rule.trigger_type not in [TriggerType.EVENT_BASED, TriggerType.COMPOSITE]:
                continue
            
            # Evaluate conditions
            context = {
                "event_type": event_type,
                **event_data,
                "timestamp": event["timestamp"],
                "event_id": event["event_id"]
            }
            
            try:
                matches, confidence = rule.evaluate_conditions(context)
                
                if matches:
                    can_execute, reason = rule.can_execute()
                    if can_execute:
                        matching_rules.append((rule, confidence, context))
                    else:
                        self.logger.debug(f"Rule {rule.id} matched but cannot execute: {reason}")
                
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.id}: {e}")
        
        # Sort by priority and confidence
        matching_rules.sort(key=lambda x: (x[0].priority, x[1]), reverse=True)
        
        # Queue for execution
        for rule, confidence, context in matching_rules:
            execution_item = {
                "rule": rule,
                "context": context,
                "confidence": confidence,
                "triggered_at": datetime.utcnow().isoformat(),
                "execution_id": uuid.uuid4().hex
            }
            
            await self.execution_queue.put(execution_item)
    
    async def _execution_loop(self):
        """Main automation execution loop."""
        while self.running:
            try:
                # Check execution capacity
                if len(self.active_executions) >= self.max_concurrent_executions:
                    await asyncio.sleep(0.5)
                    continue
                
                try:
                    execution_item = await asyncio.wait_for(
                        self.execution_queue.get(),
                        timeout=1.0
                    )
                    
                    # Execute asynchronously
                    execution_id = execution_item["execution_id"]
                    self.active_executions.add(execution_id)
                    
                    asyncio.create_task(
                        self._execute_automation_rule(execution_item)
                    )
                    
                except asyncio.TimeoutError:
                    continue
                    
            except Exception as e:
                self.logger.error(f"Error in execution loop: {e}")
                await asyncio.sleep(1)
    
    async def _execute_automation_rule(self, execution_item: Dict[str, Any]):
        """Execute automation rule actions."""
        execution_id = execution_item["execution_id"]
        rule = execution_item["rule"]
        context = execution_item["context"]
        
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Executing automation rule: {rule.name} ({rule.id})")
            
            execution_results = []
            
            # Execute all actions
            for action in rule.actions:
                action_type = ActionType(action["type"])
                action_config = action.get("config", {})
                
                if action_type in self.action_handlers:
                    handler = self.action_handlers[action_type]
                    result = await handler.execute(action_config, context)
                    execution_results.append(result)
                else:
                    self.logger.warning(f"No handler for action type: {action_type}")
                    execution_results.append({
                        "success": False,
                        "error": f"No handler for action type: {action_type.value}"
                    })
            
            # Calculate overall success
            overall_success = all(result.get("success", False) for result in execution_results)
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Record execution statistics
            rule.record_execution(overall_success, duration)
            
            # Record metrics
            self.metrics.record_automation_execution(
                rule_id=rule.id,
                success=overall_success,
                duration=duration,
                actions_count=len(rule.actions)
            )
            
            # Update execution stats
            self.execution_stats["total_executions"] += 1
            if overall_success:
                self.execution_stats["successful_executions"] += 1
            else:
                self.execution_stats["failed_executions"] += 1
            
            self.logger.info(
                f"Automation rule {rule.id} executed {'successfully' if overall_success else 'with errors'} "
                f"in {duration:.2f}s"
            )
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            rule.record_execution(False, duration)
            
            self.execution_stats["total_executions"] += 1
            self.execution_stats["failed_executions"] += 1
            
            self.logger.error(f"Error executing automation rule {rule.id}: {e}")
            
        finally:
            # Remove from active executions
            self.active_executions.discard(execution_id)
    
    async def _monitoring_loop(self):
        """Monitor automation health and performance."""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Log execution statistics
                total = self.execution_stats.get("total_executions", 0)
                successful = self.execution_stats.get("successful_executions", 0)
                failed = self.execution_stats.get("failed_executions", 0)
                
                success_rate = (successful / total * 100) if total > 0 else 0
                
                self.logger.info(
                    f"Automation stats - Total: {total}, Success: {successful}, "
                    f"Failed: {failed}, Success Rate: {success_rate:.1f}%"
                )
                
                # Check for problematic rules
                for rule in self.automation_rules.values():
                    if rule.execution_count > 10:  # Only check rules with enough data
                        rule_success_rate = (rule.success_count / rule.execution_count * 100)
                        if rule_success_rate < 70:  # Less than 70% success rate
                            self.logger.warning(
                                f"Rule {rule.id} has low success rate: {rule_success_rate:.1f}%"
                            )
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    async def _handle_content_event(self, event: Event):
        """Handle content-related events."""
        await self.trigger_event(event.type, event.data)
    
    async def _handle_protection_event(self, event: Event):
        """Handle protection-related events."""
        await self.trigger_event(event.type, event.data)
    
    async def _handle_system_event(self, event: Event):
        """Handle system-related events."""
        await self.trigger_event(event.type, event.data)
    
    async def _handle_workflow_event(self, event: Event):
        """Handle workflow-related events."""
        await self.trigger_event(event.type, event.data)
    
    def get_automation_rule(self, rule_id: str) -> Optional[AutomationRule]:
        """Get automation rule by ID."""
        return self.automation_rules.get(rule_id)
    
    def list_automation_rules(
        self, 
        owner_id: Optional[str] = None,
        trigger_type: Optional[TriggerType] = None,
        status: Optional[AutomationStatus] = None
    ) -> List[AutomationRule]:
        """List automation rules with optional filtering."""
        rules = list(self.automation_rules.values())
        
        if owner_id:
            rules = [r for r in rules if r.owner_id == owner_id]
        
        if trigger_type:
            rules = [r for r in rules if r.trigger_type == trigger_type]
        
        if status:
            rules = [r for r in rules if r.status == status]
        
        return rules
    
    def disable_automation_rule(self, rule_id: str) -> bool:
        """Disable automation rule."""
        rule = self.automation_rules.get(rule_id)
        if rule:
            rule.enabled = False
            rule.status = AutomationStatus.DISABLED
            self.logger.info(f"Disabled automation rule: {rule_id}")
            return True
        return False
    
    def enable_automation_rule(self, rule_id: str) -> bool:
        """Enable automation rule."""
        rule = self.automation_rules.get(rule_id)
        if rule:
            rule.enabled = True
            rule.status = AutomationStatus.ACTIVE
            self.logger.info(f"Enabled automation rule: {rule_id}")
            return True
        return False
    
    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation engine statistics."""
        total_rules = len(self.automation_rules)
        active_rules = sum(1 for r in self.automation_rules.values() if r.enabled)
        
        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "disabled_rules": total_rules - active_rules,
            "active_executions": len(self.active_executions),
            "queue_length": self.execution_queue.qsize(),
            "event_queue_length": self.event_queue.qsize(),
            "execution_stats": dict(self.execution_stats),
            "engine_status": "running" if self.running else "stopped"
        }
        """Trigger an event that may activate automation rules."""
        await self.event_queue.put({
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.utcnow()
        })

    async def start_automation_engine(self):
        """Start the automation engine."""
        self.is_running = True
        
        # Start event processing
        event_task = asyncio.create_task(self._process_events())
        
        # Start scheduled task processing
        schedule_task = asyncio.create_task(self._process_scheduled_tasks())
        
        try:
            await asyncio.gather(event_task, schedule_task)
        except Exception as e:
            print(f"Automation engine error: {e}")
        finally:
            self.is_running = False

    async def stop_automation_engine(self):
        """Stop the automation engine."""
        self.is_running = False

    async def _process_events(self):
        """Process events from the queue."""
        while self.is_running:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # Find matching rules
                for rule in self.rules.values():
                    if (rule.status == AutomationStatus.ACTIVE and 
                        rule.trigger_type == TriggerType.EVENT_BASED):
                        
                        # Check if rule matches event
                        if self._rule_matches_event(rule, event):
                            await self._execute_rule(rule, event["data"])
                            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Event processing error: {e}")

    async def _process_scheduled_tasks(self):
        """Process time-based automation rules."""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                for rule in self.rules.values():
                    if (rule.status == AutomationStatus.ACTIVE and 
                        rule.trigger_type == TriggerType.TIME_BASED):
                        
                        if self._should_execute_scheduled_rule(rule, current_time):
                            await self._execute_rule(rule, {"current_time": current_time})
                
                # Sleep for a minute before checking again
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"Scheduled task processing error: {e}")

    def _rule_matches_event(self, rule: AutomationRule, event: Dict) -> bool:
        """Check if a rule matches the given event."""
        event_type = event.get("type")
        event_data = event.get("data", {})
        
        # Check if rule is configured for this event type
        if "event_type" in rule.conditions and rule.conditions["event_type"] != event_type:
            return False
        
        # Check other conditions against event data
        return rule.matches_conditions(event_data)

    def _should_execute_scheduled_rule(self, rule: AutomationRule, current_time: datetime) -> bool:
        """Check if a scheduled rule should be executed now."""
        if "schedule" not in rule.conditions:
            return False
        
        schedule = rule.conditions["schedule"]
        
        # Handle different schedule types
        if schedule.get("type") == "interval":
            if not rule.last_executed:
                return True
            
            interval_minutes = schedule.get("minutes", 60)
            next_execution = rule.last_executed + timedelta(minutes=interval_minutes)
            return current_time >= next_execution
        
        elif schedule.get("type") == "daily":
            target_hour = schedule.get("hour", 9)
            target_minute = schedule.get("minute", 0)
            
            if not rule.last_executed:
                return (current_time.hour == target_hour and 
                       current_time.minute >= target_minute)
            
            # Check if we've passed the target time since last execution
            last_date = rule.last_executed.date()
            current_date = current_time.date()
            
            if current_date > last_date:
                return (current_time.hour == target_hour and 
                       current_time.minute >= target_minute)
        
        return False

    async def _execute_rule(self, rule: AutomationRule, context: Dict):
        """Execute an automation rule."""
        try:
            rule.execution_count += 1
            rule.last_executed = datetime.utcnow()
            
            # Execute the rule action
            if asyncio.iscoroutinefunction(rule.action):
                await rule.action(context)
            else:
                rule.action(context)
            
            rule.success_count += 1
            
        except Exception as e:
            rule.failure_count += 1
            rule.status = AutomationStatus.FAILED
            print(f"Rule execution failed: {rule.name} - {str(e)}")

    def create_content_upload_automation(self) -> str:
        """Create automation for new content uploads."""
        async def handle_content_upload(context: Dict):
            content_info = context.get("content", {})
            print(f"Auto-processing new content: {content_info.get('title', 'Unknown')}")
            
            # Trigger content processing pipeline
            from backend.app.workflow.pipeline import ContentPipeline
            pipeline = ContentPipeline.create_content_processing_pipeline(content_info)
            await pipeline.execute()
        
        rule = AutomationRule(
            name="Auto Process New Content",
            trigger_type=TriggerType.EVENT_BASED,
            action=handle_content_upload,
            conditions={
                "event_type": "content.uploaded",
                "media_type": {"contains": ""}  # Any media type
            }
        )
        
        return self.add_rule(rule)

    def create_seo_optimization_automation(self) -> str:
        """Create automation for SEO optimization of popular content."""
        async def optimize_popular_content(context: Dict):
            print("Running SEO optimization for popular content")
            # Mock: Find content with high engagement and optimize
            # In reality, this would query the database for popular content
        
        rule = AutomationRule(
            name="Daily SEO Optimization",
            trigger_type=TriggerType.TIME_BASED,
            action=optimize_popular_content,
            conditions={
                "schedule": {
                    "type": "daily",
                    "hour": 10,
                    "minute": 0
                }
            }
        )
        
        return self.add_rule(rule)

    def create_collaboration_matching_automation(self) -> str:
        """Create automation for finding collaboration opportunities."""
        async def find_collaborations(context: Dict):
            print("Finding new collaboration opportunities")
            # Mock: Analyze creator content and find matches
            # In reality, this would use AI to find suitable collaborators
        
        rule = AutomationRule(
            name="Weekly Collaboration Matching",
            trigger_type=TriggerType.TIME_BASED,
            action=find_collaborations,
            conditions={
                "schedule": {
                    "type": "daily",
                    "hour": 14,
                    "minute": 0
                }
            }
        )
        
        return self.add_rule(rule)

    def create_content_protection_automation(self) -> str:
        """Create automation for content protection monitoring."""
        async def monitor_content_protection(context: Dict):
            content_info = context.get("content", {})
            print(f"Monitoring protection for: {content_info.get('title', 'Unknown')}")
            
            # Mock: Check for unauthorized use across platforms
            # In reality, this would scan platforms for similar content
        
        rule = AutomationRule(
            name="Content Protection Monitoring",
            trigger_type=TriggerType.EVENT_BASED,
            action=monitor_content_protection,
            conditions={
                "event_type": "content.published",
                "protection_enabled": True
            }
        )
        
        return self.add_rule(rule)

    def create_analytics_reporting_automation(self) -> str:
        """Create automation for generating analytics reports."""
        async def generate_analytics_report(context: Dict):
            print("Generating weekly analytics report")
            # Mock: Compile performance metrics and send report
            # In reality, this would gather metrics and generate reports
        
        rule = AutomationRule(
            name="Weekly Analytics Report",
            trigger_type=TriggerType.TIME_BASED,
            action=generate_analytics_report,
            conditions={
                "schedule": {
                    "type": "daily",  # For demo, using daily
                    "hour": 9,
                    "minute": 30
                }
            }
        )
        
        return self.add_rule(rule)

    def get_automation_status(self) -> Dict:
        """Get status of all automation rules."""
        status_summary = {
            "total_rules": len(self.rules),
            "active_rules": sum(1 for r in self.rules.values() if r.status == AutomationStatus.ACTIVE),
            "paused_rules": sum(1 for r in self.rules.values() if r.status == AutomationStatus.PAUSED),
            "failed_rules": sum(1 for r in self.rules.values() if r.status == AutomationStatus.FAILED),
            "engine_running": self.is_running,
            "rules": {}
        }
        
        for rule_id, rule in self.rules.items():
            status_summary["rules"][rule_id] = {
                "name": rule.name,
                "status": rule.status.value,
                "trigger_type": rule.trigger_type.value,
                "execution_count": rule.execution_count,
                "success_rate": (rule.success_count / rule.execution_count * 100) if rule.execution_count > 0 else 0,
                "last_executed": rule.last_executed.isoformat() if rule.last_executed else None
            }
        
        return status_summary

    def setup_default_automations(self) -> Dict[str, str]:
        """Setup default automation rules for the system."""
        automation_ids = {}
        
        automation_ids["content_upload"] = self.create_content_upload_automation()
        automation_ids["seo_optimization"] = self.create_seo_optimization_automation()
        automation_ids["collaboration_matching"] = self.create_collaboration_matching_automation()
        automation_ids["content_protection"] = self.create_content_protection_automation()
        automation_ids["analytics_reporting"] = self.create_analytics_reporting_automation()
        
        return automation_ids
