# 🚀 Ainflue Infrastructure Deployment Guide

**Author:** Fahed Mlaiel <mlaiel@live.de>  
**Team:** DevOps Engineer + Infrastructure Specialist + Automation Expert  
**Version:** 1.0.0  
**Last Updated:** January 2025  

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Infrastructure Deployment](#infrastructure-deployment)
4. [Application Deployment](#application-deployment)
5. [Configuration Management](#configuration-management)
6. [Deployment Strategies](#deployment-strategies)
7. [Monitoring and Validation](#monitoring-and-validation)
8. [Troubleshooting](#troubleshooting)

---

## ⚡ Prerequisites

### Required Tools

#### Development Environment
```bash
# Install required tools
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### Cloud Provider CLIs
```bash
# Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login
```

### Access Requirements

#### AWS Credentials
```bash
# Configure AWS credentials
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set default.region us-east-1
aws configure set default.output json

# Verify access
aws sts get-caller-identity
```

#### GCP Credentials
```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project ainflue-infrastructure
gcloud auth application-default login

# Verify access
gcloud auth list
```

#### Azure Credentials
```bash
# Login to Azure
az login
az account set --subscription "ainflue-infrastructure"

# Verify access
az account show
```

---

## 🌍 Environment Setup

### Repository Structure
```
ainflue/
├── infrastructure/
│   ├── terraform/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   ├── modules/
│   │   └── global/
│   ├── kubernetes/
│   │   ├── base/
│   │   ├── overlays/
│   │   └── charts/
│   ├── ansible/
│   │   ├── playbooks/
│   │   ├── roles/
│   │   └── inventories/
│   └── scripts/
├── applications/
└── deployments/
```

### Environment Configuration

#### Development Environment
```bash
# Set environment variables
export ENVIRONMENT=dev
export CLUSTER_NAME=ainflue-dev
export REGION=us-east-1
export NAMESPACE=development

# Create environment configuration
cat > environments/dev/terraform.tfvars << EOF
environment = "dev"
cluster_name = "ainflue-dev"
region = "us-east-1"
node_instance_type = "t3.medium"
min_size = 1
max_size = 10
desired_capacity = 3
enable_cluster_autoscaler = true
enable_monitoring = true
EOF
```

#### Staging Environment
```bash
# Set environment variables
export ENVIRONMENT=staging
export CLUSTER_NAME=ainflue-staging
export REGION=us-east-1
export NAMESPACE=staging

# Create environment configuration
cat > environments/staging/terraform.tfvars << EOF
environment = "staging"
cluster_name = "ainflue-staging"
region = "us-east-1"
node_instance_type = "t3.large"
min_size = 2
max_size = 20
desired_capacity = 5
enable_cluster_autoscaler = true
enable_monitoring = true
enable_logging = true
EOF
```

#### Production Environment
```bash
# Set environment variables
export ENVIRONMENT=production
export CLUSTER_NAME=ainflue-prod
export REGION=us-east-1
export NAMESPACE=production

# Create environment configuration
cat > environments/production/terraform.tfvars << EOF
environment = "production"
cluster_name = "ainflue-prod"
region = "us-east-1"
node_instance_type = "t3.xlarge"
min_size = 5
max_size = 100
desired_capacity = 10
enable_cluster_autoscaler = true
enable_monitoring = true
enable_logging = true
enable_backup = true
multi_az = true
EOF
```

---

## 🏗️ Infrastructure Deployment

### Phase 1: Core Infrastructure

#### Step 1: Initialize Terraform
```bash
cd infrastructure/terraform/environments/$ENVIRONMENT

# Initialize Terraform
terraform init

# Plan infrastructure changes
terraform plan -var-file="terraform.tfvars"

# Apply infrastructure
terraform apply -var-file="terraform.tfvars" -auto-approve
```

#### Step 2: VPC and Networking
```hcl
# vpc.tf
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.region}a", "${var.region}b", "${var.region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Environment = var.environment
    Project = "ainflue"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}
```

#### Step 3: EKS Cluster
```hcl
# eks.tf
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 18.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.21"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Cluster access
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = true
  cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"]

  # Cluster encryption
  cluster_encryption_config = [{
    provider_key_arn = aws_kms_key.eks.arn
    resources        = ["secrets"]
  }]

  # Node groups
  node_groups = {
    general = {
      desired_capacity = var.desired_capacity
      max_capacity     = var.max_size
      min_capacity     = var.min_size

      instance_types = [var.node_instance_type]
      capacity_type  = "ON_DEMAND"

      k8s_labels = {
        Environment = var.environment
        NodeGroup   = "general"
      }

      additional_tags = {
        ExtraTag = "general-node-group"
      }
    }

    gpu = {
      desired_capacity = 1
      max_capacity     = 5
      min_capacity     = 0

      instance_types = ["p3.2xlarge"]
      capacity_type  = "ON_DEMAND"

      k8s_labels = {
        Environment = var.environment
        NodeGroup   = "gpu"
        "nvidia.com/gpu" = "true"
      }

      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }

  # OIDC Identity provider
  enable_irsa = true

  tags = {
    Environment = var.environment
    Project = "ainflue"
  }
}
```

### Phase 2: Storage Infrastructure

#### Step 1: RDS PostgreSQL
```hcl
# rds.tf
module "rds" {
  source = "terraform-aws-modules/rds/aws"
  version = "~> 3.0"

  identifier = "${var.cluster_name}-postgres"

  engine            = "postgres"
  engine_version    = "13.7"
  instance_class    = var.environment == "production" ? "db.r5.xlarge" : "db.t3.medium"
  allocated_storage = var.environment == "production" ? 500 : 100
  storage_encrypted = true

  name     = "ainflue"
  username = "ainflue_admin"
  password = random_password.postgres.result
  port     = "5432"

  vpc_security_group_ids = [aws_security_group.rds.id]
  subnet_group_name      = aws_db_subnet_group.rds.name

  # Backup configuration
  backup_retention_period = var.environment == "production" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  # Multi-AZ for production
  multi_az = var.environment == "production"

  # Enhanced Monitoring
  monitoring_interval = "60"
  monitoring_role_name = "${var.cluster_name}-postgres-monitoring"
  create_monitoring_role = true

  # Performance Insights
  performance_insights_enabled = true
  performance_insights_retention_period = 7

  tags = {
    Environment = var.environment
    Project = "ainflue"
  }
}
```

#### Step 2: ElastiCache Redis
```hcl
# elasticache.tf
resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.cluster_name}-redis"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id         = "${var.cluster_name}-redis"
  description                  = "Redis cluster for ${var.cluster_name}"
  
  engine               = "redis"
  engine_version       = "6.2"
  node_type           = var.environment == "production" ? "cache.r6g.large" : "cache.t3.micro"
  port                = 6379
  parameter_group_name = "default.redis6.x"
  
  num_cache_clusters = var.environment == "production" ? 3 : 1
  
  subnet_group_name    = aws_elasticache_subnet_group.redis.name
  security_group_ids   = [aws_security_group.redis.id]
  
  # Backup configuration
  snapshot_retention_limit = var.environment == "production" ? 7 : 1
  snapshot_window         = "03:00-05:00"
  
  # Encryption
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                = random_password.redis.result
  
  tags = {
    Environment = var.environment
    Project = "ainflue"
  }
}
```

### Phase 3: Security Configuration

#### Step 1: Security Groups
```hcl
# security-groups.tf
resource "aws_security_group" "eks_cluster" {
  name_prefix = "${var.cluster_name}-cluster"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-cluster-sg"
    Environment = var.environment
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.cluster_name}-rds"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  tags = {
    Name = "${var.cluster_name}-rds-sg"
    Environment = var.environment
  }
}
```

#### Step 2: IAM Roles and Policies
```hcl
# iam.tf
# EKS Service Role
resource "aws_iam_role" "eks_service_role" {
  name = "${var.cluster_name}-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project = "ainflue"
  }
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_service_role.name
}

# Node Group Role
resource "aws_iam_role" "eks_node_group" {
  name = "${var.cluster_name}-node-group"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_group.name
}
```

---

## 📦 Application Deployment

### Step 1: Configure kubectl
```bash
# Update kubeconfig
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Step 2: Install Core Components

#### Ingress Controller
```bash
# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.metrics.enabled=true \
  --set controller.podAnnotations."prometheus\.io/scrape"=true \
  --set controller.podAnnotations."prometheus\.io/port"=10254
```

#### Cert-Manager
```bash
# Install cert-manager for SSL certificates
helm repo add jetstack https://charts.jetstack.io
helm repo update

kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.11.0/cert-manager.crds.yaml

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.11.0 \
  --set installCRDs=true
```

#### Monitoring Stack
```bash
# Install Prometheus and Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin123 \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi
```

### Step 3: Deploy Ainflue Applications

#### Create Namespace
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ainflue
  labels:
    name: ainflue
    environment: production
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ainflue-quota
  namespace: ainflue
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "10"
    services: "20"
```

#### ConfigMap for Application Configuration
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ainflue-config
  namespace: ainflue
data:
  DATABASE_HOST: "ainflue-prod-postgres.region.rds.amazonaws.com"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "ainflue"
  REDIS_HOST: "ainflue-prod-redis.cache.amazonaws.com"
  REDIS_PORT: "6379"
  ENVIRONMENT: "production"
  LOG_LEVEL: "info"
  API_VERSION: "v1"
```

#### Secret for Sensitive Data
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ainflue-secrets
  namespace: ainflue
type: Opaque
data:
  DATABASE_PASSWORD: <base64-encoded-password>
  REDIS_PASSWORD: <base64-encoded-password>
  JWT_SECRET: <base64-encoded-jwt-secret>
  API_KEY: <base64-encoded-api-key>
```

#### Application Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainflue-api
  namespace: ainflue
  labels:
    app: ainflue-api
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ainflue-api
  template:
    metadata:
      labels:
        app: ainflue-api
        version: v1
    spec:
      containers:
      - name: api
        image: ainflue/api:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_HOST
          valueFrom:
            configMapKeyRef:
              name: ainflue-config
              key: DATABASE_HOST
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ainflue-secrets
              key: DATABASE_PASSWORD
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
```

#### Service Configuration
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ainflue-api-service
  namespace: ainflue
  labels:
    app: ainflue-api
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: ainflue-api
```

#### Ingress Configuration
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ainflue-ingress
  namespace: ainflue
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - api.ainflue.com
    secretName: ainflue-tls
  rules:
  - host: api.ainflue.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ainflue-api-service
            port:
              number: 80
```

### Step 4: Deploy with Kustomize
```bash
# Create kustomization.yaml
cat > kustomization.yaml << EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- namespace.yaml
- configmap.yaml
- secret.yaml
- deployment.yaml
- service.yaml
- ingress.yaml

commonLabels:
  environment: production
  project: ainflue

images:
- name: ainflue/api
  newTag: v1.2.3
EOF

# Apply all resources
kubectl apply -k .
```

---

## ⚙️ Configuration Management

### Ansible Playbooks

#### Infrastructure Setup Playbook
```yaml
# playbooks/infrastructure-setup.yml
---
- name: Setup Ainflue Infrastructure
  hosts: localhost
  gather_facts: false
  vars:
    environment: "{{ env | default('dev') }}"
    cluster_name: "ainflue-{{ environment }}"
    
  tasks:
    - name: Initialize Terraform
      terraform:
        project_path: "../terraform/environments/{{ environment }}"
        state: present
        force_init: true
        variables:
          environment: "{{ environment }}"
          cluster_name: "{{ cluster_name }}"
      register: terraform_output

    - name: Update kubeconfig
      shell: |
        aws eks update-kubeconfig --region us-east-1 --name {{ cluster_name }}
      
    - name: Install Helm charts
      kubernetes.core.helm:
        name: "{{ item.name }}"
        chart_ref: "{{ item.chart }}"
        release_namespace: "{{ item.namespace }}"
        create_namespace: true
        values: "{{ item.values | default({}) }}"
      loop:
        - name: ingress-nginx
          chart: ingress-nginx/ingress-nginx
          namespace: ingress-nginx
        - name: cert-manager
          chart: jetstack/cert-manager
          namespace: cert-manager
          values:
            installCRDs: true
        - name: prometheus
          chart: prometheus-community/kube-prometheus-stack
          namespace: monitoring
```

#### Application Deployment Playbook
```yaml
# playbooks/application-deployment.yml
---
- name: Deploy Ainflue Applications
  hosts: localhost
  gather_facts: false
  vars:
    environment: "{{ env | default('dev') }}"
    image_tag: "{{ tag | default('latest') }}"
    
  tasks:
    - name: Create namespace
      kubernetes.core.k8s:
        name: ainflue
        api_version: v1
        kind: Namespace
        state: present

    - name: Deploy ConfigMap
      kubernetes.core.k8s:
        definition:
          apiVersion: v1
          kind: ConfigMap
          metadata:
            name: ainflue-config
            namespace: ainflue
          data:
            DATABASE_HOST: "{{ database_host }}"
            DATABASE_PORT: "5432"
            ENVIRONMENT: "{{ environment }}"

    - name: Deploy application
      kubernetes.core.k8s:
        definition:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: ainflue-api
            namespace: ainflue
          spec:
            replicas: 3
            selector:
              matchLabels:
                app: ainflue-api
            template:
              metadata:
                labels:
                  app: ainflue-api
              spec:
                containers:
                - name: api
                  image: "ainflue/api:{{ image_tag }}"
                  ports:
                  - containerPort: 8000
```

### Helm Charts

#### Ainflue Application Chart
```yaml
# charts/ainflue/Chart.yaml
apiVersion: v2
name: ainflue
description: Ainflue Creator Economy Platform
type: application
version: 1.0.0
appVersion: "1.0.0"
dependencies:
- name: postgresql
  version: 11.9.13
  repository: https://charts.bitnami.com/bitnami
  condition: postgresql.enabled
- name: redis
  version: 17.3.7
  repository: https://charts.bitnami.com/bitnami
  condition: redis.enabled
```

```yaml
# charts/ainflue/values.yaml
replicaCount: 3

image:
  repository: ainflue/api
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.ainflue.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ainflue-tls
      hosts:
        - api.ainflue.com

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 100
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    postgresPassword: "supersecretpassword"
    database: "ainflue"

redis:
  enabled: true
  auth:
    enabled: true
    password: "supersecretpassword"
```

---

## 🚀 Deployment Strategies

### Blue-Green Deployment

#### Setup Blue-Green Environment
```bash
#!/bin/bash
# blue-green-deploy.sh

ENVIRONMENT=${1:-production}
NEW_VERSION=${2:-latest}
CURRENT_COLOR=$(kubectl get service ainflue-api-service -o jsonpath='{.spec.selector.color}' 2>/dev/null || echo "blue")
NEW_COLOR=$([ "$CURRENT_COLOR" = "blue" ] && echo "green" || echo "blue")

echo "Current environment: $CURRENT_COLOR"
echo "Deploying to: $NEW_COLOR"
echo "New version: $NEW_VERSION"

# Deploy to new color environment
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainflue-api-$NEW_COLOR
  namespace: ainflue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ainflue-api
      color: $NEW_COLOR
  template:
    metadata:
      labels:
        app: ainflue-api
        color: $NEW_COLOR
    spec:
      containers:
      - name: api
        image: ainflue/api:$NEW_VERSION
        ports:
        - containerPort: 8000
EOF

# Wait for deployment to be ready
kubectl rollout status deployment/ainflue-api-$NEW_COLOR -n ainflue --timeout=300s

# Run health checks
echo "Running health checks on $NEW_COLOR environment..."
GREEN_POD_IP=$(kubectl get pod -l color=$NEW_COLOR -o jsonpath='{.items[0].status.podIP}')
HEALTH_CHECK=$(kubectl run health-check --rm -i --restart=Never --image=curlimages/curl -- curl -s http://$GREEN_POD_IP:8000/health)

if [[ "$HEALTH_CHECK" == *"healthy"* ]]; then
    echo "Health check passed. Switching traffic to $NEW_COLOR"
    
    # Switch service to new color
    kubectl patch service ainflue-api-service -p '{"spec":{"selector":{"color":"'$NEW_COLOR'"}}}'
    
    echo "Traffic switched to $NEW_COLOR environment"
    echo "Waiting 5 minutes before cleanup..."
    sleep 300
    
    # Cleanup old deployment
    kubectl delete deployment ainflue-api-$CURRENT_COLOR -n ainflue
    echo "Blue-green deployment completed successfully"
else
    echo "Health check failed. Rolling back..."
    kubectl delete deployment ainflue-api-$NEW_COLOR -n ainflue
    exit 1
fi
```

### Canary Deployment

#### Canary Deployment with Istio
```yaml
# canary-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: ainflue-api-rollout
  namespace: ainflue
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 10m}
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 80
      - pause: {duration: 10m}
      analysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: ainflue-api-service
      trafficRouting:
        istio:
          virtualService:
            name: ainflue-api-vsvc
          destinationRule:
            name: ainflue-api-dest
            canarySubsetName: canary
            stableSubsetName: stable
  selector:
    matchLabels:
      app: ainflue-api
  template:
    metadata:
      labels:
        app: ainflue-api
    spec:
      containers:
      - name: api
        image: ainflue/api:latest
        ports:
        - containerPort: 8000
```

---

## 📊 Monitoring and Validation

### Deployment Validation Script
```bash
#!/bin/bash
# validate-deployment.sh

NAMESPACE=${1:-ainflue}
SERVICE_NAME=${2:-ainflue-api-service}

echo "Validating deployment in namespace: $NAMESPACE"

# Check pod status
echo "Checking pod status..."
kubectl get pods -n $NAMESPACE -l app=ainflue-api

# Check service endpoints
echo "Checking service endpoints..."
kubectl get endpoints -n $NAMESPACE $SERVICE_NAME

# Check ingress
echo "Checking ingress configuration..."
kubectl get ingress -n $NAMESPACE

# Health check
echo "Performing health check..."
EXTERNAL_IP=$(kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl -H "Host: api.ainflue.com" http://$EXTERNAL_IP/health

# Check metrics
echo "Checking application metrics..."
kubectl port-forward -n $NAMESPACE svc/$SERVICE_NAME 8080:80 &
PF_PID=$!
sleep 5
curl http://localhost:8080/metrics
kill $PF_PID

echo "Deployment validation completed"
```

### Automated Testing Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.21.0'
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Update kubeconfig
      run: aws eks update-kubeconfig --name ainflue-staging
    
    - name: Deploy to staging
      run: |
        kubectl apply -k overlays/staging
        kubectl rollout status deployment/ainflue-api -n ainflue-staging
    
    - name: Run integration tests
      run: |
        chmod +x scripts/integration-tests.sh
        ./scripts/integration-tests.sh staging
    
    - name: Deploy to production
      if: github.ref == 'refs/heads/main'
      run: |
        kubectl apply -k overlays/production
        kubectl rollout status deployment/ainflue-api -n ainflue-production
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Pod Startup Issues
```bash
# Check pod logs
kubectl logs -f deployment/ainflue-api -n ainflue

# Check pod events
kubectl describe pod -l app=ainflue-api -n ainflue

# Check resource constraints
kubectl top pods -n ainflue
kubectl describe nodes

# Common fix: Increase resource limits
kubectl patch deployment ainflue-api -n ainflue -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"memory":"2Gi","cpu":"1000m"}}}]}}}}'
```

#### 2. Service Discovery Issues
```bash
# Check service endpoints
kubectl get endpoints -n ainflue

# Check DNS resolution
kubectl run debug --rm -i --restart=Never --image=busybox -- nslookup ainflue-api-service.ainflue.svc.cluster.local

# Check network policies
kubectl get networkpolicies -n ainflue
```

#### 3. Ingress Issues
```bash
# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Check certificate status
kubectl describe certificate ainflue-tls -n ainflue

# Check external DNS
nslookup api.ainflue.com
```

#### 4. Database Connection Issues
```bash
# Test database connectivity
kubectl run postgres-client --rm -i --restart=Never --image=postgres:13 -- psql -h ainflue-prod-postgres.region.rds.amazonaws.com -U ainflue_admin -d ainflue -c "SELECT 1"

# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### Emergency Procedures

#### Rollback Deployment
```bash
# Quick rollback to previous version
kubectl rollout undo deployment/ainflue-api -n ainflue

# Rollback to specific revision
kubectl rollout history deployment/ainflue-api -n ainflue
kubectl rollout undo deployment/ainflue-api --to-revision=2 -n ainflue
```

#### Scale Down for Maintenance
```bash
# Scale down application
kubectl scale deployment ainflue-api --replicas=0 -n ainflue

# Scale up after maintenance
kubectl scale deployment ainflue-api --replicas=3 -n ainflue
```

#### Emergency Database Backup
```bash
# Create manual RDS snapshot
aws rds create-db-snapshot --db-instance-identifier ainflue-prod-postgres --db-snapshot-identifier emergency-backup-$(date +%Y%m%d%H%M%S)
```

---

## 📞 Support and Escalation

### On-Call Procedures

#### Severity Levels
- **P0:** System down, deploy failed
- **P1:** Performance degradation
- **P2:** Feature impaired
- **P3:** Enhancement request

#### Contact Information
- **DevOps Lead:** devops@ainflue.com
- **Infrastructure Team:** infrastructure@ainflue.com
- **Security Team:** security@ainflue.com
- **Emergency:** +1-xxx-xxx-xxxx

### Documentation Links
- **Infrastructure Architecture:** [INFRASTRUCTURE_ARCHITECTURE.md]
- **Security Compliance:** [SECURITY_COMPLIANCE.md]
- **Monitoring Setup:** [MONITORING_SETUP.md]
- **Performance Optimization:** [PERFORMANCE_OPTIMIZATION.md]

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
**Contact:** mlaiel@live.de  
**Legal Notice:** This deployment guide contains proprietary deployment procedures and infrastructure configurations.