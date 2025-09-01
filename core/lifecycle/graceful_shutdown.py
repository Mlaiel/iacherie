"""
Graceful Shutdown Implementation for All Services
Ensures proper resource cleanup and request completion during shutdown

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import signal
import logging
import time
from typing import List, Callable, Dict, Any, Optional, Awaitable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from enum import Enum


logger = logging.getLogger(__name__)


class ShutdownState(Enum):
    """Shutdown states"""
    RUNNING = "running"
    SHUTDOWN_INITIATED = "shutdown_initiated"
    DRAINING = "draining"
    STOPPING_TASKS = "stopping_tasks"
    CLEANUP = "cleanup"
    SHUTDOWN_COMPLETE = "shutdown_complete"


@dataclass
class ShutdownConfig:
    """Configuration for graceful shutdown"""
    shutdown_timeout: float = 30.0  # Maximum time to wait for shutdown
    drain_timeout: float = 15.0  # Time to wait for current requests to complete
    task_timeout: float = 10.0  # Time to wait for background tasks
    health_check_grace_period: float = 5.0  # Time before marking service unhealthy
    force_shutdown_signals: List[int] = field(default_factory=lambda: [signal.SIGTERM, signal.SIGINT])


@dataclass
class ShutdownHook:
    """A shutdown hook with priority and timeout"""
    name: str
    callback: Callable[[], Awaitable[None]]
    priority: int = 0  # Higher priority runs first
    timeout: float = 10.0
    critical: bool = False  # If True, failure will abort shutdown


class GracefulShutdownManager:
    """
    Manager for graceful application shutdown
    Coordinates shutdown sequence across all application components
    """
    
    def __init__(self, config: Optional[ShutdownConfig] = None):
        self.config = config or ShutdownConfig()
        self.state = ShutdownState.RUNNING
        self.shutdown_hooks: List[ShutdownHook] = []
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        self.background_tasks: List[asyncio.Task] = []
        self.shutdown_event = asyncio.Event()
        self.shutdown_complete_event = asyncio.Event()
        self.lock = asyncio.Lock()
        self.start_time = time.time()
        self.shutdown_start_time: Optional[float] = None
        
        # Health status
        self.healthy = True
        self.ready = True
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("Graceful shutdown manager initialized")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        for sig in self.config.force_shutdown_signals:
            try:
                signal.signal(sig, self._signal_handler)
                logger.debug(f"Registered signal handler for {signal.Signals(sig).name}")
            except (ValueError, OSError) as e:
                logger.warning(f"Could not register signal handler for {sig}: {e}")
    
    def _signal_handler(self, signum: int, frame):
        """Handle shutdown signals"""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name}, initiating graceful shutdown")
        
        # Start shutdown asynchronously
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.shutdown())
        except RuntimeError:
            # If no event loop is running, we can't do much
            logger.error("No event loop running, cannot perform graceful shutdown")
    
    def register_shutdown_hook(self, name: str, callback: Callable[[], Awaitable[None]], 
                             priority: int = 0, timeout: float = 10.0, critical: bool = False):
        """Register a shutdown hook"""
        hook = ShutdownHook(
            name=name,
            callback=callback,
            priority=priority,
            timeout=timeout,
            critical=critical
        )
        self.shutdown_hooks.append(hook)
        # Sort by priority (higher first)
        self.shutdown_hooks.sort(key=lambda h: h.priority, reverse=True)
        logger.debug(f"Added shutdown hook: {hook.name} (priority: {hook.priority})")
    
    async def track_request(self, request_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Track an active request"""
        async with self.lock:
            self.active_requests[request_id] = {
                'start_time': time.time(),
                'metadata': metadata or {},
                'completed': False
            }
    
    async def complete_request(self, request_id: str):
        """Mark a request as completed"""
        async with self.lock:
            if request_id in self.active_requests:
                self.active_requests[request_id]['completed'] = True
                self.active_requests[request_id]['end_time'] = time.time()
    
    async def is_healthy(self) -> bool:
        """Check if service is healthy"""
        if self.state == ShutdownState.RUNNING:
            return self.healthy
        
        # During shutdown, we're unhealthy after grace period
        if self.shutdown_start_time and self.state in [
            ShutdownState.SHUTDOWN_INITIATED,
            ShutdownState.DRAINING
        ]:
            elapsed = time.time() - self.shutdown_start_time
            return elapsed < self.config.health_check_grace_period
        
        return False
    
    async def is_ready(self) -> bool:
        """Check if service is ready to receive requests"""
        return self.state == ShutdownState.RUNNING and self.ready
    
    async def shutdown(self):
        """Initiate graceful shutdown"""
        if self.state != ShutdownState.RUNNING:
            logger.warning("Shutdown already in progress")
            return
        
        async with self.lock:
            if self.state != ShutdownState.RUNNING:
                return
            
            self.state = ShutdownState.SHUTDOWN_INITIATED
            self.shutdown_start_time = time.time()
            self.shutdown_event.set()
        
        logger.info("🛑 Graceful shutdown initiated")
        
        try:
            # Phase 1: Stop accepting new requests
            await self._stop_accepting_requests()
            
            # Phase 2: Drain existing requests
            await self._drain_requests()
            
            # Phase 3: Stop background tasks
            await self._stop_background_tasks()
            
            # Phase 4: Execute shutdown hooks
            await self._execute_shutdown_hooks()
            
            # Phase 5: Final cleanup
            await self._final_cleanup()
            
            self.state = ShutdownState.SHUTDOWN_COMPLETE
            self.shutdown_complete_event.set()
            
            shutdown_duration = time.time() - self.shutdown_start_time
            logger.info(f"✅ Graceful shutdown completed in {shutdown_duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
            self.state = ShutdownState.SHUTDOWN_COMPLETE
            self.shutdown_complete_event.set()
            raise
    
    async def _stop_accepting_requests(self):
        """Stop accepting new requests"""
        logger.info("📵 Stopping acceptance of new requests")
        self.state = ShutdownState.DRAINING
        self.ready = False
        
        # Wait a moment for load balancers to update
        await asyncio.sleep(self.config.health_check_grace_period)
    
    async def _drain_requests(self):
        """Wait for existing requests to complete"""
        logger.info("⏳ Draining existing requests")
        
        start_time = time.time()
        
        while time.time() - start_time < self.config.drain_timeout:
            async with self.lock:
                active_count = len([
                    req for req in self.active_requests.values()
                    if not req.get('completed', False)
                ])
            
            if active_count == 0:
                logger.info("✅ All requests completed")
                break
            
            logger.info(f"⏳ Waiting for {active_count} requests to complete")
            await asyncio.sleep(1.0)
    
    async def _stop_background_tasks(self):
        """Stop background tasks"""
        logger.info("🔄 Stopping background tasks")
        self.state = ShutdownState.STOPPING_TASKS
        
        if not self.background_tasks:
            logger.info("✅ No background tasks to stop")
            return
        
        logger.info(f"⏳ Stopping {len(self.background_tasks)} background tasks")
        
        # Cancel all tasks
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.background_tasks, return_exceptions=True),
                    timeout=self.config.task_timeout
                )
                logger.info("✅ All background tasks stopped")
            except asyncio.TimeoutError:
                logger.warning("⚠️ Some background tasks did not stop within timeout")
    
    async def _execute_shutdown_hooks(self):
        """Execute shutdown hooks in priority order"""
        logger.info("🪝 Executing shutdown hooks")
        self.state = ShutdownState.CLEANUP
        
        if not self.shutdown_hooks:
            logger.info("✅ No shutdown hooks to execute")
            return
        
        logger.info(f"⏳ Executing {len(self.shutdown_hooks)} shutdown hooks")
        
        for hook in self.shutdown_hooks:
            try:
                logger.debug(f"Executing shutdown hook: {hook.name}")
                await asyncio.wait_for(hook.callback(), timeout=hook.timeout)
                logger.debug(f"✅ Shutdown hook completed: {hook.name}")
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ Shutdown hook timed out: {hook.name}")
                if hook.critical:
                    raise
                    
            except Exception as e:
                logger.error(f"❌ Shutdown hook failed: {hook.name}: {e}")
                if hook.critical:
                    raise
        
        logger.info("✅ All shutdown hooks executed")
    
    async def _final_cleanup(self):
        """Perform final cleanup"""
        logger.info("🧹 Performing final cleanup")
        
        # Clear tracking data
        async with self.lock:
            self.active_requests.clear()
            self.background_tasks.clear()
        
        # Mark as unhealthy
        self.healthy = False
        self.ready = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current shutdown manager status"""
        active_request_count = len([
            req for req in self.active_requests.values()
            if not req.get('completed', False)
        ])
        
        background_task_count = len([
            task for task in self.background_tasks
            if not task.done()
        ])
        
        uptime = time.time() - self.start_time
        
        status = {
            'state': self.state.value,
            'healthy': self.healthy,
            'ready': self.ready,
            'uptime_seconds': uptime,
            'active_requests': active_request_count,
            'background_tasks': background_task_count,
            'shutdown_hooks': len(self.shutdown_hooks)
        }
        
        if self.shutdown_start_time:
            shutdown_duration = time.time() - self.shutdown_start_time
            status['shutdown_duration_seconds'] = shutdown_duration
        
        return status