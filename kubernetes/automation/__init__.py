"""
Deployment Automation Module - IA Influencer Agent

Enterprise-grade deployment automation system providing comprehensive
orchestration, environment management, service deployment, monitoring,
scaling, notifications, and complete pipeline execution capabilities
for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

IMPORTANT LEGAL NOTICE:
This module contains proprietary technology and intellectual property.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Contact mlaiel@live.de for licensing and authorization.

Core Components:
- Workflow Orchestrator: Advanced deployment workflow management
- Environment Provisioner: Multi-cloud infrastructure provisioning  
- Service Deployer: Intelligent service deployment with multiple strategies
- Configuration Manager: Enterprise configuration and secrets management
- Health Validator: Comprehensive health monitoring and validation
- Rollback Manager: Automated rollback and disaster recovery
- Scaling Controller: Intelligent auto-scaling and resource management
- Notification Handler: Multi-channel notification and alerting system
- Deployment Recorder: Comprehensive deployment tracking and audit trails
- Pipeline Executor: Advanced pipeline orchestration and execution engine
"""

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"

from .workflow_orchestrator import WorkflowOrchestrator
from .environment_provisioner import EnvironmentProvisioner
from .service_deployer import ServiceDeployer
from .configuration_manager import ConfigurationManager
from .health_validator import HealthValidator
from .rollback_manager import RollbackManager
from .scaling_controller import ScalingController
from .notification_handler import NotificationHandler
from .deployment_recorder import DeploymentRecorder
from .pipeline_executor import PipelineExecutor

__all__ = [
    "WorkflowOrchestrator",
    "EnvironmentProvisioner", 
    "ServiceDeployer",
    "ConfigurationManager",
    "HealthValidator",
    "RollbackManager",
    "ScalingController",
    "NotificationHandler",
    "DeploymentRecorder",
    "PipelineExecutor"
]
