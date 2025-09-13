"""Deployment Infrastructure Management - Complete Module
=========================================================
Consolidated deployment functionality with core deployment integration

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue Infrastructure Enterprise
License: Proprietary - All rights reserved
"""

# Core deployment functionality (from root deployment.py)
try:
    from .core_deployment import (
        DeploymentManager, CICDManager, PipelineManager, 
        DeploymentStrategy, PipelineStatus, PipelineConfig
    )
except ImportError:
    DeploymentManager = CICDManager = PipelineManager = None
    DeploymentStrategy = PipelineStatus = PipelineConfig = None

# Specialized deployment modules
try:
    from .blue_green_deployer import BlueGreenDeployer
except ImportError:
    BlueGreenDeployer = None

try:
    from .canary_deployer import CanaryDeployer
except ImportError:
    CanaryDeployer = None

try:
    from .rolling_updater import RollingUpdater
except ImportError:
    RollingUpdater = None

try:
    from .feature_flag_manager import FeatureFlagManager
except ImportError:
    FeatureFlagManager = None

try:
    from .pipeline_orchestrator import PipelineOrchestrator
except ImportError:
    PipelineOrchestrator = None

try:
    from .environment_manager import EnvironmentManager
except ImportError:
    EnvironmentManager = None

try:
    from .rollback_manager import RollbackManager
except ImportError:
    RollbackManager = None

try:
    from .validation_engine import ValidationEngine
except ImportError:
    ValidationEngine = None

try:
    from .release_manager import ReleaseManager
except ImportError:
    ReleaseManager = None

__all__ = [
    # Core deployment
    'DeploymentManager', 'CICDManager', 'PipelineManager',
    'DeploymentStrategy', 'PipelineStatus', 'PipelineConfig',
    # Specialized deployers
    'BlueGreenDeployer', 'CanaryDeployer', 'RollingUpdater', 
    'FeatureFlagManager', 'PipelineOrchestrator', 'EnvironmentManager', 
    'RollbackManager', 'ValidationEngine', 'ReleaseManager'
]