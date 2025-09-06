#!/usr/bin/env python3
"""Compensation Transaction Handler - Intelligent Rollback Management
====================================================================

Advanced compensation transaction handling for saga pattern rollbacks.
Provides intelligent compensation strategies, ordering optimization,
and fault-tolerant rollback execution.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class CompensationStatus(Enum):
    """Compensation execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class CompensationAction:
    """Represents a compensation action to be executed"""
    action_id: str
    action_type: str
    saga_id: str
    step_id: str
    compensation_data: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: int = 0  # Higher number = higher priority
    max_retries: int = 3
    retry_count: int = 0


@dataclass
class CompensationResult:
    """Result of compensation execution"""
    action_id: str
    status: CompensationStatus
    details: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    
    @classmethod
    def SUCCESS(cls, action_id: str, details: str = None) -> 'CompensationResult':
        return cls(action_id=action_id, status=CompensationStatus.COMPLETED, details=details)
    
    @classmethod
    def FAILED(cls, action_id: str, error: str) -> 'CompensationResult':
        return cls(action_id=action_id, status=CompensationStatus.FAILED, error=error)


@dataclass
class CompensationWorkflowResult:
    """Result of complete compensation workflow"""
    saga_id: str
    total_actions: int
    successful_actions: int
    failed_actions: int
    compensation_results: List[CompensationResult] = field(default_factory=list)
    total_execution_time: float = 0.0
    
    @classmethod
    def COMPLETED(cls, saga_id: str, results: List[CompensationResult]) -> 'CompensationWorkflowResult':
        successful = len([r for r in results if r.status == CompensationStatus.COMPLETED])
        failed = len([r for r in results if r.status == CompensationStatus.FAILED])
        
        return cls(
            saga_id=saga_id,
            total_actions=len(results),
            successful_actions=successful,
            failed_actions=failed,
            compensation_results=results
        )


class CompensationStore:
    """Storage for compensation actions"""
    
    def __init__(self):
        self.actions: Dict[str, List[CompensationAction]] = {}
        self.execution_log: List[Dict[str, Any]] = []
    
    async def store_action(self, action: CompensationAction):
        """Store compensation action"""
        if action.saga_id not in self.actions:
            self.actions[action.saga_id] = []
        self.actions[action.saga_id].append(action)
    
    async def get_actions(self, saga_id: str) -> List[CompensationAction]:
        """Get all compensation actions for saga"""
        return self.actions.get(saga_id, [])
    
    async def log_execution(self, saga_id: str, action_id: str, result: CompensationResult):
        """Log compensation execution"""
        self.execution_log.append({
            "saga_id": saga_id,
            "action_id": action_id,
            "result": result,
            "timestamp": datetime.now(timezone.utc)
        })


class CompensationStrategy(ABC):
    """Abstract base class for compensation strategies"""
    
    @abstractmethod
    async def compensate(
        self, 
        action: CompensationAction, 
        context: Dict[str, Any]
    ) -> CompensationResult:
        """Execute compensation for action"""
        pass
    
    @abstractmethod
    def can_handle(self, action_type: str) -> bool:
        """Check if strategy can handle action type"""
        pass


class ContentUploadCompensation(CompensationStrategy):
    """Compensation strategy for content upload operations"""
    
    async def compensate(
        self, 
        action: CompensationAction, 
        context: Dict[str, Any]
    ) -> CompensationResult:
        """Compensate content upload - delete files and metadata"""
        content_id = action.compensation_data.get("content_id")
        
        if not content_id:
            return CompensationResult.FAILED(
                action.action_id, 
                "Missing content_id in compensation data"
            )
        
        try:
            # Simulate file deletion
            await asyncio.sleep(0.1)
            logger.info(f"Deleted content files for {content_id}")
            
            # Simulate metadata cleanup
            await asyncio.sleep(0.05)
            logger.info(f"Cleaned up metadata for {content_id}")
            
            # Simulate search index removal
            await asyncio.sleep(0.02)
            logger.info(f"Removed search index for {content_id}")
            
            return CompensationResult.SUCCESS(
                action.action_id,
                f"Content {content_id} fully compensated"
            )
            
        except Exception as e:
            return CompensationResult.FAILED(action.action_id, str(e))
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == "content_upload"


class AIAnalysisCompensation(CompensationStrategy):
    """Compensation strategy for AI analysis operations"""
    
    async def compensate(
        self, 
        action: CompensationAction, 
        context: Dict[str, Any]
    ) -> CompensationResult:
        """Compensate AI analysis - cleanup analysis data"""
        content_id = action.compensation_data.get("content_id")
        
        try:
            # Simulate AI analysis cleanup
            await asyncio.sleep(0.05)
            logger.info(f"Cleaned up AI analysis for {content_id}")
            
            return CompensationResult.SUCCESS(
                action.action_id,
                f"AI analysis compensated for {content_id}"
            )
            
        except Exception as e:
            return CompensationResult.FAILED(action.action_id, str(e))
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == "ai_analysis"


class ContentProtectionCompensation(CompensationStrategy):
    """Compensation strategy for content protection operations"""
    
    async def compensate(
        self, 
        action: CompensationAction, 
        context: Dict[str, Any]
    ) -> CompensationResult:
        """Compensate content protection - remove protection"""
        content_id = action.compensation_data.get("content_id")
        
        try:
            # Simulate protection removal
            await asyncio.sleep(0.03)
            logger.info(f"Removed protection for {content_id}")
            
            return CompensationResult.SUCCESS(
                action.action_id,
                f"Protection compensated for {content_id}"
            )
            
        except Exception as e:
            return CompensationResult.FAILED(action.action_id, str(e))
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == "content_protection"


class PaymentProcessingCompensation(CompensationStrategy):
    """Compensation strategy for payment processing operations"""
    
    async def compensate(
        self, 
        action: CompensationAction, 
        context: Dict[str, Any]
    ) -> CompensationResult:
        """Compensate payment - reverse transaction"""
        payment_id = action.compensation_data.get("payment_id")
        amount = action.compensation_data.get("amount")
        creator_id = action.compensation_data.get("creator_id")
        
        try:
            # Simulate payment reversal
            await asyncio.sleep(0.2)
            logger.info(f"Reversed payment {payment_id} amount {amount}")
            
            # Simulate balance update
            await asyncio.sleep(0.1)
            logger.info(f"Updated balance for creator {creator_id}")
            
            return CompensationResult.SUCCESS(
                action.action_id,
                f"Payment {payment_id} reversed: {amount}"
            )
            
        except Exception as e:
            return CompensationResult.FAILED(action.action_id, str(e))
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == "payment_processing"


class SEOOptimizationCompensation(CompensationStrategy):
    """Compensation strategy for SEO optimization operations"""
    
    async def compensate(
        self, 
        action: CompensationAction, 
        context: Dict[str, Any]
    ) -> CompensationResult:
        """Compensate SEO optimization - revert changes"""
        content_id = action.compensation_data.get("content_id")
        
        try:
            # Simulate SEO reversion
            await asyncio.sleep(0.08)
            logger.info(f"Reverted SEO optimization for {content_id}")
            
            return CompensationResult.SUCCESS(
                action.action_id,
                f"SEO optimization compensated for {content_id}"
            )
            
        except Exception as e:
            return CompensationResult.FAILED(action.action_id, str(e))
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == "seo_optimization"


class CompensationTransactionHandler:
    """Main handler for compensation transactions"""
    
    def __init__(self, compensation_store: CompensationStore):
        self.compensation_store = compensation_store
        self.strategies: List[CompensationStrategy] = [
            ContentUploadCompensation(),
            AIAnalysisCompensation(),
            ContentProtectionCompensation(),
            PaymentProcessingCompensation(),
            SEOOptimizationCompensation()
        ]
        self.strategy_map: Dict[str, CompensationStrategy] = {}
        self._build_strategy_map()
    
    def _build_strategy_map(self):
        """Build strategy mapping for fast lookup"""
        for strategy in self.strategies:
            for action_type in ["content_upload", "ai_analysis", "content_protection", 
                              "payment_processing", "seo_optimization"]:
                if strategy.can_handle(action_type):
                    self.strategy_map[action_type] = strategy
    
    async def register_compensation_action(
        self,
        saga_id: str,
        step_id: str,
        action_type: str,
        compensation_data: Dict[str, Any],
        dependencies: List[str] = None
    ) -> str:
        """Register a compensation action"""
        action = CompensationAction(
            action_id=str(uuid.uuid4()),
            action_type=action_type,
            saga_id=saga_id,
            step_id=step_id,
            compensation_data=compensation_data,
            dependencies=dependencies or []
        )
        
        await self.compensation_store.store_action(action)
        logger.info(f"Registered compensation action {action.action_id} for saga {saga_id}")
        
        return action.action_id
    
    async def execute_compensation_workflow(
        self,
        saga_id: str,
        failed_step: str,
        compensation_context: Dict[str, Any] = None
    ) -> CompensationWorkflowResult:
        """Execute complete compensation workflow"""
        context = compensation_context or {}
        start_time = datetime.now(timezone.utc)
        
        # Get all compensation actions for saga
        all_actions = await self.compensation_store.get_actions(saga_id)
        
        # Filter actions to compensate (up to failed step)
        actions_to_compensate = self._filter_actions_until_failure(all_actions, failed_step)
        
        if not actions_to_compensate:
            logger.info(f"No compensation actions needed for saga {saga_id}")
            return CompensationWorkflowResult.COMPLETED(saga_id, [])
        
        # Order compensation actions
        ordered_actions = self._order_compensation_actions(actions_to_compensate)
        
        logger.info(f"Executing compensation for saga {saga_id}: {len(ordered_actions)} actions")
        
        compensation_results = []
        
        # Execute compensation actions
        for action in ordered_actions:
            try:
                result = await self._execute_single_compensation(action, context)
                compensation_results.append(result)
                
                # Log execution
                await self.compensation_store.log_execution(saga_id, action.action_id, result)
                
                if result.status == CompensationStatus.COMPLETED:
                    logger.info(f"Compensation successful for action {action.action_id}")
                else:
                    logger.error(f"Compensation failed for action {action.action_id}: {result.error}")
                
            except Exception as e:
                error_result = CompensationResult.FAILED(action.action_id, str(e))
                compensation_results.append(error_result)
                logger.error(f"Compensation exception for action {action.action_id}: {e}")
        
        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        result = CompensationWorkflowResult.COMPLETED(saga_id, compensation_results)
        result.total_execution_time = execution_time
        
        logger.info(f"Compensation workflow completed for saga {saga_id}: "
                   f"{result.successful_actions}/{result.total_actions} successful")
        
        return result
    
    async def _execute_single_compensation(
        self,
        action: CompensationAction,
        context: Dict[str, Any]
    ) -> CompensationResult:
        """Execute single compensation action with retry logic"""
        strategy = self.strategy_map.get(action.action_type)
        
        if not strategy:
            return CompensationResult.FAILED(
                action.action_id,
                f"No strategy found for action type: {action.action_type}"
            )
        
        last_error = None
        
        for attempt in range(action.max_retries + 1):
            try:
                start_time = datetime.now(timezone.utc)
                result = await strategy.compensate(action, context)
                execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                result.execution_time = execution_time
                
                if result.status == CompensationStatus.COMPLETED:
                    return result
                
                last_error = result.error
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Compensation attempt {attempt + 1} failed for {action.action_id}: {e}")
            
            if attempt < action.max_retries:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return CompensationResult.FAILED(
            action.action_id,
            f"Compensation failed after {action.max_retries + 1} attempts: {last_error}"
        )
    
    def _filter_actions_until_failure(
        self,
        actions: List[CompensationAction],
        failed_step: str
    ) -> List[CompensationAction]:
        """Filter actions that need compensation (up to failed step)"""
        # Sort by creation time to get chronological order
        sorted_actions = sorted(actions, key=lambda x: x.created_at)
        
        # Find failed step index
        failed_index = -1
        for i, action in enumerate(sorted_actions):
            if action.step_id == failed_step:
                failed_index = i
                break
        
        # Return actions up to failed step (excluding failed step itself)
        if failed_index >= 0:
            return sorted_actions[:failed_index]
        else:
            # If failed step not found, compensate all actions
            return sorted_actions
    
    def _order_compensation_actions(
        self,
        actions: List[CompensationAction]
    ) -> List[CompensationAction]:
        """Order compensation actions for optimal execution"""
        # Reverse chronological order (LIFO - Last In, First Out)
        actions.sort(key=lambda x: x.created_at, reverse=True)
        
        # Respect dependencies and priorities
        ordered = []
        remaining = actions.copy()
        
        while remaining:
            # Find actions without unmet dependencies
            ready_actions = []
            for action in remaining:
                dependencies_met = all(
                    dep_id in [a.action_id for a in ordered]
                    for dep_id in action.dependencies
                )
                if dependencies_met:
                    ready_actions.append(action)
            
            if not ready_actions:
                # No actions ready - possible circular dependency
                # Process remaining actions by priority
                ready_actions = sorted(remaining, key=lambda x: x.priority, reverse=True)[:1]
            
            # Sort ready actions by priority
            ready_actions.sort(key=lambda x: x.priority, reverse=True)
            
            # Add ready actions to ordered list
            for action in ready_actions:
                ordered.append(action)
                remaining.remove(action)
        
        return ordered
    
    async def get_compensation_status(self, saga_id: str) -> Dict[str, Any]:
        """Get compensation status for saga"""
        actions = await self.compensation_store.get_actions(saga_id)
        
        return {
            "saga_id": saga_id,
            "total_actions": len(actions),
            "action_types": list(set(action.action_type for action in actions)),
            "created_at": min(action.created_at for action in actions) if actions else None,
            "actions": [
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type,
                    "step_id": action.step_id,
                    "created_at": action.created_at,
                    "dependencies": action.dependencies
                }
                for action in actions
            ]
        }


# Global compensation handler
_compensation_handler: Optional[CompensationTransactionHandler] = None


def get_compensation_transaction_handler() -> CompensationTransactionHandler:
    """Get global compensation transaction handler"""
    global _compensation_handler
    if _compensation_handler is None:
        compensation_store = CompensationStore()
        _compensation_handler = CompensationTransactionHandler(compensation_store)
    
    return _compensation_handler


async def register_compensation(
    saga_id: str,
    step_id: str,
    action_type: str,
    compensation_data: Dict[str, Any],
    dependencies: List[str] = None
) -> str:
    """Convenience function to register compensation action"""
    handler = get_compensation_transaction_handler()
    return await handler.register_compensation_action(
        saga_id, step_id, action_type, compensation_data, dependencies
    )


async def execute_compensation(
    saga_id: str,
    failed_step: str,
    context: Dict[str, Any] = None
) -> CompensationWorkflowResult:
    """Convenience function to execute compensation workflow"""
    handler = get_compensation_transaction_handler()
    return await handler.execute_compensation_workflow(saga_id, failed_step, context)


__all__ = [
    "CompensationTransactionHandler",
    "CompensationAction",
    "CompensationResult",
    "CompensationWorkflowResult",
    "CompensationStatus",
    "CompensationStrategy",
    "CompensationStore",
    "ContentUploadCompensation",
    "AIAnalysisCompensation",
    "ContentProtectionCompensation",
    "PaymentProcessingCompensation",
    "SEOOptimizationCompensation",
    "get_compensation_transaction_handler",
    "register_compensation",
    "execute_compensation"
]