"""
Error Recovery Orchestrator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""Error Recovery Orchestrator - Intelligent Error Recovery
==========================================================

Advanced error recovery orchestrator for saga pattern failures.
Provides intelligent recovery strategies, automated healing,
and resilience management for distributed saga workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Recovery strategy types"""
    RETRY = "retry"
    ALTERNATIVE_PATH = "alternative_path"
    COMPENSATION = "compensation"
    MANUAL_INTERVENTION = "manual_intervention"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Context information about an error"""
    saga_id: str
    step_name: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    business_context: Dict[str, Any] = field(default_factory=dict)
    technical_context: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RecoveryPlan:
    """Recovery plan for error handling"""
    recovery_id: str
    saga_id: str
    primary_strategy: RecoveryStrategy
    fallback_strategies: List[RecoveryStrategy]
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    timeout_seconds: float = 300.0
    escalation_threshold: int = 2
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryExecution:
    """Represents an active recovery execution"""
    execution_id: str
    recovery_plan: RecoveryPlan
    error_context: ErrorContext
    current_strategy: RecoveryStrategy
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: List[Dict[str, Any]] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None


class ErrorRecoveryOrchestrator:
    """Main orchestrator for error recovery"""
    
    def __init__(self) -> None:
        self.active_recoveries: Dict[str, RecoveryExecution] = {}
        self.recovery_strategies: Dict[RecoveryStrategy, Callable] = {}
        self.error_patterns: Dict[str, RecoveryStrategy] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.recovery_history: List[RecoveryExecution] = []
        
        self._setup_recovery_strategies()
        self._setup_error_patterns()
    
    def _setup_recovery_strategies(self) -> None:
        """Setup recovery strategy implementations"""
        self.recovery_strategies = {
            RecoveryStrategy.RETRY: self._execute_retry_strategy,
            RecoveryStrategy.ALTERNATIVE_PATH: self._execute_alternative_path,
            RecoveryStrategy.COMPENSATION: self._execute_compensation_strategy,
            RecoveryStrategy.MANUAL_INTERVENTION: self._execute_manual_intervention,
            RecoveryStrategy.CIRCUIT_BREAKER: self._execute_circuit_breaker,
            RecoveryStrategy.GRACEFUL_DEGRADATION: self._execute_graceful_degradation
        }
    
    def _setup_error_patterns(self) -> None:
        """Setup error pattern to recovery strategy mapping"""
        self.error_patterns = {
            "TimeoutError": RecoveryStrategy.RETRY,
            "ConnectionError": RecoveryStrategy.CIRCUIT_BREAKER,
            "ServiceUnavailable": RecoveryStrategy.ALTERNATIVE_PATH,
            "ValidationError": RecoveryStrategy.MANUAL_INTERVENTION,
            "PaymentError": RecoveryStrategy.COMPENSATION,
            "ResourceExhausted": RecoveryStrategy.GRACEFUL_DEGRADATION
        }
    
    async def handle_error(
        self,
        error_context: ErrorContext,
        custom_recovery_plan: Optional[RecoveryPlan] = None
    ) -> str:
        """Handle error with intelligent recovery"""
        
        # Determine recovery plan
        if custom_recovery_plan:
            recovery_plan = custom_recovery_plan
        else:
            recovery_plan = await self._create_recovery_plan(error_context)
        
        # Create recovery execution
        execution = RecoveryExecution(
            execution_id=str(uuid.uuid4()),
            recovery_plan=recovery_plan,
            error_context=error_context,
            current_strategy=recovery_plan.primary_strategy,
            started_at=datetime.now(timezone.utc)
        )
        
        self.active_recoveries[execution.execution_id] = execution
        
        # Execute recovery asynchronously
        asyncio.create_task(self._execute_recovery(execution))
        
        logger.info(f"Started error recovery {execution.execution_id} for saga {error_context.saga_id}")
        return execution.execution_id
    
    async def _create_recovery_plan(self, error_context: ErrorContext) -> RecoveryPlan:
        """Create intelligent recovery plan based on error context"""
        
        # Determine primary strategy based on error type
        primary_strategy = self.error_patterns.get(
            error_context.error_type,
            RecoveryStrategy.RETRY  # Default
        )
        
        # Determine fallback strategies
        fallback_strategies = []
        if primary_strategy == RecoveryStrategy.RETRY:
            fallback_strategies = [RecoveryStrategy.ALTERNATIVE_PATH, RecoveryStrategy.COMPENSATION]
        elif primary_strategy == RecoveryStrategy.ALTERNATIVE_PATH:
            fallback_strategies = [RecoveryStrategy.RETRY, RecoveryStrategy.COMPENSATION]
        elif primary_strategy == RecoveryStrategy.CIRCUIT_BREAKER:
            fallback_strategies = [RecoveryStrategy.ALTERNATIVE_PATH, RecoveryStrategy.GRACEFUL_DEGRADATION]
        else:
            fallback_strategies = [RecoveryStrategy.COMPENSATION]
        
        # Adjust based on business context
        priority = error_context.business_context.get("priority", "normal")
        if priority == "critical":
            fallback_strategies.insert(0, RecoveryStrategy.MANUAL_INTERVENTION)
        
        # Adjust retry count based on error history
        max_retries = await self._calculate_optimal_retries(error_context)
        
        return RecoveryPlan(
            recovery_id=str(uuid.uuid4()),
            saga_id=error_context.saga_id,
            primary_strategy=primary_strategy,
            fallback_strategies=fallback_strategies,
            max_retries=max_retries,
            retry_delay_seconds=self._calculate_retry_delay(error_context),
            timeout_seconds=self._calculate_timeout(error_context),
            escalation_threshold=2
        )
    
    async def _execute_recovery(self, execution -> None: RecoveryExecution) -> None:
        """Execute recovery plan"""
        try:
            execution.status = "running"
            
            # Try primary strategy
            success = await self._try_strategy(execution, execution.current_strategy)
            
            if not success:
                # Try fallback strategies
                for fallback_strategy in execution.recovery_plan.fallback_strategies:
                    execution.current_strategy = fallback_strategy
                    success = await self._try_strategy(execution, fallback_strategy)
                    if success:
                        break
            
            # Update final status
            execution.status = "completed" if success else "failed"
            execution.completed_at = datetime.now(timezone.utc)
            execution.result = {"success": success}
            
            # Learn from recovery
            await self._learn_from_recovery(execution)
            
            logger.info(f"Recovery {execution.execution_id} {'succeeded' if success else 'failed'}")
            
        except Exception as e:
            execution.status = "error"
            execution.completed_at = datetime.now(timezone.utc)
            execution.result = {"success": False, "error": str(e)}
            logger.error(f"Recovery execution {execution.execution_id} failed: {e}")
        finally:
            # Move to history
            self.recovery_history.append(execution)
            if execution.execution_id in self.active_recoveries:
                del self.active_recoveries[execution.execution_id]
    
    async def _try_strategy(
        self,
        execution: RecoveryExecution,
        strategy: RecoveryStrategy
    ) -> bool:
        """Try specific recovery strategy"""
        attempt_id = str(uuid.uuid4())
        attempt_start = datetime.now(timezone.utc)
        
        try:
            strategy_func = self.recovery_strategies[strategy]
            result = await strategy_func(execution.error_context, execution.recovery_plan)
            
            # Record attempt
            execution.attempts.append({
                "attempt_id": attempt_id,
                "strategy": strategy.value,
                "started_at": attempt_start.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "success": result.get("success", False),
                "details": result
            })
            
            return result.get("success", False)
            
        except Exception as e:
            # Record failed attempt
            execution.attempts.append({
                "attempt_id": attempt_id,
                "strategy": strategy.value,
                "started_at": attempt_start.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": str(e)
            })
            
            logger.error(f"Recovery strategy {strategy.value} failed: {e}")
            return False
    
    async def _execute_retry_strategy(
        self,
        error_context: ErrorContext,
        recovery_plan: RecoveryPlan
    ) -> Dict[str, Any]:
        """Execute retry recovery strategy"""
        max_retries = recovery_plan.max_retries
        retry_delay = recovery_plan.retry_delay_seconds
        
        for attempt in range(max_retries):
            if attempt > 0:
                await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            
            try:
                # Simulate retry operation
                await asyncio.sleep(0.1)  # Simulate work
                
                # Mock success rate of 70% for retries
                import random
                if random.random() > 0.3:
                    return {
                        "success": True,
                        "strategy": "retry",
                        "attempt": attempt + 1,
                        "message": "Retry successful"
                    }
                
            except Exception as e:
                logger.warning(f"Retry attempt {attempt + 1} failed: {e}")
        
        return {
            "success": False,
            "strategy": "retry",
            "attempts": max_retries,
            "message": "All retry attempts failed"
        }
    
    async def _execute_alternative_path(
        self,
        error_context: ErrorContext,
        recovery_plan: RecoveryPlan
    ) -> Dict[str, Any]:
        """Execute alternative path strategy"""
        try:
            # Simulate alternative path execution
            await asyncio.sleep(0.2)  # Simulate work
            
            # Mock success rate of 80% for alternative paths
            import random
            if random.random() > 0.2:
                return {
                    "success": True,
                    "strategy": "alternative_path",
                    "path": "backup_service",
                    "message": "Alternative path successful"
                }
            
            return {
                "success": False,
                "strategy": "alternative_path",
                "message": "Alternative path failed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "strategy": "alternative_path",
                "error": str(e)
            }
    
    async def _execute_compensation_strategy(
        self,
        error_context: ErrorContext,
        recovery_plan: RecoveryPlan
    ) -> Dict[str, Any]:
        """Execute compensation strategy"""
        try:
            # Simulate compensation execution
            await asyncio.sleep(0.15)  # Simulate compensation work
            
            return {
                "success": True,
                "strategy": "compensation",
                "compensation_actions": ["rollback_upload", "cleanup_analysis"],
                "message": "Compensation completed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "strategy": "compensation",
                "error": str(e)
            }
    
    async def _execute_manual_intervention(
        self,
        error_context: ErrorContext,
        recovery_plan: RecoveryPlan
    ) -> Dict[str, Any]:
        """Execute manual intervention strategy"""
        # In real implementation, would create incident ticket
        return {
            "success": True,
            "strategy": "manual_intervention",
            "ticket_id": f"INC-{uuid.uuid4().hex[:8]}",
            "message": "Manual intervention ticket created"
        }
    
    async def _execute_circuit_breaker(
        self,
        error_context: ErrorContext,
        recovery_plan: RecoveryPlan
    ) -> Dict[str, Any]:
        """Execute circuit breaker strategy"""
        service_key = error_context.technical_context.get("service", "unknown")
        
        # Update circuit breaker state
        if service_key not in self.circuit_breakers:
            self.circuit_breakers[service_key] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": None
            }
        
        cb = self.circuit_breakers[service_key]
        cb["failure_count"] += 1
        cb["last_failure"] = datetime.now(timezone.utc)
        
        if cb["failure_count"] >= 5:
            cb["state"] = "open"
        
        return {
            "success": True,
            "strategy": "circuit_breaker",
            "service": service_key,
            "state": cb["state"],
            "message": f"Circuit breaker {cb['state']} for service {service_key}"
        }
    
    async def _execute_graceful_degradation(
        self,
        error_context: ErrorContext,
        recovery_plan: RecoveryPlan
    ) -> Dict[str, Any]:
        """Execute graceful degradation strategy"""
        try:
            # Simulate degraded functionality
            await asyncio.sleep(0.05)  # Simulate minimal work
            
            return {
                "success": True,
                "strategy": "graceful_degradation",
                "degraded_features": ["advanced_analytics", "real_time_sync"],
                "message": "Graceful degradation activated"
            }
            
        except Exception as e:
            return {
                "success": False,
                "strategy": "graceful_degradation",
                "error": str(e)
            }
    
    async def _calculate_optimal_retries(self, error_context: ErrorContext) -> int:
        """Calculate optimal retry count based on error history"""
        # Default retry counts by error type
        defaults = {
            "TimeoutError": 3,
            "ConnectionError": 2,
            "ServiceUnavailable": 4,
            "ValidationError": 1,
            "PaymentError": 2,
            "ResourceExhausted": 1
        }
        
        return defaults.get(error_context.error_type, 3)
    
    def _calculate_retry_delay(self, error_context: ErrorContext) -> float:
        """Calculate retry delay based on error context"""
        base_delay = 1.0
        
        # Adjust based on error type
        if error_context.error_type in ["ConnectionError", "ServiceUnavailable"]:
            base_delay = 2.0
        elif error_context.error_type == "ResourceExhausted":
            base_delay = 5.0
        
        return base_delay
    
    def _calculate_timeout(self, error_context: ErrorContext) -> float:
        """Calculate timeout based on error context"""
        base_timeout = 300.0  # 5 minutes
        
        # Adjust based on business priority
        priority = error_context.business_context.get("priority", "normal")
        if priority == "critical":
            base_timeout = 600.0  # 10 minutes
        elif priority == "low":
            base_timeout = 180.0  # 3 minutes
        
        return base_timeout
    
    async def _learn_from_recovery(self, execution -> None: RecoveryExecution) -> None:
        """Learn from recovery execution to improve future decisions"""
        # In real implementation, would update ML models or rule engines
        success = execution.result.get("success", False)
        strategy = execution.current_strategy
        error_type = execution.error_context.error_type
        
        logger.debug(f"Learning: {error_type} -> {strategy.value} = {success}")
        
        # Update error pattern mappings based on success
        if success and strategy != self.error_patterns.get(error_type):
            # This strategy worked better, consider updating default
            logger.info(f"Strategy {strategy.value} successful for {error_type}")
    
    async def get_recovery_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get recovery execution status"""
        # Check active recoveries
        if execution_id in self.active_recoveries:
            execution = self.active_recoveries[execution_id]
        else:
            # Check history
            execution = next(
                (e for e in self.recovery_history if e.execution_id == execution_id),
                None
            )
        
        if not execution:
            return None
        
        return {
            "execution_id": execution.execution_id,
            "saga_id": execution.error_context.saga_id,
            "status": execution.status,
            "current_strategy": execution.current_strategy.value,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "attempts": len(execution.attempts),
            "result": execution.result
        }
    
    async def get_recovery_analytics(self) -> Dict[str, Any]:
        """Get recovery analytics and insights"""
        all_recoveries = list(self.active_recoveries.values()) + self.recovery_history
        
        if not all_recoveries:
            return {"total_recoveries": 0}
        
        successful = len([r for r in all_recoveries if r.result and r.result.get("success")])
        failed = len(all_recoveries) - successful
        
        # Strategy success rates
        strategy_stats = {}
        for strategy in RecoveryStrategy:
            strategy_recoveries = [r for r in all_recoveries if r.current_strategy == strategy]
            if strategy_recoveries:
                strategy_successful = len([r for r in strategy_recoveries 
                                         if r.result and r.result.get("success")])
                strategy_stats[strategy.value] = {
                    "total": len(strategy_recoveries),
                    "successful": strategy_successful,
                    "success_rate": strategy_successful / len(strategy_recoveries)
                }
        
        return {
            "total_recoveries": len(all_recoveries),
            "successful_recoveries": successful,
            "failed_recoveries": failed,
            "overall_success_rate": successful / len(all_recoveries),
            "active_recoveries": len(self.active_recoveries),
            "strategy_statistics": strategy_stats,
            "circuit_breaker_states": {
                service: cb["state"] for service, cb in self.circuit_breakers.items()
            }
        }


# Global orchestrator instance
_error_recovery_orchestrator: Optional[ErrorRecoveryOrchestrator] = None


def get_error_recovery_orchestrator() -> ErrorRecoveryOrchestrator:
    """Get global error recovery orchestrator"""
    global _error_recovery_orchestrator
    if _error_recovery_orchestrator is None:
        _error_recovery_orchestrator = ErrorRecoveryOrchestrator()
    
    return _error_recovery_orchestrator


async def handle_saga_error(
    saga_id: str,
    step_name: str,
    error_type: str,
    error_message: str,
    business_context: Dict[str, Any] = None
) -> str:
    """Convenience function to handle saga error"""
    orchestrator = get_error_recovery_orchestrator()
    
    error_context = ErrorContext(
        saga_id=saga_id,
        step_name=step_name,
        error_type=error_type,
        error_message=error_message,
        business_context=business_context or {}
    )
    
    return await orchestrator.handle_error(error_context)


__all__ = [
    "ErrorRecoveryOrchestrator",
    "ErrorContext",
    "RecoveryPlan",
    "RecoveryExecution",
    "RecoveryStrategy",
    "ErrorSeverity",
    "get_error_recovery_orchestrator",
    "handle_saga_error"
]