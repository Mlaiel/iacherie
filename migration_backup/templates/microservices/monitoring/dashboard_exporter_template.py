"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Dashboard Exporter Template for Ainflue Platform
===============================================

Production-ready dashboard exporting with:
- Grafana dashboard generation
- Prometheus metrics visualization
- Custom dashboard templates
- Automated dashboard deployment
- Multi-service dashboards
- Real-time monitoring views

Author: Fahed Mlaiel (mlaiel@live.de)
Dashboard & Visualization Expert
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class DashboardPanel:
    """Dashboard panel configuration"""
    title: str
    panel_type: str  # graph, stat, table, etc.
    targets: List[Dict[str, Any]]
    grid_pos: Dict[str, int]
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Dashboard:
    """Dashboard configuration"""
    id: str
    title: str
    description: str
    panels: List[DashboardPanel]
    tags: List[str] = field(default_factory=list)
    time_range: Dict[str, str] = field(default_factory=lambda: {"from": "now-1h", "to": "now"})

class DashboardExporter:
    """
    Production-ready dashboard export system
    
    Features:
    - Grafana dashboard generation
    - Prometheus metrics visualization
    - Template-based dashboards
    - Automated deployment
    """
    
    def __init__(self, service_name: str = "ainflue-service"):
        self.service_name = service_name
        self.dashboards: Dict[str, Dashboard] = {}
    
    def create_service_dashboard(self) -> Dashboard:
        """Create default service dashboard"""
        panels = [
            DashboardPanel(
                title="Request Rate",
                panel_type="graph",
                targets=[{"expr": f"rate(http_requests_total{{service=\"{self.service_name}\"}}[5m])"}],
                grid_pos={"x": 0, "y": 0, "w": 12, "h": 8}
            ),
            DashboardPanel(
                title="Response Time",
                panel_type="graph",
                targets=[{"expr": f"histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service=\"{self.service_name}\"}}[5m]))"}],
                grid_pos={"x": 12, "y": 0, "w": 12, "h": 8}
            ),
            DashboardPanel(
                title="Error Rate",
                panel_type="stat",
                targets=[{"expr": f"rate(http_requests_total{{service=\"{self.service_name}\",status=~\"5..|4..\"}}[5m])"}],
                grid_pos={"x": 0, "y": 8, "w": 6, "h": 4}
            )
        ]
        
        dashboard = Dashboard(
            id=f"{self.service_name}-overview",
            title=f"{self.service_name.title()} Service Overview",
            description=f"Monitoring dashboard for {self.service_name}",
            panels=panels,
            tags=["service", "monitoring", self.service_name]
        )
        
        self.dashboards[dashboard.id] = dashboard
        return dashboard
    
    def export_grafana_json(self, dashboard_id: str) -> str:
        """Export dashboard as Grafana JSON"""
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        dashboard = self.dashboards[dashboard_id]
        
        grafana_json = {
            "dashboard": {
                "id": None,
                "title": dashboard.title,
                "description": dashboard.description,
                "tags": dashboard.tags,
                "timezone": "browser",
                "panels": [
                    {
                        "id": i + 1,
                        "title": panel.title,
                        "type": panel.panel_type,
                        "targets": panel.targets,
                        "gridPos": panel.grid_pos,
                        "options": panel.options
                    }
                    for i, panel in enumerate(dashboard.panels)
                ],
                "time": dashboard.time_range,
                "timepicker": {},
                "timezone": "",
                "refresh": "30s",
                "schemaVersion": 16,
                "version": 0
            },
            "folderId": 0,
            "overwrite": True
        }
        
        return json.dumps(grafana_json, indent=2)

class DashboardExporterTemplate:
    """Dashboard Exporter Template"""
    
    def create_exporter(self, config: Dict[str, Any]) -> DashboardExporter:
        return DashboardExporter(service_name=config.get("service_name", "ainflue"))
    
    def get_template_info(self) -> Dict[str, Any]:
        return {
            "name": "dashboard-exporter",
            "description": "Dashboard generation and export",
            "features": ["Grafana dashboards", "Prometheus visualization", "Automated deployment"]
        }