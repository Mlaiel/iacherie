"""Deployment Environments Module - IA Influencer Agent
====================================================
Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Multi-format Creator Platform with AI Protection & Monetization

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Comprehensive deployment environment management for all deployment scenarios.
Supports development, production, staging, testing, Docker, Kubernetes, cloud, 
performance, security, and monitoring environments.
====================================================
"""
# Core Environment Managers
from .development import DevelopmentEnvironmentManager
from .production import ProductionEnvironmentManager
from .staging import StagingEnvironmentManager
from .testing import TestingEnvironmentManager

# Infrastructure Environment Managers
from .docker import DockerEnvironmentManager
from .kubernetes import KubernetesEnvironmentManager
from .cloud import CloudEnvironmentManager

# Specialized Environment Managers
from .performance import PerformanceEnvironmentManager
from .security import SecurityEnvironmentManager
from .monitoring import MonitoringEnvironmentManager

__all__ = [
    # Core Environments
    'DevelopmentEnvironmentManager',
    'ProductionEnvironmentManager', 
    'StagingEnvironmentManager',
    'TestingEnvironmentManager',
    
    # Infrastructure Environments
    'DockerEnvironmentManager',
    'KubernetesEnvironmentManager',
    'CloudEnvironmentManager',
    
    # Specialized Environments
    'PerformanceEnvironmentManager',
    'SecurityEnvironmentManager',
    'MonitoringEnvironmentManager'
]

from .development import DevelopmentEnvironmentManager
from .staging import StagingEnvironmentManager  
from .production import ProductionEnvironmentManager
from .testing import TestingEnvironmentManager
from .docker import DockerEnvironmentManager
from .kubernetes import KubernetesEnvironmentManager
from .cloud import CloudEnvironmentManager
from .performance import PerformanceEnvironmentManager
from .security import SecurityEnvironmentManager
from .monitoring import MonitoringEnvironmentManager
from .backup import BackupEnvironmentManager
from .networking import NetworkingEnvironmentManager
from .storage import StorageEnvironmentManager
from .compliance import ComplianceEnvironmentManager
from .integration import IntegrationEnvironmentManager

__all__ = [
    'DevelopmentEnvironmentManager',
    'StagingEnvironmentManager',
    'ProductionEnvironmentManager', 
    'TestingEnvironmentManager',
    'DockerEnvironmentManager',
    'KubernetesEnvironmentManager',
    'CloudEnvironmentManager',
    'PerformanceEnvironmentManager',
    'SecurityEnvironmentManager',
    'MonitoringEnvironmentManager',
    'BackupEnvironmentManager',
    'NetworkingEnvironmentManager',
    'StorageEnvironmentManager',
    'ComplianceEnvironmentManager',
    'IntegrationEnvironmentManager'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__team__ = "Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer"
__project__ = "IA Influencer Agent - Multi-format Creator Platform with AI Protection & Monetization"
