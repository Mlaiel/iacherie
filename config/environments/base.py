"""🔧 Base Environment Configuration - IA-Influencer-Agent
==================================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: DevOps + Backend Senior + Infrastructure Architect
Date: 2025-08-15

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Configuration environnement de base pour toutes les plateformes.
Gestion centralisée des variables d'environnement enterprise.
==================================================================
"""
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import os
from dataclasses import dataclass
from pydantic import Field, validator
from pydantic_settings import BaseSettings
import json


class EnvironmentType(str, Enum):
    """Types d'environnements supportés"""    DEVELOPMENT = "development"
    STAGING = "staging" 
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Configuration base de données"""    host: str
    port: int
    name: str
    username: str
    password: str
    pool_size: int = 10
    max_overflow: int = 20
    ssl_mode: str = "prefer"
    
    @property
    def url(self) -> str:
        """URL de connexion PostgreSQL"""        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class RedisConfig:
    """Configuration Redis cache et queues"""    host: str
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 50
    socket_timeout: int = 30
    
    @property
    def url(self) -> str:
        """URL de connexion Redis"""        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


@dataclass
class SecurityConfig:
    """Configuration sécurité enterprise"""    jwt_secret_key: str
    oauth2_secret_key: str
    encryption_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    api_rate_limit: int = 1000
    session_timeout: int = 3600


@dataclass
class AIConfig:
    """Configuration modules IA et ML"""    openai_api_key: str
    huggingface_token: str
    tensorflow_gpu_enabled: bool = False
    model_cache_dir: str = "/tmp/ai_models"
    vector_db_path: str = "/data/vectordb"
    fingerprint_similarity_threshold: float = 0.85


@dataclass
class StorageConfig:
    """Configuration stockage cloud et local"""    aws_access_key_id: str
    aws_secret_access_key: str
    s3_bucket_name: str
    aws_region: str = "eu-central-1"
    local_storage_path: str = "/data/storage"
    max_file_size_mb: int = 100


@dataclass
class MonitoringConfig:
    """Configuration monitoring et observabilité"""    prometheus_enabled: bool = True
    grafana_enabled: bool = True
    jaeger_enabled: bool = True
    log_level: str = "INFO"
    metrics_port: int = 9090
    traces_endpoint: str = "http://jaeger:14268"


@dataclass
class IntegrationConfig:
    """Configuration intégrations externes"""    spotify_client_id: str
    spotify_client_secret: str
    youtube_api_key: str
    instagram_access_token: str
    tiktok_app_id: str
    twitter_bearer_token: str
    stripe_api_key: str
    wise_api_key: str


class BaseEnvironmentConfigManager(BaseSettings, ABC):
    """    Gestionnaire de configuration d'environnement de base.
    Classe abstraite pour tous les environnements.
    """    
    # Configuration générale
    environment: EnvironmentType
    debug: bool = False
    app_name: str = "IA-Influencer-Agent"
    app_version: str = "2.0.0"
    app_description: str = "Enterprise AI Influencer Agent with Content Protection"
    
    # Serveur web
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    worker_class: str = "uvicorn.workers.UvicornWorker"
    
    # Base de données
    database_config: Optional[DatabaseConfig] = None
    redis_config: Optional[RedisConfig] = None
    
    # Sécurité
    security_config: Optional[SecurityConfig] = None
    
    # IA et ML
    ai_config: Optional[AIConfig] = None
    
    # Stockage
    storage_config: Optional[StorageConfig] = None
    
    # Monitoring
    monitoring_config: Optional[MonitoringConfig] = None
    
    # Intégrations
    integration_config: Optional[IntegrationConfig] = None
    
    # Configuration avancée
    cors_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["*"]
    timezone: str = "Europe/Berlin"
    locale: str = "en_US.UTF-8"
    
    class Config:
        """Configuration Pydantic"""        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    @abstractmethod
    def load_environment_specific_config(self) -> None:
        """Charge la configuration spécifique à l'environnement"""        pass
        
    @abstractmethod
    def validate_configuration(self) -> bool:
        """Valide la configuration de l'environnement"""        pass
        
    def initialize_configuration(self) -> None:
        """Initialise la configuration complète"""        self.load_environment_specific_config()
        if not self.validate_configuration():
            raise RuntimeError(f"Configuration invalide pour l'environnement {self.environment}")
            
    def get_database_url(self) -> str:
        """Retourne l'URL de la base de données"""        if not self.database_config:
            raise ValueError("Configuration base de données non définie")
        return self.database_config.url
        
    def get_redis_url(self) -> str:
        """Retourne l'URL Redis"""        if not self.redis_config:
            raise ValueError("Configuration Redis non définie")
        return self.redis_config.url
        
    def get_security_settings(self) -> Dict[str, Any]:
        """Retourne les paramètres de sécurité"""        if not self.security_config:
            raise ValueError("Configuration sécurité non définie")
        return {
            "jwt_secret_key": self.security_config.jwt_secret_key,
            "jwt_algorithm": self.security_config.jwt_algorithm,
            "jwt_expiry_hours": self.security_config.jwt_expiry_hours,
            "api_rate_limit": self.security_config.api_rate_limit
        }
        
    def get_ai_settings(self) -> Dict[str, Any]:
        """Retourne les paramètres IA"""        if not self.ai_config:
            raise ValueError("Configuration IA non définie")
        return {
            "openai_api_key": self.ai_config.openai_api_key,
            "model_cache_dir": self.ai_config.model_cache_dir,
            "vector_db_path": self.ai_config.vector_db_path,
            "similarity_threshold": self.ai_config.fingerprint_similarity_threshold
        }
        
    def get_storage_settings(self) -> Dict[str, Any]:
        """Retourne les paramètres de stockage"""        if not self.storage_config:
            raise ValueError("Configuration stockage non définie")
        return {
            "aws_region": self.storage_config.aws_region,
            "s3_bucket": self.storage_config.s3_bucket_name,
            "local_path": self.storage_config.local_storage_path,
            "max_file_size": self.storage_config.max_file_size_mb
        }
        
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporte la configuration en dictionnaire"""        return {
            "environment": self.environment.value,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "debug": self.debug,
            "host": self.host,
            "port": self.port,
            "database_url": self.get_database_url() if self.database_config else None,
            "redis_url": self.get_redis_url() if self.redis_config else None,
            "cors_origins": self.cors_origins,
            "timezone": self.timezone
        }
        
    def export_to_json(self) -> str:
        """Exporte la configuration en JSON"""        return json.dumps(self.export_to_dict(), indent=2)
        
    @classmethod
    def from_env_file(cls, env_file_path: str):
        """Charge la configuration depuis un fichier .env"""        return cls(_env_file=env_file_path)
        
    def __str__(self) -> str:
        """Représentation string de la configuration"""        return f"{self.__class__.__name__}(environment={self.environment}, debug={self.debug})"
        
    def __repr__(self) -> str:
        """Représentation détaillée de la configuration"""        return self.__str__()


class EnvironmentConfigFactory:
    """Factory pour créer les gestionnaires de configuration"""    
    _config_managers = {}
    
    @classmethod
    def register_manager(cls, env_type: EnvironmentType, manager_class):
        """Enregistre un gestionnaire pour un type d'environnement"""        cls._config_managers[env_type] = manager_class
        
    @classmethod
    def create_manager(cls, env_type: EnvironmentType) -> BaseEnvironmentConfigManager:
        """Crée un gestionnaire pour le type d'environnement spécifié"""        if env_type not in cls._config_managers:
            raise ValueError(f"Gestionnaire non enregistré pour l'environnement {env_type}")
        
        manager_class = cls._config_managers[env_type]
        return manager_class()
        
    @classmethod
    def get_available_environments(cls) -> List[EnvironmentType]:
        """Retourne la liste des environnements disponibles"""        return list(cls._config_managers.keys())


def get_current_environment() -> EnvironmentType:
    """Détecte l'environnement actuel depuis les variables d'environnement"""    env_name = os.getenv("ENVIRONMENT", "development").lower()
    try:
        return EnvironmentType(env_name)
    except ValueError:
        return EnvironmentType.DEVELOPMENT


def load_config_for_environment(env_type: Optional[EnvironmentType] = None) -> BaseEnvironmentConfigManager:
    """Charge la configuration pour un environnement spécifique"""    if env_type is None:
        env_type = get_current_environment()
        
    config_manager = EnvironmentConfigFactory.create_manager(env_type)
    config_manager.initialize_configuration()
    return config_manager


# Auto-enregistrement des gestionnaires d'environnement
def _register_default_managers():
    """Enregistre automatiquement les gestionnaires par défaut"""    try:
        # Import conditionnel pour éviter les imports circulaires
        from .development import DevelopmentConfigManager
        from .production import ProductionConfigManager
        from .staging import StagingConfigManager
        from .testing import TestingConfigManager
        
        # Enregistrement des gestionnaires
        EnvironmentConfigFactory.register_manager(EnvironmentType.DEVELOPMENT, DevelopmentConfigManager)
        EnvironmentConfigFactory.register_manager(EnvironmentType.PRODUCTION, ProductionConfigManager)
        EnvironmentConfigFactory.register_manager(EnvironmentType.STAGING, StagingConfigManager)
        EnvironmentConfigFactory.register_manager(EnvironmentType.TESTING, TestingConfigManager)
        
    except ImportError:
        # Les gestionnaires ne sont pas encore disponibles, on ignore
        pass


# Enregistrement automatique au chargement du module
_register_default_managers()
