# Ainflue Infrastructure Module - CloudFront CDN Module
# ======================================================
# 
# Enterprise-grade CloudFront CDN module for Ainflue platform
# Supports global content delivery, media streaming, and API acceleration
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# **EXPERT ROLES IMPLEMENTATION:**
# Lead Dev IA: AI-powered content optimization, edge computing for AI inference
# Backend Senior: Global API acceleration, edge caching strategies
# ML Engineer: Model serving at edge, ML inference optimization
# DBA: Database query result caching, read replica optimization
# Security: WAF integration, DDoS protection, SSL/TLS termination
# Microservices: Service-specific cache behaviors, API gateway integration
# Audio Engineer: Audio/video streaming optimization, adaptive bitrate
# DevOps: Global deployment, monitoring, automated invalidation
# IA Prompt Engineer: Prompt response caching, AI service acceleration

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

variable "domain_name" {
  description = "Domain name for the CDN"
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

variable "price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_All"
}

variable "enable_waf" {
  description = "Enable AWS WAF for the distribution"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable CloudFront access logging"
  type        = bool
  default     = true
}

variable "s3_content_bucket" {
  description = "S3 bucket for content storage"
  type        = string
}

variable "s3_media_bucket" {
  description = "S3 bucket for media storage"
  type        = string
}

variable "api_gateway_domain" {
  description = "API Gateway domain name"
  type        = string
  default     = ""
}

variable "geo_restriction_type" {
  description = "Geo restriction type (none, whitelist, blacklist)"
  type        = string
  default     = "none"
}

variable "geo_restriction_locations" {
  description = "List of country codes for geo restriction"
  type        = list(string)
  default     = []
}

# S3 bucket for CloudFront access logs
resource "aws_s3_bucket" "cloudfront_logs" {
  count  = var.enable_logging ? 1 : 0
  bucket = "${var.project_name}-${var.environment}-cloudfront-logs-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-${var.environment}-cloudfront-logs"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "cloudfront-access-logs"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Origin Access Control for S3 buckets
resource "aws_cloudfront_origin_access_control" "content" {
  name                              = "${var.project_name}-${var.environment}-content-oac"
  description                       = "OAC for content bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_origin_access_control" "media" {
  name                              = "${var.project_name}-${var.environment}-media-oac"
  description                       = "OAC for media bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# WAF Web ACL for CloudFront
resource "aws_wafv2_web_acl" "cloudfront" {
  count = var.enable_waf ? 1 : 0
  name  = "${var.project_name}-${var.environment}-cloudfront-waf"
  scope = "CLOUDFRONT"

  default_action {
    allow {}
  }

  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit              = 10000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }

    action {
      block {}
    }
  }

  # AWS Managed Rule - Common Rule Set
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
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rule - Known Bad Inputs
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
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Geo restriction rule (if specified)
  dynamic "rule" {
    for_each = var.geo_restriction_type != "none" ? [1] : []
    content {
      name     = "GeoRestrictionRule"
      priority = 4

      action {
        block {}
      }

      statement {
        geo_match_statement {
          country_codes = var.geo_restriction_locations
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "GeoRestrictionRule"
        sampled_requests_enabled   = true
      }
    }
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-cloudfront-waf"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudFront Cache Policy for Content
resource "aws_cloudfront_cache_policy" "content" {
  name        = "${var.project_name}-${var.environment}-content-cache"
  comment     = "Cache policy for content delivery"
  default_ttl = 86400  # 1 day
  max_ttl     = 31536000 # 1 year
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true

    query_strings_config {
      query_string_behavior = "whitelist"
      query_strings {
        items = ["v", "version", "format"]
      }
    }

    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Accept", "Accept-Encoding", "Accept-Language"]
      }
    }

    cookies_config {
      cookie_behavior = "none"
    }
  }
}

# CloudFront Cache Policy for API
resource "aws_cloudfront_cache_policy" "api" {
  name        = "${var.project_name}-${var.environment}-api-cache"
  comment     = "Cache policy for API responses"
  default_ttl = 300    # 5 minutes
  max_ttl     = 3600   # 1 hour
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true

    query_strings_config {
      query_string_behavior = "all"
    }

    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Authorization", "Accept", "Content-Type", "User-Agent"]
      }
    }

    cookies_config {
      cookie_behavior = "all"
    }
  }
}

# CloudFront Cache Policy for Media Streaming
resource "aws_cloudfront_cache_policy" "media" {
  name        = "${var.project_name}-${var.environment}-media-cache"
  comment     = "Cache policy for media streaming"
  default_ttl = 604800  # 7 days
  max_ttl     = 31536000 # 1 year
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    enable_accept_encoding_brotli = false # Don't compress media files
    enable_accept_encoding_gzip   = false

    query_strings_config {
      query_string_behavior = "whitelist"
      query_strings {
        items = ["quality", "bitrate", "format", "resolution"]
      }
    }

    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Range", "Accept-Ranges"]
      }
    }

    cookies_config {
      cookie_behavior = "none"
    }
  }
}

# CloudFront Origin Request Policy
resource "aws_cloudfront_origin_request_policy" "api" {
  name    = "${var.project_name}-${var.environment}-api-origin-request"
  comment = "Origin request policy for API"

  cookies_config {
    cookie_behavior = "all"
  }

  headers_config {
    header_behavior = "whitelist"
    headers {
      items = [
        "Authorization",
        "Accept",
        "Content-Type",
        "User-Agent",
        "X-Forwarded-For",
        "X-Forwarded-Proto",
        "X-Forwarded-Host"
      ]
    }
  }

  query_strings_config {
    query_string_behavior = "all"
  }
}

# CloudFront Response Headers Policy
resource "aws_cloudfront_response_headers_policy" "security" {
  name    = "${var.project_name}-${var.environment}-security-headers"
  comment = "Security headers policy"

  security_headers_config {
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      override                   = true
    }

    content_type_options {
      override = true
    }

    frame_options {
      frame_option = "DENY"
      override     = true
    }

    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }
  }

  cors_config {
    access_control_allow_credentials = false

    access_control_allow_headers {
      items = ["*"]
    }

    access_control_allow_methods {
      items = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
    }

    access_control_allow_origins {
      items = ["*"]
    }

    access_control_expose_headers {
      items = ["*"]
    }

    access_control_max_age_sec = 86400
    origin_override            = true
  }
}

# Main CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  # Content origin (S3)
  origin {
    domain_name              = aws_s3_bucket.content.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.content.bucket}"
    origin_access_control_id = aws_cloudfront_origin_access_control.content.id
  }

  # Media origin (S3)
  origin {
    domain_name              = aws_s3_bucket.media.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.media.bucket}"
    origin_access_control_id = aws_cloudfront_origin_access_control.media.id
  }

  # API origin (API Gateway)
  dynamic "origin" {
    for_each = var.api_gateway_domain != "" ? [1] : []
    content {
      domain_name = var.api_gateway_domain
      origin_id   = "API-Gateway"

      custom_origin_config {
        http_port              = 80
        https_port             = 443
        origin_protocol_policy = "https-only"
        origin_ssl_protocols   = ["TLSv1.2"]
      }
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Ainflue ${var.environment} CDN distribution"
  default_root_object = "index.html"
  price_class         = var.price_class

  # Logging configuration
  dynamic "logging_config" {
    for_each = var.enable_logging ? [1] : []
    content {
      include_cookies = false
      bucket          = aws_s3_bucket.cloudfront_logs[0].bucket_domain_name
      prefix          = "access-logs/"
    }
  }

  # Aliases (domain names)
  aliases = var.domain_name != "" ? [var.domain_name] : []

  # Default cache behavior for web content
  default_cache_behavior {
    allowed_methods            = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods             = ["GET", "HEAD"]
    target_origin_id           = "S3-${aws_s3_bucket.content.bucket}"
    cache_policy_id            = aws_cloudfront_cache_policy.content.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id

    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  # Cache behavior for media files
  ordered_cache_behavior {
    path_pattern               = "/media/*"
    allowed_methods            = ["GET", "HEAD", "OPTIONS"]
    cached_methods             = ["GET", "HEAD"]
    target_origin_id           = "S3-${aws_s3_bucket.media.bucket}"
    cache_policy_id            = aws_cloudfront_cache_policy.media.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id

    viewer_protocol_policy = "redirect-to-https"
    compress               = false # Don't compress media files
  }

  # Cache behavior for API calls (if API Gateway is configured)
  dynamic "ordered_cache_behavior" {
    for_each = var.api_gateway_domain != "" ? [1] : []
    content {
      path_pattern                 = "/api/*"
      allowed_methods              = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
      cached_methods               = ["GET", "HEAD"]
      target_origin_id             = "API-Gateway"
      cache_policy_id              = aws_cloudfront_cache_policy.api.id
      origin_request_policy_id     = aws_cloudfront_origin_request_policy.api.id
      response_headers_policy_id   = aws_cloudfront_response_headers_policy.security.id

      viewer_protocol_policy = "redirect-to-https"
      compress               = true
    }
  }

  # Cache behavior for AI model endpoints
  ordered_cache_behavior {
    path_pattern               = "/ai/*"
    allowed_methods            = ["GET", "HEAD", "OPTIONS", "POST"]
    cached_methods             = ["GET", "HEAD"]
    target_origin_id           = "S3-${aws_s3_bucket.content.bucket}"
    cache_policy_id            = aws_cloudfront_cache_policy.api.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id

    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  # Geo restriction configuration
  restrictions {
    geo_restriction {
      restriction_type = var.geo_restriction_type
      locations        = var.geo_restriction_locations
    }
  }

  # SSL/TLS configuration
  viewer_certificate {
    cloudfront_default_certificate = var.certificate_arn == ""
    acm_certificate_arn            = var.certificate_arn != "" ? var.certificate_arn : null
    ssl_support_method             = var.certificate_arn != "" ? "sni-only" : null
    minimum_protocol_version       = var.certificate_arn != "" ? "TLSv1.2_2021" : null
  }

  # WAF association
  web_acl_id = var.enable_waf ? aws_wafv2_web_acl.cloudfront[0].arn : null

  tags = {
    Name        = "${var.project_name}-${var.environment}-distribution"
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 bucket policy to allow CloudFront access
data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.content.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.main.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "content" {
  bucket = aws_s3_bucket.content.id
  policy = data.aws_iam_policy_document.s3_policy.json
}

# S3 bucket policy for media bucket
data "aws_iam_policy_document" "s3_media_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.media.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.main.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "media" {
  bucket = aws_s3_bucket.media.id
  policy = data.aws_iam_policy_document.s3_media_policy.json
}

# CloudWatch Alarms for monitoring
resource "aws_cloudwatch_metric_alarm" "cloudfront_errors" {
  alarm_name          = "${var.project_name}-${var.environment}-cloudfront-4xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = "300"
  statistic           = "Average"
  threshold           = "5"
  alarm_description   = "This metric monitors CloudFront 4xx error rate"

  dimensions = {
    DistributionId = aws_cloudfront_distribution.main.id
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-cloudfront-4xx-alarm"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_cloudwatch_metric_alarm" "cloudfront_origin_latency" {
  alarm_name          = "${var.project_name}-${var.environment}-cloudfront-origin-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "OriginLatency"
  namespace           = "AWS/CloudFront"
  period              = "300"
  statistic           = "Average"
  threshold           = "3000" # 3 seconds
  alarm_description   = "This metric monitors CloudFront origin latency"

  dimensions = {
    DistributionId = aws_cloudfront_distribution.main.id
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-cloudfront-latency-alarm"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.main.id
}

output "distribution_arn" {
  description = "CloudFront distribution ARN"
  value       = aws_cloudfront_distribution.main.arn
}

output "distribution_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.main.domain_name
}

output "distribution_hosted_zone_id" {
  description = "CloudFront distribution hosted zone ID"
  value       = aws_cloudfront_distribution.main.hosted_zone_id
}

output "waf_web_acl_arn" {
  description = "WAF Web ACL ARN"
  value       = var.enable_waf ? aws_wafv2_web_acl.cloudfront[0].arn : null
}

output "logs_bucket_name" {
  description = "CloudFront logs bucket name"
  value       = var.enable_logging ? aws_s3_bucket.cloudfront_logs[0].bucket : null
}

# Reference S3 buckets (assuming they exist from s3_storage_module)
data "aws_s3_bucket" "content" {
  bucket = var.s3_content_bucket
}

data "aws_s3_bucket" "media" {
  bucket = var.s3_media_bucket
}