# Ainflue Infrastructure Module - S3 Storage Module
# ==================================================
# 
# Enterprise-grade S3 storage module for Ainflue platform
# Supports content storage, AI model artifacts, and media processing
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# **EXPERT ROLES IMPLEMENTATION:**
# Lead Dev IA: AI model storage, artifact management, versioning
# Backend Senior: Scalable storage architecture, lifecycle management
# ML Engineer: Model artifact storage, training data management, experiment tracking
# DBA: Metadata storage integration, backup strategies
# Security: Encryption, access control, audit logging, compliance
# Microservices: Service-specific bucket policies and access patterns
# Audio Engineer: High-performance audio/video file storage and streaming
# DevOps: Automated backup, lifecycle policies, monitoring
# IA Prompt Engineer: Prompt templates storage and versioning

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

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "enable_versioning" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}

variable "enable_encryption" {
  description = "Enable S3 bucket encryption"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable S3 access logging"
  type        = bool
  default     = true
}

variable "mfa_delete" {
  description = "Enable MFA delete for bucket versioning"
  type        = bool
  default     = false
}

variable "lifecycle_rules" {
  description = "S3 lifecycle rules"
  type = list(object({
    id     = string
    status = string
    transitions = list(object({
      days          = number
      storage_class = string
    }))
    expiration_days = number
  }))
  default = [
    {
      id     = "content_lifecycle"
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
      expiration_days = 2555 # 7 years for compliance
    }
  ]
}

# KMS Key for S3 encryption
resource "aws_kms_key" "s3" {
  description             = "KMS key for ${var.project_name} S3 encryption"
  deletion_window_in_days = 7

  tags = {
    Name        = "${var.project_name}-${var.environment}-s3-kms"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_kms_alias" "s3" {
  name          = "alias/${var.project_name}-${var.environment}-s3"
  target_key_id = aws_kms_key.s3.key_id
}

# Main content storage bucket
resource "aws_s3_bucket" "content" {
  bucket = "${var.project_name}-${var.environment}-content-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-${var.environment}-content"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "user-content-storage"
  }
}

# AI models and artifacts bucket
resource "aws_s3_bucket" "ai_models" {
  bucket = "${var.project_name}-${var.environment}-ai-models-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-${var.environment}-ai-models"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "ai-model-artifacts"
  }
}

# Audio/Media processing bucket
resource "aws_s3_bucket" "media" {
  bucket = "${var.project_name}-${var.environment}-media-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-${var.environment}-media"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "audio-video-processing"
  }
}

# Analytics and logs bucket
resource "aws_s3_bucket" "analytics" {
  bucket = "${var.project_name}-${var.environment}-analytics-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-${var.environment}-analytics"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "analytics-logs"
  }
}

# Backup bucket for disaster recovery
resource "aws_s3_bucket" "backup" {
  bucket = "${var.project_name}-${var.environment}-backup-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-${var.environment}-backup"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "disaster-recovery-backup"
  }
}

# Random ID for bucket suffix to ensure uniqueness
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "content" {
  bucket = aws_s3_bucket.content.id
  versioning_configuration {
    status     = var.enable_versioning ? "Enabled" : "Suspended"
    mfa_delete = var.mfa_delete ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_versioning" "ai_models" {
  bucket = aws_s3_bucket.ai_models.id
  versioning_configuration {
    status = "Enabled" # Always enable versioning for AI models
  }
}

resource "aws_s3_bucket_versioning" "media" {
  bucket = aws_s3_bucket.media.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

# S3 Bucket Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "content" {
  count  = var.enable_encryption ? 1 : 0
  bucket = aws_s3_bucket.content.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ai_models" {
  bucket = aws_s3_bucket.ai_models.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "media" {
  count  = var.enable_encryption ? 1 : 0
  bucket = aws_s3_bucket.media.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "analytics" {
  bucket = aws_s3_bucket.analytics.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backup" {
  bucket = aws_s3_bucket.backup.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "content" {
  bucket = aws_s3_bucket.content.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "ai_models" {
  bucket = aws_s3_bucket.ai_models.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "media" {
  bucket = aws_s3_bucket.media.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "analytics" {
  bucket = aws_s3_bucket.analytics.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "backup" {
  bucket = aws_s3_bucket.backup.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Lifecycle Configuration
resource "aws_s3_bucket_lifecycle_configuration" "content" {
  bucket = aws_s3_bucket.content.id

  dynamic "rule" {
    for_each = var.lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.status

      dynamic "transition" {
        for_each = rule.value.transitions
        content {
          days          = transition.value.days
          storage_class = transition.value.storage_class
        }
      }

      expiration {
        days = rule.value.expiration_days
      }

      noncurrent_version_expiration {
        noncurrent_days = 90
      }
    }
  }
}

# Media-specific lifecycle for large files
resource "aws_s3_bucket_lifecycle_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  rule {
    id     = "media_lifecycle"
    status = "Enabled"

    # Move to IA after 7 days for processed media
    transition {
      days          = 7
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 30 days
    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    # Move to Deep Archive after 90 days
    transition {
      days          = 90
      storage_class = "DEEP_ARCHIVE"
    }

    # Delete incomplete multipart uploads after 1 day
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

# Analytics lifecycle for log data
resource "aws_s3_bucket_lifecycle_configuration" "analytics" {
  bucket = aws_s3_bucket.analytics.id

  rule {
    id     = "analytics_lifecycle"
    status = "Enabled"

    # Move to IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Delete after 7 years for compliance
    expiration {
      days = 2555
    }
  }
}

# S3 Bucket Logging
resource "aws_s3_bucket" "access_logs" {
  count  = var.enable_logging ? 1 : 0
  bucket = "${var.project_name}-${var.environment}-access-logs-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-${var.environment}-access-logs"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "s3-access-logs"
  }
}

resource "aws_s3_bucket_logging" "content" {
  count  = var.enable_logging ? 1 : 0
  bucket = aws_s3_bucket.content.id

  target_bucket = aws_s3_bucket.access_logs[0].id
  target_prefix = "content-access-logs/"
}

# Cross-Region Replication for critical buckets
resource "aws_s3_bucket_replication_configuration" "content" {
  count  = var.environment == "prod" ? 1 : 0
  role   = aws_iam_role.replication[0].arn
  bucket = aws_s3_bucket.content.id

  rule {
    id     = "content_replication"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.backup.arn
      storage_class = "STANDARD_IA"

      encryption_configuration {
        replica_kms_key_id = aws_kms_key.s3.arn
      }
    }
  }

  depends_on = [aws_s3_bucket_versioning.content]
}

# IAM Role for S3 Replication
resource "aws_iam_role" "replication" {
  count = var.environment == "prod" ? 1 : 0
  name  = "${var.project_name}-${var.environment}-s3-replication"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-s3-replication"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_role_policy" "replication" {
  count = var.environment == "prod" ? 1 : 0
  name  = "${var.project_name}-${var.environment}-s3-replication-policy"
  role  = aws_iam_role.replication[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.content.arn}/*"
        ]
      },
      {
        Action = [
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.content.arn
        ]
      },
      {
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.backup.arn}/*"
        ]
      },
      {
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Effect = "Allow"
        Resource = [
          aws_kms_key.s3.arn
        ]
      }
    ]
  })
}

# CloudWatch Alarms for S3 monitoring
resource "aws_cloudwatch_metric_alarm" "s3_requests" {
  alarm_name          = "${var.project_name}-${var.environment}-s3-requests"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "NumberOfObjects"
  namespace           = "AWS/S3"
  period              = "86400" # Daily
  statistic           = "Average"
  threshold           = "1000000" # Alert if more than 1M objects
  alarm_description   = "This metric monitors S3 object count"

  dimensions = {
    BucketName = aws_s3_bucket.content.bucket
    StorageType = "AllStorageTypes"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-s3-objects-alarm"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "content_bucket_name" {
  description = "Name of the content storage bucket"
  value       = aws_s3_bucket.content.bucket
}

output "content_bucket_arn" {
  description = "ARN of the content storage bucket"
  value       = aws_s3_bucket.content.arn
}

output "ai_models_bucket_name" {
  description = "Name of the AI models bucket"
  value       = aws_s3_bucket.ai_models.bucket
}

output "ai_models_bucket_arn" {
  description = "ARN of the AI models bucket"
  value       = aws_s3_bucket.ai_models.arn
}

output "media_bucket_name" {
  description = "Name of the media processing bucket"
  value       = aws_s3_bucket.media.bucket
}

output "media_bucket_arn" {
  description = "ARN of the media processing bucket"
  value       = aws_s3_bucket.media.arn
}

output "analytics_bucket_name" {
  description = "Name of the analytics bucket"
  value       = aws_s3_bucket.analytics.bucket
}

output "analytics_bucket_arn" {
  description = "ARN of the analytics bucket"
  value       = aws_s3_bucket.analytics.arn
}

output "backup_bucket_name" {
  description = "Name of the backup bucket"
  value       = aws_s3_bucket.backup.bucket
}

output "backup_bucket_arn" {
  description = "ARN of the backup bucket"
  value       = aws_s3_bucket.backup.arn
}

output "kms_key_arn" {
  description = "ARN of the KMS key used for S3 encryption"
  value       = aws_kms_key.s3.arn
}

output "access_logs_bucket_name" {
  description = "Name of the access logs bucket"
  value       = var.enable_logging ? aws_s3_bucket.access_logs[0].bucket : null
}