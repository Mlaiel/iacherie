"""Ainflue Core Infrastructure - CQRS Core
=========================================

Enterprise-grade Command Query Responsibility Segregation (CQRS) implementation
providing command/query separation, event sourcing integration, read model projections,
and scalable distributed query processing for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Union, Callable
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import threading
import copy

# Setup logger
logger = logging.getLogger(__name__)

T = TypeVar('T')
TCommand = TypeVar('TCommand')
TQuery = TypeVar('TQuery')
TResult = TypeVar('TResult')

class CommandStatus(str, Enum):
    """Command execution status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class QueryStatus(str, Enum):
    """Query execution status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"

class CommandPriority(str, Enum):
    """Command priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

@dataclass
class Command:
    """Base command class"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    command_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    priority: CommandPriority = CommandPriority.NORMAL
    timeout_seconds: int = 300
    max_retries: int = 3
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    status: CommandStatus = CommandStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['scheduled_at'] = self.scheduled_at.isoformat() if self.scheduled_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Command':
        """Create command from dictionary"""
        command = cls()
        command.id = data.get('id', command.id)
        command.command_type = data.get('command_type', '')
        command.data = data.get('data', {})
        command.metadata = data.get('metadata', {})
        command.correlation_id = data.get('correlation_id')
        command.causation_id = data.get('causation_id')
        command.user_id = data.get('user_id')
        command.tenant_id = data.get('tenant_id')
        command.priority = CommandPriority(data.get('priority', CommandPriority.NORMAL.value))
        command.timeout_seconds = data.get('timeout_seconds', 300)
        command.max_retries = data.get('max_retries', 3)
        command.retry_count = data.get('retry_count', 0)
        command.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow()
        command.scheduled_at = datetime.fromisoformat(data['scheduled_at']) if data.get('scheduled_at') else None
        command.status = CommandStatus(data.get('status', CommandStatus.PENDING.value))
        return command

@dataclass
class Query:
    """Base query class"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    sorting: List[Dict[str, str]] = field(default_factory=list)
    pagination: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    cache_key: Optional[str] = None
    cache_ttl: int = 300  # 5 minutes default
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: QueryStatus = QueryStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class CommandResult:
    """Command execution result"""
    command_id: str
    success: bool
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    events_generated: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    executed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QueryResult:
    """Query execution result"""
    query_id: str
    success: bool
    data: Any = None
    total_count: Optional[int] = None
    page_info: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    execution_time_ms: float = 0.0
    cache_hit: bool = False
    executed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandHandler(ABC, Generic[TCommand]):
    """Abstract command handler"""
    
    @abstractmethod
    async def handle(self, command: TCommand) -> CommandResult:
        """Handle command execution"""
        pass
    
    @abstractmethod
    def can_handle(self, command_type: str) -> bool:
        """Check if handler can process command type"""
        pass
    
    async def validate(self, command: TCommand) -> bool:
        """Validate command before execution"""
        return True

class QueryHandler(ABC, Generic[TQuery, TResult]):
    """Abstract query handler"""
    
    @abstractmethod
    async def handle(self, query: TQuery) -> QueryResult:
        """Handle query execution"""
        pass
    
    @abstractmethod
    def can_handle(self, query_type: str) -> bool:
        """Check if handler can process query type"""
        pass
    
    async def validate(self, query: TQuery) -> bool:
        """Validate query before execution"""
        return True

class ReadModel(ABC):
    """Abstract read model for queries"""
    
    def __init__(self, name: str):
        self.name = name
        self.version = 0
        self.last_updated = datetime.utcnow()
        self.data: Dict[str, Any] = {}
    
    @abstractmethod
    async def project_event(self, event: Dict[str, Any]):
        """Project event data into read model"""
        pass
    
    @abstractmethod
    async def query(self, parameters: Dict[str, Any]) -> Any:
        """Query read model data"""
        pass
    
    async def reset(self):
        """Reset read model to initial state"""
        self.data = {}
        self.version = 0
        self.last_updated = datetime.utcnow()

class CommandBus:
    """Command bus for dispatching commands"""
    
    def __init__(self):
        self.handlers: Dict[str, CommandHandler] = {}
        self.middleware: List[Callable] = []
        self.command_queue: List[Command] = []
        self.processing_commands: Dict[str, Command] = {}
        self.results: Dict[str, CommandResult] = {}
        self.lock = threading.Lock()
        
    def register_handler(self, command_type: str, handler: CommandHandler):
        """Register command handler"""
        self.handlers[command_type] = handler
        logger.info(f"Registered command handler for: {command_type}")
    
    def add_middleware(self, middleware: Callable):
        """Add middleware to command pipeline"""
        self.middleware.append(middleware)
    
    async def dispatch(self, command: Command) -> str:
        """Dispatch command for execution"""
        try:
            # Apply middleware
            for middleware in self.middleware:
                await middleware(command)
            
            # Validate command
            if command.command_type not in self.handlers:
                raise Exception(f"No handler registered for command type: {command.command_type}")
            
            handler = self.handlers[command.command_type]
            
            # Validate with handler
            is_valid = await handler.validate(command)
            if not is_valid:
                raise Exception("Command validation failed")
            
            # Add to queue
            with self.lock:
                self.command_queue.append(command)
            
            logger.info(f"Command {command.id} queued for execution")
            return command.id
            
        except Exception as e:
            logger.error(f"Failed to dispatch command {command.id}: {str(e)}")
            # Store error result
            self.results[command.id] = CommandResult(
                command_id=command.id,
                success=False,
                error_message=str(e),
                error_code="DISPATCH_FAILED"
            )
            raise
    
    async def execute_next(self) -> Optional[CommandResult]:
        """Execute next command in queue"""
        command = None
        
        with self.lock:
            if self.command_queue:
                # Sort by priority and creation time
                self.command_queue.sort(key=lambda c: (
                    self._get_priority_order(c.priority),
                    c.created_at
                ))
                command = self.command_queue.pop(0)
                self.processing_commands[command.id] = command
        
        if not command:
            return None
        
        try:
            command.status = CommandStatus.EXECUTING
            start_time = datetime.utcnow()
            
            handler = self.handlers[command.command_type]
            result = await handler.handle(command)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time
            
            command.status = CommandStatus.COMPLETED
            self.results[command.id] = result
            
            with self.lock:
                if command.id in self.processing_commands:
                    del self.processing_commands[command.id]
            
            logger.info(f"Command {command.id} executed successfully in {execution_time:.2f}ms")
            return result
            
        except Exception as e:
            command.status = CommandStatus.FAILED
            command.retry_count += 1
            
            # Handle retries
            if command.retry_count <= command.max_retries:
                command.status = CommandStatus.RETRYING
                with self.lock:
                    self.command_queue.append(command)
                logger.warning(f"Command {command.id} failed, retrying ({command.retry_count}/{command.max_retries})")
            else:
                error_result = CommandResult(
                    command_id=command.id,
                    success=False,
                    error_message=str(e),
                    error_code="EXECUTION_FAILED"
                )
                self.results[command.id] = error_result
                logger.error(f"Command {command.id} failed after {command.max_retries} retries: {str(e)}")
            
            with self.lock:
                if command.id in self.processing_commands:
                    del self.processing_commands[command.id]
            
            return None
    
    def _get_priority_order(self, priority: CommandPriority) -> int:
        """Get numeric order for priority sorting"""
        order_map = {
            CommandPriority.URGENT: 0,
            CommandPriority.CRITICAL: 1,
            CommandPriority.HIGH: 2,
            CommandPriority.NORMAL: 3,
            CommandPriority.LOW: 4
        }
        return order_map.get(priority, 3)
    
    def get_result(self, command_id: str) -> Optional[CommandResult]:
        """Get command execution result"""
        return self.results.get(command_id)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get command queue status"""
        with self.lock:
            return {
                'queued_commands': len(self.command_queue),
                'processing_commands': len(self.processing_commands),
                'completed_commands': len(self.results),
                'registered_handlers': len(self.handlers)
            }

class QueryBus:
    """Query bus for dispatching queries"""
    
    def __init__(self):
        self.handlers: Dict[str, QueryHandler] = {}
        self.read_models: Dict[str, ReadModel] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.middleware: List[Callable] = []
        self.results: Dict[str, QueryResult] = {}
        
    def register_handler(self, query_type: str, handler: QueryHandler):
        """Register query handler"""
        self.handlers[query_type] = handler
        logger.info(f"Registered query handler for: {query_type}")
    
    def register_read_model(self, name: str, read_model: ReadModel):
        """Register read model"""
        self.read_models[name] = read_model
        logger.info(f"Registered read model: {name}")
    
    def add_middleware(self, middleware: Callable):
        """Add middleware to query pipeline"""
        self.middleware.append(middleware)
    
    async def dispatch(self, query: Query) -> QueryResult:
        """Dispatch query for execution"""
        try:
            start_time = datetime.utcnow()
            
            # Apply middleware
            for middleware in self.middleware:
                await middleware(query)
            
            # Check cache first
            if query.cache_key:
                cached_result = self._get_cached_result(query)
                if cached_result:
                    return cached_result
            
            # Validate query
            if query.query_type not in self.handlers:
                raise Exception(f"No handler registered for query type: {query.query_type}")
            
            handler = self.handlers[query.query_type]
            
            # Validate with handler
            is_valid = await handler.validate(query)
            if not is_valid:
                raise Exception("Query validation failed")
            
            # Execute query
            query.status = QueryStatus.EXECUTING
            result = await handler.handle(query)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time
            
            query.status = QueryStatus.COMPLETED
            self.results[query.id] = result
            
            # Cache result if configured
            if query.cache_key and result.success:
                self._cache_result(query, result)
            
            logger.info(f"Query {query.id} executed successfully in {execution_time:.2f}ms")
            return result
            
        except Exception as e:
            query.status = QueryStatus.FAILED
            error_result = QueryResult(
                query_id=query.id,
                success=False,
                error_message=str(e),
                error_code="EXECUTION_FAILED"
            )
            self.results[query.id] = error_result
            logger.error(f"Query {query.id} failed: {str(e)}")
            return error_result
    
    def _get_cached_result(self, query: Query) -> Optional[QueryResult]:
        """Get cached query result"""
        if query.cache_key not in self.cache:
            return None
        
        cache_time = self.cache_timestamps.get(query.cache_key)
        if not cache_time:
            return None
        
        # Check if cache is still valid
        if datetime.utcnow() - cache_time > timedelta(seconds=query.cache_ttl):
            del self.cache[query.cache_key]
            del self.cache_timestamps[query.cache_key]
            return None
        
        cached_data = self.cache[query.cache_key]
        result = QueryResult(
            query_id=query.id,
            success=True,
            data=cached_data['data'],
            total_count=cached_data.get('total_count'),
            page_info=cached_data.get('page_info', {}),
            cache_hit=True,
            executed_at=datetime.utcnow()
        )
        
        logger.debug(f"Cache hit for query {query.id}")
        return result
    
    def _cache_result(self, query: Query, result: QueryResult):
        """Cache query result"""
        self.cache[query.cache_key] = {
            'data': result.data,
            'total_count': result.total_count,
            'page_info': result.page_info
        }
        self.cache_timestamps[query.cache_key] = datetime.utcnow()
    
    def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache entries"""
        if pattern:
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
        else:
            self.cache.clear()
            self.cache_timestamps.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cached_entries': len(self.cache),
            'cache_size_bytes': sum(len(str(v)) for v in self.cache.values()),
            'registered_handlers': len(self.handlers),
            'registered_read_models': len(self.read_models)
        }

class CQRSCore:
    """Core CQRS management system"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.command_bus = CommandBus()
        self.query_bus = QueryBus()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.command_processor_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.metrics = {
            'commands_processed': 0,
            'queries_processed': 0,
            'events_handled': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_execution_time': 0.0
        }
        
        logger.info(f"CQRS Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize CQRS system"""
        try:
            # Register default middleware
            self.command_bus.add_middleware(self._command_middleware)
            self.query_bus.add_middleware(self._query_middleware)
            
            logger.info("CQRS Core initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize CQRS Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start CQRS system"""
        try:
            self.is_running = True
            
            # Start command processor
            self.command_processor_task = asyncio.create_task(self._command_processor())
            
            logger.info("CQRS Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start CQRS Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop CQRS system"""
        try:
            self.is_running = False
            
            # Cancel command processor
            if self.command_processor_task:
                self.command_processor_task.cancel()
                try:
                    await self.command_processor_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("CQRS Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop CQRS Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Check if command processor is running
            if not self.command_processor_task or self.command_processor_task.done():
                if self.is_running:
                    logger.warning("Command processor is not running")
                    return False
            
            # Check queue sizes
            queue_status = self.command_bus.get_queue_status()
            if queue_status['queued_commands'] > 10000:  # Too many pending commands
                logger.warning("Command queue is overloaded")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def _command_middleware(self, command: Command):
        """Default command middleware"""
        # Add correlation ID if not present
        if not command.correlation_id:
            command.correlation_id = str(uuid.uuid4())
        
        # Add metadata
        command.metadata['processed_at'] = datetime.utcnow().isoformat()
        command.metadata['processor'] = 'cqrs_core'
    
    async def _query_middleware(self, query: Query):
        """Default query middleware"""
        # Generate cache key if not present
        if not query.cache_key and query.parameters:
            cache_data = f"{query.query_type}:{json.dumps(query.parameters, sort_keys=True)}"
            query.cache_key = f"query_{hash(cache_data)}"
        
        # Add metadata
        query.metadata['processed_at'] = datetime.utcnow().isoformat()
        query.metadata['processor'] = 'cqrs_core'
    
    async def _command_processor(self):
        """Background command processor"""
        while self.is_running:
            try:
                result = await self.command_bus.execute_next()
                if result:
                    self.metrics['commands_processed'] += 1
                    self.metrics['total_execution_time'] += result.execution_time_ms
                    
                    # Publish events if any were generated
                    for event_id in result.events_generated:
                        await self._publish_event(event_id, result.result_data)
                else:
                    # No commands to process, sleep briefly
                    await asyncio.sleep(0.1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Command processor error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish domain event"""
        try:
            handlers = self.event_handlers.get(event_type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_data)
                    else:
                        handler(event_data)
                    self.metrics['events_handled'] += 1
                except Exception as e:
                    logger.error(f"Event handler error for {event_type}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {str(e)}")
    
    # Public API methods
    def register_command_handler(self, command_type: str, handler: CommandHandler):
        """Register command handler"""
        self.command_bus.register_handler(command_type, handler)
    
    def register_query_handler(self, query_type: str, handler: QueryHandler):
        """Register query handler"""
        self.query_bus.register_handler(query_type, handler)
    
    def register_read_model(self, name: str, read_model: ReadModel):
        """Register read model"""
        self.query_bus.register_read_model(name, read_model)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for: {event_type}")
    
    async def send_command(self, command: Command) -> str:
        """Send command for execution"""
        return await self.command_bus.dispatch(command)
    
    async def send_query(self, query: Query) -> QueryResult:
        """Send query for execution"""
        result = await self.query_bus.dispatch(query)
        self.metrics['queries_processed'] += 1
        self.metrics['total_execution_time'] += result.execution_time_ms
        
        if result.cache_hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
        
        return result
    
    def get_command_result(self, command_id: str) -> Optional[CommandResult]:
        """Get command execution result"""
        return self.command_bus.get_result(command_id)
    
    def clear_query_cache(self, pattern: Optional[str] = None):
        """Clear query cache"""
        self.query_bus.clear_cache(pattern)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        queue_status = self.command_bus.get_queue_status()
        cache_stats = self.query_bus.get_cache_stats()
        
        avg_execution_time = (
            self.metrics['total_execution_time'] / 
            (self.metrics['commands_processed'] + self.metrics['queries_processed'])
            if (self.metrics['commands_processed'] + self.metrics['queries_processed']) > 0 else 0
        )
        
        cache_hit_rate = (
            self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses'])
            if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
        )
        
        return {
            'level': self.level,
            'commands_processed': self.metrics['commands_processed'],
            'queries_processed': self.metrics['queries_processed'],
            'events_handled': self.metrics['events_handled'],
            'avg_execution_time_ms': avg_execution_time,
            'cache_hit_rate': cache_hit_rate,
            'queue_status': queue_status,
            'cache_stats': cache_stats,
            'registered_event_handlers': len(self.event_handlers),
            'is_running': self.is_running
        }

# Global instance
cqrs_core = CQRSCore()

# Convenience functions
async def send_command(command_type: str, data: Dict[str, Any], 
                      user_id: Optional[str] = None,
                      priority: CommandPriority = CommandPriority.NORMAL) -> str:
    """Send command for execution"""
    command = Command(
        command_type=command_type,
        data=data,
        user_id=user_id,
        priority=priority
    )
    return await cqrs_core.send_command(command)

async def send_query(query_type: str, parameters: Dict[str, Any],
                    user_id: Optional[str] = None, cache_ttl: int = 300) -> QueryResult:
    """Send query for execution"""
    query = Query(
        query_type=query_type,
        parameters=parameters,
        user_id=user_id,
        cache_ttl=cache_ttl
    )
    return await cqrs_core.send_query(query)

def register_command_handler(command_type: str, handler: CommandHandler):
    """Register command handler"""
    cqrs_core.register_command_handler(command_type, handler)

def register_query_handler(query_type: str, handler: QueryHandler):
    """Register query handler"""
    cqrs_core.register_query_handler(query_type, handler)

# Module exports
__all__ = [
    "CQRSCore", "Command", "Query", "CommandResult", "QueryResult",
    "CommandHandler", "QueryHandler", "ReadModel", "CommandBus", "QueryBus",
    "CommandStatus", "QueryStatus", "CommandPriority", "cqrs_core",
    "send_command", "send_query", "register_command_handler", "register_query_handler"
]

logger.info("CQRS Core module loaded")