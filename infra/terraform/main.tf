# Ainflue Infrastructure - Terraform Configuration
# ================================================
# 
# Complete infrastructure deployment for Ainflue platform
# Supports multi-cloud, scalable, and production-ready setup
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  backend "s3" {
    # Configure with your own S3 bucket for state storage
    bucket         = "ainflue-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "ainflue-terraform-locks"
  }
}

# Variables
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ainflue"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "gcp_project" {
  description = "Google Cloud project ID"
  type        = string
  default     = ""
}

variable "gcp_region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-west2"
}

variable "azure_location" {
  description = "Azure location"
  type        = string
  default     = "West US 2"
}

variable "kubernetes_cluster_size" {
  description = "Kubernetes cluster node count"
  type        = number
  default     = 3
}

variable "database_instance_class" {
  description = "Database instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "enable_monitoring" {
  description = "Enable monitoring stack"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "ainflue.com"
}

# Local values
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    CreatedAt   = timestamp()
  }
  
  resource_prefix = "${var.project_name}-${var.environment}"
}

# Random password for databases
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Random secret key
resource "random_password" "secret_key" {
  length  = 64
  special = true
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = local.common_tags
  }
}

# Google Cloud Provider Configuration
provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

# Azure Provider Configuration
provider "azurerm" {
  features {}
}

# =============================================================================
# NETWORKING
# =============================================================================

# AWS VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-vpc"
  })
}

# AWS Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-igw"
  })
}

# AWS Public Subnets
resource "aws_subnet" "public" {
  count = 3
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-public-subnet-${count.index + 1}"
    Type = "public"
  })
}

# AWS Private Subnets
resource "aws_subnet" "private" {
  count = 3
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-private-subnet-${count.index + 1}"
    Type = "private"
  })
}

# AWS NAT Gateways
resource "aws_eip" "nat" {
  count = 3
  
  domain = "vpc"
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-nat-eip-${count.index + 1}"
  })
}

resource "aws_nat_gateway" "main" {
  count = 3
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-nat-${count.index + 1}"
  })
  
  depends_on = [aws_internet_gateway.main]
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-public-rt"
  })
}

resource "aws_route_table" "private" {
  count = 3
  
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-private-rt-${count.index + 1}"
  })
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count = 3
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = 3
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# =============================================================================
# SECURITY GROUPS
# =============================================================================

# EKS Cluster Security Group
resource "aws_security_group" "eks_cluster" {
  name_prefix = "${local.resource_prefix}-eks-cluster"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-eks-cluster-sg"
  })
}

# EKS Node Group Security Group
resource "aws_security_group" "eks_nodes" {
  name_prefix = "${local.resource_prefix}-eks-nodes"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description = "Node to node communication"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }
  
  ingress {
    description     = "Cluster to node communication"
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-eks-nodes-sg"
  })
}

# Database Security Group
resource "aws_security_group" "database" {
  name_prefix = "${local.resource_prefix}-database"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description     = "PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }
  
  ingress {
    description     = "Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-database-sg"
  })
}

# =============================================================================
# EKS CLUSTER
# =============================================================================

# EKS Cluster IAM Role
resource "aws_iam_role" "eks_cluster" {
  name = "${local.resource_prefix}-eks-cluster-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "${local.resource_prefix}-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.27"
  
  vpc_config {
    subnet_ids              = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
    security_group_ids      = [aws_security_group.eks_cluster.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }
  
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
  ]
  
  tags = local.common_tags
}

# EKS Node Group IAM Role
resource "aws_iam_role" "eks_nodes" {
  name = "${local.resource_prefix}-eks-nodes-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_nodes.name
}

# EKS Node Group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${local.resource_prefix}-nodes"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = aws_subnet.private[*].id
  
  instance_types = ["t3.medium"]
  capacity_type  = "ON_DEMAND"
  
  scaling_config {
    desired_size = var.kubernetes_cluster_size
    max_size     = var.kubernetes_cluster_size * 2
    min_size     = 1
  }
  
  update_config {
    max_unavailable = 1
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]
  
  tags = local.common_tags
}

# =============================================================================
# RDS DATABASES
# =============================================================================

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${local.resource_prefix}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-db-subnet-group"
  })
}

# PostgreSQL Database
resource "aws_db_instance" "postgresql" {
  identifier = "${local.resource_prefix}-postgresql"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.database_instance_class
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "ainflue"
  username = "ainflue_admin"
  password = random_password.db_password.result
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = var.enable_backup ? 7 : 0
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = var.environment != "prod"
  deletion_protection = var.environment == "prod"
  
  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-postgresql"
  })
}

# =============================================================================
# ELASTICACHE REDIS
# =============================================================================

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${local.resource_prefix}-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

# Redis Cluster
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id         = "${local.resource_prefix}-redis"
  description                  = "Redis cluster for ${var.project_name}"
  
  node_type                    = "cache.t3.micro"
  port                         = 6379
  parameter_group_name         = "default.redis7"
  
  num_cache_clusters           = 2
  automatic_failover_enabled   = true
  multi_az_enabled            = true
  
  subnet_group_name           = aws_elasticache_subnet_group.main.name
  security_group_ids          = [aws_security_group.database.id]
  
  at_rest_encryption_enabled  = true
  transit_encryption_enabled  = true
  
  tags = local.common_tags
}

# =============================================================================
# S3 BUCKETS
# =============================================================================

# S3 Bucket for application data
resource "aws_s3_bucket" "app_data" {
  bucket = "${local.resource_prefix}-app-data"
  
  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# S3 Bucket for media files
resource "aws_s3_bucket" "media" {
  bucket = "${local.resource_prefix}-media"
  
  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "media" {
  bucket = aws_s3_bucket.media.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "media" {
  bucket = aws_s3_bucket.media.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# CloudFront Distribution for media
resource "aws_cloudfront_distribution" "media" {
  origin {
    domain_name = aws_s3_bucket.media.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.media.bucket}"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.media.cloudfront_access_identity_path
    }
  }
  
  enabled = true
  
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.media.bucket}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }
  
  price_class = "PriceClass_100"
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  
  tags = local.common_tags
}

resource "aws_cloudfront_origin_access_identity" "media" {
  comment = "OAI for ${local.resource_prefix} media bucket"
}

# =============================================================================
# SECRETS MANAGER
# =============================================================================

# Database credentials
resource "aws_secretsmanager_secret" "database_credentials" {
  name = "${local.resource_prefix}-database-credentials"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "database_credentials" {
  secret_id = aws_secretsmanager_secret.database_credentials.id
  secret_string = jsonencode({
    postgresql_host     = aws_db_instance.postgresql.endpoint
    postgresql_port     = aws_db_instance.postgresql.port
    postgresql_database = aws_db_instance.postgresql.db_name
    postgresql_username = aws_db_instance.postgresql.username
    postgresql_password = random_password.db_password.result
    redis_host          = aws_elasticache_replication_group.redis.primary_endpoint_address
    redis_port          = aws_elasticache_replication_group.redis.port
  })
}

# Application secrets
resource "aws_secretsmanager_secret" "app_secrets" {
  name = "${local.resource_prefix}-app-secrets"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    secret_key = random_password.secret_key.result
    # Add more application secrets here
    jwt_secret_key          = random_password.secret_key.result
    openai_api_key          = ""  # To be set manually
    elevenlabs_api_key      = ""  # To be set manually
    stripe_secret_key       = ""  # To be set manually
    stripe_publishable_key  = ""  # To be set manually
    shopify_api_key         = ""  # To be set manually
    midjourney_api_token    = ""  # To be set manually
  })
}

# =============================================================================
# DATA SOURCES
# =============================================================================

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# =============================================================================
# KUBERNETES PROVIDER SETUP
# =============================================================================

data "aws_eks_cluster" "main" {
  name = aws_eks_cluster.main.name
}

data "aws_eks_cluster_auth" "main" {
  name = aws_eks_cluster.main.name
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.main.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.main.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.main.token
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.main.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.main.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.main.token
  }
}

# =============================================================================
# OUTPUTS
# =============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "database_endpoint" {
  description = "PostgreSQL database endpoint"
  value       = aws_db_instance.postgresql.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
  sensitive   = true
}

output "s3_app_data_bucket" {
  description = "S3 bucket for application data"
  value       = aws_s3_bucket.app_data.bucket
}

output "s3_media_bucket" {
  description = "S3 bucket for media files"
  value       = aws_s3_bucket.media.bucket
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain"
  value       = aws_cloudfront_distribution.media.domain_name
}

output "secrets_manager_database_arn" {
  description = "ARN of database credentials secret"
  value       = aws_secretsmanager_secret.database_credentials.arn
}

output "secrets_manager_app_arn" {
  description = "ARN of application secrets"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "kubeconfig_command" {
  description = "Command to update kubeconfig"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.main.name}"
}