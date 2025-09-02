"""IA Influencer Agent - Fingerprint Manager
=========================================

Centralized fingerprint management system for comprehensive content protection
and similarity detection across all media types.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import os
import pickle
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from .audio_fingerprinter import AudioFingerprinter, AudioFingerprint
from .video_fingerprint import VideoFingerprinter, VideoFingerprint
from .image_fingerprint import ImageFingerprinter, ImageFingerprint
from .text_fingerprint import TextFingerprinter, TextFingerprint
from .vector_matcher import VectorMatcher, MatchResult
from .config import get_config, FingerprintingSystemConfig
from .metadata import extract_content_metadata, ContentMetadata
from .performance import PerformanceMonitor, performance_timer


class ContentType(Enum):
    """
Supported content types"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    UNKNOWN = "unknown"


class FingerprintStatus(Enum):
    """Fingerprint processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class FingerprintJob:
    """Fingerprint processing job"""
    job_id: str
    content_id: str
    content_path: str
    content_type: ContentType
    fingerprint_types: List[str]
    status: FingerprintStatus = FingerprintStatus.PENDING
    priority: int = 5  # 1-10, higher is more priority
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FingerprintResult:
    """
Complete fingerprint result"""
    content_id: str
    content_type: ContentType
    fingerprints: Dict[str, Any]  # Type -> fingerprint data
    metadata: Optional[ContentMetadata] = None
    processing_time: float = 0.0
    confidence_score: float = 0.0
    status: FingerprintStatus = FingerprintStatus.COMPLETED
    created_at: datetime = field(default_factory=datetime.utcnow)
    storage_locations: Dict[str, str] = field(default_factory=dict)


class FingerprintManager:
    """
    Centralized fingerprint management system.
    
    Features:
    - Multi-modal content fingerprinting
    - Job queue management
    - Priority-based processing
    - Automatic retry mechanisms
    - Result caching and storage
    - Performance optimization
    - Batch processing capabilities
    - Real-time monitoring
    - Error handling and recovery
    """
    
    def __init__(self, 
                 config: Optional[FingerprintingSystemConfig] = None,
                 storage_path: str = "/tmp/fingerprints",
                 max_workers: int = 8,
                 enable_caching: bool = True):
        """
        Initialize fingerprint manager.
        
        Args:
            config: System configuration
            storage_path: Path for storing fingerprints
            max_workers: Maximum concurrent workers
            enable_caching: Enable result caching
        """
        self.config = config or get_config("production")
        self.storage_path = Path(storage_path)
        self.max_workers = max_workers
        self.enable_caching = enable_caching
        self.logger = logging.getLogger(__name__)
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize fingerprinters
        self._initialize_fingerprinters()
        
        # Job management
        self.job_queue: asyncio.Queue = asyncio.Queue()
        self.active_jobs: Dict[str, FingerprintJob] = {}
        self.completed_jobs: Dict[str, FingerprintResult] = {}
        self.failed_jobs: Dict[str, FingerprintJob] = {}
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Worker management
        self.workers_running = False
        self.worker_tasks: List[asyncio.Task] = []
        
        # Caching
        self.fingerprint_cache: Dict[str, FingerprintResult] = {}
        self.cache_max_size = 1000
        
        # Statistics
        self.stats = {
            'total_jobs_processed': 0,
            'successful_jobs': 0,
            'failed_jobs': 0,
            'average_processing_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'system_start_time': datetime.utcnow().isoformat()
        }
        
        self.logger.info("Fingerprint manager initialized successfully")
    
    def _initialize_fingerprinters(self):
        """Initialize all fingerprinting components"""
        try:
            self.audio_fingerprinter = AudioFingerprinter(
                max_workers=self.max_workers // 4,
                gpu_acceleration=self.config.audio.enable_gpu
            )
            
            self.video_fingerprinter = VideoFingerprinter(
                max_workers=self.max_workers // 4,
                gpu_acceleration=self.config.video.gpu_memory_fraction > 0
            )
            
            self.image_fingerprinter = ImageFingerprinter(
                max_workers=self.max_workers // 4,
                gpu_acceleration=self.config.image.enable_cuda
            )
            
            self.text_fingerprinter = TextFingerprinter(
                max_workers=self.max_workers // 4,
                cache_embeddings=self.config.text.cache_embeddings
            )
            
            self.vector_matcher = VectorMatcher(config=self.config.vector_matcher)
            
            self.logger.info("All fingerprinting components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing fingerprinters: {e}")
            raise
    
    async def start_workers(self):
        """Start background worker tasks"""
        try:
            if self.workers_running:
                self.logger.warning("Workers already running")
                return
            
            self.workers_running = True
            
            # Start worker tasks
            for i in range(self.max_workers):
                task = asyncio.create_task(self._worker_loop(f"worker_{i}"))
                self.worker_tasks.append(task)
            
            self.logger.info(f"Started {self.max_workers} fingerprint workers")
            
        except Exception as e:
            self.logger.error(f"Error starting workers: {e}")
            raise
    
    async def stop_workers(self):
        """Stop background worker tasks"""
        try:
            self.workers_running = False
            
            # Cancel all worker tasks
            for task in self.worker_tasks:
                if not task.cancelled():
                    task.cancel()
            
            # Wait for tasks to complete
            if self.worker_tasks:
                await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            
            self.worker_tasks.clear()
            self.logger.info("All workers stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping workers: {e}")
    
    async def submit_fingerprint_job(self, 
                                   content_id: str,
                                   content_path: str,
                                   content_type: Optional[ContentType] = None,
                                   fingerprint_types: Optional[List[str]] = None,
                                   priority: int = 5,
                                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit a fingerprinting job.
        
        Args:
            content_id: Unique content identifier
            content_path: Path to content file
            content_type: Content type (auto-detected if not provided)
            fingerprint_types: Specific fingerprint types to extract
            priority: Job priority (1-10, higher is more priority)
            metadata: Additional metadata
            
        Returns:
            Job ID for tracking
        """
        try:
            # Auto-detect content type if not provided
            if content_type is None:
                content_type = self._detect_content_type(content_path)
            
            # Generate job ID
            job_id = f"{content_id}_{hashlib.md5(content_path.encode()).hexdigest()[:8]}"
            
            # Check if already cached
            cache_key = self._generate_cache_key(content_id, content_path, fingerprint_types)
            if self.enable_caching and cache_key in self.fingerprint_cache:
                self.stats['cache_hits'] += 1
                self.logger.info(f"Cache hit for {content_id}")
                return job_id  # Return immediately for cached results
            
            self.stats['cache_misses'] += 1
            
            # Create job
            job = FingerprintJob(
                job_id=job_id,
                content_id=content_id,
                content_path=content_path,
                content_type=content_type,
                fingerprint_types=fingerprint_types or self._get_default_fingerprint_types(content_type),
                priority=priority,
                metadata=metadata or {}
            )
            
            # Add to queue
            await self.job_queue.put(job)
            self.active_jobs[job_id] = job
            
            self.logger.info(f"Submitted fingerprint job {job_id} for {content_id}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Error submitting fingerprint job: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a fingerprinting job"""
        try:
            # Check active jobs
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                return {
                    'job_id': job_id,
                    'status': job.status.value,
                    'progress': self._calculate_job_progress(job),
                    'created_at': job.created_at.isoformat(),
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'error_message': job.error_message,
                    'retry_count': job.retry_count
                }
            
            # Check completed jobs
            if job_id in self.completed_jobs:
                result = self.completed_jobs[job_id]
                return {
                    'job_id': job_id,
                    'status': result.status.value,
                    'progress': 100,
                    'created_at': result.created_at.isoformat(),
                    'processing_time': result.processing_time,
                    'confidence_score': result.confidence_score
                }
            
            # Check failed jobs
            if job_id in self.failed_jobs:
                job = self.failed_jobs[job_id]
                return {
                    'job_id': job_id,
                    'status': job.status.value,
                    'progress': 0,
                    'created_at': job.created_at.isoformat(),
                    'error_message': job.error_message,
                    'retry_count': job.retry_count
                }
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error getting job status: {e}")
            return True
    
    async def get_fingerprint_result(self, 
                                   job_id: Optional[str] = None,
                                   content_id: Optional[str] = None) -> Optional[FingerprintResult]:
        """
        Get fingerprint result by job ID or content ID.
        
        Args:
            job_id: Job identifier
            content_id: Content identifier
            
        Returns:
            Fingerprint result if available
        """
        try:
            if job_id and job_id in self.completed_jobs:
                return self.completed_jobs[job_id]
            
            if content_id:
                # Search by content ID
                for result in self.completed_jobs.values():
                    if result.content_id == content_id:
                        return result
                
                # Check cache
                for cached_result in self.fingerprint_cache.values():
                    if cached_result.content_id == content_id:
                        return cached_result
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error getting fingerprint result: {e}")
            return True
    
    async def find_similar_content(self, 
                                 query_content_id: str,
                                 content_types: Optional[List[ContentType]] = None,
                                 similarity_threshold: float = 0.8,
                                 max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Find similar content using fingerprint matching.
        
        Args:
            query_content_id: ID of query content
            content_types: Content types to search
            similarity_threshold: Minimum similarity threshold
            max_results: Maximum number of results
            
        Returns:
            List of similar content matches
        """
        try:
            # Get query fingerprint
            query_result = await self.get_fingerprint_result(content_id=query_content_id)
            if not query_result:
                self.logger.error(f"Query content {query_content_id} not found")
                return []
            
            content_types = content_types or [query_result.content_type]
            matches = []
            
            # Search through all completed fingerprints
            for result in self.completed_jobs.values():
                if (result.content_type in content_types and 
                    result.content_id != query_content_id):
                    
                    # Calculate similarity across fingerprint types
                    similarity_scores = await self._calculate_content_similarity(
                        query_result, result
                    )
                    
                    if similarity_scores:
                        max_similarity = max(similarity_scores.values())
                        if max_similarity >= similarity_threshold:
                            matches.append({
                                'content_id': result.content_id,
                                'content_type': result.content_type.value,
                                'similarity_score': max_similarity,
                                'similarity_details': similarity_scores,
                                'confidence_score': result.confidence_score,
                                'match_timestamp': datetime.utcnow().isoformat()
                            })
            
            # Sort by similarity and limit results
            matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            return matches[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error finding similar content: {e}")
            return []
    
    async def batch_fingerprint(self, 
                              content_items: List[Dict[str, Any]],
                              batch_size: int = 20) -> Dict[str, str]:
        """
        Submit multiple fingerprinting jobs in batches.
        
        Args:
            content_items: List of content item dictionaries
            batch_size: Number of items per batch
            
        Returns:
            Dictionary mapping content_id to job_id
        """
        try:
            job_mapping = {}
            
            # Process in batches
            for i in range(0, len(content_items), batch_size):
                batch = content_items[i:i + batch_size]
                
                # Submit batch jobs
                batch_tasks = []
                for item in batch:
                    task = self.submit_fingerprint_job(
                        content_id=item['content_id'],
                        content_path=item['content_path'],
                        content_type=item.get('content_type'),
                        fingerprint_types=item.get('fingerprint_types'),
                        priority=item.get('priority', 5),
                        metadata=item.get('metadata')
                    )
                    batch_tasks.append((item['content_id'], task))
                
                # Wait for batch submission
                for content_id, task in batch_tasks:
                    job_id = await task
                    job_mapping[content_id] = job_id
                
                self.logger.info(f"Submitted batch {i // batch_size + 1} with {len(batch)} items")
            
            return job_mapping
            
        except Exception as e:
            self.logger.error(f"Error in batch fingerprinting: {e}")
            return {}
    
    async def cleanup_expired_jobs(self, max_age_hours: int = 24):
        """Clean up expired jobs and results"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Clean up completed jobs
            expired_completed = [
                job_id for job_id, result in self.completed_jobs.items()
                if result.created_at < cutoff_time
            ]
            
            for job_id in expired_completed:
                del self.completed_jobs[job_id]
            
            # Clean up failed jobs
            expired_failed = [
                job_id for job_id, job in self.failed_jobs.items()
                if job.created_at < cutoff_time
            ]
            
            for job_id in expired_failed:
                del self.failed_jobs[job_id]
            
            # Clean up cache
            if len(self.fingerprint_cache) > self.cache_max_size:
                # Remove oldest entries
                cache_items = list(self.fingerprint_cache.items())
                cache_items.sort(key=lambda x: x[1].created_at)
                
                for cache_key, _ in cache_items[:len(cache_items) - self.cache_max_size]:
                    del self.fingerprint_cache[cache_key]
            
            self.logger.info(f"Cleaned up {len(expired_completed)} completed and {len(expired_failed)} failed jobs")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired jobs: {e}")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            performance_stats = self.performance_monitor.get_performance_report()
            
            return {
                'job_statistics': self.stats,
                'queue_status': {
                    'pending_jobs': self.job_queue.qsize(),
                    'active_jobs': len(self.active_jobs),
                    'completed_jobs': len(self.completed_jobs),
                    'failed_jobs': len(self.failed_jobs)
                },
                'cache_statistics': {
                    'cached_results': len(self.fingerprint_cache),
                    'cache_hits': self.stats['cache_hits'],
                    'cache_misses': self.stats['cache_misses'],
                    'cache_hit_ratio': self.stats['cache_hits'] / max(self.stats['cache_hits'] + self.stats['cache_misses'], 1) * 100
                },
                'worker_status': {
                    'workers_running': self.workers_running,
                    'worker_count': len(self.worker_tasks),
                    'max_workers': self.max_workers
                },
                'performance_metrics': performance_stats,
                'component_statistics': {
                    'audio_fingerprinter': self.audio_fingerprinter.get_statistics(),
                    'video_fingerprinter': self.video_fingerprinter.get_statistics(),
                    'image_fingerprinter': self.image_fingerprinter.get_statistics(),
                    'text_fingerprinter': self.text_fingerprinter.get_statistics()
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system statistics: {e}")
            return {'error': str(e)}
    
    # Private helper methods
    
    async def _worker_loop(self, worker_name: str):
        """Main worker loop for processing jobs"""
        self.logger.info(f"Worker {worker_name} started")
        
        while self.workers_running:
            try:
                # Get job from queue with timeout
                job = await asyncio.wait_for(self.job_queue.get(), timeout=1.0)
                
                # Process job
                await self._process_job(job, worker_name)
                
            except asyncio.TimeoutError:
                # No jobs in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
        
        self.logger.info(f"Worker {worker_name} stopped")
    
    @performance_timer
    async def _process_job(self, job: FingerprintJob, worker_name: str):
        """Process a single fingerprinting job"""
        try:
            self.logger.info(f"Worker {worker_name} processing job {job.job_id}")
            
            # Update job status
            job.status = FingerprintStatus.PROCESSING
            job.started_at = datetime.utcnow()
            
            start_time = datetime.utcnow()
            
            # Extract fingerprints based on content type
            fingerprints = {}
            metadata = None
            
            # Extract metadata first
            try:
                metadata = await extract_content_metadata(job.content_path)
            except Exception as e:
                self.logger.warning(f"Could not extract metadata for {job.content_id}: {e}")
            
            # Extract fingerprints
            if job.content_type == ContentType.AUDIO:
                audio_fingerprints = await self.audio_fingerprinter.extract_fingerprint(
                    job.content_path, job.content_id
                )
                fingerprints['audio'] = [fp for fp in audio_fingerprints if fp]
                
            elif job.content_type == ContentType.VIDEO:
                video_fingerprints = await self.video_fingerprinter.extract_fingerprint(
                    job.content_path, job.content_id
                )
                fingerprints['video'] = [fp for fp in video_fingerprints if fp]
                
            elif job.content_type == ContentType.IMAGE:
                # Load image data
                image_fingerprints = await self.image_fingerprinter.extract_fingerprint(
                    job.content_path, job.content_id
                )
                fingerprints['image'] = [fp for fp in image_fingerprints if fp]
                
            elif job.content_type == ContentType.TEXT:
                # Load text data
                with open(job.content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                
                text_fingerprints = await self.text_fingerprinter.extract_fingerprint(
                    text_content, job.content_id
                )
                fingerprints['text'] = [fp for fp in text_fingerprints if fp]
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(fingerprints)
            
            # Create result
            result = FingerprintResult(
                content_id=job.content_id,
                content_type=job.content_type,
                fingerprints=fingerprints,
                metadata=metadata,
                processing_time=processing_time,
                confidence_score=confidence_score,
                status=FingerprintStatus.COMPLETED
            )
            
            # Store result
            await self._store_result(job, result)
            
            # Update statistics
            self.stats['total_jobs_processed'] += 1
            self.stats['successful_jobs'] += 1
            self.stats['average_processing_time'] = (
                (self.stats['average_processing_time'] * (self.stats['successful_jobs'] - 1) + processing_time) /
                self.stats['successful_jobs']
            )
            
            self.logger.info(f"Successfully processed job {job.job_id} in {processing_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error processing job {job.job_id}: {e}")
            await self._handle_job_failure(job, str(e))
    
    async def _store_result(self, job: FingerprintJob, result: FingerprintResult):
        """Store fingerprint result"""
        try:
            # Add to completed jobs
            job.status = FingerprintStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            self.completed_jobs[job.job_id] = result
            
            # Remove from active jobs
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            
            # Add to cache
            if self.enable_caching:
                cache_key = self._generate_cache_key(
                    job.content_id, job.content_path, job.fingerprint_types
                )
                self.fingerprint_cache[cache_key] = result
            
            # Optionally save to persistent storage
            await self._save_to_persistent_storage(result)
            
        except Exception as e:
            self.logger.error(f"Error storing result for job {job.job_id}: {e}")
    
    async def _handle_job_failure(self, job: FingerprintJob, error_message: str):
        """Handle job failure with retry logic"""
        try:
            job.retry_count += 1
            job.error_message = error_message
            
            if job.retry_count <= job.max_retries:
                # Retry job
                job.status = FingerprintStatus.PENDING
                await self.job_queue.put(job)
                self.logger.info(f"Retrying job {job.job_id} (attempt {job.retry_count})")
            else:
                # Mark as failed
                job.status = FingerprintStatus.FAILED
                self.failed_jobs[job.job_id] = job
                
                # Remove from active jobs
                if job.job_id in self.active_jobs:
                    del self.active_jobs[job.job_id]
                
                self.stats['total_jobs_processed'] += 1
                self.stats['failed_jobs'] += 1
                
                self.logger.error(f"Job {job.job_id} failed permanently after {job.retry_count} attempts")
            
        except Exception as e:
            self.logger.error(f"Error handling job failure: {e}")
    
    def _detect_content_type(self, file_path: str) -> ContentType:
        """Auto-detect content type from file extension"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
            video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}
            text_extensions = {'.txt', '.md', '.doc', '.docx', '.pdf', '.rtf', '.html', '.xml'}
            
            if file_ext in audio_extensions:
                return ContentType.AUDIO
            elif file_ext in video_extensions:
                return ContentType.VIDEO
            elif file_ext in image_extensions:
                return ContentType.IMAGE
            elif file_ext in text_extensions:
                return ContentType.TEXT
            else:
                return ContentType.UNKNOWN
                
        except Exception as e:
            self.logger.error(f"Error detecting content type: {e}")
            return ContentType.UNKNOWN
    
    def _get_default_fingerprint_types(self, content_type: ContentType) -> List[str]:
        """Get default fingerprint types for content type"""
        defaults = {
            ContentType.AUDIO: ['perceptual_hash', 'spectral_features', 'chromaprint'],
            ContentType.VIDEO: ['frame_hash', 'color_histogram', 'motion_analysis'],
            ContentType.IMAGE: ['perceptual_hash', 'feature_descriptor', 'color_histogram'],
            ContentType.TEXT: ['semantic_embedding', 'ngram_signature', 'stylometric_features']
        }
        
        return defaults.get(content_type, [])
    
    def _generate_cache_key(self, content_id: str, content_path: str, fingerprint_types: Optional[List[str]]) -> str:
        """
Generate cache key for fingerprint result"""
        components = [content_id, content_path]
        if fingerprint_types:
            components.extend(sorted(fingerprint_types))
        
        cache_string = '|'.join(components)
        return hashlib.sha256(cache_string.encode()).hexdigest()
    
    def _calculate_job_progress(self, job: FingerprintJob) -> int:
        """
Calculate job progress percentage"""
        if job.status == FingerprintStatus.PENDING:
            return 0
        elif job.status == FingerprintStatus.PROCESSING:
            # Estimate progress based on processing time
            if job.started_at:
                elapsed = (datetime.utcnow() - job.started_at).total_seconds()
                # Estimate 60 seconds for completion, with 80% max for processing
                progress = min(80, (elapsed / 60.0) * 80)
                return int(progress)
            return 10
        elif job.status == FingerprintStatus.COMPLETED:
            return 100
        elif job.status == FingerprintStatus.FAILED:
            return 0
        else:
            return 0
    
    def _calculate_confidence_score(self, fingerprints: Dict[str, Any]) -> float:
        """
Calculate overall confidence score for fingerprints"""
        try:
            if not fingerprints:
                return 0.0
            
            # Simple confidence calculation based on number of successful fingerprints
            total_possible = len(fingerprints)
            successful = sum(1 for fps in fingerprints.values() if fps)
            
            base_confidence = successful / total_possible if total_possible > 0 else 0.0
            
            # Adjust based on fingerprint quality
            quality_bonus = 0.0
            for fp_list in fingerprints.values():
                if fp_list:
                    quality_bonus += 0.1  # Small bonus for each successful type
            
            return min(1.0, base_confidence + quality_bonus)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence score: {e}")
            return 0.5
    
    async def _calculate_content_similarity(self, 
                                          result1: FingerprintResult, 
                                          result2: FingerprintResult) -> Dict[str, float]:
        """Calculate similarity between two fingerprint results"""
        try:
            similarities = {}
            
            # Compare fingerprints of the same type
            for fp_type in result1.fingerprints.keys():
                if fp_type in result2.fingerprints:
                    fp1_list = result1.fingerprints[fp_type]
                    fp2_list = result2.fingerprints[fp_type]
                    
                    if fp1_list and fp2_list:
                        # Use the first fingerprint of each type for comparison
                        fp1 = fp1_list[0]
                        fp2 = fp2_list[0]
                        
                        # Calculate similarity based on content type
                        if result1.content_type == ContentType.AUDIO:
                            similarity = await self._compare_audio_fingerprints(fp1, fp2)
                        elif result1.content_type == ContentType.VIDEO:
                            similarity = await self._compare_video_fingerprints(fp1, fp2)
                        elif result1.content_type == ContentType.IMAGE:
                            similarity = await self._compare_image_fingerprints(fp1, fp2)
                        elif result1.content_type == ContentType.TEXT:
                            similarity = await self._compare_text_fingerprints(fp1, fp2)
                        else:
                            similarity = 0.0
                        
                        similarities[fp_type] = similarity
            
            return similarities
            
        except Exception as e:
            self.logger.error(f"Error calculating content similarity: {e}")
            return {}
    
    async def _compare_audio_fingerprints(self, fp1, fp2) -> float:
        """Compare audio fingerprints"""
        try:
            # Placeholder - would use actual audio fingerprint comparison
            return 0.8  # Dummy similarity
        except Exception as e:
            self.logger.error(f"Error comparing audio fingerprints: {e}")
            return 0.0
    
    async def _compare_video_fingerprints(self, fp1, fp2) -> float:
        """Compare video fingerprints"""
        try:
            # Placeholder - would use actual video fingerprint comparison
            return 0.7  # Dummy similarity
        except Exception as e:
            self.logger.error(f"Error comparing video fingerprints: {e}")
            return 0.0
    
    async def _compare_image_fingerprints(self, fp1, fp2) -> float:
        """Compare image fingerprints"""
        try:
            # Use the image fingerprinter's comparison method
            if hasattr(fp1, 'fingerprint_type') and hasattr(fp2, 'fingerprint_type'):
                result = await self.image_fingerprinter.compare_fingerprints(fp1, fp2)
                return result.similarity_score
            return 0.0
        except Exception as e:
            self.logger.error(f"Error comparing image fingerprints: {e}")
            return 0.0
    
    async def _compare_text_fingerprints(self, fp1, fp2) -> float:
        """Compare text fingerprints"""
        try:
            # Use the text fingerprinter's comparison method
            if hasattr(fp1, 'fingerprint_type') and hasattr(fp2, 'fingerprint_type'):
                result = await self.text_fingerprinter.compare_fingerprints(fp1, fp2)
                return result.similarity_score
            return 0.0
        except Exception as e:
            self.logger.error(f"Error comparing text fingerprints: {e}")
            return 0.0
    
    async def _save_to_persistent_storage(self, result: FingerprintResult):
        """Save result to persistent storage"""
        try:
            # Create content-specific directory
            content_dir = self.storage_path / result.content_type.value / result.content_id
            content_dir.mkdir(parents=True, exist_ok=True)
            
            # Save fingerprint data
            fingerprint_file = content_dir / "fingerprints.json"
            with open(fingerprint_file, 'w') as f:
                # Convert result to JSON-serializable format
                result_data = asdict(result)
                # Handle datetime serialization
                result_data['created_at'] = result.created_at.isoformat()
                json.dump(result_data, f, indent=2, default=str)
            
            # Save binary data if any
            for fp_type, fp_list in result.fingerprints.items():
                for i, fp in enumerate(fp_list):
                    if hasattr(fp, 'fingerprint_data'):
                        binary_file = content_dir / f"{fp_type}_{i}.pkl"
                        with open(binary_file, 'wb') as f:
                            pickle.dump(fp.fingerprint_data, f)
            
            self.logger.debug(f"Saved result for {result.content_id} to persistent storage")
            
        except Exception as e:
            self.logger.error(f"Error saving to persistent storage: {e}")
    
    async def close(self):
        """Cleanup resources"""
        try:
            # Stop workers
            await self.stop_workers()
            
            # Close fingerprinting components
            await self.audio_fingerprinter.close()
            await self.video_fingerprinter.close()
            await self.image_fingerprinter.close()
            await self.text_fingerprinter.close()
            
            # Clear caches
            self.fingerprint_cache.clear()
            self.active_jobs.clear()
            
            self.logger.info("Fingerprint manager closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing fingerprint manager: {e}")

# Global manager instance
_manager_instance: Optional[FingerprintManager] = None

def get_fingerprint_manager(config: Optional[FingerprintingSystemConfig] = None) -> FingerprintManager:
    """Get global fingerprint manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = FingerprintManager(config)
    return _manager_instance

def reset_fingerprint_manager():
    """
Reset global fingerprint manager instance"""
    global _manager_instance
    if _manager_instance:
        asyncio.create_task(_manager_instance.close())
    _manager_instance = None
