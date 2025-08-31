"""IA Influencer Agent - Grafana Dashboard Manager
Enterprise-grade visualization and monitoring dashboards for multi-tenant AI platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Dynamic dashboard creation and management
- Multi-tenant dashboard isolation
- Real-time visualization updates
- AI model performance dashboards
- Content protection monitoring
- Revenue analytics dashboards
- Infrastructure monitoring
- Alert integration and visualization
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import requests
import aiohttp
from pathlib import Path

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.models.metrics import DashboardModel, PanelModel
from backend.utils.redis_manager import RedisManager
from backend.utils.database import get_database_session

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class DashboardConfig:
    """Dashboard configuration structure"""
    title: str
    description: str
    tags: List[str] = field(default_factory=list)
    time_range: Dict[str, str] = field(default_factory=lambda: {"from": "now-1h", "to": "now"})
    refresh_interval: str = "30s"
    editable: bool = True
    shared_crossfilter: bool = False
    tenant_id: Optional[str] = None


@dataclass
class PanelConfig:
    """Panel configuration structure"""
    title: str
    panel_type: str  # graph, stat, table, heatmap, etc.
    targets: List[Dict[str, Any]]
    grid_pos: Dict[str, int]  # x, y, w, h
    options: Optional[Dict[str, Any]] = None
    field_config: Optional[Dict[str, Any]] = None
    alert: Optional[Dict[str, Any]] = None


class GrafanaManager:
    """
    Enterprise Grafana dashboard manager with multi-tenant support
    
    Handles:
    - Dashboard creation and management
    - Panel configuration and updates
    - Data source management
    - Alert rule integration
    - Template variable management
    - Multi-tenant dashboard isolation
    """
    
    def __init__(self):
        self.base_url = settings.GRAFANA_URL
        self.api_key = settings.GRAFANA_API_KEY
        self.organization_id = settings.GRAFANA_ORG_ID
        self.redis_manager = RedisManager()
        self.logger = logger
        self.session = None
        self._dashboard_templates = {}
        self._initialize_templates()
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _initialize_templates(self) -> None:
        """Initialize dashboard templates"""
        self._dashboard_templates = {
            'application_overview': self._get_application_overview_template(),
            'ai_model_performance': self._get_ai_model_performance_template(),
            'content_protection': self._get_content_protection_template(),
            'revenue_analytics': self._get_revenue_analytics_template(),
            'infrastructure_monitoring': self._get_infrastructure_monitoring_template(),
            'user_activity': self._get_user_activity_template(),
            'security_monitoring': self._get_security_monitoring_template(),
            'business_intelligence': self._get_business_intelligence_template(),
            'api_analytics': self._get_api_analytics_template()
        }
    
    async def create_dashboard(
        self,
        config: DashboardConfig,
        template_name: Optional[str] = None,
        custom_panels: Optional[List[PanelConfig]] = None
    ) -> Dict[str, Any]:
        """Create new dashboard"""
        try:
            if template_name and template_name in self._dashboard_templates:
                dashboard_json = self._dashboard_templates[template_name].copy()
                dashboard_json['dashboard']['title'] = config.title
                dashboard_json['dashboard']['description'] = config.description
                dashboard_json['dashboard']['tags'] = config.tags
            else:
                dashboard_json = self._create_custom_dashboard(config, custom_panels)
            
            # Add tenant isolation if specified
            if config.tenant_id:
                self._apply_tenant_isolation(dashboard_json, config.tenant_id)
            
            async with self.session.post(
                f"{self.base_url}/api/dashboards/db",
                json=dashboard_json
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Dashboard created: {config.title}")
                    
                    # Cache dashboard info
                    await self._cache_dashboard_info(result, config.tenant_id)
                    
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create dashboard: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            raise
    
    async def update_dashboard(
        self,
        dashboard_id: int,
        config: DashboardConfig,
        panels: Optional[List[PanelConfig]] = None
    ) -> Dict[str, Any]:
        """Update existing dashboard"""
        try:
            # Get current dashboard
            current_dashboard = await self.get_dashboard(dashboard_id)
            
            if not current_dashboard:
                raise Exception(f"Dashboard {dashboard_id} not found")
            
            # Update dashboard properties
            dashboard_json = current_dashboard.copy()
            dashboard_json['dashboard']['title'] = config.title
            dashboard_json['dashboard']['description'] = config.description
            dashboard_json['dashboard']['tags'] = config.tags
            
            # Update panels if provided
            if panels:
                dashboard_json['dashboard']['panels'] = [
                    self._panel_config_to_json(panel) for panel in panels
                ]
            
            async with self.session.post(
                f"{self.base_url}/api/dashboards/db",
                json=dashboard_json
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Dashboard updated: {dashboard_id}")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to update dashboard: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
            raise
    
    async def get_dashboard(self, dashboard_id: int) -> Optional[Dict[str, Any]]:
        """Get dashboard by ID"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/dashboards/id/{dashboard_id}"
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get dashboard: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error getting dashboard: {e}")
            return None
    
    async def delete_dashboard(self, dashboard_uid: str) -> bool:
        """Delete dashboard by UID"""
        try:
            async with self.session.delete(
                f"{self.base_url}/api/dashboards/uid/{dashboard_uid}"
            ) as response:
                if response.status == 200:
                    self.logger.info(f"Dashboard deleted: {dashboard_uid}")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(f"Failed to delete dashboard: {error_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error deleting dashboard: {e}")
            return False
    
    async def get_tenant_dashboards(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get all dashboards for specific tenant"""
        try:
            # Get from cache first
            cached_dashboards = await self.redis_manager.get_json(f"dashboards:tenant:{tenant_id}")
            if cached_dashboards:
                return cached_dashboards
            
            # Search dashboards with tenant tag
            async with self.session.get(
                f"{self.base_url}/api/search",
                params={'tag': f'tenant:{tenant_id}'}
            ) as response:
                if response.status == 200:
                    dashboards = await response.json()
                    
                    # Cache results
                    await self.redis_manager.set_json(
                        f"dashboards:tenant:{tenant_id}",
                        dashboards,
                        expire=300  # 5 minutes
                    )
                    
                    return dashboards
                else:
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error getting tenant dashboards: {e}")
            return []
    
    async def create_data_source(
        self,
        name: str,
        source_type: str,
        url: str,
        access: str = "proxy",
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new data source"""
        try:
            data_source_config = {
                "name": name,
                "type": source_type,
                "url": url,
                "access": access,
                "isDefault": False
            }
            
            if database:
                data_source_config["database"] = database
            
            if user and password:
                data_source_config["user"] = user
                data_source_config["password"] = password
            
            # Add tenant isolation
            if tenant_id:
                data_source_config["name"] = f"{name}_{tenant_id}"
            
            async with self.session.post(
                f"{self.base_url}/api/datasources",
                json=data_source_config
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Data source created: {name}")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create data source: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error creating data source: {e}")
            raise
    
    async def create_alert_rule(
        self,
        title: str,
        condition: Dict[str, Any],
        dashboard_id: int,
        panel_id: int,
        frequency: str = "60s",
        notifications: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create alert rule for dashboard panel"""
        try:
            alert_config = {
                "dashboardId": dashboard_id,
                "panelId": panel_id,
                "name": title,
                "frequency": frequency,
                "conditions": [condition],
                "executionErrorState": "alerting",
                "noDataState": "no_data",
                "for": "5m"
            }
            
            if notifications:
                alert_config["notifications"] = notifications
            
            async with self.session.post(
                f"{self.base_url}/api/alerts",
                json=alert_config
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Alert rule created: {title}")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create alert rule: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error creating alert rule: {e}")
            raise
    
    async def setup_tenant_dashboards(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Setup default dashboards for new tenant"""
        try:
            created_dashboards = []
            
            # Create default dashboards for tenant
            for template_name, _ in self._dashboard_templates.items():
                config = DashboardConfig(
                    title=f"{template_name.replace('_', ' ').title()} - {tenant_id}",
                    description=f"Auto-generated {template_name} dashboard for tenant {tenant_id}",
                    tags=[f"tenant:{tenant_id}", template_name, "auto-generated"],
                    tenant_id=tenant_id
                )
                
                dashboard = await self.create_dashboard(config, template_name)
                created_dashboards.append(dashboard)
            
            self.logger.info(f"Created {len(created_dashboards)} dashboards for tenant {tenant_id}")
            return created_dashboards
            
        except Exception as e:
            self.logger.error(f"Error setting up tenant dashboards: {e}")
            return []
    
    def _get_application_overview_template(self) -> Dict[str, Any]:
        """Application overview dashboard template"""
        return {
            "dashboard": {
                "title": "Application Overview",
                "description": "High-level application performance metrics",
                "tags": ["application", "overview"],
                "panels": [
                    {
                        "id": 1,
                        "title": "HTTP Requests Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_http_requests_total[5m])",
                            "legendFormat": "{{method}} {{endpoint}}"
                        }],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "title": "Response Time",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, rate(ia_influencer_http_request_duration_seconds_bucket[5m]))",
                            "legendFormat": "95th percentile"
                        }],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 3,
                        "title": "Active Users",
                        "type": "stat",
                        "targets": [{
                            "expr": "ia_influencer_active_users",
                            "legendFormat": "{{time_window}} {{user_type}}"
                        }],
                        "gridPos": {"x": 0, "y": 8, "w": 6, "h": 4}
                    },
                    {
                        "id": 4,
                        "title": "Error Rate",
                        "type": "stat",
                        "targets": [{
                            "expr": "rate(ia_influencer_http_requests_total{status_code=~'5..'}[5m])",
                            "legendFormat": "5xx errors"
                        }],
                        "gridPos": {"x": 6, "y": 8, "w": 6, "h": 4}
                    }
                ]
            },
            "overwrite": True
        }
    
    def _get_ai_model_performance_template(self) -> Dict[str, Any]:
        """AI model performance dashboard template"""
        return {
            "dashboard": {
                "title": "AI Model Performance",
                "description": "AI model inference and accuracy metrics",
                "tags": ["ai", "models", "performance"],
                "panels": [
                    {
                        "id": 1,
                        "title": "Model Predictions Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_ai_predictions_total[5m])",
                            "legendFormat": "{{model_name}} {{prediction_type}}"
                        }],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "title": "Inference Duration",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, rate(ia_influencer_ai_inference_duration_seconds_bucket[5m]))",
                            "legendFormat": "{{model_name}} 95th percentile"
                        }],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 3,
                        "title": "Model Accuracy",
                        "type": "stat",
                        "targets": [{
                            "expr": "ia_influencer_ai_model_accuracy",
                            "legendFormat": "{{model_name}} {{metric_type}}"
                        }],
                        "gridPos": {"x": 0, "y": 8, "w": 24, "h": 8}
                    }
                ]
            },
            "overwrite": True
        }
    
    def _get_content_protection_template(self) -> Dict[str, Any]:
        """Content protection dashboard template"""
        return {
            "dashboard": {
                "title": "Content Protection",
                "description": "Content fingerprinting and protection metrics",
                "tags": ["content", "protection", "fingerprinting"],
                "panels": [
                    {
                        "id": 1,
                        "title": "Fingerprints Created",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_fingerprints_created_total[5m])",
                            "legendFormat": "{{content_type}} {{fingerprint_algorithm}}"
                        }],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "title": "Content Matches Detected",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_content_matches_total[5m])",
                            "legendFormat": "{{platform}} {{content_type}}"
                        }],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 3,
                        "title": "Fingerprint Processing Time",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, rate(ia_influencer_fingerprint_processing_seconds_bucket[5m]))",
                            "legendFormat": "{{content_type}} 95th percentile"
                        }],
                        "gridPos": {"x": 0, "y": 8, "w": 24, "h": 8}
                    }
                ]
            },
            "overwrite": True
        }
    
    def _get_revenue_analytics_template(self) -> Dict[str, Any]:
        """Revenue analytics dashboard template"""
        return {
            "dashboard": {
                "title": "Revenue Analytics",
                "description": "Revenue tracking and business metrics",
                "tags": ["revenue", "business", "analytics"],
                "panels": [
                    {
                        "id": 1,
                        "title": "Revenue by Platform",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_revenue_tracked_total[1h])",
                            "legendFormat": "{{platform}} {{currency}}"
                        }],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "title": "Licensing Transactions",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_licensing_transactions_total[5m])",
                            "legendFormat": "{{license_type}} {{status}}"
                        }],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 3,
                        "title": "Total Revenue (24h)",
                        "type": "stat",
                        "targets": [{
                            "expr": "sum(increase(ia_influencer_revenue_tracked_total[24h]))",
                            "legendFormat": "Total Revenue"
                        }],
                        "gridPos": {"x": 0, "y": 8, "w": 6, "h": 4}
                    },
                    {
                        "id": 4,
                        "title": "Revenue Growth Rate",
                        "type": "stat",
                        "targets": [{
                            "expr": "rate(ia_influencer_revenue_tracked_total[7d])",
                            "legendFormat": "Weekly Growth"
                        }],
                        "gridPos": {"x": 6, "y": 8, "w": 6, "h": 4}
                    },
                    {
                        "id": 5,
                        "title": "Revenue by Content Type",
                        "type": "piechart",
                        "targets": [{
                            "expr": "sum by (content_type) (increase(ia_influencer_revenue_tracked_total[24h]))",
                            "legendFormat": "{{content_type}}"
                        }],
                        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "id": 6,
                        "title": "Top Revenue Generating Users",
                        "type": "table",
                        "targets": [{
                            "expr": "topk(10, sum by (user_id) (increase(ia_influencer_revenue_tracked_total[24h])))",
                            "legendFormat": "{{user_id}}"
                        }],
                        "gridPos": {"x": 0, "y": 12, "w": 12, "h": 8}
                    },
                    {
                        "id": 7,
                        "title": "Payment Success Rate",
                        "type": "gauge",
                        "targets": [{
                            "expr": "rate(ia_influencer_payments_successful_total[5m]) / rate(ia_influencer_payments_total[5m])",
                            "legendFormat": "Success Rate"
                        }],
                        "gridPos": {"x": 12, "y": 12, "w": 12, "h": 8}
                    }
                ]
            },
            "overwrite": True
        }
    
    def _get_infrastructure_monitoring_template(self) -> Dict[str, Any]:
        """Infrastructure monitoring dashboard template"""
        return {
            "dashboard": {
                "title": "Infrastructure Monitoring",
                "description": "System resources and infrastructure metrics",
                "tags": ["infrastructure", "system", "monitoring"],
                "panels": [
                    {
                        "id": 1,
                        "title": "CPU Usage",
                        "type": "graph",
                        "targets": [{
                            "expr": "ia_influencer_system_cpu_usage_percent",
                            "legendFormat": "Core {{core}}"
                        }],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "title": "Memory Usage",
                        "type": "graph",
                        "targets": [{
                            "expr": "ia_influencer_system_memory_usage_bytes",
                            "legendFormat": "{{type}}"
                        }],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 3,
                        "title": "Disk I/O",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_disk_reads_total[5m])",
                            "legendFormat": "Disk Reads"
                        }, {
                            "expr": "rate(ia_influencer_disk_writes_total[5m])",
                            "legendFormat": "Disk Writes"
                        }],
                        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "id": 4,
                        "title": "Network Traffic",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_network_bytes_received_total[5m])",
                            "legendFormat": "Bytes Received"
                        }, {
                            "expr": "rate(ia_influencer_network_bytes_sent_total[5m])",
                            "legendFormat": "Bytes Sent"
                        }],
                        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "id": 5,
                        "title": "Database Connections",
                        "type": "stat",
                        "targets": [{
                            "expr": "ia_influencer_database_connections_active",
                            "legendFormat": "Active Connections"
                        }],
                        "gridPos": {"x": 0, "y": 16, "w": 6, "h": 4}
                    },
                    {
                        "id": 6,
                        "title": "Redis Cache Hit Rate",
                        "type": "gauge",
                        "targets": [{
                            "expr": "ia_influencer_redis_cache_hit_rate",
                            "legendFormat": "Cache Hit Rate"
                        }],
                        "gridPos": {"x": 6, "y": 16, "w": 6, "h": 4}
                    },
                    {
                        "id": 7,
                        "title": "Container Resource Usage",
                        "type": "table",
                        "targets": [{
                            "expr": "topk(10, ia_influencer_container_cpu_usage_percent)",
                            "legendFormat": "{{container_name}} CPU"
                        }],
                        "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8}
                    }
                ]
            },
            "overwrite": True
        }
    
    def _get_user_activity_template(self) -> Dict[str, Any]:
        """User activity dashboard template"""
        return {
            "dashboard": {
                "title": "User Activity",
                "description": "User engagement and activity metrics",
                "tags": ["users", "activity", "engagement"],
                "panels": [
                    {
                        "id": 1,
                        "title": "Active Users by Type",
                        "type": "graph",
                        "targets": [{
                            "expr": "ia_influencer_active_users",
                            "legendFormat": "{{user_type}} - {{time_window}}"
                        }],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "title": "User Engagement Score",
                        "type": "gauge",
                        "targets": [{
                            "expr": "avg(ia_influencer_user_engagement_score)",
                            "legendFormat": "Average Engagement"
                        }],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 3,
                        "title": "Content Uploads by User Type",
                        "type": "piechart",
                        "targets": [{
                            "expr": "rate(ia_influencer_content_uploads_total[1h])",
                            "legendFormat": "{{user_type}}"
                        }],
                        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "id": 4,
                        "title": "User Session Duration",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, rate(ia_influencer_session_duration_seconds_bucket[5m]))",
                            "legendFormat": "Session Duration P95"
                        }],
                        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "id": 5,
                        "title": "User Registration Rate",
                        "type": "stat",
                        "targets": [{
                            "expr": "rate(ia_influencer_user_registrations_total[1h])",
                            "legendFormat": "New Users/hour"
                        }],
                        "gridPos": {"x": 0, "y": 16, "w": 6, "h": 4}
                    },
                    {
                        "id": 6,
                        "title": "User Retention Rate",
                        "type": "stat",
                        "targets": [{
                            "expr": "ia_influencer_user_retention_rate",
                            "legendFormat": "{{period}} Retention"
                        }],
                        "gridPos": {"x": 6, "y": 16, "w": 6, "h": 4}
                    },
                    {
                        "id": 7,
                        "title": "Most Active Users",
                        "type": "table",
                        "targets": [{
                            "expr": "topk(10, sum by (user_id) (rate(ia_influencer_user_actions_total[24h])))",
                            "legendFormat": "{{user_id}}"
                        }],
                        "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8}
                    }
                ]
            },
            "overwrite": True
        }
    
    def _get_security_monitoring_template(self) -> Dict[str, Any]:
        """Security monitoring dashboard template"""
        return {
            "dashboard": {
                "title": "Security Monitoring",
                "description": "Security events and threat detection",
                "tags": ["security", "monitoring", "threats"],
                "panels": [
                    {
                        "id": 1,
                        "title": "Failed Authentication Attempts",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_http_requests_total{status_code='401'}[5m])",
                            "legendFormat": "Failed logins"
                        }],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "title": "Security Incidents by Severity",
                        "type": "stat",
                        "targets": [{
                            "expr": "ia_influencer_security_incidents_total",
                            "legendFormat": "{{severity}}"
                        }],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 3,
                        "title": "Suspicious Activity Score",
                        "type": "heatmap",
                        "targets": [{
                            "expr": "ia_influencer_suspicious_activity_score",
                            "legendFormat": "{{source_ip}}"
                        }],
                        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "id": 4,
                        "title": "Rate Limiting Violations",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_rate_limit_exceeded_total[5m])",
                            "legendFormat": "{{endpoint}} violations"
                        }],
                        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "id": 5,
                        "title": "Content Protection Threats",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_content_protection_threats_total[5m])",
                            "legendFormat": "{{threat_type}}"
                        }],
                        "gridPos": {"x": 0, "y": 16, "w": 12, "h": 8}
                    },
                    {
                        "id": 6,
                        "title": "User Account Anomalies",
                        "type": "table",
                        "targets": [{
                            "expr": "topk(10, ia_influencer_user_anomaly_score > 0.7)",
                            "legendFormat": "{{user_id}} - {{anomaly_type}}"
                        }],
                        "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8}
                    }
                ]
            },
            "overwrite": True
        }
    
    def _get_business_intelligence_template(self) -> Dict[str, Any]:
        """Business intelligence dashboard template"""
        return {
            "dashboard": {
                "title": "Business Overview",
                "description": "High-level business metrics and KPIs",
                "tags": ["business", "overview", "kpis"],
                "panels": [
                    {
                        "id": 1,
                        "title": "Total Revenue",
                        "type": "stat",
                        "targets": [{
                            "expr": "sum(ia_influencer_revenue_tracked_total)",
                            "legendFormat": "Total Revenue"
                        }],
                        "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4}
                    },
                    {
                        "id": 2,
                        "title": "Active Users",
                        "type": "stat",
                        "targets": [{
                            "expr": "sum(ia_influencer_active_users)",
                            "legendFormat": "Active Users"
                        }],
                        "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4}
                    },
                    {
                        "id": 3,
                        "title": "Content Protected",
                        "type": "stat",
                        "targets": [{
                            "expr": "sum(ia_influencer_content_protected_total)",
                            "legendFormat": "Protected Items"
                        }],
                        "gridPos": {"x": 12, "y": 0, "w": 6, "h": 4}
                    },
                    {
                        "id": 4,
                        "title": "Platform Health",
                        "type": "stat",
                        "targets": [{
                            "expr": "avg(up)",
                            "legendFormat": "System Uptime"
                        }],
                        "gridPos": {"x": 18, "y": 0, "w": 6, "h": 4}
                    },
                    {
                        "id": 5,
                        "title": "Revenue Trend (7 days)",
                        "type": "graph",
                        "targets": [{
                            "expr": "increase(ia_influencer_revenue_tracked_total[1d])",
                            "legendFormat": "Daily Revenue"
                        }],
                        "gridPos": {"x": 0, "y": 4, "w": 12, "h": 8}
                    },
                    {
                        "id": 6,
                        "title": "User Growth",
                        "type": "graph",
                        "targets": [{
                            "expr": "increase(ia_influencer_user_registrations_total[1d])",
                            "legendFormat": "New Users/Day"
                        }],
                        "gridPos": {"x": 12, "y": 4, "w": 12, "h": 8}
                    },
                    {
                        "id": 7,
                        "title": "Top Performing Platforms",
                        "type": "table",
                        "targets": [{
                            "expr": "topk(5, sum by (platform) (increase(ia_influencer_revenue_tracked_total[24h])))",
                            "legendFormat": "{{platform}}"
                        }],
                        "gridPos": {"x": 0, "y": 12, "w": 12, "h": 8}
                    },
                    {
                        "id": 8,
                        "title": "Content Protection Efficiency",
                        "type": "gauge",
                        "targets": [{
                            "expr": "rate(ia_influencer_content_matches_total[5m]) / rate(ia_influencer_content_scans_total[5m])",
                            "legendFormat": "Match Rate"
                        }],
                        "gridPos": {"x": 12, "y": 12, "w": 12, "h": 8}
                    }
                ]
            },
            "overwrite": True
        }
    
    def _get_api_analytics_template(self) -> Dict[str, Any]:
        """API analytics dashboard template"""
        return {
            "dashboard": {
                "title": "API Analytics",
                "description": "API usage, performance, and endpoint analytics",
                "tags": ["api", "analytics", "performance"],
                "panels": [
                    {
                        "id": 1,
                        "title": "API Request Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_http_requests_total[5m])",
                            "legendFormat": "{{method}} {{endpoint}}"
                        }],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "title": "API Response Times",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, rate(ia_influencer_http_request_duration_seconds_bucket[5m]))",
                            "legendFormat": "{{endpoint}} P95"
                        }],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 3,
                        "title": "API Error Rate by Endpoint",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(ia_influencer_http_requests_total{status_code=~\"4..|5..\"}[5m]) / rate(ia_influencer_http_requests_total[5m])",
                            "legendFormat": "{{endpoint}} {{status_code}}"
                        }],
                        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "id": 4,
                        "title": "Top API Endpoints by Usage",
                        "type": "table",
                        "targets": [{
                            "expr": "topk(10, sum by (endpoint) (rate(ia_influencer_http_requests_total[1h])))",
                            "legendFormat": "{{endpoint}}"
                        }],
                        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "id": 5,
                        "title": "API Rate Limiting Events",
                        "type": "stat",
                        "targets": [{
                            "expr": "rate(ia_influencer_rate_limit_exceeded_total[5m])",
                            "legendFormat": "Rate Limited Requests/sec"
                        }],
                        "gridPos": {"x": 0, "y": 16, "w": 6, "h": 4}
                    },
                    {
                        "id": 6,
                        "title": "Active API Clients",
                        "type": "stat",
                        "targets": [{
                            "expr": "count by (client_id) (rate(ia_influencer_http_requests_total[5m]) > 0)",
                            "legendFormat": "Active Clients"
                        }],
                        "gridPos": {"x": 6, "y": 16, "w": 6, "h": 4}
                    },
                    {
                        "id": 7,
                        "title": "API Payload Size Distribution",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, rate(ia_influencer_http_request_size_bytes_bucket[5m]))",
                            "legendFormat": "Request Size P95"
                        }, {
                            "expr": "histogram_quantile(0.95, rate(ia_influencer_http_response_size_bytes_bucket[5m]))",
                            "legendFormat": "Response Size P95"
                        }],
                        "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8}
                    }
                ]
            },
            "overwrite": True
        }
    
    def _create_custom_dashboard(
        self,
        config: DashboardConfig,
        panels: Optional[List[PanelConfig]] = None
    ) -> Dict[str, Any]:
        """Create custom dashboard from configuration"""
        dashboard_json = {
            "dashboard": {
                "title": config.title,
                "description": config.description,
                "tags": config.tags,
                "time": config.time_range,
                "refresh": config.refresh_interval,
                "editable": config.editable,
                "sharedCrosshair": config.shared_crossfilter,
                "panels": []
            },
            "overwrite": True
        }
        
        if panels:
            dashboard_json["dashboard"]["panels"] = [
                self._panel_config_to_json(panel) for panel in panels
            ]
        
        return dashboard_json
    
    def _panel_config_to_json(self, panel: PanelConfig) -> Dict[str, Any]:
        """Convert panel configuration to Grafana JSON format"""
        panel_json = {
            "title": panel.title,
            "type": panel.panel_type,
            "targets": panel.targets,
            "gridPos": panel.grid_pos
        }
        
        if panel.options:
            panel_json["options"] = panel.options
        
        if panel.field_config:
            panel_json["fieldConfig"] = panel.field_config
        
        if panel.alert:
            panel_json["alert"] = panel.alert
        
        return panel_json
    
    def _apply_tenant_isolation(self, dashboard_json: Dict[str, Any], tenant_id: str) -> None:
        """Apply tenant isolation to dashboard"""
        # Add tenant tag
        if "tags" not in dashboard_json["dashboard"]:
            dashboard_json["dashboard"]["tags"] = []
        
        dashboard_json["dashboard"]["tags"].append(f"tenant:{tenant_id}")
        
        # Apply tenant filter to all panel queries
        for panel in dashboard_json["dashboard"].get("panels", []):
            for target in panel.get("targets", []):
                if "expr" in target:
                    # Add tenant_id filter to Prometheus queries
                    expr = target["expr"]
                    if "{" in expr:
                        # Insert tenant_id filter into existing label selectors
                        target["expr"] = expr.replace("{", f'{{tenant_id="{tenant_id}",')
                    else:
                        # Add tenant_id filter to metrics without label selectors
                        target["expr"] = f'{expr}{{tenant_id="{tenant_id}"}}'
    
    async def _cache_dashboard_info(
        self,
        dashboard_result: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> None:
        """Cache dashboard information"""
        try:
            cache_key = f"dashboard:{dashboard_result['id']}"
            dashboard_info = {
                "id": dashboard_result["id"],
                "uid": dashboard_result["uid"],
                "url": dashboard_result["url"],
                "tenant_id": tenant_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.redis_manager.set_json(cache_key, dashboard_info, expire=3600)
            
            # Add to tenant dashboard list
            if tenant_id:
                tenant_cache_key = f"dashboards:tenant:{tenant_id}"
                tenant_dashboards = await self.redis_manager.get_json(tenant_cache_key) or []
                tenant_dashboards.append(dashboard_info)
                await self.redis_manager.set_json(tenant_cache_key, tenant_dashboards, expire=300)
                
        except Exception as e:
            self.logger.error(f"Error caching dashboard info: {e}")
