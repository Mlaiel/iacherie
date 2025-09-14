"""
Monitoring Configuration - Main Configuration Module
====================================================

Configuration centrale pour le système de monitoring Ainflue.
Réorganisation experte par l'équipe Lead Dev IA + Backend Senior + DevOps.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field


class MonitoringConfig(BaseSettings):
    """Configuration principale du système de monitoring."""
    
    # Configuration générale
    service_name: str = Field(default="ainflue-monitoring", env="MONITORING_SERVICE_NAME")
    environment: str = Field(default="production", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Configuration des métriques
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    metrics_path: str = Field(default="/metrics", env="METRICS_PATH")
    
    # Configuration des alertes
    alerts_enabled: bool = Field(default=True, env="ALERTS_ENABLED")
    alert_manager_url: str = Field(default="http://alertmanager:9093", env="ALERTMANAGER_URL")
    
    # Configuration des dashboards
    grafana_enabled: bool = Field(default=True, env="GRAFANA_ENABLED")
    grafana_url: str = Field(default="http://grafana:3000", env="GRAFANA_URL")
    
    # Configuration Prometheus
    prometheus_url: str = Field(default="http://prometheus:9090", env="PROMETHEUS_URL")
    prometheus_retention: str = Field(default="30d", env="PROMETHEUS_RETENTION")
    
    # Configuration Elasticsearch
    elasticsearch_enabled: bool = Field(default=True, env="ELASTICSEARCH_ENABLED")
    elasticsearch_host: str = Field(default="elasticsearch", env="ELASTICSEARCH_HOST")
    elasticsearch_port: int = Field(default=9200, env="ELASTICSEARCH_PORT")
    
    # Configuration Jaeger
    jaeger_enabled: bool = Field(default=True, env="JAEGER_ENABLED")
    jaeger_endpoint: str = Field(default="http://jaeger:14268/api/traces", env="JAEGER_ENDPOINT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instance globale de configuration
monitoring_config = MonitoringConfig()


def get_monitoring_config() -> MonitoringConfig:
    """Retourne la configuration du monitoring."""
    return monitoring_config


def get_module_configs() -> Dict[str, str]:
    """Retourne la configuration des modules de monitoring."""
    return {
        "core": "monitoring.core",
        "metrics": "monitoring.metrics", 
        "dashboards": "monitoring.dashboards",
        "alerts": "monitoring.alerts",
        "analytics": "monitoring.analytics",
        "intelligence": "monitoring.intelligence",
        "performance": "monitoring.performance",
        "reporting": "monitoring.reporting",
    }


def get_config_files() -> Dict[str, str]:
    """Retourne les chemins des fichiers de configuration."""
    base_path = os.path.dirname(__file__)
    return {
        "elasticsearch": os.path.join(base_path, "configs", "elasticsearch.yaml"),
        "jaeger": os.path.join(base_path, "configs", "jaeger.yaml"),
        "prometheus": os.path.join(base_path, "prometheus", "prometheus.yml"),
    }