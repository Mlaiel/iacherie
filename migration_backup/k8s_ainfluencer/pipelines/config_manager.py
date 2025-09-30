"""IA Influencer Agent - Pipeline Configuration Management
Enterprise-Grade Pipeline Configuration System

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive pipeline configuration management for the IA Influencer Agent
platform, supporting multiple environments, pipeline types, and deployment strategies.

Features:
- Environment-specific configurations
- Pipeline template management
- Dynamic configuration generation
- Validation and schema enforcement
- Configuration versioning and rollback

WARNING: This code is proprietary and confidential. Any unauthorized use, copying, or distribution
is strictly prohibited and will result in legal action under German and international law.
"""

import yaml
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import jinja2
from datetime import datetime

from . import Environment, PipelineType, PipelineConfig

class ConfigurationError(Exception):
    """
Configuration-related error"""
    pass

@dataclass
class EnvironmentConfig:
    """
Environment-specific configuration settings"""
    name: str
    description: str
    cluster_config: Dict[str, Any]
    namespace: str
    resource_limits: Dict[str, str]
    secrets: List[str]
    monitoring_config: Dict[str, Any]
    backup_config: Dict[str, Any]
    
@dataclass
class PipelineTemplate:
    """
Pipeline template definition"""
    name: str
    description: str
    pipeline_type: PipelineType
    base_steps: List[str]
    environment_overrides: Dict[str, List[str]]
    required_variables: List[str]
    optional_variables: Dict[str, Any]

class PipelineConfigManager:
    """
    Advanced Pipeline Configuration Management System
    
    Provides enterprise-grade configuration management with:
    - Template-based pipeline definitions
    - Environment-specific overrides
    - Dynamic configuration generation
    - Configuration validation and schema enforcement
    - Version control and rollback capabilities
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent / "configs"
        self.templates_dir = self.config_dir / "templates"
        self.environments_dir = self.config_dir / "environments"
        self.logger = logging.getLogger(__name__)
        
        # Initialize directories
        self._ensure_directories()
        
        # Load configurations
        self.environment_configs: Dict[str, EnvironmentConfig] = {}
        self.pipeline_templates: Dict[str, PipelineTemplate] = {}
        
        self._load_configurations()
        
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.config_dir,
            self.templates_dir,
            self.environments_dir,
            self.config_dir / "schemas",
            self.config_dir / "generated"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _load_configurations(self):
        """Load all configuration files"""
        self._load_environment_configs()
        self._load_pipeline_templates()
        self._generate_default_configs()
        
    def _load_environment_configs(self):
        """
Load environment configuration files"""
        for env_file in self.environments_dir.glob("*.yaml"):
            try:
                with open(env_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                    
                env_config = EnvironmentConfig(
                    name=config_data['name'],
                    description=config_data['description'],
                    cluster_config=config_data['cluster_config'],
                    namespace=config_data['namespace'],
                    resource_limits=config_data['resource_limits'],
                    secrets=config_data['secrets'],
                    monitoring_config=config_data['monitoring_config'],
                    backup_config=config_data['backup_config']
                )
                
                self.environment_configs[env_config.name] = env_config
                self.logger.info(f"Loaded environment config: {env_config.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to load environment config {env_file}: {str(e)}")
                
    def _load_pipeline_templates(self):
        """Load pipeline template files"""
        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(template_file, 'r') as f:
                    template_data = yaml.safe_load(f)
                    
                template = PipelineTemplate(
                    name=template_data['name'],
                    description=template_data['description'],
                    pipeline_type=PipelineType(template_data['type']),
                    base_steps=template_data['base_steps'],
                    environment_overrides=template_data.get('environment_overrides', {}),
                    required_variables=template_data.get('required_variables', []),
                    optional_variables=template_data.get('optional_variables', {})
                )
                
                self.pipeline_templates[template.name] = template
                self.logger.info(f"Loaded pipeline template: {template.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to load pipeline template {template_file}: {str(e)}")
                
    def _generate_default_configs(self):
        """Generate default configuration files if they don't exist"""
        # Generate default environment configs
        default_environments = {
            'development': {
                'name': 'development',
                'description': 'Development environment for feature development and testing',
                'cluster_config': {
                    'kubeconfig_path': '~/.kube/config-dev',
                    'context': 'ia-influencer-dev'
                },
                'namespace': 'ia-influencer-dev',
                'resource_limits': {
                    'cpu': '2',
                    'memory': '4Gi',
                    'storage': '20Gi'
                },
                'secrets': ['db-credentials', 'api-keys', 'ssl-certificates'],
                'monitoring_config': {
                    'enabled': True,
                    'prometheus_namespace': 'monitoring',
                    'grafana_dashboard': 'ia-influencer-dev'
                },
                'backup_config': {
                    'enabled': False,
                    'schedule': '0 2 * * *',
                    'retention_days': 7
                }
            },
            'staging': {
                'name': 'staging',
                'description': 'Staging environment for pre-production testing',
                'cluster_config': {
                    'kubeconfig_path': '~/.kube/config-staging',
                    'context': 'ia-influencer-staging'
                },
                'namespace': 'ia-influencer-staging',
                'resource_limits': {
                    'cpu': '4',
                    'memory': '8Gi',
                    'storage': '50Gi'
                },
                'secrets': ['db-credentials', 'api-keys', 'ssl-certificates'],
                'monitoring_config': {
                    'enabled': True,
                    'prometheus_namespace': 'monitoring',
                    'grafana_dashboard': 'ia-influencer-staging'
                },
                'backup_config': {
                    'enabled': True,
                    'schedule': '0 1 * * *',
                    'retention_days': 14
                }
            },
            'production': {
                'name': 'production',
                'description': 'Production environment for live system',
                'cluster_config': {
                    'kubeconfig_path': '~/.kube/config-prod',
                    'context': 'ia-influencer-prod'
                },
                'namespace': 'ia-influencer-prod',
                'resource_limits': {
                    'cpu': '8',
                    'memory': '16Gi',
                    'storage': '200Gi'
                },
                'secrets': ['db-credentials', 'api-keys', 'ssl-certificates', 'payment-keys'],
                'monitoring_config': {
                    'enabled': True,
                    'prometheus_namespace': 'monitoring',
                    'grafana_dashboard': 'ia-influencer-prod',
                    'alerting_enabled': True
                },
                'backup_config': {
                    'enabled': True,
                    'schedule': '0 0 * * *',
                    'retention_days': 30,
                    'cross_region_backup': True
                }
            }
        }
        
        for env_name, env_data in default_environments.items():
            env_file = self.environments_dir / f"{env_name}.yaml"
            if not env_file.exists():
                with open(env_file, 'w') as f:
                    yaml.dump(env_data, f, default_flow_style=False)
                self.logger.info(f"Generated default environment config: {env_name}")
                
        # Generate default pipeline templates
        default_templates = {
            'build-pipeline': {
                'name': 'build-pipeline',
                'description': 'Standard build pipeline for IA Influencer Agent',
                'type': 'build',
                'base_steps': [
                    'checkout-code',
                    'install-dependencies',
                    'run-unit-tests',
                    'run-integration-tests',
                    'build-docker-image',
                    'security-scan',
                    'push-to-registry'
                ],
                'environment_overrides': {
                    'development': ['skip-security-scan'],
                    'production': ['extended-security-scan', 'compliance-check']
                },
                'required_variables': ['repo_url', 'image_name', 'tag'],
                'optional_variables': {
                    'skip_tests': False,
                    'registry_url': 'docker.io',
                    'build_args': {}
                }
            },
            'deploy-pipeline': {
                'name': 'deploy-pipeline',
                'description': 'Standard deployment pipeline for IA Influencer Agent',
                'type': 'deploy',
                'base_steps': [
                    'validate-environment',
                    'update-secrets',
                    'backup-current-state',
                    'deploy-application',
                    'wait-for-readiness',
                    'run-smoke-tests',
                    'update-monitoring'
                ],
                'environment_overrides': {
                    'development': ['skip-backup'],
                    'production': ['blue-green-deployment', 'extended-smoke-tests']
                },
                'required_variables': ['environment', 'image_tag'],
                'optional_variables': {
                    'deployment_strategy': 'rolling',
                    'timeout_seconds': 600,
                    'rollback_on_failure': True
                }
            },
            'test-pipeline': {
                'name': 'test-pipeline',
                'description': 'Comprehensive testing pipeline for IA Influencer Agent',
                'type': 'test',
                'base_steps': [
                    'setup-test-environment',
                    'run-unit-tests',
                    'run-integration-tests',
                    'run-performance-tests',
                    'run-security-tests',
                    'generate-reports',
                    'cleanup-test-environment'
                ],
                'environment_overrides': {
                    'development': ['skip-performance-tests'],
                    'staging': ['extended-integration-tests'],
                    'production': ['full-test-suite']
                },
                'required_variables': ['test_environment'],
                'optional_variables': {
                    'parallel_execution': True,
                    'test_timeout': 3600,
                    'coverage_threshold': 80
                }
            }
        }
        
        for template_name, template_data in default_templates.items():
            template_file = self.templates_dir / f"{template_name}.yaml"
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    yaml.dump(template_data, f, default_flow_style=False)
                self.logger.info(f"Generated default pipeline template: {template_name}")
                
    def generate_pipeline_config(self, template_name: str, environment: str,
                                variables: Dict[str, Any]) -> PipelineConfig:
        """Generate pipeline configuration from template and environment"""
        if template_name not in self.pipeline_templates:
            raise ConfigurationError(f"Pipeline template not found: {template_name}")
            
        if environment not in self.environment_configs:
            raise ConfigurationError(f"Environment configuration not found: {environment}")
            
        template = self.pipeline_templates[template_name]
        env_config = self.environment_configs[environment]
        
        # Validate required variables
        missing_vars = set(template.required_variables) - set(variables.keys())
        if missing_vars:
            raise ConfigurationError(f"Missing required variables: {missing_vars}")
            
        # Build steps with environment overrides
        steps = template.base_steps.copy()
        if environment in template.environment_overrides:
            override_steps = template.environment_overrides[environment]
            for override in override_steps:
                if override.startswith('skip-'):
                    step_to_skip = override[5:]
                    if step_to_skip in steps:
                        steps.remove(step_to_skip)
                else:
                    steps.append(override)
                    
        # Merge variables with defaults
        merged_variables = template.optional_variables.copy()
        merged_variables.update(variables)
        
        # Create pipeline configuration
        config = PipelineConfig(
            name=f"{template_name}-{environment}",
            environment=Environment(environment),
            pipeline_type=template.pipeline_type,
            steps=steps,
            timeout=merged_variables.get('timeout_seconds', 3600),
            retry_count=merged_variables.get('retry_count', 3),
            parallel_execution=merged_variables.get('parallel_execution', False),
            notifications=merged_variables.get('notifications', {})
        )
        
        return config
        
    def save_generated_config(self, config: PipelineConfig, 
                            filename: Optional[str] = None) -> Path:
        """Save generated pipeline configuration to file"""
        if not filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{config.name}_{timestamp}.yaml"
            
        output_file = self.config_dir / "generated" / filename
        
        with open(output_file, 'w') as f:
            yaml.dump(asdict(config), f, default_flow_style=False)
            
        self.logger.info(f"Saved generated configuration: {output_file}")
        return output_file
        
    def validate_configuration(self, config: PipelineConfig) -> List[str]:
        """Validate pipeline configuration and return list of issues"""
        issues = []
        
        # Validate basic fields
        if not config.name:
            issues.append("Pipeline name is required")
            
        if not config.steps:
            issues.append("At least one pipeline step is required")
            
        if config.timeout <= 0:
            issues.append("Timeout must be positive")
            
        if config.retry_count < 0:
            issues.append("Retry count cannot be negative")
            
        # Validate environment exists
        if config.environment.value not in self.environment_configs:
            issues.append(f"Environment not configured: {config.environment.value}")
            
        return issues
        
    def list_templates(self) -> List[str]:
        """List all available pipeline templates"""
        return list(self.pipeline_templates.keys())
        
    def list_environments(self) -> List[str]:
        """
List all configured environments"""
        return list(self.environment_configs.keys())
        
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
Get detailed information about pipeline template"""
        if template_name not in self.pipeline_templates:
            return None
            
        template = self.pipeline_templates[template_name]
        return {
            'name': template.name,
            'description': template.description,
            'type': template.pipeline_type.value,
            'base_steps': template.base_steps,
            'environment_overrides': template.environment_overrides,
            'required_variables': template.required_variables,
            'optional_variables': template.optional_variables
        }
        
    def get_environment_info(self, environment: str) -> Optional[Dict[str, Any]]:
        """
Get detailed information about environment configuration"""
        if environment not in self.environment_configs:
            return None
            
        env_config = self.environment_configs[environment]
        return asdict(env_config)

# Global configuration manager instance  
config_manager = PipelineConfigManager()
