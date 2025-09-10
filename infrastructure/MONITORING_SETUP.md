# 📊 Ainflue Infrastructure Monitoring Setup

**Author:** Fahed Mlaiel <mlaiel@live.de>  
**Team:** DevOps Engineer + Monitoring Specialist + SRE Expert  
**Version:** 1.0.0  
**Last Updated:** January 2025  

## 📋 Table of Contents

1. [Monitoring Stack Overview](#monitoring-stack-overview)
2. [Prometheus Configuration](#prometheus-configuration)
3. [Grafana Dashboards](#grafana-dashboards)
4. [Alerting Rules](#alerting-rules)
5. [Log Management](#log-management)
6. [Distributed Tracing](#distributed-tracing)
7. [Business Metrics](#business-metrics)
8. [Alerting Channels](#alerting-channels)

---

## 🎯 Monitoring Stack Overview

### Enterprise Observability Architecture

The Ainflue monitoring stack provides **comprehensive observability** across all infrastructure layers, applications, and business metrics with AI-powered anomaly detection and predictive alerting.

### Core Components

```yaml
Monitoring Stack:
  Metrics Collection: Prometheus + Node Exporter + Custom Metrics
  Visualization: Grafana + Custom Dashboards + Business Intelligence
  Alerting: AlertManager + PagerDuty + Slack + Email
  Log Management: ELK Stack (Elasticsearch, Logstash, Kibana)
  Distributed Tracing: Jaeger + Zipkin
  APM: Application Performance Monitoring
  Business Metrics: Creator Economy KPIs + Revenue Tracking
```

### SLA Targets
```yaml
Availability Targets:
  Platform Availability: 99.99% (52.6 minutes downtime/year)
  API Response Time: <100ms (95th percentile)
  Database Query Time: <50ms (95th percentile)
  File Upload Time: <5s for 100MB files
  Creator Content Processing: <30s for standard content

Performance Targets:
  CPU Utilization: <70% average, <90% peak
  Memory Utilization: <80% average, <95% peak
  Disk I/O: <80% utilization
  Network Bandwidth: <70% utilization
```

---

## 📈 Prometheus Configuration

### Prometheus Server Setup

#### Helm Values for Prometheus
```yaml
# prometheus-values.yaml
prometheus:
  prometheusSpec:
    # Storage configuration
    retention: 30d
    retentionSize: 100GB
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: gp3
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 200Gi
    
    # Resource allocation
    resources:
      requests:
        cpu: 2000m
        memory: 8Gi
      limits:
        cpu: 4000m
        memory: 16Gi
    
    # High availability
    replicas: 2
    
    # Additional scrape configs
    additionalScrapeConfigs:
      - job_name: 'ainflue-api'
        kubernetes_sd_configs:
        - role: endpoints
        relabel_configs:
        - source_labels: [__meta_kubernetes_service_name]
          action: keep
          regex: ainflue-api-service
        - source_labels: [__meta_kubernetes_endpoint_port_name]
          action: keep
          regex: metrics
        
      - job_name: 'ainflue-workers'
        kubernetes_sd_configs:
        - role: pod
        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_label_app]
          action: keep
          regex: ainflue-worker
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
          action: keep
          regex: true
        
      - job_name: 'redis-exporter'
        static_configs:
        - targets: ['redis-exporter:9121']
        
      - job_name: 'postgres-exporter'
        static_configs:
        - targets: ['postgres-exporter:9187']

    # Recording rules for performance
    ruleSelector:
      matchLabels:
        prometheus: kube-prometheus
        role: alert-rules
        
  # External storage for long-term metrics
  thanos:
    enabled: true
    objectStorageConfig:
      secretName: thanos-objstore-secret
      secretKey: objstore.yml
```

### Custom Recording Rules
```yaml
# recording-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ainflue-recording-rules
  namespace: monitoring
  labels:
    prometheus: kube-prometheus
    role: alert-rules
spec:
  groups:
  - name: ainflue.business.rules
    interval: 30s
    rules:
    # Creator Economy Metrics
    - record: ainflue:creator_uploads_rate
      expr: rate(ainflue_uploads_total[5m])
    
    - record: ainflue:content_processing_duration_p95
      expr: histogram_quantile(0.95, rate(ainflue_content_processing_duration_seconds_bucket[5m]))
    
    - record: ainflue:api_requests_rate
      expr: rate(ainflue_api_requests_total[5m])
    
    - record: ainflue:api_error_rate
      expr: rate(ainflue_api_requests_total{status=~"5.."}[5m]) / rate(ainflue_api_requests_total[5m])
    
    - record: ainflue:revenue_per_hour
      expr: increase(ainflue_revenue_total[1h])
    
    - record: ainflue:active_creators_count
      expr: count(increase(ainflue_creator_activity_total[24h]) > 0)
    
    # Infrastructure Performance
    - record: ainflue:cpu_utilization_avg
      expr: avg(rate(container_cpu_usage_seconds_total{container!=""}[5m])) by (namespace, pod)
    
    - record: ainflue:memory_utilization_percent
      expr: (container_memory_working_set_bytes / container_spec_memory_limit_bytes) * 100
    
    - record: ainflue:disk_usage_percent
      expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
    
  - name: ainflue.sla.rules
    interval: 60s
    rules:
    # SLA Metrics
    - record: ainflue:availability_sli
      expr: (1 - (rate(ainflue_api_requests_total{status=~"5.."}[5m]) / rate(ainflue_api_requests_total[5m]))) * 100
    
    - record: ainflue:latency_sli_p95
      expr: histogram_quantile(0.95, rate(ainflue_api_request_duration_seconds_bucket[5m])) * 1000
    
    - record: ainflue:error_budget_remaining
      expr: (1 - (1 - ainflue:availability_sli / 100) / (1 - 99.99 / 100)) * 100
```

### Application Metrics Instrumentation

#### Go Application Metrics
```go
// metrics.go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    // API Metrics
    APIRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "ainflue_api_requests_total",
            Help: "Total number of API requests",
        },
        []string{"method", "endpoint", "status"},
    )
    
    APIRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "ainflue_api_request_duration_seconds",
            Help: "API request duration in seconds",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint"},
    )
    
    // Business Metrics
    UploadsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "ainflue_uploads_total",
            Help: "Total number of content uploads",
        },
        []string{"creator_id", "content_type"},
    )
    
    ContentProcessingDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "ainflue_content_processing_duration_seconds",
            Help: "Content processing duration in seconds",
            Buckets: []float64{1, 5, 10, 30, 60, 300, 600},
        },
        []string{"content_type", "processing_stage"},
    )
    
    RevenueTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "ainflue_revenue_total",
            Help: "Total revenue generated",
        },
        []string{"creator_id", "revenue_type"},
    )
    
    ActiveCreators = promauto.NewGauge(
        prometheus.GaugeOpts{
            Name: "ainflue_active_creators_count",
            Help: "Number of active creators",
        },
    )
    
    // Infrastructure Metrics
    DatabaseConnections = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "ainflue_database_connections",
            Help: "Number of database connections",
        },
        []string{"database", "state"},
    )
    
    QueueSize = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "ainflue_queue_size",
            Help: "Number of items in queue",
        },
        []string{"queue_name"},
    )
)

// Middleware for HTTP metrics
func PrometheusMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        
        // Create a response recorder to capture status code
        recorder := &responseRecorder{ResponseWriter: w, statusCode: 200}
        
        next.ServeHTTP(recorder, r)
        
        duration := time.Since(start).Seconds()
        status := strconv.Itoa(recorder.statusCode)
        
        APIRequestsTotal.WithLabelValues(r.Method, r.URL.Path, status).Inc()
        APIRequestDuration.WithLabelValues(r.Method, r.URL.Path).Observe(duration)
    })
}
```

---

## 📊 Grafana Dashboards

### Infrastructure Overview Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "Ainflue Infrastructure Overview",
    "tags": ["ainflue", "infrastructure"],
    "timezone": "UTC",
    "panels": [
      {
        "id": 1,
        "title": "API Request Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(ainflue_api_requests_total[5m]))",
            "legendFormat": "Requests/sec"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 1000}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "API Error Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(ainflue_api_requests_total{status=~\"5..\"}[5m])) / sum(rate(ainflue_api_requests_total[5m])) * 100",
            "legendFormat": "Error Rate %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 5}
              ]
            }
          }
        }
      },
      {
        "id": 3,
        "title": "Response Time P95",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(ainflue_api_request_duration_seconds_bucket[5m])) * 1000",
            "legendFormat": "P95 Latency"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ms",
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 500}
              ]
            }
          }
        }
      },
      {
        "id": 4,
        "title": "CPU Usage by Pod",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{namespace=\"ainflue\", container!=\"\"}[5m]) * 100",
            "legendFormat": "{{pod}} - {{container}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100
          }
        }
      },
      {
        "id": 5,
        "title": "Memory Usage by Pod",
        "type": "timeseries",
        "targets": [
          {
            "expr": "container_memory_working_set_bytes{namespace=\"ainflue\", container!=\"\"} / 1024 / 1024",
            "legendFormat": "{{pod}} - {{container}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "decbytes"
          }
        }
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

### Creator Economy Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "Ainflue Creator Economy Metrics",
    "tags": ["ainflue", "business", "creators"],
    "panels": [
      {
        "id": 1,
        "title": "Active Creators",
        "type": "stat",
        "targets": [
          {
            "expr": "ainflue_active_creators_count",
            "legendFormat": "Active Creators"
          }
        ]
      },
      {
        "id": 2,
        "title": "Content Uploads per Hour",
        "type": "timeseries",
        "targets": [
          {
            "expr": "increase(ainflue_uploads_total[1h])",
            "legendFormat": "{{content_type}}"
          }
        ]
      },
      {
        "id": 3,
        "title": "Revenue per Hour",
        "type": "timeseries",
        "targets": [
          {
            "expr": "increase(ainflue_revenue_total[1h])",
            "legendFormat": "{{revenue_type}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "currencyUSD"
          }
        }
      },
      {
        "id": 4,
        "title": "Content Processing Time",
        "type": "heatmap",
        "targets": [
          {
            "expr": "rate(ainflue_content_processing_duration_seconds_bucket[5m])",
            "legendFormat": "{{le}}"
          }
        ]
      },
      {
        "id": 5,
        "title": "Top Creators by Revenue",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, increase(ainflue_revenue_total[24h]))",
            "legendFormat": "{{creator_id}}"
          }
        ]
      }
    ]
  }
}
```

### SLA Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "Ainflue SLA Monitoring",
    "tags": ["ainflue", "sla", "slo"],
    "panels": [
      {
        "id": 1,
        "title": "Availability SLI",
        "type": "stat",
        "targets": [
          {
            "expr": "ainflue:availability_sli",
            "legendFormat": "Availability %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 99,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 99},
                {"color": "yellow", "value": 99.9},
                {"color": "green", "value": 99.99}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "Error Budget Remaining",
        "type": "gauge",
        "targets": [
          {
            "expr": "ainflue:error_budget_remaining",
            "legendFormat": "Error Budget %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 25},
                {"color": "green", "value": 50}
              ]
            }
          }
        }
      },
      {
        "id": 3,
        "title": "Latency SLI (P95)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "ainflue:latency_sli_p95",
            "legendFormat": "P95 Latency"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ms",
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 500}
              ]
            }
          }
        }
      }
    ]
  }
}
```

---

## 🚨 Alerting Rules

### Critical Infrastructure Alerts
```yaml
# critical-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ainflue-critical-alerts
  namespace: monitoring
  labels:
    prometheus: kube-prometheus
    role: alert-rules
spec:
  groups:
  - name: ainflue.critical
    rules:
    # Platform Availability
    - alert: PlatformDown
      expr: up{job="ainflue-api"} == 0
      for: 1m
      labels:
        severity: critical
        team: infrastructure
      annotations:
        summary: "Ainflue platform is down"
        description: "The Ainflue API is not responding. Platform is completely down."
        runbook_url: "https://docs.ainflue.com/runbooks/platform-down"
    
    - alert: HighErrorRate
      expr: rate(ainflue_api_requests_total{status=~"5.."}[5m]) / rate(ainflue_api_requests_total[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
        team: backend
      annotations:
        summary: "High API error rate detected"
        description: "API error rate is {{ $value | humanizePercentage }} which is above 5% threshold"
        
    - alert: HighLatency
      expr: histogram_quantile(0.95, rate(ainflue_api_request_duration_seconds_bucket[5m])) > 0.5
      for: 10m
      labels:
        severity: critical
        team: performance
      annotations:
        summary: "High API latency detected"
        description: "95th percentile latency is {{ $value }}s which is above 500ms threshold"
    
    # Database Alerts
    - alert: DatabaseDown
      expr: up{job="postgres-exporter"} == 0
      for: 2m
      labels:
        severity: critical
        team: database
      annotations:
        summary: "PostgreSQL database is down"
        description: "Primary PostgreSQL database is not responding"
        
    - alert: DatabaseHighConnections
      expr: pg_stat_database_numbackends > 80
      for: 5m
      labels:
        severity: warning
        team: database
      annotations:
        summary: "High database connection count"
        description: "Database has {{ $value }} connections which is approaching the limit"
    
    # Infrastructure Resource Alerts
    - alert: HighCPUUsage
      expr: rate(container_cpu_usage_seconds_total{namespace="ainflue"}[5m]) * 100 > 80
      for: 10m
      labels:
        severity: warning
        team: infrastructure
      annotations:
        summary: "High CPU usage detected"
        description: "Pod {{ $labels.pod }} CPU usage is {{ $value }}%"
        
    - alert: HighMemoryUsage
      expr: container_memory_working_set_bytes{namespace="ainflue"} / container_spec_memory_limit_bytes * 100 > 90
      for: 5m
      labels:
        severity: critical
        team: infrastructure
      annotations:
        summary: "High memory usage detected"
        description: "Pod {{ $labels.pod }} memory usage is {{ $value }}%"
        
    - alert: DiskSpaceLow
      expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 85
      for: 5m
      labels:
        severity: warning
        team: infrastructure
      annotations:
        summary: "Low disk space"
        description: "Disk usage on {{ $labels.instance }} is {{ $value }}%"

  - name: ainflue.business
    rules:
    # Business Logic Alerts
    - alert: CreatorUploadFailures
      expr: rate(ainflue_uploads_total{status="failed"}[10m]) > 0.1
      for: 5m
      labels:
        severity: warning
        team: product
      annotations:
        summary: "High creator upload failure rate"
        description: "Upload failure rate is {{ $value | humanize }} uploads/sec"
        
    - alert: RevenueProcessingDelay
      expr: increase(ainflue_revenue_processing_delay_total[5m]) > 10
      for: 2m
      labels:
        severity: critical
        team: finance
      annotations:
        summary: "Revenue processing delays detected"
        description: "{{ $value }} revenue transactions are delayed"
        
    - alert: ContentProcessingBacklog
      expr: ainflue_queue_size{queue_name="content_processing"} > 1000
      for: 10m
      labels:
        severity: warning
        team: media
      annotations:
        summary: "Content processing backlog"
        description: "Content processing queue has {{ $value }} items pending"

  - name: ainflue.sla
    rules:
    # SLA Monitoring
    - alert: SLAViolation
      expr: ainflue:availability_sli < 99.99
      for: 1m
      labels:
        severity: critical
        team: sre
      annotations:
        summary: "SLA violation detected"
        description: "Platform availability {{ $value }}% is below SLA target of 99.99%"
        
    - alert: ErrorBudgetExhausted
      expr: ainflue:error_budget_remaining < 10
      for: 5m
      labels:
        severity: warning
        team: sre
      annotations:
        summary: "Error budget nearly exhausted"
        description: "Only {{ $value }}% of error budget remaining for this month"
```

### Custom Alert Rules for Creator Economy
```yaml
# business-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ainflue-business-alerts
  namespace: monitoring
spec:
  groups:
  - name: ainflue.creator_economy
    rules:
    - alert: CreatorSignupSpike
      expr: increase(ainflue_creator_signups_total[1h]) > 100
      for: 0m
      labels:
        severity: info
        team: growth
      annotations:
        summary: "Creator signup spike detected"
        description: "{{ $value }} new creators signed up in the last hour"
        
    - alert: UnusualRevenuePattern
      expr: abs(increase(ainflue_revenue_total[1h]) - increase(ainflue_revenue_total[1h] offset 24h)) / increase(ainflue_revenue_total[1h] offset 24h) > 0.5
      for: 0m
      labels:
        severity: info
        team: finance
      annotations:
        summary: "Unusual revenue pattern detected"
        description: "Revenue is significantly different from same time yesterday"
        
    - alert: PopularContentDetected
      expr: increase(ainflue_content_views_total[10m]) > 10000
      for: 0m
      labels:
        severity: info
        team: content
      annotations:
        summary: "Viral content detected"
        description: "Content {{ $labels.content_id }} received {{ $value }} views in 10 minutes"
```

---

## 📝 Log Management

### ELK Stack Configuration

#### Elasticsearch Configuration
```yaml
# elasticsearch-values.yaml
replicas: 3
minimumMasterNodes: 2

clusterHealthCheckParams: "wait_for_status=yellow&timeout=1s"

resources:
  requests:
    cpu: "2000m"
    memory: "4Gi"
  limits:
    cpu: "2000m"
    memory: "4Gi"

volumeClaimTemplate:
  accessModes: [ "ReadWriteOnce" ]
  storageClassName: "gp3"
  resources:
    requests:
      storage: 500Gi

esConfig:
  elasticsearch.yml: |
    cluster.name: "ainflue-logs"
    network.host: 0.0.0.0
    xpack.security.enabled: true
    xpack.monitoring.collection.enabled: true
    indices.lifecycle.policy.default_policy:
      phases:
        hot:
          actions:
            rollover:
              max_size: 10gb
              max_age: 7d
        warm:
          min_age: 7d
          actions:
            allocate:
              number_of_replicas: 0
        cold:
          min_age: 30d
          actions:
            allocate:
              number_of_replicas: 0
        delete:
          min_age: 90d
```

#### Logstash Pipeline Configuration
```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
  
  http {
    port => 8080
    codec => json
  }
}

filter {
  if [kubernetes][container][name] == "ainflue-api" {
    grok {
      match => { 
        "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} \[%{DATA:logger}\] %{GREEDYDATA:message}" 
      }
      overwrite => [ "message" ]
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    if [level] == "ERROR" {
      mutate {
        add_tag => [ "error" ]
      }
    }
  }
  
  # Business logic specific parsing
  if [kubernetes][container][name] == "ainflue-api" and "upload" in [message] {
    grok {
      match => {
        "message" => "Creator %{DATA:creator_id} uploaded %{DATA:content_type} size=%{NUMBER:file_size:int} duration=%{NUMBER:upload_duration:float}"
      }
    }
    
    mutate {
      add_tag => [ "creator_upload" ]
    }
  }
  
  # Revenue tracking logs
  if [kubernetes][container][name] == "ainflue-api" and "revenue" in [message] {
    grok {
      match => {
        "message" => "Revenue processed: creator=%{DATA:creator_id} amount=%{NUMBER:amount:float} currency=%{DATA:currency}"
      }
    }
    
    mutate {
      add_tag => [ "revenue_processed" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch-master:9200"]
    index => "ainflue-logs-%{+YYYY.MM.dd}"
    template_name => "ainflue"
    template => "/usr/share/logstash/templates/ainflue-template.json"
  }
  
  # Send errors to alerting
  if "error" in [tags] {
    http {
      url => "http://alertmanager:9093/api/v1/alerts"
      http_method => "post"
      format => "json"
      mapping => {
        "alerts" => [{
          "labels" => {
            "alertname" => "ApplicationError"
            "severity" => "warning"
            "service" => "%{[kubernetes][container][name]}"
            "pod" => "%{[kubernetes][pod][name]}"
          }
          "annotations" => {
            "summary" => "Application error detected"
            "description" => "%{message}"
          }
        }]
      }
    }
  }
}
```

#### Kibana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "Ainflue Application Logs",
    "panels": [
      {
        "title": "Log Volume by Level",
        "type": "histogram",
        "query": {
          "query": "*",
          "filters": [
            {
              "term": {
                "kubernetes.container.name": "ainflue-api"
              }
            }
          ]
        },
        "aggregations": {
          "date_histogram": {
            "field": "@timestamp",
            "interval": "1m"
          },
          "terms": {
            "field": "level"
          }
        }
      },
      {
        "title": "Error Logs",
        "type": "table",
        "query": {
          "bool": {
            "must": [
              {
                "term": {
                  "level": "ERROR"
                }
              },
              {
                "range": {
                  "@timestamp": {
                    "gte": "now-1h"
                  }
                }
              }
            ]
          }
        }
      },
      {
        "title": "Creator Upload Activity",
        "type": "line",
        "query": {
          "bool": {
            "must": [
              {
                "exists": {
                  "field": "creator_id"
                }
              },
              {
                "terms": {
                  "tags": ["creator_upload"]
                }
              }
            ]
          }
        }
      }
    ]
  }
}
```

---

## 🔍 Distributed Tracing

### Jaeger Configuration

#### Jaeger Deployment
```yaml
# jaeger-values.yaml
provisionDataStore:
  cassandra: false
  elasticsearch: true

storage:
  type: elasticsearch
  elasticsearch:
    host: elasticsearch-master
    port: 9200
    
collector:
  replicaCount: 3
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 256m
      memory: 256Mi

query:
  replicaCount: 2
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 256m
      memory: 256Mi

agent:
  daemonset:
    enabled: true
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 256m
      memory: 256Mi
```

#### Application Tracing Configuration
```go
// tracing.go
package tracing

import (
    "github.com/opentracing/opentracing-go"
    "github.com/uber/jaeger-client-go"
    "github.com/uber/jaeger-client-go/config"
)

func InitJaeger() (opentracing.Tracer, error) {
    cfg := config.Configuration{
        ServiceName: "ainflue-api",
        Sampler: &config.SamplerConfig{
            Type:  jaeger.SamplerTypeConst,
            Param: 1, // Sample all traces in development
        },
        Reporter: &config.ReporterConfig{
            LogSpans: true,
            LocalAgentHostPort: "jaeger-agent:6831",
        },
    }
    
    tracer, _, err := cfg.NewTracer()
    if err != nil {
        return nil, err
    }
    
    opentracing.SetGlobalTracer(tracer)
    return tracer, nil
}

// Middleware for HTTP tracing
func TracingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        span := opentracing.StartSpan(fmt.Sprintf("%s %s", r.Method, r.URL.Path))
        defer span.Finish()
        
        ctx := opentracing.ContextWithSpan(r.Context(), span)
        r = r.WithContext(ctx)
        
        // Add useful tags
        span.SetTag("http.method", r.Method)
        span.SetTag("http.url", r.URL.String())
        span.SetTag("user.id", getUserID(r))
        
        next.ServeHTTP(w, r)
    })
}

// Business logic tracing
func TraceContentUpload(ctx context.Context, creatorID string, contentType string) {
    span, ctx := opentracing.StartSpanFromContext(ctx, "content.upload")
    defer span.Finish()
    
    span.SetTag("creator.id", creatorID)
    span.SetTag("content.type", contentType)
    
    // Trace AI processing
    aiSpan, _ := opentracing.StartSpanFromContext(ctx, "ai.processing")
    // ... AI processing logic
    aiSpan.Finish()
    
    // Trace storage
    storageSpan, _ := opentracing.StartSpanFromContext(ctx, "storage.save")
    // ... storage logic
    storageSpan.Finish()
}
```

---

## 💰 Business Metrics

### Creator Economy KPIs

#### Revenue Tracking
```go
// business_metrics.go
package metrics

// Revenue metrics
func TrackRevenue(creatorID string, amount float64, revenueType string) {
    RevenueTotal.WithLabelValues(creatorID, revenueType).Add(amount)
    
    // Also track in time series for trending
    revenueTrend.WithLabelValues(revenueType).Observe(amount)
}

// Creator activity metrics
func TrackCreatorActivity(creatorID string, activityType string) {
    CreatorActivity.WithLabelValues(creatorID, activityType).Inc()
    
    // Update active creators gauge
    updateActiveCreatorsCount()
}

// Content performance metrics
func TrackContentPerformance(contentID string, creatorID string, views int, engagement float64) {
    ContentViews.WithLabelValues(contentID, creatorID).Add(float64(views))
    ContentEngagement.WithLabelValues(contentID, creatorID).Set(engagement)
}

// Subscription metrics
func TrackSubscription(creatorID string, subscriberID string, tier string) {
    Subscriptions.WithLabelValues(creatorID, tier).Inc()
    SubscriptionRevenue.WithLabelValues(creatorID, tier).Add(getTierPrice(tier))
}
```

#### Business Intelligence Dashboard
```yaml
# Business Metrics Configuration
business_metrics:
  creator_economy:
    - metric: total_revenue_daily
      description: "Total platform revenue per day"
      query: "increase(ainflue_revenue_total[1d])"
      
    - metric: active_creators_monthly
      description: "Number of creators active in the last 30 days"
      query: "count(increase(ainflue_creator_activity_total[30d]) > 0)"
      
    - metric: average_revenue_per_creator
      description: "Average revenue per creator per month"
      query: "increase(ainflue_revenue_total[30d]) / count(increase(ainflue_creator_activity_total[30d]) > 0)"
      
    - metric: content_upload_rate
      description: "Content uploads per hour"
      query: "rate(ainflue_uploads_total[1h])"
      
    - metric: subscriber_growth_rate
      description: "New subscribers per day"
      query: "increase(ainflue_subscriptions_total[1d])"
      
  platform_health:
    - metric: platform_availability
      description: "Platform availability percentage"
      query: "ainflue:availability_sli"
      
    - metric: api_performance
      description: "95th percentile API response time"
      query: "ainflue:latency_sli_p95"
      
    - metric: error_rate
      description: "Platform error rate percentage"
      query: "ainflue:api_error_rate * 100"
```

---

## 📢 Alerting Channels

### AlertManager Configuration
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.company.com:587'
  smtp_from: 'alerts@ainflue.com'
  smtp_auth_username: 'alerts@ainflue.com'
  smtp_auth_password: 'secretpassword'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
    group_wait: 0s
    repeat_interval: 5m
    
  - match:
      team: infrastructure
    receiver: 'infrastructure-team'
    
  - match:
      team: backend
    receiver: 'backend-team'
    
  - match:
      team: business
    receiver: 'business-team'

receivers:
- name: 'default'
  email_configs:
  - to: 'alerts@ainflue.com'
    subject: 'Ainflue Alert: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      Labels: {{ range .Labels.SortedPairs }}{{ .Name }}={{ .Value }} {{ end }}
      {{ end }}

- name: 'critical-alerts'
  email_configs:
  - to: 'oncall@ainflue.com'
    subject: '🚨 CRITICAL: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
  
  pagerduty_configs:
  - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
    description: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts-critical'
    title: '🚨 Critical Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}: {{ .Annotations.description }}{{ end }}'

- name: 'infrastructure-team'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#infrastructure-alerts'
    title: '⚠️ Infrastructure Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

- name: 'backend-team'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#backend-alerts'
    title: '🔧 Backend Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

- name: 'business-team'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#business-alerts'
    title: '📊 Business Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

inhibit_rules:
- source_match:
    severity: 'critical'
  target_match:
    severity: 'warning'
  equal: ['alertname', 'cluster', 'service']
```

### Notification Templates
```html
<!-- email-template.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Ainflue Alert Notification</title>
    <style>
        .critical { background-color: #ff4444; color: white; }
        .warning { background-color: #ffaa00; color: white; }
        .info { background-color: #4444ff; color: white; }
    </style>
</head>
<body>
    <div class="{{ .GroupLabels.severity }}">
        <h2>🚨 Ainflue Platform Alert</h2>
        
        {{ range .Alerts }}
        <div style="border: 1px solid #ccc; margin: 10px; padding: 10px;">
            <h3>{{ .Annotations.summary }}</h3>
            <p><strong>Description:</strong> {{ .Annotations.description }}</p>
            <p><strong>Time:</strong> {{ .StartsAt.Format "2006-01-02 15:04:05 UTC" }}</p>
            <p><strong>Severity:</strong> {{ .Labels.severity }}</p>
            <p><strong>Team:</strong> {{ .Labels.team }}</p>
            
            {{ if .Annotations.runbook_url }}
            <p><a href="{{ .Annotations.runbook_url }}">📖 Runbook</a></p>
            {{ end }}
            
            <h4>Labels:</h4>
            <ul>
            {{ range .Labels.SortedPairs }}
                <li>{{ .Name }}: {{ .Value }}</li>
            {{ end }}
            </ul>
        </div>
        {{ end }}
        
        <p>
            <a href="https://grafana.ainflue.com">📊 View Dashboards</a> |
            <a href="https://alerts.ainflue.com">🚨 Alert Manager</a> |
            <a href="https://logs.ainflue.com">📝 View Logs</a>
        </p>
    </div>
</body>
</html>
```

---

## 🛠️ Maintenance and Optimization

### Monitoring Stack Maintenance

#### Regular Maintenance Tasks
```bash
#!/bin/bash
# monitoring-maintenance.sh

# Clean old metrics data
echo "Cleaning old metrics data..."
kubectl exec -n monitoring prometheus-server-0 -- promtool query instant 'up'

# Optimize Elasticsearch indices
echo "Optimizing Elasticsearch indices..."
curl -X POST "elasticsearch-master:9200/ainflue-logs-*/_forcemerge?max_num_segments=1"

# Clean old log indices
echo "Cleaning old log indices..."
curator --config /etc/curator/config.yml /etc/curator/actions.yml

# Update Grafana dashboards
echo "Updating Grafana dashboards..."
kubectl apply -f grafana-dashboards/

# Restart unhealthy services
echo "Checking service health..."
kubectl get pods -n monitoring | grep -v Running | awk '{print $1}' | xargs kubectl delete pod -n monitoring

echo "Monitoring maintenance completed"
```

#### Performance Optimization
```yaml
# prometheus-optimization.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config-optimized
data:
  prometheus.yml: |
    global:
      scrape_interval: 30s
      evaluation_interval: 30s
      external_labels:
        cluster: 'ainflue-production'
        environment: 'production'
    
    rule_files:
      - "/etc/prometheus/rules/*.yml"
    
    scrape_configs:
    # High frequency scraping for critical services
    - job_name: 'ainflue-api-critical'
      scrape_interval: 15s
      kubernetes_sd_configs:
      - role: endpoints
      relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: ainflue-api-service
    
    # Lower frequency for infrastructure metrics
    - job_name: 'node-exporter'
      scrape_interval: 60s
      kubernetes_sd_configs:
      - role: node
      
    # Business metrics with moderate frequency
    - job_name: 'business-metrics'
      scrape_interval: 30s
      static_configs:
      - targets: ['business-metrics-exporter:8080']
```

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
**Contact:** mlaiel@live.de  
**Legal Notice:** This monitoring setup documentation contains proprietary monitoring configurations and observability strategies.