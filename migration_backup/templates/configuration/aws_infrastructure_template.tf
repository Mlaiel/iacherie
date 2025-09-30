# AWS Infrastructure Template - Ainflue Creator Economy Platform
# ==============================================================
#
# 🎯 AWS CLOUD ARCHITECT + DEVOPS ENGINEER + INFRASTRUCTURE EXPERT  
# Lead: Fahed Mlaiel (mlaiel@live.de)
#
# AWS-specific infrastructure configuration for Creator Economy Platform:
# - AWS-native services integration
# - Creator Economy optimized AWS services
# - AI/ML services integration (SageMaker, Bedrock, Comprehend)
# - Content delivery with CloudFront and S3
# - Advanced security with AWS security services
# - Monitoring with CloudWatch and X-Ray
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
# AWS PROVIDER CONFIGURATION
# ==============================================================================
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure AWS Provider with Creator Economy optimizations
provider "aws" {
  region = var.aws_region
  
  # Assume role for cross-account deployment
  assume_role {
    role_arn     = var.aws_assume_role_arn
    session_name = "AinflueTerraformSession"
  }
  
  default_tags {
    tags = {
      Project         = "Ainflue"
      Environment     = var.environment
      BusinessUnit    = "CreatorEconomy"
      Owner           = "Fahed Mlaiel"
      ManagedBy       = "Terraform"
      AWSAccount      = data.aws_caller_identity.current.account_id
      DeploymentDate  = formatdate("YYYY-MM-DD", timestamp())
      SecurityLevel   = "Enterprise"
      ComplianceRequired = "GDPR"
      IPProtection    = "Enabled"
    }
  }
}

# ==============================================================================
# DATA SOURCES
# ==============================================================================
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# ==============================================================================
# CREATOR ECONOMY S3 BUCKETS
# ==============================================================================

# Video Content Bucket with Lifecycle Management
resource "aws_s3_bucket" "video_content" {
  bucket = "${var.cluster_name}-video-content-${random_id.bucket_suffix.hex}"
  
  tags = merge(var.common_tags, {
    Name        = "Video Content Storage"
    ContentType = "Video"
    Purpose     = "CreatorContent"
  })
}

resource "aws_s3_bucket_versioning" "video_content" {
  bucket = aws_s3_bucket.video_content.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "video_content" {
  bucket = aws_s3_bucket.video_content.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = aws_kms_key.content_encryption.arn
      }
      bucket_key_enabled = true
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "video_content" {
  bucket = aws_s3_bucket.video_content.id
  
  rule {
    id     = "video_content_lifecycle"
    status = "Enabled"
    
    # Transition to IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    # Transition to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    # Transition to Deep Archive after 365 days
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
    
    # Delete incomplete multipart uploads after 7 days
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Audio Content Bucket
resource "aws_s3_bucket" "audio_content" {
  bucket = "${var.cluster_name}-audio-content-${random_id.bucket_suffix.hex}"
  
  tags = merge(var.common_tags, {
    Name        = "Audio Content Storage"
    ContentType = "Audio"
    Purpose     = "CreatorContent"
  })
}

resource "aws_s3_bucket_versioning" "audio_content" {
  bucket = aws_s3_bucket.audio_content.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "audio_content" {
  bucket = aws_s3_bucket.audio_content.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = aws_kms_key.content_encryption.arn
      }
      bucket_key_enabled = true
    }
  }
}

# Image Content Bucket
resource "aws_s3_bucket" "image_content" {
  bucket = "${var.cluster_name}-image-content-${random_id.bucket_suffix.hex}"
  
  tags = merge(var.common_tags, {
    Name        = "Image Content Storage"
    ContentType = "Image"
    Purpose     = "CreatorContent"
  })
}

resource "aws_s3_bucket_versioning" "image_content" {
  bucket = aws_s3_bucket.image_content.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "image_content" {
  bucket = aws_s3_bucket.image_content.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = aws_kms_key.content_encryption.arn
      }
      bucket_key_enabled = true
    }
  }
}

# Random suffix for bucket uniqueness
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# ==============================================================================
# KMS ENCRYPTION KEYS
# ==============================================================================

# Content Encryption Key
resource "aws_kms_key" "content_encryption" {
  description             = "Ainflue Creator Economy Content Encryption Key"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  policy = jsonencode({
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
          Service = [
            "s3.amazonaws.com",
            "rds.amazonaws.com",
            "elasticache.amazonaws.com",
            "logs.amazonaws.com",
            "sagemaker.amazonaws.com"
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
  
  tags = merge(var.common_tags, {
    Name    = "Ainflue Content Encryption Key"
    Purpose = "ContentEncryption"
  })
}

resource "aws_kms_alias" "content_encryption" {
  name          = "alias/ainflue-content-encryption"
  target_key_id = aws_kms_key.content_encryption.key_id
}

# ==============================================================================
# AWS AI/ML SERVICES FOR CREATOR ECONOMY
# ==============================================================================

# SageMaker Domain for AI Processing
resource "aws_sagemaker_domain" "creator_ai" {
  domain_name = "${var.cluster_name}-creator-ai"
  auth_mode   = "IAM"
  vpc_id      = var.vpc_id
  subnet_ids  = var.private_subnets
  
  default_user_settings {
    execution_role = aws_iam_role.sagemaker_execution.arn
    
    # Security groups
    security_groups = [aws_security_group.sagemaker.id]
    
    # Jupyter server app settings
    jupyter_server_app_settings {
      default_resource_spec {
        instance_type        = "ml.t3.medium"
        sage_maker_image_arn = "arn:aws:sagemaker:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:image/pytorch-1.12-cpu-py38"
      }
    }
    
    # Kernel gateway app settings
    kernel_gateway_app_settings {
      default_resource_spec {
        instance_type = "ml.t3.medium"
      }
    }
  }
  
  tags = merge(var.common_tags, {
    Name    = "Creator AI Processing Domain"
    Purpose = "AIProcessing"
  })
}

# SageMaker Execution Role
resource "aws_iam_role" "sagemaker_execution" {
  name = "${var.cluster_name}-sagemaker-execution"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.common_tags
}

# Attach necessary policies to SageMaker role
resource "aws_iam_role_policy_attachment" "sagemaker_execution" {
  role       = aws_iam_role.sagemaker_execution.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_iam_role_policy" "sagemaker_s3_access" {
  name = "${var.cluster_name}-sagemaker-s3-access"
  role = aws_iam_role.sagemaker_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.video_content.arn,
          "${aws_s3_bucket.video_content.arn}/*",
          aws_s3_bucket.audio_content.arn,
          "${aws_s3_bucket.audio_content.arn}/*",
          aws_s3_bucket.image_content.arn,
          "${aws_s3_bucket.image_content.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = [aws_kms_key.content_encryption.arn]
      }
    ]
  })
}

# Security Group for SageMaker
resource "aws_security_group" "sagemaker" {
  name_prefix = "${var.cluster_name}-sagemaker-"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "SageMaker Security Group"
  })
}

# ==============================================================================
# AWS COMPREHEND FOR TEXT ANALYSIS
# ==============================================================================

# Comprehend Document Classifier for Content Categorization
resource "aws_iam_role" "comprehend_role" {
  name = "${var.cluster_name}-comprehend-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "comprehend.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.common_tags
}

resource "aws_iam_role_policy" "comprehend_s3_access" {
  name = "${var.cluster_name}-comprehend-s3-access"
  role = aws_iam_role.comprehend_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.document_content.arn,
          "${aws_s3_bucket.document_content.arn}/*"
        ]
      }
    ]
  })
}

# Document Content Bucket for Comprehend
resource "aws_s3_bucket" "document_content" {
  bucket = "${var.cluster_name}-document-content-${random_id.bucket_suffix.hex}"
  
  tags = merge(var.common_tags, {
    Name        = "Document Content Storage"
    ContentType = "Document"
    Purpose     = "CreatorContent"
  })
}

# ==============================================================================
# AWS REKOGNITION FOR IMAGE AND VIDEO ANALYSIS
# ==============================================================================

# Custom Labels Model for Creator Content Analysis
resource "aws_iam_role" "rekognition_role" {
  name = "${var.cluster_name}-rekognition-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "rekognition.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.common_tags
}

resource "aws_iam_role_policy" "rekognition_s3_access" {
  name = "${var.cluster_name}-rekognition-s3-access"
  role = aws_iam_role.rekognition_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.video_content.arn,
          "${aws_s3_bucket.video_content.arn}/*",
          aws_s3_bucket.image_content.arn,
          "${aws_s3_bucket.image_content.arn}/*"
        ]
      }
    ]
  })
}

# ==============================================================================
# AWS TRANSCRIBE FOR AUDIO CONTENT
# ==============================================================================

# S3 Bucket for Transcription Output
resource "aws_s3_bucket" "transcription_output" {
  bucket = "${var.cluster_name}-transcription-output-${random_id.bucket_suffix.hex}"
  
  tags = merge(var.common_tags, {
    Name    = "Transcription Output Storage"
    Purpose = "TranscriptionOutput"
  })
}

resource "aws_s3_bucket_encryption" "transcription_output" {
  bucket = aws_s3_bucket.transcription_output.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = aws_kms_key.content_encryption.arn
      }
      bucket_key_enabled = true
    }
  }
}

# ==============================================================================
# AWS CLOUDFRONT DISTRIBUTION
# ==============================================================================

# CloudFront Origin Access Control
resource "aws_cloudfront_origin_access_control" "content_oac" {
  name                              = "${var.cluster_name}-content-oac"
  description                       = "OAC for Ainflue Creator Economy content"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront Distribution for Creator Content
resource "aws_cloudfront_distribution" "creator_content" {
  comment             = "Ainflue Creator Economy Content Distribution"
  default_root_object = "index.html"
  enabled             = true
  is_ipv6_enabled     = true
  price_class         = var.cloudfront_price_class
  
  # Video content origin
  origin {
    domain_name              = aws_s3_bucket.video_content.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.video_content.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.content_oac.id
  }
  
  # Audio content origin
  origin {
    domain_name              = aws_s3_bucket.audio_content.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.audio_content.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.content_oac.id
  }
  
  # Image content origin
  origin {
    domain_name              = aws_s3_bucket.image_content.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.image_content.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.content_oac.id
  }
  
  # Default cache behavior
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.image_content.id}"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    
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
  
  # Video content cache behavior
  ordered_cache_behavior {
    path_pattern           = "/video/*"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.video_content.id}"
    viewer_protocol_policy = "redirect-to-https"
    compress               = false
    
    forwarded_values {
      query_string = true
      headers      = ["Range", "Origin"]
      cookies {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }
  
  # Audio content cache behavior
  ordered_cache_behavior {
    path_pattern           = "/audio/*"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.audio_content.id}"
    viewer_protocol_policy = "redirect-to-https"
    compress               = false
    
    forwarded_values {
      query_string = true
      headers      = ["Range", "Origin"]
      cookies {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }
  
  # Geographic restrictions
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  # SSL certificate
  viewer_certificate {
    acm_certificate_arn      = var.ssl_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
  
  # Custom error responses
  custom_error_response {
    error_code            = 404
    error_caching_min_ttl = 300
    response_code         = 404
    response_page_path    = "/404.html"
  }
  
  custom_error_response {
    error_code            = 500
    error_caching_min_ttl = 300
    response_code         = 500
    response_page_path    = "/500.html"
  }
  
  # Logging configuration
  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.cloudfront_logs.bucket_domain_name
    prefix          = "cloudfront-logs/"
  }
  
  tags = merge(var.common_tags, {
    Name    = "Creator Content Distribution"
    Purpose = "ContentDelivery"
  })
}

# S3 Bucket for CloudFront Logs
resource "aws_s3_bucket" "cloudfront_logs" {
  bucket = "${var.cluster_name}-cloudfront-logs-${random_id.bucket_suffix.hex}"
  
  tags = merge(var.common_tags, {
    Name    = "CloudFront Logs"
    Purpose = "Logging"
  })
}

# ==============================================================================
# AWS WAF FOR SECURITY
# ==============================================================================

# WAF Web ACL for Creator Economy Protection
resource "aws_wafv2_web_acl" "creator_economy" {
  name  = "${var.cluster_name}-creator-economy-waf"
  scope = "CLOUDFRONT"
  
  default_action {
    allow {}
  }
  
  # Rate limiting rule for API endpoints
  rule {
    name     = "RateLimitCreatorAPI"
    priority = 1
    
    action {
      block {}
    }
    
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
        
        scope_down_statement {
          byte_match_statement {
            field_to_match {
              uri_path {}
            }
            positional_constraint = "STARTS_WITH"
            search_string         = "/api/v1/creators"
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                 = "CreatorAPIRateLimit"
      sampled_requests_enabled    = true
    }
  }
  
  # AI processing rate limiting
  rule {
    name     = "RateLimitAIProcessing"
    priority = 2
    
    action {
      block {}
    }
    
    statement {
      rate_based_statement {
        limit              = 100
        aggregate_key_type = "IP"
        
        scope_down_statement {
          byte_match_statement {
            field_to_match {
              uri_path {}
            }
            positional_constraint = "STARTS_WITH"
            search_string         = "/api/v1/ai"
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                 = "AIProcessingRateLimit"
      sampled_requests_enabled    = true
    }
  }
  
  # AWS Managed Rules - Core Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 10
    
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
      metric_name                 = "CommonRuleSetMetric"
      sampled_requests_enabled    = true
    }
  }
  
  # AWS Managed Rules - SQL injection
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 11
    
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
      metric_name                 = "SQLiRuleSetMetric"
      sampled_requests_enabled    = true
    }
  }
  
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                 = "CreatorEconomyWAF"
    sampled_requests_enabled    = true
  }
  
  tags = merge(var.common_tags, {
    Name    = "Creator Economy WAF"
    Purpose = "Security"
  })
}

# Associate WAF with CloudFront
resource "aws_wafv2_web_acl_association" "cloudfront" {
  resource_arn = aws_cloudfront_distribution.creator_content.arn
  web_acl_arn  = aws_wafv2_web_acl.creator_economy.arn
}

# ==============================================================================
# AWS SECRETS MANAGER
# ==============================================================================

# Database password secret
resource "aws_secretsmanager_secret" "database_password" {
  name                    = "${var.cluster_name}/database/master-password"
  description             = "Master password for Ainflue Creator Economy database"
  recovery_window_in_days = 7
  kms_key_id             = aws_kms_key.content_encryption.arn
  
  tags = merge(var.common_tags, {
    Name    = "Database Master Password"
    Purpose = "DatabaseAuthentication"
  })
}

resource "aws_secretsmanager_secret_version" "database_password" {
  secret_id = aws_secretsmanager_secret.database_password.id
  secret_string = jsonencode({
    username = "ainflue_admin"
    password = random_password.db_password.result
  })
}

# API keys secret
resource "aws_secretsmanager_secret" "api_keys" {
  name                    = "${var.cluster_name}/api/keys"
  description             = "API keys for external services"
  recovery_window_in_days = 7
  kms_key_id             = aws_kms_key.content_encryption.arn
  
  tags = merge(var.common_tags, {
    Name    = "API Keys"
    Purpose = "ExternalIntegration"
  })
}

# Random password generation
resource "random_password" "db_password" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# ==============================================================================
# AWS EVENTBRIDGE FOR CREATOR ECONOMY EVENTS
# ==============================================================================

# Custom Event Bus for Creator Economy
resource "aws_cloudwatch_event_bus" "creator_economy" {
  name = "${var.cluster_name}-creator-economy-events"
  
  tags = merge(var.common_tags, {
    Name    = "Creator Economy Event Bus"
    Purpose = "EventDriven"
  })
}

# Event Rules for Creator Economy Events
resource "aws_cloudwatch_event_rule" "content_uploaded" {
  name           = "${var.cluster_name}-content-uploaded"
  description    = "Trigger when new content is uploaded"
  event_bus_name = aws_cloudwatch_event_bus.creator_economy.name
  
  event_pattern = jsonencode({
    source      = ["ainflue.creator-economy"]
    detail-type = ["Content Uploaded"]
    detail = {
      contentType = ["video", "audio", "image", "document"]
    }
  })
  
  tags = var.common_tags
}

resource "aws_cloudwatch_event_rule" "ai_processing_completed" {
  name           = "${var.cluster_name}-ai-processing-completed"
  description    = "Trigger when AI processing is completed"
  event_bus_name = aws_cloudwatch_event_bus.creator_economy.name
  
  event_pattern = jsonencode({
    source      = ["ainflue.ai-processing"]
    detail-type = ["AI Processing Completed"]
    detail = {
      status = ["success", "failed"]
    }
  })
  
  tags = var.common_tags
}

# ==============================================================================
# AWS SNS FOR NOTIFICATIONS
# ==============================================================================

# SNS Topic for Creator Economy Notifications
resource "aws_sns_topic" "creator_economy_notifications" {
  name              = "${var.cluster_name}-creator-economy-notifications"
  kms_master_key_id = aws_kms_key.content_encryption.arn
  
  tags = merge(var.common_tags, {
    Name    = "Creator Economy Notifications"
    Purpose = "Notifications"
  })
}

# SNS Topic Policy
resource "aws_sns_topic_policy" "creator_economy_notifications" {
  arn = aws_sns_topic.creator_economy_notifications.arn
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.creator_economy_notifications.arn
      }
    ]
  })
}

# ==============================================================================
# OUTPUTS
# ==============================================================================

output "s3_buckets" {
  description = "S3 buckets for creator content"
  value = {
    video_content       = aws_s3_bucket.video_content.id
    audio_content       = aws_s3_bucket.audio_content.id
    image_content       = aws_s3_bucket.image_content.id
    document_content    = aws_s3_bucket.document_content.id
    transcription_output = aws_s3_bucket.transcription_output.id
    cloudfront_logs     = aws_s3_bucket.cloudfront_logs.id
  }
}

output "cloudfront_distribution" {
  description = "CloudFront distribution details"
  value = {
    id          = aws_cloudfront_distribution.creator_content.id
    domain_name = aws_cloudfront_distribution.creator_content.domain_name
    arn         = aws_cloudfront_distribution.creator_content.arn
  }
}

output "kms_keys" {
  description = "KMS encryption keys"
  value = {
    content_encryption = {
      id     = aws_kms_key.content_encryption.id
      arn    = aws_kms_key.content_encryption.arn
      alias  = aws_kms_alias.content_encryption.name
    }
  }
}

output "ai_services" {
  description = "AWS AI/ML services configuration"
  value = {
    sagemaker_domain = {
      id   = aws_sagemaker_domain.creator_ai.id
      arn  = aws_sagemaker_domain.creator_ai.arn
      url  = aws_sagemaker_domain.creator_ai.url
    }
    comprehend_role_arn = aws_iam_role.comprehend_role.arn
    rekognition_role_arn = aws_iam_role.rekognition_role.arn
  }
}

output "security_services" {
  description = "AWS security services"
  value = {
    waf_web_acl = {
      id  = aws_wafv2_web_acl.creator_economy.id
      arn = aws_wafv2_web_acl.creator_economy.arn
    }
    secrets_manager = {
      database_password_arn = aws_secretsmanager_secret.database_password.arn
      api_keys_arn         = aws_secretsmanager_secret.api_keys.arn
    }
  }
}

output "event_driven_architecture" {
  description = "Event-driven architecture components"
  value = {
    event_bus = {
      name = aws_cloudwatch_event_bus.creator_economy.name
      arn  = aws_cloudwatch_event_bus.creator_economy.arn
    }
    sns_topic = {
      arn = aws_sns_topic.creator_economy_notifications.arn
    }
  }
}