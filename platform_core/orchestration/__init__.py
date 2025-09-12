# Platform Core Orchestration Module
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: © 2025 Fahed Mlaiel. All rights reserved.

"""
Platform Core Orchestration - Enterprise orchestration modules for Ainflue AI Creator Platform.

This module provides comprehensive orchestration capabilities including:
- Platform Orchestration Management
- Service Registry Management
- Workflow Engine Core
- Event Orchestration
- Resource Coordination
- Platform Health Monitoring
- Configuration Orchestration
- Security Orchestration
- Deployment Coordination
- Integration Coordination
- Performance Orchestration
"""

# Core Orchestration Modules
from .platform_orchestration_manager import PlatformOrchestrationManager
from .service_registry_manager import ServiceRegistryManager
from .workflow_engine_core import WorkflowEngineCore
from .event_orchestrator import EventOrchestrator
from .resource_coordinator import ResourceCoordinator
from .platform_health_monitor import PlatformHealthMonitor
from .configuration_orchestrator import ConfigurationOrchestrator
from .security_orchestrator import SecurityOrchestrator

# Extended Orchestration Modules
from .deployment_coordinator import DeploymentCoordinator, DeploymentStrategy, DeploymentStatus, DeploymentConfig
from .integration_coordinator import IntegrationCoordinator, IntegrationType, IntegrationStatus, SynchronizationMode
from .performance_orchestrator import PerformanceOrchestrator, OptimizationLevel, PerformanceMetricType, AlertSeverity

__all__ = [
    # Core Orchestration
    "PlatformOrchestrationManager",
    "ServiceRegistryManager", 
    "WorkflowEngineCore",
    "EventOrchestrator",
    "ResourceCoordinator",
    "PlatformHealthMonitor",
    "ConfigurationOrchestrator",
    "SecurityOrchestrator",
    
    # Extended Orchestration
    "DeploymentCoordinator",
    "DeploymentStrategy",
    "DeploymentStatus", 
    "DeploymentConfig",
    "IntegrationCoordinator",
    "IntegrationType",
    "IntegrationStatus",
    "SynchronizationMode",
    "PerformanceOrchestrator",
    "OptimizationLevel",
    "PerformanceMetricType",
    "AlertSeverity"
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise Platform Core Orchestration for Ainflue AI Creator Platform"