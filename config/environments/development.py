"""🔧 Development Environment Configuration - IA-Influencer-Agent
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

Configuration environnement développement avec debugging avancé.
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


class DevelopmentConfigManager(BaseEnvironmentConfigManager):
    """
    Configuration manager pour l'environnement de développement.
    Optimisé pour développement local avec debugging avancé.
    """
    
    def __init__(self):
        super().__init__(
            environment=EnvironmentType.DEVELOPMENT,
            debug=True,
            host="127.0.0.1",
            port=8000,
            workers=1,
            cors_origins=[
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8080",
                "http://127.0.0.1:8080"
            ]
        )
        
    def load_environment_specific_config(self) -> None:
        """Charge la configuration spécifique au développement"""
        
        # Configuration Base de Données Développement
        self.database_config = DatabaseConfig(
            host=os.getenv("DEV_DB_HOST", "localhost"),
            port=int(os.getenv("DEV_DB_PORT", "5432")),
            name=os.getenv("DEV_DB_NAME", "ia_influencer_dev"),
            username=os.getenv("DEV_DB_USER", "dev_user"),
            password=os.getenv("DEV_DB_PASSWORD", "dev_password123"),
            pool_size=5,
            max_overflow=10,
            ssl_mode="disable"
        )
        
        # Configuration Redis Développement
        self.redis_config = RedisConfig(
            host=os.getenv("DEV_REDIS_HOST", "localhost"),
            port=int(os.getenv("DEV_REDIS_PORT", "6379")),
            password=os.getenv("DEV_REDIS_PASSWORD"),
            db=0,
            max_connections=20,
            socket_timeout=10
        )
        
        # Configuration Sécurité Développement (clés faibles)
        self.security_config = SecurityConfig(
            jwt_secret_key=os.getenv("DEV_JWT_SECRET", "dev-jwt-secret-key-2025"),
            jwt_algorithm="HS256",
            jwt_expiry_hours=24,
            oauth2_secret_key=os.getenv("DEV_OAUTH2_SECRET", "dev-oauth2-secret-2025"),
            encryption_key=os.getenv("DEV_ENCRYPTION_KEY", "dev-encryption-key-32-chars-2025"),
            api_rate_limit=10000,  # Élevé pour développement
            session_timeout=7200   # 2 heures
        )
        
        # Configuration IA Développement
        self.ai_config = AIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            huggingface_token=os.getenv("HUGGINGFACE_TOKEN", ""),
            tensorflow_gpu_enabled=bool(os.getenv("DEV_GPU_ENABLED", False)),
            model_cache_dir=os.getenv("DEV_MODEL_CACHE", "/tmp/dev_ai_models"),
            vector_db_path=os.getenv("DEV_VECTOR_DB", "/tmp/dev_vectordb"),
            fingerprint_similarity_threshold=0.80  # Plus permissif en dev
        )
        
        # Configuration Stockage Développement
        self.storage_config = StorageConfig(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dev-access-key"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dev-secret-key"),
            aws_region=os.getenv("AWS_REGION", "eu-central-1"),
            s3_bucket_name=os.getenv("DEV_S3_BUCKET", "ia-influencer-dev-bucket"),
            local_storage_path=os.getenv("DEV_STORAGE_PATH", "/tmp/dev_storage"),
            max_file_size_mb=50  # Limité en dev
        )
        
        # Configuration Monitoring Développement
        self.monitoring_config = MonitoringConfig(
            prometheus_enabled=False,  # Désactivé en dev par défaut
            grafana_enabled=False,
            jaeger_enabled=True,       # Tracing activé pour debug
            log_level="DEBUG",
            metrics_port=9091,
            traces_endpoint=os.getenv("DEV_JAEGER_ENDPOINT", "http://localhost:14268")
        )
        
        # Configuration Intégrations Développement
        self.integration_config = IntegrationConfig(
            spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID", "dev-spotify-client"),
            spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET", "dev-spotify-secret"),
            youtube_api_key=os.getenv("YOUTUBE_API_KEY", "dev-youtube-key"),
            instagram_access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN", "dev-instagram-token"),
            tiktok_app_id=os.getenv("TIKTOK_APP_ID", "dev-tiktok-app"),
            twitter_bearer_token=os.getenv("TWITTER_BEARER_TOKEN", "dev-twitter-token"),
            stripe_api_key=os.getenv("STRIPE_API_KEY", "sk_test_dev"),
            wise_api_key=os.getenv("WISE_API_KEY", "dev-wise-key")
        )
        
    def validate_configuration(self) -> bool:
        """Valide la configuration développement"""
        try:
            # Vérifications minimales pour développement
            assert self.database_config is not None, "Configuration base de données requise"
            assert self.redis_config is not None, "Configuration Redis requise"
            assert self.security_config is not None, "Configuration sécurité requise"
            
            # Vérifications base de données
            assert self.database_config.host, "Host base de données requis"
            assert self.database_config.name, "Nom base de données requis"
            
            # Vérifications Redis
            assert self.redis_config.host, "Host Redis requis"
            
            # Vérifications sécurité (minimales en dev)
            assert len(self.security_config.jwt_secret_key) >= 16, "Clé JWT trop courte"
            
            return True
            
        except (AssertionError, AttributeError) as e:
            print(f"❌ Erreur validation configuration développement: {e}")
            return False
            
    def get_development_features(self) -> Dict[str, Any]:
        """Retourne les fonctionnalités spécifiques au développement"""
        return {
            "hot_reload": True,
            "debug_mode": True,
            "detailed_logging": True,
            "api_docs_enabled": True,
            "test_data_seeding": True,
            "mock_external_apis": True,
            "profiling_enabled": True,
            "auto_migrations": True
        }
        
    def get_debug_settings(self) -> Dict[str, Any]:
        """Paramètres de debugging avancés"""
        return {
            "sql_echo": True,
            "log_sql_queries": True,
            "trace_exceptions": True,
            "detailed_error_responses": True,
            "timing_middleware": True,
            "memory_profiling": True
        }
        
    def get_development_urls(self) -> Dict[str, str]:
        """URLs utiles pour développement"""
        return {
            "api_docs": f"http://{self.host}:{self.port}/docs",
            "redoc": f"http://{self.host}:{self.port}/redoc",
            "admin_panel": f"http://{self.host}:{self.port}/admin",
            "metrics": f"http://{self.host}:{self.monitoring_config.metrics_port}/metrics" if self.monitoring_config.prometheus_enabled else None,
            "jaeger_ui": "http://localhost:16686" if self.monitoring_config.jaeger_enabled else None
        }
        
    def create_dev_directories(self) -> None:
        """Crée les répertoires nécessaires au développement"""
        import os
        from pathlib import Path
        
        directories = [
            self.ai_config.model_cache_dir,
            self.ai_config.vector_db_path,
            self.storage_config.local_storage_path,
            "/tmp/dev_logs",
            "/tmp/dev_uploads",
            "/tmp/dev_fingerprints"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporte la configuration développement complète"""
        base_config = super().export_to_dict()
        base_config.update({
            "development_features": self.get_development_features(),
            "debug_settings": self.get_debug_settings(),
            "development_urls": self.get_development_urls(),
            "allowed_origins": self.cors_origins
        })
        return base_config


# Fonction utilitaire pour configuration rapide développement
def create_development_config() -> DevelopmentConfigManager:
    """Crée et initialise la configuration développement"""
    config = DevelopmentConfigManager()
    config.initialize_configuration()
    config.create_dev_directories()
    return config


# Configuration par défaut pour import direct
default_dev_config = create_development_config()
