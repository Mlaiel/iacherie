# Troubleshooting Guide

## Docker Troubleshooting for Ainflue Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### Common Issues and Solutions

#### 1. Container Startup Issues

**Problem: Container fails to start**
```bash
# Diagnostic commands
docker service ps <service-name> --no-trunc
docker service logs <service-name>
docker inspect <container-id>

# Common solutions
# 1. Check resource constraints
docker service update --limit-memory 2g <service-name>

# 2. Check port conflicts
docker service update --publish-rm 8080:8080 --publish-add 8081:8080 <service-name>

# 3. Restart service
docker service update --force <service-name>
```

**Problem: Image pull failures**
```bash
# Check image availability
docker pull <image-name>

# Check registry connectivity
docker login registry.ainflue.com

# Use alternative registry
docker service update --image backup-registry.com/ainflue/api:latest <service-name>
```

#### 2. Network Connectivity Issues

**Problem: Service-to-service communication failure**
```bash
# Check network configuration
docker network ls
docker network inspect ainflue-network

# Test connectivity between services
docker exec <container-id> ping <service-name>
docker exec <container-id> telnet <service-name> <port>

# Debug DNS resolution
docker exec <container-id> nslookup <service-name>
```

**Problem: External API connectivity**
```bash
# Test from container
docker exec <container-id> curl -v https://api.external.com

# Check firewall rules
iptables -L
ufw status

# Test with proxy
docker exec <container-id> curl --proxy http://proxy:8080 https://api.external.com
```

#### 3. Performance Issues

**Problem: High CPU usage**
```bash
# Monitor container resources
docker stats
docker exec <container-id> top

# Check for memory leaks
docker exec <container-id> ps aux --sort=-%mem | head

# Scale service if needed
docker service scale <service-name>=5

# Update resource limits
docker service update --limit-cpu 2.0 --limit-memory 4g <service-name>
```

**Problem: Slow database queries**
```bash
# PostgreSQL diagnostics
docker exec postgres psql -U ainflue -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check slow queries
docker exec postgres psql -U ainflue -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Redis diagnostics
docker exec redis redis-cli info memory
docker exec redis redis-cli slowlog get 10
```

### Debugging Techniques

#### 1. Container Debugging
```bash
# Enter running container
docker exec -it <container-id> /bin/bash

# Run debugging container with same network/volumes
docker run -it --rm \
  --network container:<container-id> \
  --volumes-from <container-id> \
  alpine:latest /bin/sh

# Debug with privileged access
docker run -it --rm --privileged \
  --pid container:<container-id> \
  --network container:<container-id> \
  alpine:latest /bin/sh
```

#### 2. Log Analysis
```bash
# Centralized logging with ELK
docker service logs --since 1h <service-name> | grep ERROR

# Follow logs in real-time
docker service logs -f <service-name>

# Search logs with jq
docker service logs <service-name> --raw | jq 'select(.level == "ERROR")'

# Export logs for analysis
docker service logs <service-name> > service-logs.txt
```

### Health Check Debugging

#### 1. Health Check Failures
```bash
# Check health check configuration
docker service inspect <service-name> | jq '.Spec.TaskTemplate.ContainerSpec.Healthcheck'

# Test health check manually
docker exec <container-id> curl -f http://localhost:8000/health

# Debug health check script
docker exec <container-id> /bin/bash -c "$(docker inspect <container-id> | jq -r '.[0].Config.Healthcheck.Test[1]')"
```

#### 2. Custom Health Checks
```python
# health-debug.py
import asyncio
import aiohttp
import time

async def debug_health_check():
    """Debug health check endpoint"""
    
    endpoints = [
        'http://api:8000/health',
        'http://audio-processor:8001/health',
        'http://database:5432'
    ]
    
    for endpoint in endpoints:
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, timeout=5) as response:
                    response_time = time.time() - start_time
                    print(f"{endpoint}: {response.status} ({response_time:.2f}s)")
                    
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

asyncio.run(debug_health_check())
```

### Storage Issues

#### 1. Volume Problems
```bash
# Check volume usage
docker system df
docker volume ls
df -h

# Inspect volume details
docker volume inspect <volume-name>

# Clean up unused volumes
docker volume prune

# Backup and restore volume
docker run --rm -v <volume-name>:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
```

#### 2. Disk Space Issues
```bash
# Find large files
docker exec <container-id> find / -type f -size +100M 2>/dev/null

# Clean up docker system
docker system prune -a

# Remove old images
docker image prune -a

# Clean up build cache
docker builder prune
```

### Security Debugging

#### 1. Permission Issues
```bash
# Check container user
docker exec <container-id> whoami
docker exec <container-id> id

# Check file permissions
docker exec <container-id> ls -la /app

# Fix permissions
docker exec <container-id> chown -R appuser:appuser /app
```

#### 2. Secret Access Issues
```bash
# Check secret mounting
docker exec <container-id> ls -la /run/secrets/

# Verify secret content
docker exec <container-id> cat /run/secrets/db_password

# Test secret in environment
docker exec <container-id> env | grep SECRET
```

### Performance Profiling

#### 1. Python Application Profiling
```python
# profile-service.py
import cProfile
import pstats
import io
from fastapi import FastAPI

app = FastAPI()

@app.middleware("http")
async def profile_middleware(request, call_next):
    pr = cProfile.Profile()
    pr.enable()
    
    response = await call_next(request)
    
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    # Log profiling results
    print(s.getvalue())
    
    return response
```

#### 2. Database Performance Profiling
```sql
-- PostgreSQL slow query analysis
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements 
WHERE mean_time > 1000  -- queries taking more than 1 second
ORDER BY mean_time DESC;

-- Check locks
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype;
```

### Monitoring and Alerting Debugging

#### 1. Metrics Collection Issues
```bash
# Check Prometheus targets
curl http://prometheus:9090/api/v1/targets

# Verify metrics endpoint
curl http://api:8000/metrics

# Test metric queries
curl 'http://prometheus:9090/api/v1/query?query=up'
```

#### 2. Alert Configuration
```yaml
# Debug alert rules
docker exec prometheus promtool check rules /etc/prometheus/rules/*.yml

# Test alert evaluation
docker exec prometheus promtool query instant prometheus:9090 'up == 0'
```

### Automated Troubleshooting Scripts

#### 1. System Health Check
```bash
#!/bin/bash
# system-health-check.sh

echo "=== Docker System Health Check ==="

# Check Docker daemon
systemctl is-active docker

# Check swarm status
docker info | grep "Swarm:"

# Check service health
docker service ls --format "table {{.Name}}\t{{.Replicas}}\t{{.Image}}"

# Check node status
docker node ls

# Check system resources
echo "Disk usage:"
df -h

echo "Memory usage:"
free -m

echo "CPU usage:"
top -n 1 -b | head -10

# Check for failed containers
FAILED_SERVICES=$(docker service ls --filter "desired-state=running" --format "{{.Name}}" | while read service; do
    if ! docker service ps $service --filter "desired-state=running" | grep -q "Running"; then
        echo $service
    fi
done)

if [ -n "$FAILED_SERVICES" ]; then
    echo "Failed services: $FAILED_SERVICES"
else
    echo "All services are healthy"
fi
```

#### 2. Auto-Recovery Script
```python
# auto-recovery.py
import docker
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoRecovery:
    def __init__(self):
        self.client = docker.from_env()
        
    def check_and_recover_services(self):
        """Check service health and attempt recovery"""
        
        services = self.client.services.list()
        
        for service in services:
            try:
                tasks = service.tasks(filters={'desired-state': 'running'})
                failed_tasks = [t for t in tasks if t['Status']['State'] == 'failed']
                
                if len(failed_tasks) > 2:
                    logger.warning(f"Service {service.name} has {len(failed_tasks)} failed tasks")
                    
                    # Attempt restart
                    service.force_update()
                    logger.info(f"Restarted service {service.name}")
                    
                    # Scale up if needed
                    spec = service.attrs['Spec']
                    current_replicas = spec['Mode']['Replicated']['Replicas']
                    
                    if current_replicas < 2:
                        service.update(mode={'Replicated': {'Replicas': 3}})
                        logger.info(f"Scaled up service {service.name} to 3 replicas")
                        
            except Exception as e:
                logger.error(f"Error checking service {service.name}: {e}")
    
    def run(self):
        """Run auto-recovery loop"""
        while True:
            self.check_and_recover_services()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    recovery = AutoRecovery()
    recovery.run()
```

### Emergency Procedures

#### 1. Emergency Service Restart
```bash
#!/bin/bash
# emergency-restart.sh

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: $0 <service-name>"
    exit 1
fi

echo "Emergency restart for service: $SERVICE_NAME"

# Force service update
docker service update --force $SERVICE_NAME

# Wait for restart
sleep 30

# Check service status
docker service ps $SERVICE_NAME

# Verify health
if docker service ls --filter name=$SERVICE_NAME --format "{{.Replicas}}" | grep -q "0/"; then
    echo "Service failed to restart. Checking logs..."
    docker service logs --tail 50 $SERVICE_NAME
else
    echo "Service restarted successfully"
fi
```

### Best Practices for Troubleshooting

1. **Start with Logs**: Always check service logs first
2. **Check Resources**: Monitor CPU, memory, and disk usage
3. **Network Diagnostics**: Test connectivity between services
4. **Health Checks**: Verify all health check endpoints
5. **Incremental Changes**: Make one change at a time when troubleshooting
6. **Document Issues**: Keep a record of common issues and solutions
7. **Monitoring**: Use comprehensive monitoring to detect issues early