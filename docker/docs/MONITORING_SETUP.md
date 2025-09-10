# Monitoring Setup Guide

## Comprehensive Monitoring for Ainflue Docker Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### Monitoring Stack Overview

Complete monitoring solution using Prometheus, Grafana, Jaeger, and ELK stack for 80+ containerized services.

### Prometheus Configuration

#### 1. Prometheus Setup
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'docker-services'
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        port: 8080
    relabel_configs:
      - source_labels: [__meta_docker_container_label_monitoring]
        action: keep
        regex: true
```

#### 2. Service Metrics Exposure
```python
# Python service metrics
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')

# Start metrics server
start_http_server(8080)
```

### Grafana Dashboards

#### 1. Docker Overview Dashboard
```json
{
  "dashboard": {
    "title": "Ainflue Docker Overview",
    "panels": [
      {
        "title": "Container CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total[5m])"
          }
        ]
      },
      {
        "title": "Container Memory Usage",
        "type": "graph", 
        "targets": [
          {
            "expr": "container_memory_usage_bytes / container_spec_memory_limit_bytes"
          }
        ]
      }
    ]
  }
}
```

#### 2. Service-Specific Dashboards
```json
{
  "dashboard": {
    "title": "Audio Processing Service",
    "panels": [
      {
        "title": "Processing Queue Length",
        "type": "singlestat",
        "targets": [
          {
            "expr": "audio_processing_queue_length"
          }
        ]
      }
    ]
  }
}
```

### Alerting Configuration

#### 1. Prometheus Alerts
```yaml
# alerts.yml
groups:
- name: docker.rules
  rules:
  - alert: ContainerDown
    expr: up == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Container {{ $labels.instance }} is down"
      
  - alert: HighCPUUsage
    expr: rate(container_cpu_usage_seconds_total[5m]) > 0.8
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage on {{ $labels.name }}"
      
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High memory usage on {{ $labels.name }}"
```

#### 2. Alertmanager Configuration
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@ainflue.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@ainflue.com'
    subject: 'Ainflue Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}
```

### Distributed Tracing

#### 1. Jaeger Configuration
```yaml
# jaeger deployment
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      COLLECTOR_ZIPKIN_HTTP_PORT: 9411
    ports:
      - "16686:16686"
      - "14268:14268"
```

#### 2. Application Tracing
```python
# OpenTelemetry tracing
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Use in code
with tracer.start_as_current_span("audio_processing"):
    process_audio_file(file_path)
```

### Logging with ELK Stack

#### 1. Elasticsearch Setup
```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    volumes:
      - es-data:/usr/share/elasticsearch/data
```

#### 2. Logstash Configuration
```yaml
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "audio-processor" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ainflue-logs-%{+YYYY.MM.dd}"
  }
}
```

#### 3. Kibana Dashboards
```json
{
  "visualization": {
    "title": "Error Rate by Service",
    "type": "line",
    "params": {
      "grid": {
        "categoryLines": false,
        "style": {
          "color": "#eee"
        }
      }
    }
  }
}
```

### Health Checks

#### 1. Application Health Endpoints
```python
# FastAPI health check
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/health")
async def health_check():
    # Check database connection
    try:
        await database.execute("SELECT 1")
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    # Check Redis connection
    try:
        await redis.ping()
    except Exception:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

#### 2. Docker Health Checks
```dockerfile
# Dockerfile health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Custom Metrics

#### 1. Business Metrics
```python
# Custom business metrics
from prometheus_client import Counter, Histogram

AUDIO_FILES_PROCESSED = Counter('audio_files_processed_total', 'Total audio files processed')
PROCESSING_DURATION = Histogram('audio_processing_duration_seconds', 'Audio processing duration')
REVENUE_GENERATED = Counter('revenue_generated_total', 'Total revenue generated', ['currency'])

# Usage
@PROCESSING_DURATION.time()
def process_audio(file_path):
    # Process audio
    AUDIO_FILES_PROCESSED.inc()
    return result
```

#### 2. Infrastructure Metrics
```python
# System metrics collection
import psutil
from prometheus_client import Gauge

CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage')
MEMORY_USAGE = Gauge('system_memory_usage_bytes', 'System memory usage')
DISK_USAGE = Gauge('system_disk_usage_percent', 'System disk usage')

def collect_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().used)
    DISK_USAGE.set(psutil.disk_usage('/').percent)
```

### Monitoring Automation

#### 1. Auto-Discovery
```python
# Service discovery for monitoring
import docker

client = docker.from_env()

def discover_services():
    services = []
    for container in client.containers.list():
        if 'monitoring=true' in container.labels:
            service_info = {
                'name': container.name,
                'ip': container.attrs['NetworkSettings']['IPAddress'],
                'port': container.labels.get('monitoring.port', '8080')
            }
            services.append(service_info)
    return services
```

#### 2. Dynamic Alert Configuration
```python
# Dynamic alerting based on service type
def configure_alerts(service_type):
    alerts = {
        'audio-processor': {
            'cpu_threshold': 0.8,
            'memory_threshold': 0.9,
            'queue_length_threshold': 100
        },
        'database': {
            'cpu_threshold': 0.7,
            'memory_threshold': 0.8,
            'connection_threshold': 80
        }
    }
    return alerts.get(service_type, {})
```

### Performance Monitoring

#### 1. SLA Monitoring
```yaml
# SLA rules
- alert: APILatencyHigh
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "API latency is high"
    
- alert: ErrorRateHigh
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Error rate is high"
```

### Monitoring Best Practices

1. **Layered Monitoring**: Implement monitoring at infrastructure, application, and business levels
2. **Meaningful Alerts**: Create alerts that require action, avoid alert fatigue
3. **Retention Policies**: Set appropriate data retention policies for metrics and logs
4. **Dashboard Organization**: Organize dashboards by service and functional area
5. **Regular Review**: Regularly review and update monitoring configuration
6. **Documentation**: Document all metrics, alerts, and runbooks