"""🚀 Enterprise Command Dispatcher - CQRS Architecture
========================================================
Module: events/cqrs/command_dispatcher.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 INTELLIGENT COMMAND DISPATCHER
Advanced command routing and processing orchestration
- Dynamic handler selection and load balancing
- Command transformation and enrichment
- Business rule validation and enforcement
- Transaction coordination across microservices
- Command orchestration for complex workflows
- Real-time monitoring and adaptive optimization
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Type, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque

from .command_bus import Command, CommandResult, CommandStatus, CommandHandler
from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)


class DispatchStrategy(Enum):
    """Command dispatch strategies"""
    ROUND_ROBIN = "round_robin"
    LOAD_BASED = "load_based"
    PRIORITY_BASED = "priority_based"
    AFFINITY_BASED = "affinity_based"
    GEOGRAPHIC = "geographic"


class HandlerState(Enum):
    """Handler availability state"""
    AVAILABLE = "available"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    CIRCUIT_OPEN = "circuit_open"
    MAINTENANCE = "maintenance"


@dataclass
class HandlerInstance:
    """Handler instance with state and metrics"""
    handler_id: str
    handler: CommandHandler
    state: HandlerState = HandlerState.AVAILABLE
    active_commands: int = 0
    max_concurrent: int = 10
    total_processed: int = 0
    total_failed: int = 0
    average_execution_time: float = 0.0
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    geographic_region: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DispatchRule:
    """Rule for command dispatch routing"""
    rule_id: str
    command_type_pattern: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    target_handlers: List[str] = field(default_factory=list)
    strategy: DispatchStrategy = DispatchStrategy.ROUND_ROBIN
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandWorkflow:
    """Multi-step command workflow definition"""
    workflow_id: str
    name: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    compensation_handlers: Dict[str, str] = field(default_factory=dict)


class TransactionCoordinator:
    """Coordinate transactions across command handlers"""
    
    def __init__(self):
        self._active_transactions: Dict[str, Dict[str, Any]] = {}
        self._transaction_logs: List[Dict[str, Any]] = []
    
    async def begin_transaction(self, transaction_id: str, participants: List[str]) -> None:
        """Begin distributed transaction"""
        self._active_transactions[transaction_id] = {
            "participants": participants,
            "status": "active",
            "started_at": datetime.utcnow(),
            "completed_steps": [],
            "rollback_data": {}
        }
        logger.info(f"Transaction {transaction_id} started with participants: {participants}")
    
    async def commit_step(self, transaction_id: str, step_id: str, rollback_data: Any = None) -> None:
        """Commit a transaction step"""
        if transaction_id in self._active_transactions:
            transaction = self._active_transactions[transaction_id]
            transaction["completed_steps"].append(step_id)
            if rollback_data:
                transaction["rollback_data"][step_id] = rollback_data
    
    async def rollback_transaction(self, transaction_id: str) -> None:
        """Rollback distributed transaction"""
        if transaction_id in self._active_transactions:
            transaction = self._active_transactions[transaction_id]
            transaction["status"] = "rolling_back"
            
            # Execute rollback for completed steps in reverse order
            for step_id in reversed(transaction["completed_steps"]):
                try:
                    # In a real implementation, this would call compensation handlers
                    logger.info(f"Rolling back step {step_id} for transaction {transaction_id}")
                except Exception as e:
                    logger.error(f"Rollback failed for step {step_id}: {e}")
            
            transaction["status"] = "rolled_back"
            transaction["completed_at"] = datetime.utcnow()
    
    async def commit_transaction(self, transaction_id: str) -> None:
        """Commit distributed transaction"""
        if transaction_id in self._active_transactions:
            transaction = self._active_transactions[transaction_id]
            transaction["status"] = "committed"
            transaction["completed_at"] = datetime.utcnow()
            
            # Move to history
            self._transaction_logs.append(transaction.copy())
            del self._active_transactions[transaction_id]


class CommandEnricher:
    """Enrich commands with additional context and data"""
    
    def __init__(self):
        self._enrichment_rules: List[Callable] = []
    
    def add_enrichment_rule(self, rule: Callable[[Command], Command]) -> None:
        """Add command enrichment rule"""
        self._enrichment_rules.append(rule)
    
    async def enrich_command(self, command: Command) -> Command:
        """Enrich command with additional context"""
        enriched_command = command
        
        for rule in self._enrichment_rules:
            try:
                if asyncio.iscoroutinefunction(rule):
                    enriched_command = await rule(enriched_command)
                else:
                    enriched_command = rule(enriched_command)
            except Exception as e:
                logger.error(f"Command enrichment failed: {e}")
        
        return enriched_command


class BusinessRuleEngine:
    """Validate and enforce business rules for commands"""
    
    def __init__(self):
        self._rules: Dict[str, List[Callable]] = defaultdict(list)
    
    def add_rule(self, command_type: str, rule: Callable[[Command], bool], error_message: str) -> None:
        """Add business rule for command type"""
        self._rules[command_type].append({
            "rule": rule,
            "error_message": error_message
        })
    
    async def validate_command(self, command: Command) -> None:
        """Validate command against business rules"""
        rules = self._rules.get(command.command_type, [])
        
        for rule_config in rules:
            rule = rule_config["rule"]
            error_message = rule_config["error_message"]
            
            try:
                if asyncio.iscoroutinefunction(rule):
                    is_valid = await rule(command)
                else:
                    is_valid = rule(command)
                
                if not is_valid:
                    raise EventValidationError(f"Business rule violation: {error_message}")
                    
            except EventValidationError:
                raise
            except Exception as e:
                logger.error(f"Business rule evaluation failed: {e}")
                raise EventValidationError(f"Business rule evaluation error: {e}")


class LoadBalancer:
    """Load balancer for handler selection"""
    
    def __init__(self):
        self._handler_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
    
    def update_handler_metrics(self, handler_id: str, execution_time: float, success: bool) -> None:
        """Update handler performance metrics"""
        self._handler_metrics[handler_id].append({
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.utcnow()
        })
    
    def select_handler(self, available_handlers: List[HandlerInstance], strategy: DispatchStrategy) -> Optional[HandlerInstance]:
        """Select best handler based on strategy"""
        if not available_handlers:
            return None
        
        if strategy == DispatchStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_handlers)
        elif strategy == DispatchStrategy.LOAD_BASED:
            return self._load_based_selection(available_handlers)
        elif strategy == DispatchStrategy.PRIORITY_BASED:
            return self._priority_based_selection(available_handlers)
        else:
            return available_handlers[0]  # Default to first available
    
    def _round_robin_selection(self, handlers: List[HandlerInstance]) -> HandlerInstance:
        """Simple round-robin selection"""
        return min(handlers, key=lambda h: h.total_processed % len(handlers))
    
    def _load_based_selection(self, handlers: List[HandlerInstance]) -> HandlerInstance:
        """Select handler with lowest current load"""
        return min(handlers, key=lambda h: h.active_commands / h.max_concurrent)
    
    def _priority_based_selection(self, handlers: List[HandlerInstance]) -> HandlerInstance:
        """Select handler based on performance metrics"""
        def score_handler(handler: HandlerInstance) -> float:
            metrics = self._handler_metrics[handler.handler_id]
            if not metrics:
                return 0.5  # Neutral score for new handlers
            
            recent_metrics = [m for m in metrics if datetime.utcnow() - m["timestamp"] < timedelta(minutes=5)]
            if not recent_metrics:
                return 0.5
            
            success_rate = sum(1 for m in recent_metrics if m["success"]) / len(recent_metrics)
            avg_time = sum(m["execution_time"] for m in recent_metrics) / len(recent_metrics)
            
            # Higher score is better (high success rate, low execution time)
            return success_rate * 100 / (avg_time + 1)
        
        return max(handlers, key=score_handler)


class EnterpriseCommandDispatcher:
    """Enterprise command dispatcher with advanced routing and orchestration"""
    
    def __init__(self):
        self._handler_registry: Dict[str, List[HandlerInstance]] = defaultdict(list)
        self._dispatch_rules: List[DispatchRule] = []
        self._workflows: Dict[str, CommandWorkflow] = {}
        
        # Components
        self._transaction_coordinator = TransactionCoordinator()
        self._command_enricher = CommandEnricher()
        self._business_rule_engine = BusinessRuleEngine()
        self._load_balancer = LoadBalancer()
        
        # Metrics and monitoring
        self._metrics = {
            "commands_dispatched": 0,
            "handlers_registered": 0,
            "active_workflows": 0,
            "average_dispatch_time": 0.0
        }
        
        # State management
        self._active_dispatches: Dict[str, Dict[str, Any]] = {}
        self._dispatch_history: deque = deque(maxlen=1000)
    
    def register_handler(self, command_type: str, handler: CommandHandler, 
                        handler_id: str = None, max_concurrent: int = 10,
                        capabilities: List[str] = None, geographic_region: str = None) -> str:
        """Register command handler with advanced configuration"""
        handler_id = handler_id or str(uuid.uuid4())
        
        handler_instance = HandlerInstance(
            handler_id=handler_id,
            handler=handler,
            max_concurrent=max_concurrent,
            capabilities=capabilities or [],
            geographic_region=geographic_region
        )
        
        self._handler_registry[command_type].append(handler_instance)
        self._metrics["handlers_registered"] += 1
        
        logger.info(f"Registered handler {handler_id} for command type {command_type}")
        return handler_id
    
    def add_dispatch_rule(self, rule: DispatchRule) -> None:
        """Add dispatch rule for command routing"""
        self._dispatch_rules.append(rule)
        self._dispatch_rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Added dispatch rule: {rule.rule_id}")
    
    def register_workflow(self, workflow: CommandWorkflow) -> None:
        """Register multi-step command workflow"""
        self._workflows[workflow.workflow_id] = workflow
        logger.info(f"Registered workflow: {workflow.workflow_id}")
    
    def add_enrichment_rule(self, rule: Callable[[Command], Command]) -> None:
        """Add command enrichment rule"""
        self._command_enricher.add_enrichment_rule(rule)
    
    def add_business_rule(self, command_type: str, rule: Callable[[Command], bool], error_message: str) -> None:
        """Add business rule validation"""
        self._business_rule_engine.add_rule(command_type, rule, error_message)
    
    async def dispatch_command(self, command: Command) -> CommandResult:
        """Dispatch command with full enterprise pipeline"""
        start_time = time.time()
        dispatch_id = str(uuid.uuid4())
        
        try:
            # Track dispatch
            self._active_dispatches[dispatch_id] = {
                "command": command,
                "started_at": datetime.utcnow(),
                "status": "processing"
            }
            
            # Command enrichment
            enriched_command = await self._command_enricher.enrich_command(command)
            
            # Business rule validation
            await self._business_rule_engine.validate_command(enriched_command)
            
            # Handler selection
            handler_instance = await self._select_handler(enriched_command)
            if not handler_instance:
                raise EventProcessingError(f"No available handler for command type: {enriched_command.command_type}")
            
            # Execute command
            result = await self._execute_command_with_handler(enriched_command, handler_instance)
            
            # Update metrics
            execution_time = (time.time() - start_time) * 1000
            await self._update_dispatch_metrics(enriched_command, result, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = CommandResult(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time
            )
            
            await self._handle_dispatch_failure(command, error_result, e)
            return error_result
            
        finally:
            # Cleanup
            self._active_dispatches.pop(dispatch_id, None)
    
    async def execute_workflow(self, workflow_id: str, initial_command: Command) -> List[CommandResult]:
        """Execute multi-step command workflow"""
        if workflow_id not in self._workflows:
            raise EventProcessingError(f"Unknown workflow: {workflow_id}")
        
        workflow = self._workflows[workflow_id]
        results = []
        transaction_id = str(uuid.uuid4())
        
        try:
            # Begin distributed transaction
            participants = [step.get("handler_type") for step in workflow.steps]
            await self._transaction_coordinator.begin_transaction(transaction_id, participants)
            
            current_command = initial_command
            
            for i, step in enumerate(workflow.steps):
                step_id = f"{workflow_id}_step_{i}"
                
                # Create command for this step
                step_command = Command(
                    command_type=step["command_type"],
                    data={**current_command.data, **step.get("data", {})},
                    metadata={**current_command.metadata, "workflow_id": workflow_id, "step_id": step_id},
                    user_id=current_command.user_id,
                    correlation_id=current_command.correlation_id,
                    causation_id=current_command.command_id
                )
                
                # Execute step
                step_result = await self.dispatch_command(step_command)
                results.append(step_result)
                
                if step_result.status == CommandStatus.FAILED:
                    # Rollback transaction on failure
                    await self._transaction_coordinator.rollback_transaction(transaction_id)
                    break
                
                # Commit step
                await self._transaction_coordinator.commit_step(transaction_id, step_id, step_result.result)
                
                # Prepare for next step
                if step_result.result and isinstance(step_result.result, dict):
                    current_command.data.update(step_result.result)
            
            # Commit transaction if all steps succeeded
            if all(r.status == CommandStatus.COMPLETED for r in results):
                await self._transaction_coordinator.commit_transaction(transaction_id)
            
            return results
            
        except Exception as e:
            await self._transaction_coordinator.rollback_transaction(transaction_id)
            logger.error(f"Workflow execution failed: {e}")
            raise
    
    async def _select_handler(self, command: Command) -> Optional[HandlerInstance]:
        """Select appropriate handler for command"""
        # Find applicable dispatch rules
        applicable_rules = [
            rule for rule in self._dispatch_rules
            if rule.enabled and self._rule_matches_command(rule, command)
        ]
        
        # Use first matching rule or default to command type
        if applicable_rules:
            rule = applicable_rules[0]
            available_handlers = [
                h for h in self._handler_registry.get(command.command_type, [])
                if h.handler_id in rule.target_handlers and h.state == HandlerState.AVAILABLE
            ]
            strategy = rule.strategy
        else:
            available_handlers = [
                h for h in self._handler_registry.get(command.command_type, [])
                if h.state == HandlerState.AVAILABLE and h.active_commands < h.max_concurrent
            ]
            strategy = DispatchStrategy.LOAD_BASED
        
        # Select handler using load balancer
        return self._load_balancer.select_handler(available_handlers, strategy)
    
    def _rule_matches_command(self, rule: DispatchRule, command: Command) -> bool:
        """Check if dispatch rule matches command"""
        # Simple pattern matching - can be extended with regex or more complex logic
        if rule.command_type_pattern != "*" and rule.command_type_pattern != command.command_type:
            return False
        
        # Check additional conditions
        for key, expected_value in rule.conditions.items():
            if key in command.data and command.data[key] != expected_value:
                return False
            if key in command.metadata and command.metadata[key] != expected_value:
                return False
        
        return True
    
    async def _execute_command_with_handler(self, command: Command, handler_instance: HandlerInstance) -> CommandResult:
        """Execute command with specific handler instance"""
        handler_instance.active_commands += 1
        start_time = time.time()
        
        try:
            result = await handler_instance.handler.handle(command)
            
            # Update handler metrics
            execution_time = (time.time() - start_time) * 1000
            success = result.status == CommandStatus.COMPLETED
            
            handler_instance.total_processed += 1
            if not success:
                handler_instance.total_failed += 1
            
            # Update average execution time
            handler_instance.average_execution_time = (
                (handler_instance.average_execution_time * (handler_instance.total_processed - 1) + execution_time) /
                handler_instance.total_processed
            )
            
            # Update load balancer metrics
            self._load_balancer.update_handler_metrics(handler_instance.handler_id, execution_time, success)
            
            return result
            
        finally:
            handler_instance.active_commands -= 1
    
    async def _update_dispatch_metrics(self, command: Command, result: CommandResult, execution_time: float) -> None:
        """Update dispatch metrics"""
        self._metrics["commands_dispatched"] += 1
        
        # Update average dispatch time
        current_avg = self._metrics["average_dispatch_time"]
        total_dispatched = self._metrics["commands_dispatched"]
        new_avg = ((current_avg * (total_dispatched - 1)) + execution_time) / total_dispatched
        self._metrics["average_dispatch_time"] = new_avg
        
        # Add to history
        self._dispatch_history.append({
            "command_id": command.command_id,
            "command_type": command.command_type,
            "status": result.status.value,
            "execution_time": execution_time,
            "timestamp": datetime.utcnow()
        })
    
    async def _handle_dispatch_failure(self, command: Command, result: CommandResult, exception: Exception) -> None:
        """Handle dispatch failure"""
        logger.error(f"Command dispatch failed: {command.command_id} - {exception}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get dispatcher metrics"""
        total_handlers = sum(len(handlers) for handlers in self._handler_registry.values())
        
        return {
            **self._metrics,
            "total_handlers": total_handlers,
            "active_dispatches": len(self._active_dispatches),
            "registered_workflows": len(self._workflows),
            "dispatch_rules": len(self._dispatch_rules)
        }
    
    def get_handler_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all handlers"""
        health_status = {}
        
        for command_type, handlers in self._handler_registry.items():
            health_status[command_type] = []
            for handler in handlers:
                health_status[command_type].append({
                    "handler_id": handler.handler_id,
                    "state": handler.state.value,
                    "active_commands": handler.active_commands,
                    "max_concurrent": handler.max_concurrent,
                    "total_processed": handler.total_processed,
                    "total_failed": handler.total_failed,
                    "success_rate": ((handler.total_processed - handler.total_failed) / handler.total_processed * 100) if handler.total_processed > 0 else 0,
                    "average_execution_time": handler.average_execution_time
                })
        
        return health_status
    
    async def health_check_handlers(self) -> None:
        """Perform health check on all handlers"""
        for handlers in self._handler_registry.values():
            for handler in handlers:
                try:
                    # Simple health check - can be extended with actual health checks
                    if handler.active_commands >= handler.max_concurrent:
                        handler.state = HandlerState.OVERLOADED
                    elif handler.total_failed / max(handler.total_processed, 1) > 0.5:
                        handler.state = HandlerState.CIRCUIT_OPEN
                    else:
                        handler.state = HandlerState.AVAILABLE
                    
                    handler.last_health_check = datetime.utcnow()
                    
                except Exception as e:
                    logger.error(f"Health check failed for handler {handler.handler_id}: {e}")
                    handler.state = HandlerState.CIRCUIT_OPEN


# Singleton instance for global access
_command_dispatcher_instance: Optional[EnterpriseCommandDispatcher] = None


def get_command_dispatcher() -> EnterpriseCommandDispatcher:
    """Get singleton command dispatcher instance"""
    global _command_dispatcher_instance
    if _command_dispatcher_instance is None:
        _command_dispatcher_instance = EnterpriseCommandDispatcher()
    return _command_dispatcher_instance


def reset_command_dispatcher() -> None:
    """Reset command dispatcher instance (for testing)"""
    global _command_dispatcher_instance
    _command_dispatcher_instance = None