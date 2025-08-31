"""Archival Data Models

Defines core data models and structures for the archival system
including archive entries, configurations, and metadata schemas.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from .archival_manager import ArchivalStatus, ArchivalTier


@dataclass
class ArchiveEntry:
    """Core archive entry model"""    archive_id: str
    content_id: str
    content_type: str
    
    # Size information
    original_size: int
    compressed_size: int
    compression_ratio: float
    
    # Storage information
    storage_tier: ArchivalTier
    archive_path: str
    
    # Status and metadata
    status: ArchivalStatus = ArchivalStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Temporal information
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Relationships
    parent_archive: Optional[str] = None
    related_archives: List[str] = field(default_factory=list)
    
    # Quality and integrity
    checksum: str = ""
    verification_status: str = "pending"
    integrity_checks: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""        return {
            "archive_id": self.archive_id,
            "content_id": self.content_id,
            "content_type": self.content_type,
            "original_size": self.original_size,
            "compressed_size": self.compressed_size,
            "compression_ratio": self.compression_ratio,
            "storage_tier": self.storage_tier.value,
            "archive_path": self.archive_path,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "parent_archive": self.parent_archive,
            "related_archives": self.related_archives,
            "checksum": self.checksum,
            "verification_status": self.verification_status,
            "integrity_checks": self.integrity_checks
        }


@dataclass
class ArchivalConfiguration:
    """Global archival configuration"""    
    # Storage settings
    default_tier: ArchivalTier = ArchivalTier.HOT
    max_file_size_gb: float = 100.0
    enable_compression: bool = True
    enable_encryption: bool = True
    enable_deduplication: bool = True
    
    # Performance settings
    max_concurrent_operations: int = 10
    chunk_size_mb: int = 64
    compression_level: int = 6
    verification_enabled: bool = True
    
    # Retention settings
    default_retention_days: int = 2555  # ~7 years
    enable_auto_cleanup: bool = True
    cleanup_interval_hours: int = 24
    
    # Monitoring settings
    enable_metrics: bool = True
    metrics_interval_seconds: int = 300
    enable_alerts: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "storage_usage_percent": 85.0,
        "failed_operations_percent": 5.0,
        "average_response_time_seconds": 10.0
    })
    
    # Storage quotas per tier
    storage_quotas: Dict[str, str] = field(default_factory=lambda: {
        "hot": "10TB",
        "warm": "50TB",
        "cold": "500TB",
        "frozen": "unlimited",
        "deep_freeze": "unlimited"
    })
    
    # Integration settings
    enable_cloud_storage: bool = False
    cloud_provider: Optional[str] = None
    cloud_config: Dict[str, Any] = field(default_factory=dict)
    
    # Security settings
    encryption_algorithm: str = "AES-256"
    key_rotation_days: int = 90
    access_control_enabled: bool = True


@dataclass
class StorageQuota:
    """Storage quota configuration for a tier"""    tier: ArchivalTier
    limit_bytes: int
    used_bytes: int = 0
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 0.95  # 95%
    
    @property
    def usage_percentage(self) -> float:
        """Calculate usage percentage"""        if self.limit_bytes == 0:
            return 0.0
        return self.used_bytes / self.limit_bytes
    
    @property
    def is_warning(self) -> bool:
        """Check if usage exceeds warning threshold"""        return self.usage_percentage >= self.warning_threshold
    
    @property
    def is_critical(self) -> bool:
        """Check if usage exceeds critical threshold"""        return self.usage_percentage >= self.critical_threshold
    
    @property
    def available_bytes(self) -> int:
        """Calculate available bytes"""        return max(0, self.limit_bytes - self.used_bytes)


@dataclass
class AccessPattern:
    """Content access pattern tracking"""    content_id: str
    archive_id: str
    
    # Access statistics
    total_accesses: int = 0
    last_access: Optional[datetime] = None
    access_frequency: float = 0.0  # accesses per day
    access_history: List[datetime] = field(default_factory=list)
    
    # Access patterns
    peak_access_hours: List[int] = field(default_factory=list)
    geographic_sources: Dict[str, int] = field(default_factory=dict)
    user_types: Dict[str, int] = field(default_factory=dict)
    
    # Business metrics
    business_value_score: float = 0.0  # 0-1 scale
    monetization_potential: float = 0.0  # 0-1 scale
    collaboration_score: float = 0.0  # 0-1 scale
    
    # Predictions
    predicted_next_access: Optional[datetime] = None
    retention_recommendation: str = "standard"
    tier_recommendation: Optional[ArchivalTier] = None
    
    def update_access(self, access_time: datetime = None):
        """Update access statistics"""        access_time = access_time or datetime.utcnow()
        
        self.total_accesses += 1
        self.last_access = access_time
        self.access_history.append(access_time)
        
        # Keep only last 100 accesses for efficiency
        if len(self.access_history) > 100:
            self.access_history = self.access_history[-100:]
        
        # Calculate access frequency (accesses per day)
        if len(self.access_history) >= 2:
            time_span = (self.access_history[-1] - self.access_history[0]).total_seconds()
            if time_span > 0:
                self.access_frequency = len(self.access_history) / (time_span / 86400)  # 86400 seconds in a day
    
    def calculate_business_value(self, creator_metrics: Dict[str, Any] = None) -> float:
        """Calculate business value score based on access patterns"""        score = 0.0
        
        # Access frequency component (0-0.4)
        if self.access_frequency > 10:  # High frequency
            score += 0.4
        elif self.access_frequency > 1:  # Medium frequency
            score += 0.3
        elif self.access_frequency > 0.1:  # Low frequency
            score += 0.2
        
        # Recency component (0-0.3)
        if self.last_access:
            days_since_access = (datetime.utcnow() - self.last_access).days
            if days_since_access <= 7:
                score += 0.3
            elif days_since_access <= 30:
                score += 0.2
            elif days_since_access <= 90:
                score += 0.1
        
        # Total access component (0-0.3)
        if self.total_accesses > 100:
            score += 0.3
        elif self.total_accesses > 50:
            score += 0.2
        elif self.total_accesses > 10:
            score += 0.1
        
        self.business_value_score = min(1.0, score)
        return self.business_value_score
    
    def recommend_tier(self) -> ArchivalTier:
        """Recommend storage tier based on access patterns"""        if self.access_frequency > 5:  # Very frequent access
            return ArchivalTier.HOT
        elif self.access_frequency > 1:  # Regular access
            return ArchivalTier.WARM
        elif self.access_frequency > 0.1:  # Occasional access
            return ArchivalTier.COLD
        elif self.total_accesses > 0 and self.last_access:
            days_since_access = (datetime.utcnow() - self.last_access).days
            if days_since_access > 365:  # Not accessed for over a year
                return ArchivalTier.DEEP_FREEZE
            else:
                return ArchivalTier.FROZEN
        else:
            return ArchivalTier.COLD
