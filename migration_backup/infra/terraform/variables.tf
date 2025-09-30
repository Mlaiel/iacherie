# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# =============================================================================
# TERRAFORM VARIABLES - MULTI-CLOUD INFRASTRUCTURE
# =============================================================================

# -----------------------------------------------------------------------------
# Environment Configuration
# -----------------------------------------------------------------------------

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "ainflue"
}

variable "region" {
  description = "Primary deployment region"
  type        = string
  default     = "us-west-2"
}

# -----------------------------------------------------------------------------
# Multi-Cloud Provider Configuration
# -----------------------------------------------------------------------------

variable "cloud_providers" {
  description = "List of cloud providers to deploy to"
  type        = list(string)
  default     = ["aws"]
  
  validation {
    condition = alltrue([
      for provider in var.cloud_providers : contains(["aws", "azure", "gcp"], provider)
    ])
    error_message = "Cloud providers must be one of: aws, azure, gcp."
  }
}

variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-west-2"
}

variable "azure_location" {
  description = "Azure deployment location"
  type        = string
  default     = "West US 2"
}

variable "gcp_region" {
  description = "GCP deployment region" 
  type        = string
  default     = "us-west2"
}

# -----------------------------------------------------------------------------
# Network Configuration
# -----------------------------------------------------------------------------

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["a", "b", "c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# -----------------------------------------------------------------------------
# Kubernetes Configuration
# -----------------------------------------------------------------------------

variable "k8s_version" {
  description = "Kubernetes cluster version"
  type        = string
  default     = "1.28"
}

variable "node_groups" {
  description = "Kubernetes node group configurations"
  type = map(object({
    instance_types = list(string)
    min_size      = number
    max_size      = number
    desired_size  = number
  }))
  default = {
    general = {
      instance_types = ["t3.medium"]
      min_size      = 1
      max_size      = 10
      desired_size  = 3
    }
    ai_workload = {
      instance_types = ["g4dn.xlarge"]
      min_size      = 0
      max_size      = 5
      desired_size  = 1
    }
  }
}

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------

variable "rds_configuration" {
  description = "RDS database configuration"
  type = object({
    engine_version    = string
    instance_class   = string
    allocated_storage = number
    backup_retention = number
    multi_az        = bool
  })
  default = {
    engine_version    = "13.13"
    instance_class   = "db.t3.micro"
    allocated_storage = 20
    backup_retention = 7
    multi_az        = false
  }
}

variable "redis_configuration" {
  description = "Redis cache configuration"
  type = object({
    node_type           = string
    num_cache_nodes    = number
    parameter_group    = string
    engine_version     = string
  })
  default = {
    node_type           = "cache.t3.micro"
    num_cache_nodes    = 1
    parameter_group    = "default.redis7"
    engine_version     = "7.0"
  }
}

# -----------------------------------------------------------------------------
# Storage Configuration
# -----------------------------------------------------------------------------

variable "s3_configuration" {
  description = "S3 bucket configuration"
  type = object({
    versioning_enabled = bool
    encryption_enabled = bool
    lifecycle_enabled  = bool
    backup_enabled     = bool
  })
  default = {
    versioning_enabled = true
    encryption_enabled = true
    lifecycle_enabled  = true
    backup_enabled     = true
  }
}

# -----------------------------------------------------------------------------
# Security Configuration
# -----------------------------------------------------------------------------

variable "enable_waf" {
  description = "Enable AWS WAF protection"
  type        = bool
  default     = true
}

variable "enable_shield" {
  description = "Enable AWS Shield DDoS protection"
  type        = bool
  default     = true
}

variable "ssl_certificate_arn" {
  description = "SSL certificate ARN for HTTPS"
  type        = string
  default     = ""
}

# -----------------------------------------------------------------------------
# Monitoring Configuration
# -----------------------------------------------------------------------------

variable "monitoring_configuration" {
  description = "Monitoring and alerting configuration"
  type = object({
    enable_prometheus = bool
    enable_grafana   = bool
    enable_jaeger    = bool
    retention_days   = number
  })
  default = {
    enable_prometheus = true
    enable_grafana   = true
    enable_jaeger    = true
    retention_days   = 30
  }
}

# -----------------------------------------------------------------------------
# Scaling Configuration
# -----------------------------------------------------------------------------

variable "auto_scaling" {
  description = "Auto scaling configuration"
  type = object({
    enable_cluster_autoscaler = bool
    enable_horizontal_pod_autoscaler = bool
    enable_vertical_pod_autoscaler = bool
  })
  default = {
    enable_cluster_autoscaler = true
    enable_horizontal_pod_autoscaler = true
    enable_vertical_pod_autoscaler = false
  }
}

# -----------------------------------------------------------------------------
# Tags Configuration
# -----------------------------------------------------------------------------

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "Ainflue"
    Environment = "dev"
    Owner       = "Fahed Mlaiel"
    ManagedBy   = "Terraform"
  }
}