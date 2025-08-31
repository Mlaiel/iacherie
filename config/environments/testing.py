"""🔧 Testing Environment Configuration - IA-Influencer-Agent
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

Configuration environnement testing pour tests automatisés.
==================================================================
"""
import os
import tempfile
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


class TestingConfigManager(BaseEnvironmentConfigManager):
    """    Configuration manager pour l'environnement de testing.
    Optimisé pour tests automatisés, données temporaires, mocks.
    """    
    def __init__(self):
        super().__init__(
            environment=EnvironmentType.TESTING,
            debug=True,
            host="127.0.0.1",
            port=8001,  # Port différent pour éviter conflits
            workers=1,   # Single worker pour tests
            cors_origins=["*"],  # Permissif pour tests
            allowed_hosts=["*"]
        )
        
    def load_environment_specific_config(self) -> None:
        """Charge la configuration spécifique aux tests"""        
        # Configuration Base de Données Test (SQLite in-memory par défaut)
        test_db_url = os.getenv("TEST_DATABASE_URL")
        if test_db_url and test_db_url.startswith("postgresql://"):
            # Base PostgreSQL dédiée aux tests
            from urllib.parse import urlparse
            parsed = urlparse(test_db_url)
            self.database_config = DatabaseConfig(
                host=parsed.hostname,
                port=parsed.port or 5432,
                name=parsed.path[1:],
                username=parsed.username,
                password=parsed.password,
                pool_size=2,  # Minimal pour tests
                max_overflow=5,
                ssl_mode="disable"
            )
        else:
            # SQLite par défaut pour tests rapides
            self.database_config = DatabaseConfig(
                host="localhost",
                port=0,
                name="test_ia_influencer.db",
                username="test_user",
                password="test_password",
                pool_size=1,
                max_overflow=2,
                ssl_mode="disable"
            )
            
        # Configuration Redis Test (in-memory ou DB séparée)
        self.redis_config = RedisConfig(
            host=os.getenv("TEST_REDIS_HOST", "localhost"),
            port=int(os.getenv("TEST_REDIS_PORT", "6379")),
            password=os.getenv("TEST_REDIS_PASSWORD"),
            db=int(os.getenv("TEST_REDIS_DB", "15")),  # DB séparée pour tests
            max_connections=5,
            socket_timeout=1
        )
        
        # Configuration Sécurité Test (clés fixes pour reproductibilité)
        self.security_config = SecurityConfig(
            jwt_secret_key="test-jwt-secret-key-fixed-2025",
            jwt_algorithm="HS256",
            jwt_expiry_hours=1,  # Court pour tests
            oauth2_secret_key="test-oauth2-secret-fixed-2025",
            encryption_key="test-encryption-key-32-chars-2025",
            api_rate_limit=10000,  # Pas de limite en test
            session_timeout=300    # 5 minutes
        )
        
        # Configuration IA Test (mocked par défaut)
        temp_dir = tempfile.gettempdir()
        self.ai_config = AIConfig(
            openai_api_key=os.getenv("TEST_OPENAI_API_KEY", "test-openai-key"),
            huggingface_token=os.getenv("TEST_HUGGINGFACE_TOKEN", "test-hf-token"),
            tensorflow_gpu_enabled=False,  # GPU désactivé pour tests
            model_cache_dir=os.path.join(temp_dir, "test_ai_models"),
            vector_db_path=os.path.join(temp_dir, "test_vectordb"),
            fingerprint_similarity_threshold=0.75  # Plus permissif pour tests
        )
        
        # Configuration Stockage Test (temporaire)
        self.storage_config = StorageConfig(
            aws_access_key_id="test-aws-access-key",
            aws_secret_access_key="test-aws-secret-key",
            aws_region="eu-central-1",
            s3_bucket_name="test-ia-influencer-bucket",
            local_storage_path=os.path.join(temp_dir, "test_storage"),
            max_file_size_mb=10  # Petit pour tests rapides
        )
        
        # Configuration Monitoring Test (minimal)
        self.monitoring_config = MonitoringConfig(
            prometheus_enabled=False,
            grafana_enabled=False,
            jaeger_enabled=False,
            log_level="DEBUG",
            metrics_port=9093,
            traces_endpoint="http://localhost:14268"
        )
        
        # Configuration Intégrations Test (mocked)
        self.integration_config = IntegrationConfig(
            spotify_client_id="test-spotify-client",
            spotify_client_secret="test-spotify-secret",
            youtube_api_key="test-youtube-key",
            instagram_access_token="test-instagram-token",
            tiktok_app_id="test-tiktok-app",
            twitter_bearer_token="test-twitter-token",
            stripe_api_key="sk_test_test_key",
            wise_api_key="test-wise-key"
        )
        
    def validate_configuration(self) -> bool:
        """Valide la configuration test (vérifications minimales)"""        try:
            # Vérifications de base pour tests
            assert self.database_config is not None, "Configuration base de données requise"
            assert self.redis_config is not None, "Configuration Redis requise"
            assert self.security_config is not None, "Configuration sécurité requise"
            
            # Vérifications spécifiques tests
            assert self.redis_config.db >= 10, "DB Redis test doit être >= 10"
            assert "test" in self.database_config.name.lower(), "DB test doit contenir 'test'"
            assert self.ai_config.tensorflow_gpu_enabled is False, "GPU désactivé en test"
            
            return True
            
        except (AssertionError, AttributeError) as e:
            print(f"❌ Erreur validation configuration test: {e}")
            return False
            
    def get_testing_features(self) -> Dict[str, Any]:
        """Retourne les fonctionnalités spécifiques aux tests"""        return {
            "hot_reload": False,
            "debug_mode": True,
            "detailed_logging": True,
            "api_docs_enabled": False,  # Pas nécessaire en test
            "test_data_seeding": True,
            "mock_external_apis": True,  # Toutes les APIs mockées
            "profiling_enabled": False,
            "auto_migrations": True,
            "database_isolation": True,
            "transaction_rollback": True,
            "parallel_testing": True,
            "coverage_enabled": True,
            "fast_mode": True,
            "cleanup_enabled": True
        }
        
    def get_mock_settings(self) -> Dict[str, Any]:
        """Configuration des mocks pour tests"""        return {
            "mock_spotify_api": True,
            "mock_youtube_api": True,
            "mock_instagram_api": True,
            "mock_tiktok_api": True,
            "mock_twitter_api": True,
            "mock_stripe_api": True,
            "mock_aws_s3": True,
            "mock_openai_api": True,
            "mock_email_service": True,
            "mock_file_uploads": True,
            "mock_ai_processing": True,
            "mock_fingerprinting": True
        }
        
    def get_test_database_settings(self) -> Dict[str, Any]:
        """Paramètres base de données spécifiques aux tests"""        return {
            "in_memory_database": True,
            "auto_create_tables": True,
            "auto_drop_tables": True,
            "transaction_isolation": True,
            "rollback_on_teardown": True,
            "test_data_fixtures": True,
            "foreign_key_checks": False,  # Pour vitesse
            "connection_pooling": False
        }
        
    def get_performance_settings(self) -> Dict[str, Any]:
        """Paramètres de performance pour tests rapides"""        return {
            "async_mode": True,
            "parallel_execution": True,
            "cache_disabled": True,
            "validation_minimal": True,
            "logging_minimal": True,
            "metrics_disabled": True,
            "tracing_disabled": True,
            "compression_disabled": True
        }
        
    def get_test_data_settings(self) -> Dict[str, Any]:
        """Configuration des données de test"""        return {
            "factory_enabled": True,
            "faker_enabled": True,
            "fixtures_enabled": True,
            "snapshots_enabled": True,
            "test_users_count": 5,
            "test_content_samples": 10,
            "mock_fingerprints": 20,
            "synthetic_data": True
        }
        
    def create_test_directories(self) -> None:
        """Crée les répertoires temporaires pour tests"""        import os
        from pathlib import Path
        
        directories = [
            self.ai_config.model_cache_dir,
            self.ai_config.vector_db_path,
            self.storage_config.local_storage_path,
            os.path.join(self.storage_config.local_storage_path, "uploads"),
            os.path.join(self.storage_config.local_storage_path, "fingerprints"),
            os.path.join(self.storage_config.local_storage_path, "test_data")
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def cleanup_test_environment(self) -> None:
        """Nettoie l'environnement de test"""        import shutil
        from pathlib import Path
        
        cleanup_paths = [
            self.ai_config.model_cache_dir,
            self.ai_config.vector_db_path,
            self.storage_config.local_storage_path
        ]
        
        for path in cleanup_paths:
            if Path(path).exists():
                shutil.rmtree(path, ignore_errors=True)
                
    def get_test_urls(self) -> Dict[str, str]:
        """URLs utiles pour tests"""        return {
            "api_base": f"http://{self.host}:{self.port}",
            "health_check": f"http://{self.host}:{self.port}/health",
            "test_runner": f"http://{self.host}:{self.port}/test",
            "coverage": f"http://{self.host}:{self.port}/coverage"
        }
        
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporte la configuration test complète"""        base_config = super().export_to_dict()
        base_config.update({
            "testing_features": self.get_testing_features(),
            "mock_settings": self.get_mock_settings(),
            "test_database": self.get_test_database_settings(),
            "performance_settings": self.get_performance_settings(),
            "test_data_settings": self.get_test_data_settings(),
            "test_urls": self.get_test_urls(),
            "temporary_storage": True
        })
        return base_config


# Fonction utilitaire pour configuration test
def create_testing_config() -> TestingConfigManager:
    """Crée et initialise la configuration test"""    config = TestingConfigManager()
    config.initialize_configuration()
    config.create_test_directories()
    return config


# Context manager pour tests isolés
class TestEnvironmentContext:
    """Context manager pour environnement de test isolé"""    
    def __init__(self):
        self.config = None
        
    def __enter__(self) -> TestingConfigManager:
        self.config = create_testing_config()
        return self.config
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.config:
            self.config.cleanup_test_environment()
