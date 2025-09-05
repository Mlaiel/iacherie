"""
Backend Orchestration Module - Complete Business Logic & AI Orchestration System

This module provides comprehensive orchestration capabilities including:
- Large-scale model ensemble management (100+ models)
- Privacy-preserving federated learning
- Brain-inspired neuromorphic computing  
- Distributed swarm intelligence decision making
- Creator business logic orchestration (NEW)
- Multi-format workflow orchestration (NEW)
- Creator-type specific orchestration (NEW)
- Content lifecycle orchestration (NEW)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# AI Orchestration Components (Existing)
from .model_ensemble import (
    LargeScaleEnsembleManager,
    ModelRegistry,
    EnsembleOrchestrator,
    ModelPool,
    EnsembleConfig,
    ModelMetrics,
    EnsembleStrategy
)

from .federated_learning import (
    FederatedOrchestrator,
    PrivacyPreservingLearning,
    FederatedClient,
    FederatedServer,
    PrivacyConfig,
    FederatedMetrics,
    PrivacyLevel
)

from .neuromorphic_compute import (
    NeuromorphicProcessor,
    SpikeNetworkOrchestrator,
    BrainInspiredCompute,
    NeuralPlasticity,
    SynapticComputing,
    NeuromorphicConfig,
    NeuronModel
)

from .swarm_intelligence import (
    SwarmOrchestrator,
    DistributedDecisionEngine,
    SwarmAgent,
    CollectiveIntelligence,
    EmergentBehavior,
    SwarmConfig,
    SwarmBehavior
)

# Business Logic Orchestration Components (NEW - Phase 1 & 2 Implementation)
from .creator_business_orchestrator import (
    CreatorBusinessOrchestrator,
    CreatorType,
    ContentFormat,
    BusinessStage,
    WorkflowStatus,
    CreatorProfile,
    ContentWorkflow,
    OrchestrationResult,
    get_creator_business_orchestrator
)

from .multi_format_workflow_orchestrator import (
    MultiFormatWorkflowOrchestrator,
    ContentFormat as MultiFormatContentFormat,
    ProcessingQuality,
    WorkflowMode,
    FormatPriority,
    FormatProcessingConfig,
    MultiFormatContent,
    WorkflowExecution,
    get_multi_format_workflow_orchestrator
)

from .creator_type_orchestration_engine import (
    CreatorTypeOrchestrationEngine,
    CreatorType as CreatorTypeEnum,
    SpecializationLevel,
    OptimizationStrategy,
    CreatorSpecialization,
    TypeSpecificWorkflow,
    get_creator_type_orchestration_engine
)

from .content_lifecycle_orchestrator import (
    ContentLifecycleOrchestrator,
    LifecycleStage,
    ContentStatus,
    LifecycleMode,
    ContentLifecycleProfile,
    LifecycleStageExecution,
    ContentLifecycleExecution,
    get_content_lifecycle_orchestrator
)

# IA Processing Business Orchestration (NEW - Phase 2)
from .ia_business_processing_orchestrator import (
    IABusinessProcessingOrchestrator,
    AIProcessingStage,
    AIModelType,
    ProcessingPriority,
    BusinessImpactLevel,
    AIModel,
    IAProcessingRequest,
    IAProcessingExecution,
    get_ia_business_processing_orchestrator
)

__all__ = [
    # AI Orchestration (Existing)
    # Model Ensemble
    "LargeScaleEnsembleManager",
    "ModelRegistry", 
    "EnsembleOrchestrator",
    "ModelPool",
    "EnsembleConfig",
    "ModelMetrics",
    "EnsembleStrategy",
    
    # Federated Learning
    "FederatedOrchestrator",
    "PrivacyPreservingLearning",
    "FederatedClient",
    "FederatedServer", 
    "PrivacyConfig",
    "FederatedMetrics",
    "PrivacyLevel",
    
    # Neuromorphic Computing
    "NeuromorphicProcessor",
    "SpikeNetworkOrchestrator",
    "BrainInspiredCompute",
    "NeuralPlasticity",
    "SynapticComputing",
    "NeuromorphicConfig",
    "NeuronModel",
    
    # Swarm Intelligence
    "SwarmOrchestrator",
    "DistributedDecisionEngine", 
    "SwarmAgent",
    "CollectiveIntelligence",
    "EmergentBehavior",
    "SwarmConfig",
    "SwarmBehavior",
    
    # Business Logic Orchestration (NEW - Phase 1 & 2)
    # Creator Business Orchestration
    "CreatorBusinessOrchestrator",
    "CreatorType",
    "ContentFormat", 
    "BusinessStage",
    "WorkflowStatus",
    "CreatorProfile",
    "ContentWorkflow",
    "OrchestrationResult",
    "get_creator_business_orchestrator",
    
    # Multi-Format Workflow Orchestration
    "MultiFormatWorkflowOrchestrator",
    "MultiFormatContentFormat",
    "ProcessingQuality",
    "WorkflowMode", 
    "FormatPriority",
    "FormatProcessingConfig",
    "MultiFormatContent",
    "WorkflowExecution",
    "get_multi_format_workflow_orchestrator",
    
    # Creator Type Orchestration
    "CreatorTypeOrchestrationEngine",
    "CreatorTypeEnum",
    "SpecializationLevel",
    "OptimizationStrategy",
    "CreatorSpecialization", 
    "TypeSpecificWorkflow",
    "get_creator_type_orchestration_engine",
    
    # Content Lifecycle Orchestration
    "ContentLifecycleOrchestrator",
    "LifecycleStage",
    "ContentStatus",
    "LifecycleMode",
    "ContentLifecycleProfile",
    "LifecycleStageExecution", 
    "ContentLifecycleExecution",
    "get_content_lifecycle_orchestrator",
    
    # IA Processing Business Orchestration (NEW - Phase 2)
    "IABusinessProcessingOrchestrator",
    "AIProcessingStage",
    "AIModelType",
    "ProcessingPriority",
    "BusinessImpactLevel",
    "AIModel",
    "IAProcessingRequest",
    "IAProcessingExecution",
    "get_ia_business_processing_orchestrator"
]