# Ainflue Infrastructure Module - Multi-Cloud Networking
# =====================================================
# 
# Enterprise-grade multi-cloud networking for Ainflue platform
# Supports cross-cloud connectivity and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# AWS VPC Peering to GCP
resource "aws_vpc_peering_connection" "aws_to_gcp" {
  count = var.enable_cross_cloud_peering ? 1 : 0

  vpc_id      = aws_vpc.ainflue_vpc.id
  peer_region = var.gcp_primary_region
  
  tags = {
    Name        = "${var.environment}-aws-gcp-peering"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

# AWS Transit Gateway for multi-region connectivity
resource "aws_ec2_transit_gateway" "ainflue_tgw" {
  count = var.enable_aws_transit_gateway ? 1 : 0

  description                     = "Ainflue Multi-Region Transit Gateway"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"
  dns_support                     = "enable"
  vpn_ecmp_support               = "enable"

  tags = {
    Name        = "${var.environment}-ainflue-tgw"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

# AWS Transit Gateway VPC Attachment
resource "aws_ec2_transit_gateway_vpc_attachment" "ainflue_tgw_attachment" {
  count = var.enable_aws_transit_gateway ? 1 : 0

  subnet_ids         = aws_subnet.ainflue_private[*].id
  transit_gateway_id = aws_ec2_transit_gateway.ainflue_tgw[0].id
  vpc_id             = aws_vpc.ainflue_vpc.id

  tags = {
    Name        = "${var.environment}-ainflue-tgw-attachment"
    Environment = var.environment
    Project     = "Ainflue"
  }
}

# GCP Global Load Balancer
resource "google_compute_global_address" "ainflue_global_ip" {
  name    = "${var.environment}-ainflue-global-ip"
  project = google_project.ainflue_project.project_id
}

resource "google_compute_global_forwarding_rule" "ainflue_global_lb" {
  name       = "${var.environment}-ainflue-global-lb"
  target     = google_compute_target_https_proxy.ainflue_https_proxy.id
  port_range = "443"
  ip_address = google_compute_global_address.ainflue_global_ip.address
  project    = google_project.ainflue_project.project_id
}

resource "google_compute_target_https_proxy" "ainflue_https_proxy" {
  name    = "${var.environment}-ainflue-https-proxy"
  url_map = google_compute_url_map.ainflue_url_map.id
  ssl_certificates = [
    google_compute_managed_ssl_certificate.ainflue_ssl_cert.id
  ]
  project = google_project.ainflue_project.project_id
}

resource "google_compute_managed_ssl_certificate" "ainflue_ssl_cert" {
  name    = "${var.environment}-ainflue-ssl-cert"
  project = google_project.ainflue_project.project_id

  managed {
    domains = var.gcp_ssl_domains
  }
}

resource "google_compute_url_map" "ainflue_url_map" {
  name            = "${var.environment}-ainflue-url-map"
  default_service = google_compute_backend_service.ainflue_backend.id
  project         = google_project.ainflue_project.project_id

  host_rule {
    hosts        = var.gcp_ssl_domains
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.ainflue_backend.id

    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.ainflue_api_backend.id
    }

    path_rule {
      paths   = ["/ai/*"]
      service = google_compute_backend_service.ainflue_ai_backend.id
    }
  }
}

resource "google_compute_backend_service" "ainflue_backend" {
  name                  = "${var.environment}-ainflue-backend"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL"
  timeout_sec           = 30
  project               = google_project.ainflue_project.project_id

  backend {
    group = google_compute_instance_group_manager.ainflue_igm.instance_group
  }

  health_checks = [google_compute_health_check.ainflue_health_check.id]
}

resource "google_compute_backend_service" "ainflue_api_backend" {
  name                  = "${var.environment}-ainflue-api-backend"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL"
  timeout_sec           = 30
  project               = google_project.ainflue_project.project_id

  backend {
    group = google_compute_instance_group_manager.ainflue_api_igm.instance_group
  }

  health_checks = [google_compute_health_check.ainflue_api_health_check.id]
}

resource "google_compute_backend_service" "ainflue_ai_backend" {
  name                  = "${var.environment}-ainflue-ai-backend"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL"
  timeout_sec           = 60
  project               = google_project.ainflue_project.project_id

  backend {
    group = google_compute_instance_group_manager.ainflue_ai_igm.instance_group
  }

  health_checks = [google_compute_health_check.ainflue_ai_health_check.id]
}

# Health Checks
resource "google_compute_health_check" "ainflue_health_check" {
  name    = "${var.environment}-ainflue-health-check"
  project = google_project.ainflue_project.project_id

  timeout_sec        = 5
  check_interval_sec = 30

  http_health_check {
    port         = "8080"
    request_path = "/health"
  }
}

resource "google_compute_health_check" "ainflue_api_health_check" {
  name    = "${var.environment}-ainflue-api-health-check"
  project = google_project.ainflue_project.project_id

  timeout_sec        = 5
  check_interval_sec = 30

  http_health_check {
    port         = "8080"
    request_path = "/api/health"
  }
}

resource "google_compute_health_check" "ainflue_ai_health_check" {
  name    = "${var.environment}-ainflue-ai-health-check"
  project = google_project.ainflue_project.project_id

  timeout_sec        = 10
  check_interval_sec = 30

  http_health_check {
    port         = "8080"
    request_path = "/ai/health"
  }
}

# Instance Group Managers
resource "google_compute_instance_group_manager" "ainflue_igm" {
  name    = "${var.environment}-ainflue-igm"
  zone    = "${var.gcp_primary_region}-a"
  project = google_project.ainflue_project.project_id

  base_instance_name = "${var.environment}-ainflue-instance"
  target_size        = var.gcp_min_instances

  version {
    instance_template = google_compute_instance_template.ainflue_template.id
  }

  named_port {
    name = "http"
    port = 8080
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.ainflue_health_check.id
    initial_delay_sec = 300
  }
}

resource "google_compute_instance_group_manager" "ainflue_api_igm" {
  name    = "${var.environment}-ainflue-api-igm"
  zone    = "${var.gcp_primary_region}-a"
  project = google_project.ainflue_project.project_id

  base_instance_name = "${var.environment}-ainflue-api-instance"
  target_size        = var.gcp_api_min_instances

  version {
    instance_template = google_compute_instance_template.ainflue_api_template.id
  }

  named_port {
    name = "http"
    port = 8080
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.ainflue_api_health_check.id
    initial_delay_sec = 300
  }
}

resource "google_compute_instance_group_manager" "ainflue_ai_igm" {
  name    = "${var.environment}-ainflue-ai-igm"
  zone    = "${var.gcp_primary_region}-a"
  project = google_project.ainflue_project.project_id

  base_instance_name = "${var.environment}-ainflue-ai-instance"
  target_size        = var.gcp_ai_min_instances

  version {
    instance_template = google_compute_instance_template.ainflue_ai_template.id
  }

  named_port {
    name = "http"
    port = 8080
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.ainflue_ai_health_check.id
    initial_delay_sec = 300
  }
}

# Instance Templates
resource "google_compute_instance_template" "ainflue_template" {
  name        = "${var.environment}-ainflue-template"
  description = "Ainflue application instance template"
  project     = google_project.ainflue_project.project_id

  machine_type = var.gcp_machine_type
  region       = var.gcp_primary_region

  disk {
    source_image = "debian-cloud/debian-11"
    auto_delete  = true
    boot         = true
    disk_type    = "pd-ssd"
    disk_size_gb = 20
  }

  network_interface {
    network    = google_compute_network.ainflue_vpc.name
    subnetwork = google_compute_subnetwork.ainflue_subnet[0].name
  }

  service_account {
    email  = google_service_account.compute_service_account.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = file("${path.module}/scripts/startup.sh")

  tags = ["ainflue-app"]
}

resource "google_compute_instance_template" "ainflue_api_template" {
  name        = "${var.environment}-ainflue-api-template"
  description = "Ainflue API instance template"
  project     = google_project.ainflue_project.project_id

  machine_type = var.gcp_api_machine_type
  region       = var.gcp_primary_region

  disk {
    source_image = "debian-cloud/debian-11"
    auto_delete  = true
    boot         = true
    disk_type    = "pd-ssd"
    disk_size_gb = 20
  }

  network_interface {
    network    = google_compute_network.ainflue_vpc.name
    subnetwork = google_compute_subnetwork.ainflue_subnet[0].name
  }

  service_account {
    email  = google_service_account.compute_service_account.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = file("${path.module}/scripts/api-startup.sh")

  tags = ["ainflue-api"]
}

resource "google_compute_instance_template" "ainflue_ai_template" {
  name        = "${var.environment}-ainflue-ai-template"
  description = "Ainflue AI instance template"
  project     = google_project.ainflue_project.project_id

  machine_type = var.gcp_ai_machine_type
  region       = var.gcp_primary_region

  disk {
    source_image = "debian-cloud/debian-11"
    auto_delete  = true
    boot         = true
    disk_type    = "pd-ssd"
    disk_size_gb = 50
  }

  network_interface {
    network    = google_compute_network.ainflue_vpc.name
    subnetwork = google_compute_subnetwork.ainflue_subnet[0].name
  }

  service_account {
    email  = google_service_account.compute_service_account.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = file("${path.module}/scripts/ai-startup.sh")

  tags = ["ainflue-ai"]
}

# Compute Service Account
resource "google_service_account" "compute_service_account" {
  account_id   = "${var.environment}-ainflue-compute-sa"
  display_name = "Ainflue Compute Service Account"
  project      = google_project.ainflue_project.project_id
}

# Autoscaler for main application
resource "google_compute_autoscaler" "ainflue_autoscaler" {
  name    = "${var.environment}-ainflue-autoscaler"
  zone    = "${var.gcp_primary_region}-a"
  target  = google_compute_instance_group_manager.ainflue_igm.id
  project = google_project.ainflue_project.project_id

  autoscaling_policy {
    max_replicas    = var.gcp_max_instances
    min_replicas    = var.gcp_min_instances
    cooldown_period = 60

    cpu_utilization {
      target = 0.7
    }

    load_balancing_utilization {
      target = 0.8
    }
  }
}

# Cloud CDN
resource "google_compute_backend_bucket" "ainflue_cdn" {
  name        = "${var.environment}-ainflue-cdn"
  description = "Ainflue CDN backend bucket"
  bucket_name = google_storage_bucket.ainflue_storage.name
  enable_cdn  = true
  project     = google_project.ainflue_project.project_id

  cdn_policy {
    cache_mode                   = "CACHE_ALL_STATIC"
    default_ttl                  = 3600
    max_ttl                      = 86400
    client_ttl                   = 3600
    negative_caching             = true
    serve_while_stale           = 86400
    
    cache_key_policy {
      include_protocol = true
      include_host     = true
      include_query_string = false
    }
  }
}

# Azure ExpressRoute for hybrid connectivity
resource "azurerm_express_route_circuit" "ainflue_expressroute" {
  count = var.enable_azure_expressroute ? 1 : 0

  name                  = "${var.environment}-ainflue-expressroute"
  resource_group_name   = azurerm_resource_group.ainflue_rg.name
  location              = var.azure_primary_region
  service_provider_name = var.azure_expressroute_provider
  peering_location      = var.azure_expressroute_location
  bandwidth_in_mbps     = var.azure_expressroute_bandwidth

  sku {
    tier   = "Standard"
    family = "MeteredData"
  }

  tags = {
    Environment = var.environment
    Project     = "Ainflue"
  }
}

# Network Security Rules
resource "google_compute_firewall" "ainflue_ingress_rules" {
  name    = "${var.environment}-ainflue-ingress"
  network = google_compute_network.ainflue_vpc.name
  project = google_project.ainflue_project.project_id

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ainflue-app", "ainflue-api", "ainflue-ai"]
}

resource "google_compute_firewall" "ainflue_internal_rules" {
  name    = "${var.environment}-ainflue-internal"
  network = google_compute_network.ainflue_vpc.name
  project = google_project.ainflue_project.project_id

  allow {
    protocol = "tcp"
    ports    = ["1-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["1-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [
    google_compute_subnetwork.ainflue_subnet[0].ip_cidr_range,
    google_compute_subnetwork.ainflue_subnet[0].secondary_ip_range[0].ip_cidr_range,
    google_compute_subnetwork.ainflue_subnet[0].secondary_ip_range[1].ip_cidr_range
  ]
}