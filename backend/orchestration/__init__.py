"""
Backend Orchestration Module - Advanced AI Orchestration System

This module provides advanced AI orchestration capabilities including:
- Large-scale model ensemble management (100+ models)
- Privacy-preserving federated learning
- Brain-inspired neuromorphic computing
- Distributed swarm intelligence decision making

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

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

__all__ = [
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
    "SwarmBehavior"
]