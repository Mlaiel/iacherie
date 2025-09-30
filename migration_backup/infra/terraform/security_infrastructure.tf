# Ainflue Infrastructure Module - Security Infrastructure
# ====================================================
# 
# Enterprise-grade security infrastructure for Ainflue platform
# Supports multi-cloud security and enterprise compliance
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# AWS Security Groups
resource "aws_security_group" "ainflue_web_sg" {
  name_prefix = "${var.environment}-ainflue-web-"
  vpc_id      = aws_vpc.ainflue_vpc.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

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

  tags = {
    Name        = "${var.environment}-ainflue-web-sg"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

resource "aws_security_group" "ainflue_app_sg" {
  name_prefix = "${var.environment}-ainflue-app-"
  vpc_id      = aws_vpc.ainflue_vpc.id

  ingress {
    description     = "App Port"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.ainflue_web_sg.id]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.aws_vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-ainflue-app-sg"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

resource "aws_security_group" "ainflue_db_sg" {
  name_prefix = "${var.environment}-ainflue-db-"
  vpc_id      = aws_vpc.ainflue_vpc.id

  ingress {
    description     = "PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ainflue_app_sg.id]
  }

  ingress {
    description     = "Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ainflue_app_sg.id]
  }

  tags = {
    Name        = "${var.environment}-ainflue-db-sg"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

# AWS KMS Keys
resource "aws_kms_key" "ainflue_main_key" {
  description             = "Ainflue main encryption key"
  deletion_window_in_days = var.environment == "production" ? 30 : 7
  key_usage               = "ENCRYPT_DECRYPT"
  
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
          Service = "logs.amazonaws.com"
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
    Name        = "${var.environment}-ainflue-main-key"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

resource "aws_kms_alias" "ainflue_main_key_alias" {
  name          = "alias/${var.environment}-ainflue-main"
  target_key_id = aws_kms_key.ainflue_main_key.key_id
}

resource "aws_kms_key" "ainflue_s3_key" {
  description             = "Ainflue S3 encryption key"
  deletion_window_in_days = var.environment == "production" ? 30 : 7
  key_usage               = "ENCRYPT_DECRYPT"

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
      }
    ]
  })

  tags = {
    Name        = "${var.environment}-ainflue-s3-key"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

resource "aws_kms_alias" "ainflue_s3_key_alias" {
  name          = "alias/${var.environment}-ainflue-s3"
  target_key_id = aws_kms_key.ainflue_s3_key.key_id
}

# AWS Secrets Manager
resource "aws_secretsmanager_secret" "ainflue_db_credentials" {
  name                    = "${var.environment}-ainflue-db-credentials"
  description             = "Database credentials for Ainflue"
  kms_key_id              = aws_kms_key.ainflue_main_key.arn
  recovery_window_in_days = var.environment == "production" ? 30 : 0

  replica {
    region = var.aws_secondary_region
  }

  tags = {
    Name        = "${var.environment}-ainflue-db-credentials"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

resource "aws_secretsmanager_secret_version" "ainflue_db_credentials" {
  secret_id = aws_secretsmanager_secret.ainflue_db_credentials.id
  secret_string = jsonencode({
    username = "ainflue_admin"
    password = random_password.db_password.result
  })
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# AWS WAF for Web Application Firewall
resource "aws_wafv2_web_acl" "ainflue_waf" {
  name  = "${var.environment}-ainflue-waf"
  scope = "CLOUDFRONT"

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimitRule"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"

        scope_down_statement {
          geo_match_statement {
            country_codes = ["US", "CA", "GB", "DE", "FR", "ES", "IT", "AU", "JP"]
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                 = "RateLimitRule"
      sampled_requests_enabled    = true
    }

    action {
      block {}
    }
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                 = "CommonRuleSet"
      sampled_requests_enabled    = true
    }
  }

  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                 = "KnownBadInputsRuleSet"
      sampled_requests_enabled    = true
    }
  }

  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 4

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                 = "SQLiRuleSet"
      sampled_requests_enabled    = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                 = "ainflueWAF"
    sampled_requests_enabled    = true
  }

  tags = {
    Name        = "${var.environment}-ainflue-waf"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

# AWS Shield Advanced (optional for production)
resource "aws_shield_protection" "ainflue_cloudfront_protection" {
  count        = var.enable_shield_advanced ? 1 : 0
  name         = "${var.environment}-ainflue-cloudfront-protection"
  resource_arn = aws_cloudfront_distribution.ainflue_distribution.arn
}

# AWS GuardDuty
resource "aws_guardduty_detector" "ainflue_guardduty" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = {
    Name        = "${var.environment}-ainflue-guardduty"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

# AWS Config for compliance monitoring
resource "aws_config_configuration_recorder" "ainflue_config_recorder" {
  name     = "${var.environment}-ainflue-config-recorder"
  role_arn = aws_iam_role.config_role.arn

  recording_group {
    all_supported = true
  }
}

resource "aws_config_delivery_channel" "ainflue_config_delivery" {
  name           = "${var.environment}-ainflue-config-delivery"
  s3_bucket_name = aws_s3_bucket.config_bucket.bucket
}

resource "aws_s3_bucket" "config_bucket" {
  bucket        = "${var.environment}-ainflue-config-${random_id.config_suffix.hex}"
  force_destroy = var.environment != "production"

  tags = {
    Name        = "${var.environment}-ainflue-config-bucket"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

resource "random_id" "config_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_server_side_encryption_configuration" "config_bucket_encryption" {
  bucket = aws_s3_bucket.config_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.ainflue_s3_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "config_bucket_pab" {
  bucket = aws_s3_bucket.config_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM Role for AWS Config
resource "aws_iam_role" "config_role" {
  name = "${var.environment}-ainflue-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.environment}-ainflue-config-role"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

resource "aws_iam_role_policy_attachment" "config_role_policy" {
  role       = aws_iam_role.config_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/ConfigRole"
}

resource "aws_iam_role_policy" "config_s3_policy" {
  name = "${var.environment}-ainflue-config-s3-policy"
  role = aws_iam_role.config_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetBucketAcl",
          "s3:GetBucketLocation",
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.config_bucket.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.config_bucket.arn}/*"
      }
    ]
  })
}

# Security Hub
resource "aws_securityhub_account" "ainflue_security_hub" {
  enable_default_standards = true
}

# Azure Security Center (if using Azure)
resource "azurerm_security_center_subscription_pricing" "ainflue_security_center" {
  count = var.enable_azure_security_center ? 1 : 0

  tier          = "Standard"
  resource_type = "VirtualMachines"
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# CloudTrail for audit logging
resource "aws_cloudtrail" "ainflue_cloudtrail" {
  name                          = "${var.environment}-ainflue-cloudtrail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_bucket.bucket
  s3_key_prefix                 = "cloudtrail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true
  kms_key_id                    = aws_kms_key.ainflue_main_key.arn

  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    exclude_management_event_sources = []

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::*/*"]
    }
  }

  tags = {
    Name        = "${var.environment}-ainflue-cloudtrail"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

resource "aws_s3_bucket" "cloudtrail_bucket" {
  bucket        = "${var.environment}-ainflue-cloudtrail-${random_id.cloudtrail_suffix.hex}"
  force_destroy = var.environment != "production"

  tags = {
    Name        = "${var.environment}-ainflue-cloudtrail-bucket"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

resource "random_id" "cloudtrail_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail_bucket_encryption" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.ainflue_main_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "cloudtrail_bucket_pab" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "cloudtrail_bucket_policy" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_bucket.arn
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = "arn:aws:cloudtrail:${var.aws_primary_region}:${data.aws_caller_identity.current.account_id}:trail/${var.environment}-ainflue-cloudtrail"
          }
        }
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_bucket.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
            "AWS:SourceArn" = "arn:aws:cloudtrail:${var.aws_primary_region}:${data.aws_caller_identity.current.account_id}:trail/${var.environment}-ainflue-cloudtrail"
          }
        }
      }
    ]
  })
}