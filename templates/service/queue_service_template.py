"""{{service_name}} Queue Service for Ainflue Platform
{{service_description}}

Enterprise-grade message queue service with Redis, RabbitMQ, and Kafka support,
job scheduling, retry mechanisms, and real-time processing.

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Role: Backend Senior + Message Queue Architect
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Set, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import time
import pickle
from dataclasses import dataclass, asdict

import aioredis
import aio_pika
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
import croniter
from celery import Celery

from core.base_service import BaseService
from core.config import get_settings
from core.database import get_async_session
from core.exceptions import ServiceException, ValidationError, QueueError
from models.queue import (
    QueueJob, QueueDefinition, JobSchedule, DeadLetterJob,
    QueueMetrics, ProcessingResult
)
from services.analytics_service import AnalyticsService
from utils.validation import validate_queue_data
from utils.serialization import serialize_data, deserialize_data
from monitoring.queue_metrics import QueueMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class QueueType(Enum):
    """Queue implementation types"""
    REDIS = "redis"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
    CELERY = "celery"
    MEMORY = "memory"


class JobPriority(Enum):
    """Job priority levels"""
    LOW = 0
    NORMAL = 5
    HIGH = 10
    URGENT = 15
    CRITICAL = 20


class JobStatus(Enum):
    """Job processing status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    DEAD_LETTER = "dead_letter"


class DeliveryMode(Enum):
    """Message delivery modes"""
    AT_MOST_ONCE = "at_most_once"      # Fire and forget
    AT_LEAST_ONCE = "at_least_once"    # May duplicate
    EXACTLY_ONCE = "exactly_once"      # Guaranteed once


class QueuePattern(Enum):
    """Queue processing patterns"""
    WORK_QUEUE = "work_queue"          # Distribute work
    PUBLISH_SUBSCRIBE = "pub_sub"      # Broadcast
    ROUTING = "routing"                # Topic-based
    RPC = "rpc"                        # Request-response
    DELAYED = "delayed"                # Scheduled execution


@dataclass
class JobPayload:
    """Job payload data structure"""
    task_name: str
    args: List[Any] = None
    kwargs: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.args is None:
            self.args = []
        if self.kwargs is None:
            self.kwargs = {}
        if self.metadata is None:
            self.metadata = {}


# Pydantic Models for Request/Response
class CreateQueueRequest(BaseModel):
    """Request model for creating queues"""
    name: str = Field(..., description="Queue name")
    queue_type: QueueType = Field(..., description="Queue implementation type")
    pattern: QueuePattern = Field(QueuePattern.WORK_QUEUE, description="Queue pattern")
    delivery_mode: DeliveryMode = Field(DeliveryMode.AT_LEAST_ONCE, description="Delivery guarantee")
    max_retries: int = Field(3, description="Maximum retry attempts")
    retry_delay: int = Field(60, description="Retry delay in seconds")
    dead_letter_enabled: bool = Field(True, description="Enable dead letter queue")
    concurrency: int = Field(1, description="Number of concurrent workers")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('name')
    def validate_name(cls, v) -> None:
        if not v or len(v.strip()) < 3:
            raise ValueError('Queue name must be at least 3 characters')
        return v.strip().lower().replace(' ', '_')

    @validator('concurrency')
    def validate_concurrency(cls, v) -> None:
        if v < 1 or v > 100:
            raise ValueError('Concurrency must be between 1 and 100')
        return v


class EnqueueJobRequest(BaseModel):
    """Request model for enqueuing jobs"""
    queue_name: str = Field(..., description="Target queue name")
    task_name: str = Field(..., description="Task/function name to execute")
    args: Optional[List[Any]] = Field(default_factory=list, description="Positional arguments")
    kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Keyword arguments")
    priority: JobPriority = Field(JobPriority.NORMAL, description="Job priority")
    delay: Optional[int] = Field(None, description="Delay execution by seconds")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule execution at specific time")
    expires_at: Optional[datetime] = Field(None, description="Job expiration time")
    unique_key: Optional[str] = Field(None, description="Unique key to prevent duplicates")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('task_name')
    def validate_task_name(cls, v) -> None:
        if not v or len(v.strip()) < 3:
            raise ValueError('Task name must be at least 3 characters')
        return v.strip()


class ScheduleJobRequest(BaseModel):
    """Request model for scheduling recurring jobs"""
    queue_name: str = Field(..., description="Target queue name")
    task_name: str = Field(..., description="Task/function name to execute")
    cron_expression: str = Field(..., description="Cron expression for scheduling")
    args: Optional[List[Any]] = Field(default_factory=list, description="Positional arguments")
    kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Keyword arguments")
    timezone: str = Field("UTC", description="Timezone for scheduling")
    enabled: bool = Field(True, description="Schedule enabled")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('cron_expression')
    def validate_cron(cls, v) -> None:
        try:
            croniter.croniter(v)
            return v
        except Exception:
            raise ValueError('Invalid cron expression')


class JobResponse(BaseModel):
    """Response model for job operations"""
    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    queue_name: str = Field(..., description="Queue name")
    task_name: str = Field(..., description="Task name")
    priority: int = Field(..., description="Job priority")
    created_at: datetime = Field(..., description="Creation time")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled execution time")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")


class {{service_class_name}}(BaseService):
    """
    Enterprise Queue Service for Ainflue Platform
    
    Handles comprehensive message queue management including:
    - Multi-backend support (Redis, RabbitMQ, Kafka, Celery)
    - Job scheduling and delayed execution
    - Priority-based processing
    - Retry mechanisms with exponential backoff
    - Dead letter queue handling
    - Real-time monitoring and metrics
    - Distributed processing
    - Cron-based job scheduling
    - Message routing and patterns
    - Exactly-once delivery guarantees
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "{{service_name}}"
        self.version = "{{service_version}}"
        self.redis_client = None
        self.rabbitmq_connection = None
        self.kafka_producer = None
        self.kafka_consumer = None
        self.celery_app = None
        self.metrics_collector = QueueMetricsCollector()
        
        # Queue backends
        self.queue_backends = {}
        
        # Active workers and consumers
        self.active_workers = {}
        self.active_consumers = {}
        
        # Job registry
        self.task_registry = {}
        
        # Scheduling
        self.scheduler_running = False
        
        # Default configurations
        self.default_config = {
            'max_retries': 3,
            'retry_delay': 60,
            'batch_size': 10,
            'prefetch_count': 1,
            'ack_timeout': 300
        }

    async def initialize(self) -> None:
        """Initialize service with dependencies"""
        try:
            await super().initialize()
            
            # Initialize Redis for lightweight queuing
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # Keep binary for job data
                retry_on_timeout=True
            )
            
            # Initialize queue backends
            await self._initialize_queue_backends()
            
            # Initialize metrics collection
            await self.metrics_collector.initialize()
            
            # Register default task handlers
            await self._register_default_tasks()
            
            # Start background workers
            asyncio.create_task(self._scheduler_worker())
            asyncio.create_task(self._dead_letter_processor())
            asyncio.create_task(self._metrics_collector_worker())
            
            self.scheduler_running = True
            
            logger.info(f"{self.name} service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} service: {e}")
            raise ServiceException(f"Service initialization failed: {e}")

    async def _initialize_queue_backends(self) -> None:
        """Initialize different queue backend connections"""
        try:
            # Redis backend (always available)
            self.queue_backends[QueueType.REDIS] = {
                'client': self.redis_client,
                'initialized': True
            }
            
            # RabbitMQ backend
            if hasattr(settings, 'RABBITMQ_URL') and settings.RABBITMQ_URL:
                try:
                    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
                    self.rabbitmq_connection = connection
                    self.queue_backends[QueueType.RABBITMQ] = {
                        'connection': connection,
                        'initialized': True
                    }
                    logger.info("RabbitMQ backend initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize RabbitMQ: {e}")
            
            # Kafka backend
            if hasattr(settings, 'KAFKA_BOOTSTRAP_SERVERS') and settings.KAFKA_BOOTSTRAP_SERVERS:
                try:
                    self.kafka_producer = AIOKafkaProducer(
                        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                        value_serializer=lambda v: pickle.dumps(v)
                    )
                    await self.kafka_producer.start()
                    
                    self.queue_backends[QueueType.KAFKA] = {
                        'producer': self.kafka_producer,
                        'initialized': True
                    }
                    logger.info("Kafka backend initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize Kafka: {e}")
            
            # Celery backend
            if hasattr(settings, 'CELERY_BROKER_URL') and settings.CELERY_BROKER_URL:
                try:
                    self.celery_app = Celery(
                        'ainflue_queue',
                        broker=settings.CELERY_BROKER_URL,
                        backend=settings.CELERY_RESULT_BACKEND
                    )
                    self.queue_backends[QueueType.CELERY] = {
                        'app': self.celery_app,
                        'initialized': True
                    }
                    logger.info("Celery backend initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize Celery: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize queue backends: {e}")
            raise ServiceException(f"Queue backend initialization failed: {e}")

    async def create_queue(
        self,
        request: CreateQueueRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Create a new queue
        
        Args:
            request: Queue creation request
            session: Database session
            
        Returns:
            Queue details
        """
        async with self.get_session(session) as db_session:
            try:
                # Check if queue already exists
                existing_queue = await self._get_queue_definition(request.name, db_session)
                if existing_queue:
                    raise ValidationError(f"Queue {request.name} already exists")
                
                # Validate queue backend availability
                if request.queue_type not in self.queue_backends:
                    raise ValidationError(f"Queue type {request.queue_type.value} not available")
                
                if not self.queue_backends[request.queue_type]['initialized']:
                    raise ValidationError(f"Queue backend {request.queue_type.value} not initialized")
                
                # Create queue definition
                queue_def = QueueDefinition(
                    id=str(uuid.uuid4()),
                    name=request.name,
                    queue_type=request.queue_type.value,
                    pattern=request.pattern.value,
                    delivery_mode=request.delivery_mode.value,
                    max_retries=request.max_retries,
                    retry_delay=request.retry_delay,
                    dead_letter_enabled=request.dead_letter_enabled,
                    concurrency=request.concurrency,
                    status="active",
                    metadata=request.metadata,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db_session.add(queue_def)
                await db_session.commit()
                
                # Initialize queue in backend
                await self._initialize_queue_backend(queue_def)
                
                # Start workers for this queue
                await self._start_queue_workers(queue_def)
                
                # Record metrics
                await self.metrics_collector.record_queue_created(
                    queue_name=request.name,
                    queue_type=request.queue_type.value,
                    concurrency=request.concurrency
                )
                
                logger.info(f"Queue created: {request.name}")
                
                return {
                    "queue_id": queue_def.id,
                    "name": queue_def.name,
                    "queue_type": queue_def.queue_type,
                    "pattern": queue_def.pattern,
                    "status": queue_def.status,
                    "concurrency": queue_def.concurrency,
                    "created_at": queue_def.created_at.isoformat()
                }
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to create queue: {e}")
                await self.metrics_collector.record_error("queue_creation", str(e))
                raise ServiceException(f"Queue creation failed: {e}")

    async def enqueue_job(
        self,
        request: EnqueueJobRequest,
        session: Optional[AsyncSession] = None
    ) -> JobResponse:
        """
        Enqueue a job for processing
        
        Args:
            request: Job enqueue request
            session: Database session
            
        Returns:
            Job details
        """
        async with self.get_session(session) as db_session:
            try:
                # Get queue definition
                queue_def = await self._get_queue_definition(request.queue_name, db_session)
                if not queue_def:
                    raise ValidationError(f"Queue {request.queue_name} not found")
                
                if queue_def.status != "active":
                    raise ValidationError(f"Queue {request.queue_name} is not active")
                
                # Check for duplicate jobs if unique key provided
                if request.unique_key:
                    existing_job = await self._get_job_by_unique_key(
                        request.queue_name, request.unique_key, db_session
                    )
                    if existing_job and existing_job.status in [
                        JobStatus.PENDING.value, JobStatus.QUEUED.value, JobStatus.PROCESSING.value
                    ]:
                        raise ValidationError(f"Job with unique key {request.unique_key} already exists")
                
                # Calculate execution time
                scheduled_at = request.scheduled_at
                if request.delay:
                    scheduled_at = datetime.utcnow() + timedelta(seconds=request.delay)
                elif not scheduled_at:
                    scheduled_at = datetime.utcnow()
                
                # Create job payload
                payload = JobPayload(
                    task_name=request.task_name,
                    args=request.args or [],
                    kwargs=request.kwargs or {},
                    metadata=request.metadata or {}
                )
                
                # Create job record
                job = QueueJob(
                    id=str(uuid.uuid4()),
                    queue_name=request.queue_name,
                    task_name=request.task_name,
                    payload=serialize_data(asdict(payload)),
                    priority=request.priority.value,
                    status=JobStatus.PENDING.value,
                    unique_key=request.unique_key,
                    scheduled_at=scheduled_at,
                    expires_at=request.expires_at,
                    max_retries=queue_def.max_retries,
                    retry_count=0,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db_session.add(job)
                await db_session.commit()
                
                # Queue job in backend
                await self._queue_job_in_backend(job, queue_def)
                
                # Update job status
                job.status = JobStatus.QUEUED.value
                job.updated_at = datetime.utcnow()
                await db_session.commit()
                
                # Record metrics
                await self.metrics_collector.record_job_enqueued(
                    job_id=job.id,
                    queue_name=request.queue_name,
                    task_name=request.task_name,
                    priority=request.priority.value
                )
                
                logger.info(f"Job enqueued: {job.id} in queue {request.queue_name}")
                
                return JobResponse(
                    job_id=job.id,
                    status=job.status,
                    queue_name=job.queue_name,
                    task_name=job.task_name,
                    priority=job.priority,
                    created_at=job.created_at,
                    scheduled_at=job.scheduled_at,
                    started_at=None,
                    completed_at=None
                )
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to enqueue job: {e}")
                await self.metrics_collector.record_error("job_enqueue", str(e))
                raise ServiceException(f"Job enqueue failed: {e}")

    async def _queue_job_in_backend(self, job -> None: QueueJob, queue_def -> None: QueueDefinition) -> None:
        """Queue job in the appropriate backend"""
        try:
            queue_type = QueueType(queue_def.queue_type)
            
            if queue_type == QueueType.REDIS:
                await self._queue_job_redis(job, queue_def)
            elif queue_type == QueueType.RABBITMQ:
                await self._queue_job_rabbitmq(job, queue_def)
            elif queue_type == QueueType.KAFKA:
                await self._queue_job_kafka(job, queue_def)
            elif queue_type == QueueType.CELERY:
                await self._queue_job_celery(job, queue_def)
            else:
                raise ServiceException(f"Unsupported queue type: {queue_type.value}")
                
        except Exception as e:
            logger.error(f"Failed to queue job in backend: {e}")
            raise ServiceException(f"Backend queueing failed: {e}")

    async def _queue_job_redis(self, job -> None: QueueJob, queue_def -> None: QueueDefinition) -> None:
        """Queue job in Redis"""
        try:
            # Prepare job data
            job_data = {
                'job_id': job.id,
                'queue_name': job.queue_name,
                'task_name': job.task_name,
                'payload': job.payload,
                'priority': job.priority,
                'scheduled_at': job.scheduled_at.isoformat(),
                'expires_at': job.expires_at.isoformat() if job.expires_at else None,
                'retry_count': job.retry_count,
                'max_retries': job.max_retries
            }
            
            serialized_job = pickle.dumps(job_data)
            
            # Choose queuing strategy based on pattern
            if queue_def.pattern == QueuePattern.DELAYED.value and job.scheduled_at > datetime.utcnow():
                # Use sorted set for delayed jobs
                score = job.scheduled_at.timestamp()
                await self.redis_client.zadd(
                    f"delayed:{job.queue_name}",
                    {serialized_job: score}
                )
            else:
                # Use priority queue for immediate jobs
                await self.redis_client.zadd(
                    f"queue:{job.queue_name}",
                    {serialized_job: job.priority}
                )
            
            logger.debug(f"Job {job.id} queued in Redis")
            
        except Exception as e:
            logger.error(f"Failed to queue job in Redis: {e}")
            raise

    async def _queue_job_rabbitmq(self, job -> None: QueueJob, queue_def -> None: QueueDefinition) -> None:
        """Queue job in RabbitMQ"""
        try:
            if not self.rabbitmq_connection:
                raise ServiceException("RabbitMQ connection not available")
            
            channel = await self.rabbitmq_connection.channel()
            
            # Declare queue
            queue = await channel.declare_queue(
                job.queue_name,
                durable=True,
                arguments={
                    'x-max-priority': 20,  # Support priorities
                    'x-message-ttl': 86400000  # 24 hours TTL
                }
            )
            
            # Prepare message
            job_data = {
                'job_id': job.id,
                'queue_name': job.queue_name,
                'task_name': job.task_name,
                'payload': job.payload,
                'scheduled_at': job.scheduled_at.isoformat(),
                'expires_at': job.expires_at.isoformat() if job.expires_at else None
            }
            
            message = aio_pika.Message(
                pickle.dumps(job_data),
                priority=min(job.priority, 20),  # RabbitMQ max priority
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            # Handle delayed jobs
            if job.scheduled_at > datetime.utcnow():
                delay_seconds = int((job.scheduled_at - datetime.utcnow()).total_seconds())
                message.headers = {'x-delay': delay_seconds * 1000}  # milliseconds
            
            await channel.default_exchange.publish(message, routing_key=job.queue_name)
            await channel.close()
            
            logger.debug(f"Job {job.id} queued in RabbitMQ")
            
        except Exception as e:
            logger.error(f"Failed to queue job in RabbitMQ: {e}")
            raise

    async def _queue_job_kafka(self, job -> None: QueueJob, queue_def -> None: QueueDefinition) -> None:
        """Queue job in Kafka"""
        try:
            if not self.kafka_producer:
                raise ServiceException("Kafka producer not available")
            
            # Prepare message
            job_data = {
                'job_id': job.id,
                'queue_name': job.queue_name,
                'task_name': job.task_name,
                'payload': job.payload,
                'priority': job.priority,
                'scheduled_at': job.scheduled_at.isoformat(),
                'expires_at': job.expires_at.isoformat() if job.expires_at else None
            }
            
            # Send message to topic
            await self.kafka_producer.send_and_wait(
                topic=job.queue_name,
                value=job_data,
                key=job.id.encode()  # Use job ID as partition key
            )
            
            logger.debug(f"Job {job.id} queued in Kafka")
            
        except Exception as e:
            logger.error(f"Failed to queue job in Kafka: {e}")
            raise

    async def _queue_job_celery(self, job -> None: QueueJob, queue_def -> None: QueueDefinition) -> None:
        """Queue job in Celery"""
        try:
            if not self.celery_app:
                raise ServiceException("Celery app not available")
            
            # Prepare task arguments
            payload_data = deserialize_data(job.payload)
            
            # Send task to Celery
            if job.scheduled_at > datetime.utcnow():
                # Delayed task
                self.celery_app.send_task(
                    job.task_name,
                    args=payload_data.get('args', []),
                    kwargs=payload_data.get('kwargs', {}),
                    queue=job.queue_name,
                    priority=job.priority,
                    eta=job.scheduled_at,
                    task_id=job.id
                )
            else:
                # Immediate task
                self.celery_app.send_task(
                    job.task_name,
                    args=payload_data.get('args', []),
                    kwargs=payload_data.get('kwargs', {}),
                    queue=job.queue_name,
                    priority=job.priority,
                    task_id=job.id
                )
            
            logger.debug(f"Job {job.id} queued in Celery")
            
        except Exception as e:
            logger.error(f"Failed to queue job in Celery: {e}")
            raise

    async def schedule_job(
        self,
        request: ScheduleJobRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Schedule a recurring job
        
        Args:
            request: Job schedule request
            session: Database session
            
        Returns:
            Schedule details
        """
        async with self.get_session(session) as db_session:
            try:
                # Validate queue exists
                queue_def = await self._get_queue_definition(request.queue_name, db_session)
                if not queue_def:
                    raise ValidationError(f"Queue {request.queue_name} not found")
                
                # Validate cron expression
                cron = croniter.croniter(request.cron_expression)
                next_run = cron.get_next(datetime)
                
                # Create schedule
                schedule = JobSchedule(
                    id=str(uuid.uuid4()),
                    queue_name=request.queue_name,
                    task_name=request.task_name,
                    cron_expression=request.cron_expression,
                    args=json.dumps(request.args or []),
                    kwargs=json.dumps(request.kwargs or {}),
                    timezone=request.timezone,
                    enabled=request.enabled,
                    next_run_at=next_run,
                    metadata=request.metadata,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db_session.add(schedule)
                await db_session.commit()
                
                logger.info(f"Job schedule created: {schedule.id}")
                
                return {
                    "schedule_id": schedule.id,
                    "queue_name": schedule.queue_name,
                    "task_name": schedule.task_name,
                    "cron_expression": schedule.cron_expression,
                    "next_run_at": schedule.next_run_at.isoformat(),
                    "enabled": schedule.enabled,
                    "created_at": schedule.created_at.isoformat()
                }
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to schedule job: {e}")
                raise ServiceException(f"Job scheduling failed: {e}")

    async def register_task(self, task_name -> None: str, task_func -> None: Callable) -> None:
        """Register a task function"""
        try:
            self.task_registry[task_name] = task_func
            logger.info(f"Task registered: {task_name}")
        except Exception as e:
            logger.error(f"Failed to register task {task_name}: {e}")
            raise ServiceException(f"Task registration failed: {e}")

    async def _process_job(self, job_data: Dict[str, Any], queue_def: QueueDefinition) -> Dict[str, Any]:
        """Process a job"""
        job_id = job_data['job_id']
        
        try:
            # Update job status to processing
            await self._update_job_status(job_id, JobStatus.PROCESSING)
            
            # Get task function
            task_name = job_data['task_name']
            task_func = self.task_registry.get(task_name)
            
            if not task_func:
                raise ServiceException(f"Task {task_name} not registered")
            
            # Execute task
            payload_data = deserialize_data(job_data['payload'])
            
            start_time = time.time()
            
            if asyncio.iscoroutinefunction(task_func):
                result = await task_func(*payload_data['args'], **payload_data['kwargs'])
            else:
                result = task_func(*payload_data['args'], **payload_data['kwargs'])
            
            execution_time = (time.time() - start_time) * 1000  # milliseconds
            
            # Update job status to completed
            await self._update_job_status(job_id, JobStatus.COMPLETED, result=result)
            
            # Record metrics
            await self.metrics_collector.record_job_completed(
                job_id=job_id,
                queue_name=job_data['queue_name'],
                task_name=task_name,
                execution_time=execution_time,
                success=True
            )
            
            logger.info(f"Job {job_id} completed successfully")
            
            return {
                'success': True,
                'result': result,
                'execution_time': execution_time
            }
            
        except Exception as e:
            # Handle job failure
            logger.error(f"Job {job_id} failed: {e}")
            
            # Check if retry is needed
            retry_count = job_data.get('retry_count', 0)
            max_retries = job_data.get('max_retries', queue_def.max_retries)
            
            if retry_count < max_retries:
                # Schedule retry
                await self._schedule_job_retry(job_id, retry_count + 1, queue_def)
                await self._update_job_status(job_id, JobStatus.RETRYING)
            else:
                # Move to dead letter queue
                await self._move_to_dead_letter(job_id, job_data, str(e))
                await self._update_job_status(job_id, JobStatus.DEAD_LETTER)
            
            # Record metrics
            await self.metrics_collector.record_job_failed(
                job_id=job_id,
                queue_name=job_data['queue_name'],
                task_name=job_data['task_name'],
                error=str(e),
                retry_count=retry_count
            )
            
            return {
                'success': False,
                'error': str(e),
                'retry_count': retry_count
            }

    # Helper methods and worker implementations...
    async def _get_queue_definition(
        self,
        queue_name: str,
        session: AsyncSession
    ) -> Optional[QueueDefinition]:
        """Get queue definition by name"""
        try:
            result = await session.execute(
                select(QueueDefinition).where(QueueDefinition.name == queue_name)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get queue definition {queue_name}: {e}")
            return None

    async def _get_job_by_unique_key(
        self,
        queue_name: str,
        unique_key: str,
        session: AsyncSession
    ) -> Optional[QueueJob]:
        """Get job by unique key"""
        try:
            result = await session.execute(
                select(QueueJob).where(
                    and_(
                        QueueJob.queue_name == queue_name,
                        QueueJob.unique_key == unique_key
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get job by unique key: {e}")
            return None

    async def _update_job_status(
        self,
        job_id -> None: str,
        status -> None: JobStatus,
        result -> None: Any = None,
        error -> None: str = None
    ) -> None:
        """Update job status"""
        async with self.get_session() as session:
            try:
                updates = {
                    'status': status.value,
                    'updated_at': datetime.utcnow()
                }
                
                if status == JobStatus.PROCESSING:
                    updates['started_at'] = datetime.utcnow()
                elif status == JobStatus.COMPLETED:
                    updates['completed_at'] = datetime.utcnow()
                    if result is not None:
                        updates['result'] = serialize_data(result)
                elif status in [JobStatus.FAILED, JobStatus.DEAD_LETTER]:
                    updates['completed_at'] = datetime.utcnow()
                    if error:
                        updates['error_message'] = error
                
                await session.execute(
                    update(QueueJob)
                    .where(QueueJob.id == job_id)
                    .values(**updates)
                )
                await session.commit()
                
            except Exception as e:
                logger.error(f"Failed to update job status: {e}")

    async def _schedule_job_retry(
        self,
        job_id -> None: str,
        retry_count -> None: int,
        queue_def -> None: QueueDefinition
    ) -> None:
        """Schedule job retry with exponential backoff"""
        try:
            # Calculate retry delay with exponential backoff
            delay = queue_def.retry_delay * (2 ** (retry_count - 1))
            retry_at = datetime.utcnow() + timedelta(seconds=delay)
            
            # Update job with retry information
            async with self.get_session() as session:
                await session.execute(
                    update(QueueJob)
                    .where(QueueJob.id == job_id)
                    .values(
                        retry_count=retry_count,
                        scheduled_at=retry_at,
                        status=JobStatus.PENDING.value,
                        updated_at=datetime.utcnow()
                    )
                )
                await session.commit()
                
                # Re-queue the job
                job_result = await session.execute(
                    select(QueueJob).where(QueueJob.id == job_id)
                )
                job = job_result.scalar_one()
                
                await self._queue_job_in_backend(job, queue_def)
            
            logger.info(f"Job {job_id} scheduled for retry {retry_count} at {retry_at}")
            
        except Exception as e:
            logger.error(f"Failed to schedule job retry: {e}")

    async def _move_to_dead_letter(
        self,
        job_id -> None: str,
        job_data -> None: Dict[str, Any],
        error_message -> None: str
    ) -> None:
        """Move job to dead letter queue"""
        try:
            async with self.get_session() as session:
                dead_letter_job = DeadLetterJob(
                    id=str(uuid.uuid4()),
                    original_job_id=job_id,
                    queue_name=job_data['queue_name'],
                    task_name=job_data['task_name'],
                    payload=job_data['payload'],
                    error_message=error_message,
                    retry_count=job_data.get('retry_count', 0),
                    failed_at=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                
                session.add(dead_letter_job)
                await session.commit()
                
            logger.warning(f"Job {job_id} moved to dead letter queue")
            
        except Exception as e:
            logger.error(f"Failed to move job to dead letter queue: {e}")

    async def _initialize_queue_backend(self, queue_def -> None: QueueDefinition) -> None:
        """Initialize queue in backend"""
        try:
            queue_type = QueueType(queue_def.queue_type)
            
            if queue_type == QueueType.RABBITMQ:
                # Create RabbitMQ queue and exchanges
                channel = await self.rabbitmq_connection.channel()
                
                await channel.declare_queue(
                    queue_def.name,
                    durable=True,
                    arguments={
                        'x-max-priority': 20,
                        'x-message-ttl': 86400000
                    }
                )
                
                if queue_def.dead_letter_enabled:
                    await channel.declare_queue(
                        f"{queue_def.name}.dlq",
                        durable=True
                    )
                
                await channel.close()
                
        except Exception as e:
            logger.error(f"Failed to initialize queue backend: {e}")

    async def _start_queue_workers(self, queue_def -> None: QueueDefinition) -> None:
        """Start workers for a queue"""
        try:
            for worker_id in range(queue_def.concurrency):
                worker_name = f"{queue_def.name}_worker_{worker_id}"
                
                if QueueType(queue_def.queue_type) == QueueType.REDIS:
                    worker_task = asyncio.create_task(
                        self._redis_worker(queue_def, worker_name)
                    )
                elif QueueType(queue_def.queue_type) == QueueType.RABBITMQ:
                    worker_task = asyncio.create_task(
                        self._rabbitmq_worker(queue_def, worker_name)
                    )
                elif QueueType(queue_def.queue_type) == QueueType.KAFKA:
                    worker_task = asyncio.create_task(
                        self._kafka_worker(queue_def, worker_name)
                    )
                
                self.active_workers[worker_name] = worker_task
                
            logger.info(f"Started {queue_def.concurrency} workers for queue {queue_def.name}")
            
        except Exception as e:
            logger.error(f"Failed to start queue workers: {e}")

    async def _redis_worker(self, queue_def -> None: QueueDefinition, worker_name -> None: str) -> None:
        """Redis queue worker"""
        while True:
            try:
                # Check for delayed jobs first
                current_time = time.time()
                delayed_jobs = await self.redis_client.zrangebyscore(
                    f"delayed:{queue_def.name}",
                    '-inf',
                    current_time,
                    start=0,
                    num=1,
                    withscores=True
                )
                
                if delayed_jobs:
                    job_data, score = delayed_jobs[0]
                    # Move from delayed to regular queue
                    await self.redis_client.zrem(f"delayed:{queue_def.name}", job_data)
                    job_info = pickle.loads(job_data)
                    await self.redis_client.zadd(
                        f"queue:{queue_def.name}",
                        {job_data: job_info['priority']}
                    )
                
                # Process regular queue
                job_data = await self.redis_client.zpopmax(f"queue:{queue_def.name}", 1)
                
                if job_data:
                    serialized_job, priority = job_data[0]
                    job_info = pickle.loads(serialized_job)
                    
                    # Process the job
                    await self._process_job(job_info, queue_def)
                else:
                    # No jobs, wait a bit
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Redis worker {worker_name} error: {e}")
                await asyncio.sleep(5)

    async def _rabbitmq_worker(self, queue_def -> None: QueueDefinition, worker_name -> None: str) -> None:
        """RabbitMQ queue worker"""
        try:
            channel = await self.rabbitmq_connection.channel()
            await channel.set_qos(prefetch_count=1)
            
            queue = await channel.declare_queue(queue_def.name, durable=True)
            
            async def process_message(message -> None: aio_pika.IncomingMessage) -> None:
                try:
                    job_info = pickle.loads(message.body)
                    await self._process_job(job_info, queue_def)
                    await message.ack()
                except Exception as e:
                    logger.error(f"Failed to process RabbitMQ message: {e}")
                    await message.nack(requeue=False)
            
            await queue.consume(process_message)
            
        except Exception as e:
            logger.error(f"RabbitMQ worker {worker_name} error: {e}")

    async def _kafka_worker(self, queue_def -> None: QueueDefinition, worker_name -> None: str) -> None:
        """Kafka queue worker"""
        try:
            consumer = AIOKafkaConsumer(
                queue_def.name,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=f"{queue_def.name}_group",
                value_deserializer=lambda m: pickle.loads(m)
            )
            
            await consumer.start()
            
            async for message in consumer:
                try:
                    job_info = message.value
                    await self._process_job(job_info, queue_def)
                    await consumer.commit()
                except Exception as e:
                    logger.error(f"Failed to process Kafka message: {e}")
                    
        except Exception as e:
            logger.error(f"Kafka worker {worker_name} error: {e}")

    async def _scheduler_worker(self) -> None:
        """Background worker for scheduled jobs"""
        while self.scheduler_running:
            try:
                async with self.get_session() as session:
                    # Get due schedules
                    result = await session.execute(
                        select(JobSchedule).where(
                            and_(
                                JobSchedule.enabled == True,
                                JobSchedule.next_run_at <= datetime.utcnow()
                            )
                        )
                    )
                    schedules = result.scalars().all()
                    
                    for schedule in schedules:
                        try:
                            # Create job from schedule
                            job_request = EnqueueJobRequest(
                                queue_name=schedule.queue_name,
                                task_name=schedule.task_name,
                                args=json.loads(schedule.args),
                                kwargs=json.loads(schedule.kwargs),
                                metadata=schedule.metadata or {}
                            )
                            
                            await self.enqueue_job(job_request, session)
                            
                            # Calculate next run time
                            cron = croniter.croniter(schedule.cron_expression)
                            next_run = cron.get_next(datetime)
                            
                            # Update schedule
                            schedule.next_run_at = next_run
                            schedule.last_run_at = datetime.utcnow()
                            schedule.run_count = (schedule.run_count or 0) + 1
                            schedule.updated_at = datetime.utcnow()
                            
                            await session.commit()
                            
                            logger.debug(f"Scheduled job created for {schedule.id}")
                            
                        except Exception as e:
                            logger.error(f"Failed to process schedule {schedule.id}: {e}")
                            continue
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Scheduler worker error: {e}")
                await asyncio.sleep(60)

    async def _dead_letter_processor(self) -> None:
        """Background processor for dead letter queue"""
        while True:
            try:
                # Process dead letter jobs for possible recovery
                # This could include retrying after manual intervention
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Dead letter processor error: {e}")
                await asyncio.sleep(300)

    async def _metrics_collector_worker(self) -> None:
        """Background worker for collecting metrics"""
        while True:
            try:
                # Collect queue metrics
                async with self.get_session() as session:
                    # Get queue statistics
                    result = await session.execute(
                        select(QueueDefinition).where(QueueDefinition.status == "active")
                    )
                    queues = result.scalars().all()
                    
                    for queue in queues:
                        # Count jobs by status
                        job_counts = {}
                        for status in JobStatus:
                            count_result = await session.execute(
                                select(func.count(QueueJob.id)).where(
                                    and_(
                                        QueueJob.queue_name == queue.name,
                                        QueueJob.status == status.value
                                    )
                                )
                            )
                            job_counts[status.value] = count_result.scalar() or 0
                        
                        await self.metrics_collector.record_queue_metrics(
                            queue_name=queue.name,
                            job_counts=job_counts
                        )
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(60)

    async def _register_default_tasks(self) -> None:
        """Register default system tasks"""
        
        async def test_task(*args, **kwargs) -> None:
            """Test task for queue validation"""
            return {"message": "Test task completed", "args": args, "kwargs": kwargs}
        
        async def cleanup_task() -> None:
            """Cleanup old completed jobs"""
            async with self.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                await session.execute(
                    delete(QueueJob).where(
                        and_(
                            QueueJob.status == JobStatus.COMPLETED.value,
                            QueueJob.completed_at < cutoff_date
                        )
                    )
                )
                await session.commit()
                return {"message": "Cleanup completed"}
        
        await self.register_task("test_task", test_task)
        await self.register_task("cleanup_task", cleanup_task)

    async def get_queue_status(
        self,
        queue_name: str,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get queue status and metrics
        
        Args:
            queue_name: Queue name
            session: Database session
            
        Returns:
            Queue status and metrics
        """
        async with self.get_session(session) as db_session:
            try:
                queue_def = await self._get_queue_definition(queue_name, db_session)
                if not queue_def:
                    raise ValidationError(f"Queue {queue_name} not found")
                
                # Get job counts by status
                job_counts = {}
                for status in JobStatus:
                    result = await db_session.execute(
                        select(func.count(QueueJob.id)).where(
                            and_(
                                QueueJob.queue_name == queue_name,
                                QueueJob.status == status.value
                            )
                        )
                    )
                    job_counts[status.value] = result.scalar() or 0
                
                # Get queue size from backend
                backend_size = 0
                if QueueType(queue_def.queue_type) == QueueType.REDIS:
                    backend_size = await self.redis_client.zcard(f"queue:{queue_name}")
                
                # Get recent performance metrics
                metrics = await self.metrics_collector.get_queue_metrics(queue_name)
                
                return {
                    "queue_name": queue_name,
                    "queue_type": queue_def.queue_type,
                    "status": queue_def.status,
                    "concurrency": queue_def.concurrency,
                    "job_counts": job_counts,
                    "backend_size": backend_size,
                    "metrics": metrics,
                    "created_at": queue_def.created_at.isoformat(),
                    "updated_at": queue_def.updated_at.isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to get queue status: {e}")
                raise ServiceException(f"Failed to get queue status: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = await super().health_check()
            
            # Check Redis connectivity
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis"] = "healthy"
            
            # Check RabbitMQ connectivity
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                health_status["rabbitmq"] = "healthy"
            
            # Check Kafka connectivity
            if self.kafka_producer:
                health_status["kafka"] = "healthy"
            
            # Check active workers
            health_status["active_workers"] = len(self.active_workers)
            health_status["registered_tasks"] = len(self.task_registry)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def cleanup(self) -> None:
        """Cleanup service resources"""
        try:
            self.scheduler_running = False
            
            # Cancel all active workers
            for worker_name, worker_task in self.active_workers.items():
                worker_task.cancel()
                try:
                    await worker_task
                except asyncio.CancelledError:
                    pass
            
            # Close connections
            if self.redis_client:
                await self.redis_client.close()
            
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                await self.rabbitmq_connection.close()
            
            if self.kafka_producer:
                await self.kafka_producer.stop()
            
            if self.metrics_collector:
                await self.metrics_collector.cleanup()
                
            await super().cleanup()
            logger.info(f"{self.name} service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Failed to cleanup {self.name} service: {e}")


# Example usage and testing
if __name__ == "__main__":
    async def main() -> None:
        service = {{service_class_name}}()
        await service.initialize()
        
        # Example task registration
        async def example_task(message -> None: str, count -> None: int = 1) -> None:
            """Example task that processes data"""
            await asyncio.sleep(1)  # Simulate work
            return f"Processed: {message} (count: {count})"
        
        await service.register_task("example_task", example_task)
        
        try:
            # Create a queue
            queue_request = CreateQueueRequest(
                name="example_queue",
                queue_type=QueueType.REDIS,
                pattern=QueuePattern.WORK_QUEUE,
                concurrency=2
            )
            
            queue_result = await service.create_queue(queue_request)
            print(f"Queue created: {queue_result}")
            
            # Enqueue a job
            job_request = EnqueueJobRequest(
                queue_name="example_queue",
                task_name="example_task",
                args=["Hello World"],
                kwargs={"count": 5},
                priority=JobPriority.HIGH
            )
            
            job_result = await service.enqueue_job(job_request)
            print(f"Job enqueued: {job_result}")
            
            # Wait a bit for processing
            await asyncio.sleep(3)
            
            # Check queue status
            status = await service.get_queue_status("example_queue")
            print(f"Queue status: {status}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await service.cleanup()

    asyncio.run(main())

# File has syntax issues - needs manual review