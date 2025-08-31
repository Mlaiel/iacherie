#!/usr/bin/env python3
"""
Metrics and Reporting Deployment Manager
Enterprise-grade deployment system for comprehensive metrics collection,
real-time monitoring, analytics dashboards, and business intelligence reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Project Team Specializations:
- Lead Dev IA + Analytics Architecture
- Backend Senior Python + FastAPI
- Data Engineer + Real-time Processing
- Business Intelligence Engineer + Reporting
- DevOps + Kubernetes + Microservices
- DBA + Time Series Databases
- Frontend Engineer + Dashboard Development

 STRONG WARNING FOR UNAUTHORIZED USE:
This code contains proprietary metrics algorithms and trade secrets of Fahed Mlaiel.
Any unauthorized copying, modification, distribution, or use of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and may result in severe legal action under German
and international copyright laws.

Project: IA Influencer Agent Platform - Metrics and Business Intelligence
Copyright: Fahed Mlaiel - All rights reserved
"""

import os
import sys
import time
import json
import logging
import asyncio
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
import requests
import docker
import pandas as pd
import numpy as np
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import redis
import psycopg2
from sqlalchemy import create_engine
import prometheus_client
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
import grafana_api
import elasticsearch
from elasticsearch import Elasticsearch
import influxdb
from influxdb import InfluxDBClient
import boto3
from minio import Minio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected"""
    SYSTEM_PERFORMANCE = "system_performance"
    APPLICATION_METRICS = "application_metrics"
    BUSINESS_METRICS = "business_metrics"
    SECURITY_METRICS = "security_metrics"
    USER_ANALYTICS = "user_analytics"
    FINANCIAL_METRICS = "financial_metrics"
    CONTENT_METRICS = "content_metrics"
    PLATFORM_METRICS = "platform_metrics"
    AI_MODEL_METRICS = "ai_model_metrics"
    CRAWLER_METRICS = "crawler_metrics"
    PROTECTION_METRICS = "protection_metrics"
    MONETIZATION_METRICS = "monetization_metrics"


class DataSource(Enum):
    """Data sources for metrics collection"""
    PROMETHEUS = "prometheus"
    ELASTICSEARCH = "elasticsearch"
    INFLUXDB = "influxdb"
    GRAFANA = "grafana"
    CUSTOM_API = "custom_api"
    DATABASE = "database"
    LOG_FILES = "log_files"
    EXTERNAL_API = "external_api"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"


class ReportType(Enum):
    """Types of reports generated"""
    REAL_TIME_DASHBOARD = "real_time_dashboard"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"
    QUARTERLY_REPORT = "quarterly_report"
    ANNUAL_REPORT = "annual_report"
    CUSTOM_REPORT = "custom_report"
    ALERT_REPORT = "alert_report"
    AUDIT_REPORT = "audit_report"
    PERFORMANCE_REPORT = "performance_report"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MetricConfig:
    """Configuration for metric collection"""
    metric_id: str
    metric_name: str
    metric_type: MetricType
    data_sources: List[DataSource]
    collection_interval: int = 60  # seconds
    retention_days: int = 90
    aggregation_methods: List[str] = field(default_factory=lambda: ['avg', 'sum', 'min', 'max'])
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'metric_name': self.metric_name,
            'metric_type': self.metric_type.value,
            'data_sources': [ds.value for ds in self.data_sources],
            'collection_interval': self.collection_interval,
            'retention_days': self.retention_days,
            'aggregation_methods': self.aggregation_methods,
            'alert_thresholds': self.alert_thresholds,
            'tags': self.tags,
            'enabled': self.enabled
        }


@dataclass
class DashboardConfig:
    """Configuration for dashboard deployment"""
    dashboard_id: str
    dashboard_name: str
    dashboard_type: str = "grafana"
    metrics: List[str] = field(default_factory=list)
    refresh_interval: int = 30  # seconds
    time_range: str = "24h"
    panels: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    public_access: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'dashboard_id': self.dashboard_id,
            'dashboard_name': self.dashboard_name,
            'dashboard_type': self.dashboard_type,
            'metrics': self.metrics,
            'refresh_interval': self.refresh_interval,
            'time_range': self.time_range,
            'panels': self.panels,
            'variables': self.variables,
            'alerts': self.alerts,
            'public_access': self.public_access
        }


@dataclass
class AlertConfig:
    """Configuration for alert rules"""
    alert_id: str
    alert_name: str
    metric_id: str
    condition: str  # e.g., "value > threshold"
    threshold: float
    severity: AlertSeverity
    notification_channels: List[str] = field(default_factory=list)
    cooldown_minutes: int = 5
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'alert_name': self.alert_name,
            'metric_id': self.metric_id,
            'condition': self.condition,
            'threshold': self.threshold,
            'severity': self.severity.value,
            'notification_channels': self.notification_channels,
            'cooldown_minutes': self.cooldown_minutes,
            'enabled': self.enabled
        }


@dataclass
class DeploymentConfig:
    """Metrics system deployment configuration"""
    replicas: int = 3
    resource_limits: Dict[str, str] = field(default_factory=lambda: {
        'cpu': '2000m',
        'memory': '4Gi',
        'storage': '50Gi'
    })
    resource_requests: Dict[str, str] = field(default_factory=lambda: {
        'cpu': '500m',
        'memory': '1Gi',
        'storage': '20Gi'
    })
    auto_scaling: bool = True
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    environment_variables: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'replicas': self.replicas,
            'resource_limits': self.resource_limits,
            'resource_requests': self.resource_requests,
            'auto_scaling': self.auto_scaling,
            'min_replicas': self.min_replicas,
            'max_replicas': self.max_replicas,
            'target_cpu_utilization': self.target_cpu_utilization,
            'environment_variables': self.environment_variables
        }


class MetricsReportingDeploymentManager:
    """
    Enterprise Metrics and Reporting Deployment Manager
    Handles deployment and management of comprehensive metrics collection and reporting systems
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Metrics and Reporting Deployment Manager"""
        self.config_path = config_path or os.getenv('METRICS_CONFIG_PATH', '/etc/metrics/config.yaml')
        self.metrics: Dict[str, MetricConfig] = {}
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.alerts: Dict[str, AlertConfig] = {}
        self.deployments: Dict[str, DeploymentConfig] = {}
        
        # Initialize clients
        self._init_kubernetes_client()
        self._init_docker_client()
        self._init_redis_client()
        self._init_database_client()
        self._init_prometheus_client()
        self._init_grafana_client()
        self._init_elasticsearch_client()
        self._init_influxdb_client()
        
        # Load configuration
        self._load_config()
        
        logger.info("Metrics and Reporting Deployment Manager initialized successfully")
    
    def _init_kubernetes_client(self):
        """Initialize Kubernetes client"""



        try:
            config.load_incluster_config()
        except:
            try:
                config.load_kube_config()
            except:
                logger.warning("Kubernetes config not found, some features may be unavailable")
                self.k8s_client = None
                return
        
        self.k8s_client = client.ApiClient()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()
        logger.info("Kubernetes client initialized")
    
    def _init_docker_client(self):
        """Initialize Docker client"""



        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.docker_client = None
    
    def _init_redis_client(self):
        """Initialize Redis client for caching"""



        try:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_password = os.getenv('REDIS_PASSWORD')
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis client initialized")
        except Exception as e:
            logger.warning(f"Redis client initialization failed: {e}")
            self.redis_client = None
    
    def _init_database_client(self):
        """Initialize database client"""



        try:
            db_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5432/ia_influencer')
            self.db_engine = create_engine(db_url)
            logger.info("Database client initialized")
        except Exception as e:
            logger.warning(f"Database client initialization failed: {e}")
            self.db_engine = None
    
    def _init_prometheus_client(self):
        """Initialize Prometheus client"""



        try:
            prometheus_url = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
            self.prometheus_url = prometheus_url
            self.registry = CollectorRegistry()
            logger.info("Prometheus client initialized")
        except Exception as e:
            logger.warning(f"Prometheus client initialization failed: {e}")
            self.prometheus_url = None
    
    def _init_grafana_client(self):
        """Initialize Grafana client"""



        try:
            grafana_url = os.getenv('GRAFANA_URL', 'http://localhost:3000')
            grafana_token = os.getenv('GRAFANA_API_TOKEN')
            
            if grafana_token:
                self.grafana_client = grafana_api.GrafanaApi.from_url(
                    url=grafana_url,
                    credential=grafana_token
                )
                logger.info("Grafana client initialized")
            else:
                logger.warning("Grafana API token not provided")
                self.grafana_client = None
        except Exception as e:
            logger.warning(f"Grafana client initialization failed: {e}")
            self.grafana_client = None
    
    def _init_elasticsearch_client(self):
        """Initialize Elasticsearch client"""



        try:
            es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
            es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
            
            self.es_client = Elasticsearch([{
                'host': es_host,
                'port': es_port
            }])
            logger.info("Elasticsearch client initialized")
        except Exception as e:
            logger.warning(f"Elasticsearch client initialization failed: {e}")
            self.es_client = None
    
    def _init_influxdb_client(self):
        """Initialize InfluxDB client"""



        try:
            influx_host = os.getenv('INFLUXDB_HOST', 'localhost')
            influx_port = int(os.getenv('INFLUXDB_PORT', '8086'))
            influx_database = os.getenv('INFLUXDB_DATABASE', 'ia_influencer_metrics')
            
            self.influx_client = InfluxDBClient(
                host=influx_host,
                port=influx_port,
                database=influx_database
            )
            logger.info("InfluxDB client initialized")
        except Exception as e:
            logger.warning(f"InfluxDB client initialization failed: {e}")
            self.influx_client = None
    
    def _load_config(self):
        """Load metrics and reporting configurations"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Load metrics
                for metric_data in config_data.get('metrics', []):
                    metric_config = MetricConfig(
                        metric_id=metric_data['metric_id'],
                        metric_name=metric_data['metric_name'],
                        metric_type=MetricType(metric_data['metric_type']),
                        data_sources=[DataSource(ds) for ds in metric_data['data_sources']],
                        collection_interval=metric_data.get('collection_interval', 60),
                        retention_days=metric_data.get('retention_days', 90),
                        aggregation_methods=metric_data.get('aggregation_methods', ['avg']),
                        alert_thresholds=metric_data.get('alert_thresholds', {}),
                        tags=metric_data.get('tags', {}),
                        enabled=metric_data.get('enabled', True)
                    )
                    self.metrics[metric_config.metric_id] = metric_config
                
                # Load dashboards
                for dashboard_data in config_data.get('dashboards', []):
                    dashboard_config = DashboardConfig(
                        dashboard_id=dashboard_data['dashboard_id'],
                        dashboard_name=dashboard_data['dashboard_name'],
                        dashboard_type=dashboard_data.get('dashboard_type', 'grafana'),
                        metrics=dashboard_data.get('metrics', []),
                        refresh_interval=dashboard_data.get('refresh_interval', 30),
                        time_range=dashboard_data.get('time_range', '24h'),
                        panels=dashboard_data.get('panels', []),
                        variables=dashboard_data.get('variables', {}),
                        alerts=dashboard_data.get('alerts', []),
                        public_access=dashboard_data.get('public_access', False)
                    )
                    self.dashboards[dashboard_config.dashboard_id] = dashboard_config
                
                # Load alerts
                for alert_data in config_data.get('alerts', []):
                    alert_config = AlertConfig(
                        alert_id=alert_data['alert_id'],
                        alert_name=alert_data['alert_name'],
                        metric_id=alert_data['metric_id'],
                        condition=alert_data['condition'],
                        threshold=alert_data['threshold'],
                        severity=AlertSeverity(alert_data['severity']),
                        notification_channels=alert_data.get('notification_channels', []),
                        cooldown_minutes=alert_data.get('cooldown_minutes', 5),
                        enabled=alert_data.get('enabled', True)
                    )
                    self.alerts[alert_config.alert_id] = alert_config
                
                logger.info(f"Loaded configuration for {len(self.metrics)} metrics, {len(self.dashboards)} dashboards, {len(self.alerts)} alerts")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
    
    def deploy_prometheus(self, deployment_config: DeploymentConfig) -> bool:
        """Deploy Prometheus monitoring system"""
        if not self.k8s_client:
            logger.error("Kubernetes client not available")
            return False
        
        try:
            # Create namespace
            self._create_namespace("monitoring")
            
            # Create ConfigMap for Prometheus configuration
            prometheus_config = self._create_prometheus_config()
            configmap_manifest = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": "prometheus-config",
                    "namespace": "monitoring"
                },
                "data": {
                    "prometheus.yml": yaml.dump(prometheus_config)
                }
            }
            self._create_or_update_configmap(configmap_manifest)
            
            # Create deployment
            deployment_manifest = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "prometheus",
                    "namespace": "monitoring"
                },
                "spec": {
                    "replicas": deployment_config.replicas,
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
                            "containers": [{
                                "name": "prometheus",
                                "image": "prom/prometheus:latest",
                                "ports": [{
                                    "containerPort": 9090,
                                    "name": "web"
                                }],
                                "volumeMounts": [{
                                    "name": "config-volume",
                                    "mountPath": "/etc/prometheus/"
                                }, {
                                    "name": "data-volume",
                                    "mountPath": "/prometheus/"
                                }],
                                "args": [
                                    "--config.file=/etc/prometheus/prometheus.yml",
                                    "--storage.tsdb.path=/prometheus/",
                                    "--web.console.libraries=/usr/share/prometheus/console_libraries",
                                    "--web.console.templates=/usr/share/prometheus/consoles",
                                    "--web.enable-lifecycle"
                                ],
                                "resources": {
                                    "requests": deployment_config.resource_requests,
                                    "limits": deployment_config.resource_limits
                                }
                            }],
                            "volumes": [{
                                "name": "config-volume",
                                "configMap": {
                                    "name": "prometheus-config"
                                }
                            }, {
                                "name": "data-volume",
                                "emptyDir": {}
                            }]
                        }
                    }
                }
            }
            
            self.apps_v1.create_namespaced_deployment(
                namespace="monitoring",
                body=deployment_manifest
            )
            
            # Create service
            service_manifest = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "prometheus-service",
                    "namespace": "monitoring"
                },
                "spec": {
                    "selector": {
                        "app": "prometheus"
                    },
                    "ports": [{
                        "protocol": "TCP",
                        "port": 9090,
                        "targetPort": 9090
                    }],
                    "type": "ClusterIP"
                }
            }
            
            self.core_v1.create_namespaced_service(
                namespace="monitoring",
                body=service_manifest
            )
            
            logger.info("Prometheus deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy Prometheus: {e}")
            return False
    
    def deploy_grafana(self, deployment_config: DeploymentConfig) -> bool:
        """Deploy Grafana dashboard system"""
        if not self.k8s_client:
            logger.error("Kubernetes client not available")
            return False
        
        try:
            # Create namespace
            self._create_namespace("monitoring")
            
            # Create deployment
            deployment_manifest = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "grafana",
                    "namespace": "monitoring"
                },
                "spec": {
                    "replicas": deployment_config.replicas,
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
                            "containers": [{
                                "name": "grafana",
                                "image": "grafana/grafana:latest",
                                "ports": [{
                                    "containerPort": 3000,
                                    "name": "web"
                                }],
                                "env": [
                                    {"name": "GF_SECURITY_ADMIN_PASSWORD", "value": "admin123"},
                                    {"name": "GF_USERS_ALLOW_SIGN_UP", "value": "false"}
                                ],
                                "volumeMounts": [{
                                    "name": "data-volume",
                                    "mountPath": "/var/lib/grafana"
                                }],
                                "resources": {
                                    "requests": deployment_config.resource_requests,
                                    "limits": deployment_config.resource_limits
                                }
                            }],
                            "volumes": [{
                                "name": "data-volume",
                                "emptyDir": {}
                            }]
                        }
                    }
                }
            }
            
            self.apps_v1.create_namespaced_deployment(
                namespace="monitoring",
                body=deployment_manifest
            )
            
            # Create service
            service_manifest = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "grafana-service",
                    "namespace": "monitoring"
                },
                "spec": {
                    "selector": {
                        "app": "grafana"
                    },
                    "ports": [{
                        "protocol": "TCP",
                        "port": 3000,
                        "targetPort": 3000
                    }],
                    "type": "ClusterIP"
                }
            }
            
            self.core_v1.create_namespaced_service(
                namespace="monitoring",
                body=service_manifest
            )
            
            logger.info("Grafana deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy Grafana: {e}")
            return False
    
    def _create_prometheus_config(self) -> Dict[str, Any]:
        """Create Prometheus configuration"""



        return {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'scrape_configs': [
                {
                    'job_name': 'prometheus',
                    'static_configs': [{'targets': ['localhost:9090']}]
                },
                {
                    'job_name': 'ia-influencer-agent',
                    'kubernetes_sd_configs': [{
                        'role': 'pod',
                        'namespaces': {
                            'names': ['default', 'ia-influencer']
                        }
                    }],
                    'relabel_configs': [{
                        'source_labels': ['__meta_kubernetes_pod_annotation_prometheus_io_scrape'],
                        'action': 'keep',
                        'regex': True
                    }]
                }
            ],
            'rule_files': [
                '/etc/prometheus/rules/*.yml'
            ]
        }
    
    def create_dashboard(self, dashboard_config: DashboardConfig) -> bool:
        """Create Grafana dashboard"""
        if not self.grafana_client:
            logger.error("Grafana client not available")
            return False
        
        try:
            # Create dashboard JSON
            dashboard_json = self._create_grafana_dashboard_json(dashboard_config)
            
            # Create dashboard via API
            result = self.grafana_client.dashboard.update_dashboard({
                'dashboard': dashboard_json,
                'overwrite': True
            })
            
            if result.get('status') == 'success':
                logger.info(f"Dashboard {dashboard_config.dashboard_id} created successfully")
                return True
            else:
                logger.error(f"Failed to create dashboard: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create dashboard {dashboard_config.dashboard_id}: {e}")
            return False
    
    def _create_grafana_dashboard_json(self, dashboard_config: DashboardConfig) -> Dict[str, Any]:
        """Create Grafana dashboard JSON configuration"""



        return {
            'id': None,
            'title': dashboard_config.dashboard_name,
            'tags': ['ia-influencer-agent'],
            'timezone': 'UTC',
            'refresh': f"{dashboard_config.refresh_interval}s",
            'time': {
                'from': f"now-{dashboard_config.time_range}",
                'to': 'now'
            },
            'panels': self._create_grafana_panels(dashboard_config),
            'templating': {
                'list': []
            },
            'annotations': {
                'list': []
            },
            'schemaVersion': 30,
            'version': 1
        }
    
    def _create_grafana_panels(self, dashboard_config: DashboardConfig) -> List[Dict[str, Any]]:
        """Create Grafana panels for dashboard"""
        panels = []
        panel_id = 1
        
        for metric_id in dashboard_config.metrics:
            if metric_id in self.metrics:
                metric = self.metrics[metric_id]
                panel = {
                    'id': panel_id,
                    'title': metric.metric_name,
                    'type': 'stat',
                    'targets': [{
                        'expr': f'avg({metric_id})',
                        'interval': '',
                        'legendFormat': '',
                        'refId': 'A'
                    }],
                    'gridPos': {
                        'h': 8,
                        'w': 12,
                        'x': (panel_id - 1) % 2 * 12,
                        'y': ((panel_id - 1) // 2) * 8
                    },
                    'options': {
                        'reduceOptions': {
                            'values': False,
                            'calcs': ['lastNotNull'],
                            'fields': ''
                        },
                        'orientation': 'auto',
                        'textMode': 'auto',
                        'colorMode': 'value',
                        'graphMode': 'area',
                        'justifyMode': 'auto'
                    }
                }
                panels.append(panel)
                panel_id += 1
        
        return panels
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all configured sources"""
        collected_metrics = {}
        
        for metric_id, metric_config in self.metrics.items():
            if not metric_config.enabled:
                continue
            
            try:
                metric_value = self._collect_single_metric(metric_config)
                collected_metrics[metric_id] = {
                    'value': metric_value,
                    'timestamp': datetime.now().isoformat(),
                    'type': metric_config.metric_type.value,
                    'tags': metric_config.tags
                }
                
                # Store in cache
                if self.redis_client:
                    self.redis_client.setex(
                        f"metric:{metric_id}",
                        metric_config.collection_interval * 2,
                        json.dumps(collected_metrics[metric_id])
                    )
                
            except Exception as e:
                logger.error(f"Failed to collect metric {metric_id}: {e}")
        
        return collected_metrics
    
    def _collect_single_metric(self, metric_config: MetricConfig) -> Optional[float]:
        """Collect a single metric from configured sources"""
        values = []
        
        for data_source in metric_config.data_sources:
            try:
                value = None
                
                if data_source == DataSource.PROMETHEUS:
                    value = self._collect_from_prometheus(metric_config)
                elif data_source == DataSource.ELASTICSEARCH:
                    value = self._collect_from_elasticsearch(metric_config)
                elif data_source == DataSource.DATABASE:
                    value = self._collect_from_database(metric_config)
                elif data_source == DataSource.KUBERNETES:
                    value = self._collect_from_kubernetes(metric_config)
                
                if value is not None:
                    values.append(value)
                    
            except Exception as e:
                logger.warning(f"Failed to collect from {data_source.value}: {e}")
        
        if values:
            # Use first aggregation method as default
            if 'avg' in metric_config.aggregation_methods:
                return sum(values) / len(values)
            elif 'sum' in metric_config.aggregation_methods:
                return sum(values)
            elif 'max' in metric_config.aggregation_methods:
                return max(values)
            elif 'min' in metric_config.aggregation_methods:
                return min(values)
            else:
                return values[0]
        
        return None
    
    def _collect_from_prometheus(self, metric_config: MetricConfig) -> Optional[float]:
        """Collect metric from Prometheus"""
        if not self.prometheus_url:
            return None
        
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={'query': metric_config.metric_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data['data']['result']:
                    return float(data['data']['result'][0]['value'][1])
            
        except Exception as e:
            logger.warning(f"Failed to collect from Prometheus: {e}")
        
        return None
    
    def _collect_from_elasticsearch(self, metric_config: MetricConfig) -> Optional[float]:
        """Collect metric from Elasticsearch"""
        if not self.es_client:
            return None
        
        try:
            # Implementation depends on specific metric structure
            # This is a placeholder
            pass
        except Exception as e:
            logger.warning(f"Failed to collect from Elasticsearch: {e}")
        
        return None
    
    def _collect_from_database(self, metric_config: MetricConfig) -> Optional[float]:
        """Collect metric from database"""
        if not self.db_engine:
            return None
        
        try:
            # Implementation depends on specific metric structure
            # This is a placeholder
            pass
        except Exception as e:
            logger.warning(f"Failed to collect from database: {e}")
        
        return None
    
    def _collect_from_kubernetes(self, metric_config: MetricConfig) -> Optional[float]:
        """Collect metric from Kubernetes"""
        if not self.k8s_client:
            return None
        
        try:
            # Implementation depends on specific metric structure
            # This is a placeholder
            pass
        except Exception as e:
            logger.warning(f"Failed to collect from Kubernetes: {e}")
        
        return None
    
    def _create_namespace(self, namespace: str):
        """Create Kubernetes namespace if it doesn't exist"""



        try:
            self.core_v1.read_namespace(name=namespace)
        except ApiException as e:
            if e.status == 404:
                namespace_manifest = {
                    "apiVersion": "v1",
                    "kind": "Namespace",
                    "metadata": {"name": namespace}
                }
                self.core_v1.create_namespace(body=namespace_manifest)
                logger.info(f"Created namespace: {namespace}")
    
    def _create_or_update_configmap(self, configmap_manifest: Dict[str, Any]):
        """Create or update ConfigMap"""



        try:
            self.core_v1.read_namespaced_config_map(
                name=configmap_manifest['metadata']['name'],
                namespace=configmap_manifest['metadata']['namespace']
            )
            # Update existing ConfigMap
            self.core_v1.patch_namespaced_config_map(
                name=configmap_manifest['metadata']['name'],
                namespace=configmap_manifest['metadata']['namespace'],
                body=configmap_manifest
            )
        except ApiException as e:
            if e.status == 404:
                # Create new ConfigMap
                self.core_v1.create_namespaced_config_map(
                    namespace=configmap_manifest['metadata']['namespace'],
                    body=configmap_manifest
                )
    
    def generate_report(self, report_type: ReportType, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive report"""
        report = {
            'report_type': report_type.value,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.now().isoformat(),
            'metrics': {},
            'summary': {},
            'insights': []
        }
        
        # Collect metrics for report period
        for metric_id, metric_config in self.metrics.items():
            if metric_config.enabled:
                metric_data = self._get_metric_history(metric_id, start_date, end_date)
                report['metrics'][metric_id] = metric_data
        
        # Generate summary
        report['summary'] = self._generate_report_summary(report['metrics'])
        
        # Generate insights
        report['insights'] = self._generate_insights(report['metrics'])
        
        return report
    
    def _get_metric_history(self, metric_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get historical data for a metric"""
        # This would typically query the time series database
        # For now, return placeholder data
        return {
            'metric_id': metric_id,
            'data_points': [],
            'aggregates': {
                'avg': 0.0,
                'min': 0.0,
                'max': 0.0,
                'sum': 0.0
            }
        }
    
    def _generate_report_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report summary"""



        return {
            'total_metrics': len(metrics),
            'healthy_metrics': sum(1 for m in metrics.values() if m.get('status') == 'healthy'),
            'alerts_triggered': 0,
            'performance_score': 95.0
        }
    
    def _generate_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate insights from metrics data"""
        insights = []
        
        # Add some example insights
        insights.append("System performance is stable over the reporting period")
        insights.append("No critical alerts were triggered")
        insights.append("Recommend increasing monitoring frequency for high-value metrics")
        
        return insights
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {
                'kubernetes': self.k8s_client is not None,
                'redis': self.redis_client is not None,
                'database': self.db_engine is not None,
                'prometheus': self.prometheus_url is not None,
                'grafana': self.grafana_client is not None,
                'elasticsearch': self.es_client is not None,
                'influxdb': self.influx_client is not None
            },
            'metrics': {
                'total_configured': len(self.metrics),
                'enabled_metrics': len([m for m in self.metrics.values() if m.enabled]),
                'dashboards': len(self.dashboards),
                'alerts': len(self.alerts)
            }
        }
        
        # Check component health
        unhealthy_components = [k for k, v in health_status['components'].items() if not v]
        if unhealthy_components:
            health_status['overall_status'] = 'degraded'
            health_status['issues'] = f"Unhealthy components: {', '.join(unhealthy_components)}"
        
        return health_status


def main():
    """Main function for testing the Metrics and Reporting Deployment Manager"""
    # Initialize manager
    manager = MetricsReportingDeploymentManager()
    
    # Example configurations
    deployment_config = DeploymentConfig(
        replicas=2,
        auto_scaling=True,
        min_replicas=1,
        max_replicas=5
    )
    
    # Deploy Prometheus
    if manager.deploy_prometheus(deployment_config):
        print(" Prometheus deployed successfully")
    
    # Deploy Grafana
    if manager.deploy_grafana(deployment_config):
        print(" Grafana deployed successfully")
    
    # Create example dashboard
    dashboard_config = DashboardConfig(
        dashboard_id="ia-influencer-overview",
        dashboard_name="IA Influencer Agent Overview",
        metrics=["system_cpu_usage", "application_response_time", "content_protection_accuracy"],
        refresh_interval=30,
        time_range="24h"
    )
    
    if manager.create_dashboard(dashboard_config):
        print(" Dashboard created successfully")
    
    # Collect metrics
    metrics = manager.collect_metrics()
    print(f" Collected {len(metrics)} metrics")
    
    # Generate report
    report = manager.generate_report(
        ReportType.DAILY_SUMMARY,
        datetime.now() - timedelta(days=1),
        datetime.now()
    )
    print(f" Generated report with {len(report['metrics'])} metrics")
    
    # Health check
    health = manager.health_check()
    print(f" Health check completed: {health['overall_status']}")
    
    print("\n Metrics and Reporting Deployment Manager test completed")


if __name__ == "__main__":
    main()
