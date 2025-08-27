# Ainflue Production Deployment Guide

**AI-Powered Content Protection & Monetization Platform**

Author: Fahed Mlaiel (mlaiel@live.de)  
Version: 2.0.0  
Last Updated: August 27, 2025

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Database Configuration](#database-configuration)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Monitoring Setup](#monitoring-setup)
8. [SSL/TLS Configuration](#ssltls-configuration)
9. [Environment Variables](#environment-variables)
10. [Health Checks](#health-checks)
11. [Backup and Recovery](#backup-and-recovery)
12. [Scaling Configuration](#scaling-configuration)
13. [Security Hardening](#security-hardening)
14. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum Production Requirements:**
- Kubernetes cluster with 3+ nodes
- 16GB RAM per node
- 100GB SSD storage per node
- 10 Gbps network connectivity
- Load balancer (NGINX/HAProxy)

**Recommended Production Setup:**
- Kubernetes cluster with 5+ nodes
- 32GB RAM per node
- 500GB NVMe SSD storage per node
- CDN integration (CloudFlare/AWS CloudFront)
- Multi-region deployment

### Required Services

**External Dependencies:**
- PostgreSQL 14+ (managed service recommended)
- Redis 6+ cluster
- MongoDB 5+ replica set
- AWS S3 or compatible object storage
- Email service (SendGrid/AWS SES)
- SMS service (Twilio)

**AI/ML Services:**
- GPU nodes for ML inference (optional but recommended)
- TensorFlow Serving
- PyTorch Serving
- FAISS vector database

---

## Infrastructure Setup

### Cloud Provider Configuration

#### AWS Setup
```bash
# Create VPC and subnets
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ainflue-vpc}]'

# Create EKS cluster
eksctl create cluster \
  --name ainflue-prod \
  --version 1.27 \
  --region us-west-2 \
  --nodegroup-name ainflue-workers \
  --node-type m5.xlarge \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed
```

#### Azure Setup
```bash
# Create resource group
az group create --name ainflue-prod --location westus2

# Create AKS cluster
az aks create \
  --resource-group ainflue-prod \
  --name ainflue-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys
```

#### Google Cloud Setup
```bash
# Create GKE cluster
gcloud container clusters create ainflue-prod \
  --zone us-west1-a \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10
```

### Networking Configuration

**Load Balancer Setup:**
```yaml
# ingress-controller.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ainflue-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
    - hosts:
        - api.ainflue.com
        - app.ainflue.com
      secretName: ainflue-tls
  rules:
    - host: api.ainflue.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ainflue-api
                port:
                  number: 8000
    - host: app.ainflue.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ainflue-frontend
                port:
                  number: 3000
```

---

## Database Configuration

### PostgreSQL Setup

**Managed Service (Recommended):**
```bash
# AWS RDS
aws rds create-db-instance \
  --db-instance-identifier ainflue-prod-db \
  --db-instance-class db.r5.xlarge \
  --engine postgres \
  --engine-version 14.9 \
  --master-username ainflue \
  --master-user-password $SECURE_PASSWORD \
  --allocated-storage 100 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted
```

**Self-Managed Setup:**
```yaml
# postgresql.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
spec:
  serviceName: postgresql
  replicas: 3
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
        - name: postgresql
          image: postgres:14
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: ainflue
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: postgres-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 100Gi
        storageClassName: fast-ssd
```

### Redis Configuration

```yaml
# redis-cluster.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  serviceName: redis-cluster
  replicas: 6
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          command:
            - redis-server
            - /etc/redis/redis.conf
            - --cluster-enabled yes
            - --cluster-config-file nodes.conf
            - --cluster-node-timeout 5000
            - --appendonly yes
          ports:
            - containerPort: 6379
            - containerPort: 16379
          volumeMounts:
            - name: redis-data
              mountPath: /data
            - name: redis-config
              mountPath: /etc/redis
  volumeClaimTemplates:
    - metadata:
        name: redis-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

---

## Backend Deployment

### Container Build

```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Kubernetes Deployment

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainflue-backend
  labels:
    app: ainflue-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ainflue-backend
  template:
    metadata:
      labels:
        app: ainflue-backend
    spec:
      containers:
        - name: ainflue-backend
          image: ainflue/backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-secret
                  key: url
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: ainflue-config
                  key: redis-url
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: app-secret
                  key: secret-key
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
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
            initialDelaySeconds: 10
            periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: ainflue-backend
spec:
  selector:
    app: ainflue-backend
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: ClusterIP
```

---

## Frontend Deployment

### Next.js Build Configuration

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production image
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### Frontend Kubernetes Deployment

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainflue-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ainflue-frontend
  template:
    metadata:
      labels:
        app: ainflue-frontend
    spec:
      containers:
        - name: ainflue-frontend
          image: ainflue/frontend:latest
          ports:
            - containerPort: 3000
          env:
            - name: NEXT_PUBLIC_API_URL
              value: "https://api.ainflue.com"
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: ainflue-frontend
spec:
  selector:
    app: ainflue-frontend
  ports:
    - protocol: TCP
      port: 3000
      targetPort: 3000
```

---

## Kubernetes Deployment

### Complete Deployment Script

```bash
#!/bin/bash
# deploy.sh

set -e

# Configuration
NAMESPACE="ainflue-prod"
DOCKER_REGISTRY="ainflue"
VERSION="${VERSION:-latest}"

echo "🚀 Starting Ainflue deployment..."

# Create namespace
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets
kubectl apply -f secrets/ -n $NAMESPACE

# Apply config maps
kubectl apply -f configmaps/ -n $NAMESPACE

# Deploy databases
echo "📦 Deploying databases..."
kubectl apply -f database/ -n $NAMESPACE

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgresql -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis-cluster -n $NAMESPACE --timeout=300s

# Run database migrations
echo "🔄 Running database migrations..."
kubectl run migrations --image=$DOCKER_REGISTRY/backend:$VERSION \
  --env="DATABASE_URL=$(kubectl get secret database-secret -o jsonpath='{.data.url}' | base64 -d)" \
  --command -- alembic upgrade head \
  -n $NAMESPACE

# Deploy backend
echo "🖥️ Deploying backend..."
envsubst < deployments/backend-deployment.yaml | kubectl apply -f - -n $NAMESPACE

# Wait for backend to be ready
kubectl wait --for=condition=available deployment/ainflue-backend -n $NAMESPACE --timeout=300s

# Deploy frontend
echo "🌐 Deploying frontend..."
envsubst < deployments/frontend-deployment.yaml | kubectl apply -f - -n $NAMESPACE

# Wait for frontend to be ready
kubectl wait --for=condition=available deployment/ainflue-frontend -n $NAMESPACE --timeout=300s

# Deploy monitoring
echo "📊 Deploying monitoring..."
kubectl apply -f monitoring/ -n $NAMESPACE

# Deploy ingress
echo "🌍 Configuring ingress..."
kubectl apply -f ingress/ -n $NAMESPACE

echo "✅ Deployment completed successfully!"
echo "🔗 Frontend: https://app.ainflue.com"
echo "🔗 API: https://api.ainflue.com"
echo "📊 Monitoring: https://monitoring.ainflue.com"
```

---

## Monitoring Setup

### Prometheus Configuration

```yaml
# monitoring/prometheus.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    rule_files:
      - "alert_rules.yml"

    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true

      - job_name: 'ainflue-backend'
        static_configs:
          - targets: ['ainflue-backend:8000']

      - job_name: 'ainflue-frontend'
        static_configs:
          - targets: ['ainflue-frontend:3000']

    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093
```

### Grafana Dashboards

```json
// grafana-dashboard.json
{
  "dashboard": {
    "title": "Ainflue Platform Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~'5..'}[5m]) / rate(http_requests_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      }
    ]
  }
}
```

---

## SSL/TLS Configuration

### Cert-Manager Setup

```yaml
# cert-manager-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@ainflue.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
```

### Certificate Configuration

```yaml
# ssl-certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: ainflue-tls
spec:
  secretName: ainflue-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - ainflue.com
    - www.ainflue.com
    - api.ainflue.com
    - app.ainflue.com
    - monitoring.ainflue.com
```

---

## Environment Variables

### Production Configuration

```yaml
# configmaps/app-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ainflue-config
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  API_VERSION: "v2"
  ALLOWED_HOSTS: "api.ainflue.com,app.ainflue.com"
  CORS_ORIGINS: "https://app.ainflue.com,https://ainflue.com"
  
  # Database settings
  DB_POOL_SIZE: "20"
  DB_MAX_OVERFLOW: "30"
  DB_POOL_TIMEOUT: "30"
  
  # Redis settings
  REDIS_URL: "redis://redis-cluster:6379"
  REDIS_MAX_CONNECTIONS: "100"
  
  # File storage
  STORAGE_BACKEND: "s3"
  AWS_S3_BUCKET: "ainflue-prod-files"
  AWS_S3_REGION: "us-west-2"
  
  # Email settings
  EMAIL_BACKEND: "sendgrid"
  
  # SMS settings
  SMS_BACKEND: "twilio"
  
  # Monitoring
  SENTRY_ENVIRONMENT: "production"
  PROMETHEUS_ENABLED: "true"
```

### Secrets Configuration

```yaml
# secrets/app-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  secret-key: # base64 encoded secret key
  jwt-secret: # base64 encoded JWT secret
  
  # Database
  database-url: # base64 encoded database URL
  
  # External services
  sendgrid-api-key: # base64 encoded SendGrid API key
  twilio-auth-token: # base64 encoded Twilio auth token
  aws-access-key-id: # base64 encoded AWS access key
  aws-secret-access-key: # base64 encoded AWS secret key
  
  # Monitoring
  sentry-dsn: # base64 encoded Sentry DSN
```

---

## Health Checks

### Application Health Endpoints

```python
# health_check.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
import redis
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/ready")
async def readiness_check():
    """Comprehensive readiness check"""
    checks = {}
    
    # Database check
    try:
        async with database.transaction():
            await database.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Redis check
    try:
        redis_client = redis.Redis.from_url(REDIS_URL)
        redis_client.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    # Overall status
    all_healthy = all(status == "healthy" for status in checks.values())
    
    if not all_healthy:
        raise HTTPException(status_code=503, detail=checks)
    
    return {"status": "ready", "checks": checks}
```

### Kubernetes Health Checks

```yaml
# health-check-config.yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

---

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_HOST="postgresql.ainflue-prod.svc.cluster.local"
DB_NAME="ainflue"

# Create backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/ainflue_$TIMESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/ainflue_$TIMESTAMP.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/ainflue_$TIMESTAMP.sql.gz s3://ainflue-backups/database/

# Clean up old local backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ainflue_$TIMESTAMP.sql.gz"
```

### Automated Backup CronJob

```yaml
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:14
              command:
                - /bin/bash
                - -c
                - |
                  pg_dump $DATABASE_URL | gzip | aws s3 cp - s3://ainflue-backups/db-$(date +%Y%m%d_%H%M%S).sql.gz
              env:
                - name: DATABASE_URL
                  valueFrom:
                    secretKeyRef:
                      name: database-secret
                      key: url
          restartPolicy: OnFailure
```

---

## Scaling Configuration

### Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ainflue-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ainflue-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

### Cluster Autoscaler

```yaml
# cluster-autoscaler.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      containers:
        - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0
          name: cluster-autoscaler
          command:
            - ./cluster-autoscaler
            - --v=4
            - --stderrthreshold=info
            - --cloud-provider=aws
            - --skip-nodes-with-local-storage=false
            - --expander=least-waste
            - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/ainflue-prod
          resources:
            limits:
              cpu: 100m
              memory: 300Mi
            requests:
              cpu: 100m
              memory: 300Mi
```

---

## Security Hardening

### Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ainflue-network-policy
spec:
  podSelector:
    matchLabels:
      app: ainflue-backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: ainflue-frontend
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgresql
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis-cluster
      ports:
        - protocol: TCP
          port: 6379
```

### Pod Security Policy

```yaml
# pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: ainflue-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

---

## Troubleshooting

### Common Issues

**Pod Startup Issues:**
```bash
# Check pod status
kubectl get pods -n ainflue-prod

# Check pod logs
kubectl logs -f deployment/ainflue-backend -n ainflue-prod

# Describe pod for events
kubectl describe pod <pod-name> -n ainflue-prod
```

**Database Connection Issues:**
```bash
# Test database connectivity
kubectl run debug --image=postgres:14 --rm -it -- bash
psql $DATABASE_URL

# Check database service
kubectl get svc postgresql -n ainflue-prod
```

**Performance Issues:**
```bash
# Check resource usage
kubectl top pods -n ainflue-prod
kubectl top nodes

# Check HPA status
kubectl get hpa -n ainflue-prod
```

### Debugging Commands

```bash
# Port forward for local debugging
kubectl port-forward svc/ainflue-backend 8000:8000 -n ainflue-prod

# Execute commands in running pods
kubectl exec -it deployment/ainflue-backend -- bash

# Check ingress status
kubectl get ingress -n ainflue-prod

# View logs from multiple pods
kubectl logs -l app=ainflue-backend -n ainflue-prod --tail=100
```

### Recovery Procedures

**Database Recovery:**
```bash
# Restore from backup
kubectl run restore --image=postgres:14 --rm -it -- bash
aws s3 cp s3://ainflue-backups/db-latest.sql.gz /tmp/
gunzip /tmp/db-latest.sql.gz
psql $DATABASE_URL < /tmp/db-latest.sql
```

**Complete Service Recovery:**
```bash
# Delete and recreate deployment
kubectl delete deployment ainflue-backend -n ainflue-prod
kubectl apply -f deployments/backend-deployment.yaml -n ainflue-prod

# Force pull latest images
kubectl patch deployment ainflue-backend -p '{"spec":{"template":{"metadata":{"annotations":{"date":"'$(date +'%s')'"}}}}}' -n ainflue-prod
```

---

## Maintenance

### Regular Maintenance Tasks

**Weekly:**
- Review monitoring dashboards
- Check disk usage and storage
- Verify backup completion
- Update security patches

**Monthly:**
- Update application dependencies
- Review resource usage and scaling
- Test disaster recovery procedures
- Security vulnerability scans

**Quarterly:**
- Major version updates
- Performance optimization review
- Security audit
- Capacity planning review

### Update Procedures

```bash
# Rolling update
kubectl set image deployment/ainflue-backend ainflue-backend=ainflue/backend:v2.1.0 -n ainflue-prod

# Monitor rollout
kubectl rollout status deployment/ainflue-backend -n ainflue-prod

# Rollback if needed
kubectl rollout undo deployment/ainflue-backend -n ainflue-prod
```

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
**Contact**: mlaiel@live.de  
**Support**: For deployment assistance and enterprise support