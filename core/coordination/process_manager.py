"""Process Manager - Enterprise Process Lifecycle Management & Execution Control

Advanced process management system providing comprehensive lifecycle control,
execution monitoring, and resource coordination for the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This process management system is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization.

🎯 BUSINESS LOGIC:
Process Creation → Resource Allocation → Execution → Monitoring → Completion → Cleanup
"""import asyncio
import uuid
import psutil
import threading
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import signal
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

logger = logging.getLogger(__name__)


class ProcessType(Enum):
    """Types of processes managed by the system"""    CONTENT_PROCESSING = "content_processing"
    AI_FINGERPRINTING = "ai_fingerprinting"
    PROTECTION_MONITORING = "protection_monitoring"
    REVENUE_CALCULATION = "revenue_calculation"
    PLATFORM_SYNCHRONIZATION = "platform_synchronization"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME_ANALYSIS = "real_time_analysis"
    BACKGROUND_TASKS = "background_tasks"


class ProcessStatus(Enum):
    """Process execution status"""    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"
    ZOMBIE = "zombie"


class ProcessPriority(Enum):
    """Process execution priority"""    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class ExecutionContext(Enum):
    """Process execution context"""    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    THREADED = "threaded"
    MULTI_PROCESS = "multi_process"
    DISTRIBUTED = "distributed"


@dataclass
class ProcessResource:
    """Process resource allocation and limits"""    cpu_cores: int = 1
    memory_mb: int = 512
    disk_space_mb: int = 1024
    network_bandwidth_mbps: int = 10
    gpu_memory_mb: int = 0
    max_execution_time: int = 3600
    max_file_descriptors: int = 1024


@dataclass
class ProcessConfiguration:
    """Complete process configuration"""    process_id: str
    name: str
    process_type: ProcessType
    execution_context: ExecutionContext
    priority: ProcessPriority
    resource_allocation: ProcessResource
    environment_variables: Dict[str, str] = field(default_factory=dict)
    command_line: Optional[str] = None
    working_directory: Optional[str] = None
    input_parameters: Dict[str, Any] = field(default_factory=dict)
    output_configuration: Dict[str, Any] = field(default_factory=dict)
    monitoring_enabled: bool = True
    auto_restart: bool = False
    max_restarts: int = 3


@dataclass
class ProcessExecution:
    """Process execution state and tracking"""    execution_id: str
    process_id: str
    configuration: ProcessConfiguration
    status: ProcessStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    pid: Optional[int] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    execution_time: float = 0.0
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_details: List[str] = field(default_factory=list)
    restart_count: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)


class ProcessManager:
    """Enterprise process lifecycle management and execution control"""    
    def __init__(self, max_processes: int = 100, monitoring_interval: int = 5):
        self.max_processes = max_processes
        self.monitoring_interval = monitoring_interval
        
        # Process registry
        self.process_configurations: Dict[str, ProcessConfiguration] = {}
        self.active_executions: Dict[str, ProcessExecution] = {}
        self.completed_executions: Dict[str, ProcessExecution] = {}
        self.execution_queue: deque = deque()
        
        # Resource management
        self.resource_pool = self._initialize_resource_pool()
        self.resource_allocations: Dict[str, ProcessResource] = {}
        
        # Execution engines
        self.thread_executor = ThreadPoolExecutor(max_workers=20)
        self.process_executor = ProcessPoolExecutor(max_workers=10)
        
        # Monitoring and events
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Performance tracking
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.resource_utilization: Dict[str, float] = {}
        
        # Initialize standard process configurations
        self._initialize_standard_processes()
        
        # Start monitoring
        self.start_monitoring()
        
        logger.info("ProcessManager initialized successfully")
    
    def _initialize_resource_pool(self) -> Dict[str, Any]:
        """Initialize system resource pool"""        try:
            system_info = {
                "cpu_cores": psutil.cpu_count(),
                "total_memory_mb": psutil.virtual_memory().total // (1024 * 1024),
                "available_memory_mb": psutil.virtual_memory().available // (1024 * 1024),
                "disk_space_gb": psutil.disk_usage('/').total // (1024 * 1024 * 1024),
                "network_interfaces": len(psutil.net_if_addrs())
            }
            
            # Calculate available resources for allocation
            available_resources = {
                "cpu_cores": system_info["cpu_cores"],
                "memory_mb": int(system_info["available_memory_mb"] * 0.8),  # Reserve 20%
                "disk_space_mb": int(system_info["disk_space_gb"] * 1024 * 0.9),  # Reserve 10%
                "network_bandwidth_mbps": 1000  # Configurable
            }
            
            logger.info(f"Resource pool initialized: {available_resources}")
            return available_resources
            
        except Exception as e:
            logger.error(f"Resource pool initialization failed: {e}")
            return {
                "cpu_cores": 4,
                "memory_mb": 8192,
                "disk_space_mb": 10240,
                "network_bandwidth_mbps": 100
            }
    
    def _initialize_standard_processes(self):
        """Initialize standard business process configurations"""        # Content Processing Process
        content_process = ProcessConfiguration(
            process_id="content_processing_standard",
            name="Standard Content Processing",
            process_type=ProcessType.CONTENT_PROCESSING,
            execution_context=ExecutionContext.ASYNCHRONOUS,
            priority=ProcessPriority.HIGH,
            resource_allocation=ProcessResource(
                cpu_cores=2,
                memory_mb=2048,
                disk_space_mb=5120,
                max_execution_time=1800
            ),
            monitoring_enabled=True,
            auto_restart=False
        )
        
        # AI Fingerprinting Process
        fingerprinting_process = ProcessConfiguration(
            process_id="ai_fingerprinting_advanced",
            name="Advanced AI Fingerprinting",
            process_type=ProcessType.AI_FINGERPRINTING,
            execution_context=ExecutionContext.MULTI_PROCESS,
            priority=ProcessPriority.CRITICAL,
            resource_allocation=ProcessResource(
                cpu_cores=4,
                memory_mb=4096,
                disk_space_mb=8192,
                gpu_memory_mb=2048,
                max_execution_time=3600
            ),
            monitoring_enabled=True,
            auto_restart=True,
            max_restarts=2
        )
        
        # Protection Monitoring Process
        monitoring_process = ProcessConfiguration(
            process_id="protection_monitoring_realtime",
            name="Real-time Protection Monitoring",
            process_type=ProcessType.PROTECTION_MONITORING,
            execution_context=ExecutionContext.BACKGROUND_TASKS,
            priority=ProcessPriority.NORMAL,
            resource_allocation=ProcessResource(
                cpu_cores=1,
                memory_mb=1024,
                disk_space_mb=2048,
                max_execution_time=86400  # 24 hours
            ),
            monitoring_enabled=True,
            auto_restart=True,
            max_restarts=5
        )
        
        # Revenue Calculation Process
        revenue_process = ProcessConfiguration(
            process_id="revenue_calculation_batch",
            name="Batch Revenue Calculation",
            process_type=ProcessType.REVENUE_CALCULATION,
            execution_context=ExecutionContext.BATCH_PROCESSING,
            priority=ProcessPriority.NORMAL,
            resource_allocation=ProcessResource(
                cpu_cores=2,
                memory_mb=3072,
                disk_space_mb=4096,
                max_execution_time=7200
            ),
            monitoring_enabled=True,
            auto_restart=False
        )
        
        # Register standard processes
        self.register_process(content_process)
        self.register_process(fingerprinting_process)
        self.register_process(monitoring_process)
        self.register_process(revenue_process)
    
    def register_process(self, configuration: ProcessConfiguration) -> bool:
        """Register a new process configuration"""        try:
            # Validate configuration
            if not self._validate_process_configuration(configuration):
                return False
            
            # Check resource availability
            if not self._check_resource_availability(configuration.resource_allocation):
                logger.error(f"Insufficient resources for process {configuration.process_id}")
                return False
            
            self.process_configurations[configuration.process_id] = configuration
            logger.info(f"Process registered: {configuration.process_id}")
            return True
            
        except Exception as e:
            logger.error(f"Process registration failed: {e}")
            return False
    
    def _validate_process_configuration(self, config: ProcessConfiguration) -> bool:
        """Validate process configuration"""        try:
            # Required fields validation
            if not all([config.process_id, config.name, config.process_type]):
                logger.error("Missing required process configuration fields")
                return False
            
            # Resource validation
            if (config.resource_allocation.cpu_cores <= 0 or 
                config.resource_allocation.memory_mb <= 0):
                logger.error("Invalid resource allocation")
                return False
            
            # Timeout validation
            if config.resource_allocation.max_execution_time <= 0:
                logger.error("Invalid execution timeout")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Process configuration validation error: {e}")
            return False
    
    def _check_resource_availability(self, required: ProcessResource) -> bool:
        """Check if required resources are available"""        try:
            current_usage = self._calculate_current_resource_usage()
            
            available_cpu = self.resource_pool["cpu_cores"] - current_usage["cpu_cores"]
            available_memory = self.resource_pool["memory_mb"] - current_usage["memory_mb"]
            
            return (available_cpu >= required.cpu_cores and 
                   available_memory >= required.memory_mb)
            
        except Exception as e:
            logger.error(f"Resource availability check failed: {e}")
            return False
    
    def _calculate_current_resource_usage(self) -> Dict[str, float]:
        """Calculate current resource usage across all active processes"""        total_cpu = 0
        total_memory = 0
        
        for execution in self.active_executions.values():
            if execution.status == ProcessStatus.RUNNING:
                total_cpu += execution.configuration.resource_allocation.cpu_cores
                total_memory += execution.configuration.resource_allocation.memory_mb
        
        return {
            "cpu_cores": total_cpu,
            "memory_mb": total_memory
        }
    
    async def start_process(
        self,
        process_id: str,
        input_parameters: Dict[str, Any] = None,
        priority_override: Optional[ProcessPriority] = None
    ) -> str:
        """Start a process execution"""        try:
            if process_id not in self.process_configurations:
                raise ValueError(f"Process configuration '{process_id}' not found")
            
            config = self.process_configurations[process_id]
            execution_id = str(uuid.uuid4())
            
            # Override priority if specified
            if priority_override:
                config.priority = priority_override
            
            # Update input parameters
            if input_parameters:
                config.input_parameters.update(input_parameters)
            
            # Create execution instance
            execution = ProcessExecution(
                execution_id=execution_id,
                process_id=process_id,
                configuration=config,
                status=ProcessStatus.INITIALIZING,
                created_at=datetime.now(timezone.utc)
            )
            
            # Check resource availability
            if not self._check_resource_availability(config.resource_allocation):
                # Queue process if resources not available
                self.execution_queue.append(execution)
                logger.info(f"Process {execution_id} queued due to resource constraints")
                return execution_id
            
            # Allocate resources
            self._allocate_resources(execution_id, config.resource_allocation)
            
            # Start execution based on context
            self.active_executions[execution_id] = execution
            await self._start_process_execution(execution)
            
            return execution_id
            
        except Exception as e:
            logger.error(f"Process start failed: {e}")
            raise
    
    def _allocate_resources(self, execution_id: str, resources: ProcessResource):
        """Allocate resources for process execution"""        self.resource_allocations[execution_id] = resources
        logger.info(f"Resources allocated for process {execution_id}")
    
    def _deallocate_resources(self, execution_id: str):
        """Deallocate resources from process execution"""        if execution_id in self.resource_allocations:
            del self.resource_allocations[execution_id]
            logger.info(f"Resources deallocated for process {execution_id}")
    
    async def _start_process_execution(self, execution: ProcessExecution):
        """Start process execution based on execution context"""        try:
            execution.status = ProcessStatus.RUNNING
            execution.started_at = datetime.now(timezone.utc)
            
            # Emit process started event
            await self._emit_process_event("process_started", execution)
            
            # Execute based on context
            if execution.configuration.execution_context == ExecutionContext.SYNCHRONOUS:
                await self._execute_synchronous(execution)
            elif execution.configuration.execution_context == ExecutionContext.ASYNCHRONOUS:
                await self._execute_asynchronous(execution)
            elif execution.configuration.execution_context == ExecutionContext.THREADED:
                await self._execute_threaded(execution)
            elif execution.configuration.execution_context == ExecutionContext.MULTI_PROCESS:
                await self._execute_multi_process(execution)
            else:
                raise ValueError(f"Unsupported execution context: {execution.configuration.execution_context}")
            
        except Exception as e:
            execution.status = ProcessStatus.FAILED
            execution.error_details.append(f"Process execution failed: {str(e)}")
            await self._handle_process_failure(execution)
            raise
    
    async def _execute_synchronous(self, execution: ProcessExecution):
        """Execute process synchronously"""        try:
            # Simulate synchronous processing
            result = await self._process_business_logic(execution)
            
            execution.output_data = result
            execution.status = ProcessStatus.COMPLETED
            execution.completed_at = datetime.now(timezone.utc)
            execution.exit_code = 0
            
            await self._complete_process_execution(execution)
            
        except Exception as e:
            execution.status = ProcessStatus.FAILED
            execution.error_details.append(str(e))
            execution.exit_code = 1
            raise
    
    async def _execute_asynchronous(self, execution: ProcessExecution):
        """Execute process asynchronously"""        try:
            # Create async task for processing
            task = asyncio.create_task(self._process_business_logic(execution))
            
            # Set timeout
            timeout = execution.configuration.resource_allocation.max_execution_time
            result = await asyncio.wait_for(task, timeout=timeout)
            
            execution.output_data = result
            execution.status = ProcessStatus.COMPLETED
            execution.completed_at = datetime.now(timezone.utc)
            execution.exit_code = 0
            
            await self._complete_process_execution(execution)
            
        except asyncio.TimeoutError:
            execution.status = ProcessStatus.FAILED
            execution.error_details.append("Process execution timeout")
            execution.exit_code = 124
            raise
        except Exception as e:
            execution.status = ProcessStatus.FAILED
            execution.error_details.append(str(e))
            execution.exit_code = 1
            raise
    
    async def _execute_threaded(self, execution: ProcessExecution):
        """Execute process in thread pool"""        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.thread_executor,
                self._process_sync_business_logic,
                execution
            )
            
            execution.output_data = result
            execution.status = ProcessStatus.COMPLETED
            execution.completed_at = datetime.now(timezone.utc)
            execution.exit_code = 0
            
            await self._complete_process_execution(execution)
            
        except Exception as e:
            execution.status = ProcessStatus.FAILED
            execution.error_details.append(str(e))
            execution.exit_code = 1
            raise
    
    async def _execute_multi_process(self, execution: ProcessExecution):
        """Execute process in process pool"""        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.process_executor,
                self._process_sync_business_logic,
                execution
            )
            
            execution.output_data = result
            execution.status = ProcessStatus.COMPLETED
            execution.completed_at = datetime.now(timezone.utc)
            execution.exit_code = 0
            
            await self._complete_process_execution(execution)
            
        except Exception as e:
            execution.status = ProcessStatus.FAILED
            execution.error_details.append(str(e))
            execution.exit_code = 1
            raise
    
    async def _process_business_logic(self, execution: ProcessExecution) -> Dict[str, Any]:
        """Process business logic asynchronously"""        # Simulate processing time based on process type
        processing_time = {
            ProcessType.CONTENT_PROCESSING: 5,
            ProcessType.AI_FINGERPRINTING: 10,
            ProcessType.PROTECTION_MONITORING: 2,
            ProcessType.REVENUE_CALCULATION: 8,
            ProcessType.PLATFORM_SYNCHRONIZATION: 3,
            ProcessType.BATCH_PROCESSING: 15,
            ProcessType.REAL_TIME_ANALYSIS: 1,
            ProcessType.BACKGROUND_TASKS: 30
        }.get(execution.configuration.process_type, 5)
        
        await asyncio.sleep(processing_time)
        
        return {
            "process_type": execution.configuration.process_type.value,
            "execution_id": execution.execution_id,
            "processing_time": processing_time,
            "input_parameters": execution.configuration.input_parameters,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "result": "success"
        }
    
    def _process_sync_business_logic(self, execution: ProcessExecution) -> Dict[str, Any]:
        """Process business logic synchronously"""        import time
        
        # Simulate processing time
        processing_time = {
            ProcessType.CONTENT_PROCESSING: 5,
            ProcessType.AI_FINGERPRINTING: 10,
            ProcessType.PROTECTION_MONITORING: 2,
            ProcessType.REVENUE_CALCULATION: 8,
            ProcessType.PLATFORM_SYNCHRONIZATION: 3,
            ProcessType.BATCH_PROCESSING: 15,
            ProcessType.REAL_TIME_ANALYSIS: 1,
            ProcessType.BACKGROUND_TASKS: 30
        }.get(execution.configuration.process_type, 5)
        
        time.sleep(processing_time)
        
        return {
            "process_type": execution.configuration.process_type.value,
            "execution_id": execution.execution_id,
            "processing_time": processing_time,
            "input_parameters": execution.configuration.input_parameters,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "result": "success"
        }
    
    async def _complete_process_execution(self, execution: ProcessExecution):
        """Complete process execution and cleanup"""        try:
            # Calculate execution time
            if execution.started_at:
                execution.execution_time = (
                    execution.completed_at - execution.started_at
                ).total_seconds()
            
            # Deallocate resources
            self._deallocate_resources(execution.execution_id)
            
            # Move to completed executions
            self.completed_executions[execution.execution_id] = execution
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            
            # Emit completion event
            await self._emit_process_event("process_completed", execution)
            
            # Process next queued process
            await self._process_next_queued()
            
            logger.info(f"Process {execution.execution_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Process completion failed: {e}")
    
    async def _handle_process_failure(self, execution: ProcessExecution):
        """Handle process execution failure"""        try:
            # Check for auto-restart
            if (execution.configuration.auto_restart and 
                execution.restart_count < execution.configuration.max_restarts):
                
                execution.restart_count += 1
                execution.status = ProcessStatus.READY
                
                logger.info(f"Restarting process {execution.execution_id} (attempt {execution.restart_count})")
                
                # Restart after delay
                await asyncio.sleep(5)
                await self._start_process_execution(execution)
                return
            
            # Process failed permanently
            execution.completed_at = datetime.now(timezone.utc)
            
            # Deallocate resources
            self._deallocate_resources(execution.execution_id)
            
            # Move to completed executions
            self.completed_executions[execution.execution_id] = execution
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            
            # Emit failure event
            await self._emit_process_event("process_failed", execution)
            
            # Process next queued process
            await self._process_next_queued()
            
            logger.error(f"Process {execution.execution_id} failed permanently")
            
        except Exception as e:
            logger.error(f"Process failure handling failed: {e}")
    
    async def _process_next_queued(self):
        """Process next queued process if resources are available"""        try:
            if self.execution_queue:
                next_execution = self.execution_queue.popleft()
                
                if self._check_resource_availability(next_execution.configuration.resource_allocation):
                    self._allocate_resources(
                        next_execution.execution_id, 
                        next_execution.configuration.resource_allocation
                    )
                    self.active_executions[next_execution.execution_id] = next_execution
                    await self._start_process_execution(next_execution)
                else:
                    # Put back in queue if still no resources
                    self.execution_queue.appendleft(next_execution)
                    
        except Exception as e:
            logger.error(f"Queue processing failed: {e}")
    
    async def _emit_process_event(self, event_type: str, execution: ProcessExecution):
        """Emit process events to registered handlers"""        try:
            event_data = {
                "event_type": event_type,
                "execution_id": execution.execution_id,
                "process_id": execution.process_id,
                "status": execution.status.value,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            for handler in self.event_handlers.get(event_type, []):
                try:
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"Event emission failed: {e}")
    
    def start_monitoring(self):
        """Start process monitoring"""        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("Process monitoring started")
    
    def stop_monitoring(self):
        """Stop process monitoring"""        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Process monitoring stopped")
    
    def _monitoring_loop(self):
        """Continuous monitoring loop"""        while self.monitoring_active:
            try:
                self._update_process_metrics()
                self._check_process_health()
                threading.Event().wait(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
    
    def _update_process_metrics(self):
        """Update process performance metrics"""        try:
            for execution in self.active_executions.values():
                if execution.pid:
                    try:
                        process = psutil.Process(execution.pid)
                        execution.cpu_usage = process.cpu_percent()
                        execution.memory_usage = process.memory_percent()
                        
                        # Update performance metrics
                        execution.performance_metrics.update({
                            "cpu_usage": execution.cpu_usage,
                            "memory_usage": execution.memory_usage,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
                    except psutil.NoSuchProcess:
                        execution.status = ProcessStatus.TERMINATED
                        
        except Exception as e:
            logger.error(f"Metrics update failed: {e}")
    
    def _check_process_health(self):
        """Check health of all active processes"""        try:
            for execution in list(self.active_executions.values()):
                # Check execution timeout
                if (execution.started_at and 
                    execution.configuration.resource_allocation.max_execution_time > 0):
                    
                    runtime = (datetime.now(timezone.utc) - execution.started_at).total_seconds()
                    if runtime > execution.configuration.resource_allocation.max_execution_time:
                        logger.warning(f"Process {execution.execution_id} exceeded timeout")
                        asyncio.create_task(self.terminate_process(execution.execution_id))
                
                # Check resource usage
                if execution.memory_usage > 90:
                    logger.warning(f"Process {execution.execution_id} high memory usage: {execution.memory_usage}%")
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    async def terminate_process(self, execution_id: str) -> bool:
        """Terminate a running process"""        try:
            if execution_id not in self.active_executions:
                return False
            
            execution = self.active_executions[execution_id]
            
            if execution.pid:
                try:
                    os.kill(execution.pid, signal.SIGTERM)
                    execution.status = ProcessStatus.TERMINATED
                except ProcessLookupError:
                    execution.status = ProcessStatus.TERMINATED
            else:
                execution.status = ProcessStatus.TERMINATED
            
            execution.completed_at = datetime.now(timezone.utc)
            execution.exit_code = 143  # SIGTERM
            
            # Cleanup
            self._deallocate_resources(execution_id)
            self.completed_executions[execution_id] = execution
            del self.active_executions[execution_id]
            
            await self._emit_process_event("process_terminated", execution)
            
            logger.info(f"Process {execution_id} terminated")
            return True
            
        except Exception as e:
            logger.error(f"Process termination failed: {e}")
            return False
    
    def get_process_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get process execution status"""        execution = (self.active_executions.get(execution_id) or 
                    self.completed_executions.get(execution_id))
        
        if not execution:
            return None
        
        return {
            "execution_id": execution.execution_id,
            "process_id": execution.process_id,
            "status": execution.status.value,
            "created_at": execution.created_at.isoformat(),
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "execution_time": execution.execution_time,
            "cpu_usage": execution.cpu_usage,
            "memory_usage": execution.memory_usage,
            "exit_code": execution.exit_code,
            "restart_count": execution.restart_count,
            "error_details": execution.error_details
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide process metrics"""        active_count = len(self.active_executions)
        queued_count = len(self.execution_queue)
        completed_count = len(self.completed_executions)
        
        resource_usage = self._calculate_current_resource_usage()
        
        return {
            "active_processes": active_count,
            "queued_processes": queued_count,
            "completed_processes": completed_count,
            "total_processed": completed_count,
            "resource_usage": resource_usage,
            "resource_pool": self.resource_pool,
            "resource_utilization": {
                "cpu": (resource_usage["cpu_cores"] / self.resource_pool["cpu_cores"]) * 100,
                "memory": (resource_usage["memory_mb"] / self.resource_pool["memory_mb"]) * 100
            }
        }
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for process events"""        self.event_handlers[event_type].append(handler)
    
    def shutdown(self):
        """Shutdown process manager and cleanup"""        try:
            self.stop_monitoring()
            
            # Terminate all active processes
            for execution_id in list(self.active_executions.keys()):
                asyncio.create_task(self.terminate_process(execution_id))
            
            # Shutdown executors
            self.thread_executor.shutdown(wait=True)
            self.process_executor.shutdown(wait=True)
            
            logger.info("ProcessManager shutdown completed")
            
        except Exception as e:
            logger.error(f"ProcessManager shutdown failed: {e}")
