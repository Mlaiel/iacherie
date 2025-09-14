# HashiCorp Vault Configuration for IA Influencer Agent Platform
# Production-ready configuration with high availability and security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

# Cluster configuration
cluster_name = "ia-influencer-vault"

# Storage backend - Consul for HA
storage "consul" {
  address = "consul.ia-influencer.svc.cluster.local:8500"
  path    = "vault/"
  
  # Service discovery
  service = "vault"
  service_tags = "ia-influencer,vault,security"
  
  # Security
  scheme = "https"
  tls_ca_file = "/vault/tls/consul-ca.pem"
  tls_cert_file = "/vault/tls/consul-client.pem"
  tls_key_file = "/vault/tls/consul-client-key.pem"
  tls_min_version = "tls12"
}

# High Availability configuration
ha_storage "consul" {
  address = "consul.ia-influencer.svc.cluster.local:8500"
  path    = "vault-ha/"
  
  # HA settings
  redirect_addr = "https://vault.ia-influencer.com:8200"
  cluster_addr  = "https://vault.ia-influencer.com:8201"
}

# Network listener configuration
listener "tcp" {
  address         = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  
  # TLS configuration
  tls_cert_file = "/vault/tls/vault.pem"
  tls_key_file  = "/vault/tls/vault-key.pem"
  tls_client_ca_file = "/vault/tls/ca.pem"
  
  # Security headers
  tls_min_version = "tls12"
  tls_cipher_suites = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384"
  
  # Performance
  tls_prefer_server_cipher_suites = true
  tls_require_and_verify_client_cert = true
}

# Telemetry for monitoring
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
  
  # Statsite configuration
  statsite_address = "statsite.monitoring.svc.cluster.local:8125"
  
  # Dogstatsd configuration  
  dogstatsd_addr = "datadog-agent.monitoring.svc.cluster.local:8125"
  dogstatsd_tags = ["environment:production", "service:vault", "platform:ia-influencer"]
}

# Seal configuration - Auto-unseal with cloud KMS
seal "azurekeyvault" {
  tenant_id      = "AZURE_TENANT_ID"
  client_id      = "AZURE_CLIENT_ID" 
  client_secret  = "AZURE_CLIENT_SECRET"
  vault_name     = "ia-influencer-vault"
  key_name       = "vault-unseal-key"
}

# API configuration
api_addr = "https://vault.ia-influencer.com:8200"
cluster_addr = "https://vault.ia-influencer.com:8201"

# UI configuration
ui = true

# Performance and caching
cache_size = "512MB"
disable_cache = false
disable_mlock = false

# Logging
log_level = "INFO"
log_format = "json"
log_file = "/vault/logs/vault.log"
log_rotate_duration = "24h"
log_rotate_max_files = 30

# Plugin directory
plugin_directory = "/vault/plugins"

# Default lease TTL and max lease TTL
default_lease_ttl = "768h"  # 32 days
max_lease_ttl = "8760h"     # 1 year

# Enterprise features (if using Vault Enterprise)
# license_path = "/vault/license/vault.hclic"

# Raw storage endpoint (disabled for security)
raw_storage_endpoint = false

# Introspection endpoint (disabled in production)
introspection_endpoint = false

# Cluster configuration for replication
cluster {
  name = "ia-influencer-primary"
  
  # Performance replication
  performance_standby = true
  
  # Disaster recovery
  dr_operation_token_ttl = "1h"
}