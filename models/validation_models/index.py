"""
🧪 VALIDATION MODELS INDEX - ENTERPRISE GRADE
============================================

Point d'entrée central pour tous les modèles Validation Enterprise
Support complet: QA, Testing, Schema Validation, Performance, Compliance

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Architecture: Enterprise Validation Models with advanced QA patterns
"""

from .base_validation_model import BaseValidationModel
from .schema_validation_model import SchemaValidationModel
from .data_validation_model import DataValidationModel
from .quality_assurance_model import QualityAssuranceModel
from .testing_model import TestingModel
from .performance_validation_model import PerformanceValidationModel
from .security_validation_model import SecurityValidationModel
from .business_validation_model import BusinessValidationModel
from .compliance_validation_model import ComplianceValidationModel
from .metrics_validation_model import MetricsValidationModel
from .integration_validation_model import IntegrationValidationModel
from .error_handling_model import ErrorHandlingModel

# Enterprise Validation Models Collection
__all__ = [
    # Core Validation Models
    'BaseValidationModel',
    'SchemaValidationModel',
    'DataValidationModel',
    'QualityAssuranceModel',
    
    # Testing & Performance
    'TestingModel',
    'PerformanceValidationModel',
    'ErrorHandlingModel',
    
    # Security & Compliance
    'SecurityValidationModel',
    'ComplianceValidationModel',
    
    # Business & Integration
    'BusinessValidationModel',
    'MetricsValidationModel',
    'IntegrationValidationModel',
]

# Enterprise Validation Registry
VALIDATION_MODELS_REGISTRY = {
    'core': {
        'base': BaseValidationModel,
        'schema': SchemaValidationModel,
        'data': DataValidationModel,
        'quality': QualityAssuranceModel,
    },
    'testing': {
        'testing': TestingModel,
        'performance': PerformanceValidationModel,
        'errors': ErrorHandlingModel,
    },
    'security': {
        'security': SecurityValidationModel,
        'compliance': ComplianceValidationModel,
    },
    'business': {
        'business': BusinessValidationModel,
        'metrics': MetricsValidationModel,
        'integration': IntegrationValidationModel,
    }
}

def get_validation_model(category: str, model_type: str):
    """
    Récupère un modèle Validation Enterprise par catégorie et type
    
    Args:
        category: core, testing, security, business
        model_type: Type spécifique de modèle validation
        
    Returns:
        Classe du modèle Validation Enterprise correspondant
    """
    return VALIDATION_MODELS_REGISTRY.get(category, {}).get(model_type)

def list_available_validation_models():
    """Liste tous les modèles Validation Enterprise disponibles"""
    return VALIDATION_MODELS_REGISTRY

# Validation Models Enterprise Stats
VALIDATION_MODELS_STATS = {
    'total_models': 12,
    'categories': 4,
    'core_models': 4,
    'testing_models': 3,
    'security_models': 2,
    'business_models': 3,
    'enterprise_ready': True,
    'automated_testing': True,
    'quality_assurance': True,
    'compliance_checking': True,
    'error_handling': True
}