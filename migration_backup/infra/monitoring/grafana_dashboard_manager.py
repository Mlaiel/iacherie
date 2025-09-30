# Ainflue Infrastructure Module - Grafana Dashboard Manager
# =======================================================
# 
# Enterprise-grade Grafana dashboard management for Ainflue platform
# Supports multi-cloud monitoring and enterprise observability
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import yaml
import os

@dataclass
class GrafanaConfig:
    """Configuration for Grafana dashboard management"""
    url: str
    username: str
    password: str
    organization: str = "Ainflue"
    timeout: int = 30
    verify_ssl: bool = True

class GrafanaDashboardManager:
    """Enterprise Grafana dashboard management for multi-cloud monitoring"""
    
    def __init__(self, config: GrafanaConfig):
        """Initialize Grafana dashboard manager
        
        Args:
            config: Grafana configuration
        """
        self.config = config
        self.logger = self._setup_logging()
        self.session = requests.Session()
        self.session.auth = (config.username, config.password)
        self.session.verify = config.verify_ssl
        
        # Dashboard templates
        self.dashboard_templates = self._load_dashboard_templates()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(f"ainflue.infra.monitoring.grafana_manager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _load_dashboard_templates(self) -> Dict[str, Dict]:
        """Load dashboard templates from configuration"""
        return {
            "ainflue_overview": self._get_overview_dashboard(),
            "ai_engine_metrics": self._get_ai_engine_dashboard(),
            "api_performance": self._get_api_performance_dashboard(),
            "mobile_app_metrics": self._get_mobile_app_dashboard(),
            "infrastructure_health": self._get_infrastructure_dashboard(),
            "security_monitoring": self._get_security_dashboard(),
            "business_metrics": self._get_business_dashboard()
        }
    
    async def create_dashboard(self, dashboard_name: str, 
                             custom_config: Optional[Dict] = None) -> bool:
        """Create a Grafana dashboard
        
        Args:
            dashboard_name: Name of the dashboard to create
            custom_config: Optional custom configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if dashboard_name not in self.dashboard_templates:
                self.logger.error(f"Unknown dashboard template: {dashboard_name}")
                return False
            
            dashboard = self.dashboard_templates[dashboard_name].copy()
            
            # Apply custom configuration if provided
            if custom_config:
                dashboard.update(custom_config)
            
            # Create dashboard payload
            payload = {
                "dashboard": dashboard,
                "overwrite": True,
                "message": f"Created by Ainflue Infrastructure Manager"
            }
            
            response = self.session.post(
                f"{self.config.url}/api/dashboards/db",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully created dashboard: {dashboard_name}")
                return True
            else:
                self.logger.error(f"Failed to create dashboard {dashboard_name}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating dashboard {dashboard_name}: {e}")
            return False
    
    async def update_dashboard(self, dashboard_id: str, updates: Dict) -> bool:
        """Update an existing dashboard
        
        Args:
            dashboard_id: ID of the dashboard to update
            updates: Updates to apply
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current dashboard
            response = self.session.get(
                f"{self.config.url}/api/dashboards/uid/{dashboard_id}",
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                self.logger.error(f"Failed to get dashboard {dashboard_id}: {response.text}")
                return False
            
            current_dashboard = response.json()["dashboard"]
            
            # Apply updates
            current_dashboard.update(updates)
            
            # Update dashboard
            payload = {
                "dashboard": current_dashboard,
                "overwrite": True,
                "message": "Updated by Ainflue Infrastructure Manager"
            }
            
            response = self.session.post(
                f"{self.config.url}/api/dashboards/db",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully updated dashboard: {dashboard_id}")
                return True
            else:
                self.logger.error(f"Failed to update dashboard {dashboard_id}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating dashboard {dashboard_id}: {e}")
            return False
    
    async def create_data_source(self, name: str, ds_type: str, url: str, 
                               additional_config: Optional[Dict] = None) -> bool:
        """Create a Grafana data source
        
        Args:
            name: Name of the data source
            ds_type: Type of data source (prometheus, elasticsearch, etc.)
            url: URL of the data source
            additional_config: Additional configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            payload = {
                "name": name,
                "type": ds_type,
                "url": url,
                "access": "proxy",
                "isDefault": False
            }
            
            if additional_config:
                payload.update(additional_config)
            
            response = self.session.post(
                f"{self.config.url}/api/datasources",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully created data source: {name}")
                return True
            else:
                self.logger.error(f"Failed to create data source {name}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating data source {name}: {e}")
            return False
    
    async def setup_alerting(self, dashboard_name: str, alert_rules: List[Dict]) -> bool:
        """Setup alerting for a dashboard
        
        Args:
            dashboard_name: Name of the dashboard
            alert_rules: List of alert rule configurations
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for rule in alert_rules:
                payload = {
                    "alert": {
                        "name": rule["name"],
                        "message": rule["message"],
                        "frequency": rule.get("frequency", "10s"),
                        "conditions": rule["conditions"],
                        "executionErrorState": "alerting",
                        "noDataState": "no_data",
                        "for": rule.get("for", "5m")
                    }
                }
                
                response = self.session.post(
                    f"{self.config.url}/api/alerts",
                    json=payload,
                    timeout=self.config.timeout
                )
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to create alert rule {rule['name']}: {response.text}")
                    return False
            
            self.logger.info(f"Successfully setup alerting for dashboard: {dashboard_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up alerting for {dashboard_name}: {e}")
            return False
    
    def _get_overview_dashboard(self) -> Dict:
        """Get Ainflue overview dashboard configuration"""
        return {
            "id": None,
            "title": "Ainflue Platform Overview",
            "tags": ["ainflue", "overview"],
            "timezone": "browser",
            "refresh": "30s",
            "schemaVersion": 16,
            "version": 1,
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "Total Users",
                    "type": "singlestat",
                    "targets": [
                        {
                            "expr": "sum(ainflue_total_users)",
                            "legendFormat": "Total Users"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Active Content Creators",
                    "type": "singlestat",
                    "targets": [
                        {
                            "expr": "sum(ainflue_active_creators)",
                            "legendFormat": "Active Creators"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "AI Processing Requests",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(ainflue_ai_requests_total[5m])",
                            "legendFormat": "AI Requests/sec"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 24, "x": 0, "y": 9}
                },
                {
                    "id": 4,
                    "title": "Revenue Metrics",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(ainflue_revenue_total)",
                            "legendFormat": "Total Revenue"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 24, "x": 0, "y": 18}
                }
            ]
        }
    
    def _get_ai_engine_dashboard(self) -> Dict:
        """Get AI engine monitoring dashboard configuration"""
        return {
            "id": None,
            "title": "Ainflue AI Engine Metrics",
            "tags": ["ainflue", "ai", "ml"],
            "timezone": "browser",
            "refresh": "10s",
            "schemaVersion": 16,
            "version": 1,
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "GPU Utilization",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "nvidia_smi_utilization_gpu",
                            "legendFormat": "GPU {{ gpu }}"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "GPU Memory Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "nvidia_smi_memory_used_bytes / nvidia_smi_memory_total_bytes * 100",
                            "legendFormat": "GPU {{ gpu }} Memory %"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "AI Model Inference Time",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, ainflue_ai_inference_duration_seconds_bucket)",
                            "legendFormat": "95th percentile"
                        },
                        {
                            "expr": "histogram_quantile(0.50, ainflue_ai_inference_duration_seconds_bucket)",
                            "legendFormat": "50th percentile"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 24, "x": 0, "y": 9}
                },
                {
                    "id": 4,
                    "title": "Processing Queue Size",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "ainflue_ai_queue_size",
                            "legendFormat": "Queue Size"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 24, "x": 0, "y": 18}
                }
            ]
        }
    
    def _get_api_performance_dashboard(self) -> Dict:
        """Get API performance dashboard configuration"""
        return {
            "id": None,
            "title": "Ainflue API Performance",
            "tags": ["ainflue", "api", "performance"],
            "timezone": "browser",
            "refresh": "30s",
            "schemaVersion": 16,
            "version": 1,
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "Request Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(rate(http_requests_total[5m])) by (method, status)",
                            "legendFormat": "{{ method }} {{ status }}"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Response Time",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)",
                            "legendFormat": "95th percentile"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Error Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))",
                            "legendFormat": "Error Rate"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 24, "x": 0, "y": 9}
                }
            ]
        }
    
    def _get_mobile_app_dashboard(self) -> Dict:
        """Get mobile app metrics dashboard configuration"""
        return {
            "id": None,
            "title": "Ainflue Mobile App Metrics",
            "tags": ["ainflue", "mobile", "app"],
            "timezone": "browser",
            "refresh": "1m",
            "schemaVersion": 16,
            "version": 1,
            "time": {
                "from": "now-24h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "Active Mobile Users",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(ainflue_mobile_active_users) by (platform)",
                            "legendFormat": "{{ platform }}"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "App Crashes",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(rate(ainflue_mobile_crashes_total[1h])) by (platform)",
                            "legendFormat": "{{ platform }} crashes/hour"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Content Upload Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(rate(ainflue_content_uploads_total[5m])) by (content_type)",
                            "legendFormat": "{{ content_type }}"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 24, "x": 0, "y": 9}
                }
            ]
        }
    
    def _get_infrastructure_dashboard(self) -> Dict:
        """Get infrastructure health dashboard configuration"""
        return {
            "id": None,
            "title": "Ainflue Infrastructure Health",
            "tags": ["ainflue", "infrastructure", "kubernetes"],
            "timezone": "browser",
            "refresh": "30s",
            "schemaVersion": 16,
            "version": 1,
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "Pod Status",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(kube_pod_status_phase) by (phase)",
                            "legendFormat": "{{ phase }}"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Node Status",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(kube_node_status_condition) by (condition, status)",
                            "legendFormat": "{{ condition }}: {{ status }}"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "CPU Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(rate(container_cpu_usage_seconds_total[5m])) by (pod)",
                            "legendFormat": "{{ pod }}"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 24, "x": 0, "y": 9}
                }
            ]
        }
    
    def _get_security_dashboard(self) -> Dict:
        """Get security monitoring dashboard configuration"""
        return {
            "id": None,
            "title": "Ainflue Security Monitoring",
            "tags": ["ainflue", "security", "threats"],
            "timezone": "browser",
            "refresh": "1m",
            "schemaVersion": 16,
            "version": 1,
            "time": {
                "from": "now-24h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "Failed Login Attempts",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(rate(ainflue_failed_logins_total[5m]))",
                            "legendFormat": "Failed Logins/5min"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Suspicious Activity",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(rate(ainflue_suspicious_activity_total[1h])) by (type)",
                            "legendFormat": "{{ type }}"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "WAF Blocked Requests",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(rate(ainflue_waf_blocked_total[5m])) by (rule)",
                            "legendFormat": "{{ rule }}"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 24, "x": 0, "y": 9}
                }
            ]
        }
    
    def _get_business_dashboard(self) -> Dict:
        """Get business metrics dashboard configuration"""
        return {
            "id": None,
            "title": "Ainflue Business Metrics",
            "tags": ["ainflue", "business", "revenue"],
            "timezone": "browser",
            "refresh": "5m",
            "schemaVersion": 16,
            "version": 1,
            "time": {
                "from": "now-7d",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "Daily Revenue",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(increase(ainflue_revenue_total[1d]))",
                            "legendFormat": "Daily Revenue"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "New User Registrations",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(increase(ainflue_user_registrations_total[1d]))",
                            "legendFormat": "Daily Registrations"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Content Creation Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "sum(rate(ainflue_content_created_total[1h])) by (type)",
                            "legendFormat": "{{ type }} content/hour"
                        }
                    ],
                    "gridPos": {"h": 9, "w": 24, "x": 0, "y": 9}
                }
            ]
        }

# Example usage
async def setup_ainflue_dashboards():
    """Setup all Ainflue Grafana dashboards"""
    config = GrafanaConfig(
        url="http://grafana.ainflue.local",
        username="admin",
        password="admin123"
    )
    
    manager = GrafanaDashboardManager(config)
    
    # Create data sources
    await manager.create_data_source(
        name="Prometheus",
        ds_type="prometheus",
        url="http://prometheus.ainflue.local:9090"
    )
    
    # Create dashboards
    dashboards = [
        "ainflue_overview",
        "ai_engine_metrics", 
        "api_performance",
        "mobile_app_metrics",
        "infrastructure_health",
        "security_monitoring",
        "business_metrics"
    ]
    
    for dashboard in dashboards:
        success = await manager.create_dashboard(dashboard)
        if success:
            print(f"✅ Created dashboard: {dashboard}")
        else:
            print(f"❌ Failed to create dashboard: {dashboard}")

if __name__ == "__main__":
    asyncio.run(setup_ainflue_dashboards())