"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Saga Orchestrator Template for Ainflue Microservices Platform
============================================================

Enterprise-grade distributed transaction coordination template providing:
- Saga pattern implementation with orchestration
- Compensation action management and rollback
- Distributed transaction state management
- Event-driven saga coordination
- Timeout and failure handling
- Saga execution monitoring and tracking
- Parallel and sequential step execution
- Transaction isolation and consistency
- Performance optimization and metrics
- Integration with microservices ecosystem

Author: Fahed Mlaiel (mlaiel@live.de)
Microservices Architect & Distributed Systems Specialist
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Type, Union, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
from collections import defaultdict

from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import aiohttp

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus
from ..communication_manager import CommunicationManager, CommunicationConfig
from ..circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class SagaStatus(str, Enum):
    """Saga execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Saga step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    SKIPPED = "skipped"


class StepType(str, Enum):
    """Saga step types"""
    ACTION = "action"
    COMPENSATION = "compensation"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class SagaStep(BaseModel):
    """Saga step definition"""
    id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Human-readable step name")
    step_type: StepType = Field(default=StepType.ACTION, description="Step type")
    service_name: str = Field(..., description="Target service name")
    action: str = Field(..., description="Action to execute")
    compensation_action: Optional[str] = Field(default=None, description="Compensation action")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Step parameters")
    dependencies: List[str] = Field(default_factory=list, description="Step dependencies")
    timeout_seconds: int = Field(default=30, description="Step timeout")
    retry_policy: Dict[str, Any] = Field(default_factory=dict, description="Retry policy")
    condition: Optional[str] = Field(default=None, description="Execution condition")
    parallel_steps: List["SagaStep"] = Field(default_factory=list, description="Parallel sub-steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


SagaStep.model_rebuild()


class SagaDefinition(BaseModel):
    """Saga definition"""
    id: str = Field(..., description="Unique saga identifier")
    name: str = Field(..., description="Human-readable saga name")
    description: Optional[str] = Field(default=None, description="Saga description")
    steps: List[SagaStep] = Field(..., description="Saga steps")
    global_timeout_seconds: int = Field(default=300, description="Global saga timeout")
    auto_compensation: bool = Field(default=True, description="Enable automatic compensation")
    isolation_level: str = Field(default="read_committed", description="Transaction isolation level")
    concurrency_control: Dict[str, Any] = Field(default_factory=dict, description="Concurrency control")
    monitoring_config: Dict[str, Any] = Field(default_factory=dict, description="Monitoring configuration")
    tags: List[str] = Field(default_factory=list, description="Saga tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SagaExecution(Base):
    """Saga execution record"""
    __tablename__ = "saga_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    saga_id = Column(String, nullable=False, index=True)
    execution_id = Column(String, nullable=False)
    status = Column(String, nullable=False, default=SagaStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    steps_completed = Column(Integer, default=0)
    steps_failed = Column(Integer, default=0)
    steps_compensated = Column(Integer, default=0)
    execution_context = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@dataclass
class StepExecutionContext:
    """Step execution context"""
    step_id: str
    execution_id: str
    saga_id: str
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    compensation_executed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SagaExecutionContext:
    """Saga execution context"""
    saga_id: str
    execution_id: str
    definition: SagaDefinition
    status: SagaStatus = SagaStatus.PENDING
    started_at: Optional[datetime] = None
    step_contexts: Dict[str, StepExecutionContext] = field(default_factory=dict)
    global_context: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    compensation_stack: List[str] = field(default_factory=list)


class SagaOrchestratorConfig(ServiceConfig):
    """Saga orchestrator service configuration"""
    # Redis settings for state management
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=4, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # Service discovery
    service_registry_url: Optional[str] = Field(default=None, description="Service registry URL")
    service_timeout_seconds: int = Field(default=30, description="Default service call timeout")
    
    # Execution settings
    max_concurrent_sagas: int = Field(default=100, description="Maximum concurrent saga executions")
    default_retry_attempts: int = Field(default=3, description="Default retry attempts")
    state_persistence_interval: int = Field(default=5, description="State persistence interval in seconds")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable saga metrics")
    enable_tracing: bool = Field(default=True, description="Enable distributed tracing")
    metrics_retention_hours: int = Field(default=24, description="Metrics retention period")


class SagaOrchestratorTemplate(BaseMicroservice):
    """
    Enterprise Saga Orchestrator Template
    
    Provides distributed transaction coordination with:
    - Saga pattern implementation
    - Automatic compensation handling
    - Parallel and sequential execution
    - State persistence and recovery
    - Comprehensive monitoring
    """
    
    def __init__(self, config: SagaOrchestratorConfig):
        super().__init__(config)
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.registered_sagas: Dict[str, SagaDefinition] = {}
        self.active_executions: Dict[str, SagaExecutionContext] = {}
        self.service_clients: Dict[str, aiohttp.ClientSession] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Metrics
        self.sagas_executed_total = Counter(
            'saga_orchestrator_executions_total',
            'Total saga executions',
            ['saga_id', 'status']
        )
        self.saga_duration_seconds = Histogram(
            'saga_orchestrator_duration_seconds',
            'Saga execution duration',
            ['saga_id']
        )
        self.active_sagas_gauge = Gauge(
            'saga_orchestrator_active_sagas',
            'Number of active saga executions'
        )
        self.step_executions_total = Counter(
            'saga_orchestrator_step_executions_total',
            'Total step executions',
            ['saga_id', 'step_id', 'status']
        )
        self.compensation_executions_total = Counter(
            'saga_orchestrator_compensations_total',
            'Total compensation executions',
            ['saga_id', 'step_id']
        )
    
    async def initialize(self) -> None:
        """Initialize saga orchestrator service"""
        try:
            logger.info("Initializing saga orchestrator service")
            
            # Initialize Redis client
            await self._initialize_redis()
            
            # Initialize service clients
            await self._initialize_service_clients()
            
            # Start state persistence task
            asyncio.create_task(self._state_persistence_task())
            
            # Start execution monitoring
            asyncio.create_task(self._execution_monitoring_task())
            
            logger.info("Saga orchestrator service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize saga orchestrator service: {e}")
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=True
        )
        
        # Test connection
        await self.redis_client.ping()
        logger.info("Redis connection established")
    
    async def _initialize_service_clients(self) -> None:
        """Initialize HTTP clients for service communication"""
        # Initialize default session
        timeout = aiohttp.ClientTimeout(total=self.config.service_timeout_seconds)
        self.default_session = aiohttp.ClientSession(timeout=timeout)
        
        logger.info("Service clients initialized")
    
    async def register_saga(self, saga_def: SagaDefinition) -> Dict[str, Any]:
        """Register a new saga definition"""
        try:
            # Validate saga definition
            await self._validate_saga_definition(saga_def)
            
            # Store saga definition
            self.registered_sagas[saga_def.id] = saga_def
            
            # Persist saga definition
            await self._persist_saga_definition(saga_def)
            
            # Initialize circuit breakers for services
            for step in saga_def.steps:
                service_name = step.service_name
                if service_name not in self.circuit_breakers:
                    self.circuit_breakers[service_name] = CircuitBreaker(
                        failure_threshold=5,
                        recovery_timeout=30,
                        expected_exception=Exception
                    )
            
            logger.info(f"Registered saga: {saga_def.id}")
            
            return {
                "saga_id": saga_def.id,
                "name": saga_def.name,
                "status": "registered",
                "steps": len(saga_def.steps),
                "timeout": saga_def.global_timeout_seconds
            }
            
        except Exception as e:
            logger.error(f"Failed to register saga {saga_def.id}: {e}")
            raise
    
    async def execute_saga(self, saga_id: str, input_data: Dict[str, Any] = None) -> str:
        """Execute a saga"""
        if saga_id not in self.registered_sagas:
            raise ValueError(f"Saga not found: {saga_id}")
        
        saga_def = self.registered_sagas[saga_id]
        execution_id = str(uuid.uuid4())
        
        # Check concurrent execution limit
        if len(self.active_executions) >= self.config.max_concurrent_sagas:
            raise RuntimeError("Maximum concurrent saga executions reached")
        
        # Create execution context
        context = SagaExecutionContext(
            saga_id=saga_id,
            execution_id=execution_id,
            definition=saga_def,
            started_at=datetime.utcnow(),
            global_context=input_data or {}
        )
        
        # Initialize step contexts
        for step in saga_def.steps:
            context.step_contexts[step.id] = StepExecutionContext(
                step_id=step.id,
                execution_id=execution_id,
                saga_id=saga_id
            )
        
        self.active_executions[execution_id] = context
        
        # Start saga execution asynchronously
        asyncio.create_task(self._execute_saga_async(context))
        
        # Update metrics
        self.active_sagas_gauge.inc()
        
        logger.info(f"Started saga execution: {execution_id} for saga: {saga_id}")
        return execution_id
    
    async def _execute_saga_async(self, context: SagaExecutionContext) -> None:
        """Execute saga asynchronously"""
        start_time = datetime.utcnow()
        
        try:
            context.status = SagaStatus.RUNNING
            
            # Execute saga steps
            success = await self._execute_saga_steps(context)
            
            if success:
                context.status = SagaStatus.COMPLETED
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                # Update metrics
                self.sagas_executed_total.labels(
                    saga_id=context.saga_id, status='completed'
                ).inc()
                self.saga_duration_seconds.labels(saga_id=context.saga_id).observe(duration)
                
                logger.info(f"Saga {context.saga_id} completed successfully in {duration:.2f}s")
            else:
                # Execute compensation
                await self._execute_compensation(context)
                context.status = SagaStatus.COMPENSATED
                
                # Update metrics
                self.sagas_executed_total.labels(
                    saga_id=context.saga_id, status='compensated'
                ).inc()
                
                logger.info(f"Saga {context.saga_id} compensated successfully")
            
        except Exception as e:
            # Handle saga failure
            context.status = SagaStatus.FAILED
            context.errors.append(str(e))
            
            # Execute compensation on failure
            try:
                await self._execute_compensation(context)
                context.status = SagaStatus.COMPENSATED
            except Exception as compensation_error:
                logger.error(f"Compensation failed for saga {context.saga_id}: {compensation_error}")
                context.errors.append(f"Compensation failed: {str(compensation_error)}")
            
            # Update metrics
            self.sagas_executed_total.labels(
                saga_id=context.saga_id, status='failed'
            ).inc()
            
            logger.error(f"Saga {context.saga_id} failed: {e}")
            
        finally:
            # Cleanup
            self.active_sagas_gauge.dec()
            
            # Persist final state
            await self._persist_execution_state(context)
            
            # Remove from active executions after delay (for monitoring)
            await asyncio.sleep(60)
            if context.execution_id in self.active_executions:
                del self.active_executions[context.execution_id]
    
    async def _execute_saga_steps(self, context: SagaExecutionContext) -> bool:
        """Execute all saga steps"""
        try:
            # Build execution plan based on dependencies
            execution_plan = self._build_execution_plan(context.definition.steps)
            
            # Execute steps according to plan
            for step_group in execution_plan:
                if len(step_group) == 1:
                    # Sequential execution
                    step = step_group[0]
                    success = await self._execute_single_step(step, context)
                    if not success:
                        return False
                else:
                    # Parallel execution
                    tasks = [
                        self._execute_single_step(step, context)
                        for step in step_group
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Check if all parallel steps succeeded
                    for result in results:
                        if isinstance(result, Exception) or result is False:
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Saga step execution failed: {e}")
            return False
    
    async def _execute_single_step(self, step: SagaStep, context: SagaExecutionContext) -> bool:
        """Execute a single saga step"""
        step_context = context.step_contexts[step.id]
        step_context.status = StepStatus.RUNNING
        step_context.started_at = datetime.utcnow()
        
        try:
            # Check step condition if specified
            if step.condition and not await self._evaluate_condition(step.condition, context):
                step_context.status = StepStatus.SKIPPED
                logger.info(f"Step {step.id} skipped due to condition")
                return True
            
            # Execute based on step type
            if step.step_type == StepType.PARALLEL:
                success = await self._execute_parallel_steps(step.parallel_steps, context)
            else:
                success = await self._execute_step_action(step, context)
            
            if success:
                step_context.status = StepStatus.COMPLETED
                step_context.completed_at = datetime.utcnow()
                
                # Add to compensation stack if compensation action exists
                if step.compensation_action:
                    context.compensation_stack.append(step.id)
                
                # Update metrics
                self.step_executions_total.labels(
                    saga_id=context.saga_id, step_id=step.id, status='completed'
                ).inc()
                
                return True
            else:
                step_context.status = StepStatus.FAILED
                step_context.completed_at = datetime.utcnow()
                
                # Update metrics
                self.step_executions_total.labels(
                    saga_id=context.saga_id, step_id=step.id, status='failed'
                ).inc()
                
                return False
                
        except Exception as e:
            step_context.status = StepStatus.FAILED
            step_context.error = str(e)
            step_context.completed_at = datetime.utcnow()
            
            logger.error(f"Step {step.id} failed: {e}")
            
            # Update metrics
            self.step_executions_total.labels(
                saga_id=context.saga_id, step_id=step.id, status='failed'
            ).inc()
            
            return False
    
    async def _execute_step_action(self, step: SagaStep, context: SagaExecutionContext) -> bool:
        """Execute step action with retry logic"""
        step_context = context.step_contexts[step.id]
        max_retries = step.retry_policy.get("max_retries", self.config.default_retry_attempts)
        
        for attempt in range(max_retries + 1):
            try:
                step_context.retry_count = attempt
                
                # Get service client with circuit breaker
                circuit_breaker = self.circuit_breakers.get(step.service_name)
                if not circuit_breaker:
                    raise RuntimeError(f"No circuit breaker found for service: {step.service_name}")
                
                # Execute action with circuit breaker
                async def execute_action():
                    return await self._call_service(
                        step.service_name, step.action, step.parameters, context
                    )
                
                result = await circuit_breaker.call(execute_action)
                
                step_context.result = result
                return True
                
            except Exception as e:
                step_context.error = str(e)
                
                if attempt < max_retries:
                    # Calculate retry delay
                    delay = step.retry_policy.get("initial_delay", 1) * (2 ** attempt)
                    max_delay = step.retry_policy.get("max_delay", 60)
                    delay = min(delay, max_delay)
                    
                    logger.warning(f"Step {step.id} attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Step {step.id} failed after {max_retries + 1} attempts: {e}")
                    return False
        
        return False
    
    async def _execute_parallel_steps(self, parallel_steps: List[SagaStep], context: SagaExecutionContext) -> bool:
        """Execute parallel steps"""
        tasks = []
        for step in parallel_steps:
            task = asyncio.create_task(self._execute_single_step(step, context))
            tasks.append(task)
        
        # Wait for all parallel steps to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check if all parallel steps succeeded
        success = True
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Parallel step {parallel_steps[i].id} failed with exception: {result}")
                success = False
            elif result is False:
                logger.error(f"Parallel step {parallel_steps[i].id} failed")
                success = False
        
        return success
    
    async def _execute_compensation(self, context: SagaExecutionContext) -> None:
        """Execute compensation actions"""
        logger.info(f"Starting compensation for saga {context.saga_id}")
        context.status = SagaStatus.COMPENSATING
        
        # Execute compensations in reverse order
        compensation_steps = list(reversed(context.compensation_stack))
        
        for step_id in compensation_steps:
            try:
                step = next(s for s in context.definition.steps if s.id == step_id)
                step_context = context.step_contexts[step_id]
                
                if step.compensation_action and not step_context.compensation_executed:
                    logger.info(f"Executing compensation for step {step_id}")
                    
                    step_context.status = StepStatus.COMPENSATING
                    
                    # Execute compensation action
                    success = await self._call_service(
                        step.service_name, 
                        step.compensation_action, 
                        step.parameters, 
                        context
                    )
                    
                    if success:
                        step_context.status = StepStatus.COMPENSATED
                        step_context.compensation_executed = True
                        
                        # Update metrics
                        self.compensation_executions_total.labels(
                            saga_id=context.saga_id, step_id=step_id
                        ).inc()
                        
                        logger.info(f"Compensation completed for step {step_id}")
                    else:
                        logger.error(f"Compensation failed for step {step_id}")
                        
            except Exception as e:
                logger.error(f"Compensation execution failed for step {step_id}: {e}")
    
    async def _call_service(
        self, service_name: str, action: str, parameters: Dict[str, Any], context: SagaExecutionContext
    ) -> Any:
        """Call a microservice action"""
        try:
            # Get service URL (in practice, this would use service discovery)
            service_url = await self._resolve_service_url(service_name)
            
            # Prepare request
            request_data = {
                "action": action,
                "parameters": parameters,
                "saga_context": {
                    "saga_id": context.saga_id,
                    "execution_id": context.execution_id,
                    "global_context": context.global_context
                }
            }
            
            # Make HTTP request
            async with self.default_session.post(
                f"{service_url}/execute",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data")
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Service call failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Service call failed for {service_name}.{action}: {e}")
            raise
    
    async def _resolve_service_url(self, service_name: str) -> str:
        """Resolve service URL using service discovery"""
        # Simple implementation - in practice, this would use a service registry
        if self.config.service_registry_url:
            # Query service registry
            async with self.default_session.get(
                f"{self.config.service_registry_url}/services/{service_name}"
            ) as response:
                if response.status == 200:
                    service_info = await response.json()
                    return service_info["url"]
        
        # Fallback to default URL pattern
        return f"http://{service_name}:8080"
    
    async def _evaluate_condition(self, condition: str, context: SagaExecutionContext) -> bool:
        """Evaluate step execution condition"""
        try:
            # Simple condition evaluation
            # In practice, this would be more sophisticated
            
            # Replace placeholders with actual values
            eval_context = {
                "global_context": context.global_context,
                "step_results": {
                    step_id: step_ctx.result 
                    for step_id, step_ctx in context.step_contexts.items()
                    if step_ctx.result is not None
                }
            }
            
            # Simple string-based evaluation
            # This should be replaced with a proper expression evaluator
            return eval(condition, {"__builtins__": {}}, eval_context)
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def _build_execution_plan(self, steps: List[SagaStep]) -> List[List[SagaStep]]:
        """Build step execution plan based on dependencies"""
        # Simple topological sort for dependency resolution
        execution_plan = []
        remaining_steps = steps.copy()
        completed_steps = set()
        
        while remaining_steps:
            # Find steps with no unresolved dependencies
            ready_steps = []
            for step in remaining_steps:
                if all(dep in completed_steps for dep in step.dependencies):
                    ready_steps.append(step)
            
            if not ready_steps:
                # Circular dependency or missing dependency
                logger.warning("Circular dependency detected, processing remaining steps")
                ready_steps = remaining_steps
            
            execution_plan.append(ready_steps)
            
            # Mark steps as completed
            for step in ready_steps:
                completed_steps.add(step.id)
                remaining_steps.remove(step)
        
        return execution_plan
    
    async def get_saga_status(self, execution_id: str) -> Dict[str, Any]:
        """Get saga execution status"""
        if execution_id not in self.active_executions:
            # Try to load from persistence
            persisted_state = await self._load_execution_state(execution_id)
            if not persisted_state:
                raise ValueError(f"Saga execution not found: {execution_id}")
            return persisted_state
        
        context = self.active_executions[execution_id]
        
        # Build step statuses
        step_statuses = {}
        for step_id, step_context in context.step_contexts.items():
            step_statuses[step_id] = {
                "status": step_context.status.value,
                "started_at": step_context.started_at.isoformat() if step_context.started_at else None,
                "completed_at": step_context.completed_at.isoformat() if step_context.completed_at else None,
                "retry_count": step_context.retry_count,
                "error": step_context.error,
                "compensation_executed": step_context.compensation_executed
            }
        
        return {
            "execution_id": execution_id,
            "saga_id": context.saga_id,
            "status": context.status.value,
            "started_at": context.started_at.isoformat() if context.started_at else None,
            "steps": step_statuses,
            "errors": context.errors,
            "compensation_stack": context.compensation_stack
        }
    
    async def cancel_saga(self, execution_id: str) -> bool:
        """Cancel a running saga execution"""
        if execution_id not in self.active_executions:
            return False
        
        context = self.active_executions[execution_id]
        context.status = SagaStatus.CANCELLED
        
        # Execute compensation for completed steps
        await self._execute_compensation(context)
        
        logger.info(f"Saga execution cancelled: {execution_id}")
        return True
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            # Check Redis connectivity
            redis_healthy = False
            try:
                await self.redis_client.ping()
                redis_healthy = True
            except Exception:
                pass
            
            return {
                "service": "saga_orchestrator_template",
                "status": "healthy" if redis_healthy else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "registered_sagas": len(self.registered_sagas),
                    "active_executions": len(self.active_executions),
                    "circuit_breakers": len(self.circuit_breakers),
                    "redis_connected": redis_healthy
                }
            }
            
        except Exception as e:
            return {
                "service": "saga_orchestrator_template",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _validate_saga_definition(self, saga_def: SagaDefinition) -> None:
        """Validate saga definition"""
        # Check for duplicate step IDs
        step_ids = [step.id for step in saga_def.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("Duplicate step IDs found in saga definition")
        
        # Check step dependencies
        for step in saga_def.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise ValueError(f"Step dependency not found: {dep}")
        
        # Check for circular dependencies
        # This is a simplified check - a full implementation would be more thorough
        for step in saga_def.steps:
            if step.id in step.dependencies:
                raise ValueError(f"Circular dependency detected for step: {step.id}")
    
    async def _persist_saga_definition(self, saga_def: SagaDefinition) -> None:
        """Persist saga definition to Redis"""
        key = f"saga_def:{saga_def.id}"
        value = saga_def.json()
        await self.redis_client.set(key, value)
    
    async def _persist_execution_state(self, context: SagaExecutionContext) -> None:
        """Persist saga execution state"""
        state_data = {
            "saga_id": context.saga_id,
            "execution_id": context.execution_id,
            "status": context.status.value,
            "started_at": context.started_at.isoformat() if context.started_at else None,
            "global_context": context.global_context,
            "errors": context.errors,
            "compensation_stack": context.compensation_stack,
            "step_contexts": {
                step_id: {
                    "status": step_ctx.status.value,
                    "started_at": step_ctx.started_at.isoformat() if step_ctx.started_at else None,
                    "completed_at": step_ctx.completed_at.isoformat() if step_ctx.completed_at else None,
                    "result": step_ctx.result,
                    "error": step_ctx.error,
                    "retry_count": step_ctx.retry_count,
                    "compensation_executed": step_ctx.compensation_executed
                }
                for step_id, step_ctx in context.step_contexts.items()
            }
        }
        
        key = f"saga_execution:{context.execution_id}"
        await self.redis_client.setex(
            key,
            timedelta(hours=self.config.metrics_retention_hours).total_seconds(),
            json.dumps(state_data, default=str)
        )
    
    async def _load_execution_state(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Load saga execution state from persistence"""
        key = f"saga_execution:{execution_id}"
        data = await self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def _state_persistence_task(self) -> None:
        """Background task for periodic state persistence"""
        while True:
            try:
                await asyncio.sleep(self.config.state_persistence_interval)
                
                # Persist state of all active executions
                for context in self.active_executions.values():
                    await self._persist_execution_state(context)
                    
            except Exception as e:
                logger.error(f"State persistence task error: {e}")
    
    async def _execution_monitoring_task(self) -> None:
        """Background task for execution monitoring and timeout handling"""
        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                current_time = datetime.utcnow()
                
                for execution_id, context in list(self.active_executions.items()):
                    # Check global timeout
                    if context.started_at:
                        elapsed = (current_time - context.started_at).total_seconds()
                        if elapsed > context.definition.global_timeout_seconds:
                            logger.warning(f"Saga {execution_id} timed out after {elapsed}s")
                            await self.cancel_saga(execution_id)
                    
                    # Check individual step timeouts
                    for step in context.definition.steps:
                        step_context = context.step_contexts[step.id]
                        if (step_context.status == StepStatus.RUNNING and 
                            step_context.started_at and
                            (current_time - step_context.started_at).total_seconds() > step.timeout_seconds):
                            
                            logger.warning(f"Step {step.id} timed out in saga {execution_id}")
                            step_context.status = StepStatus.FAILED
                            step_context.error = "Step execution timeout"
                            step_context.completed_at = current_time
                    
            except Exception as e:
                logger.error(f"Execution monitoring task error: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        try:
            logger.info("Shutting down saga orchestrator service")
            
            # Cancel all active executions
            for execution_id in list(self.active_executions.keys()):
                await self.cancel_saga(execution_id)
            
            # Close service clients
            if hasattr(self, 'default_session'):
                await self.default_session.close()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Saga orchestrator service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")