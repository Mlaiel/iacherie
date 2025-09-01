"""Enterprise Content Archival Manager

Provides comprehensive archival management with intelligent policies,
multi-tier storage, and advanced lifecycle management for content
protection and monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import uuid

from ..models.base import BaseModel
from ..exceptions import ArchivalError
from .models import ArchiveEntry, ArchivalConfiguration
from .archival_storage import ArchivalStorageBackend
from .retention_engine import RetentionEngine
from .lifecycle_manager import ArchivalLifecycleManager
from .compression_manager import ArchivalCompressionManager
from .monitoring import ArchivalMonitoring


class ArchivalStatus(Enum):
    """
Archival status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ARCHIVED = "archived"
    COMPRESSED = "compressed"
    MIGRATED = "migrated"
    RETRIEVING = "retrieving"
    RESTORED = "restored"
    FAILED = "failed"
    DELETED = "deleted"


class ArchivalTier(Enum):
    """Storage tier enumeration for archival"""

    HOT = "hot"          # Immediate access, high cost
    WARM = "warm"        # Quick access, medium cost
    COLD = "cold"        # Slow access, low cost
    FROZEN = "frozen"    # Long-term storage, minimal cost
    DEEP_FREEZE = "deep_freeze"  # Compliance/legal, minimal access


class CompressionStrategy(Enum):
    """Compression strategy for archival"""

    NONE = "none"
    MINIMAL = "minimal"    # Fast compression, basic space saving
    BALANCED = "balanced"  # Good compression ratio, moderate speed
    MAXIMUM = "maximum"    # Best compression, slower
    ADAPTIVE = "adaptive"  # AI-determined optimal compression


@dataclass
class ArchivalPolicy:
    """Comprehensive archival policy configuration"""
    policy_id: str
    name: str
    description: str
    
    # Content type filters
    content_types: List[str] = field(default_factory=list)
    file_extensions: List[str] = field(default_factory=list)
    content_categories: List[str] = field(default_factory=list)
    
    # Size thresholds
    min_file_size: Optional[int] = None
    max_file_size: Optional[int] = None
    
    # Age-based rules
    archive_after_days: int = 30
    compress_after_days: int = 7
    migrate_to_cold_days: int = 90
    migrate_to_frozen_days: int = 365
    
    # Storage tiers
    initial_tier: ArchivalTier = ArchivalTier.HOT
    final_tier: ArchivalTier = ArchivalTier.COLD
    
    # Compression settings
    compression_strategy: CompressionStrategy = CompressionStrategy.BALANCED
    compression_level: int = 6
    
    # Retention settings
    retention_period_days: Optional[int] = None
    legal_hold: bool = False
    compliance_tags: Set[str] = field(default_factory=set)
    
    # Access patterns
    expected_access_frequency: str = "low"  # low, medium, high
    priority: int = 5  # 1-10, higher = more important
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    tags: Set[str] = field(default_factory=set)


@dataclass
class ArchivalResult:
    """Result of archival operation"""
    success: bool
    archive_id: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    storage_tier: ArchivalTier
    archive_path: str
    metadata: Dict[str, Any]
    processing_time: float
    error_message: Optional[str] = None


class ArchivalManager:
    """
    Enterprise-grade archival manager with intelligent policies,
    multi-tier storage, and advanced lifecycle management
    """
    
    def __init__(
        self,
        storage_backend: ArchivalStorageBackend,
        retention_engine: RetentionEngine,
        lifecycle_manager: ArchivalLifecycleManager,
        compression_manager: ArchivalCompressionManager,
        monitoring: ArchivalMonitoring,
        config_path: Optional[str] = None
    ):
        self.storage_backend = storage_backend
        self.retention_engine = retention_engine
        self.lifecycle_manager = lifecycle_manager
        self.compression_manager = compression_manager
        self.monitoring = monitoring
        
        self.logger = logging.getLogger("archival.manager")
        self.config = self._load_configuration(config_path)
        
        # Policy management
        self.policies: Dict[str, ArchivalPolicy] = {}
        self.default_policy: Optional[ArchivalPolicy] = None
        
        # Active operations tracking
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        
        # Performance metrics
        self.metrics = {
            "archives_created": 0,
            "total_archived_size": 0,
            "total_compressed_size": 0,
            "average_compression_ratio": 0.0,
            "retrieval_requests": 0,
            "failed_operations": 0
        }
        
        # Initialize default policies
        self._initialize_default_policies()
    
    def _load_configuration(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load archival configuration"""
        default_config = {
            "max_concurrent_operations": 10,
            "default_compression_level": 6,
            "default_retention_days": 2555,  # ~7 years
            "chunk_size_mb": 64,
            "enable_deduplication": True,
            "enable_encryption": True,
            "monitoring_interval": 300,  # 5 minutes
            "health_check_interval": 3600,  # 1 hour
            "cleanup_interval": 86400,  # 24 hours
            "storage_quotas": {
                "hot": "10TB",
                "warm": "50TB", 
                "cold": "500TB",
                "frozen": "unlimited"
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_default_policies(self):
        """Initialize default archival policies"""
        
        # Audio content policy
        audio_policy = ArchivalPolicy(
            policy_id="audio_standard",
            name="Standard Audio Content Archival",
            description="Standard archival policy for audio content",
            content_types=["audio/mp3", "audio/wav", "audio/flac", "audio/aac"],
            file_extensions=[".mp3", ".wav", ".flac", ".aac", ".m4a"],
            content_categories=["music", "podcast", "audio"],
            archive_after_days=7,
            compress_after_days=1,
            migrate_to_cold_days=30,
            migrate_to_frozen_days=365,
            compression_strategy=CompressionStrategy.BALANCED,
            retention_period_days=2555,
            expected_access_frequency="medium",
            priority=7,
            tags={"audio", "content", "media"}
        )
        
        # Video content policy
        video_policy = ArchivalPolicy(
            policy_id="video_standard",
            name="Standard Video Content Archival", 
            description="Standard archival policy for video content",
            content_types=["video/mp4", "video/avi", "video/mov", "video/webm"],
            file_extensions=[".mp4", ".avi", ".mov", ".webm", ".mkv"],
            content_categories=["video", "movie", "content"],
            archive_after_days=14,
            compress_after_days=3,
            migrate_to_cold_days=60,
            migrate_to_frozen_days=730,
            compression_strategy=CompressionStrategy.MAXIMUM,
            retention_period_days=3650,
            expected_access_frequency="low",
            priority=8,
            tags={"video", "content", "media"}
        )
        
        # Image content policy
        image_policy = ArchivalPolicy(
            policy_id="image_standard",
            name="Standard Image Content Archival",
            description="Standard archival policy for image content", 
            content_types=["image/jpeg", "image/png", "image/gif", "image/webp"],
            file_extensions=[".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff"],
            content_categories=["image", "photo", "artwork"],
            archive_after_days=30,
            compress_after_days=7,
            migrate_to_cold_days=180,
            migrate_to_frozen_days=1095,
            compression_strategy=CompressionStrategy.MINIMAL,
            retention_period_days=2555,
            expected_access_frequency="medium",
            priority=6,
            tags={"image", "content", "media"}
        )
        
        # Text/Document policy
        text_policy = ArchivalPolicy(
            policy_id="text_standard",
            name="Standard Text/Document Archival",
            description="Standard archival policy for text and documents",
            content_types=["text/plain", "application/pdf", "text/markdown"],
            file_extensions=[".txt", ".md", ".pdf", ".doc", ".docx"],
            content_categories=["document", "text", "blog"],
            archive_after_days=60,
            compress_after_days=14,
            migrate_to_cold_days=365,
            migrate_to_frozen_days=1825,
            compression_strategy=CompressionStrategy.MAXIMUM,
            retention_period_days=3650,
            expected_access_frequency="low",
            priority=5,
            tags={"text", "document", "content"}
        )
        
        # Fingerprint data policy (critical for protection)
        fingerprint_policy = ArchivalPolicy(
            policy_id="fingerprint_critical",
            name="Critical Fingerprint Data Archival",
            description="Critical archival policy for content fingerprints",
            content_types=["application/json", "application/octet-stream"],
            content_categories=["fingerprint", "protection", "signature"],
            archive_after_days=1,
            compress_after_days=0,
            migrate_to_cold_days=30,
            migrate_to_frozen_days=365,
            compression_strategy=CompressionStrategy.BALANCED,
            retention_period_days=3650,
            legal_hold=True,
            expected_access_frequency="high",
            priority=10,
            compliance_tags={"legal", "protection", "copyright"},
            tags={"fingerprint", "critical", "protection"}
        )
        
        # Register all policies
        policies = [audio_policy, video_policy, image_policy, text_policy, fingerprint_policy]
        for policy in policies:
            self.register_policy(policy)
        
        # Set default policy
        self.default_policy = audio_policy
    
    def register_policy(self, policy: ArchivalPolicy):
        """Register an archival policy"""
        self.policies[policy.policy_id] = policy
        self.logger.info(f"Registered archival policy: {policy.policy_id}")
    
    def get_policy(self, policy_id: str) -> Optional[ArchivalPolicy]:
        """Get archival policy by ID"""
        return self.policies.get(policy_id)
    
    def find_applicable_policy(
        self,
        content_type: str,
        file_extension: str = None,
        content_category: str = None,
        file_size: int = None
    ) -> Optional[ArchivalPolicy]:
        """
Find the most applicable archival policy for content"""
        
        matching_policies = []
        
        for policy in self.policies.values():
            score = 0
            
            # Content type matching
            if content_type in policy.content_types:
                score += 10
            
            # File extension matching
            if file_extension and file_extension.lower() in [ext.lower() for ext in policy.file_extensions]:
                score += 8
            
            # Content category matching
            if content_category and content_category in policy.content_categories:
                score += 6
            
            # Size constraints
            if policy.min_file_size and file_size and file_size < policy.min_file_size:
                continue
            if policy.max_file_size and file_size and file_size > policy.max_file_size:
                continue
            
            if score > 0:
                matching_policies.append((policy, score))
        
        if matching_policies:
            # Sort by score (descending) and priority (descending)
            matching_policies.sort(key=lambda x: (x[1], x[0].priority), reverse=True)
            return matching_policies[0][0]
        
        return self.default_policy
    
    async def archive_content(
        self,
        content_id: str,
        content_data: Union[bytes, str, Path],
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        policy_id: Optional[str] = None
    ) -> ArchivalResult:
        """
Archive content with intelligent policy application"""
        
        start_time = datetime.utcnow()
        archive_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Starting archival for content {content_id}")
            
            # Track operation
            self.active_operations[archive_id] = {
                "content_id": content_id,
                "status": ArchivalStatus.PENDING,
                "start_time": start_time,
                "policy_id": policy_id
            }
            
            # Prepare content data
            if isinstance(content_data, str):
                content_bytes = content_data.encode('utf-8')
            elif isinstance(content_data, Path):
                with open(content_data, 'rb') as f:
                    content_bytes = f.read()
            else:
                content_bytes = content_data
            
            original_size = len(content_bytes)
            
            # Find applicable policy
            if policy_id:
                policy = self.get_policy(policy_id)
            else:
                file_extension = None
                if metadata and 'filename' in metadata:
                    file_extension = Path(metadata['filename']).suffix
                
                policy = self.find_applicable_policy(
                    content_type=content_type,
                    file_extension=file_extension,
                    content_category=metadata.get('category') if metadata else None,
                    file_size=original_size
                )
            
            if not policy:
                raise ArchivalError(f"No applicable archival policy found for content {content_id}")
            
            # Update operation status
            self.active_operations[archive_id]["status"] = ArchivalStatus.IN_PROGRESS
            self.active_operations[archive_id]["policy"] = policy.policy_id
            
            # Apply compression if required
            compressed_data = content_bytes
            compression_ratio = 1.0
            
            if policy.compression_strategy != CompressionStrategy.NONE:
                compressed_data = await self.compression_manager.compress_content(
                    content_bytes,
                    strategy=policy.compression_strategy,
                    level=policy.compression_level
                )
                compression_ratio = len(compressed_data) / original_size
            
            # Create archive entry
            archive_entry = ArchiveEntry(
                archive_id=archive_id,
                content_id=content_id,
                content_type=content_type,
                original_size=original_size,
                compressed_size=len(compressed_data),
                compression_ratio=compression_ratio,
                storage_tier=policy.initial_tier,
                policy_id=policy.policy_id,
                metadata=metadata or {},
                created_at=start_time,
                expires_at=start_time + timedelta(days=policy.retention_period_days) if policy.retention_period_days else None
            )
            
            # Store in archival backend
            archive_path = await self.storage_backend.store_archive(
                archive_id=archive_id,
                content_data=compressed_data,
                tier=policy.initial_tier,
                metadata=archive_entry.to_dict()
            )
            
            # Update archive entry with storage path
            archive_entry.archive_path = archive_path
            archive_entry.status = ArchivalStatus.ARCHIVED
            
            # Register with lifecycle manager
            await self.lifecycle_manager.register_archive(archive_entry, policy)
            
            # Register with retention engine
            await self.retention_engine.register_content(archive_entry, policy)
            
            # Update metrics
            self.metrics["archives_created"] += 1
            self.metrics["total_archived_size"] += original_size
            self.metrics["total_compressed_size"] += len(compressed_data)
            self._update_compression_ratio()
            
            # Update operation status
            self.active_operations[archive_id]["status"] = ArchivalStatus.ARCHIVED
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ArchivalResult(
                success=True,
                archive_id=archive_id,
                original_size=original_size,
                compressed_size=len(compressed_data),
                compression_ratio=compression_ratio,
                storage_tier=policy.initial_tier,
                archive_path=archive_path,
                metadata=archive_entry.metadata,
                processing_time=processing_time
            )
            
            # Record monitoring metrics
            await self.monitoring.record_archival_operation(result, policy)
            
            self.logger.info(f"Successfully archived content {content_id} as {archive_id}")
            return result
            
        except Exception as e:
            self.metrics["failed_operations"] += 1
            self.active_operations[archive_id]["status"] = ArchivalStatus.FAILED
            self.active_operations[archive_id]["error"] = str(e)
            
            self.logger.error(f"Failed to archive content {content_id}: {e}")
            
            return ArchivalResult(
                success=False,
                archive_id=archive_id,
                original_size=len(content_bytes) if 'content_bytes' in locals() else 0,
                compressed_size=0,
                compression_ratio=0.0,
                storage_tier=ArchivalTier.HOT,
                archive_path="",
                metadata={},
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                error_message=str(e)
            )
        
        finally:
            # Clean up operation tracking
            if archive_id in self.active_operations:
                del self.active_operations[archive_id]
    
    async def retrieve_content(
        self,
        archive_id: str,
        decompress: bool = True
    ) -> Optional[bytes]:
        """Retrieve archived content"""
        
        try:
            self.logger.info(f"Retrieving archived content {archive_id}")
            
            # Get archive metadata
            archive_entry = await self.storage_backend.get_archive_metadata(archive_id)
            if not archive_entry:
                self.logger.warning(f"Archive {archive_id} not found")
                return None
            
            # Retrieve content data
            content_data = await self.storage_backend.retrieve_archive(archive_id)
            if not content_data:
                return None
            
            # Decompress if requested and content is compressed
            if decompress and archive_entry.get('compression_ratio', 1.0) < 1.0:
                content_data = await self.compression_manager.decompress_content(content_data)
            
            # Update access metrics
            self.metrics["retrieval_requests"] += 1
            
            self.logger.info(f"Successfully retrieved archive {archive_id}")
            return content_data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve archive {archive_id}: {e}")
            return None
    
    async def delete_archive(self, archive_id: str, force: bool = False) -> bool:
        """Delete archived content"""
        
        try:
            # Check retention policy
            if not force:
                can_delete = await self.retention_engine.can_delete_content(archive_id)
                if not can_delete:
                    self.logger.warning(f"Archive {archive_id} cannot be deleted due to retention policy")
                    return False
            
            # Delete from storage backend
            success = await self.storage_backend.delete_archive(archive_id)
            if success:
                # Unregister from lifecycle and retention
                await self.lifecycle_manager.unregister_archive(archive_id)
                await self.retention_engine.unregister_content(archive_id)
                
                self.logger.info(f"Successfully deleted archive {archive_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete archive {archive_id}: {e}")
            return False
    
    async def migrate_archive(
        self,
        archive_id: str,
        target_tier: ArchivalTier,
        policy_override: bool = False
    ) -> bool:
        """Migrate archive to different storage tier"""
        
        try:
            self.logger.info(f"Migrating archive {archive_id} to tier {target_tier.value}")
            
            # Check if migration is allowed by policy
            if not policy_override:
                can_migrate = await self.lifecycle_manager.can_migrate_archive(archive_id, target_tier)
                if not can_migrate:
                    self.logger.warning(f"Migration of archive {archive_id} to {target_tier.value} not allowed by policy")
                    return False
            
            # Perform migration
            success = await self.storage_backend.migrate_archive(archive_id, target_tier)
            if success:
                # Update lifecycle tracking
                await self.lifecycle_manager.update_archive_tier(archive_id, target_tier)
                self.logger.info(f"Successfully migrated archive {archive_id} to {target_tier.value}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to migrate archive {archive_id}: {e}")
            return False
    
    def _update_compression_ratio(self):
        """Update average compression ratio metric"""
        if self.metrics["total_archived_size"] > 0:
            self.metrics["average_compression_ratio"] = (
                self.metrics["total_compressed_size"] / 
                self.metrics["total_archived_size"]
            )
    
    async def get_archival_statistics(self) -> Dict[str, Any]:
        """Get comprehensive archival statistics"""
        
        storage_stats = await self.storage_backend.get_storage_statistics()
        lifecycle_stats = await self.lifecycle_manager.get_lifecycle_statistics()
        retention_stats = await self.retention_engine.get_retention_statistics()
        compression_stats = await self.compression_manager.get_compression_statistics()
        
        return {
            "general_metrics": self.metrics,
            "storage_statistics": storage_stats,
            "lifecycle_statistics": lifecycle_stats,
            "retention_statistics": retention_stats,
            "compression_statistics": compression_stats,
            "active_operations": len(self.active_operations),
            "registered_policies": len(self.policies),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        
        health_status = {
            "overall_status": "healthy",
            "components": {},
            "issues": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Check storage backend
            storage_health = await self.storage_backend.health_check()
            health_status["components"]["storage"] = storage_health
            
            # Check retention engine
            retention_health = await self.retention_engine.health_check()
            health_status["components"]["retention"] = retention_health
            
            # Check lifecycle manager
            lifecycle_health = await self.lifecycle_manager.health_check()
            health_status["components"]["lifecycle"] = lifecycle_health
            
            # Check compression manager
            compression_health = await self.compression_manager.health_check()
            health_status["components"]["compression"] = compression_health
            
            # Aggregate health status
            unhealthy_components = [
                name for name, status in health_status["components"].items()
                if status.get("status") != "healthy"
            ]
            
            if unhealthy_components:
                health_status["overall_status"] = "degraded"
                health_status["issues"].append(f"Unhealthy components: {', '.join(unhealthy_components)}")
            
        except Exception as e:
            health_status["overall_status"] = "critical"
            health_status["issues"].append(f"Health check failed: {str(e)}")
        
        return health_status
    
    async def cleanup_expired_archives(self, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up expired archives according to retention policies"""
        
        cleanup_stats = {
            "archives_processed": 0,
            "archives_deleted": 0,
            "space_freed": 0,
            "errors": []
        }
        
        try:
            expired_archives = await self.retention_engine.find_expired_content()
            
            for archive_id in expired_archives:
                try:
                    cleanup_stats["archives_processed"] += 1
                    
                    if not dry_run:
                        # Get size before deletion
                        metadata = await self.storage_backend.get_archive_metadata(archive_id)
                        if metadata:
                            cleanup_stats["space_freed"] += metadata.get("compressed_size", 0)
                        
                        # Delete archive
                        success = await self.delete_archive(archive_id, force=True)
                        if success:
                            cleanup_stats["archives_deleted"] += 1
                    else:
                        cleanup_stats["archives_deleted"] += 1
                        
                except Exception as e:
                    error_msg = f"Failed to clean up archive {archive_id}: {str(e)}"
                    cleanup_stats["errors"].append(error_msg)
                    self.logger.error(error_msg)
            
        except Exception as e:
            cleanup_stats["errors"].append(f"Cleanup operation failed: {str(e)}")
        
        return cleanup_stats
    
    async def optimize_storage(self) -> Dict[str, Any]:
        """Optimize archival storage for better performance and cost"""
        
        optimization_stats = {
            "archives_optimized": 0,
            "space_saved": 0,
            "migrations_performed": 0,
            "compression_improvements": 0
        }
        
        try:
            # Get candidates for optimization
            optimization_candidates = await self.lifecycle_manager.find_optimization_candidates()
            
            for candidate in optimization_candidates:
                archive_id = candidate["archive_id"]
                optimization_type = candidate["type"]
                
                if optimization_type == "compression":
                    # Re-compress with better algorithm
                    success = await self._recompress_archive(archive_id)
                    if success:
                        optimization_stats["compression_improvements"] += 1
                        optimization_stats["space_saved"] += candidate.get("potential_savings", 0)
                
                elif optimization_type == "migration":
                    # Migrate to more appropriate tier
                    target_tier = candidate["target_tier"]
                    success = await self.migrate_archive(archive_id, target_tier)
                    if success:
                        optimization_stats["migrations_performed"] += 1
                
                optimization_stats["archives_optimized"] += 1
                
        except Exception as e:
            self.logger.error(f"Storage optimization failed: {e}")
        
        return optimization_stats
    
    async def _recompress_archive(self, archive_id: str) -> bool:
        """Re-compress archive with improved algorithm"""
        
        try:
            # Retrieve original data
            content_data = await self.retrieve_content(archive_id, decompress=True)
            if not content_data:
                return False
            
            # Get current archive metadata
            metadata = await self.storage_backend.get_archive_metadata(archive_id)
            if not metadata:
                return False
            
            # Find better compression strategy
            policy = self.get_policy(metadata.get("policy_id"))
            if not policy:
                return False
            
            # Apply improved compression
            new_compressed_data = await self.compression_manager.compress_content(
                content_data,
                strategy=CompressionStrategy.ADAPTIVE,  # Use adaptive for best results
                level=9  # Maximum compression level
            )
            
            # Check if improvement is significant
            old_size = metadata.get("compressed_size", len(content_data))
            new_size = len(new_compressed_data)
            
            if new_size < old_size * 0.9:  # At least 10% improvement
                # Replace archive with recompressed version
                await self.storage_backend.replace_archive_data(archive_id, new_compressed_data)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to recompress archive {archive_id}: {e}")
            return False
