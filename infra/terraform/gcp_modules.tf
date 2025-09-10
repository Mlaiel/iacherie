# Ainflue Infrastructure Module - Google Cloud Platform Modules
# ============================================================
# 
# Enterprise-grade GCP infrastructure modules for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# GCP Project Configuration
resource "google_project" "ainflue_project" {
  name            = var.gcp_project_name
  project_id      = var.gcp_project_id
  billing_account = var.gcp_billing_account
  org_id          = var.gcp_org_id
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "storage.googleapis.com",
    "sql.googleapis.com",
    "redis.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com"
  ])

  project = google_project.ainflue_project.project_id
  service = each.key

  disable_dependent_services = true
}

# VPC Network
resource "google_compute_network" "ainflue_vpc" {
  name                    = "${var.environment}-ainflue-vpc"
  auto_create_subnetworks = false
  project                 = google_project.ainflue_project.project_id
  routing_mode           = "REGIONAL"

  depends_on = [google_project_service.required_apis]
}

# Subnets
resource "google_compute_subnetwork" "ainflue_subnet" {
  count = length(var.gcp_regions)

  name          = "${var.environment}-ainflue-subnet-${var.gcp_regions[count.index]}"
  ip_cidr_range = var.gcp_subnet_cidrs[count.index]
  region        = var.gcp_regions[count.index]
  network       = google_compute_network.ainflue_vpc.id
  project       = google_project.ainflue_project.project_id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.gcp_pod_cidrs[count.index]
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.gcp_service_cidrs[count.index]
  }
}

# GKE Cluster
resource "google_container_cluster" "ainflue_gke" {
  name     = "${var.environment}-ainflue-gke"
  location = var.gcp_primary_region
  project  = google_project.ainflue_project.project_id

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.ainflue_vpc.name
  subnetwork = google_compute_subnetwork.ainflue_subnet[0].name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  workload_identity_config {
    workload_pool = "${google_project.ainflue_project.project_id}.svc.id.goog"
  }

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
  }

  network_policy {
    enabled = true
  }

  depends_on = [
    google_project_service.required_apis,
    google_compute_subnetwork.ainflue_subnet
  ]
}

# GKE Node Pool
resource "google_container_node_pool" "ainflue_nodes" {
  name       = "${var.environment}-ainflue-nodes"
  location   = var.gcp_primary_region
  cluster    = google_container_cluster.ainflue_gke.name
  project    = google_project.ainflue_project.project_id
  node_count = var.gcp_node_count

  node_config {
    preemptible  = var.environment != "production"
    machine_type = var.gcp_machine_type

    service_account = google_service_account.gke_service_account.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  autoscaling {
    min_node_count = var.gcp_min_nodes
    max_node_count = var.gcp_max_nodes
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# Service Account for GKE
resource "google_service_account" "gke_service_account" {
  account_id   = "${var.environment}-ainflue-gke-sa"
  display_name = "Ainflue GKE Service Account"
  project      = google_project.ainflue_project.project_id
}

# Cloud SQL Instance
resource "google_sql_database_instance" "ainflue_postgres" {
  name                = "${var.environment}-ainflue-postgres"
  database_version    = "POSTGRES_14"
  region              = var.gcp_primary_region
  project             = google_project.ainflue_project.project_id
  deletion_protection = var.environment == "production"

  settings {
    tier = var.gcp_db_tier

    backup_configuration {
      enabled                        = true
      start_time                     = "02:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.ainflue_vpc.id
      require_ssl     = true
    }

    database_flags {
      name  = "log_statement"
      value = "all"
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud SQL Database
resource "google_sql_database" "ainflue_db" {
  name     = "ainflue_${var.environment}"
  instance = google_sql_database_instance.ainflue_postgres.name
  project  = google_project.ainflue_project.project_id
}

# Cloud Storage Bucket
resource "google_storage_bucket" "ainflue_storage" {
  name     = "${var.environment}-ainflue-storage-${random_id.bucket_suffix.hex}"
  location = var.gcp_primary_region
  project  = google_project.ainflue_project.project_id

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.storage_key.id
  }

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
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

# Redis Instance
resource "google_redis_instance" "ainflue_redis" {
  name           = "${var.environment}-ainflue-redis"
  memory_size_gb = var.gcp_redis_memory
  region         = var.gcp_primary_region
  project        = google_project.ainflue_project.project_id

  auth_enabled   = true
  redis_version  = "REDIS_6_X"
  transit_encryption_mode = "SERVER_AUTHENTICATION"

  authorized_network = google_compute_network.ainflue_vpc.id

  depends_on = [google_project_service.required_apis]
}

# KMS Key Ring
resource "google_kms_key_ring" "ainflue_keyring" {
  name     = "${var.environment}-ainflue-keyring"
  location = var.gcp_primary_region
  project  = google_project.ainflue_project.project_id
}

# KMS Crypto Key for Storage
resource "google_kms_crypto_key" "storage_key" {
  name     = "${var.environment}-storage-key"
  key_ring = google_kms_key_ring.ainflue_keyring.id
  purpose  = "ENCRYPT_DECRYPT"

  rotation_period = "7776000s" # 90 days
}

# Random ID for bucket suffix
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# IAM bindings for GKE service account
resource "google_project_iam_member" "gke_sa_bindings" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/storage.objectViewer",
    "roles/artifactregistry.reader"
  ])

  project = google_project.ainflue_project.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.gke_service_account.email}"
}