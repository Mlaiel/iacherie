# 🚀 Core Module Deployment Guide

## Enterprise Production Deployment

### 🎯 Deployment Overview

This guide provides comprehensive instructions for deploying the Backend Core Module in production environments, ensuring scalability, security, and high availability.

---

## 📋 Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **Python:** 3.11+
- **Memory:** Minimum 8GB RAM (16GB+ recommended)
- **Storage:** 100GB+ SSD storage
- **Network:** High-speed internet connection

### Dependencies
```bash
# Core dependencies
postgresql >= 14.0
redis >= 6.2
nginx >= 1.20
docker >= 20.10
kubernetes >= 1.24 (for k8s deployment)
```

---

## 🐳 Docker Deployment

### Single Container Deployment

#### 1. Build Core Container
```bash
# Navigate to project root
cd /workspaces/Ainflue

# Build optimized production image
docker build -f docker/Dockerfile.core -t ainflue-core:latest .

# Verify build
docker images | grep ainflue-core
```

#### 2. Run Core Container
```bash
# Run with environment configuration
docker run -d \
  --name ainflue-core \
  --restart=always \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/ainflue" \
  -e REDIS_URL="redis://redis:6379/0" \
  -e SECRET_KEY="your-production-secret-key" \
  -e ENVIRONMENT="production" \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  ainflue-core:latest
```

### Docker Compose Deployment

#### 1. Create Production Compose File
```yaml
# docker-compose.core.yml
version: '3.8'

services:
  ainflue-core:
    build:
      context: .
      dockerfile: docker/Dockerfile.core
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/ainflue
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: always

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=ainflue
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:6.2-alpine
    volumes:
      - redis_data:/data
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/core.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ainflue-core
    restart: always

volumes:
  postgres_data:
  redis_data:
```

#### 2. Deploy with Compose
```bash
# Set environment variables
export DB_PASSWORD="secure-db-password"
export SECRET_KEY="super-secure-secret-key"

# Deploy stack
docker-compose -f docker-compose.core.yml up -d

# Verify deployment
docker-compose -f docker-compose.core.yml ps
```

---

## ☸️ Kubernetes Deployment

### 1. Create Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ainflue-core
```

### 2. ConfigMap and Secrets
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: core-config
  namespace: ainflue-core
data:
  DATABASE_HOST: "postgres-service"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "ainflue"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  ENVIRONMENT: "production"

---
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: core-secrets
  namespace: ainflue-core
type: Opaque
data:
  DATABASE_PASSWORD: <base64-encoded-password>
  SECRET_KEY: <base64-encoded-secret>
```

### 3. Core Application Deployment
```yaml
# k8s/core-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainflue-core
  namespace: ainflue-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ainflue-core
  template:
    metadata:
      labels:
        app: ainflue-core
    spec:
      containers:
      - name: core
        image: ainflue-core:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: core-config
        - secretRef:
            name: core-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
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

---
# k8s/core-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: core-service
  namespace: ainflue-core
spec:
  selector:
    app: ainflue-core
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### 4. Database and Redis
```yaml
# k8s/postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: ainflue-core
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        env:
        - name: POSTGRES_DB
          value: "ainflue"
        - name: POSTGRES_USER
          value: "postgres"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: core-secrets
              key: DATABASE_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
# k8s/postgres-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: ainflue-core
spec:
  selector:
    app: postgres
  ports:
  - protocol: TCP
    port: 5432
    targetPort: 5432
```

### 5. Deploy to Kubernetes
```bash
# Apply all configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/core-deployment.yaml

# Verify deployment
kubectl get pods -n ainflue-core
kubectl get services -n ainflue-core

# Check logs
kubectl logs -f deployment/ainflue-core -n ainflue-core
```

---

## 🔧 Environment Configuration

### Production Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/ainflue
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# Security Configuration
SECRET_KEY=your-super-secure-secret-key-here
JWT_SECRET=your-jwt-secret-key
ENCRYPTION_KEY=your-32-byte-encryption-key

# Performance Configuration
WORKER_PROCESSES=4
WORKER_THREADS=8
MAX_REQUESTS_PER_WORKER=1000

# Monitoring Configuration
PROMETHEUS_ENABLED=true
METRICS_PORT=9090
LOG_LEVEL=INFO

# Feature Flags
AI_PROCESSING_ENABLED=true
ANALYTICS_ENABLED=true
SECURITY_ENHANCED=true
```

### Configuration File (`config/production.py`)
```python
import os
from typing import Optional

class ProductionConfig:
    """Production environment configuration"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL")
    REDIS_POOL_SIZE: int = int(os.getenv("REDIS_POOL_SIZE", "10"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    
    # Performance
    WORKER_PROCESSES: int = int(os.getenv("WORKER_PROCESSES", "4"))
    WORKER_THREADS: int = int(os.getenv("WORKER_THREADS", "8"))
    
    # Features
    AI_PROCESSING_ENABLED: bool = os.getenv("AI_PROCESSING_ENABLED", "true").lower() == "true"
    ANALYTICS_ENABLED: bool = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"
```

---

## 🔒 Security Configuration

### SSL/TLS Setup
```nginx
# nginx/core.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://ainflue-core:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Database Security
```sql
-- Create dedicated database user
CREATE USER ainflue_app WITH PASSWORD 'secure-password';

-- Grant minimal required permissions
GRANT CONNECT ON DATABASE ainflue TO ainflue_app;
GRANT USAGE ON SCHEMA public TO ainflue_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ainflue_app;

-- Enable row-level security
ALTER TABLE sensitive_table ENABLE ROW LEVEL SECURITY;
```

---

## 📊 Monitoring and Logging

### Prometheus Metrics
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Core metrics
request_count = Counter('core_requests_total', 'Total requests')
request_duration = Histogram('core_request_duration_seconds', 'Request duration')
active_connections = Gauge('core_active_connections', 'Active connections')
```

### Logging Configuration
```python
# logging_config.py
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/core.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        }
    },
    'loggers': {
        'backend.core': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

---

## 🔄 Database Migrations

### Production Migration Strategy
```bash
# 1. Backup database
pg_dump -h localhost -U postgres ainflue > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migrations
python -m backend.core.database_migrations_suite --environment=production

# 3. Verify migration
python -c "
from backend.core import DatabaseSchemaManager
manager = DatabaseSchemaManager()
status = manager.get_migration_status()
print(f'Migration status: {status}')
"
```

### Migration Rollback Plan
```bash
# Emergency rollback procedure
python -m backend.core.database_migrations_suite --rollback --target=previous

# Verify rollback
python -c "
from backend.core import DatabaseSchemaManager
manager = DatabaseSchemaManager()
integrity = manager.validate_schema_integrity()
print(f'Schema integrity: {integrity}')
"
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database connectivity
pg_isready -h localhost -p 5432

# Verify credentials
psql -h localhost -U postgres -d ainflue -c "SELECT version();"
```

#### 2. Memory Issues
```bash
# Check memory usage
docker stats ainflue-core

# Adjust memory limits in deployment
# Update resources.limits.memory in k8s deployment
```

#### 3. Performance Issues
```bash
# Check application metrics
curl http://localhost:9090/metrics

# Analyze slow queries
docker exec -it postgres psql -d ainflue -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

### Health Checks
```python
# health_check.py
async def health_check():
    """Comprehensive health check"""
    checks = {
        'database': await check_database_connection(),
        'redis': await check_redis_connection(),
        'migrations': await check_migration_status(),
        'services': await check_service_status()
    }
    return checks
```

---

## 📈 Scaling Considerations

### Horizontal Scaling
```yaml
# HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: core-hpa
  namespace: ainflue-core
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ainflue-core
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
```

### Database Scaling
```python
# Database sharding configuration
SHARD_CONFIG = {
    'shards': [
        {'name': 'shard_1', 'url': 'postgresql://user:pass@db1:5432/ainflue_1'},
        {'name': 'shard_2', 'url': 'postgresql://user:pass@db2:5432/ainflue_2'},
        {'name': 'shard_3', 'url': 'postgresql://user:pass@db3:5432/ainflue_3'}
    ],
    'shard_key': 'user_id',
    'shard_function': 'hash'
}
```

---

**© 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform**  
**Production Deployment Guide - Enterprise Edition**
