#!/usr/bin/env python3
"""
🐳 DOCKER COMPOSE TEMPLATE - ENTERPRISE CONTAINER ORCHESTRATION
===============================================================

Production-ready Docker Compose templates for multi-service applications
with networking, volumes, secrets, and health monitoring.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import yaml
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DockerComposeConfig:
    """Docker Compose configuration"""
    service_name: str
    image: str
    port: int = 8080
    environment: Dict[str, str] = None
    volumes: List[str] = None
    networks: List[str] = None
    depends_on: List[str] = None

class DockerComposeTemplate:
    """
    🚀 ENTERPRISE DOCKER COMPOSE TEMPLATE
    
    Multi-service containerized applications with production configurations.
    """
    
    def __init__(self):
        """Initialize Docker Compose template"""
        self.services = {}
        self.networks = {}
        self.volumes = {}
    
    def add_service(self, config: DockerComposeConfig):
        """Add service to compose configuration"""
        service_config = {
            "image": config.image,
            "ports": [f"{config.port}:{config.port}"],
            "restart": "unless-stopped",
            "healthcheck": {
                "test": f"curl -f http://localhost:{config.port}/health || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "40s"
            }
        }
        
        if config.environment:
            service_config["environment"] = config.environment
        
        if config.volumes:
            service_config["volumes"] = config.volumes
        
        if config.networks:
            service_config["networks"] = config.networks
        
        if config.depends_on:
            service_config["depends_on"] = config.depends_on
        
        self.services[config.service_name] = service_config
    
    def generate_compose_file(self) -> str:
        """Generate Docker Compose YAML file"""
        compose_config = {
            "version": "3.8",
            "services": self.services
        }
        
        if self.networks:
            compose_config["networks"] = self.networks
        
        if self.volumes:
            compose_config["volumes"] = self.volumes
        
        return yaml.dump(compose_config, default_flow_style=False)

# Factory function
def create_docker_compose(**kwargs) -> DockerComposeTemplate:
    """Create Docker Compose template"""
    return DockerComposeTemplate(**kwargs)