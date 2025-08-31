# 🚀 Ainflue Microservices Infrastructure

## Infrastructure Microservices Industrielle
### ☸️ Kubernetes Production Multi-Région

Production-ready Kubernetes infrastructure for Ainflue's 9 core microservices with multi-region deployment capabilities.

## 🏗️ Architecture Overview

### Core Microservices (9 Services)

```yaml
┌─────────────────────────────────────────────────────────────────────┐
│                    API Gateway (Kong/Istio)                         │
├─────────────────────────────────────────────────────────────────────┤
│  user-service   │  content-service  │  ai-service   │ protection-service│
├─────────────────────────────────────────────────────────────────────┤
│ collaboration-  │  payment-service  │ notification- │ analytics-service │
│ service         │                   │ service       │                   │
└─────────────────────────────────────────────────────────────────────┘
```

1. **api-gateway**: Kong/Istio service mesh - Entry point and routing
2. **user-service**: Authentication + profiles - User management and auth
3. **content-service**: Upload + storage - Content management and storage
4. **ai-service**: ML models + processing - AI/ML processing pipeline
5. **protection-service**: Fingerprinting + monitoring - Content protection
6. **collaboration-service**: Matching + projects - Artist collaboration
7. **payment-service**: Transactions + billing - Payment processing
8. **notification-service**: Alerts + communications - Notification system
9. **analytics-service**: Metrics + reporting - Analytics and reporting

## 🌍 Multi-Region Deployment

### Supported Regions

- **us-east-1** (Primary): US East (N. Virginia)
- **us-west-2** (Secondary): US West (Oregon)  
- **eu-west-1** (Secondary): EU West (Ireland)
- **ap-southeast-1** (Secondary): AP Southeast (Singapore)

### Region Configuration

Each region includes:
- Auto-scaling Kubernetes clusters
- Regional databases (PostgreSQL, Redis, MongoDB)
- Regional S3 storage buckets
- Regional CDN endpoints
- Cross-region replication and failover

## 📁 Directory Structure

```
kubernetes/
├── microservices/                 # Core microservices
│   ├── api-gateway/              # Kong/Istio API Gateway
│   ├── user-service/             # Authentication service
│   ├── content-service/          # Content management
│   ├── ai-service/               # AI/ML processing
│   ├── protection-service/       # Content protection
│   ├── collaboration-service/    # Artist collaboration
│   ├── payment-service/          # Payment processing
│   ├── notification-service/     # Notification system
│   ├── analytics-service/        # Analytics and reporting
│   ├── namespace.yaml            # Production namespace
│   ├── istio-config.yaml         # Istio service mesh
│   ├── monitoring.yaml           # Prometheus monitoring
│   └── security.yaml             # RBAC and security
├── multi-region/                 # Multi-region configs
│   ├── us-east-1/               # Primary region
│   ├── us-west-2/               # Secondary region
│   ├── eu-west-1/               # European region
│   ├── ap-southeast-1/          # Asia-Pacific region
│   └── global-lb-config.yaml    # Global load balancer
└── scripts/                      # Deployment scripts
    ├── generate_microservices.py # Generate service manifests
    ├── generate_multi_region.py  # Generate regional configs
    └── deploy_production.py      # Production deployment
```

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (1.21+)
- kubectl configured
- Istio service mesh installed
- Helm 3.x
- Access to container registry

### 1. Deploy Infrastructure

```bash
# Create production namespace and basic infrastructure
kubectl apply -f kubernetes/microservices/namespace.yaml
kubectl apply -f kubernetes/microservices/security.yaml
```

### 2. Deploy Core Services

```bash
# Deploy all microservices
python scripts/deploy_production.py --region us-east-1

# Or deploy specific service
kubectl apply -f kubernetes/microservices/api-gateway/
```

### 3. Configure Service Mesh

```bash
# Apply Istio configuration
kubectl apply -f kubernetes/microservices/istio-config.yaml
```

### 4. Setup Monitoring

```bash
# Deploy Prometheus monitoring
kubectl apply -f kubernetes/microservices/monitoring.yaml
```

## 🔧 Configuration

### Environment Variables

Each microservice supports the following environment variables:

- `ENVIRONMENT`: production/staging/development
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR
- `ENABLE_METRICS`: true/false
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string

### Service-Specific Configuration

Each service has its own ConfigMap with service-specific settings:

```yaml
# Example: user-service-config
auth:
  jwt_algorithm: "HS256"
  jwt_expiration: 3600
  password_hash_rounds: 12
  
security:
  rate_limiting:
    login_attempts: 5
    window_minutes: 15
```

## 📊 Monitoring & Observability

### Prometheus Metrics

All services expose Prometheus metrics on `/metrics` endpoint:

- Request rate and latency
- Error rates by endpoint
- Resource utilization
- Business metrics

### Alerting Rules

Pre-configured alerts for:
- High error rates (>10%)
- High response times (>1s 95th percentile)
- Pod not ready
- High CPU/memory usage
- Service downtime

### Grafana Dashboards

- Service overview dashboard
- Resource utilization dashboard
- Business metrics dashboard
- Error tracking dashboard

## 🔒 Security

### RBAC Configuration

- Service accounts for each microservice
- Role-based access control
- Principle of least privilege

### Network Policies

- Default deny-all policy
- Selective ingress/egress rules
- Service-to-service communication control

### Secret Management

- Kubernetes secrets for sensitive data
- Secret rotation capabilities
- External secret management integration

## 🔄 Auto-Scaling

### Horizontal Pod Autoscaler (HPA)

All services configured with HPA:
- CPU utilization target: 70%
- Memory utilization target: 80%
- Custom metrics support

### Cluster Autoscaler

- Automatic node scaling
- Multi-AZ deployment
- Cost optimization with spot instances

## 🚨 Disaster Recovery

### Backup Strategy

- Automated database backups
- Cross-region replication
- Point-in-time recovery

### Failover Procedures

- Automatic service failover
- Regional traffic routing
- Data consistency checks

## 📈 Performance Tuning

### Resource Optimization

Each service optimized for:
- Memory usage patterns
- CPU requirements
- I/O operations
- Network traffic

### Caching Strategy

- Redis for session management
- Application-level caching
- CDN for static content

## 🔧 Deployment Scripts

### Generate Manifests

```bash
# Generate all microservice manifests
python scripts/generate_microservices.py

# Generate multi-region configurations
python scripts/generate_multi_region.py
```

### Production Deployment

```bash
# Full production deployment
python scripts/deploy_production.py --region us-east-1

# Dry run deployment
python scripts/deploy_production.py --region us-east-1 --dry-run

# Deploy specific phase
python scripts/deploy_production.py --phase microservices
```

## 🐛 Troubleshooting

### Common Issues

1. **Pod not starting**: Check resource limits and node capacity
2. **Service discovery**: Verify DNS resolution and service names
3. **Database connections**: Check connection strings and credentials
4. **Ingress issues**: Verify ingress controller and DNS configuration

### Debug Commands

```bash
# Check pod status
kubectl get pods -n production

# View pod logs
kubectl logs -f <pod-name> -n production

# Describe resources
kubectl describe deployment <service-name> -n production

# Check service endpoints
kubectl get endpoints -n production
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Istio Service Mesh](https://istio.io/latest/docs/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Kong API Gateway](https://docs.konghq.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

Copyright © 2024 Ainflue. All rights reserved.

---

**Built with ❤️ for enterprise-grade microservices deployment**