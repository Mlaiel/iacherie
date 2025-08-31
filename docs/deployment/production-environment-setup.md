# Production Environment Configuration Guide

## Overview

This guide provides comprehensive instructions for configuring the Ainflue platform's production environment, including:

- **Kubernetes Secrets** for external APIs
- **Production Environment Variables** for optimal performance
- **Monitoring Dashboards** with comprehensive observability

## Quick Start

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured and connected to your cluster
- Python 3.8+ with kubernetes client library
- Proper RBAC permissions for creating resources

### Automated Deployment

The fastest way to deploy the complete production environment:

```bash
cd kubernetes/scripts
./deploy_production_environment.sh
```

This script will:
1. Create necessary namespaces
2. Deploy production ConfigMaps and Secrets
3. Set up the monitoring stack (Prometheus, Grafana, Jaeger)
4. Configure comprehensive dashboards
5. Apply production-optimized settings

## Component Details

### 1. External API Secrets

#### Configured APIs
- **Social Media**: YouTube, Instagram, TikTok, Spotify, Twitter, LinkedIn, Facebook
- **AI/ML Services**: OpenAI, HuggingFace, Anthropic, Google Cloud, Azure
- **Communication**: SendGrid, Twilio
- **Payments**: Stripe, PayPal, Wise
- **Monitoring**: Sentry, DataDog, New Relic, PagerDuty
- **Cloud Services**: AWS, Cloudflare
- **Additional**: Discord, Telegram bots

#### Manual Secret Configuration

To configure secrets with real API keys:

```bash
# Set environment variables with your API keys
export OPENAI_API_KEY="sk-your-openai-key"
export STRIPE_SECRET_KEY="sk_live_your-stripe-key"
export YOUTUBE_API_KEY="your-youtube-api-key"
# ... add other API keys

# Run the secrets manager
python3 kubernetes/scripts/production_secrets_manager.py
```

#### Secret Structure

Secrets are base64 encoded and stored in Kubernetes secrets:
- `ainflue-secrets`: Main application secrets
- `ainflue-external-api-secrets`: External API credentials
- `ainflue-tls-secret`: TLS certificates
- `docker-registry-secret`: Container registry access

### 2. Production Environment Variables

#### Performance Optimizations
- **Workers**: 16 workers for high concurrency
- **Database Pool**: 25 connections with 50 overflow
- **Redis Connections**: 100 max connections
- **AI Processing**: 32 batch size, GPU optimization
- **Caching**: 2GB cache with compression

#### Security Settings
- **CORS**: HTTPS-only origins
- **Rate Limiting**: 120 requests/minute with 300 burst
- **Session Management**: 30-minute timeout
- **JWT**: 8-hour expiry for security

#### Content Processing
- **File Size**: Up to 1GB content files
- **Formats**: All major audio/video/image formats
- **Retention**: 7 years (2555 days) for compliance
- **AI Accuracy**: 90% similarity threshold

#### Business Configuration
- **Revenue Sharing**: 85% to creators, 15% platform fee
- **Payouts**: $10 minimum threshold
- **Processing**: Hourly revenue calculations
- **Compliance**: GDPR and CCPA enabled

### 3. Monitoring Dashboards

#### System Overview Dashboard
- **Metrics**: Request rate, response time, error rate
- **Resources**: CPU, memory, network I/O
- **Status**: System health, active users
- **Performance**: 95th percentile response times

#### AI Models Dashboard
- **Inference Performance**: Processing time, accuracy scores
- **Resource Usage**: GPU utilization, model memory
- **Queue Status**: Content processing backlog
- **Business Impact**: Revenue detection, violation matches

#### Database Performance Dashboard
- **Query Performance**: Duration, slow queries, locks
- **Connections**: Active/idle connection pools
- **Replication**: Lag monitoring for read replicas
- **Cache Performance**: Hit rates and efficiency

#### Business Metrics Dashboard
- **Revenue**: Real-time revenue tracking, trends
- **Users**: Registration rates, activity patterns
- **Content**: Upload rates, platform distribution
- **Violations**: Detection rates, takedown metrics

## Environment-Specific Configurations

### Development
```bash
export ENVIRONMENT=development
export KUBERNETES_NAMESPACE=ainflue-dev
export MONITORING_NAMESPACE=ainflue-monitoring-dev
```

### Staging
```bash
export ENVIRONMENT=staging
export KUBERNETES_NAMESPACE=ainflue-staging
export MONITORING_NAMESPACE=ainflue-monitoring-staging
```

### Production
```bash
export ENVIRONMENT=production
export KUBERNETES_NAMESPACE=ainflue
export MONITORING_NAMESPACE=ainflue-monitoring
```

## Advanced Configuration

### Secret Rotation

```bash
# Rotate secrets automatically
python3 kubernetes/scripts/production_secrets_manager.py --rotate
```

### Monitoring Stack Management

```bash
# Deploy only monitoring components
python3 kubernetes/scripts/monitoring_stack_deployment.py

# Check monitoring status
kubectl get all -n ainflue-monitoring
```

### Environment Variable Updates

```bash
# Update production configuration
python3 kubernetes/scripts/production_environment_manager.py
```

## Access Instructions

### Grafana Dashboard
```bash
kubectl port-forward -n ainflue-monitoring svc/grafana 3000:3000
# Open: http://localhost:3000
# Login: admin/admin123
```

### Prometheus Metrics
```bash
kubectl port-forward -n ainflue-monitoring svc/prometheus 9090:9090
# Open: http://localhost:9090
```

### Jaeger Tracing
```bash
kubectl port-forward -n ainflue-monitoring svc/jaeger-query 16686:16686
# Open: http://localhost:16686
```

## Security Considerations

### 1. Secret Management
- Use external secret management systems (AWS Secrets Manager, Azure Key Vault)
- Implement regular secret rotation (90-day cycle)
- Audit secret access and usage

### 2. Network Security
- Enable network policies for namespace isolation
- Use service mesh for mTLS between services
- Implement ingress-level security controls

### 3. Access Control
- Configure RBAC with principle of least privilege
- Use service accounts for application access
- Implement audit logging for all operations

### 4. Data Protection
- Enable encryption at rest for databases
- Use TLS 1.3 for all communications
- Implement data retention policies

## Compliance Features

### GDPR Compliance
- **Data Retention**: Configurable retention periods
- **Right to be Forgotten**: Automated data deletion
- **Consent Management**: User preference tracking
- **Audit Logging**: Complete access trail

### CCPA Compliance
- **Data Transparency**: User data disclosure
- **Opt-out Rights**: User preference management
- **Data Minimization**: Collect only necessary data
- **Breach Notification**: Automated alert systems

## Performance Tuning

### Database Optimization
- **Connection Pooling**: 25 base + 50 overflow connections
- **Query Optimization**: Automatic slow query detection
- **Read Replicas**: Load balancing for read operations
- **Caching**: Multi-layer caching strategy

### AI/ML Optimization
- **GPU Utilization**: 80% memory allocation
- **Batch Processing**: 32-item batches for efficiency
- **Model Caching**: 10GB model cache
- **Mixed Precision**: Enabled for performance

### Content Processing
- **Parallel Processing**: 8 AI workers
- **Queue Management**: Intelligent priority queuing
- **Format Support**: Optimized codecs for all formats
- **CDN Integration**: Global content delivery

## Troubleshooting

### Common Issues

1. **Secret Not Found**
   ```bash
   kubectl get secrets -n ainflue
   kubectl describe secret ainflue-secrets -n ainflue
   ```

2. **ConfigMap Issues**
   ```bash
   kubectl get configmaps -n ainflue
   kubectl describe configmap ainflue-production-config -n ainflue
   ```

3. **Monitoring Stack Issues**
   ```bash
   kubectl get deployments -n ainflue-monitoring
   kubectl logs -l app=prometheus -n ainflue-monitoring
   ```

### Log Aggregation
All logs are centralized in Elasticsearch and accessible through:
- Kibana dashboard for log analysis
- Grafana for metrics visualization
- Jaeger for distributed tracing

## Maintenance

### Regular Tasks
- **Weekly**: Review monitoring alerts and performance metrics
- **Monthly**: Update dashboards and add new metrics
- **Quarterly**: Rotate secrets and review access permissions
- **Annually**: Compliance audit and security review

### Backup Strategy
- **Database**: Automated backups every 6 hours
- **Configuration**: GitOps-managed configuration as code
- **Secrets**: Encrypted backup in external vault
- **Monitoring Data**: 30-day retention with archival

## Support

For technical support or questions about the production environment:
- **Technical Lead**: Fahed Mlaiel <mlaiel@live.de>
- **Documentation**: This file and inline code comments
- **Monitoring**: Real-time alerts through PagerDuty integration

---

**Author**: Fahed Mlaiel <mlaiel@live.de>  
**Last Updated**: 2025-08-31  
**Version**: 1.0.0