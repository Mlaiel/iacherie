"""
Content-Aware Rate Limiter Enterprise - Ainflue
===============================================
Rate Limiter spécialisé pour types de contenu Ainflue.
Audio/Video/Image upload limits + processing costs + quality tiers.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Rate Limiting
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
import mimetypes
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

class ContentType(Enum):
    """Types de contenu supportés"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    LIVESTREAM = "livestream"
    PODCAST = "podcast"
    THUMBNAIL = "thumbnail"
    SUBTITLE = "subtitle"
    METADATA = "metadata"

class QualityTier(Enum):
    """Tiers de qualité contenu"""
    STANDARD = "standard"
    HIGH = "high"
    PROFESSIONAL = "professional"
    STUDIO = "studio"
    RAW = "raw"
    COMPRESSED = "compressed"

class ProcessingType(Enum):
    """Types de processing"""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    TRANSCODING = "transcoding"
    AI_ANALYSIS = "ai_analysis"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    PREVIEW_GENERATION = "preview_generation"
    COMPRESSION = "compression"
    ENHANCEMENT = "enhancement"
    STREAMING = "streaming"

class BandwidthUnit(Enum):
    """Unités bandwidth"""
    BYTES = "bytes"
    KB = "kb"
    MB = "mb"
    GB = "gb"
    MBPS = "mbps"
    GBPS = "gbps"

@dataclass
class ContentLimitsMatrix:
    """Matrice limites par type contenu"""
    content_type: ContentType
    upload_rate_mb_per_hour: int
    download_rate_mb_per_hour: int
    processing_cost_tokens: int
    max_file_size_mb: int
    max_concurrent_uploads: int
    max_concurrent_downloads: int
    quality_multipliers: Dict[QualityTier, float]
    processing_multipliers: Dict[ProcessingType, float]
    user_tier_multipliers: Dict[str, float]
    
    @classmethod
    def get_default_matrix(cls) -> Dict[ContentType, 'ContentLimitsMatrix']:
        """Matrice limites par défaut"""
        return {
            ContentType.AUDIO: cls(
                content_type=ContentType.AUDIO,
                upload_rate_mb_per_hour=500,
                download_rate_mb_per_hour=1000,
                processing_cost_tokens=10,
                max_file_size_mb=100,
                max_concurrent_uploads=5,
                max_concurrent_downloads=10,
                quality_multipliers={
                    QualityTier.STANDARD: 1.0,
                    QualityTier.HIGH: 1.5,
                    QualityTier.PROFESSIONAL: 2.0,
                    QualityTier.STUDIO: 3.0,
                    QualityTier.RAW: 4.0
                },
                processing_multipliers={
                    ProcessingType.UPLOAD: 1.0,
                    ProcessingType.TRANSCODING: 2.0,
                    ProcessingType.AI_ANALYSIS: 3.0,
                    ProcessingType.ENHANCEMENT: 2.5
                },
                user_tier_multipliers={
                    "free": 1.0,
                    "basic": 2.0,
                    "pro": 5.0,
                    "enterprise": 10.0
                }
            ),
            ContentType.VIDEO: cls(
                content_type=ContentType.VIDEO,
                upload_rate_mb_per_hour=2000,
                download_rate_mb_per_hour=5000,
                processing_cost_tokens=50,
                max_file_size_mb=1000,
                max_concurrent_uploads=3,
                max_concurrent_downloads=8,
                quality_multipliers={
                    QualityTier.STANDARD: 1.0,      # 720p
                    QualityTier.HIGH: 2.0,          # 1080p
                    QualityTier.PROFESSIONAL: 4.0,  # 4K
                    QualityTier.STUDIO: 8.0,        # 8K
                    QualityTier.RAW: 10.0          # RAW video
                },
                processing_multipliers={
                    ProcessingType.UPLOAD: 1.0,
                    ProcessingType.TRANSCODING: 5.0,
                    ProcessingType.AI_ANALYSIS: 4.0,
                    ProcessingType.THUMBNAIL_GENERATION: 1.5,
                    ProcessingType.COMPRESSION: 3.0
                },
                user_tier_multipliers={
                    "free": 0.5,
                    "basic": 1.0,
                    "pro": 3.0,
                    "enterprise": 8.0
                }
            ),
            ContentType.LIVESTREAM: cls(
                content_type=ContentType.LIVESTREAM,
                upload_rate_mb_per_hour=10000,  # Higher for streaming
                download_rate_mb_per_hour=20000,
                processing_cost_tokens=100,
                max_file_size_mb=0,  # N/A for livestream
                max_concurrent_uploads=1,
                max_concurrent_downloads=100,
                quality_multipliers={
                    QualityTier.STANDARD: 1.0,      # 720p
                    QualityTier.HIGH: 2.0,          # 1080p
                    QualityTier.PROFESSIONAL: 4.0,  # 4K
                    QualityTier.STUDIO: 6.0         # 4K Ultra
                },
                processing_multipliers={
                    ProcessingType.STREAMING: 1.0,
                    ProcessingType.AI_ANALYSIS: 2.0,
                    ProcessingType.TRANSCODING: 3.0
                },
                user_tier_multipliers={
                    "free": 0.2,  # Very limited for free
                    "basic": 0.5,
                    "pro": 1.0,
                    "enterprise": 3.0
                }
            ),
            ContentType.IMAGE: cls(
                content_type=ContentType.IMAGE,
                upload_rate_mb_per_hour=200,
                download_rate_mb_per_hour=500,
                processing_cost_tokens=5,
                max_file_size_mb=50,
                max_concurrent_uploads=10,
                max_concurrent_downloads=20,
                quality_multipliers={
                    QualityTier.STANDARD: 1.0,
                    QualityTier.HIGH: 1.5,
                    QualityTier.PROFESSIONAL: 2.5,
                    QualityTier.RAW: 4.0
                },
                processing_multipliers={
                    ProcessingType.UPLOAD: 1.0,
                    ProcessingType.AI_ANALYSIS: 2.0,
                    ProcessingType.ENHANCEMENT: 1.5,
                    ProcessingType.COMPRESSION: 1.2
                },
                user_tier_multipliers={
                    "free": 1.0,
                    "basic": 3.0,
                    "pro": 8.0,
                    "enterprise": 15.0
                }
            )
        }

@dataclass
class ContentRequest:
    """Request avec contexte contenu"""
    identifier: str
    content_type: ContentType
    processing_type: ProcessingType
    file_size_mb: float
    quality_tier: QualityTier = QualityTier.STANDARD
    user_tier: str = "free"
    mime_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    resolution: Optional[str] = None
    bitrate: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_processing_cost(self, limits_matrix: ContentLimitsMatrix) -> int:
        """Calcul coût processing"""
        base_cost = limits_matrix.processing_cost_tokens
        
        # Multiplier qualité
        quality_multiplier = limits_matrix.quality_multipliers.get(self.quality_tier, 1.0)
        
        # Multiplier processing type
        processing_multiplier = limits_matrix.processing_multipliers.get(self.processing_type, 1.0)
        
        # Multiplier user tier
        user_multiplier = limits_matrix.user_tier_multipliers.get(self.user_tier, 1.0)
        
        # Multiplier taille fichier
        size_multiplier = max(1.0, self.file_size_mb / 10.0)  # +10% per 10MB
        
        total_cost = base_cost * quality_multiplier * processing_multiplier * user_multiplier * size_multiplier
        return int(total_cost)

@dataclass
class ContentLimitResult:
    """Résultat rate limiting contenu"""
    allowed: bool
    content_type: ContentType
    processing_type: ProcessingType
    bandwidth_consumed_mb: float
    processing_tokens_used: int
    quality_tier_applied: QualityTier
    concurrent_operations: int
    rate_limit_result: RateLimitResult
    content_warnings: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    estimated_processing_time: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BandwidthQuota:
    """Quota bandwidth par utilisateur"""
    user_id: str
    upload_quota_mb: int
    download_quota_mb: int
    used_upload_mb: float = 0.0
    used_download_mb: float = 0.0
    reset_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    @property
    def upload_remaining_mb(self) -> float:
        return max(0.0, self.upload_quota_mb - self.used_upload_mb)
    
    @property
    def download_remaining_mb(self) -> float:
        return max(0.0, self.download_quota_mb - self.used_download_mb)
    
    @property
    def upload_usage_percentage(self) -> float:
        if self.upload_quota_mb <= 0:
            return 0.0
        return min(100.0, (self.used_upload_mb / self.upload_quota_mb) * 100)

class ContentAnalyzer:
    """Analyseur contenu pour optimisation rate limiting"""
    
    def __init__(self):
        self.content_patterns = defaultdict(lambda: deque(maxlen=1000))
        self.processing_stats = defaultdict(lambda: {"total_time": 0, "count": 0})
        self.logger = logging.getLogger(__name__)
    
    async def analyze_content_characteristics(self, request: ContentRequest) -> Dict[str, Any]:
        """Analyse caractéristiques contenu"""
        try:
            characteristics = {
                "content_type": request.content_type.value,
                "estimated_processing_complexity": await self._estimate_processing_complexity(request),
                "bandwidth_impact": await self._estimate_bandwidth_impact(request),
                "resource_requirements": await self._estimate_resource_requirements(request),
                "optimization_opportunities": await self._identify_optimization_opportunities(request)
            }
            
            return characteristics
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            return {"error": str(e)}
    
    async def _estimate_processing_complexity(self, request: ContentRequest) -> str:
        """Estimation complexité processing"""
        complexity_score = 0
        
        # Score basé sur type contenu
        type_scores = {
            ContentType.AUDIO: 2,
            ContentType.VIDEO: 5,
            ContentType.LIVESTREAM: 8,
            ContentType.IMAGE: 1
        }
        complexity_score += type_scores.get(request.content_type, 1)
        
        # Score basé sur qualité
        quality_scores = {
            QualityTier.STANDARD: 1,
            QualityTier.HIGH: 2,
            QualityTier.PROFESSIONAL: 4,
            QualityTier.STUDIO: 6,
            QualityTier.RAW: 8
        }
        complexity_score += quality_scores.get(request.quality_tier, 1)
        
        # Score basé sur taille
        if request.file_size_mb > 100:
            complexity_score += 3
        elif request.file_size_mb > 50:
            complexity_score += 2
        elif request.file_size_mb > 10:
            complexity_score += 1
        
        # Classification
        if complexity_score >= 12:
            return "very_high"
        elif complexity_score >= 8:
            return "high"
        elif complexity_score >= 5:
            return "medium"
        else:
            return "low"
    
    async def _estimate_bandwidth_impact(self, request: ContentRequest) -> Dict[str, float]:
        """Estimation impact bandwidth"""
        # Base bandwidth = file size
        base_bandwidth = request.file_size_mb
        
        # Multipliers basés sur processing type
        processing_multipliers = {
            ProcessingType.UPLOAD: 1.0,
            ProcessingType.DOWNLOAD: 1.0,
            ProcessingType.STREAMING: 2.0,  # Higher bandwidth for streaming
            ProcessingType.TRANSCODING: 1.5,  # Additional bandwidth for transcoding
            ProcessingType.AI_ANALYSIS: 0.5   # Lower bandwidth for analysis
        }
        
        multiplier = processing_multipliers.get(request.processing_type, 1.0)
        estimated_bandwidth = base_bandwidth * multiplier
        
        return {
            "estimated_mb": estimated_bandwidth,
            "peak_mbps": estimated_bandwidth / 60,  # Assume 1 minute transfer
            "sustained_mbps": estimated_bandwidth / 300  # Assume 5 minute transfer
        }
    
    async def _estimate_resource_requirements(self, request: ContentRequest) -> Dict[str, Any]:
        """Estimation besoins ressources"""
        # CPU requirements
        cpu_base = {
            ContentType.AUDIO: 1,
            ContentType.VIDEO: 4,
            ContentType.LIVESTREAM: 6,
            ContentType.IMAGE: 1
        }.get(request.content_type, 1)
        
        # GPU requirements (pour certains processing types)
        gpu_required = request.processing_type in [
            ProcessingType.AI_ANALYSIS,
            ProcessingType.ENHANCEMENT,
            ProcessingType.TRANSCODING
        ]
        
        # Memory requirements
        memory_mb = max(100, request.file_size_mb * 2)  # At least 2x file size
        
        # Storage requirements
        storage_mb = request.file_size_mb
        if request.processing_type == ProcessingType.TRANSCODING:
            storage_mb *= 2  # Temporary storage for transcoding
        
        return {
            "cpu_cores": cpu_base,
            "gpu_required": gpu_required,
            "memory_mb": memory_mb,
            "storage_mb": storage_mb,
            "network_bandwidth_mbps": request.file_size_mb / 60  # 1 min transfer
        }
    
    async def _identify_optimization_opportunities(self, request: ContentRequest) -> List[str]:
        """Identification opportunités optimisation"""
        opportunities = []
        
        # Optimisation taille fichier
        if request.file_size_mb > 100:
            opportunities.append("Consider file compression to reduce size")
        
        # Optimisation qualité
        if (request.quality_tier in [QualityTier.STUDIO, QualityTier.RAW] and 
            request.user_tier == "free"):
            opportunities.append("Reduce quality tier for better rate limits")
        
        # Optimisation processing
        if request.processing_type == ProcessingType.AI_ANALYSIS:
            opportunities.append("Batch multiple files for efficient processing")
        
        # Optimisation timing
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            opportunities.append("Consider processing during off-peak hours")
        
        return opportunities

class ContentAwareRateLimiter:
    """
    Rate Limiter spécialisé pour types de contenu Ainflue.
    Audio/Video/Image upload limits + processing costs + quality tiers.
    """
    
    def __init__(self, distributed_limiter: DistributedRateLimiter):
        self.distributed_limiter = distributed_limiter
        self.content_limits_matrix = ContentLimitsMatrix.get_default_matrix()
        self.content_analyzer = ContentAnalyzer()
        
        # Quotas utilisateurs
        self.bandwidth_quotas = {}  # user_id -> BandwidthQuota
        self.concurrent_operations = defaultdict(int)  # user_id -> count
        self.processing_queue = defaultdict(deque)  # content_type -> queue
        
        # Métriques contenu
        self.content_metrics = {
            "total_requests": 0,
            "bandwidth_consumed_mb": 0.0,
            "processing_tokens_used": 0,
            "content_type_distribution": defaultdict(int),
            "quality_tier_distribution": defaultdict(int),
            "user_tier_distribution": defaultdict(int)
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._background_tasks = []
        self._stop_event = asyncio.Event()
    
    async def initialize(self) -> bool:
        """Initialisation content-aware rate limiter"""
        try:
            # Initialisation distributed limiter base
            await self.distributed_limiter.initialize()
            
            # Chargement quotas par défaut
            await self._load_default_bandwidth_quotas()
            
            # Démarrage background tasks
            await self._start_background_tasks()
            
            self.logger.info("Content-aware rate limiter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Content-aware rate limiter initialization failed: {e}")
            return False
    
    async def apply_content_specific_limits(self, request: ContentRequest) -> ContentLimitResult:
        """Rate limiting spécialisé selon type contenu et qualité"""
        start_time = time.time()
        self.content_metrics["total_requests"] += 1
        self.content_metrics["content_type_distribution"][request.content_type.value] += 1
        self.content_metrics["quality_tier_distribution"][request.quality_tier.value] += 1
        self.content_metrics["user_tier_distribution"][request.user_tier] += 1
        
        try:
            # 1. Récupération limites pour type contenu
            limits_matrix = self.content_limits_matrix.get(request.content_type)
            if not limits_matrix:
                return ContentLimitResult(
                    allowed=False,
                    content_type=request.content_type,
                    processing_type=request.processing_type,
                    bandwidth_consumed_mb=0.0,
                    processing_tokens_used=0,
                    quality_tier_applied=request.quality_tier,
                    concurrent_operations=0,
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.ERROR,
                        allowed=False
                    ),
                    content_warnings=["Unsupported content type"]
                )
            
            # 2. Vérification quota bandwidth
            bandwidth_check = await self._check_bandwidth_quota(request, limits_matrix)
            if not bandwidth_check["allowed"]:
                return ContentLimitResult(
                    allowed=False,
                    content_type=request.content_type,
                    processing_type=request.processing_type,
                    bandwidth_consumed_mb=request.file_size_mb,
                    processing_tokens_used=0,
                    quality_tier_applied=request.quality_tier,
                    concurrent_operations=self.concurrent_operations.get(request.identifier, 0),
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.DENIED,
                        allowed=False
                    ),
                    content_warnings=bandwidth_check["warnings"]
                )
            
            # 3. Vérification limites concurrence
            concurrent_check = await self._check_concurrent_limits(request, limits_matrix)
            if not concurrent_check["allowed"]:
                return ContentLimitResult(
                    allowed=False,
                    content_type=request.content_type,
                    processing_type=request.processing_type,
                    bandwidth_consumed_mb=request.file_size_mb,
                    processing_tokens_used=0,
                    quality_tier_applied=request.quality_tier,
                    concurrent_operations=self.concurrent_operations.get(request.identifier, 0),
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.THROTTLED,
                        allowed=False
                    ),
                    content_warnings=concurrent_check["warnings"]
                )
            
            # 4. Calcul coût processing
            processing_cost = request.calculate_processing_cost(limits_matrix)
            
            # 5. Vérification rate limiting distribué
            rate_limit_result = await self.distributed_limiter.check_rate_limit(
                f"content:{request.identifier}:{request.content_type.value}",
                processing_cost,
                {
                    "content_type": request.content_type.value,
                    "processing_type": request.processing_type.value,
                    "quality_tier": request.quality_tier.value,
                    "file_size_mb": request.file_size_mb
                }
            )
            
            if not rate_limit_result.allowed:
                return ContentLimitResult(
                    allowed=False,
                    content_type=request.content_type,
                    processing_type=request.processing_type,
                    bandwidth_consumed_mb=request.file_size_mb,
                    processing_tokens_used=processing_cost,
                    quality_tier_applied=request.quality_tier,
                    concurrent_operations=self.concurrent_operations.get(request.identifier, 0),
                    rate_limit_result=rate_limit_result,
                    content_warnings=["Rate limit exceeded for content processing"]
                )
            
            # 6. Analyse contenu pour optimisations
            content_analysis = await self.content_analyzer.analyze_content_characteristics(request)
            
            # 7. Update quotas et métriques
            await self._update_bandwidth_quota(request)
            await self._update_concurrent_operations(request.identifier, 1)
            
            # Update métriques globales
            self.content_metrics["bandwidth_consumed_mb"] += request.file_size_mb
            self.content_metrics["processing_tokens_used"] += processing_cost
            
            # 8. Génération suggestions optimisation
            optimization_suggestions = content_analysis.get("optimization_opportunities", [])
            
            # 9. Estimation temps processing
            estimated_time = await self._estimate_processing_time(request, limits_matrix)
            
            # 10. Construction résultat final
            result = ContentLimitResult(
                allowed=True,
                content_type=request.content_type,
                processing_type=request.processing_type,
                bandwidth_consumed_mb=request.file_size_mb,
                processing_tokens_used=processing_cost,
                quality_tier_applied=request.quality_tier,
                concurrent_operations=self.concurrent_operations.get(request.identifier, 0),
                rate_limit_result=rate_limit_result,
                content_warnings=[],
                optimization_suggestions=optimization_suggestions,
                estimated_processing_time=estimated_time,
                metadata={
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "content_analysis": content_analysis,
                    "bandwidth_impact": content_analysis.get("bandwidth_impact", {}),
                    "resource_requirements": content_analysis.get("resource_requirements", {})
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content-specific rate limiting failed for {request.identifier}: {e}")
            return ContentLimitResult(
                allowed=False,
                content_type=request.content_type,
                processing_type=request.processing_type,
                bandwidth_consumed_mb=0.0,
                processing_tokens_used=0,
                quality_tier_applied=request.quality_tier,
                concurrent_operations=0,
                rate_limit_result=RateLimitResult(
                    status=RateLimitStatus.ERROR,
                    allowed=False
                ),
                content_warnings=[f"Processing error: {str(e)}"],
                metadata={"error": str(e)}
            )
    
    async def _check_bandwidth_quota(self, request: ContentRequest, 
                                   limits_matrix: ContentLimitsMatrix) -> Dict[str, Any]:
        """Vérification quota bandwidth"""
        # Récupération quota utilisateur
        bandwidth_quota = await self._get_or_create_bandwidth_quota(request.identifier, request.user_tier)
        
        # Calcul limite effective avec multipliers
        user_multiplier = limits_matrix.user_tier_multipliers.get(request.user_tier, 1.0)
        quality_multiplier = limits_matrix.quality_multipliers.get(request.quality_tier, 1.0)
        
        # Détermination limite selon processing type
        if request.processing_type == ProcessingType.UPLOAD:
            effective_limit = limits_matrix.upload_rate_mb_per_hour * user_multiplier
            current_usage = bandwidth_quota.used_upload_mb
            remaining = bandwidth_quota.upload_remaining_mb
        else:  # DOWNLOAD ou autres
            effective_limit = limits_matrix.download_rate_mb_per_hour * user_multiplier
            current_usage = bandwidth_quota.used_download_mb
            remaining = bandwidth_quota.download_remaining_mb
        
        # Ajustement pour qualité
        required_bandwidth = request.file_size_mb * quality_multiplier
        
        # Vérification quota
        if required_bandwidth > remaining:
            return {
                "allowed": False,
                "warnings": [
                    f"Bandwidth quota exceeded: {required_bandwidth:.1f}MB required, {remaining:.1f}MB remaining",
                    f"Current usage: {current_usage:.1f}MB / {effective_limit:.1f}MB"
                ]
            }
        
        return {"allowed": True, "warnings": []}
    
    async def _check_concurrent_limits(self, request: ContentRequest,
                                     limits_matrix: ContentLimitsMatrix) -> Dict[str, Any]:
        """Vérification limites concurrence"""
        current_concurrent = self.concurrent_operations.get(request.identifier, 0)
        
        # Limite concurrence selon processing type
        if request.processing_type == ProcessingType.UPLOAD:
            max_concurrent = limits_matrix.max_concurrent_uploads
        else:
            max_concurrent = limits_matrix.max_concurrent_downloads
        
        # Ajustement pour user tier
        user_multiplier = limits_matrix.user_tier_multipliers.get(request.user_tier, 1.0)
        effective_max = int(max_concurrent * user_multiplier)
        
        if current_concurrent >= effective_max:
            return {
                "allowed": False,
                "warnings": [
                    f"Concurrent operations limit reached: {current_concurrent}/{effective_max}",
                    "Wait for current operations to complete"
                ]
            }
        
        return {"allowed": True, "warnings": []}
    
    async def _get_or_create_bandwidth_quota(self, user_id: str, user_tier: str) -> BandwidthQuota:
        """Récupération ou création quota bandwidth"""
        if user_id not in self.bandwidth_quotas:
            # Création nouveau quota basé sur user tier
            tier_quotas = {
                "free": {"upload": 100, "download": 200},
                "basic": {"upload": 500, "download": 1000},
                "pro": {"upload": 2000, "download": 5000},
                "enterprise": {"upload": 10000, "download": 20000}
            }
            
            quotas = tier_quotas.get(user_tier, tier_quotas["free"])
            
            self.bandwidth_quotas[user_id] = BandwidthQuota(
                user_id=user_id,
                upload_quota_mb=quotas["upload"],
                download_quota_mb=quotas["download"]
            )
        
        # Vérification reset si nécessaire
        quota = self.bandwidth_quotas[user_id]
        if datetime.now() > quota.reset_date:
            quota.used_upload_mb = 0.0
            quota.used_download_mb = 0.0
            quota.reset_date = datetime.now() + timedelta(hours=1)
        
        return quota
    
    async def _update_bandwidth_quota(self, request: ContentRequest):
        """Update quota bandwidth"""
        quota = await self._get_or_create_bandwidth_quota(request.identifier, request.user_tier)
        
        if request.processing_type == ProcessingType.UPLOAD:
            quota.used_upload_mb += request.file_size_mb
        else:
            quota.used_download_mb += request.file_size_mb
    
    async def _update_concurrent_operations(self, user_id: str, delta: int):
        """Update compteur opérations concurrentes"""
        self.concurrent_operations[user_id] = max(0, self.concurrent_operations[user_id] + delta)
    
    async def _estimate_processing_time(self, request: ContentRequest,
                                      limits_matrix: ContentLimitsMatrix) -> int:
        """Estimation temps processing"""
        # Base time selon type contenu (en secondes)
        base_times = {
            ContentType.AUDIO: 30,
            ContentType.VIDEO: 180,
            ContentType.LIVESTREAM: 5,  # Real-time
            ContentType.IMAGE: 10
        }
        
        base_time = base_times.get(request.content_type, 60)
        
        # Ajustements
        size_multiplier = max(1.0, request.file_size_mb / 10.0)  # +time per 10MB
        quality_multiplier = limits_matrix.quality_multipliers.get(request.quality_tier, 1.0)
        processing_multiplier = limits_matrix.processing_multipliers.get(request.processing_type, 1.0)
        
        estimated_time = base_time * size_multiplier * quality_multiplier * processing_multiplier
        return int(estimated_time)
    
    async def _load_default_bandwidth_quotas(self):
        """Chargement quotas bandwidth par défaut"""
        # Les quotas sont créés dynamiquement lors de la première requête
        pass
    
    async def _start_background_tasks(self):
        """Démarrage tâches background"""
        # Tâche reset quotas périodique
        quota_reset_task = asyncio.create_task(self._quota_reset_loop())
        self._background_tasks.append(quota_reset_task)
        
        # Tâche cleanup concurrent operations
        cleanup_task = asyncio.create_task(self._concurrent_cleanup_loop())
        self._background_tasks.append(cleanup_task)
        
        # Tâche analysis patterns contenu
        pattern_task = asyncio.create_task(self._content_pattern_analysis_loop())
        self._background_tasks.append(pattern_task)
    
    async def _quota_reset_loop(self):
        """Loop reset quotas bandwidth"""
        while not self._stop_event.is_set():
            try:
                now = datetime.now()
                for user_id, quota in self.bandwidth_quotas.items():
                    if now > quota.reset_date:
                        quota.used_upload_mb = 0.0
                        quota.used_download_mb = 0.0
                        quota.reset_date = now + timedelta(hours=1)
                        self.logger.info(f"Bandwidth quota reset for user {user_id}")
                
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                self.logger.error(f"Quota reset loop error: {e}")
                await asyncio.sleep(60)
    
    async def _concurrent_cleanup_loop(self):
        """Loop cleanup opérations concurrentes abandonnées"""
        while not self._stop_event.is_set():
            try:
                # Simulation cleanup - dans une vraie implémentation,
                # tracker operations actives et cleanup celles terminées
                for user_id in list(self.concurrent_operations.keys()):
                    if self.concurrent_operations[user_id] > 0:
                        # Décrémentation graduelle pour opérations "perdues"
                        self.concurrent_operations[user_id] = max(0, 
                                                                 self.concurrent_operations[user_id] - 1)
                
                await asyncio.sleep(60)  # Every minute
            except Exception as e:
                self.logger.error(f"Concurrent cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def _content_pattern_analysis_loop(self):
        """Loop analyse patterns contenu"""
        while not self._stop_event.is_set():
            try:
                # Analyse patterns usage contenu
                await self._analyze_content_usage_patterns()
                
                # Optimisation limites basées sur patterns
                await self._optimize_content_limits_based_on_patterns()
                
                await asyncio.sleep(1800)  # Every 30 minutes
            except Exception as e:
                self.logger.error(f"Pattern analysis error: {e}")
                await asyncio.sleep(600)
    
    async def _analyze_content_usage_patterns(self):
        """Analyse patterns usage contenu"""
        # Analyse distribution types contenu
        total_requests = sum(self.content_metrics["content_type_distribution"].values())
        if total_requests > 0:
            for content_type, count in self.content_metrics["content_type_distribution"].items():
                percentage = (count / total_requests) * 100
                self.logger.info(f"Content type {content_type}: {percentage:.1f}% of requests")
    
    async def _optimize_content_limits_based_on_patterns(self):
        """Optimisation limites basées sur patterns"""
        # Ajustement dynamique limites basé sur usage
        # Implementation simplifiée - dans une vraie version, ML-based optimization
        pass
    
    async def complete_content_operation(self, user_id: str, request: ContentRequest) -> bool:
        """Completion opération contenu"""
        try:
            # Décrémentation concurrent operations
            await self._update_concurrent_operations(user_id, -1)
            
            self.logger.info(f"Content operation completed for user {user_id}: {request.content_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete content operation: {e}")
            return False
    
    async def get_content_status(self, user_id: str) -> Dict[str, Any]:
        """Status contenu utilisateur"""
        try:
            bandwidth_quota = self.bandwidth_quotas.get(user_id)
            concurrent_ops = self.concurrent_operations.get(user_id, 0)
            
            status = {
                "user_id": user_id,
                "bandwidth_quota": {
                    "upload_used_mb": bandwidth_quota.used_upload_mb if bandwidth_quota else 0,
                    "upload_remaining_mb": bandwidth_quota.upload_remaining_mb if bandwidth_quota else 0,
                    "download_used_mb": bandwidth_quota.used_download_mb if bandwidth_quota else 0,
                    "download_remaining_mb": bandwidth_quota.download_remaining_mb if bandwidth_quota else 0,
                    "reset_date": bandwidth_quota.reset_date.isoformat() if bandwidth_quota else None
                },
                "concurrent_operations": concurrent_ops,
                "global_metrics": self.content_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            return {"error": str(e)}

# Factory functions pour différents use cases
def create_audio_focused_limiter(redis_client) -> ContentAwareRateLimiter:
    """Factory pour limiter focalisé audio"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=50,
        burst_capacity=100,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        redis_key_prefix="audio_rl"
    ))
    
    limiter = ContentAwareRateLimiter(base_limiter)
    
    # Customisation limites audio
    audio_limits = limiter.content_limits_matrix[ContentType.AUDIO]
    audio_limits.upload_rate_mb_per_hour = 1000  # Plus généreux pour audio
    audio_limits.processing_cost_tokens = 5      # Moins coûteux
    
    return limiter

def create_video_optimized_limiter(redis_client) -> ContentAwareRateLimiter:
    """Factory pour limiter optimisé vidéo"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=20,  # Plus restrictif pour vidéo
        burst_capacity=40,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        redis_key_prefix="video_rl"
    ))
    
    limiter = ContentAwareRateLimiter(base_limiter)
    
    # Customisation limites vidéo
    video_limits = limiter.content_limits_matrix[ContentType.VIDEO]
    video_limits.max_concurrent_uploads = 2  # Plus restrictif
    video_limits.processing_cost_tokens = 100  # Plus coûteux
    
    return limiter

def create_livestream_limiter(redis_client) -> ContentAwareRateLimiter:
    """Factory pour limiter livestream"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=10,
        burst_capacity=20,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.LEAKY_BUCKET,
        redis_key_prefix="stream_rl"
    ))
    
    limiter = ContentAwareRateLimiter(base_limiter)
    
    # Customisation limites livestream
    stream_limits = limiter.content_limits_matrix[ContentType.LIVESTREAM]
    stream_limits.max_concurrent_uploads = 1  # Un seul stream actif
    stream_limits.upload_rate_mb_per_hour = 50000  # Très élevé pour streaming
    
    return limiter

# Export classes principales
__all__ = [
    'ContentAwareRateLimiter',
    'ContentRequest',
    'ContentLimitResult',
    'ContentType',
    'QualityTier',
    'ProcessingType',
    'ContentLimitsMatrix',
    'BandwidthQuota',
    'create_audio_focused_limiter',
    'create_video_optimized_limiter',
    'create_livestream_limiter'
]