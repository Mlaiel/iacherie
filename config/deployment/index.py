"""
Deployment Configuration Index for IA-Influencer Agent Platform
===============================================================

Central index and factory for all deployment configuration modules
providing enterprise-grade infrastructure management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

 CRITICAL COPYRIGHT WARNING
 This entire codebase, concept, and business logic is the EXCLUSIVE intellectual property of Fahed Mlaiel (mlaiel@live.de).

 ZERO TOLERANCE POLICY: Any individual or organization attempting to:
- Copy, reproduce, or steal this code
- Reverse engineer the concepts or algorithms  
- Use this intellectual property without written authorization
- Claim ownership of these innovations

WILL FACE IMMEDIATE LEGAL ACTION under German and international intellectual property law.

 Contact: mlaiel@live.de for licensing and usage permissions ONLY.
"""

import os
import yaml
from typing import Dict, List, Optional, Any, Type, Union
from pathlib import Path
from enum import Enum
import logging

# Import all configuration classes
from .docker_config import DockerConfig
from .kubernetes_config import KubernetesConfig
from .aws_config import AWSConfig
from .azure_config import AzureConfig
from .gcp_config import GCPConfig
from .terraform_config import TerraformConfig
from .monitoring_config import MonitoringConfig
from .testing_config import TestingConfig
from .ci_cd_config import CICDConfig
from .ssl_config import SSLConfig
from .load_balancer_config import LoadBalancerConfig
from .cdn_config import CDNConfig
from .backup_config import BackupConfig
from .scaling_config import ScalingConfig
from .web_monitoring_config import WebMonitoringConfig
from .revenue_monetization_config import RevenueMonetizationConfig
from .collaboration_matching_config import CollaborationMatchingConfig
from .security_compliance_config import SecurityComplianceConfig


class DeploymentEnvironment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    TESTING = "testing"
    DR = "disaster_recovery"


class ConfigurationType(Enum):
    """Configuration types"""
    INFRASTRUCTURE = "infrastructure"
    CLOUD = "cloud"
    SECURITY = "security"
    MONITORING = "monitoring"
    NETWORKING = "networking"
    STORAGE = "storage"
    COMPUTE = "compute"
    APPLICATION = "application"
    BUSINESS = "business"


class DeploymentConfigurationIndex:
    """
    Central index and factory for all deployment configurations.
    
    Provides:
    - Centralized configuration management
    - Environment-specific configurations
    - Configuration validation and testing
    - Bulk configuration export/import
    - Configuration templating and inheritance
    - Cross-module dependency resolution
    - Configuration versioning and rollback
    - Automated deployment orchestration
    """
    
    def __init__(self, environment: DeploymentEnvironment = DeploymentEnvironment.DEVELOPMENT):
        self.environment = environment
        self.project_name = "ia-influencer-agent"
        self.config_registry = self._initialize_config_registry()
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("deployment_config_index")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_config_registry(self) -> Dict[str, Dict[str, Any]]:
        """Initialize configuration registry"""



        return {
            "docker": {
                "class": DockerConfig,
                "type": ConfigurationType.INFRASTRUCTURE,
                "dependencies": [],
                "description": "Docker containerization configuration"
            },
            "kubernetes": {
                "class": KubernetesConfig,
                "type": ConfigurationType.INFRASTRUCTURE,
                "dependencies": ["docker"],
                "description": "Kubernetes orchestration configuration"
            },
            "aws": {
                "class": AWSConfig,
                "type": ConfigurationType.CLOUD,
                "dependencies": [],
                "description": "Amazon Web Services configuration"
            },
            "azure": {
                "class": AzureConfig,
                "type": ConfigurationType.CLOUD,
                "dependencies": [],
                "description": "Microsoft Azure configuration"
            },
            "gcp": {
                "class": GCPConfig,
                "type": ConfigurationType.CLOUD,
                "dependencies": [],
                "description": "Google Cloud Platform configuration"
            },
            "terraform": {
                "class": TerraformConfig,
                "type": ConfigurationType.INFRASTRUCTURE,
                "dependencies": ["aws", "azure", "gcp"],
                "description": "Infrastructure as Code configuration"
            },
            "monitoring": {
                "class": MonitoringConfig,
                "type": ConfigurationType.MONITORING,
                "dependencies": ["kubernetes"],
                "description": "Monitoring and observability configuration"
            },
            "testing": {
                "class": TestingConfig,
                "type": ConfigurationType.APPLICATION,
                "dependencies": ["docker"],
                "description": "Testing and quality assurance configuration"
            },
            "ci_cd": {
                "class": CICDConfig,
                "type": ConfigurationType.APPLICATION,
                "dependencies": ["docker", "kubernetes", "testing"],
                "description": "Continuous integration and deployment configuration"
            },
            "ssl": {
                "class": SSLConfig,
                "type": ConfigurationType.SECURITY,
                "dependencies": [],
                "description": "SSL/TLS certificate management configuration"
            },
            "load_balancer": {
                "class": LoadBalancerConfig,
                "type": ConfigurationType.NETWORKING,
                "dependencies": ["ssl"],
                "description": "Load balancer and traffic distribution configuration"
            },
            "cdn": {
                "class": CDNConfig,
                "type": ConfigurationType.NETWORKING,
                "dependencies": ["ssl"],
                "description": "Content delivery network configuration"
            },
            "backup": {
                "class": BackupConfig,
                "type": ConfigurationType.STORAGE,
                "dependencies": [],
                "description": "Backup and disaster recovery configuration"
            },
            "scaling": {
                "class": ScalingConfig,
                "type": ConfigurationType.COMPUTE,
                "dependencies": ["kubernetes", "monitoring"],
                "description": "Auto-scaling and capacity management configuration"
            },
            "web_monitoring": {
                "class": WebMonitoringConfig,
                "type": ConfigurationType.BUSINESS,
                "dependencies": ["monitoring"],
                "description": "Web monitoring and content surveillance configuration"
            },
            "revenue_monetization": {
                "class": RevenueMonetizationConfig,
                "type": ConfigurationType.BUSINESS,
                "dependencies": ["security_compliance"],
                "description": "Revenue tracking and monetization configuration"
            },
            "collaboration_matching": {
                "class": CollaborationMatchingConfig,
                "type": ConfigurationType.BUSINESS,
                "dependencies": ["security_compliance"],
                "description": "Collaboration and influencer matching configuration"
            },
            "security_compliance": {
                "class": SecurityComplianceConfig,
                "type": ConfigurationType.SECURITY,
                "dependencies": [],
                "description": "Security and compliance configuration"
            }
        }
    
    def get_config_instance(self, config_name: str, environment: Optional[str] = None) -> Any:
        """Get configuration instance by name"""
        if config_name not in self.config_registry:
            raise ValueError(f"Unknown configuration: {config_name}")
        
        config_info = self.config_registry[config_name]
        config_class = config_info["class"]
        
        # Use provided environment or default
        env = environment or self.environment.value
        
        try:
            return config_class(environment=env)
        except TypeError:
            # Some classes might not accept environment parameter
            return config_class()
    
    def get_all_configs(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """Get all configuration instances"""
        configs = {}
        env = environment or self.environment.value
        
        for config_name in self.config_registry.keys():
            try:
                configs[config_name] = self.get_config_instance(config_name, env)
                self.logger.info(f"Loaded configuration: {config_name}")
            except Exception as e:
                self.logger.error(f"Failed to load configuration {config_name}: {e}")
        
        return configs
    
    def get_configs_by_type(self, config_type: ConfigurationType, environment: Optional[str] = None) -> Dict[str, Any]:
        """Get configurations by type"""
        configs = {}
        env = environment or self.environment.value
        
        for config_name, config_info in self.config_registry.items():
            if config_info["type"] == config_type:
                try:
                    configs[config_name] = self.get_config_instance(config_name, env)
                except Exception as e:
                    self.logger.error(f"Failed to load configuration {config_name}: {e}")
        
        return configs
    
    def validate_dependencies(self, config_name: str) -> List[str]:
        """Validate configuration dependencies"""
        if config_name not in self.config_registry:
            return [f"Configuration '{config_name}' not found"]
        
        errors = []
        config_info = self.config_registry[config_name]
        
        for dependency in config_info.get("dependencies", []):
            if dependency not in self.config_registry:
                errors.append(f"Dependency '{dependency}' not found for '{config_name}'")
        
        return errors
    
    def get_deployment_order(self) -> List[str]:
        """Get deployment order based on dependencies"""
        ordered_configs = []
        visited = set()
        temp_visited = set()
        
        def visit(config_name: str):
            if config_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {config_name}")
            if config_name in visited:
                return
            
            temp_visited.add(config_name)
            
            config_info = self.config_registry.get(config_name, {})
            for dependency in config_info.get("dependencies", []):
                visit(dependency)
            
            temp_visited.remove(config_name)
            visited.add(config_name)
            ordered_configs.append(config_name)
        
        for config_name in self.config_registry.keys():
            if config_name not in visited:
                visit(config_name)
        
        return ordered_configs
    
    def export_all_configurations(self, output_dir: str = "./complete-deployment-configs") -> Dict[str, Dict[str, str]]:
        """Export all configurations to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        all_exported_files = {}
        configs = self.get_all_configs()
        
        for config_name, config_instance in configs.items():
            if hasattr(config_instance, 'export_configurations'):
                try:
                    config_output_dir = output_path / config_name
                    exported_files = config_instance.export_configurations(str(config_output_dir))
                    all_exported_files[config_name] = exported_files
                    self.logger.info(f"Exported {config_name} configurations to {config_output_dir}")
                except Exception as e:
                    self.logger.error(f"Failed to export {config_name} configurations: {e}")
        
        # Create summary file
        summary = {
            "project": self.project_name,
            "environment": self.environment.value,
            "total_configurations": len(all_exported_files),
            "deployment_order": self.get_deployment_order(),
            "configuration_types": {
                config_type.value: [
                    name for name, info in self.config_registry.items() 
                    if info["type"] == config_type
                ]
                for config_type in ConfigurationType
            },
            "exported_files": all_exported_files
        }
        
        summary_path = output_path / "deployment_summary.yaml"
        with open(summary_path, 'w') as f:
            yaml.safe_dump(summary, f, default_flow_style=False)
        
        self.logger.info(f"Deployment configuration export completed. Summary: {summary_path}")
        return all_exported_files
    
    def generate_deployment_manifest(self) -> Dict[str, Any]:
        """Generate complete deployment manifest"""
        deployment_order = self.get_deployment_order()
        
        manifest = {
            "version": "1.0",
            "project": self.project_name,
            "environment": self.environment.value,
            "deployment_strategy": {
                "type": "blue_green" if self.environment == DeploymentEnvironment.PRODUCTION else "rolling",
                "rollback_enabled": True,
                "health_checks": True,
                "automated_tests": True
            },
            "phases": []
        }
        
        # Group configurations by phase
        infrastructure_configs = ["docker", "kubernetes", "terraform"]
        cloud_configs = ["aws", "azure", "gcp"]
        security_configs = ["ssl", "security_compliance"]
        networking_configs = ["load_balancer", "cdn"]
        storage_configs = ["backup"]
        compute_configs = ["scaling"]
        monitoring_configs = ["monitoring"]
        application_configs = ["ci_cd", "testing"]
        business_configs = ["web_monitoring", "revenue_monetization", "collaboration_matching"]
        
        phases = [
            {"name": "Infrastructure Setup", "configs": infrastructure_configs},
            {"name": "Cloud Services", "configs": cloud_configs},
            {"name": "Security Configuration", "configs": security_configs},
            {"name": "Networking Setup", "configs": networking_configs},
            {"name": "Storage Configuration", "configs": storage_configs},
            {"name": "Compute Configuration", "configs": compute_configs},
            {"name": "Monitoring Setup", "configs": monitoring_configs},
            {"name": "Application Deployment", "configs": application_configs},
            {"name": "Business Logic", "configs": business_configs}
        ]
        
        for phase in phases:
            phase_configs = [config for config in phase["configs"] if config in deployment_order]
            if phase_configs:
                manifest["phases"].append({
                    "phase": phase["name"],
                    "configurations": phase_configs,
                    "parallel_execution": len(phase_configs) > 1,
                    "failure_strategy": "rollback"
                })
        
        return manifest
    
    def get_environment_specific_overrides(self, environment: DeploymentEnvironment) -> Dict[str, Any]:
        """Get environment-specific configuration overrides"""
        overrides = {
            DeploymentEnvironment.DEVELOPMENT: {
                "docker": {"enable_debug": True, "resource_limits": "low"},
                "kubernetes": {"replica_count": 1, "resource_requests": "minimal"},
                "monitoring": {"retention_days": 7, "alert_sensitivity": "low"},
                "security_compliance": {"audit_level": "basic", "encryption_level": "standard"}
            },
            DeploymentEnvironment.STAGING: {
                "docker": {"enable_debug": False, "resource_limits": "medium"},
                "kubernetes": {"replica_count": 2, "resource_requests": "moderate"},
                "monitoring": {"retention_days": 30, "alert_sensitivity": "medium"},
                "security_compliance": {"audit_level": "enhanced", "encryption_level": "high"}
            },
            DeploymentEnvironment.PRODUCTION: {
                "docker": {"enable_debug": False, "resource_limits": "high"},
                "kubernetes": {"replica_count": 3, "resource_requests": "production"},
                "monitoring": {"retention_days": 365, "alert_sensitivity": "high"},
                "security_compliance": {"audit_level": "maximum", "encryption_level": "maximum"}
            }
        }
        
        return overrides.get(environment, {})


# Factory function
def create_deployment_configuration_index(environment: DeploymentEnvironment = DeploymentEnvironment.DEVELOPMENT) -> DeploymentConfigurationIndex:
    """Create deployment configuration index for specific environment"""



    return DeploymentConfigurationIndex(environment=environment)


# Default instance
deployment_config_index = create_deployment_configuration_index()

# Export all classes and functions
__all__ = [
    "DeploymentConfigurationIndex",
    "DeploymentEnvironment",
    "ConfigurationType",
    "create_deployment_configuration_index",
    "deployment_config_index",
    # Re-export all configuration classes
    "DockerConfig",
    "KubernetesConfig", 
    "AWSConfig",
    "AzureConfig",
    "GCPConfig",
    "TerraformConfig",
    "MonitoringConfig",
    "TestingConfig",
    "CICDConfig",
    "SSLConfig",
    "LoadBalancerConfig",
    "CDNConfig",
    "BackupConfig",
    "ScalingConfig",
    "WebMonitoringConfig",
    "RevenueMonetizationConfig",
    "CollaborationMatchingConfig",
    "SecurityComplianceConfig"
]
