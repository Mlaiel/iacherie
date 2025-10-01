"""Ansible Playbook Template for IA Chéries Platform
Enterprise-grade configuration management template for creator economy platform.

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE
© 2025 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés - Utilisation commerciale interdite sans autorisation écrite explicite

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2024-09-18
"""

import logging
import yaml
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class DeploymentTarget(Enum):
    """Deployment target types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ServiceType(Enum):
    """Service types for IA Chéries platform"""
    API_GATEWAY = "api_gateway"
    AUTH_SERVICE = "auth_service"
    CONTENT_PROCESSOR = "content_processor"
    AI_SERVICES = "ai_services"
    DATABASE = "database"
    CACHE = "cache"
    MONITORING = "monitoring"
    LOAD_BALANCER = "load_balancer"


@dataclass
class AnsibleConfig:
    """Ansible configuration structure"""
    project_name: str
    environment: DeploymentTarget
    hosts_group: str
    python_version: str = "3.11"
    docker_version: str = "24.0"
    node_version: str = "18"
    
    # IA Chéries specific services
    enable_ai_processing: bool = True
    enable_media_services: bool = True
    enable_analytics: bool = True
    enable_monitoring: bool = True


class AnsiblePlaybookTemplate:
    """Enterprise Ansible Playbook Template for IA Chéries Platform"""
    
    def __init__(self, config: AnsibleConfig):
        self.config = config
        self.playbooks = {}
        
    def generate_main_playbook(self) -> Dict[str, Any]:
        """Generate main deployment playbook"""
        return {
            "name": f"Deploy IA Chéries Platform - {self.config.environment.value.title()}",
            "hosts": self.config.hosts_group,
            "become": True,
            "gather_facts": True,
            "vars": self._generate_variables(),
            "pre_tasks": self._generate_pre_tasks(),
            "roles": self._generate_roles(),
            "post_tasks": self._generate_post_tasks(),
            "handlers": self._generate_handlers()
        }
    
    def _generate_variables(self) -> Dict[str, Any]:
        """Generate playbook variables"""
        return {
            "project_name": self.config.project_name,
            "environment": self.config.environment.value,
            "python_version": self.config.python_version,
            "docker_version": self.config.docker_version,
            "node_version": self.config.node_version,
            
            # IA Chéries platform specific
            "ainflue_user": "ainflue",
            "ainflue_group": "ainflue",
            "ainflue_home": "/opt/ainflue",
            "ainflue_logs": "/var/log/ainflue",
            "ainflue_data": "/var/lib/ainflue",
            
            # Service configurations
            "services": {
                "api_gateway": {
                    "port": 8000,
                    "workers": 4,
                    "memory_limit": "2g"
                },
                "auth_service": {
                    "port": 8001,
                    "workers": 2,
                    "memory_limit": "1g"
                },
                "content_processor": {
                    "port": 8002,
                    "workers": 4,
                    "memory_limit": "4g"
                },
                "ai_services": {
                    "port": 8003,
                    "workers": 2,
                    "memory_limit": "8g",
                    "gpu_enabled": True
                }
            },
            
            # Database configurations
            "database": {
                "postgresql": {
                    "version": "15",
                    "port": 5432,
                    "max_connections": 200
                },
                "redis": {
                    "version": "7",
                    "port": 6379,
                    "memory_limit": "2g"
                }
            },
            
            # Security configurations
            "security": {
                "ssl_enabled": True,
                "firewall_enabled": True,
                "fail2ban_enabled": True,
                "automatic_updates": True
            }
        }
    
    def _generate_pre_tasks(self) -> List[Dict[str, Any]]:
        """Generate pre-deployment tasks"""
        return [
            {
                "name": "Update system packages",
                "package": {
                    "name": "*",
                    "state": "latest"
                },
                "when": "ansible_os_family == 'Debian'"
            },
            {
                "name": "Install required system packages",
                "package": {
                    "name": [
                        "curl",
                        "wget",
                        "git",
                        "htop",
                        "unzip",
                        "software-properties-common",
                        "apt-transport-https",
                        "ca-certificates",
                        "gnupg",
                        "lsb-release"
                    ],
                    "state": "present"
                }
            },
            {
                "name": "Create ainflue system user",
                "user": {
                    "name": "{{ ainflue_user }}",
                    "group": "{{ ainflue_group }}",
                    "home": "{{ ainflue_home }}",
                    "shell": "/bin/bash",
                    "system": True
                }
            },
            {
                "name": "Create ainflue directories",
                "file": {
                    "path": "{{ item }}",
                    "state": "directory",
                    "owner": "{{ ainflue_user }}",
                    "group": "{{ ainflue_group }}",
                    "mode": "0755"
                },
                "loop": [
                    "{{ ainflue_home }}",
                    "{{ ainflue_logs }}",
                    "{{ ainflue_data }}",
                    "{{ ainflue_home }}/config",
                    "{{ ainflue_home }}/scripts",
                    "{{ ainflue_home }}/backups"
                ]
            }
        ]
    
    def _generate_roles(self) -> List[str]:
        """Generate roles to include"""
        base_roles = [
            "common",
            "security",
            "docker",
            "python",
            "nginx"
        ]
        
        if self.config.enable_ai_processing:
            base_roles.extend(["cuda", "pytorch"])
            
        if self.config.enable_media_services:
            base_roles.append("ffmpeg")
            
        if self.config.enable_monitoring:
            base_roles.extend(["prometheus", "grafana"])
            
        base_roles.extend([
            "postgresql",
            "redis",
            "ainflue_platform"
        ])
        
        return base_roles
    
    def _generate_post_tasks(self) -> List[Dict[str, Any]]:
        """Generate post-deployment tasks"""
        return [
            {
                "name": "Start and enable ainflue services",
                "systemd": {
                    "name": "{{ item }}",
                    "state": "started",
                    "enabled": True
                },
                "loop": [
                    "ainflue-api-gateway",
                    "ainflue-auth-service",
                    "ainflue-content-processor"
                ]
            },
            {
                "name": "Wait for services to be ready",
                "uri": {
                    "url": "http://localhost:{{ services.api_gateway.port }}/health",
                    "method": "GET",
                    "status_code": 200
                },
                "retries": 30,
                "delay": 10
            },
            {
                "name": "Run database migrations",
                "command": "{{ ainflue_home }}/scripts/migrate.sh",
                "become_user": "{{ ainflue_user }}",
                "when": "environment != 'production' or database_migration_approved | default(false)"
            },
            {
                "name": "Create initial admin user",
                "command": "{{ ainflue_home }}/scripts/create_admin.sh",
                "become_user": "{{ ainflue_user }}",
                "when": "environment == 'development'"
            }
        ]
    
    def _generate_handlers(self) -> List[Dict[str, Any]]:
        """Generate event handlers"""
        return [
            {
                "name": "restart nginx",
                "systemd": {
                    "name": "nginx",
                    "state": "restarted"
                }
            },
            {
                "name": "restart postgresql",
                "systemd": {
                    "name": "postgresql",
                    "state": "restarted"
                }
            },
            {
                "name": "restart redis",
                "systemd": {
                    "name": "redis",
                    "state": "restarted"
                }
            },
            {
                "name": "restart ainflue services",
                "systemd": {
                    "name": "{{ item }}",
                    "state": "restarted"
                },
                "loop": [
                    "ainflue-api-gateway",
                    "ainflue-auth-service",
                    "ainflue-content-processor"
                ]
            }
        ]
    
    def generate_inventory(self) -> Dict[str, Any]:
        """Generate Ansible inventory"""
        return {
            "all": {
                "children": {
                    self.config.environment.value: {
                        "children": {
                            "web_servers": {
                                "hosts": {
                                    f"web-{i+1}": {
                                        "ansible_host": f"10.0.{i+1}.10",
                                        "ansible_user": "ubuntu",
                                        "ansible_ssh_private_key_file": "~/.ssh/ainflue-key.pem"
                                    }
                                    for i in range(2)
                                }
                            },
                            "app_servers": {
                                "hosts": {
                                    f"app-{i+1}": {
                                        "ansible_host": f"10.0.{i+10}.10",
                                        "ansible_user": "ubuntu",
                                        "ansible_ssh_private_key_file": "~/.ssh/ainflue-key.pem"
                                    }
                                    for i in range(3)
                                }
                            },
                            "db_servers": {
                                "hosts": {
                                    "db-1": {
                                        "ansible_host": "10.0.100.10",
                                        "ansible_user": "ubuntu",
                                        "ansible_ssh_private_key_file": "~/.ssh/ainflue-key.pem",
                                        "postgresql_role": "primary"
                                    },
                                    "db-2": {
                                        "ansible_host": "10.0.200.10",
                                        "ansible_user": "ubuntu",
                                        "ansible_ssh_private_key_file": "~/.ssh/ainflue-key.pem",
                                        "postgresql_role": "replica"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def generate_group_vars(self) -> Dict[str, Any]:
        """Generate group variables"""
        return {
            "all": {
                "project_name": self.config.project_name,
                "environment": self.config.environment.value,
                "timezone": "UTC",
                "locale": "en_US.UTF-8"
            },
            f"{self.config.environment.value}": {
                "domain_name": f"{self.config.project_name}-{self.config.environment.value}.com",
                "ssl_certificate_email": "admin@ainflue.com",
                "backup_retention_days": 30 if self.config.environment == DeploymentTarget.PRODUCTION else 7,
                "log_level": "INFO" if self.config.environment == DeploymentTarget.PRODUCTION else "DEBUG"
            }
        }
    
    def generate_creator_economy_tasks(self) -> List[Dict[str, Any]]:
        """Generate IA Chéries creator economy specific tasks"""
        return [
            {
                "name": "Install AI/ML dependencies",
                "pip": {
                    "name": [
                        "torch",
                        "transformers",
                        "librosa",
                        "soundfile",
                        "opencv-python",
                        "pillow",
                        "numpy",
                        "scikit-learn"
                    ],
                    "virtualenv": "{{ ainflue_home }}/venv"
                },
                "when": "{{ enable_ai_processing }}"
            },
            {
                "name": "Configure FFmpeg for media processing",
                "package": {
                    "name": [
                        "ffmpeg",
                        "libavcodec-extra",
                        "libavformat-dev",
                        "libavutil-dev",
                        "libswscale-dev",
                        "libswresample-dev"
                    ],
                    "state": "present"
                },
                "when": "{{ enable_media_services }}"
            },
            {
                "name": "Setup creator content directories",
                "file": {
                    "path": "{{ item }}",
                    "state": "directory",
                    "owner": "{{ ainflue_user }}",
                    "group": "{{ ainflue_group }}",
                    "mode": "0755"
                },
                "loop": [
                    "{{ ainflue_data }}/uploads",
                    "{{ ainflue_data }}/processed",
                    "{{ ainflue_data }}/thumbnails",
                    "{{ ainflue_data }}/temp",
                    "{{ ainflue_data }}/analytics"
                ]
            },
            {
                "name": "Configure content processing workers",
                "template": {
                    "src": "celery-worker.service.j2",
                    "dest": "/etc/systemd/system/ainflue-content-worker@.service",
                    "owner": "root",
                    "group": "root",
                    "mode": "0644"
                },
                "notify": "reload systemd"
            },
            {
                "name": "Start content processing workers",
                "systemd": {
                    "name": f"ainflue-content-worker@{i+1}",
                    "state": "started",
                    "enabled": True
                },
                "loop": "{{ range(1, services.content_processor.workers + 1) | list }}"
            }
        ]
    
    def generate_security_hardening_tasks(self) -> List[Dict[str, Any]]:
        """Generate security hardening tasks"""
        return [
            {
                "name": "Configure UFW firewall",
                "ufw": {
                    "rule": "allow",
                    "port": "{{ item }}",
                    "proto": "tcp"
                },
                "loop": [
                    "22",  # SSH
                    "80",  # HTTP
                    "443",  # HTTPS
                    "{{ services.api_gateway.port }}"
                ]
            },
            {
                "name": "Enable UFW",
                "ufw": {
                    "state": "enabled",
                    "policy": "deny"
                }
            },
            {
                "name": "Install and configure fail2ban",
                "package": {
                    "name": "fail2ban",
                    "state": "present"
                }
            },
            {
                "name": "Configure fail2ban for SSH",
                "copy": {
                    "content": |
                        [sshd]
                        enabled = true
                        port = ssh
                        filter = sshd
                        logpath = /var/log/auth.log
                        maxretry = 3
                        bantime = 3600
                    ,
                    "dest": "/etc/fail2ban/jail.local",
                    "owner": "root",
                    "group": "root",
                    "mode": "0644"
                },
                "notify": "restart fail2ban"
            },
            {
                "name": "Configure automatic security updates",
                "package": {
                    "name": "unattended-upgrades",
                    "state": "present"
                }
            },
            {
                "name": "Enable automatic security updates",
                "lineinfile": {
                    "path": "/etc/apt/apt.conf.d/20auto-upgrades",
                    "regexp": "^APT::Periodic::Unattended-Upgrade",
                    "line": 'APT::Periodic::Unattended-Upgrade "1";',
                    "create": True
                }
            }
        ]
    
    def save_playbook(self, output_dir: str) -> None:
        """Save all playbook components to directory"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Main playbook
        main_playbook = [self.generate_main_playbook()]
        with open(output_path / "deploy.yml", 'w') as f:
            yaml.dump(main_playbook, f, default_flow_style=False, indent=2)
        
        # Inventory
        with open(output_path / "inventory.yml", 'w') as f:
            yaml.dump(self.generate_inventory(), f, default_flow_style=False, indent=2)
        
        # Group vars
        group_vars_dir = output_path / "group_vars"
        group_vars_dir.mkdir(exist_ok=True)
        
        group_vars = self.generate_group_vars()
        for group, vars_data in group_vars.items():
            with open(group_vars_dir / f"{group}.yml", 'w') as f:
                yaml.dump(vars_data, f, default_flow_style=False, indent=2)
        
        logger.info(f"Ansible playbook saved to {output_dir}")


# Example usage and configuration templates
def create_production_config() -> AnsibleConfig:
    """Create production environment configuration"""
    return AnsibleConfig(
        project_name="ainflue-platform",
        environment=DeploymentTarget.PRODUCTION,
        hosts_group="production",
        python_version="3.11",
        docker_version="24.0",
        enable_ai_processing=True,
        enable_media_services=True,
        enable_analytics=True,
        enable_monitoring=True
    )


def create_development_config() -> AnsibleConfig:
    """Create development environment configuration"""
    return AnsibleConfig(
        project_name="ainflue-dev",
        environment=DeploymentTarget.DEVELOPMENT,
        hosts_group="development",
        python_version="3.11",
        docker_version="24.0",
        enable_ai_processing=False,  # Disabled for dev to save resources
        enable_media_services=True,
        enable_analytics=False,
        enable_monitoring=False
    )


if __name__ == "__main__":
    # Generate production playbook
    prod_config = create_production_config()
    prod_template = AnsiblePlaybookTemplate(prod_config)
    
    print("Ansible Playbook Template for IA Chéries Platform")
    print("Configuration:")
    print(f"- Environment: {prod_config.environment.value}")
    print(f"- Python Version: {prod_config.python_version}")
    print(f"- AI Processing: {prod_config.enable_ai_processing}")
    print(f"- Media Services: {prod_config.enable_media_services}")
    print(f"- Monitoring: {prod_config.enable_monitoring}")
