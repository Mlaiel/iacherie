"""
Collaborative Features Module - IA Influencer Agent

Enterprise-grade collaboration system for multi-format content creators
enabling real-time collaboration, project management, team coordination,
and monetization opportunities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de

Project Team Specialties:
- Lead AI Developer & Architect: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI
- ML Engineer: TensorFlow/PyTorch/Hugging Face
- Audio Processing Engineer: Spotify/Audio Analysis
- DevOps Engineer: Kubernetes/Docker/CI-CD
- Database Administrator: PostgreSQL/Redis/Vector DB
- Security Engineer: Enterprise Security/Compliance
- Microservices Architect: Distributed Systems
"""

from .team_coordination import (
    TeamManager,
    CollaboratorInviteService,
    RolePermissionManager,
    TeamWorkflowOrchestrator,
    CollaborationHub
)

from .project_management import (
    ProjectCoordinator,
    TaskDistributionEngine,
    MilestoneTracker,
    ResourceAllocationManager,
    ProjectTimelineManager
)

from .matching_engine import (
    CollaborationMatcher,
    SkillBasedMatcher,
    ProjectCompatibilityAnalyzer,
    InfluencerNetworkEngine,
    OpportunityDetector
)

from .communication_hub import (
    CollaborativeCommunicationManager,
    RealTimeMessageHandler,
    VideoConferenceIntegrator,
    FileShareCoordinator,
    NotificationDispatcher
)

from .workflow_synchronization import (
    WorkflowSynchronizer,
    ContentVersionController,
    ConflictResolutionManager,
    SynchronousEditingEngine,
    WorkflowStateManager
)

from .revenue_sharing import (
    RevenueDistributionEngine,
    ContractAutomationService,
    PaymentOrchestratorService,
    RoyaltyCalculationEngine,
    FinancialReportingManager
)

from .collaboration_analytics import (
    CollaborationMetricsCollector,
    TeamPerformanceAnalyzer,
    EngagementTracker,
    ProductivityMeasurer,
    ROICalculator
)

from .networking_engine import (
    ProfessionalNetworkingEngine,
    InfluencerDiscoveryService,
    NetworkGrowthOptimizer,
    ConnectionRecommendationEngine,
    CommunityBuildingFacilitator
)

from .content_co_creation import (
    CoCreationWorkspace,
    CollaborativeEditingEngine,
    ContentMergingSystem,
    CreativeWorkflowManager,
    MultiFormatCoCreator
)

from .partnership_management import (
    PartnershipBroker,
    BrandCollaborationManager,
    SponsorshipCoordinator,
    CampaignManagementService,
    ContractNegotiationEngine
)

from .index import (
    CollaborativeFeaturesRegistry,
    CollaborationWorkflowManager,
    collaboration_registry,
    get_collaboration_service,
    initialize_collaboration_features,
    get_feature_summary
)

__all__ = [
    # Team Coordination
    "TeamManager",
    "CollaboratorInviteService", 
    "RolePermissionManager",
    "TeamWorkflowOrchestrator",
    "CollaborationHub",
    
    # Project Management
    "ProjectCoordinator",
    "TaskDistributionEngine",
    "MilestoneTracker", 
    "ResourceAllocationManager",
    "ProjectTimelineManager",
    
    # Matching Engine
    "CollaborationMatcher",
    "SkillBasedMatcher",
    "ProjectCompatibilityAnalyzer",
    "InfluencerNetworkEngine",
    "OpportunityDetector",
    
    # Communication Hub
    "CollaborativeCommunicationManager",
    "RealTimeMessageHandler",
    "VideoConferenceIntegrator",
    "FileShareCoordinator",
    "NotificationDispatcher",
    
    # Workflow Synchronization
    "WorkflowSynchronizer",
    "ContentVersionController",
    "ConflictResolutionManager",
    "SynchronousEditingEngine",
    "WorkflowStateManager",
    
    # Revenue Sharing
    "RevenueDistributionEngine",
    "ContractAutomationService",
    "PaymentOrchestratorService",
    "RoyaltyCalculationEngine",
    "FinancialReportingManager",
    
    # Collaboration Analytics
    "CollaborationMetricsCollector",
    "TeamPerformanceAnalyzer",
    "EngagementTracker",
    "ProductivityMeasurer",
    "ROICalculator",
    
    # Networking Engine
    "ProfessionalNetworkingEngine",
    "InfluencerDiscoveryService",
    "NetworkGrowthOptimizer",
    "ConnectionRecommendationEngine",
    "CommunityBuildingFacilitator",
    
    # Content Co-Creation
    "CoCreationWorkspace",
    "CollaborativeEditingEngine",
    "ContentMergingSystem",
    "CreativeWorkflowManager",
    "MultiFormatCoCreator",
    
    # Partnership Management
    "PartnershipBroker",
    "BrandCollaborationManager",
    "SponsorshipCoordinator",
    "CampaignManagementService",
    "ContractNegotiationEngine",
    
    # Registry and Management
    "CollaborativeFeaturesRegistry",
    "CollaborationWorkflowManager",
    "collaboration_registry",
    "get_collaboration_service",
    "initialize_collaboration_features",
    "get_feature_summary"
]
