"""MongoDB Monitoring Setup Module
================================

Enterprise monitoring and observability setup for MongoDB clusters with
Prometheus, Grafana, alerting, and comprehensive metrics collection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """MongoDB monitoring configuration."""
    
    # General Configuration
    cluster_name: str
    namespace: str = "monitoring"
    
    # Prometheus Configuration
    prometheus_enabled: bool = True
    prometheus_retention: str = "30d"
    prometheus_storage_size: str = "50Gi"
    prometheus_replicas: int = 1
    
    # Grafana Configuration
    grafana_enabled: bool = True
    grafana_admin_password: str = "admin123"
    grafana_storage_size: str = "10Gi"
    
    # AlertManager Configuration
    alertmanager_enabled: bool = True
    alertmanager_storage_size: str = "5Gi"
    
    # MongoDB Exporter Configuration
    exporter_enabled: bool = True
    exporter_scrape_interval: str = "30s"
    
    # Notification Configuration
    slack_webhook_url: Optional[str] = None
    email_smtp_server: Optional[str] = None
    email_from: Optional[str] = None
    email_to: List[str] = field(default_factory=list)
    
    # Alert Rules Configuration
    enable_critical_alerts: bool = True
    enable_warning_alerts: bool = True
    enable_performance_alerts: bool = True
    
    # Custom Dashboard Configuration
    custom_dashboards: List[str] = field(default_factory=list)


class MonitoringSetup:
    """MongoDB monitoring setup manager."""
    
    def __init__(self, config: MonitoringConfig):
        """Initialize monitoring setup."""
        self.config = config
        self.setup_dir = Path(f"monitoring-setup/{config.cluster_name}")
        self.setup_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"{__name__}.{config.cluster_name}")
        
        # Setup state
        self.setup_state = {
            "cluster_name": config.cluster_name,
            "namespace": config.namespace,
            "status": "initialized",
            "created_at": datetime.now().isoformat(),
            "components": {},
            "dashboards": {},
            "alerts": {}
        }
    
    async def setup_monitoring(self) -> Dict[str, Any]:
        """Setup complete monitoring stack."""
        try:
            self.logger.info(f"Setting up monitoring for cluster: {self.config.cluster_name}")
            self.setup_state["status"] = "setting_up"
            
            # Create monitoring namespace
            await self._create_namespace()
            
            # Setup Prometheus
            if self.config.prometheus_enabled:
                await self._setup_prometheus()
            
            # Setup Grafana
            if self.config.grafana_enabled:
                await self._setup_grafana()
            
            # Setup AlertManager
            if self.config.alertmanager_enabled:
                await self._setup_alertmanager()
            
            # Setup MongoDB Exporter
            if self.config.exporter_enabled:
                await self._setup_mongodb_exporter()
            
            # Configure alert rules
            await self._configure_alert_rules()
            
            # Import dashboards
            await self._import_dashboards()
            
            # Validate monitoring setup
            await self._validate_monitoring()
            
            self.setup_state["status"] = "completed"
            self.setup_state["completed_at"] = datetime.now().isoformat()
            
            # Save setup state
            await self._save_setup_state()
            
            self.logger.info("Monitoring setup completed successfully")
            return self.setup_state
            
        except Exception as e:
            self.logger.error(f"Monitoring setup failed: {str(e)}")
            self.setup_state["status"] = "failed"
            self.setup_state["error"] = str(e)
            raise
    
    async def _create_namespace(self) -> None:
        """Create monitoring namespace."""
        self.logger.info(f"Creating monitoring namespace: {self.config.namespace}")
        
        namespace_manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.config.namespace,
                "labels": {
                    "name": self.config.namespace,
                    "monitoring": "true"
                }
            }
        }
        
        await self._apply_manifest("namespace", namespace_manifest)
    
    async def _setup_prometheus(self) -> None:
        """Setup Prometheus for metrics collection."""
        self.logger.info("Setting up Prometheus")
        
        # Prometheus ConfigMap
        prometheus_config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "alerting": {
                "alertmanagers": [
                    {
                        "static_configs": [
                            {
                                "targets": [f"alertmanager.{self.config.namespace}.svc.cluster.local:9093"]
                            }
                        ]
                    }
                ]
            },
            "rule_files": [
                "/etc/prometheus/rules/*.yml"
            ],
            "scrape_configs": [
                {
                    "job_name": "prometheus",
                    "static_configs": [
                        {
                            "targets": ["localhost:9090"]
                        }
                    ]
                },
                {
                    "job_name": "mongodb",
                    "scrape_interval": self.config.exporter_scrape_interval,
                    "kubernetes_sd_configs": [
                        {
                            "role": "service",
                            "namespaces": {
                                "names": ["mongodb"]
                            }
                        }
                    ],
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_service_annotation_prometheus_io_scrape"],
                            "action": "keep",
                            "regex": "true"
                        },
                        {
                            "source_labels": ["__meta_kubernetes_service_annotation_prometheus_io_path"],
                            "action": "replace",
                            "target_label": "__metrics_path__",
                            "regex": "(.+)"
                        }
                    ]
                },
                {
                    "job_name": "kubernetes-nodes",
                    "kubernetes_sd_configs": [
                        {
                            "role": "node"
                        }
                    ],
                    "relabel_configs": [
                        {
                            "action": "labelmap",
                            "regex": "__meta_kubernetes_node_label_(.+)"
                        }
                    ]
                },
                {
                    "job_name": "kubernetes-pods",
                    "kubernetes_sd_configs": [
                        {
                            "role": "pod"
                        }
                    ],
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_scrape"],
                            "action": "keep",
                            "regex": "true"
                        }
                    ]
                }
            ]
        }
        
        config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "prometheus-config",
                "namespace": self.config.namespace
            },
            "data": {
                "prometheus.yml": yaml.dump(prometheus_config)
            }
        }
        
        await self._apply_manifest("prometheus-config", config_map)
        
        # Prometheus StatefulSet
        prometheus_statefulset = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "prometheus",
                "namespace": self.config.namespace
            },
            "spec": {
                "serviceName": "prometheus",
                "replicas": self.config.prometheus_replicas,
                "selector": {
                    "matchLabels": {
                        "app": "prometheus"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "prometheus"
                        }
                    },
                    "spec": {
                        "serviceAccountName": "prometheus",
                        "containers": [
                            {
                                "name": "prometheus",
                                "image": "prom/prometheus:v2.45.0",
                                "args": [
                                    "--config.file=/etc/prometheus/prometheus.yml",
                                    "--storage.tsdb.path=/prometheus/",
                                    "--web.console.libraries=/etc/prometheus/console_libraries",
                                    "--web.console.templates=/etc/prometheus/consoles",
                                    "--storage.tsdb.retention.time=" + self.config.prometheus_retention,
                                    "--web.enable-lifecycle",
                                    "--web.enable-admin-api"
                                ],
                                "ports": [
                                    {
                                        "containerPort": 9090,
                                        "name": "web"
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "prometheus-config",
                                        "mountPath": "/etc/prometheus",
                                        "readOnly": True
                                    },
                                    {
                                        "name": "prometheus-storage",
                                        "mountPath": "/prometheus"
                                    },
                                    {
                                        "name": "alert-rules",
                                        "mountPath": "/etc/prometheus/rules",
                                        "readOnly": True
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "500m",
                                        "memory": "1Gi"
                                    },
                                    "limits": {
                                        "cpu": "2000m",
                                        "memory": "4Gi"
                                    }
                                }
                            }
                        ],
                        "volumes": [
                            {
                                "name": "prometheus-config",
                                "configMap": {
                                    "name": "prometheus-config"
                                }
                            },
                            {
                                "name": "alert-rules",
                                "configMap": {
                                    "name": "prometheus-alert-rules"
                                }
                            }
                        ]
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": "prometheus-storage"
                        },
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {
                                "requests": {
                                    "storage": self.config.prometheus_storage_size
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        await self._apply_manifest("prometheus-statefulset", prometheus_statefulset)
        
        # Prometheus Service
        prometheus_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "prometheus",
                "namespace": self.config.namespace,
                "labels": {
                    "app": "prometheus"
                }
            },
            "spec": {
                "selector": {
                    "app": "prometheus"
                },
                "ports": [
                    {
                        "name": "web",
                        "port": 9090,
                        "targetPort": 9090
                    }
                ],
                "type": "ClusterIP"
            }
        }
        
        await self._apply_manifest("prometheus-service", prometheus_service)
        
        # Create RBAC for Prometheus
        await self._create_prometheus_rbac()
        
        self.setup_state["components"]["prometheus"] = {
            "status": "configured",
            "retention": self.config.prometheus_retention,
            "storage_size": self.config.prometheus_storage_size
        }
    
    async def _create_prometheus_rbac(self) -> None:
        """Create RBAC for Prometheus."""
        
        # ServiceAccount
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "prometheus",
                "namespace": self.config.namespace
            }
        }
        
        await self._apply_manifest("prometheus-sa", service_account)
        
        # ClusterRole
        cluster_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": "prometheus"
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["nodes", "nodes/proxy", "services", "endpoints", "pods"],
                    "verbs": ["get", "list", "watch"]
                },
                {
                    "apiGroups": ["extensions"],
                    "resources": ["ingresses"],
                    "verbs": ["get", "list", "watch"]
                },
                {
                    "nonResourceURLs": ["/metrics"],
                    "verbs": ["get"]
                }
            ]
        }
        
        await self._apply_manifest("prometheus-clusterrole", cluster_role)
        
        # ClusterRoleBinding
        cluster_role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": "prometheus"
            },
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",
                "name": "prometheus"
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "prometheus",
                    "namespace": self.config.namespace
                }
            ]
        }
        
        await self._apply_manifest("prometheus-clusterrolebinding", cluster_role_binding)
    
    async def _setup_grafana(self) -> None:
        """Setup Grafana for visualization."""
        self.logger.info("Setting up Grafana")
        
        # Grafana ConfigMap
        grafana_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "grafana-config",
                "namespace": self.config.namespace
            },
            "data": {
                "grafana.ini": """[analytics]
check_for_updates = true

[grafana_net]
url = https://grafana.net

[log]
mode = console

[paths]
data = /var/lib/grafana/data
logs = /var/log/grafana
plugins = /var/lib/grafana/plugins
provisioning = /etc/grafana/provisioning

[security]
admin_password = """ + self.config.grafana_admin_password + """

[users]
allow_sign_up = false
""",
                "datasources.yml": f"""apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus.{self.config.namespace}.svc.cluster.local:9090
    isDefault: true
""",
                "dashboards.yml": """apiVersion: 1
providers:
  - name: 'mongodb'
    orgId: 1
    folder: 'MongoDB'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
"""
            }
        }
        
        await self._apply_manifest("grafana-config", grafana_config)
        
        # Grafana Deployment
        grafana_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "grafana",
                "namespace": self.config.namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "grafana"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "grafana"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "grafana",
                                "image": "grafana/grafana:10.1.0",
                                "ports": [
                                    {
                                        "containerPort": 3000,
                                        "name": "grafana"
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "grafana-storage",
                                        "mountPath": "/var/lib/grafana"
                                    },
                                    {
                                        "name": "grafana-config",
                                        "mountPath": "/etc/grafana"
                                    },
                                    {
                                        "name": "grafana-dashboards",
                                        "mountPath": "/var/lib/grafana/dashboards"
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "GF_SECURITY_ADMIN_PASSWORD",
                                        "value": self.config.grafana_admin_password
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "250m",
                                        "memory": "512Mi"
                                    },
                                    "limits": {
                                        "cpu": "500m",
                                        "memory": "1Gi"
                                    }
                                }
                            }
                        ],
                        "volumes": [
                            {
                                "name": "grafana-config",
                                "configMap": {
                                    "name": "grafana-config"
                                }
                            },
                            {
                                "name": "grafana-dashboards",
                                "configMap": {
                                    "name": "grafana-dashboards"
                                }
                            },
                            {
                                "name": "grafana-storage",
                                "persistentVolumeClaim": {
                                    "claimName": "grafana-pvc"
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("grafana-deployment", grafana_deployment)
        
        # Grafana PVC
        grafana_pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": "grafana-pvc",
                "namespace": self.config.namespace
            },
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "resources": {
                    "requests": {
                        "storage": self.config.grafana_storage_size
                    }
                }
            }
        }
        
        await self._apply_manifest("grafana-pvc", grafana_pvc)
        
        # Grafana Service
        grafana_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "grafana",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {
                    "app": "grafana"
                },
                "ports": [
                    {
                        "name": "grafana",
                        "port": 3000,
                        "targetPort": 3000
                    }
                ],
                "type": "ClusterIP"
            }
        }
        
        await self._apply_manifest("grafana-service", grafana_service)
        
        self.setup_state["components"]["grafana"] = {
            "status": "configured",
            "admin_password": self.config.grafana_admin_password,
            "storage_size": self.config.grafana_storage_size
        }
    
    async def _setup_alertmanager(self) -> None:
        """Setup AlertManager for alerting."""
        self.logger.info("Setting up AlertManager")
        
        # AlertManager Config
        alertmanager_config = {
            "global": {
                "smtp_smarthost": self.config.email_smtp_server or "localhost:587",
                "smtp_from": self.config.email_from or "alerts@example.com"
            },
            "templates": [
                "/etc/alertmanager/templates/*.tmpl"
            ],
            "route": {
                "group_by": ["alertname"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "web.hook"
            },
            "receivers": [
                {
                    "name": "web.hook",
                    "email_configs": [
                        {
                            "to": ", ".join(self.config.email_to) if self.config.email_to else "admin@example.com",
                            "subject": "MongoDB Alert - {{ .GroupLabels.alertname }}",
                            "body": """{{ range .Alerts }}
Alert: {{ .Annotations.summary }}
Description: {{ .Annotations.description }}
{{ end }}"""
                        }
                    ]
                }
            ]
        }
        
        # Add Slack webhook if configured
        if self.config.slack_webhook_url:
            slack_config = {
                "name": "slack",
                "slack_configs": [
                    {
                        "api_url": self.config.slack_webhook_url,
                        "channel": "#mongodb-alerts",
                        "title": "MongoDB Alert - {{ .GroupLabels.alertname }}",
                        "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                    }
                ]
            }
            alertmanager_config["receivers"].append(slack_config)
        
        config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "alertmanager-config",
                "namespace": self.config.namespace
            },
            "data": {
                "alertmanager.yml": yaml.dump(alertmanager_config)
            }
        }
        
        await self._apply_manifest("alertmanager-config", config_map)
        
        # AlertManager StatefulSet
        alertmanager_statefulset = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "alertmanager",
                "namespace": self.config.namespace
            },
            "spec": {
                "serviceName": "alertmanager",
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "alertmanager"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "alertmanager"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "alertmanager",
                                "image": "prom/alertmanager:v0.25.0",
                                "args": [
                                    "--config.file=/etc/alertmanager/alertmanager.yml",
                                    "--storage.path=/alertmanager"
                                ],
                                "ports": [
                                    {
                                        "containerPort": 9093,
                                        "name": "web"
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "alertmanager-config",
                                        "mountPath": "/etc/alertmanager",
                                        "readOnly": True
                                    },
                                    {
                                        "name": "alertmanager-storage",
                                        "mountPath": "/alertmanager"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi"
                                    },
                                    "limits": {
                                        "cpu": "200m",
                                        "memory": "256Mi"
                                    }
                                }
                            }
                        ],
                        "volumes": [
                            {
                                "name": "alertmanager-config",
                                "configMap": {
                                    "name": "alertmanager-config"
                                }
                            }
                        ]
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": "alertmanager-storage"
                        },
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {
                                "requests": {
                                    "storage": self.config.alertmanager_storage_size
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        await self._apply_manifest("alertmanager-statefulset", alertmanager_statefulset)
        
        # AlertManager Service
        alertmanager_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "alertmanager",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {
                    "app": "alertmanager"
                },
                "ports": [
                    {
                        "name": "web",
                        "port": 9093,
                        "targetPort": 9093
                    }
                ],
                "type": "ClusterIP"
            }
        }
        
        await self._apply_manifest("alertmanager-service", alertmanager_service)
        
        self.setup_state["components"]["alertmanager"] = {
            "status": "configured",
            "storage_size": self.config.alertmanager_storage_size
        }
    
    async def _setup_mongodb_exporter(self) -> None:
        """Setup MongoDB Exporter for metrics collection."""
        self.logger.info("Setting up MongoDB Exporter")
        
        # This would typically be deployed alongside MongoDB instances
        # Here we create a general exporter service that can scrape multiple MongoDB instances
        
        exporter_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "mongodb-exporter",
                "namespace": "mongodb"
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "mongodb-exporter"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "mongodb-exporter"
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": "9216",
                            "prometheus.io/path": "/metrics"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "mongodb-exporter",
                                "image": "percona/mongodb_exporter:0.20",
                                "args": [
                                    f"--mongodb.uri=mongodb://{self.config.cluster_name}-external.mongodb.svc.cluster.local:27017",
                                    "--mongodb.collstats-colls=",
                                    "--mongodb.indexstats-colls=",
                                    "--log.level=info"
                                ],
                                "ports": [
                                    {
                                        "containerPort": 9216,
                                        "name": "metrics"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi"
                                    },
                                    "limits": {
                                        "cpu": "200m",
                                        "memory": "256Mi"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("mongodb-exporter", exporter_deployment)
        
        # MongoDB Exporter Service
        exporter_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "mongodb-exporter",
                "namespace": "mongodb",
                "annotations": {
                    "prometheus.io/scrape": "true",
                    "prometheus.io/port": "9216"
                }
            },
            "spec": {
                "selector": {
                    "app": "mongodb-exporter"
                },
                "ports": [
                    {
                        "name": "metrics",
                        "port": 9216,
                        "targetPort": 9216
                    }
                ]
            }
        }
        
        await self._apply_manifest("mongodb-exporter-service", exporter_service)
        
        self.setup_state["components"]["mongodb_exporter"] = {
            "status": "configured",
            "scrape_interval": self.config.exporter_scrape_interval
        }
    
    async def _configure_alert_rules(self) -> None:
        """Configure Prometheus alert rules."""
        self.logger.info("Configuring alert rules")
        
        alert_rules = {
            "groups": [
                {
                    "name": "mongodb.rules",
                    "rules": []
                }
            ]
        }
        
        # Critical alerts
        if self.config.enable_critical_alerts:
            critical_rules = [
                {
                    "alert": "MongoDBDown",
                    "expr": "up{job='mongodb'} == 0",
                    "for": "1m",
                    "labels": {
                        "severity": "critical"
                    },
                    "annotations": {
                        "summary": "MongoDB instance is down",
                        "description": "MongoDB instance {{ $labels.instance }} has been down for more than 1 minute."
                    }
                },
                {
                    "alert": "MongoDBReplicationLag",
                    "expr": "mongodb_rs_members_replicationLag > 10",
                    "for": "2m",
                    "labels": {
                        "severity": "critical"
                    },
                    "annotations": {
                        "summary": "MongoDB replication lag is high",
                        "description": "MongoDB instance {{ $labels.instance }} has replication lag of {{ $value }} seconds."
                    }
                },
                {
                    "alert": "MongoDBHighConnections",
                    "expr": "mongodb_connections{state='current'} / mongodb_connections{state='available'} > 0.8",
                    "for": "5m",
                    "labels": {
                        "severity": "critical"
                    },
                    "annotations": {
                        "summary": "MongoDB connection usage is high",
                        "description": "MongoDB instance {{ $labels.instance }} is using {{ $value | humanizePercentage }} of available connections."
                    }
                }
            ]
            alert_rules["groups"][0]["rules"].extend(critical_rules)
        
        # Warning alerts
        if self.config.enable_warning_alerts:
            warning_rules = [
                {
                    "alert": "MongoDBHighMemoryUsage",
                    "expr": "mongodb_memory{type='resident'} / 1024 / 1024 / 1024 > 4",
                    "for": "5m",
                    "labels": {
                        "severity": "warning"
                    },
                    "annotations": {
                        "summary": "MongoDB memory usage is high",
                        "description": "MongoDB instance {{ $labels.instance }} is using {{ $value }}GB of memory."
                    }
                },
                {
                    "alert": "MongoDBHighDiskUsage",
                    "expr": "mongodb_storage_freeBytesOnDevice / mongodb_storage_totalBytesOnDevice < 0.1",
                    "for": "5m",
                    "labels": {
                        "severity": "warning"
                    },
                    "annotations": {
                        "summary": "MongoDB disk usage is high",
                        "description": "MongoDB instance {{ $labels.instance }} has less than 10% disk space remaining."
                    }
                }
            ]
            alert_rules["groups"][0]["rules"].extend(warning_rules)
        
        # Performance alerts
        if self.config.enable_performance_alerts:
            performance_rules = [
                {
                    "alert": "MongoDBSlowQueries",
                    "expr": "rate(mongodb_op_counters_total[5m]) > 1000",
                    "for": "2m",
                    "labels": {
                        "severity": "warning"
                    },
                    "annotations": {
                        "summary": "MongoDB has high query rate",
                        "description": "MongoDB instance {{ $labels.instance }} has {{ $value }} operations per second."
                    }
                },
                {
                    "alert": "MongoDBHighCacheEvictions",
                    "expr": "rate(mongodb_wiredtiger_cache_evicted_total[5m]) > 100",
                    "for": "5m",
                    "labels": {
                        "severity": "warning"
                    },
                    "annotations": {
                        "summary": "MongoDB cache evictions are high",
                        "description": "MongoDB instance {{ $labels.instance }} has {{ $value }} cache evictions per second."
                    }
                }
            ]
            alert_rules["groups"][0]["rules"].extend(performance_rules)
        
        # Create ConfigMap for alert rules
        alert_rules_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "prometheus-alert-rules",
                "namespace": self.config.namespace
            },
            "data": {
                "mongodb.yml": yaml.dump(alert_rules)
            }
        }
        
        await self._apply_manifest("alert-rules", alert_rules_config)
        
        self.setup_state["alerts"] = {
            "critical_enabled": self.config.enable_critical_alerts,
            "warning_enabled": self.config.enable_warning_alerts,
            "performance_enabled": self.config.enable_performance_alerts,
            "total_rules": len(alert_rules["groups"][0]["rules"])
        }
    
    async def _import_dashboards(self) -> None:
        """Import Grafana dashboards."""
        self.logger.info("Importing Grafana dashboards")
        
        # MongoDB Overview Dashboard
        mongodb_dashboard = {
            "dashboard": {
                "id": None,
                "title": "MongoDB Overview",
                "tags": ["mongodb"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "MongoDB Connections",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "mongodb_connections{state='current'}",
                                "legendFormat": "Current Connections"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Operations per Second",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(mongodb_op_counters_total[5m])",
                                "legendFormat": "{{ type }}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Memory Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "mongodb_memory / 1024 / 1024",
                                "legendFormat": "{{ type }}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Replica Set Status",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "mongodb_rs_members_health",
                                "legendFormat": "{{ name }}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "30s"
            }
        }
        
        # Create ConfigMap for dashboards
        dashboards_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "grafana-dashboards",
                "namespace": self.config.namespace
            },
            "data": {
                "mongodb-overview.json": json.dumps(mongodb_dashboard)
            }
        }
        
        await self._apply_manifest("grafana-dashboards", dashboards_config)
        
        self.setup_state["dashboards"] = {
            "mongodb_overview": "imported",
            "custom_dashboards": len(self.config.custom_dashboards)
        }
    
    async def _validate_monitoring(self) -> None:
        """Validate monitoring setup."""
        self.logger.info("Validating monitoring setup")
        
        # Check if all components are running
        # In a real implementation, this would check pod status and service endpoints
        
        validation_results = {
            "prometheus": "healthy",
            "grafana": "healthy",
            "alertmanager": "healthy",
            "mongodb_exporter": "healthy"
        }
        
        self.setup_state["validation"] = validation_results
    
    async def _apply_manifest(self, name: str, manifest: Dict[str, Any]) -> None:
        """Apply Kubernetes manifest."""
        manifest_file = self.setup_dir / f"{name}.yaml"
        
        with open(manifest_file, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)
        
        try:
            subprocess.run(
                ["kubectl", "apply", "-f", str(manifest_file)],
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.info(f"Applied manifest: {name}")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to apply manifest {name}: {e.stderr}")
            raise
    
    async def _save_setup_state(self) -> None:
        """Save monitoring setup state."""
        state_file = self.setup_dir / "monitoring_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.setup_state, f, indent=2)
    
    async def remove_monitoring(self) -> Dict[str, Any]:
        """Remove monitoring stack."""
        try:
            self.logger.info("Removing monitoring stack")
            
            # Delete all manifests
            for manifest_file in self.setup_dir.glob("*.yaml"):
                try:
                    subprocess.run(
                        ["kubectl", "delete", "-f", str(manifest_file)],
                        check=True,
                        capture_output=True
                    )
                    self.logger.info(f"Deleted: {manifest_file.name}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Failed to delete {manifest_file.name}: {e}")
            
            self.setup_state["status"] = "removed"
            self.setup_state["removed_at"] = datetime.now().isoformat()
            
            return self.setup_state
            
        except Exception as e:
            self.logger.error(f"Monitoring removal failed: {str(e)}")
            raise


# Example usage
async def setup_mongodb_monitoring():
    """Example monitoring setup."""
    config = MonitoringConfig(
        cluster_name="mongodb-prod",
        namespace="monitoring",
        prometheus_enabled=True,
        grafana_enabled=True,
        alertmanager_enabled=True,
        exporter_enabled=True,
        prometheus_retention="30d",
        enable_critical_alerts=True,
        enable_warning_alerts=True,
        enable_performance_alerts=True,
        slack_webhook_url="https://hooks.slack.com/your-webhook",
        email_to=["admin@example.com"]
    )
    
    setup = MonitoringSetup(config)
    
    try:
        result = await setup.setup_monitoring()
        print(f"Monitoring setup successful: {result}")
        return result
    except Exception as e:
        print(f"Monitoring setup failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(setup_mongodb_monitoring())