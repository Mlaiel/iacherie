"""🔧 Kubernetes Environment Configuration - IA-Influencer-Agent
==================================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: DevOps + Backend Senior + ML Engineer + Cloud Architect
Date: 2025-08-15

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Configuration environnement Kubernetes avec auto-scaling et HA.
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


class KubernetesConfigManager(BaseEnvironmentConfigManager):
    """
    Configuration manager pour l'environnement Kubernetes.
    Optimisé pour orchestration cloud-native avec high availability.
    """
    
    def __init__(self):
        super().__init__(
            environment=EnvironmentType.PRODUCTION,  # K8s = production ready
            debug=False,
            host="0.0.0.0",
            port=8000,  # Port standard dans pod
            workers=int(os.getenv("K8S_WORKERS", "4")),
            cors_origins=self._get_kubernetes_cors_origins()
        )
        
    def _get_kubernetes_cors_origins(self) -> List[str]:
        """Définit les origins CORS pour Kubernetes"""
        origins_env = os.getenv("K8S_CORS_ORIGINS", "")
        if origins_env:
            return [origin.strip() for origin in origins_env.split(",")]
        return [
            "https://ia-influencer.com",
            "https://www.ia-influencer.com",
            "https://app.ia-influencer.com"
        ]
        
    def load_environment_specific_config(self) -> None:
        """Charge la configuration spécifique Kubernetes"""
        
        # Configuration Base de Données Kubernetes (service externe)
        self.database_config = DatabaseConfig(
            host=os.getenv("DATABASE_SERVICE_HOST", "postgres-service"),
            port=int(os.getenv("DATABASE_SERVICE_PORT", "5432")),
            name=os.getenv("POSTGRES_DB", "ia_influencer"),
            username=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "30")),
            ssl_mode="require"
        )
        
        # Configuration Redis Kubernetes (service externe)
        self.redis_config = RedisConfig(
            host=os.getenv("REDIS_SERVICE_HOST", "redis-service"),
            port=int(os.getenv("REDIS_SERVICE_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            db=0,
            max_connections=int(os.getenv("REDIS_MAX_CONN", "100")),
            socket_timeout=5
        )
        
        # Configuration Sécurité Kubernetes (secrets)
        self.security_config = SecurityConfig(
            jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
            jwt_algorithm="HS256",
            jwt_expiry_hours=int(os.getenv("JWT_EXPIRY_HOURS", "12")),
            oauth2_secret_key=os.getenv("OAUTH2_SECRET_KEY"),
            encryption_key=os.getenv("ENCRYPTION_KEY"),
            api_rate_limit=int(os.getenv("API_RATE_LIMIT", "100")),
            session_timeout=int(os.getenv("SESSION_TIMEOUT", "1800"))
        )
        
        # Configuration IA Kubernetes
        self.ai_config = AIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            huggingface_token=os.getenv("HUGGINGFACE_TOKEN"),
            tensorflow_gpu_enabled=bool(os.getenv("GPU_ENABLED", False)),
            model_cache_dir="/app/models",  # Volume persistant
            vector_db_path="/app/vectordb",  # Volume persistant
            fingerprint_similarity_threshold=0.90
        )
        
        # Configuration Stockage Kubernetes (persistent volumes)
        self.storage_config = StorageConfig(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("AWS_REGION", "eu-central-1"),
            s3_bucket_name=os.getenv("S3_BUCKET_NAME"),
            local_storage_path="/app/storage",
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "500"))
        )
        
        # Configuration Monitoring Kubernetes
        self.monitoring_config = MonitoringConfig(
            prometheus_enabled=True,
            grafana_enabled=True,
            jaeger_enabled=True,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            metrics_port=9090,
            traces_endpoint=os.getenv("JAEGER_COLLECTOR_URL", "http://jaeger-collector:14268")
        )
        
        # Configuration Intégrations Kubernetes
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
        """Valide la configuration Kubernetes"""
        try:
            # Vérifications critiques K8s
            assert self.database_config is not None, "Configuration base de données requise"
            assert self.redis_config is not None, "Configuration Redis requise"
            assert self.security_config is not None, "Configuration sécurité requise"
            
            # Vérifications secrets K8s
            assert self.security_config.jwt_secret_key, "JWT secret manquant (K8s Secret)"
            assert self.database_config.password, "DB password manquant (K8s Secret)"
            
            # Vérifications services K8s
            assert "service" in self.database_config.host, "DB host doit être un service K8s"
            assert "service" in self.redis_config.host, "Redis host doit être un service K8s"
            
            return True
            
        except (AssertionError, AttributeError) as e:
            print(f"❌ Erreur validation configuration Kubernetes: {e}")
            return False
            
    def get_kubernetes_features(self) -> Dict[str, Any]:
        """Fonctionnalités spécifiques Kubernetes"""
        return {
            "cloud_native": True,
            "auto_scaling": True,
            "high_availability": True,
            "rolling_updates": True,
            "health_checks": True,
            "service_discovery": True,
            "load_balancing": True,
            "persistent_storage": True,
            "secrets_management": True,
            "config_maps": True,
            "resource_limits": True,
            "network_policies": True
        }
        
    def get_deployment_config(self) -> Dict[str, Any]:
        """Configuration Kubernetes Deployment"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "ia-influencer-api",
                "labels": {
                    "app": "ia-influencer-api",
                    "version": self.app_version,
                    "tier": "backend"
                }
            },
            "spec": {
                "replicas": int(os.getenv("K8S_REPLICAS", "3")),
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxSurge": 1,
                        "maxUnavailable": 0
                    }
                },
                "selector": {
                    "matchLabels": {"app": "ia-influencer-api"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "ia-influencer-api"}
                    },
                    "spec": {
                        "containers": [{
                            "name": "ia-influencer-api",
                            "image": f"ia-influencer/api:{self.app_version}",
                            "ports": [{"containerPort": 8000}],
                            "env": self._get_kubernetes_env_vars(),
                            "resources": self.get_resource_limits(),
                            "livenessProbe": self.get_liveness_probe(),
                            "readinessProbe": self.get_readiness_probe(),
                            "volumeMounts": self.get_volume_mounts()
                        }],
                        "volumes": self.get_volumes(),
                        "imagePullSecrets": [{"name": "docker-registry-secret"}]
                    }
                }
            }
        }
        
    def get_service_config(self) -> Dict[str, Any]:
        """Configuration Kubernetes Service"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "ia-influencer-api-service",
                "labels": {"app": "ia-influencer-api"}
            },
            "spec": {
                "type": "ClusterIP",
                "ports": [{
                    "port": 80,
                    "targetPort": 8000,
                    "protocol": "TCP"
                }],
                "selector": {"app": "ia-influencer-api"}
            }
        }
        
    def get_ingress_config(self) -> Dict[str, Any]:
        """Configuration Kubernetes Ingress"""
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "ia-influencer-ingress",
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rate-limit": "100"
                }
            },
            "spec": {
                "tls": [{
                    "hosts": ["api.ia-influencer.com"],
                    "secretName": "ia-influencer-tls"
                }],
                "rules": [{
                    "host": "api.ia-influencer.com",
                    "http": {
                        "paths": [{
                            "path": "/",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "ia-influencer-api-service",
                                    "port": {"number": 80}
                                }
                            }
                        }]
                    }
                }]
            }
        }
        
    def get_hpa_config(self) -> Dict[str, Any]:
        """Configuration Horizontal Pod Autoscaler"""
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {"name": "ia-influencer-hpa"},
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "ia-influencer-api"
                },
                "minReplicas": int(os.getenv("K8S_MIN_REPLICAS", "2")),
                "maxReplicas": int(os.getenv("K8S_MAX_REPLICAS", "10")),
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 80
                            }
                        }
                    }
                ]
            }
        }
        
    def get_resource_limits(self) -> Dict[str, Any]:
        """Limites de ressources Kubernetes"""
        return {
            "requests": {
                "memory": os.getenv("K8S_MEMORY_REQUEST", "512Mi"),
                "cpu": os.getenv("K8S_CPU_REQUEST", "500m")
            },
            "limits": {
                "memory": os.getenv("K8S_MEMORY_LIMIT", "2Gi"),
                "cpu": os.getenv("K8S_CPU_LIMIT", "2")
            }
        }
        
    def get_liveness_probe(self) -> Dict[str, Any]:
        """Configuration liveness probe"""
        return {
            "httpGet": {
                "path": "/health",
                "port": 8000
            },
            "initialDelaySeconds": 30,
            "periodSeconds": 10,
            "timeoutSeconds": 5,
            "failureThreshold": 3
        }
        
    def get_readiness_probe(self) -> Dict[str, Any]:
        """Configuration readiness probe"""
        return {
            "httpGet": {
                "path": "/ready",
                "port": 8000
            },
            "initialDelaySeconds": 10,
            "periodSeconds": 5,
            "timeoutSeconds": 3,
            "failureThreshold": 3
        }
        
    def get_volume_mounts(self) -> List[Dict[str, Any]]:
        """Configuration volume mounts"""
        return [
            {
                "name": "model-cache",
                "mountPath": "/app/models"
            },
            {
                "name": "vector-db",
                "mountPath": "/app/vectordb"
            },
            {
                "name": "storage-data",
                "mountPath": "/app/storage"
            }
        ]
        
    def get_volumes(self) -> List[Dict[str, Any]]:
        """Configuration volumes"""
        return [
            {
                "name": "model-cache",
                "persistentVolumeClaim": {
                    "claimName": "model-cache-pvc"
                }
            },
            {
                "name": "vector-db",
                "persistentVolumeClaim": {
                    "claimName": "vector-db-pvc"
                }
            },
            {
                "name": "storage-data",
                "persistentVolumeClaim": {
                    "claimName": "storage-data-pvc"
                }
            }
        ]
        
    def _get_kubernetes_env_vars(self) -> List[Dict[str, Any]]:
        """Variables d'environnement Kubernetes avec secrets"""
        return [
            {"name": "ENVIRONMENT", "value": self.environment.value},
            {"name": "LOG_LEVEL", "value": self.monitoring_config.log_level},
            {"name": "WORKERS", "value": str(self.workers)},
            {
                "name": "DATABASE_URL",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": "ia-influencer-secrets",
                        "key": "database-url"
                    }
                }
            },
            {
                "name": "JWT_SECRET_KEY",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": "ia-influencer-secrets",
                        "key": "jwt-secret"
                    }
                }
            },
            {
                "name": "OPENAI_API_KEY",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": "ia-influencer-secrets",
                        "key": "openai-key"
                    }
                }
            }
        ]
        
    def generate_kubernetes_manifests(self) -> Dict[str, str]:
        """Génère tous les manifestes Kubernetes"""
        import yaml
        
        manifests = {
            "deployment.yaml": yaml.dump(self.get_deployment_config(), default_flow_style=False),
            "service.yaml": yaml.dump(self.get_service_config(), default_flow_style=False),
            "ingress.yaml": yaml.dump(self.get_ingress_config(), default_flow_style=False),
            "hpa.yaml": yaml.dump(self.get_hpa_config(), default_flow_style=False)
        }
        
        return manifests
        
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporte la configuration Kubernetes complète"""
        base_config = super().export_to_dict()
        base_config.update({
            "kubernetes_features": self.get_kubernetes_features(),
            "deployment_config": self.get_deployment_config(),
            "service_config": self.get_service_config(),
            "ingress_config": self.get_ingress_config(),
            "hpa_config": self.get_hpa_config(),
            "resource_limits": self.get_resource_limits(),
            "cloud_native": True
        })
        return base_config


def create_kubernetes_config() -> KubernetesConfigManager:
    """Crée et initialise la configuration Kubernetes"""
    config = KubernetesConfigManager()
    config.initialize_configuration()
    return config
