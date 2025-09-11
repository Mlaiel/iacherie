"""MongoDB Multi-Platform Sync Module
====================================

Multi-platform data synchronization and content distribution system
for the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

TEAM SPECIALTIES:
- Lead AI Engineer: Fahed Mlaiel - AI-driven platform optimization and content matching
- Backend Senior Engineer: Infrastructure robuste multi-plateforme et APIs enterprise
- ML Engineer: Algorithmes ML pour content adaptation et audience targeting
- DBA: Optimisation cross-platform data sync et schema mapping
- Security Specialist: Protection multi-plateforme et compliance per-platform
- Microservices Architect: Architecture distribuée pour intégrations platforms
- Audio Engineer: Processing audio multi-format pour distribution platforms
- DevOps Engineer: Orchestration deployments multi-platform et monitoring
- IA Prompt Engineer: Optimisation content generation per platform requirements
"""

import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Import all platform modules
from .platform_manager import (
    PlatformManager, PlatformType, PlatformConfig, PlatformCredentials,
    PlatformLimits, PlatformStatus, create_platform_manager
)
from .content_distributor import (
    ContentDistributor, ContentMetadata, PlatformAdaptation, DistributionJob,
    DistributionStatus, OptimizationLevel, create_content_distributor
)
from .sync_scheduler import (
    SyncScheduler, ScheduleType, ScheduleStatus, Priority, ScheduleRule,
    ScheduledTask, OptimalTimeRecommendation, create_sync_scheduler
)
from .conflict_handler import (
    ConflictHandler, ConflictType, ConflictSeverity, ConflictStatus,
    ResolutionStrategy, Conflict, create_conflict_handler
)

logger = logging.getLogger(__name__)

class SyncDirection(Enum):
    """Platform sync directions."""
    UPLOAD_ONLY = "upload_only"
    DOWNLOAD_ONLY = "download_only"
    BIDIRECTIONAL = "bidirectional"
    MIRROR = "mirror"

class ContentFormat(Enum):
    """Content format types."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVESTREAM = "livestream"
    STORY = "story"
    POST = "post"
    REEL = "reel"
    SHORT = "short"

@dataclass
class ContentItem:
    """Content item for platform sync."""
    content_id: str
    title: str
    description: str
    content_format: ContentFormat
    file_path: Optional[str]
    metadata: Dict[str, Any]
    platform_specific_data: Dict[str, Any]
    tags: List[str]
    thumbnail_path: Optional[str] = None

# Export classes and functions
__all__ = [
    # Enums
    'PlatformType',
    'SyncDirection', 
    'ContentFormat',
    'PlatformStatus',
    'DistributionStatus',
    'OptimizationLevel',
    'ScheduleType',
    'ScheduleStatus',
    'Priority',
    'ConflictType',
    'ConflictSeverity',
    'ConflictStatus',
    'ResolutionStrategy',
    
    # Data Classes
    'PlatformConfig',
    'PlatformCredentials',
    'PlatformLimits',
    'ContentItem',
    'ContentMetadata',
    'PlatformAdaptation',
    'DistributionJob',
    'ScheduleRule',
    'ScheduledTask',
    'OptimalTimeRecommendation',
    'Conflict',
    
    # Main Classes
    'PlatformManager',
    'ContentDistributor',
    'SyncScheduler',
    'ConflictHandler',
    
    # Factory Functions
    'create_platform_manager',
    'create_content_distributor',
    'create_sync_scheduler',
    'create_conflict_handler'
]

# Module initialization
logger.info("MongoDB Platforms module initialized - Multi-platform sync ready with all components")