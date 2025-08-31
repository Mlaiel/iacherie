"""Parser Manager Module
====================

Centralized management system for all parser operations and orchestration.
Provides high-level interface for parsing workflows and batch operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import traceback

from .parser_factory import ParserFactory, ParserType, ParserCategory
from .parser_config import ParserConfig
from .exceptions import ParserManagerError, ParsingError, ValidationError


class ParseStatus(Enum):
    """Status of parsing operations"""    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ParsePriority(Enum):
    """Priority levels for parsing operations"""    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ParseTask:
    """Represents a parsing task"""    task_id: str
    parser_type: Union[ParserType, str]
    content_path: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: ParsePriority = ParsePriority.NORMAL
    status: ParseStatus = ParseStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ParseResult:
    """Result of a parsing operation"""    task_id: str
    parser_type: str
    status: ParseStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ParserManager:
    """Centralized manager for all parser operations"""    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.factory = ParserFactory(config)
        self.logger = logging.getLogger(__name__)
        
        # Task management
        self._tasks: Dict[str, ParseTask] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._task_counter = 0
        
        # Configuration
        self._max_concurrent_tasks = config.performance.max_concurrent_parsers
        self._default_timeout = config.performance.timeout_seconds
        
        # Callbacks
        self._callbacks: Dict[str, List[Callable]] = {
            'task_started': [],
            'task_completed': [],
            'task_failed': [],
            'task_cancelled': []
        }
        
        # Statistics
        self._stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'cancelled_tasks': 0,
            'average_duration': 0.0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""        await self.shutdown()
    
    def generate_task_id(self) -> str:
        """Generate unique task ID"""        self._task_counter += 1
        return f"parse_task_{self._task_counter}_{int(datetime.now().timestamp())}"
    
    async def parse_single(
        self,
        parser_type: Union[ParserType, str],
        content_path: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> ParseResult:
        """Parse single content item"""        try:
            # Create task
            task_id = self.generate_task_id()
            task = ParseTask(
                task_id=task_id,
                parser_type=parser_type,
                content_path=content_path,
                parameters=parameters or {},
                priority=ParsePriority.NORMAL
            )
            
            # Execute immediately
            result = await self._execute_task(task, timeout or self._default_timeout)
            return result
            
        except Exception as e:
            self.logger.error(f"Single parse failed: {str(e)}")
            return ParseResult(
                task_id="immediate",
                parser_type=str(parser_type),
                status=ParseStatus.FAILED,
                error=str(e)
            )
    
    async def parse_batch(
        self,
        parse_requests: List[Dict[str, Any]],
        max_concurrent: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> List[ParseResult]:
        """Parse multiple content items in batch"""        try:
            # Create tasks
            tasks = []
            for request in parse_requests:
                task_id = self.generate_task_id()
                task = ParseTask(
                    task_id=task_id,
                    parser_type=request['parser_type'],
                    content_path=request['content_path'],
                    parameters=request.get('parameters', {}),
                    priority=ParsePriority(request.get('priority', ParsePriority.NORMAL.value))
                )
                tasks.append(task)
            
            # Execute batch
            results = await self._execute_batch(
                tasks,
                max_concurrent or self._max_concurrent_tasks,
                timeout or self._default_timeout
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Batch parse failed: {str(e)}")
            raise ParserManagerError(f"Batch parsing failed: {str(e)}")
    
    async def queue_task(
        self,
        parser_type: Union[ParserType, str],
        content_path: str,
        parameters: Optional[Dict[str, Any]] = None,
        priority: ParsePriority = ParsePriority.NORMAL
    ) -> str:
        """Queue a parsing task for later execution"""        try:
            task_id = self.generate_task_id()
            task = ParseTask(
                task_id=task_id,
                parser_type=parser_type,
                content_path=content_path,
                parameters=parameters or {},
                priority=priority
            )
            
            self._tasks[task_id] = task
            self._stats['total_tasks'] += 1
            
            self.logger.info(f"Task queued: {task_id}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to queue task: {str(e)}")
            raise ParserManagerError(f"Failed to queue task: {str(e)}")
    
    async def execute_queued_tasks(
        self,
        max_concurrent: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> List[ParseResult]:
        """Execute all queued tasks"""        try:
            # Get pending tasks sorted by priority
            pending_tasks = [
                task for task in self._tasks.values()
                if task.status == ParseStatus.PENDING
            ]
            
            pending_tasks.sort(key=lambda t: t.priority.value, reverse=True)
            
            if not pending_tasks:
                return []
            
            # Execute tasks
            results = await self._execute_batch(
                pending_tasks,
                max_concurrent or self._max_concurrent_tasks,
                timeout or self._default_timeout
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to execute queued tasks: {str(e)}")
            raise ParserManagerError(f"Failed to execute queued tasks: {str(e)}")
    
    async def _execute_task(self, task: ParseTask, timeout: float) -> ParseResult:
        """Execute a single parsing task"""        start_time = datetime.now(timezone.utc)
        
        try:
            # Update task status
            task.status = ParseStatus.RUNNING
            task.started_at = start_time
            
            # Trigger callback
            await self._trigger_callback('task_started', task)
            
            # Create parser
            parser = self.factory.create_parser(task.parser_type)
            
            # Execute parsing with timeout
            async with parser:
                result_data = await asyncio.wait_for(
                    self._call_parser_method(parser, task),
                    timeout=timeout
                )
            
            # Calculate duration
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            # Update task
            task.status = ParseStatus.COMPLETED
            task.completed_at = end_time
            task.result = result_data
            
            # Update statistics
            self._stats['completed_tasks'] += 1
            self._update_average_duration(duration)
            
            # Create result
            result = ParseResult(
                task_id=task.task_id,
                parser_type=str(task.parser_type),
                status=ParseStatus.COMPLETED,
                result=result_data,
                duration=duration,
                metadata={
                    'started_at': start_time.isoformat(),
                    'completed_at': end_time.isoformat(),
                    'retry_count': task.retry_count
                }
            )
            
            # Trigger callback
            await self._trigger_callback('task_completed', task, result)
            
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Task timeout after {timeout} seconds"
            return await self._handle_task_error(task, error_msg, start_time)
            
        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            return await self._handle_task_error(task, error_msg, start_time)
    
    async def _handle_task_error(self, task: ParseTask, error_msg: str, start_time: datetime) -> ParseResult:
        """Handle task execution error"""        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        self.logger.error(f"Task {task.task_id} failed: {error_msg}")
        
        # Check if should retry
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = ParseStatus.PENDING
            task.error = None
            
            self.logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count + 1})")
            
            # Retry with exponential backoff
            await asyncio.sleep(2 ** task.retry_count)
            return await self._execute_task(task, self._default_timeout)
        
        # Mark as failed
        task.status = ParseStatus.FAILED
        task.completed_at = end_time
        task.error = error_msg
        
        # Update statistics
        self._stats['failed_tasks'] += 1
        
        # Create result
        result = ParseResult(
            task_id=task.task_id,
            parser_type=str(task.parser_type),
            status=ParseStatus.FAILED,
            error=error_msg,
            duration=duration,
            metadata={
                'started_at': start_time.isoformat(),
                'failed_at': end_time.isoformat(),
                'retry_count': task.retry_count
            }
        )
        
        # Trigger callback
        await self._trigger_callback('task_failed', task, result)
        
        return result
    
    async def _execute_batch(self, tasks: List[ParseTask], max_concurrent: int, timeout: float) -> List[ParseResult]:
        """Execute batch of tasks with concurrency control"""        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(task: ParseTask) -> ParseResult:
            async with semaphore:
                return await self._execute_task(task, timeout)
        
        # Create coroutines
        coroutines = [execute_with_semaphore(task) for task in tasks]
        
        # Execute with gather
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exception
                task = tasks[i]
                error_result = ParseResult(
                    task_id=task.task_id,
                    parser_type=str(task.parser_type),
                    status=ParseStatus.FAILED,
                    error=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _call_parser_method(self, parser: Any, task: ParseTask) -> Dict[str, Any]:
        """Call the appropriate parser method based on parser type"""        parser_type_str = str(task.parser_type)
        
        if 'platform' in parser_type_str:
            return await parser.parse_platform_content(task.content_path, **task.parameters)
        elif 'media' in parser_type_str:
            return await parser.parse_media_file(task.content_path, **task.parameters)
        elif 'metadata' in parser_type_str:
            return await parser.parse_metadata(task.content_path, **task.parameters)
        elif 'content' in parser_type_str:
            return await parser.parse_content(task.content_path, **task.parameters)
        elif 'analytics' in parser_type_str:
            return await parser.parse_analytics(**task.parameters)
        elif 'engagement' in parser_type_str:
            return await parser.parse_engagement(task.content_path, **task.parameters)
        elif 'revenue' in parser_type_str:
            return await parser.parse_revenue(**task.parameters)
        elif 'fingerprint' in parser_type_str:
            return await parser.parse_for_fingerprint(task.content_path, **task.parameters)
        else:
            # Default method
            if hasattr(parser, 'parse'):
                return await parser.parse(task.content_path, **task.parameters)
            else:
                raise ParserManagerError(f"No suitable parse method found for parser type: {parser_type_str}")
    
    def get_task_status(self, task_id: str) -> Optional[ParseTask]:
        """Get status of a specific task"""        return self._tasks.get(task_id)
    
    def get_all_tasks(self, status_filter: Optional[ParseStatus] = None) -> List[ParseTask]:
        """Get all tasks, optionally filtered by status"""        tasks = list(self._tasks.values())
        
        if status_filter:
            tasks = [task for task in tasks if task.status == status_filter]
        
        return tasks
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics"""        return {
            **self._stats,
            'pending_tasks': len([t for t in self._tasks.values() if t.status == ParseStatus.PENDING]),
            'running_tasks': len([t for t in self._tasks.values() if t.status == ParseStatus.RUNNING]),
            'total_queued': len(self._tasks)
        }
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for parser events"""        if event in self._callbacks:
            self._callbacks[event].append(callback)
        else:
            raise ValueError(f"Unknown event type: {event}")
    
    async def _trigger_callback(self, event: str, *args):
        """Trigger callbacks for an event"""        for callback in self._callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args)
                else:
                    callback(*args)
            except Exception as e:
                self.logger.error(f"Callback error for {event}: {str(e)}")
    
    def _update_average_duration(self, duration: float):
        """Update average task duration"""        completed = self._stats['completed_tasks']
        if completed == 1:
            self._stats['average_duration'] = duration
        else:
            # Running average
            current_avg = self._stats['average_duration']
            self._stats['average_duration'] = (current_avg * (completed - 1) + duration) / completed
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a queued or running task"""        try:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            if task.status == ParseStatus.PENDING:
                task.status = ParseStatus.CANCELLED
                self._stats['cancelled_tasks'] += 1
                await self._trigger_callback('task_cancelled', task)
                return True
            
            if task.status == ParseStatus.RUNNING and task_id in self._running_tasks:
                running_task = self._running_tasks[task_id]
                running_task.cancel()
                task.status = ParseStatus.CANCELLED
                self._stats['cancelled_tasks'] += 1
                await self._trigger_callback('task_cancelled', task)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False
    
    def clear_completed_tasks(self):
        """Clear completed and failed tasks from memory"""        to_remove = [
            task_id for task_id, task in self._tasks.items()
            if task.status in [ParseStatus.COMPLETED, ParseStatus.FAILED, ParseStatus.CANCELLED]
        ]
        
        for task_id in to_remove:
            del self._tasks[task_id]
        
        self.logger.info(f"Cleared {len(to_remove)} completed tasks")
    
    async def shutdown(self):
        """Shutdown the parser manager"""        try:
            # Cancel all running tasks
            for task_id, running_task in self._running_tasks.items():
                running_task.cancel()
            
            # Wait for tasks to complete
            if self._running_tasks:
                await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)
            
            # Clear factory cache
            self.factory.clear_cache()
            
            self.logger.info("Parser manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
    
    async def validate_content(self, content_path: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
        """Validate content before parsing"""        try:
            import os
            from pathlib import Path
            
            if not os.path.exists(content_path):
                raise ValidationError(f"Content not found: {content_path}")
            
            file_path = Path(content_path)
            file_stats = os.stat(content_path)
            
            validation_result = {
                'valid': True,
                'file_size': file_stats.st_size,
                'file_extension': file_path.suffix.lower(),
                'is_file': file_path.is_file(),
                'is_readable': os.access(content_path, os.R_OK),
                'auto_detected_type': None,
                'warnings': []
            }
            
            # Auto-detect parser type
            content_info = {
                'file_extension': file_path.suffix.lower(),
                'mime_type': self._get_mime_type(content_path)
            }
            
            auto_type = self.factory.auto_detect_parser_type(content_info)
            if auto_type:
                validation_result['auto_detected_type'] = auto_type.value
            
            # Size warnings
            if file_stats.st_size > 100 * 1024 * 1024:  # 100MB
                validation_result['warnings'].append("Large file size may impact performance")
            
            if file_stats.st_size == 0:
                validation_result['warnings'].append("Empty file")
            
            # Type validation
            if expected_type and auto_type:
                if str(auto_type.value) != expected_type:
                    validation_result['warnings'].append(
                        f"Expected type {expected_type} but detected {auto_type.value}"
                    )
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'warnings': []
            }
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type of file"""        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    
    async def get_parser_capabilities(self) -> Dict[str, Any]:
        """Get information about parser capabilities"""        return {
            'available_parsers': [pt.value for pt in self.factory.get_available_parser_types()],
            'categories': [cat.value for cat in self.factory.get_categories()],
            'factory_info': self.factory.get_cache_info(),
            'manager_config': {
                'max_concurrent_tasks': self._max_concurrent_tasks,
                'default_timeout': self._default_timeout,
                'max_retries': 3
            }
        }
    
    async def parse_with_auto_detection(
        self,
        content_path: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> ParseResult:
        """Parse content with automatic parser type detection"""        try:
            # Validate content
            validation = await self.validate_content(content_path)
            
            if not validation['valid']:
                return ParseResult(
                    task_id="auto_detect",
                    parser_type="unknown",
                    status=ParseStatus.FAILED,
                    error=validation.get('error', 'Validation failed')
                )
            
            # Auto-detect parser type
            auto_type = validation.get('auto_detected_type')
            if not auto_type:
                return ParseResult(
                    task_id="auto_detect",
                    parser_type="unknown",
                    status=ParseStatus.FAILED,
                    error="Could not auto-detect parser type"
                )
            
            # Parse with detected type
            result = await self.parse_single(auto_type, content_path, parameters, timeout)
            result.metadata['auto_detected'] = True
            result.metadata['detection_info'] = validation
            
            return result
            
        except Exception as e:
            return ParseResult(
                task_id="auto_detect",
                parser_type="unknown",
                status=ParseStatus.FAILED,
                error=f"Auto-detection failed: {str(e)}"
            )
