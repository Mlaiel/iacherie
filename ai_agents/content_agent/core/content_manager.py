"""Content Agent Manager - Orchestrates Content Processing Operations

Manages the content agent lifecycle, configurations, and provides high-level interfaces
for content processing operations across multiple formats.

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import json

from .content_agent import ContentAgent
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import AgentManagerError, ContentProcessingError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    AgentManagerError, ContentProcessingError = globals().get('AgentManagerError, ContentProcessingError', Exception)
from ...database.models import ContentAnalysis, ProcessingJob
from ...tasks.content_tasks import process_content_async, batch_process_content
from ...utils.cache_utils import CacheManager
from ...monitoring.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class ContentAgentManager:
    """    High-level manager for content processing operations.
    
    Responsibilities:
    - Agent lifecycle management
    - Batch processing coordination
    - Result caching and storage
    - Performance monitoring
    - Error handling and recovery
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.agent = None
        self.cache_manager = CacheManager(namespace="content_agent")
        self.metrics = MetricsCollector("content_agent")
        self.processing_jobs = {}
        self.is_initialized = False
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for content agent"""        return {
            'max_file_size_mb': 500,
            'supported_formats': {
                'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
                'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
                'image': ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'],
                'text': ['.txt', '.md', '.html', '.json', '.xml', '.csv']
            },
            'default_analysis_options': ['basic', 'quality', 'metadata'],
            'cache_ttl_hours': 24,
            'batch_size': 10,
            'max_concurrent_jobs': 5
        }
    
    async def initialize(self):
        """Initialize the content agent manager"""        try:
            # Initialize the content agent
            self.agent = ContentAgent(config=self.config)
            await self.agent.initialize()
            
            # Initialize cache manager
            await self.cache_manager.initialize()
            
            # Initialize metrics collector
            self.metrics.start_collecting()
            
            self.is_initialized = True
            logger.info("Content Agent Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Content Agent Manager: {e}")
            raise AgentManagerError(f"Initialization failed: {e}")
    
    def get_agent(self) -> ContentAgent:
        """Get the managed content agent instance"""        if not self.is_initialized:
            raise AgentManagerError("Manager not initialized")
        return self.agent
    
    async def process_content(
        self, 
        content_path: Union[str, Path],
        analysis_options: Optional[List[str]] = None,
        optimization_options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        store_results: bool = True
    ) -> Dict[str, Any]:
        """        Process single content file with advanced options.
        
        Args:
            content_path: Path to content file
            analysis_options: Types of analysis to perform
            optimization_options: Optimization settings
            metadata: Additional metadata
            use_cache: Whether to use cached results
            store_results: Whether to store results in database
        
        Returns:
            Dictionary with analysis results
        """        if not self.is_initialized:
            await self.initialize()
        
        content_path = Path(content_path)
        
        # Generate cache key
        cache_key = self._generate_cache_key(content_path, analysis_options)
        
        # Check cache first
        if use_cache:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Using cached results for {content_path}")
                return cached_result
        
        # Validate file
        if not await self._validate_content_file(content_path):
            raise ContentProcessingError(f"Invalid content file: {content_path}")
        
        # Prepare request
        request_data = {
            'content_path': str(content_path),
            'analysis_options': analysis_options or self.config['default_analysis_options'],
            'optimization_options': optimization_options or {},
            'metadata': metadata or {}
        }
        
        # Process content
        start_time = datetime.utcnow()
        try:
            result = await self.agent.process(request_data)
            
            if result.success:
                # Cache results
                if use_cache:
                    await self.cache_manager.set(
                        cache_key, 
                        result.data, 
                        ttl_hours=self.config['cache_ttl_hours']
                    )
                
                # Store results in database
                if store_results:
                    await self._store_analysis_result(content_path, result.data)
                
                # Update metrics
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                self.metrics.record_processing_time(processing_time)
                self.metrics.increment_counter('successful_processing')
                
                logger.info(f"Successfully processed content: {content_path}")
                return result.data
            else:
                self.metrics.increment_counter('failed_processing')
                raise ContentProcessingError(f"Processing failed: {result.error}")
                
        except Exception as e:
            self.metrics.increment_counter('failed_processing')
            logger.error(f"Content processing error for {content_path}: {e}")
            raise
    
    async def batch_process_content(
        self,
        content_paths: List[Union[str, Path]],
        analysis_options: Optional[List[str]] = None,
        optimization_options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_workers: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """        Process multiple content files in parallel.
        
        Args:
            content_paths: List of content file paths
            analysis_options: Types of analysis to perform
            optimization_options: Optimization settings
            metadata: Additional metadata
            max_workers: Maximum parallel workers
        
        Returns:
            Dictionary mapping file paths to analysis results
        """        if not self.is_initialized:
            await self.initialize()
        
        max_workers = max_workers or self.config['max_concurrent_jobs']
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_single(content_path):
            async with semaphore:
                try:
                    return await self.process_content(
                        content_path,
                        analysis_options,
                        optimization_options,
                        metadata
                    )
                except Exception as e:
                    logger.error(f"Batch processing error for {content_path}: {e}")
                    return {'error': str(e)}
        
        # Create processing tasks
        tasks = []
        for content_path in content_paths:
            task = asyncio.create_task(process_single(content_path))
            tasks.append((str(content_path), task))
        
        # Wait for all tasks to complete
        results = {}
        for content_path, task in tasks:
            try:
                result = await task
                results[content_path] = result
            except Exception as e:
                results[content_path] = {'error': str(e)}
        
        logger.info(f"Batch processed {len(content_paths)} files")
        return results
    
    async def schedule_processing_job(
        self,
        job_id: str,
        content_paths: List[Union[str, Path]],
        analysis_options: Optional[List[str]] = None,
        optimization_options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: int = 1
    ) -> str:
        """        Schedule a background processing job.
        
        Args:
            job_id: Unique job identifier
            content_paths: List of content file paths
            analysis_options: Types of analysis to perform
            optimization_options: Optimization settings
            metadata: Additional metadata
            priority: Job priority (higher = more important)
        
        Returns:
            Job ID for tracking
        """        if not self.is_initialized:
            await self.initialize()
        
        # Create job data
        job_data = {
            'job_id': job_id,
            'content_paths': [str(p) for p in content_paths],
            'analysis_options': analysis_options or self.config['default_analysis_options'],
            'optimization_options': optimization_options or {},
            'metadata': metadata or {},
            'priority': priority,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'scheduled'
        }
        
        # Store job info
        self.processing_jobs[job_id] = job_data
        
        # Schedule async processing
        task = asyncio.create_task(
            batch_process_content.delay(
                content_paths,
                analysis_options,
                optimization_options,
                metadata
            )
        )
        
        job_data['task'] = task
        job_data['status'] = 'running'
        
        logger.info(f"Scheduled processing job: {job_id}")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a processing job"""        if job_id not in self.processing_jobs:
            return {'error': f'Job {job_id} not found'}
        
        job = self.processing_jobs[job_id]
        status = {
            'job_id': job_id,
            'status': job['status'],
            'created_at': job['created_at'],
            'content_count': len(job['content_paths']),
            'progress': 0
        }
        
        # Check if task is completed
        if 'task' in job:
            task = job['task']
            if task.done():
                try:
                    result = await task
                    status['status'] = 'completed'
                    status['results'] = result
                    status['progress'] = 100
                except Exception as e:
                    status['status'] = 'failed'
                    status['error'] = str(e)
                    status['progress'] = 0
        
        return status
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a processing job"""        if job_id not in self.processing_jobs:
            return False
        
        job = self.processing_jobs[job_id]
        if 'task' in job:
            task = job['task']
            task.cancel()
            job['status'] = 'cancelled'
        
        logger.info(f"Cancelled processing job: {job_id}")
        return True
    
    async def get_content_history(
        self, 
        content_path: Union[str, Path],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get processing history for a content file"""        try:
            # Query database for historical analysis results
            from ...database.queries import get_content_analysis_history
            
            history = await get_content_analysis_history(
                str(content_path), 
                limit=limit
            )
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get content history for {content_path}: {e}")
            return []
    
    async def get_analytics_summary(
        self, 
        date_range: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """Get analytics summary for content processing"""        try:
            # Get metrics from collector
            metrics = self.metrics.get_summary()
            
            # Get database statistics
            from ...database.queries import get_content_processing_stats
            
            if date_range:
                start_date, end_date = date_range
            else:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
            
            db_stats = await get_content_processing_stats(start_date, end_date)
            
            return {
                'performance_metrics': metrics,
                'processing_stats': db_stats,
                'cache_stats': await self.cache_manager.get_stats(),
                'active_jobs': len(self.processing_jobs),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {'error': str(e)}
    
    async def cleanup_old_data(self, days_old: int = 30) -> Dict[str, int]:
        """Clean up old cache and database entries"""        try:
            # Clean cache
            cache_cleaned = await self.cache_manager.cleanup_expired()
            
            # Clean database
            from ...database.queries import cleanup_old_content_analysis
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            db_cleaned = await cleanup_old_content_analysis(cutoff_date)
            
            # Clean completed jobs
            completed_jobs = [
                job_id for job_id, job in self.processing_jobs.items()
                if job['status'] in ['completed', 'failed', 'cancelled']
            ]
            
            for job_id in completed_jobs:
                del self.processing_jobs[job_id]
            
            result = {
                'cache_entries_cleaned': cache_cleaned,
                'database_entries_cleaned': db_cleaned,
                'jobs_cleaned': len(completed_jobs)
            }
            
            logger.info(f"Cleanup completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {'error': str(e)}
    
    def _generate_cache_key(
        self, 
        content_path: Path, 
        analysis_options: Optional[List[str]]
    ) -> str:
        """Generate cache key for content analysis"""        import hashlib
        
        # Include file hash, modification time, and options
        file_stats = content_path.stat()
        key_components = [
            str(content_path),
            str(file_stats.st_mtime),
            str(file_stats.st_size),
            str(sorted(analysis_options or []))
        ]
        
        key_string = '|'.join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _validate_content_file(self, content_path: Path) -> bool:
        """Validate content file before processing"""        try:
            # Check file existence
            if not content_path.exists():
                return False
            
            # Check file size
            file_size_mb = content_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config['max_file_size_mb']:
                logger.warning(f"File too large: {file_size_mb}MB > {self.config['max_file_size_mb']}MB")
                return False
            
            # Check format support
            file_extension = content_path.suffix.lower()
            supported_extensions = []
            for format_exts in self.config['supported_formats'].values():
                supported_extensions.extend(format_exts)
            
            if file_extension not in supported_extensions:
                logger.warning(f"Unsupported file format: {file_extension}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False
    
    async def _store_analysis_result(
        self, 
        content_path: Path, 
        analysis_data: Dict[str, Any]
    ) -> bool:
        """Store analysis results in database"""        try:
            from ...database.operations import store_content_analysis
            
            await store_content_analysis({
                'file_path': str(content_path),
                'file_size': content_path.stat().st_size,
                'content_type': analysis_data.get('content_type'),
                'analysis_data': analysis_data,
                'created_at': datetime.utcnow()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store analysis result: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the content agent manager"""        try:
            # Cancel all running jobs
            for job_id, job in self.processing_jobs.items():
                if 'task' in job and not job['task'].done():
                    job['task'].cancel()
            
            # Stop metrics collection
            self.metrics.stop_collecting()
            
            # Cleanup resources
            if self.cache_manager:
                await self.cache_manager.close()
            
            self.is_initialized = False
            logger.info("Content Agent Manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
