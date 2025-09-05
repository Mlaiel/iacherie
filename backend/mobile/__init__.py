"""Backend Mobile Services
Mobile-specific backend services and integrations

Enterprise Mobile Backend Architecture implementing:
- Creator Multi-Format Upload Integration
- Mobile Content Orchestration  
- Mobile-Optimized Media Processing
- Creator Workflow Mobile Integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Original mobile services
from .push_notifications import PushNotificationService, NotificationPriority, NotificationType
from .offline_sync import OfflineSyncManager, SyncStrategy, ConflictResolution

# Phase 1: Creator Mobile Workflow Core (CRITICAL PRIORITY)
from .mobile_content_orchestrator import (
    MobileContentOrchestrator,
    MobileContentRequest, 
    WorkflowStatus,
    CreatorType,
    WorkflowStage,
    MobileOptimization
)

from .creator_upload_manager import (
    CreatorUploadManager,
    UploadRequest,
    UploadProgress,
    CreatorUploadSettings,
    ContentFormat,
    UploadStatus,
    UploadMethod
)

from .mobile_media_processor import (
    MobileMediaProcessor,
    ProcessingRequest,
    ProcessingResult,
    MobileProcessingSettings,
    QualityLevel,
    MobileFormat,
    ProcessingStatus
)

from .creator_workflow_mobile import (
    CreatorWorkflowMobile,
    CreatorWorkflowState,
    MobileWorkflowConfiguration,
    MobileWorkflowEvent,
    WorkflowEvent
)

__all__ = [
    # Original services
    "PushNotificationService",
    "NotificationPriority", 
    "NotificationType",
    "OfflineSyncManager",
    "SyncStrategy",
    "ConflictResolution",
    
    # Phase 1: Creator Mobile Workflow Core
    "MobileContentOrchestrator",
    "MobileContentRequest",
    "WorkflowStatus", 
    "CreatorType",
    "WorkflowStage",
    "MobileOptimization",
    
    "CreatorUploadManager",
    "UploadRequest",
    "UploadProgress",
    "CreatorUploadSettings",
    "ContentFormat",
    "UploadStatus",
    "UploadMethod",
    
    "MobileMediaProcessor", 
    "ProcessingRequest",
    "ProcessingResult",
    "MobileProcessingSettings",
    "QualityLevel",
    "MobileFormat",
    "ProcessingStatus",
    
    "CreatorWorkflowMobile",
    "CreatorWorkflowState",
    "MobileWorkflowConfiguration", 
    "MobileWorkflowEvent",
    "WorkflowEvent"
]