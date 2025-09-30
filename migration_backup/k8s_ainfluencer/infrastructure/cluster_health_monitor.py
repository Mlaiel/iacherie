"""Cluster Health Monitoring with Proactive Alerting
==================================================

Kubernetes cluster health monitoring with comprehensive metrics,
alerting, and proactive issue detection for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class MonitoringComponent(Enum):
    """Monitoring system components"""
    PROMETHEUS = "prometheus"
    ALERTMANAGER = "alertmanager"
    GRAFANA = "grafana"
    NODE_EXPORTER = "node-exporter"
    KUBE_STATE_METRICS = "kube-state-metrics"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    query: str
    duration: str
    severity: AlertSeverity
    summary: str
    description: str
    runbook_url: str = ""


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    namespace: str = "monitoring"
    cluster_name: str = "ia-influencer-cluster"
    retention_days: int = 30
    alert_retention_days: int = 7
    scrape_interval: str = "30s"
    evaluation_interval: str = "30s"


class ClusterHealthMonitor:
    """Manages cluster health monitoring and alerting"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alert_rules = self._initialize_alert_rules()
    
    def _initialize_alert_rules(self) -> List[AlertRule]:
        """Initialize comprehensive alert rules"""
        return [
            # Node-level alerts
            AlertRule(
                name="NodeDown",
                query='up{job="node-exporter"} == 0',
                duration="5m",
                severity=AlertSeverity.CRITICAL,
                summary="Node {{ $labels.instance }} is down",
                description="Node {{ $labels.instance }} has been down for more than 5 minutes",
                runbook_url="https://runbooks.ainflue.com/alerts/NodeDown"
            ),
            AlertRule(
                name="NodeHighCPUUsage",
                query='100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance) * 100) > 90',
                duration="10m",
                severity=AlertSeverity.WARNING,
                summary="High CPU usage on node {{ $labels.instance }}",
                description="CPU usage on node {{ $labels.instance }} is above 90% for more than 10 minutes"
            ),
            AlertRule(
                name="NodeHighMemoryUsage",
                query='(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90',
                duration="10m",
                severity=AlertSeverity.WARNING,
                summary="High memory usage on node {{ $labels.instance }}",
                description="Memory usage on node {{ $labels.instance }} is above 90% for more than 10 minutes"
            ),
            AlertRule(
                name="NodeDiskSpaceUsage",
                query='(1 - (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"})) * 100 > 90',
                duration="5m",
                severity=AlertSeverity.CRITICAL,
                summary="Low disk space on node {{ $labels.instance }}",
                description="Disk space usage on {{ $labels.instance }} is above 90%"
            ),
            
            # Kubernetes cluster alerts
            AlertRule(
                name="KubernetesApiServerDown",
                query='up{job="apiserver"} == 0',
                duration="1m",
                severity=AlertSeverity.CRITICAL,
                summary="Kubernetes API server is down",
                description="Kubernetes API server has been down for more than 1 minute"
            ),
            AlertRule(
                name="KubernetesNodeNotReady",
                query='kube_node_status_condition{condition="Ready",status="true"} == 0',
                duration="5m",
                severity=AlertSeverity.CRITICAL,
                summary="Kubernetes node {{ $labels.node }} is not ready",
                description="Kubernetes node {{ $labels.node }} has been in NotReady state for more than 5 minutes"
            ),
            AlertRule(
                name="KubernetesPodCrashLooping",
                query='rate(kube_pod_container_status_restarts_total[5m]) * 60 * 5 > 0',
                duration="5m",
                severity=AlertSeverity.WARNING,
                summary="Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping",
                description="Pod {{ $labels.namespace }}/{{ $labels.pod }} is restarting frequently"
            ),
            AlertRule(
                name="KubernetesPodNotRunning",
                query='kube_pod_status_phase{phase!="Running",phase!="Succeeded"} == 1',
                duration="5m",
                severity=AlertSeverity.WARNING,
                summary="Pod {{ $labels.namespace }}/{{ $labels.pod }} is not running",
                description="Pod {{ $labels.namespace }}/{{ $labels.pod }} has been in {{ $labels.phase }} phase for more than 5 minutes"
            ),
            AlertRule(
                name="KubernetesDeploymentReplicasMismatch",
                query='kube_deployment_spec_replicas != kube_deployment_status_replicas_available',
                duration="10m",
                severity=AlertSeverity.WARNING,
                summary="Deployment {{ $labels.namespace }}/{{ $labels.deployment }} has mismatched replicas",
                description="Deployment {{ $labels.namespace }}/{{ $labels.deployment }} has not matched desired replica count for more than 10 minutes"
            ),
            
            # Application-specific alerts
            AlertRule(
                name="HighErrorRate",
                query='rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1',
                duration="5m",
                severity=AlertSeverity.CRITICAL,
                summary="High error rate in {{ $labels.service }}",
                description="Error rate in {{ $labels.service }} is above 10% for more than 5 minutes"
            ),
            AlertRule(
                name="HighResponseTime",
                query='histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1',
                duration="10m",
                severity=AlertSeverity.WARNING,
                summary="High response time in {{ $labels.service }}",
                description="95th percentile response time in {{ $labels.service }} is above 1 second"
            ),
            
            # Storage alerts
            AlertRule(
                name="PersistentVolumeUsageHigh",
                query='kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes > 0.9',
                duration="5m",
                severity=AlertSeverity.WARNING,
                summary="Persistent volume {{ $labels.persistentvolumeclaim }} usage is high",
                description="Persistent volume {{ $labels.persistentvolumeclaim }} usage is above 90%"
            ),
            
            # ETCD alerts
            AlertRule(
                name="EtcdDown",
                query='up{job="etcd"} == 0',
                duration="1m",
                severity=AlertSeverity.CRITICAL,
                summary="ETCD instance {{ $labels.instance }} is down",
                description="ETCD instance {{ $labels.instance }} has been down for more than 1 minute"
            ),
            AlertRule(
                name="EtcdHighCommitDurations",
                query='histogram_quantile(0.99, rate(etcd_disk_wal_fsync_duration_seconds_bucket[5m])) > 0.5',
                duration="10m",
                severity=AlertSeverity.WARNING,
                summary="ETCD high commit durations",
                description="ETCD 99th percentile commit durations are above 500ms"
            )
        ]
    
    def create_prometheus_config(self) -> Dict[str, Any]:
        """Create Prometheus configuration"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "prometheus-config",
                "namespace": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "prometheus"
                }
            },
            "data": {
                "prometheus.yml": yaml.dump({
                    "global": {
                        "scrape_interval": self.config.scrape_interval,
                        "evaluation_interval": self.config.evaluation_interval,
                        "external_labels": {
                            "cluster": self.config.cluster_name,
                            "environment": "production"
                        }
                    },
                    "alerting": {
                        "alertmanagers": [
                            {
                                "static_configs": [
                                    {
                                        "targets": ["alertmanager:9093"]
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
                            "job_name": "kubernetes-apiservers",
                            "kubernetes_sd_configs": [
                                {
                                    "role": "endpoints"
                                }
                            ],
                            "scheme": "https",
                            "tls_config": {
                                "ca_file": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
                            },
                            "bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
                            "relabel_configs": [
                                {
                                    "source_labels": ["__meta_kubernetes_namespace", "__meta_kubernetes_service_name", "__meta_kubernetes_endpoint_port_name"],
                                    "action": "keep",
                                    "regex": "default;kubernetes;https"
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
                            "scheme": "https",
                            "tls_config": {
                                "ca_file": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
                            },
                            "bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
                            "relabel_configs": [
                                {
                                    "action": "labelmap",
                                    "regex": "__meta_kubernetes_node_label_(.+)"
                                }
                            ]
                        },
                        {
                            "job_name": "node-exporter",
                            "kubernetes_sd_configs": [
                                {
                                    "role": "endpoints"
                                }
                            ],
                            "relabel_configs": [
                                {
                                    "source_labels": ["__meta_kubernetes_endpoints_name"],
                                    "action": "keep",
                                    "regex": "node-exporter"
                                }
                            ]
                        },
                        {
                            "job_name": "kube-state-metrics",
                            "kubernetes_sd_configs": [
                                {
                                    "role": "endpoints"
                                }
                            ],
                            "relabel_configs": [
                                {
                                    "source_labels": ["__meta_kubernetes_service_name"],
                                    "action": "keep",
                                    "regex": "kube-state-metrics"
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
                                    "regex": True
                                },
                                {
                                    "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_path"],
                                    "action": "replace",
                                    "target_label": "__metrics_path__",
                                    "regex": "(.+)"
                                },
                                {
                                    "source_labels": ["__address__", "__meta_kubernetes_pod_annotation_prometheus_io_port"],
                                    "action": "replace",
                                    "regex": "([^:]+)(?::\\d+)?;(\\d+)",
                                    "replacement": "$1:$2",
                                    "target_label": "__address__"
                                }
                            ]
                        }
                    ]
                }, default_flow_style=False)
            }
        }
    
    def create_alert_rules_configmap(self) -> Dict[str, Any]:
        """Create ConfigMap with alert rules"""
        rules_data = {}
        
        # Group alerts by category
        alert_groups = {
            "node": [],
            "kubernetes": [],
            "application": [],
            "storage": [],
            "etcd": []
        }
        
        for rule in self.alert_rules:
            if "Node" in rule.name:
                alert_groups["node"].append(rule)
            elif "Kubernetes" in rule.name or "Kube" in rule.name:
                alert_groups["kubernetes"].append(rule)
            elif "Error" in rule.name or "Response" in rule.name:
                alert_groups["application"].append(rule)
            elif "Volume" in rule.name or "Storage" in rule.name:
                alert_groups["storage"].append(rule)
            elif "Etcd" in rule.name:
                alert_groups["etcd"].append(rule)
        
        for group_name, rules in alert_groups.items():
            if rules:
                rules_config = {
                    "groups": [
                        {
                            "name": f"{group_name}-alerts",
                            "rules": [
                                {
                                    "alert": rule.name,
                                    "expr": rule.query,
                                    "for": rule.duration,
                                    "labels": {
                                        "severity": rule.severity.value,
                                        "cluster": self.config.cluster_name
                                    },
                                    "annotations": {
                                        "summary": rule.summary,
                                        "description": rule.description,
                                        "runbook_url": rule.runbook_url
                                    }
                                }
                                for rule in rules
                            ]
                        }
                    ]
                }
                rules_data[f"{group_name}-alerts.yml"] = yaml.dump(rules_config, default_flow_style=False)
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "prometheus-alert-rules",
                "namespace": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "prometheus"
                }
            },
            "data": rules_data
        }
    
    def create_alertmanager_config(self) -> Dict[str, Any]:
        """Create Alertmanager configuration"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "alertmanager-config",
                "namespace": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "alertmanager"
                }
            },
            "data": {
                "alertmanager.yml": yaml.dump({
                    "global": {
                        "smtp_smarthost": "smtp.gmail.com:587",
                        "smtp_from": "alerts@ainflue.com",
                        "smtp_auth_username": "alerts@ainflue.com",
                        "smtp_auth_password": "${SMTP_PASSWORD}",
                        "slack_api_url": "${SLACK_WEBHOOK_URL}"
                    },
                    "templates": [
                        "/etc/alertmanager/templates/*.tmpl"
                    ],
                    "route": {
                        "group_by": ["alertname", "cluster", "service"],
                        "group_wait": "10s",
                        "group_interval": "10s",
                        "repeat_interval": "1h",
                        "receiver": "web.hook",
                        "routes": [
                            {
                                "match": {
                                    "severity": "critical"
                                },
                                "receiver": "critical-alerts",
                                "repeat_interval": "5m"
                            },
                            {
                                "match": {
                                    "severity": "warning"
                                },
                                "receiver": "warning-alerts",
                                "repeat_interval": "30m"
                            }
                        ]
                    },
                    "receivers": [
                        {
                            "name": "web.hook",
                            "webhook_configs": [
                                {
                                    "url": "http://webhook-receiver:9093/webhook"
                                }
                            ]
                        },
                        {
                            "name": "critical-alerts",
                            "email_configs": [
                                {
                                    "to": "ops-team@ainflue.com",
                                    "subject": "🚨 CRITICAL: {{ .GroupLabels.alertname }}",
                                    "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                                }
                            ],
                            "slack_configs": [
                                {
                                    "channel": "#alerts-critical",
                                    "title": "🚨 Critical Alert",
                                    "text": "{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}"
                                }
                            ]
                        },
                        {
                            "name": "warning-alerts",
                            "email_configs": [
                                {
                                    "to": "dev-team@ainflue.com",
                                    "subject": "⚠️ WARNING: {{ .GroupLabels.alertname }}",
                                    "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                                }
                            ],
                            "slack_configs": [
                                {
                                    "channel": "#alerts-warning",
                                    "title": "⚠️ Warning Alert",
                                    "text": "{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}"
                                }
                            ]
                        }
                    ],
                    "inhibit_rules": [
                        {
                            "source_match": {
                                "severity": "critical"
                            },
                            "target_match": {
                                "severity": "warning"
                            },
                            "equal": ["alertname", "cluster", "service"]
                        }
                    ]
                }, default_flow_style=False)
            }
        }
    
    def create_grafana_dashboards_configmap(self) -> Dict[str, Any]:
        """Create Grafana dashboards ConfigMap"""
        cluster_dashboard = {
            "dashboard": {
                "id": None,
                "title": "IA-Influencer Cluster Overview",
                "tags": ["kubernetes", "cluster"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Cluster Nodes",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "count(kube_node_info)",
                                "legendFormat": "Total Nodes"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Running Pods",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "count(kube_pod_info{phase=\"Running\"})",
                                "legendFormat": "Running Pods"
                            }
                        ]
                    },
                    {
                        "id": 3,
                        "title": "CPU Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
                                "legendFormat": "CPU Usage %"
                            }
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Memory Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
                                "legendFormat": "Memory Usage %"
                            }
                        ]
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "refresh": "30s"
            }
        }
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "grafana-dashboards",
                "namespace": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "grafana"
                }
            },
            "data": {
                "cluster-overview.json": yaml.dump(cluster_dashboard, default_flow_style=False)
            }
        }
    
    def generate_all_manifests(self) -> Dict[str, str]:
        """Generate all monitoring manifests"""
        manifests = {}
        
        # Prometheus configuration
        prometheus_config = self.create_prometheus_config()
        manifests["prometheus-config"] = yaml.dump(prometheus_config, default_flow_style=False)
        
        # Alert rules
        alert_rules = self.create_alert_rules_configmap()
        manifests["prometheus-alert-rules"] = yaml.dump(alert_rules, default_flow_style=False)
        
        # Alertmanager configuration
        alertmanager_config = self.create_alertmanager_config()
        manifests["alertmanager-config"] = yaml.dump(alertmanager_config, default_flow_style=False)
        
        # Grafana dashboards
        grafana_dashboards = self.create_grafana_dashboards_configmap()
        manifests["grafana-dashboards"] = yaml.dump(grafana_dashboards, default_flow_style=False)
        
        return manifests
    
    def save_manifests_to_files(self, output_dir: str = "./k8s-manifests/monitoring"):
        """Save all monitoring manifests to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        manifests = self.generate_all_manifests()
        
        for name, manifest in manifests.items():
            file_path = os.path.join(output_dir, f"{name}.yaml")
            with open(file_path, 'w') as f:
                f.write(manifest)
            logger.info(f"Monitoring manifest saved: {file_path}")
        
        return len(manifests)


# Export main functionality
__all__ = ['ClusterHealthMonitor', 'MonitoringConfig', 'AlertRule', 'AlertSeverity', 'MonitoringComponent']