"""🔧 Environments Configuration - IA-Influencer-Agent
==================================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: DevOps + Backend Senior + ML Engineer + DBA + Security + Cloud Architect
Date: 2025-08-15

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Gestionnaires de configuration multi-environnements enterprise.
Support complet: Development, Staging, Testing, Production, Docker, K8s, Cloud.
==================================================================
"""

import os
from typing import Dict, Any, Optional, Type, Union
from enum import Enum

# Import des configurations de base
from .base import (
    BaseEnvironmentConfigManager, 
    EnvironmentType,
    EnvironmentConfigFactory,
    get_current_environment,
    load_config_for_environment
)

# Import des configurations d'environnement standard
from .development import DevelopmentConfigManager, create_development_config
from .production import ProductionConfigManager, create_production_config
from .staging import StagingConfigManager, create_staging_config
from .testing import TestingConfigManager, create_testing_config, TestEnvironmentContext

# Import des configurations spécialisées
from .docker import DockerConfigManager, create_docker_config
from .kubernetes import KubernetesConfigManager, create_kubernetes_config
from .cloud import (
    CloudConfigManager, 
    CloudProvider, 
    create_cloud_config, 
    auto_detect_cloud_provider
)


class DeploymentType(str, Enum):
    """
Types de déploiement supportés"""

    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"
    SERVERLESS = "serverless"


class EnvironmentManagerFactory:
    """
    Factory avancé pour créer les gestionnaires d'environnements.
    Support auto-détection et configuration intelligente.
    """
    
    # Mapping des configurations par environnement
    _environment_managers: Dict[EnvironmentType, Type[BaseEnvironmentConfigManager]] = {
        EnvironmentType.DEVELOPMENT: DevelopmentConfigManager,
        EnvironmentType.STAGING: StagingConfigManager,
        EnvironmentType.TESTING: TestingConfigManager,
        EnvironmentType.PRODUCTION: ProductionConfigManager,
    }
    
    # Mapping des configurations par déploiement
    _deployment_managers: Dict[DeploymentType, Type[BaseEnvironmentConfigManager]] = {
        DeploymentType.LOCAL: DevelopmentConfigManager,
        DeploymentType.DOCKER: DockerConfigManager,
        DeploymentType.KUBERNETES: KubernetesConfigManager,
        DeploymentType.CLOUD: CloudConfigManager,
    }
    
    @classmethod
    def create_manager(
        cls, 
        env_type: Optional[EnvironmentType] = None,
        deployment_type: Optional[DeploymentType] = None,
        cloud_provider: Optional[CloudProvider] = None,
        auto_detect: bool = True
    ) -> BaseEnvironmentConfigManager:
        """
        Crée un gestionnaire de configuration intelligent.
        
        Args:
            env_type: Type d'environnement (development, staging, testing, production)
            deployment_type: Type de déploiement (local, docker, kubernetes, cloud)
            cloud_provider: Provider cloud si applicable
            auto_detect: Active la détection automatique
            
        Returns:
            Instance du gestionnaire de configuration approprié
        """
        
        # Détection automatique si activée
        if auto_detect:
            if env_type is None:
                env_type = cls._auto_detect_environment()
            if deployment_type is None:
                deployment_type = cls._auto_detect_deployment()
            if cloud_provider is None and deployment_type == DeploymentType.CLOUD:
                cloud_provider = auto_detect_cloud_provider()
        
        # Sélection du gestionnaire approprié
        if deployment_type == DeploymentType.CLOUD:
            manager = CloudConfigManager(cloud_provider or CloudProvider.AWS)
        elif deployment_type == DeploymentType.KUBERNETES:
            manager = KubernetesConfigManager()
        elif deployment_type == DeploymentType.DOCKER:
            manager = DockerConfigManager()
        elif env_type in cls._environment_managers:
            manager_class = cls._environment_managers[env_type]
            manager = manager_class()
        else:
            # Fallback sur development
            manager = DevelopmentConfigManager()
        
        # Initialisation
        manager.initialize_configuration()
        return manager
        
    @classmethod
    def _auto_detect_environment(cls) -> EnvironmentType:
        """
Détecte automatiquement l'environnement"""
        env_indicators = {
            EnvironmentType.PRODUCTION: [
                "PROD", "PRODUCTION", "prod",
                lambda: os.getenv("NODE_ENV") == "production",
                lambda: os.getenv("FLASK_ENV") == "production",
                lambda: bool(os.getenv("AWS_EXECUTION_ENV")),
                lambda: bool(os.getenv("KUBERNETES_SERVICE_HOST"))
            ],
            EnvironmentType.STAGING: [
                "STAGING", "STAGE", "staging",
                lambda: "staging" in os.getenv("DATABASE_URL", "").lower(),
                lambda: "staging" in os.getenv("REDIS_URL", "").lower()
            ],
            EnvironmentType.TESTING: [
                "TEST", "TESTING", "test",
                lambda: bool(os.getenv("PYTEST_CURRENT_TEST")),
                lambda: bool(os.getenv("UNITTEST_RUNNING")),
                lambda: "test" in os.getenv("DATABASE_URL", "").lower()
            ]
        }
        
        # Vérification des indicateurs
        for env_type, indicators in env_indicators.items():
            for indicator in indicators:
                if callable(indicator):
                    try:
                        if indicator():
                            return env_type
                    except Exception:
                        continue
                elif isinstance(indicator, str):
                    if (os.getenv("ENVIRONMENT", "").upper() == indicator or
                        os.getenv("ENV", "").upper() == indicator):
                        return env_type
                        
        # Default development
        return EnvironmentType.DEVELOPMENT
        
    @classmethod
    def _auto_detect_deployment(cls) -> DeploymentType:
        """Détecte automatiquement le type de déploiement"""
        
        # Kubernetes
        if (os.getenv("KUBERNETES_SERVICE_HOST") or 
            os.path.exists("/var/run/secrets/kubernetes.io")):
            return DeploymentType.KUBERNETES
            
        # Docker
        if (os.path.exists("/.dockerenv") or 
            os.getenv("DOCKER_CONTAINER") or
            os.path.exists("/proc/1/cgroup") and "docker" in open("/proc/1/cgroup").read()):
            return DeploymentType.DOCKER
            
        # Cloud (AWS Lambda, Azure Functions, GCP Cloud Functions)
        if (os.getenv("AWS_LAMBDA_FUNCTION_NAME") or
            os.getenv("FUNCTIONS_WORKER_RUNTIME") or
            os.getenv("GAE_APPLICATION")):
            return DeploymentType.SERVERLESS
            
        # Cloud général
        if (os.getenv("AWS_REGION") or 
            os.getenv("AZURE_CLIENT_ID") or 
            os.getenv("GOOGLE_CLOUD_PROJECT")):
            return DeploymentType.CLOUD
            
        # Default local
        return DeploymentType.LOCAL
        
    @classmethod
    def get_available_environments(cls) -> Dict[str, Any]:
        """Retourne les environnements disponibles avec leurs descriptions"""
        return {
            "environments": {
                env_type.value: {
                    "name": env_type.value.title(),
                    "manager_class": manager_class.__name__,
                    "description": manager_class.__doc__.split('\n')[1].strip() if manager_class.__doc__ else ""
                }
                for env_type, manager_class in cls._environment_managers.items()
            },
            "deployments": {
                deploy_type.value: {
                    "name": deploy_type.value.title(),
                    "manager_class": manager_class.__name__,
                    "description": f"Déploiement {deploy_type.value}"
                }
                for deploy_type, manager_class in cls._deployment_managers.items()
            },
            "cloud_providers": [provider.value for provider in CloudProvider]
        }


# Configuration par défaut du système
def get_default_config() -> BaseEnvironmentConfigManager:
    """Retourne la configuration par défaut avec détection automatique"""
    return EnvironmentManagerFactory.create_manager(auto_detect=True)


def create_config_from_env() -> BaseEnvironmentConfigManager:
    """
Crée la configuration à partir des variables d'environnement"""
    env_type_str = os.getenv("ENVIRONMENT", "development").lower()
    deployment_type_str = os.getenv("DEPLOYMENT_TYPE", "local").lower()
    cloud_provider_str = os.getenv("CLOUD_PROVIDER", "aws").lower()
    
    try:
        env_type = EnvironmentType(env_type_str)
    except ValueError:
        env_type = EnvironmentType.DEVELOPMENT
        
    try:
        deployment_type = DeploymentType(deployment_type_str)
    except ValueError:
        deployment_type = DeploymentType.LOCAL
        
    try:
        cloud_provider = CloudProvider(cloud_provider_str)
    except ValueError:
        cloud_provider = CloudProvider.AWS
    
    return EnvironmentManagerFactory.create_manager(
        env_type=env_type,
        deployment_type=deployment_type,
        cloud_provider=cloud_provider,
        auto_detect=False
    )


def validate_all_configurations() -> Dict[str, bool]:
    """Valide toutes les configurations disponibles"""
    results = {}
    
    # Test des environnements standard
    for env_type, manager_class in EnvironmentManagerFactory._environment_managers.items():
        try:
            manager = manager_class()
            manager.load_environment_specific_config()
            results[f"environment_{env_type.value}"] = manager.validate_configuration()
        except Exception as e:
            results[f"environment_{env_type.value}"] = False
            print(f"❌ Erreur validation {env_type.value}: {e}")
            
    # Test des déploiements spécialisés
    specialized_configs = {
        "docker": DockerConfigManager,
        "kubernetes": KubernetesConfigManager,
        "cloud_aws": lambda: CloudConfigManager(CloudProvider.AWS),
        "cloud_azure": lambda: CloudConfigManager(CloudProvider.AZURE),
        "cloud_gcp": lambda: CloudConfigManager(CloudProvider.GCP)
    }
    
    for config_name, config_factory in specialized_configs.items():
        try:
            if callable(config_factory):
                manager = config_factory()
            else:
                manager = config_factory()
            manager.load_environment_specific_config()
            results[f"specialized_{config_name}"] = manager.validate_configuration()
        except Exception as e:
            results[f"specialized_{config_name}"] = False
            print(f"❌ Erreur validation {config_name}: {e}")
            
    return results


# Exports publics
__all__ = [
    # Classes de base
    "BaseEnvironmentConfigManager",
    "EnvironmentType",
    "DeploymentType",
    "CloudProvider",
    
    # Gestionnaires d'environnement
    "DevelopmentConfigManager", 
    "ProductionConfigManager",
    "StagingConfigManager",
    "TestingConfigManager",
    
    # Gestionnaires spécialisés
    "DockerConfigManager",
    "KubernetesConfigManager", 
    "CloudConfigManager",
    
    # Factory et utilitaires
    "EnvironmentManagerFactory",
    "EnvironmentConfigFactory",
    
    # Fonctions utilitaires
    "get_default_config",
    "get_current_environment",
    "load_config_for_environment",
    "create_config_from_env",
    "auto_detect_cloud_provider",
    "validate_all_configurations",
    
    # Fonctions de création rapide
    "create_development_config",
    "create_production_config", 
    "create_staging_config",
    "create_testing_config",
    "create_docker_config",
    "create_kubernetes_config",
    "create_cloud_config",
    
    # Context managers
    "TestEnvironmentContext"
]
