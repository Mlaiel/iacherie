"""Infrastructure Monitoring Configuration for IA-Influencer Agent Platform
=========================================================================

Professional infrastructure monitoring configuration for comprehensive
platform infrastructure monitoring with advanced alerting and automation.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import logging
import psutil
import asyncio
import aiohttp
from collections import defaultdict


class InfrastructureLayer(Enum):
    """
Infrastructure monitoring layers"""

    HARDWARE = "hardware"
    OPERATING_SYSTEM = "operating_system"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    APPLICATION = "application"
    NETWORK = "network"
    STORAGE = "storage"
    DATABASE = "database"


class ResourceType(Enum):
    """Infrastructure resource types"""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    CONTAINER = "container"
    POD = "pod"
    SERVICE = "service"
    VOLUME = "volume"


class MonitoringCollectorType(Enum):
    """Monitoring collector types"""

    NODE_EXPORTER = "node_exporter"
    CADVISOR = "cadvisor"
    KUBERNETES_STATE = "kubernetes_state"
    CUSTOM_EXPORTER = "custom_exporter"
    SNMP = "snmp"
    AGENT = "agent"


@dataclass
class InfrastructureTarget:
    """Infrastructure monitoring target"""
    name: str
    target_type: str
    endpoint: str
    layer: InfrastructureLayer
    labels: Dict[str, str] = field(default_factory=dict)
    scrape_interval: str = "15s"
    scrape_timeout: str = "10s"
    metrics_path: str = "/metrics"
    enabled: bool = True
    authentication: Optional[Dict[str, str]] = None


@dataclass
class ResourceThreshold:
    """Resource monitoring threshold"""
    resource_type: ResourceType
    warning_threshold: float
    critical_threshold: float
    unit: str
    evaluation_period: str = "5m"
    comparison_operator: str = ">"  # >, <, ==, >=, <=


@dataclass
class InfrastructureAlert:
    """Infrastructure alert rule"""
    name: str
    description: str
    expression: str
    severity: str
    duration: str = "5m"
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True


class InfrastructureMonitoringConfig:
    """
    Professional infrastructure monitoring configuration
    
    Manages comprehensive infrastructure monitoring including hardware,
    containers, Kubernetes, databases, and network components with
    advanced alerting and automated remediation capabilities.
    """
    
    def __init__(self):
        """
Initialize infrastructure monitoring configuration"""
        self._targets = {}
        self._thresholds = {}
        self._alert_rules = {}
        self._collectors = {}
        
        # Configuration from environment
        self.config = {
            "cluster_name": os.getenv("CLUSTER_NAME", "ia-influencer-cluster"),
            "environment": os.getenv("ENVIRONMENT", "production"),
            "region": os.getenv("AWS_REGION", "eu-central-1"),
            "availability_zone": os.getenv("AZ", "eu-central-1a"),
            
            # Monitoring endpoints
            "prometheus_endpoint": os.getenv("PROMETHEUS_ENDPOINT", "http://prometheus:9090"),
            "alertmanager_endpoint": os.getenv("ALERTMANAGER_ENDPOINT", "http://alertmanager:9093"),
            "grafana_endpoint": os.getenv("GRAFANA_ENDPOINT", "http://grafana:3000"),
            
            # Collection settings
            "global_scrape_interval": os.getenv("GLOBAL_SCRAPE_INTERVAL", "15s"),
            "global_evaluation_interval": os.getenv("GLOBAL_EVALUATION_INTERVAL", "15s"),
            "scrape_timeout": os.getenv("SCRAPE_TIMEOUT", "10s"),
            
            # Retention settings
            "metrics_retention": os.getenv("METRICS_RETENTION", "30d"),
            "alerting_retention": os.getenv("ALERTING_RETENTION", "5d"),
            
            # Storage configuration
            "storage_path": os.getenv("PROMETHEUS_STORAGE_PATH", "/prometheus/data"),
            "max_block_duration": os.getenv("MAX_BLOCK_DURATION", "2h"),
            "min_block_duration": os.getenv("MIN_BLOCK_DURATION", "2h"),
            
            # Performance settings
            "query_max_concurrency": int(os.getenv("QUERY_MAX_CONCURRENCY", "20")),
            "query_timeout": os.getenv("QUERY_TIMEOUT", "2m"),
            "max_samples_per_query": int(os.getenv("MAX_SAMPLES_PER_QUERY", "50000000")),
        }
        
        self._setup_infrastructure_targets()
        self._setup_resource_thresholds()
        self._setup_infrastructure_alerts()
        self._setup_collectors()
    
    def _setup_infrastructure_targets(self):
        """Setup infrastructure monitoring targets"""
        # Kubernetes cluster monitoring
        self.register_target(InfrastructureTarget(
            name="kube-state-metrics",
            target_type="kubernetes_metrics",
            endpoint="kube-state-metrics:8080",
            layer=InfrastructureLayer.KUBERNETES,
            labels={
                "job": "kube-state-metrics",
                "cluster": self.config["cluster_name"]
            },
            scrape_interval="30s",
            metrics_path="/metrics"
        ))
        
        self.register_target(InfrastructureTarget(
            name="kubernetes-apiserver",
            target_type="kubernetes_api",
            endpoint="kubernetes.default.svc:443",
            layer=InfrastructureLayer.KUBERNETES,
            labels={
                "job": "kubernetes-apiserver",
                "cluster": self.config["cluster_name"]
            },
            scrape_interval="30s",
            metrics_path="/metrics",
            authentication={"bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token"}
        ))
        
        # Node monitoring
        self.register_target(InfrastructureTarget(
            name="node-exporter",
            target_type="system_metrics",
            endpoint="node-exporter:9100",
            layer=InfrastructureLayer.OPERATING_SYSTEM,
            labels={
                "job": "node-exporter",
                "cluster": self.config["cluster_name"]
            },
            scrape_interval="15s",
            metrics_path="/metrics"
        ))
        
        # Container monitoring
        self.register_target(InfrastructureTarget(
            name="cadvisor",
            target_type="container_metrics",
            endpoint="cadvisor:8080",
            layer=InfrastructureLayer.CONTAINER,
            labels={
                "job": "cadvisor",
                "cluster": self.config["cluster_name"]
            },
            scrape_interval="15s",
            metrics_path="/metrics"
        ))
        
        # Database monitoring
        self.register_target(InfrastructureTarget(
            name="postgres-exporter",
            target_type="database_metrics",
            endpoint="postgres-exporter:9187",
            layer=InfrastructureLayer.DATABASE,
            labels={
                "job": "postgres-exporter",
                "database": "postgresql"
            },
            scrape_interval="30s",
            metrics_path="/metrics"
        ))
        
        self.register_target(InfrastructureTarget(
            name="redis-exporter",
            target_type="cache_metrics",
            endpoint="redis-exporter:9121",
            layer=InfrastructureLayer.DATABASE,
            labels={
                "job": "redis-exporter",
                "database": "redis"
            },
            scrape_interval="30s",
            metrics_path="/metrics"
        ))
        
        # Application monitoring
        self.register_target(InfrastructureTarget(
            name="api-gateway",
            target_type="application_metrics",
            endpoint="api-gateway:8080",
            layer=InfrastructureLayer.APPLICATION,
            labels={
                "job": "api-gateway",
                "service": "api-gateway",
                "tier": "frontend"
            },
            scrape_interval="15s",
            metrics_path="/metrics"
        ))
        
        self.register_target(InfrastructureTarget(
            name="ai-processing-service",
            target_type="application_metrics",
            endpoint="ai-processing:8081",
            layer=InfrastructureLayer.APPLICATION,
            labels={
                "job": "ai-processing",
                "service": "ai-processing",
                "tier": "backend"
            },
            scrape_interval="15s",
            metrics_path="/metrics"
        ))
        
        self.register_target(InfrastructureTarget(
            name="content-protection-service",
            target_type="application_metrics",
            endpoint="content-protection:8082",
            layer=InfrastructureLayer.APPLICATION,
            labels={
                "job": "content-protection",
                "service": "content-protection",
                "tier": "backend"
            },
            scrape_interval="20s",
            metrics_path="/metrics"
        ))
        
        # Network monitoring
        self.register_target(InfrastructureTarget(
            name="blackbox-exporter",
            target_type="network_probe",
            endpoint="blackbox-exporter:9115",
            layer=InfrastructureLayer.NETWORK,
            labels={
                "job": "blackbox",
                "probe_type": "http_2xx"
            },
            scrape_interval="30s",
            metrics_path="/probe"
        ))
        
        # Storage monitoring
        self.register_target(InfrastructureTarget(
            name="minio-exporter",
            target_type="storage_metrics",
            endpoint="minio:9000",
            layer=InfrastructureLayer.STORAGE,
            labels={
                "job": "minio",
                "storage": "object_storage"
            },
            scrape_interval="60s",
            metrics_path="/minio/v2/metrics/cluster"
        ))
    
    def _setup_resource_thresholds(self):
        """Setup resource monitoring thresholds"""
        # CPU thresholds
        self.register_threshold(ResourceThreshold(
            resource_type=ResourceType.CPU,
            warning_threshold=70.0,
            critical_threshold=90.0,
            unit="percent",
            evaluation_period="5m"
        ))
        
        # Memory thresholds
        self.register_threshold(ResourceThreshold(
            resource_type=ResourceType.MEMORY,
            warning_threshold=80.0,
            critical_threshold=95.0,
            unit="percent",
            evaluation_period="5m"
        ))
        
        # Disk thresholds
        self.register_threshold(ResourceThreshold(
            resource_type=ResourceType.DISK,
            warning_threshold=80.0,
            critical_threshold=90.0,
            unit="percent",
            evaluation_period="5m"
        ))
        
        # Network thresholds (bytes per second)
        self.register_threshold(ResourceThreshold(
            resource_type=ResourceType.NETWORK,
            warning_threshold=100000000,  # 100MB/s
            critical_threshold=1000000000,  # 1GB/s
            unit="bytes_per_second",
            evaluation_period="2m"
        ))
        
        # Container resource thresholds
        self.register_threshold(ResourceThreshold(
            resource_type=ResourceType.CONTAINER,
            warning_threshold=0.8,  # 80% of limit
            critical_threshold=0.95,  # 95% of limit
            unit="ratio",
            evaluation_period="5m"
        ))
    
    def _setup_infrastructure_alerts(self):
        """Setup infrastructure alert rules"""
        # Node alerts
        self.register_alert_rule(InfrastructureAlert(
            name="NodeDown",
            description="Node has been down for more than 5 minutes",
            expression='up{job="node-exporter"} == 0',
            severity="critical",
            duration="5m",
            labels={"category": "infrastructure", "component": "node"},
            annotations={
                "summary": "Node {{ $labels.instance }} is down",
                "description": "Node {{ $labels.instance }} has been down for more than 5 minutes."
            }
        ))
        
        self.register_alert_rule(InfrastructureAlert(
            name="HighCPUUsage",
            description="High CPU usage detected",
            expression='100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90',
            severity="warning",
            duration="10m",
            labels={"category": "performance", "resource": "cpu"},
            annotations={
                "summary": "High CPU usage on {{ $labels.instance }}",
                "description": "CPU usage is above 90% for more than 10 minutes on {{ $labels.instance }}."
            }
        ))
        
        self.register_alert_rule(InfrastructureAlert(
            name="HighMemoryUsage",
            description="High memory usage detected",
            expression='(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90',
            severity="warning",
            duration="10m",
            labels={"category": "performance", "resource": "memory"},
            annotations={
                "summary": "High memory usage on {{ $labels.instance }}",
                "description": "Memory usage is above 90% on {{ $labels.instance }}."
            }
        ))
        
        self.register_alert_rule(InfrastructureAlert(
            name="DiskSpaceLow",
            description="Disk space is running low",
            expression='(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10',
            severity="warning",
            duration="5m",
            labels={"category": "storage", "resource": "disk"},
            annotations={
                "summary": "Disk space low on {{ $labels.instance }}",
                "description": "Disk space is below 10% on {{ $labels.instance }} mount {{ $labels.mountpoint }}."
            }
        ))
        
        # Kubernetes alerts
        self.register_alert_rule(InfrastructureAlert(
            name="KubernetesPodCrashLooping",
            description="Pod is crash looping",
            expression='rate(kube_pod_container_status_restarts_total[15m]) > 0',
            severity="warning",
            duration="5m",
            labels={"category": "kubernetes", "component": "pod"},
            annotations={
                "summary": "Pod {{ $labels.pod }} is crash looping",
                "description": "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is crash looping."
            }
        ))
        
        self.register_alert_rule(InfrastructureAlert(
            name="KubernetesNodeNotReady",
            description="Kubernetes node is not ready",
            expression='kube_node_status_condition{condition="Ready",status="true"} == 0',
            severity="critical",
            duration="10m",
            labels={"category": "kubernetes", "component": "node"},
            annotations={
                "summary": "Kubernetes node {{ $labels.node }} is not ready",
                "description": "Kubernetes node {{ $labels.node }} has been not ready for more than 10 minutes."
            }
        ))
        
        # Database alerts
        self.register_alert_rule(InfrastructureAlert(
            name="PostgreSQLDown",
            description="PostgreSQL is down",
            expression='pg_up == 0',
            severity="critical",
            duration="2m",
            labels={"category": "database", "component": "postgresql"},
            annotations={
                "summary": "PostgreSQL is down on {{ $labels.instance }}",
                "description": "PostgreSQL database is down on {{ $labels.instance }}."
            }
        ))
        
        self.register_alert_rule(InfrastructureAlert(
            name="RedisDown",
            description="Redis is down",
            expression='redis_up == 0',
            severity="critical",
            duration="2m",
            labels={"category": "database", "component": "redis"},
            annotations={
                "summary": "Redis is down on {{ $labels.instance }}",
                "description": "Redis cache is down on {{ $labels.instance }}."
            }
        ))
        
        # Application alerts
        self.register_alert_rule(InfrastructureAlert(
            name="HighHTTPErrorRate",
            description="High HTTP error rate detected",
            expression='rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05',
            severity="warning",
            duration="5m",
            labels={"category": "application", "component": "api"},
            annotations={
                "summary": "High HTTP error rate on {{ $labels.job }}",
                "description": "HTTP error rate is above 5% for {{ $labels.job }}."
            }
        ))
        
        # Network alerts
        self.register_alert_rule(InfrastructureAlert(
            name="ServiceDown",
            description="Service endpoint is down",
            expression='probe_success == 0',
            severity="critical",
            duration="2m",
            labels={"category": "network", "component": "service"},
            annotations={
                "summary": "Service {{ $labels.instance }} is down",
                "description": "Service {{ $labels.instance }} has been down for more than 2 minutes."
            }
        ))
    
    def _setup_collectors(self):
        """Setup monitoring collectors configuration"""
        self._collectors = {
            "node_exporter": {
                "type": MonitoringCollectorType.NODE_EXPORTER,
                "version": "1.6.1",
                "port": 9100,
                "enabled_collectors": [
                    "cpu", "diskstats", "filesystem", "loadavg", "meminfo",
                    "netdev", "netstat", "stat", "time", "uname", "vmstat"
                ],
                "disabled_collectors": ["arp", "bcache", "bonding"],
                "collector_args": {
                    "filesystem.ignored-mount-points": "^/(dev|proc|sys|var/lib/docker/.+)($|/)",
                    "filesystem.ignored-fs-types": "^(autofs|binfmt_misc|bpf|cgroup2?|configfs|debugfs|devpts|devtmpfs|fusectl|hugetlbfs|iso9660|mqueue|nsfs|overlay|proc|procfs|pstore|rpc_pipefs|securityfs|selinuxfs|squashfs|sysfs|tracefs)$"
                }
            },
            "cadvisor": {
                "type": MonitoringCollectorType.CADVISOR,
                "version": "0.47.0",
                "port": 8080,
                "housekeeping_interval": "10s",
                "max_housekeeping_interval": "15s",
                "enable_load_reader": True,
                "docker_only": False,
                "store_container_labels": True
            },
            "postgres_exporter": {
                "type": MonitoringCollectorType.CUSTOM_EXPORTER,
                "version": "0.12.0",
                "port": 9187,
                "data_source_name": os.getenv("POSTGRES_EXPORTER_DSN", "postgresql://postgres:password@localhost:5432/postgres?sslmode=disable"),
                "query_timeout": "5s",
                "disable_default_metrics": False,
                "custom_queries": "/etc/postgres_exporter/queries.yaml"
            },
            "redis_exporter": {
                "type": MonitoringCollectorType.CUSTOM_EXPORTER,
                "version": "1.52.0",
                "port": 9121,
                "redis_addr": os.getenv("REDIS_ADDR", "redis://localhost:6379"),
                "connection_timeout": "15s",
                "include_system_metrics": True,
                "export_client_list": True
            }
        }
    
    def register_target(self, target: InfrastructureTarget):
        """Register infrastructure monitoring target"""
        self._targets[target.name] = target
        logging.info(f"Registered infrastructure target: {target.name}")
    
    def register_threshold(self, threshold: ResourceThreshold):
        """Register resource threshold"""
        key = f"{threshold.resource_type.value}_threshold"
        self._thresholds[key] = threshold
        logging.info(f"Registered threshold: {key}")
    
    def register_alert_rule(self, alert_rule: InfrastructureAlert):
        """Register alert rule"""
        self._alert_rules[alert_rule.name] = alert_rule
        logging.info(f"Registered infrastructure alert: {alert_rule.name}")
    
    def get_target(self, name: str) -> Optional[InfrastructureTarget]:
        """Get target by name"""
        return self._targets.get(name)
    
    def get_threshold(self, resource_type: ResourceType) -> Optional[ResourceThreshold]:
        """
Get threshold by resource type"""
        key = f"{resource_type.value}_threshold"
        return self._thresholds.get(key)
    
    def get_alert_rule(self, name: str) -> Optional[InfrastructureAlert]:
        """Get alert rule by name"""
        return self._alert_rules.get(name)
    
    def get_targets_by_layer(self, layer: InfrastructureLayer) -> List[InfrastructureTarget]:
        """
Get targets by infrastructure layer"""
        return [target for target in self._targets.values() 
                if target.layer == layer]
    
    def get_critical_alerts(self) -> List[InfrastructureAlert]:
        """
Get critical alert rules"""
        return [alert for alert in self._alert_rules.values() 
                if alert.severity == "critical"]
    
    def generate_prometheus_config(self) -> Dict[str, Any]:
        """Generate Prometheus configuration"""
        scrape_configs = []
        
        for target in self._targets.values():
            if not target.enabled:
                continue
                
            job_config = {
                "job_name": target.labels.get("job", target.name),
                "scrape_interval": target.scrape_interval,
                "scrape_timeout": target.scrape_timeout,
                "metrics_path": target.metrics_path,
                "static_configs": [{
                    "targets": [target.endpoint],
                    "labels": target.labels
                }]
            }
            
            if target.authentication:
                job_config.update(target.authentication)
                
            scrape_configs.append(job_config)
        
        return {
            "global": {
                "scrape_interval": self.config["global_scrape_interval"],
                "evaluation_interval": self.config["global_evaluation_interval"],
                "scrape_timeout": self.config["scrape_timeout"],
                "external_labels": {
                    "cluster": self.config["cluster_name"],
                    "environment": self.config["environment"],
                    "region": self.config["region"]
                }
            },
            "scrape_configs": scrape_configs,
            "alerting": {
                "alertmanagers": [{
                    "static_configs": [{
                        "targets": [self.config["alertmanager_endpoint"].replace("http://", "")]
                    }]
                }]
            },
            "rule_files": [
                "/etc/prometheus/rules/*.yml"
            ]
        }
    
    def generate_alert_rules_config(self) -> Dict[str, Any]:
        """Generate alert rules configuration"""
        groups = defaultdict(list)
        
        for alert in self._alert_rules.values():
            if not alert.enabled:
                continue
                
            category = alert.labels.get("category", "general")
            groups[category].append({
                "alert": alert.name,
                "expr": alert.expression,
                "for": alert.duration,
                "labels": alert.labels,
                "annotations": alert.annotations
            })
        
        return {
            "groups": [
                {
                    "name": f"{category}_alerts",
                    "interval": "30s",
                    "rules": rules
                }
                for category, rules in groups.items()
            ]
        }
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export complete infrastructure monitoring configuration"""
        return {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "cluster": self.config["cluster_name"],
                "environment": self.config["environment"]
            },
            "config": self.config,
            "targets": {
                name: {
                    "name": target.name,
                    "type": target.target_type,
                    "endpoint": target.endpoint,
                    "layer": target.layer.value,
                    "enabled": target.enabled,
                    "labels": target.labels
                }
                for name, target in self._targets.items()
            },
            "thresholds": {
                name: {
                    "resource_type": threshold.resource_type.value,
                    "warning": threshold.warning_threshold,
                    "critical": threshold.critical_threshold,
                    "unit": threshold.unit
                }
                for name, threshold in self._thresholds.items()
            },
            "alert_rules": {
                name: {
                    "name": alert.name,
                    "description": alert.description,
                    "severity": alert.severity,
                    "duration": alert.duration,
                    "enabled": alert.enabled
                }
                for name, alert in self._alert_rules.items()
            },
            "collectors": self._collectors
        }


# Global infrastructure monitoring configuration instance
infrastructure_monitoring_config = InfrastructureMonitoringConfig()

# Export key components for easy import
__all__ = [
    'InfrastructureMonitoringConfig',
    'InfrastructureLayer',
    'ResourceType',
    'MonitoringCollectorType',
    'InfrastructureTarget',
    'ResourceThreshold',
    'InfrastructureAlert',
    'infrastructure_monitoring_config'
]
