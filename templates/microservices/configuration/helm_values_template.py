#!/usr/bin/env python3
"""Helm Values Template - Helm chart values management"""

import yaml

class HelmValuesTemplate:
    """Helm values template management"""
    
    def __init__(self, chart_name: str):
        self.chart_name = chart_name
    
    def generate_values(self, config: dict) -> str:
        """Generate Helm values.yaml"""
        return yaml.dump(config, default_flow_style=False)