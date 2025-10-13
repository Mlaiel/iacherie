# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade certificate management for Ainflue platform
# Supports multi-cloud SSL/TLS certificate provisioning and management
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# Variables for certificate management
variable "domain_name" {
  description = "Primary domain name for Ainflue platform"
  type        = string
  default     = "ainflue.com"
}

variable "subject_alternative_names" {
  description = "Subject Alternative Names for the certificate"
  type        = list(string)
  default     = [
    "*.ainflue.com",
    "api.ainflue.com",
    "mobile.ainflue.com",
    "ai.ainflue.com",
    "creators.ainflue.com",
    "analytics.ainflue.com"
  ]
}

variable "environment" {
  description = "Environment (production, staging, development)"
  type        = string
  default     = "production"
}

variable "auto_renewal_enabled" {
  description = "Enable automatic certificate renewal"
  type        = bool
  default     = true
}

# Data sources for Route 53 hosted zone
data "aws_route53_zone" "main" {
  name         = var.domain_name
  private_zone = false
}

# ACM Certificate for AWS CloudFront and Load Balancers
resource "aws_acm_certificate" "ainflue_primary" {
  domain_name               = var.domain_name
  subject_alternative_names = var.subject_alternative_names
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "ainflue-${var.environment}-primary-cert"
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Primary SSL certificate for Ainflue platform"
    AutoRenewal = var.auto_renewal_enabled
  }
}

# Route 53 validation records
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.ainflue_primary.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.main.zone_id
}

# Certificate validation
resource "aws_acm_certificate_validation" "ainflue_primary" {
  certificate_arn         = aws_acm_certificate.ainflue_primary.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]

  timeouts {
    create = "10m"
  }
}

# Regional ACM certificate for API Gateway (us-east-1)
resource "aws_acm_certificate" "ainflue_api_gateway" {
  provider = aws.us_east_1
  
  domain_name               = "api.${var.domain_name}"
  subject_alternative_names = ["mobile.${var.domain_name}", "ai.${var.domain_name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "ainflue-${var.environment}-api-gateway-cert"
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "API Gateway SSL certificate"
    Region      = "us-east-1"
  }
}

# Certificate for creator subdomain
resource "aws_acm_certificate" "ainflue_creators" {
  domain_name       = "creators.${var.domain_name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "ainflue-${var.environment}-creators-cert"
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Creators platform SSL certificate"
  }
}

# Google Cloud SSL Certificate
resource "google_compute_managed_ssl_certificate" "ainflue_gcp" {
  name = "ainflue-${var.environment}-ssl-cert"

  managed {
    domains = [
      var.domain_name,
      "www.${var.domain_name}",
      "api.${var.domain_name}",
      "gcp.${var.domain_name}"
    ]
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Azure Key Vault for certificate storage
resource "azurerm_key_vault" "ainflue_certs" {
  name                = "ainflue-${var.environment}-certs"
  location            = var.azure_location
  resource_group_name = var.azure_resource_group
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "premium"

  enabled_for_deployment         = true
  enabled_for_template_deployment = true
  enabled_for_disk_encryption     = true
  soft_delete_retention_days      = 90
  purge_protection_enabled        = true

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    
    ip_rules = var.allowed_ip_ranges
    
    virtual_network_subnet_ids = var.allowed_subnet_ids
  }

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Certificate management"
  }
}

# Azure Key Vault access policy
resource "azurerm_key_vault_access_policy" "certificate_admin" {
  key_vault_id = azurerm_key_vault.ainflue_certs.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  certificate_permissions = [
    "Backup",
    "Create",
    "Delete",
    "DeleteIssuers",
    "Get",
    "GetIssuers",
    "Import",
    "List",
    "ListIssuers",
    "ManageContacts",
    "ManageIssuers",
    "Purge",
    "Recover",
    "Restore",
    "SetIssuers",
    "Update"
  ]

  secret_permissions = [
    "Backup",
    "Delete",
    "Get",
    "List",
    "Purge",
    "Recover",
    "Restore",
    "Set"
  ]
}

# Azure App Service Certificate
resource "azurerm_app_service_certificate" "ainflue_azure" {
  name                = "ainflue-${var.environment}-app-cert"
  resource_group_name = var.azure_resource_group
  location            = var.azure_location
  key_vault_secret_id = azurerm_key_vault_certificate.ainflue_azure.secret_id
  
  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Azure App Service certificate"
  }
}

# Certificate monitoring and alerting
resource "aws_cloudwatch_metric_alarm" "certificate_expiry" {
  alarm_name          = "ainflue-${var.environment}-cert-expiry"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DaysUntilExpiry"
  namespace           = "AWS/CertificateManager"
  period              = "86400"  # 24 hours
  statistic           = "Minimum"
  threshold           = "30"      # Alert 30 days before expiry
  alarm_description   = "This metric monitors Ainflue certificate expiry"
  alarm_actions       = [aws_sns_topic.certificate_alerts.arn]

  dimensions = {
    CertificateArn = aws_acm_certificate.ainflue_primary.arn
  }

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Certificate expiry monitoring"
  }
}

# SNS topic for certificate alerts
resource "aws_sns_topic" "certificate_alerts" {
  name = "ainflue-${var.environment}-certificate-alerts"

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Certificate management alerts"
  }
}

# Lambda function for certificate renewal automation
resource "aws_lambda_function" "cert_renewal" {
  filename         = "cert_renewal.zip"
  function_name    = "ainflue-${var.environment}-cert-renewal"
  role            = aws_iam_role.cert_renewal_lambda.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 300

  environment {
    variables = {
      DOMAIN_NAME = var.domain_name
      ENVIRONMENT = var.environment
      SNS_TOPIC_ARN = aws_sns_topic.certificate_alerts.arn
    }
  }

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Automated certificate renewal"
  }
}

# IAM role for Lambda certificate renewal
resource "aws_iam_role" "cert_renewal_lambda" {
  name = "ainflue-${var.environment}-cert-renewal-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Certificate renewal automation"
  }
}

# IAM policy for certificate management
resource "aws_iam_role_policy" "cert_renewal_policy" {
  name = "ainflue-${var.environment}-cert-renewal-policy"
  role = aws_iam_role.cert_renewal_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "acm:*",
          "route53:*",
          "sns:Publish",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# EventBridge rule for automated certificate checks
resource "aws_cloudwatch_event_rule" "cert_check_schedule" {
  name                = "ainflue-${var.environment}-cert-check"
  description         = "Trigger certificate check daily"
  schedule_expression = "rate(1 day)"

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Certificate monitoring schedule"
  }
}

# EventBridge target for Lambda
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.cert_check_schedule.name
  target_id = "TriggerLambda"
  arn       = aws_lambda_function.cert_renewal.arn
}

# Lambda permission for EventBridge
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cert_renewal.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cert_check_schedule.arn
}

# Outputs
output "aws_certificate_arn" {
  description = "ARN of the primary AWS ACM certificate"
  value       = aws_acm_certificate.ainflue_primary.arn
}

output "aws_api_certificate_arn" {
  description = "ARN of the API Gateway ACM certificate"
  value       = aws_acm_certificate.ainflue_api_gateway.arn
}

output "gcp_certificate_name" {
  description = "Name of the GCP managed SSL certificate"
  value       = google_compute_managed_ssl_certificate.ainflue_gcp.name
}

output "azure_keyvault_id" {
  description = "ID of the Azure Key Vault for certificates"
  value       = azurerm_key_vault.ainflue_certs.id
}

output "certificate_monitoring_topic_arn" {
  description = "ARN of the SNS topic for certificate alerts"
  value       = aws_sns_topic.certificate_alerts.arn
}

output "certificate_domains" {
  description = "List of domains covered by certificates"
  value = concat(
    [var.domain_name],
    var.subject_alternative_names
  )
}