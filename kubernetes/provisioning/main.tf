# Terraform Multi-Cloud Infrastructure Provisioning for Ainflue Platform
# Author: Fahed Mlaiel <mlaiel@live.de>
# Enterprise-grade infrastructure as code for AWS, Azure, and GCP

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
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
  }
  
  backend "s3" {
    bucket = "ainflue-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
    
    dynamodb_table = "ainflue-terraform-locks"
    encrypt        = true
  }
}

# Variables
variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ainflue"
}

variable "regions" {
  description = "List of regions for multi-region deployment"
  type = map(object({
    aws_region    = string
    azure_region  = string
    gcp_region    = string
    is_primary    = bool
  }))
  default = {
    us_east = {
      aws_region    = "us-east-1"
      azure_region  = "East US"
      gcp_region    = "us-east1"
      is_primary    = true
    }
    us_west = {
      aws_region    = "us-west-2"
      azure_region  = "West US 2"
      gcp_region    = "us-west1"
      is_primary    = false
    }
    eu_west = {
      aws_region    = "eu-west-1"
      azure_region  = "West Europe"
      gcp_region    = "europe-west1"
      is_primary    = false
    }
    ap_southeast = {
      aws_region    = "ap-southeast-1"
      azure_region  = "Southeast Asia"
      gcp_region    = "asia-southeast1"
      is_primary    = false
    }
  }
}

variable "cluster_config" {
  description = "Kubernetes cluster configuration"
  type = object({
    node_count_min = number
    node_count_max = number
    node_type      = string
    disk_size      = number
  })
  default = {
    node_count_min = 3
    node_count_max = 10
    node_type      = "m5.xlarge"
    disk_size      = 100
  }
}

# Local values
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = "fahed.mlaiel@live.de"
  }
}

# AWS Provider Configuration
provider "aws" {
  alias  = "us_east"
  region = var.regions.us_east.aws_region
  
  default_tags {
    tags = local.common_tags
  }
}

provider "aws" {
  alias  = "us_west"
  region = var.regions.us_west.aws_region
  
  default_tags {
    tags = local.common_tags
  }
}

provider "aws" {
  alias  = "eu_west"
  region = var.regions.eu_west.aws_region
  
  default_tags {
    tags = local.common_tags
  }
}

provider "aws" {
  alias  = "ap_southeast"
  region = var.regions.ap_southeast.aws_region
  
  default_tags {
    tags = local.common_tags
  }
}

# Azure Provider Configuration
provider "azurerm" {
  alias = "primary"
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

# Google Cloud Provider Configuration
provider "google" {
  alias   = "primary"
  project = "${var.project_name}-${var.environment}"
  region  = var.regions.us_east.gcp_region
}

# AWS EKS Clusters
module "aws_eks_us_east" {
  source = "./modules/aws-eks"
  providers = {
    aws = aws.us_east
  }
  
  cluster_name    = "${var.project_name}-${var.environment}-us-east-1"
  cluster_version = "1.28"
  region          = var.regions.us_east.aws_region
  
  vpc_cidr = "10.1.0.0/16"
  
  node_groups = {
    main = {
      instance_types = [var.cluster_config.node_type]
      min_size       = var.cluster_config.node_count_min
      max_size       = var.cluster_config.node_count_max
      desired_size   = var.cluster_config.node_count_min
      disk_size      = var.cluster_config.disk_size
    }
    spot = {
      instance_types = ["m5.large", "m5.xlarge", "m4.large"]
      min_size       = 0
      max_size       = 20
      desired_size   = 2
      disk_size      = var.cluster_config.disk_size
      capacity_type  = "SPOT"
    }
  }
  
  enable_irsa = true
  
  tags = merge(local.common_tags, {
    Region = "us-east-1"
    Type   = "primary"
  })
}

module "aws_eks_us_west" {
  source = "./modules/aws-eks"
  providers = {
    aws = aws.us_west
  }
  
  cluster_name    = "${var.project_name}-${var.environment}-us-west-2"
  cluster_version = "1.28"
  region          = var.regions.us_west.aws_region
  
  vpc_cidr = "10.2.0.0/16"
  
  node_groups = {
    main = {
      instance_types = [var.cluster_config.node_type]
      min_size       = var.cluster_config.node_count_min
      max_size       = var.cluster_config.node_count_max
      desired_size   = var.cluster_config.node_count_min
      disk_size      = var.cluster_config.disk_size
    }
  }
  
  enable_irsa = true
  
  tags = merge(local.common_tags, {
    Region = "us-west-2"
    Type   = "secondary"
  })
}

module "aws_eks_eu_west" {
  source = "./modules/aws-eks"
  providers = {
    aws = aws.eu_west
  }
  
  cluster_name    = "${var.project_name}-${var.environment}-eu-west-1"
  cluster_version = "1.28"
  region          = var.regions.eu_west.aws_region
  
  vpc_cidr = "10.3.0.0/16"
  
  node_groups = {
    main = {
      instance_types = [var.cluster_config.node_type]
      min_size       = var.cluster_config.node_count_min
      max_size       = var.cluster_config.node_count_max
      desired_size   = var.cluster_config.node_count_min
      disk_size      = var.cluster_config.disk_size
    }
  }
  
  enable_irsa = true
  
  tags = merge(local.common_tags, {
    Region = "eu-west-1"
    Type   = "secondary"
  })
}

module "aws_eks_ap_southeast" {
  source = "./modules/aws-eks"
  providers = {
    aws = aws.ap_southeast
  }
  
  cluster_name    = "${var.project_name}-${var.environment}-ap-southeast-1"
  cluster_version = "1.28"
  region          = var.regions.ap_southeast.aws_region
  
  vpc_cidr = "10.4.0.0/16"
  
  node_groups = {
    main = {
      instance_types = [var.cluster_config.node_type]
      min_size       = var.cluster_config.node_count_min
      max_size       = var.cluster_config.node_count_max
      desired_size   = var.cluster_config.node_count_min
      disk_size      = var.cluster_config.disk_size
    }
  }
  
  enable_irsa = true
  
  tags = merge(local.common_tags, {
    Region = "ap-southeast-1"
    Type   = "secondary"
  })
}

# RDS Databases (Primary in us-east-1, Read Replicas in other regions)
module "rds_primary" {
  source = "./modules/aws-rds"
  providers = {
    aws = aws.us_east
  }
  
  identifier = "${var.project_name}-${var.environment}-primary"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.xlarge"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true
  
  db_name  = "ainflue"
  username = "ainflue_admin"
  
  vpc_id               = module.aws_eks_us_east.vpc_id
  subnet_ids           = module.aws_eks_us_east.database_subnet_ids
  vpc_security_groups  = [module.aws_eks_us_east.database_security_group_id]
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  monitoring_interval = 60
  performance_insights_enabled = true
  
  enable_cross_region_backups = true
  
  tags = merge(local.common_tags, {
    Type = "primary-database"
  })
}

# Redis Clusters
module "redis_us_east" {
  source = "./modules/aws-elasticache"
  providers = {
    aws = aws.us_east
  }
  
  cluster_id = "${var.project_name}-${var.environment}-us-east"
  
  engine_version = "7.0"
  node_type      = "cache.r7g.large"
  num_cache_nodes = 3
  
  parameter_group_name = "default.redis7"
  port                = 6379
  
  vpc_id     = module.aws_eks_us_east.vpc_id
  subnet_ids = module.aws_eks_us_east.cache_subnet_ids
  security_groups = [module.aws_eks_us_east.cache_security_group_id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token_enabled        = true
  
  backup_retention_limit = 5
  backup_window         = "05:00-07:00"
  maintenance_window    = "sun:07:00-sun:09:00"
  
  tags = merge(local.common_tags, {
    Region = "us-east-1"
  })
}

# S3 Buckets for Content Storage
module "s3_content_storage" {
  source = "./modules/aws-s3"
  
  for_each = var.regions
  
  providers = {
    aws = aws.us_east
  }
  
  bucket_name = "${var.project_name}-content-${replace(each.key, "_", "-")}"
  
  versioning_enabled = true
  
  lifecycle_rules = [
    {
      id     = "content_lifecycle"
      status = "Enabled"
      
      transition = [
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
  
  cors_rules = [
    {
      allowed_headers = ["*"]
      allowed_methods = ["GET", "POST", "PUT", "DELETE", "HEAD"]
      allowed_origins = ["https://*.ainflue.com", "https://ainflue.com"]
      expose_headers  = ["ETag"]
      max_age_seconds = 3000
    }
  ]
  
  server_side_encryption = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = module.kms_content.key_id
      }
      bucket_key_enabled = true
    }
  }
  
  tags = merge(local.common_tags, {
    Purpose = "content-storage"
    Region  = each.value.aws_region
  })
}

# KMS Keys for Encryption
module "kms_content" {
  source = "./modules/aws-kms"
  providers = {
    aws = aws.us_east
  }
  
  key_description = "KMS key for Ainflue content encryption"
  key_usage       = "ENCRYPT_DECRYPT"
  
  key_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Ainflue Services"
        Effect = "Allow"
        Principal = {
          AWS = module.aws_eks_us_east.worker_role_arn
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
  
  tags = merge(local.common_tags, {
    Purpose = "content-encryption"
  })
}

# CloudFront Distribution for Global Content Delivery
module "cloudfront" {
  source = "./modules/aws-cloudfront"
  providers = {
    aws = aws.us_east
  }
  
  distribution_name = "${var.project_name}-${var.environment}-cdn"
  
  origins = [
    {
      domain_name = module.s3_content_storage["us_east"].bucket_domain_name
      origin_id   = "s3-us-east"
      
      s3_origin_config = {
        origin_access_identity = module.cloudfront.origin_access_identity_path
      }
    }
  ]
  
  default_cache_behavior = {
    target_origin_id       = "s3-us-east"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    
    allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods  = ["GET", "HEAD"]
    
    forwarded_values = {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]
      cookies = {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }
  
  price_class = "PriceClass_All"
  
  geo_restriction = {
    restriction_type = "none"
  }
  
  viewer_certificate = {
    acm_certificate_arn      = module.acm_certificate.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
  
  custom_error_responses = [
    {
      error_code         = 403
      response_code      = 200
      response_page_path = "/index.html"
    },
    {
      error_code         = 404
      response_code      = 200
      response_page_path = "/index.html"
    }
  ]
  
  tags = merge(local.common_tags, {
    Purpose = "global-cdn"
  })
}

# ACM Certificate for SSL/TLS
module "acm_certificate" {
  source = "./modules/aws-acm"
  providers = {
    aws = aws.us_east
  }
  
  domain_name = "*.ainflue.com"
  
  subject_alternative_names = [
    "ainflue.com",
    "api.ainflue.com",
    "www.ainflue.com",
    "cdn.ainflue.com"
  ]
  
  validation_method = "DNS"
  
  tags = merge(local.common_tags, {
    Purpose = "ssl-certificate"
  })
}

# Route53 DNS
module "route53" {
  source = "./modules/aws-route53"
  providers = {
    aws = aws.us_east
  }
  
  domain_name = "ainflue.com"
  
  records = [
    {
      name    = ""
      type    = "A"
      alias = {
        name                   = module.cloudfront.domain_name
        zone_id                = module.cloudfront.hosted_zone_id
        evaluate_target_health = false
      }
    },
    {
      name    = "www"
      type    = "A"
      alias = {
        name                   = module.cloudfront.domain_name
        zone_id                = module.cloudfront.hosted_zone_id
        evaluate_target_health = false
      }
    },
    {
      name    = "api"
      type    = "A"
      alias = {
        name                   = module.aws_eks_us_east.load_balancer_dns
        zone_id                = module.aws_eks_us_east.load_balancer_zone_id
        evaluate_target_health = true
      }
    }
  ]
  
  health_checks = [
    {
      fqdn                            = "api.ainflue.com"
      port                            = 443
      type                            = "HTTPS"
      resource_path                   = "/health"
      failure_threshold               = 3
      request_interval                = 30
      cloudwatch_alarm_region         = "us-east-1"
      cloudwatch_alarm_name           = "api-health-check"
      insufficient_data_health_status = "Failure"
    }
  ]
  
  tags = merge(local.common_tags, {
    Purpose = "dns-management"
  })
}

# Data sources
data "aws_caller_identity" "current" {
  provider = aws.us_east
}

data "aws_availability_zones" "available" {
  provider = aws.us_east
  state    = "available"
}

# Outputs
output "cluster_endpoints" {
  description = "Kubernetes cluster endpoints"
  value = {
    us_east      = module.aws_eks_us_east.cluster_endpoint
    us_west      = module.aws_eks_us_west.cluster_endpoint
    eu_west      = module.aws_eks_eu_west.cluster_endpoint
    ap_southeast = module.aws_eks_ap_southeast.cluster_endpoint
  }
  sensitive = true
}

output "database_endpoints" {
  description = "Database endpoints"
  value = {
    primary = module.rds_primary.endpoint
  }
  sensitive = true
}

output "redis_endpoints" {
  description = "Redis cluster endpoints"
  value = {
    us_east = module.redis_us_east.endpoint
  }
  sensitive = true
}

output "cloudfront_distribution" {
  description = "CloudFront distribution details"
  value = {
    domain_name = module.cloudfront.domain_name
    distribution_id = module.cloudfront.distribution_id
  }
}

output "certificate_arn" {
  description = "ACM certificate ARN"
  value = module.acm_certificate.certificate_arn
}

output "s3_buckets" {
  description = "S3 bucket details"
  value = {
    for region, bucket in module.s3_content_storage : region => {
      bucket_name   = bucket.bucket_name
      bucket_arn    = bucket.bucket_arn
      domain_name   = bucket.bucket_domain_name
    }
  }
}