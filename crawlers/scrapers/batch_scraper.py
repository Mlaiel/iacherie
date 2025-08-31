"""Batch Scraper - IA-Influencer-Agent
===================================

High-performance batch scraping for large-scale operations.
Optimized for concurrent processing and resource management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
from urllib.parse import urlparse
import hashlib
import json
import csv
import sqlite3
from pathlib import Path

@dataclass
class BatchJob:
    """Batch scraping job definition."""    job_id: str
    urls: List[str]
    callback: Optional[Callable] = None
    priority: int = 1
    retries: int = 3
    timeout: int = 30
    headers: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = 'pending'  # pending, running, completed, failed
    results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class BatchConfig:
    """Batch scraping configuration."""    concurrent_jobs: int = 5
    concurrent_urls_per_job: int = 10
    max_retries: int = 3
    timeout: int = 30
    rate_limit: float = 1.0  # requests per second
    save_results: bool = True
    result_format: str = 'json'  # json, csv, sqlite
    output_dir: str = './batch_results'
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds
    progress_callback: Optional[Callable] = None

class BatchScraper:
    """    High-performance batch web scraper.
    
    Features:
    - Concurrent processing
    - Job queue management
    - Priority-based scheduling
    - Result persistence
    - Progress tracking
    - Error handling and retries
    - Resource management
    - Caching
    """    
    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        self.logger = logging.getLogger(__name__)
        
        # Queue management
        self.job_queue = queue.PriorityQueue()
        self.active_jobs: Dict[str, BatchJob] = {}
        self.completed_jobs: Dict[str, BatchJob] = {}
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.config.concurrent_jobs)
        self.running = False
        self.worker_threads: List[threading.Thread] = []
        
        # Statistics
        self.stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'total_urls': 0,
            'successful_urls': 0,
            'failed_urls': 0,
            'start_time': None,
            'total_processing_time': 0
        }
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Caching
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        # Setup output directory
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager entry."""        await self._initialize_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        await self.stop()
        
    async def _initialize_session(self):
        """Initialize HTTP session."""        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
    def submit_job(self, job: BatchJob) -> str:
        """Submit batch job to queue."""        job.job_id = job.job_id or self._generate_job_id()
        job.status = 'pending'
        
        # Add to queue with priority (lower number = higher priority)
        priority = -job.priority  # Negate for proper priority queue ordering
        self.job_queue.put((priority, time.time(), job))
        
        self.stats['total_jobs'] += 1
        self.stats['total_urls'] += len(job.urls)
        
        self.logger.info(f"Submitted job {job.job_id} with {len(job.urls)} URLs")
        return job.job_id
        
    def create_job(self, urls: List[str], job_id: Optional[str] = None, 
                  priority: int = 1, **kwargs) -> BatchJob:
        """Create batch job from URLs."""        return BatchJob(
            job_id=job_id or self._generate_job_id(),
            urls=urls,
            priority=priority,
            **kwargs
        )
        
    def _generate_job_id(self) -> str:
        """Generate unique job ID."""        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"job_{timestamp}_{random_part}"
        
    async def start(self):
        """Start batch processing."""        if self.running:
            self.logger.warning("Batch scraper is already running")
            return
            
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        if not self.session:
            await self._initialize_session()
            
        self.logger.info("Starting batch scraper")
        
        # Start worker threads
        for i in range(self.config.concurrent_jobs):
            thread = threading.Thread(target=self._worker_thread, args=(i,))
            thread.daemon = True
            thread.start()
            self.worker_threads.append(thread)
            
    async def stop(self):
        """Stop batch processing."""        if not self.running:
            return
            
        self.logger.info("Stopping batch scraper")
        self.running = False
        
        # Wait for active jobs to complete
        while self.active_jobs:
            await asyncio.sleep(0.1)
            
        # Cleanup session
        if self.session:
            await self.session.close()
            
        self.logger.info("Batch scraper stopped")
        
    def _worker_thread(self, worker_id: int):
        """Worker thread for processing jobs."""        self.logger.info(f"Worker {worker_id} started")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.running:
                try:
                    # Get job from queue with timeout
                    priority, timestamp, job = self.job_queue.get(timeout=1.0)
                    
                    if job:
                        loop.run_until_complete(self._process_job(job, worker_id))
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Worker {worker_id} error: {e}")
                    
        finally:
            loop.close()
            self.logger.info(f"Worker {worker_id} stopped")
            
    async def _process_job(self, job: BatchJob, worker_id: int):
        """Process single batch job."""        job.status = 'running'
        job.started_at = datetime.now()
        self.active_jobs[job.job_id] = job
        
        self.logger.info(f"Worker {worker_id} processing job {job.job_id}")
        
        try:
            # Process URLs concurrently
            semaphore = asyncio.Semaphore(self.config.concurrent_urls_per_job)
            
            async def process_url_with_semaphore(url: str) -> Dict[str, Any]:
                async with semaphore:
                    return await self._process_url(url, job)
                    
            tasks = [process_url_with_semaphore(url) for url in job.urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    job.errors.append(f"URL {job.urls[i]}: {str(result)}")
                    self.stats['failed_urls'] += 1
                else:
                    job.results.append(result)
                    self.stats['successful_urls'] += 1
                    
            job.status = 'completed'
            job.completed_at = datetime.now()
            
            # Save results
            if self.config.save_results:
                await self._save_job_results(job)
                
            # Call callback if provided
            if job.callback:
                try:
                    if asyncio.iscoroutinefunction(job.callback):
                        await job.callback(job)
                    else:
                        job.callback(job)
                except Exception as e:
                    self.logger.error(f"Callback error for job {job.job_id}: {e}")
                    
            self.stats['completed_jobs'] += 1
            self.logger.info(f"Completed job {job.job_id} with {len(job.results)} successful results")
            
        except Exception as e:
            job.status = 'failed'
            job.completed_at = datetime.now()
            job.errors.append(f"Job processing error: {str(e)}")
            self.stats['failed_jobs'] += 1
            self.logger.error(f"Job {job.job_id} failed: {e}")
            
        finally:
            # Move job to completed
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            self.completed_jobs[job.job_id] = job
            
            # Update statistics
            if job.started_at and job.completed_at:
                processing_time = (job.completed_at - job.started_at).total_seconds()
                self.stats['total_processing_time'] += processing_time
                
            # Progress callback
            if self.config.progress_callback:
                try:
                    self.config.progress_callback(job, self.stats)
                except Exception as e:
                    self.logger.error(f"Progress callback error: {e}")
                    
    async def _process_url(self, url: str, job: BatchJob) -> Dict[str, Any]:
        """Process single URL."""        start_time = time.time()
        
        # Check cache first
        if self.config.enable_caching:
            cached_result = self._get_cached_result(url)
            if cached_result:
                return cached_result
                
        # Rate limiting
        await asyncio.sleep(1.0 / self.config.rate_limit)
        
        # Prepare headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
        if job.headers:
            headers.update(job.headers)
            
        # Perform request with retries
        for attempt in range(job.retries + 1):
            try:
                async with self.session.get(url, headers=headers) as response:
                    content = await response.text()
                    
                    result = {
                        'url': url,
                        'status_code': response.status,
                        'content': content,
                        'headers': dict(response.headers),
                        'content_length': len(content),
                        'processing_time': time.time() - start_time,
                        'timestamp': datetime.now().isoformat(),
                        'attempt': attempt + 1,
                        'success': True
                    }
                    
                    # Cache result
                    if self.config.enable_caching and response.status == 200:
                        self._cache_result(url, result)
                        
                    return result
                    
            except Exception as e:
                if attempt == job.retries:
                    # Final attempt failed
                    return {
                        'url': url,
                        'status_code': 0,
                        'content': '',
                        'headers': {},
                        'content_length': 0,
                        'processing_time': time.time() - start_time,
                        'timestamp': datetime.now().isoformat(),
                        'attempt': attempt + 1,
                        'success': False,
                        'error': str(e)
                    }
                else:
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
    def _get_cached_result(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached result for URL."""        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        if url_hash in self.cache:
            cached_data = self.cache[url_hash]
            
            # Check TTL
            if datetime.fromisoformat(cached_data['cached_at']) + timedelta(seconds=self.config.cache_ttl) > datetime.now():
                return cached_data['result']
            else:
                # Remove expired cache
                del self.cache[url_hash]
                
        return None
        
    def _cache_result(self, url: str, result: Dict[str, Any]):
        """Cache result for URL."""        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        self.cache[url_hash] = {
            'result': result,
            'cached_at': datetime.now().isoformat()
        }
        
    async def _save_job_results(self, job: BatchJob):
        """Save job results to file."""        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.config.result_format == 'json':
            filename = f"{self.config.output_dir}/job_{job.job_id}_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump({
                    'job_id': job.job_id,
                    'metadata': job.metadata,
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'status': job.status,
                    'results': job.results,
                    'errors': job.errors,
                    'stats': {
                        'total_urls': len(job.urls),
                        'successful_urls': len(job.results),
                        'failed_urls': len(job.errors),
                        'success_rate': len(job.results) / len(job.urls) * 100 if job.urls else 0
                    }
                }, f, indent=2)
                
        elif self.config.result_format == 'csv':
            filename = f"{self.config.output_dir}/job_{job.job_id}_{timestamp}.csv"
            with open(filename, 'w', newline='') as f:
                if job.results:
                    writer = csv.DictWriter(f, fieldnames=job.results[0].keys())
                    writer.writeheader()
                    writer.writerows(job.results)
                    
        elif self.config.result_format == 'sqlite':
            filename = f"{self.config.output_dir}/batch_results.db"
            conn = sqlite3.connect(filename)
            
            # Create tables if not exist
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    metadata TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    status TEXT,
                    total_urls INTEGER,
                    successful_urls INTEGER,
                    failed_urls INTEGER
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    url TEXT,
                    status_code INTEGER,
                    content_length INTEGER,
                    processing_time REAL,
                    timestamp TEXT,
                    success BOOLEAN,
                    error TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
            ''')
            
            # Insert job data
            conn.execute('''
                INSERT OR REPLACE INTO jobs 
                (job_id, metadata, started_at, completed_at, status, total_urls, successful_urls, failed_urls)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.job_id,
                json.dumps(job.metadata),
                job.started_at.isoformat() if job.started_at else None,
                job.completed_at.isoformat() if job.completed_at else None,
                job.status,
                len(job.urls),
                len(job.results),
                len(job.errors)
            ))
            
            # Insert results
            for result in job.results:
                conn.execute('''
                    INSERT INTO results 
                    (job_id, url, status_code, content_length, processing_time, timestamp, success, error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.job_id,
                    result.get('url'),
                    result.get('status_code'),
                    result.get('content_length'),
                    result.get('processing_time'),
                    result.get('timestamp'),
                    result.get('success'),
                    result.get('error')
                ))
                
            conn.commit()
            conn.close()
            
        self.logger.info(f"Saved results for job {job.job_id} to {filename}")
        
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific job."""        # Check active jobs
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
        elif job_id in self.completed_jobs:
            job = self.completed_jobs[job_id]
        else:
            return None
            
        return {
            'job_id': job.job_id,
            'status': job.status,
            'urls_total': len(job.urls),
            'results_count': len(job.results),
            'errors_count': len(job.errors),
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'processing_time': (job.completed_at - job.started_at).total_seconds() if job.started_at and job.completed_at else None
        }
        
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get status of all jobs."""        all_jobs = []
        
        # Active jobs
        for job in self.active_jobs.values():
            all_jobs.append(self.get_job_status(job.job_id))
            
        # Completed jobs
        for job in self.completed_jobs.values():
            all_jobs.append(self.get_job_status(job.job_id))
            
        return sorted(all_jobs, key=lambda x: x['created_at'], reverse=True)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get batch scraper statistics."""        current_stats = self.stats.copy()
        
        if current_stats['start_time']:
            current_stats['uptime'] = (datetime.now() - current_stats['start_time']).total_seconds()
            current_stats['start_time'] = current_stats['start_time'].isoformat()
            
        current_stats.update({
            'active_jobs': len(self.active_jobs),
            'queued_jobs': self.job_queue.qsize(),
            'completed_jobs_count': len(self.completed_jobs),
            'success_rate': (current_stats['successful_urls'] / current_stats['total_urls'] * 100) if current_stats['total_urls'] > 0 else 0,
            'average_processing_time': current_stats['total_processing_time'] / current_stats['completed_jobs'] if current_stats['completed_jobs'] > 0 else 0,
            'cache_size': len(self.cache),
            'is_running': self.running
        })
        
        return current_stats
        
    async def wait_for_completion(self):
        """Wait for all jobs to complete."""        while self.active_jobs or not self.job_queue.empty():
            await asyncio.sleep(1)
            
    def clear_completed_jobs(self):
        """Clear completed jobs from memory."""        self.completed_jobs.clear()
        self.logger.info("Cleared completed jobs from memory")
        
    def clear_cache(self):
        """Clear result cache."""        self.cache.clear()
        self.logger.info("Cleared result cache")
