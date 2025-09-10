"""
Deployment Infrastructure Module
===================================
Enterprise deployment management for Ainflue platform

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue - IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved
"""

from .blue_green_deployer import BluegreendeployerManager, get_blue_green_deployer_manager
from .canary_deployer import CanarydeployerManager, get_canary_deployer_manager
from .pipeline_orchestrator import PipelineorchestratorManager, get_pipeline_orchestrator_manager

# Aliases for compatibility
DeploymentManager = BluegreendeployerManager
CICDManager = PipelineorchestratorManager  
PipelineManager = PipelineorchestratorManager
ReleaseManager = CanarydeployerManager

def get_deployment_manager():
    return get_blue_green_deployer_manager()

def get_cicd_manager():
    return get_pipeline_orchestrator_manager()
    
def get_pipeline_manager():
    return get_pipeline_orchestrator_manager()
    
def get_release_manager():
    return get_canary_deployer_manager()

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

__all__ = [
    "BluegreendeployerManager", "get_blue_green_deployer_manager",
    "CanarydeployerManager", "get_canary_deployer_manager", 
    "PipelineorchestratorManager", "get_pipeline_orchestrator_manager",
    "DeploymentManager", "CICDManager", "PipelineManager", "ReleaseManager",
    "get_deployment_manager", "get_cicd_manager", "get_pipeline_manager", "get_release_manager"
]