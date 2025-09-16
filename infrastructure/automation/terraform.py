"""
Terraform IaC Manager - Enterprise Infrastructure as Code for Ainflue
===================================================================

Advanced Terraform automation for multi-cloud provisioning, infrastructure
lifecycle management, and creator platform infrastructure orchestration.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import logging
import subprocess
import json
import os
import shutil
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import tempfile
import hashlib
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class TerraformAction(Enum):
    """Terraform actions for infrastructure management."""
    INIT = "init"
    PLAN = "plan"
    APPLY = "apply"
    DESTROY = "destroy"
    VALIDATE = "validate"
    FORMAT = "fmt"
    IMPORT = "import"
    REFRESH = "refresh"
    OUTPUT = "output"
    STATE_LIST = "state list"
    STATE_SHOW = "state show"


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITALOCEAN = "digitalocean"
    KUBERNETES = "kubernetes"


class InfrastructureType(Enum):
    """Infrastructure component types."""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORKING = "networking"
    DATABASE = "database"
    MONITORING = "monitoring"
    SECURITY = "security"
    AI_PROCESSING = "ai_processing"
    CONTENT_DELIVERY = "content_delivery"
    CREATOR_PLATFORM = "creator_platform"


@dataclass
class TerraformConfig:
    """Terraform configuration for infrastructure components."""
    module_name: str
    cloud_provider: CloudProvider
    infrastructure_type: InfrastructureType
    environment: str = "production"
    region: str = "us-east-1"
    variables: Dict[str, Any] = field(default_factory=dict)
    backend_config: Dict[str, Any] = field(default_factory=dict)
    terraform_version: str = "1.6.0"
    required_providers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set default providers based on cloud provider."""
        if not self.required_providers:
            provider_versions = {
                CloudProvider.AWS: {"aws": "~> 5.0"},
                CloudProvider.AZURE: {"azurerm": "~> 3.0"},
                CloudProvider.GCP: {"google": "~> 4.0"},
                CloudProvider.DIGITALOCEAN: {"digitalocean": "~> 2.0"},
                CloudProvider.KUBERNETES: {"kubernetes": "~> 2.0"}
            }
            self.required_providers = provider_versions.get(self.cloud_provider, {})


@dataclass
class TerraformResult:
    """Result of Terraform operation."""
    action: TerraformAction
    success: bool
    output: str
    error: Optional[str] = None
    resources_changed: int = 0
    resources_created: int = 0
    resources_destroyed: int = 0
    execution_time: float = 0.0
    state_changes: List[Dict[str, Any]] = field(default_factory=list)


class TerraformManager:
    """
    Enterprise Terraform Infrastructure as Code Manager.
    
    Manages multi-cloud infrastructure provisioning, lifecycle management,
    and creator platform specific infrastructure automation.
    """
    
    def __init__(self, workspace_dir: str = "/tmp/terraform"):
        """
        Initialize Terraform manager.
        
        Args:
            workspace_dir: Directory for Terraform workspaces
        """
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.terraform_binary = self._find_terraform_binary()
        
        # Creator Platform specific configurations
        self.creator_platform_modules = {
            "ai_processing_cluster": {
                "description": "GPU clusters for 53 AI agents processing",
                "resources": ["compute", "gpu", "auto_scaling"]
            },
            "content_storage": {
                "description": "High-performance storage for creator content",
                "resources": ["storage", "backup", "cdn"]
            },
            "platform_api_gateway": {
                "description": "API gateways for 65+ platform integrations",
                "resources": ["networking", "load_balancer", "ssl"]
            },
            "global_distribution": {
                "description": "Multi-region infrastructure for global reach",
                "resources": ["cdn", "dns", "load_balancer"]
            },
            "monitoring_stack": {
                "description": "Comprehensive monitoring for creator platform",
                "resources": ["prometheus", "grafana", "alerting"]
            }
        }
    
    def _find_terraform_binary(self) -> str:
        """Find Terraform binary in system PATH."""
        terraform_path = shutil.which("terraform")
        if not terraform_path:
            self.logger.warning("Terraform binary not found in PATH")
            # Return default path for installation
            return "/usr/local/bin/terraform"
        return terraform_path
    
    async def install_terraform(self, version: str = "1.6.0") -> bool:
        """
        Install Terraform binary if not present.
        
        Args:
            version: Terraform version to install
            
        Returns:
            bool: True if installation successful
        """
        try:
            # Check if already installed
            result = await self._run_command([self.terraform_binary, "version"])
            if result.returncode == 0:
                self.logger.info(f"Terraform already installed: {result.stdout}")
                return True
            
            # Download and install Terraform
            install_script = f"""
            curl -fsSL https://releases.hashicorp.com/terraform/{version}/terraform_{version}_linux_amd64.zip -o terraform.zip
            unzip terraform.zip
            sudo mv terraform /usr/local/bin/
            rm terraform.zip
            """
            
            result = await self._run_command(["bash", "-c", install_script])
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to install Terraform: {e}")
            return False
    
    async def create_workspace(self, config: TerraformConfig) -> Path:
        """
        Create Terraform workspace for infrastructure module.
        
        Args:
            config: Terraform configuration
            
        Returns:
            Path: Workspace directory path
        """
        workspace_path = self.workspace_dir / config.module_name
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Generate main.tf
        main_tf = self._generate_main_tf(config)
        (workspace_path / "main.tf").write_text(main_tf)
        
        # Generate variables.tf
        variables_tf = self._generate_variables_tf(config)
        (workspace_path / "variables.tf").write_text(variables_tf)
        
        # Generate outputs.tf
        outputs_tf = self._generate_outputs_tf(config)
        (workspace_path / "outputs.tf").write_text(outputs_tf)
        
        # Generate terraform.tfvars
        if config.variables:
            tfvars = self._generate_tfvars(config.variables)
            (workspace_path / "terraform.tfvars").write_text(tfvars)
        
        self.logger.info(f"Created Terraform workspace: {workspace_path}")
        return workspace_path
    
    def _generate_main_tf(self, config: TerraformConfig) -> str:
        """Generate main.tf configuration."""
        providers_block = ""
        for provider, version in config.required_providers.items():
            providers_block += f"""
      {provider} = {{
        source  = "hashicorp/{provider}"
        version = "{version}"
      }}"""
        
        backend_block = ""
        if config.backend_config:
            backend_type = config.backend_config.get("type", "s3")
            backend_block = f"""
  backend "{backend_type}" {{"""
            for key, value in config.backend_config.items():
                if key != "type":
                    backend_block += f'\n    {key} = "{value}"'
            backend_block += "\n  }"
        
        return f"""terraform {{
  required_version = ">= {config.terraform_version}"
  required_providers {{{providers_block}
  }}{backend_block}
}}

# Provider configuration
provider "{config.cloud_provider.value}" {{
  region = var.region
}}

# Creator Platform specific tags
locals {{
  common_tags = {{
    Environment    = var.environment
    Project       = "Ainflue"
    Component     = "{config.infrastructure_type.value}"
    ManagedBy     = "Terraform"
    Owner         = "Fahed Mlaiel"
    CreatorPlatform = "true"
    AIAgentsSupport = "53"
    PlatformCount   = "65+"
  }}
}}

# Infrastructure module for {config.module_name}
module "{config.module_name}" {{
  source = "./{config.infrastructure_type.value}"
  
  environment = var.environment
  region     = var.region
  tags       = local.common_tags
  
  # Creator platform specific configurations
  ai_agents_count = var.ai_agents_count
  platform_integrations = var.platform_integrations
  creator_capacity = var.creator_capacity
}}
"""
    
    def _generate_variables_tf(self, config: TerraformConfig) -> str:
        """Generate variables.tf configuration."""
        variables = f"""variable "environment" {{
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "{config.environment}"
}}

variable "region" {{
  description = "Cloud provider region"
  type        = string
  default     = "{config.region}"
}}

# Creator Platform Variables
variable "ai_agents_count" {{
  description = "Number of AI agents to support"
  type        = number
  default     = 53
}}

variable "platform_integrations" {{
  description = "Number of platform integrations"
  type        = number
  default     = 65
}}

variable "creator_capacity" {{
  description = "Expected number of concurrent creators"
  type        = number
  default     = 10000
}}

variable "content_storage_size" {{
  description = "Content storage size in GB"
  type        = number
  default     = 10000
}}

variable "high_availability" {{
  description = "Enable high availability setup"
  type        = bool
  default     = true
}}
"""
        
        # Add custom variables from config
        for var_name, var_config in config.variables.items():
            if isinstance(var_config, dict):
                var_type = var_config.get("type", "string")
                description = var_config.get("description", f"Custom variable {var_name}")
                default_value = var_config.get("default", '""')
            else:
                var_type = "string"
                description = f"Custom variable {var_name}"
                default_value = f'"{var_config}"'
            
            variables += f"""
variable "{var_name}" {{
  description = "{description}"
  type        = {var_type}
  default     = {default_value}
}}
"""
        
        return variables
    
    def _generate_outputs_tf(self, config: TerraformConfig) -> str:
        """Generate outputs.tf configuration."""
        return f"""# Infrastructure outputs for {config.module_name}

output "infrastructure_id" {{
  description = "Infrastructure identifier"
  value       = module.{config.module_name}.infrastructure_id
}}

output "endpoint_urls" {{
  description = "Infrastructure endpoint URLs"
  value       = module.{config.module_name}.endpoint_urls
}}

output "resource_arns" {{
  description = "AWS Resource ARNs (if applicable)"
  value       = module.{config.module_name}.resource_arns
  sensitive   = true
}}

output "connection_strings" {{
  description = "Database and service connection strings"
  value       = module.{config.module_name}.connection_strings
  sensitive   = true
}}

output "monitoring_endpoints" {{
  description = "Monitoring and observability endpoints"
  value       = module.{config.module_name}.monitoring_endpoints
}}

# Creator Platform specific outputs
output "ai_processing_endpoints" {{
  description = "AI agents processing endpoints"
  value       = module.{config.module_name}.ai_processing_endpoints
}}

output "content_storage_endpoints" {{
  description = "Content storage access endpoints"
  value       = module.{config.module_name}.content_storage_endpoints
}}

output "platform_integration_configs" {{
  description = "Configuration for platform integrations"
  value       = module.{config.module_name}.platform_integration_configs
  sensitive   = true
}}
"""
    
    def _generate_tfvars(self, variables: Dict[str, Any]) -> str:
        """Generate terraform.tfvars file."""
        tfvars = "# Terraform variables for Ainflue Infrastructure\n\n"
        
        for key, value in variables.items():
            if isinstance(value, str):
                tfvars += f'{key} = "{value}"\n'
            elif isinstance(value, bool):
                tfvars += f'{key} = {str(value).lower()}\n'
            elif isinstance(value, (int, float)):
                tfvars += f'{key} = {value}\n'
            elif isinstance(value, list):
                tfvars += f'{key} = {json.dumps(value)}\n'
            elif isinstance(value, dict):
                tfvars += f'{key} = {json.dumps(value)}\n'
        
        return tfvars
    
    async def execute_terraform_action(
        self, 
        workspace_path: Path, 
        action: TerraformAction,
        options: List[str] = None
    ) -> TerraformResult:
        """
        Execute Terraform action in specified workspace.
        
        Args:
            workspace_path: Path to Terraform workspace
            action: Terraform action to execute
            options: Additional Terraform options
            
        Returns:
            TerraformResult: Execution result
        """
        start_time = time.time()
        options = options or []
        
        # Prepare command
        cmd = [self.terraform_binary, action.value] + options
        
        try:
            # Change to workspace directory
            original_cwd = os.getcwd()
            os.chdir(workspace_path)
            
            # Execute command
            result = await self._run_command(cmd)
            execution_time = time.time() - start_time
            
            # Parse output for resource changes
            resources_created, resources_changed, resources_destroyed = self._parse_terraform_output(result.stdout)
            
            terraform_result = TerraformResult(
                action=action,
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                resources_created=resources_created,
                resources_changed=resources_changed,
                resources_destroyed=resources_destroyed,
                execution_time=execution_time
            )
            
            if terraform_result.success:
                self.logger.info(f"Terraform {action.value} completed successfully in {execution_time:.2f}s")
            else:
                self.logger.error(f"Terraform {action.value} failed: {terraform_result.error}")
            
            return terraform_result
            
        except Exception as e:
            self.logger.error(f"Terraform execution failed: {e}")
            return TerraformResult(
                action=action,
                success=False,
                output="",
                error=str(e),
                execution_time=time.time() - start_time
            )
        finally:
            os.chdir(original_cwd)
    
    def _parse_terraform_output(self, output: str) -> tuple:
        """Parse Terraform output for resource changes."""
        resources_created = 0
        resources_changed = 0
        resources_destroyed = 0
        
        lines = output.split('\n')
        for line in lines:
            if " to add," in line:
                try:
                    resources_created = int(line.split(" to add,")[0].strip().split()[-1])
                except:
                    pass
            elif " to change," in line:
                try:
                    resources_changed = int(line.split(" to change,")[0].strip().split()[-1])
                except:
                    pass
            elif " to destroy," in line:
                try:
                    resources_destroyed = int(line.split(" to destroy,")[0].strip().split()[-1])
                except:
                    pass
        
        return resources_created, resources_changed, resources_destroyed
    
    async def _run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run command asynchronously."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout.decode('utf-8'),
            stderr=stderr.decode('utf-8')
        )
    
    async def provision_creator_platform_infrastructure(
        self, 
        environment: str = "production",
        cloud_provider: CloudProvider = CloudProvider.AWS
    ) -> Dict[str, TerraformResult]:
        """
        Provision complete creator platform infrastructure.
        
        Args:
            environment: Target environment
            cloud_provider: Cloud provider to use
            
        Returns:
            Dict[str, TerraformResult]: Results for each infrastructure component
        """
        results = {}
        
        # Infrastructure components for creator platform
        infrastructure_configs = [
            TerraformConfig(
                module_name="ai_processing_cluster",
                cloud_provider=cloud_provider,
                infrastructure_type=InfrastructureType.AI_PROCESSING,
                environment=environment,
                variables={
                    "ai_agents_count": 53,
                    "gpu_instance_type": "p3.2xlarge",
                    "auto_scaling_enabled": True
                }
            ),
            TerraformConfig(
                module_name="content_storage",
                cloud_provider=cloud_provider,
                infrastructure_type=InfrastructureType.STORAGE,
                environment=environment,
                variables={
                    "storage_size_gb": 100000,
                    "backup_enabled": True,
                    "cdn_enabled": True
                }
            ),
            TerraformConfig(
                module_name="platform_api_gateway",
                cloud_provider=cloud_provider,
                infrastructure_type=InfrastructureType.NETWORKING,
                environment=environment,
                variables={
                    "platform_count": 65,
                    "rate_limiting_enabled": True,
                    "ssl_enabled": True
                }
            ),
            TerraformConfig(
                module_name="monitoring_stack",
                cloud_provider=cloud_provider,
                infrastructure_type=InfrastructureType.MONITORING,
                environment=environment,
                variables={
                    "prometheus_enabled": True,
                    "grafana_enabled": True,
                    "alerting_enabled": True
                }
            )
        ]
        
        for config in infrastructure_configs:
            try:
                # Create workspace
                workspace_path = await self.create_workspace(config)
                
                # Initialize Terraform
                init_result = await self.execute_terraform_action(
                    workspace_path, 
                    TerraformAction.INIT
                )
                
                if not init_result.success:
                    results[config.module_name] = init_result
                    continue
                
                # Plan infrastructure
                plan_result = await self.execute_terraform_action(
                    workspace_path,
                    TerraformAction.PLAN,
                    ["-out=tfplan"]
                )
                
                if not plan_result.success:
                    results[config.module_name] = plan_result
                    continue
                
                # Apply infrastructure
                apply_result = await self.execute_terraform_action(
                    workspace_path,
                    TerraformAction.APPLY,
                    ["tfplan"]
                )
                
                results[config.module_name] = apply_result
                
                self.logger.info(f"Provisioned {config.module_name} infrastructure")
                
            except Exception as e:
                self.logger.error(f"Failed to provision {config.module_name}: {e}")
                results[config.module_name] = TerraformResult(
                    action=TerraformAction.APPLY,
                    success=False,
                    output="",
                    error=str(e)
                )
        
        return results
    
    async def get_infrastructure_outputs(self, workspace_path: Path) -> Dict[str, Any]:
        """
        Get Terraform outputs for infrastructure.
        
        Args:
            workspace_path: Path to Terraform workspace
            
        Returns:
            Dict[str, Any]: Infrastructure outputs
        """
        try:
            result = await self.execute_terraform_action(
                workspace_path,
                TerraformAction.OUTPUT,
                ["-json"]
            )
            
            if result.success:
                return json.loads(result.output)
            else:
                self.logger.error(f"Failed to get outputs: {result.error}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Failed to parse outputs: {e}")
            return {}
    
    async def destroy_infrastructure(self, workspace_path: Path) -> TerraformResult:
        """
        Destroy infrastructure in workspace.
        
        Args:
            workspace_path: Path to Terraform workspace
            
        Returns:
            TerraformResult: Destruction result
        """
        return await self.execute_terraform_action(
            workspace_path,
            TerraformAction.DESTROY,
            ["-auto-approve"]
        )


# Creator Platform Infrastructure Templates
CREATOR_PLATFORM_MODULES = {
    "ai_processing": {
        "aws": {
            "compute": "EC2 instances with GPU support",
            "auto_scaling": "Auto Scaling Groups for AI agents",
            "load_balancer": "Application Load Balancer"
        },
        "azure": {
            "compute": "Virtual Machine Scale Sets with GPU",
            "auto_scaling": "Azure Auto Scale",
            "load_balancer": "Azure Load Balancer"
        },
        "gcp": {
            "compute": "Compute Engine with GPU",
            "auto_scaling": "Managed Instance Groups",
            "load_balancer": "Cloud Load Balancing"
        }
    },
    "content_storage": {
        "aws": {
            "storage": "S3 buckets with versioning",
            "cdn": "CloudFront distribution",
            "backup": "S3 Cross-Region Replication"
        },
        "azure": {
            "storage": "Blob Storage with versioning",
            "cdn": "Azure CDN",
            "backup": "Geo-redundant storage"
        },
        "gcp": {
            "storage": "Cloud Storage with versioning",
            "cdn": "Cloud CDN",
            "backup": "Multi-regional storage"
        }
    }
}


# Export public interface
__all__ = [
    "TerraformManager",
    "TerraformConfig",
    "TerraformResult",
    "TerraformAction",
    "CloudProvider",
    "InfrastructureType",
    "CREATOR_PLATFORM_MODULES"
]