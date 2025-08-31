"""
 Monitoring Stack Docker Configuration - IA-Influencer-Agent Platform
=======================================================================
Expert: DevOps Engineer + Monitoring Specialist + Observability Expert
Creator: Fahed Mlaiel <mlaiel@live.de>
=======================================================================

  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL 
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional monitoring stack Docker configuration for comprehensive
observability, metrics collection, and alerting systems.
"""

from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass, field
import yaml
import json

logger = logging.getLogger(__name__)

@dataclass
class MonitoringStackDockerConfig:
    """Enterprise Monitoring Stack Docker configuration"""
    
    # Prometheus Configuration
    prometheus_image: str = "prom/prometheus:v2.48.0"
    prometheus_port: int = 9090
    prometheus_retention: str = "30d"
    prometheus_storage_size: str = "100Gi"
    
    # Grafana Configuration
    grafana_image: str = "grafana/grafana:10.2.2"
    grafana_port: int = 3000
    grafana_admin_user: str = "admin"
    grafana_admin_password: str = "secure_grafana_password"
    
    # AlertManager Configuration
    alertmanager_image: str = "prom/alertmanager:v0.26.0"
    alertmanager_port: int = 9093
    
    # Jaeger Configuration
    jaeger_image: str = "jaegertracing/all-in-one:1.51"
    jaeger_ui_port: int = 16686
    jaeger_collector_port: int = 14268
    jaeger_agent_port: int = 6831
    
    # Node Exporter Configuration
    node_exporter_image: str = "prom/node-exporter:v1.7.0"
    node_exporter_port: int = 9100
    
    # Loki Configuration
    loki_image: str = "grafana/loki:2.9.2"
    loki_port: int = 3100
    
    # Promtail Configuration
    promtail_image: str = "grafana/promtail:2.9.2"
    promtail_port: int = 9080
    
    # Environment Configuration
    environment: str = "production"
    retention_days: int = 30
    scrape_interval: str = "15s"
    evaluation_interval: str = "15s"
    
    # Alert Configuration
    alert_channels: Dict[str, bool] = field(default_factory=lambda: {
        "email": True,
        "slack": True,
        "webhook": True,
        "pagerduty": False
    })
    
    # Resource Limits
    prometheus_cpu_limit: str = "2000m"
    prometheus_memory_limit: str = "4Gi"
    grafana_cpu_limit: str = "1000m"
    grafana_memory_limit: str = "2Gi"
    
    def generate_prometheus_config(self) -> str:
        """Generate Prometheus configuration"""



        return f"""
# IA-Influencer Prometheus Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>

global:
  scrape_interval: {self.scrape_interval}
  evaluation_interval: {self.evaluation_interval}
  external_labels:
    environment: '{self.environment}'
    platform: 'ia-influencer'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:{self.alertmanager_port}

# Load rules once and periodically evaluate them
rule_files:
  - "/etc/prometheus/rules/*.yml"

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:{self.prometheus_port}']

  # Node Exporter
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:{self.node_exporter_port}']

  # Application metrics
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'backend-services'
    static_configs:
      - targets: ['backend-services:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'ai-engines'
    static_configs:
      - targets: ['ai-engines:9090']
    metrics_path: '/metrics'
    scrape_interval: 60s

  - job_name: 'fingerprinting-engine'
    static_configs:
      - targets: ['fingerprinting-engine:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'content-protection'
    static_configs:
      - targets: ['content-protection:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'monetization-engine'
    static_configs:
      - targets: ['monetization-engine:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # Database metrics
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s

  - job_name: 'elasticsearch-exporter'
    static_configs:
      - targets: ['elasticsearch-exporter:9114']
    scrape_interval: 30s

  # Infrastructure metrics
  - job_name: 'nginx-exporter'
    static_configs:
      - targets: ['nginx-exporter:9113']
    scrape_interval: 30s

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 30s
"""

    def generate_alert_rules(self) -> str:
        """Generate Prometheus alert rules"""



        return """
# IA-Influencer Alert Rules
# Creator: Fahed Mlaiel <mlaiel@live.de>

groups:
  - name: ia-influencer-services
    rules:
      # Service availability alerts
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          description: "{{ $labels.job }} on {{ $labels.instance }} has been down for more than 1 minute."

      # High response time alerts
      - alert: HighResponseTime
        expr: http_request_duration_seconds{quantile="0.95"} > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time on {{ $labels.instance }}"
          description: "95th percentile response time is {{ $value }}s for {{ $labels.instance }}"

      # High error rate alerts
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.instance }}"
          description: "Error rate is {{ $value }} requests/second for {{ $labels.instance }}"

  - name: ia-influencer-infrastructure
    rules:
      # High CPU usage
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is {{ $value }}% on {{ $labels.instance }}"

      # Low disk space
      - alert: LowDiskSpace
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk usage is {{ $value }}% on {{ $labels.instance }}"

  - name: ia-influencer-database
    rules:
      # Database connection issues
      - alert: PostgreSQLDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
          description: "PostgreSQL database on {{ $labels.instance }} is down"

      # High database connections
      - alert: HighDatabaseConnections
        expr: pg_stat_database_numbackends / pg_settings_max_connections * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database connections are at {{ $value }}% of maximum"

      # Slow database queries
      - alert: SlowDatabaseQueries
        expr: pg_stat_statements_mean_time_ms > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow database queries detected"
          description: "Average query time is {{ $value }}ms"

  - name: ia-influencer-business
    rules:
      # Content protection alerts
      - alert: HighViolationDetectionRate
        expr: rate(content_violations_detected_total[5m]) > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High content violation detection rate"
          description: "Detecting {{ $value }} violations per second"

      # Fingerprinting performance
      - alert: FingerprintingBacklog
        expr: fingerprinting_queue_size > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Fingerprinting queue backlog"
          description: "{{ $value }} items in fingerprinting queue"

      # Revenue tracking issues
      - alert: RevenueTrackingErrors
        expr: rate(revenue_tracking_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Revenue tracking errors"
          description: "{{ $value }} revenue tracking errors per second"
"""

    def generate_docker_compose_services(self) -> Dict[str, Any]:
        """Generate docker-compose services for monitoring stack"""
        services = {
            # Prometheus
            "prometheus": {
                "image": self.prometheus_image,
                "container_name": "ia-influencer-prometheus",
                "restart": "unless-stopped",
                "ports": [f"{self.prometheus_port}:{self.prometheus_port}"],
                "command": [
                    "--config.file=/etc/prometheus/prometheus.yml",
                    "--storage.tsdb.path=/prometheus",
                    f"--storage.tsdb.retention.time={self.prometheus_retention}",
                    "--web.console.libraries=/etc/prometheus/console_libraries",
                    "--web.console.templates=/etc/prometheus/consoles",
                    "--web.enable-lifecycle",
                    "--web.enable-admin-api"
                ],
                "volumes": [
                    "./config/prometheus:/etc/prometheus:ro",
                    "prometheus_data:/prometheus"
                ],
                "networks": ["ia-influencer-network"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": self.prometheus_cpu_limit,
                            "memory": self.prometheus_memory_limit
                        },
                        "reservations": {
                            "cpus": "1000m",
                            "memory": "2Gi"
                        }
                    }
                },
                "healthcheck": {
                    "test": f"wget --no-verbose --tries=1 --spider http://localhost:{self.prometheus_port}/-/healthy || exit 1",
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            },
            
            # Grafana
            "grafana": {
                "image": self.grafana_image,
                "container_name": "ia-influencer-grafana",
                "restart": "unless-stopped",
                "ports": [f"{self.grafana_port}:{self.grafana_port}"],
                "environment": {
                    "GF_SECURITY_ADMIN_USER": self.grafana_admin_user,
                    "GF_SECURITY_ADMIN_PASSWORD": self.grafana_admin_password,
                    "GF_USERS_ALLOW_SIGN_UP": "false",
                    "GF_INSTALL_PLUGINS": "grafana-piechart-panel,grafana-worldmap-panel,grafana-clock-panel",
                    "GF_SERVER_DOMAIN": "monitoring.ia-influencer.com",
                    "GF_SMTP_ENABLED": "true",
                    "GF_SMTP_HOST": "smtp.gmail.com:587",
                    "GF_SMTP_FROM_ADDRESS": "alerts@ia-influencer.com"
                },
                "volumes": [
                    "grafana_data:/var/lib/grafana",
                    "./config/grafana/provisioning:/etc/grafana/provisioning:ro",
                    "./config/grafana/dashboards:/var/lib/grafana/dashboards:ro"
                ],
                "networks": ["ia-influencer-network"],
                "depends_on": ["prometheus"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": self.grafana_cpu_limit,
                            "memory": self.grafana_memory_limit
                        },
                        "reservations": {
                            "cpus": "500m",
                            "memory": "1Gi"
                        }
                    }
                },
                "healthcheck": {
                    "test": f"curl -f http://localhost:{self.grafana_port}/api/health || exit 1",
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            },
            
            # AlertManager
            "alertmanager": {
                "image": self.alertmanager_image,
                "container_name": "ia-influencer-alertmanager",
                "restart": "unless-stopped",
                "ports": [f"{self.alertmanager_port}:{self.alertmanager_port}"],
                "command": [
                    "--config.file=/etc/alertmanager/alertmanager.yml",
                    "--storage.path=/alertmanager",
                    "--web.external-url=http://localhost:9093"
                ],
                "volumes": [
                    "./config/alertmanager:/etc/alertmanager:ro",
                    "alertmanager_data:/alertmanager"
                ],
                "networks": ["ia-influencer-network"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "500m",
                            "memory": "512Mi"
                        }
                    }
                }
            },
            
            # Jaeger
            "jaeger": {
                "image": self.jaeger_image,
                "container_name": "ia-influencer-jaeger",
                "restart": "unless-stopped",
                "ports": [
                    f"{self.jaeger_ui_port}:16686",
                    f"{self.jaeger_collector_port}:14268",
                    f"{self.jaeger_agent_port}:6831/udp"
                ],
                "environment": {
                    "COLLECTOR_OTLP_ENABLED": "true"
                },
                "networks": ["ia-influencer-network"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "1000m",
                            "memory": "1Gi"
                        }
                    }
                }
            },
            
            # Node Exporter
            "node-exporter": {
                "image": self.node_exporter_image,
                "container_name": "ia-influencer-node-exporter",
                "restart": "unless-stopped",
                "ports": [f"{self.node_exporter_port}:{self.node_exporter_port}"],
                "command": [
                    "--path.procfs=/host/proc",
                    "--path.rootfs=/rootfs",
                    "--path.sysfs=/host/sys",
                    "--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)"
                ],
                "volumes": [
                    "/proc:/host/proc:ro",
                    "/sys:/host/sys:ro",
                    "/:/rootfs:ro"
                ],
                "networks": ["ia-influencer-network"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "200m",
                            "memory": "256Mi"
                        }
                    }
                }
            },
            
            # Loki
            "loki": {
                "image": self.loki_image,
                "container_name": "ia-influencer-loki",
                "restart": "unless-stopped",
                "ports": [f"{self.loki_port}:{self.loki_port}"],
                "command": "-config.file=/etc/loki/local-config.yaml",
                "volumes": [
                    "./config/loki:/etc/loki:ro",
                    "loki_data:/loki"
                ],
                "networks": ["ia-influencer-network"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "1000m",
                            "memory": "1Gi"
                        }
                    }
                }
            },
            
            # Promtail
            "promtail": {
                "image": self.promtail_image,
                "container_name": "ia-influencer-promtail",
                "restart": "unless-stopped",
                "ports": [f"{self.promtail_port}:{self.promtail_port}"],
                "command": "-config.file=/etc/promtail/config.yml",
                "volumes": [
                    "./config/promtail:/etc/promtail:ro",
                    "./logs:/var/log:ro",
                    "/var/lib/docker/containers:/var/lib/docker/containers:ro"
                ],
                "networks": ["ia-influencer-network"],
                "depends_on": ["loki"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "500m",
                            "memory": "512Mi"
                        }
                    }
                }
            },
            
            # cAdvisor
            "cadvisor": {
                "image": "gcr.io/cadvisor/cadvisor:v0.47.2",
                "container_name": "ia-influencer-cadvisor",
                "restart": "unless-stopped",
                "ports": ["8080:8080"],
                "volumes": [
                    "/:/rootfs:ro",
                    "/var/run:/var/run:ro",
                    "/sys:/sys:ro",
                    "/var/lib/docker/:/var/lib/docker:ro",
                    "/dev/disk/:/dev/disk:ro"
                ],
                "networks": ["ia-influencer-network"],
                "privileged": True,
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "500m",
                            "memory": "512Mi"
                        }
                    }
                }
            }
        }
        
        return services

    def save_config_files(self, output_dir: str) -> List[str]:
        """Save all configuration files to output directory"""
        import os
        from pathlib import Path
        
        config_dir = Path(output_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Save Prometheus configuration
        prometheus_config_path = config_dir / "prometheus.yml"
        with open(prometheus_config_path, 'w') as f:
            f.write(self.generate_prometheus_config())
        files_created.append(str(prometheus_config_path))
        
        # Save alert rules
        alert_rules_path = config_dir / "alert_rules.yml"
        with open(alert_rules_path, 'w') as f:
            f.write(self.generate_alert_rules())
        files_created.append(str(alert_rules_path))
        
        # Save docker-compose service config
        compose_config_path = config_dir / "docker-compose.monitoring.yml"
        service_config = {
            "version": "3.8",
            "services": self.generate_docker_compose_services(),
            "volumes": {
                "prometheus_data": {},
                "grafana_data": {},
                "alertmanager_data": {},
                "loki_data": {}
            }
        }
        with open(compose_config_path, 'w') as f:
            yaml.dump(service_config, f, default_flow_style=False)
        files_created.append(str(compose_config_path))
        
        logger.info(f" Monitoring Stack configuration files saved: {files_created}")
        return files_created
