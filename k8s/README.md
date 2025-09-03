# 🚀 Ainflue Platform - Infrastructure & DevOps Documentation

## 📋 Overview

This document provides comprehensive documentation for the Ainflue platform's Kubernetes infrastructure and monitoring setup. All components are production-ready and follow enterprise-grade best practices.

## 🏗️ Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Ainflue Platform                         │
├─────────────────────────────────────────────────────────────┤
│  Ingress (NGINX) - SSL/TLS, Security Headers, CORS        │
├─────────────────────────────────────────────────────────────┤
│  API Gateway     │  AI Engine      │  Microservices       │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL      │  Redis Cache    │  Message Queues      │
├─────────────────────────────────────────────────────────────┤
│  Monitoring Stack (Prometheus, Grafana, ELK, Jaeger)      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | Kubernetes | Container orchestration |
| **Ingress** | NGINX Ingress Controller | Load balancing, SSL termination |
| **API Gateway** | FastAPI/Python | Main application entry point |
| **AI Engine** | Python/gRPC | Content analysis and AI processing |
| **Database** | PostgreSQL 15 | Primary data storage |
| **Cache** | Redis 7 | High-performance caching |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization |
| **Logging** | ELK Stack | Centralized log management |
| **Tracing** | Jaeger | Distributed tracing |
| **Alerting** | AlertManager | Incident management |

## 📁 Directory Structure

```
k8s/
├── namespace.yaml              # Namespace with resource quotas
├── deployments/               # Application deployments
│   ├── api-gateway.yaml      # Main API service
│   ├── ai-engine.yaml        # AI processing service
│   ├── database.yaml         # PostgreSQL database
│   └── redis.yaml            # Redis cache
├── services/                 # Kubernetes services
│   ├── api-gateway.yaml      # API Gateway service
│   ├── ai-engine.yaml        # AI Engine service
│   └── database.yaml         # Database services
├── configmaps/               # Application configuration
│   ├── api-gateway.yaml      # API Gateway config
│   ├── ai-engine.yaml        # AI Engine config
│   └── database.yaml         # Database config
├── secrets/                  # Encrypted secrets (gitignored)
│   ├── README.md             # Security documentation
│   ├── templates/            # Secret templates
│   │   ├── api-gateway.yaml.template
│   │   └── database.yaml.template
│   ├── api-gateway.yaml      # Actual secrets (not in git)
│   └── database.yaml         # Actual secrets (not in git)
├── hpa/                      # Auto-scaling configuration
│   ├── main-services.yaml    # HPA for core services
│   └── microservices.yaml   # HPA for additional services
├── ingress.yaml              # External access configuration
└── deploy.sh                 # Deployment automation script

monitoring/
├── prometheus-config.yaml    # Prometheus configuration
├── alerting-rules.yaml      # Alert rules and conditions
├── elasticsearch-config.yaml # ELK stack configuration
├── jaeger-config.yaml       # Distributed tracing setup
└── grafana-dashboards/      # Grafana dashboard definitions
    ├── platform-overview.json
    ├── business-metrics.json
    └── kubernetes-infrastructure.json
```

## 🔧 Configuration Details

### 1. Namespace Configuration (`k8s/namespace.yaml`)

- **Dedicated namespace**: `ainflue`
- **Resource quotas**: CPU (8-16 cores), Memory (16-32GB)
- **Pod limits**: 50 pods maximum
- **Security policies**: Network policies for traffic isolation

### 2. Deployments (`k8s/deployments/`)

#### API Gateway
- **Image**: `ainflue/api-gateway:1.0.0`
- **Replicas**: 3 (production)
- **Resources**: 200m-1000m CPU, 256Mi-1Gi memory
- **Health checks**: Liveness, readiness, startup probes
- **Auto-scaling**: 3-20 replicas based on CPU/memory

#### AI Engine
- **Image**: `ainflue/ai-engine:1.0.0`
- **Replicas**: 2 (production)
- **Resources**: 500m-2000m CPU, 1Gi-4Gi memory
- **Specialized**: GPU support, model storage volumes
- **Auto-scaling**: 2-10 replicas based on processing queue

#### Database (PostgreSQL)
- **Image**: `postgres:15-alpine`
- **Replicas**: 1 (stateful)
- **Storage**: Persistent volumes for data
- **Monitoring**: postgres_exporter for metrics
- **Configuration**: Production-tuned settings

#### Redis Cache
- **Image**: `redis:7-alpine`
- **Replicas**: 1 (stateful)
- **Storage**: Persistent volumes for data persistence
- **Monitoring**: redis_exporter for metrics

### 3. Services (`k8s/services/`)

All services include:
- **ClusterIP**: Internal cluster communication
- **Headless services**: For service discovery
- **Metrics endpoints**: Prometheus scraping
- **Health check ports**: Monitoring integration

### 4. ConfigMaps (`k8s/configmaps/`)

Comprehensive application configuration:
- **Environment variables**: All application settings
- **Feature flags**: A/B testing and gradual rollouts
- **Integration settings**: External service configurations
- **Performance tuning**: Optimized for production workloads

### 5. Secrets Management (`k8s/secrets/`)

**Security-first approach**:
- **Gitignored**: Secrets never committed to version control
- **Template-based**: Safe templates for reference
- **Base64 encoded**: Kubernetes-compatible format
- **Rotation ready**: Easy to update and rotate

Secret categories:
- Database credentials
- API keys (third-party services)
- JWT signing keys
- SSL certificates
- Payment processor keys

### 6. Auto-scaling (`k8s/hpa/`)

#### Horizontal Pod Autoscaling (HPA)
- **API Gateway**: 3-20 replicas, CPU 70%, memory 80%
- **AI Engine**: 2-10 replicas, CPU 75%, queue-based scaling
- **Custom metrics**: HTTP requests/sec, processing queue length

#### Vertical Pod Autoscaling (VPA)
- **Database**: Resource recommendations (update mode: off)
- **Redis**: Automatic resource adjustment (update mode: auto)

### 7. Ingress Configuration (`k8s/ingress.yaml`)

**Production-ready features**:
- **SSL/TLS**: Automatic certificate management
- **Security headers**: XSS, CSRF, content-type protection
- **CORS**: Configured for multi-domain access
- **Rate limiting**: DDoS protection
- **Load balancing**: Session affinity support

**Supported domains**:
- `ainflue.com` - Main application
- `api.ainflue.com` - API endpoints  
- `monitoring.ainflue.com` - Monitoring dashboards

## 📊 Monitoring & Observability

### 1. Prometheus Configuration (`monitoring/prometheus-config.yaml`)

**Comprehensive metrics collection**:
- **Application metrics**: Custom business metrics
- **Infrastructure metrics**: Node, pod, container metrics
- **Service discovery**: Kubernetes-native auto-discovery
- **Retention**: 30 days local, long-term storage via Thanos

**Scrape targets**:
- All Ainflue services (10-15s intervals)
- Kubernetes components (30s intervals)
- Infrastructure exporters (30s intervals)

### 2. Alerting Rules (`monitoring/alerting-rules.yaml`)

**Four categories of alerts**:

#### Infrastructure Alerts
- High CPU usage (>85%)
- High memory usage (>90%)
- Disk space critical (>90%)
- Node down conditions

#### Application Alerts
- High error rates (>5%)
- High response times (>2s)
- Service unavailability
- Processing queue backups

#### Database Alerts
- Connection pool exhaustion
- Slow query detection
- Replication lag
- Storage issues

#### Business Metrics Alerts
- Low content upload rates
- Revenue generation drops
- High copyright violation rates
- Collaboration success rate drops

### 3. ELK Stack (`monitoring/elasticsearch-config.yaml`)

**Centralized logging**:
- **Elasticsearch**: Log storage and indexing
- **Logstash**: Log processing and enrichment
- **Kibana**: Log visualization and analysis

**Log processing features**:
- JSON log parsing
- Kubernetes metadata enrichment
- Request tracing correlation
- Log level classification
- Performance monitoring

### 4. Distributed Tracing (`monitoring/jaeger-config.yaml`)

**Request flow tracking**:
- **End-to-end tracing**: Full request lifecycle
- **Performance analysis**: Bottleneck identification
- **Error correlation**: Failed request debugging
- **Sampling strategies**: Optimized for performance

**Components**:
- Jaeger All-in-One (development/staging)
- Jaeger Agent (production collection)
- Elasticsearch storage backend
- Sampling configuration per service

### 5. Grafana Dashboards (`monitoring/grafana-dashboards/`)

#### Platform Overview Dashboard
- API request rates and error rates
- AI processing queue metrics
- Database connection status
- Pod health and availability

#### Business Metrics Dashboard
- Content upload trends
- Revenue generation tracking
- Copyright violation detection
- User engagement metrics
- SEO performance scores

#### Infrastructure Dashboard
- Cluster resource utilization
- Node performance metrics
- Network and disk I/O
- Kubernetes object status

## 🚀 Deployment Guide

### Prerequisites

1. **Kubernetes cluster** (v1.24+)
2. **kubectl** configured and connected
3. **NGINX Ingress Controller** installed
4. **Cert-Manager** for SSL certificates (optional)
5. **Metrics Server** for HPA functionality

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Mlaiel/Ainflue.git
cd Ainflue

# Create secrets from templates
cp k8s/secrets/templates/api-gateway.yaml.template k8s/secrets/api-gateway.yaml
cp k8s/secrets/templates/database.yaml.template k8s/secrets/database.yaml

# Edit secrets with actual values
vim k8s/secrets/api-gateway.yaml
vim k8s/secrets/database.yaml

# Deploy the platform
./k8s/deploy.sh deploy

# Verify deployment
./k8s/deploy.sh verify
```

### Manual Deployment

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Deploy secrets and configmaps
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/configmaps/

# 3. Deploy services
kubectl apply -f k8s/services/

# 4. Deploy applications (in order)
kubectl apply -f k8s/deployments/database.yaml
kubectl apply -f k8s/deployments/redis.yaml
kubectl apply -f k8s/deployments/ai-engine.yaml
kubectl apply -f k8s/deployments/api-gateway.yaml

# 5. Deploy auto-scaling
kubectl apply -f k8s/hpa/

# 6. Deploy ingress
kubectl apply -f k8s/ingress.yaml

# 7. Deploy monitoring
kubectl apply -f monitoring/
```

## 🔒 Security Considerations

### Network Security
- **Network policies**: Traffic isolation between namespaces
- **TLS encryption**: All external communication encrypted
- **Service mesh ready**: Istio/Linkerd integration prepared

### Secret Management
- **Kubernetes secrets**: Base64 encoded sensitive data
- **GitOps friendly**: Secrets excluded from version control
- **Rotation support**: Easy credential updates
- **External integrations**: Vault, AWS Secrets Manager ready

### Container Security
- **Non-root containers**: All services run as non-privileged users
- **Read-only filesystems**: Immutable container environments
- **Security contexts**: Proper user/group assignments
- **Image scanning**: Vulnerability assessment in CI/CD

### Access Control
- **RBAC**: Role-based access control
- **Service accounts**: Principle of least privilege
- **Network policies**: Microsegmentation
- **Audit logging**: All API access logged

## 📈 Scalability Features

### Horizontal Scaling
- **Auto-scaling**: Based on CPU, memory, and custom metrics
- **Load balancing**: Intelligent request distribution
- **Circuit breakers**: Fault tolerance patterns
- **Graceful degradation**: Service resilience

### Performance Optimization
- **Resource limits**: Prevent resource exhaustion
- **Caching layers**: Multi-level caching strategy
- **Database optimization**: Connection pooling, query optimization
- **CDN integration**: Static asset optimization

### High Availability
- **Multi-replica deployments**: Fault tolerance
- **Pod disruption budgets**: Maintenance safety
- **Health checks**: Automatic failover
- **Backup strategies**: Data protection

## 🔧 Maintenance & Operations

### Regular Tasks
- **Security updates**: Container image updates
- **Secret rotation**: Credential refresh
- **Database maintenance**: Vacuum, reindex operations
- **Log rotation**: Storage management

### Monitoring & Alerting
- **24/7 monitoring**: Comprehensive observability
- **Alert escalation**: Multi-channel notifications
- **Performance trending**: Capacity planning
- **SLA tracking**: Service level monitoring

### Backup & Recovery
- **Database backups**: Automated daily backups
- **Configuration backups**: Infrastructure as Code
- **Disaster recovery**: Cross-region replication
- **Testing procedures**: Recovery validation

## 🆘 Troubleshooting

### Common Issues

#### Pod Startup Failures
```bash
# Check pod status
kubectl get pods -n ainflue

# View pod logs
kubectl logs <pod-name> -n ainflue

# Describe pod for events
kubectl describe pod <pod-name> -n ainflue
```

#### Service Discovery Issues
```bash
# Check service endpoints
kubectl get endpoints -n ainflue

# Test service connectivity
kubectl run debug --image=busybox -i --tty --rm -- nslookup <service-name>
```

#### Database Connection Problems
```bash
# Check database pod logs
kubectl logs ainflue-database-xxx -n ainflue

# Verify secrets
kubectl get secret ainflue-database-secrets -n ainflue -o yaml

# Test database connectivity
kubectl exec -it ainflue-api-gateway-xxx -n ainflue -- ping ainflue-database
```

#### Performance Issues
```bash
# Check resource usage
kubectl top pods -n ainflue
kubectl top nodes

# View HPA status
kubectl get hpa -n ainflue

# Check metrics
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
```

## 📞 Support & Contact

- **Technical Lead**: Fahed Mlaiel <mlaiel@live.de>
- **Documentation**: This repository's docs/ directory
- **Issues**: GitHub Issues for bug reports
- **Monitoring**: Grafana dashboards for real-time status

## 📄 License

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.