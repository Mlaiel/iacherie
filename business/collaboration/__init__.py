"""Collaboration Business Logic Module for IA Influencer Agent
Professional collaboration management and workflow orchestration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
# Main collaboration manager and models
from .manager import CollaborationManager, CollaborationManagerConfig, CollaborationManagerResponse

# Core models
from .collaboration_models import (
    CollaborationType, CollaborationStatus, SkillLevel,
    CollaborationSkill, CollaborationRequest, CollaborationMatch,
    CollaborationContract, CollaborationAnalytics, CollaborationNotification
)

# Processors
from .collaboration_processors import (
    MatchingStrategy, ProcessingResult,
    CollaborationMatchingProcessor, CollaborationWorkflowProcessor, 
    CollaborationContractProcessor
)

# Services
from .collaboration_services import (
    ServiceResponse, CollaborationDiscoveryService,
    CollaborationMatchingService, CollaborationManagementService,
    CollaborationAnalyticsService
)

# Analytics
from .collaboration_analytics import (
    AnalyticsMetric, AnalyticsInsight, CollaborationTrendData,
    CollaborationAnalyticsEngine, CollaborationReportGenerator
)

# Partnership Engine
from .partnership_engine import (
    PartnershipEngine, PartnershipType, PartnershipPriority, PartnershipCriteria,
    PartnershipMetrics, PartnershipProposal
)

# Platform Distributor
from .platform_distributor import (
    MultiPlatformDistributor, PlatformType, DistributionStatus, ContentFormat,
    PlatformConfig, DistributionTarget, DistributionRequest, DistributionResult
)

# Revenue Sharing
from .revenue_sharing import (
    RevenueSharingEngine, RevenueStreamType, PaymentStatus, RevenueShareModel,
    CollaboratorShare, RevenueMetrics, RevenueTransaction, RevenueSharingAgreement,
    PayoutRecord
)

# Notification Engine
from .notification_engine import (
    NotificationEngine, NotificationType, NotificationPriority, NotificationChannel,
    NotificationStatus, NotificationRecipient, NotificationTemplate,
    CollaborationNotification, NotificationDeliveryResult, NotificationAnalytics
)

# Content Synchronization
from .content_sync import (
    ContentSyncEngine, ContentType, SyncAction, SyncStatus, ConflictResolution,
    ContentVersion, SyncEndpoint, SyncConflict, ContentSyncRequest, SyncResult
)

# System Index and Coordination
from .index import (
    CollaborationIndex, CollaborationIndexConfig, CollaborationSystemStatus,
    SystemHealthMetrics, collaboration_index, get_collaboration_index,
    get_authenticated_creator, health_check
)

# Export all collaboration components
__all__ = [
    # Main manager
    'CollaborationManager', 'CollaborationManagerConfig', 'CollaborationManagerResponse',
    
    # Models
    'CollaborationType', 'CollaborationStatus', 'SkillLevel',
    'CollaborationSkill', 'CollaborationRequest', 'CollaborationMatch',
    'CollaborationContract', 'CollaborationAnalytics', 'CollaborationNotification',
    
        # Processors
    'MatchingStrategy', 'ProcessingResult',
    'CollaborationMatchingProcessor', 'CollaborationWorkflowProcessor', 
    'CollaborationContractProcessor',
    
    # Services
    'ServiceResponse', 'CollaborationDiscoveryService',
    'CollaborationMatchingService', 'CollaborationManagementService',
    'CollaborationAnalyticsService',
    
    # Analytics
    'AnalyticsMetric', 'AnalyticsInsight', 'CollaborationTrendData',
    'CollaborationAnalyticsEngine', 'CollaborationReportGenerator',
    
    # Partnership Engine
    'PartnershipEngine', 'PartnershipType', 'PartnershipPriority', 'PartnershipCriteria',
    'PartnershipMetrics', 'PartnershipProposal',
    
    # Platform Distribution
    'MultiPlatformDistributor', 'PlatformType', 'DistributionStatus', 'ContentFormat',
    'PlatformConfig', 'DistributionTarget', 'DistributionRequest', 'DistributionResult',
    
    # Revenue Sharing
    'RevenueSharingEngine', 'RevenueStreamType', 'PaymentStatus', 'RevenueShareModel',
    'CollaboratorShare', 'RevenueMetrics', 'RevenueTransaction', 'RevenueSharingAgreement',
    'PayoutRecord',
    
    # Notification System
    'NotificationEngine', 'NotificationType', 'NotificationPriority', 'NotificationChannel',
    'NotificationStatus', 'NotificationRecipient', 'NotificationTemplate',
    'CollaborationNotification', 'NotificationDeliveryResult', 'NotificationAnalytics',
    
    # Content Synchronization
    'ContentSyncEngine', 'ContentType', 'SyncAction', 'SyncStatus', 'ConflictResolution',
    'ContentVersion', 'SyncEndpoint', 'SyncConflict', 'ContentSyncRequest', 'SyncResult',
    
    # System Index and Coordination
    'CollaborationIndex', 'CollaborationIndexConfig', 'CollaborationSystemStatus',
    'SystemHealthMetrics', 'collaboration_index', 'get_collaboration_index',
    'get_authenticated_creator', 'health_check'
]

# Version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Advanced collaboration business logic module for IA Influencer Agent"

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from .services.collaboration_orchestrator import CollaborationOrchestrator
from .services.matching_engine import MatchingEngine
from .services.partnership_manager import PartnershipManager
from .services.revenue_sharing_engine import RevenueSharingEngine
from .services.communication_hub import CommunicationHub

from .models.collaboration_models import (
    CollaborationRequest,
    Partnership,
    CollaborationProject,
    MatchingProfile,
    RevenueSplit
)

from .processors.request_processor import CollaborationRequestProcessor
from .processors.matching_processor import MatchingProcessor
from .processors.partnership_processor import PartnershipProcessor

from .analytics.collaboration_analytics import CollaborationAnalytics
from .analytics.performance_tracker import PerformanceTracker
from .analytics.revenue_analytics import RevenueAnalytics

__version__ = "2.0.0"

__all__ = [
    # Core Services
    "CollaborationOrchestrator",
    "MatchingEngine", 
    "PartnershipManager",
    "RevenueSharingEngine",
    "CommunicationHub",
    
    # Models
    "CollaborationRequest",
    "Partnership",
    "CollaborationProject",
    "MatchingProfile",
    "RevenueSplit",
    
    # Processors
    "CollaborationRequestProcessor",
    "MatchingProcessor", 
    "PartnershipProcessor",
    
    # Analytics
    "CollaborationAnalytics",
    "PerformanceTracker",
    "RevenueAnalytics"
]
