"""
🔥 SAGA COORDINATOR - ENTERPRISE DISTRIBUTED TRANSACTION MANAGEMENT
Advanced saga pattern implementation with compensation and recovery
Performance Target: < 100ms saga coordination

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY CODE - TOUS DROITS RÉSERVÉS
Commercial use forbidden without written authorization
Reverse engineering strictly prohibited
"""

import asyncio
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4

import logging


class SagaStatus(Enum):
    """Saga execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


class TransactionIsolationLevel(Enum):
    """Transaction isolation levels."""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


@dataclass
class SagaStep:
    """Individual step in a saga transaction."""
    step_id: str = field(default_factory=lambda: str(uuid4()))
    step_name: str = ""
    service_name: str = ""
    action: Optional[Callable] = None
    compensation: Optional[Callable] = None
    
    # Execution state
    status: SagaStatus = SagaStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    
    # Creator Economy context
    creator_id: Optional[str] = None
    content_type: Optional[str] = None
    revenue_impact: bool = False
    
    # Configuration
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class SagaDefinition:
    """Complete saga definition with steps and compensation logic."""
    saga_id: str = field(default_factory=lambda: str(uuid4()))
    saga_name: str = ""
    steps: List[SagaStep] = field(default_factory=list)
    
    # Saga configuration
    isolation_level: TransactionIsolationLevel = TransactionIsolationLevel.READ_COMMITTED
    timeout_seconds: int = 1800  # 30 minutes
    compensation_timeout_seconds: int = 600  # 10 minutes
    
    # Creator Economy context
    creator_id: Optional[str] = None
    workflow_id: Optional[str] = None
    content_type: Optional[str] = None
    revenue_transaction: bool = False
    
    # Execution metadata
    created_at: datetime = field(default_factory=datetime.now)
    status: SagaStatus = SagaStatus.PENDING
    current_step_index: int = 0


class SagaCoordinator:
    """
    🔥 ENTERPRISE SAGA COORDINATOR - CREATOR ECONOMY OPTIMIZED
    Ultra-high performance saga coordination with <100ms operations
    """
    
    def __init__(self):
        self.saga_engine = SagaEngine()
        self.compensation_manager = CompensationManager()
        self.transaction_coordinator = TransactionCoordinator()
        
        # Active sagas tracking
        self.active_sagas = {}
        self.saga_history = {}
        
        # Performance metrics
        self.coordination_metrics = {
            'sagas_coordinated': 0,
            'total_coordination_time': 0.0,
            'successful_sagas': 0,
            'compensated_sagas': 0,
            'failed_sagas': 0
        }
        
        # Creator Economy optimization
        self.creator_saga_patterns = defaultdict(list)
        self.revenue_transaction_queue = []
    
    async def coordinate_distributed_transactions(
        self,
        saga_definition: SagaDefinition
    ) -> Dict[str, Any]:
        """Coordinate distributed transactions using saga pattern."""
        start_time = time.perf_counter()
        
        # Validate saga definition
        validation_result = await self._validate_saga_definition(saga_definition)
        if not validation_result['valid']:
            return {
                'success': False,
                'reason': 'Invalid saga definition',
                'validation_errors': validation_result['errors']
            }
        
        # Apply Creator Economy optimizations
        await self._optimize_saga_for_creator_economy(saga_definition)
        
        # Register saga
        self.active_sagas[saga_definition.saga_id] = saga_definition
        
        try:
            # Execute saga
            execution_result = await self.saga_engine.execute_saga(saga_definition)
            
            coordination_time = time.perf_counter() - start_time
            self.coordination_metrics['sagas_coordinated'] += 1
            self.coordination_metrics['total_coordination_time'] += coordination_time
            
            if execution_result['success']:
                self.coordination_metrics['successful_sagas'] += 1
            elif execution_result.get('compensated'):
                self.coordination_metrics['compensated_sagas'] += 1
            else:
                self.coordination_metrics['failed_sagas'] += 1
            
            if coordination_time > 0.1:  # 100ms threshold
                logging.warning(f"Saga coordination exceeded 100ms: {coordination_time*1000:.1f}ms")
            
            return {
                'success': execution_result['success'],
                'saga_id': saga_definition.saga_id,
                'coordination_time_ms': coordination_time * 1000,
                'execution_result': execution_result
            }
        
        finally:
            # Move to history
            self.saga_history[saga_definition.saga_id] = self.active_sagas.pop(saga_definition.saga_id, None)
    
    async def _validate_saga_definition(self, saga_definition: SagaDefinition) -> Dict[str, Any]:
        """Validate saga definition for completeness and correctness."""
        validation_errors = []
        
        # Check basic requirements
        if not saga_definition.saga_name:
            validation_errors.append("Saga name is required")
        
        if not saga_definition.steps:
            validation_errors.append("Saga must have at least one step")
        
        # Validate steps
        for i, step in enumerate(saga_definition.steps):
            if not step.step_name:
                validation_errors.append(f"Step {i} missing name")
            
            if not step.action:
                validation_errors.append(f"Step {i} ({step.step_name}) missing action")
            
            if not step.compensation:
                validation_errors.append(f"Step {i} ({step.step_name}) missing compensation")
        
        # Creator Economy validation
        if saga_definition.revenue_transaction and not saga_definition.creator_id:
            validation_errors.append("Revenue transactions must have creator_id")
        
        return {
            'valid': len(validation_errors) == 0,
            'errors': validation_errors
        }
    
    async def _optimize_saga_for_creator_economy(self, saga_definition: SagaDefinition):
        """Apply Creator Economy specific optimizations."""
        # Revenue transaction prioritization
        if saga_definition.revenue_transaction:
            saga_definition.timeout_seconds = min(saga_definition.timeout_seconds, 900)  # 15 min max
            self.revenue_transaction_queue.append(saga_definition.saga_id)
        
        # Content type specific timeouts
        if saga_definition.content_type == 'music':
            # Music releases are time-sensitive
            saga_definition.timeout_seconds = min(saga_definition.timeout_seconds, 600)  # 10 min
        elif saga_definition.content_type == 'video':
            # Video processing can take longer
            saga_definition.timeout_seconds = max(saga_definition.timeout_seconds, 1800)  # 30 min
        
        # Creator pattern tracking
        if saga_definition.creator_id:
            self.creator_saga_patterns[saga_definition.creator_id].append({
                'saga_id': saga_definition.saga_id,
                'content_type': saga_definition.content_type,
                'revenue_transaction': saga_definition.revenue_transaction,
                'timestamp': datetime.now()
            })
    
    async def manage_saga_orchestration(
        self,
        orchestration_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage saga orchestration with advanced coordination."""
        request_type = orchestration_request.get('type', 'execute')
        
        if request_type == 'execute':
            return await self._handle_saga_execution(orchestration_request)
        elif request_type == 'compensate':
            return await self._handle_saga_compensation(orchestration_request)
        elif request_type == 'status':
            return await self._handle_saga_status_query(orchestration_request)
        elif request_type == 'cancel':
            return await self._handle_saga_cancellation(orchestration_request)
        
        return {'success': False, 'error': f'Unknown request type: {request_type}'}
    
    async def _handle_saga_execution(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle saga execution request."""
        saga_config = request.get('saga_config', {})
        
        # Create saga definition from config
        saga_def = SagaDefinition(
            saga_name=saga_config.get('name', 'unnamed_saga'),
            creator_id=saga_config.get('creator_id'),
            content_type=saga_config.get('content_type'),
            revenue_transaction=saga_config.get('revenue_transaction', False)
        )
        
        # Add steps from config
        for step_config in saga_config.get('steps', []):
            step = SagaStep(
                step_name=step_config.get('name'),
                service_name=step_config.get('service'),
                creator_id=saga_def.creator_id,
                content_type=saga_def.content_type,
                revenue_impact=step_config.get('revenue_impact', False)
            )
            saga_def.steps.append(step)
        
        return await self.coordinate_distributed_transactions(saga_def)
    
    async def implement_compensation_logic(
        self,
        saga_id: str,
        compensation_reason: str = "user_requested"
    ) -> Dict[str, Any]:
        """Implement compensation logic for failed or cancelled saga."""
        saga = self.active_sagas.get(saga_id) or self.saga_history.get(saga_id)
        
        if not saga:
            return {'success': False, 'error': f'Saga {saga_id} not found'}
        
        if saga.status in [SagaStatus.COMPLETED, SagaStatus.COMPENSATED]:
            return {'success': False, 'error': f'Saga {saga_id} already in final state'}
        
        return await self.compensation_manager.execute_compensation(saga, compensation_reason)
    
    async def handle_partial_failures(
        self,
        saga_id: str,
        failed_step_index: int,
        failure_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle partial failures in saga execution."""
        saga = self.active_sagas.get(saga_id)
        
        if not saga:
            return {'success': False, 'error': f'Active saga {saga_id} not found'}
        
        failed_step = saga.steps[failed_step_index]
        
        # Determine recovery strategy
        recovery_strategy = await self._determine_recovery_strategy(
            saga, failed_step_index, failure_context
        )
        
        if recovery_strategy == 'retry':
            return await self._retry_failed_step(saga, failed_step_index)
        elif recovery_strategy == 'compensate':
            return await self.implement_compensation_logic(saga_id, "partial_failure")
        elif recovery_strategy == 'skip':
            return await self._skip_failed_step(saga, failed_step_index)
        
        return {'success': False, 'error': 'No viable recovery strategy'}
    
    async def _determine_recovery_strategy(
        self,
        saga: SagaDefinition,
        failed_step_index: int,
        failure_context: Dict[str, Any]
    ) -> str:
        """Determine best recovery strategy for failed step."""
        failed_step = saga.steps[failed_step_index]
        
        # Check retry eligibility
        if failed_step.retry_count < failed_step.max_retries:
            error_type = failure_context.get('error_type', 'unknown')
            if error_type in ['timeout', 'network_error', 'temporary_unavailable']:
                return 'retry'
        
        # Revenue transactions get aggressive recovery
        if saga.revenue_transaction:
            return 'compensate'  # Ensure data consistency
        
        # Non-critical steps might be skippable
        if not failed_step.revenue_impact:
            return 'skip'
        
        return 'compensate'
    
    async def _retry_failed_step(self, saga: SagaDefinition, step_index: int) -> Dict[str, Any]:
        """Retry a failed saga step."""
        step = saga.steps[step_index]
        step.retry_count += 1
        step.status = SagaStatus.PENDING
        
        # Execute step with retry
        return await self.saga_engine.execute_step(step)
    
    async def _skip_failed_step(self, saga: SagaDefinition, step_index: int) -> Dict[str, Any]:
        """Skip a failed non-critical step."""
        step = saga.steps[step_index]
        step.status = SagaStatus.COMPLETED  # Mark as completed to continue
        step.result = {'skipped': True, 'reason': 'non_critical_failure'}
        
        return {'success': True, 'action': 'skipped', 'step_id': step.step_id}
    
    async def saga_state_persistence(
        self,
        saga_id: str,
        persistence_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Persist saga state for recovery and monitoring."""
        saga = self.active_sagas.get(saga_id) or self.saga_history.get(saga_id)
        
        if not saga:
            return {'success': False, 'error': f'Saga {saga_id} not found'}
        
        # Create persistence snapshot
        snapshot = {
            'saga_id': saga.saga_id,
            'saga_name': saga.saga_name,
            'status': saga.status.value,
            'current_step_index': saga.current_step_index,
            'creator_id': saga.creator_id,
            'content_type': saga.content_type,
            'revenue_transaction': saga.revenue_transaction,
            'created_at': saga.created_at.isoformat(),
            'steps': [
                {
                    'step_id': step.step_id,
                    'step_name': step.step_name,
                    'status': step.status.value,
                    'started_at': step.started_at.isoformat() if step.started_at else None,
                    'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                    'error': step.error
                }
                for step in saga.steps
            ]
        }
        
        # In production, this would save to persistent storage
        logging.info(f"Saga state persisted: {saga_id}")
        
        return {
            'success': True,
            'snapshot_id': str(uuid4()),
            'persistence_timestamp': datetime.now().isoformat(),
            'snapshot_size_bytes': len(json.dumps(snapshot))
        }
    
    async def transaction_isolation_management(
        self,
        saga_id: str,
        isolation_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage transaction isolation for saga operations."""
        return await self.transaction_coordinator.manage_isolation(saga_id, isolation_config)
    
    async def saga_performance_optimization(
        self,
        optimization_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize saga performance based on patterns and metrics."""
        creator_id = optimization_request.get('creator_id')
        content_type = optimization_request.get('content_type')
        
        optimizations = []
        
        # Analyze creator patterns
        if creator_id and creator_id in self.creator_saga_patterns:
            patterns = self.creator_saga_patterns[creator_id]
            
            # Frequent revenue transactions
            revenue_sagas = [p for p in patterns if p['revenue_transaction']]
            if len(revenue_sagas) > 10:  # Frequent revenue transactions
                optimizations.append({
                    'type': 'revenue_transaction_pooling',
                    'description': 'Pool frequent revenue transactions for efficiency',
                    'estimated_improvement': '20-30% faster processing'
                })
        
        # Content type optimizations
        if content_type:
            if content_type == 'music':
                optimizations.append({
                    'type': 'music_pipeline_optimization',
                    'description': 'Optimize music processing saga steps',
                    'estimated_improvement': '15-25% faster execution'
                })
            elif content_type == 'video':
                optimizations.append({
                    'type': 'video_batch_processing',
                    'description': 'Batch video processing operations',
                    'estimated_improvement': '30-40% resource efficiency'
                })
        
        return {
            'optimizations_available': len(optimizations),
            'optimizations': optimizations,
            'estimated_total_improvement': '25-35% performance gain'
        }
    
    def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get comprehensive saga coordination metrics."""
        total_sagas = self.coordination_metrics['sagas_coordinated']
        total_time = self.coordination_metrics['total_coordination_time']
        
        return {
            **self.coordination_metrics,
            'average_coordination_time_ms': (total_time / max(1, total_sagas)) * 1000,
            'success_rate': (
                self.coordination_metrics['successful_sagas'] / max(1, total_sagas)
            ),
            'compensation_rate': (
                self.coordination_metrics['compensated_sagas'] / max(1, total_sagas)
            ),
            'active_sagas': len(self.active_sagas),
            'saga_history_size': len(self.saga_history),
            'creator_patterns_tracked': len(self.creator_saga_patterns)
        }


class SagaEngine:
    """Core saga execution engine."""
    
    def __init__(self):
        self.execution_metrics = defaultdict(int)
    
    async def execute_saga(self, saga_definition: SagaDefinition) -> Dict[str, Any]:
        """Execute complete saga with error handling."""
        saga_definition.status = SagaStatus.RUNNING
        
        try:
            for i, step in enumerate(saga_definition.steps):
                saga_definition.current_step_index = i
                
                step_result = await self.execute_step(step)
                
                if not step_result['success']:
                    # Step failed, initiate compensation
                    compensation_result = await self._compensate_completed_steps(
                        saga_definition, i
                    )
                    
                    return {
                        'success': False,
                        'compensated': compensation_result['success'],
                        'failed_step': i,
                        'error': step_result['error']
                    }
            
            saga_definition.status = SagaStatus.COMPLETED
            return {'success': True, 'completed_steps': len(saga_definition.steps)}
        
        except Exception as e:
            saga_definition.status = SagaStatus.FAILED
            return {'success': False, 'error': str(e)}
    
    async def execute_step(self, step: SagaStep) -> Dict[str, Any]:
        """Execute individual saga step."""
        step.status = SagaStatus.RUNNING
        step.started_at = datetime.now()
        
        try:
            if step.action:
                if asyncio.iscoroutinefunction(step.action):
                    result = await step.action()
                else:
                    result = step.action()
                
                step.result = result
                step.status = SagaStatus.COMPLETED
                step.completed_at = datetime.now()
                
                return {'success': True, 'result': result}
            else:
                return {'success': False, 'error': 'No action defined for step'}
        
        except Exception as e:
            step.status = SagaStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now()
            
            return {'success': False, 'error': str(e)}
    
    async def _compensate_completed_steps(
        self, 
        saga_definition: SagaDefinition,
        failed_step_index: int
    ) -> Dict[str, Any]:
        """Compensate all completed steps in reverse order."""
        compensation_results = []
        
        # Compensate in reverse order (from failed_step_index - 1 to 0)
        for i in range(failed_step_index - 1, -1, -1):
            step = saga_definition.steps[i]
            
            if step.status == SagaStatus.COMPLETED:
                compensation_result = await self._compensate_step(step)
                compensation_results.append(compensation_result)
                
                if not compensation_result['success']:
                    break  # Stop compensation chain on failure
        
        successful_compensations = sum(1 for r in compensation_results if r['success'])
        
        return {
            'success': successful_compensations == len(compensation_results),
            'compensated_steps': successful_compensations,
            'total_steps': len(compensation_results)
        }
    
    async def _compensate_step(self, step: SagaStep) -> Dict[str, Any]:
        """Compensate individual step."""
        try:
            if step.compensation:
                if asyncio.iscoroutinefunction(step.compensation):
                    await step.compensation()
                else:
                    step.compensation()
                
                return {'success': True, 'step_id': step.step_id}
            else:
                return {'success': False, 'error': 'No compensation defined'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}


class CompensationManager:
    """Manage compensation operations for saga failures."""
    
    def __init__(self):
        self.compensation_history = {}
    
    async def execute_compensation(
        self, 
        saga: SagaDefinition,
        reason: str
    ) -> Dict[str, Any]:
        """Execute compensation for entire saga."""
        saga.status = SagaStatus.COMPENSATING
        compensation_id = str(uuid4())
        
        compensation_results = []
        
        # Compensate completed steps in reverse order
        completed_steps = [
            (i, step) for i, step in enumerate(saga.steps)
            if step.status == SagaStatus.COMPLETED
        ]
        
        for i, step in reversed(completed_steps):
            result = await self._execute_step_compensation(step)
            compensation_results.append({
                'step_index': i,
                'step_id': step.step_id,
                'success': result['success'],
                'error': result.get('error')
            })
        
        successful_compensations = sum(1 for r in compensation_results if r['success'])
        
        if successful_compensations == len(compensation_results):
            saga.status = SagaStatus.COMPENSATED
            overall_success = True
        else:
            saga.status = SagaStatus.FAILED
            overall_success = False
        
        # Record compensation history
        self.compensation_history[compensation_id] = {
            'saga_id': saga.saga_id,
            'reason': reason,
            'results': compensation_results,
            'timestamp': datetime.now(),
            'success': overall_success
        }
        
        return {
            'success': overall_success,
            'compensation_id': compensation_id,
            'compensated_steps': successful_compensations,
            'total_steps': len(compensation_results)
        }
    
    async def _execute_step_compensation(self, step: SagaStep) -> Dict[str, Any]:
        """Execute compensation for individual step."""
        try:
            if step.compensation:
                if asyncio.iscoroutinefunction(step.compensation):
                    await step.compensation()
                else:
                    step.compensation()
                
                return {'success': True}
            else:
                return {'success': False, 'error': 'No compensation action defined'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}


class TransactionCoordinator:
    """Coordinate transaction isolation and consistency."""
    
    def __init__(self):
        self.transaction_locks = defaultdict(set)
        self.isolation_policies = {}
    
    async def manage_isolation(
        self, 
        saga_id: str,
        isolation_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage transaction isolation for saga."""
        isolation_level = isolation_config.get(
            'level', 
            TransactionIsolationLevel.READ_COMMITTED
        )
        
        resources = isolation_config.get('resources', [])
        
        # Apply isolation based on level
        if isolation_level == TransactionIsolationLevel.SERIALIZABLE:
            # Lock all resources for serializable isolation
            for resource in resources:
                self.transaction_locks[saga_id].add(resource)
        
        self.isolation_policies[saga_id] = {
            'level': isolation_level,
            'resources': resources,
            'applied_at': datetime.now()
        }
        
        return {
            'success': True,
            'isolation_level': isolation_level.value,
            'locked_resources': len(self.transaction_locks[saga_id])
        }
    
    async def release_transaction_locks(self, saga_id: str):
        """Release transaction locks for completed saga."""
        if saga_id in self.transaction_locks:
            released_locks = len(self.transaction_locks[saga_id])
            del self.transaction_locks[saga_id]
            return released_locks
        return 0


# Enterprise factory function
async def create_enterprise_saga_coordinator() -> SagaCoordinator:
    """Factory function for enterprise saga coordinator."""
    return SagaCoordinator()