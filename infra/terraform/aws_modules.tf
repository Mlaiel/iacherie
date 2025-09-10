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

# AWS Cloud Provider Modules
module "vpc" {
  source = "./modules/vpc"
  
  name               = "${var.project_name}-${var.environment}"
  cidr_block         = var.vpc_cidr
  availability_zones = var.availability_zones
  
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true
  
  tags = var.common_tags
}

module "eks_cluster" {
  source = "./modules/eks"
  
  cluster_name    = "${var.project_name}-${var.environment}"
  cluster_version = var.k8s_version
  
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  
  node_groups = var.node_groups
  
  enable_irsa = true
  enable_logging = true
  
  tags = var.common_tags
  
  depends_on = [module.vpc]
}

module "rds_postgres" {
  source = "./modules/rds"
  
  identifier = "${var.project_name}-${var.environment}-db"
  
  engine         = "postgres"
  engine_version = var.rds_configuration.engine_version
  instance_class = var.rds_configuration.instance_class
  
  allocated_storage     = var.rds_configuration.allocated_storage
  max_allocated_storage = var.rds_configuration.allocated_storage * 2
  
  db_name  = "${var.project_name}_${var.environment}"
  username = "postgres"
  
  vpc_security_group_ids = [module.security_groups.rds_sg_id]
  db_subnet_group_name   = module.vpc.db_subnet_group_name
  
  backup_retention_period = var.rds_configuration.backup_retention
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  multi_az               = var.rds_configuration.multi_az
  publicly_accessible    = false
  storage_encrypted      = true
  
  deletion_protection = var.environment == "prod"
  skip_final_snapshot = var.environment != "prod"
  
  tags = var.common_tags
  
  depends_on = [module.vpc]
}

module "elasticache_redis" {
  source = "./modules/elasticache"
  
  cluster_id = "${var.project_name}-${var.environment}-redis"
  
  node_type       = var.redis_configuration.node_type
  num_cache_nodes = var.redis_configuration.num_cache_nodes
  parameter_group = var.redis_configuration.parameter_group
  engine_version  = var.redis_configuration.engine_version
  
  subnet_group_name  = module.vpc.elasticache_subnet_group_name
  security_group_ids = [module.security_groups.elasticache_sg_id]
  
  tags = var.common_tags
  
  depends_on = [module.vpc]
}

module "s3_buckets" {
  source = "./modules/s3"
  
  project_name = var.project_name
  environment  = var.environment
  
  versioning_enabled = var.s3_configuration.versioning_enabled
  encryption_enabled = var.s3_configuration.encryption_enabled
  lifecycle_enabled  = var.s3_configuration.lifecycle_enabled
  backup_enabled     = var.s3_configuration.backup_enabled
  
  tags = var.common_tags
}

module "cloudfront" {
  source = "./modules/cloudfront"
  
  s3_bucket_domain = module.s3_buckets.content_bucket_domain
  
  price_class = "PriceClass_100"
  
  tags = var.common_tags
  
  depends_on = [module.s3_buckets]
}

module "security_groups" {
  source = "./modules/security_groups"
  
  vpc_id = module.vpc.vpc_id
  
  project_name = var.project_name
  environment  = var.environment
  
  vpc_cidr = var.vpc_cidr
  
  tags = var.common_tags
  
  depends_on = [module.vpc]
}

module "iam_roles" {
  source = "./modules/iam"
  
  project_name = var.project_name
  environment  = var.environment
  
  oidc_provider_arn = module.eks_cluster.oidc_provider_arn
  
  tags = var.common_tags
}

module "load_balancer" {
  source = "./modules/alb"
  
  name = "${var.project_name}-${var.environment}-alb"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnet_ids
  
  security_group_ids = [module.security_groups.alb_sg_id]
  
  enable_deletion_protection = var.environment == "prod"
  
  tags = var.common_tags
  
  depends_on = [module.vpc, module.security_groups]
}

# Conditional Azure Resources
module "azure_infrastructure" {
  source = "./modules/azure"
  count  = contains(var.cloud_providers, "azure") ? 1 : 0
  
  project_name = var.project_name
  environment  = var.environment
  location     = var.azure_location
  
  tags = var.common_tags
}

# Conditional GCP Resources  
module "gcp_infrastructure" {
  source = "./modules/gcp"
  count  = contains(var.cloud_providers, "gcp") ? 1 : 0
  
  project_name = var.project_name
  environment  = var.environment
  region       = var.gcp_region
  
  labels = var.common_tags
}

# Monitoring Infrastructure
module "monitoring" {
  source = "./modules/monitoring"
  
  project_name = var.project_name
  environment  = var.environment
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  
  enable_prometheus = var.monitoring_configuration.enable_prometheus
  enable_grafana   = var.monitoring_configuration.enable_grafana
  enable_jaeger    = var.monitoring_configuration.enable_jaeger
  
  retention_days = var.monitoring_configuration.retention_days
  
  tags = var.common_tags
  
  depends_on = [module.vpc, module.eks_cluster]
}