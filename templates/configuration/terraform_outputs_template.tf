# Terraform Outputs - Ainflue Creator Economy Platform
# ====================================================
#
# 🎯 DEVOPS ENGINEER + CLOUD ARCHITECT + INFRASTRUCTURE EXPERT
# Lead: Fahed Mlaiel (mlaiel@live.de)
#
# Enterprise Infrastructure Outputs Definition
# - EKS cluster connection details
# - Database connection endpoints
# - Load balancer and CDN information
# - Security and monitoring endpoints
# - Creator Economy specific outputs
# - AI processing infrastructure details
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
# CLUSTER INFORMATION OUTPUTS
# ==============================================================================

output "cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_id
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = module.eks.cluster_arn
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster API server endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_version" {
  description = "EKS cluster Kubernetes version"
  value       = module.eks.cluster_version
}

output "cluster_platform_version" {
  description = "EKS cluster platform version"
  value       = module.eks.cluster_platform_version
}

output "cluster_status" {
  description = "EKS cluster status"
  value       = module.eks.cluster_status
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN of the EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster for the OpenID Connect identity provider"
  value       = module.eks.cluster_oidc_issuer_url
}

output "cluster_primary_security_group_id" {
  description = "EKS cluster primary security group ID"
  value       = module.eks.cluster_primary_security_group_id
}

# ==============================================================================
# NODE GROUPS OUTPUTS
# ==============================================================================

output "node_groups" {
  description = "EKS node groups information"
  value = {
    creator_economy = {
      arn           = module.eks.eks_managed_node_groups["creator_economy"].arn
      status        = module.eks.eks_managed_node_groups["creator_economy"].status
      capacity_type = module.eks.eks_managed_node_groups["creator_economy"].capacity_type
      instance_types = module.eks.eks_managed_node_groups["creator_economy"].instance_types
      ami_type      = module.eks.eks_managed_node_groups["creator_economy"].ami_type
      node_group_name = module.eks.eks_managed_node_groups["creator_economy"].node_group_name
    }
    
    ai_processing = {
      arn           = module.eks.eks_managed_node_groups["ai_processing"].arn
      status        = module.eks.eks_managed_node_groups["ai_processing"].status
      capacity_type = module.eks.eks_managed_node_groups["ai_processing"].capacity_type
      instance_types = module.eks.eks_managed_node_groups["ai_processing"].instance_types
      ami_type      = module.eks.eks_managed_node_groups["ai_processing"].ami_type
      node_group_name = module.eks.eks_managed_node_groups["ai_processing"].node_group_name
    }
    
    system = {
      arn           = module.eks.eks_managed_node_groups["system"].arn
      status        = module.eks.eks_managed_node_groups["system"].status
      capacity_type = module.eks.eks_managed_node_groups["system"].capacity_type
      instance_types = module.eks.eks_managed_node_groups["system"].instance_types
      ami_type      = module.eks.eks_managed_node_groups["system"].ami_type
      node_group_name = module.eks.eks_managed_node_groups["system"].node_group_name
    }
  }
}

# ==============================================================================
# NETWORK OUTPUTS
# ==============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_arn" {
  description = "VPC ARN"
  value       = module.vpc.vpc_arn
}

output "vpc_cidr_block" {
  description = "VPC CIDR block"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnets
}

output "database_subnets" {
  description = "List of database subnet IDs"
  value       = module.vpc.database_subnets
}

output "database_subnet_group" {
  description = "Database subnet group name"
  value       = module.vpc.database_subnet_group
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = module.vpc.nat_gateway_ids
}

output "internet_gateway_id" {
  description = "Internet Gateway ID"
  value       = module.vpc.internet_gateway_id
}

# ==============================================================================
# DATABASE OUTPUTS
# ==============================================================================

output "database_endpoints" {
  description = "Database connection endpoints"
  value = {
    postgresql = {
      endpoint = module.database.postgresql_endpoint
      port     = module.database.postgresql_port
      username = module.database.postgresql_username
      database_name = module.database.postgresql_database_name
    }
    
    mysql = {
      endpoint = module.database.mysql_endpoint
      port     = module.database.mysql_port
      username = module.database.mysql_username
      database_name = module.database.mysql_database_name
    }
  }
  
  sensitive = true
}

output "database_security_group_ids" {
  description = "Database security group IDs"
  value = {
    postgresql = module.database.postgresql_security_group_id
    mysql      = module.database.mysql_security_group_id
  }
}

output "redis_endpoints" {
  description = "Redis cache endpoints"
  value = {
    primary_endpoint   = module.database.redis_primary_endpoint
    reader_endpoint    = module.database.redis_reader_endpoint
    configuration_endpoint = module.database.redis_configuration_endpoint
  }
  
  sensitive = true
}

output "redis_security_group_id" {
  description = "Redis security group ID"
  value       = module.database.redis_security_group_id
}

# ==============================================================================
# SECURITY OUTPUTS
# ==============================================================================

output "security_configurations" {
  description = "Security infrastructure details"
  value = {
    waf_arn                    = module.security.waf_arn
    shield_protection_id       = module.security.shield_protection_id
    secrets_manager_arn        = module.security.secrets_manager_arn
    certificate_manager_arn    = module.security.certificate_manager_arn
    kms_key_arn               = aws_kms_key.eks.arn
    kms_key_alias             = aws_kms_alias.eks.name
  }
}

output "iam_roles" {
  description = "IAM roles created for the infrastructure"
  value = {
    cluster_service_role_arn = module.eks.cluster_iam_role_arn
    node_group_role_arn     = module.eks.eks_managed_node_groups["creator_economy"].iam_role_arn
    rds_monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn
  }
}

# ==============================================================================
# CONTENT DELIVERY OUTPUTS
# ==============================================================================

output "cdn_distribution" {
  description = "CloudFront distribution details"
  value = {
    id                = module.cdn.cloudfront_distribution_id
    arn               = module.cdn.cloudfront_distribution_arn
    domain_name       = module.cdn.cloudfront_distribution_domain_name
    hosted_zone_id    = module.cdn.cloudfront_distribution_hosted_zone_id
    status            = module.cdn.cloudfront_distribution_status
  }
}

output "content_buckets" {
  description = "S3 buckets for content storage"
  value = {
    video_bucket = {
      id                = module.cdn.video_bucket_id
      arn               = module.cdn.video_bucket_arn
      domain_name       = module.cdn.video_bucket_domain_name
      regional_domain_name = module.cdn.video_bucket_regional_domain_name
    }
    
    audio_bucket = {
      id                = module.cdn.audio_bucket_id
      arn               = module.cdn.audio_bucket_arn
      domain_name       = module.cdn.audio_bucket_domain_name
      regional_domain_name = module.cdn.audio_bucket_regional_domain_name
    }
    
    images_bucket = {
      id                = module.cdn.images_bucket_id
      arn               = module.cdn.images_bucket_arn
      domain_name       = module.cdn.images_bucket_domain_name
      regional_domain_name = module.cdn.images_bucket_regional_domain_name
    }
    
    documents_bucket = {
      id                = module.cdn.documents_bucket_id
      arn               = module.cdn.documents_bucket_arn
      domain_name       = module.cdn.documents_bucket_domain_name
      regional_domain_name = module.cdn.documents_bucket_regional_domain_name
    }
  }
}

# ==============================================================================
# MONITORING OUTPUTS
# ==============================================================================

output "monitoring_endpoints" {
  description = "Monitoring and observability endpoints"
  value = {
    prometheus_endpoint = module.monitoring.prometheus_endpoint
    grafana_endpoint   = module.monitoring.grafana_endpoint
    jaeger_endpoint    = module.monitoring.jaeger_endpoint
    kibana_endpoint    = module.monitoring.kibana_endpoint
    x_ray_endpoint     = module.monitoring.x_ray_endpoint
  }
  
  sensitive = true
}

output "log_groups" {
  description = "CloudWatch log groups"
  value = {
    cluster_logs        = module.monitoring.cluster_log_group_name
    application_logs    = module.monitoring.application_log_group_name
    vpc_flow_logs      = module.monitoring.vpc_flow_log_group_name
    creator_economy_logs = module.monitoring.creator_economy_log_group_name
    ai_processing_logs  = module.monitoring.ai_processing_log_group_name
  }
}

# ==============================================================================
# CREATOR ECONOMY SPECIFIC OUTPUTS
# ==============================================================================

output "creator_economy_infrastructure" {
  description = "Creator Economy specific infrastructure details"
  value = {
    # Content processing endpoints
    content_processing = {
      video_processing_endpoint = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/content/video/process"
      audio_processing_endpoint = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/content/audio/process"
      image_processing_endpoint = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/content/image/process"
    }
    
    # Collaboration endpoints
    collaboration = {
      real_time_api_endpoint = "wss://${module.cdn.cloudfront_distribution_domain_name}/api/v1/collaboration/realtime"
      version_control_endpoint = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/collaboration/versions"
      comment_system_endpoint = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/collaboration/comments"
    }
    
    # Monetization endpoints
    monetization = {
      payment_processing_endpoint = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/monetization/payments"
      revenue_sharing_endpoint   = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/monetization/revenue"
      subscription_endpoint      = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/monetization/subscriptions"
    }
    
    # SEO optimization endpoints
    seo = {
      optimization_endpoint = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/seo/optimize"
      analytics_endpoint   = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/seo/analytics"
      sitemap_endpoint     = "https://${module.cdn.cloudfront_distribution_domain_name}/sitemap.xml"
    }
    
    # Distribution endpoints
    distribution = {
      content_api_endpoint = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/distribution/content"
      social_media_endpoint = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/distribution/social"
      embed_endpoint       = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/distribution/embed"
    }
  }
}

# ==============================================================================
# AI PROCESSING OUTPUTS
# ==============================================================================

output "ai_processing_infrastructure" {
  description = "AI processing infrastructure details"
  value = {
    # GPU node information
    gpu_nodes = {
      instance_types = var.ai_processing_instance_types
      min_nodes     = var.ai_processing_nodes_min
      max_nodes     = var.ai_processing_nodes_max
      current_nodes = var.ai_processing_nodes_desired
      gpu_enabled   = var.enable_gpu_nodes
    }
    
    # AI processing endpoints
    ai_services = {
      video_ai_endpoint    = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/ai/video"
      audio_ai_endpoint    = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/ai/audio"
      image_ai_endpoint    = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/ai/image"
      text_ai_endpoint     = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/ai/text"
      ml_model_endpoint    = "https://${module.cdn.cloudfront_distribution_domain_name}/api/v1/ai/models"
    }
    
    # AI processing configuration
    processing_limits = {
      video_max_processing_time = var.ai_processing_config.video_ai.max_processing_time
      audio_max_processing_time = var.ai_processing_config.audio_ai.max_processing_time
      image_max_processing_time = var.ai_processing_config.image_ai.max_processing_time
      text_max_processing_time  = var.ai_processing_config.text_ai.max_processing_time
    }
  }
}

# ==============================================================================
# AUTO-SCALING OUTPUTS
# ==============================================================================

output "autoscaling_configuration" {
  description = "Auto-scaling configuration details"
  value = {
    # Horizontal Pod Autoscaler
    hpa_configs = module.autoscaling.hpa_configurations
    
    # Vertical Pod Autoscaler
    vpa_enabled = var.enable_vpa
    
    # Cluster Autoscaler
    cluster_autoscaler = module.autoscaling.cluster_autoscaler_configuration
  }
}

# ==============================================================================
# PERFORMANCE OUTPUTS
# ==============================================================================

output "performance_configuration" {
  description = "Performance optimization configuration"
  value = {
    cdn_enabled           = var.performance_config.enable_cdn
    caching_enabled       = var.performance_config.enable_caching
    cache_ttl_seconds     = var.performance_config.cache_ttl_seconds
    max_concurrent_uploads = var.performance_config.max_concurrent_uploads
    max_file_size_mb      = var.performance_config.max_file_size_mb
    auto_scaling_enabled  = var.performance_config.enable_auto_scaling
    load_balancing_enabled = var.performance_config.enable_load_balancing
  }
}

# ==============================================================================
# COST OPTIMIZATION OUTPUTS
# ==============================================================================

output "cost_optimization" {
  description = "Cost optimization configuration and estimates"
  value = {
    spot_instances_enabled     = var.cost_optimization_config.enable_spot_instances
    scheduled_scaling_enabled  = var.cost_optimization_config.enable_scheduled_scaling
    resource_tagging_enabled   = var.cost_optimization_config.enable_resource_tagging
    cost_monitoring_enabled    = var.cost_optimization_config.enable_cost_monitoring
    budget_alert_threshold_usd = var.cost_optimization_config.budget_alert_threshold
  }
}

# ==============================================================================
# CONNECTION INSTRUCTIONS OUTPUTS
# ==============================================================================

output "kubectl_config_command" {
  description = "Command to configure kubectl for the EKS cluster"
  value = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "cluster_connection_info" {
  description = "Information needed to connect to the cluster"
  value = {
    cluster_name   = module.eks.cluster_name
    cluster_region = var.aws_region
    cluster_endpoint = module.eks.cluster_endpoint
    
    # Commands for connection
    kubectl_config_cmd = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
    helm_repo_add_cmd  = "helm repo add ainflue-charts https://charts.ainflue.com"
    
    # Dashboard URLs (when deployed)
    dashboard_urls = {
      kubernetes_dashboard = "https://${module.cdn.cloudfront_distribution_domain_name}/dashboard"
      grafana             = "https://${module.cdn.cloudfront_distribution_domain_name}/grafana"
      prometheus          = "https://${module.cdn.cloudfront_distribution_domain_name}/prometheus"
      jaeger              = "https://${module.cdn.cloudfront_distribution_domain_name}/jaeger"
      kibana              = "https://${module.cdn.cloudfront_distribution_domain_name}/kibana"
    }
  }
}

# ==============================================================================
# ENVIRONMENT SUMMARY OUTPUT
# ==============================================================================

output "deployment_summary" {
  description = "Complete deployment summary for Ainflue Creator Economy Platform"
  value = {
    # Infrastructure details
    infrastructure = {
      environment        = var.environment
      region            = var.aws_region
      cluster_name      = module.eks.cluster_name
      kubernetes_version = var.kubernetes_version
      vpc_cidr          = var.vpc_cidr
    }
    
    # Creator Economy features
    creator_economy_features = {
      content_analytics_enabled     = var.enable_content_analytics
      collaboration_features_enabled = var.enable_collaboration_features
      monetization_features_enabled  = var.enable_monetization_features
      seo_optimization_enabled      = var.enable_seo_optimization
      ai_processing_enabled         = var.enable_gpu_nodes
      drm_enabled                   = var.enable_drm
    }
    
    # Security features
    security_features = {
      waf_enabled           = var.enable_waf
      shield_advanced_enabled = var.enable_shield_advanced
      secrets_manager_enabled = true
      certificate_manager_enabled = true
      vpc_flow_logs_enabled = true
      encryption_enabled    = true
    }
    
    # Monitoring features
    monitoring_features = {
      prometheus_enabled = true
      grafana_enabled   = true
      jaeger_enabled    = true
      elk_stack_enabled = var.enable_elk_stack
      x_ray_enabled     = true
      cloudwatch_logs_enabled = true
    }
    
    # Performance features
    performance_features = {
      auto_scaling_enabled   = var.performance_config.enable_auto_scaling
      load_balancing_enabled = var.performance_config.enable_load_balancing
      cdn_enabled           = var.performance_config.enable_cdn
      caching_enabled       = var.performance_config.enable_caching
      vpa_enabled           = var.enable_vpa
    }
    
    # Deployment timestamp
    deployed_at = formatdate("YYYY-MM-DD'T'hh:mm:ssZ", timestamp())
    deployed_by = "Terraform"
    owner       = "Fahed Mlaiel (mlaiel@live.de)"
  }
}