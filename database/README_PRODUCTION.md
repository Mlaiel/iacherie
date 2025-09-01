# 🗄️ Database Production Setup - Ainflue Platform

This module provides a complete production-ready database deployment system for the Ainflue platform, implementing all critical database production requirements with enterprise-grade security, performance, and reliability.

## 🎯 Production Requirements Implemented

### ✅ **Exécuter migrations Alembic** sur base de production
- Automated Alembic migration execution with rollback support
- Schema versioning and migration history tracking
- Production-safe migration strategies

### ✅ **Créer index de performance** sur toutes les tables à fort volume
- Intelligent index creation for high-volume tables
- Performance optimization for content, fingerprints, violations, transactions, and events
- Concurrent index creation to avoid blocking operations

### ✅ **Configurer connection pooling** (pgbouncer ou équivalent)
- Advanced asyncpg connection pooling with configurable parameters
- Connection health monitoring and automatic recovery
- Read/write splitting support for replica databases

### ✅ **Implémenter backup automatique** quotidien avec rétention 30 jours
- Automated daily backup system with configurable retention
- Local and cloud storage support (S3, local filesystem)
- Compression and encryption options for backup security

### ✅ **Configurer réplication** master-slave pour lecture
- Master-slave replication setup for read scaling
- Replication lag monitoring and alerting
- Automatic failover capabilities

### ✅ **Monitorer performances requêtes** avec pg_stat_statements
- pg_stat_statements extension for comprehensive query monitoring
- Slow query detection and analysis
- Performance metrics collection and reporting

### ✅ **Configurer archivage WAL** pour point-in-time recovery
- WAL (Write-Ahead Log) archiving configuration
- Point-in-time recovery (PITR) capabilities
- WAL file management and cleanup

### ✅ **Implémenter health check** base de données avec timeout
- Comprehensive database health monitoring with timeout controls
- Connection, query performance, and resource utilization checks
- Automated health reporting and alerting

### ✅ **Sécuriser connexions** avec SSL/TLS obligatoire
- Complete SSL/TLS certificate management system
- Certificate generation, rotation, and validation
- Enforced encrypted connections with configurable security levels

### ✅ **Configurer utilisateurs** avec privilèges minimaux par service
- Service-based user management with minimal privilege principle
- Role-based access control (RBAC) implementation
- Automated user provisioning and privilege auditing

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install production database requirements
pip install -r database/requirements-production.txt

# Install PostgreSQL extensions (if needed)
sudo apt-get install postgresql-contrib
```

### 2. Configure Environment

Create a configuration file (optional - defaults will be used):

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "ainflue_prod",
    "admin_user": "postgres",
    "admin_password": "your_admin_password"
  },
  "ssl": {
    "mode": "require",
    "cert_path": "/etc/ssl/ainflue",
    "require_client_cert": false
  },
  "backup": {
    "retention_days": 30,
    "storage_path": "/backup/ainflue"
  }
}
```

### 3. Run Production Deployment

```bash
# Full production deployment
python database/production_deployment.py

# With custom configuration
python database/production_deployment.py --config /path/to/config.json

# Dry run (no changes made)
python database/production_deployment.py --dry-run
```

## 📋 Deployment Steps

The production deployment script executes the following steps in order:

1. **Database Connection Setup** - Establish admin connection and verify connectivity
2. **Alembic Migrations** - Execute pending database migrations to latest schema
3. **Performance Indexes** - Create optimized indexes on high-volume tables
4. **Connection Pooling** - Configure and validate connection pool settings
5. **SSL Security** - Setup SSL/TLS certificates and secure connections
6. **User Management** - Create service users with minimal privileges
7. **Backup System** - Configure automated backup with retention policies
8. **Replication** - Setup master-slave replication for read scaling
9. **Performance Monitoring** - Enable pg_stat_statements and query monitoring
10. **WAL Archiving** - Configure write-ahead log archiving for PITR
11. **Health Checks** - Implement comprehensive database health monitoring
12. **Final Validation** - Verify all production requirements are met

## 🔧 Individual Components

### Health Check System

```python
from database.health_check import DatabaseHealthChecker, HealthCheckConfig

# Configure health checks
config = HealthCheckConfig(
    connection_timeout=5.0,
    query_timeout=10.0,
    check_interval_seconds=30
)

# Initialize health checker
health_checker = DatabaseHealthChecker(config, connection_pool)

# Perform health check
result = await health_checker.perform_health_check()
print(f"Database status: {result.status.value}")
```

### SSL/TLS Management

```python
from database.ssl_manager import DatabaseSSLManager, SSLConfig, SSLMode

# Configure SSL
ssl_config = SSLConfig(
    ssl_mode=SSLMode.REQUIRE,
    require_client_cert=False
)

# Setup SSL infrastructure
ssl_manager = DatabaseSSLManager(ssl_config)
result = await ssl_manager.setup_ssl_infrastructure()
```

### User Management

```python
from database.user_manager import DatabaseUserManager, ServiceRole

# Initialize user manager
user_manager = DatabaseUserManager(admin_connection_pool)

# Setup complete user management system
result = await user_manager.setup_user_management_system()

# Create specific service user
user_result = await user_manager.create_user_account(ServiceRole.APPLICATION)
```

## 📊 Monitoring and Maintenance

### Health Check Dashboard

The system provides comprehensive health monitoring:

- **Connection Health**: Database connectivity and pool status
- **Query Performance**: Slow query detection and optimization suggestions
- **Resource Utilization**: CPU, memory, and disk usage monitoring
- **Replication Status**: Lag monitoring and replica health
- **Security Validation**: SSL certificate status and expiration alerts

### Performance Metrics

Key performance indicators tracked:

- Average query response time
- Connection pool utilization
- Slow query frequency
- Replication lag
- Backup success rate
- Health check response time

### Automated Maintenance

The system includes automated maintenance tasks:

- Daily backups with 30-day retention
- SSL certificate rotation
- User password rotation
- Performance index optimization
- WAL file cleanup

## 🔒 Security Features

### Service-Based User Management

Each service gets dedicated database users with minimal required privileges:

- **ainflue_app**: Application read/write access
- **ainflue_readonly**: Read-only access for reporting
- **ainflue_backup**: Backup and restore operations
- **ainflue_replication**: Replication management
- **ainflue_monitor**: Performance monitoring
- **ainflue_analytics**: Analytics data access
- **ainflue_migration**: Schema migration access
- **ainflue_admin**: Administrative operations

### SSL/TLS Encryption

- **Certificate Management**: Automated certificate generation and rotation
- **Connection Encryption**: All database connections encrypted
- **Certificate Validation**: Full certificate chain validation
- **Client Authentication**: Optional mutual TLS authentication

### Access Control

- **Row Level Security**: Sensitive tables protected with RLS policies
- **Connection Limits**: Per-user connection limits to prevent resource exhaustion
- **IP Restrictions**: Optional IP-based access control
- **Audit Logging**: Complete audit trail of all database operations

## 🛠️ Production Configuration

### PostgreSQL Settings

Key production settings configured:

```ini
# Connection and Authentication
max_connections = 200
ssl = on
password_encryption = scram-sha-256

# Performance
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 32MB

# WAL and Replication
wal_level = replica
max_wal_senders = 10
archive_mode = on

# Monitoring
log_connections = on
log_statement = 'ddl'
```

### Connection Pool Settings

```python
pool_config = {
    "min_size": 10,
    "max_size": 100,
    "connection_timeout": 30.0,
    "command_timeout": 60.0
}
```

### Backup Configuration

```python
backup_config = {
    "retention_days": 30,
    "schedule": "0 2 * * *",  # Daily at 2 AM
    "storage_path": "/backup/ainflue",
    "compression": True
}
```

## 📈 Performance Optimization

### Index Strategy

The system creates strategic indexes for optimal performance:

- **Content Tables**: Creator ID, creation date, status, fingerprint hash
- **Fingerprints**: Hash value, content ID, creation date
- **Violations**: Content ID, status, detection date
- **Transactions**: User ID, creation date, status, amount
- **Events**: Timestamp, event type, user ID

### Query Optimization

- pg_stat_statements for query performance monitoring
- Slow query detection and alerting
- Query plan analysis and optimization recommendations
- Index usage statistics and optimization

## 🔄 Backup and Recovery

### Backup Strategy

- **Daily Full Backups**: Complete database dumps with 30-day retention
- **WAL Archiving**: Continuous archiving for point-in-time recovery
- **Compression**: Backup compression to reduce storage requirements
- **Encryption**: Optional backup encryption for enhanced security

### Recovery Procedures

- **Point-in-Time Recovery**: Restore to any point in time using WAL archives
- **Full Database Restore**: Complete database restoration from backup
- **Partial Recovery**: Table-level or schema-level recovery options

## 🚨 Troubleshooting

### Common Issues

1. **Connection Pool Exhaustion**
   - Check connection limits and pool configuration
   - Monitor active connections and query duration

2. **Slow Query Performance**
   - Review pg_stat_statements for slow queries
   - Analyze query plans and index usage

3. **Replication Lag**
   - Monitor replication lag metrics
   - Check network connectivity and disk I/O

4. **SSL Certificate Issues**
   - Verify certificate validity and chain
   - Check certificate permissions and paths

### Diagnostic Commands

```bash
# Check deployment status
python database/production_deployment.py --dry-run

# Monitor health checks
tail -f database_production_setup.log

# View recent deployment reports
ls -la deployment_report_*.json
```

## 📝 Maintenance Tasks

### Regular Maintenance

- **Weekly**: Review slow query reports and optimize
- **Monthly**: Audit user privileges and access patterns
- **Quarterly**: Rotate SSL certificates and review security settings
- **Annually**: Review backup retention policies and disaster recovery procedures

### Performance Tuning

- Monitor and adjust connection pool settings
- Optimize queries based on pg_stat_statements data
- Review and update index strategies
- Tune PostgreSQL configuration parameters

## 🤝 Support and Contributing

For issues, questions, or contributions related to the database production setup:

- **Author**: Fahed Mlaiel (mlaiel@live.de)
- **Documentation**: See individual module documentation for detailed API references
- **Logging**: All operations are logged to `database_production_setup.log`
- **Reports**: Detailed deployment reports are saved as JSON files

## ⚠️ Important Notes

1. **Production Safety**: All operations are designed to be production-safe with minimal downtime
2. **Backup First**: Always ensure recent backups before running production deployment
3. **Testing**: Test the deployment process in staging environment first
4. **Monitoring**: Monitor system health closely after deployment
5. **Security**: Review and customize security settings for your specific requirements

---

**Copyright (c) 2025 Fahed Mlaiel. All rights reserved.**

This production database setup provides enterprise-grade reliability, security, and performance for the Ainflue platform's production environment.