"""Platform Integrations Database Module

Module de base de données pour les intégrations avec les plateformes externes
dans la plateforme IA Influencer Agent.

Ce module fournit une infrastructure complète pour :
- Gestion des connexions aux plateformes (Spotify, YouTube, Instagram, TikTok, etc.)
- Sécurisation et rotation des credentials d'API
- Configuration personnalisable des intégrations
- Synchronisation bidirectionnelle des données
- Monitoring et analytics des services externes
- Gestion des webhooks et événements temps réel

Auteur: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Équipe: Lead AI Developer, Backend Senior, DevOps Engineer, Security Specialist, 
        Database Architect, Platform Integration Specialist

⚠️  AVERTISSEMENT LEGAL ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon le droit allemand et international.

Contact pour autorisation: mlaiel@live.de
"""from typing import List, Dict, Any, Optional, Union
import logging

# Import des modules principaux
from .platform_connections import (
    PlatformConnection, 
    PlatformEndpoint, 
    PlatformWebhook, 
    PlatformSyncLog
)
from .api_credentials import (
    APICredential, 
    CredentialUsageLog, 
    PlatformAPIMapping, 
    CredentialRotationHistory,
    SUPPORTED_PLATFORMS,
    create_platform_credential
)
from .integration_settings import (
    PlatformIntegrationSetting, 
    IntegrationProfile, 
    PlatformCapability, 
    IntegrationHealthCheck,
    IntegrationSettingType,
    IntegrationStatus,
    DEFAULT_PLATFORM_SETTINGS,
    create_default_settings_for_platform
)
from .sync_configurations import (
    SyncConfiguration, 
    SyncExecution, 
    SyncFieldMapping, 
    DataTransformationRule, 
    SyncBenchmark,
    SyncDirection,
    SyncStrategy,
    SyncStatus,
    DEFAULT_SYNC_CONFIGURATIONS,
    create_default_sync_configurations
)
from .external_services import (
    ExternalService, 
    ServiceEndpoint, 
    ServiceIntegration, 
    ServiceDependency, 
    ServiceUsageAnalytics,
    ServiceType,
    ServiceStatus,
    EXTERNAL_SERVICES_CATALOG,
    create_external_service_from_catalog,
    get_services_by_type
)
from .index import (
    PlatformIntegrationManager,
    initialize_platform_integrations_schema,
    get_supported_platforms,
    validate_platform_configuration
)

logger = logging.getLogger(__name__)

# Version du module
__version__ = "2.0.0"

# Modules exportés
__all__ = [
    # Modules de base
    "platform_connections",
    "api_credentials", 
    "integration_settings",
    "sync_configurations",
    "external_services",
    "index",
    
    # Classes principales - Connexions
    "PlatformConnection",
    "PlatformEndpoint", 
    "PlatformWebhook",
    "PlatformSyncLog",
    
    # Classes principales - Credentials
    "APICredential",
    "CredentialUsageLog",
    "PlatformAPIMapping", 
    "CredentialRotationHistory",
    
    # Classes principales - Settings
    "PlatformIntegrationSetting",
    "IntegrationProfile",
    "PlatformCapability",
    "IntegrationHealthCheck",
    
    # Classes principales - Synchronisation
    "SyncConfiguration",
    "SyncExecution",
    "SyncFieldMapping",
    "DataTransformationRule",
    "SyncBenchmark",
    
    # Classes principales - Services externes
    "ExternalService",
    "ServiceEndpoint",
    "ServiceIntegration",
    "ServiceDependency",
    "ServiceUsageAnalytics",
    
    # Enums
    "IntegrationSettingType",
    "IntegrationStatus", 
    "SyncDirection",
    "SyncStrategy",
    "SyncStatus",
    "ServiceType",
    "ServiceStatus",
    
    # Gestionnaire principal
    "PlatformIntegrationManager",
    
    # Utilitaires et fonctions
    "initialize_platform_integrations_schema",
    "get_supported_platforms",
    "validate_platform_configuration",
    "create_platform_credential",
    "create_default_settings_for_platform",
    "create_default_sync_configurations",
    "create_external_service_from_catalog",
    "get_services_by_type",
    
    # Constantes et configurations
    "SUPPORTED_PLATFORMS",
    "DEFAULT_PLATFORM_SETTINGS", 
    "DEFAULT_SYNC_CONFIGURATIONS",
    "EXTERNAL_SERVICES_CATALOG",
    
    # Fonctions utilitaires du module
    "get_module_info",
    "get_module_statistics",
    "validate_module_health"
]


def get_module_info() -> Dict[str, Any]:
    """    Retourne les informations complètes du module Platform Integrations.
    
    Returns:
        Dict[str, Any]: Informations détaillées du module
    """    return {
        "name": "Platform Integrations Database",
        "version": __version__,
        "author": "Fahed Mlaiel",
        "email": "mlaiel@live.de",
        "description": "Base de données complète pour intégrations plateformes externes",
        "modules": [
            "platform_connections",
            "api_credentials", 
            "integration_settings",
            "sync_configurations",
            "external_services"
        ],
        "supported_platforms": list(SUPPORTED_PLATFORMS.keys()),
        "external_services": list(EXTERNAL_SERVICES_CATALOG.keys()),
        "capabilities": [
            "OAuth2 Authentication",
            "API Key Management", 
            "Real-time Synchronization",
            "Bidirectional Data Sync",
            "Webhook Management",
            "Rate Limiting",
            "Health Monitoring",
            "Usage Analytics",
            "Credential Rotation",
            "Error Handling & Retry Logic"
        ],
        "security_features": [
            "Encrypted Credential Storage",
            "Automatic Key Rotation",
            "Access Token Management",
            "Audit Logging",
            "Permission Scoping"
        ]
    }


def get_module_statistics() -> Dict[str, Any]:
    """    Retourne les statistiques du module Platform Integrations.
    
    Returns:
        Dict[str, Any]: Statistiques du module
    """    return {
        "total_models": 19,
        "connection_models": 4,
        "credential_models": 4, 
        "setting_models": 4,
        "sync_models": 5,
        "service_models": 5,
        "enum_types": 7,
        "supported_platforms_count": len(SUPPORTED_PLATFORMS),
        "external_services_count": len(EXTERNAL_SERVICES_CATALOG),
        "default_settings_count": sum(len(settings) for settings in DEFAULT_PLATFORM_SETTINGS.values()),
        "default_sync_configs_count": sum(len(configs) for configs in DEFAULT_SYNC_CONFIGURATIONS.values())
    }


def validate_module_health() -> Dict[str, Any]:
    """    Valide la santé et la cohérence du module Platform Integrations.
    
    Returns:
        Dict[str, Any]: Rapport de santé du module
    """    health_report = {
        "status": "healthy",
        "warnings": [],
        "errors": [],
        "checks": {
            "imports": True,
            "constants": True,
            "configurations": True
        }
    }
    
    try:
        # Vérification des imports
        required_modules = [
            platform_connections, api_credentials, integration_settings,
            sync_configurations, external_services
        ]
        
        # Vérification des constantes
        if not SUPPORTED_PLATFORMS:
            health_report["warnings"].append("SUPPORTED_PLATFORMS est vide")
            
        if not EXTERNAL_SERVICES_CATALOG:
            health_report["warnings"].append("EXTERNAL_SERVICES_CATALOG est vide")
        
        # Vérification des configurations par défaut
        for platform in SUPPORTED_PLATFORMS.keys():
            if platform not in DEFAULT_PLATFORM_SETTINGS:
                health_report["warnings"].append(f"Paramètres par défaut manquants pour {platform}")
                
            if platform not in DEFAULT_SYNC_CONFIGURATIONS:
                health_report["warnings"].append(f"Configurations de sync manquantes pour {platform}")
        
        # Définir le statut global
        if health_report["errors"]:
            health_report["status"] = "critical"
        elif health_report["warnings"]:
            health_report["status"] = "warning"
            
    except Exception as e:
        health_report["status"] = "critical"
        health_report["errors"].append(f"Erreur lors de la validation: {str(e)}")
        health_report["checks"]["imports"] = False
    
    return health_report


# Initialisation du module
logger.info(f"Module Platform Integrations v{__version__} chargé avec succès")
logger.info(f"Plateformes supportées: {list(SUPPORTED_PLATFORMS.keys())}")
logger.info(f"Services externes: {list(EXTERNAL_SERVICES_CATALOG.keys())}")
