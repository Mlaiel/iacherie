# Ainflue Production Configuration Guide

## Overview

This guide covers the complete production configuration setup for the Ainflue platform, including environment variables, Kubernetes secrets, monitoring with Grafana/Prometheus, and automated CI/CD deployment.

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 1.0.0  
**Date:** 2025-01-15

## Table of Contents

1. [Production Environment Variables](#production-environment-variables)
2. [Kubernetes Secrets Management](#kubernetes-secrets-management)
3. [Monitoring Configuration](#monitoring-configuration)
4. [CI/CD Pipeline Setup](#cicd-pipeline-setup)
5. [Security Validation](#security-validation)
6. [Deployment Process](#deployment-process)
7. [Troubleshooting](#troubleshooting)

## Production Environment Variables

### 1. Environment File Setup

The production environment is configured using the `.env.production` file. This file contains all necessary configuration variables for production deployment.

**Location:** `.env.production`

### 2. Critical Configuration Sections

#### Application Configuration
```bash
APP_NAME=Ainflue
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

#### Database Configuration
```bash
POSTGRES_HOST=ainflue-postgresql-cluster.postgres.svc.cluster.local
REDIS_HOST=ainflue-redis-cluster.redis.svc.cluster.local
MONGODB_HOST=ainflue-mongodb-cluster.mongodb.svc.cluster.local
```

#### Security Configuration
```bash
JWT_SECRET_KEY=${JWT_SECRET_KEY_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY_SECRET}
FORCE_HTTPS=true
```

#### External API Configuration
```bash
OPENAI_API_KEY=${OPENAI_API_KEY_SECRET}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY_SECRET}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID_SECRET}
```

### 3. Secret References

All sensitive values in the `.env.production` file use placeholder syntax `${SECRET_NAME_SECRET}` which are replaced by Kubernetes secrets during deployment.

## Kubernetes Secrets Management

### 1. Secret Manifests

Production secrets are managed through Kubernetes secret manifests located at:
`kubernetes/secrets/production-secrets.yaml`

### 2. Secret Categories

#### External API Secrets
- OpenAI API key
- Social media platform APIs (YouTube, Instagram, TikTok, etc.)
- Payment processor APIs (Stripe, PayPal, Wise)

#### Database Secrets
- PostgreSQL passwords
- Redis passwords
- MongoDB passwords

#### Security Secrets
- JWT secret keys
- Encryption keys
- OAuth2 secrets

#### Cloud Infrastructure Secrets
- AWS access keys
- Monitoring credentials

### 3. Applying Secrets

Before deployment, replace all placeholder values in the secrets file:

```bash
# Edit the secrets file
nano kubernetes/secrets/production-secrets.yaml

# Apply secrets to Kubernetes
kubectl apply -f kubernetes/secrets/production-secrets.yaml -n ainflue
```

## Monitoring Configuration

### 1. Grafana Dashboard

A comprehensive production monitoring dashboard is provided:
`monitoring/grafana/production_monitoring_dashboard.json`

**Features:**
- System overview and uptime monitoring
- API response time and request rate metrics
- Error rate tracking
- Database connection monitoring
- Resource utilization (CPU, Memory, Disk)
- Business metrics (AI processing, revenue, active users)

### 2. Prometheus Configuration

Production-ready Prometheus configuration includes:
- Service discovery for Kubernetes
- Comprehensive metric collection
- Alert rule definitions

**Location:** `monitoring/prometheus/prometheus.yml`

### 3. Alert Rules

Production alert rules cover:
- Infrastructure alerts (service down, high resource usage)
- Database alerts (connection issues, high load)
- Application alerts (API errors, queue backlogs)
- Security alerts (failed logins, rate limit violations)
- Business alerts (revenue drops, low user activity)

**Location:** `monitoring/prometheus/production_alert_rules.yml`

### 4. Monitoring Stack Deployment

Deploy the monitoring stack using Docker Compose:

```bash
# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana at http://localhost:3000
# Access Prometheus at http://localhost:9090
```

## CI/CD Pipeline Setup

### 1. GitHub Actions Workflow

The automated deployment pipeline is configured in:
`.github/workflows/production-deployment.yml`

### 2. Pipeline Stages

1. **Security Scan** - Code security analysis
2. **Build and Test** - Code quality and unit tests
3. **Docker Build** - Multi-arch container images
4. **Vulnerability Scan** - Container security scanning
5. **Staging Deployment** - Automated staging deployment
6. **Integration Tests** - End-to-end testing
7. **Production Deployment** - Blue-green production deployment
8. **Post-deployment** - Cache warming and notifications

### 3. Deployment Strategy

The pipeline uses **Blue-Green deployment** for zero-downtime updates:

1. Deploy new version to "green" environment
2. Run health checks on green deployment
3. Switch traffic from blue to green
4. Keep blue as rollback option

### 4. Required Secrets

Configure these secrets in GitHub repository settings:

```
POSTGRES_PASSWORD
REDIS_PASSWORD
JWT_SECRET_KEY
OPENAI_API_KEY
STRIPE_SECRET_KEY
KUBE_CONFIG_PRODUCTION
SLACK_WEBHOOK_URL
```

## Security Validation

### 1. Security Validation Script

A comprehensive security validation script is provided:
`scripts/validate_production_security.py`

### 2. Validation Checks

- Secret strength and entropy validation
- Placeholder value detection
- Production setting verification
- Security header configuration
- Database security settings
- API security configuration

### 3. Running Security Validation

```bash
# Validate production configuration
python3 scripts/validate_production_security.py --env-file .env.production

# Generate secure keys
python3 scripts/validate_production_security.py --generate-keys

# Output in JSON format
python3 scripts/validate_production_security.py --json
```

### 4. Security Requirements

- All placeholder values must be replaced
- Secrets must have minimum length and entropy
- DEBUG mode must be disabled
- HTTPS must be enforced
- Proper security headers must be configured

## Deployment Process

### 1. Automated Setup Script

Use the production setup script for streamlined deployment:
`scripts/setup_production.sh`

### 2. Manual Deployment Steps

1. **Prerequisites Check**
   ```bash
   # Verify tools are installed
   kubectl version --client
   docker --version
   python3 --version
   ```

2. **Security Validation**
   ```bash
   # Validate configuration
   python3 scripts/validate_production_security.py
   ```

3. **Replace Placeholder Values**
   ```bash
   # Generate secure keys
   python3 scripts/validate_production_security.py --generate-keys
   
   # Update .env.production and secrets files
   nano .env.production
   nano kubernetes/secrets/production-secrets.yaml
   ```

4. **Deploy Infrastructure**
   ```bash
   # Create namespaces
   kubectl create namespace ainflue
   kubectl create namespace ainflue-monitoring
   
   # Apply secrets
   kubectl apply -f kubernetes/secrets/production-secrets.yaml -n ainflue
   
   # Deploy monitoring
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

5. **Deploy Application**
   ```bash
   # Deploy production stack
   docker-compose -f docker-compose.production.yml up -d
   
   # Or use Kubernetes
   kubectl apply -f kubernetes/environments/production/ -n ainflue
   ```

6. **Verify Deployment**
   ```bash
   # Check pod status
   kubectl get pods -n ainflue
   
   # Run health checks
   curl -f https://api.ainflue.com/health
   ```

### 3. Automated Deployment

For automated deployment via CI/CD:

1. Push to main branch or create a version tag
2. GitHub Actions automatically triggers deployment
3. Monitor deployment progress in Actions tab
4. Verify deployment success through monitoring dashboards

## Troubleshooting

### 1. Common Issues

#### Secret Validation Failures
```bash
# Problem: Placeholder values not replaced
# Solution: Update secrets with actual values
python3 scripts/validate_production_security.py --generate-keys
```

#### Database Connection Issues
```bash
# Check database pod status
kubectl get pods -n ainflue | grep postgres

# Check database logs
kubectl logs deployment/postgresql-master -n ainflue
```

#### API Service Unavailable
```bash
# Check API pod status
kubectl get pods -n ainflue | grep ainflue-api

# Check service endpoints
kubectl get endpoints -n ainflue
```

### 2. Monitoring and Alerts

- **Grafana Dashboard:** http://localhost:3000 (admin/admin)
- **Prometheus Metrics:** http://localhost:9090
- **Alert Manager:** http://localhost:9093

### 3. Log Analysis

```bash
# Application logs
kubectl logs deployment/ainflue-api -n ainflue --follow

# Database logs
kubectl logs deployment/postgresql-master -n ainflue

# Monitoring logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### 4. Rollback Procedures

#### Automatic Rollback
The CI/CD pipeline automatically rolls back on deployment failures.

#### Manual Rollback
```bash
# Kubernetes rollback
kubectl rollout undo deployment/ainflue-api -n ainflue

# Docker Compose rollback
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d
```

## Security Considerations

### 1. Secret Management
- Use Kubernetes secrets for sensitive data
- Rotate secrets regularly
- Never commit secrets to version control
- Use strong, randomly generated keys

### 2. Network Security
- Enable HTTPS enforcement
- Configure proper CORS policies
- Implement rate limiting
- Use security headers

### 3. Monitoring Security
- Monitor failed login attempts
- Track API abuse patterns
- Set up security alerts
- Regular security audits

## Maintenance

### 1. Regular Tasks
- Update dependencies monthly
- Rotate secrets quarterly
- Review security configurations
- Monitor resource usage trends

### 2. Backup Procedures
- Database backups run daily at 2 AM UTC
- Configuration backups before changes
- Monitor backup success through alerts

### 3. Updates and Patches
- Security patches applied automatically
- Feature updates through CI/CD pipeline
- Staged rollout for major changes

## Support

For production deployment assistance:
- **Email:** mlaiel@live.de
- **Documentation:** This guide
- **Monitoring:** Grafana dashboards
- **Alerts:** Configured through AlertManager

---

**Copyright © 2025 Fahed Mlaiel. All rights reserved.**