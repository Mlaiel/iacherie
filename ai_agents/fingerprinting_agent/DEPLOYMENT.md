# 🚀 Fingerprinting Agent - Production Deployment Guide

## 📋 Deployment Overview

**Author**: **Fahed Mlaiel** <mlaiel@live.de>  
**Expert Team**: Lead AI Developer + Senior Backend Engineer + ML Engineer + Database Architect + Security Expert + Microservices Architect + Audio Processing Specialist + DevOps Engineer + AI Prompt Engineer

**⚠️ LEGAL NOTICE**: This deployment guide is proprietary to Fahed Mlaiel. Unauthorized use is strictly prohibited.

---

## 🏗️ Infrastructure Requirements

### Minimum System Requirements

```yaml
# Production Environment Specifications
compute:
  cpu: "16 cores (Intel Xeon or AMD EPYC)"
  memory: "64 GB RAM"
  gpu: "NVIDIA RTX 4090 or A100 (optional but recommended)"
  storage: "2 TB NVMe SSD"

network:
  bandwidth: "10 Gbps"
  latency: "< 1ms to database"

operating_system: "Ubuntu 22.04 LTS or RHEL 9+"
```

### Recommended Production Setup

```yaml
# High-Availability Configuration
load_balancer:
  type: "NGINX or AWS ALB"
  instances: 2
  ssl_termination: true

application_servers:
  instances: 4
  type: "c5.4xlarge (AWS) or equivalent"
  memory: "32 GB per instance"
  cpu: "16 cores per instance"

database:
  primary: "PostgreSQL 15+ on r5.2xlarge"
  replicas: 2
  memory: "64 GB"
  storage: "1 TB SSD with 10k IOPS"

cache:
  redis_cluster: "3 nodes, 16 GB memory each"
  
vector_storage:
  faiss_storage: "High-memory instances"
  backup: "S3 or equivalent"
```

## 🐳 Docker Deployment

### Production Dockerfile

```dockerfile
# Multi-stage production Dockerfile
FROM python:3.11-slim as base

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libavutil-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base as production

# Application code
COPY . .

# Create non-root user
RUN groupadd -r fingerprint && useradd -r -g fingerprint fingerprint
RUN chown -R fingerprint:fingerprint /app
USER fingerprint

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "fingerprinting_agent.main:app"]
```

### Docker Compose Production

```yaml
version: '3.8'

services:
  fingerprinting-agent:
    build:
      context: .
      target: production
    image: fingerprinting-agent:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/fingerprinting
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=INFO
      - WORKERS=4
    depends_on:
      - postgres
      - redis
    volumes:
      - ./models:/app/models:ro
      - ./logs:/app/logs
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '8'
          memory: 16G
        reservations:
          cpus: '4'
          memory: 8G
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: fingerprinting
      POSTGRES_USER: fingerprint_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 4gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    deploy:
      resources:
        limits:
          memory: 4G

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - fingerprinting-agent

volumes:
  postgres_data:
  redis_data:
```

## ☸️ Kubernetes Deployment

### Namespace Configuration

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fingerprinting-system
  labels:
    app: fingerprinting-agent
    owner: fahed-mlaiel
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fingerprinting-config
  namespace: fingerprinting-system
data:
  config.yaml: |
    environment: production
    debug: false
    database:
      host: postgres-service
      port: 5432
      database: fingerprinting
      pool_size: 20
      max_overflow: 40
    redis:
      host: redis-service
      port: 6379
      db: 0
    performance:
      max_workers: 16
      batch_size: 64
      similarity_threshold: 0.85
    monitoring:
      log_level: INFO
      enable_metrics: true
      metrics_port: 9090
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fingerprinting-agent
  namespace: fingerprinting-system
spec:
  replicas: 6
  selector:
    matchLabels:
      app: fingerprinting-agent
  template:
    metadata:
      labels:
        app: fingerprinting-agent
    spec:
      containers:
      - name: fingerprinting-agent
        image: fingerprinting-agent:latest
        ports:
        - containerPort: 8000
        - containerPort: 9090  # Metrics
        env:
        - name: CONFIG_FILE
          value: /config/config.yaml
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        volumeMounts:
        - name: config-volume
          mountPath: /config
        - name: models-volume
          mountPath: /app/models
        resources:
          requests:
            cpu: 4000m
            memory: 8Gi
          limits:
            cpu: 8000m
            memory: 16Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: config-volume
        configMap:
          name: fingerprinting-config
      - name: models-volume
        persistentVolumeClaim:
          claimName: models-pvc
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fingerprinting-service
  namespace: fingerprinting-system
spec:
  selector:
    app: fingerprinting-agent
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer
```

## 🗄️ Database Setup

### PostgreSQL Initialization

```sql
-- Production database initialization script
-- File: init-db.sql

-- Create database and user
CREATE DATABASE fingerprinting;
CREATE USER fingerprint_user WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE fingerprinting TO fingerprint_user;

-- Connect to the fingerprinting database
\c fingerprinting;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Main fingerprints table
CREATE TABLE content_fingerprints (
    fingerprint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID NOT NULL,
    user_id UUID,
    tenant_id UUID,
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('audio', 'video', 'image', 'text', 'composite')),
    fingerprint_type VARCHAR(50) NOT NULL,
    quality_level VARCHAR(20) NOT NULL CHECK (quality_level IN ('basic', 'standard', 'advanced', 'ultra')),
    hash_fingerprint VARCHAR(255) NOT NULL,
    feature_fingerprint BYTEA,
    embedding_fingerprint BYTEA,
    metadata JSONB DEFAULT '{}',
    extraction_params JSONB DEFAULT '{}',
    quality_metrics JSONB DEFAULT '{}',
    file_size BIGINT,
    duration_seconds FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT unique_content_fingerprint UNIQUE (content_id, fingerprint_type)
);

-- Similarity matches table
CREATE TABLE similarity_matches (
    match_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_fingerprint_id UUID NOT NULL REFERENCES content_fingerprints(fingerprint_id),
    matched_fingerprint_id UUID NOT NULL REFERENCES content_fingerprints(fingerprint_id),
    similarity_score FLOAT NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
    similarity_type VARCHAR(50) NOT NULL,
    confidence_level FLOAT NOT NULL CHECK (confidence_level >= 0 AND confidence_level <= 1),
    match_details JSONB DEFAULT '{}',
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT no_self_match CHECK (query_fingerprint_id != matched_fingerprint_id)
);

-- Performance indexes
CREATE INDEX idx_fingerprints_content_type ON content_fingerprints(content_type);
CREATE INDEX idx_fingerprints_user_tenant ON content_fingerprints(user_id, tenant_id);
CREATE INDEX idx_fingerprints_hash ON content_fingerprints USING HASH (hash_fingerprint);
CREATE INDEX idx_fingerprints_created ON content_fingerprints(created_at DESC);
CREATE INDEX idx_fingerprints_quality ON content_fingerprints(quality_level, content_type);
CREATE INDEX idx_fingerprints_expires ON content_fingerprints(expires_at) WHERE expires_at IS NOT NULL;

-- GIN indexes for JSONB
CREATE INDEX idx_fingerprints_metadata_gin ON content_fingerprints USING GIN (metadata);
CREATE INDEX idx_fingerprints_quality_metrics_gin ON content_fingerprints USING GIN (quality_metrics);

-- Similarity matches indexes
CREATE INDEX idx_matches_query_fp ON similarity_matches(query_fingerprint_id);
CREATE INDEX idx_matches_matched_fp ON similarity_matches(matched_fingerprint_id);
CREATE INDEX idx_matches_similarity_score ON similarity_matches(similarity_score DESC);
CREATE INDEX idx_matches_detected_at ON similarity_matches(detected_at DESC);

-- Partitioning by date for large datasets
CREATE TABLE content_fingerprints_y2025m01 PARTITION OF content_fingerprints
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Add more partitions as needed
-- CREATE TABLE content_fingerprints_y2025m02 PARTITION OF content_fingerprints
--     FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Statistics and maintenance
CREATE TABLE processing_statistics (
    stat_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date_recorded DATE DEFAULT CURRENT_DATE,
    content_type VARCHAR(50),
    total_processed INTEGER DEFAULT 0,
    average_processing_time FLOAT DEFAULT 0,
    average_quality_score FLOAT DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_daily_stat UNIQUE (date_recorded, content_type)
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_fingerprints_updated_at 
    BEFORE UPDATE ON content_fingerprints 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO fingerprint_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO fingerprint_user;
```

### Database Migration Scripts

```python
# Alembic migration script
"""Create fingerprinting tables

Revision ID: 001_initial_fingerprinting
Revises: 
Create Date: 2025-01-15 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial_fingerprinting'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Execute the SQL from above
    with open('init-db.sql', 'r') as f:
        op.execute(f.read())

def downgrade():
    op.execute('DROP TABLE IF EXISTS similarity_matches CASCADE;')
    op.execute('DROP TABLE IF EXISTS content_fingerprints CASCADE;')
    op.execute('DROP TABLE IF EXISTS processing_statistics CASCADE;')
```

## 🔧 Configuration Management

### Production Configuration

```yaml
# production.yaml
environment: production
debug: false

# Database configuration
database:
  host: ${DATABASE_HOST}
  port: ${DATABASE_PORT}
  database: ${DATABASE_NAME}
  username: ${DATABASE_USER}
  password: ${DATABASE_PASSWORD}
  pool_size: 20
  max_overflow: 40
  echo_sql: false
  ssl_mode: require
  pool_timeout: 30
  pool_recycle: 3600

# Redis configuration  
redis:
  host: ${REDIS_HOST}
  port: ${REDIS_PORT}
  db: ${REDIS_DB}
  password: ${REDIS_PASSWORD}
  max_connections: 100
  socket_timeout: 5
  socket_connect_timeout: 5

# Security configuration
security:
  encryption_key: ${ENCRYPTION_KEY}
  jwt_secret: ${JWT_SECRET}
  api_key_required: true
  rate_limit_per_minute: 100
  max_request_size: 100MB
  cors_origins: 
    - "https://yourdomain.com"
    - "https://api.yourdomain.com"

# Performance optimization
performance:
  max_workers: 16
  batch_size: 64
  similarity_threshold: 0.85
  quality_threshold: 0.9
  cache_ttl: 3600
  max_concurrent_jobs: 20
  gpu_enabled: true
  mixed_precision: true

# Monitoring configuration
monitoring:
  log_level: INFO
  log_format: json
  log_file: /app/logs/fingerprinting.log
  log_max_size: 100MB
  log_backup_count: 10
  enable_metrics: true
  metrics_port: 9090
  enable_distributed_tracing: true
  jaeger_endpoint: ${JAEGER_ENDPOINT}

# Storage configuration
storage:
  models_path: /app/models
  cache_path: /app/cache
  temp_path: /app/tmp
  max_temp_size: 10GB
  cleanup_interval: 3600

# Feature flags
features:
  deep_learning_enabled: true
  cross_modal_analysis: true
  real_time_monitoring: true
  batch_processing: true
  automatic_quality_assessment: true
```

### Environment Variables

```bash
# .env.production
DATABASE_HOST=postgres.production.internal
DATABASE_PORT=5432
DATABASE_NAME=fingerprinting
DATABASE_USER=fingerprint_user
DATABASE_PASSWORD=super_secure_password_here

REDIS_HOST=redis.production.internal  
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redis_secure_password

ENCRYPTION_KEY=your_32_character_encryption_key_here
JWT_SECRET=your_jwt_secret_key_here

JAEGER_ENDPOINT=http://jaeger:14268/api/traces

# Sentry for error tracking
SENTRY_DSN=https://your_sentry_dsn_here

# AWS/Cloud credentials (if applicable)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-west-2
```

## 📊 Monitoring & Observability

### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fingerprinting-agent'
    static_configs:
      - targets: ['fingerprinting-service:9090']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Fingerprinting Agent Monitoring",
    "panels": [
      {
        "title": "Processing Rate",
        "targets": [
          {
            "expr": "rate(fingerprints_generated_total[5m])",
            "legendFormat": "Fingerprints/sec"
          }
        ]
      },
      {
        "title": "Processing Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, fingerprint_processing_seconds)",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(fingerprints_failed_total[5m]) / rate(fingerprints_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "targets": [
          {
            "expr": "container_memory_usage_bytes{pod=~\"fingerprinting-agent.*\"}",
            "legendFormat": "Memory Usage"
          }
        ]
      }
    ]
  }
}
```

### Alerting Rules

```yaml
# alerts.yml
groups:
- name: fingerprinting-agent-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(fingerprints_failed_total[5m]) / rate(fingerprints_total[5m]) > 0.05
    for: 2m
    annotations:
      summary: "High error rate in fingerprinting agent"
      
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes{pod=~"fingerprinting-agent.*"} / container_spec_memory_limit_bytes > 0.9
    for: 5m
    annotations:
      summary: "High memory usage in fingerprinting agent"
      
  - alert: SlowProcessing
    expr: histogram_quantile(0.95, fingerprint_processing_seconds) > 30
    for: 3m
    annotations:
      summary: "Slow fingerprint processing detected"
```

## 🔐 Security Hardening

### Network Security

```yaml
# Network policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: fingerprinting-network-policy
spec:
  podSelector:
    matchLabels:
      app: fingerprinting-agent
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: api-gateway
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
```

### Secret Management

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: fingerprinting-secrets
  namespace: fingerprinting-system
type: Opaque
data:
  database-password: <base64-encoded-password>
  redis-password: <base64-encoded-password>
  encryption-key: <base64-encoded-key>
  jwt-secret: <base64-encoded-secret>
```

### SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name fingerprinting-api.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://fingerprinting-service:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🚀 Deployment Scripts

### Automated Deployment Script

```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e

# Configuration
NAMESPACE="fingerprinting-system"
IMAGE_TAG=${1:-latest}
ENVIRONMENT=${2:-production}

echo "🚀 Starting deployment of Fingerprinting Agent"
echo "Environment: $ENVIRONMENT"
echo "Image Tag: $IMAGE_TAG"

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply configuration
echo "📝 Applying configuration..."
envsubst < k8s/configmap.yaml | kubectl apply -f -
kubectl apply -f k8s/secrets.yaml

# Deploy database
echo "🗄️ Deploying database..."
kubectl apply -f k8s/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

# Run database migrations
echo "📊 Running database migrations..."
kubectl create job migration-$(date +%s) --from=cronjob/db-migration
kubectl wait --for=condition=complete job -l app=db-migration --timeout=300s

# Deploy application
echo "🏗️ Deploying application..."
sed "s/IMAGE_TAG/$IMAGE_TAG/g" k8s/deployment.yaml | kubectl apply -f -
kubectl apply -f k8s/service.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/fingerprinting-agent --timeout=600s

# Deploy ingress/load balancer
echo "🌐 Setting up load balancer..."
kubectl apply -f k8s/ingress.yaml

# Health check
echo "🏥 Running health checks..."
kubectl get pods -l app=fingerprinting-agent
kubectl get services

# Test deployment
echo "🧪 Testing deployment..."
EXTERNAL_IP=$(kubectl get service fingerprinting-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -f http://$EXTERNAL_IP/health || echo "❌ Health check failed"

echo "✅ Deployment completed successfully!"
echo "External IP: $EXTERNAL_IP"
```

### Rollback Script

```bash
#!/bin/bash
# rollback.sh - Emergency rollback script

set -e

NAMESPACE="fingerprinting-system"
REVISION=${1:-previous}

echo "🔄 Rolling back Fingerprinting Agent deployment"
echo "Revision: $REVISION"

# Rollback deployment
kubectl rollout undo deployment/fingerprinting-agent --to-revision=$REVISION -n $NAMESPACE

# Wait for rollback
kubectl rollout status deployment/fingerprinting-agent -n $NAMESPACE --timeout=300s

# Verify rollback
kubectl get pods -l app=fingerprinting-agent -n $NAMESPACE

echo "✅ Rollback completed successfully!"
```

## 📈 Performance Tuning

### Application Performance

```python
# Performance optimization settings
PERFORMANCE_CONFIG = {
    # CPU optimization
    'max_workers': min(32, (os.cpu_count() or 1) * 2),
    'worker_connections': 1000,
    'thread_pool_size': 20,
    
    # Memory optimization
    'batch_size': 64,
    'max_memory_per_worker': '4GB',
    'cache_size': '2GB',
    
    # GPU optimization (if available)
    'gpu_batch_size': 128,
    'mixed_precision': True,
    'optimize_model': True,
    
    # I/O optimization
    'async_io': True,
    'connection_pool_size': 100,
    'keep_alive_timeout': 30
}
```

### Database Performance

```sql
-- Performance optimization queries
-- Update statistics
ANALYZE content_fingerprints;
ANALYZE similarity_matches;

-- Optimize queries
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM content_fingerprints 
WHERE content_type = 'audio' 
AND created_at > NOW() - INTERVAL '1 day';

-- Monitor slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC;
```

## 🔧 Maintenance Procedures

### Regular Maintenance Tasks

```bash
#!/bin/bash
# maintenance.sh - Regular maintenance script

echo "🔧 Starting maintenance procedures..."

# Database cleanup
echo "🗄️ Database cleanup..."
kubectl exec -i postgres-0 -- psql -U fingerprint_user -d fingerprinting << EOF
-- Clean up expired fingerprints
DELETE FROM content_fingerprints 
WHERE expires_at IS NOT NULL AND expires_at < NOW();

-- Clean up old similarity matches (older than 30 days)
DELETE FROM similarity_matches 
WHERE detected_at < NOW() - INTERVAL '30 days';

-- Update statistics
ANALYZE;

-- Reindex if needed
REINDEX DATABASE fingerprinting;
EOF

# Clear old logs
echo "📄 Log cleanup..."
kubectl exec deployment/fingerprinting-agent -- find /app/logs -name "*.log" -mtime +7 -delete

# Clear temporary files
echo "🗑️ Temp file cleanup..."
kubectl exec deployment/fingerprinting-agent -- find /app/tmp -type f -mtime +1 -delete

# Update FAISS indexes
echo "🔍 FAISS index optimization..."
kubectl exec deployment/fingerprinting-agent -- python -m fingerprinting_agent --optimize-indexes

echo "✅ Maintenance completed!"
```

### Backup Procedures

```bash
#!/bin/bash
# backup.sh - Backup script

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/fingerprinting_$BACKUP_DATE"

echo "💾 Starting backup procedures..."

# Database backup
echo "🗄️ Database backup..."
kubectl exec postgres-0 -- pg_dump -U fingerprint_user fingerprinting | gzip > "$BACKUP_DIR/database.sql.gz"

# FAISS indexes backup
echo "🔍 FAISS indexes backup..."
kubectl cp fingerprinting-agent-0:/app/faiss_indexes "$BACKUP_DIR/faiss_indexes"

# Configuration backup
echo "⚙️ Configuration backup..."
kubectl get configmap fingerprinting-config -o yaml > "$BACKUP_DIR/configmap.yaml"

# Upload to cloud storage (AWS S3 example)
aws s3 sync "$BACKUP_DIR" "s3://your-backup-bucket/fingerprinting/$BACKUP_DATE"

echo "✅ Backup completed: $BACKUP_DIR"
```

---

**⚠️ REMINDER**: This deployment guide is proprietary technology owned by Fahed Mlaiel. All usage requires explicit written authorization. Contact: mlaiel@live.de

*© 2025 Fahed Mlaiel. All rights reserved.*
