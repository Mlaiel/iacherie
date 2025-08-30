
# 🚀 Ainflue Platform Infrastructure Startup Guide

## Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.8+
- At least 8GB RAM available

## Quick Start

### 1. Start Basic Services
```bash
# Start basic platform services
docker compose up -d

# Check service health
docker compose ps
```

### 2. Start Monitoring Stack
```bash
# Start monitoring services
docker compose -f docker-compose.monitoring.yml up -d

# Access monitoring interfaces:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin123)
# - AlertManager: http://localhost:9093
```

### 3. Initialize Database
```bash
# Run database migrations
bash test_database_migrations.sh
```

### 4. Production Deployment
```bash
# Copy environment template
cp .env.production.example .env.production

# Edit .env.production with your configuration
# Then start production services:
docker compose -f docker-compose.production.yml --env-file .env.production up -d
```

## Health Checks

### Service Health
```bash
# Check all services
docker compose ps

# Check specific service logs
docker compose logs -f [service-name]
```

### Monitoring Health
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana health
curl http://localhost:3000/api/health
```

### Database Health
```bash
# Check PostgreSQL
docker exec [postgres-container] pg_isready

# Check Redis
docker exec [redis-container] redis-cli ping
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Check if ports 3000, 5432, 6379, 9090 are free
   - Stop conflicting services or change ports in compose files

2. **Memory Issues**
   - Ensure at least 8GB RAM available
   - Reduce replica counts in production compose file

3. **Network Issues**
   - Check Docker network configuration
   - Ensure proper DNS resolution between containers

### Getting Help

- Check logs: `docker compose logs [service]`
- View resource usage: `docker stats`
- Network debugging: `docker network ls`

For support: mlaiel@live.de
