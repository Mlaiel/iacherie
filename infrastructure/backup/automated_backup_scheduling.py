"""
Automated Backup Scheduling Engine - Intelligent Scheduling and Optimization
==========================================================================

Advanced scheduling system with AI-powered optimization, creator activity awareness,
resource management, and intelligent backup orchestration.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import heapq

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Types of backup schedules."""
    FIXED_INTERVAL = "fixed_interval"
    CRON_EXPRESSION = "cron_expression"
    EVENT_DRIVEN = "event_driven"
    AI_OPTIMIZED = "ai_optimized"
    CREATOR_ADAPTIVE = "creator_adaptive"


class SchedulePriority(Enum):
    """Schedule priority levels."""
    CRITICAL = "critical"       # Monetization, financial data
    HIGH = "high"              # Premium creator content
    MEDIUM = "medium"          # Standard creator content
    LOW = "low"                # System maintenance backups
    BULK = "bulk"              # Bulk operations during off-peak


class ResourceType(Enum):
    """Types of resources for scheduling."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE_IO = "storage_io"
    NETWORK_BANDWIDTH = "network_bandwidth"
    DATABASE_CONNECTIONS = "database_connections"


@dataclass
class ScheduleDefinition:
    """Backup schedule definition."""
    schedule_id: str
    name: str
    schedule_type: ScheduleType
    schedule_expression: str  # Cron or interval expression
    priority: SchedulePriority
    target_backup_type: str
    target_sources: List[str]
    enabled: bool = True
    creator_id: Optional[str] = None
    creator_tier: Optional[str] = None
    resource_requirements: Dict[ResourceType, float] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduledJob:
    """Individual scheduled backup job."""
    job_id: str
    schedule_id: str
    scheduled_time: datetime
    priority: SchedulePriority
    backup_type: str
    sources: List[str]
    creator_context: Optional[Dict[str, Any]] = None
    resource_allocation: Dict[ResourceType, float] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    max_duration_minutes: int = 60
    retry_attempts: int = 3
    status: str = "pending"
    actual_start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    execution_duration_seconds: Optional[float] = None


@dataclass
class ResourcePool:
    """Resource pool for backup operations."""
    resource_type: ResourceType
    total_capacity: float
    available_capacity: float
    allocated_jobs: Dict[str, float] = field(default_factory=dict)
    usage_history: List[Tuple[datetime, float]] = field(default_factory=list)


@dataclass
class CreatorActivity:
    """Creator activity pattern for scheduling optimization."""
    creator_id: str
    active_hours: List[int]  # Hours of day when creator is active
    content_upload_patterns: Dict[str, List[int]]  # Day of week -> hours
    backup_preferences: Dict[str, Any] = field(default_factory=dict)
    timezone: str = "UTC"
    last_activity: Optional[datetime] = None


class AutomatedBackupScheduling:
    """
    Enterprise automated backup scheduling engine with AI optimization.
    
    Features:
    - Intelligent backup scheduling with AI optimization
    - Creator activity-aware scheduling
    - Resource-based scheduling and load balancing
    - Priority-based job queuing and execution
    - Dynamic schedule optimization
    - Conflict resolution and dependency management
    - Performance monitoring and schedule tuning
    - Creator-specific scheduling preferences
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize automated backup scheduling engine."""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Scheduling components
        self.schedules: Dict[str, ScheduleDefinition] = {}
        self.job_queue: List[ScheduledJob] = []  # Priority queue (heap)
        self.active_jobs: Dict[str, ScheduledJob] = {}
        self.completed_jobs: List[ScheduledJob] = []
        
        # Resource management
        self.resource_pools: Dict[ResourceType, ResourcePool] = {}
        
        # Creator activity tracking
        self.creator_activities: Dict[str, CreatorActivity] = {}
        
        # AI optimization
        self.scheduling_patterns: Dict[str, Any] = {}
        self.optimization_metrics: Dict[str, float] = {}
        
        # Creator platform scheduling preferences
        self.tier_scheduling_policies = {
            'premium': {
                'max_concurrent_backups': 5,
                'priority_boost': 2,
                'avoid_active_hours': True,
                'preferred_time_windows': [(2, 6), (22, 24)],  # 2-6 AM, 10 PM-12 AM
                'max_backup_duration_minutes': 30
            },
            'pro': {
                'max_concurrent_backups': 3,
                'priority_boost': 1,
                'avoid_active_hours': True,
                'preferred_time_windows': [(1, 7), (20, 24)],
                'max_backup_duration_minutes': 60
            },
            'standard': {
                'max_concurrent_backups': 2,
                'priority_boost': 0,
                'avoid_active_hours': False,
                'preferred_time_windows': [(0, 8), (18, 24)],
                'max_backup_duration_minutes': 120
            },
            'basic': {
                'max_concurrent_backups': 1,
                'priority_boost': -1,
                'avoid_active_hours': False,
                'preferred_time_windows': [(0, 24)],  # Anytime
                'max_backup_duration_minutes': 240
            }
        }
        
        # Initialize scheduling engine
        asyncio.create_task(self._initialize_scheduling_engine())
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default scheduling configuration."""
        return {
            'max_concurrent_jobs': 20,
            'job_processing_interval_seconds': 30,
            'resource_monitoring_interval_seconds': 60,
            'schedule_optimization_interval_hours': 24,
            'creator_activity_learning_enabled': True,
            'ai_optimization_enabled': True,
            'conflict_resolution_enabled': True,
            'dynamic_resource_allocation': True,
            'performance_based_scheduling': True
        }
    
    async def _initialize_scheduling_engine(self) -> None:
        """Initialize scheduling engine components."""
        try:
            # Initialize resource pools
            await self._initialize_resource_pools()
            
            # Setup default schedules
            await self._setup_default_schedules()
            
            # Start background tasks
            asyncio.create_task(self._job_processing_loop())
            asyncio.create_task(self._resource_monitoring_loop())
            asyncio.create_task(self._schedule_optimization_loop())
            asyncio.create_task(self._creator_activity_learning_loop())
            
            self.logger.info("⏰ Automated backup scheduling engine initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scheduling engine: {e}")
    
    async def _initialize_resource_pools(self) -> None:
        """Initialize resource pools for backup operations."""
        resource_configs = {
            ResourceType.CPU: 100.0,              # 100 CPU units
            ResourceType.MEMORY: 64.0,            # 64 GB
            ResourceType.STORAGE_IO: 1000.0,      # 1000 IOPS
            ResourceType.NETWORK_BANDWIDTH: 10.0, # 10 Gbps
            ResourceType.DATABASE_CONNECTIONS: 50.0  # 50 connections
        }
        
        for resource_type, capacity in resource_configs.items():
            self.resource_pools[resource_type] = ResourcePool(
                resource_type=resource_type,
                total_capacity=capacity,
                available_capacity=capacity
            )
    
    async def _setup_default_schedules(self) -> None:
        """Setup default backup schedules."""
        default_schedules = [
            ScheduleDefinition(
                schedule_id="premium_creator_hourly",
                name="Premium Creator Hourly Backup",
                schedule_type=ScheduleType.AI_OPTIMIZED,
                schedule_expression="0 * * * *",  # Every hour
                priority=SchedulePriority.HIGH,
                target_backup_type="creator_content",
                target_sources=["creator_uploads", "monetization_data"],
                conditions={'creator_tier': 'premium'},
                resource_requirements={
                    ResourceType.CPU: 10.0,
                    ResourceType.MEMORY: 4.0,
                    ResourceType.STORAGE_IO: 100.0
                }
            ),
            ScheduleDefinition(
                schedule_id="ai_models_daily",
                name="AI Models Daily Backup",
                schedule_type=ScheduleType.CRON_EXPRESSION,
                schedule_expression="0 2 * * *",  # Daily at 2 AM
                priority=SchedulePriority.HIGH,
                target_backup_type="ai_processing",
                target_sources=["ai_models", "training_data"],
                resource_requirements={
                    ResourceType.CPU: 20.0,
                    ResourceType.MEMORY: 8.0,
                    ResourceType.STORAGE_IO: 200.0
                }
            ),
            ScheduleDefinition(
                schedule_id="monetization_critical",
                name="Monetization Data Critical Backup",
                schedule_type=ScheduleType.EVENT_DRIVEN,
                schedule_expression="on_financial_transaction",
                priority=SchedulePriority.CRITICAL,
                target_backup_type="monetization_data",
                target_sources=["financial_records", "revenue_data"],
                resource_requirements={
                    ResourceType.CPU: 5.0,
                    ResourceType.MEMORY: 2.0,
                    ResourceType.DATABASE_CONNECTIONS: 5.0
                }
            ),
            ScheduleDefinition(
                schedule_id="system_weekly",
                name="System Weekly Full Backup",
                schedule_type=ScheduleType.CRON_EXPRESSION,
                schedule_expression="0 0 * * 0",  # Weekly on Sunday
                priority=SchedulePriority.MEDIUM,
                target_backup_type="system_backup",
                target_sources=["database", "configuration", "logs"],
                resource_requirements={
                    ResourceType.CPU: 30.0,
                    ResourceType.MEMORY: 16.0,
                    ResourceType.STORAGE_IO: 500.0
                }
            ),
            ScheduleDefinition(
                schedule_id="creator_adaptive",
                name="Creator Adaptive Backup",
                schedule_type=ScheduleType.CREATOR_ADAPTIVE,
                schedule_expression="adaptive",
                priority=SchedulePriority.MEDIUM,
                target_backup_type="creator_content",
                target_sources=["creator_uploads", "processed_content"],
                resource_requirements={
                    ResourceType.CPU: 8.0,
                    ResourceType.MEMORY: 3.0,
                    ResourceType.STORAGE_IO: 80.0
                }
            )
        ]
        
        for schedule in default_schedules:
            self.schedules[schedule.schedule_id] = schedule
    
    async def create_schedule(
        self,
        schedule_definition: ScheduleDefinition
    ) -> str:
        """Create new backup schedule."""
        try:
            self.schedules[schedule_definition.schedule_id] = schedule_definition
            
            # Generate initial jobs if applicable
            if schedule_definition.schedule_type in [ScheduleType.FIXED_INTERVAL, ScheduleType.CRON_EXPRESSION]:
                await self._generate_schedule_jobs(schedule_definition)
            
            self.logger.info(f"⏰ Created backup schedule: {schedule_definition.schedule_id}")
            return schedule_definition.schedule_id
            
        except Exception as e:
            self.logger.error(f"Failed to create schedule: {e}")
            raise
    
    async def _generate_schedule_jobs(self, schedule: ScheduleDefinition) -> None:
        """Generate jobs for schedule based on type."""
        if schedule.schedule_type == ScheduleType.CRON_EXPRESSION:
            # Parse cron and generate next execution times
            next_times = await self._parse_cron_schedule(schedule.schedule_expression, 24)  # Next 24 hours
            
            for exec_time in next_times:
                job = ScheduledJob(
                    job_id=f"{schedule.schedule_id}_{int(exec_time.timestamp())}",
                    schedule_id=schedule.schedule_id,
                    scheduled_time=exec_time,
                    priority=schedule.priority,
                    backup_type=schedule.target_backup_type,
                    sources=schedule.target_sources,
                    resource_allocation=schedule.resource_requirements.copy(),
                    max_duration_minutes=self._get_max_duration_for_schedule(schedule)
                )
                
                await self._add_job_to_queue(job)
        
        elif schedule.schedule_type == ScheduleType.FIXED_INTERVAL:
            # Generate jobs at fixed intervals
            interval_minutes = int(schedule.schedule_expression)  # Assume minutes
            start_time = datetime.now()
            
            for i in range(24 * 60 // interval_minutes):  # Next 24 hours
                exec_time = start_time + timedelta(minutes=i * interval_minutes)
                
                job = ScheduledJob(
                    job_id=f"{schedule.schedule_id}_{int(exec_time.timestamp())}",
                    schedule_id=schedule.schedule_id,
                    scheduled_time=exec_time,
                    priority=schedule.priority,
                    backup_type=schedule.target_backup_type,
                    sources=schedule.target_sources,
                    resource_allocation=schedule.resource_requirements.copy()
                )
                
                await self._add_job_to_queue(job)
    
    async def _parse_cron_schedule(self, cron_expression: str, hours_ahead: int) -> List[datetime]:
        """Parse cron expression and return next execution times."""
        # Simplified cron parsing - in production, use proper cron library
        execution_times = []
        
        if cron_expression == "0 * * * *":  # Every hour
            current_time = datetime.now()
            for i in range(hours_ahead):
                next_hour = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=i+1)
                execution_times.append(next_hour)
        
        elif cron_expression == "0 2 * * *":  # Daily at 2 AM
            current_time = datetime.now()
            for i in range(hours_ahead // 24 + 1):
                next_2am = (current_time + timedelta(days=i)).replace(hour=2, minute=0, second=0, microsecond=0)
                if next_2am > current_time:
                    execution_times.append(next_2am)
        
        elif cron_expression == "0 0 * * 0":  # Weekly on Sunday
            current_time = datetime.now()
            days_until_sunday = (6 - current_time.weekday()) % 7
            if days_until_sunday == 0 and current_time.hour >= 0:
                days_until_sunday = 7
            
            next_sunday = (current_time + timedelta(days=days_until_sunday)).replace(hour=0, minute=0, second=0, microsecond=0)
            execution_times.append(next_sunday)
        
        return execution_times
    
    def _get_max_duration_for_schedule(self, schedule: ScheduleDefinition) -> int:
        """Get maximum duration for schedule based on type and tier."""
        if schedule.creator_tier:
            policy = self.tier_scheduling_policies.get(schedule.creator_tier, {})
            return policy.get('max_backup_duration_minutes', 60)
        
        # Default durations by backup type
        duration_map = {
            'creator_content': 30,
            'monetization_data': 15,
            'ai_processing': 60,
            'system_backup': 240
        }
        
        return duration_map.get(schedule.target_backup_type, 60)
    
    async def _add_job_to_queue(self, job: ScheduledJob) -> None:
        """Add job to priority queue."""
        # Convert priority to numeric value for heap (lower number = higher priority)
        priority_values = {
            SchedulePriority.CRITICAL: 1,
            SchedulePriority.HIGH: 2,
            SchedulePriority.MEDIUM: 3,
            SchedulePriority.LOW: 4,
            SchedulePriority.BULK: 5
        }
        
        priority_value = priority_values.get(job.priority, 3)
        
        # Use timestamp as secondary sort key
        heapq.heappush(self.job_queue, (priority_value, job.scheduled_time.timestamp(), job))
    
    async def trigger_event_driven_backup(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> List[str]:
        """Trigger event-driven backups."""
        triggered_jobs = []
        
        # Find schedules that match the event
        for schedule in self.schedules.values():
            if (schedule.schedule_type == ScheduleType.EVENT_DRIVEN and
                schedule.schedule_expression == event_type and
                schedule.enabled):
                
                # Create immediate job
                job = ScheduledJob(
                    job_id=f"{schedule.schedule_id}_event_{int(datetime.now().timestamp())}",
                    schedule_id=schedule.schedule_id,
                    scheduled_time=datetime.now(),
                    priority=schedule.priority,
                    backup_type=schedule.target_backup_type,
                    sources=schedule.target_sources,
                    creator_context=event_data.get('creator_context'),
                    resource_allocation=schedule.resource_requirements.copy()
                )
                
                await self._add_job_to_queue(job)
                triggered_jobs.append(job.job_id)
        
        self.logger.info(f"🎯 Event-driven backups triggered: {len(triggered_jobs)} jobs for event {event_type}")
        return triggered_jobs
    
    async def _job_processing_loop(self) -> None:
        """Main job processing loop."""
        while True:
            try:
                await self._process_pending_jobs()
                await asyncio.sleep(self.config['job_processing_interval_seconds'])
                
            except Exception as e:
                self.logger.error(f"Error in job processing loop: {e}")
                await asyncio.sleep(60)
    
    async def _process_pending_jobs(self) -> None:
        """Process pending jobs in priority order."""
        current_time = datetime.now()
        processed_count = 0
        
        # Process jobs that are due
        while (self.job_queue and 
               len(self.active_jobs) < self.config['max_concurrent_jobs'] and
               processed_count < 10):  # Limit processing per cycle
            
            # Peek at next job
            if self.job_queue[0][2].scheduled_time <= current_time:
                priority_value, timestamp, job = heapq.heappop(self.job_queue)
                
                # Check if resources are available
                if await self._check_resource_availability(job):
                    await self._start_job_execution(job)
                    processed_count += 1
                else:
                    # Put job back in queue for later
                    heapq.heappush(self.job_queue, (priority_value, timestamp, job))
                    break
            else:
                break
    
    async def _check_resource_availability(self, job: ScheduledJob) -> bool:
        """Check if required resources are available for job."""
        for resource_type, required_amount in job.resource_allocation.items():
            pool = self.resource_pools.get(resource_type)
            if not pool or pool.available_capacity < required_amount:
                return False
        
        return True
    
    async def _start_job_execution(self, job: ScheduledJob) -> None:
        """Start executing a backup job."""
        try:
            # Allocate resources
            await self._allocate_resources(job)
            
            # Move to active jobs
            job.status = "running"
            job.actual_start_time = datetime.now()
            self.active_jobs[job.job_id] = job
            
            # Start backup execution (simulate)
            asyncio.create_task(self._execute_backup_job(job))
            
            self.logger.info(f"🚀 Started backup job: {job.job_id} ({job.backup_type})")
            
        except Exception as e:
            job.status = "failed"
            self.logger.error(f"Failed to start job {job.job_id}: {e}")
    
    async def _allocate_resources(self, job: ScheduledJob) -> None:
        """Allocate resources for job execution."""
        for resource_type, required_amount in job.resource_allocation.items():
            pool = self.resource_pools[resource_type]
            pool.available_capacity -= required_amount
            pool.allocated_jobs[job.job_id] = required_amount
    
    async def _execute_backup_job(self, job: ScheduledJob) -> None:
        """Execute the actual backup job."""
        try:
            # Simulate backup execution
            execution_time = await self._simulate_backup_execution(job)
            
            # Complete job successfully
            job.status = "completed"
            job.completion_time = datetime.now()
            job.execution_duration_seconds = execution_time
            
            self.logger.info(f"✅ Completed backup job: {job.job_id} in {execution_time:.1f}s")
            
        except Exception as e:
            job.status = "failed"
            job.completion_time = datetime.now()
            self.logger.error(f"❌ Backup job failed: {job.job_id} - {str(e)}")
        
        finally:
            # Release resources and cleanup
            await self._release_job_resources(job)
            
            # Move to completed jobs
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            self.completed_jobs.append(job)
    
    async def _simulate_backup_execution(self, job: ScheduledJob) -> float:
        """Simulate backup execution time."""
        # Base execution time based on backup type
        base_times = {
            'creator_content': 300,     # 5 minutes
            'monetization_data': 60,    # 1 minute
            'ai_processing': 900,       # 15 minutes
            'system_backup': 3600       # 1 hour
        }
        
        base_time = base_times.get(job.backup_type, 300)
        
        # Add some randomness
        import random
        execution_time = base_time * (0.8 + 0.4 * random.random())
        
        # Simulate execution delay
        await asyncio.sleep(min(execution_time / 60, 5))  # Max 5 seconds for simulation
        
        return execution_time
    
    async def _release_job_resources(self, job: ScheduledJob) -> None:
        """Release resources allocated to job."""
        for resource_type, allocated_amount in job.resource_allocation.items():
            pool = self.resource_pools[resource_type]
            pool.available_capacity += allocated_amount
            
            if job.job_id in pool.allocated_jobs:
                del pool.allocated_jobs[job.job_id]
    
    async def _resource_monitoring_loop(self) -> None:
        """Monitor resource utilization and optimization."""
        while True:
            try:
                await self._monitor_resource_utilization()
                await self._optimize_resource_allocation()
                await asyncio.sleep(self.config['resource_monitoring_interval_seconds'])
                
            except Exception as e:
                self.logger.error(f"Error in resource monitoring: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_resource_utilization(self) -> None:
        """Monitor current resource utilization."""
        current_time = datetime.now()
        
        for resource_type, pool in self.resource_pools.items():
            utilization = (pool.total_capacity - pool.available_capacity) / pool.total_capacity
            pool.usage_history.append((current_time, utilization))
            
            # Keep only last 24 hours of history
            cutoff_time = current_time - timedelta(hours=24)
            pool.usage_history = [
                (time, util) for time, util in pool.usage_history
                if time > cutoff_time
            ]
    
    async def _optimize_resource_allocation(self) -> None:
        """Optimize resource allocation for pending jobs."""
        if self.config.get('dynamic_resource_allocation', True):
            # Analyze resource usage patterns and adjust allocations
            for job_priority, timestamp, job in self.job_queue:
                if job.status == "pending":
                    await self._adjust_job_resource_allocation(job)
    
    async def _adjust_job_resource_allocation(self, job: ScheduledJob) -> None:
        """Adjust resource allocation for job based on current conditions."""
        # AI-based resource optimization would go here
        # For now, simple heuristics
        
        if job.priority == SchedulePriority.CRITICAL:
            # Boost resources for critical jobs
            for resource_type in job.resource_allocation:
                job.resource_allocation[resource_type] *= 1.2
        
        elif job.priority == SchedulePriority.BULK:
            # Reduce resources for bulk jobs
            for resource_type in job.resource_allocation:
                job.resource_allocation[resource_type] *= 0.8
    
    async def _schedule_optimization_loop(self) -> None:
        """Optimize schedules based on performance data."""
        while True:
            try:
                if self.config.get('ai_optimization_enabled', True):
                    await self._optimize_schedules()
                
                await asyncio.sleep(self.config['schedule_optimization_interval_hours'] * 3600)
                
            except Exception as e:
                self.logger.error(f"Error in schedule optimization: {e}")
                await asyncio.sleep(7200)
    
    async def _optimize_schedules(self) -> None:
        """Optimize schedules based on performance metrics."""
        # Analyze completed jobs to optimize future scheduling
        recent_jobs = [
            job for job in self.completed_jobs
            if job.completion_time and 
            job.completion_time > datetime.now() - timedelta(days=7)
        ]
        
        # Group by schedule
        schedule_performance = {}
        for job in recent_jobs:
            schedule_id = job.schedule_id
            if schedule_id not in schedule_performance:
                schedule_performance[schedule_id] = []
            
            if job.execution_duration_seconds:
                schedule_performance[schedule_id].append({
                    'duration': job.execution_duration_seconds,
                    'success': job.status == "completed",
                    'scheduled_time': job.scheduled_time,
                    'actual_start_time': job.actual_start_time
                })
        
        # Optimize each schedule
        for schedule_id, performance_data in schedule_performance.items():
            if schedule_id in self.schedules:
                await self._optimize_individual_schedule(
                    self.schedules[schedule_id], performance_data
                )
    
    async def _optimize_individual_schedule(
        self,
        schedule: ScheduleDefinition,
        performance_data: List[Dict[str, Any]]
    ) -> None:
        """Optimize individual schedule based on performance data."""
        if not performance_data:
            return
        
        # Calculate average execution time
        avg_duration = sum(p['duration'] for p in performance_data) / len(performance_data)
        
        # Calculate success rate
        success_rate = sum(1 for p in performance_data if p['success']) / len(performance_data)
        
        # Update resource requirements if needed
        if avg_duration > schedule.metadata.get('expected_duration', 0) * 1.5:
            # Increase resource allocation
            for resource_type in schedule.resource_requirements:
                schedule.resource_requirements[resource_type] *= 1.1
            
            self.logger.info(f"⚡ Increased resources for schedule {schedule.schedule_id}")
        
        # Store optimization metrics
        self.optimization_metrics[schedule.schedule_id] = {
            'avg_duration': avg_duration,
            'success_rate': success_rate,
            'jobs_analyzed': len(performance_data),
            'last_optimized': datetime.now().isoformat()
        }
    
    async def _creator_activity_learning_loop(self) -> None:
        """Learn creator activity patterns for adaptive scheduling."""
        while True:
            try:
                if self.config.get('creator_activity_learning_enabled', True):
                    await self._update_creator_activity_patterns()
                
                await asyncio.sleep(3600)  # Update hourly
                
            except Exception as e:
                self.logger.error(f"Error in creator activity learning: {e}")
                await asyncio.sleep(1800)
    
    async def _update_creator_activity_patterns(self) -> None:
        """Update creator activity patterns based on recent data."""
        # This would integrate with creator platform APIs to learn activity patterns
        # For simulation, create some sample patterns
        
        sample_creators = ['creator_1', 'creator_2', 'creator_3']
        
        for creator_id in sample_creators:
            if creator_id not in self.creator_activities:
                self.creator_activities[creator_id] = CreatorActivity(
                    creator_id=creator_id,
                    active_hours=[9, 10, 11, 14, 15, 16, 20, 21],  # Typical active hours
                    content_upload_patterns={
                        'monday': [10, 14, 20],
                        'tuesday': [9, 15, 21],
                        'wednesday': [11, 16, 19],
                        'thursday': [10, 14, 22],
                        'friday': [9, 17, 20],
                        'saturday': [12, 18],
                        'sunday': [14, 19]
                    },
                    timezone="UTC"
                )
    
    async def get_scheduling_metrics(self) -> Dict[str, Any]:
        """Get comprehensive scheduling metrics."""
        # Job statistics
        total_jobs = len(self.completed_jobs) + len(self.active_jobs) + len(self.job_queue)
        completed_jobs = len(self.completed_jobs)
        active_jobs = len(self.active_jobs)
        pending_jobs = len(self.job_queue)
        
        # Success rate
        successful_jobs = len([j for j in self.completed_jobs if j.status == "completed"])
        success_rate = successful_jobs / completed_jobs if completed_jobs > 0 else 0
        
        # Resource utilization
        resource_utilization = {}
        for resource_type, pool in self.resource_pools.items():
            utilization = (pool.total_capacity - pool.available_capacity) / pool.total_capacity
            resource_utilization[resource_type.value] = round(utilization, 3)
        
        # Average execution time by backup type
        execution_times = {}
        for job in self.completed_jobs:
            if job.execution_duration_seconds and job.backup_type:
                if job.backup_type not in execution_times:
                    execution_times[job.backup_type] = []
                execution_times[job.backup_type].append(job.execution_duration_seconds)
        
        avg_execution_times = {}
        for backup_type, times in execution_times.items():
            avg_execution_times[backup_type] = round(sum(times) / len(times), 2)
        
        # Creator-specific metrics
        creator_jobs = len([j for j in self.completed_jobs if j.creator_context])
        
        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'active_jobs': active_jobs,
            'pending_jobs': pending_jobs,
            'success_rate': round(success_rate, 3),
            'resource_utilization': resource_utilization,
            'average_execution_times': avg_execution_times,
            'creator_specific_jobs': creator_jobs,
            'active_schedules': len([s for s in self.schedules.values() if s.enabled]),
            'optimization_metrics': self.optimization_metrics,
            'creator_activity_patterns': len(self.creator_activities),
            'ai_optimization_enabled': self.config.get('ai_optimization_enabled', False)
        }


# Export public interface
__all__ = [
    'AutomatedBackupScheduling',
    'ScheduleType',
    'SchedulePriority',
    'ResourceType',
    'ScheduleDefinition',
    'ScheduledJob',
    'ResourcePool',
    'CreatorActivity'
]