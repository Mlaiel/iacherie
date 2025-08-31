"""
IA Influencer Agent - Logging Configuration
Default configuration for logging infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, Any, List


class LoggingConfiguration:
    """Central configuration for IA Influencer Agent logging system"""
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default logging configuration"""



        
        return {
            # Log Aggregator Configuration
            "aggregator": {
                "buffer_size": int(os.getenv("LOG_BUFFER_SIZE", "1000")),
                "flush_interval": int(os.getenv("LOG_FLUSH_INTERVAL", "30")),
                "max_log_size": int(os.getenv("MAX_LOG_SIZE", "10485760")),  # 10MB
                
                # Elasticsearch Integration
                "elasticsearch": {
                    "enabled": os.getenv("ELASTICSEARCH_ENABLED", "true").lower() == "true",
                    "hosts": os.getenv("ELASTICSEARCH_HOSTS", "localhost:9200").split(","),
                    "username": os.getenv("ELASTICSEARCH_USERNAME"),
                    "password": os.getenv("ELASTICSEARCH_PASSWORD"),
                    "index_pattern": os.getenv("ELASTICSEARCH_INDEX_PATTERN", "ia-influencer-logs-%Y.%m.%d"),
                    "use_ssl": os.getenv("ELASTICSEARCH_USE_SSL", "false").lower() == "true",
                    "verify_certs": os.getenv("ELASTICSEARCH_VERIFY_CERTS", "true").lower() == "true"
                },
                
                # Redis Integration
                "redis": {
                    "enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true",
                    "url": os.getenv("REDIS_URL", "redis://localhost:6379"),
                    "stream_name": os.getenv("REDIS_STREAM_NAME", "ia-influencer-logs"),
                    "max_stream_length": int(os.getenv("REDIS_MAX_STREAM_LENGTH", "10000"))
                },
                
                # File Logging
                "file": {
                    "enabled": os.getenv("FILE_LOGGING_ENABLED", "true").lower() == "true",
                    "directory": os.getenv("LOG_DIRECTORY", "/var/log/ia-influencer"),
                    "rotation_size": int(os.getenv("LOG_ROTATION_SIZE", str(100 * 1024 * 1024))),  # 100MB
                    "max_files": int(os.getenv("LOG_MAX_FILES", "10"))
                },
                
                # Sentry Integration
                "sentry": {
                    "enabled": os.getenv("SENTRY_ENABLED", "false").lower() == "true",
                    "dsn": os.getenv("SENTRY_DSN"),
                    "environment": os.getenv("ENVIRONMENT", "production"),
                    "traces_sample_rate": float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
                }
            },
            
            # Elasticsearch Configuration
            "elasticsearch": {
                "hosts": os.getenv("ELASTICSEARCH_HOSTS", "localhost:9200").split(","),
                "username": os.getenv("ELASTICSEARCH_USERNAME"),
                "password": os.getenv("ELASTICSEARCH_PASSWORD"),
                "use_ssl": os.getenv("ELASTICSEARCH_USE_SSL", "false").lower() == "true",
                "verify_certs": os.getenv("ELASTICSEARCH_VERIFY_CERTS", "true").lower() == "true",
                "ca_certs": os.getenv("ELASTICSEARCH_CA_CERTS"),
                "client_cert": os.getenv("ELASTICSEARCH_CLIENT_CERT"),
                "client_key": os.getenv("ELASTICSEARCH_CLIENT_KEY"),
                "timeout": int(os.getenv("ELASTICSEARCH_TIMEOUT", "30")),
                "max_retries": int(os.getenv("ELASTICSEARCH_MAX_RETRIES", "3")),
                "retry_on_timeout": os.getenv("ELASTICSEARCH_RETRY_ON_TIMEOUT", "true").lower() == "true",
                "index_strategy": os.getenv("ELASTICSEARCH_INDEX_STRATEGY", "daily"),
                "base_index_name": os.getenv("ELASTICSEARCH_BASE_INDEX", "ia-influencer-logs")
            },
            
            # Fluentd Configuration
            "fluentd": {
                "host": os.getenv("FLUENTD_HOST", "localhost"),
                "port": int(os.getenv("FLUENTD_PORT", "24224")),
                "buffer_chunk_limit": os.getenv("FLUENTD_BUFFER_CHUNK_LIMIT", "2M"),
                "buffer_queue_limit": int(os.getenv("FLUENTD_BUFFER_QUEUE_LIMIT", "32")),
                "flush_interval": os.getenv("FLUENTD_FLUSH_INTERVAL", "60s"),
                "retry_limit": int(os.getenv("FLUENTD_RETRY_LIMIT", "17")),
                "retry_wait": os.getenv("FLUENTD_RETRY_WAIT", "1s"),
                "max_retry_wait": os.getenv("FLUENTD_MAX_RETRY_WAIT", "131072s"),
                "num_threads": int(os.getenv("FLUENTD_NUM_THREADS", "1"))
            },
            
            # Log Retention Configuration
            "retention": {
                "config_path": os.getenv("RETENTION_CONFIG_PATH", "/etc/ia-influencer/retention.json"),
                "scheduler_interval_hours": int(os.getenv("RETENTION_INTERVAL_HOURS", "24")),
                "s3_bucket": os.getenv("LOG_ARCHIVE_S3_BUCKET", "ia-influencer-logs-archive"),
                "s3_region": os.getenv("AWS_REGION", "eu-central-1"),
                
                # Default retention policies
                "policies": [
                    {
                        "name": "application_logs",
                        "log_patterns": ["*.log", "app-*.log", "api-*.log"],
                        "hot_retention": "90d",
                        "warm_retention": "180d",
                        "cold_retention": "365d",
                        "delete_after": "2555d",  # 7 years
                        "compression": "gzip",
                        "archive_to_s3": True,
                        "s3_prefix": "application"
                    },
                    {
                        "name": "ai_processing_logs",
                        "log_patterns": ["ai-*.log", "*-ml-*.log", "*-fingerprint-*.log"],
                        "hot_retention": "30d",
                        "warm_retention": "90d",
                        "cold_retention": "180d",
                        "delete_after": "365d",
                        "compression": "gzip",
                        "archive_to_s3": True,
                        "s3_prefix": "ai-processing"
                    },
                    {
                        "name": "error_logs",
                        "log_patterns": ["*error*.log", "*exception*.log", "*crash*.log"],
                        "hot_retention": "180d",
                        "warm_retention": "365d",
                        "cold_retention": "2555d",
                        "compression": "gzip",
                        "archive_to_s3": True,
                        "s3_prefix": "errors"
                    },
                    {
                        "name": "audit_logs",
                        "log_patterns": ["audit-*.log", "*-security-*.log", "*-access-*.log"],
                        "hot_retention": "365d",
                        "warm_retention": "2555d",
                        "compression": "gzip",
                        "archive_to_s3": True,
                        "s3_prefix": "audit"
                    },
                    {
                        "name": "performance_logs",
                        "log_patterns": ["*-performance-*.log", "*-metrics-*.log", "*-stats-*.log"],
                        "hot_retention": "7d",
                        "warm_retention": "30d",
                        "cold_retention": "90d",
                        "delete_after": "180d",
                        "compression": "gzip",
                        "archive_to_s3": False
                    }
                ]
            },
            
            # Analytics Configuration
            "analytics": {
                "anomaly_detection": {
                    "enabled": os.getenv("ANOMALY_DETECTION_ENABLED", "true").lower() == "true",
                    "contamination": float(os.getenv("ANOMALY_CONTAMINATION", "0.1")),
                    "training_data_hours": int(os.getenv("ANOMALY_TRAINING_HOURS", "168")),  # 1 week
                    "min_training_samples": int(os.getenv("ANOMALY_MIN_SAMPLES", "100"))
                },
                
                "trend_analysis": {
                    "enabled": os.getenv("TREND_ANALYSIS_ENABLED", "true").lower() == "true",
                    "time_bucket_minutes": int(os.getenv("TREND_BUCKET_MINUTES", "60")),
                    "volatility_threshold": float(os.getenv("VOLATILITY_THRESHOLD", "0.5"))
                },
                
                "pattern_analysis": {
                    "enabled": os.getenv("PATTERN_ANALYSIS_ENABLED", "true").lower() == "true",
                    "clustering_enabled": os.getenv("CLUSTERING_ENABLED", "true").lower() == "true",
                    "min_cluster_size": int(os.getenv("MIN_CLUSTER_SIZE", "5"))
                },
                
                # Default alerts
                "alerts": [
                    {
                        "id": "high_error_rate",
                        "name": "High Error Rate",
                        "description": "Error rate exceeds 5% in 15 minutes",
                        "query": "level:ERROR OR level:CRITICAL",
                        "threshold": 0.05,
                        "severity": "high",
                        "time_window_minutes": 15,
                        "enabled": True
                    },
                    {
                        "id": "ai_processing_failures",
                        "name": "AI Processing Failures",
                        "description": "AI processing failures exceed 10 in 30 minutes",
                        "query": "service:ai* AND level:ERROR",
                        "threshold": 10,
                        "severity": "medium",
                        "time_window_minutes": 30,
                        "enabled": True
                    },
                    {
                        "id": "fingerprinting_anomalies",
                        "name": "Fingerprinting Anomalies",
                        "description": "Fingerprinting errors exceed 5 in 10 minutes",
                        "query": "service:fingerprinting AND level:ERROR",
                        "threshold": 5,
                        "severity": "high",
                        "time_window_minutes": 10,
                        "enabled": True
                    },
                    {
                        "id": "user_auth_failures",
                        "name": "Authentication Failures",
                        "description": "Authentication failures exceed 20 in 5 minutes",
                        "query": "module:auth AND level:ERROR",
                        "threshold": 20,
                        "severity": "critical",
                        "time_window_minutes": 5,
                        "enabled": True
                    },
                    {
                        "id": "revenue_processing_errors",
                        "name": "Revenue Processing Errors",
                        "description": "Revenue processing errors detected",
                        "query": "service:monetization AND level:ERROR",
                        "threshold": 1,
                        "severity": "critical",
                        "time_window_minutes": 60,
                        "enabled": True
                    }
                ],
                
                # Default metrics
                "metrics": [
                    {
                        "name": "log_volume",
                        "description": "Total log volume per hour",
                        "query": "*",
                        "aggregation": "count",
                        "time_window_minutes": 60
                    },
                    {
                        "name": "error_rate",
                        "description": "Error rate percentage",
                        "query": "level:ERROR OR level:CRITICAL",
                        "aggregation": "count",
                        "time_window_minutes": 60
                    },
                    {
                        "name": "avg_processing_time",
                        "description": "Average processing time",
                        "query": "metadata.processing_time_ms:*",
                        "aggregation": "avg",
                        "field": "metadata.processing_time_ms",
                        "time_window_minutes": 60
                    },
                    {
                        "name": "unique_users",
                        "description": "Unique active users",
                        "query": "user_id:*",
                        "aggregation": "cardinality",
                        "field": "user_id",
                        "time_window_minutes": 60
                    },
                    {
                        "name": "fingerprint_success_rate",
                        "description": "Fingerprinting success rate",
                        "query": "service:fingerprinting",
                        "aggregation": "count",
                        "filters": {"level": "INFO"},
                        "time_window_minutes": 60
                    }
                ]
            },
            
            # Monitoring Configuration
            "monitoring": {
                "redis_url": os.getenv("MONITORING_REDIS_URL", "redis://localhost:6379"),
                "buffer_size": int(os.getenv("MONITORING_BUFFER_SIZE", "100")),
                "check_interval": int(os.getenv("MONITORING_CHECK_INTERVAL", "30")),
                "alert_checking_interval": int(os.getenv("ALERT_CHECK_INTERVAL", "300")),
                
                # Notification channels
                "notifications": {
                    "email": {
                        "enabled": os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                        "smtp_host": os.getenv("SMTP_HOST", "localhost"),
                        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                        "username": os.getenv("SMTP_USERNAME"),
                        "password": os.getenv("SMTP_PASSWORD"),
                        "from_email": os.getenv("SMTP_FROM_EMAIL"),
                        "to_emails": os.getenv("ALERT_EMAIL_RECIPIENTS", "").split(",") if os.getenv("ALERT_EMAIL_RECIPIENTS") else [],
                        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true"
                    },
                    
                    "slack": {
                        "enabled": os.getenv("SLACK_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                        "token": os.getenv("SLACK_BOT_TOKEN"),
                        "channel": os.getenv("SLACK_ALERT_CHANNEL", "#alerts")
                    },
                    
                    "webhook": {
                        "enabled": os.getenv("WEBHOOK_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                        "webhook_url": os.getenv("WEBHOOK_URL"),
                        "auth_token": os.getenv("WEBHOOK_AUTH_TOKEN"),
                        "headers": {
                            "Content-Type": "application/json"
                        }
                    },
                    
                    "teams": {
                        "enabled": os.getenv("TEAMS_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                        "webhook_url": os.getenv("TEAMS_WEBHOOK_URL")
                    }
                },
                
                # Default monitoring rules
                "rules": [
                    {
                        "id": "critical_errors",
                        "name": "Critical Error Spike",
                        "description": "Critical errors exceeding threshold",
                        "log_pattern": "level:CRITICAL",
                        "condition": "count > 5 in 5min",
                        "severity": "critical",
                        "notification_channels": ["email", "slack"],
                        "cooldown_minutes": 10,
                        "enabled": True
                    },
                    {
                        "id": "high_error_rate",
                        "name": "High Error Rate",
                        "description": "Error rate above 10% in 15 minutes",
                        "log_pattern": "level:ERROR OR level:CRITICAL",
                        "condition": "rate > 0.1 in 15min",
                        "severity": "high",
                        "notification_channels": ["email", "slack"],
                        "cooldown_minutes": 15,
                        "enabled": True
                    },
                    {
                        "id": "ai_processing_failures",
                        "name": "AI Processing Failures",
                        "description": "AI processing failures spike",
                        "log_pattern": "service:ai* AND level:ERROR",
                        "condition": "count > 20 in 30min",
                        "severity": "high",
                        "notification_channels": ["slack", "webhook"],
                        "cooldown_minutes": 20,
                        "enabled": True
                    },
                    {
                        "id": "fingerprinting_errors",
                        "name": "Fingerprinting Errors",
                        "description": "Fingerprinting service errors",
                        "log_pattern": "service:fingerprinting AND level:ERROR",
                        "condition": "count > 10 in 15min",
                        "severity": "high",
                        "notification_channels": ["email", "teams"],
                        "cooldown_minutes": 15,
                        "enabled": True
                    },
                    {
                        "id": "auth_failures",
                        "name": "Authentication Failures",
                        "description": "Authentication failure spike",
                        "log_pattern": "module:auth AND level:ERROR",
                        "condition": "count > 50 in 10min",
                        "severity": "critical",
                        "notification_channels": ["email", "slack"],
                        "cooldown_minutes": 5,
                        "enabled": True
                    },
                    {
                        "id": "revenue_processing_errors",
                        "name": "Revenue Processing Errors",
                        "description": "Revenue processing system errors",
                        "log_pattern": "service:monetization AND level:ERROR",
                        "condition": "count > 1 in 60min",
                        "severity": "critical",
                        "notification_channels": ["email", "teams"],
                        "cooldown_minutes": 30,
                        "enabled": True
                    },
                    {
                        "id": "database_connection_errors",
                        "name": "Database Connection Errors",
                        "description": "Database connection issues",
                        "log_pattern": "message:*database* AND level:ERROR",
                        "condition": "count > 5 in 10min",
                        "severity": "critical",
                        "notification_channels": ["email", "slack"],
                        "cooldown_minutes": 10,
                        "enabled": True
                    },
                    {
                        "id": "storage_errors",
                        "name": "Storage Errors",
                        "description": "File storage system errors",
                        "log_pattern": "service:storage AND level:ERROR",
                        "condition": "count > 10 in 30min",
                        "severity": "medium",
                        "notification_channels": ["slack", "webhook"],
                        "cooldown_minutes": 20,
                        "enabled": True
                    }
                ]
            },
            
            # Environment-specific settings
            "environment": {
                "name": os.getenv("ENVIRONMENT", "production"),
                "debug": os.getenv("DEBUG", "false").lower() == "true",
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                "service_name": os.getenv("SERVICE_NAME", "ia-influencer-agent"),
                "version": os.getenv("SERVICE_VERSION", "1.0.0"),
                "hostname": os.getenv("HOSTNAME", "localhost"),
                "region": os.getenv("AWS_REGION", "eu-central-1")
            }
        }
    
    @staticmethod
    def get_fluentd_config_yaml() -> str:
        """Get Fluentd configuration as YAML"""



        
        return '''
# IA Influencer Agent Fluentd Configuration
# Author: Fahed Mlaiel <mlaiel@live.de>

<system>
  workers 1
  root_dir /var/log/fluentd
  log_level info
</system>

# HTTP input for API logs
<source>
  @type http
  @id api_logs
  tag ia.api
  port 9880
  bind 0.0.0.0
  format json
</source>

# Forward input for application logs
<source>
  @type forward
  @id app_logs
  tag ia.app
  port 24224
  bind 0.0.0.0
</source>

# Tail container logs
<source>
  @type tail
  @id container_logs
  tag ia.container
  path /var/log/containers/*.log
  pos_file /var/log/fluentd/containers.log.pos
  format json
  read_from_head true
</source>

# Add metadata to all logs
<filter ia.**>
  @type record_transformer
  <record>
    hostname ${hostname}
    environment #{ENV['ENVIRONMENT']}
    service_version #{ENV['SERVICE_VERSION']}
    region #{ENV['AWS_REGION']}
  </record>
</filter>

# Parse AI-specific logs
<filter ia.ai.**>
  @type record_transformer
  <record>
    log_type ai_processing
    processing_pipeline ${record['metadata']['pipeline'] || 'unknown'}
    model_version ${record['metadata']['model_version'] || 'unknown'}
  </record>
</filter>

# Parse fingerprinting logs
<filter ia.fingerprint.**>
  @type record_transformer
  <record>
    log_type fingerprinting
    content_type ${record['metadata']['content_type'] || 'unknown'}
    fingerprint_algorithm ${record['metadata']['algorithm'] || 'unknown'}
  </record>
</filter>

# Filter errors for alerting
<filter ia.**>
  @type grep
  <regexp>
    key level
    pattern ERROR|CRITICAL
  </regexp>
</filter>

# Output to Elasticsearch
<match ia.**>
  @type elasticsearch
  @id elasticsearch_output
  hosts elasticsearch:9200
  index_name ia-influencer-${Time.at(time).strftime('%Y.%m.%d')}
  type_name _doc
  
  <buffer>
    @type file
    path /var/log/fluentd/buffers/elasticsearch
    chunk_limit_size 2M
    queue_limit_length 32
    flush_interval 60s
    retry_type exponential_backoff
  </buffer>
</match>

# Backup to S3
<match ia.backup.**>
  @type s3
  @id s3_backup
  s3_bucket ia-influencer-logs
  s3_region eu-central-1
  path logs/${Time.at(time).strftime('%Y/%m/%d')}/
  s3_object_key_format %{path}%{time_slice}_%{index}.%{file_extension}
  time_slice_format %Y%m%d%H
  
  <buffer>
    @type file
    path /var/log/fluentd/buffers/s3
    chunk_limit_size 10M
    queue_limit_length 16
    flush_interval 300s
    retry_type exponential_backoff
  </buffer>
</match>

# Error alerts
<match ia.error>
  @type http
  @id error_alerts
  endpoint http://alertmanager:9093/api/v1/alerts
  http_method post
  format json
</match>
'''
    
    @staticmethod
    def get_docker_compose_config() -> str:
        """Get Docker Compose configuration for logging stack"""



        
        return '''
version: '3.8'

services:
  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    container_name: ia-elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - logging

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    container_name: ia-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - logging

  # Fluentd
  fluentd:
    build:
      context: .
      dockerfile: Dockerfile.fluentd
    container_name: ia-fluentd
    ports:
      - "24224:24224"
      - "9880:9880"
    volumes:
      - ./fluentd/conf:/fluentd/etc
      - ./logs:/var/log/ia-influencer
    environment:
      - FLUENTD_CONF=fluent.conf
      - ENVIRONMENT=production
      - SERVICE_VERSION=1.0.0
      - AWS_REGION=eu-central-1
    depends_on:
      - elasticsearch
    networks:
      - logging

  # Redis
  redis:
    image: redis:7-alpine
    container_name: ia-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - logging

  # Grafana
  grafana:
    image: grafana/grafana:10.0.0
    container_name: ia-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - logging

  # Prometheus
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: ia-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - logging

volumes:
  elasticsearch_data:
  redis_data:
  grafana_data:
  prometheus_data:

networks:
  logging:
    driver: bridge
'''
    
    @staticmethod
    def get_kubernetes_manifests() -> Dict[str, str]:
        """Get Kubernetes manifests for logging infrastructure"""



        
        return {
            "namespace.yaml": '''
apiVersion: v1
kind: Namespace
metadata:
  name: ia-logging
  labels:
    name: ia-logging
    app.kubernetes.io/name: ia-influencer-logging
    app.kubernetes.io/component: infrastructure
''',
            
            "elasticsearch.yaml": '''
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch
  namespace: ia-logging
spec:
  serviceName: elasticsearch
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
        ports:
        - containerPort: 9200
        env:
        - name: discovery.type
          value: single-node
        - name: ES_JAVA_OPTS
          value: "-Xms1g -Xmx1g"
        - name: xpack.security.enabled
          value: "false"
        volumeMounts:
        - name: es-data
          mountPath: /usr/share/elasticsearch/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: es-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
  namespace: ia-logging
spec:
  selector:
    app: elasticsearch
  ports:
  - port: 9200
    targetPort: 9200
  type: ClusterIP
''',
            
            "fluentd.yaml": '''
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: ia-logging
data:
  fluent.conf: |
    <system>
      workers 1
      root_dir /var/log/fluentd
      log_level info
    </system>
    
    <source>
      @type forward
      port 24224
      bind 0.0.0.0
    </source>
    
    <filter **>
      @type kubernetes_metadata_filter
      @id filter_kube_metadata
    </filter>
    
    <match **>
      @type elasticsearch
      host elasticsearch.ia-logging.svc.cluster.local
      port 9200
      index_name ia-influencer-logs
      type_name _doc
    </match>
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: ia-logging
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      serviceAccountName: fluentd
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1.16-debian-elasticsearch7-1
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch.ia-logging.svc.cluster.local"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        volumeMounts:
        - name: config-volume
          mountPath: /fluentd/etc
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: config-volume
        configMap:
          name: fluentd-config
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluentd
  namespace: ia-logging
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fluentd
rules:
- apiGroups: [""]
  resources: ["pods", "namespaces"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: fluentd
roleRef:
  kind: ClusterRole
  name: fluentd
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: ServiceAccount
  name: fluentd
  namespace: ia-logging
'''
        }


# Export configuration for easy import
DEFAULT_LOGGING_CONFIG = LoggingConfiguration.get_default_config()
