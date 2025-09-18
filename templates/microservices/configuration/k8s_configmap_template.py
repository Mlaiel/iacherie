#!/usr/bin/env python3
"""K8s ConfigMap Template - Kubernetes ConfigMap management"""

import yaml

class K8sConfigMapTemplate:
    """Kubernetes ConfigMap management template"""
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
    
    def create_configmap(self, name: str, data: dict) -> str:
        """Create Kubernetes ConfigMap YAML"""
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name,
                "namespace": self.namespace
            },
            "data": data
        }
        return yaml.dump(configmap)