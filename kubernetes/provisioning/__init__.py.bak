"""Infrastructure Provisioning Module

Enterprise-grade infrastructure provisioning system for the IA Influencer Agent + Content Protection Platform.
This module handles automated infrastructure deployment, configuration management, and resource provisioning 
across cloud environments.

Project Owner: Fahed Mlaiel (mlaiel@live.de)

⚠️ CRITICAL LEGAL WARNING:
This software and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or appropriation of this code, concept, 
or business idea without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is strictly prohibited and will result in immediate legal action. All rights reserved.

Architecture Components:
- Cloud Providers: Multi-cloud infrastructure management
- Templates: Infrastructure as Code templates
- Scripts: Automated provisioning scripts
- Configs: Environment-specific configurations
- Validators: Infrastructure validation and testing
- Managers: Resource lifecycle management

Business Logic Flow:
Content Creator → Upload Multi-format → AI Protection → SEO Optimization → 
Collaboration Matching → Multi-platform Distribution
"""__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Enhanced imports for complete provisioning system
from .cloud_providers import *
from .templates import *
from .scripts import *
from .configs import *
from .validators import *
from .managers import *

# Core provisioning components
__all__ = [
    # Cloud Providers
    'AWSProvisioner',
    'GCPProvisioner', 
    'AzureProvisioner',
    'MultiCloudManager',
    
    # Templates
    'TerraformTemplate',
    'AnsiblePlaybook',
    'PulumiTemplate',
    'HelmChart',
    
    # Scripts
    'ProvisioningScript',
    'DeploymentScript',
    'ValidationScript',
    'RollbackScript',
    
    # Configs
    'EnvironmentConfig',
    'NetworkConfig',
    'SecurityConfig',
    'DatabaseConfig',
    
    # Validators
    'InfrastructureValidator',
    'SecurityValidator',
    'PerformanceValidator',
    'ComplianceValidator',
    
    # Managers
    'DeploymentManager',
    'ResourceManager',
    'ConfigurationManager',
    'LifecycleManager'
]

# Module configuration
PROVISIONING_CONFIG = {
    'supported_clouds': ['aws', 'gcp', 'azure'],
    'supported_environments': ['development', 'staging', 'production'],
    'infrastructure_components': [
        'kubernetes',
        'databases',
        'storage',
        'networking',
        'security',
        'monitoring'
    ],
    'deployment_strategies': [
        'blue_green',
        'rolling',
        'canary',
        'recreate'
    ]
}
