"""Grafana Configuration Module for IA-Influencer Agent Platform
=============================================================

Professional Grafana dashboard and visualization configuration for
comprehensive monitoring of content creators platform with AI processing.

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
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class DashboardType(Enum):
    """
Grafana dashboard types"""

    SYSTEM_OVERVIEW = "system_overview"
    AI_SERVICES = "ai_services"
    CONTENT_PROTECTION = "content_protection"
    BUSINESS_METRICS = "business_metrics"
    SECURITY = "security"
    AUDIO_PROCESSING = "audio_processing"
    MONETIZATION = "monetization"


class VisualizationType(Enum):
    """Grafana visualization types"""

    GRAPH = "graph"
    STAT = "stat"
    GAUGE = "gauge"
    BAR_GAUGE = "bargauge"
    TABLE = "table"
    HEATMAP = "heatmap"
    PIE_CHART = "piechart"
    WORLDMAP = "grafana-worldmap-panel"


@dataclass
class GrafanaPanel:
    """Grafana panel configuration"""
    title: str
    type: VisualizationType
    targets: List[Dict[str, Any]]
    grid_pos: Dict[str, int] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    field_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GrafanaDashboard:
    """
Grafana dashboard configuration"""
    title: str
    tags: List[str]
    panels: List[GrafanaPanel]
    uid: Optional[str] = None
    refresh: str = "30s"
    time_from: str = "now-1h"
    time_to: str = "now"


class GrafanaConfig:
    """Professional Grafana configuration for IA-Influencer platform"""
    
    def __init__(self):
        self.grafana_url = os.getenv("GRAFANA_URL", "http://grafana:3000")
        self.grafana_admin_user = os.getenv("GRAFANA_ADMIN_USER", "admin")
        self.grafana_admin_password = os.getenv("GRAFANA_ADMIN_PASSWORD", "admin")
        self.prometheus_url = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
        self.organization_name = os.getenv("GRAFANA_ORG_NAME", "IA-Influencer")
    
    def get_datasource_config(self) -> Dict[str, Any]:
        """Get Prometheus datasource configuration"""
        return {
            "name": "Prometheus",
            "type": "prometheus",
            "access": "proxy",
            "url": self.prometheus_url,
            "isDefault": True,
            "basicAuth": False,
            "jsonData": {
                "timeInterval": "15s",
                "queryTimeout": "60s",
                "httpMethod": "POST"
            }
        }
    
    def get_system_overview_dashboard(self) -> GrafanaDashboard:
        """Create system overview dashboard"""
        panels = [
            GrafanaPanel(
                title="System Health Overview",
                type=VisualizationType.STAT,
                targets=[{
                    "expr": "up",
                    "legendFormat": "{{job}} - {{instance}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 0},
                options={
                    "reduceOptions": {
                        "values": False,
                        "calcs": ["lastNotNull"],
                        "fields": ""
                    },
                    "orientation": "auto",
                    "textMode": "auto",
                    "colorMode": "value",
                    "graphMode": "area"
                }
            ),
            GrafanaPanel(
                title="Request Rate",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "rate(http_requests_total[5m])",
                    "legendFormat": "{{service}} - {{method}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 0}
            ),
            GrafanaPanel(
                title="Response Time P95",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                    "legendFormat": "{{service}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 8}
            ),
            GrafanaPanel(
                title="Error Rate",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])",
                    "legendFormat": "{{service}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 8}
            )
        ]
        
        return GrafanaDashboard(
            title="System Overview",
            tags=["system", "overview"],
            panels=panels,
            uid="system-overview"
        )
    
    def get_ai_services_dashboard(self) -> GrafanaDashboard:
        """Create AI services monitoring dashboard"""
        panels = [
            GrafanaPanel(
                title="AI Model Inference Latency",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "histogram_quantile(0.95, rate(ai_inference_duration_seconds_bucket[5m]))",
                    "legendFormat": "{{model_type}} - {{content_type}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 0}
            ),
            GrafanaPanel(
                title="AI Processing Queue Size",
                type=VisualizationType.GAUGE,
                targets=[{
                    "expr": "ai_processing_queue_size",
                    "legendFormat": "{{queue_type}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 0}
            ),
            GrafanaPanel(
                title="Model Accuracy Metrics",
                type=VisualizationType.STAT,
                targets=[{
                    "expr": "ai_model_accuracy",
                    "legendFormat": "{{model_name}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 8}
            ),
            GrafanaPanel(
                title="GPU/CPU Utilization",
                type=VisualizationType.GRAPH,
                targets=[
                    {
                        "expr": "ai_gpu_utilization_percent",
                        "legendFormat": "GPU {{device_id}}",
                        "refId": "A"
                    },
                    {
                        "expr": "ai_cpu_utilization_percent",
                        "legendFormat": "CPU",
                        "refId": "B"
                    }
                ],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 8}
            )
        ]
        
        return GrafanaDashboard(
            title="AI Services",
            tags=["ai", "machine-learning", "inference"],
            panels=panels,
            uid="ai-services"
        )
    
    def get_content_protection_dashboard(self) -> GrafanaDashboard:
        """Create content protection monitoring dashboard"""
        panels = [
            GrafanaPanel(
                title="Content Protection Matches",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "rate(protection_matches_total[5m])",
                    "legendFormat": "{{content_type}} - {{platform}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 0}
            ),
            GrafanaPanel(
                title="Fingerprint Database Size",
                type=VisualizationType.GAUGE,
                targets=[{
                    "expr": "fingerprint_database_size",
                    "legendFormat": "{{content_type}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 0}
            ),
            GrafanaPanel(
                title="Crawler Success Rate",
                type=VisualizationType.STAT,
                targets=[{
                    "expr": "crawler_success_rate",
                    "legendFormat": "{{platform}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 8}
            ),
            GrafanaPanel(
                title="Takedown Requests",
                type=VisualizationType.BAR_GAUGE,
                targets=[{
                    "expr": "rate(takedown_requests_total[1h])",
                    "legendFormat": "{{platform}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 8}
            )
        ]
        
        return GrafanaDashboard(
            title="Content Protection",
            tags=["protection", "fingerprinting", "crawling"],
            panels=panels,
            uid="content-protection"
        )
    
    def get_business_metrics_dashboard(self) -> GrafanaDashboard:
        """Create business metrics dashboard"""
        panels = [
            GrafanaPanel(
                title="Content Uploads by Type",
                type=VisualizationType.PIE_CHART,
                targets=[{
                    "expr": "increase(content_uploads_total[1h])",
                    "legendFormat": "{{content_type}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 0}
            ),
            GrafanaPanel(
                title="Revenue Generated",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "increase(revenue_generated_total[1h])",
                    "legendFormat": "{{platform}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 0}
            ),
            GrafanaPanel(
                title="Active Users",
                type=VisualizationType.STAT,
                targets=[{
                    "expr": "active_users_count",
                    "legendFormat": "Active Users",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 6, "x": 0, "y": 8}
            ),
            GrafanaPanel(
                title="Platform Distribution",
                type=VisualizationType.BAR_GAUGE,
                targets=[{
                    "expr": "platform_usage_count",
                    "legendFormat": "{{platform}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 6, "x": 6, "y": 8}
            ),
            GrafanaPanel(
                title="Collaboration Matches",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "rate(collaboration_matches_total[1h])",
                    "legendFormat": "{{match_type}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 8}
            )
        ]
        
        return GrafanaDashboard(
            title="Business Metrics",
            tags=["business", "revenue", "users"],
            panels=panels,
            uid="business-metrics"
        )
    
    def get_audio_processing_dashboard(self) -> GrafanaDashboard:
        """Create audio processing monitoring dashboard"""
        panels = [
            GrafanaPanel(
                title="Audio Processing Latency",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "histogram_quantile(0.95, rate(audio_processing_duration_seconds_bucket[5m]))",
                    "legendFormat": "{{processing_type}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 0}
            ),
            GrafanaPanel(
                title="Audio Fingerprint Generation Rate",
                type=VisualizationType.STAT,
                targets=[{
                    "expr": "rate(audio_fingerprints_generated_total[5m])",
                    "legendFormat": "Fingerprints/sec",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 0}
            ),
            GrafanaPanel(
                title="Spectral Analysis Queue",
                type=VisualizationType.GAUGE,
                targets=[{
                    "expr": "spectral_analysis_queue_size",
                    "legendFormat": "Queue Size",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 8}
            ),
            GrafanaPanel(
                title="Audio Format Distribution",
                type=VisualizationType.PIE_CHART,
                targets=[{
                    "expr": "audio_format_count",
                    "legendFormat": "{{format}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 8}
            )
        ]
        
        return GrafanaDashboard(
            title="Audio Processing",
            tags=["audio", "processing", "fingerprinting"],
            panels=panels,
            uid="audio-processing"
        )
    
    def get_security_dashboard(self) -> GrafanaDashboard:
        """Create security monitoring dashboard"""
        panels = [
            GrafanaPanel(
                title="Authentication Attempts",
                type=VisualizationType.GRAPH,
                targets=[
                    {
                        "expr": "rate(auth_attempts_total{status=\"success\"}[5m])",
                        "legendFormat": "Successful",
                        "refId": "A"
                    },
                    {
                        "expr": "rate(auth_attempts_total{status=\"failure\"}[5m])",
                        "legendFormat": "Failed",
                        "refId": "B"
                    }
                ],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 0}
            ),
            GrafanaPanel(
                title="Security Incidents",
                type=VisualizationType.STAT,
                targets=[{
                    "expr": "security_incidents_total",
                    "legendFormat": "{{severity}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 0}
            ),
            GrafanaPanel(
                title="Suspicious Activity Heatmap",
                type=VisualizationType.HEATMAP,
                targets=[{
                    "expr": "suspicious_activity_score",
                    "legendFormat": "{{source_ip}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 8}
            ),
            GrafanaPanel(
                title="API Rate Limiting",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "rate(api_rate_limit_exceeded_total[5m])",
                    "legendFormat": "{{endpoint}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 8}
            )
        ]
        
        return GrafanaDashboard(
            title="Security Monitoring",
            tags=["security", "authentication", "threats"],
            panels=panels,
            uid="security-monitoring"
        )
    
    def get_monetization_dashboard(self) -> GrafanaDashboard:
        """Create monetization tracking dashboard"""
        panels = [
            GrafanaPanel(
                title="Revenue by Platform",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "increase(platform_revenue_total[1h])",
                    "legendFormat": "{{platform}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 0}
            ),
            GrafanaPanel(
                title="Payment Processing Status",
                type=VisualizationType.STAT,
                targets=[{
                    "expr": "payment_processing_status",
                    "legendFormat": "{{status}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 0}
            ),
            GrafanaPanel(
                title="License Agreements",
                type=VisualizationType.BAR_GAUGE,
                targets=[{
                    "expr": "license_agreements_active",
                    "legendFormat": "{{license_type}}",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 0, "y": 8}
            ),
            GrafanaPanel(
                title="Revenue Trends",
                type=VisualizationType.GRAPH,
                targets=[{
                    "expr": "rate(total_revenue[24h])",
                    "legendFormat": "Daily Revenue",
                    "refId": "A"
                }],
                grid_pos={"h": 8, "w": 12, "x": 12, "y": 8}
            )
        ]
        
        return GrafanaDashboard(
            title="Monetization Tracking",
            tags=["monetization", "revenue", "payments"],
            panels=panels,
            uid="monetization-tracking"
        )
    
    def get_all_dashboards(self) -> List[GrafanaDashboard]:
        """Get all configured dashboards"""
        return [
            self.get_system_overview_dashboard(),
            self.get_ai_services_dashboard(),
            self.get_content_protection_dashboard(),
            self.get_business_metrics_dashboard(),
            self.get_audio_processing_dashboard(),
            self.get_security_dashboard(),
            self.get_monetization_dashboard()
        ]
    
    def export_dashboard_json(self, dashboard: GrafanaDashboard) -> str:
        """
Export dashboard configuration as JSON"""
        dashboard_json = {
            "dashboard": {
                "id": None,
                "uid": dashboard.uid,
                "title": dashboard.title,
                "tags": dashboard.tags,
                "timezone": "browser",
                "refresh": dashboard.refresh,
                "schemaVersion": 30,
                "version": 1,
                "panels": [
                    {
                        "id": idx + 1,
                        "title": panel.title,
                        "type": panel.type.value,
                        "targets": panel.targets,
                        "gridPos": panel.grid_pos,
                        "options": panel.options,
                        "fieldConfig": panel.field_config
                    }
                    for idx, panel in enumerate(dashboard.panels)
                ],
                "time": {
                    "from": dashboard.time_from,
                    "to": dashboard.time_to
                }
            },
            "overwrite": True
        }
        
        return json.dumps(dashboard_json, indent=2)
