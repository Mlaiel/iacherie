#!/usr/bin/env python3
"""
⛑️ HELM CHART TEMPLATE - KUBERNETES PACKAGE MANAGEMENT
======================================================

Production-ready Helm charts for Kubernetes applications with templating,
values management, and release lifecycle automation.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import yaml
from typing import Dict, Any

class HelmChartTemplate:
    """Enterprise Helm chart template generator"""
    
    def __init__(self, chart_name: str, version: str = "1.0.0"):
        self.chart_name = chart_name
        self.version = version
    
    def generate_chart_yaml(self) -> str:
        """Generate Chart.yaml"""
        chart = {
            "apiVersion": "v2",
            "name": self.chart_name,
            "description": f"Helm chart for {self.chart_name}",
            "type": "application",
            "version": self.version,
            "appVersion": "1.0.0"
        }
        return yaml.dump(chart, default_flow_style=False)
    
    def generate_values_yaml(self) -> str:
        """Generate values.yaml"""
        values = {
            "replicaCount": 2,
            "image": {
                "repository": f"nginx",
                "pullPolicy": "IfNotPresent",
                "tag": "latest"
            },
            "service": {
                "type": "ClusterIP",
                "port": 80
            },
            "ingress": {
                "enabled": False
            },
            "resources": {
                "limits": {
                    "cpu": "500m",
                    "memory": "512Mi"
                },
                "requests": {
                    "cpu": "250m", 
                    "memory": "256Mi"
                }
            }
        }
        return yaml.dump(values, default_flow_style=False)