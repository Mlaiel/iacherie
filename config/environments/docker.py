"""🔧 Docker Environment Configuration - IA-Influencer-Agent
==================================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: DevOps + Backend Senior + ML Engineer + Infrastructure
Date: 2025-08-15

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Configuration environnement Docker avec orchestration microservices.
==================================================================
"""
import os
from typing import Dict, Any, List, Optional
from .base import (
    BaseEnvironmentConfigManager, 
    DatabaseConfig, 
    RedisConfig,
    SecurityConfig,
    AIConfig,
    StorageConfig,
    MonitoringConfig,
    IntegrationConfig,
    EnvironmentType
)


class DockerConfigManager(BaseEnvironmentConfigManager):
    """
    Configuration manager pour l'environnement Docker.
    Optimisé pour conteneurs et orchestration microservices.
    """
    
    def __init__(self):
        super().__init__(
            environment=EnvironmentType.DEVELOPMENT,  # Base development
            debug=bool(os.getenv("DOCKER_DEBUG", False)),
            host="0.0.0.0",  # Bind all interfaces in container
            port=int(os.getenv("CONTAINER_PORT", "8000")),
            workers=int(os.getenv("CONTAINER_WORKERS", "4")),
            cors_origins=self._get_docker_cors_origins()
        )
        
    def _get_docker_cors_origins(self) -> List[str]:
        """Définit les origins CORS pour Docker"""
        origins_env = os.getenv("DOCKER_CORS_ORIGINS", "")
        if origins_env:
            return [origin.strip() for origin in origins_env.split(",")]
        return [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://frontend:3000",  # Service Docker
            "http://web:8080"
        ]
        
    def load_environment_specific_config(self) -> None:
        """Charge la configuration spécifique Docker"""
        
        # Configuration Base de Données Docker (service externe)
        self.database_config = DatabaseConfig(
            host=os.getenv("DATABASE_HOST", "postgres"),  # Service Docker
            port=int(os.getenv("DATABASE_PORT", "5432")),
            name=os.getenv("DATABASE_NAME", "ia_influencer"),
            username=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "postgres"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            ssl_mode=os.getenv("DB_SSL_MODE", "prefer")
        )
        
        # Configuration Redis Docker (service externe)
        self.redis_config = RedisConfig(
            host=os.getenv("REDIS_HOST", "redis"),  # Service Docker
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB", "0")),
            max_connections=int(os.getenv("REDIS_MAX_CONN", "50")),
            socket_timeout=int(os.getenv("REDIS_TIMEOUT", "30"))
        )
        
        # Configuration Sécurité Docker
        self.security_config = SecurityConfig(
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "docker-jwt-secret-2025"),
            jwt_algorithm="HS256",
            jwt_expiry_hours=int(os.getenv("JWT_EXPIRY_HOURS", "24")),
            oauth2_secret_key=os.getenv("OAUTH2_SECRET_KEY", "docker-oauth2-secret"),
            encryption_key=os.getenv("ENCRYPTION_KEY", "docker-encryption-key-32-chars"),
            api_rate_limit=int(os.getenv("API_RATE_LIMIT", "1000")),
            session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600"))
        )
        
        # Configuration IA Docker
        self.ai_config = AIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            huggingface_token=os.getenv("HUGGINGFACE_TOKEN"),
            tensorflow_gpu_enabled=bool(os.getenv("GPU_ENABLED", False)),
            model_cache_dir=os.getenv("MODEL_CACHE_DIR", "/app/models"),
            vector_db_path=os.getenv("VECTOR_DB_PATH", "/app/vectordb"),
            fingerprint_similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
        )
        
        # Configuration Stockage Docker (volumes persistants)
        self.storage_config = StorageConfig(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("AWS_REGION", "eu-central-1"),
            s3_bucket_name=os.getenv("S3_BUCKET_NAME"),
            local_storage_path=os.getenv("STORAGE_PATH", "/app/storage"),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "100"))
        )
        
        # Configuration Monitoring Docker
        self.monitoring_config = MonitoringConfig(
            prometheus_enabled=bool(os.getenv("PROMETHEUS_ENABLED", True)),
            grafana_enabled=bool(os.getenv("GRAFANA_ENABLED", True)),
            jaeger_enabled=bool(os.getenv("JAEGER_ENABLED", True)),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            metrics_port=int(os.getenv("METRICS_PORT", "9090")),
            traces_endpoint=os.getenv("JAEGER_ENDPOINT", "http://jaeger:14268")
        )
        
        # Configuration Intégrations Docker
        self.integration_config = IntegrationConfig(
            spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            youtube_api_key=os.getenv("YOUTUBE_API_KEY"),
            instagram_access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            tiktok_app_id=os.getenv("TIKTOK_APP_ID"),
            twitter_bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            stripe_api_key=os.getenv("STRIPE_API_KEY"),
            wise_api_key=os.getenv("WISE_API_KEY")
        )
        
    def validate_configuration(self) -> bool:
        """Valide la configuration Docker"""
        try:
            # Vérifications Docker spécifiques
            assert self.database_config is not None, "Configuration base de données requise"
            assert self.redis_config is not None, "Configuration Redis requise"
            
            # Vérifications services Docker
            assert self.database_config.host, "Host base de données requis"
            assert self.redis_config.host, "Host Redis requis"
            
            # Vérifications ports et réseau
            assert 1024 <= self.port <= 65535, "Port invalide pour conteneur"
            assert self.host == "0.0.0.0", "Host doit être 0.0.0.0 en Docker"
            
            return True
            
        except (AssertionError, AttributeError) as e:
            print(f"❌ Erreur validation configuration Docker: {e}")
            return False
            
    def get_docker_features(self) -> Dict[str, Any]:
        """Fonctionnalités spécifiques Docker"""
        return {
            "containerized": True,
            "microservices_ready": True,
            "service_discovery": True,
            "health_checks": True,
            "graceful_shutdown": True,
            "volume_persistence": True,
            "network_isolation": True,
            "scaling_enabled": True,
            "load_balancing": True,
            "auto_restart": True
        }
        
    def get_docker_services(self) -> Dict[str, Dict[str, Any]]:
        """Configuration des services Docker"""
        return {
            "postgres": {
                "image": "postgres:15-alpine",
                "environment": {
                    "POSTGRES_DB": self.database_config.name,
                    "POSTGRES_USER": self.database_config.username,
                    "POSTGRES_PASSWORD": self.database_config.password
                },
                "volumes": ["postgres_data:/var/lib/postgresql/data"],
                "ports": [f"{self.database_config.port}:5432"],
                "restart": "unless-stopped"
            },
            "redis": {
                "image": "redis:7-alpine",
                "command": f"redis-server --requirepass {self.redis_config.password or ''}",
                "volumes": ["redis_data:/data"],
                "ports": [f"{self.redis_config.port}:6379"],
                "restart": "unless-stopped"
            },
            "prometheus": {
                "image": "prom/prometheus:latest",
                "ports": [f"{self.monitoring_config.metrics_port}:9090"],
                "volumes": ["prometheus_config:/etc/prometheus"],
                "restart": "unless-stopped"
            } if self.monitoring_config.prometheus_enabled else None,
            "grafana": {
                "image": "grafana/grafana:latest",
                "ports": ["3000:3000"],
                "volumes": ["grafana_data:/var/lib/grafana"],
                "restart": "unless-stopped"
            } if self.monitoring_config.grafana_enabled else None,
            "jaeger": {
                "image": "jaegertracing/all-in-one:latest",
                "ports": ["16686:16686", "14268:14268"],
                "restart": "unless-stopped"
            } if self.monitoring_config.jaeger_enabled else None
        }
        
    def get_docker_networks(self) -> Dict[str, Dict[str, Any]]:
        """Configuration des réseaux Docker"""
        return {
            "ia-influencer-network": {
                "driver": "bridge",
                "ipam": {
                    "config": [{"subnet": "172.20.0.0/16"}]
                }
            }
        }
        
    def get_docker_volumes(self) -> List[str]:
        """Volumes Docker persistants"""
        return [
            "postgres_data",
            "redis_data",
            "model_cache",
            "vector_db",
            "storage_data",
            "prometheus_config",
            "grafana_data",
            "logs"
        ]
        
    def get_health_check_config(self) -> Dict[str, Any]:
        """Configuration health check Docker"""
        return {
            "test": ["CMD", "curl", "-f", f"http://localhost:{self.port}/health"],
            "interval": "30s",
            "timeout": "10s",
            "retries": 3,
            "start_period": "40s"
        }
        
    def generate_docker_compose(self) -> str:
        """Génère le fichier docker-compose.yml"""
        services = self.get_docker_services()
        networks = self.get_docker_networks()
        volumes = self.get_docker_volumes()
        
        compose_config = {
            "version": "3.8",
            "services": {k: v for k, v in services.items() if v is not None},
            "networks": networks,
            "volumes": {vol: {} for vol in volumes}
        }
        
        # Ajout du service principal
        compose_config["services"]["ia-influencer-api"] = {
            "build": {
                "context": ".",
                "dockerfile": "Dockerfile"
            },
            "ports": [f"{self.port}:8000"],
            "environment": self._get_environment_variables(),
            "volumes": [
                "model_cache:/app/models",
                "vector_db:/app/vectordb",
                "storage_data:/app/storage",
                "logs:/app/logs"
            ],
            "depends_on": ["postgres", "redis"],
            "networks": ["ia-influencer-network"],
            "healthcheck": self.get_health_check_config(),
            "restart": "unless-stopped"
        }
        
        import yaml
        return yaml.dump(compose_config, default_flow_style=False)
        
    def _get_environment_variables(self) -> Dict[str, str]:
        """Variables d'environnement pour conteneur"""
        return {
            "ENVIRONMENT": self.environment.value,
            "DATABASE_URL": self.get_database_url(),
            "REDIS_URL": self.get_redis_url(),
            "JWT_SECRET_KEY": self.security_config.jwt_secret_key,
            "LOG_LEVEL": self.monitoring_config.log_level,
            "WORKERS": str(self.workers),
            "PORT": str(self.port)
        }
        
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporte la configuration Docker complète"""
        base_config = super().export_to_dict()
        base_config.update({
            "docker_features": self.get_docker_features(),
            "docker_services": self.get_docker_services(),
            "docker_networks": self.get_docker_networks(),
            "docker_volumes": self.get_docker_volumes(),
            "health_check": self.get_health_check_config(),
            "containerized": True
        })
        return base_config


def create_docker_config() -> DockerConfigManager:
    """Crée et initialise la configuration Docker"""
    config = DockerConfigManager()
    config.initialize_configuration()
    return config
