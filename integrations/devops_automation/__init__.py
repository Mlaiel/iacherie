"""⚙️ DevOps Automation Module - Enterprise Implementation
======================================================

Module d'automation DevOps enterprise avec CI/CD avancé, Infrastructure as Code
et monitoring distribué pour Ainflue.

Author: Fahed Mlaiel (mlaiel@live.de)
Date: 14 Septembre 2025
"""

from .enterprise_devops_automation import (
    EnterpriseDevOpsAutomation,
    PipelineConfiguration,
    DeploymentJob,
    InfrastructureResource,
    MonitoringAlert,
    DeploymentStage,
    DeploymentStrategy,
    InfrastructureProvider,
    MonitoringLevel,
    AlertSeverity,
    initialize_devops_automation
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "EnterpriseDevOpsAutomation",
    "PipelineConfiguration",
    "DeploymentJob",
    "InfrastructureResource",
    "MonitoringAlert",
    "DeploymentStage",
    "DeploymentStrategy",
    "InfrastructureProvider",
    "MonitoringLevel",
    "AlertSeverity",
    "initialize_devops_automation"
]