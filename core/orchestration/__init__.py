"""Ainflue Core Orchestration - Enterprise System Orchestration
============================================================

Core orchestration management providing enterprise orchestration, microservices
coordination, business logic pipelines, workflow engines, state machines,
saga patterns, event-driven architecture, and cloud-native orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any

# Orchestration core imports (existing files to be moved here)
try:
    from .enterprise_orchestration_core import EnterpriseOrchestrationCore
except ImportError:
    EnterpriseOrchestrationCore = None

try:
    from .microservices_core import MicroservicesCore
except ImportError:
    MicroservicesCore = None

try:
    from .business_logic_pipeline_core import BusinessLogicPipelineCore
except ImportError:
    BusinessLogicPipelineCore = None

# New orchestration core files (to be created)
try:
    from .workflow_engine_core import WorkflowEngineCore
except ImportError:
    WorkflowEngineCore = None

try:
    from .state_machine_core import StateMachineCore
except ImportError:
    StateMachineCore = None

try:
    from .saga_pattern_core import SagaPatternCore
except ImportError:
    SagaPatternCore = None

try:
    from .event_driven_core import EventDrivenCore
except ImportError:
    EventDrivenCore = None

try:
    from .async_orchestrator_core import AsyncOrchestratorCore
except ImportError:
    AsyncOrchestratorCore = None

try:
    from .pipeline_scheduler_core import PipelineSchedulerCore
except ImportError:
    PipelineSchedulerCore = None

try:
    from .task_coordinator_core import TaskCoordinatorCore
except ImportError:
    TaskCoordinatorCore = None

try:
    from .process_automation_core import ProcessAutomationCore
except ImportError:
    ProcessAutomationCore = None

try:
    from .integration_hub_core import IntegrationHubCore
except ImportError:
    IntegrationHubCore = None

try:
    from .api_composition_core import APICompositionCore
except ImportError:
    APICompositionCore = None

try:
    from .service_mesh_core import ServiceMeshCore
except ImportError:
    ServiceMeshCore = None

try:
    from .kubernetes_operator_core import KubernetesOperatorCore
except ImportError:
    KubernetesOperatorCore = None

try:
    from .container_orchestration_core import ContainerOrchestrationCore
except ImportError:
    ContainerOrchestrationCore = None

try:
    from .cloud_native_core import CloudNativeCore
except ImportError:
    CloudNativeCore = None

__all__ = [
    "EnterpriseOrchestrationCore", "MicroservicesCore", "BusinessLogicPipelineCore",
    "WorkflowEngineCore", "StateMachineCore", "SagaPatternCore", "EventDrivenCore",
    "AsyncOrchestratorCore", "PipelineSchedulerCore", "TaskCoordinatorCore",
    "ProcessAutomationCore", "IntegrationHubCore", "APICompositionCore",
    "ServiceMeshCore", "KubernetesOperatorCore", "ContainerOrchestrationCore",
    "CloudNativeCore"
]