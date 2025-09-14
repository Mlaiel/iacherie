"""
  Init   module
Enterprise implementation for Ainflue platform
"""

# Platform Core Enterprise Architecture Module
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: © 2025 Fahed Mlaiel. All rights reserved.

"""
Platform Core Enterprise Architecture

Comprehensive platform orchestration, management, and infrastructure services
for the Ainflue AI creator platform ecosystem.

This module provides:
- Platform Orchestration Engine
- Communication Infrastructure
- Enterprise Management Systems
- Notification and Support Systems
- Additional Enterprise Modules
"""

# Orchestration Engine Components
from .orchestration.platform_orchestration_manager import PlatformOrchestrationManager, create_platform_orchestrator
from .orchestration.service_registry_manager import ServiceRegistryManager, create_service_registry
from .orchestration.workflow_engine_core import WorkflowEngineCore, create_workflow_engine
from .orchestration.event_orchestrator import EventOrchestrator, create_event_orchestrator
from .orchestration.resource_coordinator import ResourceCoordinator, create_resource_coordinator
from .orchestration.platform_health_monitor import PlatformHealthMonitor, create_platform_health_monitor
from .orchestration.configuration_orchestrator import ConfigurationOrchestrator, create_configuration_orchestrator
from .orchestration.security_orchestrator import SecurityOrchestrator, create_security_orchestrator

__all__ = [
    # Orchestration Engine
    'PlatformOrchestrationManager',
    'create_platform_orchestrator',
    'ServiceRegistryManager', 
    'create_service_registry',
    'WorkflowEngineCore',
    'create_workflow_engine',
    'EventOrchestrator',
    'create_event_orchestrator',
    'ResourceCoordinator',
    'create_resource_coordinator',
    'PlatformHealthMonitor',
    'create_platform_health_monitor',
    'ConfigurationOrchestrator',
    'create_configuration_orchestrator',
    'SecurityOrchestrator',
    'create_security_orchestrator'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel (mlaiel@live.de)"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
