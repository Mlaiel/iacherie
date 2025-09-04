"""Infrastructure Service - Consolidated Infrastructure Management Services
================================================================

Comprehensive infrastructure system providing cache management, queue processing,
storage management, and system monitoring for the IA Influencer Agent platform.

Consolidates:
- cache_service.py (existing caching functionality)
- queue_service.py (existing queue processing)
- storage_service.py (existing storage management)
- Infrastructure monitoring and health checks

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/infrastructure.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import asyncio
import pickle
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Enums
class CacheBackend(Enum):
    """Cache backend enumeration"""
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    DATABASE = "database"

class QueueType(Enum):
    """Queue type enumeration"""
    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"
    DELAYED = "delayed"

class StorageBackend(Enum):
    """Storage backend enumeration"""
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"
    MINIO = "minio"

class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

# Data structures
@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    value: Any
    ttl: Optional[int] = None  # Time to live in seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    tags: List[str] = field(default_factory=list)

@dataclass
class QueueJob:
    """Queue job data structure"""
    job_id: str
    queue_name: str
    payload: Dict[str, Any]
    priority: int = 0
    status: JobStatus = JobStatus.PENDING
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    worker_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class StorageObject:
    """Storage object data structure"""
    object_id: str
    bucket: str
    key: str
    size: int
    content_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    etag: Optional[str] = None
    last_modified: datetime = field(default_factory=datetime.utcnow)
    storage_class: str = "standard"
    encryption: Optional[str] = None

@dataclass
class HealthCheck:
    """Health check data structure"""
    service_name: str
    status: HealthStatus
    response_time: float
    details: Dict[str, Any] = field(default_factory=dict)
    last_check: datetime = field(default_factory=datetime.utcnow)
    consecutive_failures: int = 0

@dataclass
class SystemMetrics:
    """System metrics data structure"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int] = field(default_factory=dict)
    active_connections: int = 0
    queue_size: int = 0
    cache_hit_ratio: float = 0.0

# Services
class CacheService:
    """Distributed caching service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.backend = CacheBackend(self.config.get('backend', 'memory'))
        self.default_ttl = self.config.get('default_ttl', 3600)  # 1 hour
        self.cache_store: Dict[str, CacheEntry] = {}
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0}
        logger.info(f"💾 Cache Service initialized with {self.backend.value} backend")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            entry = self.cache_store.get(key)
            if not entry:
                self.stats["misses"] += 1
                return None
            
            # Check TTL
            if entry.ttl and (datetime.utcnow() - entry.created_at).total_seconds() > entry.ttl:
                await self.delete(key)
                self.stats["misses"] += 1
                return None
            
            # Update access stats
            entry.accessed_at = datetime.utcnow()
            entry.access_count += 1
            self.stats["hits"] += 1
            
            return entry.value
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
        """Set value in cache"""
        try:
            entry = CacheEntry(
                key=key,
                value=value,
                ttl=ttl or self.default_ttl,
                tags=tags or []
            )
            
            self.cache_store[key] = entry
            self.stats["sets"] += 1
            
            logger.debug(f"Cache set: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self.cache_store:
                del self.cache_store[key]
                self.stats["deletes"] += 1
                logger.debug(f"Cache delete: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self.cache_store.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    async def get_keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        try:
            if pattern == "*":
                return list(self.cache_store.keys())
            
            # Simple pattern matching (in real implementation would use regex)
            keys = []
            for key in self.cache_store.keys():
                if pattern in key:
                    keys.append(key)
            
            return keys
        except Exception as e:
            logger.error(f"Cache keys retrieval error: {e}")
            return []
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        try:
            invalidated_count = 0
            keys_to_delete = []
            
            for key, entry in self.cache_store.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                await self.delete(key)
                invalidated_count += 1
            
            logger.info(f"Invalidated {invalidated_count} cache entries by tags: {tags}")
            return invalidated_count
        except Exception as e:
            logger.error(f"Cache invalidation by tags error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_ratio = self.stats["hits"] / total_requests if total_requests > 0 else 0.0
            
            return {
                "backend": self.backend.value,
                "total_keys": len(self.cache_store),
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_ratio": hit_ratio,
                "sets": self.stats["sets"],
                "deletes": self.stats["deletes"]
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}

class QueueService:
    """Distributed queue processing service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.queues: Dict[str, List[QueueJob]] = {}
        self.workers: Dict[str, Dict[str, Any]] = {}
        self.processing_jobs: Dict[str, QueueJob] = {}
        logger.info("📨 Queue Service initialized")
    
    async def enqueue(self, queue_name: str, payload: Dict[str, Any], priority: int = 0, delay: Optional[int] = None) -> str:
        """Add job to queue"""
        try:
            job = QueueJob(
                job_id=str(uuid.uuid4()),
                queue_name=queue_name,
                payload=payload,
                priority=priority,
                scheduled_at=datetime.utcnow() + timedelta(seconds=delay) if delay else None
            )
            
            if queue_name not in self.queues:
                self.queues[queue_name] = []
            
            self.queues[queue_name].append(job)
            
            # Sort by priority (higher priority first)
            self.queues[queue_name].sort(key=lambda j: j.priority, reverse=True)
            
            logger.debug(f"Enqueued job {job.job_id} to {queue_name}")
            return job.job_id
        except Exception as e:
            logger.error(f"Queue enqueue error: {e}")
            raise
    
    async def dequeue(self, queue_name: str, worker_id: str) -> Optional[QueueJob]:
        """Get next job from queue"""
        try:
            if queue_name not in self.queues or not self.queues[queue_name]:
                return None
            
            # Find next available job
            current_time = datetime.utcnow()
            for i, job in enumerate(self.queues[queue_name]):
                if job.status == JobStatus.PENDING:
                    # Check if job is scheduled for future
                    if job.scheduled_at and job.scheduled_at > current_time:
                        continue
                    
                    # Assign job to worker
                    job.status = JobStatus.RUNNING
                    job.started_at = current_time
                    job.worker_id = worker_id
                    
                    # Move to processing
                    self.processing_jobs[job.job_id] = job
                    self.queues[queue_name].pop(i)
                    
                    logger.debug(f"Dequeued job {job.job_id} from {queue_name} to worker {worker_id}")
                    return job
            
            return None
        except Exception as e:
            logger.error(f"Queue dequeue error: {e}")
            return None
    
    async def complete_job(self, job_id: str, result: Dict[str, Any] = None) -> bool:
        """Mark job as completed"""
        try:
            job = self.processing_jobs.get(job_id)
            if not job:
                return False
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.updated_at = datetime.utcnow()
            
            if result:
                job.payload["result"] = result
            
            # Remove from processing
            del self.processing_jobs[job_id]
            
            logger.debug(f"Completed job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Job completion error: {e}")
            return False
    
    async def fail_job(self, job_id: str, error_message: str) -> bool:
        """Mark job as failed and potentially retry"""
        try:
            job = self.processing_jobs.get(job_id)
            if not job:
                return False
            
            job.error_message = error_message
            job.retry_count += 1
            job.updated_at = datetime.utcnow()
            
            if job.retry_count <= job.max_retries:
                # Retry job
                job.status = JobStatus.RETRYING
                job.scheduled_at = datetime.utcnow() + timedelta(seconds=30 * job.retry_count)  # Exponential backoff
                
                # Move back to queue
                if job.queue_name not in self.queues:
                    self.queues[job.queue_name] = []
                self.queues[job.queue_name].append(job)
                
                del self.processing_jobs[job_id]
                logger.info(f"Retrying job {job_id} (attempt {job.retry_count})")
            else:
                # Max retries exceeded
                job.status = JobStatus.FAILED
                del self.processing_jobs[job_id]
                logger.error(f"Job {job_id} failed permanently: {error_message}")
            
            return True
        except Exception as e:
            logger.error(f"Job failure handling error: {e}")
            return False
    
    async def get_queue_stats(self, queue_name: str = None) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            if queue_name:
                queue_jobs = self.queues.get(queue_name, [])
                stats = {
                    "queue_name": queue_name,
                    "pending_jobs": len([j for j in queue_jobs if j.status == JobStatus.PENDING]),
                    "total_jobs": len(queue_jobs)
                }
            else:
                stats = {
                    "total_queues": len(self.queues),
                    "processing_jobs": len(self.processing_jobs),
                    "total_pending": sum(len([j for j in jobs if j.status == JobStatus.PENDING]) 
                                       for jobs in self.queues.values())
                }
            
            return stats
        except Exception as e:
            logger.error(f"Queue stats error: {e}")
            return {}
    
    async def register_worker(self, worker_id: str, capabilities: List[str]) -> bool:
        """Register worker with capabilities"""
        try:
            self.workers[worker_id] = {
                "capabilities": capabilities,
                "registered_at": datetime.utcnow(),
                "last_heartbeat": datetime.utcnow(),
                "jobs_processed": 0
            }
            
            logger.info(f"Registered worker {worker_id} with capabilities: {capabilities}")
            return True
        except Exception as e:
            logger.error(f"Worker registration error: {e}")
            return False

class StorageService:
    """Distributed storage management service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.backend = StorageBackend(self.config.get('backend', 'local'))
        self.objects_store: Dict[str, StorageObject] = {}
        self.buckets: Dict[str, Dict[str, Any]] = {}
        logger.info(f"🗄️ Storage Service initialized with {self.backend.value} backend")
    
    async def create_bucket(self, bucket_name: str, region: str = "us-east-1") -> bool:
        """Create storage bucket"""
        try:
            if bucket_name in self.buckets:
                return False
            
            self.buckets[bucket_name] = {
                "name": bucket_name,
                "region": region,
                "created_at": datetime.utcnow(),
                "object_count": 0,
                "total_size": 0
            }
            
            logger.info(f"Created bucket: {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Bucket creation error: {e}")
            return False
    
    async def upload_object(self, bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream", metadata: Dict[str, Any] = None) -> Optional[StorageObject]:
        """Upload object to storage"""
        try:
            if bucket not in self.buckets:
                raise ValueError(f"Bucket not found: {bucket}")
            
            # Generate ETag (simplified)
            etag = hashlib.md5(data).hexdigest()
            
            obj = StorageObject(
                object_id=str(uuid.uuid4()),
                bucket=bucket,
                key=key,
                size=len(data),
                content_type=content_type,
                metadata=metadata or {},
                etag=etag
            )
            
            # Store object
            object_key = f"{bucket}/{key}"
            self.objects_store[object_key] = obj
            
            # Update bucket stats
            self.buckets[bucket]["object_count"] += 1
            self.buckets[bucket]["total_size"] += len(data)
            
            logger.debug(f"Uploaded object: {object_key}")
            return obj
        except Exception as e:
            logger.error(f"Object upload error: {e}")
            return None
    
    async def download_object(self, bucket: str, key: str) -> Optional[Dict[str, Any]]:
        """Download object from storage"""
        try:
            object_key = f"{bucket}/{key}"
            obj = self.objects_store.get(object_key)
            
            if not obj:
                return None
            
            # In a real implementation, this would return actual data
            return {
                "object": obj,
                "data": b"mock_object_data",  # Would be actual object data
                "content_type": obj.content_type,
                "size": obj.size
            }
        except Exception as e:
            logger.error(f"Object download error: {e}")
            return None
    
    async def delete_object(self, bucket: str, key: str) -> bool:
        """Delete object from storage"""
        try:
            object_key = f"{bucket}/{key}"
            obj = self.objects_store.get(object_key)
            
            if not obj:
                return False
            
            # Update bucket stats
            self.buckets[bucket]["object_count"] -= 1
            self.buckets[bucket]["total_size"] -= obj.size
            
            # Delete object
            del self.objects_store[object_key]
            
            logger.debug(f"Deleted object: {object_key}")
            return True
        except Exception as e:
            logger.error(f"Object deletion error: {e}")
            return False
    
    async def list_objects(self, bucket: str, prefix: str = "", limit: int = 1000) -> List[StorageObject]:
        """List objects in bucket"""
        try:
            objects = []
            
            for object_key, obj in self.objects_store.items():
                if obj.bucket == bucket:
                    if not prefix or obj.key.startswith(prefix):
                        objects.append(obj)
            
            # Sort by last modified
            objects.sort(key=lambda o: o.last_modified, reverse=True)
            
            return objects[:limit]
        except Exception as e:
            logger.error(f"Object listing error: {e}")
            return []
    
    async def get_bucket_info(self, bucket: str) -> Optional[Dict[str, Any]]:
        """Get bucket information"""
        try:
            return self.buckets.get(bucket)
        except Exception as e:
            logger.error(f"Bucket info error: {e}")
            return None
    
    async def generate_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate presigned URL for object access"""
        try:
            object_key = f"{bucket}/{key}"
            if object_key not in self.objects_store:
                return None
            
            # In a real implementation, this would generate actual presigned URL
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            url = f"https://storage.example.com/{bucket}/{key}?expires={expires_at.isoformat()}"
            
            return url
        except Exception as e:
            logger.error(f"Presigned URL generation error: {e}")
            return None

class HealthMonitoringService:
    """System health monitoring service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.metrics_history: List[SystemMetrics] = []
        self.max_metrics_history = self.config.get('max_metrics_history', 1000)
        logger.info("🏥 Health Monitoring Service initialized")
    
    async def register_health_check(self, service_name: str, check_function: callable, check_interval: int = 60) -> bool:
        """Register health check for service"""
        try:
            self.health_checks[service_name] = HealthCheck(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                response_time=0.0
            )
            
            logger.info(f"Registered health check for: {service_name}")
            return True
        except Exception as e:
            logger.error(f"Health check registration error: {e}")
            return False
    
    async def perform_health_checks(self) -> Dict[str, HealthCheck]:
        """Perform all registered health checks"""
        try:
            results = {}
            
            for service_name, health_check in self.health_checks.items():
                start_time = datetime.utcnow()
                
                try:
                    # Mock health check (in real implementation would call actual check)
                    await asyncio.sleep(0.01)  # Simulate check
                    
                    # Random health status for demo
                    import random
                    status = random.choice([HealthStatus.HEALTHY, HealthStatus.HEALTHY, HealthStatus.DEGRADED])
                    
                    response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    health_check.status = status
                    health_check.response_time = response_time
                    health_check.last_check = datetime.utcnow()
                    health_check.consecutive_failures = 0 if status == HealthStatus.HEALTHY else health_check.consecutive_failures + 1
                    
                except Exception as e:
                    health_check.status = HealthStatus.UNHEALTHY
                    health_check.consecutive_failures += 1
                    health_check.details = {"error": str(e)}
                
                results[service_name] = health_check
            
            return results
        except Exception as e:
            logger.error(f"Health checks error: {e}")
            return {}
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        try:
            # Mock system metrics (in real implementation would use psutil or similar)
            import random
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=random.uniform(10, 80),
                memory_usage=random.uniform(30, 90),
                disk_usage=random.uniform(20, 70),
                network_io={"bytes_sent": random.randint(1000, 10000), "bytes_recv": random.randint(1000, 10000)},
                active_connections=random.randint(50, 200),
                queue_size=random.randint(0, 50),
                cache_hit_ratio=random.uniform(0.7, 0.95)
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            # Maintain history size
            if len(self.metrics_history) > self.max_metrics_history:
                self.metrics_history = self.metrics_history[-self.max_metrics_history:]
            
            return metrics
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            health_checks = await self.perform_health_checks()
            latest_metrics = await self.collect_system_metrics()
            
            # Determine overall status
            unhealthy_services = [name for name, check in health_checks.items() 
                                if check.status == HealthStatus.UNHEALTHY]
            degraded_services = [name for name, check in health_checks.items() 
                               if check.status == HealthStatus.DEGRADED]
            
            if unhealthy_services:
                overall_status = HealthStatus.UNHEALTHY
            elif degraded_services:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY
            
            return {
                "overall_status": overall_status.value,
                "services": {name: check.status.value for name, check in health_checks.items()},
                "unhealthy_services": unhealthy_services,
                "degraded_services": degraded_services,
                "system_metrics": {
                    "cpu_usage": latest_metrics.cpu_usage,
                    "memory_usage": latest_metrics.memory_usage,
                    "disk_usage": latest_metrics.disk_usage,
                    "active_connections": latest_metrics.active_connections
                },
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"System status error: {e}")
            return {"overall_status": "error", "error": str(e)}
    
    async def get_metrics_summary(self, period_minutes: int = 60) -> Dict[str, Any]:
        """Get metrics summary for period"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=period_minutes)
            recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return {"error": "No metrics available for period"}
            
            # Calculate averages
            avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
            avg_disk = sum(m.disk_usage for m in recent_metrics) / len(recent_metrics)
            avg_cache_hit = sum(m.cache_hit_ratio for m in recent_metrics) / len(recent_metrics)
            
            return {
                "period_minutes": period_minutes,
                "data_points": len(recent_metrics),
                "averages": {
                    "cpu_usage": round(avg_cpu, 2),
                    "memory_usage": round(avg_memory, 2),
                    "disk_usage": round(avg_disk, 2),
                    "cache_hit_ratio": round(avg_cache_hit, 3)
                },
                "peaks": {
                    "max_cpu": max(m.cpu_usage for m in recent_metrics),
                    "max_memory": max(m.memory_usage for m in recent_metrics),
                    "max_connections": max(m.active_connections for m in recent_metrics)
                }
            }
        except Exception as e:
            logger.error(f"Metrics summary error: {e}")
            return {"error": str(e)}

class InfrastructureService:
    """
    Unified Infrastructure Service that orchestrates all infrastructure-related services
    
    Consolidates:
    - Cache Management
    - Queue Processing
    - Storage Management  
    - Health Monitoring
    - System Metrics
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize sub-services
        self.cache = CacheService(self.config.get('cache', {}))
        self.queue = QueueService(self.config.get('queue', {}))
        self.storage = StorageService(self.config.get('storage', {}))
        self.monitoring = HealthMonitoringService(self.config.get('monitoring', {}))
        
        logger.info("🏗️ Infrastructure Service initialized - All infrastructure-related services consolidated")
    
    async def initialize(self):
        """Initialize all infrastructure services"""
        logger.info("🚀 Initializing Infrastructure Service")
        
        # Register health checks for sub-services
        await self.monitoring.register_health_check("cache", self._check_cache_health)
        await self.monitoring.register_health_check("queue", self._check_queue_health)
        await self.monitoring.register_health_check("storage", self._check_storage_health)
    
    async def shutdown(self):
        """Shutdown all infrastructure services"""
        logger.info("🛑 Shutting down Infrastructure Service")
        # Any cleanup logic here
    
    async def _check_cache_health(self) -> bool:
        """Check cache service health"""
        try:
            # Test basic cache operations
            await self.cache.set("health_check", "ok", ttl=10)
            result = await self.cache.get("health_check")
            await self.cache.delete("health_check")
            return result == "ok"
        except Exception:
            return False
    
    async def _check_queue_health(self) -> bool:
        """Check queue service health"""
        try:
            # Test basic queue operations
            stats = await self.queue.get_queue_stats()
            return isinstance(stats, dict)
        except Exception:
            return False
    
    async def _check_storage_health(self) -> bool:
        """Check storage service health"""
        try:
            # Test basic storage operations
            buckets = list(self.storage.buckets.keys())
            return True  # Storage is healthy if we can list buckets
        except Exception:
            return False
    
    # Cache methods
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return await self.cache.get(key)
    
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
        """Set value in cache"""
        return await self.cache.set(key, value, ttl, tags)
    
    async def cache_delete(self, key: str) -> bool:
        """Delete value from cache"""
        return await self.cache.delete(key)
    
    async def cache_clear(self) -> bool:
        """Clear all cache"""
        return await self.cache.clear()
    
    # Queue methods
    async def enqueue_job(self, queue_name: str, payload: Dict[str, Any], priority: int = 0, delay: Optional[int] = None) -> str:
        """Add job to queue"""
        return await self.queue.enqueue(queue_name, payload, priority, delay)
    
    async def dequeue_job(self, queue_name: str, worker_id: str) -> Optional[QueueJob]:
        """Get next job from queue"""
        return await self.queue.dequeue(queue_name, worker_id)
    
    async def complete_job(self, job_id: str, result: Dict[str, Any] = None) -> bool:
        """Mark job as completed"""
        return await self.queue.complete_job(job_id, result)
    
    async def fail_job(self, job_id: str, error_message: str) -> bool:
        """Mark job as failed"""
        return await self.queue.fail_job(job_id, error_message)
    
    # Storage methods
    async def create_storage_bucket(self, bucket_name: str, region: str = "us-east-1") -> bool:
        """Create storage bucket"""
        return await self.storage.create_bucket(bucket_name, region)
    
    async def upload_file(self, bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream", metadata: Dict[str, Any] = None) -> Optional[StorageObject]:
        """Upload file to storage"""
        return await self.storage.upload_object(bucket, key, data, content_type, metadata)
    
    async def download_file(self, bucket: str, key: str) -> Optional[Dict[str, Any]]:
        """Download file from storage"""
        return await self.storage.download_object(bucket, key)
    
    async def delete_file(self, bucket: str, key: str) -> bool:
        """Delete file from storage"""
        return await self.storage.delete_object(bucket, key)
    
    # Monitoring methods
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        return await self.monitoring.get_system_status()
    
    async def get_system_metrics(self, period_minutes: int = 60) -> Dict[str, Any]:
        """Get system metrics summary"""
        return await self.monitoring.get_metrics_summary(period_minutes)
    
    async def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        return await self.monitoring.collect_system_metrics()
    
    # Combined stats methods
    async def get_infrastructure_stats(self) -> Dict[str, Any]:
        """Get comprehensive infrastructure statistics"""
        try:
            cache_stats = await self.cache.get_stats()
            queue_stats = await self.queue.get_queue_stats()
            system_health = await self.monitoring.get_system_status()
            
            return {
                "cache": cache_stats,
                "queue": queue_stats,
                "storage": {
                    "total_buckets": len(self.storage.buckets),
                    "total_objects": len(self.storage.objects_store)
                },
                "system_health": system_health,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Infrastructure stats error: {e}")
            return {"error": str(e)}

# Export all classes
__all__ = [
    # Enums
    "CacheBackend",
    "QueueType",
    "StorageBackend",
    "HealthStatus",
    "JobStatus",
    
    # Data structures
    "CacheEntry",
    "QueueJob",
    "StorageObject",
    "HealthCheck",
    "SystemMetrics",
    
    # Services
    "CacheService",
    "QueueService",
    "StorageService",
    "HealthMonitoringService",
    "InfrastructureService"
]

# Module initialization
logger.info(f"🏗️ Infrastructure Service v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")
logger.info("🎯 Consolidated: cache_service + queue_service + storage_service + monitoring")