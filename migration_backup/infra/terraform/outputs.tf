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
# TERRAFORM OUTPUTS - MULTI-CLOUD INFRASTRUCTURE
# =============================================================================

# -----------------------------------------------------------------------------
# Network Outputs
# -----------------------------------------------------------------------------

output "vpc_id" {
  description = "ID of the VPC"
  value       = try(aws_vpc.main[0].id, null)
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = try(aws_vpc.main[0].cidr_block, null)
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = try(aws_subnet.private[*].id, [])
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = try(aws_subnet.public[*].id, [])
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = try(aws_internet_gateway.main[0].id, null)
}

output "nat_gateway_ids" {
  description = "IDs of the NAT Gateways"
  value       = try(aws_nat_gateway.main[*].id, [])
}

# -----------------------------------------------------------------------------
# Kubernetes Outputs
# -----------------------------------------------------------------------------

output "eks_cluster_id" {
  description = "EKS cluster ID"
  value       = try(aws_eks_cluster.main[0].id, null)
}

output "eks_cluster_arn" {
  description = "EKS cluster ARN"
  value       = try(aws_eks_cluster.main[0].arn, null)
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = try(aws_eks_cluster.main[0].endpoint, null)
  sensitive   = true
}

output "eks_cluster_version" {
  description = "EKS cluster Kubernetes version"
  value       = try(aws_eks_cluster.main[0].version, null)
}

output "eks_cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = try(aws_eks_cluster.main[0].vpc_config[0].cluster_security_group_id, null)
}

output "eks_node_group_arns" {
  description = "EKS node group ARNs"
  value       = try([for ng in aws_eks_node_group.main : ng.arn], [])
}

# -----------------------------------------------------------------------------
# Database Outputs
# -----------------------------------------------------------------------------

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = try(aws_db_instance.main[0].endpoint, null)
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = try(aws_db_instance.main[0].port, null)
}

output "rds_database_name" {
  description = "RDS database name"
  value       = try(aws_db_instance.main[0].db_name, null)
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = try(aws_elasticache_cluster.main[0].cache_nodes[0].address, null)
  sensitive   = true
}

output "redis_port" {
  description = "Redis cluster port"
  value       = try(aws_elasticache_cluster.main[0].cache_nodes[0].port, null)
}

# -----------------------------------------------------------------------------
# Storage Outputs
# -----------------------------------------------------------------------------

output "s3_bucket_names" {
  description = "Names of created S3 buckets"
  value = {
    content = try(aws_s3_bucket.content[0].id, null)
    media   = try(aws_s3_bucket.media[0].id, null)
    backup  = try(aws_s3_bucket.backup[0].id, null)
  }
}

output "s3_bucket_arns" {
  description = "ARNs of created S3 buckets"
  value = {
    content = try(aws_s3_bucket.content[0].arn, null)
    media   = try(aws_s3_bucket.media[0].arn, null)
    backup  = try(aws_s3_bucket.backup[0].arn, null)
  }
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = try(aws_cloudfront_distribution.main[0].id, null)
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = try(aws_cloudfront_distribution.main[0].domain_name, null)
}

# -----------------------------------------------------------------------------
# Load Balancer Outputs
# -----------------------------------------------------------------------------

output "alb_arn" {
  description = "Application Load Balancer ARN"
  value       = try(aws_lb.main[0].arn, null)
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = try(aws_lb.main[0].dns_name, null)
}

output "alb_zone_id" {
  description = "Application Load Balancer hosted zone ID"
  value       = try(aws_lb.main[0].zone_id, null)
}

# -----------------------------------------------------------------------------
# Security Outputs
# -----------------------------------------------------------------------------

output "kms_key_id" {
  description = "KMS key ID for encryption"
  value       = try(aws_kms_key.main[0].key_id, null)
}

output "kms_key_arn" {
  description = "KMS key ARN for encryption"
  value       = try(aws_kms_key.main[0].arn, null)
}

output "waf_web_acl_id" {
  description = "WAF web ACL ID"
  value       = try(aws_wafv2_web_acl.main[0].id, null)
}

output "security_group_ids" {
  description = "Security group IDs"
  value = {
    eks_cluster = try(aws_security_group.eks_cluster[0].id, null)
    rds         = try(aws_security_group.rds[0].id, null)
    alb         = try(aws_security_group.alb[0].id, null)
  }
}

# -----------------------------------------------------------------------------
# IAM Outputs
# -----------------------------------------------------------------------------

output "iam_roles" {
  description = "IAM role ARNs"
  value = {
    eks_cluster_service_role = try(aws_iam_role.eks_cluster_service_role[0].arn, null)
    eks_node_group_role     = try(aws_iam_role.eks_node_group_role[0].arn, null)
    eks_pod_execution_role  = try(aws_iam_role.eks_pod_execution_role[0].arn, null)
  }
}

# -----------------------------------------------------------------------------
# Monitoring Outputs
# -----------------------------------------------------------------------------

output "cloudwatch_log_groups" {
  description = "CloudWatch log group names"
  value = {
    eks_cluster = try(aws_cloudwatch_log_group.eks_cluster[0].name, null)
    application = try(aws_cloudwatch_log_group.application[0].name, null)
  }
}

# -----------------------------------------------------------------------------
# DNS Outputs
# -----------------------------------------------------------------------------

output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = try(aws_route53_zone.main[0].zone_id, null)
}

output "route53_zone_name" {
  description = "Route53 hosted zone name"
  value       = try(aws_route53_zone.main[0].name, null)
}

# -----------------------------------------------------------------------------
# Multi-Cloud Outputs
# -----------------------------------------------------------------------------

output "azure_resource_group_name" {
  description = "Azure resource group name"
  value       = try(azurerm_resource_group.main[0].name, null)
}

output "gcp_project_id" {
  description = "GCP project ID"
  value       = try(google_project.main[0].project_id, null)
}

# -----------------------------------------------------------------------------
# Environment Information
# -----------------------------------------------------------------------------

output "deployment_info" {
  description = "Deployment information"
  value = {
    environment      = var.environment
    project_name     = var.project_name
    region          = var.region
    cloud_providers = var.cloud_providers
    deployment_time = timestamp()
  }
}

# -----------------------------------------------------------------------------
# Connection Information
# -----------------------------------------------------------------------------

output "connection_info" {
  description = "Connection information for services"
  value = {
    kubectl_config_command = contains(var.cloud_providers, "aws") ? "aws eks update-kubeconfig --region ${var.aws_region} --name ${var.project_name}-${var.environment}" : null
    database_connection    = try("postgresql://${aws_db_instance.main[0].username}@${aws_db_instance.main[0].endpoint}:${aws_db_instance.main[0].port}/${aws_db_instance.main[0].db_name}", null)
    redis_connection      = try("redis://${aws_elasticache_cluster.main[0].cache_nodes[0].address}:${aws_elasticache_cluster.main[0].cache_nodes[0].port}", null)
  }
  sensitive = true
}