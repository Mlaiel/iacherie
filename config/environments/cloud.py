"""🔧 Cloud Environment Configuration - IA-Influencer-Agent
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

Configuration environnement cloud multi-provider (AWS, GCP, Azure).
==================================================================
"""

import os
from typing import Dict, Any, List, Optional, Union
from enum import Enum
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


class CloudProvider(str, Enum):
    """
Providers cloud supportés"""

    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI_CLOUD = "multi_cloud"


class CloudConfigManager(BaseEnvironmentConfigManager):
    """
    Configuration manager pour environnements cloud.
    Support multi-cloud avec provider-specific optimizations.
    """
    
    def __init__(self, provider: CloudProvider = CloudProvider.AWS):
        self.cloud_provider = provider
        super().__init__(
            environment=EnvironmentType.PRODUCTION,
            debug=False,
            host="0.0.0.0",
            port=8000,
            workers=int(os.getenv("CLOUD_WORKERS", "6")),
            cors_origins=self._get_cloud_cors_origins()
        )
        
    def _get_cloud_cors_origins(self) -> List[str]:
        """Définit les origins CORS pour cloud"""
        origins_env = os.getenv("CLOUD_CORS_ORIGINS", "")
        if origins_env:
            return [origin.strip() for origin in origins_env.split(",")]
        return [
            "https://ia-influencer.com",
            "https://www.ia-influencer.com",
            "https://app.ia-influencer.com",
            "https://api.ia-influencer.com"
        ]
        
    def load_environment_specific_config(self) -> None:
        """Charge la configuration spécifique au cloud"""
        
        # Configuration selon le provider cloud
        if self.cloud_provider == CloudProvider.AWS:
            self._configure_aws()
        elif self.cloud_provider == CloudProvider.AZURE:
            self._configure_azure()
        elif self.cloud_provider == CloudProvider.GCP:
            self._configure_gcp()
        elif self.cloud_provider == CloudProvider.MULTI_CLOUD:
            self._configure_multi_cloud()
            
    def _configure_aws(self) -> None:
        """
Configuration AWS spécifique"""
        
        # RDS PostgreSQL
        self.database_config = DatabaseConfig(
            host=os.getenv("AWS_RDS_ENDPOINT"),
            port=int(os.getenv("AWS_RDS_PORT", "5432")),
            name=os.getenv("AWS_RDS_DATABASE", "ia_influencer"),
            username=os.getenv("AWS_RDS_USERNAME"),
            password=os.getenv("AWS_RDS_PASSWORD"),
            pool_size=int(os.getenv("AWS_DB_POOL_SIZE", "25")),
            max_overflow=int(os.getenv("AWS_DB_MAX_OVERFLOW", "35")),
            ssl_mode="require"
        )
        
        # ElastiCache Redis
        self.redis_config = RedisConfig(
            host=os.getenv("AWS_ELASTICACHE_ENDPOINT"),
            port=int(os.getenv("AWS_ELASTICACHE_PORT", "6379")),
            password=os.getenv("AWS_ELASTICACHE_AUTH_TOKEN"),
            db=0,
            max_connections=150,
            socket_timeout=5
        )
        
        # AWS Secrets Manager
        self.security_config = SecurityConfig(
            jwt_secret_key=self._get_aws_secret("jwt-secret-key"),
            oauth2_secret_key=self._get_aws_secret("oauth2-secret-key"),
            encryption_key=self._get_aws_secret("encryption-key"),
            api_rate_limit=100,
            session_timeout=1800
        )
        
        # AWS AI Services
        self.ai_config = AIConfig(
            openai_api_key=self._get_aws_secret("openai-api-key"),
            huggingface_token=self._get_aws_secret("huggingface-token"),
            tensorflow_gpu_enabled=True,  # GPU instances
            model_cache_dir="/app/models",
            vector_db_path="/app/vectordb",
            fingerprint_similarity_threshold=0.90
        )
        
        # S3 Storage
        self.storage_config = StorageConfig(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("AWS_REGION", "eu-central-1"),
            s3_bucket_name=os.getenv("AWS_S3_BUCKET"),
            local_storage_path="/tmp/cache",
            max_file_size_mb=500
        )
        
        # CloudWatch Monitoring
        self.monitoring_config = MonitoringConfig(
            prometheus_enabled=True,
            grafana_enabled=True,
            jaeger_enabled=True,
            log_level="INFO",
            metrics_port=9090,
            traces_endpoint=os.getenv("AWS_X_RAY_ENDPOINT")
        )
        
    def _configure_azure(self) -> None:
        """Configuration Azure spécifique"""
        
        # Azure Database for PostgreSQL
        self.database_config = DatabaseConfig(
            host=os.getenv("AZURE_DB_HOST"),
            port=int(os.getenv("AZURE_DB_PORT", "5432")),
            name=os.getenv("AZURE_DB_NAME", "ia_influencer"),
            username=os.getenv("AZURE_DB_USERNAME"),
            password=os.getenv("AZURE_DB_PASSWORD"),
            pool_size=20,
            max_overflow=30,
            ssl_mode="require"
        )
        
        # Azure Cache for Redis
        self.redis_config = RedisConfig(
            host=os.getenv("AZURE_REDIS_HOST"),
            port=int(os.getenv("AZURE_REDIS_PORT", "6380")),  # SSL port
            password=os.getenv("AZURE_REDIS_KEY"),
            db=0,
            max_connections=100,
            socket_timeout=5
        )
        
        # Azure Key Vault
        self.security_config = SecurityConfig(
            jwt_secret_key=self._get_azure_secret("jwt-secret-key"),
            oauth2_secret_key=self._get_azure_secret("oauth2-secret-key"),
            encryption_key=self._get_azure_secret("encryption-key"),
            api_rate_limit=100,
            session_timeout=1800
        )
        
    def _configure_gcp(self) -> None:
        """Configuration Google Cloud spécifique"""
        
        # Cloud SQL PostgreSQL
        self.database_config = DatabaseConfig(
            host=os.getenv("GCP_SQL_HOST"),
            port=int(os.getenv("GCP_SQL_PORT", "5432")),
            name=os.getenv("GCP_SQL_DATABASE", "ia_influencer"),
            username=os.getenv("GCP_SQL_USERNAME"),
            password=os.getenv("GCP_SQL_PASSWORD"),
            pool_size=20,
            max_overflow=30,
            ssl_mode="require"
        )
        
        # Memorystore Redis
        self.redis_config = RedisConfig(
            host=os.getenv("GCP_REDIS_HOST"),
            port=int(os.getenv("GCP_REDIS_PORT", "6379")),
            password=os.getenv("GCP_REDIS_AUTH"),
            db=0,
            max_connections=100,
            socket_timeout=5
        )
        
        # Secret Manager
        self.security_config = SecurityConfig(
            jwt_secret_key=self._get_gcp_secret("jwt-secret-key"),
            oauth2_secret_key=self._get_gcp_secret("oauth2-secret-key"),
            encryption_key=self._get_gcp_secret("encryption-key"),
            api_rate_limit=100,
            session_timeout=1800
        )
        
    def _configure_multi_cloud(self) -> None:
        """Configuration multi-cloud avec failover"""
        primary_provider = os.getenv("PRIMARY_CLOUD_PROVIDER", "aws").lower()
        
        if primary_provider == "aws":
            self._configure_aws()
        elif primary_provider == "azure":
            self._configure_azure()
        else:
            self._configure_gcp()
            
        # Configuration failover
        self._setup_failover_configuration()
        
    def _get_aws_secret(self, secret_name: str) -> str:
        """Récupère un secret depuis AWS Secrets Manager"""
        try:
            import boto3
            client = boto3.client('secretsmanager', region_name=self.storage_config.aws_region if self.storage_config else 'eu-central-1')
            response = client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except Exception:
            return os.getenv(secret_name.upper().replace('-', '_'), f"fallback-{secret_name}")
            
    def _get_azure_secret(self, secret_name: str) -> str:
        """Récupère un secret depuis Azure Key Vault"""
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            vault_url = os.getenv("AZURE_KEY_VAULT_URL")
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)
            secret = client.get_secret(secret_name)
            return secret.value
        except Exception:
            return os.getenv(secret_name.upper().replace('-', '_'), f"fallback-{secret_name}")
            
    def _get_gcp_secret(self, secret_name: str) -> str:
        """Récupère un secret depuis GCP Secret Manager"""
        try:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()
            project_id = os.getenv("GCP_PROJECT_ID")
            name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception:
            return os.getenv(secret_name.upper().replace('-', '_'), f"fallback-{secret_name}")
            
    def _setup_failover_configuration(self) -> None:
        """Configure le failover multi-cloud"""
        self.failover_config = {
            "enabled": True,
            "primary_provider": self.cloud_provider.value,
            "secondary_providers": self._get_secondary_providers(),
            "health_check_interval": 30,
            "failover_threshold": 3,
            "auto_recovery": True
        }
        
    def _get_secondary_providers(self) -> List[str]:
        """Retourne les providers de failover"""
        secondary = os.getenv("SECONDARY_CLOUD_PROVIDERS", "").split(",")
        return [p.strip() for p in secondary if p.strip()]
        
    def validate_configuration(self) -> bool:
        """Valide la configuration cloud"""
        try:
            # Vérifications cloud génériques
            assert self.database_config is not None, "Configuration base de données requise"
            assert self.redis_config is not None, "Configuration Redis requise"
            assert self.security_config is not None, "Configuration sécurité requise"
            assert self.storage_config is not None, "Configuration stockage requise"
            
            # Vérifications spécifiques cloud
            if self.cloud_provider == CloudProvider.AWS:
                assert self.storage_config.s3_bucket_name, "Bucket S3 AWS requis"
                assert self.storage_config.aws_region, "Région AWS requise"
            elif self.cloud_provider == CloudProvider.AZURE:
                assert os.getenv("AZURE_SUBSCRIPTION_ID"), "Subscription Azure requise"
            elif self.cloud_provider == CloudProvider.GCP:
                assert os.getenv("GCP_PROJECT_ID"), "Project ID GCP requis"
                
            return True
            
        except (AssertionError, AttributeError) as e:
            print(f"❌ Erreur validation configuration cloud: {e}")
            return False
            
    def get_cloud_features(self) -> Dict[str, Any]:
        """Fonctionnalités spécifiques cloud"""
        return {
            "cloud_native": True,
            "auto_scaling": True,
            "load_balancing": True,
            "managed_services": True,
            "serverless_ready": True,
            "cdn_enabled": True,
            "backup_automated": True,
            "disaster_recovery": True,
            "multi_region": True,
            "secrets_management": True,
            "monitoring_integrated": True,
            "cost_optimization": True
        }
        
    def get_aws_specific_config(self) -> Dict[str, Any]:
        """Configuration spécifique AWS"""
        if self.cloud_provider != CloudProvider.AWS:
            return {}
            
        return {
            "services": {
                "rds": {
                    "instance_class": os.getenv("AWS_RDS_INSTANCE_CLASS", "db.r5.large"),
                    "multi_az": bool(os.getenv("AWS_RDS_MULTI_AZ", True)),
                    "backup_retention": int(os.getenv("AWS_RDS_BACKUP_RETENTION", "7"))
                },
                "elasticache": {
                    "node_type": os.getenv("AWS_ELASTICACHE_NODE_TYPE", "cache.r6g.large"),
                    "num_cache_nodes": int(os.getenv("AWS_ELASTICACHE_NODES", "2"))
                },
                "s3": {
                    "storage_class": os.getenv("AWS_S3_STORAGE_CLASS", "STANDARD"),
                    "versioning": bool(os.getenv("AWS_S3_VERSIONING", True)),
                    "encryption": "AES256"
                },
                "cloudfront": {
                    "enabled": bool(os.getenv("AWS_CLOUDFRONT_ENABLED", True)),
                    "price_class": os.getenv("AWS_CLOUDFRONT_PRICE_CLASS", "PriceClass_100")
                }
            },
            "regions": {
                "primary": os.getenv("AWS_REGION", "eu-central-1"),
                "secondary": os.getenv("AWS_SECONDARY_REGION", "eu-west-1")
            }
        }
        
    def get_azure_specific_config(self) -> Dict[str, Any]:
        """Configuration spécifique Azure"""
        if self.cloud_provider != CloudProvider.AZURE:
            return {}
            
        return {
            "services": {
                "database": {
                    "sku": os.getenv("AZURE_DB_SKU", "GP_Gen5_4"),
                    "tier": os.getenv("AZURE_DB_TIER", "GeneralPurpose")
                },
                "redis": {
                    "sku": os.getenv("AZURE_REDIS_SKU", "Standard"),
                    "family": "C",
                    "capacity": int(os.getenv("AZURE_REDIS_CAPACITY", "1"))
                },
                "storage": {
                    "account_type": os.getenv("AZURE_STORAGE_TYPE", "Standard_LRS"),
                    "tier": "Hot"
                }
            },
            "regions": {
                "primary": os.getenv("AZURE_REGION", "West Europe"),
                "secondary": os.getenv("AZURE_SECONDARY_REGION", "North Europe")
            }
        }
        
    def get_gcp_specific_config(self) -> Dict[str, Any]:
        """Configuration spécifique GCP"""
        if self.cloud_provider != CloudProvider.GCP:
            return {}
            
        return {
            "services": {
                "sql": {
                    "tier": os.getenv("GCP_SQL_TIER", "db-n1-standard-4"),
                    "availability_type": os.getenv("GCP_SQL_AVAILABILITY", "REGIONAL")
                },
                "redis": {
                    "tier": os.getenv("GCP_REDIS_TIER", "STANDARD_HA"),
                    "memory_size_gb": int(os.getenv("GCP_REDIS_MEMORY", "4"))
                },
                "storage": {
                    "storage_class": os.getenv("GCP_STORAGE_CLASS", "STANDARD"),
                    "location": os.getenv("GCP_STORAGE_LOCATION", "EU")
                }
            },
            "regions": {
                "primary": os.getenv("GCP_REGION", "europe-west3"),
                "secondary": os.getenv("GCP_SECONDARY_REGION", "europe-west1")
            }
        }
        
    def get_cost_optimization_config(self) -> Dict[str, Any]:
        """Configuration optimisation coûts"""
        return {
            "auto_shutdown": {
                "enabled": bool(os.getenv("COST_AUTO_SHUTDOWN", True)),
                "schedule": os.getenv("SHUTDOWN_SCHEDULE", "0 2 * * *"),  # 2 AM daily
                "environment_filter": ["dev", "staging"]
            },
            "resource_tagging": {
                "project": "ia-influencer",
                "owner": "fahed-mlaiel",
                "environment": self.environment.value,
                "cost_center": os.getenv("COST_CENTER", "engineering")
            },
            "budget_alerts": {
                "enabled": True,
                "monthly_limit": int(os.getenv("MONTHLY_BUDGET", "1000")),
                "alert_thresholds": [50, 75, 90, 100]
            }
        }
        
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporte la configuration cloud complète"""
        base_config = super().export_to_dict()
        base_config.update({
            "cloud_provider": self.cloud_provider.value,
            "cloud_features": self.get_cloud_features(),
            "cost_optimization": self.get_cost_optimization_config(),
            "provider_specific": {
                "aws": self.get_aws_specific_config(),
                "azure": self.get_azure_specific_config(),
                "gcp": self.get_gcp_specific_config()
            }
        })
        
        if hasattr(self, 'failover_config'):
            base_config["failover_config"] = self.failover_config
            
        return base_config


def create_cloud_config(provider: CloudProvider = CloudProvider.AWS) -> CloudConfigManager:
    """Crée et initialise la configuration cloud"""
    config = CloudConfigManager(provider)
    config.initialize_configuration()
    return config


def auto_detect_cloud_provider() -> CloudProvider:
    """
Détecte automatiquement le provider cloud"""
    # Détection AWS
    if os.getenv("AWS_REGION") or os.getenv("AWS_EXECUTION_ENV"):
        return CloudProvider.AWS
    
    # Détection Azure
    if os.getenv("AZURE_CLIENT_ID") or os.getenv("WEBSITE_SITE_NAME"):
        return CloudProvider.AZURE
    
    # Détection GCP
    if os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GAE_APPLICATION"):
        return CloudProvider.GCP
    
    # Default AWS
    return CloudProvider.AWS
