# MongoDB Deployment Guide
# Ainflue Platform Database Layer

## 📋 PROJECT INFORMATION
**Project:** Ainflue - AI-Powered Influencer Agent Platform  
**Module:** MongoDB Deployment Guide  
**Version:** 1.0.0  
**Last Updated:** September 12, 2025  

## 👥 TEAM SPECIALTIES
- **Lead DevOps Engineer:** Fahed Mlaiel (mlaiel@live.de)
- **Infrastructure Architect:** Fahed Mlaiel (mlaiel@live.de)
- **Cloud Deployment Specialist:** Fahed Mlaiel (mlaiel@live.de)
- **Kubernetes Expert:** Fahed Mlaiel (mlaiel@live.de)

## ⚠️ INTELLECTUAL PROPERTY WARNING
**CRITICAL NOTICE:** This deployment guide and all related intellectual property are the exclusive property of **Fahed Mlaiel**. Any unauthorized use, reproduction, or distribution is strictly prohibited.

**Contact for Authorization:** mlaiel@live.de

---

# 🚀 PRODUCTION DEPLOYMENT GUIDE

## 🎯 Deployment Objectives

### 🔧 Infrastructure Goals
- **High Availability**: 99.99% uptime with zero-downtime deployments
- **Auto-Scaling**: Dynamic scaling based on demand and performance metrics
- **Multi-Cloud**: Deploy across AWS, GCP, Azure, and on-premise
- **Security First**: Zero-trust architecture with encryption everywhere
- **Monitoring**: Comprehensive observability and alerting
- **Disaster Recovery**: Automated backup and recovery procedures
- **Compliance**: GDPR, HIPAA, PCI-DSS compliant infrastructure

---

## 🏗️ DEPLOYMENT ARCHITECTURE

### 🌐 Multi-Cloud Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        LOAD BALANCER LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│  AWS ALB   │  GCP LB    │  Azure LB   │  HAProxy    │  NGINX     │
│  (US-East) │ (US-West)  │  (Europe)   │ (On-Prem)   │ (Failover) │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│ Kubernetes Clusters (Multi-Region, Multi-Cloud)                │
│ AWS EKS │ GCP GKE │ Azure AKS │ On-Premise K8s │ Edge Locations │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│           MongoDB Sharded Cluster (Multi-Region)               │
│ Config Servers │ Shard 1 │ Shard 2 │ Shard 3 │ Mongos Routers │
│   (3 Replicas)  │(3 Nodes)│(3 Nodes)│(3 Nodes)│  (Multi-AZ)    │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│ AWS EBS │ GCP PD │ Azure Disk │ NetApp │ Object Storage (Backup) │
│ (NVMe)  │ (SSD)  │   (Premium) │ (SAN)  │    (S3/GCS/Blob)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ☁️ CLOUD-SPECIFIC DEPLOYMENTS

### 🌟 AWS Deployment

#### 1. EKS Cluster Configuration
```yaml
# aws-eks-cluster.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mongodb-config
  namespace: mongodb
data:
  mongodb.conf: |
    # MongoDB Configuration for AWS EKS
    net:
      port: 27017
      bindIpAll: true
      tls:
        mode: requireTLS
        certificateKeyFile: /etc/ssl/mongodb.pem
        CAFile: /etc/ssl/ca.pem
        
    security:
      authorization: enabled
      clusterAuthMode: x509
      
    storage:
      dbPath: /data/db
      engine: wiredTiger
      wiredTiger:
        engineConfig:
          cacheSizeGB: 4
          directoryForIndexes: true
          journalCompressor: snappy
        collectionConfig:
          blockCompressor: snappy
          
    replication:
      replSetName: rs0
      
    sharding:
      clusterRole: shardsvr
      
    operationProfiling:
      slowOpThresholdMs: 100
      mode: slowOp
      
    setParameter:
      enableLocalhostAuthBypass: false
      authenticationMechanisms: SCRAM-SHA-256,MONGODB-X509

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb-shard
  namespace: mongodb
spec:
  serviceName: mongodb-shard
  replicas: 3
  selector:
    matchLabels:
      app: mongodb-shard
  template:
    metadata:
      labels:
        app: mongodb-shard
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: password
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
        - name: mongodb-config
          mountPath: /etc/mongod.conf
          subPath: mongodb.conf
        - name: mongodb-ssl
          mountPath: /etc/ssl
        livenessProbe:
          exec:
            command:
            - mongo
            - --eval
            - "db.adminCommand('ping')"
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - mongo
            - --eval
            - "db.adminCommand('ping')"
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "4Gi"
            cpu: "1000m"
          limits:
            memory: "8Gi"
            cpu: "2000m"
      volumes:
      - name: mongodb-config
        configMap:
          name: mongodb-config
      - name: mongodb-ssl
        secret:
          secretName: mongodb-ssl-secret
  volumeClaimTemplates:
  - metadata:
      name: mongodb-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "gp3-fast"
      resources:
        requests:
          storage: 100Gi
```

#### 2. AWS Infrastructure as Code (Terraform)
```hcl
# aws-infrastructure.tf
provider "aws" {
  region = var.aws_region
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = "ainflue-mongodb-cluster"
  cluster_version = "1.28"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  # Enable cluster logging
  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  
  # Node groups
  node_groups = {
    mongodb_nodes = {
      desired_capacity = 6
      max_capacity     = 12
      min_capacity     = 3
      
      instance_types = ["m5.2xlarge"]
      
      k8s_labels = {
        Environment = "production"
        Application = "mongodb"
      }
      
      additional_tags = {
        ExtraTag = "mongodb-nodes"
      }
      
      # Use latest EKS optimized AMI
      ami_type = "AL2_x86_64"
      
      # Enable monitoring
      enable_monitoring = true
    }
  }
  
  # OIDC Provider for service accounts
  enable_irsa = true
  
  tags = {
    Environment = "production"
    Project     = "ainflue"
  }
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "ainflue-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = true
  enable_dns_hostnames = true
  enable_dns_support = true
  
  tags = {
    Environment = "production"
    Project     = "ainflue"
  }
}

# EBS Storage Class for high-performance storage
resource "kubernetes_storage_class" "gp3_fast" {
  metadata {
    name = "gp3-fast"
  }
  
  storage_provisioner = "ebs.csi.aws.com"
  reclaim_policy      = "Retain"
  volume_binding_mode = "WaitForFirstConsumer"
  
  parameters = {
    type = "gp3"
    iops = "3000"
    throughput = "125"
    encrypted = "true"
  }
}

# Application Load Balancer
resource "aws_lb" "mongodb_alb" {
  name               = "ainflue-mongodb-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = module.vpc.public_subnets
  
  enable_deletion_protection = true
  
  tags = {
    Environment = "production"
    Project     = "ainflue"
  }
}
```

### 🔵 Google Cloud Platform Deployment

#### 1. GKE Cluster Configuration
```yaml
# gcp-gke-cluster.yaml
apiVersion: container.cnrm.cloud.google.com/v1beta1
kind: ContainerCluster
metadata:
  name: ainflue-mongodb-cluster
  namespace: default
spec:
  location: us-central1
  initialNodeCount: 1
  
  # Enable autopilot for fully managed experience
  enableAutopilot: true
  
  # Network configuration
  networkRef:
    name: ainflue-vpc
  subnetworkRef:
    name: ainflue-subnet
    
  # Security configuration
  masterAuth:
    clusterCaCertificate: ""
  
  # Enable workload identity
  workloadIdentityConfig:
    workloadPool: PROJECT_ID.svc.id.goog
    
  # Monitoring and logging
  monitoringConfig:
    enableComponents:
    - SYSTEM_COMPONENTS
    - WORKLOADS
    
  loggingConfig:
    enableComponents:
    - SYSTEM_COMPONENTS
    - WORKLOADS
    
  # Node pool configuration for MongoDB
  nodePools:
  - name: mongodb-pool
    initialNodeCount: 3
    nodeConfig:
      machineType: n2-highmem-4
      diskSizeGb: 100
      diskType: pd-ssd
      
      # Enable monitoring
      metadata:
        disable-legacy-endpoints: "true"
        
      # Security
      serviceAccount: mongodb-sa@PROJECT_ID.iam.gserviceaccount.com
      oauthScopes:
      - https://www.googleapis.com/auth/devstorage.read_only
      - https://www.googleapis.com/auth/logging.write
      - https://www.googleapis.com/auth/monitoring
      
    autoscaling:
      enabled: true
      minNodeCount: 3
      maxNodeCount: 10
      
    management:
      autoUpgrade: true
      autoRepair: true
```

#### 2. GCP Terraform Configuration
```hcl
# gcp-infrastructure.tf
provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

# GKE Cluster
resource "google_container_cluster" "mongodb_cluster" {
  name     = "ainflue-mongodb-cluster"
  location = var.gcp_region
  
  # Remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1
  
  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.gcp_project}.svc.id.goog"
  }
  
  # Network
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name
  
  # Enable features
  addons_config {
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
    
    network_policy_config {
      enabled = true
    }
  }
  
  # Monitoring and logging
  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }
  
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }
}

# Node pool for MongoDB
resource "google_container_node_pool" "mongodb_nodes" {
  name       = "mongodb-pool"
  location   = var.gcp_region
  cluster    = google_container_cluster.mongodb_cluster.name
  node_count = 3
  
  node_config {
    preemptible  = false
    machine_type = "n2-highmem-4"
    
    # Service account
    service_account = google_service_account.mongodb_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]
    
    # Storage
    disk_size_gb = 100
    disk_type    = "pd-ssd"
    
    metadata = {
      disable-legacy-endpoints = "true"
    }
  }
  
  autoscaling {
    min_node_count = 3
    max_node_count = 10
  }
  
  management {
    auto_repair  = true
    auto_upgrade = true
  }
}
```

### 🔷 Azure Deployment

#### 1. AKS Cluster Configuration
```yaml
# azure-aks-cluster.yaml
apiVersion: containerservice.azure.com/v1beta1
kind: ManagedCluster
metadata:
  name: ainflue-mongodb-cluster
  location: East US 2
spec:
  dnsPrefix: ainflue-mongodb
  
  # Node pools
  agentPoolProfiles:
  - name: mongodb
    count: 3
    vmSize: Standard_D4s_v3
    osDiskSizeGB: 100
    osType: Linux
    
    # Enable auto-scaling
    enableAutoScaling: true
    minCount: 3
    maxCount: 10
    
    # Node labels
    nodeLabels:
      workload: mongodb
      
  # Network configuration
  networkProfile:
    networkPlugin: azure
    serviceCidr: "10.2.0.0/24"
    dnsServiceIP: "10.2.0.10"
    dockerBridgeCidr: "172.17.0.1/16"
    
  # Enable managed identity
  identity:
    type: SystemAssigned
    
  # Enable monitoring
  addonProfiles:
    omsagent:
      enabled: true
      config:
        logAnalyticsWorkspaceResourceID: /subscriptions/.../Microsoft.OperationalInsights/workspaces/...
        
  # Enable RBAC
  enableRBAC: true
  
  # Kubernetes version
  kubernetesVersion: "1.28"
```

#### 2. Azure Terraform Configuration
```hcl
# azure-infrastructure.tf
provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "mongodb" {
  name     = "ainflue-mongodb-rg"
  location = var.azure_region
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "mongodb" {
  name                = "ainflue-mongodb-aks"
  location            = azurerm_resource_group.mongodb.location
  resource_group_name = azurerm_resource_group.mongodb.name
  dns_prefix          = "ainflue-mongodb"
  kubernetes_version  = "1.28"
  
  default_node_pool {
    name                = "mongodb"
    node_count          = 3
    vm_size             = "Standard_D4s_v3"
    os_disk_size_gb     = 100
    enable_auto_scaling = true
    min_count           = 3
    max_count           = 10
    
    node_labels = {
      workload = "mongodb"
    }
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  # Network configuration
  network_profile {
    network_plugin = "azure"
    service_cidr   = "10.2.0.0/24"
    dns_service_ip = "10.2.0.10"
  }
  
  # Enable monitoring
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.mongodb.id
  }
  
  # Enable RBAC
  role_based_access_control {
    enabled = true
  }
  
  tags = {
    Environment = "production"
    Project     = "ainflue"
  }
}
```

---

## 🐳 CONTAINERIZATION

### 📦 Docker Images

#### 1. Production MongoDB Dockerfile
```dockerfile
# Dockerfile.mongodb-prod
FROM mongo:7.0-jammy

# Install additional tools
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Create MongoDB user
RUN groupadd -r mongodb && useradd -r -g mongodb mongodb

# Create directories
RUN mkdir -p /data/db /data/configdb /var/log/mongodb \
    && chown -R mongodb:mongodb /data/db /data/configdb /var/log/mongodb

# Copy configuration files
COPY configs/mongod.conf /etc/mongod.conf
COPY scripts/docker-entrypoint.sh /usr/local/bin/
COPY scripts/mongo-init.js /docker-entrypoint-initdb.d/

# Copy SSL certificates
COPY ssl/ /etc/ssl/mongodb/

# Set permissions
RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && chmod 600 /etc/ssl/mongodb/*

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD mongo --eval "db.adminCommand('ping')" || exit 1

# Switch to mongodb user
USER mongodb

# Expose port
EXPOSE 27017

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["mongod", "--config", "/etc/mongod.conf"]
```

#### 2. MongoDB Monitoring Sidecar
```dockerfile
# Dockerfile.mongodb-exporter
FROM prom/mongodb-exporter:latest

# Copy custom configuration
COPY configs/mongodb-exporter.yml /etc/mongodb-exporter/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9216/metrics || exit 1

EXPOSE 9216

CMD ["--config.file=/etc/mongodb-exporter/mongodb-exporter.yml"]
```

### 🔧 Docker Compose for Development
```yaml
# docker-compose.mongodb.yml
version: '3.8'

services:
  # MongoDB Config Servers
  config1:
    image: mongo:7.0
    command: mongod --configsvr --replSet configReplSet --port 27017
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
    volumes:
      - config1_data:/data/db
      - ./configs/mongod-config.conf:/etc/mongod.conf
    networks:
      - mongodb-network
    
  config2:
    image: mongo:7.0
    command: mongod --configsvr --replSet configReplSet --port 27017
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
    volumes:
      - config2_data:/data/db
      - ./configs/mongod-config.conf:/etc/mongod.conf
    networks:
      - mongodb-network
      
  config3:
    image: mongo:7.0
    command: mongod --configsvr --replSet configReplSet --port 27017
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
    volumes:
      - config3_data:/data/db
      - ./configs/mongod-config.conf:/etc/mongod.conf
    networks:
      - mongodb-network

  # MongoDB Shard 1
  shard1a:
    image: mongo:7.0
    command: mongod --shardsvr --replSet shard1ReplSet --port 27017
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
    volumes:
      - shard1a_data:/data/db
      - ./configs/mongod-shard.conf:/etc/mongod.conf
    networks:
      - mongodb-network
      
  shard1b:
    image: mongo:7.0
    command: mongod --shardsvr --replSet shard1ReplSet --port 27017
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
    volumes:
      - shard1b_data:/data/db
      - ./configs/mongod-shard.conf:/etc/mongod.conf
    networks:
      - mongodb-network
      
  shard1c:
    image: mongo:7.0
    command: mongod --shardsvr --replSet shard1ReplSet --port 27017
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
    volumes:
      - shard1c_data:/data/db
      - ./configs/mongod-shard.conf:/etc/mongod.conf
    networks:
      - mongodb-network

  # Mongos Router
  mongos:
    image: mongo:7.0
    command: mongos --configdb configReplSet/config1:27017,config2:27017,config3:27017 --port 27017
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
    ports:
      - "27017:27017"
    depends_on:
      - config1
      - config2
      - config3
      - shard1a
      - shard1b
      - shard1c
    networks:
      - mongodb-network

  # MongoDB Monitoring
  mongodb-exporter:
    image: percona/mongodb_exporter:latest
    command: --mongodb.uri=mongodb://admin:${MONGODB_ROOT_PASSWORD}@mongos:27017/admin
    ports:
      - "9216:9216"
    depends_on:
      - mongos
    networks:
      - mongodb-network

volumes:
  config1_data:
  config2_data:
  config3_data:
  shard1a_data:
  shard1b_data:
  shard1c_data:

networks:
  mongodb-network:
    driver: bridge
```

---

## 🎛️ CONFIGURATION MANAGEMENT

### ⚙️ Environment-Specific Configurations

#### 1. Production Configuration
```yaml
# configs/production.yaml
mongodb:
  # Connection settings
  connection:
    host: "mongodb-cluster.ainflue.com"
    port: 27017
    database: "ainflue_prod"
    replica_set: "rs0"
    ssl: true
    ssl_cert_reqs: "CERT_REQUIRED"
    ssl_ca_certs: "/etc/ssl/mongodb/ca.pem"
    ssl_certfile: "/etc/ssl/mongodb/client.pem"
    
  # Authentication
  auth:
    mechanism: "SCRAM-SHA-256"
    source: "admin"
    
  # Connection pool
  pool:
    min_size: 10
    max_size: 100
    max_idle_time_ms: 30000
    wait_queue_timeout_ms: 10000
    server_selection_timeout_ms: 5000
    
  # Performance
  performance:
    read_preference: "secondaryPreferred"
    read_concern: "majority"
    write_concern:
      w: "majority"
      j: true
      wtimeout: 10000
      
  # Monitoring
  monitoring:
    enable_command_monitoring: true
    enable_connection_monitoring: true
    enable_server_monitoring: true
    slow_operation_threshold_ms: 100
    
  # Security
  security:
    encrypt_fields: true
    audit_logging: true
    compliance_mode: "strict"
    
# Application settings
application:
  environment: "production"
  debug: false
  log_level: "INFO"
  
  # Feature flags
  features:
    ai_processing: true
    real_time_analytics: true
    advanced_search: true
    multi_platform_sync: true
    
# Infrastructure
infrastructure:
  kubernetes:
    namespace: "mongodb-prod"
    storage_class: "fast-ssd"
    resource_limits:
      cpu: "4000m"
      memory: "8Gi"
    resource_requests:
      cpu: "2000m"
      memory: "4Gi"
      
  monitoring:
    prometheus_endpoint: "https://prometheus.ainflue.com"
    grafana_dashboard: "https://grafana.ainflue.com"
    alert_manager: "https://alerts.ainflue.com"
    
  backup:
    schedule: "0 2 * * *"  # Daily at 2 AM
    retention_days: 30
    cloud_storage: "s3://ainflue-backups/mongodb"
    encryption: true
```

#### 2. Staging Configuration
```yaml
# configs/staging.yaml
mongodb:
  connection:
    host: "mongodb-staging.ainflue.com"
    port: 27017
    database: "ainflue_staging"
    replica_set: "rs0-staging"
    ssl: true
    
  pool:
    min_size: 5
    max_size: 50
    
  performance:
    read_preference: "secondary"
    
application:
  environment: "staging"
  debug: true
  log_level: "DEBUG"
  
  features:
    ai_processing: true
    real_time_analytics: false
    advanced_search: true
    multi_platform_sync: false

infrastructure:
  kubernetes:
    namespace: "mongodb-staging"
    resource_limits:
      cpu: "2000m"
      memory: "4Gi"
```

#### 3. Development Configuration
```yaml
# configs/development.yaml
mongodb:
  connection:
    host: "localhost"
    port: 27017
    database: "ainflue_dev"
    ssl: false
    
  pool:
    min_size: 2
    max_size: 10
    
  performance:
    read_preference: "primary"
    
application:
  environment: "development"
  debug: true
  log_level: "DEBUG"
  
  features:
    ai_processing: false
    real_time_analytics: false
    advanced_search: false
    multi_platform_sync: false
```

---

## 🚀 CI/CD PIPELINE

### 🔄 GitHub Actions Workflow

#### 1. Build and Test Pipeline
```yaml
# .github/workflows/mongodb-ci.yml
name: MongoDB CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    paths: ['mongodb/**']
  pull_request:
    branches: [main]
    paths: ['mongodb/**']

env:
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: ainflue/mongodb

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:7.0
        env:
          MONGO_INITDB_ROOT_USERNAME: admin
          MONGO_INITDB_ROOT_PASSWORD: password
        ports:
          - 27017:27017
        options: >-
          --health-cmd "mongo --eval 'db.adminCommand(\"ping\")'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
          
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
        
    - name: Run unit tests
      run: |
        cd mongodb
        python -m pytest tests/ -v --cov=. --cov-report=xml
        
    - name: Run integration tests
      env:
        MONGODB_URI: mongodb://admin:password@localhost:27017/test?authSource=admin
      run: |
        cd mongodb
        python -m pytest tests/integration/ -v
        
    - name: Run security tests
      run: |
        cd mongodb
        python -m pytest tests/security/ -v
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./mongodb/coverage.xml
        
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.DOCKER_REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
          
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: ./mongodb
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
        
    - name: Deploy to staging
      run: |
        kubectl apply -f kubernetes/staging/
        kubectl rollout status deployment/mongodb-deployment -n mongodb-staging
        
    - name: Run smoke tests
      run: |
        kubectl run smoke-test --image=ainflue/smoke-tests:latest \
          --env="MONGODB_URI=${{ secrets.MONGODB_URI_STAGING }}" \
          --restart=Never -n mongodb-staging
        kubectl wait --for=condition=complete job/smoke-test -n mongodb-staging --timeout=300s
        
  deploy-production:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
        
    - name: Deploy to production
      run: |
        kubectl apply -f kubernetes/production/
        kubectl rollout status deployment/mongodb-deployment -n mongodb-prod --timeout=600s
        
    - name: Verify deployment
      run: |
        kubectl get pods -n mongodb-prod
        kubectl run health-check --image=ainflue/health-check:latest \
          --env="MONGODB_URI=${{ secrets.MONGODB_URI_PRODUCTION }}" \
          --restart=Never -n mongodb-prod
        kubectl wait --for=condition=complete job/health-check -n mongodb-prod --timeout=300s
```

#### 2. Security Scanning Pipeline
```yaml
# .github/workflows/security-scan.yml
name: Security Scanning

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: './mongodb'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
        
    - name: Run Bandit security linter
      run: |
        pip install bandit
        bandit -r mongodb/ -f json -o bandit-results.json
        
    - name: Run Safety dependency check
      run: |
        pip install safety
        safety check --json --output safety-results.json
        
    - name: Run Semgrep static analysis
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/secrets
          p/python
```

---

## 📊 MONITORING & OBSERVABILITY

### 📈 Prometheus Monitoring Stack

#### 1. MongoDB Exporter Configuration
```yaml
# monitoring/mongodb-exporter.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb-exporter
  namespace: mongodb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb-exporter
  template:
    metadata:
      labels:
        app: mongodb-exporter
    spec:
      containers:
      - name: mongodb-exporter
        image: percona/mongodb_exporter:latest
        ports:
        - containerPort: 9216
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: mongodb-exporter-secret
              key: mongodb-uri
        args:
        - --mongodb.uri=$(MONGODB_URI)
        - --mongodb.direct-connect
        - --mongodb.global-conn-pool
        - --collect-all
        - --compatible-mode
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /metrics
            port: 9216
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /metrics
            port: 9216
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb-exporter
  namespace: mongodb
  labels:
    app: mongodb-exporter
spec:
  ports:
  - port: 9216
    targetPort: 9216
    name: metrics
  selector:
    app: mongodb-exporter
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: mongodb-exporter
  namespace: mongodb
spec:
  selector:
    matchLabels:
      app: mongodb-exporter
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

#### 2. Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "id": null,
    "title": "MongoDB Cluster Overview",
    "tags": ["mongodb", "ainflue"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "MongoDB Connections",
        "type": "stat",
        "targets": [
          {
            "expr": "mongodb_connections{job=\"mongodb-exporter\"}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 80}
              ]
            },
            "unit": "short"
          }
        }
      },
      {
        "id": 2,
        "title": "Operations per Second",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(mongodb_op_counters_total[5m])"
          }
        ]
      },
      {
        "id": 3,
        "title": "Replica Set Status",
        "type": "table",
        "targets": [
          {
            "expr": "mongodb_replset_member_health"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

---

## 📞 SUPPORT & CONTACT

**DevOps Engineering:** Fahed Mlaiel (mlaiel@live.de)  
**Project:** Ainflue Platform  
**Module:** MongoDB Deployment Guide  
**Documentation Version:** 1.0.0  

---

**© 2025 Fahed Mlaiel - All Rights Reserved**  
**Contact:** mlaiel@live.de  
**Unauthorized use prohibited - Legal action will be taken**