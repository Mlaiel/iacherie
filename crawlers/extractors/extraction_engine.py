"""
Extraction Engine - Core Industrial IA Data Extraction System
============================================================

Ultra-advanced professional extraction engine for multi-platform content processing.
Implements high-performance extraction coordination, AI-powered analysis, and enterprise-grade management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.
"""

import asyncio
import logging
import time
import traceback
from typing import Dict, List, Optional, Any, Union, Callable, Type, AsyncGenerator
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import json
import hashlib
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class ExtractionStatus(Enum):
    """Extraction status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExtractionPriority(Enum):
    """Extraction priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ContentType(Enum):
    """Supported content types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    STRUCTURED = "structured"
    STREAM = "stream"


@dataclass
class ExtractionRequest:
    """Data extraction request specification"""
    
    request_id: str = field(default_factory=lambda: str(uuid4()))
    source_url: Optional[str] = None
    source_path: Optional[str] = None
    source_data: Optional[bytes] = None
    content_type: ContentType = ContentType.TEXT
    platform: Optional[str] = None
    extraction_types: List[str] = field(default_factory=list)
    priority: ExtractionPriority = ExtractionPriority.NORMAL
    timeout: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    proxy: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate request after initialization"""
        if not any([self.source_url, self.source_path, self.source_data]):
            raise ValueError("At least one source must be provided")
        
        if not self.extraction_types:
            self.extraction_types = ["content", "metadata"]


@dataclass  
class ExtractionResult:
    """Data extraction result container"""
    
    request_id: str
    status: ExtractionStatus
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    extraction_time: float = 0.0
    file_size: int = 0
    content_hash: Optional[str] = None
    quality_score: float = 0.0
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        result = asdict(self)
        result['status'] = self.status.value
        if self.completed_at:
            result['completed_at'] = self.completed_at.isoformat()
        return result
    
    def is_successful(self) -> bool:
        """Check if extraction was successful"""
        return self.status == ExtractionStatus.COMPLETED and bool(self.extracted_data)


class BaseExtractor(ABC):
    """Abstract base class for all extractors"""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_time': 0.0
        }
    
    @abstractmethod
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if extractor can handle the request"""
        pass
    
    @abstractmethod
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Perform data extraction"""
        pass
    
    async def validate_request(self, request: ExtractionRequest) -> bool:
        """Validate extraction request"""
        try:
            if not request.request_id:
                return False
            
            if request.timeout <= 0:
                return False
                
            return await self.can_handle(request)
            
        except Exception as e:
            self.logger.error(f"Request validation failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get extractor statistics"""
        stats = self._stats.copy()
        if stats['total_extractions'] > 0:
            stats['success_rate'] = stats['successful_extractions'] / stats['total_extractions']
            stats['average_time'] = stats['total_time'] / stats['total_extractions']
        else:
            stats['success_rate'] = 0.0
            stats['average_time'] = 0.0
        return stats
    
    def _update_stats(self, success: bool, extraction_time: float):
        """Update extractor statistics"""
        self._stats['total_extractions'] += 1
        self._stats['total_time'] += extraction_time
        
        if success:
            self._stats['successful_extractions'] += 1
        else:
            self._stats['failed_extractions'] += 1


class ExtractionEngine:
    """High-performance data extraction engine"""
    
    def __init__(self, 
                 max_workers: int = 10,
                 max_concurrent_extractions: int = 50,
                 default_timeout: int = 300):
        
        self.max_workers = max_workers
        self.max_concurrent_extractions = max_concurrent_extractions
        self.default_timeout = default_timeout
        
        # Core components
        self._extractors: Dict[str, BaseExtractor] = {}
        self._active_extractions: Dict[str, asyncio.Task] = {}
        self._extraction_queue = asyncio.Queue()
        self._results_cache: Dict[str, ExtractionResult] = {}
        
        # Thread pool for CPU-intensive tasks
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # Coordination primitives
        self._semaphore = asyncio.Semaphore(max_concurrent_extractions)
        self._shutdown_event = asyncio.Event()
        self._worker_tasks: List[asyncio.Task] = []
        
        # Metrics and monitoring
        self._metrics = {
            'total_requests': 0,
            'completed_requests': 0,
            'failed_requests': 0,
            'queued_requests': 0,
            'active_extractions': 0,
            'total_extraction_time': 0.0
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Extraction engine initialized with {max_workers} workers")
    
    async def start(self):
        """Start the extraction engine"""
        self.logger.info("Starting extraction engine...")
        
        # Start worker tasks
        for i in range(self.max_workers):
            task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self._worker_tasks.append(task)
        
        self.logger.info(f"Started {len(self._worker_tasks)} worker tasks")
    
    async def stop(self):
        """Stop the extraction engine"""
        self.logger.info("Stopping extraction engine...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel all active extractions
        for task in self._active_extractions.values():
            task.cancel()
        
        # Wait for workers to finish
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        
        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True)
        
        self.logger.info("Extraction engine stopped")
    
    def register_extractor(self, extractor: BaseExtractor, name: Optional[str] = None):
        """Register a data extractor"""
        extractor_name = name or extractor.name
        self._extractors[extractor_name] = extractor
        self.logger.info(f"Registered extractor: {extractor_name}")
    
    def unregister_extractor(self, name: str):
        """Unregister a data extractor"""
        if name in self._extractors:
            del self._extractors[name]
            self.logger.info(f"Unregistered extractor: {name}")
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Submit extraction request and wait for result"""
        
        # Update metrics
        self._metrics['total_requests'] += 1
        
        # Check cache first
        cache_key = self._generate_cache_key(request)
        if cache_key in self._results_cache:
            cached_result = self._results_cache[cache_key]
            self.logger.debug(f"Returning cached result for {request.request_id}")
            return cached_result
        
        try:
            # Find suitable extractor
            extractor = await self._find_extractor(request)
            if not extractor:
                return ExtractionResult(
                    request_id=request.request_id,
                    status=ExtractionStatus.FAILED,
                    errors=["No suitable extractor found"]
                )
            
            # Perform extraction
            start_time = time.time()
            
            async with self._semaphore:
                self._metrics['active_extractions'] += 1
                
                try:
                    result = await asyncio.wait_for(
                        extractor.extract(request),
                        timeout=request.timeout
                    )
                    
                    # Update result timing
                    result.extraction_time = time.time() - start_time
                    result.completed_at = datetime.utcnow()
                    
                    # Cache successful results
                    if result.is_successful():
                        self._results_cache[cache_key] = result
                        self._metrics['completed_requests'] += 1
                    else:
                        self._metrics['failed_requests'] += 1
                    
                    return result
                    
                except asyncio.TimeoutError:
                    self.logger.warning(f"Extraction timeout for {request.request_id}")
                    return ExtractionResult(
                        request_id=request.request_id,
                        status=ExtractionStatus.TIMEOUT,
                        errors=[f"Extraction timed out after {request.timeout}s"]
                    )
                
                finally:
                    self._metrics['active_extractions'] -= 1
                    self._metrics['total_extraction_time'] += time.time() - start_time
        
        except Exception as e:
            self.logger.error(f"Extraction failed for {request.request_id}: {e}")
            self._metrics['failed_requests'] += 1
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                errors=[str(e)]
            )
    
    async def extract_async(self, request: ExtractionRequest) -> str:
        """Submit extraction request for asynchronous processing"""
        
        # Add to queue
        await self._extraction_queue.put(request)
        self._metrics['queued_requests'] += 1
        
        self.logger.info(f"Queued extraction request: {request.request_id}")
        return request.request_id
    
    async def get_result(self, request_id: str) -> Optional[ExtractionResult]:
        """Get result of asynchronous extraction"""
        
        # Check active extractions
        if request_id in self._active_extractions:
            task = self._active_extractions[request_id]
            if task.done():
                try:
                    return await task
                except Exception as e:
                    return ExtractionResult(
                        request_id=request_id,
                        status=ExtractionStatus.FAILED,
                        errors=[str(e)]
                    )
            else:
                return ExtractionResult(
                    request_id=request_id,
                    status=ExtractionStatus.RUNNING
                )
        
        # Check cache
        for result in self._results_cache.values():
            if result.request_id == request_id:
                return result
        
        return None
    
    async def _worker_loop(self, worker_name: str):
        """Main worker loop for processing extraction queue"""
        
        self.logger.info(f"Worker {worker_name} started")
        
        while not self._shutdown_event.is_set():
            try:
                # Wait for request with timeout
                request = await asyncio.wait_for(
                    self._extraction_queue.get(),
                    timeout=1.0
                )
                
                self._metrics['queued_requests'] -= 1
                
                # Create extraction task
                task = asyncio.create_task(self.extract(request))
                self._active_extractions[request.request_id] = task
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {e}")
        
        self.logger.info(f"Worker {worker_name} stopped")
    
    async def _find_extractor(self, request: ExtractionRequest) -> Optional[BaseExtractor]:
        """Find suitable extractor for request"""
        
        for extractor in self._extractors.values():
            try:
                if await extractor.can_handle(request):
                    return extractor
            except Exception as e:
                self.logger.warning(f"Extractor check failed: {e}")
        
        return None
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed extraction tasks"""
        
        completed_ids = []
        for request_id, task in self._active_extractions.items():
            if task.done():
                completed_ids.append(request_id)
        
        for request_id in completed_ids:
            del self._active_extractions[request_id]
    
    def _generate_cache_key(self, request: ExtractionRequest) -> str:
        """Generate cache key for request"""
        
        # Create unique identifier from request components
        key_data = {
            'source_url': request.source_url,
            'source_path': request.source_path,
            'content_type': request.content_type.value,
            'platform': request.platform,
            'extraction_types': sorted(request.extraction_types)
        }
        
        # Add source_data hash if present
        if request.source_data:
            key_data['source_data_hash'] = hashlib.md5(request.source_data).hexdigest()
        
        # Generate hash
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive engine metrics and performance data"""
        metrics = self._metrics.copy()
        metrics['queue_size'] = self._extraction_queue.qsize()
        metrics['active_tasks'] = len(self._active_extractions)
        metrics['registered_extractors'] = len(self._extractors)
        metrics['cache_size'] = len(self._results_cache)
        metrics['cache_hit_rate'] = self._calculate_cache_hit_rate()
        
        if metrics['completed_requests'] > 0:
            metrics['average_extraction_time'] = (
                metrics['total_extraction_time'] / metrics['completed_requests']
            )
            metrics['success_rate'] = (
                metrics['successful_requests'] / metrics['completed_requests']
            )
        else:
            metrics['average_extraction_time'] = 0.0
            metrics['success_rate'] = 0.0
        
        # Performance analytics
        metrics['throughput_per_minute'] = self._calculate_throughput()
        metrics['error_rate'] = self._calculate_error_rate()
        metrics['resource_utilization'] = self._get_resource_utilization()
        
        return metrics
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total_requests = self._metrics.get('total_requests', 0)
        cache_hits = self._metrics.get('cache_hits', 0)
        return (cache_hits / total_requests * 100) if total_requests > 0 else 0.0
    
    def _calculate_throughput(self) -> float:
        """Calculate requests throughput per minute"""
        if not hasattr(self, '_start_time'):
            return 0.0
        
        uptime_minutes = (datetime.utcnow() - self._start_time).total_seconds() / 60
        completed = self._metrics.get('completed_requests', 0)
        return completed / uptime_minutes if uptime_minutes > 0 else 0.0
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        total = self._metrics.get('total_requests', 0)
        failed = self._metrics.get('failed_requests', 0)
        return (failed / total * 100) if total > 0 else 0.0
    
    def _get_resource_utilization(self) -> Dict[str, float]:
        """Get current resource utilization metrics"""
        return {
            'cpu_usage': self._get_cpu_usage(),
            'memory_usage': self._get_memory_usage(),
            'active_threads': threading.active_count(),
            'queue_utilization': (self._extraction_queue.qsize() / 1000) * 100
        }
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0
    
    def get_extractor_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive statistics for all registered extractors"""
        stats = {}
        for name, extractor in self._extractors.items():
            extractor_stats = extractor.get_stats()
            extractor_stats['supported_types'] = getattr(extractor, 'supported_types', [])
            extractor_stats['last_used'] = getattr(extractor, '_last_used', None)
            stats[name] = extractor_stats
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': (datetime.utcnow() - self._start_time).total_seconds(),
            'checks': {}
        }
        
        # Check queue health
        queue_size = self._extraction_queue.qsize()
        health_status['checks']['queue'] = {
            'status': 'healthy' if queue_size < 1000 else 'warning',
            'size': queue_size,
            'max_capacity': 1000
        }
        
        # Check active tasks
        active_tasks = len(self._active_extractions)
        health_status['checks']['tasks'] = {
            'status': 'healthy' if active_tasks < self.max_concurrent_extractions else 'warning',
            'active': active_tasks,
            'max_concurrent': self.max_concurrent_extractions
        }
        
        # Check extractors
        extractor_health = {}
        for name, extractor in self._extractors.items():
            try:
                # Test extractor responsiveness
                test_request = ExtractionRequest(
                    source_data=b"test",
                    content_type=ContentType.TEXT
                )
                can_handle = await extractor.can_handle(test_request)
                extractor_health[name] = {
                    'status': 'healthy' if can_handle else 'degraded',
                    'responsive': True
                }
            except Exception as e:
                extractor_health[name] = {
                    'status': 'unhealthy',
                    'responsive': False,
                    'error': str(e)
                }
        
        health_status['checks']['extractors'] = extractor_health
        
        # Overall health determination
        unhealthy_checks = [
            check for check in [
                health_status['checks']['queue'],
                health_status['checks']['tasks']
            ] + list(extractor_health.values())
            if check['status'] == 'unhealthy'
        ]
        
        if unhealthy_checks:
            health_status['status'] = 'unhealthy'
        elif any(check['status'] == 'warning' or check['status'] == 'degraded' 
                for check in [health_status['checks']['queue'], health_status['checks']['tasks']] + list(extractor_health.values())):
            health_status['status'] = 'degraded'
        
        return health_status
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Perform automatic performance optimization"""
        optimization_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'actions_taken': [],
            'performance_improvement': {}
        }
        
        # Clear old cache entries
        cache_cleared = await self._cleanup_cache()
        if cache_cleared > 0:
            optimization_results['actions_taken'].append(f"Cleared {cache_cleared} old cache entries")
        
        # Cleanup completed tasks
        cleaned_tasks = self._cleanup_completed_tasks()
        if cleaned_tasks > 0:
            optimization_results['actions_taken'].append(f"Cleaned up {cleaned_tasks} completed tasks")
        
        # Optimize queue if needed
        if self._extraction_queue.qsize() > 500:
            await self._optimize_queue()
            optimization_results['actions_taken'].append("Optimized extraction queue")
        
        # Memory cleanup
        import gc
        collected = gc.collect()
        if collected > 0:
            optimization_results['actions_taken'].append(f"Garbage collected {collected} objects")
        
        return optimization_results
    
    async def _cleanup_cache(self) -> int:
        """Clean up old cache entries"""
        current_time = datetime.utcnow()
        cache_ttl = timedelta(hours=24)  # 24 hour TTL
        
        expired_keys = [
            key for key, result in self._results_cache.items()
            if result.completed_at and (current_time - result.completed_at) > cache_ttl
        ]
        
        for key in expired_keys:
            del self._results_cache[key]
        
        return len(expired_keys)
    
    def _cleanup_completed_tasks(self) -> int:
        """Clean up completed async tasks"""
        completed_tasks = [
            request_id for request_id, task in self._active_extractions.items()
            if task.done()
        ]
        
        for request_id in completed_tasks:
            del self._active_extractions[request_id]
        
        return len(completed_tasks)
    
    async def _optimize_queue(self):
        """Optimize extraction queue by reordering high-priority items"""
        queue_items = []
        
        # Extract all items from queue
        while not self._extraction_queue.empty():
            try:
                item = self._extraction_queue.get_nowait()
                queue_items.append(item)
            except asyncio.QueueEmpty:
                break
        
        # Sort by priority (highest first)
        queue_items.sort(key=lambda x: x.priority.value, reverse=True)
        
        # Put items back in queue
        for item in queue_items:
            await self._extraction_queue.put(item)
    
    @asynccontextmanager
    async def extraction_context(self):
        """Context manager for engine lifecycle with proper resource management"""
        self._start_time = datetime.utcnow()
        await self.start()
        try:
            yield self
        finally:
            await self.stop()

    async def export_metrics(self, format_type: str = "json") -> Union[Dict, str]:
        """Export comprehensive metrics in various formats"""
        metrics_data = {
            'engine_metrics': self.get_metrics(),
            'extractor_stats': self.get_extractor_stats(),
            'health_status': await self.health_check(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if format_type.lower() == "json":
            return metrics_data
        elif format_type.lower() == "csv":
            return self._export_to_csv(metrics_data)
        elif format_type.lower() == "prometheus":
            return self._export_to_prometheus(metrics_data)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_to_csv(self, metrics_data: Dict) -> str:
        """Export metrics to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['metric_name', 'value', 'category', 'timestamp'])
        
        # Write engine metrics
        for key, value in metrics_data['engine_metrics'].items():
            if isinstance(value, (int, float)):
                writer.writerow([key, value, 'engine', metrics_data['timestamp']])
        
        # Write extractor stats
        for extractor_name, stats in metrics_data['extractor_stats'].items():
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    writer.writerow([f"{extractor_name}_{key}", value, 'extractor', metrics_data['timestamp']])
        
        return output.getvalue()
    
    def _export_to_prometheus(self, metrics_data: Dict) -> str:
        """Export metrics to Prometheus format"""
        lines = []
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        
        # Engine metrics
        for key, value in metrics_data['engine_metrics'].items():
            if isinstance(value, (int, float)):
                lines.append(f"extraction_engine_{key} {value} {timestamp}")
        
        # Extractor metrics
        for extractor_name, stats in metrics_data['extractor_stats'].items():
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    lines.append(f'extractor_{key}{{extractor="{extractor_name}"}} {value} {timestamp}')
        
        return '\n'.join(lines)

    async def create_extraction_pipeline(self, 
                                       requests: List[ExtractionRequest],
                                       pipeline_id: str = None) -> Dict[str, Any]:
        """Create and execute a pipeline of related extractions"""
        pipeline_id = pipeline_id or str(uuid4())
        
        pipeline_results = {
            'pipeline_id': pipeline_id,
            'total_requests': len(requests),
            'completed': 0,
            'failed': 0,
            'results': {},
            'start_time': datetime.utcnow(),
            'end_time': None,
            'duration': None
        }
        
        try:
            # Execute all requests concurrently
            tasks = []
            for request in requests:
                request.metadata['pipeline_id'] = pipeline_id
                task = asyncio.create_task(self.extract(request))
                tasks.append((request.request_id, task))
            
            # Wait for all tasks to complete
            for request_id, task in tasks:
                try:
                    result = await task
                    pipeline_results['results'][request_id] = result.to_dict()
                    
                    if result.is_successful():
                        pipeline_results['completed'] += 1
                    else:
                        pipeline_results['failed'] += 1
                        
                except Exception as e:
                    pipeline_results['failed'] += 1
                    pipeline_results['results'][request_id] = {
                        'status': 'failed',
                        'error': str(e)
                    }
            
            pipeline_results['end_time'] = datetime.utcnow()
            pipeline_results['duration'] = (
                pipeline_results['end_time'] - pipeline_results['start_time']
            ).total_seconds()
            
            return pipeline_results
            
        except Exception as e:
            self.logger.error(f"Pipeline {pipeline_id} failed: {e}")
            pipeline_results['end_time'] = datetime.utcnow()
            pipeline_results['error'] = str(e)
            return pipeline_results

    def __del__(self):
        """Cleanup on object destruction"""
        try:
            # Cancel any running tasks
            for task in self._active_extractions.values():
                if not task.done():
                    task.cancel()
        except Exception:
            pass  # Ignore cleanup errors during destruction


# Factory functions for common extraction scenarios
async def create_content_extraction_engine() -> ExtractionEngine:
    """Factory function to create a content-focused extraction engine"""
    engine = ExtractionEngine(
        max_workers=20,
        max_concurrent_extractions=100,
        default_timeout=600
    )
    
    # Register content extractors here
    # This would be done by the main application
    return engine


async def create_realtime_extraction_engine() -> ExtractionEngine:
    """Factory function to create a real-time extraction engine"""
    engine = ExtractionEngine(
        max_workers=50,
        max_concurrent_extractions=200,
        default_timeout=30
    )
    
    return engine


async def create_batch_extraction_engine() -> ExtractionEngine:
    """Factory function to create a batch processing extraction engine"""
    engine = ExtractionEngine(
        max_workers=10,
        max_concurrent_extractions=500,
        default_timeout=1800  # 30 minutes
    )
    
    return engine
