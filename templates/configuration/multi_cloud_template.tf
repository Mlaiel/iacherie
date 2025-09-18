# =====================================================================================
# Multi-Cloud Infrastructure Template - Ainflue Configuration Module
# =====================================================================================
# © 2025 Fahed Mlaiel <mlaiel@live.de>
# TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
# Utilisation commerciale INTERDITE sans autorisation écrite
# =====================================================================================

# Provider Configuration
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.20"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
    consul = {
      source  = "hashicorp/consul"
      version = "~> 2.18"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.15"
    }
  }
}

# Configure Providers
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = local.common_tags
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

provider "azurerm" {
  features {}
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Local Variables
locals {
  # Ainflue Creator Economy Multi-Cloud Configuration
  project_name = var.project_name
  environment  = var.environment
  
  # Common tags for all cloud providers
  common_tags = {
    Project              = "Ainflue"
    Environment         = local.environment
    Owner               = "Fahed Mlaiel"
    BusinessUnit        = "Creator Economy"
    CostCenter          = "Infrastructure"
    ManagedBy           = "Terraform"
    MultiCloud          = "true"
    SecurityLevel       = var.security_level
    ComplianceLevel     = var.compliance_level
    BackupPolicy        = var.backup_policy
    MonitoringLevel     = var.monitoring_level
    DisasterRecovery    = var.disaster_recovery_enabled
    CreatedDate         = formatdate("YYYY-MM-DD", timestamp())
  }
  
  # Multi-Cloud Strategy Configuration
  primary_cloud   = var.primary_cloud_provider
  secondary_cloud = var.secondary_cloud_provider
  tertiary_cloud  = var.tertiary_cloud_provider
  
  # Creator Economy Services Distribution
  creator_services_distribution = {
    # Primary cloud - Core business logic
    primary = [
      "user-management",
      "content-processing", 
      "ai-enhancement",
      "protection-engine"
    ]
    # Secondary cloud - Analytics and ML
    secondary = [
      "analytics-engine",
      "ml-training",
      "recommendation-engine",
      "performance-monitoring"
    ]
    # Tertiary cloud - Media and CDN
    tertiary = [
      "media-storage",
      "cdn-distribution",
      "backup-services",
      "disaster-recovery"
    ]
    # Edge locations - Real-time services
    edge = [
      "real-time-collaboration",
      "live-streaming",
      "chat-services",
      "notification-gateway"
    ]
  }
  
  # Global DNS configuration
  global_dns_zones = {
    main     = var.domain_name
    api      = "api.${var.domain_name}"
    cdn      = "cdn.${var.domain_name}"
    creators = "creators.${var.domain_name}"
    admin    = "admin.${var.domain_name}"
  }
  
  # Cross-cloud networking
  vpc_cidrs = {
    aws   = "10.0.0.0/16"
    gcp   = "10.1.0.0/16"
    azure = "10.2.0.0/16"
  }
}

# =====================================================================================
# CLOUDFLARE GLOBAL DNS AND CDN
# =====================================================================================

# Cloudflare Zone for global DNS
resource "cloudflare_zone" "main" {
  zone = var.domain_name
  plan = var.cloudflare_plan
  
  meta = {
    wildcard_proxied = true
  }
}

# Global Load Balancer Pool - AWS Primary
resource "cloudflare_load_balancer_pool" "aws_primary" {
  name = "aws-primary-pool"
  
  dynamic "origins" {
    for_each = var.aws_enabled ? [1] : []
    content {
      name    = "aws-primary"
      address = aws_lb.main[0].dns_name
      enabled = true
      weight  = 1
    }
  }
  
  description = "AWS Primary Region Pool"
  enabled     = var.aws_enabled
  
  monitor = cloudflare_load_balancer_monitor.http_monitor.id
  
  notification_email = var.alert_email
}

# Global Load Balancer Pool - GCP Secondary
resource "cloudflare_load_balancer_pool" "gcp_secondary" {
  name = "gcp-secondary-pool"
  
  dynamic "origins" {
    for_each = var.gcp_enabled ? [1] : []
    content {
      name    = "gcp-secondary"
      address = google_compute_global_forwarding_rule.main[0].ip_address
      enabled = true
      weight  = 1
    }
  }
  
  description = "GCP Secondary Region Pool"
  enabled     = var.gcp_enabled
  
  monitor = cloudflare_load_balancer_monitor.http_monitor.id
  
  notification_email = var.alert_email
}

# Global Load Balancer Pool - Azure Tertiary
resource "cloudflare_load_balancer_pool" "azure_tertiary" {
  name = "azure-tertiary-pool"
  
  dynamic "origins" {
    for_each = var.azure_enabled ? [1] : []
    content {
      name    = "azure-tertiary"
      address = azurerm_public_ip.app_gateway[0].ip_address
      enabled = true
      weight  = 1
    }
  }
  
  description = "Azure Tertiary Region Pool"
  enabled     = var.azure_enabled
  
  monitor = cloudflare_load_balancer_monitor.http_monitor.id
  
  notification_email = var.alert_email
}

# Health Monitor
resource "cloudflare_load_balancer_monitor" "http_monitor" {
  expected_body   = "healthy"
  expected_codes  = "200"
  method          = "GET"
  timeout         = 7
  path            = "/health"
  interval        = 60
  retries         = 2
  description     = "Ainflue Health Monitor"
  type            = "http"
  port            = 80
  
  header {
    header = "Host"
    values = [var.domain_name]
  }
}

# Global Load Balancer
resource "cloudflare_load_balancer" "main" {
  zone_id          = cloudflare_zone.main.id
  name             = var.domain_name
  fallback_pool_id = cloudflare_load_balancer_pool.aws_primary.id
  
  default_pool_ids = [
    cloudflare_load_balancer_pool.aws_primary.id,
    cloudflare_load_balancer_pool.gcp_secondary.id,
    cloudflare_load_balancer_pool.azure_tertiary.id
  ]
  
  description = "Ainflue Global Load Balancer"
  ttl         = 30
  proxied     = true
  
  # Geo-steering rules
  region_pools {
    region = "WNAM"  # Western North America
    pool_ids = [
      cloudflare_load_balancer_pool.aws_primary.id,
      cloudflare_load_balancer_pool.gcp_secondary.id
    ]
  }
  
  region_pools {
    region = "ENAM"  # Eastern North America  
    pool_ids = [
      cloudflare_load_balancer_pool.aws_primary.id,
      cloudflare_load_balancer_pool.azure_tertiary.id
    ]
  }
  
  region_pools {
    region = "WEU"   # Western Europe
    pool_ids = [
      cloudflare_load_balancer_pool.azure_tertiary.id,
      cloudflare_load_balancer_pool.gcp_secondary.id
    ]
  }
  
  region_pools {
    region = "APAC"  # Asia Pacific
    pool_ids = [
      cloudflare_load_balancer_pool.gcp_secondary.id,
      cloudflare_load_balancer_pool.aws_primary.id
    ]
  }
  
  # Session affinity for creator sessions
  session_affinity = "cookie"
  session_affinity_ttl = 3600
  
  # Adaptive routing for performance
  adaptive_routing {
    failover_across_pools = true
  }
}

# DNS Records for API services
resource "cloudflare_record" "api" {
  zone_id = cloudflare_zone.main.id
  name    = "api"
  value   = cloudflare_load_balancer.main.name
  type    = "CNAME"
  proxied = true
  ttl     = 1  # Automatic
}

# DNS Records for CDN
resource "cloudflare_record" "cdn" {
  zone_id = cloudflare_zone.main.id
  name    = "cdn"
  value   = cloudflare_load_balancer.main.name
  type    = "CNAME"
  proxied = true
  ttl     = 1  # Automatic
}

# =====================================================================================
# AWS INFRASTRUCTURE (Primary Cloud)
# =====================================================================================

# AWS VPC
resource "aws_vpc" "main" {
  count = var.aws_enabled ? 1 : 0
  
  cidr_block           = local.vpc_cidrs.aws
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-vpc"
    CloudProvider = "AWS"
  })
}

# AWS Subnets
resource "aws_subnet" "public" {
  count = var.aws_enabled ? length(var.aws_availability_zones) : 0
  
  vpc_id            = aws_vpc.main[0].id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = var.aws_availability_zones[count.index]
  
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-public-${count.index + 1}"
    Type = "Public"
    CloudProvider = "AWS"
  })
}

resource "aws_subnet" "private" {
  count = var.aws_enabled ? length(var.aws_availability_zones) : 0
  
  vpc_id            = aws_vpc.main[0].id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = var.aws_availability_zones[count.index]
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-private-${count.index + 1}"
    Type = "Private"
    CloudProvider = "AWS"
  })
}

# AWS Internet Gateway
resource "aws_internet_gateway" "main" {
  count = var.aws_enabled ? 1 : 0
  
  vpc_id = aws_vpc.main[0].id
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-igw"
    CloudProvider = "AWS"
  })
}

# AWS EKS Cluster
resource "aws_eks_cluster" "main" {
  count = var.aws_enabled ? 1 : 0
  
  name     = "${local.project_name}-${local.environment}-eks"
  role_arn = aws_iam_role.eks_cluster[0].arn
  version  = var.aws_kubernetes_version
  
  vpc_config {
    subnet_ids              = aws_subnet.private[*].id
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.aws_eks_public_access_cidrs
  }
  
  # Encryption
  encryption_config {
    provider {
      key_arn = aws_kms_key.eks[0].arn
    }
    resources = ["secrets"]
  }
  
  # Logging
  enabled_cluster_log_types = [
    "api",
    "audit", 
    "authenticator",
    "controllerManager",
    "scheduler"
  ]
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_cloudwatch_log_group.eks_cluster
  ]
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-eks"
    CloudProvider = "AWS"
  })
}

# AWS Load Balancer
resource "aws_lb" "main" {
  count = var.aws_enabled ? 1 : 0
  
  name               = "${local.project_name}-${local.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb[0].id]
  subnets           = aws_subnet.public[*].id
  
  enable_deletion_protection = var.aws_deletion_protection
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-alb"
    CloudProvider = "AWS"
  })
}

# =====================================================================================
# GOOGLE CLOUD INFRASTRUCTURE (Secondary Cloud)
# =====================================================================================

# GCP VPC Network
resource "google_compute_network" "main" {
  count = var.gcp_enabled ? 1 : 0
  
  name                    = "${local.project_name}-${local.environment}-network"
  auto_create_subnetworks = false
  mtu                     = 1460
  
  depends_on = [google_project_service.required_apis]
}

# GCP Subnet
resource "google_compute_subnetwork" "main" {
  count = var.gcp_enabled ? 1 : 0
  
  name          = "${local.project_name}-${local.environment}-subnet"
  ip_cidr_range = "10.1.1.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main[0].id
  
  private_ip_google_access = true
  
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.16.0/20"
  }
  
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.1.32.0/20"
  }
}

# GCP Project Services
resource "google_project_service" "required_apis" {
  count = var.gcp_enabled ? 1 : 0
  
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "cloudsql.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])
  
  project = var.gcp_project_id
  service = each.value
  
  disable_dependent_services = false
  disable_on_destroy = false
}

# GCP GKE Cluster
resource "google_container_cluster" "main" {
  count = var.gcp_enabled ? 1 : 0
  
  name     = "${local.project_name}-${local.environment}-gke"
  location = var.gcp_region
  
  network    = google_compute_network.main[0].name
  subnetwork = google_compute_subnetwork.main[0].name
  
  remove_default_node_pool = true
  initial_node_count       = 1
  
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
  
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  
  depends_on = [google_project_service.required_apis]
}

# GCP Global Load Balancer
resource "google_compute_global_forwarding_rule" "main" {
  count = var.gcp_enabled ? 1 : 0
  
  name       = "${local.project_name}-${local.environment}-lb"
  target     = google_compute_target_http_proxy.main[0].id
  port_range = "80"
  
  depends_on = [google_project_service.required_apis]
}

resource "google_compute_target_http_proxy" "main" {
  count = var.gcp_enabled ? 1 : 0
  
  name    = "${local.project_name}-${local.environment}-proxy"
  url_map = google_compute_url_map.main[0].id
}

resource "google_compute_url_map" "main" {
  count = var.gcp_enabled ? 1 : 0
  
  name            = "${local.project_name}-${local.environment}-urlmap"
  default_service = google_compute_backend_service.main[0].id
}

resource "google_compute_backend_service" "main" {
  count = var.gcp_enabled ? 1 : 0
  
  name                  = "${local.project_name}-${local.environment}-backend"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL"
  timeout_sec           = 30
  
  health_checks = [google_compute_health_check.main[0].id]
}

resource "google_compute_health_check" "main" {
  count = var.gcp_enabled ? 1 : 0
  
  name = "${local.project_name}-${local.environment}-healthcheck"
  
  timeout_sec        = 5
  check_interval_sec = 10
  
  http_health_check {
    port         = 80
    request_path = "/health"
  }
}

# =====================================================================================
# AZURE INFRASTRUCTURE (Tertiary Cloud)
# =====================================================================================

# Azure Resource Group
resource "azurerm_resource_group" "main" {
  count = var.azure_enabled ? 1 : 0
  
  name     = "${local.project_name}-${local.environment}-rg"
  location = var.azure_location
  
  tags = local.common_tags
}

# Azure Virtual Network
resource "azurerm_virtual_network" "main" {
  count = var.azure_enabled ? 1 : 0
  
  name                = "${local.project_name}-${local.environment}-vnet"
  address_space       = [local.vpc_cidrs.azure]
  location            = azurerm_resource_group.main[0].location
  resource_group_name = azurerm_resource_group.main[0].name
  
  tags = local.common_tags
}

# Azure Subnet
resource "azurerm_subnet" "main" {
  count = var.azure_enabled ? 1 : 0
  
  name                 = "${local.project_name}-${local.environment}-subnet"
  resource_group_name  = azurerm_resource_group.main[0].name
  virtual_network_name = azurerm_virtual_network.main[0].name
  address_prefixes     = ["10.2.1.0/24"]
}

# Azure AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  count = var.azure_enabled ? 1 : 0
  
  name                = "${local.project_name}-${local.environment}-aks"
  location            = azurerm_resource_group.main[0].location
  resource_group_name = azurerm_resource_group.main[0].name
  dns_prefix          = "${local.project_name}-${local.environment}-aks"
  
  default_node_pool {
    name       = "default"
    node_count = var.azure_node_count
    vm_size    = var.azure_vm_size
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  tags = local.common_tags
}

# Azure Public IP for Application Gateway
resource "azurerm_public_ip" "app_gateway" {
  count = var.azure_enabled ? 1 : 0
  
  name                = "${local.project_name}-${local.environment}-appgw-pip"
  resource_group_name = azurerm_resource_group.main[0].name
  location            = azurerm_resource_group.main[0].location
  allocation_method   = "Static"
  sku                 = "Standard"
  
  tags = local.common_tags
}

# =====================================================================================
# CROSS-CLOUD VPN CONNECTIONS
# =====================================================================================

# AWS VPN Gateway
resource "aws_vpn_gateway" "main" {
  count = var.aws_enabled && var.enable_cross_cloud_vpn ? 1 : 0
  
  vpc_id = aws_vpc.main[0].id
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-vpn-gw"
    CloudProvider = "AWS"
  })
}

# GCP VPN Gateway  
resource "google_compute_vpn_gateway" "main" {
  count = var.gcp_enabled && var.enable_cross_cloud_vpn ? 1 : 0
  
  name    = "${local.project_name}-${local.environment}-vpn-gw"
  network = google_compute_network.main[0].id
  region  = var.gcp_region
}

# Azure VPN Gateway
resource "azurerm_virtual_network_gateway" "main" {
  count = var.azure_enabled && var.enable_cross_cloud_vpn ? 1 : 0
  
  name                = "${local.project_name}-${local.environment}-vpn-gw"
  location            = azurerm_resource_group.main[0].location
  resource_group_name = azurerm_resource_group.main[0].name
  
  type     = "Vpn"
  vpn_type = "RouteBased"
  
  active_active = false
  enable_bgp    = false
  sku           = "VpnGw1"
  
  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.vpn_gateway[0].id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway[0].id
  }
  
  tags = local.common_tags
}

resource "azurerm_public_ip" "vpn_gateway" {
  count = var.azure_enabled && var.enable_cross_cloud_vpn ? 1 : 0
  
  name                = "${local.project_name}-${local.environment}-vpn-gw-pip"
  location            = azurerm_resource_group.main[0].location
  resource_group_name = azurerm_resource_group.main[0].name
  allocation_method   = "Dynamic"
  
  tags = local.common_tags
}

resource "azurerm_subnet" "gateway" {
  count = var.azure_enabled && var.enable_cross_cloud_vpn ? 1 : 0
  
  name                 = "GatewaySubnet"
  resource_group_name  = azurerm_resource_group.main[0].name
  virtual_network_name = azurerm_virtual_network.main[0].name
  address_prefixes     = ["10.2.255.0/24"]
}

# =====================================================================================
# CONSUL SERVICE MESH (Cross-Cloud Service Discovery)
# =====================================================================================

# Consul datacenter configuration for each cloud
resource "consul_config_entry" "service_defaults" {
  for_each = var.enable_service_mesh ? toset(["aws", "gcp", "azure"]) : toset([])
  
  kind = "service-defaults"
  name = "ainflue-${each.key}"
  
  config_json = jsonencode({
    Protocol = "http"
    MeshGateway = {
      Mode = "local"
    }
    Expose = {
      Checks = true
      Paths = [{
        Path            = "/health"
        LocalPathPort   = 8080
        ListenerPort    = 21500
        Protocol        = "http"
      }]
    }
  })
}

# =====================================================================================
# MONITORING AND OBSERVABILITY (Cross-Cloud)
# =====================================================================================

# Grafana Cloud for centralized monitoring
resource "grafana_cloud_stack" "main" {
  count = var.enable_centralized_monitoring ? 1 : 0
  
  name        = "${local.project_name}-${local.environment}"
  slug        = "${local.project_name}-${local.environment}"
  region_slug = var.grafana_cloud_region
  description = "Ainflue Multi-Cloud Monitoring Stack"
  
  labels = {
    "environment" = local.environment
    "project"     = local.project_name
    "multi-cloud" = "true"
  }
}

# =====================================================================================
# SECURITY AND COMPLIANCE (Cross-Cloud)
# =====================================================================================

# AWS KMS Key
resource "aws_kms_key" "eks" {
  count = var.aws_enabled ? 1 : 0
  
  description             = "EKS encryption key"
  deletion_window_in_days = 7
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-eks-key"
    CloudProvider = "AWS"
  })
}

# AWS IAM Role for EKS
resource "aws_iam_role" "eks_cluster" {
  count = var.aws_enabled ? 1 : 0
  
  name = "${local.project_name}-${local.environment}-eks-cluster"
  
  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
  
  tags = merge(local.common_tags, {
    CloudProvider = "AWS"
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  count = var.aws_enabled ? 1 : 0
  
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster[0].name
}

# AWS Security Group for ALB
resource "aws_security_group" "alb" {
  count = var.aws_enabled ? 1 : 0
  
  name_prefix = "${local.project_name}-${local.environment}-alb-"
  vpc_id      = aws_vpc.main[0].id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
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
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-alb-sg"
    CloudProvider = "AWS"
  })
}

# AWS CloudWatch Log Group
resource "aws_cloudwatch_log_group" "eks_cluster" {
  count = var.aws_enabled ? 1 : 0
  
  name              = "/aws/eks/${local.project_name}-${local.environment}-eks/cluster"
  retention_in_days = var.aws_log_retention_days
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-eks-logs"
    CloudProvider = "AWS"
  })
}

# =====================================================================================
# DISASTER RECOVERY AND BACKUP
# =====================================================================================

# Cross-cloud backup strategy
resource "aws_s3_bucket" "backup" {
  count = var.aws_enabled && var.disaster_recovery_enabled ? 1 : 0
  
  bucket = "${local.project_name}-${local.environment}-backup-${random_id.bucket_suffix.hex}"
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-backup"
    Purpose = "Disaster Recovery"
    CloudProvider = "AWS"
  })
}

resource "random_id" "bucket_suffix" {
  byte_length = 8
}

resource "aws_s3_bucket_versioning" "backup" {
  count = var.aws_enabled && var.disaster_recovery_enabled ? 1 : 0
  
  bucket = aws_s3_bucket.backup[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backup" {
  count = var.aws_enabled && var.disaster_recovery_enabled ? 1 : 0
  
  bucket = aws_s3_bucket.backup[0].id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
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

variable "domain_name" {
  description = "Primary domain name"
  type        = string
}

# Cloud Provider Configuration
variable "primary_cloud_provider" {
  description = "Primary cloud provider"
  type        = string
  default     = "aws"
  validation {
    condition     = contains(["aws", "gcp", "azure"], var.primary_cloud_provider)
    error_message = "Primary cloud provider must be aws, gcp, or azure."
  }
}

variable "secondary_cloud_provider" {
  description = "Secondary cloud provider"
  type        = string
  default     = "gcp"
  validation {
    condition     = contains(["aws", "gcp", "azure"], var.secondary_cloud_provider)
    error_message = "Secondary cloud provider must be aws, gcp, or azure."
  }
}

variable "tertiary_cloud_provider" {
  description = "Tertiary cloud provider"
  type        = string
  default     = "azure"
  validation {
    condition     = contains(["aws", "gcp", "azure"], var.tertiary_cloud_provider)
    error_message = "Tertiary cloud provider must be aws, gcp, or azure."
  }
}

# Cloud Provider Enable Flags
variable "aws_enabled" {
  description = "Enable AWS infrastructure"
  type        = bool
  default     = true
}

variable "gcp_enabled" {
  description = "Enable GCP infrastructure"
  type        = bool
  default     = true
}

variable "azure_enabled" {
  description = "Enable Azure infrastructure"
  type        = bool
  default     = true
}

# AWS Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_availability_zones" {
  description = "AWS availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "aws_kubernetes_version" {
  description = "AWS EKS Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "aws_eks_public_access_cidrs" {
  description = "CIDR blocks for EKS public access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "aws_deletion_protection" {
  description = "Enable deletion protection for AWS resources"
  type        = bool
  default     = true
}

variable "aws_log_retention_days" {
  description = "AWS CloudWatch log retention days"
  type        = number
  default     = 90
}

# GCP Configuration
variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

# Azure Configuration
variable "azure_location" {
  description = "Azure location"
  type        = string
  default     = "West Europe"
}

variable "azure_node_count" {
  description = "Azure AKS node count"
  type        = number
  default     = 3
}

variable "azure_vm_size" {
  description = "Azure VM size"
  type        = string
  default     = "Standard_D2s_v3"
}

# Cloudflare Configuration
variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_plan" {
  description = "Cloudflare plan"
  type        = string
  default     = "pro"
}

# Multi-Cloud Features
variable "enable_cross_cloud_vpn" {
  description = "Enable cross-cloud VPN connections"
  type        = bool
  default     = false
}

variable "enable_service_mesh" {
  description = "Enable cross-cloud service mesh"
  type        = bool
  default     = true
}

variable "enable_centralized_monitoring" {
  description = "Enable centralized monitoring with Grafana Cloud"
  type        = bool
  default     = true
}

variable "disaster_recovery_enabled" {
  description = "Enable disaster recovery"
  type        = bool
  default     = true
}

variable "grafana_cloud_region" {
  description = "Grafana Cloud region"
  type        = string
  default     = "us"
}

# Security Configuration
variable "security_level" {
  description = "Security level"
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
  default     = "cross-cloud"
}

variable "monitoring_level" {
  description = "Monitoring level"
  type        = string
  default     = "comprehensive"
}

# Alerting Configuration
variable "alert_email" {
  description = "Email address for alerts"
  type        = string
}

# =====================================================================================
# OUTPUTS
# =====================================================================================

output "primary_cloud" {
  description = "Primary cloud provider"
  value       = local.primary_cloud
}

output "secondary_cloud" {
  description = "Secondary cloud provider"
  value       = local.secondary_cloud
}

output "tertiary_cloud" {
  description = "Tertiary cloud provider"
  value       = local.tertiary_cloud
}

output "global_load_balancer_dns" {
  description = "Global load balancer DNS name"
  value       = cloudflare_load_balancer.main.name
}

output "domain_name" {
  description = "Primary domain name"
  value       = var.domain_name
}

# AWS Outputs
output "aws_vpc_id" {
  description = "AWS VPC ID"
  value       = var.aws_enabled ? aws_vpc.main[0].id : null
}

output "aws_eks_cluster_name" {
  description = "AWS EKS cluster name"
  value       = var.aws_enabled ? aws_eks_cluster.main[0].name : null
}

output "aws_load_balancer_dns" {
  description = "AWS load balancer DNS name"
  value       = var.aws_enabled ? aws_lb.main[0].dns_name : null
}

# GCP Outputs
output "gcp_network_name" {
  description = "GCP network name"
  value       = var.gcp_enabled ? google_compute_network.main[0].name : null
}

output "gcp_cluster_name" {
  description = "GCP GKE cluster name"
  value       = var.gcp_enabled ? google_container_cluster.main[0].name : null
}

output "gcp_load_balancer_ip" {
  description = "GCP load balancer IP"
  value       = var.gcp_enabled ? google_compute_global_forwarding_rule.main[0].ip_address : null
}

# Azure Outputs
output "azure_resource_group_name" {
  description = "Azure resource group name"
  value       = var.azure_enabled ? azurerm_resource_group.main[0].name : null
}

output "azure_aks_cluster_name" {
  description = "Azure AKS cluster name"
  value       = var.azure_enabled ? azurerm_kubernetes_cluster.main[0].name : null
}

output "azure_public_ip" {
  description = "Azure public IP"
  value       = var.azure_enabled ? azurerm_public_ip.app_gateway[0].ip_address : null
}

# Multi-cloud Configuration Outputs
output "creator_services_distribution" {
  description = "Creator services distribution across clouds"
  value       = local.creator_services_distribution
}

output "global_dns_zones" {
  description = "Global DNS zones configuration"
  value       = local.global_dns_zones
}

output "vpc_cidrs" {
  description = "VPC CIDR blocks for each cloud"
  value       = local.vpc_cidrs
}

# =====================================================================================
# END OF TEMPLATE
# =====================================================================================