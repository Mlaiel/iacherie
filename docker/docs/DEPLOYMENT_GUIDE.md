# Docker Deployment Guide

## Production-Ready Deployment for Ainflue Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### Prerequisites

- Docker Engine 24.0+
- Docker Compose 2.20+
- Docker Swarm initialized
- Minimum 32GB RAM
- 8 CPU cores
- 1TB SSD storage

### Environment Setup

#### 1. Initialize Docker Swarm
```bash
docker swarm init --advertise-addr <manager-ip>
```

#### 2. Add Worker Nodes
```bash
docker swarm join --token <token> <manager-ip>:2377
```

#### 3. Create Overlay Networks
```bash
docker network create --driver overlay ainflue-network
docker network create --driver overlay monitoring-network
docker network create --driver overlay security-network
```

### Production Deployment

#### 1. Deploy Core Infrastructure
```bash
docker stack deploy -c docker-compose.infrastructure.yml infrastructure
```

#### 2. Deploy Business Services
```bash
# Audio processing services
docker stack deploy -c docker/audio/docker-compose.audio.yml audio

# Protection services  
docker stack deploy -c docker/protection/docker-compose.protection.yml protection

# Monetization services
docker stack deploy -c docker/monetization/docker-compose.monetization.yml monetization
```

#### 3. Deploy Monitoring Stack
```bash
docker stack deploy -c docker/monitoring/docker-compose.monitoring.yml monitoring
```

### Service Configuration

#### Environment Variables
Create `.env.production` with:
```env
# Database
POSTGRES_HOST=postgres-cluster
POSTGRES_DB=ainflue_prod
POSTGRES_USER=ainflue
POSTGRES_PASSWORD=<secure-password>

# Redis
REDIS_HOST=redis-cluster
REDIS_PASSWORD=<secure-password>

# Security
JWT_SECRET=<secure-jwt-secret>
ENCRYPTION_KEY=<secure-encryption-key>

# External APIs
OPENAI_API_KEY=<api-key>
STRIPE_SECRET_KEY=<stripe-key>
```

#### Service Scaling
```bash
# Scale audio processing
docker service scale audio_audio-processor=3

# Scale monetization services
docker service scale monetization_payment-processor=2
docker service scale monetization_revenue-tracker=2
```

### Health Checks

All services include health checks:
```bash
# Check service health
docker service ls
docker service ps <service-name>

# View service logs
docker service logs <service-name>
```

### SSL/TLS Configuration

#### 1. Generate Certificates
```bash
# Using Let's Encrypt
certbot certonly --standalone -d api.ainflue.com
```

#### 2. Update nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name api.ainflue.com;
    
    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;
    
    location / {
        proxy_pass http://api-gateway:8000;
    }
}
```

### Backup Strategy

#### Daily Database Backups
```bash
# PostgreSQL backup
docker exec postgres pg_dump -U ainflue ainflue_prod > backup_$(date +%Y%m%d).sql

# MongoDB backup
docker exec mongodb mongodump --db ainflue --out /backup/$(date +%Y%m%d)
```

#### Configuration Backups
```bash
# Backup Docker configs
docker config ls --format "table {{.Name}}"
docker config inspect <config-name> > configs/backup/
```

### Troubleshooting

#### Common Issues

1. **Service Won't Start**
   ```bash
   docker service ps <service-name> --no-trunc
   docker service logs <service-name>
   ```

2. **Network Connectivity Issues**
   ```bash
   docker network ls
   docker network inspect ainflue-network
   ```

3. **Resource Constraints**
   ```bash
   docker node ls
   docker node inspect <node-id>
   ```

### Performance Optimization

#### Resource Limits
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

#### Update Configuration
```yaml
deploy:
  update_config:
    parallelism: 2
    delay: 30s
    failure_action: rollback
```

### Security Hardening

#### Service User
All services run as non-root users:
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```

#### Network Segmentation
```yaml
networks:
  frontend:
    external: true
  backend:
    internal: true
```

#### Secret Management
```bash
# Create secrets
echo "password" | docker secret create db_password -
```

### Monitoring Integration

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'docker-services'
    static_configs:
      - targets: ['localhost:9100']
```

#### Grafana Dashboards
- Docker Swarm Overview
- Service Performance Metrics
- Resource Utilization
- Error Rate Monitoring