# Kubernetes Deployment Guide for Ainflue Platform

## Overview
This guide covers the complete Kubernetes deployment of the Ainflue AI-powered content protection and monetization platform.

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Platform Version:** 1.0.0  
**Kubernetes Version:** 1.28+  

## Prerequisites

### Required Tools
- Kubernetes cluster (1.28+)
- kubectl CLI configured
- Helm 3.x
- Docker registry access
- SSL certificates

### Cluster Requirements
- **Minimum Nodes:** 3 (for high availability)
- **CPU:** 8 cores per node
- **Memory:** 16GB per node
- **Storage:** 500GB per node (SSD recommended)
- **Network:** Load balancer support

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Ainflue Platform                     │
├─────────────────────────────────────────────────────────┤
│  Ingress Controller (nginx)                             │
├─────────────────────────────────────────────────────────┤
│  API Gateway Service                                    │
├─────────────────┬─────────────────┬─────────────────────┤
│  Monetization   │   Analytics     │    AI Engine       │
│  Service        │   Service       │    Service          │
├─────────────────┼─────────────────┼─────────────────────┤
│  Crawler        │   Protection    │    Collaboration    │
│  Service        │   Service       │    Service          │
├─────────────────┴─────────────────┴─────────────────────┤
│  Data Layer                                             │
│  ┌─────────────┬─────────────┬─────────────────────────┐│
│  │ PostgreSQL  │  MongoDB    │  Redis Cluster          ││
│  └─────────────┴─────────────┴─────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

## Namespace Setup

### Create Ainflue Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ainflue
  labels:
    name: ainflue
    environment: production
    owner: fahed-mlaiel
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ainflue-quota
  namespace: ainflue
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    persistentvolumeclaims: "20"
    services.loadbalancers: "3"
```

Apply namespace:
```bash
kubectl apply -f namespace.yaml
```

## Secrets Management

### Create Application Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ainflue-secrets
  namespace: ainflue
type: Opaque
stringData:
  # Database Credentials
  POSTGRES_PASSWORD: "your_postgres_password"
  MONGODB_PASSWORD: "your_mongodb_password"
  REDIS_PASSWORD: "your_redis_password"
  
  # JWT Configuration
  JWT_SECRET_KEY: "your_jwt_secret_key_256_bits"
  ENCRYPTION_KEY: "your_encryption_key_256_bits"
  PASSWORD_SALT: "your_password_salt"
  
  # Payment Providers
  STRIPE_SECRET_KEY: "sk_live_your_stripe_secret"
  STRIPE_WEBHOOK_SECRET: "whsec_your_webhook_secret"
  PAYPAL_CLIENT_SECRET: "your_paypal_client_secret"
  WISE_API_KEY: "your_wise_api_key"
  
  # Platform APIs
  YOUTUBE_API_KEY: "your_youtube_api_key"
  SPOTIFY_CLIENT_SECRET: "your_spotify_client_secret"
  INSTAGRAM_CLIENT_SECRET: "your_instagram_client_secret"
  
  # AI/ML Services
  OPENAI_API_KEY: "your_openai_api_key"
  HUGGINGFACE_TOKEN: "your_huggingface_token"
  
  # Storage
  AWS_SECRET_ACCESS_KEY: "your_aws_secret_key"
  
  # Monitoring
  SENTRY_DSN: "your_sentry_dsn"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: ainflue-config
  namespace: ainflue
data:
  # Application Configuration
  ENVIRONMENT: "production"
  DEBUG: "false"
  APP_NAME: "Ainflue"
  APP_VERSION: "1.0.0"
  
  # Server Configuration
  HOST: "0.0.0.0"
  PORT: "8000"
  
  # Database Hosts
  POSTGRES_HOST: "ainflue-postgresql"
  POSTGRES_PORT: "5432"
  POSTGRES_USER: "ainflue"
  POSTGRES_DB: "ainflue_platform"
  
  MONGODB_HOST: "ainflue-mongodb"
  MONGODB_PORT: "27017"
  MONGODB_USER: "ainflue"
  MONGODB_DB: "ainflue_documents"
  
  REDIS_HOST: "ainflue-redis"
  REDIS_PORT: "6379"
  REDIS_DB: "0"
  
  # API Configuration
  API_PREFIX: "/api/v1"
  CORS_ORIGINS: "*"
  
  # Storage Configuration
  AWS_REGION: "eu-central-1"
  AWS_S3_BUCKET: "ainflue-content-prod"
  
  # Monitoring
  PROMETHEUS_ENABLED: "true"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
```

Apply secrets:
```bash
kubectl apply -f secrets.yaml
```

## Database Deployments

### PostgreSQL Deployment

```yaml
# postgresql-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ainflue-postgresql
  namespace: ainflue
spec:
  serviceName: ainflue-postgresql
  replicas: 3
  selector:
    matchLabels:
      app: ainflue-postgresql
  template:
    metadata:
      labels:
        app: ainflue-postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: ainflue-config
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            configMapKeyRef:
              name: ainflue-config
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ainflue-secrets
              key: POSTGRES_PASSWORD
        - name: POSTGRES_INITDB_ARGS
          value: "--auth-host=scram-sha-256"
        volumeMounts:
        - name: postgresql-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - ainflue
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - ainflue
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgresql-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi
---
apiVersion: v1
kind: Service
metadata:
  name: ainflue-postgresql
  namespace: ainflue
spec:
  selector:
    app: ainflue-postgresql
  ports:
  - port: 5432
    targetPort: 5432
  clusterIP: None
```

### MongoDB Deployment

```yaml
# mongodb-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ainflue-mongodb
  namespace: ainflue
spec:
  serviceName: ainflue-mongodb
  replicas: 3
  selector:
    matchLabels:
      app: ainflue-mongodb
  template:
    metadata:
      labels:
        app: ainflue-mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            configMapKeyRef:
              name: ainflue-config
              key: MONGODB_USER
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ainflue-secrets
              key: MONGODB_PASSWORD
        volumeMounts:
        - name: mongodb-storage
          mountPath: /data/db
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - mongosh
            - --eval
            - "db.adminCommand('ping')"
          initialDelaySeconds: 30
          periodSeconds: 10
  volumeClaimTemplates:
  - metadata:
      name: mongodb-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: ainflue-mongodb
  namespace: ainflue
spec:
  selector:
    app: ainflue-mongodb
  ports:
  - port: 27017
    targetPort: 27017
  clusterIP: None
```

### Redis Cluster Deployment

```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ainflue-redis
  namespace: ainflue
spec:
  serviceName: ainflue-redis
  replicas: 6
  selector:
    matchLabels:
      app: ainflue-redis
  template:
    metadata:
      labels:
        app: ainflue-redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        - containerPort: 16379
        command:
        - redis-server
        - /etc/redis/redis.conf
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ainflue-secrets
              key: REDIS_PASSWORD
        volumeMounts:
        - name: redis-config
          mountPath: /etc/redis
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
  volumeClaimTemplates:
  - metadata:
      name: redis-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: ainflue-redis
  namespace: ainflue
spec:
  selector:
    app: ainflue-redis
  ports:
  - name: redis
    port: 6379
    targetPort: 6379
  - name: cluster
    port: 16379
    targetPort: 16379
```

## Application Services

### Main API Service

```yaml
# api-deployment.yaml
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
        image: ainflue/platform:1.0.0
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: ainflue-config
        - secretRef:
            name: ainflue-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
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
        volumeMounts:
        - name: storage
          mountPath: /app/storage
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: ainflue-api-storage
---
apiVersion: v1
kind: Service
metadata:
  name: ainflue-api
  namespace: ainflue
spec:
  selector:
    app: ainflue-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ainflue-api-storage
  namespace: ainflue
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: "fast-ssd"
  resources:
    requests:
      storage: 50Gi
```

### Crawler Service

```yaml
# crawler-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainflue-crawler
  namespace: ainflue
spec:
  replicas: 5
  selector:
    matchLabels:
      app: ainflue-crawler
  template:
    metadata:
      labels:
        app: ainflue-crawler
    spec:
      containers:
      - name: crawler
        image: ainflue/crawler:1.0.0
        envFrom:
        - configMapRef:
            name: ainflue-config
        - secretRef:
            name: ainflue-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        env:
        - name: SERVICE_TYPE
          value: "crawler"
---
apiVersion: v1
kind: Service
metadata:
  name: ainflue-crawler
  namespace: ainflue
spec:
  selector:
    app: ainflue-crawler
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

## Ingress Configuration

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ainflue-ingress
  namespace: ainflue
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.ainflue.com
    - www.ainflue.com
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
              number: 80
  - host: www.ainflue.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ainflue-api
            port:
              number: 80
```

## Monitoring Stack

### Prometheus Configuration

```yaml
# prometheus.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: ainflue
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
        - name: prometheus-storage
          mountPath: /prometheus
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-storage
        persistentVolumeClaim:
          claimName: prometheus-storage
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: ainflue
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
```

## Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ainflue-api-hpa
  namespace: ainflue
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ainflue-api
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

## Deployment Script

```bash
#!/bin/bash
# deploy-ainflue.sh

set -e

echo "🚀 Starting Ainflue Platform Deployment"

# Check prerequisites
echo "📋 Checking prerequisites..."
kubectl version --client || { echo "kubectl not found"; exit 1; }
helm version || { echo "helm not found"; exit 1; }

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f namespace.yaml

# Deploy secrets and config
echo "🔐 Deploying secrets and configuration..."
kubectl apply -f secrets.yaml

# Deploy databases
echo "🗄️ Deploying databases..."
kubectl apply -f postgresql-deployment.yaml
kubectl apply -f mongodb-deployment.yaml
kubectl apply -f redis-deployment.yaml

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
kubectl wait --for=condition=Ready pod -l app=ainflue-postgresql -n ainflue --timeout=300s
kubectl wait --for=condition=Ready pod -l app=ainflue-mongodb -n ainflue --timeout=300s
kubectl wait --for=condition=Ready pod -l app=ainflue-redis -n ainflue --timeout=300s

# Deploy application services
echo "🚀 Deploying application services..."
kubectl apply -f api-deployment.yaml
kubectl apply -f crawler-deployment.yaml

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
kubectl wait --for=condition=Available deployment/ainflue-api -n ainflue --timeout=300s
kubectl wait --for=condition=Available deployment/ainflue-crawler -n ainflue --timeout=300s

# Deploy ingress
echo "🌐 Deploying ingress..."
kubectl apply -f ingress.yaml

# Deploy monitoring
echo "📊 Deploying monitoring..."
kubectl apply -f prometheus.yaml

# Deploy autoscaling
echo "⚖️ Deploying autoscaling..."
kubectl apply -f hpa.yaml

echo "✅ Ainflue Platform deployed successfully!"
echo "🔗 Access the platform at: https://api.ainflue.com"
echo "📊 Monitoring at: https://monitoring.ainflue.com"
```

## Maintenance Commands

### Scale Services
```bash
# Scale API service
kubectl scale deployment ainflue-api --replicas=10 -n ainflue

# Scale crawler service
kubectl scale deployment ainflue-crawler --replicas=20 -n ainflue
```

### Rolling Updates
```bash
# Update API service
kubectl set image deployment/ainflue-api api=ainflue/platform:1.1.0 -n ainflue

# Check rollout status
kubectl rollout status deployment/ainflue-api -n ainflue
```

### Backup Database
```bash
# PostgreSQL backup
kubectl exec -it ainflue-postgresql-0 -n ainflue -- pg_dump -U ainflue ainflue_platform > backup.sql

# MongoDB backup
kubectl exec -it ainflue-mongodb-0 -n ainflue -- mongodump --db ainflue_documents
```

### Health Checks
```bash
# Check all pods
kubectl get pods -n ainflue

# Check service endpoints
kubectl get endpoints -n ainflue

# View logs
kubectl logs -f deployment/ainflue-api -n ainflue
```

## Troubleshooting

### Common Issues

1. **Pod Not Starting**
   ```bash
   kubectl describe pod <pod-name> -n ainflue
   kubectl logs <pod-name> -n ainflue
   ```

2. **Database Connection Issues**
   ```bash
   kubectl exec -it <pod-name> -n ainflue -- env | grep DB
   kubectl get svc -n ainflue
   ```

3. **High Memory Usage**
   ```bash
   kubectl top pods -n ainflue
   kubectl describe hpa -n ainflue
   ```

4. **SSL Certificate Issues**
   ```bash
   kubectl describe certificate ainflue-tls -n ainflue
   kubectl get certificaterequest -n ainflue
   ```

## Security Considerations

1. **Network Policies**: Implement network policies to restrict pod-to-pod communication
2. **RBAC**: Configure Role-Based Access Control for service accounts
3. **Pod Security**: Use Pod Security Standards for enhanced security
4. **Secret Rotation**: Regularly rotate secrets and API keys
5. **Image Security**: Scan container images for vulnerabilities

---

**Copyright © 2025 Fahed Mlaiel. All rights reserved.**

For deployment support: mlaiel@live.de