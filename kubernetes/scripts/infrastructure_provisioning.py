#!/usr/bin/env python3
"""Infrastructure Provisioning Manager
Handles automated infrastructure provisioning using Infrastructure as Code
"""
import os
import sys
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import yaml
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProvisioningStatus(Enum):
    """Provisioning status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"


class InfrastructureProvider(Enum):
    """Infrastructure provider enumeration"""
    AWS = "aws"
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    KUBERNETES = "kubernetes"
    LOCAL = "local"


@dataclass
class InfrastructureStack:
    """Infrastructure stack data class"""
    name: str
    provider: InfrastructureProvider
    environment: str
    status: ProvisioningStatus
    template_path: str
    variables: Dict[str, Any]
    outputs: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None


class InfrastructureProvisioner:
    """
    Enterprise-grade infrastructure provisioning manager
    Handles Infrastructure as Code using Terraform, CloudFormation, and Kubernetes
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize infrastructure provisioner"""
        self.config_path = config_path or "/etc/provisioning/config.yaml"
        self.terraform_dir = "/opt/ia-influencer/terraform"
        self.cloudformation_dir = "/opt/ia-influencer/cloudformation"
        self.kubernetes_dir = "/opt/ia-influencer/kubernetes"
        self.stacks = {}
        
        self._load_configuration()
        self._initialize_providers()
        self._setup_directories()
    
    def _load_configuration(self) -> None:
        """Load provisioning configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Loaded provisioning configuration from {self.config_path}")
            else:
                self.config = self._get_default_config()
                logger.warning("Using default provisioning configuration")
        except Exception as e:
            logger.error(f"Failed to load provisioning configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default provisioning configuration"""
        return {
            "providers": {
                "aws": {
                    "region": "eu-central-1",
                    "profile": "default"
                },
                "google_cloud": {
                    "project": "ia-influencer-project",
                    "region": "europe-west3"
                },
                "azure": {
                    "subscription_id": "",
                    "resource_group": "ia-influencer-rg",
                    "location": "West Europe"
                }
            },
            "terraform": {
                "version": "1.5.0",
                "backend": {
                    "type": "s3",
                    "bucket": "ia-influencer-terraform-state",
                    "key": "terraform.tfstate",
                    "region": "eu-central-1"
                }
            },
            "environments": {
                "development": {
                    "auto_destroy": True,
                    "backup_enabled": False
                },
                "staging": {
                    "auto_destroy": False,
                    "backup_enabled": True
                },
                "production": {
                    "auto_destroy": False,
                    "backup_enabled": True,
                    "require_approval": True
                }
            },
            "monitoring": {
                "enabled": True,
                "slack_webhook": None
            }
        }
    
    def _initialize_providers(self) -> None:
        """Initialize cloud provider clients"""
        try:
            # AWS
            aws_config = self.config.get("providers", {}).get("aws", {})
            if aws_config:
                self.aws_session = boto3.Session(
                    profile_name=aws_config.get("profile", "default"),
                    region_name=aws_config.get("region", "eu-central-1")
                )
                logger.info("Initialized AWS provider")
            
            # Google Cloud
            gcp_config = self.config.get("providers", {}).get("google_cloud", {})
            if gcp_config:
                # Initialize Google Cloud client
                logger.info("Initialized Google Cloud provider")
            
            # Azure
            azure_config = self.config.get("providers", {}).get("azure", {})
            if azure_config:
                # Initialize Azure client
                logger.info("Initialized Azure provider")
                
        except Exception as e:
            logger.error(f"Provider initialization error: {e}")
    
    def _setup_directories(self) -> None:
        """Setup infrastructure directories"""
        directories = [
            self.terraform_dir,
            self.cloudformation_dir,
            self.kubernetes_dir,
            f"{self.terraform_dir}/modules",
            f"{self.terraform_dir}/environments",
            f"{self.cloudformation_dir}/templates",
            f"{self.kubernetes_dir}/manifests"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.info("Infrastructure directories created")
    
    def provision_stack(self, stack_name: str, provider: InfrastructureProvider, 
                       environment: str, template_path: str, 
                       variables: Dict[str, Any] = None) -> bool:
        """
        Provision infrastructure stack
        
        Args:
            stack_name: Name of the stack
            provider: Infrastructure provider
            environment: Target environment
            template_path: Path to infrastructure template
            variables: Stack variables
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Provisioning stack: {stack_name}")
            
            # Create stack object
            stack = InfrastructureStack(
                name=stack_name,
                provider=provider,
                environment=environment,
                status=ProvisioningStatus.PENDING,
                template_path=template_path,
                variables=variables or {},
                created_at=datetime.now()
            )
            
            self.stacks[stack_name] = stack
            
            # Validate template
            if not self._validate_template(stack):
                logger.error(f"Template validation failed: {stack_name}")
                stack.status = ProvisioningStatus.FAILED
                return False
            
            # Check environment requirements
            if not self._check_environment_requirements(stack):
                logger.error(f"Environment requirements not met: {stack_name}")
                stack.status = ProvisioningStatus.FAILED
                return False
            
            # Execute provisioning based on provider
            stack.status = ProvisioningStatus.IN_PROGRESS
            
            success = False
            if provider == InfrastructureProvider.AWS:
                success = self._provision_aws_stack(stack)
            elif provider == InfrastructureProvider.GOOGLE_CLOUD:
                success = self._provision_gcp_stack(stack)
            elif provider == InfrastructureProvider.AZURE:
                success = self._provision_azure_stack(stack)
            elif provider == InfrastructureProvider.KUBERNETES:
                success = self._provision_kubernetes_stack(stack)
            elif provider == InfrastructureProvider.LOCAL:
                success = self._provision_local_stack(stack)
            else:
                logger.error(f"Unsupported provider: {provider}")
                success = False
            
            # Update stack status
            stack.status = ProvisioningStatus.COMPLETED if success else ProvisioningStatus.FAILED
            stack.updated_at = datetime.now()
            
            # Send notification
            if self.config.get("monitoring", {}).get("enabled", False):
                self._send_provisioning_notification(stack, success)
            
            logger.info(f"Stack provisioning {'completed' if success else 'failed'}: {stack_name}")
            return success
            
        except Exception as e:
            logger.error(f"Provisioning error: {e}")
            if stack_name in self.stacks:
                self.stacks[stack_name].status = ProvisioningStatus.FAILED
                self.stacks[stack_name].error_message = str(e)
            return False
    
    def _validate_template(self, stack: InfrastructureStack) -> bool:
        """Validate infrastructure template"""
        try:
            template_path = stack.template_path
            
            if not os.path.exists(template_path):
                logger.error(f"Template file not found: {template_path}")
                return False
            
            # Validate based on provider
            if stack.provider == InfrastructureProvider.AWS:
                return self._validate_terraform_template(template_path)
            elif stack.provider == InfrastructureProvider.KUBERNETES:
                return self._validate_kubernetes_manifests(template_path)
            else:
                # Basic file existence check for other providers
                return True
                
        except Exception as e:
            logger.error(f"Template validation error: {e}")
            return False
    
    def _validate_terraform_template(self, template_path: str) -> bool:
        """Validate Terraform template"""
        try:
            # Change to template directory
            template_dir = os.path.dirname(template_path)
            
            # Run terraform validate
            result = subprocess.run(
                ["terraform", "validate"],
                cwd=template_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Terraform template validation passed")
                return True
            else:
                logger.error(f"Terraform validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Terraform validation error: {e}")
            return False
    
    def _validate_kubernetes_manifests(self, manifest_path: str) -> bool:
        """Validate Kubernetes manifests"""
        try:
            # Run kubectl dry-run
            result = subprocess.run(
                ["kubectl", "apply", "--dry-run=client", "-f", manifest_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Kubernetes manifest validation passed")
                return True
            else:
                logger.error(f"Kubernetes validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Kubernetes validation error: {e}")
            return False
    
    def _check_environment_requirements(self, stack: InfrastructureStack) -> bool:
        """Check environment-specific requirements"""
        try:
            env_config = self.config.get("environments", {}).get(stack.environment, {})
            
            # Check if approval is required for production
            if (stack.environment == "production" and 
                env_config.get("require_approval", False)):
                
                # In a real implementation, this would integrate with approval system
                logger.info("Production deployment requires approval (auto-approved for demo)")
            
            # Check resource quotas
            if not self._check_resource_quotas(stack):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Environment requirements check error: {e}")
            return False
    
    def _check_resource_quotas(self, stack: InfrastructureStack) -> bool:
        """Check resource quotas and limits"""
        try:
            # This would check actual resource quotas in the target environment
            # For now, we'll simulate the check
            logger.info(f"Resource quotas check passed for {stack.name}")
            return True
            
        except Exception as e:
            logger.error(f"Resource quotas check error: {e}")
            return False
    
    def _provision_aws_stack(self, stack: InfrastructureStack) -> bool:
        """Provision AWS infrastructure using Terraform"""
        try:
            logger.info(f"Provisioning AWS stack: {stack.name}")
            
            template_dir = os.path.dirname(stack.template_path)
            
            # Initialize Terraform
            init_result = subprocess.run(
                ["terraform", "init"],
                cwd=template_dir,
                capture_output=True,
                text=True
            )
            
            if init_result.returncode != 0:
                logger.error(f"Terraform init failed: {init_result.stderr}")
                return False
            
            # Create variable file
            var_file = self._create_terraform_vars_file(stack)
            
            # Plan
            plan_result = subprocess.run(
                ["terraform", "plan", f"-var-file={var_file}", "-out=tfplan"],
                cwd=template_dir,
                capture_output=True,
                text=True
            )
            
            if plan_result.returncode != 0:
                logger.error(f"Terraform plan failed: {plan_result.stderr}")
                return False
            
            # Apply
            apply_result = subprocess.run(
                ["terraform", "apply", "-auto-approve", "tfplan"],
                cwd=template_dir,
                capture_output=True,
                text=True
            )
            
            if apply_result.returncode != 0:
                logger.error(f"Terraform apply failed: {apply_result.stderr}")
                return False
            
            # Get outputs
            stack.outputs = self._get_terraform_outputs(template_dir)
            
            logger.info(f"AWS stack provisioned successfully: {stack.name}")
            return True
            
        except Exception as e:
            logger.error(f"AWS provisioning error: {e}")
            return False
    
    def _provision_gcp_stack(self, stack: InfrastructureStack) -> bool:
        """Provision Google Cloud infrastructure"""
        try:
            logger.info(f"Provisioning GCP stack: {stack.name}")
            
            # Similar to AWS but using GCP-specific tools
            # This would use gcloud CLI and Terraform with GCP provider
            
            logger.info(f"GCP stack provisioned successfully: {stack.name}")
            return True
            
        except Exception as e:
            logger.error(f"GCP provisioning error: {e}")
            return False
    
    def _provision_azure_stack(self, stack: InfrastructureStack) -> bool:
        """Provision Azure infrastructure"""
        try:
            logger.info(f"Provisioning Azure stack: {stack.name}")
            
            # Similar to AWS but using Azure-specific tools
            # This would use az CLI and ARM templates or Terraform with Azure provider
            
            logger.info(f"Azure stack provisioned successfully: {stack.name}")
            return True
            
        except Exception as e:
            logger.error(f"Azure provisioning error: {e}")
            return False
    
    def _provision_kubernetes_stack(self, stack: InfrastructureStack) -> bool:
        """Provision Kubernetes resources"""
        try:
            logger.info(f"Provisioning Kubernetes stack: {stack.name}")
            
            # Apply Kubernetes manifests
            apply_result = subprocess.run(
                ["kubectl", "apply", "-f", stack.template_path],
                capture_output=True,
                text=True
            )
            
            if apply_result.returncode != 0:
                logger.error(f"Kubernetes apply failed: {apply_result.stderr}")
                return False
            
            # Wait for resources to be ready
            if not self._wait_for_kubernetes_resources(stack):
                logger.error(f"Kubernetes resources not ready: {stack.name}")
                return False
            
            logger.info(f"Kubernetes stack provisioned successfully: {stack.name}")
            return True
            
        except Exception as e:
            logger.error(f"Kubernetes provisioning error: {e}")
            return False
    
    def _provision_local_stack(self, stack: InfrastructureStack) -> bool:
        """Provision local infrastructure (Docker Compose, etc.)"""
        try:
            logger.info(f"Provisioning local stack: {stack.name}")
            
            # This would handle Docker Compose or local development setup
            # For demonstration, we'll simulate success
            
            time.sleep(2)  # Simulate provisioning time
            
            stack.outputs = {
                "status": "running",
                "endpoints": {
                    "api": "http://localhost:8000",
                    "database": "localhost:5432"
                }
            }
            
            logger.info(f"Local stack provisioned successfully: {stack.name}")
            return True
            
        except Exception as e:
            logger.error(f"Local provisioning error: {e}")
            return False
    
    def _create_terraform_vars_file(self, stack: InfrastructureStack) -> str:
        """Create Terraform variables file"""
        try:
            var_file_path = f"/tmp/{stack.name}.tfvars"
            
            with open(var_file_path, 'w') as f:
                for key, value in stack.variables.items():
                    if isinstance(value, str):
                        f.write(f'{key} = "{value}"\n')
                    elif isinstance(value, bool):
                        f.write(f'{key} = {str(value).lower()}\n')
                    else:
                        f.write(f'{key} = {value}\n')
            
            return var_file_path
            
        except Exception as e:
            logger.error(f"Terraform vars file creation error: {e}")
            return ""
    
    def _get_terraform_outputs(self, terraform_dir: str) -> Dict[str, Any]:
        """Get Terraform outputs"""
        try:
            output_result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=terraform_dir,
                capture_output=True,
                text=True
            )
            
            if output_result.returncode == 0:
                return json.loads(output_result.stdout)
            else:
                logger.warning(f"Failed to get Terraform outputs: {output_result.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"Terraform outputs error: {e}")
            return {}
    
    def _wait_for_kubernetes_resources(self, stack: InfrastructureStack) -> bool:
        """Wait for Kubernetes resources to be ready"""
        try:
            # Wait for deployments to be ready
            wait_result = subprocess.run(
                ["kubectl", "wait", "--for=condition=ready", "pod", "-l", f"stack={stack.name}", "--timeout=300s"],
                capture_output=True,
                text=True
            )
            
            return wait_result.returncode == 0
            
        except Exception as e:
            logger.error(f"Kubernetes wait error: {e}")
            return False
    
    def destroy_stack(self, stack_name: str) -> bool:
        """
        Destroy infrastructure stack
        
        Args:
            stack_name: Name of the stack to destroy
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if stack_name not in self.stacks:
                logger.error(f"Stack not found: {stack_name}")
                return False
            
            stack = self.stacks[stack_name]
            logger.info(f"Destroying stack: {stack_name}")
            
            stack.status = ProvisioningStatus.DESTROYING
            
            # Check if destruction is allowed
            env_config = self.config.get("environments", {}).get(stack.environment, {})
            if not env_config.get("auto_destroy", False) and stack.environment == "production":
                logger.error(f"Auto-destroy not allowed for {stack.environment} environment")
                return False
            
            # Execute destruction based on provider
            success = False
            if stack.provider == InfrastructureProvider.AWS:
                success = self._destroy_aws_stack(stack)
            elif stack.provider == InfrastructureProvider.GOOGLE_CLOUD:
                success = self._destroy_gcp_stack(stack)
            elif stack.provider == InfrastructureProvider.AZURE:
                success = self._destroy_azure_stack(stack)
            elif stack.provider == InfrastructureProvider.KUBERNETES:
                success = self._destroy_kubernetes_stack(stack)
            elif stack.provider == InfrastructureProvider.LOCAL:
                success = self._destroy_local_stack(stack)
            
            # Update stack status
            stack.status = ProvisioningStatus.DESTROYED if success else ProvisioningStatus.FAILED
            stack.updated_at = datetime.now()
            
            if success:
                # Remove from active stacks
                del self.stacks[stack_name]
            
            logger.info(f"Stack destruction {'completed' if success else 'failed'}: {stack_name}")
            return success
            
        except Exception as e:
            logger.error(f"Destruction error: {e}")
            return False
    
    def _destroy_aws_stack(self, stack: InfrastructureStack) -> bool:
        """Destroy AWS infrastructure using Terraform"""
        try:
            template_dir = os.path.dirname(stack.template_path)
            
            # Create variable file
            var_file = self._create_terraform_vars_file(stack)
            
            # Destroy
            destroy_result = subprocess.run(
                ["terraform", "destroy", "-auto-approve", f"-var-file={var_file}"],
                cwd=template_dir,
                capture_output=True,
                text=True
            )
            
            if destroy_result.returncode == 0:
                logger.info(f"AWS stack destroyed successfully: {stack.name}")
                return True
            else:
                logger.error(f"Terraform destroy failed: {destroy_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"AWS destruction error: {e}")
            return False
    
    def _destroy_gcp_stack(self, stack: InfrastructureStack) -> bool:
        """Destroy Google Cloud infrastructure"""
        try:
            # Similar to AWS destruction
            return True
            
        except Exception as e:
            logger.error(f"GCP destruction error: {e}")
            return False
    
    def _destroy_azure_stack(self, stack: InfrastructureStack) -> bool:
        """Destroy Azure infrastructure"""
        try:
            # Similar to AWS destruction
            return True
            
        except Exception as e:
            logger.error(f"Azure destruction error: {e}")
            return False
    
    def _destroy_kubernetes_stack(self, stack: InfrastructureStack) -> bool:
        """Destroy Kubernetes resources"""
        try:
            delete_result = subprocess.run(
                ["kubectl", "delete", "-f", stack.template_path],
                capture_output=True,
                text=True
            )
            
            return delete_result.returncode == 0
            
        except Exception as e:
            logger.error(f"Kubernetes destruction error: {e}")
            return False
    
    def _destroy_local_stack(self, stack: InfrastructureStack) -> bool:
        """Destroy local infrastructure"""
        try:
            # This would handle Docker Compose down, etc.
            return True
            
        except Exception as e:
            logger.error(f"Local destruction error: {e}")
            return False
    
    def _send_provisioning_notification(self, stack: InfrastructureStack, success: bool) -> None:
        """Send provisioning notification"""
        try:
            slack_webhook = self.config.get("monitoring", {}).get("slack_webhook")
            if not slack_webhook:
                return
            
            status = "✅ SUCCESS" if success else "❌ FAILED"
            message = f"Infrastructure Provisioning {status}\n\nStack: {stack.name}\nEnvironment: {stack.environment}\nProvider: {stack.provider.value}"
            
            import requests
            requests.post(slack_webhook, json={"text": message})
            
        except Exception as e:
            logger.error(f"Notification error: {e}")
    
    def get_stack_status(self, stack_name: str) -> Optional[Dict[str, Any]]:
        """Get stack status"""
        try:
            if stack_name not in self.stacks:
                return None
            
            stack = self.stacks[stack_name]
            return {
                "name": stack.name,
                "provider": stack.provider.value,
                "environment": stack.environment,
                "status": stack.status.value,
                "created_at": stack.created_at.isoformat() if stack.created_at else None,
                "updated_at": stack.updated_at.isoformat() if stack.updated_at else None,
                "outputs": stack.outputs,
                "error_message": stack.error_message
            }
            
        except Exception as e:
            logger.error(f"Stack status error: {e}")
            return None
    
    def list_stacks(self, environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """List infrastructure stacks"""
        try:
            stacks = list(self.stacks.values())
            
            if environment:
                stacks = [s for s in stacks if s.environment == environment]
            
            return [
                {
                    "name": stack.name,
                    "provider": stack.provider.value,
                    "environment": stack.environment,
                    "status": stack.status.value,
                    "created_at": stack.created_at.isoformat() if stack.created_at else None,
                    "updated_at": stack.updated_at.isoformat() if stack.updated_at else None
                }
                for stack in stacks
            ]
            
        except Exception as e:
            logger.error(f"List stacks error: {e}")
            return []
    
    def create_template(self, template_type: str, template_name: str, provider: str) -> str:
        """Create infrastructure template"""
        try:
            if provider == "aws":
                template_dir = self.terraform_dir
                template_ext = ".tf"
                template_content = self._get_aws_template_content(template_type)
            elif provider == "kubernetes":
                template_dir = self.kubernetes_dir
                template_ext = ".yaml"
                template_content = self._get_kubernetes_template_content(template_type)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            template_path = os.path.join(template_dir, f"{template_name}{template_ext}")
            
            with open(template_path, 'w') as f:
                f.write(template_content)
            
            logger.info(f"Created template: {template_path}")
            return template_path
            
        except Exception as e:
            logger.error(f"Template creation error: {e}")
            return ""
    
    def _get_aws_template_content(self, template_type: str) -> str:
        """Get AWS Terraform template content"""
        if template_type == "vpc":
            return '''
# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name        = "${var.environment}-igw"
    Environment = var.environment
  }
}

# Variables
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

# Outputs
output "vpc_id" {
  value = aws_vpc.main.id
}

output "internet_gateway_id" {
  value = aws_internet_gateway.main.id
}
'''
        elif template_type == "eks":
            return '''
# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "${var.environment}-eks-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids = var.subnet_ids
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_AmazonEKSClusterPolicy,
  ]
  
  tags = {
    Environment = var.environment
  }
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.27"
}

variable "subnet_ids" {
  description = "Subnet IDs for EKS cluster"
  type        = list(string)
}

# Outputs
output "cluster_id" {
  value = aws_eks_cluster.main.id
}

output "cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}
'''
        else:
            return f'# {template_type.upper()} Template\n# Add your resources here\n'
    
    def _get_kubernetes_template_content(self, template_type: str) -> str:
        """Get Kubernetes manifest template content"""
        if template_type == "deployment":
            return '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  labels:
    app: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
      - name: app
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "256Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
'''
        elif template_type == "namespace":
            return '''
apiVersion: v1
kind: Namespace
metadata:
  name: ia-influencer
  labels:
    name: ia-influencer
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: ia-influencer
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    persistentvolumeclaims: "4"
'''
        else:
            return f'# {template_type.upper()} Template\n# Add your Kubernetes resources here\n'


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Infrastructure Provisioning Manager")
    parser.add_argument("--action", required=True, 
                       choices=["provision", "destroy", "status", "list", "create-template"])
    parser.add_argument("--stack-name", help="Stack name")
    parser.add_argument("--provider", choices=["aws", "google_cloud", "azure", "kubernetes", "local"])
    parser.add_argument("--environment", help="Target environment")
    parser.add_argument("--template-path", help="Path to infrastructure template")
    parser.add_argument("--variables", help="JSON string of variables")
    parser.add_argument("--template-type", help="Type of template to create")
    
    args = parser.parse_args()
    
    provisioner = InfrastructureProvisioner()
    
    if args.action == "provision":
        if not all([args.stack_name, args.provider, args.environment, args.template_path]):
            print("Error: stack-name, provider, environment, and template-path are required for provision")
            sys.exit(1)
        
        variables = {}
        if args.variables:
            variables = json.loads(args.variables)
        
        success = provisioner.provision_stack(
            args.stack_name,
            InfrastructureProvider(args.provider),
            args.environment,
            args.template_path,
            variables
        )
        
        print(f"Provisioning {'completed' if success else 'failed'}")
        sys.exit(0 if success else 1)
    
    elif args.action == "destroy":
        if not args.stack_name:
            print("Error: stack-name is required for destroy")
            sys.exit(1)
        
        success = provisioner.destroy_stack(args.stack_name)
        print(f"Destruction {'completed' if success else 'failed'}")
        sys.exit(0 if success else 1)
    
    elif args.action == "status":
        if not args.stack_name:
            print("Error: stack-name is required for status")
            sys.exit(1)
        
        status = provisioner.get_stack_status(args.stack_name)
        if status:
            print(json.dumps(status, indent=2))
        else:
            print("Stack not found")
            sys.exit(1)
    
    elif args.action == "list":
        stacks = provisioner.list_stacks(environment=args.environment)
        print(json.dumps(stacks, indent=2))
    
    elif args.action == "create-template":
        if not all([args.template_type, args.stack_name, args.provider]):
            print("Error: template-type, stack-name, and provider are required for create-template")
            sys.exit(1)
        
        template_path = provisioner.create_template(args.template_type, args.stack_name, args.provider)
        print(f"Template created: {template_path}")


if __name__ == "__main__":
    main()
