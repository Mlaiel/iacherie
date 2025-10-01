"""Terraform Infrastructure Template for iacherie Platform
Enterprise-grade Infrastructure as Code template for scalable creator economy platform.

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE
© 2025 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés - Utilisation commerciale interdite sans autorisation écrite explicite

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2024-09-18
"""

import logging
import json
import os
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITAL_OCEAN = "digitalocean"


class EnvironmentType(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"


@dataclass
class TerraformConfig:
    """Terraform configuration structure"""
    project_name: str
    environment: EnvironmentType
    region: str
    availability_zones: List[str]
    vpc_cidr: str
    public_subnets: List[str]
    private_subnets: List[str]
    database_subnets: List[str]
    enable_nat_gateway: bool = True
    enable_vpn_gateway: bool = False
    enable_dns_hostnames: bool = True
    enable_dns_support: bool = True
    
    # Creator Economy specific
    enable_media_processing: bool = True
    enable_ai_services: bool = True
    enable_content_delivery: bool = True
    enable_analytics_services: bool = True


class TerraformInfrastructureTemplate:
    """Enterprise Terraform Infrastructure Template for iacherie Platform"""
    
    def __init__(self, config: TerraformConfig, provider: CloudProvider = CloudProvider.AWS):
        self.config = config
        self.provider = provider
        self.templates = {}
        
    def generate_provider_configuration(self) -> str:
        """Generate provider configuration"""
        if self.provider == CloudProvider.AWS:
            return self._generate_aws_provider()
        elif self.provider == CloudProvider.AZURE:
            return self._generate_azure_provider()
        elif self.provider == CloudProvider.GCP:
            return self._generate_gcp_provider()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _generate_aws_provider(self) -> str:
        """Generate AWS provider configuration"""
        return f'''# Terraform AWS Provider Configuration - iacherie Platform
terraform {{
  required_version = ">= 1.5"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
    random = {{
      source  = "hashicorp/random"
      version = "~> 3.1"
    }}
  }}
  
  backend "s3" {{
    bucket = "iacherie-terraform-state-{self.config.environment.value}"
    key    = "infrastructure/{self.config.project_name}/terraform.tfstate"
    region = "{self.config.region}"
    encrypt = true
    dynamodb_table = "iacherie-terraform-locks"
  }}
}}

provider "aws" {{
  region = "{self.config.region}"
  
  default_tags {{
    tags = {{
      Project = "{self.config.project_name}"
      Environment = "{self.config.environment.value}"
      ManagedBy = "terraform"
      Owner = "iacherie-platform"
      CostCenter = "creator-economy"
    }}
  }}
}}

# Random suffix for unique resource naming
resource "random_id" "suffix" {{
  byte_length = 4
}}

locals {{
  name_prefix = "{self.config.project_name}-{self.config.environment.value}"
  common_tags = {{
    Project = "{self.config.project_name}"
    Environment = "{self.config.environment.value}"
    ManagedBy = "terraform"
    Owner = "iacherie-platform"
    CostCenter = "creator-economy"
  }}
}}'''

    def generate_complete_template(self) -> str:
        """Generate complete Terraform template"""
        template_parts = [
            "# iacherie Platform - Enterprise Terraform Infrastructure Template",
            "# Creator Economy Platform - Production-Ready Infrastructure",
            "# Author: Fahed Mlaiel (mlaiel@live.de)",
            "# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.",
            "",
            self.generate_provider_configuration(),
        ]
        
        return "\n".join(template_parts)


# Example usage and configuration templates
def create_production_config() -> TerraformConfig:
    """Create production environment configuration"""
    return TerraformConfig(
        project_name="iacherie-platform",
        environment=EnvironmentType.PRODUCTION,
        region="us-west-2",
        availability_zones=["us-west-2a", "us-west-2b", "us-west-2c"],
        vpc_cidr="10.0.0.0/16",
        public_subnets=["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
        private_subnets=["10.0.10.0/24", "10.0.20.0/24", "10.0.30.0/24"],
        database_subnets=["10.0.100.0/24", "10.0.200.0/24", "10.0.210.0/24"],
        enable_nat_gateway=True,
        enable_media_processing=True,
        enable_ai_services=True,
        enable_content_delivery=True,
        enable_analytics_services=True
    )


def create_development_config() -> TerraformConfig:
    """Create development environment configuration"""
    return TerraformConfig(
        project_name="iacherie-dev",
        environment=EnvironmentType.DEVELOPMENT,
        region="us-west-2",
        availability_zones=["us-west-2a", "us-west-2b"],
        vpc_cidr="10.1.0.0/16",
        public_subnets=["10.1.1.0/24", "10.1.2.0/24"],
        private_subnets=["10.1.10.0/24", "10.1.20.0/24"],
        database_subnets=["10.1.100.0/24", "10.1.200.0/24"],
        enable_nat_gateway=False,  # Cost optimization for dev
        enable_media_processing=True,
        enable_ai_services=False,  # Disabled for dev to save costs
        enable_content_delivery=False,
        enable_analytics_services=False
    )


if __name__ == "__main__":
    # Generate production template
    prod_config = create_production_config()
    prod_template = TerraformInfrastructureTemplate(prod_config, CloudProvider.AWS)
    
    # This would typically be used in a deployment script
    print("Terraform Infrastructure Template for iacherie Platform")
    print("Configuration:")
    print(f"- Environment: {prod_config.environment.value}")
    print(f"- Region: {prod_config.region}")
    print(f"- VPC CIDR: {prod_config.vpc_cidr}")
    print(f"- Media Processing: {prod_config.enable_media_processing}")
    print(f"- AI Services: {prod_config.enable_ai_services}")
    print(f"- CDN: {prod_config.enable_content_delivery}")
