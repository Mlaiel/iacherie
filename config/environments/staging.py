"""🔧 Staging Environment Configuration - IA-Influencer-Agent
==================================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: DevOps + Backend Senior + ML Engineer + DBA + Security
Date: 2025-08-15

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Configuration environnement staging pour tests pré-production.
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


class StagingConfigManager(BaseEnvironmentConfigManager):
    """
    Configuration manager pour l'environnement de staging.
    Réplication de production avec données de test sécurisées.
    """
    
    def __init__(self):
        super().__init__(
            environment=EnvironmentType.STAGING,
            debug=False,
            host="0.0.0.0",
            port=int(os.getenv("STAGING_PORT", "8000")),
            workers=int(os.getenv("STAGING_WORKERS", "4")),
            worker_class="uvicorn.workers.UvicornWorker",
            cors_origins=self._get_staging_cors_origins(),
            allowed_hosts=self._get_staging_allowed_hosts()
        )
        
    def _get_staging_cors_origins(self) -> List[str]:
        """Définit les origins CORS autorisées en staging"""
        origins_env = os.getenv("STAGING_CORS_ORIGINS", "")
        if origins_env:
            return [origin.strip() for origin in origins_env.split(",")]
        return [
            "https://staging.ia-influencer.com",
            "https://staging-app.ia-influencer.com",
            "https://staging-api.ia-influencer.com",
            "http://localhost:3000"  # Pour tests locaux
        ]
        
    def _get_staging_allowed_hosts(self) -> List[str]:
        """Définit les hosts autorisés en staging"""
        hosts_env = os.getenv("STAGING_ALLOWED_HOSTS", "")
        if hosts_env:
            return [host.strip() for host in hosts_env.split(",")]
        return [
            "staging.ia-influencer.com",
            "staging-app.ia-influencer.com",
            "staging-api.ia-influencer.com",
            "localhost"
        ]
        
    def load_environment_specific_config(self) -> None:
        """Charge la configuration spécifique au staging"""
        
        # Configuration Base de Données Staging
        self.database_config = DatabaseConfig(
            host=os.getenv("STAGING_DB_HOST"),
            port=int(os.getenv("STAGING_DB_PORT", "5432")),
            name=os.getenv("STAGING_DB_NAME", "ia_influencer_staging"),
            username=os.getenv("STAGING_DB_USER"),
            password=os.getenv("STAGING_DB_PASSWORD"),
            pool_size=int(os.getenv("STAGING_DB_POOL_SIZE", "15")),
            max_overflow=int(os.getenv("STAGING_DB_MAX_OVERFLOW", "20")),
            ssl_mode="prefer"  # SSL préféré mais pas obligatoire
        )
        
        # Configuration Redis Staging
        self.redis_config = RedisConfig(
            host=os.getenv("STAGING_REDIS_HOST"),
            port=int(os.getenv("STAGING_REDIS_PORT", "6379")),
            password=os.getenv("STAGING_REDIS_PASSWORD"),
            db=int(os.getenv("STAGING_REDIS_DB", "1")),
            max_connections=int(os.getenv("STAGING_REDIS_MAX_CONN", "50")),
            socket_timeout=int(os.getenv("STAGING_REDIS_TIMEOUT", "10"))
        )
        
        # Configuration Sécurité Staging (intermédiaire)
        self.security_config = SecurityConfig(
            jwt_secret_key=os.getenv("STAGING_JWT_SECRET", "staging-jwt-secret-key-2025-secure"),
            jwt_algorithm="HS256",
            jwt_expiry_hours=int(os.getenv("STAGING_JWT_EXPIRY", "24")),
            oauth2_secret_key=os.getenv("STAGING_OAUTH2_SECRET", "staging-oauth2-secret-2025"),
            encryption_key=os.getenv("STAGING_ENCRYPTION_KEY", "staging-encryption-key-32-chars-2025"),
            api_rate_limit=int(os.getenv("STAGING_API_RATE_LIMIT", "500")),
            session_timeout=int(os.getenv("STAGING_SESSION_TIMEOUT", "3600"))
        )
        
        # Configuration IA Staging
        self.ai_config = AIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY_STAGING") or os.getenv("OPENAI_API_KEY"),
            huggingface_token=os.getenv("HUGGINGFACE_TOKEN_STAGING") or os.getenv("HUGGINGFACE_TOKEN"),
            tensorflow_gpu_enabled=bool(os.getenv("STAGING_GPU_ENABLED", False)),
            model_cache_dir=os.getenv("STAGING_MODEL_CACHE", "/app/staging/models"),
            vector_db_path=os.getenv("STAGING_VECTOR_DB", "/app/staging/vectordb"),
            fingerprint_similarity_threshold=float(os.getenv("STAGING_SIMILARITY_THRESHOLD", "0.85"))
        )
        
        # Configuration Stockage Staging (AWS S3 sandbox)
        self.storage_config = StorageConfig(
            aws_access_key_id=os.getenv("STAGING_AWS_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("STAGING_AWS_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("STAGING_AWS_REGION", "eu-central-1"),
            s3_bucket_name=os.getenv("STAGING_S3_BUCKET", "ia-influencer-staging-bucket"),
            local_storage_path=os.getenv("STAGING_STORAGE_PATH", "/app/staging/storage"),
            max_file_size_mb=int(os.getenv("STAGING_MAX_FILE_SIZE_MB", "200"))
        )
        
        # Configuration Monitoring Staging (complet pour tests)
        self.monitoring_config = MonitoringConfig(
            prometheus_enabled=True,
            grafana_enabled=True,
            jaeger_enabled=True,
            log_level=os.getenv("STAGING_LOG_LEVEL", "INFO"),
            metrics_port=int(os.getenv("STAGING_METRICS_PORT", "9092")),
            traces_endpoint=os.getenv("STAGING_JAEGER_ENDPOINT", "http://staging-jaeger:14268")
        )
        
        # Configuration Intégrations Staging (sandbox/test APIs)
        self.integration_config = IntegrationConfig(
            spotify_client_id=os.getenv("STAGING_SPOTIFY_CLIENT_ID") or os.getenv("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=os.getenv("STAGING_SPOTIFY_CLIENT_SECRET") or os.getenv("SPOTIFY_CLIENT_SECRET"),
            youtube_api_key=os.getenv("STAGING_YOUTUBE_API_KEY") or os.getenv("YOUTUBE_API_KEY"),
            instagram_access_token=os.getenv("STAGING_INSTAGRAM_ACCESS_TOKEN") or os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            tiktok_app_id=os.getenv("STAGING_TIKTOK_APP_ID") or os.getenv("TIKTOK_APP_ID"),
            twitter_bearer_token=os.getenv("STAGING_TWITTER_BEARER_TOKEN") or os.getenv("TWITTER_BEARER_TOKEN"),
            stripe_api_key=os.getenv("STAGING_STRIPE_API_KEY", "sk_test_staging"),  # Test keys
            wise_api_key=os.getenv("STAGING_WISE_API_KEY") or os.getenv("WISE_API_KEY")
        )
        
    def validate_configuration(self) -> bool:
        """Valide la configuration staging"""
        try:
            # Vérifications importantes pour staging
            assert self.database_config is not None, "Configuration base de données requise"
            assert self.redis_config is not None, "Configuration Redis requise"
            assert self.security_config is not None, "Configuration sécurité requise"
            assert self.ai_config is not None, "Configuration IA requise"
            assert self.storage_config is not None, "Configuration stockage requise"
            
            # Vérifications base de données
            assert self.database_config.host, "Host base de données requis en staging"
            assert self.database_config.name, "Nom base de données requis en staging"
            assert self.database_config.username, "Utilisateur base de données requis"
            assert self.database_config.password, "Mot de passe base de données requis"
            
            # Vérifications Redis
            assert self.redis_config.host, "Host Redis requis en staging"
            
            # Vérifications sécurité (intermédiaires)
            assert len(self.security_config.jwt_secret_key) >= 24, "Clé JWT trop faible pour staging"
            assert len(self.security_config.oauth2_secret_key) >= 24, "Clé OAuth2 trop faible"
            
            # Vérifications stockage
            assert self.storage_config.s3_bucket_name, "Bucket S3 requis en staging"
            
            # Vérifications spécifiques staging
            assert "staging" in self.database_config.name.lower(), "DB staging doit contenir 'staging'"
            assert "staging" in self.storage_config.s3_bucket_name.lower(), "Bucket staging doit contenir 'staging'"
            
            return True
            
        except (AssertionError, AttributeError) as e:
            print(f"❌ Erreur validation configuration staging: {e}")
            return False
            
    def get_staging_features(self) -> Dict[str, Any]:
        """Retourne les fonctionnalités spécifiques au staging"""
        return {
            "hot_reload": False,
            "debug_mode": False,
            "detailed_logging": True,  # Plus verbeux pour debug
            "api_docs_enabled": True,  # Activé pour tests
            "test_data_seeding": True,
            "mock_external_apis": False,  # APIs réelles en staging
            "profiling_enabled": True,
            "auto_migrations": True,   # Automatique en staging
            "ssl_required": False,     # Optionnel en staging
            "rate_limiting": True,
            "request_validation": True,
            "response_compression": True,
            "security_headers": True,
            "audit_logging": True,
            "integration_testing": True,
            "performance_testing": True
        }
        
    def get_testing_settings(self) -> Dict[str, Any]:
        """Paramètres spécifiques aux tests en staging"""
        return {
            "load_testing_enabled": True,
            "integration_tests_enabled": True,
            "api_testing_enabled": True,
            "ui_testing_enabled": True,
            "stress_testing_enabled": True,
            "security_testing_enabled": True,
            "test_data_isolation": True,
            "test_cleanup_enabled": True
        }
        
    def get_staging_urls(self) -> Dict[str, str]:
        """URLs utiles pour staging"""
        return {
            "api_docs": f"https://staging-api.ia-influencer.com/docs",
            "redoc": f"https://staging-api.ia-influencer.com/redoc",
            "admin_panel": f"https://staging-api.ia-influencer.com/admin",
            "metrics": f"https://staging-api.ia-influencer.com:{self.monitoring_config.metrics_port}/metrics",
            "grafana": "https://staging-grafana.ia-influencer.com",
            "jaeger": "https://staging-jaeger.ia-influencer.com"
        }
        
    def get_data_management_settings(self) -> Dict[str, Any]:
        """Paramètres de gestion des données staging"""
        return {
            "data_anonymization": True,
            "synthetic_data_generation": True,
            "data_masking": True,
            "backup_enabled": True,
            "data_retention_days": 30,
            "cleanup_schedule": "daily",
            "test_data_refresh": "weekly"
        }
        
    def create_staging_directories(self) -> None:
        """Crée les répertoires nécessaires au staging"""
        import os
        from pathlib import Path
        
        directories = [
            self.ai_config.model_cache_dir,
            self.ai_config.vector_db_path,
            self.storage_config.local_storage_path,
            "/app/staging/logs",
            "/app/staging/uploads",
            "/app/staging/fingerprints",
            "/app/staging/test_data",
            "/app/staging/backups"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporte la configuration staging complète"""
        base_config = super().export_to_dict()
        base_config.update({
            "staging_features": self.get_staging_features(),
            "testing_settings": self.get_testing_settings(),
            "staging_urls": self.get_staging_urls(),
            "data_management": self.get_data_management_settings(),
            "environment_type": "pre-production"
        })
        return base_config


# Fonction utilitaire pour configuration staging
def create_staging_config() -> StagingConfigManager:
    """Crée et initialise la configuration staging"""
    config = StagingConfigManager()
    config.initialize_configuration()
    config.create_staging_directories()
    return config
