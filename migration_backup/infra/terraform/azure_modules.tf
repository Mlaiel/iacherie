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

# Azure Resource Group
resource "azurerm_resource_group" "main" {
  count = contains(var.cloud_providers, "azure") ? 1 : 0
  
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.azure_location
  
  tags = var.common_tags
}

# Azure Virtual Network
resource "azurerm_virtual_network" "main" {
  count = contains(var.cloud_providers, "azure") ? 1 : 0
  
  name                = "${var.project_name}-${var.environment}-vnet"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.main[0].location
  resource_group_name = azurerm_resource_group.main[0].name
  
  tags = var.common_tags
}

# Azure Subnets
resource "azurerm_subnet" "private" {
  count = contains(var.cloud_providers, "azure") ? length(var.availability_zones) : 0
  
  name                 = "${var.project_name}-${var.environment}-private-${count.index + 1}"
  resource_group_name  = azurerm_resource_group.main[0].name
  virtual_network_name = azurerm_virtual_network.main[0].name
  address_prefixes     = ["10.1.${count.index + 1}.0/24"]
}

resource "azurerm_subnet" "public" {
  count = contains(var.cloud_providers, "azure") ? length(var.availability_zones) : 0
  
  name                 = "${var.project_name}-${var.environment}-public-${count.index + 1}"
  resource_group_name  = azurerm_resource_group.main[0].name
  virtual_network_name = azurerm_virtual_network.main[0].name
  address_prefixes     = ["10.1.${count.index + 101}.0/24"]
}

# Azure Kubernetes Service (AKS)
resource "azurerm_kubernetes_cluster" "main" {
  count = contains(var.cloud_providers, "azure") ? 1 : 0
  
  name                = "${var.project_name}-${var.environment}-aks"
  location            = azurerm_resource_group.main[0].location
  resource_group_name = azurerm_resource_group.main[0].name
  dns_prefix          = "${var.project_name}-${var.environment}"
  
  kubernetes_version = var.k8s_version
  
  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D2_v2"
    
    vnet_subnet_id = azurerm_subnet.private[0].id
    
    enable_auto_scaling = true
    min_count          = 1
    max_count          = 10
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  network_profile {
    network_plugin = "azure"
    service_cidr   = "10.2.0.0/16"
    dns_service_ip = "10.2.0.10"
  }
  
  tags = var.common_tags
}

# Azure Database for PostgreSQL
resource "azurerm_postgresql_flexible_server" "main" {
  count = contains(var.cloud_providers, "azure") ? 1 : 0
  
  name                   = "${var.project_name}-${var.environment}-postgres"
  resource_group_name    = azurerm_resource_group.main[0].name
  location               = azurerm_resource_group.main[0].location
  version                = "13"
  delegated_subnet_id    = azurerm_subnet.private[0].id
  private_dns_zone_id    = azurerm_private_dns_zone.postgres[0].id
  administrator_login    = "postgres"
  administrator_password = random_password.postgres_password[0].result
  
  zone = "1"
  
  storage_mb   = 32768
  sku_name     = "GP_Standard_D2s_v3"
  
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  
  tags = var.common_tags
  
  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]
}

# Azure Cache for Redis
resource "azurerm_redis_cache" "main" {
  count = contains(var.cloud_providers, "azure") ? 1 : 0
  
  name                = "${var.project_name}-${var.environment}-redis"
  location            = azurerm_resource_group.main[0].location
  resource_group_name = azurerm_resource_group.main[0].name
  capacity            = 1
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  
  redis_configuration {
    enable_authentication = true
  }
  
  tags = var.common_tags
}

# Azure Storage Account
resource "azurerm_storage_account" "main" {
  count = contains(var.cloud_providers, "azure") ? 1 : 0
  
  name                     = "${var.project_name}${var.environment}storage"
  resource_group_name      = azurerm_resource_group.main[0].name
  location                 = azurerm_resource_group.main[0].location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  blob_properties {
    versioning_enabled = true
  }
  
  tags = var.common_tags
}

# Azure Private DNS Zone for PostgreSQL
resource "azurerm_private_dns_zone" "postgres" {
  count = contains(var.cloud_providers, "azure") ? 1 : 0
  
  name                = "${var.project_name}-${var.environment}-postgres.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main[0].name
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  count = contains(var.cloud_providers, "azure") ? 1 : 0
  
  name                  = "${var.project_name}-${var.environment}-postgres-link"
  private_dns_zone_name = azurerm_private_dns_zone.postgres[0].name
  virtual_network_id    = azurerm_virtual_network.main[0].id
  resource_group_name   = azurerm_resource_group.main[0].name
}

# Random password for PostgreSQL
resource "random_password" "postgres_password" {
  count = contains(var.cloud_providers, "azure") ? 1 : 0
  
  length  = 16
  special = true
}