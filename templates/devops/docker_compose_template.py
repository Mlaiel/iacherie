"""Docker Compose Template for iacherie Platform
Enterprise-grade container orchestration template for development and testing.

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
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    LOCAL = "local"


@dataclass
class DockerComposeConfig:
    """Docker Compose configuration"""
    project_name: str
    environment: EnvironmentType
    network_name: str = "iacherie_network"
    
    # Database settings
    postgres_version: str = "15"
    redis_version: str = "7"
    
    # Service settings
    enable_ai_services: bool = True
    enable_monitoring: bool = True
    enable_media_processing: bool = True
    
    # Development settings
    enable_hot_reload: bool = True
    enable_debug_mode: bool = True
    expose_all_ports: bool = True


class DockerComposeTemplate:
    """Enterprise Docker Compose Template for iacherie Platform"""
    
    def __init__(self, config: DockerComposeConfig):
        self.config = config
        
    def generate_compose_file(self) -> Dict[str, Any]:
        """Generate complete docker-compose.yml"""
        compose = {
            "version": "3.8",
            "name": self.config.project_name,
            "services": self._generate_services(),
            "networks": self._generate_networks(),
            "volumes": self._generate_volumes()
        }
        
        return compose
    
    def _generate_services(self) -> Dict[str, Any]:
        """Generate all services"""
        services = {}
        
        # Core infrastructure services
        services.update(self._generate_infrastructure_services())
        
        # Application services
        services.update(self._generate_application_services())
        
        # Optional services
        if self.config.enable_ai_services:
            services.update(self._generate_ai_services())
            
        if self.config.enable_monitoring:
            services.update(self._generate_monitoring_services())
        
        return services
    
    def _generate_infrastructure_services(self) -> Dict[str, Any]:
        """Generate infrastructure services (DB, Redis, etc.)"""
        return {
            "postgres": {
                "image": f"postgres:{self.config.postgres_version}",
                "container_name": f"{self.config.project_name}_postgres",
                "environment": {
                    "POSTGRES_DB": "iacherie",
                    "POSTGRES_USER": "iacherie",
                    "POSTGRES_PASSWORD": "iacherie_password",
                    "POSTGRES_MULTIPLE_EXTENSIONS": "uuid-ossp,vector"
                },
                "ports": ["5432:5432"] if self.config.expose_all_ports else [],
                "volumes": [
                    "postgres_data:/var/lib/postgresql/data",
                    "./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql:ro"
                ],
                "networks": [self.config.network_name],
                "healthcheck": {
                    "test": ["CMD-SHELL", "pg_isready -U iacherie -d iacherie"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                },
                "restart": "unless-stopped"
            },
            
            "redis": {
                "image": f"redis:{self.config.redis_version}-alpine",
                "container_name": f"{self.config.project_name}_redis",
                "command": "redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru",
                "ports": ["6379:6379"] if self.config.expose_all_ports else [],
                "volumes": ["redis_data:/data"],
                "networks": [self.config.network_name],
                "healthcheck": {
                    "test": ["CMD", "redis-cli", "ping"],
                    "interval": "10s",
                    "timeout": "3s",
                    "retries": 5
                },
                "restart": "unless-stopped"
            },
            
            "nginx": {
                "image": "nginx:alpine",
                "container_name": f"{self.config.project_name}_nginx",
                "ports": ["80:80", "443:443"],
                "volumes": [
                    "./nginx/nginx.conf:/etc/nginx/nginx.conf:ro",
                    "./nginx/ssl:/etc/nginx/ssl:ro",
                    "media_storage:/var/www/media:ro"
                ],
                "networks": [self.config.network_name],
                "depends_on": ["api-gateway"],
                "restart": "unless-stopped"
            }
        }
    
    def _generate_application_services(self) -> Dict[str, Any]:
        """Generate main application services"""
        base_environment = {
            "ENVIRONMENT": self.config.environment.value,
            "DEBUG": str(self.config.enable_debug_mode).lower(),
            "DATABASE_URL": "postgresql://iacherie:iacherie_password@postgres:5432/iacherie",
            "REDIS_URL": "redis://redis:6379/0",
            "JWT_SECRET": "your-jwt-secret-key-change-in-production",
            "CORS_ORIGINS": "*" if self.config.environment == EnvironmentType.DEVELOPMENT else "https://iacherie.com"
        }
        
        services = {
            "api-gateway": {
                "build": {
                    "context": "./api-gateway",
                    "dockerfile": "Dockerfile.dev" if self.config.enable_hot_reload else "Dockerfile"
                },
                "container_name": f"{self.config.project_name}_api_gateway",
                "ports": ["8000:8000"],
                "environment": {
                    **base_environment,
                    "SERVICE_NAME": "api-gateway",
                    "SERVICE_PORT": "8000"
                },
                "volumes": self._get_development_volumes("./api-gateway:/app") if self.config.enable_hot_reload else [],
                "networks": [self.config.network_name],
                "depends_on": {
                    "postgres": {"condition": "service_healthy"},
                    "redis": {"condition": "service_healthy"}
                },
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                },
                "restart": "unless-stopped"
            },
            
            "auth-service": {
                "build": {
                    "context": "./auth-service",
                    "dockerfile": "Dockerfile.dev" if self.config.enable_hot_reload else "Dockerfile"
                },
                "container_name": f"{self.config.project_name}_auth_service",
                "ports": ["8001:8001"] if self.config.expose_all_ports else [],
                "environment": {
                    **base_environment,
                    "SERVICE_NAME": "auth-service",
                    "SERVICE_PORT": "8001",
                    "JWT_EXPIRATION": "86400",
                    "BCRYPT_ROUNDS": "12"
                },
                "volumes": self._get_development_volumes("./auth-service:/app") if self.config.enable_hot_reload else [],
                "networks": [self.config.network_name],
                "depends_on": {
                    "postgres": {"condition": "service_healthy"},
                    "redis": {"condition": "service_healthy"}
                },
                "restart": "unless-stopped"
            },
            
            "content-processor": {
                "build": {
                    "context": "./content-processor",
                    "dockerfile": "Dockerfile.dev" if self.config.enable_hot_reload else "Dockerfile"
                },
                "container_name": f"{self.config.project_name}_content_processor",
                "ports": ["8002:8002"] if self.config.expose_all_ports else [],
                "environment": {
                    **base_environment,
                    "SERVICE_NAME": "content-processor",
                    "SERVICE_PORT": "8002",
                    "MAX_FILE_SIZE": "100MB",
                    "ALLOWED_FORMATS": "mp3,wav,flac,aac,mp4,avi,mov,mkv,jpg,png,gif",
                    "PROCESSING_TIMEOUT": "300"
                },
                "volumes": [
                    "media_storage:/app/media",
                    "temp_storage:/app/temp"
                ] + (self._get_development_volumes("./content-processor:/app") if self.config.enable_hot_reload else []),
                "networks": [self.config.network_name],
                "depends_on": {
                    "postgres": {"condition": "service_healthy"},
                    "redis": {"condition": "service_healthy"}
                },
                "restart": "unless-stopped"
            }
        }
        
        # Add Celery worker for background tasks
        services["celery-worker"] = {
            "build": {
                "context": "./content-processor",
                "dockerfile": "Dockerfile.dev" if self.config.enable_hot_reload else "Dockerfile"
            },
            "container_name": f"{self.config.project_name}_celery_worker",
            "command": "celery -A app.celery worker --loglevel=info --concurrency=4",
            "environment": {
                **base_environment,
                "SERVICE_NAME": "celery-worker",
                "C_FORCE_ROOT": "1"
            },
            "volumes": [
                "media_storage:/app/media",
                "temp_storage:/app/temp"
            ] + (self._get_development_volumes("./content-processor:/app") if self.config.enable_hot_reload else []),
            "networks": [self.config.network_name],
            "depends_on": {
                "postgres": {"condition": "service_healthy"},
                "redis": {"condition": "service_healthy"}
            },
            "restart": "unless-stopped"
        }
        
        # Add Celery Beat for scheduled tasks
        services["celery-beat"] = {
            "build": {
                "context": "./content-processor",
                "dockerfile": "Dockerfile.dev" if self.config.enable_hot_reload else "Dockerfile"
            },
            "container_name": f"{self.config.project_name}_celery_beat",
            "command": "celery -A app.celery beat --loglevel=info",
            "environment": {
                **base_environment,
                "SERVICE_NAME": "celery-beat",
                "C_FORCE_ROOT": "1"
            },
            "volumes": self._get_development_volumes("./content-processor:/app") if self.config.enable_hot_reload else [],
            "networks": [self.config.network_name],
            "depends_on": {
                "postgres": {"condition": "service_healthy"},
                "redis": {"condition": "service_healthy"}
            },
            "restart": "unless-stopped"
        }
        
        return services
    
    def _generate_ai_services(self) -> Dict[str, Any]:
        """Generate AI and ML services"""
        base_environment = {
            "ENVIRONMENT": self.config.environment.value,
            "DATABASE_URL": "postgresql://iacherie:iacherie_password@postgres:5432/iacherie",
            "REDIS_URL": "redis://redis:6379/0",
            "CUDA_VISIBLE_DEVICES": "",  # CPU only for development
            "HF_DATASETS_OFFLINE": "1",
            "TRANSFORMERS_CACHE": "/app/cache/transformers",
            "HF_HOME": "/app/cache/huggingface"
        }
        
        return {
            "ai-services": {
                "build": {
                    "context": "./ai-services",
                    "dockerfile": "Dockerfile.dev" if self.config.enable_hot_reload else "Dockerfile"
                },
                "container_name": f"{self.config.project_name}_ai_services",
                "ports": ["8003:8003"] if self.config.expose_all_ports else [],
                "environment": {
                    **base_environment,
                    "SERVICE_NAME": "ai-services",
                    "SERVICE_PORT": "8003",
                    "MODEL_CACHE_SIZE": "1GB",
                    "MAX_BATCH_SIZE": "32"
                },
                "volumes": [
                    "ai_models:/app/models",
                    "ai_cache:/app/cache"
                ] + (self._get_development_volumes("./ai-services:/app") if self.config.enable_hot_reload else []),
                "networks": [self.config.network_name],
                "depends_on": {
                    "postgres": {"condition": "service_healthy"},
                    "redis": {"condition": "service_healthy"}
                },
                "restart": "unless-stopped",
                "deploy": {
                    "resources": {
                        "limits": {
                            "memory": "4G"
                        },
                        "reservations": {
                            "memory": "2G"
                        }
                    }
                }
            }
        }
    
    def _generate_monitoring_services(self) -> Dict[str, Any]:
        """Generate monitoring and observability services"""
        return {
            "prometheus": {
                "image": "prom/prometheus:latest",
                "container_name": f"{self.config.project_name}_prometheus",
                "ports": ["9090:9090"] if self.config.expose_all_ports else [],
                "volumes": [
                    "./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro",
                    "prometheus_data:/prometheus"
                ],
                "networks": [self.config.network_name],
                "command": [
                    "--config.file=/etc/prometheus/prometheus.yml",
                    "--storage.tsdb.path=/prometheus",
                    "--web.console.libraries=/etc/prometheus/console_libraries",
                    "--web.console.templates=/etc/prometheus/consoles",
                    "--storage.tsdb.retention.time=200h",
                    "--web.enable-lifecycle"
                ],
                "restart": "unless-stopped"
            },
            
            "grafana": {
                "image": "grafana/grafana:latest",
                "container_name": f"{self.config.project_name}_grafana",
                "ports": ["3000:3000"] if self.config.expose_all_ports else [],
                "environment": {
                    "GF_SECURITY_ADMIN_USER": "admin",
                    "GF_SECURITY_ADMIN_PASSWORD": "admin123",
                    "GF_USERS_ALLOW_SIGN_UP": "false"
                },
                "volumes": [
                    "grafana_data:/var/lib/grafana",
                    "./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro",
                    "./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro"
                ],
                "networks": [self.config.network_name],
                "depends_on": ["prometheus"],
                "restart": "unless-stopped"
            },
            
            "jaeger": {
                "image": "jaegertracing/all-in-one:latest",
                "container_name": f"{self.config.project_name}_jaeger",
                "ports": [
                    "16686:16686",  # Jaeger UI
                    "14268:14268"   # Jaeger collector
                ] if self.config.expose_all_ports else [],
                "environment": {
                    "COLLECTOR_OTLP_ENABLED": "true"
                },
                "networks": [self.config.network_name],
                "restart": "unless-stopped"
            }
        }
    
    def _generate_networks(self) -> Dict[str, Any]:
        """Generate network configuration"""
        return {
            self.config.network_name: {
                "driver": "bridge",
                "ipam": {
                    "config": [
                        {"subnet": "172.20.0.0/16"}
                    ]
                }
            }
        }
    
    def _generate_volumes(self) -> Dict[str, Any]:
        """Generate volume configuration"""
        volumes = {
            "postgres_data": {"driver": "local"},
            "redis_data": {"driver": "local"},
            "media_storage": {"driver": "local"},
            "temp_storage": {"driver": "local"}
        }
        
        if self.config.enable_ai_services:
            volumes.update({
                "ai_models": {"driver": "local"},
                "ai_cache": {"driver": "local"}
            })
        
        if self.config.enable_monitoring:
            volumes.update({
                "prometheus_data": {"driver": "local"},
                "grafana_data": {"driver": "local"}
            })
        
        return volumes
    
    def _get_development_volumes(self, mount: str) -> List[str]:
        """Get development volume mounts for hot reload"""
        if self.config.enable_hot_reload:
            return [mount]
        return []
    
    def generate_override_file(self) -> Dict[str, Any]:
        """Generate docker-compose.override.yml for development"""
        if self.config.environment != EnvironmentType.DEVELOPMENT:
            return {}
        
        return {
            "version": "3.8",
            "services": {
                "api-gateway": {
                    "command": "uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
                    "environment": {
                        "PYTHONPATH": "/app",
                        "WATCHFILES_FORCE_POLLING": "true"
                    }
                },
                "auth-service": {
                    "command": "uvicorn main:app --host 0.0.0.0 --port 8001 --reload",
                    "environment": {
                        "PYTHONPATH": "/app",
                        "WATCHFILES_FORCE_POLLING": "true"
                    }
                },
                "content-processor": {
                    "command": "uvicorn main:app --host 0.0.0.0 --port 8002 --reload",
                    "environment": {
                        "PYTHONPATH": "/app",
                        "WATCHFILES_FORCE_POLLING": "true"
                    }
                }
            }
        }
    
    def generate_test_file(self) -> Dict[str, Any]:
        """Generate docker-compose.test.yml for testing"""
        test_compose = self.generate_compose_file()
        
        # Override for testing
        test_compose["services"]["postgres"]["environment"]["POSTGRES_DB"] = "iacherie_test"
        test_compose["services"]["postgres"]["ports"] = []
        
        # Add test runner service
        test_compose["services"]["test-runner"] = {
            "build": {
                "context": ".",
                "dockerfile": "Dockerfile.test"
            },
            "container_name": f"{self.config.project_name}_test_runner",
            "environment": {
                "ENVIRONMENT": "testing",
                "DATABASE_URL": "postgresql://iacherie:iacherie_password@postgres:5432/iacherie_test",
                "REDIS_URL": "redis://redis:6379/1"  # Different Redis DB for tests
            },
            "volumes": [
                ".:/app",
                "test_reports:/app/test-reports"
            ],
            "networks": [self.config.network_name],
            "depends_on": {
                "postgres": {"condition": "service_healthy"},
                "redis": {"condition": "service_healthy"}
            },
            "command": "pytest tests/ --cov=. --cov-report=html --cov-report=xml --junitxml=test-reports/junit.xml"
        }
        
        test_compose["volumes"]["test_reports"] = {"driver": "local"}
        
        return test_compose
    
    def save_compose_files(self, output_dir: str) -> None:
        """Save all Docker Compose files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Main compose file
        with open(output_path / "docker-compose.yml", 'w') as f:
            yaml.dump(self.generate_compose_file(), f, default_flow_style=False, indent=2)
        
        # Override file for development
        if self.config.environment == EnvironmentType.DEVELOPMENT:
            override = self.generate_override_file()
            if override:
                with open(output_path / "docker-compose.override.yml", 'w') as f:
                    yaml.dump(override, f, default_flow_style=False, indent=2)
        
        # Test file
        with open(output_path / "docker-compose.test.yml", 'w') as f:
            yaml.dump(self.generate_test_file(), f, default_flow_style=False, indent=2)
        
        logger.info(f"Docker Compose files saved to {output_dir}")


# Example usage
def create_development_config() -> DockerComposeConfig:
    """Create development configuration"""
    return DockerComposeConfig(
        project_name="iacherie-dev",
        environment=EnvironmentType.DEVELOPMENT,
        enable_ai_services=True,
        enable_monitoring=True,
        enable_media_processing=True,
        enable_hot_reload=True,
        enable_debug_mode=True,
        expose_all_ports=True
    )


def create_testing_config() -> DockerComposeConfig:
    """Create testing configuration"""
    return DockerComposeConfig(
        project_name="iacherie-test",
        environment=EnvironmentType.TESTING,
        enable_ai_services=False,
        enable_monitoring=False,
        enable_media_processing=True,
        enable_hot_reload=False,
        enable_debug_mode=True,
        expose_all_ports=False
    )


if __name__ == "__main__":
    dev_config = create_development_config()
    template = DockerComposeTemplate(dev_config)
    
    print("Docker Compose Template for iacherie Platform")
    print("Configuration:")
    print(f"- Environment: {dev_config.environment.value}")
    print(f"- AI Services: {dev_config.enable_ai_services}")
    print(f"- Monitoring: {dev_config.enable_monitoring}")
    print(f"- Hot Reload: {dev_config.enable_hot_reload}")
    print(f"- Debug Mode: {dev_config.enable_debug_mode}")
