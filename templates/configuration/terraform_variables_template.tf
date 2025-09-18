# Terraform Variables - Ainflue Creator Economy Platform
# ======================================================
#
# 🎯 DEVOPS ENGINEER + CLOUD ARCHITECT + INFRASTRUCTURE EXPERT
# Lead: Fahed Mlaiel (mlaiel@live.de)
#
# Enterprise Infrastructure Variables Definition
# - Environment-specific configurations
# - Resource sizing and scaling parameters
# - Security and compliance settings
# - Creator Economy specific parameters
# - AI processing configurations
# - Monitoring and observability settings
#
# ⚠️ INTELLECTUAL PROPERTY PROTECTION:
# ==========================================
# © 2025 Fahed Mlaiel <mlaiel@live.de>
# TOUS DROITS RÉSERVÉS
#
# 🚨 PROTECTION INTELLECTUELLE:
# - Code propriétaire de Fahed Mlaiel
# - Utilisation commerciale INTERDITE sans autorisation écrite
# - Reverse engineering STRICTEMENT INTERDIT
# - Distribution INTERDITE sans licence explicite
# - Violation = Poursuites judiciaires automatiques
#
# Created: 2025-01-18
# Version: 1.0.0

# ==============================================================================
# GENERAL CONFIGURATION
# ==============================================================================

variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  
  validation {
    condition = contains([
      "development",
      "staging", 
      "production",
      "testing"
    ], var.environment)
    error_message = "Environment must be one of: development, staging, production, testing."
  }
}

variable "aws_region" {
  description = "AWS region for infrastructure deployment"
  type        = string
  default     = "us-east-1"
  
  validation {
    condition = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.aws_region))
    error_message = "AWS region must be in the format: us-east-1, eu-west-1, etc."
  }
}

variable "aws_assume_role_arn" {
  description = "ARN of the IAM role to assume for cross-account access"
  type        = string
  default     = null
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project       = "Ainflue"
    BusinessUnit  = "CreatorEconomy"
    ManagedBy     = "Terraform"
    Owner         = "Fahed Mlaiel"
  }
}

# ==============================================================================
# NETWORK CONFIGURATION
# ==============================================================================

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "enable_vpn_gateway" {
  description = "Enable VPN gateway for VPC"
  type        = bool
  default     = false
}

variable "cluster_endpoint_public_access" {
  description = "Enable public access to EKS cluster endpoint"
  type        = bool
  default     = true
}

# ==============================================================================
# KUBERNETES CLUSTER CONFIGURATION
# ==============================================================================

variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
  
  validation {
    condition = can(regex("^1\\.(2[4-9]|[3-9][0-9])$", var.kubernetes_version))
    error_message = "Kubernetes version must be 1.24 or higher."
  }
}

# ==============================================================================
# CREATOR ECONOMY NODE GROUP CONFIGURATION
# ==============================================================================

variable "creator_economy_instance_types" {
  description = "Instance types for Creator Economy workloads"
  type        = list(string)
  default     = ["m5.xlarge", "m5.2xlarge"]
  
  validation {
    condition = length(var.creator_economy_instance_types) > 0
    error_message = "At least one instance type must be specified."
  }
}

variable "creator_economy_nodes_min" {
  description = "Minimum number of nodes in Creator Economy node group"
  type        = number
  default     = 2
  
  validation {
    condition = var.creator_economy_nodes_min >= 1
    error_message = "Minimum nodes must be at least 1."
  }
}

variable "creator_economy_nodes_max" {
  description = "Maximum number of nodes in Creator Economy node group"
  type        = number
  default     = 20
  
  validation {
    condition = var.creator_economy_nodes_max >= var.creator_economy_nodes_min
    error_message = "Maximum nodes must be greater than or equal to minimum nodes."
  }
}

variable "creator_economy_nodes_desired" {
  description = "Desired number of nodes in Creator Economy node group"
  type        = number
  default     = 3
  
  validation {
    condition = (
      var.creator_economy_nodes_desired >= var.creator_economy_nodes_min &&
      var.creator_economy_nodes_desired <= var.creator_economy_nodes_max
    )
    error_message = "Desired nodes must be between minimum and maximum nodes."
  }
}

# ==============================================================================
# AI PROCESSING NODE GROUP CONFIGURATION
# ==============================================================================

variable "enable_gpu_nodes" {
  description = "Enable GPU nodes for AI processing workloads"
  type        = bool
  default     = true
}

variable "ai_processing_instance_types" {
  description = "Instance types for AI processing workloads"
  type        = list(string)
  default     = ["p3.2xlarge", "p3.8xlarge"]
  
  validation {
    condition = length(var.ai_processing_instance_types) > 0
    error_message = "At least one instance type must be specified."
  }
}

variable "ai_processing_nodes_min" {
  description = "Minimum number of nodes in AI processing node group"
  type        = number
  default     = 0
  
  validation {
    condition = var.ai_processing_nodes_min >= 0
    error_message = "Minimum nodes must be at least 0."
  }
}

variable "ai_processing_nodes_max" {
  description = "Maximum number of nodes in AI processing node group"
  type        = number
  default     = 10
  
  validation {
    condition = var.ai_processing_nodes_max >= var.ai_processing_nodes_min
    error_message = "Maximum nodes must be greater than or equal to minimum nodes."
  }
}

variable "ai_processing_nodes_desired" {
  description = "Desired number of nodes in AI processing node group"
  type        = number
  default     = 1
  
  validation {
    condition = (
      var.ai_processing_nodes_desired >= var.ai_processing_nodes_min &&
      var.ai_processing_nodes_desired <= var.ai_processing_nodes_max
    )
    error_message = "Desired nodes must be between minimum and maximum nodes."
  }
}

# ==============================================================================
# SYSTEM NODE GROUP CONFIGURATION
# ==============================================================================

variable "system_instance_types" {
  description = "Instance types for system workloads (monitoring, logging)"
  type        = list(string)
  default     = ["m5.large", "m5.xlarge"]
}

variable "system_nodes_min" {
  description = "Minimum number of nodes in system node group"
  type        = number
  default     = 1
  
  validation {
    condition = var.system_nodes_min >= 1
    error_message = "Minimum system nodes must be at least 1."
  }
}

variable "system_nodes_max" {
  description = "Maximum number of nodes in system node group"
  type        = number
  default     = 5
  
  validation {
    condition = var.system_nodes_max >= var.system_nodes_min
    error_message = "Maximum nodes must be greater than or equal to minimum nodes."
  }
}

variable "system_nodes_desired" {
  description = "Desired number of nodes in system node group"
  type        = number
  default     = 2
  
  validation {
    condition = (
      var.system_nodes_desired >= var.system_nodes_min &&
      var.system_nodes_desired <= var.system_nodes_max
    )
    error_message = "Desired nodes must be between minimum and maximum nodes."
  }
}

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================

variable "database_instance_class" {
  description = "RDS instance class for main PostgreSQL database"
  type        = string
  default     = "db.r5.large"
  
  validation {
    condition = can(regex("^db\\.[a-z0-9]+\\.[a-z0-9]+$", var.database_instance_class))
    error_message = "Database instance class must be in the format: db.r5.large."
  }
}

variable "database_allocated_storage" {
  description = "Allocated storage for main PostgreSQL database (GB)"
  type        = number
  default     = 100
  
  validation {
    condition = var.database_allocated_storage >= 20
    error_message = "Database allocated storage must be at least 20 GB."
  }
}

variable "analytics_database_instance_class" {
  description = "RDS instance class for analytics MySQL database"
  type        = string
  default     = "db.r5.xlarge"
}

variable "analytics_database_allocated_storage" {
  description = "Allocated storage for analytics MySQL database (GB)"
  type        = number
  default     = 200
  
  validation {
    condition = var.analytics_database_allocated_storage >= 20
    error_message = "Analytics database allocated storage must be at least 20 GB."
  }
}

variable "backup_retention_period" {
  description = "Backup retention period for databases (days)"
  type        = number
  default     = 30
  
  validation {
    condition = var.backup_retention_period >= 1 && var.backup_retention_period <= 35
    error_message = "Backup retention period must be between 1 and 35 days."
  }
}

# ==============================================================================
# REDIS CONFIGURATION
# ==============================================================================

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.r6g.large"
  
  validation {
    condition = can(regex("^cache\\.[a-z0-9]+\\.[a-z0-9]+$", var.redis_node_type))
    error_message = "Redis node type must be in the format: cache.r6g.large."
  }
}

variable "redis_num_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 2
  
  validation {
    condition = var.redis_num_nodes >= 1
    error_message = "Number of Redis nodes must be at least 1."
  }
}

# ==============================================================================
# SECURITY CONFIGURATION
# ==============================================================================

variable "enable_waf" {
  description = "Enable AWS WAF for web application firewall"
  type        = bool
  default     = true
}

variable "enable_shield_advanced" {
  description = "Enable AWS Shield Advanced for DDoS protection"
  type        = bool
  default     = false
}

variable "enable_drm" {
  description = "Enable Digital Rights Management for content protection"
  type        = bool
  default     = true
}

# ==============================================================================
# CONTENT DELIVERY CONFIGURATION
# ==============================================================================

variable "cloudfront_price_class" {
  description = "CloudFront distribution price class"
  type        = string
  default     = "PriceClass_100"
  
  validation {
    condition = contains([
      "PriceClass_All",
      "PriceClass_200", 
      "PriceClass_100"
    ], var.cloudfront_price_class)
    error_message = "CloudFront price class must be one of: PriceClass_All, PriceClass_200, PriceClass_100."
  }
}

variable "cloudfront_aliases" {
  description = "Custom domain aliases for CloudFront distribution"
  type        = list(string)
  default     = []
}

variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate for custom domains"
  type        = string
  default     = null
}

# ==============================================================================
# MONITORING CONFIGURATION
# ==============================================================================

variable "enable_elk_stack" {
  description = "Enable ELK (Elasticsearch, Logstash, Kibana) stack for logging"
  type        = bool
  default     = true
}

variable "enable_vpa" {
  description = "Enable Vertical Pod Autoscaler"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention period (days)"
  type        = number
  default     = 30
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch retention period."
  }
}

variable "alert_channels" {
  description = "Alert notification channels configuration"
  type = object({
    slack_webhook_url = optional(string)
    email_addresses   = optional(list(string))
    sns_topic_arn     = optional(string)
    pagerduty_key     = optional(string)
  })
  default = {}
}

# ==============================================================================
# CREATOR ECONOMY SPECIFIC CONFIGURATION
# ==============================================================================

variable "enable_content_analytics" {
  description = "Enable advanced content analytics and insights"
  type        = bool
  default     = true
}

variable "enable_collaboration_features" {
  description = "Enable real-time collaboration features"
  type        = bool
  default     = true
}

variable "enable_monetization_features" {
  description = "Enable monetization and revenue sharing features"
  type        = bool
  default     = true
}

variable "enable_seo_optimization" {
  description = "Enable SEO optimization features"
  type        = bool
  default     = true
}

variable "content_processing_config" {
  description = "Content processing configuration for different media types"
  type = object({
    video_processing = object({
      max_resolution    = optional(string, "4K")
      supported_formats = optional(list(string), ["mp4", "webm", "avi", "mov"])
      enable_ai_enhancement = optional(bool, true)
    })
    
    audio_processing = object({
      max_bitrate       = optional(string, "320kbps")
      supported_formats = optional(list(string), ["mp3", "wav", "flac", "aac"])
      enable_ai_enhancement = optional(bool, true)
    })
    
    image_processing = object({
      max_resolution    = optional(string, "8K")
      supported_formats = optional(list(string), ["jpg", "png", "webp", "svg"])
      enable_ai_enhancement = optional(bool, true)
    })
  })
  
  default = {
    video_processing = {
      max_resolution    = "4K"
      supported_formats = ["mp4", "webm", "avi", "mov"]
      enable_ai_enhancement = true
    }
    audio_processing = {
      max_bitrate       = "320kbps" 
      supported_formats = ["mp3", "wav", "flac", "aac"]
      enable_ai_enhancement = true
    }
    image_processing = {
      max_resolution    = "8K"
      supported_formats = ["jpg", "png", "webp", "svg"]
      enable_ai_enhancement = true
    }
  }
}

variable "revenue_sharing_config" {
  description = "Revenue sharing configuration for creators"
  type = object({
    platform_fee_percentage = optional(number, 5.0)
    creator_minimum_payout  = optional(number, 10.0)
    payment_schedule        = optional(string, "weekly")
    supported_currencies    = optional(list(string), ["USD", "EUR", "GBP"])
  })
  
  default = {
    platform_fee_percentage = 5.0
    creator_minimum_payout  = 10.0
    payment_schedule        = "weekly"
    supported_currencies    = ["USD", "EUR", "GBP"]
  }
  
  validation {
    condition = (
      var.revenue_sharing_config.platform_fee_percentage >= 0 &&
      var.revenue_sharing_config.platform_fee_percentage <= 30
    )
    error_message = "Platform fee percentage must be between 0 and 30."
  }
}

variable "collaboration_config" {
  description = "Collaboration features configuration"
  type = object({
    max_collaborators_per_project = optional(number, 10)
    enable_real_time_editing     = optional(bool, true)
    enable_version_control       = optional(bool, true)
    enable_comment_system        = optional(bool, true)
    enable_approval_workflow     = optional(bool, true)
  })
  
  default = {
    max_collaborators_per_project = 10
    enable_real_time_editing     = true
    enable_version_control       = true
    enable_comment_system        = true
    enable_approval_workflow     = true
  }
  
  validation {
    condition = var.collaboration_config.max_collaborators_per_project >= 1
    error_message = "Maximum collaborators per project must be at least 1."
  }
}

# ==============================================================================
# AI PROCESSING CONFIGURATION
# ==============================================================================

variable "ai_processing_config" {
  description = "AI processing configuration for content enhancement"
  type = object({
    # Video AI processing
    video_ai = object({
      enable_upscaling     = optional(bool, true)
      enable_denoising     = optional(bool, true)
      enable_stabilization = optional(bool, true)
      enable_auto_editing  = optional(bool, true)
      max_processing_time  = optional(number, 3600) # seconds
    })
    
    # Audio AI processing
    audio_ai = object({
      enable_noise_reduction = optional(bool, true)
      enable_voice_enhancement = optional(bool, true)
      enable_auto_mastering   = optional(bool, true)
      enable_transcription    = optional(bool, true)
      max_processing_time     = optional(number, 1800) # seconds
    })
    
    # Image AI processing
    image_ai = object({
      enable_upscaling      = optional(bool, true)
      enable_enhancement    = optional(bool, true)
      enable_background_removal = optional(bool, true)
      enable_auto_tagging   = optional(bool, true)
      max_processing_time   = optional(number, 300) # seconds
    })
    
    # Text AI processing
    text_ai = object({
      enable_translation    = optional(bool, true)
      enable_summarization  = optional(bool, true)
      enable_seo_optimization = optional(bool, true)
      enable_sentiment_analysis = optional(bool, true)
      max_processing_time   = optional(number, 60) # seconds
    })
  })
  
  default = {
    video_ai = {
      enable_upscaling     = true
      enable_denoising     = true
      enable_stabilization = true
      enable_auto_editing  = true
      max_processing_time  = 3600
    }
    audio_ai = {
      enable_noise_reduction  = true
      enable_voice_enhancement = true
      enable_auto_mastering   = true
      enable_transcription    = true
      max_processing_time     = 1800
    }
    image_ai = {
      enable_upscaling         = true
      enable_enhancement       = true
      enable_background_removal = true
      enable_auto_tagging      = true
      max_processing_time      = 300
    }
    text_ai = {
      enable_translation       = true
      enable_summarization     = true
      enable_seo_optimization  = true
      enable_sentiment_analysis = true
      max_processing_time      = 60
    }
  }
}

# ==============================================================================
# PERFORMANCE AND SCALING CONFIGURATION
# ==============================================================================

variable "performance_config" {
  description = "Performance optimization configuration"
  type = object({
    enable_auto_scaling       = optional(bool, true)
    enable_load_balancing     = optional(bool, true)
    enable_cdn               = optional(bool, true)
    enable_caching           = optional(bool, true)
    cache_ttl_seconds        = optional(number, 3600)
    max_concurrent_uploads   = optional(number, 100)
    max_file_size_mb         = optional(number, 5000)
  })
  
  default = {
    enable_auto_scaling       = true
    enable_load_balancing     = true
    enable_cdn               = true
    enable_caching           = true
    cache_ttl_seconds        = 3600
    max_concurrent_uploads   = 100
    max_file_size_mb         = 5000
  }
  
  validation {
    condition = var.performance_config.max_file_size_mb <= 10000
    error_message = "Maximum file size must not exceed 10000 MB (10 GB)."
  }
}

# ==============================================================================
# COST OPTIMIZATION CONFIGURATION
# ==============================================================================

variable "cost_optimization_config" {
  description = "Cost optimization configuration"
  type = object({
    enable_spot_instances     = optional(bool, false)
    enable_scheduled_scaling  = optional(bool, true)
    enable_resource_tagging   = optional(bool, true)
    enable_cost_monitoring    = optional(bool, true)
    budget_alert_threshold    = optional(number, 1000.0) # USD
  })
  
  default = {
    enable_spot_instances     = false
    enable_scheduled_scaling  = true
    enable_resource_tagging   = true
    enable_cost_monitoring    = true
    budget_alert_threshold    = 1000.0
  }
  
  validation {
    condition = var.cost_optimization_config.budget_alert_threshold > 0
    error_message = "Budget alert threshold must be greater than 0."
  }
}