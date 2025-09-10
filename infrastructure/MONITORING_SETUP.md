# 📊 Ainflue Infrastructure Monitoring Setup

**Enterprise Monitoring Configuration and Alerting Guide**

## 📋 Overview

This guide provides comprehensive monitoring setup procedures for the Ainflue Infrastructure module, covering observability stack deployment, metrics collection, alerting configuration, and dashboard creation.

## 🎯 Monitoring Objectives

### Primary Goals
- **Comprehensive Observability**: Full visibility into infrastructure health
- **Proactive Alerting**: Early detection of issues and anomalies
- **Performance Tracking**: Continuous performance monitoring
- **Cost Visibility**: Real-time cost tracking and optimization
- **Security Monitoring**: Security event detection and response
- **Business Metrics**: Creator economy specific metrics

### Key Metrics Categories
- **System Metrics**: CPU, Memory, Disk, Network
- **Application Metrics**: Response time, Error rate, Throughput
- **Business Metrics**: Active users, Content uploads, Revenue
- **Security Metrics**: Authentication events, Access violations
- **Cost Metrics**: Resource costs, Budget utilization

## 🏗️ Monitoring Architecture

### Observability Stack Components
```
Data Collection Layer
├── Prometheus (Metrics collection)
├── Jaeger (Distributed tracing)
├── Fluentd (Log collection)
└── Custom Exporters (Business metrics)

Storage Layer
├── Prometheus TSDB (Time-series data)
├── Elasticsearch (Log storage)
├── Jaeger Storage (Trace storage)
└── InfluxDB (High-frequency metrics)

Visualization Layer
├── Grafana (Dashboards)
├── Kibana (Log analysis)
├── Jaeger UI (Trace visualization)
└── Custom UIs (Business dashboards)

Alerting Layer
├── Alertmanager (Alert routing)
├── PagerDuty (Incident management)
├── Slack/Teams (Team notifications)
└── Email (Backup notifications)
```

## 🚀 Prometheus Setup

### 1. Prometheus Installation

#### Helm Chart Deployment
```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=100Gi \
  --set grafana.adminPassword=ainflue-monitoring \
  --set alertmanager.alertmanagerSpec.storage.volumeClaimTemplate.spec.resources.requests.storage=10Gi \
  --values infrastructure/monitoring/prometheus-values.yaml
```

#### Custom Prometheus Configuration
```yaml
# infrastructure/monitoring/prometheus-values.yaml
prometheus:
  prometheusSpec:
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    retention: 30d
    retentionSize: 90GB
    resources:
      requests:
        memory: 2Gi
        cpu: 1000m
      limits:
        memory: 4Gi
        cpu: 2000m
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: fast-ssd
          resources:
            requests:
              storage: 100Gi
    additionalScrapeConfigs:
      - job_name: 'infrastructure-orchestrator'
        static_configs:
          - targets: ['infrastructure-orchestrator:8080']
        metrics_path: /metrics
        scrape_interval: 30s
      - job_name: 'multi-cloud-manager'
        static_configs:
          - targets: ['multi-cloud-manager:8080']
        metrics_path: /metrics
        scrape_interval: 30s
      - job_name: 'cost-manager'
        static_configs:
          - targets: ['cost-manager:8080']
        metrics_path: /metrics
        scrape_interval: 60s
```

### 2. Custom Metrics Exporters

#### Infrastructure Orchestrator Metrics
```python
# infrastructure/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
deployment_total = Counter('ainflue_deployments_total', 'Total deployments', ['status', 'cloud'])
deployment_duration = Histogram('ainflue_deployment_duration_seconds', 'Deployment duration')
active_resources = Gauge('ainflue_active_resources', 'Active resources', ['cloud', 'type'])
cost_current = Gauge('ainflue_cost_current_usd', 'Current cost in USD', ['cloud', 'service'])

# Custom metrics collection
class InfrastructureMetrics:
    def collect_deployment_metrics(self):
        # Collect deployment statistics
        pass
    
    def collect_resource_metrics(self):
        # Collect resource utilization
        pass
    
    def collect_cost_metrics(self):
        # Collect cost information
        pass

# Start metrics server
start_http_server(8080)
```

#### Multi-Cloud Metrics Exporter
```bash
# Create custom exporter for cloud provider metrics
kubectl apply -f infrastructure/monitoring/cloud-exporter.yaml
```

```yaml
# infrastructure/monitoring/cloud-exporter.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloud-metrics-exporter
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cloud-metrics-exporter
  template:
    metadata:
      labels:
        app: cloud-metrics-exporter
    spec:
      containers:
      - name: exporter
        image: ainflue/cloud-metrics-exporter:latest
        ports:
        - containerPort: 9090
        env:
        - name: AWS_REGION
          value: "us-east-1"
        - name: GCP_PROJECT_ID
          value: "ainflue-infrastructure"
        - name: AZURE_SUBSCRIPTION_ID
          value: "subscription-id"
        resources:
          requests:
            memory: 128Mi
            cpu: 100m
          limits:
            memory: 256Mi
            cpu: 200m
```

### 3. Service Monitors

#### Infrastructure Service Monitor
```yaml
# infrastructure/monitoring/servicemonitor-infrastructure.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: infrastructure-services
  namespace: monitoring
spec:
  selector:
    matchLabels:
      monitoring: enabled
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
    honorLabels: true
  namespaceSelector:
    matchNames:
    - ainflue-system
```

#### Database Monitor
```yaml
# infrastructure/monitoring/servicemonitor-database.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: database-services
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app.kubernetes.io/component: database
  endpoints:
  - port: metrics
    interval: 60s
    path: /metrics
```

## 📈 Grafana Dashboard Setup

### 1. Grafana Configuration

#### Access Grafana
```bash
# Port forward to access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring

# Login credentials
Username: admin
Password: ainflue-monitoring  # Set during installation

# Or get password from secret
kubectl get secret prometheus-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode
```

#### Configure Data Sources
```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://prometheus-kube-prometheus-prometheus:9090",
  "access": "proxy",
  "isDefault": true
}
```

### 2. Infrastructure Dashboards

#### Main Infrastructure Dashboard
```json
{
  "dashboard": {
    "title": "Ainflue Infrastructure Overview",
    "panels": [
      {
        "title": "Resource Utilization",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(ainflue_active_resources) by (cloud)",
            "legendFormat": "{{cloud}}"
          }
        ]
      },
      {
        "title": "Deployment Success Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(ainflue_deployments_total{status=\"success\"}[5m]) / rate(ainflue_deployments_total[5m]) * 100"
          }
        ]
      },
      {
        "title": "Current Costs by Cloud",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum(ainflue_cost_current_usd) by (cloud)",
            "legendFormat": "{{cloud}}"
          }
        ]
      }
    ]
  }
}
```

#### Performance Dashboard
```json
{
  "dashboard": {
    "title": "Infrastructure Performance",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error Rate %"
          }
        ]
      }
    ]
  }
}
```

#### Cost Monitoring Dashboard
```json
{
  "dashboard": {
    "title": "Cost Monitoring",
    "panels": [
      {
        "title": "Daily Cost Trend",
        "type": "graph",
        "targets": [
          {
            "expr": "increase(ainflue_cost_current_usd[1d])",
            "legendFormat": "Daily Cost"
          }
        ]
      },
      {
        "title": "Cost by Service",
        "type": "table",
        "targets": [
          {
            "expr": "sum(ainflue_cost_current_usd) by (service)",
            "format": "table"
          }
        ]
      }
    ]
  }
}
```

### 3. Import Dashboards
```bash
# Import dashboard via API
curl -X POST \
  http://admin:ainflue-monitoring@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @infrastructure/monitoring/dashboards/infrastructure-overview.json

# Import all dashboards
for dashboard in infrastructure/monitoring/dashboards/*.json; do
  curl -X POST \
    http://admin:ainflue-monitoring@localhost:3000/api/dashboards/db \
    -H 'Content-Type: application/json' \
    -d @$dashboard
done
```

## 🚨 Alerting Configuration

### 1. Alertmanager Setup

#### Alertmanager Configuration
```yaml
# infrastructure/monitoring/alertmanager-config.yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default'
  routes:
  - match:
      severity: critical
    receiver: 'pagerduty-critical'
  - match:
      severity: warning
    receiver: 'slack-warnings'

receivers:
- name: 'default'
  slack_configs:
  - channel: '#infrastructure-alerts'
    title: 'Ainflue Infrastructure Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

- name: 'pagerduty-critical'
  pagerduty_configs:
  - routing_key: 'R026XXXXXXXXXXXXXXXXXXXXXXXXX'
    description: '{{ .GroupLabels.alertname }}: {{ .GroupLabels.instance }}'

- name: 'slack-warnings'
  slack_configs:
  - channel: '#infrastructure-warnings'
    title: 'Infrastructure Warning'
    text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

### 2. Prometheus Alert Rules

#### Infrastructure Alert Rules
```yaml
# infrastructure/monitoring/alert-rules-infrastructure.yaml
groups:
- name: infrastructure.rules
  rules:
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      description: "CPU usage is above 80% for more than 5 minutes"

  - alert: HighMemoryUsage
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage detected"
      description: "Memory usage is above 85% for more than 5 minutes"

  - alert: DiskSpaceLow
    expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Disk space critically low"
      description: "Disk usage is above 90% for more than 5 minutes"

  - alert: PodCrashLooping
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Pod is crash looping"
      description: "Pod {{ $labels.pod }} is restarting frequently"

  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
      description: "Service {{ $labels.job }} is down"
```

#### Application Alert Rules
```yaml
# infrastructure/monitoring/alert-rules-application.yaml
groups:
- name: application.rules
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100 > 5
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is above 5% for more than 5 minutes"

  - alert: SlowAPIResponse
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Slow API response time"
      description: "95th percentile response time is above 1 second"

  - alert: DeploymentFailed
    expr: increase(ainflue_deployments_total{status="failed"}[5m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Deployment failed"
      description: "A deployment has failed in the last 5 minutes"
```

#### Cost Alert Rules
```yaml
# infrastructure/monitoring/alert-rules-cost.yaml
groups:
- name: cost.rules
  rules:
  - alert: BudgetExceeded
    expr: ainflue_cost_current_usd > ainflue_budget_limit_usd
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Budget exceeded"
      description: "Current costs have exceeded the budget limit"

  - alert: CostAnomalyDetected
    expr: increase(ainflue_cost_current_usd[1h]) > 1.5 * avg_over_time(increase(ainflue_cost_current_usd[1h])[7d:1h])
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Cost anomaly detected"
      description: "Cost increase is significantly higher than average"
```

### 3. Apply Alert Rules
```bash
# Apply alert rules
kubectl apply -f infrastructure/monitoring/alert-rules-infrastructure.yaml
kubectl apply -f infrastructure/monitoring/alert-rules-application.yaml
kubectl apply -f infrastructure/monitoring/alert-rules-cost.yaml

# Verify alert rules
kubectl get prometheusrules -n monitoring

# Test alert rules
kubectl exec -n monitoring prometheus-kube-prometheus-prometheus-0 \
  -- promtool query instant 'ALERTS{alertstate="firing"}'
```

## 📊 Log Management

### 1. ELK Stack Setup

#### Elasticsearch Installation
```bash
# Add Elastic Helm repository
helm repo add elastic https://helm.elastic.co
helm repo update

# Install Elasticsearch
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace \
  --set replicas=3 \
  --set volumeClaimTemplate.resources.requests.storage=100Gi \
  --set resources.requests.memory=2Gi \
  --set resources.limits.memory=4Gi
```

#### Logstash Installation
```bash
# Install Logstash
helm install logstash elastic/logstash \
  --namespace logging \
  --set resources.requests.memory=1Gi \
  --set resources.limits.memory=2Gi \
  --values infrastructure/monitoring/logstash-values.yaml
```

#### Kibana Installation
```bash
# Install Kibana
helm install kibana elastic/kibana \
  --namespace logging \
  --set service.type=LoadBalancer
```

### 2. Fluentd Configuration

#### Fluentd DaemonSet
```yaml
# infrastructure/monitoring/fluentd-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: logging
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      format json
      time_format %Y-%m-%dT%H:%M:%S.%NZ
    </source>

    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>

    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch-master.logging.svc.cluster.local
      port 9200
      index_name fluentd
      type_name fluentd
    </match>
```

### 3. Log Analysis Queries

#### Common Log Queries
```bash
# Search for errors in infrastructure logs
{
  "query": {
    "bool": {
      "must": [
        {"match": {"kubernetes.namespace_name": "ainflue-system"}},
        {"match": {"level": "ERROR"}}
      ],
      "filter": {
        "range": {
          "@timestamp": {
            "gte": "now-1h"
          }
        }
      }
    }
  }
}

# Search for specific deployment events
{
  "query": {
    "bool": {
      "must": [
        {"match": {"kubernetes.container_name": "infrastructure-orchestrator"}},
        {"match": {"message": "deployment"}}
      ]
    }
  }
}
```

## 🔍 Distributed Tracing

### 1. Jaeger Setup

#### Jaeger Installation
```bash
# Install Jaeger Operator
kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.25.0/jaeger-operator.yaml

# Create Jaeger instance
kubectl apply -f infrastructure/monitoring/jaeger-instance.yaml
```

#### Jaeger Configuration
```yaml
# infrastructure/monitoring/jaeger-instance.yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger-infrastructure
  namespace: monitoring
spec:
  strategy: production
  storage:
    type: elasticsearch
    elasticsearch:
      nodeCount: 3
      resources:
        requests:
          memory: 2Gi
        limits:
          memory: 4Gi
      redundancyPolicy: SingleRedundancy
  query:
    resources:
      requests:
        memory: 512Mi
      limits:
        memory: 1Gi
  collector:
    resources:
      requests:
        memory: 512Mi
      limits:
        memory: 1Gi
```

### 2. Application Instrumentation

#### Python Tracing Setup
```python
# infrastructure/monitoring/tracing.py
from jaeger_client import Config
from opentracing.ext import tags
import opentracing

def init_tracer(service_name):
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service_name,
    )
    return config.initialize_tracer()

# Use in infrastructure orchestrator
tracer = init_tracer('infrastructure-orchestrator')

def deploy_resource(resource_id):
    with tracer.start_span('deploy_resource') as span:
        span.set_tag(tags.COMPONENT, 'infrastructure')
        span.set_tag('resource.id', resource_id)
        
        # Deployment logic here
        
        span.set_tag(tags.HTTP_STATUS_CODE, 200)
```

## 📱 Custom Monitoring Dashboards

### 1. Business Metrics Dashboard

#### Creator Economy Metrics
```json
{
  "dashboard": {
    "title": "Creator Economy Metrics",
    "panels": [
      {
        "title": "Active Creators",
        "type": "stat",
        "targets": [
          {
            "expr": "ainflue_active_creators_total"
          }
        ]
      },
      {
        "title": "Content Uploads",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ainflue_content_uploads_total[5m])",
            "legendFormat": "Uploads per second"
          }
        ]
      },
      {
        "title": "Revenue Tracking",
        "type": "graph",
        "targets": [
          {
            "expr": "increase(ainflue_revenue_usd[1h])",
            "legendFormat": "Hourly Revenue"
          }
        ]
      }
    ]
  }
}
```

### 2. SLA Monitoring Dashboard

#### SLA Metrics
```json
{
  "dashboard": {
    "title": "SLA Monitoring",
    "panels": [
      {
        "title": "Uptime SLA",
        "type": "stat",
        "targets": [
          {
            "expr": "(1 - (rate(up{job=\"infrastructure-orchestrator\"}[30d]) == 0)) * 100"
          }
        ]
      },
      {
        "title": "Performance SLA",
        "type": "stat",
        "targets": [
          {
            "expr": "(histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[30d])) < 0.1) * 100"
          }
        ]
      }
    ]
  }
}
```

## 🔧 Monitoring Automation

### 1. Automated Alert Testing

#### Alert Testing Script
```bash
#!/bin/bash
# infrastructure/monitoring/test-alerts.sh

# Test high CPU alert
kubectl run cpu-stress --image=progrium/stress \
  --rm -it --restart=Never \
  -- --cpu 2 --timeout 300s

# Test memory alert
kubectl run memory-stress --image=progrium/stress \
  --rm -it --restart=Never \
  -- --vm 1 --vm-bytes 2G --timeout 300s

# Test service down alert
kubectl scale deployment infrastructure-orchestrator --replicas=0
sleep 60
kubectl scale deployment infrastructure-orchestrator --replicas=3
```

### 2. Dashboard Backup and Restore

#### Backup Dashboards
```bash
# Export all dashboards
mkdir -p infrastructure/monitoring/dashboard-backups
for uid in $(curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  http://grafana.monitoring.svc.cluster.local/api/search | jq -r '.[].uid'); do
  curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
    http://grafana.monitoring.svc.cluster.local/api/dashboards/uid/$uid | \
    jq '.dashboard' > infrastructure/monitoring/dashboard-backups/$uid.json
done
```

#### Restore Dashboards
```bash
# Restore all dashboards
for dashboard in infrastructure/monitoring/dashboard-backups/*.json; do
  curl -X POST \
    -H "Authorization: Bearer $GRAFANA_TOKEN" \
    -H "Content-Type: application/json" \
    -d @$dashboard \
    http://grafana.monitoring.svc.cluster.local/api/dashboards/db
done
```

## 📊 Performance Monitoring

### 1. APM Integration

#### Application Performance Monitoring
```python
# infrastructure/monitoring/apm.py
from elastic_apm import Client
from elastic_apm.contrib.flask import ElasticAPM

# Initialize APM client
apm_client = Client(
    service_name='infrastructure-orchestrator',
    server_url='http://apm-server.monitoring.svc.cluster.local:8200',
    environment='production'
)

# Flask integration
app = Flask(__name__)
apm = ElasticAPM(app, client=apm_client)

@app.route('/deploy')
@apm.capture_span('deploy_resource')
def deploy():
    # Deployment logic
    pass
```

### 2. Custom Performance Metrics

#### Infrastructure Performance Metrics
```python
# Custom performance collector
class PerformanceCollector:
    def collect_deployment_metrics(self):
        # Collect deployment time metrics
        pass
    
    def collect_scaling_metrics(self):
        # Collect auto-scaling metrics
        pass
    
    def collect_cost_metrics(self):
        # Collect cost efficiency metrics
        pass
```

## 🚨 Incident Response

### 1. Runbook Integration

#### Automated Runbooks
```yaml
# infrastructure/monitoring/runbook-cpu-high.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: runbook-cpu-high
  namespace: monitoring
data:
  runbook.md: |
    # High CPU Usage Runbook
    
    ## Immediate Actions
    1. Check current CPU usage: `kubectl top nodes`
    2. Identify high CPU pods: `kubectl top pods --all-namespaces`
    3. Scale affected deployments: `kubectl scale deployment <name> --replicas=<count>`
    
    ## Investigation Steps
    1. Review metrics in Grafana
    2. Check application logs
    3. Analyze performance trends
    
    ## Resolution Steps
    1. Implement resource limits
    2. Optimize application code
    3. Consider horizontal scaling
```

### 2. Automated Remediation

#### Self-Healing Scripts
```bash
#!/bin/bash
# infrastructure/monitoring/auto-remediation.sh

# Auto-restart failed pods
kubectl get pods --all-namespaces --field-selector=status.phase=Failed \
  -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{"\n"}{end}' | \
  while read namespace pod; do
    kubectl delete pod $pod -n $namespace
  done

# Auto-scale on high CPU
kubectl get hpa --all-namespaces -o json | \
  jq -r '.items[] | select(.status.currentCPUUtilizationPercentage > 80) | 
  .metadata.namespace + " " + .metadata.name' | \
  while read namespace hpa; do
    kubectl patch hpa $hpa -n $namespace -p '{"spec":{"maxReplicas":10}}'
  done
```

## 📋 Monitoring Maintenance

### 1. Regular Maintenance Tasks

#### Daily Tasks
- Check alert status and resolve false positives
- Review dashboard performance
- Validate metric collection
- Monitor storage usage

#### Weekly Tasks
- Review and update alert thresholds
- Analyze performance trends
- Update monitoring configurations
- Test backup and restore procedures

#### Monthly Tasks
- Capacity planning review
- Performance optimization
- Security audit of monitoring stack
- Documentation updates

### 2. Monitoring Health Checks

#### Health Check Script
```bash
#!/bin/bash
# infrastructure/monitoring/health-check.sh

# Check Prometheus health
curl -f http://prometheus.monitoring.svc.cluster.local:9090/-/healthy

# Check Grafana health
curl -f http://grafana.monitoring.svc.cluster.local/api/health

# Check Alertmanager health
curl -f http://alertmanager.monitoring.svc.cluster.local:9093/-/healthy

# Check metric ingestion rate
prometheus_query="rate(prometheus_tsdb_symbol_table_size_bytes[5m])"
curl -G http://prometheus.monitoring.svc.cluster.local:9090/api/v1/query \
  --data-urlencode "query=${prometheus_query}"
```

---

**Created by**: Fahed Mlaiel (mlaiel@live.de)  
**Version**: 1.0  
**Last Updated**: 2025  
**Classification**: Enterprise Monitoring Documentation

© 2025 Fahed Mlaiel. All rights reserved.