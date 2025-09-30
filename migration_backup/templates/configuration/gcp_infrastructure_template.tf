# =====================================================================================
# GCP Infrastructure Template - Ainflue Configuration Module
# =====================================================================================
# © 2025 Fahed Mlaiel <mlaiel@live.de>
# TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
# Utilisation commerciale INTERDITE sans autorisation écrite
# =====================================================================================

# Provider Configuration
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
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

# Local Variables
locals {
  project_id = var.project_id
  region     = var.region
  zone       = var.zone
  
  # Ainflue Creator Economy Labels
  common_labels = {
    project             = "ainflue"
    environment         = var.environment
    owner              = "fahed-mlaiel"
    business_unit      = "creator-economy"
    cost_center        = "infrastructure"
    managed_by         = "terraform"
    security_level     = var.security_level
    compliance_level   = var.compliance_level
    backup_policy      = var.backup_policy
    monitoring_level   = var.monitoring_level
  }

  # Network Configuration
  network_name = "${var.project_name}-${var.environment}-network"
  subnet_name  = "${var.project_name}-${var.environment}-subnet"
  
  # Security Configuration
  security_group_name = "${var.project_name}-${var.environment}-security-group"
  
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
}

# =====================================================================================
# GOOGLE CLOUD PROJECT CONFIGURATION
# =====================================================================================

# Project Services
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "cloudsql.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "cloudsecurity.googleapis.com",
    "cloudkms.googleapis.com",
    "cloudasset.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "dns.googleapis.com",
    "certificatemanager.googleapis.com",
    "storage.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "pubsub.googleapis.com",
    "dataflow.googleapis.com",
    "bigquery.googleapis.com",
    "ml.googleapis.com",
    "speech.googleapis.com",
    "vision.googleapis.com",
    "translate.googleapis.com"
  ])

  project = local.project_id
  service = each.value
  
  disable_dependent_services = false
  disable_on_destroy = false
}

# =====================================================================================
# NETWORKING INFRASTRUCTURE
# =====================================================================================

# VPC Network
resource "google_compute_network" "main" {
  name                    = local.network_name
  auto_create_subnetworks = false
  mtu                     = 1460
  routing_mode           = "REGIONAL"
  
  depends_on = [google_project_service.required_apis]
}

# Subnets for different tiers
resource "google_compute_subnetwork" "private" {
  name          = "${local.subnet_name}-private"
  ip_cidr_range = var.private_subnet_cidr
  region        = local.region
  network       = google_compute_network.main.id
  
  private_ip_google_access = true
  
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr_range
  }
  
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr_range
  }

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata            = "INCLUDE_ALL_METADATA"
  }
}

resource "google_compute_subnetwork" "public" {
  name          = "${local.subnet_name}-public"
  ip_cidr_range = var.public_subnet_cidr
  region        = local.region
  network       = google_compute_network.main.id
  
  private_ip_google_access = true
}

# Cloud Router
resource "google_compute_router" "main" {
  name    = "${var.project_name}-${var.environment}-router"
  region  = local.region
  network = google_compute_network.main.id
  
  bgp {
    asn = 64514
  }
}

# Cloud NAT
resource "google_compute_router_nat" "main" {
  name                               = "${var.project_name}-${var.environment}-nat"
  router                            = google_compute_router.main.name
  region                            = local.region
  nat_ip_allocate_option            = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# =====================================================================================
# GOOGLE KUBERNETES ENGINE (GKE) CLUSTER
# =====================================================================================

# GKE Cluster
resource "google_container_cluster" "primary" {
  name     = "${var.project_name}-${var.environment}-gke"
  location = local.region
  
  # Network configuration
  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.private.name
  
  # Remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1
  
  # Network policy
  network_policy {
    enabled = true
  }
  
  # IP allocation policy
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
  
  # Private cluster config
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.master_cidr_block
  }
  
  # Master auth
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
  
  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    
    horizontal_pod_autoscaling {
      disabled = false
    }
    
    network_policy_config {
      disabled = false
    }
    
    istio_config {
      disabled = false
      auth     = "AUTH_MUTUAL_TLS"
    }
    
    cloudrun_config {
      disabled = false
    }
  }
  
  # Workload Identity
  workload_identity_config {
    workload_pool = "${local.project_id}.svc.id.goog"
  }
  
  # Binary authorization
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }
  
  # Database encryption
  database_encryption {
    state    = "ENCRYPTED"
    key_name = google_kms_crypto_key.gke.id
  }
  
  # Logging and monitoring
  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"
  
  # Maintenance policy
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }
  
  # Resource labels
  resource_labels = local.common_labels
  
  depends_on = [
    google_project_service.required_apis,
    google_compute_subnetwork.private
  ]
}

# Node Pools
resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.project_name}-${var.environment}-nodes"
  location   = local.region
  cluster    = google_container_cluster.primary.name
  node_count = var.initial_node_count

  # Auto-scaling
  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }

  # Node configuration
  node_config {
    preemptible  = var.use_preemptible_nodes
    machine_type = var.node_machine_type
    disk_size_gb = var.node_disk_size
    disk_type    = "pd-ssd"
    image_type   = "COS_CONTAINERD"

    # Service account
    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/trace.append"
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Security
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    # Labels
    labels = merge(local.common_labels, {
      node_pool = "primary"
    })

    # Taints for creator economy workloads
    dynamic "taint" {
      for_each = var.enable_gpu_nodes ? [1] : []
      content {
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }
    }

    # Metadata
    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  # Management
  management {
    auto_repair  = true
    auto_upgrade = true
  }

  # Upgrade settings
  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# GPU Node Pool for AI Processing
resource "google_container_node_pool" "gpu_nodes" {
  count = var.enable_gpu_nodes ? 1 : 0
  
  name       = "${var.project_name}-${var.environment}-gpu-nodes"
  location   = local.region
  cluster    = google_container_cluster.primary.name
  node_count = var.gpu_node_count

  autoscaling {
    min_node_count = 0
    max_node_count = var.max_gpu_nodes
  }

  node_config {
    preemptible  = false
    machine_type = var.gpu_machine_type
    disk_size_gb = var.gpu_disk_size
    disk_type    = "pd-ssd"

    # GPU configuration
    guest_accelerator {
      type  = var.gpu_type
      count = var.gpu_count_per_node
    }

    # Service account
    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/trace.append"
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Labels
    labels = merge(local.common_labels, {
      node_pool = "gpu"
      gpu_type  = var.gpu_type
    })

    # Taints
    taint {
      key    = "nvidia.com/gpu"
      value  = "true"
      effect = "NO_SCHEDULE"
    }

    # Metadata
    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# =====================================================================================
# CLOUD SQL DATABASE
# =====================================================================================

# Database instance
resource "google_sql_database_instance" "main" {
  name             = "${var.project_name}-${var.environment}-db"
  database_version = var.database_version
  region          = local.region
  
  deletion_protection = var.deletion_protection

  settings {
    tier      = var.database_tier
    disk_size = var.database_disk_size
    disk_type = "PD_SSD"
    
    # Availability
    availability_type = var.database_availability_type
    
    # Backup configuration
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }
    
    # Database flags
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
    
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
    
    database_flags {
      name  = "log_temp_files"
      value = "0"
    }
    
    # IP configuration
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.main.id
      enable_private_path_for_google_cloud_services = true
    }
    
    # Maintenance window
    maintenance_window {
      day          = 7
      hour         = 4
      update_track = "stable"
    }
    
    # Insights config
    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }
    
    # User labels
    user_labels = local.common_labels
  }
  
  depends_on = [google_project_service.required_apis]
}

# Database
resource "google_sql_database" "ainflue" {
  name     = "ainflue_${var.environment}"
  instance = google_sql_database_instance.main.name
  charset  = "UTF8"
  collation = "en_US.UTF8"
}

# Database users
resource "google_sql_user" "app_user" {
  name     = var.database_user
  instance = google_sql_database_instance.main.name
  password = var.database_password
}

# =====================================================================================
# REDIS MEMORYSTORE
# =====================================================================================

resource "google_redis_instance" "cache" {
  name           = "${var.project_name}-${var.environment}-redis"
  memory_size_gb = var.redis_memory_size
  region         = local.region
  
  tier                    = var.redis_tier
  redis_version          = var.redis_version
  authorized_network     = google_compute_network.main.id
  connect_mode           = "PRIVATE_SERVICE_ACCESS"
  auth_enabled           = true
  transit_encryption_mode = "SERVER_AUTH"
  
  # Maintenance policy
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
        nanos   = 0
        seconds = 0
      }
    }
  }
  
  # Labels
  labels = local.common_labels
  
  depends_on = [google_project_service.required_apis]
}

# =====================================================================================
# CLOUD STORAGE
# =====================================================================================

# Main application bucket
resource "google_storage_bucket" "app_storage" {
  name     = "${var.project_name}-${var.environment}-storage"
  location = var.storage_location
  
  # Storage class
  storage_class = var.storage_class
  
  # Versioning
  versioning {
    enabled = true
  }
  
  # Encryption
  encryption {
    default_kms_key_name = google_kms_crypto_key.storage.id
  }
  
  # Lifecycle management
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  # CORS configuration for creator uploads
  cors {
    origin          = var.allowed_origins
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
  
  # Uniform bucket-level access
  uniform_bucket_level_access = true
  
  # Labels
  labels = local.common_labels
}

# Content processing bucket
resource "google_storage_bucket" "content_processing" {
  name     = "${var.project_name}-${var.environment}-content-processing"
  location = var.storage_location
  
  storage_class = "STANDARD"
  
  versioning {
    enabled = false
  }
  
  # Encryption
  encryption {
    default_kms_key_name = google_kms_crypto_key.storage.id
  }
  
  # Auto-deletion for temporary processing files
  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type = "Delete"
    }
  }
  
  uniform_bucket_level_access = true
  labels = local.common_labels
}

# Backup bucket
resource "google_storage_bucket" "backups" {
  name     = "${var.project_name}-${var.environment}-backups"
  location = var.backup_location
  
  storage_class = "ARCHIVE"
  
  versioning {
    enabled = true
  }
  
  # Encryption
  encryption {
    default_kms_key_name = google_kms_crypto_key.storage.id
  }
  
  # Retention policy
  retention_policy {
    retention_period = var.backup_retention_seconds
  }
  
  uniform_bucket_level_access = true
  labels = local.common_labels
}

# =====================================================================================
# CLOUD KMS
# =====================================================================================

# Key ring
resource "google_kms_key_ring" "main" {
  name     = "${var.project_name}-${var.environment}-keyring"
  location = local.region
  
  depends_on = [google_project_service.required_apis]
}

# GKE encryption key
resource "google_kms_crypto_key" "gke" {
  name     = "gke-encryption-key"
  key_ring = google_kms_key_ring.main.id
  
  rotation_period = "7776000s" # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# Storage encryption key
resource "google_kms_crypto_key" "storage" {
  name     = "storage-encryption-key"
  key_ring = google_kms_key_ring.main.id
  
  rotation_period = "7776000s" # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# Database encryption key
resource "google_kms_crypto_key" "database" {
  name     = "database-encryption-key"
  key_ring = google_kms_key_ring.main.id
  
  rotation_period = "7776000s" # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# =====================================================================================
# IAM CONFIGURATION
# =====================================================================================

# GKE service account
resource "google_service_account" "gke_nodes" {
  account_id   = "${var.project_name}-${var.environment}-gke-nodes"
  display_name = "GKE Nodes Service Account"
  description  = "Service account for GKE nodes"
}

# Application service account
resource "google_service_account" "app" {
  account_id   = "${var.project_name}-${var.environment}-app"
  display_name = "Application Service Account"
  description  = "Service account for Ainflue application"
}

# Creator processing service account
resource "google_service_account" "creator_processing" {
  account_id   = "${var.project_name}-${var.environment}-creator-processing"
  display_name = "Creator Processing Service Account"
  description  = "Service account for creator content processing"
}

# IAM bindings for application service account
resource "google_project_iam_member" "app_storage" {
  project = local.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.app.email}"
}

resource "google_project_iam_member" "app_cloudsql" {
  project = local.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.app.email}"
}

resource "google_project_iam_member" "app_secretmanager" {
  project = local.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# Creator processing IAM bindings
resource "google_project_iam_member" "creator_processing_ml" {
  project = local.project_id
  role    = "roles/ml.developer"
  member  = "serviceAccount:${google_service_account.creator_processing.email}"
}

resource "google_project_iam_member" "creator_processing_speech" {
  project = local.project_id
  role    = "roles/speech.editor"
  member  = "serviceAccount:${google_service_account.creator_processing.email}"
}

resource "google_project_iam_member" "creator_processing_vision" {
  project = local.project_id
  role    = "roles/vision.admin"
  member  = "serviceAccount:${google_service_account.creator_processing.email}"
}

# =====================================================================================
# CLOUD ENDPOINTS
# =====================================================================================

# API Gateway for creator economy services
resource "google_api_gateway_api" "creator_api" {
  provider = google-beta
  api_id   = "${var.project_name}-${var.environment}-creator-api"
  
  labels = local.common_labels
  
  depends_on = [google_project_service.required_apis]
}

# =====================================================================================
# CLOUD FUNCTIONS
# =====================================================================================

# Content processing function bucket
resource "google_storage_bucket" "functions" {
  name     = "${var.project_name}-${var.environment}-functions"
  location = var.storage_location
  
  uniform_bucket_level_access = true
  labels = local.common_labels
}

# =====================================================================================
# MONITORING AND ALERTING
# =====================================================================================

# Notification channels
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Alerts"
  type         = "email"
  
  labels = {
    email_address = var.alert_email
  }
  
  user_labels = local.common_labels
}

# Alert policies
resource "google_monitoring_alert_policy" "high_cpu" {
  display_name = "High CPU Usage"
  combiner     = "OR"
  
  conditions {
    display_name = "CPU usage over 80%"
    
    condition_threshold {
      filter          = "resource.type=\"gce_instance\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.id]
  
  alert_strategy {
    auto_close = "1800s"
  }
  
  user_labels = local.common_labels
}

# =====================================================================================
# SECURITY CONFIGURATION
# =====================================================================================

# Security Command Center
resource "google_security_center_organization_custom_module" "ainflue_security" {
  count = var.enable_security_center ? 1 : 0
  
  organization = var.organization_id
  display_name = "Ainflue Security Module"
  
  enablement_state = "ENABLED"
  
  custom_config {
    predicate {
      expression = "true"
    }
    
    custom_output {
      properties {
        name = "creator_content_protection"
        value_expression {
          expression = "resource.data"
        }
      }
    }
    
    description = "Custom security module for Ainflue creator economy platform"
    recommendation = "Ensure proper content protection and user data security"
    severity = "HIGH"
  }
}

# =====================================================================================
# OUTPUTS
# =====================================================================================

output "project_id" {
  description = "The GCP project ID"
  value       = local.project_id
}

output "region" {
  description = "The GCP region"
  value       = local.region
}

output "network_name" {
  description = "The name of the VPC network"
  value       = google_compute_network.main.name
}

output "network_id" {
  description = "The ID of the VPC network"
  value       = google_compute_network.main.id
}

output "private_subnet_name" {
  description = "The name of the private subnet"
  value       = google_compute_subnetwork.private.name
}

output "public_subnet_name" {
  description = "The name of the public subnet"
  value       = google_compute_subnetwork.public.name
}

output "gke_cluster_name" {
  description = "The name of the GKE cluster"
  value       = google_container_cluster.primary.name
}

output "gke_cluster_endpoint" {
  description = "The endpoint of the GKE cluster"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "gke_cluster_ca_certificate" {
  description = "The CA certificate of the GKE cluster"
  value       = google_container_cluster.primary.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "database_instance_name" {
  description = "The name of the Cloud SQL instance"
  value       = google_sql_database_instance.main.name
}

output "database_connection_name" {
  description = "The connection name of the Cloud SQL instance"
  value       = google_sql_database_instance.main.connection_name
}

output "database_private_ip" {
  description = "The private IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.main.private_ip_address
  sensitive   = true
}

output "redis_instance_id" {
  description = "The ID of the Redis instance"
  value       = google_redis_instance.cache.id
}

output "redis_host" {
  description = "The IP address of the Redis instance"
  value       = google_redis_instance.cache.host
  sensitive   = true
}

output "storage_bucket_name" {
  description = "The name of the main storage bucket"
  value       = google_storage_bucket.app_storage.name
}

output "content_processing_bucket_name" {
  description = "The name of the content processing bucket"
  value       = google_storage_bucket.content_processing.name
}

output "backup_bucket_name" {
  description = "The name of the backup bucket"
  value       = google_storage_bucket.backups.name
}

output "app_service_account_email" {
  description = "The email of the application service account"
  value       = google_service_account.app.email
}

output "creator_processing_service_account_email" {
  description = "The email of the creator processing service account"
  value       = google_service_account.creator_processing.email
}

output "kms_key_ring_id" {
  description = "The ID of the KMS key ring"
  value       = google_kms_key_ring.main.id
}

output "gke_encryption_key_id" {
  description = "The ID of the GKE encryption key"
  value       = google_kms_crypto_key.gke.id
}

output "storage_encryption_key_id" {
  description = "The ID of the storage encryption key"
  value       = google_kms_crypto_key.storage.id
}

output "monitoring_notification_channel_id" {
  description = "The ID of the monitoring notification channel"
  value       = google_monitoring_notification_channel.email.id
}

# Creator Economy Specific Outputs
output "creator_services" {
  description = "List of creator economy services"
  value       = local.creator_services
}

output "api_gateway_id" {
  description = "The ID of the API Gateway"
  value       = google_api_gateway_api.creator_api.api_id
}

output "functions_bucket_name" {
  description = "The name of the Cloud Functions bucket"
  value       = google_storage_bucket.functions.name
}

# =====================================================================================
# VARIABLES
# =====================================================================================

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "ainflue"
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "organization_id" {
  description = "The GCP organization ID"
  type        = string
  default     = ""
}

# Network Configuration
variable "private_subnet_cidr" {
  description = "CIDR block for private subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.2.0/24"
}

variable "pods_cidr_range" {
  description = "CIDR range for Kubernetes pods"
  type        = string
  default     = "10.1.0.0/16"
}

variable "services_cidr_range" {
  description = "CIDR range for Kubernetes services"
  type        = string
  default     = "10.2.0.0/16"
}

variable "master_cidr_block" {
  description = "CIDR block for GKE master"
  type        = string
  default     = "172.16.0.0/28"
}

# GKE Configuration
variable "initial_node_count" {
  description = "Initial number of nodes in the node pool"
  type        = number
  default     = 3
}

variable "min_node_count" {
  description = "Minimum number of nodes in the node pool"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum number of nodes in the node pool"
  type        = number
  default     = 10
}

variable "node_machine_type" {
  description = "Machine type for GKE nodes"
  type        = string
  default     = "e2-standard-4"
}

variable "node_disk_size" {
  description = "Disk size for GKE nodes in GB"
  type        = number
  default     = 100
}

variable "use_preemptible_nodes" {
  description = "Use preemptible nodes for cost optimization"
  type        = bool
  default     = false
}

# GPU Configuration
variable "enable_gpu_nodes" {
  description = "Enable GPU nodes for AI processing"
  type        = bool
  default     = true
}

variable "gpu_node_count" {
  description = "Number of GPU nodes"
  type        = number
  default     = 1
}

variable "max_gpu_nodes" {
  description = "Maximum number of GPU nodes"
  type        = number
  default     = 5
}

variable "gpu_machine_type" {
  description = "Machine type for GPU nodes"
  type        = string
  default     = "n1-standard-4"
}

variable "gpu_disk_size" {
  description = "Disk size for GPU nodes in GB"
  type        = number
  default     = 200
}

variable "gpu_type" {
  description = "Type of GPU"
  type        = string
  default     = "nvidia-tesla-t4"
}

variable "gpu_count_per_node" {
  description = "Number of GPUs per node"
  type        = number
  default     = 1
}

# Database Configuration
variable "database_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "POSTGRES_15"
}

variable "database_tier" {
  description = "Database instance tier"
  type        = string
  default     = "db-custom-2-4096"
}

variable "database_disk_size" {
  description = "Database disk size in GB"
  type        = number
  default     = 100
}

variable "database_availability_type" {
  description = "Database availability type"
  type        = string
  default     = "REGIONAL"
}

variable "database_user" {
  description = "Database user name"
  type        = string
  default     = "ainflue"
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "deletion_protection" {
  description = "Enable deletion protection for critical resources"
  type        = bool
  default     = true
}

# Redis Configuration
variable "redis_memory_size" {
  description = "Redis memory size in GB"
  type        = number
  default     = 4
}

variable "redis_tier" {
  description = "Redis service tier"
  type        = string
  default     = "STANDARD_HA"
}

variable "redis_version" {
  description = "Redis version"
  type        = string
  default     = "REDIS_7_0"
}

# Storage Configuration
variable "storage_location" {
  description = "Storage bucket location"
  type        = string
  default     = "US"
}

variable "storage_class" {
  description = "Storage class for main bucket"
  type        = string
  default     = "STANDARD"
}

variable "backup_location" {
  description = "Backup bucket location"
  type        = string
  default     = "US"
}

variable "backup_retention_seconds" {
  description = "Backup retention period in seconds"
  type        = number
  default     = 31536000 # 1 year
}

variable "allowed_origins" {
  description = "Allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

# Security Configuration
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

variable "enable_security_center" {
  description = "Enable Security Command Center"
  type        = bool
  default     = false
}

# Monitoring Configuration
variable "alert_email" {
  description = "Email address for alerts"
  type        = string
}

# =====================================================================================
# END OF TEMPLATE
# =====================================================================================