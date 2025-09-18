#!/usr/bin/env python3
"""
🔧 ANSIBLE PLAYBOOK TEMPLATE - CONFIGURATION MANAGEMENT
=======================================================

Enterprise Ansible playbooks for automated server configuration,
application deployment, and infrastructure management.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import yaml

class AnsiblePlaybookTemplate:
    """Enterprise Ansible playbook template"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def generate_playbook(self) -> str:
        """Generate Ansible playbook"""
        playbook = [{
            "name": f"Deploy {self.service_name}",
            "hosts": "production",
            "become": True,
            "vars": {
                "service_name": self.service_name,
                "app_port": 8080
            },
            "tasks": [
                {
                    "name": "Update package cache",
                    "apt": {
                        "update_cache": True
                    }
                },
                {
                    "name": "Install Docker",
                    "apt": {
                        "name": "docker.io",
                        "state": "present"
                    }
                },
                {
                    "name": f"Deploy {self.service_name} container",
                    "docker_container": {
                        "name": self.service_name,
                        "image": f"{self.service_name}:latest",
                        "ports": ["{{ app_port }}:{{ app_port }}"],
                        "restart_policy": "unless-stopped"
                    }
                }
            ]
        }]
        return yaml.dump(playbook, default_flow_style=False)