"""MongoDB Deployment Automation Module
=====================================

Production-ready deployment automation for MongoDB clusters and infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from .cluster_deployer import ClusterDeployer, DeploymentConfig
from .kubernetes_manager import KubernetesManager, KubernetesConfig
from .monitoring_setup import MonitoringSetup, MonitoringConfig
from .backup_automation import BackupAutomation, BackupConfig
from .security_hardening import SecurityHardening, SecurityConfig
from .health_checker import HealthChecker, HealthConfig

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel (mlaiel@live.de)"

__all__ = [
    'ClusterDeployer',
    'DeploymentConfig',
    'KubernetesManager',
    'KubernetesConfig',
    'MonitoringSetup',
    'MonitoringConfig',
    'BackupAutomation',
    'BackupConfig',
    'SecurityHardening',
    'SecurityConfig',
    'HealthChecker',
    'HealthConfig'
]