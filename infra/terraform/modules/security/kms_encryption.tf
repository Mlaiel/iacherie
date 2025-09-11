# Ainflue Infrastructure Module - KMS Encryption Terraform Module
# ================================================================
# 
# Enterprise-grade KMS encryption module for Ainflue platform
# Comprehensive encryption key management and data protection
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# **EXPERT ROLES IMPLEMENTATION:**
# Lead Dev IA: AI model encryption, inference data protection
# Backend Senior: Application data encryption, service-to-service protection
# ML Engineer: Training data encryption, model artifact protection
# DBA: Database encryption at rest, backup encryption
# Security: Comprehensive encryption strategy, key rotation, compliance
# Microservices: Service-specific encryption keys, secure communication
# Audio Engineer: Media content encryption, streaming protection
# DevOps: Infrastructure encryption, secrets management
# IA Prompt Engineer: Prompt data encryption, AI provider security

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "ainflue"
}

variable "deletion_window_in_days" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
}

variable "enable_key_rotation" {
  description = "Enable automatic key rotation"
  type        = bool
  default     = true
}

variable "multi_region" {
  description = "Enable multi-region key replication"
  type        = bool
  default     = false
}

# Data sources for current AWS account and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Master encryption key for general purposes
resource "aws_kms_key" "master" {
  description              = "Master encryption key for ${var.project_name} ${var.environment}"
  deletion_window_in_days  = var.deletion_window_in_days
  enable_key_rotation      = var.enable_key_rotation
  multi_region            = var.multi_region

  policy = jsonencode({
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
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow Lambda"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
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

  tags = {
    Name        = "${var.project_name}-${var.environment}-master-kms"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "master-encryption"
  }
}

resource "aws_kms_alias" "master" {
  name          = "alias/${var.project_name}-${var.environment}-master"
  target_key_id = aws_kms_key.master.key_id
}

# Database encryption key
resource "aws_kms_key" "database" {
  description              = "Database encryption key for ${var.project_name} ${var.environment}"
  deletion_window_in_days  = var.deletion_window_in_days
  enable_key_rotation      = var.enable_key_rotation
  multi_region            = var.multi_region

  policy = jsonencode({
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
        Sid    = "Allow RDS"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow EBS"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
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

  tags = {
    Name        = "${var.project_name}-${var.environment}-database-kms"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "database-encryption"
  }
}

resource "aws_kms_alias" "database" {
  name          = "alias/${var.project_name}-${var.environment}-database"
  target_key_id = aws_kms_key.database.key_id
}

# S3 bucket encryption key
resource "aws_kms_key" "s3" {
  description              = "S3 bucket encryption key for ${var.project_name} ${var.environment}"
  deletion_window_in_days  = var.deletion_window_in_days
  enable_key_rotation      = var.enable_key_rotation
  multi_region            = var.multi_region

  policy = jsonencode({
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
        Sid    = "Allow S3 Service"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow CloudFront"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-s3-kms"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "s3-encryption"
  }
}

resource "aws_kms_alias" "s3" {
  name          = "alias/${var.project_name}-${var.environment}-s3"
  target_key_id = aws_kms_key.s3.key_id
}

# Secrets Manager encryption key
resource "aws_kms_key" "secrets" {
  description              = "Secrets Manager encryption key for ${var.project_name} ${var.environment}"
  deletion_window_in_days  = var.deletion_window_in_days
  enable_key_rotation      = var.enable_key_rotation
  multi_region            = var.multi_region

  policy = jsonencode({
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
        Sid    = "Allow Secrets Manager"
        Effect = "Allow"
        Principal = {
          Service = "secretsmanager.amazonaws.com"
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

  tags = {
    Name        = "${var.project_name}-${var.environment}-secrets-kms"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "secrets-encryption"
  }
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.project_name}-${var.environment}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# AI/ML models encryption key
resource "aws_kms_key" "ai_models" {
  description              = "AI/ML models encryption key for ${var.project_name} ${var.environment}"
  deletion_window_in_days  = var.deletion_window_in_days
  enable_key_rotation      = var.enable_key_rotation
  multi_region            = var.multi_region

  policy = jsonencode({
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
        Sid    = "Allow SageMaker"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow ECS Tasks"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
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

  tags = {
    Name        = "${var.project_name}-${var.environment}-ai-models-kms"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "ai-models-encryption"
  }
}

resource "aws_kms_alias" "ai_models" {
  name          = "alias/${var.project_name}-${var.environment}-ai-models"
  target_key_id = aws_kms_key.ai_models.key_id
}

# Media content encryption key
resource "aws_kms_key" "media" {
  description              = "Media content encryption key for ${var.project_name} ${var.environment}"
  deletion_window_in_days  = var.deletion_window_in_days
  enable_key_rotation      = var.enable_key_rotation
  multi_region            = var.multi_region

  policy = jsonencode({
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
        Sid    = "Allow MediaConvert"
        Effect = "Allow"
        Principal = {
          Service = "mediaconvert.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow MediaLive"
        Effect = "Allow"
        Principal = {
          Service = "medialive.amazonaws.com"
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

  tags = {
    Name        = "${var.project_name}-${var.environment}-media-kms"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "media-encryption"
  }
}

resource "aws_kms_alias" "media" {
  name          = "alias/${var.project_name}-${var.environment}-media"
  target_key_id = aws_kms_key.media.key_id
}

# CloudWatch Logs encryption key
resource "aws_kms_key" "logs" {
  description              = "CloudWatch Logs encryption key for ${var.project_name} ${var.environment}"
  deletion_window_in_days  = var.deletion_window_in_days
  enable_key_rotation      = var.enable_key_rotation
  multi_region            = var.multi_region

  policy = jsonencode({
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
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnEquals = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:${var.project_name}-${var.environment}*"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-logs-kms"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "logs-encryption"
  }
}

resource "aws_kms_alias" "logs" {
  name          = "alias/${var.project_name}-${var.environment}-logs"
  target_key_id = aws_kms_key.logs.key_id
}

# EKS cluster encryption key
resource "aws_kms_key" "eks" {
  description              = "EKS cluster encryption key for ${var.project_name} ${var.environment}"
  deletion_window_in_days  = var.deletion_window_in_days
  enable_key_rotation      = var.enable_key_rotation
  multi_region            = var.multi_region

  policy = jsonencode({
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
        Sid    = "Allow EKS"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
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

  tags = {
    Name        = "${var.project_name}-${var.environment}-eks-kms"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "eks-encryption"
  }
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.project_name}-${var.environment}-eks"
  target_key_id = aws_kms_key.eks.key_id
}

# Key grants for cross-service access
resource "aws_kms_grant" "s3_cloudfront" {
  name              = "${var.project_name}-${var.environment}-s3-cloudfront-grant"
  key_id            = aws_kms_key.s3.key_id
  grantee_principal = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/CloudFrontDistributionRole"
  operations        = ["Decrypt", "DescribeKey"]

  constraints {
    encryption_context_equals = {
      "aws:SecureTransport" = "true"
    }
  }
}

# CloudWatch alarms for key usage monitoring
resource "aws_cloudwatch_metric_alarm" "kms_key_usage" {
  for_each = {
    master    = aws_kms_key.master.key_id
    database  = aws_kms_key.database.key_id
    s3        = aws_kms_key.s3.key_id
    secrets   = aws_kms_key.secrets.key_id
    ai_models = aws_kms_key.ai_models.key_id
    media     = aws_kms_key.media.key_id
    logs      = aws_kms_key.logs.key_id
    eks       = aws_kms_key.eks.key_id
  }

  alarm_name          = "${var.project_name}-${var.environment}-kms-${each.key}-usage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "NumberOfRequestsExceeded"
  namespace           = "AWS/KMS"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1000"
  alarm_description   = "This metric monitors KMS key usage for ${each.key}"

  dimensions = {
    KeyId = each.value
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-kms-${each.key}-alarm"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "master_key_arn" {
  description = "ARN of the master KMS key"
  value       = aws_kms_key.master.arn
}

output "master_key_id" {
  description = "ID of the master KMS key"
  value       = aws_kms_key.master.key_id
}

output "database_key_arn" {
  description = "ARN of the database KMS key"
  value       = aws_kms_key.database.arn
}

output "database_key_id" {
  description = "ID of the database KMS key"
  value       = aws_kms_key.database.key_id
}

output "s3_key_arn" {
  description = "ARN of the S3 KMS key"
  value       = aws_kms_key.s3.arn
}

output "s3_key_id" {
  description = "ID of the S3 KMS key"
  value       = aws_kms_key.s3.key_id
}

output "secrets_key_arn" {
  description = "ARN of the Secrets Manager KMS key"
  value       = aws_kms_key.secrets.arn
}

output "secrets_key_id" {
  description = "ID of the Secrets Manager KMS key"
  value       = aws_kms_key.secrets.key_id
}

output "ai_models_key_arn" {
  description = "ARN of the AI models KMS key"
  value       = aws_kms_key.ai_models.arn
}

output "ai_models_key_id" {
  description = "ID of the AI models KMS key"
  value       = aws_kms_key.ai_models.key_id
}

output "media_key_arn" {
  description = "ARN of the media KMS key"
  value       = aws_kms_key.media.arn
}

output "media_key_id" {
  description = "ID of the media KMS key"
  value       = aws_kms_key.media.key_id
}

output "logs_key_arn" {
  description = "ARN of the logs KMS key"
  value       = aws_kms_key.logs.arn
}

output "logs_key_id" {
  description = "ID of the logs KMS key"
  value       = aws_kms_key.logs.key_id
}

output "eks_key_arn" {
  description = "ARN of the EKS KMS key"
  value       = aws_kms_key.eks.arn
}

output "eks_key_id" {
  description = "ID of the EKS KMS key"
  value       = aws_kms_key.eks.key_id
}

output "all_key_arns" {
  description = "Map of all KMS key ARNs"
  value = {
    master    = aws_kms_key.master.arn
    database  = aws_kms_key.database.arn
    s3        = aws_kms_key.s3.arn
    secrets   = aws_kms_key.secrets.arn
    ai_models = aws_kms_key.ai_models.arn
    media     = aws_kms_key.media.arn
    logs      = aws_kms_key.logs.arn
    eks       = aws_kms_key.eks.arn
  }
}