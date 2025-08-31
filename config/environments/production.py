"""🔧 Production Environment Configuration - IA-Influencer-Agent
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

Configuration environnement production avec sécurité maximale.
==================================================================
"""
import os
import secrets
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


class ProductionConfigManager(BaseEnvironmentConfigManager):
    """    Configuration manager pour l'environnement de production.
    Sécurité maximale, performance optimisée, monitoring complet.
    """    
    def __init__(self):
        super().__init__(
            environment=EnvironmentType.PRODUCTION,
            debug=False,
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            workers=int(os.getenv("WORKERS", "8")),
            worker_class="uvicorn.workers.UvicornWorker",
            cors_origins=self._get_production_cors_origins(),
            allowed_hosts=self._get_production_allowed_hosts()
        )
        
    def _get_production_cors_origins(self) -> List[str]:
        """Définit les origins CORS autorisées en production"""        origins_env = os.getenv("CORS_ORIGINS", "")
        if origins_env:
            return [origin.strip() for origin in origins_env.split(",")]
        return [
            "https://ia-influencer.com",
            "https://www.ia-influencer.com",
            "https://app.ia-influencer.com",
            "https://api.ia-influencer.com"
        ]
        
    def _get_production_allowed_hosts(self) -> List[str]:
        """Définit les hosts autorisés en production"""        hosts_env = os.getenv("ALLOWED_HOSTS", "")
        if hosts_env:
            return [host.strip() for host in hosts_env.split(",")]
        return [
            "ia-influencer.com",
            "www.ia-influencer.com", 
            "app.ia-influencer.com",
            "api.ia-influencer.com"
        ]
        
    def load_environment_specific_config(self) -> None:
        """Charge la configuration spécifique à la production"""        
        # Configuration Base de Données Production
        self.database_config = DatabaseConfig(
            host=os.getenv("PROD_DB_HOST"),
            port=int(os.getenv("PROD_DB_PORT", "5432")),
            name=os.getenv("PROD_DB_NAME"),
            username=os.getenv("PROD_DB_USER"),
            password=os.getenv("PROD_DB_PASSWORD"),
            pool_size=int(os.getenv("PROD_DB_POOL_SIZE", "20")),
            max_overflow=int(os.getenv("PROD_DB_MAX_OVERFLOW", "30")),
            ssl_mode="require"  # SSL obligatoire en production
        )
        
        # Configuration Redis Production (cluster)
        self.redis_config = RedisConfig(
            host=os.getenv("PROD_REDIS_HOST"),
            port=int(os.getenv("PROD_REDIS_PORT", "6379")),
            password=os.getenv("PROD_REDIS_PASSWORD"),
            db=0,
            max_connections=int(os.getenv("PROD_REDIS_MAX_CONN", "100")),
            socket_timeout=int(os.getenv("PROD_REDIS_TIMEOUT", "5"))
        )
        
        # Configuration Sécurité Production (clés fortes)
        self.security_config = SecurityConfig(
            jwt_secret_key=os.getenv("PROD_JWT_SECRET") or self._generate_secure_key(),
            jwt_algorithm="HS256",
            jwt_expiry_hours=int(os.getenv("PROD_JWT_EXPIRY", "12")),  # Plus court
            oauth2_secret_key=os.getenv("PROD_OAUTH2_SECRET") or self._generate_secure_key(),
            encryption_key=os.getenv("PROD_ENCRYPTION_KEY") or self._generate_secure_key(),
            api_rate_limit=int(os.getenv("PROD_API_RATE_LIMIT", "100")),  # Strict
            session_timeout=int(os.getenv("PROD_SESSION_TIMEOUT", "1800"))  # 30 min
        )
        
        # Configuration IA Production
        self.ai_config = AIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            huggingface_token=os.getenv("HUGGINGFACE_TOKEN"),
            tensorflow_gpu_enabled=bool(os.getenv("PROD_GPU_ENABLED", True)),
            model_cache_dir=os.getenv("PROD_MODEL_CACHE", "/app/models/cache"),
            vector_db_path=os.getenv("PROD_VECTOR_DB", "/app/data/vectordb"),
            fingerprint_similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.90"))
        )
        
        # Configuration Stockage Production (AWS S3)
        self.storage_config = StorageConfig(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("AWS_REGION", "eu-central-1"),
            s3_bucket_name=os.getenv("PROD_S3_BUCKET"),
            local_storage_path=os.getenv("PROD_STORAGE_PATH", "/app/storage"),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "500"))
        )
        
        # Configuration Monitoring Production (complet)
        self.monitoring_config = MonitoringConfig(
            prometheus_enabled=True,
            grafana_enabled=True,
            jaeger_enabled=True,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            metrics_port=int(os.getenv("METRICS_PORT", "9090")),
            traces_endpoint=os.getenv("JAEGER_ENDPOINT", "http://jaeger:14268")
        )
        
        # Configuration Intégrations Production
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
        
    def _generate_secure_key(self) -> str:
        """Génère une clé sécurisée pour production"""        return secrets.token_urlsafe(32)
        
    def validate_configuration(self) -> bool:
        """Valide la configuration production avec vérifications strictes"""        try:
            # Vérifications critiques pour production
            assert self.database_config is not None, "Configuration base de données requise"
            assert self.redis_config is not None, "Configuration Redis requise"
            assert self.security_config is not None, "Configuration sécurité requise"
            assert self.ai_config is not None, "Configuration IA requise"
            assert self.storage_config is not None, "Configuration stockage requise"
            assert self.monitoring_config is not None, "Configuration monitoring requise"
            assert self.integration_config is not None, "Configuration intégrations requise"
            
            # Vérifications base de données
            assert self.database_config.host, "Host base de données requis en production"
            assert self.database_config.name, "Nom base de données requis en production"
            assert self.database_config.username, "Utilisateur base de données requis"
            assert self.database_config.password, "Mot de passe base de données requis"
            assert self.database_config.ssl_mode == "require", "SSL requis en production"
            
            # Vérifications Redis
            assert self.redis_config.host, "Host Redis requis en production"
            assert self.redis_config.password, "Mot de passe Redis requis en production"
            
            # Vérifications sécurité strictes
            assert len(self.security_config.jwt_secret_key) >= 32, "Clé JWT trop faible pour production"
            assert len(self.security_config.oauth2_secret_key) >= 32, "Clé OAuth2 trop faible"
            assert len(self.security_config.encryption_key) >= 32, "Clé chiffrement trop faible"
            assert self.security_config.api_rate_limit <= 1000, "Rate limit trop élevé"
            
            # Vérifications IA
            assert self.ai_config.openai_api_key, "Clé OpenAI requise en production"
            assert self.ai_config.huggingface_token, "Token HuggingFace requis"
            
            # Vérifications stockage
            assert self.storage_config.aws_access_key_id, "Clés AWS requises en production"
            assert self.storage_config.aws_secret_access_key, "Secret AWS requis"
            assert self.storage_config.s3_bucket_name, "Bucket S3 requis"
            
            # Vérifications intégrations
            assert self.integration_config.spotify_client_id, "Client Spotify requis"
            assert self.integration_config.stripe_api_key, "Clé Stripe requise"
            
            # Vérifications CORS et sécurité réseau
            assert all(origin.startswith("https://") for origin in self.cors_origins), "HTTPS obligatoire en production"
            assert "localhost" not in str(self.cors_origins), "Localhost interdit en production"
            
            return True
            
        except (AssertionError, AttributeError) as e:
            print(f"❌ ERREUR CRITIQUE - Configuration production invalide: {e}")
            return False
            
    def get_production_features(self) -> Dict[str, Any]:
        """Retourne les fonctionnalités spécifiques à la production"""        return {
            "hot_reload": False,
            "debug_mode": False,
            "detailed_logging": False,
            "api_docs_enabled": False,  # Sécurité
            "test_data_seeding": False,
            "mock_external_apis": False,
            "profiling_enabled": False,
            "auto_migrations": False,   # Contrôlé manuellement
            "ssl_required": True,
            "rate_limiting": True,
            "request_validation": True,
            "response_compression": True,
            "security_headers": True,
            "audit_logging": True
        }
        
    def get_security_settings(self) -> Dict[str, Any]:
        """Paramètres de sécurité renforcés pour production"""        base_settings = super().get_security_settings()
        base_settings.update({
            "ssl_required": True,
            "hsts_enabled": True,
            "csrf_protection": True,
            "xss_protection": True,
            "content_type_nosniff": True,
            "referrer_policy": "strict-origin-when-cross-origin",
            "permissions_policy": "camera=(), microphone=(), geolocation=()",
            "session_cookie_secure": True,
            "session_cookie_httponly": True,
            "session_cookie_samesite": "strict"
        })
        return base_settings
        
    def get_performance_settings(self) -> Dict[str, Any]:
        """Paramètres de performance pour production"""        return {
            "connection_pooling": True,
            "query_caching": True,
            "response_caching": True,
            "cdn_enabled": True,
            "compression_enabled": True,
            "keep_alive": True,
            "worker_connections": 1000,
            "max_requests_per_worker": 10000,
            "preload_app": True,
            "graceful_timeout": 30
        }
        
    def get_monitoring_settings(self) -> Dict[str, Any]:
        """Configuration monitoring complète"""        return {
            "health_checks": True,
            "metrics_collection": True,
            "distributed_tracing": True,
            "error_tracking": True,
            "performance_monitoring": True,
            "business_metrics": True,
            "alerting_enabled": True,
            "log_aggregation": True
        }
        
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporte la configuration production complète"""        base_config = super().export_to_dict()
        base_config.update({
            "production_features": self.get_production_features(),
            "security_settings": self.get_security_settings(),
            "performance_settings": self.get_performance_settings(),
            "monitoring_settings": self.get_monitoring_settings(),
            "ssl_required": True,
            "debug_disabled": True
        })
        return base_config


# Fonction utilitaire pour configuration production
def create_production_config() -> ProductionConfigManager:
    """Crée et initialise la configuration production"""    config = ProductionConfigManager()
    config.initialize_configuration()
    return config
