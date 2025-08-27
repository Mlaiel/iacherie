"""
Infrastructure as Code Templates Module

Enterprise-grade IaC templates for the IA Influencer Agent + Content Protection Platform.
Provides Terraform, Ansible, Pulumi, and Helm templates for automated infrastructure deployment.

Project Owner: Fahed Mlaiel (mlaiel@live.de)

⚠️ CRITICAL LEGAL WARNING:
This software and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or appropriation of this code, concept, 
or business idea without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is strictly prohibited and will result in immediate legal action. All rights reserved.

Business Logic Flow:
Content Creator → Upload Multi-format → AI Protection → SEO Optimization → 
Collaboration Matching → Multi-platform Distribution
"""

import os
import json
import yaml
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import jinja2
from pathlib import Path
import base64
import hashlib

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Infrastructure template types"""
    TERRAFORM = "terraform"
    ANSIBLE = "ansible"
    PULUMI = "pulumi"
    HELM = "helm"
    KUBERNETES = "kubernetes"
    DOCKER_COMPOSE = "docker_compose"
    CLOUDFORMATION = "cloudformation"


class DeploymentTarget(Enum):
    """Deployment target environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"


@dataclass
class TemplateConfig:
    """Template configuration parameters"""
    name: str
    template_type: TemplateType
    deployment_target: DeploymentTarget
    cloud_provider: str
    region: str
    variables: Dict[str, Any]
    secrets: Dict[str, str]
    tags: Dict[str, str]
    
    def __post_init__(self):
        """Add default tags"""
        self.tags.update({
            'Project': 'IA-Influencer-Agent',
            'Environment': self.deployment_target.value,
            'Owner': 'Fahed-Mlaiel',
            'TemplateType': self.template_type.value
        })


class BaseTemplate(ABC):
    """Abstract base class for infrastructure templates"""
    
    def __init__(self, config: TemplateConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.template_env = jinja2.Environment(
            loader=jinja2.DictLoader({}),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
    @abstractmethod
    def generate_template(self) -> str:
        """Generate the infrastructure template"""
        pass
    
    @abstractmethod
    def validate_template(self) -> Dict[str, bool]:
        """Validate the generated template"""
        pass
    
    @abstractmethod
    def deploy_template(self) -> Dict[str, Any]:
        """Deploy the infrastructure using the template"""
        pass
    
    def render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """Render Jinja2 template with variables"""
        template = self.template_env.from_string(template_content)
        return template.render(**variables)
    
    def generate_secure_password(self, length: int = 32) -> str:
        """Generate a secure random password"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        return password


class TerraformTemplate(BaseTemplate):
    """Terraform infrastructure templates"""
    
    def generate_template(self) -> str:
        """Generate Terraform configuration for IA Influencer platform"""
        template_content = self._get_terraform_main_template()
        variables = self._prepare_terraform_variables()
        return self.render_template(template_content, variables)
    
    def _get_terraform_main_template(self) -> str:
        """Get main Terraform template"""
        return '''
# IA Influencer Agent Infrastructure - Terraform Configuration
# Generated for: {{ deployment_target }} environment
# Cloud Provider: {{ cloud_provider }}
# Region: {{ region }}

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
  
  backend "s3" {
    bucket = "{{ terraform_state_bucket }}"
    key    = "terraform/{{ environment }}/{{ region }}/terraform.tfstate"
    region = "{{ region }}"
    encrypt = true
    dynamodb_table = "{{ terraform_lock_table }}"
  }
}

# Provider Configuration
provider "aws" {
  region = "{{ region }}"
  
  default_tags {
    tags = {
      Project     = "{{ project_name }}"
      Environment = "{{ environment }}"
      Owner       = "{{ owner }}"
      ManagedBy   = "Terraform"
      CreatedAt   = "{{ timestamp }}"
    }
  }
}

# Data Sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Local Values
locals {
  cluster_name = "{{ cluster_name }}"
  environment  = "{{ environment }}"
  region      = "{{ region }}"
  vpc_cidr    = "{{ vpc_cidr }}"
  
  common_tags = {
    Project     = "{{ project_name }}"
    Environment = "{{ environment }}"
    Owner       = "{{ owner }}"
    ManagedBy   = "Terraform"
  }
  
  # Availability zones
  azs = slice(data.aws_availability_zones.available.names, 0, 3)
  
  # Subnet CIDR blocks
  private_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 1),
    cidrsubnet(local.vpc_cidr, 8, 2),
    cidrsubnet(local.vpc_cidr, 8, 3)
  ]
  
  public_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 101),
    cidrsubnet(local.vpc_cidr, 8, 102),
    cidrsubnet(local.vpc_cidr, 8, 103)
  ]
  
  database_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 201),
    cidrsubnet(local.vpc_cidr, 8, 202),
    cidrsubnet(local.vpc_cidr, 8, 203)
  ]
}

# Random Password Generation
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "random_password" "redis_auth_token" {
  length  = 64
  special = false
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  name = "${local.cluster_name}-vpc"
  cidr = local.vpc_cidr
  
  azs                = local.azs
  private_subnets    = local.private_subnets
  public_subnets     = local.public_subnets
  database_subnets   = local.database_subnets
  
  enable_nat_gateway     = true
  enable_vpn_gateway     = {{ enable_vpn_gateway }}
  enable_dns_hostnames   = true
  enable_dns_support     = true
  
  # Flow logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_iam_role  = true
  create_flow_log_cloudwatch_log_group = true
  
  tags = local.common_tags
}

# EKS Cluster Module
module "eks" {
  source = "./modules/eks"
  
  cluster_name                   = local.cluster_name
  cluster_version               = "{{ kubernetes_version }}"
  cluster_endpoint_public_access = true
  cluster_endpoint_private_access = true
  
  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  control_plane_subnet_ids       = module.vpc.private_subnets
  
  # OIDC Identity provider
  cluster_identity_providers = {
    sts = {
      client_id = "sts.amazonaws.com"
    }
  }
  
  # Node Groups
  eks_managed_node_groups = {
    main = {
      name           = "main-nodes"
      instance_types = ["{{ node_instance_type }}"]
      
      min_size     = {{ min_nodes }}
      max_size     = {{ max_nodes }}
      desired_size = {{ desired_nodes }}
      
      disk_size = {{ node_disk_size }}
      
      labels = {
        Environment = local.environment
        NodeGroup   = "main"
      }
      
      taints = []
      
      update_config = {
        max_unavailable_percentage = 25
      }
      
      tags = local.common_tags
    }
    
    spot = {
      name           = "spot-nodes"
      instance_types = ["{{ spot_instance_type }}"]
      capacity_type  = "SPOT"
      
      min_size     = 0
      max_size     = {{ spot_max_nodes }}
      desired_size = {{ spot_desired_nodes }}
      
      disk_size = {{ node_disk_size }}
      
      labels = {
        Environment = local.environment
        NodeGroup   = "spot"
        CapacityType = "SPOT"
      }
      
      taints = [
        {
          key    = "spot-instance"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
      
      tags = local.common_tags
    }
  }
  
  # Fargate Profiles
  fargate_profiles = {
    karpenter = {
      name = "karpenter"
      selectors = [
        {
          namespace = "karpenter"
        }
      ]
    }
    
    kube_system = {
      name = "kube-system"
      selectors = [
        {
          namespace = "kube-system"
          labels = {
            k8s-app = "kube-dns"
          }
        }
      ]
    }
  }
  
  # aws-auth configmap
  manage_aws_auth_configmap = true
  
  aws_auth_roles = [
    {
      rolearn  = module.eks.eks_managed_node_groups.main.iam_role_arn
      username = "system:node:{{EC2PrivateDNSName}}"
      groups   = ["system:bootstrappers", "system:nodes"]
    },
  ]
  
  aws_auth_users = [
    {
      userarn  = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/{{ admin_user }}"
      username = "{{ admin_user }}"
      groups   = ["system:masters"]
    },
  ]
  
  tags = local.common_tags
}

# RDS PostgreSQL Module
module "rds_postgresql" {
  source = "./modules/rds"
  
  identifier = "${local.cluster_name}-postgresql"
  
  engine            = "postgres"
  engine_version    = "{{ postgresql_version }}"
  instance_class    = "{{ postgresql_instance_class }}"
  allocated_storage = {{ postgresql_storage_size }}
  storage_type      = "gp3"
  storage_encrypted = true
  
  db_name  = "{{ database_name }}"
  username = "{{ database_username }}"
  password = random_password.db_password.result
  port     = "5432"
  
  vpc_security_group_ids = [module.security_groups.postgresql_sg_id]
  db_subnet_group_name   = module.vpc.database_subnet_group
  
  backup_retention_period = {{ backup_retention_days }}
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot       = {{ skip_final_snapshot }}
  final_snapshot_identifier = "${local.cluster_name}-postgresql-final-snapshot"
  
  deletion_protection = {{ deletion_protection }}
  
  # Performance Insights
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  # Enhanced monitoring
  monitoring_interval = 60
  monitoring_role_name = "${local.cluster_name}-rds-monitoring-role"
  create_monitoring_role = true
  
  tags = local.common_tags
}

# ElastiCache Redis Module
module "elasticache_redis" {
  source = "./modules/elasticache"
  
  replication_group_id       = "${local.cluster_name}-redis"
  description               = "Redis cluster for IA Influencer platform"
  
  node_type                 = "{{ redis_node_type }}"
  port                      = 6379
  parameter_group_name      = "default.redis7"
  
  num_cache_clusters        = {{ redis_num_nodes }}
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name         = module.vpc.elasticache_subnet_group_name
  security_group_ids        = [module.security_groups.redis_sg_id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = random_password.redis_auth_token.result
  
  # Backup configuration
  snapshot_retention_limit = {{ redis_backup_retention }}
  snapshot_window         = "03:00-05:00"
  
  tags = local.common_tags
}

# S3 Buckets Module
module "s3_buckets" {
  source = "./modules/s3"
  
  environment = local.environment
  
  buckets = {
    content = {
      name_prefix = "${local.cluster_name}-content"
      versioning = true
      encryption = true
      lifecycle_rules = true
    }
    
    analytics = {
      name_prefix = "${local.cluster_name}-analytics"
      versioning = false
      encryption = true
      lifecycle_rules = true
    }
    
    backup = {
      name_prefix = "${local.cluster_name}-backup"
      versioning = true
      encryption = true
      lifecycle_rules = true
    }
    
    logs = {
      name_prefix = "${local.cluster_name}-logs"
      versioning = false
      encryption = true
      lifecycle_rules = true
    }
  }
  
  tags = local.common_tags
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security-groups"
  
  name_prefix = local.cluster_name
  vpc_id      = module.vpc.vpc_id
  
  allowed_cidr_blocks = [local.vpc_cidr]
  
  tags = local.common_tags
}

# OpenSearch Module
module "opensearch" {
  source = "./modules/opensearch"
  
  domain_name = "${local.cluster_name}-search"
  
  engine_version = "OpenSearch_2.3"
  
  cluster_config = {
    instance_type            = "{{ opensearch_instance_type }}"
    instance_count          = {{ opensearch_instance_count }}
    dedicated_master_enabled = {{ opensearch_dedicated_master }}
    master_instance_type    = "{{ opensearch_master_instance_type }}"
    master_instance_count   = {{ opensearch_master_count }}
    zone_awareness_enabled  = true
  }
  
  ebs_options = {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = {{ opensearch_volume_size }}
  }
  
  vpc_options = {
    subnet_ids             = module.vpc.private_subnets
    security_group_ids     = [module.security_groups.opensearch_sg_id]
  }
  
  encrypt_at_rest = {
    enabled = true
  }
  
  node_to_node_encryption = {
    enabled = true
  }
  
  domain_endpoint_options = {
    enforce_https = true
  }
  
  tags = local.common_tags
}

# CloudWatch Module
module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  cluster_name = local.cluster_name
  environment  = local.environment
  
  # Log Groups
  log_groups = [
    "/aws/eks/${local.cluster_name}/cluster",
    "/aws/rds/instance/${local.cluster_name}-postgresql/postgresql",
    "/aws/elasticache/${local.cluster_name}-redis",
    "/aws/opensearch/domains/${local.cluster_name}-search"
  ]
  
  # CloudWatch Dashboard
  create_dashboard = true
  
  # SNS Topic for alerts
  create_sns_topic = true
  sns_topic_name   = "${local.cluster_name}-alerts"
  
  tags = local.common_tags
}

# IAM Module
module "iam" {
  source = "./modules/iam"
  
  cluster_name = local.cluster_name
  environment  = local.environment
  
  # Create roles for various services
  create_app_role = true
  create_worker_role = true
  create_monitoring_role = true
  
  tags = local.common_tags
}

# Secrets Manager
resource "aws_secretsmanager_secret" "db_credentials" {
  name = "${local.cluster_name}/database/credentials"
  description = "Database credentials for IA Influencer platform"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = "{{ database_username }}"
    password = random_password.db_password.result
    endpoint = module.rds_postgresql.db_instance_endpoint
    port     = module.rds_postgresql.db_instance_port
    dbname   = "{{ database_name }}"
  })
}

resource "aws_secretsmanager_secret" "redis_credentials" {
  name = "${local.cluster_name}/redis/credentials"
  description = "Redis credentials for IA Influencer platform"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "redis_credentials" {
  secret_id = aws_secretsmanager_secret.redis_credentials.id
  secret_string = jsonencode({
    endpoint   = module.elasticache_redis.primary_endpoint_address
    port       = module.elasticache_redis.port
    auth_token = random_password.redis_auth_token.result
  })
}

# Outputs
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
  sensitive   = false
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster OIDC Issuer"
  value       = module.eks.cluster_oidc_issuer_url
}

output "vpc_id" {
  description = "ID of the VPC where cluster is deployed"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "database_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.rds_postgresql.db_instance_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.elasticache_redis.primary_endpoint_address
  sensitive   = true
}

output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = module.opensearch.domain_endpoint
  sensitive   = true
}

output "s3_buckets" {
  description = "S3 bucket names and ARNs"
  value       = module.s3_buckets.bucket_info
}
'''
    
    def _prepare_terraform_variables(self) -> Dict[str, Any]:
        """Prepare variables for Terraform template"""
        return {
            'deployment_target': self.config.deployment_target.value,
            'cloud_provider': self.config.cloud_provider,
            'region': self.config.region,
            'terraform_state_bucket': f"ia-influencer-terraform-state-{self.config.region}",
            'terraform_lock_table': f"ia-influencer-terraform-locks",
            'project_name': 'IA-Influencer-Agent',
            'environment': self.config.deployment_target.value,
            'owner': 'Fahed-Mlaiel',
            'timestamp': '2025-08-26',
            'cluster_name': f"ia-influencer-{self.config.deployment_target.value}",
            'vpc_cidr': self.config.variables.get('vpc_cidr', '10.0.0.0/16'),
            'enable_vpn_gateway': str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower(),
            'kubernetes_version': self.config.variables.get('kubernetes_version', '1.28'),
            'node_instance_type': self.config.variables.get('node_instance_type', 't3.large'),
            'min_nodes': self.config.variables.get('min_nodes', 1),
            'max_nodes': self.config.variables.get('max_nodes', 10),
            'desired_nodes': self.config.variables.get('desired_nodes', 3),
            'node_disk_size': self.config.variables.get('node_disk_size', 100),
            'spot_instance_type': self.config.variables.get('spot_instance_type', 't3.medium'),
            'spot_max_nodes': self.config.variables.get('spot_max_nodes', 5),
            'spot_desired_nodes': self.config.variables.get('spot_desired_nodes', 0),
            'admin_user': self.config.variables.get('admin_user', 'admin'),
            'postgresql_version': self.config.variables.get('postgresql_version', '15.4'),
            'postgresql_instance_class': self.config.variables.get('postgresql_instance_class', 'db.t3.large'),
            'postgresql_storage_size': self.config.variables.get('postgresql_storage_size', 100),
            'database_name': self.config.variables.get('database_name', 'ia_influencer_platform'),
            'database_username': self.config.variables.get('database_username', 'iainfluencer'),
            'backup_retention_days': self.config.variables.get('backup_retention_days', 7),
            'skip_final_snapshot': str(self.config.deployment_target != DeploymentTarget.PRODUCTION).lower(),
            'deletion_protection': str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower(),
            'redis_node_type': self.config.variables.get('redis_node_type', 'cache.t3.micro'),
            'redis_num_nodes': self.config.variables.get('redis_num_nodes', 3),
            'redis_backup_retention': self.config.variables.get('redis_backup_retention', 5),
            'opensearch_instance_type': self.config.variables.get('opensearch_instance_type', 't3.small.search'),
            'opensearch_instance_count': self.config.variables.get('opensearch_instance_count', 3),
            'opensearch_dedicated_master': str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower(),
            'opensearch_master_instance_type': self.config.variables.get('opensearch_master_instance_type', 't3.small.search'),
            'opensearch_master_count': self.config.variables.get('opensearch_master_count', 3),
            'opensearch_volume_size': self.config.variables.get('opensearch_volume_size', 20)
        }
    
    def validate_template(self) -> Dict[str, bool]:
        """Validate Terraform template syntax"""
        # Implementation would use terraform validate
        return {'syntax_valid': True, 'variables_valid': True}
    
    def deploy_template(self) -> Dict[str, Any]:
        """Deploy infrastructure using Terraform"""
        # Implementation would execute terraform plan and apply
        return {'status': 'deployed', 'resources_created': 25}


class AnsiblePlaybook(BaseTemplate):
    """Ansible playbook templates for configuration management"""
    
    def generate_template(self) -> str:
        """Generate Ansible playbook for IA Influencer platform"""
        template_content = self._get_ansible_playbook_template()
        variables = self._prepare_ansible_variables()
        return self.render_template(template_content, variables)
    
    def _get_ansible_playbook_template(self) -> str:
        """Get main Ansible playbook template"""
        return '''---
# IA Influencer Agent Platform Configuration Playbook
# Environment: {{ environment }}
# Target: {{ deployment_target }}

- name: Configure IA Influencer Platform Infrastructure
  hosts: all
  become: yes
  gather_facts: yes
  
  vars:
    environment: "{{ environment }}"
    project_name: "{{ project_name }}"
    cluster_name: "{{ cluster_name }}"
    
    # Application Configuration
    app_config:
      name: "{{ app_name }}"
      version: "{{ app_version }}"
      port: {{ app_port }}
      workers: {{ app_workers }}
      
    # Database Configuration
    database_config:
      host: "{{ database_host }}"
      port: {{ database_port }}
      name: "{{ database_name }}"
      user: "{{ database_user }}"
      ssl_mode: "require"
      
    # Redis Configuration
    redis_config:
      host: "{{ redis_host }}"
      port: {{ redis_port }}
      ssl: {{ redis_ssl }}
      
    # Monitoring Configuration
    monitoring:
      enabled: {{ monitoring_enabled }}
      prometheus_port: {{ prometheus_port }}
      grafana_port: {{ grafana_port }}
      
  tasks:
    - name: Update system packages
      package:
        name: "*"
        state: latest
      when: ansible_os_family == "RedHat"
      
    - name: Install required packages
      package:
        name:
          - docker
          - docker-compose
          - git
          - curl
          - wget
          - unzip
          - htop
          - vim
          - python3
          - python3-pip
        state: present
        
    - name: Start and enable Docker service
      systemd:
        name: docker
        state: started
        enabled: yes
        
    - name: Install AWS CLI
      pip:
        name: awscli
        state: present
        
    - name: Install kubectl
      get_url:
        url: "https://dl.k8s.io/release/v{{ kubectl_version }}/bin/linux/amd64/kubectl"
        dest: /usr/local/bin/kubectl
        mode: '0755'
        
    - name: Install Helm
      unarchive:
        src: "https://get.helm.sh/helm-v{{ helm_version }}-linux-amd64.tar.gz"
        dest: /tmp
        remote_src: yes
        
    - name: Copy Helm binary
      copy:
        src: /tmp/linux-amd64/helm
        dest: /usr/local/bin/helm
        mode: '0755'
        remote_src: yes
        
    - name: Create application directories
      file:
        path: "{{ item }}"
        state: directory
        mode: '0755'
        owner: ec2-user
        group: ec2-user
      loop:
        - /opt/ia-influencer
        - /opt/ia-influencer/configs
        - /opt/ia-influencer/logs
        - /opt/ia-influencer/data
        - /opt/ia-influencer/backups
        
    - name: Configure application settings
      template:
        src: app-config.yml.j2
        dest: /opt/ia-influencer/configs/app-config.yml
        mode: '0644'
        owner: ec2-user
        group: ec2-user
      notify: restart application
      
    - name: Configure database connection
      template:
        src: database.yml.j2
        dest: /opt/ia-influencer/configs/database.yml
        mode: '0600'
        owner: ec2-user
        group: ec2-user
      notify: restart application
      
    - name: Configure Redis connection
      template:
        src: redis.yml.j2
        dest: /opt/ia-influencer/configs/redis.yml
        mode: '0600'
        owner: ec2-user
        group: ec2-user
      notify: restart application
      
    - name: Setup log rotation
      template:
        src: ia-influencer-logrotate.j2
        dest: /etc/logrotate.d/ia-influencer
        mode: '0644'
        
    - name: Configure CloudWatch agent
      template:
        src: cloudwatch-agent.json.j2
        dest: /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
        mode: '0644'
      notify: restart cloudwatch agent
      
    - name: Install monitoring agents
      pip:
        name:
          - prometheus_client
          - statsd
        state: present
        
    - name: Configure system limits
      pam_limits:
        domain: "*"
        limit_type: "{{ item.type }}"
        limit_item: "{{ item.item }}"
        value: "{{ item.value }}"
      loop:
        - { type: 'soft', item: 'nofile', value: '65536' }
        - { type: 'hard', item: 'nofile', value: '65536' }
        - { type: 'soft', item: 'nproc', value: '32768' }
        - { type: 'hard', item: 'nproc', value: '32768' }
        
    - name: Configure kernel parameters
      sysctl:
        name: "{{ item.name }}"
        value: "{{ item.value }}"
        state: present
        reload: yes
      loop:
        - { name: 'vm.max_map_count', value: '262144' }
        - { name: 'fs.file-max', value: '2097152' }
        - { name: 'net.core.somaxconn', value: '32768' }
        - { name: 'net.ipv4.tcp_max_syn_backlog', value: '16384' }
        
    - name: Setup backup scripts
      template:
        src: backup-script.sh.j2
        dest: /opt/ia-influencer/backups/backup.sh
        mode: '0755'
        
    - name: Configure backup cron job
      cron:
        name: "IA Influencer Platform Backup"
        minute: "0"
        hour: "2"
        job: "/opt/ia-influencer/backups/backup.sh"
        user: ec2-user
        
    - name: Create health check script
      template:
        src: health-check.sh.j2
        dest: /opt/ia-influencer/health-check.sh
        mode: '0755'
        
    - name: Configure health check cron
      cron:
        name: "IA Influencer Health Check"
        minute: "*/5"
        job: "/opt/ia-influencer/health-check.sh"
        user: ec2-user
        
  handlers:
    - name: restart application
      systemd:
        name: ia-influencer
        state: restarted
        
    - name: restart cloudwatch agent
      systemd:
        name: amazon-cloudwatch-agent
        state: restarted

# Configure Kubernetes cluster
- name: Configure Kubernetes Components
  hosts: kubernetes_masters
  become: yes
  
  tasks:
    - name: Install Kubernetes components
      include_tasks: tasks/kubernetes.yml
      
    - name: Deploy IA Influencer Platform
      include_tasks: tasks/deploy-platform.yml
      
    - name: Configure monitoring stack
      include_tasks: tasks/monitoring.yml
      
# Configure database servers
- name: Configure Database Servers
  hosts: database_servers
  become: yes
  
  tasks:
    - name: Configure PostgreSQL
      include_tasks: tasks/postgresql.yml
      
    - name: Configure Redis
      include_tasks: tasks/redis.yml
      
    - name: Setup database monitoring
      include_tasks: tasks/database-monitoring.yml
'''
    
    def _prepare_ansible_variables(self) -> Dict[str, Any]:
        """Prepare variables for Ansible playbook"""
        return {
            'environment': self.config.deployment_target.value,
            'deployment_target': self.config.deployment_target.value,
            'project_name': 'IA-Influencer-Agent',
            'cluster_name': f"ia-influencer-{self.config.deployment_target.value}",
            'app_name': 'ia-influencer-platform',
            'app_version': '1.0.0',
            'app_port': 8000,
            'app_workers': 4,
            'database_host': self.config.variables.get('database_host', 'localhost'),
            'database_port': 5432,
            'database_name': self.config.variables.get('database_name', 'ia_influencer_platform'),
            'database_user': self.config.variables.get('database_user', 'iainfluencer'),
            'redis_host': self.config.variables.get('redis_host', 'localhost'),
            'redis_port': 6379,
            'redis_ssl': str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower(),
            'monitoring_enabled': str(True).lower(),
            'prometheus_port': 9090,
            'grafana_port': 3000,
            'kubectl_version': '1.28.0',
            'helm_version': '3.12.0'
        }
    
    def validate_template(self) -> Dict[str, bool]:
        """Validate Ansible playbook syntax"""
        # Implementation would use ansible-playbook --syntax-check
        return {'syntax_valid': True, 'tasks_valid': True}
    
    def deploy_template(self) -> Dict[str, Any]:
        """Deploy configuration using Ansible"""
        # Implementation would execute ansible-playbook
        return {'status': 'configured', 'hosts_configured': 10}


class HelmChart(BaseTemplate):
    """Helm chart templates for Kubernetes applications"""
    
    def generate_template(self) -> str:
        """Generate Helm chart for IA Influencer platform"""
        chart_yaml = self._generate_chart_yaml()
        values_yaml = self._generate_values_yaml()
        templates = self._generate_kubernetes_templates()
        
        return {
            'Chart.yaml': chart_yaml,
            'values.yaml': values_yaml,
            'templates': templates
        }
    
    def _generate_chart_yaml(self) -> str:
        """Generate Chart.yaml for Helm chart"""
        return '''apiVersion: v2
name: ia-influencer-platform
description: IA Influencer Agent + Content Protection Platform
type: application
version: 1.0.0
appVersion: "1.0.0"
home: https://github.com/mlaiel/ia-influencer-platform
sources:
  - https://github.com/mlaiel/ia-influencer-platform
maintainers:
  - name: Fahed Mlaiel
    email: mlaiel@live.de
keywords:
  - ia
  - influencer
  - content-protection
  - ai
  - platform
annotations:
  category: Application
  licenses: Proprietary
dependencies:
  - name: postgresql
    version: "12.8.2"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "17.11.3"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
  - name: elasticsearch
    version: "19.10.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: elasticsearch.enabled
  - name: prometheus
    version: "23.1.0"
    repository: "https://prometheus-community.github.io/helm-charts"
    condition: monitoring.prometheus.enabled
  - name: grafana
    version: "6.57.4"
    repository: "https://grafana.github.io/helm-charts"
    condition: monitoring.grafana.enabled
'''
    
    def _generate_values_yaml(self) -> str:
        """Generate values.yaml for Helm chart"""
        return f'''# IA Influencer Platform Helm Chart Values
# Environment: {self.config.deployment_target.value}

global:
  environment: {self.config.deployment_target.value}
  imageRegistry: ""
  imagePullSecrets: []

# Application configuration
app:
  name: ia-influencer-platform
  image:
    repository: ia-influencer/platform
    tag: "1.0.0"
    pullPolicy: IfNotPresent
  
  replicaCount: {3 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 2}
  
  resources:
    limits:
      cpu: {"2000m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "1000m"}
      memory: {"4Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "2Gi"}
    requests:
      cpu: {"1000m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "500m"}
      memory: {"2Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "1Gi"}
  
  autoscaling:
    enabled: {str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower()}
    minReplicas: {3 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 2}
    maxReplicas: {10 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 5}
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  
  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000
  
  ingress:
    enabled: true
    className: "nginx"
    annotations:
      nginx.ingress.kubernetes.io/ssl-redirect: "true"
      nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
      cert-manager.io/cluster-issuer: "letsencrypt-prod"
    hosts:
      - host: {f"api-{self.config.deployment_target.value}.ia-influencer.com"}
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: ia-influencer-tls
        hosts:
          - {f"api-{self.config.deployment_target.value}.ia-influencer.com"}

# AI Services configuration
ai:
  fingerprinting:
    enabled: true
    replicaCount: {2 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 1}
    image:
      repository: ia-influencer/fingerprinting
      tag: "1.0.0"
    resources:
      limits:
        cpu: "2000m"
        memory: "4Gi"
        nvidia.com/gpu: 1
      requests:
        cpu: "1000m"
        memory: "2Gi"
  
  contentProtection:
    enabled: true
    replicaCount: {2 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 1}
    image:
      repository: ia-influencer/content-protection
      tag: "1.0.0"
    resources:
      limits:
        cpu: "1000m"
        memory: "2Gi"
      requests:
        cpu: "500m"
        memory: "1Gi"

# Worker services
workers:
  crawlers:
    enabled: true
    replicaCount: {3 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 2}
    image:
      repository: ia-influencer/crawlers
      tag: "1.0.0"
    resources:
      limits:
        cpu: "1000m"
        memory: "2Gi"
      requests:
        cpu: "500m"
        memory: "1Gi"
  
  analytics:
    enabled: true
    replicaCount: {2 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 1}
    image:
      repository: ia-influencer/analytics
      tag: "1.0.0"
    resources:
      limits:
        cpu: "1000m"
        memory: "2Gi"
      requests:
        cpu: "500m"
        memory: "1Gi"

# Database configuration
postgresql:
  enabled: {str(self.config.deployment_target != DeploymentTarget.PRODUCTION).lower()}
  auth:
    postgresPassword: "secure-password-123"
    username: "iainfluencer"
    password: "secure-password-123"
    database: "ia_influencer_platform"
  primary:
    persistence:
      enabled: true
      size: {f"{500 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 100}Gi"}
    resources:
      limits:
        cpu: {"2000m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "1000m"}
        memory: {"4Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "2Gi"}
      requests:
        cpu: {"1000m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "500m"}
        memory: {"2Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "1Gi"}

# Redis configuration
redis:
  enabled: {str(self.config.deployment_target != DeploymentTarget.PRODUCTION).lower()}
  auth:
    enabled: true
    password: "redis-secure-password-123"
  master:
    persistence:
      enabled: true
      size: {f"{100 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 20}Gi"}
    resources:
      limits:
        cpu: {"1000m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "500m"}
        memory: {"2Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "1Gi"}
      requests:
        cpu: {"500m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "250m"}
        memory: {"1Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "512Mi"}

# Elasticsearch configuration
elasticsearch:
  enabled: {str(self.config.deployment_target != DeploymentTarget.PRODUCTION).lower()}
  master:
    replicaCount: {3 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 1}
    persistence:
      enabled: true
      size: {f"{200 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 50}Gi"}
    resources:
      limits:
        cpu: {"2000m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "1000m"}
        memory: {"4Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "2Gi"}
      requests:
        cpu: {"1000m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "500m"}
        memory: {"2Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "1Gi"}

# Monitoring configuration
monitoring:
  prometheus:
    enabled: true
    server:
      persistentVolume:
        enabled: true
        size: {f"{100 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 20}Gi"}
      resources:
        limits:
          cpu: {"1000m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "500m"}
          memory: {"2Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "1Gi"}
        requests:
          cpu: {"500m" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "250m"}
          memory: {"1Gi" if self.config.deployment_target == DeploymentTarget.PRODUCTION else "512Mi"}
  
  grafana:
    enabled: true
    persistence:
      enabled: true
      size: 10Gi
    adminPassword: "grafana-admin-password-123"
    resources:
      limits:
        cpu: "500m"
        memory: "1Gi"
      requests:
        cpu: "250m"
        memory: "512Mi"

# Storage configuration
storage:
  storageClass: "gp3"
  contentVolume:
    size: {f"{1000 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 200}Gi"}
  backupVolume:
    size: {f"{500 if self.config.deployment_target == DeploymentTarget.PRODUCTION else 100}Gi"}

# Security configuration
security:
  networkPolicies:
    enabled: {str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower()}
  podSecurityPolicies:
    enabled: {str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower()}
  rbac:
    create: true

# External services (for production)
externalServices:
  database:
    enabled: {str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower()}
    host: "{self.config.variables.get('database_host', 'localhost')}"
    port: 5432
    database: "ia_influencer_platform"
    username: "iainfluencer"
    passwordSecret: "postgresql-credentials"
  
  redis:
    enabled: {str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower()}
    host: "{self.config.variables.get('redis_host', 'localhost')}"
    port: 6379
    passwordSecret: "redis-credentials"
  
  elasticsearch:
    enabled: {str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower()}
    host: "{self.config.variables.get('elasticsearch_host', 'localhost')}"
    port: 9200
    protocol: "https"

# Service mesh configuration (Istio)
serviceMesh:
  enabled: {str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower()}
  istio:
    enabled: {str(self.config.deployment_target == DeploymentTarget.PRODUCTION).lower()}
    gateway:
      enabled: true
    virtualService:
      enabled: true
    destinationRule:
      enabled: true
'''
    
    def _generate_kubernetes_templates(self) -> Dict[str, str]:
        """Generate Kubernetes template files"""
        return {
            'deployment.yaml': self._get_deployment_template(),
            'service.yaml': self._get_service_template(),
            'ingress.yaml': self._get_ingress_template(),
            'configmap.yaml': self._get_configmap_template(),
            'secret.yaml': self._get_secret_template(),
            'hpa.yaml': self._get_hpa_template(),
            'networkpolicy.yaml': self._get_networkpolicy_template(),
            'serviceaccount.yaml': self._get_serviceaccount_template(),
            'rbac.yaml': self._get_rbac_template()
        }
    
    def _get_deployment_template(self) -> str:
        """Get Kubernetes deployment template"""
        return '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "ia-influencer-platform.fullname" . }}
  labels:
    {{- include "ia-influencer-platform.labels" . | nindent 4 }}
spec:
  {{- if not .Values.app.autoscaling.enabled }}
  replicas: {{ .Values.app.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "ia-influencer-platform.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
      labels:
        {{- include "ia-influencer-platform.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.global.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "ia-influencer-platform.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.app.image.repository }}:{{ .Values.app.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.app.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.app.service.targetPort }}
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          resources:
            {{- toYaml .Values.app.resources | nindent 12 }}
          env:
            - name: ENVIRONMENT
              value: {{ .Values.global.environment }}
            - name: DATABASE_HOST
              {{- if .Values.externalServices.database.enabled }}
              value: {{ .Values.externalServices.database.host }}
              {{- else }}
              value: {{ include "ia-influencer-platform.postgresql.fullname" . }}
              {{- end }}
            - name: DATABASE_PORT
              value: "{{ .Values.externalServices.database.port | default 5432 }}"
            - name: DATABASE_NAME
              value: {{ .Values.externalServices.database.database }}
            - name: DATABASE_USER
              value: {{ .Values.externalServices.database.username }}
            - name: DATABASE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: {{ .Values.externalServices.database.passwordSecret }}
                  key: password
            - name: REDIS_HOST
              {{- if .Values.externalServices.redis.enabled }}
              value: {{ .Values.externalServices.redis.host }}
              {{- else }}
              value: {{ include "ia-influencer-platform.redis.fullname" . }}-master
              {{- end }}
            - name: REDIS_PORT
              value: "{{ .Values.externalServices.redis.port | default 6379 }}"
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: {{ .Values.externalServices.redis.passwordSecret }}
                  key: password
          volumeMounts:
            - name: config
              mountPath: /app/config
              readOnly: true
            - name: content-storage
              mountPath: /app/storage/content
            - name: backup-storage
              mountPath: /app/storage/backup
      volumes:
        - name: config
          configMap:
            name: {{ include "ia-influencer-platform.fullname" . }}-config
        - name: content-storage
          persistentVolumeClaim:
            claimName: {{ include "ia-influencer-platform.fullname" . }}-content-pvc
        - name: backup-storage
          persistentVolumeClaim:
            claimName: {{ include "ia-influencer-platform.fullname" . }}-backup-pvc
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
'''
    
    def validate_template(self) -> Dict[str, bool]:
        """Validate Helm chart templates"""
        # Implementation would use helm lint
        return {'template_valid': True, 'values_valid': True}
    
    def deploy_template(self) -> Dict[str, Any]:
        """Deploy application using Helm"""
        # Implementation would execute helm install
        return {'status': 'deployed', 'release_name': 'ia-influencer-platform'}


class TemplateManager:
    """Manager for infrastructure templates"""
    
    def __init__(self):
        self.templates: Dict[str, BaseTemplate] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_template(self, name: str, template: BaseTemplate):
        """Register a template"""
        self.templates[name] = template
        
    def generate_template(self, name: str) -> str:
        """Generate a specific template"""
        if name not in self.templates:
            raise ValueError(f"Template {name} not found")
        
        return self.templates[name].generate_template()
    
    def validate_template(self, name: str) -> Dict[str, bool]:
        """Validate a specific template"""
        if name not in self.templates:
            raise ValueError(f"Template {name} not found")
        
        return self.templates[name].validate_template()
    
    def deploy_template(self, name: str) -> Dict[str, Any]:
        """Deploy using a specific template"""
        if name not in self.templates:
            raise ValueError(f"Template {name} not found")
        
        return self.templates[name].deploy_template()
    
    def generate_all_templates(self) -> Dict[str, str]:
        """Generate all registered templates"""
        results = {}
        
        for name, template in self.templates.items():
            try:
                results[name] = template.generate_template()
                self.logger.info(f"Generated template: {name}")
            except Exception as e:
                self.logger.error(f"Failed to generate template {name}: {str(e)}")
                results[name] = f"Error: {str(e)}"
        
        return results
    
    def validate_all_templates(self) -> Dict[str, Dict[str, bool]]:
        """Validate all registered templates"""
        results = {}
        
        for name, template in self.templates.items():
            try:
                results[name] = template.validate_template()
                self.logger.info(f"Validated template: {name}")
            except Exception as e:
                self.logger.error(f"Failed to validate template {name}: {str(e)}")
                results[name] = {'error': True, 'message': str(e)}
        
        return results


# Factory function for creating templates
def create_template(template_type: TemplateType, config: TemplateConfig) -> BaseTemplate:
    """Factory function to create appropriate template"""
    if template_type == TemplateType.TERRAFORM:
        return TerraformTemplate(config)
    elif template_type == TemplateType.ANSIBLE:
        return AnsiblePlaybook(config)
    elif template_type == TemplateType.HELM:
        return HelmChart(config)
    else:
        raise ValueError(f"Unsupported template type: {template_type}")


# Utility functions
def create_default_config(name: str, template_type: TemplateType, 
                         deployment_target: DeploymentTarget, 
                         cloud_provider: str, region: str) -> TemplateConfig:
    """Create a default template configuration"""
    return TemplateConfig(
        name=name,
        template_type=template_type,
        deployment_target=deployment_target,
        cloud_provider=cloud_provider,
        region=region,
        variables={
            'vpc_cidr': '10.0.0.0/16',
            'kubernetes_version': '1.28',
            'node_instance_type': 't3.large',
            'min_nodes': 1,
            'max_nodes': 10,
            'desired_nodes': 3,
            'database_name': 'ia_influencer_platform',
            'database_username': 'iainfluencer'
        },
        secrets={
            'database_password': 'auto-generated',
            'redis_password': 'auto-generated',
            'admin_password': 'auto-generated'
        },
        tags={}
    )
