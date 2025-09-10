# Docker Scaling Strategies

## Auto-Scaling and Performance Optimization for Ainflue Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### Scaling Overview

The Ainflue platform implements intelligent auto-scaling across 80+ containerized services to handle varying workloads efficiently.

### Horizontal Scaling Strategies

#### 1. Service-Based Scaling
```yaml
# docker-compose.yml
services:
  audio-processor:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      placement:
        max_replicas_per_node: 1
```

#### 2. Load-Based Auto-Scaling
```yaml
# Scaling based on CPU usage
version: '3.8'
services:
  monetization-api:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Vertical Scaling Configuration

#### Resource Optimization
```yaml
services:
  ai-inference:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'  
          memory: 4G
```

### Auto-Scaling Triggers

#### 1. CPU-Based Scaling
```bash
# Scale up when CPU > 70%
docker service update --replicas 5 audio_processor
```

#### 2. Memory-Based Scaling
```bash
# Monitor memory usage
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

#### 3. Custom Metrics Scaling
```python
# Auto-scaling script
import docker

client = docker.from_env()

def scale_service(service_name, target_replicas):
    service = client.services.get(service_name)
    service.update(mode={'Replicated': {'Replicas': target_replicas}})
    
def monitor_and_scale():
    # Monitor custom metrics (queue length, response time)
    queue_length = get_queue_length()
    if queue_length > 100:
        scale_service('audio_processor', 5)
    elif queue_length < 20:
        scale_service('audio_processor', 2)
```

### Load Balancing Strategies

#### 1. Round Robin (Default)
```yaml
services:
  api-gateway:
    ports:
      - "80:80"
    deploy:
      replicas: 3
```

#### 2. Least Connections
```nginx
# nginx.conf
upstream backend {
    least_conn;
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}
```

#### 3. Weighted Load Balancing
```nginx
upstream backend {
    server api-1:8000 weight=3;
    server api-2:8000 weight=2;
    server api-3:8000 weight=1;
}
```

### Database Scaling

#### Read Replicas
```yaml
services:
  postgres-master:
    image: postgres:15
    environment:
      POSTGRES_DB: ainflue
      
  postgres-replica:
    image: postgres:15
    environment:
      PGUSER: replicator
    command: |
      pg_basebackup -h postgres-master -D /var/lib/postgresql/data -U replicator -v -P -W
```

#### Connection Pooling
```yaml
services:
  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    environment:
      DATABASES_HOST: postgres-master
      DATABASES_PORT: 5432
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 1000
```

### Caching Strategies

#### Redis Cluster
```yaml
services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    
  redis-replica:
    image: redis:7-alpine
    command: redis-server --slaveof redis-master 6379
```

#### Application-Level Caching
```python
# Cache decorator for expensive operations
from functools import wraps
import redis

redis_client = redis.Redis(host='redis-cluster')

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Container Optimization

#### Multi-Stage Builds
```dockerfile
# Optimize image size
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
```

#### Resource Limits
```yaml
services:
  service-name:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
          pids: 100
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Network Optimization

#### Service Mesh
```yaml
# Istio service mesh for advanced traffic management
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: audio-processor
spec:
  http:
  - match:
    - headers:
        user-type:
          exact: premium
    route:
    - destination:
        host: audio-processor
        subset: high-performance
      weight: 100
```

#### Network Policies
```yaml
# Restrict network access
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: audio-policy
spec:
  podSelector:
    matchLabels:
      app: audio-processor
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
```

### Monitoring and Alerting

#### Auto-Scaling Metrics
```yaml
# Prometheus rules
groups:
- name: scaling.rules
  rules:
  - alert: HighCPUUsage
    expr: avg(cpu_usage_percent) > 80
    for: 5m
    annotations:
      summary: "High CPU usage detected"
      
  - alert: HighMemoryUsage
    expr: avg(memory_usage_percent) > 85
    for: 5m
    annotations:
      summary: "High memory usage detected"
```

#### Grafana Dashboards
```json
{
  "dashboard": {
    "title": "Auto-Scaling Dashboard",
    "panels": [
      {
        "title": "Service Replicas",
        "type": "graph",
        "targets": [
          {
            "expr": "docker_service_replicas"
          }
        ]
      }
    ]
  }
}
```

### Performance Testing

#### Load Testing
```bash
# Apache Bench
ab -n 10000 -c 100 http://api.ainflue.com/

# Artillery.js
artillery quick --count 100 --num 10 http://api.ainflue.com/
```

#### Stress Testing
```bash
# Docker resource stress test
docker run --rm -it --cpus=2 --memory=4g stress-ng --cpu 2 --timeout 60s
```

### Cost Optimization

#### Resource Right-Sizing
```python
# Automatic resource optimization
def optimize_resources():
    for service in get_services():
        metrics = get_service_metrics(service)
        if metrics['cpu_avg'] < 30:
            reduce_cpu_allocation(service, 0.5)
        if metrics['memory_avg'] < 50:
            reduce_memory_allocation(service, 0.5)
```

#### Spot Instance Integration
```yaml
# Use spot instances for non-critical workloads
services:
  batch-processor:
    deploy:
      placement:
        constraints:
          - node.labels.instance-type==spot
```

### Best Practices

1. **Monitor First**: Implement comprehensive monitoring before scaling
2. **Gradual Scaling**: Scale gradually to avoid resource contention
3. **Test Scaling**: Regularly test auto-scaling scenarios
4. **Resource Limits**: Always set resource limits and reservations
5. **Network Optimization**: Optimize service-to-service communication
6. **Cache Effectively**: Implement multiple levels of caching
7. **Database Optimization**: Scale databases separately from application services