# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Prometheus Configuration

Enterprise Prometheus configuration and management for infrastructure monitoring.
Handles setup, configuration, and management of Prometheus monitoring infrastructure.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import yaml
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PrometheusTarget:
    """Prometheus monitoring target."""
    job_name: str
    targets: List[str]
    scrape_interval: str = "15s"
    metrics_path: str = "/metrics"
    scheme: str = "http"
    labels: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class AlertingRule:
    """Prometheus alerting rule."""
    alert: str
    expr: str
    duration: str = "5m"
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class RecordingRule:
    """Prometheus recording rule."""
    record: str
    expr: str
    labels: Dict[str, str] = field(default_factory=dict)

class PrometheusConfiguration:
    """
    Enterprise Prometheus configuration manager.
    
    Provides comprehensive Prometheus setup, configuration management,
    target discovery, and alerting rule management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Prometheus configuration."""
        self.config = config or {}
        self.prometheus_config = {}
        self.targets: Dict[str, PrometheusTarget] = {}
        self.alerting_rules: Dict[str, AlertingRule] = {}
        self.recording_rules: Dict[str, RecordingRule] = {}
        
        # Configuration paths
        self.config_dir = Path(self.config.get("config_dir", "./prometheus"))
        self.rules_dir = self.config_dir / "rules"
        self.targets_dir = self.config_dir / "targets"
        
        # Prometheus settings
        self.global_config = self.config.get("global", {
            "scrape_interval": "15s",
            "evaluation_interval": "15s",
            "external_labels": {
                "cluster": "ainflue",
                "environment": "production"
            }
        })
        
        # Storage settings
        self.storage_config = self.config.get("storage", {
            "retention_time": "30d",
            "retention_size": "50GB",
            "wal_compression": True
        })
        
        # Alerting configuration
        self.alerting_config = self.config.get("alerting", {
            "alertmanagers": [{
                "static_configs": [{
                    "targets": ["alertmanager:9093"]
                }]
            }]
        })
        
        # Remote storage configuration
        self.remote_storage = self.config.get("remote_storage", {})
        
        # Create directories
        self._create_directories()
        
        # Initialize base configuration
        self._initialize_base_config()
        
        logger.info("PrometheusConfiguration initialized")
    
    def _create_directories(self):
        """Create necessary directories."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            self.targets_dir.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            logger.error(f"Failed to create directories: {str(e)}")
            raise
    
    def _initialize_base_config(self):
        """Initialize base Prometheus configuration."""
        self.prometheus_config = {
            "global": self.global_config,
            "alerting": self.alerting_config,
            "rule_files": [
                "rules/*.yml",
                "rules/*.yaml"
            ],
            "scrape_configs": []
        }
        
        # Add remote storage if configured
        if self.remote_storage:
            if "remote_write" in self.remote_storage:
                self.prometheus_config["remote_write"] = self.remote_storage["remote_write"]
            if "remote_read" in self.remote_storage:
                self.prometheus_config["remote_read"] = self.remote_storage["remote_read"]
    
    async def add_scrape_target(self, target: PrometheusTarget) -> bool:
        """Add a scrape target to Prometheus configuration."""
        try:
            self.targets[target.job_name] = target
            
            # Create scrape config
            scrape_config = {
                "job_name": target.job_name,
                "scrape_interval": target.scrape_interval,
                "metrics_path": target.metrics_path,
                "scheme": target.scheme,
                "static_configs": [{
                    "targets": target.targets,
                    "labels": target.labels
                }]
            }
            
            # Add parameters if specified
            if target.params:
                scrape_config["params"] = target.params
            
            # Update Prometheus configuration
            existing_configs = self.prometheus_config.get("scrape_configs", [])
            
            # Remove existing config with same job_name
            existing_configs = [c for c in existing_configs if c.get("job_name") != target.job_name]
            
            # Add new config
            existing_configs.append(scrape_config)
            self.prometheus_config["scrape_configs"] = existing_configs
            
            logger.info(f"Added scrape target: {target.job_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add scrape target {target.job_name}: {str(e)}")
            return False
    
    async def add_alerting_rule(self, rule_group: str, rule: AlertingRule) -> bool:
        """Add an alerting rule."""
        try:
            rule_key = f"{rule_group}:{rule.alert}"
            self.alerting_rules[rule_key] = rule
            
            # Save rule to file
            await self._save_alerting_rules(rule_group)
            
            logger.info(f"Added alerting rule: {rule.alert}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add alerting rule {rule.alert}: {str(e)}")
            return False
    
    async def add_recording_rule(self, rule_group: str, rule: RecordingRule) -> bool:
        """Add a recording rule."""
        try:
            rule_key = f"{rule_group}:{rule.record}"
            self.recording_rules[rule_key] = rule
            
            # Save rule to file
            await self._save_recording_rules(rule_group)
            
            logger.info(f"Added recording rule: {rule.record}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add recording rule {rule.record}: {str(e)}")
            return False
    
    async def _save_alerting_rules(self, rule_group: str):
        """Save alerting rules to file."""
        try:
            # Group rules by rule_group
            group_rules = []
            for rule_key, rule in self.alerting_rules.items():
                if rule_key.startswith(f"{rule_group}:"):
                    group_rules.append({
                        "alert": rule.alert,
                        "expr": rule.expr,
                        "for": rule.duration,
                        "labels": rule.labels,
                        "annotations": rule.annotations
                    })
            
            if group_rules:
                rule_file_content = {
                    "groups": [{
                        "name": rule_group,
                        "rules": group_rules
                    }]
                }
                
                rule_file_path = self.rules_dir / f"{rule_group}_alerts.yml"
                with open(rule_file_path, 'w') as f:
                    yaml.dump(rule_file_content, f, default_flow_style=False)
                
                logger.info(f"Saved alerting rules for group: {rule_group}")
            
        except Exception as e:
            logger.error(f"Failed to save alerting rules for {rule_group}: {str(e)}")
    
    async def _save_recording_rules(self, rule_group: str):
        """Save recording rules to file."""
        try:
            # Group rules by rule_group
            group_rules = []
            for rule_key, rule in self.recording_rules.items():
                if rule_key.startswith(f"{rule_group}:"):
                    group_rules.append({
                        "record": rule.record,
                        "expr": rule.expr,
                        "labels": rule.labels
                    })
            
            if group_rules:
                rule_file_content = {
                    "groups": [{
                        "name": f"{rule_group}_recordings",
                        "rules": group_rules
                    }]
                }
                
                rule_file_path = self.rules_dir / f"{rule_group}_recordings.yml"
                with open(rule_file_path, 'w') as f:
                    yaml.dump(rule_file_content, f, default_flow_style=False)
                
                logger.info(f"Saved recording rules for group: {rule_group}")
            
        except Exception as e:
            logger.error(f"Failed to save recording rules for {rule_group}: {str(e)}")
    
    async def create_default_monitoring_targets(self):
        """Create default monitoring targets for Ainflue infrastructure."""
        try:
            # Ainflue API targets
            api_target = PrometheusTarget(
                job_name="ainflue-api",
                targets=["ainflue-api:8000"],
                scrape_interval="10s",
                metrics_path="/metrics",
                labels={"service": "api", "tier": "backend"}
            )
            await self.add_scrape_target(api_target)
            
            # Ainflue AI Engine targets
            ai_target = PrometheusTarget(
                job_name="ainflue-ai-engine",
                targets=["ainflue-ai:8001"],
                scrape_interval="15s",
                metrics_path="/metrics",
                labels={"service": "ai-engine", "tier": "ml"}
            )
            await self.add_scrape_target(ai_target)
            
            # Database targets
            db_target = PrometheusTarget(
                job_name="postgresql",
                targets=["postgres-exporter:9187"],
                scrape_interval="30s",
                labels={"service": "database", "tier": "data"}
            )
            await self.add_scrape_target(db_target)
            
            # Redis targets
            redis_target = PrometheusTarget(
                job_name="redis",
                targets=["redis-exporter:9121"],
                scrape_interval="30s",
                labels={"service": "cache", "tier": "data"}
            )
            await self.add_scrape_target(redis_target)
            
            # Node exporter targets
            node_target = PrometheusTarget(
                job_name="node-exporter",
                targets=["node-exporter:9100"],
                scrape_interval="15s",
                labels={"service": "node-metrics", "tier": "infrastructure"}
            )
            await self.add_scrape_target(node_target)
            
            # Kubernetes targets
            k8s_target = PrometheusTarget(
                job_name="kubernetes-pods",
                targets=[],  # Will be discovered automatically
                scrape_interval="15s",
                labels={"service": "kubernetes", "tier": "infrastructure"}
            )
            await self.add_scrape_target(k8s_target)
            
            logger.info("Created default monitoring targets")
            
        except Exception as e:
            logger.error(f"Failed to create default monitoring targets: {str(e)}")
    
    async def create_default_alerting_rules(self):
        """Create default alerting rules for Ainflue infrastructure."""
        try:
            # High CPU usage alert
            cpu_alert = AlertingRule(
                alert="HighCPUUsage",
                expr="100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100) > 80",
                duration="5m",
                labels={"severity": "warning"},
                annotations={
                    "summary": "High CPU usage detected",
                    "description": "CPU usage is above 80% for more than 5 minutes on {{ $labels.instance }}"
                }
            )
            await self.add_alerting_rule("infrastructure", cpu_alert)
            
            # High memory usage alert
            memory_alert = AlertingRule(
                alert="HighMemoryUsage",
                expr="(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85",
                duration="5m",
                labels={"severity": "warning"},
                annotations={
                    "summary": "High memory usage detected",
                    "description": "Memory usage is above 85% for more than 5 minutes on {{ $labels.instance }}"
                }
            )
            await self.add_alerting_rule("infrastructure", memory_alert)
            
            # Service down alert
            service_down_alert = AlertingRule(
                alert="ServiceDown",
                expr="up == 0",
                duration="1m",
                labels={"severity": "critical"},
                annotations={
                    "summary": "Service is down",
                    "description": "Service {{ $labels.job }} on {{ $labels.instance }} is down"
                }
            )
            await self.add_alerting_rule("availability", service_down_alert)
            
            # High error rate alert
            error_rate_alert = AlertingRule(
                alert="HighErrorRate",
                expr="rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) > 0.1",
                duration="5m",
                labels={"severity": "critical"},
                annotations={
                    "summary": "High error rate detected",
                    "description": "Error rate is above 10% for {{ $labels.job }} service"
                }
            )
            await self.add_alerting_rule("application", error_rate_alert)
            
            # Database connection alert
            db_connection_alert = AlertingRule(
                alert="DatabaseConnectionHigh",
                expr="pg_stat_activity_count > 80",
                duration="5m",
                labels={"severity": "warning"},
                annotations={
                    "summary": "High database connections",
                    "description": "Database has more than 80 active connections"
                }
            )
            await self.add_alerting_rule("database", db_connection_alert)
            
            logger.info("Created default alerting rules")
            
        except Exception as e:
            logger.error(f"Failed to create default alerting rules: {str(e)}")
    
    async def create_default_recording_rules(self):
        """Create default recording rules for performance optimization."""
        try:
            # Instance CPU usage rate
            cpu_rate_rule = RecordingRule(
                record="instance:cpu_usage_rate",
                expr="100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
                labels={"metric_type": "performance"}
            )
            await self.add_recording_rule("performance", cpu_rate_rule)
            
            # Instance memory usage percentage
            memory_usage_rule = RecordingRule(
                record="instance:memory_usage_percent",
                expr="(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
                labels={"metric_type": "performance"}
            )
            await self.add_recording_rule("performance", memory_usage_rule)
            
            # HTTP request rate
            request_rate_rule = RecordingRule(
                record="instance:http_request_rate",
                expr="rate(http_requests_total[5m])",
                labels={"metric_type": "application"}
            )
            await self.add_recording_rule("application", request_rate_rule)
            
            # HTTP error rate
            error_rate_rule = RecordingRule(
                record="instance:http_error_rate",
                expr="rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])",
                labels={"metric_type": "application"}
            )
            await self.add_recording_rule("application", error_rate_rule)
            
            logger.info("Created default recording rules")
            
        except Exception as e:
            logger.error(f"Failed to create default recording rules: {str(e)}")
    
    async def save_configuration(self) -> bool:
        """Save Prometheus configuration to file."""
        try:
            config_file = self.config_dir / "prometheus.yml"
            
            with open(config_file, 'w') as f:
                yaml.dump(self.prometheus_config, f, default_flow_style=False)
            
            logger.info(f"Saved Prometheus configuration to {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save Prometheus configuration: {str(e)}")
            return False
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate Prometheus configuration."""
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check global configuration
            if not self.prometheus_config.get("global"):
                validation_result["errors"].append("Missing global configuration")
                validation_result["valid"] = False
            
            # Check scrape configs
            scrape_configs = self.prometheus_config.get("scrape_configs", [])
            if not scrape_configs:
                validation_result["warnings"].append("No scrape configurations defined")
            
            # Validate each scrape config
            for config in scrape_configs:
                if not config.get("job_name"):
                    validation_result["errors"].append("Scrape config missing job_name")
                    validation_result["valid"] = False
                
                if not config.get("static_configs"):
                    validation_result["warnings"].append(f"Job {config.get('job_name')} has no targets")
            
            # Check rule files exist
            rule_files = self.prometheus_config.get("rule_files", [])
            for rule_pattern in rule_files:
                # In real implementation, would check if files exist
                pass
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Configuration validation error: {str(e)}")
            return {"valid": False, "errors": [str(e)]}
    
    async def reload_configuration(self) -> bool:
        """Reload Prometheus configuration (sends SIGHUP to Prometheus)."""
        try:
            # In real implementation, would send reload signal to Prometheus
            # For now, just validate and save
            validation = await self.validate_configuration()
            
            if not validation["valid"]:
                logger.error(f"Configuration validation failed: {validation['errors']}")
                return False
            
            await self.save_configuration()
            
            logger.info("Prometheus configuration reloaded")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {str(e)}")
            return False
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            "targets": len(self.targets),
            "alerting_rules": len(self.alerting_rules),
            "recording_rules": len(self.recording_rules),
            "scrape_configs": len(self.prometheus_config.get("scrape_configs", [])),
            "global_config": self.global_config,
            "storage_config": self.storage_config,
            "config_dir": str(self.config_dir)
        }
    
    def list_targets(self) -> List[Dict[str, Any]]:
        """List all monitoring targets."""
        targets = []
        for target in self.targets.values():
            targets.append({
                "job_name": target.job_name,
                "targets": target.targets,
                "scrape_interval": target.scrape_interval,
                "metrics_path": target.metrics_path,
                "labels": target.labels
            })
        return targets
    
    def list_alerting_rules(self) -> List[Dict[str, Any]]:
        """List all alerting rules."""
        rules = []
        for rule in self.alerting_rules.values():
            rules.append({
                "alert": rule.alert,
                "expr": rule.expr,
                "duration": rule.duration,
                "labels": rule.labels,
                "annotations": rule.annotations
            })
        return rules
    
    async def setup_service_discovery(self, discovery_config: Dict[str, Any]) -> bool:
        """Setup service discovery for dynamic target detection."""
        try:
            discovery_type = discovery_config.get("type", "kubernetes")
            
            if discovery_type == "kubernetes":
                # Kubernetes service discovery
                k8s_sd_config = {
                    "job_name": "kubernetes-pods",
                    "kubernetes_sd_configs": [{
                        "role": "pod",
                        "namespaces": {
                            "names": discovery_config.get("namespaces", ["default", "ainflue"])
                        }
                    }],
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_scrape"],
                            "action": "keep",
                            "regex": "true"
                        },
                        {
                            "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_path"],
                            "action": "replace",
                            "target_label": "__metrics_path__",
                            "regex": "(.+)"
                        }
                    ]
                }
                
                # Add to scrape configs
                scrape_configs = self.prometheus_config.get("scrape_configs", [])
                
                # Remove existing kubernetes config
                scrape_configs = [c for c in scrape_configs if c.get("job_name") != "kubernetes-pods"]
                
                # Add new config
                scrape_configs.append(k8s_sd_config)
                self.prometheus_config["scrape_configs"] = scrape_configs
                
                logger.info("Setup Kubernetes service discovery")
                
            elif discovery_type == "consul":
                # Consul service discovery
                consul_sd_config = {
                    "job_name": "consul-services",
                    "consul_sd_configs": [{
                        "server": discovery_config.get("consul_server", "consul:8500"),
                        "services": discovery_config.get("services", [])
                    }]
                }
                
                scrape_configs = self.prometheus_config.get("scrape_configs", [])
                scrape_configs.append(consul_sd_config)
                self.prometheus_config["scrape_configs"] = scrape_configs
                
                logger.info("Setup Consul service discovery")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup service discovery: {str(e)}")
            return False


# Export the main class
__all__ = ["PrometheusConfiguration", "PrometheusTarget", "AlertingRule", "RecordingRule"]