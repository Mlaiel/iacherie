# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade secrets management for Ainflue platform
# Supports multi-cloud secrets storage, rotation, and access control
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# Variables for secrets management
variable "environment" {
  description = "Environment (production, staging, development)"
  type        = string
  default     = "production"
}

variable "enable_automatic_rotation" {
  description = "Enable automatic secret rotation"
  type        = bool
  default     = true
}

variable "rotation_interval_days" {
  description = "Number of days between secret rotations"
  type        = number
  default     = 30
}

variable "allowed_principals" {
  description = "List of principals allowed to access secrets"
  type        = list(string)
  default     = []
}

# AWS Secrets Manager for database credentials
resource "aws_secretsmanager_secret" "database_credentials" {
  name                    = "ainflue/${var.environment}/database/credentials"
  description             = "Ainflue database connection credentials"
  recovery_window_in_days = 30

  tags = {
    Name        = "ainflue-${var.environment}-db-credentials"
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Database authentication"
    Rotation    = var.enable_automatic_rotation ? "enabled" : "disabled"
  }
}

# Database credentials secret value
resource "aws_secretsmanager_secret_version" "database_credentials" {
  secret_id = aws_secretsmanager_secret.database_credentials.id
  secret_string = jsonencode({
    username = "ainflue_admin"
    password = random_password.database_password.result
    engine   = "postgres"
    host     = "ainflue-${var.environment}-db.cluster-xyz.region.rds.amazonaws.com"
    port     = 5432
    dbname   = "ainflue"
  })
}

# Random password for database
resource "random_password" "database_password" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# AWS Secrets Manager for Redis credentials
resource "aws_secretsmanager_secret" "redis_credentials" {
  name                    = "ainflue/${var.environment}/redis/credentials"
  description             = "Ainflue Redis connection credentials"
  recovery_window_in_days = 30

  tags = {
    Name        = "ainflue-${var.environment}-redis-credentials"
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Redis authentication"
  }
}

# Redis credentials secret value
resource "aws_secretsmanager_secret_version" "redis_credentials" {
  secret_id = aws_secretsmanager_secret.redis_credentials.id
  secret_string = jsonencode({
    auth_token = random_password.redis_auth_token.result
    host       = "ainflue-${var.environment}-redis.cache.amazonaws.com"
    port       = 6379
    ssl        = true
  })
}

# Random auth token for Redis
resource "random_password" "redis_auth_token" {
  length  = 64
  special = false
  upper   = true
  lower   = true
  numeric = true
}

# AWS Secrets Manager for API keys
resource "aws_secretsmanager_secret" "api_keys" {
  name                    = "ainflue/${var.environment}/api/keys"
  description             = "Ainflue API keys and tokens"
  recovery_window_in_days = 30

  tags = {
    Name        = "ainflue-${var.environment}-api-keys"
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "API authentication"
  }
}

# API keys secret value
resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    jwt_secret_key     = random_password.jwt_secret.result
    openai_api_key     = var.openai_api_key
    google_api_key     = var.google_api_key
    azure_api_key      = var.azure_api_key
    stripe_secret_key  = var.stripe_secret_key
    paypal_client_secret = var.paypal_client_secret
  })
}

# Random JWT secret
resource "random_password" "jwt_secret" {
  length  = 64
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# AWS Secrets Manager for encryption keys
resource "aws_secretsmanager_secret" "encryption_keys" {
  name                    = "ainflue/${var.environment}/encryption/keys"
  description             = "Ainflue encryption keys for data protection"
  recovery_window_in_days = 30

  tags = {
    Name        = "ainflue-${var.environment}-encryption-keys"
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Data encryption"
  }
}

# Encryption keys secret value
resource "aws_secretsmanager_secret_version" "encryption_keys" {
  secret_id = aws_secretsmanager_secret.encryption_keys.id
  secret_string = jsonencode({
    content_encryption_key = random_password.content_encryption_key.result
    pii_encryption_key     = random_password.pii_encryption_key.result
    payment_encryption_key = random_password.payment_encryption_key.result
    ai_model_encryption_key = random_password.ai_model_encryption_key.result
  })
}

# Random encryption keys
resource "random_password" "content_encryption_key" {
  length  = 64
  special = false
  upper   = true
  lower   = true
  numeric = true
}

resource "random_password" "pii_encryption_key" {
  length  = 64
  special = false
  upper   = true
  lower   = true
  numeric = true
}

resource "random_password" "payment_encryption_key" {
  length  = 64
  special = false
  upper   = true
  lower   = true
  numeric = true
}

resource "random_password" "ai_model_encryption_key" {
  length  = 64
  special = false
  upper   = true
  lower   = true
  numeric = true
}

# AWS Secrets Manager for OAuth credentials
resource "aws_secretsmanager_secret" "oauth_credentials" {
  name                    = "ainflue/${var.environment}/oauth/credentials"
  description             = "Ainflue OAuth provider credentials"
  recovery_window_in_days = 30

  tags = {
    Name        = "ainflue-${var.environment}-oauth-credentials"
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "OAuth authentication"
  }
}

# OAuth credentials secret value
resource "aws_secretsmanager_secret_version" "oauth_credentials" {
  secret_id = aws_secretsmanager_secret.oauth_credentials.id
  secret_string = jsonencode({
    google_client_id     = var.google_oauth_client_id
    google_client_secret = var.google_oauth_client_secret
    facebook_app_id      = var.facebook_app_id
    facebook_app_secret  = var.facebook_app_secret
    twitter_api_key      = var.twitter_api_key
    twitter_api_secret   = var.twitter_api_secret
    linkedin_client_id   = var.linkedin_client_id
    linkedin_client_secret = var.linkedin_client_secret
  })
}

# Automatic rotation for database credentials
resource "aws_secretsmanager_secret_rotation" "database_rotation" {
  count = var.enable_automatic_rotation ? 1 : 0
  
  secret_id           = aws_secretsmanager_secret.database_credentials.id
  rotation_lambda_arn = aws_lambda_function.secret_rotation[0].arn

  rotation_rules {
    automatically_after_days = var.rotation_interval_days
  }
}

# Lambda function for secret rotation
resource "aws_lambda_function" "secret_rotation" {
  count = var.enable_automatic_rotation ? 1 : 0
  
  filename         = "secret_rotation.zip"
  function_name    = "ainflue-${var.environment}-secret-rotation"
  role            = aws_iam_role.secret_rotation_lambda[0].arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300

  environment {
    variables = {
      SECRETS_MANAGER_ENDPOINT = "https://secretsmanager.${data.aws_region.current.name}.amazonaws.com"
      ENVIRONMENT             = var.environment
    }
  }

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Automated secret rotation"
  }
}

# IAM role for secret rotation Lambda
resource "aws_iam_role" "secret_rotation_lambda" {
  count = var.enable_automatic_rotation ? 1 : 0
  
  name = "ainflue-${var.environment}-secret-rotation-lambda"

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
    Purpose     = "Secret rotation automation"
  }
}

# IAM policy for secret rotation
resource "aws_iam_role_policy" "secret_rotation_policy" {
  count = var.enable_automatic_rotation ? 1 : 0
  
  name = "ainflue-${var.environment}-secret-rotation-policy"
  role = aws_iam_role.secret_rotation_lambda[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:*",
          "rds:*",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Google Cloud Secret Manager
resource "google_secret_manager_secret" "ainflue_gcp_secrets" {
  secret_id = "ainflue-${var.environment}-credentials"

  replication {
    automatic = true
  }

  labels = {
    environment = var.environment
    project     = "ainflue"
    purpose     = "application-credentials"
  }
}

# GCP secret version
resource "google_secret_manager_secret_version" "ainflue_gcp_version" {
  secret = google_secret_manager_secret.ainflue_gcp_secrets.id

  secret_data = jsonencode({
    database_url    = "postgresql://user:pass@host:5432/db"
    redis_url       = "redis://user:pass@host:6379/0"
    storage_bucket  = "ainflue-${var.environment}-storage"
    service_account = var.gcp_service_account_key
  })
}

# Azure Key Vault for secrets
resource "azurerm_key_vault" "ainflue_secrets" {
  name                = "ainflue-${var.environment}-secrets"
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
    Purpose     = "Secrets management"
  }
}

# Azure Key Vault access policy
resource "azurerm_key_vault_access_policy" "secrets_admin" {
  key_vault_id = azurerm_key_vault.ainflue_secrets.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

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

  key_permissions = [
    "Backup",
    "Create",
    "Decrypt",
    "Delete",
    "Encrypt",
    "Get",
    "Import",
    "List",
    "Purge",
    "Recover",
    "Restore",
    "Sign",
    "UnwrapKey",
    "Update",
    "Verify",
    "WrapKey"
  ]
}

# Azure Key Vault secrets
resource "azurerm_key_vault_secret" "database_connection" {
  name         = "database-connection-string"
  value        = "Server=ainflue-${var.environment}-db.database.windows.net;Database=ainflue;User Id=admin;Password=${random_password.azure_db_password.result};"
  key_vault_id = azurerm_key_vault.ainflue_secrets.id

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Database connection"
  }
}

resource "random_password" "azure_db_password" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# Secret monitoring and alerting
resource "aws_cloudwatch_metric_alarm" "secret_access_anomaly" {
  alarm_name          = "ainflue-${var.environment}-secret-access-anomaly"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "GetSecretValue"
  namespace           = "AWS/SecretsManager"
  period              = "300"
  statistic           = "Sum"
  threshold           = "100"
  alarm_description   = "This metric monitors unusual secret access patterns"
  alarm_actions       = [aws_sns_topic.security_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Security monitoring"
  }
}

# SNS topic for security alerts
resource "aws_sns_topic" "security_alerts" {
  name = "ainflue-${var.environment}-security-alerts"

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
    Purpose     = "Security incident alerts"
  }
}

# Data sources
data "aws_region" "current" {}
data "azurerm_client_config" "current" {}

# Variable declarations for external inputs
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "google_api_key" {
  description = "Google API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "azure_api_key" {
  description = "Azure API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "stripe_secret_key" {
  description = "Stripe secret key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "paypal_client_secret" {
  description = "PayPal client secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "google_oauth_client_id" {
  description = "Google OAuth client ID"
  type        = string
  default     = ""
}

variable "google_oauth_client_secret" {
  description = "Google OAuth client secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "facebook_app_id" {
  description = "Facebook app ID"
  type        = string
  default     = ""
}

variable "facebook_app_secret" {
  description = "Facebook app secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "twitter_api_key" {
  description = "Twitter API key"
  type        = string
  default     = ""
}

variable "twitter_api_secret" {
  description = "Twitter API secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "linkedin_client_id" {
  description = "LinkedIn client ID"
  type        = string
  default     = ""
}

variable "linkedin_client_secret" {
  description = "LinkedIn client secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "azure_location" {
  description = "Azure location"
  type        = string
  default     = "East US"
}

variable "azure_resource_group" {
  description = "Azure resource group name"
  type        = string
  default     = "ainflue-resources"
}

variable "allowed_ip_ranges" {
  description = "Allowed IP ranges for Key Vault access"
  type        = list(string)
  default     = []
}

variable "allowed_subnet_ids" {
  description = "Allowed subnet IDs for Key Vault access"
  type        = list(string)
  default     = []
}

variable "gcp_service_account_key" {
  description = "GCP service account key JSON"
  type        = string
  sensitive   = true
  default     = ""
}

# Outputs
output "aws_database_secret_arn" {
  description = "ARN of the database credentials secret"
  value       = aws_secretsmanager_secret.database_credentials.arn
}

output "aws_redis_secret_arn" {
  description = "ARN of the Redis credentials secret"
  value       = aws_secretsmanager_secret.redis_credentials.arn
}

output "aws_api_keys_secret_arn" {
  description = "ARN of the API keys secret"
  value       = aws_secretsmanager_secret.api_keys.arn
}

output "gcp_secret_id" {
  description = "ID of the GCP secret"
  value       = google_secret_manager_secret.ainflue_gcp_secrets.secret_id
}

output "azure_keyvault_id" {
  description = "ID of the Azure Key Vault"
  value       = azurerm_key_vault.ainflue_secrets.id
}

output "security_alerts_topic_arn" {
  description = "ARN of the security alerts SNS topic"
  value       = aws_sns_topic.security_alerts.arn
}