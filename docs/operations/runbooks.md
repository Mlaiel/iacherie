# 🔧 Ainflue Platform - Operational Runbooks

## 📋 Overview

This comprehensive operational runbook provides detailed procedures for the day-to-day operations of the Ainflue AI-powered content protection and monetization platform. These runbooks ensure consistent, reliable operations and provide step-by-step guidance for common operational tasks.

## 🎯 Runbook Categories

### 1. System Operations
- **[Service Management](#service-management)** - Starting, stopping, and managing services
- **[Performance Monitoring](#performance-monitoring)** - System performance tracking
- **[Health Checks](#health-checks)** - System health verification
- **[Log Management](#log-management)** - Log collection and analysis
- **[Database Operations](#database-operations)** - Database maintenance and troubleshooting

### 2. Security Operations
- **[Security Monitoring](#security-monitoring)** - Security event monitoring
- **[Incident Response](#incident-response)** - Security incident procedures
- **[Access Management](#access-management)** - User access control
- **[Certificate Management](#certificate-management)** - SSL/TLS certificate operations
- **[Vulnerability Management](#vulnerability-management)** - Security assessment procedures

### 3. Deployment Operations
- **[Application Deployment](#application-deployment)** - Code deployment procedures
- **[Configuration Management](#configuration-management)** - Configuration updates
- **[Rollback Procedures](#rollback-procedures)** - Deployment rollback steps
- **[Environment Management](#environment-management)** - Environment maintenance

### 4. Data Operations
- **[Backup Procedures](#backup-procedures)** - Data backup operations
- **[Data Recovery](#data-recovery)** - Data restoration procedures
- **[Data Migration](#data-migration)** - Data transfer operations
- **[Archive Management](#archive-management)** - Long-term data storage

## 🔧 Service Management

### Starting Services

#### Prerequisites
- Verify system resources are available
- Check dependency services are running
- Validate configuration files
- Ensure database connectivity

#### Kubernetes Service Startup
```bash
# Check cluster status
kubectl cluster-info
kubectl get nodes

# Start core services in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmaps.yaml
kubectl apply -f k8s/secrets.yaml

# Start database services
kubectl apply -f k8s/database/
kubectl wait --for=condition=ready pod -l app=postgresql --timeout=300s

# Start application services
kubectl apply -f k8s/api/
kubectl apply -f k8s/ai-engine/
kubectl apply -f k8s/content-protection/

# Verify deployments
kubectl get deployments
kubectl get services
kubectl get pods
```

#### Docker Compose Service Startup
```bash
# Production environment
cd /opt/ainflue
docker-compose -f docker-compose.production.yml up -d

# Verify services
docker-compose ps
docker-compose logs -f

# Check health endpoints
curl -f http://localhost/health
curl -f http://localhost/api/v1/health
```

### Stopping Services

#### Graceful Shutdown Procedure
```bash
# Kubernetes graceful shutdown
kubectl scale deployment api-gateway --replicas=0
kubectl scale deployment content-processor --replicas=0
kubectl scale deployment ai-engine --replicas=0

# Wait for pods to terminate gracefully
kubectl get pods -w

# Stop database services last
kubectl scale statefulset postgresql --replicas=0
kubectl scale statefulset mongodb --replicas=0

# Docker Compose graceful shutdown
docker-compose -f docker-compose.production.yml down --timeout 60
```

#### Emergency Shutdown
```bash
# Force immediate shutdown if graceful fails
kubectl delete pods --all --force --grace-period=0
docker-compose kill
docker stop $(docker ps -q)
```

### Service Status Verification

#### Health Check Commands
```bash
# Kubernetes service health
kubectl get pods --all-namespaces
kubectl describe pod <pod-name>
kubectl logs <pod-name> --tail=100

# Application health endpoints
curl -s http://localhost/health | jq
curl -s http://localhost/api/v1/health | jq
curl -s http://localhost/metrics

# Database connectivity
psql -h localhost -U postgres -d ainflue -c "SELECT 1"
mongo --host localhost --eval "db.runCommand({ping: 1})"
redis-cli ping
```

## 📊 Performance Monitoring

### System Resource Monitoring

#### CPU and Memory Monitoring
```bash
# Real-time system monitoring
top -p $(pgrep -d',' -f ainflue)
htop
iotop

# Historical resource usage
sar -u 1 10  # CPU usage
sar -r 1 10  # Memory usage
sar -d 1 10  # Disk I/O

# Container resource usage
docker stats
kubectl top nodes
kubectl top pods
```

#### Application Performance Metrics
```bash
# API response times
curl -w "@curl-format.txt" -s -o /dev/null http://localhost/api/v1/users

# Database performance
psql -d ainflue -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
psql -d ainflue -c "SELECT * FROM pg_stat_database WHERE datname = 'ainflue';"

# Queue monitoring
redis-cli info stats
celery -A ainflue.app inspect active
celery -A ainflue.app inspect stats
```

### Performance Thresholds and Alerts

#### Critical Thresholds
```yaml
performance_thresholds:
  cpu_usage:
    warning: 70%
    critical: 85%
    action: "scale_horizontally"
  
  memory_usage:
    warning: 75%
    critical: 90%
    action: "restart_high_memory_pods"
  
  disk_usage:
    warning: 80%
    critical: 95%
    action: "cleanup_logs_expand_storage"
  
  api_response_time:
    warning: 2000ms
    critical: 5000ms
    action: "investigate_performance_bottleneck"
  
  database_connections:
    warning: 80%
    critical: 95%
    action: "optimize_connection_pooling"
```

## 🩺 Health Checks

### Application Health Verification

#### Automated Health Checks
```bash
#!/bin/bash
# health-check.sh - Comprehensive health verification

# API Gateway Health
echo "Checking API Gateway..."
if curl -f -s http://localhost/health > /dev/null; then
    echo "✅ API Gateway: Healthy"
else
    echo "❌ API Gateway: Unhealthy"
    exit 1
fi

# Database Health
echo "Checking Database..."
if psql -h localhost -U postgres -d ainflue -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ Database: Healthy"
else
    echo "❌ Database: Unhealthy"
    exit 1
fi

# Redis Health
echo "Checking Redis..."
if redis-cli ping | grep -q PONG; then
    echo "✅ Redis: Healthy"
else
    echo "❌ Redis: Unhealthy"
    exit 1
fi

# AI Engine Health
echo "Checking AI Engine..."
if curl -f -s http://localhost:8001/health > /dev/null; then
    echo "✅ AI Engine: Healthy"
else
    echo "❌ AI Engine: Unhealthy"
    exit 1
fi

echo "All health checks passed ✅"
```

#### Manual Health Verification
```bash
# Check service endpoints
curl -v http://localhost/api/v1/status
curl -v http://localhost/api/v1/metrics

# Verify authentication
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'

# Test content processing
curl -X POST http://localhost/api/v1/content/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.mp3"
```

### Infrastructure Health Checks

#### Kubernetes Cluster Health
```bash
# Cluster component health
kubectl get componentstatuses
kubectl cluster-info

# Node health
kubectl get nodes
kubectl describe nodes

# Pod health
kubectl get pods --all-namespaces
kubectl get events --sort-by=.metadata.creationTimestamp

# Service connectivity
kubectl get services
kubectl get endpoints
```

#### Network Connectivity
```bash
# External connectivity
ping -c 3 8.8.8.8
nslookup google.com

# Internal service connectivity
kubectl exec -it <pod-name> -- ping <service-name>
kubectl exec -it <pod-name> -- nslookup <service-name>

# Load balancer health
curl -I http://load-balancer-ip/health
```

## 📋 Log Management

### Log Collection and Analysis

#### Application Logs
```bash
# Kubernetes pod logs
kubectl logs -f deployment/api-gateway
kubectl logs -f deployment/ai-engine --tail=100
kubectl logs --previous deployment/content-processor

# Container logs
docker logs -f ainflue_api_1
docker logs --tail=100 ainflue_database_1

# System logs
journalctl -u ainflue.service -f
tail -f /var/log/ainflue/application.log
```

#### Log Analysis Commands
```bash
# Error log analysis
grep -i error /var/log/ainflue/*.log | tail -20
grep -i "exception\|error\|fail" /var/log/ainflue/app.log

# Performance log analysis
grep "slow query" /var/log/postgresql/postgresql.log
grep "response_time" /var/log/ainflue/access.log | awk '$8 > 2000'

# Security log analysis
grep -i "unauthorized\|forbidden\|failed.*login" /var/log/ainflue/security.log
grep -i "sql injection\|xss\|csrf" /var/log/ainflue/security.log
```

#### Log Rotation and Cleanup
```bash
# Manual log rotation
logrotate -f /etc/logrotate.d/ainflue

# Cleanup old logs
find /var/log/ainflue -name "*.log.*" -mtime +30 -delete
find /var/log/ainflue -name "*.gz" -mtime +90 -delete

# Container log cleanup
docker system prune -f
docker volume prune -f
```

## 🗄️ Database Operations

### PostgreSQL Operations

#### Database Maintenance
```sql
-- Database health check
SELECT 
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit
FROM pg_stat_database 
WHERE datname = 'ainflue';

-- Table statistics
SELECT 
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

-- Index usage analysis
SELECT 
    indexrelname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

#### Performance Optimization
```sql
-- Analyze table statistics
ANALYZE;

-- Vacuum database
VACUUM ANALYZE;

-- Reindex if needed
REINDEX DATABASE ainflue;

-- Update table statistics
UPDATE pg_stat_reset();
```

#### Backup Operations
```bash
# Create database backup
pg_dump -h localhost -U postgres -d ainflue > backup_$(date +%Y%m%d_%H%M%S).sql

# Create compressed backup
pg_dump -h localhost -U postgres -d ainflue | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore from backup
psql -h localhost -U postgres -d ainflue < backup_file.sql

# Point-in-time recovery
pg_basebackup -h localhost -U postgres -D /backup/base -Ft -z -P
```

### MongoDB Operations

#### Database Monitoring
```javascript
// Database status
db.runCommand({serverStatus: 1})

// Collection statistics
db.users.stats()
db.content.stats()

// Index usage
db.users.aggregate([{$indexStats: {}}])

// Current operations
db.currentOp()
```

#### Maintenance Operations
```javascript
// Compact collections
db.runCommand({compact: "users"})

// Repair database
db.repairDatabase()

// Update indexes
db.users.reIndex()

// Profiler analysis
db.getProfilingStatus()
db.system.profile.find().sort({ts: -1}).limit(5)
```

### Redis Operations

#### Cache Monitoring
```bash
# Redis information
redis-cli info all
redis-cli info memory
redis-cli info stats

# Key analysis
redis-cli --bigkeys
redis-cli --latency-history

# Memory usage
redis-cli memory usage <key>
redis-cli memory stats
```

#### Cache Maintenance
```bash
# Clear specific cache
redis-cli del "cache:users:*"
redis-cli flushdb

# Expire keys
redis-cli expire "session:*" 3600

# Export/Import data
redis-cli --rdb dump.rdb
redis-cli --pipe < commands.txt
```

## 🚀 Application Deployment

### Deployment Prerequisites

#### Pre-deployment Checklist
```bash
# Verify environment readiness
kubectl get nodes
kubectl get namespaces
kubectl describe nodes | grep -A 5 "Allocated resources"

# Check container registry access
docker login registry.ainflue.com
docker pull registry.ainflue.com/ainflue/api:latest

# Validate configuration
kubectl apply --dry-run=client -f k8s/
helm template . --validate

# Database migration check
python manage.py check --deploy
python manage.py migrate --check
```

### Blue-Green Deployment

#### Deployment Process
```bash
#!/bin/bash
# blue-green-deploy.sh

CURRENT_ENV=$(kubectl get service api-gateway -o jsonpath='{.spec.selector.version}')
NEW_ENV=$([ "$CURRENT_ENV" = "blue" ] && echo "green" || echo "blue")

echo "Current environment: $CURRENT_ENV"
echo "Deploying to: $NEW_ENV"

# Deploy new version
kubectl apply -f k8s/api-$NEW_ENV.yaml
kubectl apply -f k8s/ai-engine-$NEW_ENV.yaml

# Wait for deployment
kubectl rollout status deployment/api-gateway-$NEW_ENV
kubectl rollout status deployment/ai-engine-$NEW_ENV

# Run health checks
./scripts/health-check.sh $NEW_ENV

# Switch traffic
kubectl patch service api-gateway -p '{"spec":{"selector":{"version":"'$NEW_ENV'"}}}'

# Verify traffic switch
curl -s http://localhost/api/v1/version | jq .environment

echo "Deployment to $NEW_ENV completed successfully"
```

### Rolling Deployment

#### Kubernetes Rolling Update
```bash
# Update deployment image
kubectl set image deployment/api-gateway \
  api-gateway=registry.ainflue.com/ainflue/api:v2.1.0

# Monitor rollout
kubectl rollout status deployment/api-gateway
kubectl rollout history deployment/api-gateway

# Rollback if needed
kubectl rollout undo deployment/api-gateway
kubectl rollout undo deployment/api-gateway --to-revision=2
```

### Database Migrations

#### Migration Process
```bash
# Backup database before migration
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > pre_migration_backup.sql

# Run migrations
python manage.py migrate --plan
python manage.py migrate

# Verify migration
python manage.py showmigrations
```

## 🔄 Rollback Procedures

### Application Rollback

#### Immediate Rollback
```bash
# Kubernetes rollback
kubectl rollout undo deployment/api-gateway
kubectl rollout undo deployment/ai-engine

# Docker Compose rollback
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d --force-recreate

# Verify rollback
./scripts/health-check.sh
curl -s http://localhost/api/v1/version
```

#### Database Rollback
```bash
# Stop application
kubectl scale deployment api-gateway --replicas=0

# Restore database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < pre_migration_backup.sql

# Restart application with previous version
kubectl set image deployment/api-gateway \
  api-gateway=registry.ainflue.com/ainflue/api:v2.0.0
kubectl scale deployment api-gateway --replicas=3
```

## 🔍 Troubleshooting Procedures

### Common Issues and Solutions

#### High CPU Usage
```bash
# Identify high CPU processes
top -o %CPU
ps aux --sort=-%cpu | head

# Kubernetes CPU usage
kubectl top pods --sort-by=cpu
kubectl describe pod <high-cpu-pod>

# Scale horizontally if needed
kubectl scale deployment api-gateway --replicas=5
```

#### Memory Leaks
```bash
# Monitor memory usage
free -h
ps aux --sort=-%mem | head

# Check for memory leaks
valgrind --tool=memcheck --leak-check=full python app.py

# Restart high memory pods
kubectl delete pod <high-memory-pod>
```

#### Database Connection Issues
```bash
# Check connection pool
psql -d ainflue -c "SELECT * FROM pg_stat_activity;"

# Restart database connections
sudo systemctl restart postgresql
kubectl rollout restart deployment/api-gateway

# Update connection pool settings
# Edit postgresql.conf: max_connections = 200
# Edit app config: SQLALCHEMY_POOL_SIZE = 20
```

#### Disk Space Issues
```bash
# Check disk usage
df -h
du -sh /var/log/* | sort -rh

# Clean up logs
find /var/log -name "*.log" -mtime +7 -delete
docker system prune -f

# Expand storage if needed
lvextend -L +10G /dev/mapper/vg-lv
resize2fs /dev/mapper/vg-lv
```

## 📞 Emergency Procedures

### Emergency Contacts
- **On-Call Engineer**: +1-XXX-XXX-XXXX
- **Database Administrator**: +1-XXX-XXX-XXXX
- **Security Team**: +1-XXX-XXX-XXXX
- **Executive Escalation**: +1-XXX-XXX-XXXX

### Emergency Response Steps
1. **Assess Severity**: Determine impact level
2. **Notify Team**: Alert appropriate personnel
3. **Immediate Actions**: Take containment measures
4. **Communicate**: Update stakeholders
5. **Resolve**: Implement solution
6. **Verify**: Confirm resolution
7. **Document**: Record incident details

### Emergency Commands
```bash
# Emergency shutdown
kubectl delete pods --all --force --grace-period=0
docker-compose kill

# Emergency database recovery
pg_ctl stop -D /var/lib/postgresql/data -m immediate
pg_ctl start -D /var/lib/postgresql/data

# Emergency log cleanup
rm -rf /var/log/ainflue/*.log
truncate -s 0 /var/log/ainflue/app.log
```

---

**Document Information**
- **Version**: 1.0.0
- **Last Updated**: {{current_date}}
- **Next Review**: {{next_review_date}}
- **Owner**: Operations Team
- **Approved By**: CTO

---

**Quick Reference**
- **Health Check Script**: `/opt/scripts/health-check.sh`
- **Emergency Procedures**: `/opt/docs/emergency-procedures.md`
- **Contact List**: `/opt/docs/emergency-contacts.txt`
- **Log Locations**: `/var/log/ainflue/`

---

> **Note**: This runbook should be accessible during emergencies. Keep printed copies in secure locations and ensure all operations team members are familiar with these procedures.