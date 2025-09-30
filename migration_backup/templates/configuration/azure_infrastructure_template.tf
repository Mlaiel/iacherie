# =====================================================================================
# Azure Infrastructure Template - Ainflue Configuration Module
# =====================================================================================
# © 2025 Fahed Mlaiel <mlaiel@live.de>
# TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
# Utilisation commerciale INTERDITE sans autorisation écrite
# =====================================================================================

# Provider Configuration
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.45"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
    
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    
    cognitive_account {
      purge_soft_delete_on_destroy = true
    }
  }
}

# Local Variables
locals {
  # Ainflue Creator Economy Configuration
  project_name = var.project_name
  environment  = var.environment
  location     = var.location
  
  # Naming convention
  resource_prefix = "${local.project_name}-${local.environment}"
  
  # Common tags for all resources
  common_tags = {
    Project            = "Ainflue"
    Environment        = local.environment
    Owner              = "Fahed Mlaiel"
    BusinessUnit       = "Creator Economy"
    CostCenter         = "Infrastructure"
    ManagedBy          = "Terraform"
    SecurityLevel      = var.security_level
    ComplianceLevel    = var.compliance_level
    BackupPolicy       = var.backup_policy
    MonitoringLevel    = var.monitoring_level
    CreatedDate        = formatdate("YYYY-MM-DD", timestamp())
  }
  
  # Creator Economy Services
  creator_services = [
    "content-processing",
    "ai-enhancement", 
    "protection-engine",
    "monetization-platform",
    "collaboration-hub",
    "analytics-engine",
    "distribution-network",
    "gamification-system"
  ]
  
  # Network configuration
  vnet_address_space = ["10.0.0.0/16"]
  subnet_configs = {
    aks = {
      name             = "aks-subnet"
      address_prefixes = ["10.0.1.0/24"]
    }
    database = {
      name             = "database-subnet"
      address_prefixes = ["10.0.2.0/24"]
    }
    application_gateway = {
      name             = "appgw-subnet"
      address_prefixes = ["10.0.3.0/24"]
    }
    private_endpoints = {
      name             = "private-endpoints-subnet"
      address_prefixes = ["10.0.4.0/24"]
    }
  }
}

# =====================================================================================
# RESOURCE GROUP
# =====================================================================================

resource "azurerm_resource_group" "main" {
  name     = "${local.resource_prefix}-rg"
  location = local.location
  
  tags = local.common_tags
}

# =====================================================================================
# NETWORKING
# =====================================================================================

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${local.resource_prefix}-vnet"
  address_space       = local.vnet_address_space
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  tags = local.common_tags
}

# Subnets
resource "azurerm_subnet" "subnets" {
  for_each = local.subnet_configs
  
  name                 = "${local.resource_prefix}-${each.value.name}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = each.value.address_prefixes
  
  # Service endpoints
  service_endpoints = [
    "Microsoft.Storage",
    "Microsoft.Sql",
    "Microsoft.KeyVault",
    "Microsoft.CognitiveServices"
  ]
}

# Network Security Groups
resource "azurerm_network_security_group" "aks" {
  name                = "${local.resource_prefix}-aks-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # Allow AKS traffic
  security_rule {
    name                       = "AllowAKSTraffic"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }

  # Allow HTTPS
  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = local.common_tags
}

# Associate NSG with AKS subnet
resource "azurerm_subnet_network_security_group_association" "aks" {
  subnet_id                 = azurerm_subnet.subnets["aks"].id
  network_security_group_id = azurerm_network_security_group.aks.id
}

# Public IP for Application Gateway
resource "azurerm_public_ip" "app_gateway" {
  name                = "${local.resource_prefix}-appgw-pip"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
  sku                 = "Standard"
  
  tags = local.common_tags
}

# =====================================================================================
# AZURE KUBERNETES SERVICE (AKS)
# =====================================================================================

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${local.resource_prefix}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${local.resource_prefix}-aks"
  
  # Kubernetes version
  kubernetes_version = var.kubernetes_version
  
  # Default node pool
  default_node_pool {
    name                = "default"
    node_count          = var.default_node_count
    vm_size             = var.default_vm_size
    os_disk_size_gb     = var.default_disk_size_gb
    vnet_subnet_id      = azurerm_subnet.subnets["aks"].id
    type                = "VirtualMachineScaleSets"
    
    # Auto-scaling
    enable_auto_scaling = true
    min_count          = var.min_node_count
    max_count          = var.max_node_count
    
    # Node labels
    node_labels = {
      "nodepool-type" = "default"
      "environment"   = local.environment
      "business-unit" = "creator-economy"
    }
    
    # Node taints for system workloads
    node_taints = [
      "CriticalAddonsOnly=true:NoSchedule"
    ]
    
    tags = local.common_tags
  }
  
  # Identity
  identity {
    type = "SystemAssigned"
  }
  
  # Network profile
  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = "10.1.0.0/16"
    dns_service_ip    = "10.1.0.10"
  }
  
  # Azure AD integration
  azure_active_directory_role_based_access_control {
    managed                = true
    admin_group_object_ids = var.aks_admin_group_object_ids
    azure_rbac_enabled     = true
  }
  
  # Add-ons
  ingress_application_gateway {
    gateway_id = azurerm_application_gateway.main.id
  }
  
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }
  
  azure_policy_enabled = true
  
  # Key Vault integration
  key_vault_secrets_provider {
    secret_rotation_enabled  = true
    secret_rotation_interval = "2m"
  }
  
  # Auto-upgrade
  automatic_channel_upgrade = "patch"
  
  # Maintenance window
  maintenance_window {
    allowed {
      day   = "Sunday"
      hours = [2, 3, 4]
    }
  }
  
  tags = local.common_tags
  
  depends_on = [
    azurerm_role_assignment.aks_network_contributor,
    azurerm_application_gateway.main
  ]
}

# User node pool for creator workloads
resource "azurerm_kubernetes_cluster_node_pool" "creator_workloads" {
  name                  = "creators"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size              = var.creator_vm_size
  node_count           = var.creator_node_count
  os_disk_size_gb      = var.creator_disk_size_gb
  vnet_subnet_id       = azurerm_subnet.subnets["aks"].id
  
  # Auto-scaling
  enable_auto_scaling = true
  min_count          = var.creator_min_nodes
  max_count          = var.creator_max_nodes
  
  # Node labels
  node_labels = {
    "nodepool-type" = "creator-workloads"
    "environment"   = local.environment
    "workload-type" = "user"
  }
  
  # Taints for creator workloads
  node_taints = [
    "workload=creator:NoSchedule"
  ]
  
  tags = local.common_tags
}

# GPU node pool for AI processing
resource "azurerm_kubernetes_cluster_node_pool" "gpu" {
  count = var.enable_gpu_nodes ? 1 : 0
  
  name                  = "gpu"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size              = var.gpu_vm_size
  node_count           = var.gpu_node_count
  os_disk_size_gb      = var.gpu_disk_size_gb
  vnet_subnet_id       = azurerm_subnet.subnets["aks"].id
  
  # Auto-scaling
  enable_auto_scaling = true
  min_count          = 0
  max_count          = var.gpu_max_nodes
  
  # Node labels
  node_labels = {
    "nodepool-type"    = "gpu"
    "environment"      = local.environment
    "accelerator"      = "nvidia-gpu"
  }
  
  # Taints for GPU workloads
  node_taints = [
    "nvidia.com/gpu=true:NoSchedule"
  ]
  
  tags = local.common_tags
}

# =====================================================================================
# APPLICATION GATEWAY
# =====================================================================================

resource "azurerm_application_gateway" "main" {
  name                = "${local.resource_prefix}-appgw"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  
  sku {
    name     = var.app_gateway_sku_name
    tier     = var.app_gateway_sku_tier
    capacity = var.app_gateway_capacity
  }
  
  gateway_ip_configuration {
    name      = "appGatewayIpConfig"
    subnet_id = azurerm_subnet.subnets["application_gateway"].id
  }
  
  frontend_port {
    name = "http"
    port = 80
  }
  
  frontend_port {
    name = "https"
    port = 443
  }
  
  frontend_ip_configuration {
    name                 = "appGatewayFrontendIP"
    public_ip_address_id = azurerm_public_ip.app_gateway.id
  }
  
  backend_address_pool {
    name = "appGatewayBackendPool"
  }
  
  backend_http_settings {
    name                  = "appGatewayBackendHttpSettings"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 60
  }
  
  http_listener {
    name                           = "appGatewayHttpListener"
    frontend_ip_configuration_name = "appGatewayFrontendIP"
    frontend_port_name            = "http"
    protocol                      = "Http"
  }
  
  request_routing_rule {
    name                       = "appGatewayRule"
    rule_type                  = "Basic"
    http_listener_name         = "appGatewayHttpListener"
    backend_address_pool_name  = "appGatewayBackendPool"
    backend_http_settings_name = "appGatewayBackendHttpSettings"
    priority                   = 100
  }
  
  # WAF configuration
  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
    
    # Disable specific rules if needed
    disabled_rule_group {
      rule_group_name = "REQUEST-920-PROTOCOL-ENFORCEMENT"
      rules           = [920300, 920440]
    }
  }
  
  tags = local.common_tags
}

# =====================================================================================
# AZURE DATABASE FOR POSTGRESQL
# =====================================================================================

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${local.resource_prefix}-postgresql"
  resource_group_name    = azurerm_resource_group.main.name
  location              = azurerm_resource_group.main.location
  version               = var.postgresql_version
  
  administrator_login    = var.postgresql_admin_username
  administrator_password = var.postgresql_admin_password
  
  # Compute and storage
  sku_name   = var.postgresql_sku_name
  storage_mb = var.postgresql_storage_mb
  
  # Network
  delegated_subnet_id = azurerm_subnet.subnets["database"].id
  private_dns_zone_id = azurerm_private_dns_zone.postgresql.id
  
  # Backup
  backup_retention_days        = var.postgresql_backup_retention_days
  geo_redundant_backup_enabled = var.postgresql_geo_redundant_backup
  
  # High availability
  dynamic "high_availability" {
    for_each = var.postgresql_high_availability ? [1] : []
    content {
      mode = "ZoneRedundant"
    }
  }
  
  # Maintenance window
  maintenance_window {
    day_of_week  = 0  # Sunday
    start_hour   = 3
    start_minute = 0
  }
  
  tags = local.common_tags
  
  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgresql]
}

# PostgreSQL database
resource "azurerm_postgresql_flexible_server_database" "ainflue" {
  name      = "ainflue_${local.environment}"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# PostgreSQL firewall rules
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Private DNS Zone for PostgreSQL
resource "azurerm_private_dns_zone" "postgresql" {
  name                = "${local.resource_prefix}-postgresql.private.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
  
  tags = local.common_tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgresql" {
  name                  = "${local.resource_prefix}-postgresql-vnet-link"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.postgresql.name
  virtual_network_id    = azurerm_virtual_network.main.id
  
  tags = local.common_tags
}

# =====================================================================================
# AZURE CACHE FOR REDIS
# =====================================================================================

resource "azurerm_redis_cache" "main" {
  name                = "${local.resource_prefix}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = var.redis_capacity
  family              = var.redis_family
  sku_name            = var.redis_sku_name
  
  # Network
  subnet_id = azurerm_subnet.subnets["private_endpoints"].id
  
  # Security
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  
  # Auth
  redis_configuration {
    enable_authentication = true
  }
  
  # Backup
  redis_configuration {
    rdb_backup_enabled            = var.redis_backup_enabled
    rdb_backup_frequency          = var.redis_backup_frequency
    rdb_backup_max_snapshot_count = var.redis_backup_max_snapshots
    rdb_storage_connection_string = azurerm_storage_account.main.primary_blob_connection_string
  }
  
  # Patch schedule
  patch_schedule {
    day_of_week    = "Sunday"
    start_hour_utc = 3
  }
  
  tags = local.common_tags
}

# =====================================================================================
# STORAGE ACCOUNT
# =====================================================================================

resource "azurerm_storage_account" "main" {
  name                     = "${replace(local.resource_prefix, "-", "")}storage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_replication_type
  account_kind             = "StorageV2"
  
  # Security
  enable_https_traffic_only      = true
  min_tls_version               = "TLS1_2"
  allow_nested_items_to_be_public = false
  
  # Advanced threat protection
  threat_protection_enabled = true
  
  # Blob properties
  blob_properties {
    versioning_enabled = true
    
    # Soft delete
    delete_retention_policy {
      days = var.blob_soft_delete_retention_days
    }
    
    # Container soft delete
    container_delete_retention_policy {
      days = var.container_soft_delete_retention_days
    }
    
    # CORS for creator uploads
    cors_rule {
      allowed_headers    = ["*"]
      allowed_methods    = ["GET", "HEAD", "PUT", "POST", "DELETE"]
      allowed_origins    = var.allowed_cors_origins
      exposed_headers    = ["*"]
      max_age_in_seconds = 3600
    }
  }
  
  # Network rules
  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = [azurerm_subnet.subnets["aks"].id]
    ip_rules                   = var.storage_allowed_ips
  }
  
  tags = local.common_tags
}

# Storage containers
resource "azurerm_storage_container" "containers" {
  for_each = toset([
    "content-uploads",
    "processed-content", 
    "backups",
    "logs",
    "assets"
  ])
  
  name                  = each.value
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# =====================================================================================
# KEY VAULT
# =====================================================================================

# Current client data
data "azurerm_client_config" "current" {}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                = "${local.resource_prefix}-kv"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "premium"
  
  # Security features
  enabled_for_disk_encryption     = true
  enabled_for_deployment          = true
  enabled_for_template_deployment = true
  enable_rbac_authorization       = true
  purge_protection_enabled        = true
  soft_delete_retention_days      = 90
  
  # Network ACLs
  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    
    virtual_network_subnet_ids = [
      azurerm_subnet.subnets["aks"].id,
      azurerm_subnet.subnets["private_endpoints"].id
    ]
    
    ip_rules = var.keyvault_allowed_ips
  }
  
  tags = local.common_tags
}

# Key Vault secrets
resource "azurerm_key_vault_secret" "secrets" {
  for_each = var.key_vault_secrets
  
  name         = each.key
  value        = each.value
  key_vault_id = azurerm_key_vault.main.id
  
  content_type = "text/plain"
  
  depends_on = [azurerm_role_assignment.current_user_kv_admin]
}

# =====================================================================================
# COGNITIVE SERVICES
# =====================================================================================

# Cognitive Services account for AI processing
resource "azurerm_cognitive_account" "main" {
  name                = "${local.resource_prefix}-cognitive"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "CognitiveServices"
  sku_name            = var.cognitive_services_sku
  
  # Network access
  network_acls {
    default_action = "Deny"
    
    virtual_network_rules {
      subnet_id = azurerm_subnet.subnets["aks"].id
    }
    
    ip_rules = var.cognitive_services_allowed_ips
  }
  
  # Identity
  identity {
    type = "SystemAssigned"
  }
  
  tags = local.common_tags
}

# Computer Vision for content analysis
resource "azurerm_cognitive_account" "computer_vision" {
  name                = "${local.resource_prefix}-computer-vision"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "ComputerVision"
  sku_name            = var.computer_vision_sku
  
  tags = local.common_tags
}

# Speech Services for audio processing
resource "azurerm_cognitive_account" "speech" {
  name                = "${local.resource_prefix}-speech"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "SpeechServices"
  sku_name            = var.speech_services_sku
  
  tags = local.common_tags
}

# Text Analytics for content understanding
resource "azurerm_cognitive_account" "text_analytics" {
  name                = "${local.resource_prefix}-text-analytics"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "TextAnalytics"
  sku_name            = var.text_analytics_sku
  
  tags = local.common_tags
}

# =====================================================================================
# MONITORING AND LOGGING
# =====================================================================================

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${local.resource_prefix}-law"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = var.log_analytics_sku
  retention_in_days   = var.log_analytics_retention_days
  
  tags = local.common_tags
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "${local.resource_prefix}-appinsights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  
  tags = local.common_tags
}

# Action Group for alerts
resource "azurerm_monitor_action_group" "main" {
  name                = "${local.resource_prefix}-action-group"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "ainflue"
  
  email_receiver {
    name          = "admin"
    email_address = var.alert_email
  }
  
  webhook_receiver {
    name        = "slack"
    service_uri = var.slack_webhook_url
  }
  
  tags = local.common_tags
}

# Metric alerts
resource "azurerm_monitor_metric_alert" "cpu_usage" {
  name                = "${local.resource_prefix}-cpu-alert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_kubernetes_cluster.main.id]
  description         = "Alert when CPU usage is high"
  
  criteria {
    metric_namespace = "Microsoft.ContainerService/managedClusters"
    metric_name      = "cpu_usage_percentage"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 80
  }
  
  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
  
  tags = local.common_tags
}

# =====================================================================================
# RBAC AND PERMISSIONS
# =====================================================================================

# Network Contributor role for AKS
resource "azurerm_role_assignment" "aks_network_contributor" {
  scope                = azurerm_virtual_network.main.id
  role_definition_name = "Network Contributor"
  principal_id         = azurerm_kubernetes_cluster.main.identity[0].principal_id
}

# Key Vault Administrator for current user
resource "azurerm_role_assignment" "current_user_kv_admin" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
}

# Storage Blob Data Contributor for AKS
resource "azurerm_role_assignment" "aks_storage_contributor" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_kubernetes_cluster.main.identity[0].principal_id
}

# =====================================================================================
# VARIABLES
# =====================================================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "ainflue"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "West Europe"
}

# Security and compliance
variable "security_level" {
  description = "Security level for resources"
  type        = string
  default     = "high"
}

variable "compliance_level" {
  description = "Compliance level"
  type        = string
  default     = "enterprise"
}

variable "backup_policy" {
  description = "Backup policy"
  type        = string
  default     = "daily"
}

variable "monitoring_level" {
  description = "Monitoring level"
  type        = string
  default     = "comprehensive"
}

# AKS Configuration
variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28.0"
}

variable "default_node_count" {
  description = "Default node count"
  type        = number
  default     = 3
}

variable "min_node_count" {
  description = "Minimum node count"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum node count"
  type        = number
  default     = 10
}

variable "default_vm_size" {
  description = "Default VM size for nodes"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "default_disk_size_gb" {
  description = "Default disk size in GB"
  type        = number
  default     = 100
}

variable "creator_vm_size" {
  description = "VM size for creator workloads"
  type        = string
  default     = "Standard_D8s_v3"
}

variable "creator_node_count" {
  description = "Initial creator node count"
  type        = number
  default     = 2
}

variable "creator_min_nodes" {
  description = "Minimum creator nodes"
  type        = number
  default     = 1
}

variable "creator_max_nodes" {
  description = "Maximum creator nodes"
  type        = number
  default     = 20
}

variable "creator_disk_size_gb" {
  description = "Creator node disk size in GB"
  type        = number
  default     = 200
}

variable "enable_gpu_nodes" {
  description = "Enable GPU nodes for AI processing"
  type        = bool
  default     = true
}

variable "gpu_vm_size" {
  description = "VM size for GPU nodes"
  type        = string
  default     = "Standard_NC6s_v3"
}

variable "gpu_node_count" {
  description = "Initial GPU node count"
  type        = number
  default     = 1
}

variable "gpu_max_nodes" {
  description = "Maximum GPU nodes"
  type        = number
  default     = 5
}

variable "gpu_disk_size_gb" {
  description = "GPU node disk size in GB"
  type        = number
  default     = 300
}

variable "aks_admin_group_object_ids" {
  description = "Azure AD group object IDs for AKS admins"
  type        = list(string)
  default     = []
}

# Application Gateway Configuration
variable "app_gateway_sku_name" {
  description = "Application Gateway SKU name"
  type        = string
  default     = "WAF_v2"
}

variable "app_gateway_sku_tier" {
  description = "Application Gateway SKU tier"
  type        = string
  default     = "WAF_v2"
}

variable "app_gateway_capacity" {
  description = "Application Gateway capacity"
  type        = number
  default     = 2
}

# Database Configuration
variable "postgresql_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15"
}

variable "postgresql_sku_name" {
  description = "PostgreSQL SKU name"
  type        = string
  default     = "GP_Standard_D4s_v3"
}

variable "postgresql_storage_mb" {
  description = "PostgreSQL storage in MB"
  type        = number
  default     = 32768
}

variable "postgresql_admin_username" {
  description = "PostgreSQL admin username"
  type        = string
  default     = "ainflue_admin"
}

variable "postgresql_admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "postgresql_backup_retention_days" {
  description = "PostgreSQL backup retention days"
  type        = number
  default     = 30
}

variable "postgresql_geo_redundant_backup" {
  description = "Enable geo-redundant backup"
  type        = bool
  default     = true
}

variable "postgresql_high_availability" {
  description = "Enable high availability"
  type        = bool
  default     = true
}

# Redis Configuration
variable "redis_capacity" {
  description = "Redis capacity"
  type        = number
  default     = 2
}

variable "redis_family" {
  description = "Redis family"
  type        = string
  default     = "P"
}

variable "redis_sku_name" {
  description = "Redis SKU name"
  type        = string
  default     = "Premium"
}

variable "redis_backup_enabled" {
  description = "Enable Redis backup"
  type        = bool
  default     = true
}

variable "redis_backup_frequency" {
  description = "Redis backup frequency in minutes"
  type        = number
  default     = 60
}

variable "redis_backup_max_snapshots" {
  description = "Maximum Redis backup snapshots"
  type        = number
  default     = 5
}

# Storage Configuration
variable "storage_account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}

variable "storage_replication_type" {
  description = "Storage replication type"
  type        = string
  default     = "ZRS"
}

variable "blob_soft_delete_retention_days" {
  description = "Blob soft delete retention days"
  type        = number
  default     = 30
}

variable "container_soft_delete_retention_days" {
  description = "Container soft delete retention days"
  type        = number
  default     = 30
}

variable "allowed_cors_origins" {
  description = "Allowed CORS origins"
  type        = list(string)
  default     = ["*"]
}

variable "storage_allowed_ips" {
  description = "Allowed IP addresses for storage"
  type        = list(string)
  default     = []
}

# Key Vault Configuration
variable "keyvault_allowed_ips" {
  description = "Allowed IP addresses for Key Vault"
  type        = list(string)
  default     = []
}

variable "key_vault_secrets" {
  description = "Key Vault secrets"
  type        = map(string)
  default     = {}
  sensitive   = true
}

# Cognitive Services Configuration
variable "cognitive_services_sku" {
  description = "Cognitive Services SKU"
  type        = string
  default     = "S0"
}

variable "computer_vision_sku" {
  description = "Computer Vision SKU"
  type        = string
  default     = "S1"
}

variable "speech_services_sku" {
  description = "Speech Services SKU"
  type        = string
  default     = "S0"
}

variable "text_analytics_sku" {
  description = "Text Analytics SKU"
  type        = string
  default     = "S"
}

variable "cognitive_services_allowed_ips" {
  description = "Allowed IP addresses for Cognitive Services"
  type        = list(string)
  default     = []
}

# Monitoring Configuration
variable "log_analytics_sku" {
  description = "Log Analytics SKU"
  type        = string
  default     = "PerGB2018"
}

variable "log_analytics_retention_days" {
  description = "Log Analytics retention days"
  type        = number
  default     = 90
}

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alerts"
  type        = string
  default     = ""
}

# =====================================================================================
# OUTPUTS
# =====================================================================================

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.name
}

output "aks_cluster_fqdn" {
  description = "FQDN of the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.fqdn
}

output "aks_cluster_kube_config" {
  description = "Kube config for the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive   = true
}

output "postgresql_fqdn" {
  description = "FQDN of the PostgreSQL server"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "redis_hostname" {
  description = "Hostname of the Redis cache"
  value       = azurerm_redis_cache.main.hostname
}

output "redis_primary_access_key" {
  description = "Primary access key for Redis"
  value       = azurerm_redis_cache.main.primary_access_key
  sensitive   = true
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "storage_account_primary_key" {
  description = "Primary key of the storage account"
  value       = azurerm_storage_account.main.primary_access_key
  sensitive   = true
}

output "key_vault_uri" {
  description = "URI of the Key Vault"
  value       = azurerm_key_vault.main.vault_uri
}

output "application_insights_instrumentation_key" {
  description = "Instrumentation key for Application Insights"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Connection string for Application Insights"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "cognitive_services_endpoint" {
  description = "Endpoint for Cognitive Services"
  value       = azurerm_cognitive_account.main.endpoint
}

output "computer_vision_endpoint" {
  description = "Endpoint for Computer Vision"
  value       = azurerm_cognitive_account.computer_vision.endpoint
}

output "speech_services_endpoint" {
  description = "Endpoint for Speech Services"
  value       = azurerm_cognitive_account.speech.endpoint
}

output "text_analytics_endpoint" {
  description = "Endpoint for Text Analytics"
  value       = azurerm_cognitive_account.text_analytics.endpoint
}

output "application_gateway_public_ip" {
  description = "Public IP of the Application Gateway"
  value       = azurerm_public_ip.app_gateway.ip_address
}

output "creator_services" {
  description = "List of creator economy services"
  value       = local.creator_services
}

# =====================================================================================
# END OF TEMPLATE
# =====================================================================================