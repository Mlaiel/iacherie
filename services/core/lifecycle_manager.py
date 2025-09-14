"""
Lifecycle Manager - Enterprise Service Lifecycle Management
==========================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Backend Senior + DevOps + Microservices + Lead Dev IA
**Module**: Core Services - Lifecycle Management
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade service lifecycle management with dependency tracking,
graceful shutdowns, health monitoring, and automated recovery.
"""

import asyncio
import logging
import signal
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
# import aioredis  # Disabled for Python 3.12 compatibility
import json


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LifecycleState(Enum):
    """Service lifecycle states"""
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    PAUSING = "pausing"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    CRASHED = "crashed"
    RESTARTING = "restarting"


class LifecycleEvent(Enum):
    """Lifecycle events"""
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"
    BEFORE_RESTART = "before_restart"
    AFTER_RESTART = "after_restart"
    HEALTH_CHECK = "health_check"
    ERROR_OCCURRED = "error_occurred"
    DEPENDENCY_READY = "dependency_ready"
    DEPENDENCY_FAILED = "dependency_failed"


@dataclass
class ServiceLifecycle:
    """Service lifecycle definition"""
    service_id: str
    service_name: str
    
    # State management
    current_state: LifecycleState = LifecycleState.UNKNOWN
    target_state: LifecycleState = LifecycleState.STOPPED
    previous_state: Optional[LifecycleState] = None
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    # Lifecycle hooks
    startup_hooks: List[Callable] = field(default_factory=list)
    shutdown_hooks: List[Callable] = field(default_factory=list)
    health_check_hook: Optional[Callable] = None
    
    # Configuration
    startup_timeout: int = 60  # seconds
    shutdown_timeout: int = 30  # seconds
    health_check_interval: int = 30  # seconds
    max_restart_attempts: int = 3
    restart_delay: int = 5  # seconds
    
    # Metrics
    start_time: Optional[datetime] = None
    uptime_seconds: int = 0
    restart_count: int = 0
    crash_count: int = 0
    last_health_check: Optional[datetime] = None
    
    # Error handling
    last_error: Optional[str] = None
    error_count: int = 0
    auto_restart: bool = True
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['current_state'] = self.current_state.value
        data['target_state'] = self.target_state.value
        if self.previous_state:
            data['previous_state'] = self.previous_state.value
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.last_health_check:
            data['last_health_check'] = self.last_health_check.isoformat()
        
        # Remove non-serializable fields
        del data['startup_hooks']
        del data['shutdown_hooks']
        del data['health_check_hook']
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceLifecycle':
        """Create instance from dictionary"""
        # Convert enum values
        data['current_state'] = LifecycleState(data['current_state'])
        data['target_state'] = LifecycleState(data['target_state'])
        if data.get('previous_state'):
            data['previous_state'] = LifecycleState(data['previous_state'])
        
        # Convert datetime strings
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('last_health_check'):
            data['last_health_check'] = datetime.fromisoformat(data['last_health_check'])
        
        # Remove hook fields that can't be deserialized
        data.pop('startup_hooks', None)
        data.pop('shutdown_hooks', None)
        data.pop('health_check_hook', None)
        
        return cls(**data)


@dataclass
class DependencyGraph:
    """Service dependency graph"""
    nodes: Set[str] = field(default_factory=set)
    edges: Dict[str, Set[str]] = field(default_factory=dict)  # service -> dependencies
    reverse_edges: Dict[str, Set[str]] = field(default_factory=dict)  # service -> dependents
    
    def add_service(self, service_id: str) -> None:
        """Add service to graph"""
        self.nodes.add(service_id)
        if service_id not in self.edges:
            self.edges[service_id] = set()
        if service_id not in self.reverse_edges:
            self.reverse_edges[service_id] = set()
    
    def add_dependency(self, service_id: str, dependency_id: str) -> None:
        """Add dependency relationship"""
        self.add_service(service_id)
        self.add_service(dependency_id)
        
        self.edges[service_id].add(dependency_id)
        self.reverse_edges[dependency_id].add(service_id)
    
    def remove_dependency(self, service_id: str, dependency_id: str) -> None:
        """Remove dependency relationship"""
        if service_id in self.edges:
            self.edges[service_id].discard(dependency_id)
        if dependency_id in self.reverse_edges:
            self.reverse_edges[dependency_id].discard(service_id)
    
    def get_dependencies(self, service_id: str) -> Set[str]:
        """Get direct dependencies of a service"""
        return self.edges.get(service_id, set()).copy()
    
    def get_dependents(self, service_id: str) -> Set[str]:
        """Get direct dependents of a service"""
        return self.reverse_edges.get(service_id, set()).copy()
    
    def get_startup_order(self) -> List[str]:
        """Get topological order for startup"""
        return self._topological_sort()
    
    def get_shutdown_order(self) -> List[str]:
        """Get reverse topological order for shutdown"""
        return list(reversed(self._topological_sort()))
    
    def _topological_sort(self) -> List[str]:
        """Topological sort using Kahn's algorithm"""
        in_degree = {node: 0 for node in self.nodes}
        
        # Calculate in-degrees
        for node in self.nodes:
            for dependency in self.edges[node]:
                in_degree[node] += 1
        
        # Queue of nodes with no dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Remove this node from the graph
            for dependent in self.reverse_edges[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check for circular dependencies
        if len(result) != len(self.nodes):
            logger.warning("Circular dependencies detected in service graph")
        
        return result
    
    def has_circular_dependencies(self) -> bool:
        """Check if the graph has circular dependencies"""
        return len(self._topological_sort()) != len(self.nodes)


class LifecycleManager:
    """
    Enterprise Service Lifecycle Manager with Dependency Management
    
    **Expert Roles Implemented:**
    - Backend Senior: Robust async lifecycle management, state coordination
    - DevOps: Service orchestration, health monitoring, automated recovery
    - Microservices: Dependency management, graceful shutdowns, service mesh integration
    - Lead Dev IA: Intelligent dependency resolution, predictive failure handling
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        health_check_interval: int = 30,
        state_sync_interval: int = 10,
        max_concurrent_operations: int = 10
    ):
        self.redis_url = redis_url
        self.health_check_interval = health_check_interval
        self.state_sync_interval = state_sync_interval
        self.max_concurrent_operations = max_concurrent_operations
        
        # Storage
        self.redis_client: Optional[aioredis.Redis] = None
        self.services: Dict[str, ServiceLifecycle] = {}
        self.dependency_graph = DependencyGraph()
        
        # Event handlers
        self.event_handlers: Dict[LifecycleEvent, List[Callable]] = {
            event: [] for event in LifecycleEvent
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.operation_semaphore = asyncio.Semaphore(max_concurrent_operations)
        
        # State management
        self.running = False
        self.shutdown_initiated = False
        
        # Signal handling
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self.shutdown_all_services())
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def initialize(self) -> None:
        """Initialize lifecycle manager"""
        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Load existing service lifecycles
            await self._load_service_lifecycles()
            
            # Start background tasks
            self.running = True
            self.background_tasks = [
                asyncio.create_task(self._health_monitoring_loop()),
                asyncio.create_task(self._state_sync_loop()),
                asyncio.create_task(self._dependency_monitoring_loop())
            ]
            
            logger.info("Lifecycle Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Lifecycle Manager: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        self.running = False
        self.shutdown_initiated = True
        
        # Stop all services in dependency order
        await self.shutdown_all_services()
        
        # Cancel health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(
            *self.health_check_tasks.values(),
            *self.background_tasks,
            return_exceptions=True
        )
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Lifecycle Manager shutdown completed")
    
    async def register_service(self, service_lifecycle: ServiceLifecycle) -> bool:
        """
        Register a service for lifecycle management
        
        **Roles**: Backend Senior + Microservices
        """
        try:
            service_id = service_lifecycle.service_id
            
            # Validate service lifecycle
            if not self._validate_service_lifecycle(service_lifecycle):
                return False
            
            # Store service
            self.services[service_id] = service_lifecycle
            
            # Add to dependency graph
            self.dependency_graph.add_service(service_id)
            for dependency in service_lifecycle.dependencies:
                self.dependency_graph.add_dependency(service_id, dependency)
            
            # Persist to Redis
            await self._save_service_lifecycle(service_lifecycle)
            
            # Start health checking if running
            if service_lifecycle.current_state == LifecycleState.RUNNING:
                await self._start_health_checking(service_lifecycle)
            
            logger.info(f"Service registered: {service_lifecycle.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service_lifecycle.service_name}: {e}")
            return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """Unregister a service"""
        try:
            if service_id not in self.services:
                return False
            
            service = self.services[service_id]
            
            # Stop the service first
            await self.stop_service(service_id)
            
            # Remove from dependency graph
            self.dependency_graph.nodes.discard(service_id)
            if service_id in self.dependency_graph.edges:
                del self.dependency_graph.edges[service_id]
            if service_id in self.dependency_graph.reverse_edges:
                del self.dependency_graph.reverse_edges[service_id]
            
            # Remove from storage
            del self.services[service_id]
            await self._remove_service_lifecycle(service_id)
            
            # Stop health checking
            if service_id in self.health_check_tasks:
                self.health_check_tasks[service_id].cancel()
                del self.health_check_tasks[service_id]
            
            logger.info(f"Service unregistered: {service.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service {service_id}: {e}")
            return False
    
    async def start_service(self, service_id: str) -> bool:
        """
        Start a service and its dependencies
        
        **Roles**: DevOps + Lead Dev IA + Microservices
        """
        async with self.operation_semaphore:
            try:
                if service_id not in self.services:
                    logger.error(f"Service not found: {service_id}")
                    return False
                
                service = self.services[service_id]
                
                # Check if already running
                if service.current_state == LifecycleState.RUNNING:
                    logger.info(f"Service already running: {service.service_name}")
                    return True
                
                # Start dependencies first
                dependencies = self.dependency_graph.get_dependencies(service_id)
                for dep_id in dependencies:
                    if not await self._ensure_dependency_running(dep_id):
                        logger.error(f"Failed to start dependency {dep_id} for service {service_id}")
                        return False
                
                # Execute startup sequence
                return await self._execute_startup_sequence(service)
                
            except Exception as e:
                logger.error(f"Failed to start service {service_id}: {e}")
                return False
    
    async def stop_service(self, service_id: str, force: bool = False) -> bool:
        """
        Stop a service and its dependents
        
        **Roles**: DevOps + Microservices
        """
        async with self.operation_semaphore:
            try:
                if service_id not in self.services:
                    logger.error(f"Service not found: {service_id}")
                    return False
                
                service = self.services[service_id]
                
                # Check if already stopped
                if service.current_state in [LifecycleState.STOPPED, LifecycleState.STOPPING]:
                    logger.info(f"Service already stopped/stopping: {service.service_name}")
                    return True
                
                # Stop dependents first
                if not force:
                    dependents = self.dependency_graph.get_dependents(service_id)
                    for dep_id in dependents:
                        await self.stop_service(dep_id)
                
                # Execute shutdown sequence
                return await self._execute_shutdown_sequence(service, force)
                
            except Exception as e:
                logger.error(f"Failed to stop service {service_id}: {e}")
                return False
    
    async def restart_service(self, service_id: str) -> bool:
        """
        Restart a service
        
        **Roles**: DevOps + Backend Senior
        """
        try:
            if service_id not in self.services:
                return False
            
            service = self.services[service_id]
            
            # Trigger before restart event
            await self._trigger_lifecycle_event(service, LifecycleEvent.BEFORE_RESTART)
            
            # Stop then start
            if await self.stop_service(service_id):
                await asyncio.sleep(service.restart_delay)
                success = await self.start_service(service_id)
                
                if success:
                    service.restart_count += 1
                    await self._trigger_lifecycle_event(service, LifecycleEvent.AFTER_RESTART)
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to restart service {service_id}: {e}")
            return False
    
    async def start_all_services(self) -> bool:
        """Start all services in dependency order"""
        try:
            startup_order = self.dependency_graph.get_startup_order()
            success_count = 0
            
            for service_id in startup_order:
                if service_id in self.services:
                    if await self.start_service(service_id):
                        success_count += 1
                    else:
                        logger.error(f"Failed to start service in startup sequence: {service_id}")
            
            logger.info(f"Started {success_count}/{len(startup_order)} services")
            return success_count == len(startup_order)
            
        except Exception as e:
            logger.error(f"Failed to start all services: {e}")
            return False
    
    async def shutdown_all_services(self) -> bool:
        """Shutdown all services in reverse dependency order"""
        try:
            shutdown_order = self.dependency_graph.get_shutdown_order()
            success_count = 0
            
            for service_id in shutdown_order:
                if service_id in self.services:
                    if await self.stop_service(service_id):
                        success_count += 1
                    else:
                        logger.warning(f"Failed to stop service in shutdown sequence: {service_id}")
            
            logger.info(f"Stopped {success_count}/{len(shutdown_order)} services")
            return success_count == len(shutdown_order)
            
        except Exception as e:
            logger.error(f"Failed to shutdown all services: {e}")
            return False
    
    async def _execute_startup_sequence(self, service: ServiceLifecycle) -> bool:
        """Execute service startup sequence"""
        try:
            # Update state
            await self._update_service_state(service, LifecycleState.STARTING)
            
            # Trigger before start event
            await self._trigger_lifecycle_event(service, LifecycleEvent.BEFORE_START)
            
            # Execute startup hooks
            for hook in service.startup_hooks:
                try:
                    if asyncio.iscoroutinefunction(hook):
                        await asyncio.wait_for(hook(), timeout=service.startup_timeout)
                    else:
                        hook()
                except Exception as e:
                    logger.error(f"Startup hook failed for {service.service_name}: {e}")
                    await self._update_service_state(service, LifecycleState.ERROR)
                    service.last_error = str(e)
                    service.error_count += 1
                    return False
            
            # Update to running state
            await self._update_service_state(service, LifecycleState.RUNNING)
            service.start_time = datetime.now()
            
            # Start health checking
            await self._start_health_checking(service)
            
            # Trigger after start event
            await self._trigger_lifecycle_event(service, LifecycleEvent.AFTER_START)
            
            logger.info(f"Service started successfully: {service.service_name}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"Service startup timeout: {service.service_name}")
            await self._update_service_state(service, LifecycleState.ERROR)
            service.last_error = "Startup timeout"
            service.error_count += 1
            return False
        
        except Exception as e:
            logger.error(f"Service startup failed: {service.service_name}: {e}")
            await self._update_service_state(service, LifecycleState.ERROR)
            service.last_error = str(e)
            service.error_count += 1
            return False
    
    async def _execute_shutdown_sequence(self, service: ServiceLifecycle, force: bool = False) -> bool:
        """Execute service shutdown sequence"""
        try:
            # Update state
            await self._update_service_state(service, LifecycleState.STOPPING)
            
            # Stop health checking
            if service.service_id in self.health_check_tasks:
                self.health_check_tasks[service.service_id].cancel()
                del self.health_check_tasks[service.service_id]
            
            # Trigger before stop event
            await self._trigger_lifecycle_event(service, LifecycleEvent.BEFORE_STOP)
            
            # Execute shutdown hooks
            for hook in service.shutdown_hooks:
                try:
                    timeout = 5 if force else service.shutdown_timeout
                    if asyncio.iscoroutinefunction(hook):
                        await asyncio.wait_for(hook(), timeout=timeout)
                    else:
                        hook()
                except Exception as e:
                    if not force:
                        logger.error(f"Shutdown hook failed for {service.service_name}: {e}")
                        service.last_error = str(e)
                        service.error_count += 1
            
            # Update to stopped state
            await self._update_service_state(service, LifecycleState.STOPPED)
            
            # Calculate uptime
            if service.start_time:
                uptime = (datetime.now() - service.start_time).total_seconds()
                service.uptime_seconds += int(uptime)
                service.start_time = None
            
            # Trigger after stop event
            await self._trigger_lifecycle_event(service, LifecycleEvent.AFTER_STOP)
            
            logger.info(f"Service stopped successfully: {service.service_name}")
            return True
            
        except asyncio.TimeoutError:
            if not force:
                logger.error(f"Service shutdown timeout: {service.service_name}")
                await self._update_service_state(service, LifecycleState.ERROR)
                service.last_error = "Shutdown timeout"
                service.error_count += 1
                return False
            else:
                # Force stop
                await self._update_service_state(service, LifecycleState.STOPPED)
                return True
        
        except Exception as e:
            logger.error(f"Service shutdown failed: {service.service_name}: {e}")
            await self._update_service_state(service, LifecycleState.ERROR)
            service.last_error = str(e)
            service.error_count += 1
            return False
    
    async def _ensure_dependency_running(self, dependency_id: str) -> bool:
        """Ensure a dependency is running"""
        if dependency_id not in self.services:
            logger.error(f"Dependency not found: {dependency_id}")
            return False
        
        dependency = self.services[dependency_id]
        
        if dependency.current_state == LifecycleState.RUNNING:
            return True
        
        # Try to start the dependency
        return await self.start_service(dependency_id)
    
    async def _start_health_checking(self, service: ServiceLifecycle) -> None:
        """Start health checking for a service"""
        if not service.health_check_hook:
            return
        
        async def health_check_worker():
            while (self.running and 
                   service.service_id in self.services and 
                   self.services[service.service_id].current_state == LifecycleState.RUNNING):
                try:
                    # Perform health check
                    is_healthy = await self._perform_health_check(service)
                    
                    if not is_healthy:
                        logger.warning(f"Health check failed for {service.service_name}")
                        
                        # Handle unhealthy service
                        await self._handle_unhealthy_service(service)
                    
                    service.last_health_check = datetime.now()
                    await asyncio.sleep(service.health_check_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Health check error for {service.service_name}: {e}")
                    await asyncio.sleep(5)
        
        task = asyncio.create_task(health_check_worker())
        self.health_check_tasks[service.service_id] = task
    
    async def _perform_health_check(self, service: ServiceLifecycle) -> bool:
        """Perform health check on a service"""
        if not service.health_check_hook:
            return True
        
        try:
            if asyncio.iscoroutinefunction(service.health_check_hook):
                result = await asyncio.wait_for(
                    service.health_check_hook(),
                    timeout=30
                )
            else:
                result = service.health_check_hook()
            
            # Trigger health check event
            await self._trigger_lifecycle_event(service, LifecycleEvent.HEALTH_CHECK)
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Health check exception for {service.service_name}: {e}")
            return False
    
    async def _handle_unhealthy_service(self, service: ServiceLifecycle) -> None:
        """Handle an unhealthy service"""
        service.error_count += 1
        
        if service.auto_restart and service.restart_count < service.max_restart_attempts:
            logger.info(f"Attempting to restart unhealthy service: {service.service_name}")
            await self.restart_service(service.service_id)
        else:
            logger.error(f"Service marked as crashed: {service.service_name}")
            await self._update_service_state(service, LifecycleState.CRASHED)
            service.crash_count += 1
    
    async def _update_service_state(self, service: ServiceLifecycle, new_state: LifecycleState) -> None:
        """Update service state"""
        old_state = service.current_state
        service.previous_state = old_state
        service.current_state = new_state
        
        # Persist state change
        await self._save_service_lifecycle(service)
        
        logger.debug(f"Service {service.service_name} state: {old_state.value} -> {new_state.value}")
    
    async def _trigger_lifecycle_event(self, service: ServiceLifecycle, event: LifecycleEvent) -> None:
        """Trigger lifecycle event handlers"""
        handlers = self.event_handlers.get(event, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(service, event)
                else:
                    handler(service, event)
            except Exception as e:
                logger.error(f"Lifecycle event handler error for {event.value}: {e}")
    
    def register_event_handler(self, event: LifecycleEvent, handler: Callable) -> None:
        """Register an event handler"""
        self.event_handlers[event].append(handler)
    
    def unregister_event_handler(self, event: LifecycleEvent, handler: Callable) -> None:
        """Unregister an event handler"""
        if handler in self.event_handlers[event]:
            self.event_handlers[event].remove(handler)
    
    def _validate_service_lifecycle(self, service: ServiceLifecycle) -> bool:
        """Validate service lifecycle configuration"""
        if not service.service_id or not service.service_name:
            return False
        
        if service.startup_timeout <= 0 or service.shutdown_timeout <= 0:
            return False
        
        return True
    
    async def _save_service_lifecycle(self, service: ServiceLifecycle) -> None:
        """Save service lifecycle to Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"lifecycle:{service.service_id}"
            value = json.dumps(service.to_dict())
            await self.redis_client.set(key, value)
        except Exception as e:
            logger.error(f"Failed to save service lifecycle to Redis: {e}")
    
    async def _remove_service_lifecycle(self, service_id: str) -> None:
        """Remove service lifecycle from Redis"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(f"lifecycle:{service_id}")
        except Exception as e:
            logger.error(f"Failed to remove service lifecycle from Redis: {e}")
    
    async def _load_service_lifecycles(self) -> None:
        """Load service lifecycles from Redis"""
        if not self.redis_client:
            return
        
        try:
            keys = await self.redis_client.keys("lifecycle:*")
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    service_data = json.loads(data)
                    service = ServiceLifecycle.from_dict(service_data)
                    self.services[service.service_id] = service
                    
                    # Rebuild dependency graph
                    self.dependency_graph.add_service(service.service_id)
                    for dependency in service.dependencies:
                        self.dependency_graph.add_dependency(service.service_id, dependency)
            
            logger.info(f"Loaded {len(self.services)} service lifecycles")
        except Exception as e:
            logger.error(f"Failed to load service lifecycles from Redis: {e}")
    
    async def _health_monitoring_loop(self) -> None:
        """Background health monitoring loop"""
        while self.running:
            try:
                # Monitor overall system health
                await self._monitor_system_health()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_system_health(self) -> None:
        """Monitor overall system health"""
        running_services = len([s for s in self.services.values() if s.current_state == LifecycleState.RUNNING])
        total_services = len(self.services)
        
        if total_services > 0:
            health_percentage = (running_services / total_services) * 100
            logger.debug(f"System health: {running_services}/{total_services} services running ({health_percentage:.1f}%)")
    
    async def _state_sync_loop(self) -> None:
        """Background state synchronization loop"""
        while self.running:
            try:
                await self._sync_service_states()
                await asyncio.sleep(self.state_sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"State sync error: {e}")
                await asyncio.sleep(10)
    
    async def _sync_service_states(self) -> None:
        """Synchronize service states with Redis"""
        for service in self.services.values():
            await self._save_service_lifecycle(service)
    
    async def _dependency_monitoring_loop(self) -> None:
        """Background dependency monitoring loop"""
        while self.running:
            try:
                await self._check_dependency_violations()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Dependency monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _check_dependency_violations(self) -> None:
        """Check for dependency violations"""
        for service_id, service in self.services.items():
            if service.current_state == LifecycleState.RUNNING:
                # Check if all dependencies are running
                for dep_id in service.dependencies:
                    if dep_id in self.services:
                        dep_service = self.services[dep_id]
                        if dep_service.current_state != LifecycleState.RUNNING:
                            logger.warning(f"Dependency violation: {service.service_name} running but {dep_service.service_name} not running")
                            await self._trigger_lifecycle_event(service, LifecycleEvent.DEPENDENCY_FAILED)
    
    async def get_service_status(self, service_id: str) -> Optional[ServiceLifecycle]:
        """Get current status of a service"""
        return self.services.get(service_id)
    
    async def get_all_services(self) -> List[ServiceLifecycle]:
        """Get all registered services"""
        return list(self.services.values())
    
    async def get_services_by_state(self, state: LifecycleState) -> List[ServiceLifecycle]:
        """Get services by state"""
        return [s for s in self.services.values() if s.current_state == state]
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get system overview"""
        states = {}
        for service in self.services.values():
            state = service.current_state.value
            states[state] = states.get(state, 0) + 1
        
        return {
            'total_services': len(self.services),
            'states': states,
            'dependency_graph_size': len(self.dependency_graph.nodes),
            'has_circular_dependencies': self.dependency_graph.has_circular_dependencies(),
            'startup_order': self.dependency_graph.get_startup_order(),
            'shutdown_order': self.dependency_graph.get_shutdown_order()
        }