# 🔍 Service Discovery Module - Enterprise Microservices

**© FAHED MLAIEL 2024-2025 - PROPRIÉTÉ INTELLECTUELLE STRICTE**  
**⚠️ ARCHITECTURE CONFIDENTIELLE - NIVEAU ENTERPRISE UNIQUEMENT**

## 🎯 Overview

Enterprise-grade service discovery module providing intelligent service location, health monitoring, and load balancing across multiple service registries and discovery mechanisms.

## 🏗️ Architecture

```
service_discovery/
├── __init__.py                     # Module exports
├── index.py                        # Entry point
├── README.md                       # This documentation
├── consul_discovery_service.py     # Consul integration
├── kubernetes_discovery_service.py # Kubernetes service discovery
├── etcd_discovery_service.py       # etcd integration
├── dns_discovery_service.py        # DNS-based discovery
└── discovery_orchestrator.py       # Central orchestrator
```

## ✨ Features

### 🔍 Multi-Registry Support
- **Consul** - HashiCorp Consul integration
- **Kubernetes** - Native Kubernetes service discovery
- **etcd** - etcd v3 service registry
- **DNS** - DNS-based service discovery
- **Static** - Static service configuration

### 🎯 Intelligent Routing
- AI-powered service selection
- Multiple load balancing algorithms
- Health-aware routing
- Zone-aware load balancing

### 📊 Health Monitoring
- Real-time health checks
- Configurable health check intervals
- Circuit breaker integration
- Failure detection and recovery

### ⚖️ Load Balancing Algorithms
- Round Robin
- Weighted Round Robin
- Least Connections
- IP Hash
- Random
- AI-Optimized selection

## 🚀 Quick Start

### Basic Usage

```python
from microservices.service_discovery import create_discovery_service

# Create service discovery
discovery = create_discovery_service(
    backends=['consul', 'kubernetes'],
    default_algorithm='ai_optimized'
)

# Register a service
await discovery.register_service(
    name="api-service",
    instances=[
        {"host": "10.0.1.10", "port": 8080},
        {"host": "10.0.1.11", "port": 8080}
    ]
)

# Discover services
instances = await discovery.discover("api-service")
selected = await discovery.select_instance("api-service")
```

### Advanced Configuration

```python
from microservices.service_discovery import (
    DiscoveryConfig,
    ServiceDiscoveryOrchestrator,
    LoadBalancingAlgorithm
)

config = DiscoveryConfig(
    consul_host="localhost:8500",
    kubernetes_namespace="production",
    health_check_interval=30,
    enable_ai_optimization=True
)

discovery = ServiceDiscoveryOrchestrator(config)
```

## 📊 Performance Metrics

### Key Metrics Tracked
- **Discovery Latency** - Service lookup time
- **Health Check Success Rate** - Service health reliability
- **Load Balancing Efficiency** - Distribution effectiveness
- **Cache Hit Ratio** - Discovery cache performance

### Example Metrics
```python
metrics = await discovery.get_metrics()
print(f"Average discovery latency: {metrics['avg_latency_ms']}ms")
print(f"Services registered: {metrics['services_count']}")
print(f"Health checks performed: {metrics['health_checks_total']}")
```

## 🔧 Configuration

### Environment Variables
```bash
# Consul Configuration
CONSUL_HOST=localhost
CONSUL_PORT=8500
CONSUL_TOKEN=your-consul-token

# Kubernetes Configuration
KUBERNETES_NAMESPACE=default
KUBERNETES_SERVICE_ACCOUNT=discovery-service

# Health Check Configuration
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=5
MAX_RETRY_ATTEMPTS=3
```

### Service Definition
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: service-discovery-config
data:
  config.yaml: |
    discovery:
      backends:
        - consul
        - kubernetes
      cache_ttl: 300
      health_checks:
        enabled: true
        interval: 30
        timeout: 5
      load_balancing:
        algorithm: ai_optimized
        sticky_sessions: false
```

## 🛡️ Security

### Authentication
- Consul ACL tokens
- Kubernetes RBAC integration
- mTLS for inter-service communication

### Authorization
- Service-level access control
- Namespace isolation
- Role-based permissions

## 📈 Monitoring & Observability

### Health Checks
```python
# Configure health checks
health_config = {
    'path': '/health',
    'interval': 30,
    'timeout': 5,
    'retries': 3
}

await discovery.configure_health_checks("api-service", health_config)
```

### Distributed Tracing
- OpenTelemetry integration
- Jaeger trace collection
- Service dependency mapping

### Metrics Collection
- Prometheus metrics export
- Custom dashboards
- Real-time alerting

## 🔄 High Availability

### Failover Strategies
- Automatic backend failover
- Cross-region discovery
- Circuit breaker patterns

### Data Consistency
- Eventually consistent updates
- Conflict resolution
- Split-brain prevention

## 🌍 Multi-Cloud Support

### Cloud Provider Integration
- AWS ECS/EKS service discovery
- Azure Service Fabric
- Google Cloud Service Directory
- Multi-cloud federation

## 📚 API Reference

### Core Methods

#### `register_service(name, instances, metadata=None)`
Register a service with discovery system.

**Parameters:**
- `name` (str): Service name
- `instances` (List[Dict]): Service instances
- `metadata` (Dict): Optional service metadata

**Returns:**
- `Dict`: Registration result

#### `discover_service(name, filters=None)`
Discover service instances.

**Parameters:**
- `name` (str): Service name
- `filters` (Dict): Optional filters

**Returns:**
- `List[ServiceInstance]`: Available instances

#### `select_instance(name, algorithm=None, client_context=None)`
Select optimal service instance.

**Parameters:**
- `name` (str): Service name
- `algorithm` (LoadBalancingAlgorithm): Selection algorithm
- `client_context` (Dict): Client context for routing

**Returns:**
- `ServiceInstance`: Selected instance

## 🧪 Testing

### Unit Tests
```bash
# Run service discovery tests
python -m pytest microservices/service_discovery/tests/

# Run with coverage
python -m pytest --cov=microservices.service_discovery
```

### Integration Tests
```bash
# Test with live backends
python -m pytest microservices/service_discovery/tests/integration/
```

### Load Testing
```bash
# Performance testing
python -m pytest microservices/service_discovery/tests/performance/
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.12-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY microservices/service_discovery/ /app/service_discovery/
WORKDIR /app

CMD ["python", "-m", "service_discovery"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-discovery
spec:
  replicas: 3
  selector:
    matchLabels:
      app: service-discovery
  template:
    metadata:
      labels:
        app: service-discovery
    spec:
      containers:
      - name: service-discovery
        image: ainflue/service-discovery:latest
        ports:
        - containerPort: 8080
        env:
        - name: CONSUL_HOST
          value: "consul.default.svc.cluster.local"
        - name: KUBERNETES_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
```

## 📞 Support

### Team Contact
- **Lead Developer:** Fahed Mlaiel (mlaiel@live.de)
- **Team:** Service Discovery Team
- **Expertise:** Multi-cloud service discovery, load balancing, health monitoring

### Documentation
- [API Documentation](./docs/api.md)
- [Configuration Guide](./docs/configuration.md)
- [Troubleshooting](./docs/troubleshooting.md)

---

**Enterprise Service Discovery Module - Production Ready**  
*Part of Ainflue Microservices Architecture*