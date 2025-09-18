# Terraform Modules Template - Ainflue Creator Economy Platform
# =============================================================
#
# 🎯 DEVOPS ENGINEER + TERRAFORM EXPERT + MODULE ARCHITECT
# Lead: Fahed Mlaiel (mlaiel@live.de)
#
# Enterprise Terraform modules structure for Creator Economy Platform:
# - Reusable infrastructure modules
# - Creator Economy specific modules
# - AI processing infrastructure modules
# - Security and compliance modules
# - Monitoring and observability modules
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
# VPC MODULE
# ==============================================================================
module "vpc" {
  source = "./modules/vpc"
  
  # Basic configuration
  name               = var.cluster_name
  cidr               = var.vpc_cidr
  azs                = data.aws_availability_zones.available.names
  private_subnets    = local.private_subnets
  public_subnets     = local.public_subnets
  database_subnets   = local.database_subnets
  
  # NAT Gateway configuration
  enable_nat_gateway   = true
  single_nat_gateway   = var.environment == "development"
  enable_vpn_gateway   = var.enable_vpn_gateway
  
  # DNS configuration
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  # VPC Flow Logs for security
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true
  flow_log_max_aggregation_interval    = 60
  
  # Creator Economy specific networking
  enable_s3_endpoint       = true
  enable_dynamodb_endpoint = true
  enable_ec2_endpoint      = true
  enable_ecs_endpoint      = true
  enable_ecr_api_endpoint  = true
  enable_ecr_dkr_endpoint  = true
  
  # Subnet configuration
  create_database_subnet_group           = true
  create_database_subnet_route_table     = true
  create_database_internet_gateway_route = false
  
  # DHCP options
  enable_dhcp_options                = true
  dhcp_options_domain_name          = "${var.environment}.ainflue.local"
  dhcp_options_domain_name_servers  = ["AmazonProvidedDNS"]
  
  tags = merge(local.common_tags, {
    Name = "${var.cluster_name}-vpc"
    Module = "vpc"
  })
}

# ==============================================================================
# EKS MODULE
# ==============================================================================
module "eks" {
  source = "./modules/eks"
  
  # Cluster configuration
  cluster_name                   = var.cluster_name
  cluster_version               = var.kubernetes_version
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = var.cluster_endpoint_public_access
  
  # Network configuration
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  # Control plane logging
  cluster_enabled_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]
  
  # OIDC configuration
  enable_irsa = true
  
  # Encryption configuration
  cluster_encryption_config = [
    {
      provider_key_arn = module.kms.key_arn
      resources        = ["secrets"]
    }
  ]
  
  # Node groups configuration
  node_groups = local.node_groups_config
  
  # Addons
  cluster_addons = {
    coredns = {
      resolve_conflicts = "OVERWRITE"
      addon_version     = "v1.10.1-eksbuild.4"
    }
    kube-proxy = {
      resolve_conflicts = "OVERWRITE"
      addon_version     = "v1.28.2-eksbuild.2"
    }
    vpc-cni = {
      resolve_conflicts = "OVERWRITE"
      addon_version     = "v1.15.1-eksbuild.1"
      configuration_values = jsonencode({
        env = {
          ENABLE_PREFIX_DELEGATION = "true"
          WARM_PREFIX_TARGET      = "1"
        }
      })
    }
    aws-ebs-csi-driver = {
      resolve_conflicts = "OVERWRITE"
      addon_version     = "v1.24.0-eksbuild.1"
    }
  }
  
  tags = merge(local.common_tags, {
    Module = "eks"
  })
}

# ==============================================================================
# SECURITY MODULE
# ==============================================================================
module "security" {
  source = "./modules/security"
  
  # Basic configuration
  cluster_name = var.cluster_name
  vpc_id       = module.vpc.vpc_id
  environment  = var.environment
  
  # WAF configuration
  enable_waf = var.enable_waf
  waf_config = {
    name        = "${var.cluster_name}-waf"
    description = "WAF for Ainflue Creator Economy Platform"
    
    # Rate limiting rules
    rate_limit_rules = [
      {
        name     = "CreatorAPIRateLimit"
        priority = 1
        rate_limit = {
          limit              = 2000
          window             = 300 # 5 minutes
          aggregate_key_type = "IP"
        }
        statement = {
          byte_match_statement = {
            field_to_match = {
              uri_path = {}
            }
            positional_constraint = "STARTS_WITH"
            search_string        = "/api/v1/creators"
            text_transformations = [
              {
                priority = 0
                type     = "LOWERCASE"
              }
            ]
          }
        }
      },
      {
        name     = "AIProcessingRateLimit"
        priority = 2
        rate_limit = {
          limit              = 100
          window             = 300
          aggregate_key_type = "IP"
        }
        statement = {
          byte_match_statement = {
            field_to_match = {
              uri_path = {}
            }
            positional_constraint = "STARTS_WITH"
            search_string        = "/api/v1/ai"
            text_transformations = [
              {
                priority = 0
                type     = "LOWERCASE"
              }
            ]
          }
        }
      }
    ]
    
    # Geo blocking rules
    geo_blocking_rules = [
      {
        name     = "BlockHighRiskCountries"
        priority = 10
        countries = ["CN", "RU", "KP"] # Block high-risk countries
      }
    ]
    
    # SQL injection protection
    sqli_rules = [
      {
        name     = "SQLInjectionProtection"
        priority = 20
        action   = "BLOCK"
      }
    ]
    
    # XSS protection
    xss_rules = [
      {
        name     = "XSSProtection"
        priority = 21
        action   = "BLOCK"
      }
    ]
  }
  
  # Shield configuration
  enable_shield_advanced = var.enable_shield_advanced
  shield_config = {
    protection_groups = [
      {
        protection_group_id = "${var.cluster_name}-creators"
        aggregation        = "SUM"
        pattern           = "ALL"
        resource_type     = "APPLICATION_LOAD_BALANCER"
      }
    ]
  }
  
  # Secrets Manager configuration
  enable_secrets_manager = true
  secrets_config = {
    secrets = [
      {
        name        = "${var.cluster_name}/database/password"
        description = "Database master password"
        generate_password = true
        password_length   = 32
      },
      {
        name        = "${var.cluster_name}/redis/password"
        description = "Redis authentication password"
        generate_password = true
        password_length   = 32
      },
      {
        name        = "${var.cluster_name}/jwt/secret"
        description = "JWT signing secret"
        generate_password = true
        password_length   = 64
      }
    ]
  }
  
  # Certificate Manager configuration
  enable_certificate_manager = true
  certificate_config = {
    domain_name = "ainflue.com"
    subject_alternative_names = [
      "*.ainflue.com",
      "api.ainflue.com",
      "creators.ainflue.com",
      "collaborate.ainflue.com",
      "monetize.ainflue.com",
      "ai.ainflue.com",
      "cdn.ainflue.com"
    ]
    validation_method = "DNS"
  }
  
  # Creator Economy security features
  enable_content_protection = true
  content_protection_config = {
    enable_drm           = var.enable_drm
    enable_watermarking  = true
    enable_access_control = true
    allowed_domains = [
      "ainflue.com",
      "creators.ainflue.com"
    ]
  }
  
  # IP protection
  enable_ip_protection = true
  ip_protection_config = {
    enable_copyright_detection = true
    enable_plagiarism_check   = true
    enable_content_fingerprinting = true
  }
  
  tags = merge(local.common_tags, {
    Module = "security"
  })
}

# ==============================================================================
# DATABASE MODULE
# ==============================================================================
module "database" {
  source = "./modules/database"
  
  # Basic configuration
  cluster_name = var.cluster_name
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.database_subnets
  environment  = var.environment
  
  # PostgreSQL configuration (Main database)
  enable_postgresql = true
  postgresql_config = {
    identifier     = "${var.cluster_name}-postgresql"
    engine_version = "15.4"
    instance_class = var.database_instance_class
    
    allocated_storage     = var.database_allocated_storage
    max_allocated_storage = var.database_allocated_storage * 2
    storage_type         = "gp3"
    storage_encrypted    = true
    kms_key_id          = module.kms.key_arn
    
    db_name  = "ainflue"
    username = "ainflue_admin"
    port     = 5432
    
    # High availability
    multi_az                = var.environment == "production"
    backup_retention_period = var.backup_retention_period
    backup_window          = "03:00-04:00"
    maintenance_window     = "sun:04:00-sun:05:00"
    
    # Performance insights
    performance_insights_enabled          = true
    performance_insights_retention_period = 7
    performance_insights_kms_key_id      = module.kms.key_arn
    
    # Enhanced monitoring
    monitoring_interval = 60
    
    # Parameter group settings
    parameters = [
      {
        name  = "shared_preload_libraries"
        value = "pg_stat_statements,auto_explain"
      },
      {
        name  = "log_statement"
        value = "all"
      },
      {
        name  = "log_min_duration_statement"
        value = "1000"
      },
      {
        name  = "max_connections"
        value = "200"
      }
    ]
  }
  
  # MySQL configuration (Analytics database)
  enable_mysql = true
  mysql_config = {
    identifier     = "${var.cluster_name}-mysql"
    engine_version = "8.0.35"
    instance_class = var.analytics_database_instance_class
    
    allocated_storage     = var.analytics_database_allocated_storage
    max_allocated_storage = var.analytics_database_allocated_storage * 2
    storage_type         = "gp3"
    storage_encrypted    = true
    kms_key_id          = module.kms.key_arn
    
    db_name  = "ainflue_analytics"
    username = "analytics_admin"
    port     = 3306
    
    # High availability
    multi_az                = var.environment == "production"
    backup_retention_period = var.backup_retention_period
    backup_window          = "02:00-03:00"
    maintenance_window     = "sun:03:00-sun:04:00"
    
    # Performance insights
    performance_insights_enabled          = true
    performance_insights_retention_period = 7
    performance_insights_kms_key_id      = module.kms.key_arn
    
    # Parameter group settings
    parameters = [
      {
        name  = "innodb_buffer_pool_size"
        value = "{DBInstanceClassMemory*3/4}"
      },
      {
        name  = "slow_query_log"
        value = "1"
      },
      {
        name  = "long_query_time"
        value = "2"
      }
    ]
  }
  
  # ElastiCache Redis configuration
  enable_elasticache = true
  elasticache_config = {
    cluster_id           = "${var.cluster_name}-redis"
    engine               = "redis"
    engine_version       = "7.0"
    port                 = 6379
    parameter_group_name = "default.redis7"
    node_type           = var.redis_node_type
    num_cache_nodes     = var.redis_num_nodes
    
    # High availability
    automatic_failover_enabled = var.environment == "production"
    multi_az_enabled          = var.environment == "production"
    
    # Security
    at_rest_encryption_enabled = true
    transit_encryption_enabled = true
    auth_token_enabled         = true
    
    # Backup
    snapshot_retention_limit = 7
    snapshot_window         = "01:00-02:00"
    
    # Maintenance
    maintenance_window = "sun:02:00-sun:03:00"
    
    # Log configuration
    log_delivery_configuration = [
      {
        destination      = module.monitoring.redis_log_group_name
        destination_type = "cloudwatch-logs"
        log_format      = "json"
        log_type        = "slow-log"
      }
    ]
  }
  
  tags = merge(local.common_tags, {
    Module = "database"
  })
}

# ==============================================================================
# CDN MODULE
# ==============================================================================
module "cdn" {
  source = "./modules/cdn"
  
  # Basic configuration
  cluster_name = var.cluster_name
  environment  = var.environment
  
  # S3 buckets for content storage
  enable_s3_buckets = true
  s3_buckets_config = local.content_buckets_config
  
  # CloudFront distribution
  enable_cloudfront = true
  cloudfront_config = {
    aliases             = var.cloudfront_aliases
    comment            = "Ainflue Creator Economy CDN"
    default_root_object = "index.html"
    enabled            = true
    http_version       = "http2and3"
    is_ipv6_enabled    = true
    price_class        = var.cloudfront_price_class
    
    # Origin configuration
    origins = [
      {
        domain_name = module.load_balancer.dns_name
        origin_id   = "ALB-${var.cluster_name}"
        
        custom_origin_config = {
          http_port              = 80
          https_port             = 443
          origin_protocol_policy = "https-only"
          origin_ssl_protocols   = ["TLSv1.2"]
        }
      }
    ]
    
    # Default cache behavior
    default_cache_behavior = {
      target_origin_id       = "ALB-${var.cluster_name}"
      viewer_protocol_policy = "redirect-to-https"
      
      allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
      cached_methods   = ["GET", "HEAD"]
      compress        = true
      
      forwarded_values = {
        query_string = true
        cookies = {
          forward = "all"
        }
        headers = [
          "Authorization",
          "CloudFront-Forwarded-Proto",
          "Host",
          "User-Agent",
          "Referer"
        ]
      }
      
      min_ttl     = 0
      default_ttl = 3600
      max_ttl     = 86400
    }
    
    # Ordered cache behaviors for different content types
    ordered_cache_behaviors = [
      # Static assets
      {
        path_pattern     = "/static/*"
        target_origin_id = "S3-${var.cluster_name}-static"
        
        allowed_methods        = ["GET", "HEAD", "OPTIONS"]
        cached_methods         = ["GET", "HEAD"]
        viewer_protocol_policy = "redirect-to-https"
        compress              = true
        
        forwarded_values = {
          query_string = false
          cookies = {
            forward = "none"
          }
        }
        
        min_ttl     = 0
        default_ttl = 86400
        max_ttl     = 31536000
      },
      
      # API endpoints (no caching)
      {
        path_pattern     = "/api/*"
        target_origin_id = "ALB-${var.cluster_name}"
        
        allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
        cached_methods         = ["GET", "HEAD"]
        viewer_protocol_policy = "redirect-to-https"
        compress              = false
        
        forwarded_values = {
          query_string = true
          cookies = {
            forward = "all"
          }
          headers = ["*"]
        }
        
        min_ttl     = 0
        default_ttl = 0
        max_ttl     = 0
      },
      
      # Video content
      {
        path_pattern     = "/content/video/*"
        target_origin_id = "S3-${var.cluster_name}-video"
        
        allowed_methods        = ["GET", "HEAD"]
        cached_methods         = ["GET", "HEAD"]
        viewer_protocol_policy = "redirect-to-https"
        compress              = false
        
        forwarded_values = {
          query_string = true
          cookies = {
            forward = "whitelist"
            whitelisted_names = ["auth_token"]
          }
          headers = [
            "Range",
            "Origin",
            "Access-Control-Request-Headers",
            "Access-Control-Request-Method"
          ]
        }
        
        min_ttl     = 0
        default_ttl = 86400
        max_ttl     = 31536000
      }
    ]
    
    # Geographic restrictions
    restrictions = {
      geo_restriction = {
        restriction_type = "none"
      }
    }
    
    # SSL certificate
    viewer_certificate = {
      acm_certificate_arn      = var.ssl_certificate_arn
      ssl_support_method       = "sni-only"
      minimum_protocol_version = "TLSv1.2_2021"
    }
    
    # Custom error pages
    custom_error_responses = [
      {
        error_code            = 404
        error_caching_min_ttl = 300
        response_code         = 404
        response_page_path    = "/404.html"
      },
      {
        error_code            = 500
        error_caching_min_ttl = 300
        response_code         = 500
        response_page_path    = "/500.html"
      }
    ]
    
    # Web ACL association
    web_acl_id = module.security.waf_arn
  }
  
  tags = merge(local.common_tags, {
    Module = "cdn"
  })
}

# ==============================================================================
# MONITORING MODULE
# ==============================================================================
module "monitoring" {
  source = "./modules/monitoring"
  
  # Basic configuration
  cluster_name = var.cluster_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnets
  
  # CloudWatch configuration
  enable_cloudwatch = true
  cloudwatch_config = {
    log_retention_days = var.log_retention_days
    
    log_groups = [
      {
        name              = "/aws/eks/${var.cluster_name}/cluster"
        retention_in_days = var.log_retention_days
        kms_key_id       = module.kms.key_arn
      },
      {
        name              = "/ainflue/creator-economy/application"
        retention_in_days = var.log_retention_days
        kms_key_id       = module.kms.key_arn
      },
      {
        name              = "/ainflue/ai-processing/jobs"
        retention_in_days = var.log_retention_days
        kms_key_id       = module.kms.key_arn
      },
      {
        name              = "/ainflue/collaboration/realtime"
        retention_in_days = var.log_retention_days
        kms_key_id       = module.kms.key_arn
      },
      {
        name              = "/ainflue/monetization/transactions"
        retention_in_days = var.log_retention_days
        kms_key_id       = module.kms.key_arn
      }
    ]
    
    # Creator Economy specific metrics
    custom_metrics = [
      {
        namespace   = "Ainflue/CreatorEconomy"
        metric_name = "ActiveCreators"
        unit        = "Count"
      },
      {
        namespace   = "Ainflue/CreatorEconomy"
        metric_name = "ContentProcessingJobs"
        unit        = "Count"
      },
      {
        namespace   = "Ainflue/CreatorEconomy"
        metric_name = "RevenueGenerated"
        unit        = "Count"
      },
      {
        namespace   = "Ainflue/AIProcessing"
        metric_name = "ProcessingTime"
        unit        = "Seconds"
      }
    ]
    
    # Alarms configuration
    alarms = [
      {
        alarm_name        = "${var.cluster_name}-high-cpu"
        alarm_description = "High CPU utilization"
        metric_name       = "CPUUtilization"
        namespace         = "AWS/EKS"
        statistic         = "Average"
        period            = 300
        evaluation_periods = 2
        threshold         = 80
        comparison_operator = "GreaterThanThreshold"
        alarm_actions     = [module.sns.topic_arn]
      },
      {
        alarm_name        = "${var.cluster_name}-failed-ai-jobs"
        alarm_description = "High AI processing job failures"
        metric_name       = "FailedJobs"
        namespace         = "Ainflue/AIProcessing"
        statistic         = "Sum"
        period            = 300
        evaluation_periods = 1
        threshold         = 5
        comparison_operator = "GreaterThanThreshold"
        alarm_actions     = [module.sns.topic_arn]
      }
    ]
  }
  
  # Prometheus configuration
  enable_prometheus = true
  prometheus_config = {
    retention_days = 15
    storage_size   = "100Gi"
    
    # Creator Economy specific scrape configs
    scrape_configs = [
      {
        job_name = "creator-platform"
        metrics_path = "/metrics"
        scrape_interval = "30s"
        static_configs = [
          {
            targets = ["creator-platform-service:8080"]
          }
        ]
      },
      {
        job_name = "ai-processor"
        metrics_path = "/metrics"
        scrape_interval = "60s"
        static_configs = [
          {
            targets = ["ai-processing-service:8080"]
          }
        ]
      }
    ]
  }
  
  # Grafana configuration
  enable_grafana = true
  grafana_config = {
    storage_size = "50Gi"
    
    # Creator Economy dashboards
    dashboards = [
      {
        title = "Creator Economy Overview"
        path  = "dashboards/creator-economy-overview.json"
      },
      {
        title = "AI Processing Metrics"
        path  = "dashboards/ai-processing-metrics.json"
      },
      {
        title = "Collaboration Metrics"
        path  = "dashboards/collaboration-metrics.json"
      },
      {
        title = "Monetization Dashboard"
        path  = "dashboards/monetization-dashboard.json"
      }
    ]
  }
  
  # Jaeger tracing
  enable_jaeger = true
  jaeger_config = {
    storage_type = "elasticsearch"
    retention_days = 7
  }
  
  # ELK Stack
  enable_elk_stack = var.enable_elk_stack
  elk_config = {
    elasticsearch = {
      storage_size = "200Gi"
      replicas     = 3
    }
    kibana = {
      replicas = 2
    }
    logstash = {
      replicas = 2
    }
  }
  
  # X-Ray tracing
  enable_x_ray = true
  
  # SNS for alerting
  enable_sns = true
  sns_config = {
    topic_name = "${var.cluster_name}-alerts"
    endpoints  = var.alert_channels.email_addresses
  }
  
  tags = merge(local.common_tags, {
    Module = "monitoring"
  })
}

# ==============================================================================
# KMS MODULE
# ==============================================================================
module "kms" {
  source = "./modules/kms"
  
  # Basic configuration
  cluster_name = var.cluster_name
  environment  = var.environment
  
  # Key configuration
  key_description = "Ainflue Creator Economy Platform encryption key"
  key_usage       = "ENCRYPT_DECRYPT"
  key_spec        = "SYMMETRIC_DEFAULT"
  
  # Key policy for Creator Economy services
  key_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EnableIAMUserPermissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "AllowCreatorEconomyServices"
        Effect = "Allow"
        Principal = {
          AWS = [
            module.eks.cluster_iam_role_arn,
            module.database.rds_monitoring_role_arn
          ]
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
  
  # Key rotation
  enable_key_rotation = true
  
  # Aliases
  aliases = [
    "alias/${var.cluster_name}-main",
    "alias/ainflue-creator-economy"
  ]
  
  tags = merge(local.common_tags, {
    Module = "kms"
  })
}

# ==============================================================================
# AUTOSCALING MODULE
# ==============================================================================
module "autoscaling" {
  source = "./modules/autoscaling"
  
  # Basic configuration
  cluster_name = var.cluster_name
  environment  = var.environment
  
  # HPA configurations for Creator Economy services
  hpa_configs = {
    creator_platform = {
      min_replicas = 3
      max_replicas = 50
      target_cpu_utilization    = 70
      target_memory_utilization = 80
      scale_down_stabilization_window = "5m"
      scale_up_stabilization_window   = "30s"
      
      # Custom metrics for Creator Economy
      custom_metrics = [
        {
          type = "Resource"
          resource = {
            name = "cpu"
            target = {
              type                = "Utilization"
              average_utilization = 70
            }
          }
        },
        {
          type = "Pods"
          pods = {
            metric = {
              name = "active_creators_per_pod"
            }
            target = {
              type          = "AverageValue"
              average_value = "10"
            }
          }
        }
      ]
    }
    
    ai_processing = {
      min_replicas = 1
      max_replicas = 20
      target_cpu_utilization    = 60
      target_memory_utilization = 70
      scale_down_stabilization_window = "10m"
      scale_up_stabilization_window   = "60s"
      
      # AI processing specific metrics
      custom_metrics = [
        {
          type = "Pods"
          pods = {
            metric = {
              name = "processing_queue_length"
            }
            target = {
              type          = "AverageValue"
              average_value = "5"
            }
          }
        }
      ]
    }
    
    collaboration_service = {
      min_replicas = 2
      max_replicas = 30
      target_cpu_utilization    = 75
      target_memory_utilization = 85
      
      # Collaboration specific metrics
      custom_metrics = [
        {
          type = "Pods"
          pods = {
            metric = {
              name = "active_collaboration_sessions"
            }
            target = {
              type          = "AverageValue"
              average_value = "20"
            }
          }
        }
      ]
    }
    
    monetization_service = {
      min_replicas = 2
      max_replicas = 15
      target_cpu_utilization    = 70
      target_memory_utilization = 80
      
      # Payment processing metrics
      custom_metrics = [
        {
          type = "Pods"
          pods = {
            metric = {
              name = "payment_transactions_per_second"
            }
            target = {
              type          = "AverageValue"
              average_value = "10"
            }
          }
        }
      ]
    }
  }
  
  # VPA configuration
  enable_vpa = var.enable_vpa
  vpa_configs = {
    creator_platform = {
      update_mode = "Auto"
      resource_policy = {
        container_policies = [
          {
            container_name = "creator-platform"
            max_allowed = {
              cpu    = "4"
              memory = "8Gi"
            }
            min_allowed = {
              cpu    = "100m"
              memory = "128Mi"
            }
          }
        ]
      }
    }
  }
  
  # Cluster Autoscaler configuration
  cluster_autoscaler_config = {
    scale_down_delay_after_add       = "10m"
    scale_down_unneeded_time        = "10m"
    scale_down_utilization_threshold = 0.5
    skip_nodes_with_local_storage   = false
    skip_nodes_with_system_pods     = false
    
    # Creator Economy specific node pool scaling
    node_group_auto_discovery = [
      {
        name = "creator-economy"
        tags = {
          "k8s.io/cluster-autoscaler/enabled"             = "true"
          "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned"
          "k8s.io/cluster-autoscaler/node-template/label/workload-type" = "creator-economy"
        }
      },
      {
        name = "ai-processing"
        tags = {
          "k8s.io/cluster-autoscaler/enabled"             = "true"
          "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned"
          "k8s.io/cluster-autoscaler/node-template/label/workload-type" = "ai-processing"
        }
      }
    ]
  }
  
  tags = merge(local.common_tags, {
    Module = "autoscaling"
  })
}