# 📋 Service Registry Module - Enterprise Microservices

**© FAHED MLAIEL 2024-2025 - PROPRIÉTÉ INTELLECTUELLE STRICTE**  
**⚠️ ARCHITECTURE CONFIDENTIELLE - NIVEAU ENTERPRISE UNIQUEMENT**

## 🎯 Overview

Advanced service registry module for enterprise microservices architecture. Provides centralized service registration, discovery, metadata management, and intelligent service topology with real-time synchronization and multi-region support.

## 🏗️ Architecture

```
service_registry/
├── __init__.py                      # Module exports
├── index.py                         # Entry point
├── README.md                        # This documentation
├── consul_registry.py              # Consul-based registry
├── kubernetes_registry.py          # Kubernetes service registry
├── etcd_registry.py                # etcd-based registry
├── redis_registry.py               # Redis-based registry
├── in_memory_registry.py           # In-memory registry (testing)
├── distributed_registry.py         # Multi-backend registry
├── service_metadata_manager.py     # Service metadata management
├── registry_synchronizer.py        # Cross-registry synchronization
├── service_discovery_cache.py      # Intelligent caching layer
├── registry_health_monitor.py      # Registry health monitoring
└── service_topology_analyzer.py    # Service dependency analysis
```

## ✨ Features

### 🗄️ Multi-Backend Support
- **Consul** - HashiCorp Consul service mesh
- **Kubernetes** - Native Kubernetes services
- **etcd** - Distributed key-value store
- **Redis** - High-performance caching
- **Hybrid** - Multi-backend federation

### 🌍 Advanced Capabilities
- Cross-region service federation
- Intelligent service caching
- Real-time synchronization
- Service dependency mapping
- Metadata enrichment

### 📊 Service Intelligence
- Service health aggregation
- Performance metrics integration
- Automated service discovery
- Topology visualization
- Impact analysis

### 🔒 Enterprise Security
- mTLS service authentication
- Service authorization policies
- Audit logging
- Encrypted communication

## 🚀 Quick Start

### Basic Registry Usage

```python
from microservices.service_registry import ServiceRegistry
from microservices.service_registry.backends import ConsulRegistry

# Create service registry with Consul backend
consul_backend = ConsulRegistry(
    host="localhost",
    port=8500,
    token="your-consul-token"
)

registry = ServiceRegistry(backend=consul_backend)

# Register a service
service_info = {
    "name": "user-api",
    "version": "v1.2.3",
    "protocol": "http",
    "host": "10.0.1.100",
    "port": 8080,
    "endpoints": ["/users", "/profiles"],
    "health_check": "/health",
    "tags": ["api", "users", "production"],
    "metadata": {
        "team": "user-team",
        "environment": "production",
        "deployment_id": "deploy-123"
    }
}

registration_result = await registry.register_service(service_info)
print(f"Service registered: {registration_result.service_id}")

# Discover services
services = await registry.discover_services(
    name="user-api",
    tags=["production"],
    healthy_only=True
)

for service in services:
    print(f"Service: {service.name} at {service.host}:{service.port}")
```

### Advanced Configuration

```python
from microservices.service_registry import (
    DistributedRegistry,
    ServiceMetadataManager,
    RegistrySynchronizer
)

# Create distributed registry with multiple backends
distributed_registry = DistributedRegistry(
    primary_backend=consul_backend,
    secondary_backends=[
        KubernetesRegistry(namespace="production"),
        EtcdRegistry(endpoints=["etcd1:2379", "etcd2:2379"])
    ],
    synchronization_strategy="eventual_consistency",
    consistency_level="quorum"
)

# Enhanced metadata management
metadata_manager = ServiceMetadataManager()

enhanced_service = await metadata_manager.enrich_service_metadata(
    service_info,
    enrichments=[
        "dependency_graph",
        "performance_metrics",
        "security_profile",
        "compliance_tags"
    ]
)

# Register with enhanced metadata
await distributed_registry.register_service(enhanced_service)
```

## 🗄️ Registry Backends

### Consul Registry
```python
from microservices.service_registry import ConsulRegistry

# Configure Consul registry
consul_registry = ConsulRegistry(
    host="consul.service.consul",
    port=8500,
    token="your-consul-acl-token",
    datacenter="dc1",
    tls_config={
        "verify": True,
        "cert_file": "/path/to/client.crt",
        "key_file": "/path/to/client.key",
        "ca_file": "/path/to/ca.crt"
    }
)

# Register with Consul-specific features
await consul_registry.register_service(
    service_info,
    consul_options={
        "enable_tag_override": True,
        "meta": {"version": "1.2.3", "region": "us-east-1"},
        "weights": {"passing": 10, "warning": 1}
    }
)
```

### Kubernetes Registry
```python
from microservices.service_registry import KubernetesRegistry

# Configure Kubernetes registry
k8s_registry = KubernetesRegistry(
    namespace="production",
    kubeconfig_path="/path/to/kubeconfig",
    service_account="service-registry",
    cluster_role="service-registry-reader"
)

# Register with Kubernetes annotations
await k8s_registry.register_service(
    service_info,
    k8s_options={
        "annotations": {
            "service.ainflue.com/version": "v1.2.3",
            "service.ainflue.com/team": "user-team",
            "service.ainflue.com/sla": "critical"
        },
        "labels": {
            "app": "user-api",
            "version": "v1.2.3",
            "tier": "backend"
        }
    }
)
```

### etcd Registry
```python
from microservices.service_registry import EtcdRegistry

# Configure etcd registry
etcd_registry = EtcdRegistry(
    endpoints=["etcd1:2379", "etcd2:2379", "etcd3:2379"],
    username="service-registry",
    password="your-etcd-password",
    tls_config={
        "cert_file": "/path/to/client.crt",
        "key_file": "/path/to/client.key",
        "ca_file": "/path/to/ca.crt"
    },
    key_prefix="/services/"
)

# Register with etcd TTL
await etcd_registry.register_service(
    service_info,
    etcd_options={
        "ttl": 30,  # 30 seconds TTL
        "refresh_interval": 10,  # Refresh every 10 seconds
        "lease_id": "lease-12345"
    }
)
```

## 🌍 Multi-Region & Federation

### Cross-Region Federation
```python
from microservices.service_registry import RegistryFederation

# Configure multi-region federation
federation = RegistryFederation([
    {
        "region": "us-east-1",
        "primary": True,
        "registry": ConsulRegistry(host="consul-us-east-1")
    },
    {
        "region": "us-west-2", 
        "primary": False,
        "registry": ConsulRegistry(host="consul-us-west-2")
    },
    {
        "region": "eu-west-1",
        "primary": False,
        "registry": ConsulRegistry(host="consul-eu-west-1")
    }
])

# Cross-region service discovery
global_services = await federation.discover_services_globally(
    name="user-api",
    prefer_local_region=True,
    fallback_regions=["us-west-2", "eu-west-1"]
)
```

### Service Mesh Integration
```python
# Integration with service mesh
mesh_config = {
    "istio": {
        "enabled": True,
        "namespace": "istio-system",
        "proxy_config": {
            "concurrency": 2,
            "memory_limit": "256Mi"
        }
    },
    "linkerd": {
        "enabled": True,
        "namespace": "linkerd",
        "proxy_injection": "enabled"
    }
}

await registry.configure_service_mesh_integration(mesh_config)

# Register service with mesh metadata
mesh_service = await registry.register_service_with_mesh(
    service_info,
    mesh_metadata={
        "traffic_policy": "round_robin",
        "circuit_breaker": True,
        "retry_policy": {"max_attempts": 3},
        "timeout": "30s"
    }
)
```

## 📊 Service Metadata Management

### Enhanced Metadata
```python
from microservices.service_registry import ServiceMetadataManager

metadata_manager = ServiceMetadataManager()

# Define metadata schema
metadata_schema = {
    "service_info": {
        "required": ["name", "version", "team"],
        "optional": ["description", "documentation_url"]
    },
    "technical_info": {
        "required": ["runtime", "framework"],
        "optional": ["language_version", "dependencies"]
    },
    "operational_info": {
        "required": ["environment", "deployment_strategy"],
        "optional": ["scaling_policy", "monitoring_dashboard"]
    },
    "security_info": {
        "required": ["security_tier", "data_classification"],
        "optional": ["compliance_tags", "encryption_required"]
    }
}

await metadata_manager.set_metadata_schema(metadata_schema)

# Validate and enrich service metadata
validated_service = await metadata_manager.validate_and_enrich(
    service_info,
    auto_enrich=True,
    validation_level="strict"
)
```

### Automated Discovery
```python
# Automated service discovery from deployment systems
discovery_config = {
    "kubernetes": {
        "enabled": True,
        "watch_namespaces": ["production", "staging"],
        "annotation_mapping": {
            "service.ainflue.com/version": "version",
            "service.ainflue.com/team": "team",
            "service.ainflue.com/sla": "sla_tier"
        }
    },
    "docker": {
        "enabled": True,
        "docker_socket": "/var/run/docker.sock",
        "label_mapping": {
            "com.ainflue.service.name": "name",
            "com.ainflue.service.version": "version"
        }
    }
}

await registry.configure_automated_discovery(discovery_config)

# Start automated discovery
await registry.start_automated_discovery()
```

## 🔄 Synchronization & Consistency

### Registry Synchronization
```python
from microservices.service_registry import RegistrySynchronizer

# Configure cross-registry synchronization
synchronizer = RegistrySynchronizer([
    consul_registry,
    k8s_registry,
    etcd_registry
])

# Define synchronization policies
sync_policies = {
    "conflict_resolution": "last_writer_wins",
    "consistency_model": "eventual_consistency",
    "sync_interval": 30,  # seconds
    "batch_size": 100,
    "retry_policy": {
        "max_attempts": 3,
        "backoff_factor": 2
    }
}

await synchronizer.configure_synchronization(sync_policies)

# Start synchronization
await synchronizer.start_sync()

# Monitor synchronization health
sync_status = await synchronizer.get_sync_status()
print(f"Sync lag: {sync_status.max_lag_seconds}s")
print(f"Conflicts detected: {sync_status.conflicts_count}")
```

### Conflict Resolution
```python
# Custom conflict resolution strategy
class TimestampBasedResolver:
    async def resolve_conflict(self, services):
        # Sort by last_updated timestamp
        latest_service = max(services, key=lambda s: s.last_updated)
        return latest_service

# Apply custom resolver
await synchronizer.set_conflict_resolver(TimestampBasedResolver())
```

## 🕸️ Service Topology Analysis

### Dependency Mapping
```python
from microservices.service_registry import ServiceTopologyAnalyzer

# Create topology analyzer
topology_analyzer = ServiceTopologyAnalyzer(registry)

# Discover service dependencies
dependency_graph = await topology_analyzer.build_dependency_graph(
    include_external_services=True,
    depth_limit=5,
    include_infrastructure=True
)

# Analyze critical path
critical_services = await topology_analyzer.identify_critical_services(
    dependency_graph,
    criticality_factors=["fan_out", "fan_in", "sla_tier"]
)

# Impact analysis
impact_analysis = await topology_analyzer.analyze_failure_impact(
    service="user-api",
    failure_scenarios=["total_failure", "degraded_performance"]
)
```

### Service Health Aggregation
```python
# Aggregate health across service topology
health_aggregator = await topology_analyzer.create_health_aggregator(
    dependency_graph,
    aggregation_strategy="weighted_average",
    weights={
        "direct_dependencies": 0.6,
        "transitive_dependencies": 0.3,
        "infrastructure": 0.1
    }
)

# Get aggregated health score
aggregated_health = await health_aggregator.get_service_health(
    service="user-api",
    include_predictions=True
)
```

## 🔧 Configuration

### Environment Variables
```bash
# Service Registry Configuration
SERVICE_REGISTRY_BACKEND=consul
SERVICE_REGISTRY_HOST=localhost
SERVICE_REGISTRY_PORT=8500
SERVICE_REGISTRY_TOKEN=your-token

# Synchronization Settings
SERVICE_REGISTRY_SYNC_ENABLED=true
SERVICE_REGISTRY_SYNC_INTERVAL=30
SERVICE_REGISTRY_CONSISTENCY_LEVEL=eventual

# Caching Configuration
SERVICE_REGISTRY_CACHE_ENABLED=true
SERVICE_REGISTRY_CACHE_TTL=300
SERVICE_REGISTRY_CACHE_SIZE=10000
```

### YAML Configuration
```yaml
service_registry:
  backends:
    consul:
      host: consul.service.consul
      port: 8500
      datacenter: dc1
      token: "${CONSUL_TOKEN}"
      tls:
        enabled: true
        verify: true
        cert_file: /certs/client.crt
        key_file: /certs/client.key
    
    kubernetes:
      namespace: production
      service_account: service-registry
      cluster_role: service-registry-reader
    
    etcd:
      endpoints:
        - etcd1:2379
        - etcd2:2379
        - etcd3:2379
      username: service-registry
      password: "${ETCD_PASSWORD}"
      key_prefix: /services/
  
  federation:
    enabled: true
    regions:
      - name: us-east-1
        primary: true
        weight: 1.0
      - name: us-west-2
        primary: false
        weight: 0.8
      - name: eu-west-1
        primary: false
        weight: 0.7
  
  synchronization:
    enabled: true
    interval: 30
    batch_size: 100
    conflict_resolution: timestamp_based
    consistency_model: eventual_consistency
  
  caching:
    enabled: true
    ttl: 300
    max_size: 10000
    invalidation_strategy: ttl_based
  
  metadata:
    schema_validation: strict
    auto_enrichment: true
    required_fields:
      - name
      - version
      - team
      - environment
```

## 📈 Monitoring & Observability

### Prometheus Metrics
```python
# Exported metrics
service_registry_services_total{backend="consul", region="us-east-1"}
service_registry_registrations_total{backend="consul", status="success"}
service_registry_discoveries_total{service="user-api", result="found"}
service_registry_sync_lag_seconds{source="consul", target="kubernetes"}
service_registry_cache_hit_ratio{backend="consul"}
service_registry_health_check_duration_seconds{service="user-api"}
service_topology_dependency_count{service="user-api", depth="1"}
service_registry_conflicts_total{resolution="timestamp_based"}
```

### Health Dashboard
```python
# Get registry dashboard data
dashboard = await registry.get_dashboard_data()

print(f"Total services: {dashboard['total_services']}")
print(f"Healthy services: {dashboard['healthy_services']}")
print(f"Registry backends: {dashboard['active_backends']}")
print(f"Sync status: {dashboard['sync_status']}")
```

## 🧪 Testing

### Unit Tests
```bash
# Run service registry tests
python -m pytest microservices/service_registry/tests/

# Test specific backend
python -m pytest microservices/service_registry/tests/test_consul_registry.py -v
```

### Integration Tests
```bash
# Test with real backends
python -m pytest microservices/service_registry/tests/integration/

# Test cross-registry synchronization
python -m pytest microservices/service_registry/tests/test_synchronization.py
```

### Performance Tests
```bash
# Test registry performance
python -m pytest microservices/service_registry/tests/performance/test_registry_load.py
```

## 🚀 Deployment

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-registry
spec:
  replicas: 3
  selector:
    matchLabels:
      app: service-registry
  template:
    metadata:
      labels:
        app: service-registry
    spec:
      serviceAccountName: service-registry
      containers:
      - name: registry
        image: ainflue/service-registry:latest
        ports:
        - containerPort: 8080
        env:
        - name: SERVICE_REGISTRY_BACKEND
          value: "kubernetes"
        - name: SERVICE_REGISTRY_SYNC_ENABLED
          value: "true"
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service Account (Kubernetes)
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: service-registry
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: service-registry-reader
rules:
- apiGroups: [""]
  resources: ["services", "endpoints"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: service-registry-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: service-registry-reader
subjects:
- kind: ServiceAccount
  name: service-registry
  namespace: default
```

## 📞 Support

### Team Contact
- **Lead Developer:** Fahed Mlaiel (mlaiel@live.de)
- **Team:** Service Registry Team
- **Expertise:** Service discovery, distributed systems, topology analysis

### Documentation
- [Backend Comparison](./docs/backends.md)
- [Federation Guide](./docs/federation.md)
- [Topology Analysis](./docs/topology.md)
- [Troubleshooting](./docs/troubleshooting.md)

---

**Enterprise Service Registry Module - Production Ready**  
*Part of Ainflue Microservices Architecture*