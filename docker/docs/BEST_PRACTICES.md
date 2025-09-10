# Docker Best Practices

## Enterprise Docker Best Practices for Ainflue Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### Image Best Practices

#### 1. Dockerfile Optimization
```dockerfile
# Use specific version tags, not 'latest'
FROM python:3.11.6-slim AS base

# Set environment variables early
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code last
COPY . .

# Use non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Use specific ENTRYPOINT and CMD
ENTRYPOINT ["python"]
CMD ["main.py"]
```

#### 2. Multi-Stage Builds
```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim AS runtime
COPY --from=builder /root/.local /root/.local
COPY . .

# Security: run as non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

ENV PATH=/root/.local/bin:$PATH
CMD ["python", "main.py"]
```

### Container Security Best Practices

#### 1. Security Configuration
```yaml
# Secure service configuration
version: '3.8'
services:
  api:
    image: ainflue/api:latest
    security_opt:
      - no-new-privileges:true
      - apparmor:docker-default
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
    user: "10001:10001"
```

#### 2. Secret Management
```yaml
# Proper secret handling
version: '3.8'
services:
  api:
    secrets:
      - db_password
      - jwt_secret
    environment:
      - DATABASE_URL=postgresql://user:@db:5432/ainflue
    configs:
      - source: app_config
        target: /app/config.yml

secrets:
  db_password:
    external: true
  jwt_secret:
    external: true

configs:
  app_config:
    file: ./config.yml
```

### Resource Management

#### 1. Resource Limits and Reservations
```yaml
services:
  audio-processor:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
          pids: 1000
        reservations:
          cpus: '1.0'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
```

#### 2. Health Checks
```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Network Best Practices

#### 1. Network Segmentation
```yaml
# Proper network isolation
networks:
  frontend:
    driver: overlay
    attachable: true
  backend:
    driver: overlay
    internal: true
  database:
    driver: overlay
    internal: true

services:
  web:
    networks:
      - frontend
      - backend
  api:
    networks:
      - backend
      - database
  db:
    networks:
      - database
```

#### 2. Service Discovery
```yaml
# Use service names for internal communication
services:
  api:
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
      - REDIS_URL=redis://redis:6379/0
      - AUDIO_SERVICE_URL=http://audio-processor:8001
```

### Storage Best Practices

#### 1. Volume Management
```yaml
# Proper volume configuration
volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  audio-files:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nfs-server.local,rw
      device: ":/path/to/audio"

services:
  postgres:
    volumes:
      - postgres-data:/var/lib/postgresql/data
    tmpfs:
      - /run/postgresql:noexec,nosuid,size=100m
```

#### 2. Backup Integration
```yaml
# Automated backup service
services:
  backup:
    image: ainflue/backup:latest
    volumes:
      - postgres-data:/data/postgres:ro
      - redis-data:/data/redis:ro
      - /backup:/backup
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    deploy:
      restart_policy:
        condition: on-failure
```

### Monitoring and Logging

#### 1. Structured Logging
```python
# Structured logging example
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'service': 'audio-processor',
            'version': '1.0.0'
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
logging.getLogger().handlers[0].setFormatter(JSONFormatter())
```

#### 2. Metrics Exposure
```python
# Prometheus metrics best practices
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Use descriptive metric names
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections_current',
    'Current number of active connections'
)

# Instrument your code
@REQUEST_DURATION.time()
def process_request(method, endpoint):
    # Process request
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status_code=200
    ).inc()
```

### Development Workflow

#### 1. Development Environment
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  api:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules  # Anonymous volume for node_modules
    environment:
      - NODE_ENV=development
      - DEBUG=*
    ports:
      - "8000:8000"
    command: npm run dev
```

#### 2. Testing Configuration
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  api-test:
    build:
      context: .
      target: test
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgresql://test:test@postgres-test:5432/test
    depends_on:
      - postgres-test
    command: npm test

  postgres-test:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    tmpfs:
      - /var/lib/postgresql/data
```

### CI/CD Best Practices

#### 1. Build Pipeline
```yaml
# .github/workflows/docker.yml
name: Docker Build and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Container Registry
        uses: docker/login-action@v2
        with:
          registry: registry.ainflue.com
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
          
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            registry.ainflue.com/api:${{ github.sha }}
            registry.ainflue.com/api:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

#### 2. Security Scanning
```yaml
# Security scanning in CI/CD
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'registry.ainflue.com/api:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

### Performance Optimization

#### 1. Application Performance
```python
# Connection pooling example
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

# Optimized database connection
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Disable SQL logging in production
)

# Async connection handling
import asyncpg
import asyncio

async def get_connection_pool():
    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=10,
        max_size=50,
        command_timeout=60
    )
```

#### 2. Caching Strategy
```python
# Multi-layer caching
import redis
from functools import wraps
import json
import hashlib

redis_client = redis.Redis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

def cache_result(ttl=3600, prefix="cache"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{prefix}:{func.__name__}:{hashlib.md5(str(args).encode()).hexdigest()}"
            
            # Try to get from cache
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
            except Exception as e:
                print(f"Cache get error: {e}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                redis_client.setex(cache_key, ttl, json.dumps(result))
            except Exception as e:
                print(f"Cache set error: {e}")
            
            return result
        return wrapper
    return decorator
```

### Deployment Strategies

#### 1. Blue-Green Deployment
```yaml
# Blue-Green deployment strategy
version: '3.8'
services:
  app-blue:
    image: ainflue/api:blue
    deploy:
      replicas: 3
      labels:
        - "traefik.enable=true"
        - "traefik.http.services.app.loadbalancer.server.port=8000"
        - "traefik.http.routers.app-blue.rule=Host(`api.ainflue.com`) && Headers(`X-Version`, `blue`)"
        
  app-green:
    image: ainflue/api:green
    deploy:
      replicas: 0  # Standby
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.app-green.rule=Host(`api.ainflue.com`) && Headers(`X-Version`, `green`)"
```

#### 2. Rolling Updates
```yaml
# Rolling update configuration
services:
  api:
    deploy:
      replicas: 6
      update_config:
        parallelism: 2
        delay: 30s
        failure_action: rollback
        monitor: 60s
        max_failure_ratio: 0.3
      rollback_config:
        parallelism: 2
        delay: 0s
        monitor: 60s
        failure_action: pause
        max_failure_ratio: 0.3
```

### Documentation Standards

#### 1. Service Documentation
```yaml
# Well-documented service
version: '3.8'
services:
  audio-processor:
    image: ainflue/audio-processor:1.2.0
    # Purpose: Process audio files with AI enhancement
    # Dependencies: Redis for caching, PostgreSQL for metadata
    # Port 8001: HTTP API
    # Port 8002: gRPC API
    # Health: GET /health returns 200 when healthy
    # Metrics: GET /metrics for Prometheus
    environment:
      - LOG_LEVEL=INFO
      - REDIS_URL=redis://redis:6379/1
      - DATABASE_URL=postgresql://user:pass@postgres:5432/audio
    networks:
      - audio-network
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

### Maintenance and Operations

#### 1. Regular Maintenance Tasks
```bash
#!/bin/bash
# docker-maintenance.sh

echo "Starting Docker maintenance..."

# Clean up unused resources
docker system prune -f

# Update base images
docker images --format "table {{.Repository}}\t{{.Tag}}" | grep -v "<none>" | while read repo tag; do
    if [[ $tag != "latest" ]]; then
        docker pull $repo:$tag
    fi
done

# Check for security updates
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image --severity HIGH,CRITICAL $(docker images --format "{{.Repository}}:{{.Tag}}")

echo "Maintenance completed"
```

### Best Practices Summary

1. **Security First**: Always run containers as non-root users
2. **Resource Limits**: Set appropriate CPU and memory limits
3. **Health Checks**: Implement comprehensive health checks
4. **Logging**: Use structured logging for better observability
5. **Monitoring**: Expose metrics for all services
6. **Secrets**: Never store secrets in images or environment variables
7. **Networking**: Use proper network segmentation
8. **Updates**: Keep base images and dependencies updated
9. **Testing**: Test in environments that mirror production
10. **Documentation**: Document all services and their dependencies