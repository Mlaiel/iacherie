#!/usr/bin/env python3
"""Compensation Transaction Manager - Saga Pattern Implementation
===============================================================

Advanced compensation transaction management for IA Chéries platform error handling.
Provides saga pattern implementation, distributed transaction rollback,
and automated compensation workflows for enterprise-scale deployments.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque

from .error_handler import ErrorHandler, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)


class SagaState(Enum):
    """Saga execution state enumeration."""
    STARTED = "started"
    EXECUTING = "executing"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TransactionState(Enum):
    """Individual transaction state enumeration."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"
    COMPENSATION_FAILED = "compensation_failed"


class CompensationStrategy(Enum):
    """Compensation strategy enumeration."""
    IMMEDIATE = "immediate"
    LAZY = "lazy"
    BEST_EFFORT = "best_effort"
    STRICT_ORDER = "strict_order"
    PARALLEL = "parallel"


class SagaPattern(Enum):
    """Saga pattern type enumeration."""
    ORCHESTRATOR = "orchestrator"
    CHOREOGRAPHY = "choreography"
    HYBRID = "hybrid"


@dataclass
class Transaction:
    """Individual transaction in saga."""
    transaction_id: str
    saga_id: str
    service_name: str
    operation: str
    compensation_operation: str
    order: int
    state: TransactionState = TransactionState.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_ms: int = 30000
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompensationAction:
    """Compensation action definition."""
    action_id: str
    transaction_id: str
    compensation_operation: str
    service_name: str
    compensation_payload: Dict[str, Any]
    execution_order: int
    state: TransactionState = TransactionState.PENDING
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class SagaDefinition:
    """Saga workflow definition."""
    saga_id: str
    saga_name: str
    pattern: SagaPattern
    compensation_strategy: CompensationStrategy
    transactions: List[Transaction]
    state: SagaState = SagaState.STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration_ms: Optional[float] = None
    compensation_actions: List[CompensationAction] = field(default_factory=list)
    failure_transaction: Optional[str] = None
    rollback_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SagaAuditRecord:
    """Saga audit trail record."""
    record_id: str
    saga_id: str
    transaction_id: Optional[str]
    action_type: str
    action_details: Dict[str, Any]
    timestamp: datetime
    service_name: str
    success: bool
    error_details: Optional[str] = None


class CompensationTransactionManager:
    """Compensation transactions enterprise avec saga patterns."""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """Initialize compensation transaction manager.
        
        Args:
            error_handler: Optional error handler for integration
        """
        self.error_handler = error_handler
        
        # Saga management
        self.active_sagas: Dict[str, SagaDefinition] = {}
        self.completed_sagas: Dict[str, SagaDefinition] = {}
        self.saga_templates: Dict[str, Dict[str, Any]] = {}
        
        # Transaction coordination
        self.transaction_registry: Dict[str, Transaction] = {}
        self.compensation_queue: deque = deque()
        self.retry_queue: deque = deque()
        
        # Audit and monitoring
        self.audit_trail: List[SagaAuditRecord] = []
        self.compensation_metrics: Dict[str, Any] = {
            "total_sagas": 0,
            "completed_sagas": 0,
            "failed_sagas": 0,
            "compensated_sagas": 0,
            "success_rate": 0.0,
            "compensation_success_rate": 0.0,
            "average_saga_duration": 0.0
        }
        
        # Configuration
        self.default_timeout_ms = 30000
        self.max_saga_duration_ms = 300000  # 5 minutes
        self.compensation_timeout_ms = 60000
        self.audit_retention_hours = 72
        
        self.logger = logger
        self._coordination_task: Optional[asyncio.Task] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        
    async def start_compensation_manager(self):
        """Start compensation transaction manager."""
        self._coordination_task = asyncio.create_task(self._saga_coordination_loop())
        self._monitoring_task = asyncio.create_task(self._saga_monitoring_loop())
        self.logger.info("Compensation transaction manager started")
    
    async def stop_compensation_manager(self):
        """Stop compensation transaction manager."""
        tasks = [self._coordination_task, self._monitoring_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.logger.info("Compensation transaction manager stopped")
    
    async def saga_compensation_orchestration(
        self,
        saga_definition: SagaDefinition
    ) -> Dict[str, Any]:
        """Orchestrate saga compensation process.
        
        Args:
            saga_definition: Saga definition to orchestrate
            
        Returns:
            Orchestration results
        """
        orchestration_result = {
            "saga_id": saga_definition.saga_id,
            "orchestration_status": "started",
            "transactions_executed": 0,
            "transactions_compensated": 0,
            "compensation_actions": [],
            "orchestration_success": False
        }
        
        try:
            # Register saga
            self.active_sagas[saga_definition.saga_id] = saga_definition
            saga_definition.start_time = datetime.now()
            saga_definition.state = SagaState.EXECUTING
            
            # Audit saga start
            await self._record_audit(
                saga_definition.saga_id,
                None,
                "saga_started",
                {"pattern": saga_definition.pattern.value},
                saga_definition.saga_name,
                True
            )
            
            # Execute transactions based on pattern
            if saga_definition.pattern == SagaPattern.ORCHESTRATOR:
                execution_result = await self._execute_orchestrator_pattern(saga_definition)
            elif saga_definition.pattern == SagaPattern.CHOREOGRAPHY:
                execution_result = await self._execute_choreography_pattern(saga_definition)
            else:  # HYBRID
                execution_result = await self._execute_hybrid_pattern(saga_definition)
            
            orchestration_result.update(execution_result)
            
            # Check if saga completed successfully
            if execution_result.get("success", False):
                saga_definition.state = SagaState.COMPLETED
                saga_definition.end_time = datetime.now()
                if saga_definition.start_time:
                    duration = (saga_definition.end_time - saga_definition.start_time).total_seconds() * 1000
                    saga_definition.total_duration_ms = duration
                
                orchestration_result["orchestration_success"] = True
                
                # Move to completed sagas
                self.completed_sagas[saga_definition.saga_id] = saga_definition
                del self.active_sagas[saga_definition.saga_id]
                
            else:
                # Saga failed, initiate compensation
                await self._initiate_saga_compensation(saga_definition, execution_result.get("failure_reason", "unknown"))
                orchestration_result["orchestration_status"] = "compensating"
            
        except Exception as e:
            self.logger.error(f"Error in saga orchestration: {e}")
            saga_definition.state = SagaState.FAILED
            orchestration_result["orchestration_status"] = "failed"
            orchestration_result["error"] = str(e)
        
        return orchestration_result
    
    async def compensation_action_coordination(
        self,
        saga_id: str,
        failed_transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Coordinate compensation actions for a saga.
        
        Args:
            saga_id: ID of saga to compensate
            failed_transaction_id: ID of failed transaction
            
        Returns:
            Compensation coordination results
        """
        coordination_result = {
            "saga_id": saga_id,
            "compensation_status": "started",
            "compensated_transactions": [],
            "failed_compensations": [],
            "coordination_success": False
        }
        
        if saga_id not in self.active_sagas:
            coordination_result["compensation_status"] = "saga_not_found"
            return coordination_result
        
        saga = self.active_sagas[saga_id]
        saga.state = SagaState.COMPENSATING
        
        try:
            # Build compensation plan
            compensation_plan = await self._build_compensation_plan(saga, failed_transaction_id)
            
            # Execute compensation based on strategy
            if saga.compensation_strategy == CompensationStrategy.IMMEDIATE:
                compensation_result = await self._execute_immediate_compensation(compensation_plan)
            elif saga.compensation_strategy == CompensationStrategy.LAZY:
                compensation_result = await self._execute_lazy_compensation(compensation_plan)
            elif saga.compensation_strategy == CompensationStrategy.BEST_EFFORT:
                compensation_result = await self._execute_best_effort_compensation(compensation_plan)
            elif saga.compensation_strategy == CompensationStrategy.STRICT_ORDER:
                compensation_result = await self._execute_strict_order_compensation(compensation_plan)
            else:  # PARALLEL
                compensation_result = await self._execute_parallel_compensation(compensation_plan)
            
            coordination_result.update(compensation_result)
            
            # Update saga state based on compensation result
            if compensation_result.get("success", False):
                saga.state = SagaState.COMPLETED
                coordination_result["coordination_success"] = True
                self.compensation_metrics["compensated_sagas"] += 1
            else:
                saga.state = SagaState.FAILED
                coordination_result["compensation_status"] = "failed"
            
            # Record compensation completion
            await self._record_audit(
                saga_id,
                None,
                "compensation_completed",
                coordination_result,
                saga.saga_name,
                coordination_result["coordination_success"]
            )
            
        except Exception as e:
            self.logger.error(f"Error in compensation coordination: {e}")
            saga.state = SagaState.FAILED
            coordination_result["compensation_status"] = "error"
            coordination_result["error"] = str(e)
        
        return coordination_result
    
    async def distributed_transaction_rollback(
        self,
        transaction_ids: List[str],
        rollback_strategy: str = "reverse_order"
    ) -> Dict[str, Any]:
        """Rollback distributed transactions.
        
        Args:
            transaction_ids: List of transaction IDs to rollback
            rollback_strategy: Strategy for rollback execution
            
        Returns:
            Rollback results
        """
        rollback_result = {
            "rollback_strategy": rollback_strategy,
            "total_transactions": len(transaction_ids),
            "successful_rollbacks": 0,
            "failed_rollbacks": 0,
            "rollback_details": [],
            "rollback_success": False
        }
        
        # Get transactions to rollback
        transactions_to_rollback = []
        for txn_id in transaction_ids:
            if txn_id in self.transaction_registry:
                txn = self.transaction_registry[txn_id]
                if txn.state == TransactionState.COMPLETED:
                    transactions_to_rollback.append(txn)
        
        # Order transactions for rollback
        if rollback_strategy == "reverse_order":
            transactions_to_rollback.sort(key=lambda t: t.order, reverse=True)
        elif rollback_strategy == "parallel":
            pass  # No ordering needed
        else:  # original_order
            transactions_to_rollback.sort(key=lambda t: t.order)
        
        # Execute rollbacks
        if rollback_strategy == "parallel":
            rollback_tasks = [
                self._execute_transaction_rollback(txn)
                for txn in transactions_to_rollback
            ]
            rollback_results = await asyncio.gather(*rollback_tasks, return_exceptions=True)
            
            for i, result in enumerate(rollback_results):
                txn = transactions_to_rollback[i]
                if isinstance(result, Exception):
                    rollback_result["failed_rollbacks"] += 1
                    rollback_result["rollback_details"].append({
                        "transaction_id": txn.transaction_id,
                        "status": "failed",
                        "error": str(result)
                    })
                else:
                    rollback_result["successful_rollbacks"] += 1
                    rollback_result["rollback_details"].append({
                        "transaction_id": txn.transaction_id,
                        "status": "success",
                        "result": result
                    })
        else:
            # Sequential rollback
            for txn in transactions_to_rollback:
                try:
                    result = await self._execute_transaction_rollback(txn)
                    rollback_result["successful_rollbacks"] += 1
                    rollback_result["rollback_details"].append({
                        "transaction_id": txn.transaction_id,
                        "status": "success",
                        "result": result
                    })
                except Exception as e:
                    rollback_result["failed_rollbacks"] += 1
                    rollback_result["rollback_details"].append({
                        "transaction_id": txn.transaction_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    
                    # Decide whether to continue based on strategy
                    if rollback_strategy == "strict_order":
                        break  # Stop on first failure
        
        # Determine overall success
        rollback_result["rollback_success"] = rollback_result["failed_rollbacks"] == 0
        
        return rollback_result
    
    async def compensation_state_management(self) -> Dict[str, Any]:
        """Manage compensation state across all active sagas.
        
        Returns:
            Compensation state management results
        """
        state_management = {
            "active_sagas": len(self.active_sagas),
            "completed_sagas": len(self.completed_sagas),
            "compensation_queue_size": len(self.compensation_queue),
            "saga_states": {},
            "compensation_performance": {},
            "state_transitions": {}
        }
        
        # Analyze saga states
        saga_state_counts = defaultdict(int)
        for saga in self.active_sagas.values():
            saga_state_counts[saga.state.value] += 1
            
            state_management["saga_states"][saga.saga_id] = {
                "state": saga.state.value,
                "progress": await self._calculate_saga_progress(saga),
                "duration_ms": self._calculate_saga_duration(saga),
                "transaction_count": len(saga.transactions),
                "completed_transactions": len([t for t in saga.transactions if t.state == TransactionState.COMPLETED])
            }
        
        state_management["saga_state_distribution"] = dict(saga_state_counts)
        
        # Analyze compensation performance
        compensating_sagas = [s for s in self.active_sagas.values() if s.state == SagaState.COMPENSATING]
        if compensating_sagas:
            compensation_durations = [
                self._calculate_saga_duration(s) for s in compensating_sagas
                if self._calculate_saga_duration(s) > 0
            ]
            
            if compensation_durations:
                state_management["compensation_performance"] = {
                    "average_compensation_duration": sum(compensation_durations) / len(compensation_durations),
                    "max_compensation_duration": max(compensation_durations),
                    "active_compensations": len(compensating_sagas)
                }
        
        return state_management
    
    async def saga_error_recovery(self, saga_id: str) -> Dict[str, Any]:
        """Recover from saga errors and failures.
        
        Args:
            saga_id: ID of saga to recover
            
        Returns:
            Recovery results
        """
        recovery_result = {
            "saga_id": saga_id,
            "recovery_status": "started",
            "recovery_actions": [],
            "recovery_success": False
        }
        
        saga = self.active_sagas.get(saga_id) or self.completed_sagas.get(saga_id)
        if not saga:
            recovery_result["recovery_status"] = "saga_not_found"
            return recovery_result
        
        try:
            # Analyze failure state
            failure_analysis = await self._analyze_saga_failure(saga)
            recovery_result["failure_analysis"] = failure_analysis
            
            # Determine recovery strategy
            recovery_strategy = await self._determine_recovery_strategy(saga, failure_analysis)
            recovery_result["recovery_strategy"] = recovery_strategy
            
            # Execute recovery actions
            if recovery_strategy == "retry_failed_transaction":
                recovery_actions = await self._retry_failed_transactions(saga)
            elif recovery_strategy == "partial_compensation":
                recovery_actions = await self._execute_partial_compensation(saga)
            elif recovery_strategy == "full_compensation":
                recovery_actions = await self._execute_full_compensation(saga)
            elif recovery_strategy == "manual_intervention":
                recovery_actions = await self._request_manual_intervention(saga)
            else:  # restart_saga
                recovery_actions = await self._restart_saga(saga)
            
            recovery_result["recovery_actions"] = recovery_actions
            recovery_result["recovery_success"] = len([a for a in recovery_actions if a.get("success", False)]) > 0
            
            # Update saga state if recovery successful
            if recovery_result["recovery_success"]:
                if saga.state == SagaState.FAILED:
                    saga.state = SagaState.EXECUTING
                recovery_result["recovery_status"] = "completed"
            else:
                recovery_result["recovery_status"] = "failed"
            
        except Exception as e:
            self.logger.error(f"Error in saga recovery: {e}")
            recovery_result["recovery_status"] = "error"
            recovery_result["error"] = str(e)
        
        return recovery_result
    
    async def compensation_audit_trail(
        self,
        saga_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get compensation audit trail.
        
        Args:
            saga_id: Optional specific saga ID
            hours: Hours of history to include
            
        Returns:
            Audit trail results
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter audit records
        filtered_records = [
            record for record in self.audit_trail
            if record.timestamp >= cutoff_time and (not saga_id or record.saga_id == saga_id)
        ]
        
        audit_result = {
            "total_records": len(filtered_records),
            "records": [],
            "saga_summary": {},
            "success_rate": 0.0,
            "error_patterns": {}
        }
        
        # Process records
        saga_actions = defaultdict(list)
        success_count = 0
        
        for record in filtered_records:
            record_data = {
                "record_id": record.record_id,
                "saga_id": record.saga_id,
                "transaction_id": record.transaction_id,
                "action_type": record.action_type,
                "timestamp": record.timestamp.isoformat(),
                "service_name": record.service_name,
                "success": record.success,
                "error_details": record.error_details
            }
            audit_result["records"].append(record_data)
            
            saga_actions[record.saga_id].append(record)
            
            if record.success:
                success_count += 1
        
        # Calculate success rate
        if filtered_records:
            audit_result["success_rate"] = success_count / len(filtered_records)
        
        # Generate saga summaries
        for saga_id, records in saga_actions.items():
            audit_result["saga_summary"][saga_id] = {
                "total_actions": len(records),
                "successful_actions": len([r for r in records if r.success]),
                "failed_actions": len([r for r in records if not r.success]),
                "first_action": min(records, key=lambda r: r.timestamp).timestamp.isoformat(),
                "last_action": max(records, key=lambda r: r.timestamp).timestamp.isoformat()
            }
        
        return audit_result
    
    async def register_saga_template(
        self,
        template_name: str,
        template_definition: Dict[str, Any]
    ):
        """Register a saga template for reuse.
        
        Args:
            template_name: Name of the template
            template_definition: Template definition
        """
        self.saga_templates[template_name] = template_definition
        self.logger.info(f"Registered saga template: {template_name}")
    
    async def create_saga_from_template(
        self,
        template_name: str,
        saga_id: str,
        parameters: Dict[str, Any]
    ) -> SagaDefinition:
        """Create saga from template.
        
        Args:
            template_name: Name of template to use
            saga_id: Unique saga ID
            parameters: Template parameters
            
        Returns:
            Created saga definition
        """
        if template_name not in self.saga_templates:
            raise ValueError(f"Template {template_name} not found")
        
        template = self.saga_templates[template_name]
        
        # Create transactions from template
        transactions = []
        for i, txn_template in enumerate(template.get("transactions", [])):
            transaction = Transaction(
                transaction_id=f"{saga_id}_txn_{i}",
                saga_id=saga_id,
                service_name=txn_template["service_name"],
                operation=txn_template["operation"],
                compensation_operation=txn_template["compensation_operation"],
                order=i,
                payload=parameters.get(f"txn_{i}_payload", {}),
                timeout_ms=txn_template.get("timeout_ms", self.default_timeout_ms),
                max_retries=txn_template.get("max_retries", 3)
            )
            transactions.append(transaction)
            self.transaction_registry[transaction.transaction_id] = transaction
        
        # Create saga definition
        saga = SagaDefinition(
            saga_id=saga_id,
            saga_name=template.get("name", template_name),
            pattern=SagaPattern(template.get("pattern", "orchestrator")),
            compensation_strategy=CompensationStrategy(template.get("compensation_strategy", "immediate")),
            transactions=transactions,
            metadata=parameters
        )
        
        return saga
    
    async def _saga_coordination_loop(self):
        """Main saga coordination loop."""
        while True:
            try:
                # Process compensation queue
                await self._process_compensation_queue()
                
                # Process retry queue
                await self._process_retry_queue()
                
                # Check for saga timeouts
                await self._check_saga_timeouts()
                
                # Update saga states
                await self._update_saga_states()
                
                await asyncio.sleep(1.0)  # Process every second
                
            except Exception as e:
                self.logger.error(f"Error in saga coordination loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _saga_monitoring_loop(self):
        """Main saga monitoring loop."""
        while True:
            try:
                # Update metrics
                await self._update_compensation_metrics()
                
                # Clean up old audit records
                await self._cleanup_audit_trail()
                
                # Check for stuck sagas
                await self._check_stuck_sagas()
                
                await asyncio.sleep(10.0)  # Monitor every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in saga monitoring loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _execute_orchestrator_pattern(self, saga: SagaDefinition) -> Dict[str, Any]:
        """Execute saga using orchestrator pattern."""
        result = {
            "pattern": "orchestrator",
            "success": False,
            "completed_transactions": 0,
            "failed_transaction": None,
            "failure_reason": None
        }
        
        # Execute transactions in order
        for transaction in sorted(saga.transactions, key=lambda t: t.order):
            try:
                txn_result = await self._execute_transaction(transaction)
                
                if txn_result["success"]:
                    result["completed_transactions"] += 1
                    transaction.state = TransactionState.COMPLETED
                else:
                    transaction.state = TransactionState.FAILED
                    result["failed_transaction"] = transaction.transaction_id
                    result["failure_reason"] = txn_result.get("error", "unknown")
                    return result
                    
            except Exception as e:
                transaction.state = TransactionState.FAILED
                result["failed_transaction"] = transaction.transaction_id
                result["failure_reason"] = str(e)
                return result
        
        result["success"] = True
        return result
    
    async def _execute_choreography_pattern(self, saga: SagaDefinition) -> Dict[str, Any]:
        """Execute saga using choreography pattern."""
        result = {
            "pattern": "choreography",
            "success": False,
            "completed_transactions": 0,
            "failed_transaction": None,
            "failure_reason": None
        }
        
        # In choreography pattern, transactions coordinate themselves
        # This is a simplified implementation
        
        # Execute all transactions in parallel and let them coordinate
        tasks = [
            self._execute_transaction(txn)
            for txn in saga.transactions
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, txn_result in enumerate(results):
            transaction = saga.transactions[i]
            
            if isinstance(txn_result, Exception):
                transaction.state = TransactionState.FAILED
                result["failed_transaction"] = transaction.transaction_id
                result["failure_reason"] = str(txn_result)
            elif txn_result.get("success", False):
                transaction.state = TransactionState.COMPLETED
                result["completed_transactions"] += 1
            else:
                transaction.state = TransactionState.FAILED
                result["failed_transaction"] = transaction.transaction_id
                result["failure_reason"] = txn_result.get("error", "unknown")
        
        result["success"] = result["failed_transaction"] is None
        return result
    
    async def _execute_hybrid_pattern(self, saga: SagaDefinition) -> Dict[str, Any]:
        """Execute saga using hybrid pattern."""
        # Simplified hybrid implementation - combines orchestrator and choreography
        return await self._execute_orchestrator_pattern(saga)
    
    async def _execute_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """Execute a single transaction.
        
        Args:
            transaction: Transaction to execute
            
        Returns:
            Execution result
        """
        transaction.start_time = datetime.now()
        transaction.state = TransactionState.EXECUTING
        
        try:
            # Record transaction start
            await self._record_audit(
                transaction.saga_id,
                transaction.transaction_id,
                "transaction_started",
                {"operation": transaction.operation},
                transaction.service_name,
                True
            )
            
            # Simulate transaction execution (in real implementation, this would call actual service)
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # For demonstration, assume 90% success rate
            import random
            success = random.random() > 0.1
            
            transaction.end_time = datetime.now()
            if transaction.start_time:
                duration = (transaction.end_time - transaction.start_time).total_seconds() * 1000
                transaction.duration_ms = duration
            
            if success:
                transaction.result = {"status": "completed", "data": "mock_result"}
                
                await self._record_audit(
                    transaction.saga_id,
                    transaction.transaction_id,
                    "transaction_completed",
                    transaction.result,
                    transaction.service_name,
                    True
                )
                
                return {"success": True, "result": transaction.result}
            else:
                error_msg = "Mock transaction failure"
                transaction.error = error_msg
                
                await self._record_audit(
                    transaction.saga_id,
                    transaction.transaction_id,
                    "transaction_failed",
                    {"error": error_msg},
                    transaction.service_name,
                    False,
                    error_msg
                )
                
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            transaction.end_time = datetime.now()
            transaction.error = str(e)
            transaction.state = TransactionState.FAILED
            
            await self._record_audit(
                transaction.saga_id,
                transaction.transaction_id,
                "transaction_error",
                {"error": str(e)},
                transaction.service_name,
                False,
                str(e)
            )
            
            return {"success": False, "error": str(e)}
    
    async def _initiate_saga_compensation(self, saga: SagaDefinition, failure_reason: str):
        """Initiate compensation for a failed saga."""
        saga.state = SagaState.COMPENSATING
        saga.rollback_reason = failure_reason
        
        # Add to compensation queue
        self.compensation_queue.append({
            "saga_id": saga.saga_id,
            "timestamp": datetime.now(),
            "reason": failure_reason
        })
        
        await self._record_audit(
            saga.saga_id,
            None,
            "compensation_initiated",
            {"reason": failure_reason},
            saga.saga_name,
            True
        )
    
    async def _build_compensation_plan(
        self,
        saga: SagaDefinition,
        failed_transaction_id: Optional[str]
    ) -> List[CompensationAction]:
        """Build compensation plan for saga."""
        compensation_actions = []
        
        # Find transactions to compensate (completed transactions before failure)
        transactions_to_compensate = []
        
        if failed_transaction_id:
            failed_transaction = next(
                (t for t in saga.transactions if t.transaction_id == failed_transaction_id),
                None
            )
            if failed_transaction:
                # Compensate all transactions completed before the failed one
                transactions_to_compensate = [
                    t for t in saga.transactions
                    if t.state == TransactionState.COMPLETED and t.order < failed_transaction.order
                ]
        else:
            # Compensate all completed transactions
            transactions_to_compensate = [
                t for t in saga.transactions
                if t.state == TransactionState.COMPLETED
            ]
        
        # Create compensation actions
        for i, transaction in enumerate(transactions_to_compensate):
            compensation_action = CompensationAction(
                action_id=f"{saga.saga_id}_comp_{i}",
                transaction_id=transaction.transaction_id,
                compensation_operation=transaction.compensation_operation,
                service_name=transaction.service_name,
                compensation_payload=transaction.payload,  # Simplified
                execution_order=len(transactions_to_compensate) - i - 1  # Reverse order
            )
            compensation_actions.append(compensation_action)
        
        saga.compensation_actions = compensation_actions
        return compensation_actions
    
    async def _execute_immediate_compensation(
        self,
        compensation_plan: List[CompensationAction]
    ) -> Dict[str, Any]:
        """Execute immediate compensation strategy."""
        result = {
            "strategy": "immediate",
            "success": False,
            "compensated_actions": 0,
            "failed_compensations": 0,
            "compensation_details": []
        }
        
        # Execute compensations in order
        for action in sorted(compensation_plan, key=lambda a: a.execution_order):
            try:
                comp_result = await self._execute_compensation_action(action)
                
                if comp_result["success"]:
                    action.state = TransactionState.COMPENSATED
                    result["compensated_actions"] += 1
                else:
                    action.state = TransactionState.COMPENSATION_FAILED
                    result["failed_compensations"] += 1
                
                result["compensation_details"].append({
                    "action_id": action.action_id,
                    "success": comp_result["success"],
                    "error": comp_result.get("error")
                })
                
            except Exception as e:
                action.state = TransactionState.COMPENSATION_FAILED
                result["failed_compensations"] += 1
                result["compensation_details"].append({
                    "action_id": action.action_id,
                    "success": False,
                    "error": str(e)
                })
        
        result["success"] = result["failed_compensations"] == 0
        return result
    
    async def _execute_lazy_compensation(
        self,
        compensation_plan: List[CompensationAction]
    ) -> Dict[str, Any]:
        """Execute lazy compensation strategy."""
        # For lazy compensation, we queue actions for later execution
        for action in compensation_plan:
            self.compensation_queue.append({
                "type": "compensation_action",
                "action": action,
                "timestamp": datetime.now()
            })
        
        return {
            "strategy": "lazy",
            "success": True,
            "queued_actions": len(compensation_plan),
            "compensation_details": [{"action_id": a.action_id, "status": "queued"} for a in compensation_plan]
        }
    
    async def _execute_best_effort_compensation(
        self,
        compensation_plan: List[CompensationAction]
    ) -> Dict[str, Any]:
        """Execute best effort compensation strategy."""
        result = {
            "strategy": "best_effort",
            "success": True,  # Always succeed in best effort
            "compensated_actions": 0,
            "failed_compensations": 0,
            "compensation_details": []
        }
        
        # Try to compensate all actions, but don't fail if some fail
        for action in compensation_plan:
            try:
                comp_result = await self._execute_compensation_action(action)
                
                if comp_result["success"]:
                    result["compensated_actions"] += 1
                else:
                    result["failed_compensations"] += 1
                
                result["compensation_details"].append({
                    "action_id": action.action_id,
                    "success": comp_result["success"],
                    "error": comp_result.get("error")
                })
                
            except Exception as e:
                result["failed_compensations"] += 1
                result["compensation_details"].append({
                    "action_id": action.action_id,
                    "success": False,
                    "error": str(e)
                })
        
        return result
    
    async def _execute_strict_order_compensation(
        self,
        compensation_plan: List[CompensationAction]
    ) -> Dict[str, Any]:
        """Execute strict order compensation strategy."""
        return await self._execute_immediate_compensation(compensation_plan)
    
    async def _execute_parallel_compensation(
        self,
        compensation_plan: List[CompensationAction]
    ) -> Dict[str, Any]:
        """Execute parallel compensation strategy."""
        result = {
            "strategy": "parallel",
            "success": False,
            "compensated_actions": 0,
            "failed_compensations": 0,
            "compensation_details": []
        }
        
        # Execute all compensations in parallel
        tasks = [self._execute_compensation_action(action) for action in compensation_plan]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, comp_result in enumerate(results):
            action = compensation_plan[i]
            
            if isinstance(comp_result, Exception):
                action.state = TransactionState.COMPENSATION_FAILED
                result["failed_compensations"] += 1
                result["compensation_details"].append({
                    "action_id": action.action_id,
                    "success": False,
                    "error": str(comp_result)
                })
            elif comp_result.get("success", False):
                action.state = TransactionState.COMPENSATED
                result["compensated_actions"] += 1
                result["compensation_details"].append({
                    "action_id": action.action_id,
                    "success": True
                })
            else:
                action.state = TransactionState.COMPENSATION_FAILED
                result["failed_compensations"] += 1
                result["compensation_details"].append({
                    "action_id": action.action_id,
                    "success": False,
                    "error": comp_result.get("error", "unknown")
                })
        
        result["success"] = result["failed_compensations"] == 0
        return result
    
    async def _execute_compensation_action(self, action: CompensationAction) -> Dict[str, Any]:
        """Execute a single compensation action."""
        try:
            # Record compensation start
            await self._record_audit(
                action.action_id.split("_comp_")[0],  # Extract saga_id
                action.transaction_id,
                "compensation_started",
                {"compensation_operation": action.compensation_operation},
                action.service_name,
                True
            )
            
            # Simulate compensation execution
            await asyncio.sleep(0.05)  # Simulate processing time
            
            # For demonstration, assume 95% success rate for compensations
            import random
            success = random.random() > 0.05
            
            if success:
                action.result = {"status": "compensated", "data": "mock_compensation_result"}
                
                await self._record_audit(
                    action.action_id.split("_comp_")[0],
                    action.transaction_id,
                    "compensation_completed",
                    action.result,
                    action.service_name,
                    True
                )
                
                return {"success": True, "result": action.result}
            else:
                error_msg = "Mock compensation failure"
                action.error = error_msg
                
                await self._record_audit(
                    action.action_id.split("_comp_")[0],
                    action.transaction_id,
                    "compensation_failed",
                    {"error": error_msg},
                    action.service_name,
                    False,
                    error_msg
                )
                
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            action.error = str(e)
            return {"success": False, "error": str(e)}
    
    async def _execute_transaction_rollback(self, transaction: Transaction) -> Dict[str, Any]:
        """Execute rollback for a single transaction."""
        # Create compensation action
        compensation_action = CompensationAction(
            action_id=f"{transaction.transaction_id}_rollback",
            transaction_id=transaction.transaction_id,
            compensation_operation=transaction.compensation_operation,
            service_name=transaction.service_name,
            compensation_payload=transaction.payload,
            execution_order=0
        )
        
        # Execute compensation
        result = await self._execute_compensation_action(compensation_action)
        
        if result["success"]:
            transaction.state = TransactionState.COMPENSATED
        else:
            transaction.state = TransactionState.COMPENSATION_FAILED
        
        return result
    
    async def _record_audit(
        self,
        saga_id: str,
        transaction_id: Optional[str],
        action_type: str,
        action_details: Dict[str, Any],
        service_name: str,
        success: bool,
        error_details: Optional[str] = None
    ):
        """Record audit trail entry."""
        audit_record = SagaAuditRecord(
            record_id=str(uuid.uuid4()),
            saga_id=saga_id,
            transaction_id=transaction_id,
            action_type=action_type,
            action_details=action_details,
            timestamp=datetime.now(),
            service_name=service_name,
            success=success,
            error_details=error_details
        )
        
        self.audit_trail.append(audit_record)
    
    def _calculate_saga_progress(self, saga: SagaDefinition) -> float:
        """Calculate saga progress percentage."""
        if not saga.transactions:
            return 0.0
        
        completed_transactions = len([t for t in saga.transactions if t.state == TransactionState.COMPLETED])
        return completed_transactions / len(saga.transactions)
    
    def _calculate_saga_duration(self, saga: SagaDefinition) -> float:
        """Calculate saga duration in milliseconds."""
        if not saga.start_time:
            return 0.0
        
        end_time = saga.end_time or datetime.now()
        return (end_time - saga.start_time).total_seconds() * 1000
    
    async def _process_compensation_queue(self):
        """Process pending compensation actions."""
        while self.compensation_queue:
            item = self.compensation_queue.popleft()
            
            if item.get("type") == "compensation_action":
                action = item["action"]
                try:
                    await self._execute_compensation_action(action)
                except Exception as e:
                    self.logger.error(f"Error executing queued compensation action: {e}")
    
    async def _process_retry_queue(self):
        """Process pending retry actions."""
        # Placeholder for retry processing
        pass
    
    async def _check_saga_timeouts(self):
        """Check for saga timeouts."""
        current_time = datetime.now()
        
        for saga in list(self.active_sagas.values()):
            if saga.start_time:
                duration_ms = (current_time - saga.start_time).total_seconds() * 1000
                
                if duration_ms > self.max_saga_duration_ms:
                    saga.state = SagaState.TIMEOUT
                    await self._initiate_saga_compensation(saga, "saga_timeout")
    
    async def _update_saga_states(self):
        """Update saga states based on transaction states."""
        for saga in list(self.active_sagas.values()):
            if saga.state == SagaState.EXECUTING:
                # Check if all transactions are completed
                if all(t.state == TransactionState.COMPLETED for t in saga.transactions):
                    saga.state = SagaState.COMPLETED
                    saga.end_time = datetime.now()
                    
                    # Move to completed sagas
                    self.completed_sagas[saga.saga_id] = saga
                    del self.active_sagas[saga.saga_id]
    
    async def _update_compensation_metrics(self):
        """Update compensation performance metrics."""
        total_sagas = len(self.active_sagas) + len(self.completed_sagas)
        completed_sagas = len(self.completed_sagas)
        failed_sagas = len([s for s in self.completed_sagas.values() if s.state == SagaState.FAILED])
        
        self.compensation_metrics.update({
            "total_sagas": total_sagas,
            "completed_sagas": completed_sagas,
            "failed_sagas": failed_sagas,
            "success_rate": completed_sagas / max(total_sagas, 1),
            "active_sagas": len(self.active_sagas)
        })
    
    async def _cleanup_audit_trail(self):
        """Clean up old audit trail records."""
        cutoff_time = datetime.now() - timedelta(hours=self.audit_retention_hours)
        
        self.audit_trail = [
            record for record in self.audit_trail
            if record.timestamp >= cutoff_time
        ]
    
    async def _check_stuck_sagas(self):
        """Check for stuck sagas and take corrective action."""
        current_time = datetime.now()
        
        for saga in self.active_sagas.values():
            if saga.start_time:
                duration_hours = (current_time - saga.start_time).total_seconds() / 3600
                
                if duration_hours > 1 and saga.state == SagaState.EXECUTING:  # Stuck for over 1 hour
                    self.logger.warning(f"Detected stuck saga: {saga.saga_id}")
                    # Could trigger recovery or escalation here
    
    # Recovery methods (simplified implementations)
    async def _analyze_saga_failure(self, saga: SagaDefinition) -> Dict[str, Any]:
        """Analyze saga failure."""
        return {"failure_type": "transaction_failure", "analysis": "simplified"}
    
    async def _determine_recovery_strategy(self, saga: SagaDefinition, failure_analysis: Dict[str, Any]) -> str:
        """Determine recovery strategy."""
        return "retry_failed_transaction"
    
    async def _retry_failed_transactions(self, saga: SagaDefinition) -> List[Dict[str, Any]]:
        """Retry failed transactions."""
        return [{"action": "retry", "success": True}]
    
    async def _execute_partial_compensation(self, saga: SagaDefinition) -> List[Dict[str, Any]]:
        """Execute partial compensation."""
        return [{"action": "partial_compensation", "success": True}]
    
    async def _execute_full_compensation(self, saga: SagaDefinition) -> List[Dict[str, Any]]:
        """Execute full compensation."""
        return [{"action": "full_compensation", "success": True}]
    
    async def _request_manual_intervention(self, saga: SagaDefinition) -> List[Dict[str, Any]]:
        """Request manual intervention."""
        return [{"action": "manual_intervention_requested", "success": True}]
    
    async def _restart_saga(self, saga: SagaDefinition) -> List[Dict[str, Any]]:
        """Restart saga."""
        return [{"action": "saga_restart", "success": True}]