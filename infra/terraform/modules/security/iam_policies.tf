# Ainflue Infrastructure Module - IAM Policies Terraform Security Module
# =======================================================================
# 
# Enterprise-grade IAM policies for Ainflue platform
# Supports multi-cloud IAM management and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "ainflue"
}

variable "enable_mfa_requirement" {
  description = "Require MFA for sensitive operations"
  type        = bool
  default     = true
}

# Local values
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
    SecurityLevel = "enterprise"
    CreatedBy   = "ainflue-infrastructure"
  }
}

# Account Password Policy
resource "aws_iam_account_password_policy" "main" {
  minimum_password_length        = 14
  require_lowercase_characters   = true
  require_uppercase_characters   = true
  require_numbers               = true
  require_symbols               = true
  allow_users_to_change_password = true
  max_password_age              = 90
  password_reuse_prevention     = 12
}

# Creator Economy API Role
resource "aws_iam_role" "api_role" {
  name = "${var.project_name}-${var.environment}-api-role"
  
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
  
  tags = local.common_tags
}

# API Service Policy
resource "aws_iam_policy" "api_policy" {
  name        = "${var.project_name}-${var.environment}-api-policy"
  description = "Policy for Ainflue API service"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-${var.environment}-content/*",
          "arn:aws:s3:::${var.project_name}-${var.environment}-uploads/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-${var.environment}-content",
          "arn:aws:s3:::${var.project_name}-${var.environment}-uploads"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:*:*:secret:${var.project_name}/${var.environment}/*"
        ]
      }
    ]
  })
  
  tags = local.common_tags
}

# Attach API policy to role
resource "aws_iam_role_policy_attachment" "api_policy_attachment" {
  role       = aws_iam_role.api_role.name
  policy_arn = aws_iam_policy.api_policy.arn
}

# Data sources
data "aws_caller_identity" "current" {}

# Outputs
output "api_role_arn" {
  description = "ARN of the API service role"
  value       = aws_iam_role.api_role.arn
}