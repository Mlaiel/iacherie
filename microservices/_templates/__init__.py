#!/usr/bin/env python3
"""
🏗️ Enterprise Microservices Templates - Ainflue
==============================================
Templates standardisés pour création microservices enterprise.
Support patterns avancés + observability + resilience.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Microservices
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture microservices et tous ses templates sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, 
distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice avec la PLEINE RIGUEUR de la loi.
"""

from typing import Dict, Type, Optional, List
import logging

# Core base template
from .service_template import EnterpriseServiceBase, ServiceConfig

# Import all specialized templates
try:
    from .api_service_template import APIServiceTemplate
except ImportError:
    APIServiceTemplate = None

try:
    from .message_service_template import MessageServiceTemplate
except ImportError:
    MessageServiceTemplate = None

try:
    from .data_service_template import DataServiceTemplate
except ImportError:
    DataServiceTemplate = None

try:
    from .ml_service_template import MLServiceTemplate
except ImportError:
    MLServiceTemplate = None

try:
    from .authentication_service_template import AuthServiceTemplate
except ImportError:
    AuthServiceTemplate = None

try:
    from .monitoring_service_template import MonitoringServiceTemplate
except ImportError:
    MonitoringServiceTemplate = None

try:
    from .notification_service_template import NotificationServiceTemplate
except ImportError:
    NotificationServiceTemplate = None

try:
    from .file_service_template import FileServiceTemplate
except ImportError:
    FileServiceTemplate = None

try:
    from .cache_service_template import CacheServiceTemplate
except ImportError:
    CacheServiceTemplate = None

try:
    from .workflow_service_template import WorkflowServiceTemplate
except ImportError:
    WorkflowServiceTemplate = None

try:
    from .integration_service_template import IntegrationServiceTemplate
except ImportError:
    IntegrationServiceTemplate = None

# Utility templates
try:
    from .testing_service_template import TestingServiceTemplate
except ImportError:
    TestingServiceTemplate = None

try:
    from .deployment_service_template import DeploymentServiceTemplate
except ImportError:
    DeploymentServiceTemplate = None

try:
    from .documentation_service_template import DocumentationServiceTemplate
except ImportError:
    DocumentationServiceTemplate = None

try:
    from .configuration_service_template import ConfigurationServiceTemplate
except ImportError:
    ConfigurationServiceTemplate = None

try:
    from .logging_service_template import LoggingServiceTemplate
except ImportError:
    LoggingServiceTemplate = None

# Export core components
__all__ = [
    'EnterpriseServiceBase',
    'ServiceConfig',
    'TEMPLATES_REGISTRY',
    'get_template',
    'get_available_templates',
    'TemplateFactory'
]

# Set up logging
logger = logging.getLogger(__name__)

# Templates registry pour auto-discovery
TEMPLATES_REGISTRY: Dict[str, Type[EnterpriseServiceBase]] = {
    'base': EnterpriseServiceBase,
}

# Register available templates
if APIServiceTemplate:
    TEMPLATES_REGISTRY['api'] = APIServiceTemplate
if MessageServiceTemplate:
    TEMPLATES_REGISTRY['messaging'] = MessageServiceTemplate
if DataServiceTemplate:
    TEMPLATES_REGISTRY['data'] = DataServiceTemplate
if MLServiceTemplate:
    TEMPLATES_REGISTRY['ml'] = MLServiceTemplate
if AuthServiceTemplate:
    TEMPLATES_REGISTRY['auth'] = AuthServiceTemplate
if MonitoringServiceTemplate:
    TEMPLATES_REGISTRY['monitoring'] = MonitoringServiceTemplate
if NotificationServiceTemplate:
    TEMPLATES_REGISTRY['notification'] = NotificationServiceTemplate
if FileServiceTemplate:
    TEMPLATES_REGISTRY['file'] = FileServiceTemplate
if CacheServiceTemplate:
    TEMPLATES_REGISTRY['cache'] = CacheServiceTemplate
if WorkflowServiceTemplate:
    TEMPLATES_REGISTRY['workflow'] = WorkflowServiceTemplate
if IntegrationServiceTemplate:
    TEMPLATES_REGISTRY['integration'] = IntegrationServiceTemplate
if TestingServiceTemplate:
    TEMPLATES_REGISTRY['testing'] = TestingServiceTemplate
if DeploymentServiceTemplate:
    TEMPLATES_REGISTRY['deployment'] = DeploymentServiceTemplate
if DocumentationServiceTemplate:
    TEMPLATES_REGISTRY['documentation'] = DocumentationServiceTemplate
if ConfigurationServiceTemplate:
    TEMPLATES_REGISTRY['configuration'] = ConfigurationServiceTemplate
if LoggingServiceTemplate:
    TEMPLATES_REGISTRY['logging'] = LoggingServiceTemplate


def get_template(template_type: str) -> Optional[Type[EnterpriseServiceBase]]:
    """
    Factory pour récupérer template par type.
    
    Args:
        template_type: Type de template ('api', 'messaging', 'data', etc.)
    
    Returns:
        Classe du template ou None si non trouvé
    """
    template_class = TEMPLATES_REGISTRY.get(template_type.lower())
    if not template_class:
        logger.warning(f"Template '{template_type}' not found in registry. Available: {list(TEMPLATES_REGISTRY.keys())}")
    return template_class


def get_available_templates() -> List[str]:
    """
    Récupère la liste des templates disponibles.
    
    Returns:
        Liste des noms de templates disponibles
    """
    return list(TEMPLATES_REGISTRY.keys())


class TemplateFactory:
    """
    🏭 Factory enterprise pour création templates microservices.
    Patterns avancés + validation + observability intégrée.
    """
    
    @staticmethod
    def create_service(template_type: str, config: ServiceConfig) -> Optional[EnterpriseServiceBase]:
        """
        Création service depuis template avec validation.
        
        Args:
            template_type: Type de template à utiliser
            config: Configuration du service
        
        Returns:
            Instance du service ou None si erreur
        """
        try:
            template_class = get_template(template_type)
            if not template_class:
                logger.error(f"Template '{template_type}' not available")
                return None
            
            # Validation de la configuration
            if not isinstance(config, ServiceConfig):
                logger.error("Invalid service configuration provided")
                return None
            
            # Création de l'instance
            service_instance = template_class(config)
            logger.info(f"✅ Service created successfully: {config.service_name} ({template_type})")
            
            return service_instance
            
        except Exception as e:
            logger.error(f"❌ Failed to create service '{config.service_name}' with template '{template_type}': {e}")
            return None
    
    @staticmethod
    def validate_config(config: ServiceConfig) -> bool:
        """
        Validation configuration template.
        
        Args:
            config: Configuration à valider
        
        Returns:
            True si configuration valide
        """
        try:
            if not config.service_name:
                logger.error("Service name is required")
                return False
            
            if not config.service_version:
                logger.error("Service version is required")
                return False
            
            if config.port <= 0 or config.port > 65535:
                logger.error("Port must be between 1 and 65535")
                return False
            
            if config.health_check_interval <= 0:
                logger.error("Health check interval must be positive")
                return False
            
            logger.info(f"✅ Configuration validation passed for service: {config.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            return False
    
    @staticmethod
    def get_template_info(template_type: str) -> Optional[Dict]:
        """
        Récupère informations sur un template.
        
        Args:
            template_type: Type de template
        
        Returns:
            Dictionnaire avec informations du template
        """
        template_class = get_template(template_type)
        if not template_class:
            return None
        
        return {
            'name': template_type,
            'class': template_class.__name__,
            'module': template_class.__module__,
            'doc': template_class.__doc__ or "No documentation available"
        }


# Log initialization
logger.info(f"🏗️ Ainflue Microservices Templates initialized - {len(TEMPLATES_REGISTRY)} templates available")
logger.info(f"📋 Available templates: {', '.join(get_available_templates())}")