"""
AINFLUE DOCKER SERVICES ORCHESTRATOR & REGISTRY
===============================================

Main orchestration engine for Docker services with intelligent service discovery,
health monitoring, and automated scaling capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import json
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import from __init__.py directly
try:
    from . import DOCKER_SERVICES, get_service_config
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append(os.path.dirname(__file__))
    from __init__ import DOCKER_SERVICES, get_service_config

class DockerOrchestrator:
    """Enterprise Docker orchestration engine."""
    
    def __init__(self, base_path: str = "/home/runner/work/Ainflue/Ainflue/docker"):
        self.base_path = Path(base_path)
        self.services_registry = DOCKER_SERVICES
        self.active_services = {}
        self.compose_files = {}
        
    def register_service(self, category: str, service_name: str, config: Dict[str, Any]) -> bool:
        """Register a new service in the orchestrator."""
        try:
            if category not in self.services_registry:
                self.services_registry[category] = []
            
            if service_name not in self.services_registry[category]:
                self.services_registry[category].append(service_name)
                
            self.active_services[service_name] = {
                "category": category,
                "config": config,
                "status": "registered"
            }
            return True
        except Exception as e:
            print(f"❌ Failed to register service {service_name}: {e}")
            return False
    
    def get_service_dockerfile_path(self, service_name: str) -> str:
        """Get the dockerfile path for a service."""
        return f"{service_name}.dockerfile"
    
    def generate_compose_config(self, category: str) -> Dict[str, Any]:
        """Generate docker-compose configuration for a service category."""
        services = self.services_registry.get(category, [])
        config = get_service_config(category)
        
        compose_config = {
            "version": "3.8",
            "services": {},
            "networks": {
                f"ainflue_{category}_network": {
                    "driver": "bridge",
                    "internal": False
                }
            },
            "volumes": {
                f"ainflue_{category}_data": {
                    "driver": "local"
                }
            }
        }
        
        for service in services:
            service_config = {
                "build": {
                    "context": ".",
                    "dockerfile": self.get_service_dockerfile_path(service)
                },
                "container_name": f"ainflue_{service}",
                "restart": "unless-stopped",
                "networks": [f"ainflue_{category}_network"],
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                    "interval": config["health_check"]["interval"],
                    "timeout": config["health_check"]["timeout"],
                    "retries": config["health_check"]["retries"],
                    "start_period": config["health_check"]["start_period"]
                },
                "security_opt": [
                    "no-new-privileges:true"
                ],
                "read_only": True,
                "user": f"{config['security']['user_id']}:{config['security']['group_id']}",
                "deploy": {
                    "resources": {
                        "limits": config["resources"]
                    }
                },
                "environment": [
                    "PYTHONPATH=/app",
                    f"SERVICE_NAME={service}",
                    f"SERVICE_CATEGORY={category}"
                ],
                "volumes": [
                    f"ainflue_{category}_data:/app/data",
                    "/tmp:/tmp:rw"
                ],
                "tmpfs": [
                    "/run:rw,size=100m",
                    "/var/cache:rw,size=100m"
                ]
            }
            
            # Add category-specific configurations
            if category == "ai" or category == "audio_processing":
                service_config["deploy"]["resources"]["reservations"] = {"devices": [{"driver": "nvidia", "count": 1, "capabilities": ["gpu"]}]}
                
            if category == "protection" or category == "monetization":
                service_config["environment"].extend([
                    "ENCRYPTION_ENABLED=true",
                    "AUDIT_LOGGING=true"
                ])
                
            compose_config["services"][service] = service_config
            
        return compose_config
    
    def save_compose_file(self, category: str, config: Dict[str, Any]) -> bool:
        """Save docker-compose configuration to file."""
        try:
            compose_path = self.base_path / f"docker-compose.{category}.yml"
            with open(compose_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            self.compose_files[category] = str(compose_path)
            print(f"✅ Saved compose file: {compose_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to save compose file for {category}: {e}")
            return False
    
    def generate_master_compose(self) -> Dict[str, Any]:
        """Generate master docker-compose file including all services."""
        master_config = {
            "version": "3.8",
            "services": {},
            "networks": {
                "ainflue_main_network": {
                    "driver": "bridge",
                    "external": False
                },
                "ainflue_internal_network": {
                    "driver": "bridge", 
                    "internal": True
                }
            },
            "volumes": {
                "ainflue_shared_data": {"driver": "local"},
                "ainflue_logs": {"driver": "local"},
                "ainflue_config": {"driver": "local"}
            }
        }
        
        # Include key services from each category
        priority_services = {
            "core": ["ai_service", "analytics_service"],
            "audio_processing": ["audio_processing"],
            "protection": ["protection_service"],
            "monetization": ["revenue_tracker"],
            "collaboration": ["collaboration_engine"],
            "seo": ["seo_optimizer"],
            "distribution": ["distribution_hub"],
            "analytics": ["ai_insights_engine"]
        }
        
        for category, services in priority_services.items():
            for service in services:
                config = get_service_config(category)
                service_config = {
                    "build": {
                        "context": ".",
                        "dockerfile": self.get_service_dockerfile_path(service)
                    },
                    "container_name": f"ainflue_{service}",
                    "restart": "unless-stopped",
                    "networks": ["ainflue_main_network"],
                    "depends_on": [],
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    },
                    "environment": [
                        "PYTHONPATH=/app",
                        f"SERVICE_NAME={service}",
                        f"SERVICE_CATEGORY={category}",
                        "LOG_LEVEL=INFO"
                    ],
                    "volumes": [
                        "ainflue_shared_data:/app/data",
                        "ainflue_logs:/app/logs",
                        "ainflue_config:/app/config"
                    ]
                }
                master_config["services"][service] = service_config
        
        return master_config
    
    def create_all_compose_files(self) -> bool:
        """Create all docker-compose files for all categories."""
        success = True
        
        for category in self.services_registry.keys():
            config = self.generate_compose_config(category)
            if not self.save_compose_file(category, config):
                success = False
        
        # Create master compose file
        master_config = self.generate_master_compose()
        if not self.save_compose_file("master", master_config):
            success = False
            
        return success
    
    def list_services(self) -> Dict[str, List[str]]:
        """List all registered services by category."""
        return self.services_registry
    
    def get_service_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific service."""
        return self.active_services.get(service_name)

# Main orchestrator instance
orchestrator = DockerOrchestrator()

def main():
    """Main orchestration function."""
    print("🐳 Ainflue Docker Orchestrator v2.1.0")
    print("=" * 50)
    
    print(f"📊 Total service categories: {len(orchestrator.services_registry)}")
    print(f"📦 Total services: {sum(len(services) for services in orchestrator.services_registry.values())}")
    
    print("\n📋 Service Registry:")
    for category, services in orchestrator.services_registry.items():
        print(f"  🏷️  {category}: {len(services)} services")
        for service in services[:3]:  # Show first 3 services
            print(f"    • {service}")
        if len(services) > 3:
            print(f"    ... and {len(services) - 3} more")
    
    print(f"\n🎯 Creating docker-compose configurations...")
    if orchestrator.create_all_compose_files():
        print("✅ All docker-compose files created successfully!")
    else:
        print("❌ Some docker-compose files failed to create")

if __name__ == "__main__":
    main()