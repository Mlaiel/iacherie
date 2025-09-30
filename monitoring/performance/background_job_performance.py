"""
⚠️ CONFIDENTIEL - IA Chérie Creator Platform ⚠️

Background Job Performance Monitor
Advanced background job and task queue performance monitoring for Creator Economy

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import time
import json
import logging
import statistics
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import deque, defaultdict, Counter
import threading
from concurrent.futures import ThreadPoolExecutor
import uuid
import traceback
import psutil
from enum import Enum

# Celery and task queue imports
try:
    from celery import Celery
    from celery.events.state import State
    from celery.events import EventReceiver
    from celery.app.control import Control
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

try:
    import redis
    import rq
    from rq import Queue, Worker, Job
    RQ_AVAILABLE = True
except ImportError:
    RQ_AVAILABLE = False

# Prometheus metrics
from prometheus_client import Gauge, Counter, Histogram, Summary

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"

class JobPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class BackgroundJobMetrics:
    """Background job performance metrics"""
    job_id: str
    job_name: str
    job_type: str  # celery, rq, custom
    queue_name: str
    status: JobStatus
    priority: JobPriority
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_ms: Optional[float]
    wait_time_ms: Optional[float]  # Time in queue before execution
    worker_id: Optional[str]
    retry_count: int
    max_retries: int
    memory_usage_mb: Optional[float]
    cpu_usage_percent: Optional[float]
    error_message: Optional[str]
    creator_id: Optional[str] = None
    content_id: Optional[str] = None
    workflow_type: Optional[str] = None  # upload, processing, monetization, etc.

@dataclass
class QueueMetrics:
    """Queue performance metrics"""
    queue_name: str
    queue_type: str  # celery, rq, custom
    pending_jobs: int
    active_jobs: int
    failed_jobs: int
    completed_jobs: int
    total_jobs: int
    avg_wait_time_ms: float
    avg_execution_time_ms: float
    throughput_jobs_per_minute: float
    worker_count: int
    active_workers: int
    idle_workers: int
    timestamp: datetime

@dataclass
class WorkerMetrics:
    """Worker performance metrics"""
    worker_id: str
    worker_type: str
    queue_names: List[str]
    is_active: bool
    current_job: Optional[str]
    jobs_processed: int
    jobs_failed: int
    avg_job_time_ms: float
    cpu_usage_percent: float
    memory_usage_mb: float
    last_heartbeat: datetime
    uptime_seconds: float

class BackgroundJobPerformance:
    """
    Enterprise Background Job Performance Monitor
    Monitors Celery, RQ, and custom job queues for Creator Economy platform
    Tracks performance, resource usage, and optimization opportunities
    """
    
    def __init__(self,
                 celery_app: Optional[Celery] = None,
                 redis_client: Optional[redis.Redis] = None,
                 enable_celery_monitoring: bool = True,
                 enable_rq_monitoring: bool = True,
                 monitoring_interval: int = 30,
                 max_metrics_history: int = 10000):
        
        self.celery_app = celery_app
        self.redis_client = redis_client
        self.enable_celery_monitoring = enable_celery_monitoring and CELERY_AVAILABLE
        self.enable_rq_monitoring = enable_rq_monitoring and RQ_AVAILABLE
        self.monitoring_interval = monitoring_interval
        self.max_metrics_history = max_metrics_history
        
        # Metrics storage
        self.job_metrics: deque = deque(maxlen=max_metrics_history)
        self.queue_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.worker_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Real-time tracking
        self.active_jobs: Dict[str, BackgroundJobMetrics] = {}
        self.job_history: Dict[str, BackgroundJobMetrics] = {}
        self.queue_states: Dict[str, QueueMetrics] = {}
        
        # Performance analytics
        self.job_patterns: defaultdict = defaultdict(Counter)
        self.failure_patterns: defaultdict = defaultdict(Counter)
        self.performance_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Celery event monitoring
        self.celery_state: Optional[State] = None
        self.celery_receiver: Optional[EventReceiver] = None
        
        # Initialize Prometheus metrics
        self._init_prometheus_metrics()
        
        # Initialize queue monitoring
        if self.enable_celery_monitoring and self.celery_app:
            self._init_celery_monitoring()
        
        if self.enable_rq_monitoring and self.redis_client:
            self._init_rq_monitoring()
        
        logger.info("BackgroundJobPerformance monitor initialized")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.job_execution_duration = Histogram(
            'background_job_execution_duration_seconds',
            'Background job execution duration',
            ['job_name', 'queue_name', 'status']
        )
        
        self.job_wait_duration = Histogram(
            'background_job_wait_duration_seconds',
            'Background job wait time in queue',
            ['job_name', 'queue_name']
        )
        
        self.jobs_total = Counter(
            'background_jobs_total',
            'Total background jobs processed',
            ['job_name', 'queue_name', 'status']
        )
        
        self.queue_size = Gauge(
            'background_queue_size',
            'Background queue size',
            ['queue_name', 'job_type']
        )
        
        self.active_workers = Gauge(
            'background_active_workers',
            'Number of active background workers',
            ['queue_name']
        )
        
        self.job_retry_count = Counter(
            'background_job_retries_total',
            'Total job retries',
            ['job_name', 'queue_name']
        )
        
        self.worker_memory_usage = Gauge(
            'background_worker_memory_usage_mb',
            'Worker memory usage in MB',
            ['worker_id']
        )
    
    def _init_celery_monitoring(self):
        """Initialize Celery event monitoring"""
        if not self.celery_app:
            return
        
        try:
            self.celery_state = State()
            
            # Set up event receiver
            with self.celery_app.connection() as connection:
                self.celery_receiver = EventReceiver(
                    connection,
                    handlers={
                        'task-sent': self._on_task_sent,
                        'task-started': self._on_task_started,
                        'task-succeeded': self._on_task_succeeded,
                        'task-failed': self._on_task_failed,
                        'task-retried': self._on_task_retried,
                        'task-revoked': self._on_task_revoked,
                        'worker-heartbeat': self._on_worker_heartbeat,
                    }
                )
            
            logger.info("Celery event monitoring initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Celery monitoring: {e}")
            self.enable_celery_monitoring = False
    
    def _init_rq_monitoring(self):
        """Initialize RQ monitoring"""
        if not self.redis_client:
            return
        
        try:
            # Test RQ connection
            queues = Queue.all(connection=self.redis_client)
            logger.info(f"RQ monitoring initialized with {len(queues)} queues")
            
        except Exception as e:
            logger.error(f"Failed to initialize RQ monitoring: {e}")
            self.enable_rq_monitoring = False
    
    async def start_monitoring(self):
        """Start background job performance monitoring"""
        if self.monitoring_active:
            logger.warning("Background job monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        # Start Celery event monitoring if enabled
        if self.enable_celery_monitoring and self.celery_receiver:
            asyncio.create_task(self._celery_event_loop())
        
        logger.info("Background job performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop background job monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=30)
        
        logger.info("Background job performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Monitor RQ queues
                if self.enable_rq_monitoring:
                    self._monitor_rq_queues()
                
                # Monitor Celery queues (if not using events)
                if self.enable_celery_monitoring and not self.celery_receiver:
                    self._monitor_celery_queues()
                
                # Update queue metrics
                self._update_queue_metrics()
                
                # Update worker metrics
                self._update_worker_metrics()
                
                # Clean up old metrics
                self._cleanup_old_metrics()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in background job monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    async def _celery_event_loop(self):
        """Celery event monitoring loop"""
        if not self.celery_receiver:
            return
        
        try:
            while self.monitoring_active:
                self.celery_receiver.capture(limit=None, timeout=1, wakeup=True)
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in Celery event loop: {e}")
    
    def _monitor_rq_queues(self):
        """Monitor RQ queue metrics"""
        if not self.redis_client:
            return
        
        try:
            queues = Queue.all(connection=self.redis_client)
            
            for queue in queues:
                queue_name = queue.name
                
                # Get queue statistics
                pending_jobs = len(queue)
                failed_jobs = len(queue.failed_job_registry)
                
                # Get active jobs (simplified)
                active_jobs = 0
                workers = Worker.all(connection=self.redis_client)
                for worker in workers:
                    if worker.get_current_job() and worker.get_current_job().origin == queue_name:
                        active_jobs += 1
                
                # Create queue metrics
                queue_metrics = QueueMetrics(
                    queue_name=queue_name,
                    queue_type='rq',
                    pending_jobs=pending_jobs,
                    active_jobs=active_jobs,
                    failed_jobs=failed_jobs,
                    completed_jobs=0,  # RQ doesn't track this easily
                    total_jobs=pending_jobs + active_jobs + failed_jobs,
                    avg_wait_time_ms=0.0,  # Would need historical tracking
                    avg_execution_time_ms=0.0,  # Would need historical tracking
                    throughput_jobs_per_minute=0.0,  # Would need time window
                    worker_count=len([w for w in workers if queue_name in w.queue_names()]),
                    active_workers=len([w for w in workers if w.get_current_job() and w.get_current_job().origin == queue_name]),
                    idle_workers=0,  # Calculated below
                    timestamp=datetime.utcnow()
                )
                
                queue_metrics.idle_workers = queue_metrics.worker_count - queue_metrics.active_workers
                
                # Store metrics
                self.queue_states[queue_name] = queue_metrics
                self.queue_metrics[queue_name].append(queue_metrics)
                
                # Update Prometheus metrics
                self.queue_size.labels(
                    queue_name=queue_name,
                    job_type='pending'
                ).set(pending_jobs)
                
                self.active_workers.labels(
                    queue_name=queue_name
                ).set(queue_metrics.active_workers)
        
        except Exception as e:
            logger.error(f"Error monitoring RQ queues: {e}")
    
    def _monitor_celery_queues(self):
        """Monitor Celery queue metrics (when not using events)"""
        if not self.celery_app:
            return
        
        try:
            # Get queue information from Celery
            inspect = self.celery_app.control.inspect()
            
            # Get active tasks
            active_tasks = inspect.active()
            if active_tasks:
                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        queue_name = task.get('routing_key', 'default')
                        # Process active task information
                        
            # Get reserved tasks
            reserved_tasks = inspect.reserved()
            if reserved_tasks:
                for worker, tasks in reserved_tasks.items():
                    for task in tasks:
                        queue_name = task.get('routing_key', 'default')
                        # Process reserved task information
            
            # Note: Getting queue sizes in Celery requires broker-specific queries
            # This is a simplified implementation
            
        except Exception as e:
            logger.error(f"Error monitoring Celery queues: {e}")
    
    def _update_queue_metrics(self):
        """Update aggregated queue metrics"""
        for queue_name, metrics_history in self.queue_metrics.items():
            if not metrics_history:
                continue
            
            # Calculate recent performance trends
            recent_metrics = list(metrics_history)[-10:]  # Last 10 measurements
            
            if len(recent_metrics) > 1:
                # Calculate throughput
                time_window = (recent_metrics[-1].timestamp - recent_metrics[0].timestamp).total_seconds()
                if time_window > 0:
                    jobs_processed = sum(m.completed_jobs for m in recent_metrics)
                    throughput = (jobs_processed / time_window) * 60  # jobs per minute
                    
                    # Update latest metrics
                    if queue_name in self.queue_states:
                        self.queue_states[queue_name].throughput_jobs_per_minute = throughput
    
    def _update_worker_metrics(self):
        """Update worker performance metrics"""
        try:
            # Monitor RQ workers
            if self.enable_rq_monitoring and self.redis_client:
                workers = Worker.all(connection=self.redis_client)
                
                for worker in workers:
                    worker_metrics = WorkerMetrics(
                        worker_id=worker.name,
                        worker_type='rq',
                        queue_names=worker.queue_names(),
                        is_active=not worker.stopped,
                        current_job=worker.get_current_job().id if worker.get_current_job() else None,
                        jobs_processed=worker.successful_job_count,
                        jobs_failed=worker.failed_job_count,
                        avg_job_time_ms=0.0,  # Would need historical tracking
                        cpu_usage_percent=0.0,  # Would need process monitoring
                        memory_usage_mb=0.0,    # Would need process monitoring
                        last_heartbeat=datetime.utcnow(),
                        uptime_seconds=(datetime.utcnow() - worker.birth_date).total_seconds() if worker.birth_date else 0
                    )
                    
                    self.worker_metrics[worker.name].append(worker_metrics)
            
            # Monitor Celery workers
            if self.enable_celery_monitoring and self.celery_app:
                inspect = self.celery_app.control.inspect()
                
                # Get worker statistics
                stats = inspect.stats()
                if stats:
                    for worker_name, worker_stats in stats.items():
                        worker_metrics = WorkerMetrics(
                            worker_id=worker_name,
                            worker_type='celery',
                            queue_names=[],  # Would need additional query
                            is_active=True,  # Assume active if responding
                            current_job=None,  # Would need additional query
                            jobs_processed=worker_stats.get('total', {}).get('tasks.successful', 0),
                            jobs_failed=worker_stats.get('total', {}).get('tasks.failed', 0),
                            avg_job_time_ms=0.0,
                            cpu_usage_percent=0.0,
                            memory_usage_mb=0.0,
                            last_heartbeat=datetime.utcnow(),
                            uptime_seconds=0.0
                        )
                        
                        self.worker_metrics[worker_name].append(worker_metrics)
        
        except Exception as e:
            logger.error(f"Error updating worker metrics: {e}")
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory leaks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean up job metrics
        self.job_metrics = deque([
            m for m in self.job_metrics 
            if m.created_at >= cutoff_time
        ], maxlen=self.max_metrics_history)
        
        # Clean up job history
        old_job_ids = [
            job_id for job_id, job in self.job_history.items()
            if job.created_at < cutoff_time
        ]
        for job_id in old_job_ids:
            del self.job_history[job_id]
    
    # Celery event handlers
    def _on_task_sent(self, event):
        """Handle Celery task sent event"""
        job_metrics = BackgroundJobMetrics(
            job_id=event['uuid'],
            job_name=event['name'],
            job_type='celery',
            queue_name=event.get('routing_key', 'default'),
            status=JobStatus.PENDING,
            priority=JobPriority.NORMAL,  # Would need to parse from event
            created_at=datetime.fromtimestamp(event['timestamp']),
            started_at=None,
            completed_at=None,
            execution_time_ms=None,
            wait_time_ms=None,
            worker_id=None,
            retry_count=0,
            max_retries=event.get('retries', 3),
            memory_usage_mb=None,
            cpu_usage_percent=None,
            error_message=None
        )
        
        self.active_jobs[event['uuid']] = job_metrics
        self.job_history[event['uuid']] = job_metrics
    
    def _on_task_started(self, event):
        """Handle Celery task started event"""
        job_id = event['uuid']
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.STARTED
            job.started_at = datetime.fromtimestamp(event['timestamp'])
            job.worker_id = event.get('hostname')
            
            # Calculate wait time
            if job.created_at:
                job.wait_time_ms = (job.started_at - job.created_at).total_seconds() * 1000
    
    def _on_task_succeeded(self, event):
        """Handle Celery task succeeded event"""
        job_id = event['uuid']
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.SUCCESS
            job.completed_at = datetime.fromtimestamp(event['timestamp'])
            
            # Calculate execution time
            if job.started_at:
                job.execution_time_ms = (job.completed_at - job.started_at).total_seconds() * 1000
            
            # Record metrics
            self.job_metrics.append(job)
            
            # Update Prometheus metrics
            self.jobs_total.labels(
                job_name=job.job_name,
                queue_name=job.queue_name,
                status='success'
            ).inc()
            
            if job.execution_time_ms:
                self.job_execution_duration.labels(
                    job_name=job.job_name,
                    queue_name=job.queue_name,
                    status='success'
                ).observe(job.execution_time_ms / 1000)
            
            if job.wait_time_ms:
                self.job_wait_duration.labels(
                    job_name=job.job_name,
                    queue_name=job.queue_name
                ).observe(job.wait_time_ms / 1000)
            
            # Remove from active jobs
            del self.active_jobs[job_id]
    
    def _on_task_failed(self, event):
        """Handle Celery task failed event"""
        job_id = event['uuid']
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.FAILURE
            job.completed_at = datetime.fromtimestamp(event['timestamp'])
            job.error_message = event.get('exception', 'Unknown error')
            
            # Calculate execution time
            if job.started_at:
                job.execution_time_ms = (job.completed_at - job.started_at).total_seconds() * 1000
            
            # Record metrics
            self.job_metrics.append(job)
            
            # Track failure patterns
            self.failure_patterns[job.job_name][job.error_message] += 1
            
            # Update Prometheus metrics
            self.jobs_total.labels(
                job_name=job.job_name,
                queue_name=job.queue_name,
                status='failure'
            ).inc()
            
            # Remove from active jobs
            del self.active_jobs[job_id]
    
    def _on_task_retried(self, event):
        """Handle Celery task retry event"""
        job_id = event['uuid']
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.RETRY
            job.retry_count += 1
            
            # Update Prometheus metrics
            self.job_retry_count.labels(
                job_name=job.job_name,
                queue_name=job.queue_name
            ).inc()
    
    def _on_task_revoked(self, event):
        """Handle Celery task revoked event"""
        job_id = event['uuid']
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.REVOKED
            job.completed_at = datetime.fromtimestamp(event['timestamp'])
            
            # Record metrics
            self.job_metrics.append(job)
            
            # Remove from active jobs
            del self.active_jobs[job_id]
    
    def _on_worker_heartbeat(self, event):
        """Handle Celery worker heartbeat event"""
        # Update worker last seen time
        # Could be used for worker health monitoring
        pass
    
    async def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get background job performance summary"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_jobs = [j for j in self.job_metrics if j.created_at >= cutoff_time]
        
        if not recent_jobs:
            return {"error": "No job metrics available"}
        
        # Overall statistics
        total_jobs = len(recent_jobs)
        successful_jobs = len([j for j in recent_jobs if j.status == JobStatus.SUCCESS])
        failed_jobs = len([j for j in recent_jobs if j.status == JobStatus.FAILURE])
        
        execution_times = [j.execution_time_ms for j in recent_jobs if j.execution_time_ms]
        wait_times = [j.wait_time_ms for j in recent_jobs if j.wait_time_ms]
        
        # Queue analysis
        queue_analysis = {}
        for queue_name in set(j.queue_name for j in recent_jobs):
            queue_jobs = [j for j in recent_jobs if j.queue_name == queue_name]
            
            queue_execution_times = [j.execution_time_ms for j in queue_jobs if j.execution_time_ms]
            queue_analysis[queue_name] = {
                'total_jobs': len(queue_jobs),
                'success_rate': len([j for j in queue_jobs if j.status == JobStatus.SUCCESS]) / len(queue_jobs) * 100,
                'avg_execution_time_ms': statistics.mean(queue_execution_times) if queue_execution_times else 0,
                'current_pending': self.queue_states.get(queue_name, QueueMetrics("", "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, datetime.utcnow())).pending_jobs
            }
        
        # Top slow jobs
        slow_jobs = sorted([j for j in recent_jobs if j.execution_time_ms], 
                          key=lambda x: x.execution_time_ms, reverse=True)[:10]
        
        return {
            'time_window_hours': hours,
            'summary_timestamp': datetime.utcnow().isoformat(),
            'overall_metrics': {
                'total_jobs': total_jobs,
                'success_rate': (successful_jobs / total_jobs) * 100 if total_jobs > 0 else 0,
                'failure_rate': (failed_jobs / total_jobs) * 100 if total_jobs > 0 else 0,
                'avg_execution_time_ms': statistics.mean(execution_times) if execution_times else 0,
                'avg_wait_time_ms': statistics.mean(wait_times) if wait_times else 0,
                'throughput_jobs_per_hour': total_jobs / max(hours, 1)
            },
            'queue_analysis': queue_analysis,
            'active_jobs_count': len(self.active_jobs),
            'slow_jobs': [
                {
                    'job_name': job.job_name,
                    'execution_time_ms': job.execution_time_ms,
                    'queue_name': job.queue_name
                }
                for job in slow_jobs
            ],
            'failure_patterns': dict(self.failure_patterns),
            'worker_status': {
                'total_workers': len(self.worker_metrics),
                'active_workers': sum(1 for workers in self.worker_metrics.values() 
                                    if workers and workers[-1].is_active)
            }
        }
    
    async def creator_workflow_analysis(self, creator_id: str) -> Dict[str, Any]:
        """Analyze background job performance for specific creator workflows"""
        creator_jobs = [j for j in self.job_metrics if j.creator_id == creator_id]
        
        if not creator_jobs:
            return {"error": f"No job metrics found for creator {creator_id}"}
        
        # Workflow analysis
        workflow_patterns = defaultdict(list)
        for job in creator_jobs:
            if job.workflow_type:
                workflow_patterns[job.workflow_type].append(job)
        
        workflow_analysis = {}
        for workflow_type, jobs in workflow_patterns.items():
            execution_times = [j.execution_time_ms for j in jobs if j.execution_time_ms]
            
            workflow_analysis[workflow_type] = {
                'total_jobs': len(jobs),
                'success_rate': len([j for j in jobs if j.status == JobStatus.SUCCESS]) / len(jobs) * 100,
                'avg_execution_time_ms': statistics.mean(execution_times) if execution_times else 0,
                'retry_rate': sum(j.retry_count for j in jobs) / len(jobs),
                'most_common_errors': Counter([j.error_message for j in jobs if j.error_message]).most_common(3)
            }
        
        return {
            'creator_id': creator_id,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'total_jobs_processed': len(creator_jobs),
            'workflow_performance': workflow_analysis,
            'optimization_recommendations': [
                'Consider batching small jobs for better efficiency',
                'Implement job prioritization for time-sensitive workflows',
                'Monitor and optimize retry strategies for failed jobs'
            ]
        }
    
    async def optimize_job_processing(self) -> Dict[str, Any]:
        """Provide job processing optimization recommendations"""
        recommendations = {
            'queue_optimization': [],
            'worker_optimization': [],
            'job_optimization': [],
            'resource_optimization': []
        }
        
        # Analyze queue performance
        for queue_name, queue_state in self.queue_states.items():
            if queue_state.pending_jobs > queue_state.active_workers * 10:
                recommendations['queue_optimization'].append({
                    'queue': queue_name,
                    'issue': 'High pending job backlog',
                    'recommendation': 'Consider adding more workers or increasing worker concurrency'
                })
            
            if queue_state.avg_wait_time_ms > 30000:  # > 30 seconds
                recommendations['queue_optimization'].append({
                    'queue': queue_name,
                    'issue': 'High wait times',
                    'recommendation': 'Optimize job priority or add dedicated workers'
                })
        
        # Analyze recent job patterns
        recent_jobs = list(self.job_metrics)[-1000:]  # Last 1000 jobs
        
        # Find frequently failing jobs
        failure_counts = Counter(j.job_name for j in recent_jobs if j.status == JobStatus.FAILURE)
        for job_name, count in failure_counts.most_common(5):
            if count > 10:
                recommendations['job_optimization'].append({
                    'job': job_name,
                    'issue': f'High failure rate ({count} failures)',
                    'recommendation': 'Review job implementation and error handling'
                })
        
        # Find slow jobs
        execution_times = [(j.job_name, j.execution_time_ms) for j in recent_jobs 
                          if j.execution_time_ms and j.execution_time_ms > 60000]  # > 1 minute
        if execution_times:
            slow_jobs = Counter(job_name for job_name, _ in execution_times)
            for job_name, count in slow_jobs.most_common(3):
                recommendations['job_optimization'].append({
                    'job': job_name,
                    'issue': 'Long execution times',
                    'recommendation': 'Profile and optimize job implementation'
                })
        
        return {
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'recommendations': recommendations,
            'priority_actions': self._get_priority_optimization_actions(recommendations)
        }
    
    def _get_priority_optimization_actions(self, recommendations: Dict[str, List]) -> List[str]:
        """Get prioritized optimization actions"""
        actions = []
        
        # High priority actions
        for category, recs in recommendations.items():
            if len(recs) > 2:  # Multiple issues in same category
                actions.append(f"Address multiple {category.replace('_', ' ')} issues")
        
        # General recommendations
        actions.extend([
            "Implement job monitoring dashboards",
            "Set up automated alerting for job failures",
            "Consider job result caching for expensive operations",
            "Implement graceful job degradation strategies"
        ])
        
        return actions[:5]  # Top 5 priorities