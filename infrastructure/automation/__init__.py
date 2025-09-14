"""
Automation Module - Enterprise Infrastructure Automation
================================================================================

Expert Team: DevOps + Backend Senior + Security + Lead Dev IA
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚙️ DevOps: Infrastructure automation, CI/CD pipelines, deployment automation
🏗️ Backend Senior: Microservices orchestration, service automation
🔒 Security: Security automation, compliance automation
🧠 Lead Dev IA: AI-powered automation, intelligent infrastructure management

Enterprise automation for Ainflue infrastructure including:
- Ansible automation and configuration management
- Terraform Infrastructure as Code
- CI/CD pipeline automation
- Deployment automation across multiple environments
- Security and compliance automation
- Multi-cloud automation orchestration
"""

from .ansible import AnsibleAutomation
from .terraform import TerraformIaC
from .ci_cd_pipeline_manager import CICDPipelineManager
from .deployment_automation import DeploymentAutomation
from .infrastructure_automation import InfrastructureAutomation
from .configuration_automation import ConfigurationAutomation
from .testing_automation import TestingAutomation
from .monitoring_automation import MonitoringAutomation
from .security_automation import SecurityAutomation
from .backup_automation import BackupAutomation
from .multi_cloud_automation import MultiCloudAutomation
from .workflow_automation import WorkflowAutomation
from .compliance_automation import ComplianceAutomation

__all__ = [
    'AnsibleAutomation',
    'TerraformIaC',
    'CICDPipelineManager',
    'DeploymentAutomation',
    'InfrastructureAutomation',
    'ConfigurationAutomation',
    'TestingAutomation',
    'MonitoringAutomation',
    'SecurityAutomation',
    'BackupAutomation',
    'MultiCloudAutomation',
    'WorkflowAutomation',
    'ComplianceAutomation'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise infrastructure automation for Ainflue platform"