#!/usr/bin/env python3
"""
📊 Grafana Dashboard Template - IA Chéries Creator Economy Platform
================================================================

Advanced Grafana Dashboard Templates for Creator Economy Monitoring
Author: Fahed Mlaiel <mlaiel@live.de>
Expert Roles: DevOps Engineer + Monitoring Specialist + Data Engineer

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de> - TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class DashboardType(Enum):
    """Dashboard types for Creator Economy"""
    CREATOR_OVERVIEW = "creator_overview"
    AI_PROCESSING = "ai_processing"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    CONTENT_ANALYTICS = "content_analytics"
    SECURITY_MONITORING = "security_monitoring"
    INFRASTRUCTURE = "infrastructure"
    BUSINESS_METRICS = "business_metrics"

class PanelType(Enum):
    """Grafana panel types"""
    GRAPH = "graph"
    STAT = "stat"
    TABLE = "table"
    HEATMAP = "heatmap"
    PIE_CHART = "piechart"
    BAR_GAUGE = "bargauge"
    GAUGE = "gauge"
    ALERT_LIST = "alertlist"
    TEXT = "text"
    LOGS = "logs"

@dataclass
class DashboardConfig:
    """Configuration for Grafana dashboard generation"""
    title: str
    dashboard_type: DashboardType
    environment: str
    tags: List[str]
    refresh_rate: str = "30s"
    time_range: str = "1h"
    auto_refresh: bool = True
    creator_specific: bool = True

class GrafanaDashboardTemplate:
    """
    Enterprise Grafana Dashboard Template Generator for Creator Economy Platform
    
    Features:
    - Creator-specific metrics and KPIs
    - AI processing performance monitoring
    - Monetization and revenue tracking
    - Collaboration analytics
    - Content performance metrics
    - Security and compliance monitoring
    - Real-time alerting integration
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.author = "Fahed Mlaiel <mlaiel@live.de>"
        
    def generate_dashboard(self, config: DashboardConfig) -> Dict[str, Any]:
        """Generate complete Grafana dashboard based on configuration"""
        
        base_dashboard = {
            "dashboard": {
                "id": None,
                "title": config.title,
                "tags": config.tags + ["ainflue", "creator-economy"],
                "style": "dark",
                "timezone": "UTC",
                "refresh": config.refresh_rate,
                "schemaVersion": 30,
                "version": 1,
                "time": {
                    "from": f"now-{config.time_range}",
                    "to": "now"
                },
                "timepicker": {
                    "refresh_intervals": ["5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"],
                    "time_options": ["5m", "15m", "1h", "6h", "12h", "24h", "2d", "7d", "30d"]
                },
                "templating": {
                    "list": self._get_template_variables(config)
                },
                "annotations": {
                    "list": self._get_annotations(config)
                },
                "panels": self._get_panels_for_dashboard_type(config),
                "links": self._get_dashboard_links(config)
            },
            "meta": {
                "type": "db",
                "canSave": True,
                "canEdit": True,
                "canAdmin": True,
                "created": datetime.now().isoformat(),
                "createdBy": self.author,
                "updated": datetime.now().isoformat(),
                "updatedBy": self.author,
                "version": 1
            }
        }
        
        return base_dashboard
    
    def _get_template_variables(self, config: DashboardConfig) -> List[Dict[str, Any]]:
        """Generate template variables for dynamic dashboards"""
        variables = [
            {
                "name": "environment",
                "type": "custom",
                "label": "Environment",
                "options": [
                    {"text": "Production", "value": "production", "selected": True},
                    {"text": "Staging", "value": "staging", "selected": False},
                    {"text": "Development", "value": "development", "selected": False}
                ],
                "current": {"text": config.environment.title(), "value": config.environment},
                "hide": 0,
                "includeAll": False,
                "multi": False
            },
            {
                "name": "creator_id",
                "type": "query",
                "label": "Creator",
                "query": "label_values(creator_metrics, creator_id)",
                "datasource": "prometheus",
                "current": {"text": "All", "value": "$__all"},
                "hide": 0,
                "includeAll": True,
                "multi": True,
                "allValue": ".*"
            },
            {
                "name": "content_type",
                "type": "custom",
                "label": "Content Type",
                "options": [
                    {"text": "All", "value": "$__all", "selected": True},
                    {"text": "Video", "value": "video", "selected": False},
                    {"text": "Audio", "value": "audio", "selected": False},
                    {"text": "Image", "value": "image", "selected": False},
                    {"text": "Text", "value": "text", "selected": False},
                    {"text": "3D", "value": "3d", "selected": False},
                    {"text": "VR", "value": "vr", "selected": False}
                ],
                "current": {"text": "All", "value": "$__all"},
                "hide": 0,
                "includeAll": True,
                "multi": True
            }
        ]
        
        if config.creator_specific:
            variables.extend([
                {
                    "name": "platform",
                    "type": "custom",
                    "label": "Platform",
                    "options": [
                        {"text": "All", "value": "$__all", "selected": True},
                        {"text": "YouTube", "value": "youtube", "selected": False},
                        {"text": "TikTok", "value": "tiktok", "selected": False},
                        {"text": "Instagram", "value": "instagram", "selected": False},
                        {"text": "Spotify", "value": "spotify", "selected": False},
                        {"text": "Twitch", "value": "twitch", "selected": False}
                    ],
                    "current": {"text": "All", "value": "$__all"},
                    "hide": 0,
                    "includeAll": True,
                    "multi": True
                }
            ])
        
        return variables
    
    def _get_annotations(self, config: DashboardConfig) -> List[Dict[str, Any]]:
        """Generate annotations for important events"""
        return [
            {
                "name": "Deployments",
                "datasource": "prometheus",
                "enable": True,
                "hide": False,
                "iconColor": "rgba(0, 211, 255, 1)",
                "query": "ALERTS{alertname=\"DeploymentStarted\"}",
                "textFormat": "{{alertname}}: {{summary}}",
                "titleFormat": "Deployment"
            },
            {
                "name": "Creator Events",
                "datasource": "prometheus", 
                "enable": True,
                "hide": False,
                "iconColor": "rgba(255, 96, 96, 1)",
                "query": "ALERTS{alertname=~\"Creator.*\"}",
                "textFormat": "{{alertname}}: {{description}}",
                "titleFormat": "Creator Event"
            }
        ]
    
    def _get_panels_for_dashboard_type(self, config: DashboardConfig) -> List[Dict[str, Any]]:
        """Generate panels based on dashboard type"""
        
        if config.dashboard_type == DashboardType.CREATOR_OVERVIEW:
            return self._get_creator_overview_panels()
        elif config.dashboard_type == DashboardType.AI_PROCESSING:
            return self._get_ai_processing_panels()
        elif config.dashboard_type == DashboardType.MONETIZATION:
            return self._get_monetization_panels()
        elif config.dashboard_type == DashboardType.COLLABORATION:
            return self._get_collaboration_panels()
        elif config.dashboard_type == DashboardType.CONTENT_ANALYTICS:
            return self._get_content_analytics_panels()
        elif config.dashboard_type == DashboardType.SECURITY_MONITORING:
            return self._get_security_monitoring_panels()
        elif config.dashboard_type == DashboardType.INFRASTRUCTURE:
            return self._get_infrastructure_panels()
        elif config.dashboard_type == DashboardType.BUSINESS_METRICS:
            return self._get_business_metrics_panels()
        else:
            return self._get_default_panels()
    
    def _get_creator_overview_panels(self) -> List[Dict[str, Any]]:
        """Generate Creator Overview dashboard panels"""
        return [
            {
                "id": 1,
                "title": "Active Creators",
                "type": "stat",
                "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                "targets": [{
                    "expr": "count(creators_active{environment=\"$environment\"})",
                    "legendFormat": "Active Creators",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "steps": [
                                {"color": "red", "value": 0},
                                {"color": "yellow", "value": 100},
                                {"color": "green", "value": 1000}
                            ]
                        },
                        "unit": "short"
                    }
                }
            },
            {
                "id": 2,
                "title": "New Creator Registrations",
                "type": "graph",
                "gridPos": {"h": 8, "w": 18, "x": 6, "y": 0},
                "targets": [{
                    "expr": "rate(creator_registrations_total{environment=\"$environment\"}[5m])",
                    "legendFormat": "Registrations/sec",
                    "refId": "A"
                }],
                "yAxes": [
                    {"label": "Registrations/sec", "min": 0},
                    {"show": False}
                ]
            },
            {
                "id": 3,
                "title": "Content Upload Activity",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                "targets": [
                    {
                        "expr": "rate(content_uploads_total{environment=\"$environment\", content_type=~\"$content_type\"}[5m])",
                        "legendFormat": "{{content_type}} uploads/sec",
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 4,
                "title": "Creator Engagement Score",
                "type": "gauge",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                "targets": [{
                    "expr": "avg(creator_engagement_score{environment=\"$environment\", creator_id=~\"$creator_id\"})",
                    "legendFormat": "Engagement Score",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "min": 0,
                        "max": 100,
                        "unit": "percent",
                        "thresholds": {
                            "steps": [
                                {"color": "red", "value": 0},
                                {"color": "yellow", "value": 50},
                                {"color": "green", "value": 80}
                            ]
                        }
                    }
                }
            },
            {
                "id": 5,
                "title": "Top Creators by Revenue",
                "type": "table",
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
                "targets": [{
                    "expr": "topk(10, creator_revenue_total{environment=\"$environment\"})",
                    "legendFormat": "{{creator_name}}",
                    "refId": "A",
                    "format": "table"
                }],
                "styles": [
                    {"pattern": "creator_name", "type": "string", "alias": "Creator"},
                    {"pattern": "Value", "type": "number", "alias": "Revenue ($)", "unit": "currencyUSD"}
                ]
            }
        ]
    
    def _get_ai_processing_panels(self) -> List[Dict[str, Any]]:
        """Generate AI Processing monitoring panels"""
        return [
            {
                "id": 1,
                "title": "AI Processing Queue Size",
                "type": "stat",
                "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                "targets": [{
                    "expr": "ai_processing_queue_size{environment=\"$environment\"}",
                    "legendFormat": "Queue Size",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "steps": [
                                {"color": "green", "value": 0},
                                {"color": "yellow", "value": 100},
                                {"color": "red", "value": 1000}
                            ]
                        }
                    }
                }
            },
            {
                "id": 2,
                "title": "AI Model Performance",
                "type": "graph",
                "gridPos": {"h": 8, "w": 18, "x": 6, "y": 0},
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, ai_model_inference_duration_seconds_bucket{environment=\"$environment\"})",
                        "legendFormat": "{{model_name}} - 95th percentile",
                        "refId": "A"
                    },
                    {
                        "expr": "histogram_quantile(0.50, ai_model_inference_duration_seconds_bucket{environment=\"$environment\"})",
                        "legendFormat": "{{model_name}} - 50th percentile",
                        "refId": "B"
                    }
                ],
                "yAxes": [
                    {"label": "Duration (seconds)", "min": 0},
                    {"show": False}
                ]
            },
            {
                "id": 3,
                "title": "AI Processing Success Rate",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                "targets": [{
                    "expr": "rate(ai_processing_success_total{environment=\"$environment\"}[5m]) / rate(ai_processing_total{environment=\"$environment\"}[5m]) * 100",
                    "legendFormat": "{{model_type}} Success Rate",
                    "refId": "A"
                }],
                "yAxes": [
                    {"label": "Success Rate (%)", "min": 0, "max": 100},
                    {"show": False}
                ]
            },
            {
                "id": 4,
                "title": "GPU Utilization",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                "targets": [{
                    "expr": "nvidia_gpu_utilization_gpu{environment=\"$environment\"}",
                    "legendFormat": "GPU {{gpu}} Utilization",
                    "refId": "A"
                }],
                "yAxes": [
                    {"label": "Utilization (%)", "min": 0, "max": 100},
                    {"show": False}
                ]
            }
        ]
    
    def _get_monetization_panels(self) -> List[Dict[str, Any]]:
        """Generate Monetization dashboard panels"""
        return [
            {
                "id": 1,
                "title": "Total Revenue",
                "type": "stat",
                "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                "targets": [{
                    "expr": "sum(revenue_total{environment=\"$environment\"})",
                    "legendFormat": "Total Revenue",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "unit": "currencyUSD",
                        "color": {"mode": "value"},
                        "thresholds": {
                            "steps": [
                                {"color": "green", "value": 0}
                            ]
                        }
                    }
                }
            },
            {
                "id": 2,
                "title": "Revenue by Stream",
                "type": "piechart",
                "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
                "targets": [{
                    "expr": "sum by (revenue_stream) (revenue_total{environment=\"$environment\"})",
                    "legendFormat": "{{revenue_stream}}",
                    "refId": "A"
                }]
            },
            {
                "id": 3,
                "title": "Revenue Growth Rate",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                "targets": [{
                    "expr": "rate(revenue_total{environment=\"$environment\"}[1h])",
                    "legendFormat": "Revenue Growth ($/hour)",
                    "refId": "A"
                }]
            },
            {
                "id": 4,
                "title": "Active Subscriptions",
                "type": "stat",
                "gridPos": {"h": 8, "w": 6, "x": 0, "y": 8},
                "targets": [{
                    "expr": "count(subscriptions_active{environment=\"$environment\"})",
                    "legendFormat": "Active Subscriptions",
                    "refId": "A"
                }]
            },
            {
                "id": 5,
                "title": "Payment Processing Success Rate",
                "type": "gauge",
                "gridPos": {"h": 8, "w": 6, "x": 6, "y": 8},
                "targets": [{
                    "expr": "rate(payment_success_total{environment=\"$environment\"}[5m]) / rate(payment_attempts_total{environment=\"$environment\"}[5m]) * 100",
                    "legendFormat": "Success Rate",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "min": 0,
                        "max": 100,
                        "unit": "percent",
                        "thresholds": {
                            "steps": [
                                {"color": "red", "value": 0},
                                {"color": "yellow", "value": 95},
                                {"color": "green", "value": 99}
                            ]
                        }
                    }
                }
            },
            {
                "id": 6,
                "title": "Creator Earnings Distribution",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                "targets": [{
                    "expr": "histogram_quantile(0.95, creator_earnings_bucket{environment=\"$environment\"})",
                    "legendFormat": "95th percentile",
                    "refId": "A"
                }, {
                    "expr": "histogram_quantile(0.50, creator_earnings_bucket{environment=\"$environment\"})",
                    "legendFormat": "Median",
                    "refId": "B"
                }]
            }
        ]
    
    def _get_dashboard_links(self, config: DashboardConfig) -> List[Dict[str, Any]]:
        """Generate navigation links between dashboards"""
        return [
            {
                "title": "Creator Overview",
                "url": "/d/creator-overview",
                "type": "dashboards",
                "icon": "external link"
            },
            {
                "title": "AI Processing",
                "url": "/d/ai-processing",
                "type": "dashboards",
                "icon": "external link"
            },
            {
                "title": "Monetization",
                "url": "/d/monetization",
                "type": "dashboards",
                "icon": "external link"
            },
            {
                "title": "Infrastructure",
                "url": "/d/infrastructure",
                "type": "dashboards",
                "icon": "external link"
            }
        ]
    
    def generate_complete_dashboard_suite(self, environment: str = "production") -> Dict[str, Any]:
        """Generate complete suite of Creator Economy dashboards"""
        
        dashboards = {}
        
        # Creator Overview Dashboard
        creator_config = DashboardConfig(
            title="IA Chéries Creator Economy - Overview",
            dashboard_type=DashboardType.CREATOR_OVERVIEW,
            environment=environment,
            tags=["creator", "overview", "main"]
        )
        dashboards["creator_overview"] = self.generate_dashboard(creator_config)
        
        # AI Processing Dashboard
        ai_config = DashboardConfig(
            title="IA Chéries AI Processing - Performance",
            dashboard_type=DashboardType.AI_PROCESSING,
            environment=environment,
            tags=["ai", "processing", "performance"]
        )
        dashboards["ai_processing"] = self.generate_dashboard(ai_config)
        
        # Monetization Dashboard
        monetization_config = DashboardConfig(
            title="IA Chéries Monetization - Revenue Analytics",
            dashboard_type=DashboardType.MONETIZATION,
            environment=environment,
            tags=["monetization", "revenue", "analytics"]
        )
        dashboards["monetization"] = self.generate_dashboard(monetization_config)
        
        return dashboards
    
    def export_dashboard_json(self, dashboard: Dict[str, Any], filename: str) -> str:
        """Export dashboard to JSON file"""
        with open(filename, 'w') as f:
            json.dump(dashboard, f, indent=2)
        return filename

# Example usage
def main():
    """Example usage of Grafana Dashboard Template"""
    template = GrafanaDashboardTemplate()
    
    # Generate complete dashboard suite
    dashboards = template.generate_complete_dashboard_suite("production")
    
    print("🚀 Grafana Dashboard Template - Generation Complete!")
    print(f"Generated {len(dashboards)} dashboards:")
    
    for dashboard_name, dashboard_config in dashboards.items():
        filename = f"grafana-{dashboard_name}-dashboard.json"
        template.export_dashboard_json(dashboard_config, filename)
        print(f"  ✅ {dashboard_name}: {filename}")

if __name__ == "__main__":
    main()