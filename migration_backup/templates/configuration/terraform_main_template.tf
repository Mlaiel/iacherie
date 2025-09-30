# Terraform Main Configuration - Ainflue Creator Economy Platform
# ================================================================
#
# 🎯 DEVOPS ENGINEER + CLOUD ARCHITECT + INFRASTRUCTURE EXPERT
# Lead: Fahed Mlaiel (mlaiel@live.de)
#
# Enterprise Infrastructure as Code for Creator Economy Platform
# - Multi-cloud deployment capabilities (AWS, GCP, Azure)
# - High availability and auto-scaling
# - Security-first architecture
# - Creator Economy specific optimizations
# - AI processing infrastructure
# - Content delivery and storage
# - Monitoring and observability
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

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    bucket         = "ainflue-terraform-state-${var.environment}"
    key            = "infrastructure/terraform.tfstate"
    region         = var.aws_region
    encrypt        = true
    dynamodb_table = "ainflue-terraform-locks"
    
    # State locking for team collaboration
    workspace_key_prefix = "workspaces"
  }
}

# Provider Configuration
provider "aws" {
  region = var.aws_region
  
  # Assume role for cross-account access
  assume_role {
    role_arn = var.aws_assume_role_arn
  }
  
  default_tags {
    tags = {
      Project         = "Ainflue"
      Environment     = var.environment
      Owner           = "Fahed Mlaiel"
      ManagedBy       = "Terraform"
      CreatedDate     = formatdate("YYYY-MM-DD", timestamp())
      BusinessUnit    = "CreatorEconomy"
      CostCenter      = "Infrastructure"
      SecurityLevel   = "Enterprise"
      ComplianceRequired = "true"
      DataProtection  = "GDPR"
      IPProtection    = "Enabled"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks", "get-token",
      "--cluster-name", module.eks.cluster_name,
      "--region", var.aws_region
    ]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks", "get-token",
        "--cluster-name", module.eks.cluster_name,
        "--region", var.aws_region
      ]
    }
  }
}

# Data Sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# Random password for databases
resource "random_password" "database_passwords" {
  for_each = toset(["postgresql", "mysql", "redis"])
  
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# Local Values
locals {
  cluster_name = "ainflue-${var.environment}"
  region      = var.aws_region
  
  # Ainflue Creator Economy specific configuration
  creator_economy_config = {
    content_types = [
      "video",
      "audio", 
      "images",
      "documents",
      "interactive",
      "live_streaming"
    ]
    
    # AI processing requirements
    ai_processing = {
      gpu_enabled = var.enable_gpu_nodes
      ml_frameworks = [
        "tensorflow",
        "pytorch", 
        "transformers",
        "opencv",
        "ffmpeg"
      ]
    }
    
    # Monetization features
    monetization = {
      payment_providers = [
        "stripe",
        "paypal",
        "square",
        "blockchain"
      ]
      revenue_sharing = true
      subscription_management = true
    }
    
    # Collaboration features
    collaboration = {
      real_time_editing = true
      version_control = true
      comment_system = true
      approval_workflow = true
    }
  }
  
  # Network configuration
  vpc_cidr = var.vpc_cidr
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 3)
  
  private_subnets = [
    for i, az in local.availability_zones :
    cidrsubnet(local.vpc_cidr, 8, i + 10)
  ]
  
  public_subnets = [
    for i, az in local.availability_zones :
    cidrsubnet(local.vpc_cidr, 8, i + 100)
  ]
  
  database_subnets = [
    for i, az in local.availability_zones :
    cidrsubnet(local.vpc_cidr, 8, i + 200)
  ]
  
  # Common tags
  common_tags = merge(
    var.common_tags,
    {
      CreatorEconomyEnabled = "true"
      MultiFormatSupport    = "true"
      AIProcessingEnabled   = "true"
      MonetizationSupport   = "true"
      CollaborationEnabled  = "true"
      SEOOptimized         = "true"
      DistributionReady    = "true"
    }
  )
}

# VPC Module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  
  name = "${local.cluster_name}-vpc"
  cidr = local.vpc_cidr
  
  azs             = local.availability_zones
  private_subnets = local.private_subnets
  public_subnets  = local.public_subnets
  database_subnets = local.database_subnets
  
  # NAT Gateway configuration
  enable_nat_gateway   = true
  single_nat_gateway   = var.environment == "development" ? true : false
  enable_vpn_gateway   = var.enable_vpn_gateway
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  # VPC Flow Logs for security monitoring
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true
  flow_log_max_aggregation_interval    = 60
  
  # Database subnet group
  create_database_subnet_group = true
  
  # Internet Gateway
  create_igw = true
  
  # Enable DHCP options
  enable_dhcp_options = true
  dhcp_options_domain_name = "${var.environment}.ainflue.local"
  dhcp_options_domain_name_servers = ["AmazonProvidedDNS"]
  
  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-vpc"
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
  })
  
  public_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                      = "1"
    SubnetType = "Public"
  }
  
  private_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"             = "1"
    SubnetType = "Private"
  }
  
  database_subnet_tags = {
    SubnetType = "Database"
  }
}

# EKS Cluster Module
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"
  
  cluster_name    = local.cluster_name
  cluster_version = var.kubernetes_version
  
  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = var.cluster_endpoint_public_access
  
  # OIDC Identity provider
  cluster_identity_providers = {
    sts = {
      client_id = "sts.amazonaws.com"
    }
  }
  
  # Cluster encryption
  cluster_encryption_config = {
    provider_key_arn = aws_kms_key.eks.arn
    resources        = ["secrets"]
  }
  
  # CloudWatch Logging
  cluster_enabled_log_types = [
    "api",
    "audit", 
    "authenticator",
    "controllerManager",
    "scheduler"
  ]
  
  # EKS Managed Node Groups
  eks_managed_node_groups = {
    # Creator Economy workloads
    creator_economy = {
      name           = "creator-economy"
      instance_types = var.creator_economy_instance_types
      ami_type       = "AL2_x86_64"
      
      min_size     = var.creator_economy_nodes_min
      max_size     = var.creator_economy_nodes_max
      desired_size = var.creator_economy_nodes_desired
      
      # Enable spot instances for cost optimization
      capacity_type = var.environment == "production" ? "ON_DEMAND" : "SPOT"
      
      # Taints for workload isolation
      taints = {
        creator_economy = {
          key    = "workload-type"
          value  = "creator-economy"
          effect = "NO_SCHEDULE"
        }
      }
      
      labels = {
        WorkloadType = "creator-economy"
        Environment  = var.environment
        NodeGroup    = "creator-economy"
      }
      
      # User data for node customization
      pre_bootstrap_user_data = <<-EOT
        #!/bin/bash
        # Install additional packages for creator workloads
        yum update -y
        yum install -y docker htop nvme-cli
        
        # Configure Docker for creator content processing
        mkdir -p /etc/docker
        cat > /etc/docker/daemon.json <<EOF
        {
          "log-driver": "json-file",
          "log-opts": {
            "max-size": "100m",
            "max-file": "5"
          },
          "storage-driver": "overlay2"
        }
        EOF
      EOT
    }
    
    # AI Processing workloads
    ai_processing = {
      name           = "ai-processing"
      instance_types = var.ai_processing_instance_types
      ami_type       = var.enable_gpu_nodes ? "AL2_x86_64_GPU" : "AL2_x86_64"
      
      min_size     = var.ai_processing_nodes_min
      max_size     = var.ai_processing_nodes_max
      desired_size = var.ai_processing_nodes_desired
      
      capacity_type = "ON_DEMAND" # AI workloads need guaranteed capacity
      
      taints = {
        ai_processing = {
          key    = "workload-type"
          value  = "ai-processing"
          effect = "NO_SCHEDULE"
        }
      }
      
      labels = {
        WorkloadType = "ai-processing"
        Environment  = var.environment
        NodeGroup    = "ai-processing"
        GPUEnabled   = var.enable_gpu_nodes ? "true" : "false"
      }
      
      # GPU and AI-specific user data
      pre_bootstrap_user_data = var.enable_gpu_nodes ? <<-EOT
        #!/bin/bash
        # Install NVIDIA drivers and Docker GPU support
        yum update -y
        yum install -y gcc kernel-devel-$(uname -r)
        
        # Install NVIDIA drivers
        aws s3 cp --recursive s3://ec2-linux-nvidia-drivers/latest/ .
        chmod +x NVIDIA-Linux-x86_64*.run
        ./NVIDIA-Linux-x86_64*.run --silent
        
        # Install nvidia-docker2
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
        curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | tee /etc/yum.repos.d/nvidia-docker.repo
        yum install -y nvidia-docker2
        systemctl restart docker
      EOT : <<-EOT
        #!/bin/bash
        yum update -y
        yum install -y htop nvme-cli python3-pip
        pip3 install --upgrade awscli
      EOT
    }
    
    # System workloads (monitoring, logging, etc.)
    system = {
      name           = "system"
      instance_types = var.system_instance_types
      ami_type       = "AL2_x86_64"
      
      min_size     = var.system_nodes_min
      max_size     = var.system_nodes_max
      desired_size = var.system_nodes_desired
      
      capacity_type = "ON_DEMAND"
      
      labels = {
        WorkloadType = "system"
        Environment  = var.environment
        NodeGroup    = "system"
      }
    }
  }
  
  # Cluster security group rules
  cluster_security_group_additional_rules = {
    ingress_nodes_ephemeral_ports_tcp = {
      description                = "Node groups to cluster API"
      protocol                   = "tcp"
      from_port                  = 1025
      to_port                    = 65535
      type                       = "ingress"
      source_node_security_group = true
    }
  }
  
  # Node security group rules
  node_security_group_additional_rules = {
    ingress_cluster_to_node_all_traffic = {
      description                   = "Cluster API to node groups"
      protocol                      = "-1"
      from_port                     = 0
      to_port                       = 0
      type                          = "ingress"
      source_cluster_security_group = true
    }
    
    ingress_self_all = {
      description = "Node to node all traffic"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }
    
    egress_all = {
      description      = "Node all egress"
      protocol         = "-1"
      from_port        = 0
      to_port          = 0
      type             = "egress"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
  }
  
  tags = local.common_tags
}

# KMS Key for EKS encryption
resource "aws_kms_key" "eks" {
  description = "EKS Secret Encryption Key for ${local.cluster_name}"
  
  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-eks-encryption-key"
  })
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${local.cluster_name}-eks"
  target_key_id = aws_kms_key.eks.key_id
}

# Security Infrastructure
module "security" {
  source = "./modules/security"
  
  cluster_name = local.cluster_name
  vpc_id       = module.vpc.vpc_id
  environment  = var.environment
  
  # IP Protection and Content Security
  enable_waf              = var.enable_waf
  enable_shield_advanced  = var.enable_shield_advanced
  enable_secrets_manager  = true
  enable_certificate_manager = true
  
  # Creator Economy security features
  enable_content_protection = true
  enable_ip_protection     = true
  enable_drm               = var.enable_drm
  
  tags = local.common_tags
}

# RDS Database Infrastructure
module "database" {
  source = "./modules/database"
  
  cluster_name = local.cluster_name
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.database_subnets
  environment  = var.environment
  
  # Creator Economy databases
  databases = {
    # Main application database
    postgresql = {
      engine         = "postgres"
      engine_version = "15.4"
      instance_class = var.database_instance_class
      allocated_storage = var.database_allocated_storage
      
      database_name = "ainflue_${var.environment}"
      username      = "ainflue_admin"
      password      = random_password.database_passwords["postgresql"].result
      
      backup_retention_period = var.backup_retention_period
      backup_window          = "03:00-04:00"
      maintenance_window     = "sun:04:00-sun:05:00"
      
      multi_az               = var.environment == "production"
      publicly_accessible    = false
      
      # Performance Insights
      performance_insights_enabled = true
      performance_insights_retention_period = 7
      
      # Enhanced monitoring
      monitoring_interval = 60
      monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn
      
      tags = merge(local.common_tags, {
        DatabaseType = "PostgreSQL"
        Purpose      = "MainApplication"
      })
    }
    
    # Analytics database
    mysql = {
      engine         = "mysql"
      engine_version = "8.0.35"
      instance_class = var.analytics_database_instance_class
      allocated_storage = var.analytics_database_allocated_storage
      
      database_name = "ainflue_analytics_${var.environment}"
      username      = "analytics_admin"
      password      = random_password.database_passwords["mysql"].result
      
      backup_retention_period = var.backup_retention_period
      backup_window          = "02:00-03:00"
      maintenance_window     = "sun:03:00-sun:04:00"
      
      multi_az               = var.environment == "production"
      publicly_accessible    = false
      
      tags = merge(local.common_tags, {
        DatabaseType = "MySQL"
        Purpose      = "Analytics"
      })
    }
  }
  
  # ElastiCache for Redis
  enable_elasticache = true
  elasticache_config = {
    node_type = var.redis_node_type
    num_cache_nodes = var.redis_num_nodes
    parameter_group_name = "default.redis7"
    engine_version = "7.0"
    port = 6379
    
    # High availability
    automatic_failover_enabled = var.environment == "production"
    multi_az_enabled          = var.environment == "production"
    
    tags = merge(local.common_tags, {
      CacheType = "Redis"
      Purpose   = "SessionStore"
    })
  }
  
  tags = local.common_tags
}

# Enhanced monitoring IAM role
resource "aws_iam_role" "rds_enhanced_monitoring" {
  name = "${local.cluster_name}-rds-enhanced-monitoring"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Content Delivery Network
module "cdn" {
  source = "./modules/cdn"
  
  cluster_name = local.cluster_name
  environment  = var.environment
  
  # Creator content distribution
  enable_cloudfront = true
  enable_s3_buckets = true
  
  # Multi-format content support
  content_buckets = {
    # Video content
    video = {
      bucket_name = "${local.cluster_name}-video-content"
      versioning  = true
      encryption  = true
      lifecycle_rules = [
        {
          id     = "video_lifecycle"
          status = "Enabled"
          transitions = [
            {
              days          = 30
              storage_class = "STANDARD_IA"
            },
            {
              days          = 90
              storage_class = "GLACIER"
            },
            {
              days          = 365
              storage_class = "DEEP_ARCHIVE"
            }
          ]
        }
      ]
    }
    
    # Audio content
    audio = {
      bucket_name = "${local.cluster_name}-audio-content"
      versioning  = true
      encryption  = true
      lifecycle_rules = [
        {
          id     = "audio_lifecycle"
          status = "Enabled"
          transitions = [
            {
              days          = 30
              storage_class = "STANDARD_IA"
            },
            {
              days          = 180
              storage_class = "GLACIER"
            }
          ]
        }
      ]
    }
    
    # Image content
    images = {
      bucket_name = "${local.cluster_name}-image-content"
      versioning  = true
      encryption  = true
      lifecycle_rules = [
        {
          id     = "image_lifecycle"
          status = "Enabled"
          transitions = [
            {
              days          = 90
              storage_class = "STANDARD_IA"
            }
          ]
        }
      ]
    }
    
    # Document content
    documents = {
      bucket_name = "${local.cluster_name}-document-content"
      versioning  = true
      encryption  = true
    }
  }
  
  # CloudFront distribution configuration
  cloudfront_config = {
    price_class = var.cloudfront_price_class
    
    # Geographic restrictions
    geo_restriction = {
      restriction_type = "none"
    }
    
    # Custom domain
    aliases = var.cloudfront_aliases
    
    # SSL certificate
    acm_certificate_arn = var.ssl_certificate_arn
    
    # Cache behaviors for different content types
    cache_behaviors = [
      {
        path_pattern     = "/api/*"
        compress         = true
        viewer_protocol_policy = "redirect-to-https"
        cache_policy_id  = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad" # CachingDisabled
      },
      {
        path_pattern     = "/static/*"
        compress         = true
        viewer_protocol_policy = "redirect-to-https"
        cache_policy_id  = "658327ea-f89d-4fab-a63d-7e88639e58f6" # CachingOptimized
      }
    ]
  }
  
  tags = local.common_tags
}

# Monitoring and Observability
module "monitoring" {
  source = "./modules/monitoring"
  
  cluster_name = local.cluster_name
  environment  = var.environment
  
  # Creator Economy specific monitoring
  enable_business_metrics    = true
  enable_creator_analytics   = true
  enable_revenue_tracking    = true
  enable_content_analytics   = true
  enable_collaboration_metrics = true
  
  # Technical monitoring
  enable_prometheus = true
  enable_grafana   = true
  enable_jaeger    = true
  enable_elk_stack = var.enable_elk_stack
  enable_x_ray     = true
  
  # Alerting configuration
  alert_channels = var.alert_channels
  
  # Log retention
  log_retention_days = var.log_retention_days
  
  tags = local.common_tags
}

# Auto Scaling Infrastructure
module "autoscaling" {
  source = "./modules/autoscaling"
  
  cluster_name = local.cluster_name
  environment  = var.environment
  
  # Horizontal Pod Autoscaler (HPA) configurations
  hpa_configs = {
    creator_platform = {
      min_replicas = 2
      max_replicas = 20
      target_cpu_utilization = 70
      target_memory_utilization = 80
    }
    
    ai_processing = {
      min_replicas = 1
      max_replicas = 10
      target_cpu_utilization = 60
      target_memory_utilization = 70
      scale_down_stabilization_window = "5m"
      scale_up_stabilization_window   = "30s"
    }
    
    api_gateway = {
      min_replicas = 3
      max_replicas = 50
      target_cpu_utilization = 75
      target_memory_utilization = 85
    }
  }
  
  # Vertical Pod Autoscaler (VPA) configurations
  enable_vpa = var.enable_vpa
  
  # Cluster Autoscaler configuration
  cluster_autoscaler_config = {
    scale_down_delay_after_add    = "10m"
    scale_down_unneeded_time      = "10m"
    scale_down_utilization_threshold = 0.5
    skip_nodes_with_local_storage = false
    skip_nodes_with_system_pods   = false
  }
  
  tags = local.common_tags
}