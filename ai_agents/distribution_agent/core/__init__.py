"""
Core Distribution Module - Enterprise Distribution Engine Components

Ultra-advanced core components for multi-platform content distribution
with AI-powered optimization and intelligent orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .distribution_engine import (
    DistributionEngine,
    DistributionJob,
    DistributionResult,
    DistributionStatus,
    PlatformType,
    ContentType,
    ContentMetadata,
    PlatformSpecification
)

from .orchestrator import (
    DistributionOrchestrator,
    JobPriority,
    JobExecution,
    WorkerPool,
    OrchestrationStrategy,
    ResourceType
)

from .coordinator import (
    CampaignCoordinator,
    CampaignConfig,
    CampaignExecution,
    CampaignType,
    CampaignStatus,
    SyncStrategy,
    CampaignGoal,
    PlatformStrategy,
    CollaborationSpec
)

__all__ = [
    "DistributionEngine",
    "DistributionJob",
    "DistributionResult", 
    "DistributionStatus",
    "PlatformType",
    "ContentType",
    "ContentMetadata",
    "PlatformSpecification",
    "DistributionOrchestrator",
    "JobPriority",
    "JobExecution",
    "WorkerPool",
    "OrchestrationStrategy",
    "ResourceType",
    "CampaignCoordinator",
    "CampaignConfig",
    "CampaignExecution",
    "CampaignType",
    "CampaignStatus",
    "SyncStrategy",
    "CampaignGoal",
    "PlatformStrategy",
    "CollaborationSpec"
]
