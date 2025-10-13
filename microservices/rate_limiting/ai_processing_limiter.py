"""
AI Processing Rate Limiter Enterprise - IA Chérie
===============================================
Rate Limiter spécialisé pour processing IA/ML.
GPU/CPU quotas + model complexity + processing queues.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Rate Limiting
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import statistics

from .distributed_rate_limiter import (
    DistributedRateLimiter, RateLimitConfig, RateLimitResult, 
    RateLimitAlgorithm, RateLimitStatus
)

logger = logging.getLogger(__name__)

class AIModelType(Enum):
    """Types de modèles IA"""
    AUDIO_ANALYSIS = "audio_analysis"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    MUSIC_GENERATION = "music_generation"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    VIDEO_ANALYSIS = "video_analysis"
    VIDEO_ENHANCEMENT = "video_enhancement"
    IMAGE_RECOGNITION = "image_recognition"
    IMAGE_GENERATION = "image_generation"
    CONTENT_MODERATION = "content_moderation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    LANGUAGE_TRANSLATION = "language_translation"
    RECOMMENDATION = "recommendation"
    TRENDING_PREDICTION = "trending_prediction"

class ProcessingPriority(Enum):
    """Priorités processing"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    REAL_TIME = "real_time"

class ResourceType(Enum):
    """Types de ressources"""
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"

class ModelComplexity(Enum):
    """Complexité modèles"""
    LIGHT = "light"        # < 100M parameters
    MEDIUM = "medium"      # 100M - 1B parameters
    LARGE = "large"        # 1B - 10B parameters
    EXTRA_LARGE = "xl"     # > 10B parameters

@dataclass
class AIProcessingLimits:
    """Limites processing IA par modèle"""
    model_type: AIModelType
    complexity: ModelComplexity
    gpu_time_seconds: int
    cpu_time_seconds: int
    memory_mb: int
    max_concurrent: int
    queue_priority: ProcessingPriority
    cost_per_second: float
    max_input_size_mb: int
    estimated_processing_time: int
    resource_requirements: Dict[ResourceType, float]
    user_tier_multipliers: Dict[str, float]
    
    @classmethod
    def get_default_limits(cls) -> Dict[AIModelType, 'AIProcessingLimits']:
        """Limites par défaut par modèle"""
        return {
            AIModelType.AUDIO_ANALYSIS: cls(
                model_type=AIModelType.AUDIO_ANALYSIS,
                complexity=ModelComplexity.MEDIUM,
                gpu_time_seconds=30,
                cpu_time_seconds=60,
                memory_mb=2048,
                max_concurrent=5,
                queue_priority=ProcessingPriority.NORMAL,
                cost_per_second=0.01,
                max_input_size_mb=100,
                estimated_processing_time=45,
                resource_requirements={
                    ResourceType.GPU: 0.5,
                    ResourceType.CPU: 2.0,
                    ResourceType.MEMORY: 2048,
                    ResourceType.STORAGE: 500
                },
                user_tier_multipliers={
                    "free": 0.5,
                    "basic": 1.0,
                    "pro": 2.0,
                    "enterprise": 5.0
                }
            ),
            AIModelType.SPEECH_TO_TEXT: cls(
                model_type=AIModelType.SPEECH_TO_TEXT,
                complexity=ModelComplexity.LARGE,
                gpu_time_seconds=60,
                cpu_time_seconds=120,
                memory_mb=4096,
                max_concurrent=3,
                queue_priority=ProcessingPriority.HIGH,
                cost_per_second=0.05,
                max_input_size_mb=200,
                estimated_processing_time=90,
                resource_requirements={
                    ResourceType.GPU: 1.0,
                    ResourceType.CPU: 4.0,
                    ResourceType.MEMORY: 4096,
                    ResourceType.STORAGE: 1000
                },
                user_tier_multipliers={
                    "free": 0.2,
                    "basic": 0.5,
                    "pro": 1.0,
                    "enterprise": 3.0
                }
            ),
            AIModelType.MUSIC_GENERATION: cls(
                model_type=AIModelType.MUSIC_GENERATION,
                complexity=ModelComplexity.EXTRA_LARGE,
                gpu_time_seconds=300,
                cpu_time_seconds=600,
                memory_mb=8192,
                max_concurrent=1,
                queue_priority=ProcessingPriority.LOW,
                cost_per_second=0.20,
                max_input_size_mb=50,
                estimated_processing_time=600,
                resource_requirements={
                    ResourceType.GPU: 2.0,
                    ResourceType.CPU: 8.0,
                    ResourceType.MEMORY: 8192,
                    ResourceType.STORAGE: 2000
                },
                user_tier_multipliers={
                    "free": 0.1,
                    "basic": 0.3,
                    "pro": 1.0,
                    "enterprise": 2.0
                }
            ),
            AIModelType.VIDEO_ANALYSIS: cls(
                model_type=AIModelType.VIDEO_ANALYSIS,
                complexity=ModelComplexity.LARGE,
                gpu_time_seconds=120,
                cpu_time_seconds=240,
                memory_mb=6144,
                max_concurrent=2,
                queue_priority=ProcessingPriority.NORMAL,
                cost_per_second=0.10,
                max_input_size_mb=500,
                estimated_processing_time=180,
                resource_requirements={
                    ResourceType.GPU: 1.5,
                    ResourceType.CPU: 6.0,
                    ResourceType.MEMORY: 6144,
                    ResourceType.STORAGE: 1500
                },
                user_tier_multipliers={
                    "free": 0.1,
                    "basic": 0.5,
                    "pro": 1.0,
                    "enterprise": 2.0
                }
            ),
            AIModelType.CONTENT_MODERATION: cls(
                model_type=AIModelType.CONTENT_MODERATION,
                complexity=ModelComplexity.MEDIUM,
                gpu_time_seconds=10,
                cpu_time_seconds=20,
                memory_mb=1024,
                max_concurrent=10,
                queue_priority=ProcessingPriority.CRITICAL,
                cost_per_second=0.005,
                max_input_size_mb=50,
                estimated_processing_time=15,
                resource_requirements={
                    ResourceType.GPU: 0.2,
                    ResourceType.CPU: 1.0,
                    ResourceType.MEMORY: 1024,
                    ResourceType.STORAGE: 200
                },
                user_tier_multipliers={
                    "free": 1.0,
                    "basic": 1.0,
                    "pro": 1.0,
                    "enterprise": 1.0
                }
            ),
            AIModelType.RECOMMENDATION: cls(
                model_type=AIModelType.RECOMMENDATION,
                complexity=ModelComplexity.LIGHT,
                gpu_time_seconds=5,
                cpu_time_seconds=10,
                memory_mb=512,
                max_concurrent=20,
                queue_priority=ProcessingPriority.REAL_TIME,
                cost_per_second=0.001,
                max_input_size_mb=10,
                estimated_processing_time=5,
                resource_requirements={
                    ResourceType.GPU: 0.1,
                    ResourceType.CPU: 0.5,
                    ResourceType.MEMORY: 512,
                    ResourceType.STORAGE: 100
                },
                user_tier_multipliers={
                    "free": 1.0,
                    "basic": 2.0,
                    "pro": 5.0,
                    "enterprise": 10.0
                }
            )
        }

@dataclass
class AIRequest:
    """Request processing IA"""
    request_id: str
    user_id: str
    model_type: AIModelType
    input_data_size_mb: float
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    user_tier: str = "free"
    expected_output_size_mb: Optional[float] = None
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_resource_cost(self, limits: AIProcessingLimits) -> Dict[str, float]:
        """Calcul coût ressources"""
        user_multiplier = limits.user_tier_multipliers.get(self.user_tier, 1.0)
        size_multiplier = max(1.0, self.input_data_size_mb / 10.0)  # +cost per 10MB
        
        return {
            "gpu_seconds": limits.gpu_time_seconds * user_multiplier * size_multiplier,
            "cpu_seconds": limits.cpu_time_seconds * user_multiplier * size_multiplier,
            "memory_mb": limits.memory_mb * size_multiplier,
            "total_cost": limits.cost_per_second * limits.gpu_time_seconds * user_multiplier * size_multiplier
        }

@dataclass
class AILimitResult:
    """Résultat rate limiting IA"""
    allowed: bool
    model_type: AIModelType
    queue_position: int
    estimated_wait_time_seconds: int
    resource_allocation: Dict[str, float]
    processing_cost: float
    rate_limit_result: RateLimitResult
    resource_warnings: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    alternative_models: List[AIModelType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceQuota:
    """Quota ressources utilisateur"""
    user_id: str
    gpu_seconds_quota: int
    cpu_seconds_quota: int
    memory_mb_quota: int
    used_gpu_seconds: float = 0.0
    used_cpu_seconds: float = 0.0
    used_memory_mb: float = 0.0
    reset_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    
    @property
    def gpu_remaining(self) -> float:
        return max(0.0, self.gpu_seconds_quota - self.used_gpu_seconds)
    
    @property
    def cpu_remaining(self) -> float:
        return max(0.0, self.cpu_seconds_quota - self.used_cpu_seconds)
    
    @property
    def memory_remaining(self) -> float:
        return max(0.0, self.memory_mb_quota - self.used_memory_mb)

@dataclass
class ProcessingJob:
    """Job processing en queue"""
    job_id: str
    request: AIRequest
    limits: AIProcessingLimits
    queued_at: datetime
    estimated_completion: datetime
    status: str = "queued"  # queued, processing, completed, failed
    
    @property
    def wait_time_seconds(self) -> int:
        return int((datetime.now() - self.queued_at).total_seconds())

class ResourceManager:
    """Gestionnaire ressources IA"""
    
    def __init__(self):
        self.available_resources = {
            ResourceType.GPU: 8.0,      # 8 GPU units available
            ResourceType.CPU: 32.0,     # 32 CPU cores
            ResourceType.MEMORY: 65536, # 64GB memory
            ResourceType.STORAGE: 1000000  # 1TB storage
        }
        self.allocated_resources = defaultdict(float)
        self.resource_history = deque(maxlen=1000)
        self.logger = logging.getLogger(__name__)
    
    async def check_resource_availability(self, requirements: Dict[ResourceType, float]) -> Dict[str, Any]:
        """Vérification disponibilité ressources"""
        availability = {}
        warnings = []
        
        for resource_type, required_amount in requirements.items():
            available = self.available_resources.get(resource_type, 0.0)
            allocated = self.allocated_resources.get(resource_type, 0.0)
            remaining = available - allocated
            
            availability[resource_type.value] = {
                "available": available,
                "allocated": allocated,
                "remaining": remaining,
                "required": required_amount,
                "sufficient": remaining >= required_amount
            }
            
            if remaining < required_amount:
                warnings.append(f"Insufficient {resource_type.value}: {remaining:.1f} available, {required_amount:.1f} required")
        
        return {
            "availability": availability,
            "all_sufficient": all(r["sufficient"] for r in availability.values()),
            "warnings": warnings
        }
    
    async def allocate_resources(self, requirements: Dict[ResourceType, float]) -> bool:
        """Allocation ressources"""
        # Vérification disponibilité
        availability = await self.check_resource_availability(requirements)
        
        if not availability["all_sufficient"]:
            return False
        
        # Allocation ressources
        for resource_type, amount in requirements.items():
            self.allocated_resources[resource_type] += amount
        
        # Enregistrement allocation
        allocation_record = {
            "timestamp": datetime.now(),
            "requirements": {rt.value: amt for rt, amt in requirements.items()},
            "total_allocated": dict(self.allocated_resources)
        }
        self.resource_history.append(allocation_record)
        
        return True
    
    async def release_resources(self, requirements: Dict[ResourceType, float]):
        """Libération ressources"""
        for resource_type, amount in requirements.items():
            current_allocated = self.allocated_resources.get(resource_type, 0.0)
            self.allocated_resources[resource_type] = max(0.0, current_allocated - amount)
    
    async def get_resource_stats(self) -> Dict[str, Any]:
        """Statistiques ressources"""
        stats = {}
        
        for resource_type, total_available in self.available_resources.items():
            allocated = self.allocated_resources.get(resource_type, 0.0)
            utilization = (allocated / total_available) * 100 if total_available > 0 else 0
            
            stats[resource_type.value] = {
                "total": total_available,
                "allocated": allocated,
                "free": total_available - allocated,
                "utilization_percent": utilization
            }
        
        return stats

class ProcessingQueue:
    """Queue processing IA avec priorités"""
    
    def __init__(self):
        self.queues = {
            ProcessingPriority.REAL_TIME: deque(),
            ProcessingPriority.CRITICAL: deque(),
            ProcessingPriority.HIGH: deque(),
            ProcessingPriority.NORMAL: deque(),
            ProcessingPriority.LOW: deque()
        }
        self.processing_jobs = {}  # job_id -> ProcessingJob
        self.completed_jobs = deque(maxlen=1000)
        self.logger = logging.getLogger(__name__)
    
    async def enqueue_job(self, job: ProcessingJob) -> int:
        """Ajout job à la queue"""
        priority = job.request.priority
        self.queues[priority].append(job)
        self.processing_jobs[job.job_id] = job
        
        # Calcul position dans queue
        position = 0
        for p in ProcessingPriority:
            if p == priority:
                position += len(self.queues[p])
                break
            else:
                position += len(self.queues[p])
        
        self.logger.info(f"Job {job.job_id} enqueued at position {position}")
        return position
    
    async def dequeue_next_job(self) -> Optional[ProcessingJob]:
        """Récupération prochain job par priorité"""
        for priority in ProcessingPriority:
            if self.queues[priority]:
                job = self.queues[priority].popleft()
                job.status = "processing"
                return job
        
        return None
    
    async def complete_job(self, job_id: str, success: bool = True):
        """Completion job"""
        if job_id in self.processing_jobs:
            job = self.processing_jobs[job_id]
            job.status = "completed" if success else "failed"
            
            # Archive job
            self.completed_jobs.append(job)
            del self.processing_jobs[job_id]
            
            self.logger.info(f"Job {job_id} completed: {job.status}")
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Statistiques queues"""
        return {
            "queued_by_priority": {
                priority.value: len(queue) 
                for priority, queue in self.queues.items()
            },
            "total_queued": sum(len(q) for q in self.queues.values()),
            "processing": len(self.processing_jobs),
            "completed_today": len([
                job for job in self.completed_jobs 
                if (datetime.now() - job.queued_at).days < 1
            ])
        }
    
    async def estimate_wait_time(self, priority: ProcessingPriority, 
                               model_type: AIModelType) -> int:
        """Estimation temps d'attente"""
        # Jobs avant ce priority level
        jobs_ahead = 0
        for p in ProcessingPriority:
            if p == priority:
                break
            jobs_ahead += len(self.queues[p])
        
        # Jobs dans même priority
        jobs_ahead += len(self.queues[priority])
        
        # Estimation basée sur temps processing moyen
        avg_processing_times = {
            AIModelType.RECOMMENDATION: 5,
            AIModelType.CONTENT_MODERATION: 15,
            AIModelType.AUDIO_ANALYSIS: 45,
            AIModelType.SPEECH_TO_TEXT: 90,
            AIModelType.VIDEO_ANALYSIS: 180,
            AIModelType.MUSIC_GENERATION: 600
        }
        
        avg_time = avg_processing_times.get(model_type, 60)
        estimated_wait = jobs_ahead * avg_time
        
        return estimated_wait

class AIProcessingRateLimiter:
    """
    Rate Limiter spécialisé pour processing IA/ML.
    GPU/CPU quotas + model complexity + processing queues.
    """
    
    def __init__(self, distributed_limiter: DistributedRateLimiter):
        self.distributed_limiter = distributed_limiter
        self.ai_processing_limits = AIProcessingLimits.get_default_limits()
        self.resource_manager = ResourceManager()
        self.processing_queue = ProcessingQueue()
        
        # Quotas utilisateurs
        self.resource_quotas = {}  # user_id -> ResourceQuota
        self.concurrent_jobs = defaultdict(int)  # user_id -> count
        
        # Métriques IA
        self.ai_metrics = {
            "total_ai_requests": 0,
            "gpu_seconds_used": 0.0,
            "cpu_seconds_used": 0.0,
            "total_processing_cost": 0.0,
            "model_type_distribution": defaultdict(int),
            "average_queue_wait_time": 0.0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._background_tasks = []
        self._stop_event = asyncio.Event()
    
    async def initialize(self) -> bool:
        """Initialisation AI processing rate limiter"""
        try:
            # Initialisation distributed limiter base
            await self.distributed_limiter.initialize()
            
            # Chargement quotas par défaut
            await self._load_default_resource_quotas()
            
            # Démarrage background tasks
            await self._start_background_tasks()
            
            self.logger.info("AI processing rate limiter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"AI processing rate limiter initialization failed: {e}")
            return False
    
    async def limit_ai_processing_requests(self, request: AIRequest) -> AILimitResult:
        """Rate limiting pour requests IA processing avec resource awareness"""
        start_time = time.time()
        self.ai_metrics["total_ai_requests"] += 1
        self.ai_metrics["model_type_distribution"][request.model_type.value] += 1
        
        try:
            # 1. Récupération limites pour modèle
            limits = self.ai_processing_limits.get(request.model_type)
            if not limits:
                return AILimitResult(
                    allowed=False,
                    model_type=request.model_type,
                    queue_position=0,
                    estimated_wait_time_seconds=0,
                    resource_allocation={},
                    processing_cost=0.0,
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.ERROR,
                        allowed=False
                    ),
                    resource_warnings=["Unsupported AI model type"]
                )
            
            # 2. Vérification taille input
            if request.input_data_size_mb > limits.max_input_size_mb:
                return AILimitResult(
                    allowed=False,
                    model_type=request.model_type,
                    queue_position=0,
                    estimated_wait_time_seconds=0,
                    resource_allocation={},
                    processing_cost=0.0,
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.DENIED,
                        allowed=False
                    ),
                    resource_warnings=[f"Input size {request.input_data_size_mb}MB exceeds limit {limits.max_input_size_mb}MB"]
                )
            
            # 3. Calcul coût ressources
            resource_cost = request.calculate_resource_cost(limits)
            
            # 4. Vérification quota ressources utilisateur
            quota_check = await self._check_resource_quota(request.user_id, resource_cost, request.user_tier)
            if not quota_check["allowed"]:
                return AILimitResult(
                    allowed=False,
                    model_type=request.model_type,
                    queue_position=0,
                    estimated_wait_time_seconds=0,
                    resource_allocation=resource_cost,
                    processing_cost=resource_cost["total_cost"],
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.DENIED,
                        allowed=False
                    ),
                    resource_warnings=quota_check["warnings"]
                )
            
            # 5. Vérification concurrence utilisateur
            concurrent_check = await self._check_concurrent_jobs(request.user_id, limits)
            if not concurrent_check["allowed"]:
                return AILimitResult(
                    allowed=False,
                    model_type=request.model_type,
                    queue_position=0,
                    estimated_wait_time_seconds=0,
                    resource_allocation=resource_cost,
                    processing_cost=resource_cost["total_cost"],
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.THROTTLED,
                        allowed=False
                    ),
                    resource_warnings=concurrent_check["warnings"]
                )
            
            # 6. Vérification disponibilité ressources globales
            resource_requirements = {
                ResourceType.GPU: resource_cost["gpu_seconds"] / 60,  # Convert to concurrent units
                ResourceType.CPU: resource_cost["cpu_seconds"] / 60,
                ResourceType.MEMORY: resource_cost["memory_mb"],
                ResourceType.STORAGE: request.input_data_size_mb
            }
            
            resource_availability = await self.resource_manager.check_resource_availability(resource_requirements)
            
            # 7. Vérification rate limiting distribué
            ai_tokens = int(resource_cost["total_cost"] * 100)  # Convert cost to tokens
            rate_limit_result = await self.distributed_limiter.check_rate_limit(
                f"ai:{request.user_id}:{request.model_type.value}",
                ai_tokens,
                {
                    "model_type": request.model_type.value,
                    "complexity": limits.complexity.value,
                    "resource_cost": resource_cost,
                    "priority": request.priority.value
                }
            )
            
            if not rate_limit_result.allowed:
                return AILimitResult(
                    allowed=False,
                    model_type=request.model_type,
                    queue_position=0,
                    estimated_wait_time_seconds=0,
                    resource_allocation=resource_cost,
                    processing_cost=resource_cost["total_cost"],
                    rate_limit_result=rate_limit_result,
                    resource_warnings=["Rate limit exceeded for AI processing"]
                )
            
            # 8. Création job processing
            job = ProcessingJob(
                job_id=request.request_id,
                request=request,
                limits=limits,
                queued_at=datetime.now(),
                estimated_completion=datetime.now() + timedelta(seconds=limits.estimated_processing_time)
            )
            
            # 9. Ajout à la queue ou processing immédiat
            if resource_availability["all_sufficient"]:
                # Ressources disponibles - processing immédiat possible
                queue_position = await self.processing_queue.enqueue_job(job)
                
                # Tentative allocation ressources
                allocated = await self.resource_manager.allocate_resources(resource_requirements)
                if allocated:
                    # Update quotas utilisateur
                    await self._update_resource_quota(request.user_id, resource_cost)
                    await self._update_concurrent_jobs(request.user_id, 1)
                    
                    # Update métriques globales
                    self.ai_metrics["gpu_seconds_used"] += resource_cost["gpu_seconds"]
                    self.ai_metrics["cpu_seconds_used"] += resource_cost["cpu_seconds"]
                    self.ai_metrics["total_processing_cost"] += resource_cost["total_cost"]
                    
                    wait_time = 0  # Processing immédiat
                else:
                    # Ressources occupées malgré vérification
                    wait_time = await self.processing_queue.estimate_wait_time(
                        request.priority, request.model_type
                    )
            else:
                # Ressources insuffisantes - ajout à la queue
                queue_position = await self.processing_queue.enqueue_job(job)
                wait_time = await self.processing_queue.estimate_wait_time(
                    request.priority, request.model_type
                )
            
            # 10. Génération suggestions optimisation
            optimization_suggestions = await self._generate_optimization_suggestions(
                request, limits, resource_availability
            )
            
            # 11. Modèles alternatifs si ressources insuffisantes
            alternative_models = []
            if not resource_availability["all_sufficient"]:
                alternative_models = await self._suggest_alternative_models(request.model_type)
            
            # 12. Construction résultat final
            result = AILimitResult(
                allowed=True,
                model_type=request.model_type,
                queue_position=queue_position,
                estimated_wait_time_seconds=wait_time,
                resource_allocation=resource_cost,
                processing_cost=resource_cost["total_cost"],
                rate_limit_result=rate_limit_result,
                resource_warnings=resource_availability["warnings"],
                optimization_suggestions=optimization_suggestions,
                alternative_models=alternative_models,
                metadata={
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "complexity": limits.complexity.value,
                    "estimated_processing_seconds": limits.estimated_processing_time,
                    "resource_availability": resource_availability["availability"]
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"AI processing rate limiting failed for {request.user_id}: {e}")
            return AILimitResult(
                allowed=False,
                model_type=request.model_type,
                queue_position=0,
                estimated_wait_time_seconds=0,
                resource_allocation={},
                processing_cost=0.0,
                rate_limit_result=RateLimitResult(
                    status=RateLimitStatus.ERROR,
                    allowed=False
                ),
                resource_warnings=[f"Processing error: {str(e)}"],
                metadata={"error": str(e)}
            )
    
    async def _check_resource_quota(self, user_id: str, resource_cost: Dict[str, float],
                                  user_tier: str) -> Dict[str, Any]:
        """Vérification quota ressources utilisateur"""
        quota = await self._get_or_create_resource_quota(user_id, user_tier)
        
        warnings = []
        
        # Vérification GPU quota
        if resource_cost["gpu_seconds"] > quota.gpu_remaining:
            warnings.append(f"GPU quota exceeded: {resource_cost['gpu_seconds']:.1f}s required, {quota.gpu_remaining:.1f}s remaining")
        
        # Vérification CPU quota
        if resource_cost["cpu_seconds"] > quota.cpu_remaining:
            warnings.append(f"CPU quota exceeded: {resource_cost['cpu_seconds']:.1f}s required, {quota.cpu_remaining:.1f}s remaining")
        
        # Vérification Memory quota
        if resource_cost["memory_mb"] > quota.memory_remaining:
            warnings.append(f"Memory quota exceeded: {resource_cost['memory_mb']:.1f}MB required, {quota.memory_remaining:.1f}MB remaining")
        
        return {
            "allowed": len(warnings) == 0,
            "warnings": warnings
        }
    
    async def _check_concurrent_jobs(self, user_id: str, limits: AIProcessingLimits) -> Dict[str, Any]:
        """Vérification jobs concurrents utilisateur"""
        current_concurrent = self.concurrent_jobs.get(user_id, 0)
        user_multiplier = limits.user_tier_multipliers.get("free", 1.0)  # Simplified
        max_concurrent = int(limits.max_concurrent * user_multiplier)
        
        if current_concurrent >= max_concurrent:
            return {
                "allowed": False,
                "warnings": [f"Concurrent jobs limit reached: {current_concurrent}/{max_concurrent}"]
            }
        
        return {"allowed": True, "warnings": []}
    
    async def _get_or_create_resource_quota(self, user_id: str, user_tier: str) -> ResourceQuota:
        """Récupération ou création quota ressources"""
        if user_id not in self.resource_quotas:
            # Quotas basés sur tier utilisateur
            tier_quotas = {
                "free": {"gpu": 300, "cpu": 600, "memory": 2048},      # 5min GPU, 10min CPU, 2GB
                "basic": {"gpu": 1800, "cpu": 3600, "memory": 8192},   # 30min GPU, 1h CPU, 8GB
                "pro": {"gpu": 7200, "cpu": 14400, "memory": 32768},   # 2h GPU, 4h CPU, 32GB
                "enterprise": {"gpu": 28800, "cpu": 57600, "memory": 131072}  # 8h GPU, 16h CPU, 128GB
            }
            
            quotas = tier_quotas.get(user_tier, tier_quotas["free"])
            
            self.resource_quotas[user_id] = ResourceQuota(
                user_id=user_id,
                gpu_seconds_quota=quotas["gpu"],
                cpu_seconds_quota=quotas["cpu"],
                memory_mb_quota=quotas["memory"]
            )
        
        # Vérification reset si nécessaire
        quota = self.resource_quotas[user_id]
        if datetime.now() > quota.reset_date:
            quota.used_gpu_seconds = 0.0
            quota.used_cpu_seconds = 0.0
            quota.used_memory_mb = 0.0
            quota.reset_date = datetime.now() + timedelta(hours=24)
        
        return quota
    
    async def _update_resource_quota(self, user_id: str, resource_cost: Dict[str, float]):
        """Update quota ressources"""
        quota = self.resource_quotas.get(user_id)
        if quota:
            quota.used_gpu_seconds += resource_cost["gpu_seconds"]
            quota.used_cpu_seconds += resource_cost["cpu_seconds"]
            quota.used_memory_mb += resource_cost["memory_mb"]
    
    async def _update_concurrent_jobs(self, user_id: str, delta: int):
        """Update compteur jobs concurrents"""
        self.concurrent_jobs[user_id] = max(0, self.concurrent_jobs[user_id] + delta)
    
    async def _generate_optimization_suggestions(self, request: AIRequest,
                                               limits: AIProcessingLimits,
                                               resource_availability: Dict[str, Any]) -> List[str]:
        """Génération suggestions optimisation"""
        suggestions = []
        
        # Suggestions taille input
        if request.input_data_size_mb > 50:
            suggestions.append("Consider reducing input size for faster processing")
        
        # Suggestions priorité
        if request.priority == ProcessingPriority.LOW and not resource_availability["all_sufficient"]:
            suggestions.append("Increase priority for faster queue processing")
        
        # Suggestions modèle
        if limits.complexity == ModelComplexity.EXTRA_LARGE:
            suggestions.append("Consider using a lighter model for reduced resource usage")
        
        # Suggestions timing
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            suggestions.append("Process during off-peak hours for better resource availability")
        
        return suggestions
    
    async def _suggest_alternative_models(self, current_model: AIModelType) -> List[AIModelType]:
        """Suggestion modèles alternatifs"""
        alternatives = {
            AIModelType.MUSIC_GENERATION: [AIModelType.AUDIO_ANALYSIS, AIModelType.AUDIO_ENHANCEMENT],
            AIModelType.VIDEO_ANALYSIS: [AIModelType.IMAGE_RECOGNITION, AIModelType.CONTENT_MODERATION],
            AIModelType.SPEECH_TO_TEXT: [AIModelType.AUDIO_ANALYSIS],
            AIModelType.VIDEO_ENHANCEMENT: [AIModelType.VIDEO_ANALYSIS]
        }
        
        return alternatives.get(current_model, [])
    
    async def _load_default_resource_quotas(self):
        """Chargement quotas ressources par défaut"""
        # Les quotas sont créés dynamiquement lors de la première requête
        pass
    
    async def _start_background_tasks(self):
        """Démarrage tâches background"""
        # Tâche processing jobs en queue
        job_processor_task = asyncio.create_task(self._job_processing_loop())
        self._background_tasks.append(job_processor_task)
        
        # Tâche reset quotas ressources
        quota_reset_task = asyncio.create_task(self._resource_quota_reset_loop())
        self._background_tasks.append(quota_reset_task)
        
        # Tâche cleanup ressources
        resource_cleanup_task = asyncio.create_task(self._resource_cleanup_loop())
        self._background_tasks.append(resource_cleanup_task)
        
        # Tâche analysis performance IA
        performance_task = asyncio.create_task(self._ai_performance_analysis_loop())
        self._background_tasks.append(performance_task)
    
    async def _job_processing_loop(self):
        """Loop processing jobs en queue"""
        while not self._stop_event.is_set():
            try:
                # Récupération prochain job
                job = await self.processing_queue.dequeue_next_job()
                
                if job:
                    # Simulation processing
                    processing_time = job.limits.estimated_processing_time
                    await asyncio.sleep(min(processing_time, 5))  # Max 5s pour simulation
                    
                    # Completion job
                    await self.processing_queue.complete_job(job.job_id, success=True)
                    
                    # Libération ressources
                    resource_requirements = {
                        ResourceType.GPU: job.request.calculate_resource_cost(job.limits)["gpu_seconds"] / 60,
                        ResourceType.CPU: job.request.calculate_resource_cost(job.limits)["cpu_seconds"] / 60,
                        ResourceType.MEMORY: job.request.calculate_resource_cost(job.limits)["memory_mb"]
                    }
                    
                    await self.resource_manager.release_resources(resource_requirements)
                    await self._update_concurrent_jobs(job.request.user_id, -1)
                    
                    self.logger.info(f"Job {job.job_id} processing completed")
                else:
                    # Pas de jobs - attente
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Job processing loop error: {e}")
                await asyncio.sleep(5)
    
    async def _resource_quota_reset_loop(self):
        """Loop reset quotas ressources"""
        while not self._stop_event.is_set():
            try:
                now = datetime.now()
                for user_id, quota in self.resource_quotas.items():
                    if now > quota.reset_date:
                        quota.used_gpu_seconds = 0.0
                        quota.used_cpu_seconds = 0.0
                        quota.used_memory_mb = 0.0
                        quota.reset_date = now + timedelta(hours=24)
                        self.logger.info(f"Resource quota reset for user {user_id}")
                
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                self.logger.error(f"Resource quota reset error: {e}")
                await asyncio.sleep(300)
    
    async def _resource_cleanup_loop(self):
        """Loop cleanup ressources"""
        while not self._stop_event.is_set():
            try:
                # Cleanup ressources "perdues"
                for resource_type in ResourceType:
                    current_allocated = self.resource_manager.allocated_resources.get(resource_type, 0.0)
                    if current_allocated > 0:
                        # Gradual cleanup pour ressources potentiellement perdues
                        cleanup_amount = current_allocated * 0.1  # 10% cleanup per cycle
                        self.resource_manager.allocated_resources[resource_type] = max(0.0, 
                                                                                      current_allocated - cleanup_amount)
                
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                self.logger.error(f"Resource cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def _ai_performance_analysis_loop(self):
        """Loop analyse performance IA"""
        while not self._stop_event.is_set():
            try:
                # Analyse distribution modèles
                total_requests = sum(self.ai_metrics["model_type_distribution"].values())
                if total_requests > 0:
                    self.logger.info(f"AI model usage distribution: {dict(self.ai_metrics['model_type_distribution'])}")
                
                # Analyse utilisation ressources
                resource_stats = await self.resource_manager.get_resource_stats()
                self.logger.info(f"Resource utilization: {resource_stats}")
                
                # Update métriques queue
                queue_stats = await self.processing_queue.get_queue_stats()
                if queue_stats["total_queued"] > 0:
                    # Estimation temps d'attente moyen
                    avg_wait = sum(
                        job.wait_time_seconds 
                        for job in self.processing_queue.processing_jobs.values()
                    ) / len(self.processing_queue.processing_jobs) if self.processing_queue.processing_jobs else 0
                    
                    self.ai_metrics["average_queue_wait_time"] = avg_wait
                
                await asyncio.sleep(1800)  # Every 30 minutes
            except Exception as e:
                self.logger.error(f"AI performance analysis error: {e}")
                await asyncio.sleep(600)
    
    async def complete_ai_processing(self, request_id: str, success: bool = True) -> bool:
        """Completion processing IA"""
        try:
            await self.processing_queue.complete_job(request_id, success)
            self.logger.info(f"AI processing completed for request {request_id}: {'success' if success else 'failed'}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to complete AI processing: {e}")
            return False
    
    async def get_ai_processing_status(self, user_id: str) -> Dict[str, Any]:
        """Status processing IA utilisateur"""
        try:
            resource_quota = self.resource_quotas.get(user_id)
            concurrent_jobs = self.concurrent_jobs.get(user_id, 0)
            
            # Jobs utilisateur en queue
            user_jobs = [
                job for job in self.processing_queue.processing_jobs.values()
                if job.request.user_id == user_id
            ]
            
            return {
                "user_id": user_id,
                "resource_quota": {
                    "gpu_used": resource_quota.used_gpu_seconds if resource_quota else 0,
                    "gpu_remaining": resource_quota.gpu_remaining if resource_quota else 0,
                    "cpu_used": resource_quota.used_cpu_seconds if resource_quota else 0,
                    "cpu_remaining": resource_quota.cpu_remaining if resource_quota else 0,
                    "memory_used": resource_quota.used_memory_mb if resource_quota else 0,
                    "memory_remaining": resource_quota.memory_remaining if resource_quota else 0,
                    "reset_date": resource_quota.reset_date.isoformat() if resource_quota else None
                },
                "concurrent_jobs": concurrent_jobs,
                "queued_jobs": [
                    {
                        "job_id": job.job_id,
                        "model_type": job.request.model_type.value,
                        "status": job.status,
                        "queued_at": job.queued_at.isoformat(),
                        "wait_time_seconds": job.wait_time_seconds
                    } for job in user_jobs
                ],
                "global_metrics": self.ai_metrics,
                "resource_stats": await self.resource_manager.get_resource_stats(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}

# Factory functions
def create_audio_ai_limiter(redis_client) -> AIProcessingRateLimiter:
    """Factory pour limiter IA audio"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=30,
        burst_capacity=60,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        redis_key_prefix="audio_ai_rl"
    ))
    
    return AIProcessingRateLimiter(base_limiter)

def create_video_ai_limiter(redis_client) -> AIProcessingRateLimiter:
    """Factory pour limiter IA vidéo"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=10,  # Plus restrictif pour vidéo
        burst_capacity=20,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.LEAKY_BUCKET,
        redis_key_prefix="video_ai_rl"
    ))
    
    return AIProcessingRateLimiter(base_limiter)

def create_realtime_ai_limiter(redis_client) -> AIProcessingRateLimiter:
    """Factory pour limiter IA temps réel"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=100,  # Plus permissif pour temps réel
        burst_capacity=200,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        redis_key_prefix="realtime_ai_rl"
    ))
    
    return AIProcessingRateLimiter(base_limiter)

# Export classes principales
__all__ = [
    'AIProcessingRateLimiter',
    'AIRequest',
    'AILimitResult',
    'AIModelType',
    'ProcessingPriority',
    'ModelComplexity',
    'ResourceType',
    'AIProcessingLimits',
    'ResourceQuota',
    'create_audio_ai_limiter',
    'create_video_ai_limiter',
    'create_realtime_ai_limiter'
]