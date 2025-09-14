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

# Deployment automation tools
try:
    from .ansible import (
        AnsibleManager, PlaybookRunner, ConfigurationManager, InventoryManager,
        ansible_manager, playbook_runner, configuration_manager, inventory_manager
    )
except ImportError:
    AnsibleManager = PlaybookRunner = ConfigurationManager = InventoryManager = None
    ansible_manager = playbook_runner = configuration_manager = inventory_manager = None

try:
    from .terraform import (
        TerraformManager, InfrastructureProvisioner, CloudResourceManager, StateManager,
        terraform_manager, infrastructure_provisioner, cloud_resource_manager, state_manager
    )
except ImportError:
    TerraformManager = InfrastructureProvisioner = CloudResourceManager = StateManager = None
    terraform_manager = infrastructure_provisioner = cloud_resource_manager = state_manager = None

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
    # Automation tools
    'AnsibleManager', 'PlaybookRunner', 'ConfigurationManager', 'InventoryManager',
    'ansible_manager', 'playbook_runner', 'configuration_manager', 'inventory_manager',
    'TerraformManager', 'InfrastructureProvisioner', 'CloudResourceManager', 'StateManager',
    'terraform_manager', 'infrastructure_provisioner', 'cloud_resource_manager', 'state_manager',
    # Specialized deployers
    'BlueGreenDeployer', 'CanaryDeployer', 'RollingUpdater', 
    'FeatureFlagManager', 'PipelineOrchestrator', 'EnvironmentManager', 
    'RollbackManager', 'ValidationEngine', 'ReleaseManager'
]
# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Deployment infrastructure module for Ainflue creator platform"

