"""Backend Edge Computing Services
Edge computing modules for local inference, 5G MEC integration,
IoT mesh networking, and fog computing orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core local inference components
from .local_inference import LocalInferenceEngine, ModelType, InferenceBackend

# Import from 5g_mec.py using a valid Python import name
import importlib
_mec_module = importlib.import_module('backend.edge.5g_mec')
MECOrchestrator = _mec_module.MECOrchestrator
EdgeNode = _mec_module.EdgeNode
ServiceType = _mec_module.ServiceType

# Edge inference orchestrator
from .edge_inference import (
    EdgeInferenceOrchestrator,
    EdgeOptimizationStrategy,
    EdgeDeploymentMode,
    EdgeInferenceConfig,
    EdgeInferenceMetrics,
    create_edge_inference_orchestrator
)

# 5G MEC integration layer
_mec_integration_module = importlib.import_module('backend.edge.5g_mec_integration')
MECIntegrationLayer = _mec_integration_module.MECIntegrationLayer
IntegrationProtocol = _mec_integration_module.IntegrationProtocol
NetworkFunction = _mec_integration_module.NetworkFunction
SliceProfile = _mec_integration_module.SliceProfile
MECIntegrationConfig = _mec_integration_module.MECIntegrationConfig
NetworkSliceConfig = _mec_integration_module.NetworkSliceConfig
MECServiceRegistration = _mec_integration_module.MECServiceRegistration
create_mec_integration_layer = _mec_integration_module.create_mec_integration_layer

# IoT mesh network orchestration
from .iot_mesh_network import (
    IoTMeshOrchestrator,
    DeviceType,
    DeviceCapability,
    NetworkTopology,
    CommunicationProtocol,
    DeviceStatus,
    DeviceInfo,
    MeshLink,
    MeshRoute,
    IoTMeshConfig,
    create_iot_mesh_orchestrator
)

# Fog computing orchestration
from .fog_computing import (
    FogComputingOrchestrator,
    ProcessingTier,
    WorkloadType,
    ResourceType,
    TaskPriority,
    TaskStatus,
    LoadBalancingStrategy,
    FogNode,
    ProcessingTask,
    TaskExecution,
    FogComputingConfig,
    create_fog_computing_orchestrator
)

# Real-time optimization
from .real_time_optimizer import (
    RealTimeOptimizer,
    OptimizationStrategy,
    OptimizationScope,
    MetricType,
    PerformanceMetric,
    OptimizationTarget,
    OptimizationResult,
    create_real_time_optimizer
)

# Resource management
from .resource_manager import (
    EdgeResourceManager,
    ResourceType as ResourceManagerResourceType,
    ResourceStatus,
    AllocationStrategy,
    ResourcePriority,
    ResourceSpec,
    ResourceAllocation,
    ResourceUsage,
    ResourceNode,
    create_resource_manager
)

# Edge caching system
from .edge_cache import (
    EdgeCache,
    CacheStrategy,
    CacheType,
    CacheLevel,
    InvalidationStrategy,
    CacheItem,
    CacheStats,
    create_edge_cache
)

__all__ = [
    # Core local inference
    "LocalInferenceEngine",
    "ModelType", 
    "InferenceBackend",
    
    # Base MEC components
    "MECOrchestrator",
    "EdgeNode",
    "ServiceType",
    
    # Edge inference orchestration
    "EdgeInferenceOrchestrator",
    "EdgeOptimizationStrategy",
    "EdgeDeploymentMode",
    "EdgeInferenceConfig",
    "EdgeInferenceMetrics",
    "create_edge_inference_orchestrator",
    
    # 5G MEC integration
    "MECIntegrationLayer",
    "IntegrationProtocol",
    "NetworkFunction",
    "SliceProfile",
    "MECIntegrationConfig",
    "NetworkSliceConfig",
    "MECServiceRegistration",
    "create_mec_integration_layer",
    
    # IoT mesh networking
    "IoTMeshOrchestrator",
    "DeviceType",
    "DeviceCapability",
    "NetworkTopology",
    "CommunicationProtocol",
    "DeviceStatus",
    "DeviceInfo",
    "MeshLink",
    "MeshRoute",
    "IoTMeshConfig",
    "create_iot_mesh_orchestrator",
    
    # Fog computing
    "FogComputingOrchestrator",
    "ProcessingTier",
    "WorkloadType",
    "ResourceType",
    "TaskPriority",
    "TaskStatus",
    "LoadBalancingStrategy",
    "FogNode",
    "ProcessingTask",
    "TaskExecution",
    "FogComputingConfig",
    "create_fog_computing_orchestrator",
    
    # Real-time optimization
    "RealTimeOptimizer",
    "OptimizationStrategy",
    "OptimizationScope",
    "MetricType",
    "PerformanceMetric",
    "OptimizationTarget",
    "OptimizationResult",
    "create_real_time_optimizer",
    
    # Resource management
    "EdgeResourceManager",
    "ResourceManagerResourceType",
    "ResourceStatus",
    "AllocationStrategy",
    "ResourcePriority",
    "ResourceSpec",
    "ResourceAllocation",
    "ResourceUsage",
    "ResourceNode",
    "create_resource_manager",
    
    # Edge caching
    "EdgeCache",
    "CacheStrategy",
    "CacheType",
    "CacheLevel",
    "InvalidationStrategy",
    "CacheItem",
    "CacheStats",
    "create_edge_cache"
    
    # Monitoring module
    # Note: Individual monitoring components available via backend.edge.monitoring
    
    # Network module  
    # Note: Individual network components available via backend.edge.network
    
    # Security module
    # Note: Individual security components available via backend.edge.security
]