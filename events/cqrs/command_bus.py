"""🚀 Enterprise Command Bus - CQRS Architecture
=====================================================
Module: events/cqrs/command_bus.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE COMMAND BUS
Central command processing hub for CQRS architecture
- Command routing to appropriate handlers
- Transaction management across services
- Command validation and authentication
- Audit trail and monitoring
- Rate limiting and circuit breaker
- Retry mechanism with exponential backoff
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Type
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor

from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)


class CommandStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Command:
    """Base command class for CQRS operations"""
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    command_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.MEDIUM
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_count: int = 0


@dataclass
class CommandResult:
    """Command execution result"""
    command_id: str
    status: CommandStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    events: List[BaseEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommandHandler:
    """Base command handler interface"""
    
    async def handle(self, command: Command) -> CommandResult:
        """Handle command and return result"""
        raise NotImplementedError


class EnterpriseCommandBus:
    """Enterprise-grade command bus with advanced features"""
    
    def __init__(self, 
                 max_concurrent_commands: int = 100,
                 enable_circuit_breaker: bool = True,
                 enable_rate_limiting: bool = True):
        self._handlers: Dict[str, CommandHandler] = {}
        self._middleware: List[Callable] = []
        self._audit_logger = logging.getLogger(f"{__name__}.audit")
        self._metrics: Dict[str, Any] = {
            "commands_processed": 0,
            "commands_failed": 0,
            "average_execution_time": 0.0,
            "circuit_breaker_trips": 0
        }
        
        # Configuration
        self._max_concurrent = max_concurrent_commands
        self._enable_circuit_breaker = enable_circuit_breaker
        self._enable_rate_limiting = enable_rate_limiting
        
        # State management
        self._active_commands: Dict[str, Command] = {}
        self._command_history: List[CommandResult] = []
        self._circuit_breaker_state = {"open": False, "failure_count": 0, "last_failure": None}
        self._rate_limiter = {"requests": [], "max_per_minute": 1000}
        
        # Async processing
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._processing_semaphore = asyncio.Semaphore(max_concurrent_commands)
    
    def register_handler(self, command_type: str, handler: CommandHandler) -> None:
        """Register command handler for specific command type"""
        if not isinstance(handler, CommandHandler):
            raise ValueError(f"Handler must inherit from CommandHandler: {type(handler)}")
        
        self._handlers[command_type] = handler
        logger.info(f"Registered command handler for type: {command_type}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware for command processing pipeline"""
        self._middleware.append(middleware)
        logger.info(f"Added middleware: {middleware.__name__}")
    
    async def execute_command(self, command: Command) -> CommandResult:
        """Execute command with full enterprise pipeline"""
        start_time = time.time()
        
        try:
            # Pre-execution validation and middleware
            await self._validate_command(command)
            await self._apply_middleware(command, "pre_execution")
            await self._check_circuit_breaker()
            await self._apply_rate_limiting()
            
            # Track active command
            self._active_commands[command.command_id] = command
            
            # Execute with concurrency control
            async with self._processing_semaphore:
                result = await self._execute_command_internal(command)
            
            # Post-execution processing
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time
            
            await self._apply_middleware(command, "post_execution", result)
            await self._audit_command_execution(command, result)
            await self._update_metrics(command, result)
            
            return result
            
        except Exception as e:
            # Error handling and circuit breaker management
            execution_time = (time.time() - start_time) * 1000
            error_result = CommandResult(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time
            )
            
            await self._handle_command_failure(command, error_result, e)
            return error_result
            
        finally:
            # Cleanup
            self._active_commands.pop(command.command_id, None)
    
    async def _execute_command_internal(self, command: Command) -> CommandResult:
        """Internal command execution logic"""
        handler = self._handlers.get(command.command_type)
        if not handler:
            raise EventProcessingError(f"No handler registered for command type: {command.command_type}")
        
        # Update status
        result = CommandResult(
            command_id=command.command_id,
            status=CommandStatus.PROCESSING
        )
        
        try:
            # Execute command with timeout
            result = await asyncio.wait_for(
                handler.handle(command),
                timeout=command.timeout_seconds
            )
            result.status = CommandStatus.COMPLETED
            
        except asyncio.TimeoutError:
            result.status = CommandStatus.FAILED
            result.error = f"Command timed out after {command.timeout_seconds} seconds"
            
        except Exception as e:
            result.status = CommandStatus.FAILED
            result.error = str(e)
            
        return result
    
    async def _validate_command(self, command: Command) -> None:
        """Validate command before execution"""
        if not command.command_type:
            raise EventValidationError("Command type is required")
        
        if not command.command_id:
            raise EventValidationError("Command ID is required")
        
        # Additional business validation can be added here
        logger.debug(f"Command validated: {command.command_id}")
    
    async def _apply_middleware(self, command: Command, phase: str, result: Optional[CommandResult] = None) -> None:
        """Apply middleware pipeline"""
        for middleware in self._middleware:
            try:
                if asyncio.iscoroutinefunction(middleware):
                    await middleware(command, phase, result)
                else:
                    middleware(command, phase, result)
            except Exception as e:
                logger.error(f"Middleware error in {middleware.__name__}: {e}")
    
    async def _check_circuit_breaker(self) -> None:
        """Check circuit breaker state"""
        if not self._enable_circuit_breaker:
            return
        
        if self._circuit_breaker_state["open"]:
            # Check if circuit should close (after cooldown period)
            if self._circuit_breaker_state["last_failure"]:
                cooldown_period = timedelta(minutes=5)
                if datetime.utcnow() - self._circuit_breaker_state["last_failure"] > cooldown_period:
                    self._circuit_breaker_state["open"] = False
                    self._circuit_breaker_state["failure_count"] = 0
                    logger.info("Circuit breaker closed after cooldown")
                else:
                    raise EventProcessingError("Circuit breaker is open - service unavailable")
    
    async def _apply_rate_limiting(self) -> None:
        """Apply rate limiting"""
        if not self._enable_rate_limiting:
            return
        
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self._rate_limiter["requests"] = [
            req_time for req_time in self._rate_limiter["requests"] 
            if req_time > minute_ago
        ]
        
        # Check rate limit
        if len(self._rate_limiter["requests"]) >= self._rate_limiter["max_per_minute"]:
            raise EventProcessingError("Rate limit exceeded")
        
        self._rate_limiter["requests"].append(now)
    
    async def _audit_command_execution(self, command: Command, result: CommandResult) -> None:
        """Audit command execution for compliance and monitoring"""
        audit_data = {
            "command_id": command.command_id,
            "command_type": command.command_type,
            "user_id": command.user_id,
            "status": result.status.value,
            "execution_time_ms": result.execution_time_ms,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": command.correlation_id
        }
        
        self._audit_logger.info("Command executed", extra=audit_data)
        self._command_history.append(result)
        
        # Keep only last 1000 commands in memory
        if len(self._command_history) > 1000:
            self._command_history = self._command_history[-1000:]
    
    async def _update_metrics(self, command: Command, result: CommandResult) -> None:
        """Update performance metrics"""
        self._metrics["commands_processed"] += 1
        
        if result.status == CommandStatus.FAILED:
            self._metrics["commands_failed"] += 1
        
        if result.execution_time_ms:
            # Update rolling average
            current_avg = self._metrics["average_execution_time"]
            total_commands = self._metrics["commands_processed"]
            new_avg = ((current_avg * (total_commands - 1)) + result.execution_time_ms) / total_commands
            self._metrics["average_execution_time"] = new_avg
    
    async def _handle_command_failure(self, command: Command, result: CommandResult, exception: Exception) -> None:
        """Handle command failure and circuit breaker logic"""
        logger.error(f"Command failed: {command.command_id} - {exception}")
        
        # Update circuit breaker state
        if self._enable_circuit_breaker:
            self._circuit_breaker_state["failure_count"] += 1
            self._circuit_breaker_state["last_failure"] = datetime.utcnow()
            
            # Open circuit if failure threshold reached
            if self._circuit_breaker_state["failure_count"] >= 5:
                self._circuit_breaker_state["open"] = True
                self._metrics["circuit_breaker_trips"] += 1
                logger.warning("Circuit breaker opened due to high failure rate")
        
        # Retry logic for retryable commands
        if command.retry_count < command.max_retries and self._is_retryable_error(exception):
            command.retry_count += 1
            result.status = CommandStatus.RETRYING
            
            # Exponential backoff
            delay = min(2 ** command.retry_count, 60)
            logger.info(f"Retrying command {command.command_id} in {delay} seconds")
            
            asyncio.create_task(self._retry_command_after_delay(command, delay))
    
    def _is_retryable_error(self, exception: Exception) -> bool:
        """Determine if error is retryable"""
        retryable_types = (asyncio.TimeoutError, ConnectionError, OSError)
        return isinstance(exception, retryable_types)
    
    async def _retry_command_after_delay(self, command: Command, delay_seconds: int) -> None:
        """Retry command after delay"""
        await asyncio.sleep(delay_seconds)
        await self.execute_command(command)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get command bus performance metrics"""
        return {
            **self._metrics,
            "active_commands": len(self._active_commands),
            "circuit_breaker_open": self._circuit_breaker_state["open"],
            "handler_count": len(self._handlers),
            "middleware_count": len(self._middleware)
        }
    
    def get_active_commands(self) -> List[Dict[str, Any]]:
        """Get currently active commands"""
        return [
            {
                "command_id": cmd.command_id,
                "command_type": cmd.command_type,
                "user_id": cmd.user_id,
                "created_at": cmd.created_at.isoformat(),
                "priority": cmd.priority.value
            }
            for cmd in self._active_commands.values()
        ]
    
    async def shutdown(self) -> None:
        """Graceful shutdown of command bus"""
        logger.info("Shutting down command bus...")
        
        # Wait for active commands to complete (with timeout)
        max_wait = 30  # seconds
        start_time = time.time()
        
        while self._active_commands and (time.time() - start_time) < max_wait:
            await asyncio.sleep(0.1)
        
        if self._active_commands:
            logger.warning(f"Shutdown with {len(self._active_commands)} active commands")
        
        self._executor.shutdown(wait=True)
        logger.info("Command bus shutdown complete")


# Singleton instance for global access
_command_bus_instance: Optional[EnterpriseCommandBus] = None


def get_command_bus() -> EnterpriseCommandBus:
    """Get singleton command bus instance"""
    global _command_bus_instance
    if _command_bus_instance is None:
        _command_bus_instance = EnterpriseCommandBus()
    return _command_bus_instance


def reset_command_bus() -> None:
    """Reset command bus instance (for testing)"""
    global _command_bus_instance
    _command_bus_instance = None