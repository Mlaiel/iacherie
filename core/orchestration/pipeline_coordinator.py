"""Pipeline Coordinator - Advanced Multi-Pipeline Orchestration System

Sophisticated pipeline management system for coordinating complex content processing
pipelines with intelligent load balancing, resource optimization, and quality gates.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class PipelineStatus(Enum):
    """Pipeline execution status enumeration."""    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    MAINTENANCE = "maintenance"


class PipelineType(Enum):
    """Pipeline type classification."""    CONTENT_PROCESSING = "content_processing"
    AI_ENHANCEMENT = "ai_enhancement"
    PROTECTION_WORKFLOW = "protection_workflow"
    MONETIZATION_FLOW = "monetization_flow"
    COLLABORATION_MATCHING = "collaboration_matching"
    DISTRIBUTION_PIPELINE = "distribution_pipeline"
    ANALYTICS_PROCESSING = "analytics_processing"


class QualityGateType(Enum):
    """Quality gate validation types."""    CONTENT_VALIDATION = "content_validation"
    SECURITY_SCAN = "security_scan"
    PERFORMANCE_CHECK = "performance_check"
    BUSINESS_RULES = "business_rules"
    COMPLIANCE_CHECK = "compliance_check"


@dataclass
class QualityGate:
    """Quality gate definition for pipeline validation."""    gate_id: str
    name: str
    gate_type: QualityGateType
    validator: str
    criteria: Dict[str, Any]
    blocking: bool = True
    timeout: int = 300
    retry_count: int = 2
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineStage:
    """Individual pipeline stage definition."""    stage_id: str
    name: str
    processor: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    quality_gates: List[QualityGate] = field(default_factory=list)
    timeout: Optional[int] = None
    retry_count: int = 3
    parallel_execution: bool = False
    dependencies: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineDefinition:
    """Complete pipeline definition structure."""    pipeline_id: str
    name: str
    description: str
    pipeline_type: PipelineType
    stages: List[PipelineStage]
    global_timeout: Optional[int] = None
    max_retries: int = 3
    rollback_enabled: bool = True
    priority: int = 5
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineExecution:
    """Pipeline execution tracking information."""    pipeline_id: str
    execution_id: str
    status: PipelineStatus = PipelineStatus.IDLE
    current_stage: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    completed_stages: int = 0
    total_stages: int = 0
    failed_stages: int = 0
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    stage_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourcePool:
    """Resource pool for pipeline execution."""    pool_id: str
    name: str
    resource_type: str
    capacity: int
    available: int
    allocated: Dict[str, int] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    health_status: str = "healthy"
    metadata: Dict[str, Any] = field(default_factory=dict)


class PipelineCoordinator:
    """    Advanced multi-pipeline orchestration system for enterprise content processing.
    
    Provides comprehensive pipeline coordination capabilities including:
    - Intelligent pipeline scheduling and resource allocation
    - Quality gate validation and compliance checking
    - Cross-pipeline dependency management
    - Performance optimization and load balancing
    - Real-time monitoring and alerting
    """    
    def __init__(self, max_concurrent_pipelines: int = 50):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.max_concurrent_pipelines = max_concurrent_pipelines
        self.pipeline_definitions: Dict[str, PipelineDefinition] = {}
        self.active_executions: Dict[str, PipelineExecution] = {}
        self.stage_processors: Dict[str, Callable] = {}
        self.quality_validators: Dict[str, Callable] = {}
        self.resource_pools: Dict[str, ResourcePool] = {}
        
        # Scheduling and coordination
        self.execution_queue: List[str] = []
        self.priority_queue: List[str] = []
        self.dependency_graph: Dict[str, Set[str]] = {}
        
        # Performance tracking
        self.coordination_stats = {
            'total_pipelines': 0,
            'successful_pipelines': 0,
            'failed_pipelines': 0,
            'average_duration': 0.0,
            'throughput': 0.0,
            'resource_utilization': 0.0,
            'quality_gate_failures': 0
        }
        
        # Optimization settings
        self.load_balancing_enabled = True
        self.auto_scaling_enabled = True
        self.predictive_scheduling = True
        
        self.logger.info("PipelineCoordinator initialized successfully")
    
    async def register_pipeline(self, pipeline_def: PipelineDefinition) -> bool:
        """        Register a new pipeline definition.
        
        Args:
            pipeline_def: Complete pipeline definition
            
        Returns:
            bool: Success status
        """        try:
            # Validate pipeline definition
            if not await self._validate_pipeline_definition(pipeline_def):
                return False
            
            # Store pipeline definition
            self.pipeline_definitions[pipeline_def.pipeline_id] = pipeline_def
            
            # Build dependency graph for this pipeline
            await self._build_pipeline_dependencies(pipeline_def)
            
            # Emit registration event
            await self.event_dispatcher.emit('pipeline_registered', {
                'pipeline_id': pipeline_def.pipeline_id,
                'name': pipeline_def.name,
                'type': pipeline_def.pipeline_type.value,
                'stage_count': len(pipeline_def.stages)
            })
            
            await self.metrics_collector.increment('pipelines.registered')
            self.logger.info(f"Pipeline registered: {pipeline_def.pipeline_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register pipeline: {e}")
            await self.metrics_collector.increment('pipelines.registration_failed')
            return False
    
    async def register_stage_processor(self, processor_name: str, processor_func: Callable) -> bool:
        """        Register a stage processor function.
        
        Args:
            processor_name: Unique processor identifier
            processor_func: Async callable for stage processing
            
        Returns:
            bool: Success status
        """        try:
            if not asyncio.iscoroutinefunction(processor_func):
                raise ValueError("Processor must be an async function")
            
            self.stage_processors[processor_name] = processor_func
            
            await self.metrics_collector.increment('processors.registered')
            self.logger.info(f"Stage processor registered: {processor_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register processor: {e}")
            return False
    
    async def register_quality_validator(self, validator_name: str, validator_func: Callable) -> bool:
        """        Register a quality gate validator function.
        
        Args:
            validator_name: Unique validator identifier
            validator_func: Async callable for quality validation
            
        Returns:
            bool: Success status
        """        try:
            if not asyncio.iscoroutinefunction(validator_func):
                raise ValueError("Validator must be an async function")
            
            self.quality_validators[validator_name] = validator_func
            
            await self.metrics_collector.increment('validators.registered')
            self.logger.info(f"Quality validator registered: {validator_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register validator: {e}")
            return False
    
    async def execute_pipeline(
        self,
        pipeline_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        priority: int = 5
    ) -> str:
        """        Execute a pipeline with given input data.
        
        Args:
            pipeline_id: ID of pipeline to execute
            input_data: Input data for pipeline
            context: Additional execution context
            priority: Execution priority (1-10)
            
        Returns:
            str: Execution ID
        """        execution_id = str(uuid.uuid4())
        
        try:
            # Check pipeline exists
            if pipeline_id not in self.pipeline_definitions:
                raise ValueError(f"Pipeline not found: {pipeline_id}")
            
            # Check concurrency limits
            if len(self.active_executions) >= self.max_concurrent_pipelines:
                raise RuntimeError("Maximum concurrent pipelines reached")
            
            pipeline_def = self.pipeline_definitions[pipeline_id]
            
            # Check resource availability
            if not await self._check_resource_availability(pipeline_def):
                raise RuntimeError("Insufficient resources available")
            
            # Create execution tracking
            execution = PipelineExecution(
                pipeline_id=pipeline_id,
                execution_id=execution_id,
                status=PipelineStatus.IDLE,
                total_stages=len(pipeline_def.stages),
                input_data=input_data,
                context=context or {},
                metadata={'priority': priority}
            )
            
            self.active_executions[execution_id] = execution
            
            # Allocate resources
            await self._allocate_resources(execution_id, pipeline_def)
            
            # Add to execution queue
            if priority >= 8:
                self.priority_queue.append(execution_id)
            else:
                self.execution_queue.append(execution_id)
            
            # Start pipeline execution
            asyncio.create_task(self._execute_pipeline_async(execution_id))
            
            await self.event_dispatcher.emit('pipeline_started', {
                'pipeline_id': pipeline_id,
                'execution_id': execution_id,
                'priority': priority,
                'input_size': len(json.dumps(input_data))
            })
            
            await self.metrics_collector.increment('pipelines.started')
            self.logger.info(f"Pipeline execution started: {execution_id}")
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to start pipeline: {e}")
            await self.metrics_collector.increment('pipelines.start_failed')
            raise
    
    async def _execute_pipeline_async(self, execution_id: str) -> None:
        """        Internal asynchronous pipeline execution.
        
        Args:
            execution_id: Unique execution identifier
        """        execution = self.active_executions[execution_id]
        pipeline_def = self.pipeline_definitions[execution.pipeline_id]
        
        try:
            execution.status = PipelineStatus.RUNNING
            execution.start_time = datetime.now()
            
            # Execute pipeline stages
            await self._execute_pipeline_stages(execution_id)
            
            # Finalize execution
            execution.end_time = datetime.now()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            
            if execution.failed_stages == 0:
                execution.status = PipelineStatus.COMPLETED
                self.coordination_stats['successful_pipelines'] += 1
            else:
                execution.status = PipelineStatus.FAILED
                self.coordination_stats['failed_pipelines'] += 1
            
            # Update statistics
            self.coordination_stats['total_pipelines'] += 1
            self._update_performance_stats()
            
            await self.event_dispatcher.emit('pipeline_completed', {
                'pipeline_id': execution.pipeline_id,
                'execution_id': execution_id,
                'status': execution.status.value,
                'duration': execution.duration,
                'completed_stages': execution.completed_stages,
                'failed_stages': execution.failed_stages,
                'quality_score': execution.quality_metrics.get('overall_score', 0.0)
            })
            
            await self.metrics_collector.record('pipeline.duration', execution.duration)
            await self.metrics_collector.increment(f'pipelines.{execution.status.value}')
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.end_time = datetime.now()
            execution.errors.append(str(e))
            
            self.logger.error(f"Pipeline execution failed: {e}")
            await self.metrics_collector.increment('pipelines.execution_failed')
        
        finally:
            # Release resources
            await self._release_resources(execution_id)
            
            # Cleanup
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _execute_pipeline_stages(self, execution_id: str) -> None:
        """Execute all pipeline stages in sequence."""        execution = self.active_executions[execution_id]
        pipeline_def = self.pipeline_definitions[execution.pipeline_id]
        
        current_data = execution.input_data.copy()
        
        for stage in pipeline_def.stages:
            try:
                execution.current_stage = stage.stage_id
                
                # Check stage dependencies
                if not await self._check_stage_dependencies(execution_id, stage):
                    continue
                
                # Execute quality gates (pre-stage)
                if not await self._execute_quality_gates(execution_id, stage, current_data, 'pre'):
                    execution.failed_stages += 1
                    if stage.stage_id in [s.stage_id for s in pipeline_def.stages if s.retry_count == 0]:
                        break
                    continue
                
                # Execute stage processor
                stage_result = await self._execute_stage_processor(
                    execution_id, stage, current_data
                )
                
                if stage_result is not None:
                    execution.stage_results[stage.stage_id] = stage_result
                    current_data.update(stage_result.get('output_data', {}))
                    
                    # Execute quality gates (post-stage)
                    if await self._execute_quality_gates(execution_id, stage, current_data, 'post'):
                        execution.completed_stages += 1
                    else:
                        execution.failed_stages += 1
                else:
                    execution.failed_stages += 1
                
            except Exception as e:
                execution.errors.append(f"Stage {stage.stage_id}: {str(e)}")
                execution.failed_stages += 1
                self.logger.error(f"Stage execution failed: {stage.stage_id} - {e}")
        
        # Set final output data
        execution.output_data = current_data
        execution.current_stage = None
    
    async def _execute_stage_processor(
        self,
        execution_id: str,
        stage: PipelineStage,
        input_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """        Execute individual stage processor.
        
        Args:
            execution_id: Pipeline execution ID
            stage: Stage definition
            input_data: Input data for stage
            
        Returns:
            Optional[Dict[str, Any]]: Stage execution result
        """        execution = self.active_executions[execution_id]
        
        try:
            # Get stage processor
            if stage.processor not in self.stage_processors:
                raise ValueError(f"Processor not found: {stage.processor}")
            
            processor = self.stage_processors[stage.processor]
            
            # Prepare processor input
            processor_input = {
                'data': input_data,
                'parameters': stage.parameters,
                'context': execution.context,
                'execution_id': execution_id,
                'stage_id': stage.stage_id
            }
            
            # Execute with timeout
            start_time = datetime.now()
            
            if stage.timeout:
                result = await asyncio.wait_for(
                    processor(processor_input),
                    timeout=stage.timeout
                )
            else:
                result = await processor(processor_input)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            await self.event_dispatcher.emit('stage_completed', {
                'stage_id': stage.stage_id,
                'execution_id': execution_id,
                'duration': duration,
                'processor': stage.processor
            })
            
            await self.metrics_collector.record('stage.duration', duration)
            await self.metrics_collector.increment('stages.completed')
            
            return result
            
        except asyncio.TimeoutError:
            raise Exception(f"Stage timeout after {stage.timeout} seconds")
        except Exception as e:
            await self.metrics_collector.increment('stages.failed')
            raise e
    
    async def _execute_quality_gates(
        self,
        execution_id: str,
        stage: PipelineStage,
        data: Dict[str, Any],
        phase: str
    ) -> bool:
        """        Execute quality gates for stage validation.
        
        Args:
            execution_id: Pipeline execution ID
            stage: Stage definition
            data: Data to validate
            phase: Validation phase ('pre' or 'post')
            
        Returns:
            bool: All quality gates passed
        """        execution = self.active_executions[execution_id]
        
        for gate in stage.quality_gates:
            try:
                # Get validator
                if gate.validator not in self.quality_validators:
                    self.logger.warning(f"Validator not found: {gate.validator}")
                    continue
                
                validator = self.quality_validators[gate.validator]
                
                # Prepare validation input
                validation_input = {
                    'data': data,
                    'criteria': gate.criteria,
                    'context': execution.context,
                    'execution_id': execution_id,
                    'stage_id': stage.stage_id,
                    'gate_id': gate.gate_id,
                    'phase': phase
                }
                
                # Execute validation
                if gate.timeout:
                    validation_result = await asyncio.wait_for(
                        validator(validation_input),
                        timeout=gate.timeout
                    )
                else:
                    validation_result = await validator(validation_input)
                
                # Check result
                if not validation_result.get('passed', False):
                    if gate.blocking:
                        execution.quality_metrics[f'{gate.gate_id}_failed'] = True
                        self.coordination_stats['quality_gate_failures'] += 1
                        
                        await self.event_dispatcher.emit('quality_gate_failed', {
                            'gate_id': gate.gate_id,
                            'stage_id': stage.stage_id,
                            'execution_id': execution_id,
                            'reason': validation_result.get('reason', 'Unknown')
                        })
                        
                        await self.metrics_collector.increment('quality_gates.failed')
                        return False
                    else:
                        self.logger.warning(f"Non-blocking quality gate failed: {gate.gate_id}")
                
                execution.quality_metrics[f'{gate.gate_id}_score'] = validation_result.get('score', 0.0)
                
            except Exception as e:
                if gate.blocking:
                    self.logger.error(f"Quality gate execution failed: {gate.gate_id} - {e}")
                    return False
                else:
                    self.logger.warning(f"Non-blocking quality gate failed: {gate.gate_id} - {e}")
        
        return True
    
    async def _validate_pipeline_definition(self, pipeline_def: PipelineDefinition) -> bool:
        """Validate pipeline definition structure."""        try:
            # Check basic structure
            if not pipeline_def.pipeline_id or not pipeline_def.name:
                return False
            
            # Check stage definitions
            stage_ids = set()
            for stage in pipeline_def.stages:
                if not stage.stage_id or not stage.processor:
                    return False
                
                if stage.stage_id in stage_ids:
                    return False  # Duplicate stage ID
                
                stage_ids.add(stage.stage_id)
            
            # Check dependencies
            for stage in pipeline_def.stages:
                for dep in stage.dependencies:
                    if dep not in stage_ids:
                        return False  # Invalid dependency
            
            return True
            
        except Exception:
            return False
    
    async def _build_pipeline_dependencies(self, pipeline_def: PipelineDefinition) -> None:
        """Build pipeline stage dependency graph."""        pipeline_id = pipeline_def.pipeline_id
        self.dependency_graph[pipeline_id] = {}
        
        for stage in pipeline_def.stages:
            self.dependency_graph[pipeline_id][stage.stage_id] = set(stage.dependencies)
    
    async def _check_stage_dependencies(self, execution_id: str, stage: PipelineStage) -> bool:
        """Check if stage dependencies are satisfied."""        execution = self.active_executions[execution_id]
        
        # Check all dependencies are completed
        for dep_id in stage.dependencies:
            if dep_id not in execution.stage_results:
                return False
        
        return True
    
    async def _check_resource_availability(self, pipeline_def: PipelineDefinition) -> bool:
        """Check if required resources are available."""        required_resources = pipeline_def.resource_requirements
        
        for resource_type, required_amount in required_resources.items():
            if resource_type in self.resource_pools:
                pool = self.resource_pools[resource_type]
                if pool.available < required_amount:
                    return False
        
        return True
    
    async def _allocate_resources(self, execution_id: str, pipeline_def: PipelineDefinition) -> None:
        """Allocate resources for pipeline execution."""        required_resources = pipeline_def.resource_requirements
        
        for resource_type, required_amount in required_resources.items():
            if resource_type in self.resource_pools:
                pool = self.resource_pools[resource_type]
                pool.available -= required_amount
                pool.allocated[execution_id] = required_amount
    
    async def _release_resources(self, execution_id: str) -> None:
        """Release allocated resources."""        for pool in self.resource_pools.values():
            if execution_id in pool.allocated:
                pool.available += pool.allocated[execution_id]
                del pool.allocated[execution_id]
    
    def _update_performance_stats(self) -> None:
        """Update coordination performance statistics."""        if self.coordination_stats['total_pipelines'] > 0:
            # Calculate resource utilization
            total_capacity = sum(pool.capacity for pool in self.resource_pools.values())
            total_available = sum(pool.available for pool in self.resource_pools.values())
            
            if total_capacity > 0:
                self.coordination_stats['resource_utilization'] = (
                    (total_capacity - total_available) / total_capacity
                )
    
    async def add_resource_pool(self, pool: ResourcePool) -> bool:
        """Add a new resource pool."""        try:
            self.resource_pools[pool.pool_id] = pool
            
            await self.event_dispatcher.emit('resource_pool_added', {
                'pool_id': pool.pool_id,
                'resource_type': pool.resource_type,
                'capacity': pool.capacity
            })
            
            await self.metrics_collector.increment('resource_pools.added')
            self.logger.info(f"Resource pool added: {pool.pool_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add resource pool: {e}")
            return False
    
    async def get_pipeline_status(self, execution_id: str) -> Optional[PipelineExecution]:
        """Get current pipeline execution status."""        return self.active_executions.get(execution_id)
    
    async def cancel_pipeline(self, execution_id: str) -> bool:
        """Cancel running pipeline execution."""        try:
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                execution.status = PipelineStatus.CANCELLED
                execution.end_time = datetime.now()
                
                await self.event_dispatcher.emit('pipeline_cancelled', {
                    'execution_id': execution_id,
                    'pipeline_id': execution.pipeline_id
                })
                
                await self.metrics_collector.increment('pipelines.cancelled')
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel pipeline: {e}")
            return False
    
    async def get_coordination_stats(self) -> Dict[str, Any]:
        """Get coordinator performance statistics."""        return {
            **self.coordination_stats,
            'active_pipelines': len(self.active_executions),
            'registered_pipelines': len(self.pipeline_definitions),
            'registered_processors': len(self.stage_processors),
            'registered_validators': len(self.quality_validators),
            'resource_pools': len(self.resource_pools),
            'queue_length': len(self.execution_queue),
            'priority_queue_length': len(self.priority_queue)
        }
