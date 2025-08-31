"""🚀 Validation Module Index - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/data_management/validation/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
==================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 INDEX PRINCIPAL DU MODULE DE VALIDATION
Point d'entrée centralisé pour toutes les fonctionnalités de validation
- Imports consolidés
- Configuration centralisée
- Utilité pour tests et intégrations
- Documentation des composants disponibles
"""from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from pathlib import Path

# Import des modules principaux
from .content_validator import (
    ContentValidator,
    AsyncContentValidator,
    ContentValidationResult,
    AudioContentValidator,
    VideoContentValidator,
    ImageContentValidator,
    TextContentValidator
)

from .format_validator import (
    FormatValidator,
    AsyncFormatValidator
)

from .business_validator import (
    BusinessValidator,
    AsyncBusinessValidator
)

from .security_validator import (
    SecurityValidator,
    AsyncSecurityValidator
)

from .fingerprint_validator import (
    FingerprintValidator,
    AsyncFingerprintValidator,
    FingerprintValidationResult,
    FingerprintResult,
    SimilarityMatch,
    FingerprintType,
    AudioFingerprintGenerator,
    VideoFingerprintGenerator,
    ImageFingerprintGenerator,
    TextFingerprintGenerator,
    SimilarityMatcher
)

from .quality_assessor import (
    QualityAssessor,
    AsyncQualityAssessor,
    QualityAssessmentResult,
    QualityScore,
    QualityDimension,
    QualityLevel,
    AudioQualityAnalyzer,
    VideoQualityAnalyzer
)

from .metadata_extractor import (
    MetadataExtractor,
    AsyncMetadataExtractor,
    ContentMetadata,
    TechnicalMetadata,
    MediaDimensions,
    CreativeMetadata,
    BusinessMetadata,
    GeolocationData,
    ImageMetadataExtractor,
    AudioMetadataExtractor,
    VideoMetadataExtractor,
    TextMetadataExtractor
)

from .compliance_checker import (
    ComplianceChecker,
    AsyncComplianceChecker,
    ComplianceResult,
    ComplianceIssue,
    ComplianceLevel,
    ComplianceCategory,
    JurisdictionType,
    PrivacyComplianceChecker,
    CopyrightComplianceChecker,
    PlatformPolicyChecker
)

from .workflow_validator import (
    WorkflowValidator,
    WorkflowOrchestrator,
    WorkflowResult,
    WorkflowConfiguration,
    WorkflowStepResult,
    WorkflowStep,
    WorkflowStatus,
    CreatorType
)

from .rules_engine import (
    RulesEngine,
    AsyncRulesEngine,
    RuleSetManager,
    RuleEvaluator,
    ValidationRule,
    RulesEvaluationResult,
    RuleEvaluationResult,
    RuleType,
    RuleOperator,
    RuleCondition,
    RuleSeverity
)

from .metrics import (
    ValidationMetrics,
    MetricsCollector,
    MetricsAnalyzer,
    MetricsDashboard,
    ValidationMetric,
    ValidationEvent,
    MetricSummary,
    MetricType,
    AggregationType,
    validation_metrics
)

# Import du gestionnaire principal
from . import (
    ValidationManager,
    ValidationConfig,
    ValidationResult,
    ValidationLevel,
    validation_manager
)

logger = logging.getLogger(__name__)

class ValidationModuleInfo:
    """Informations sur le module de validation"""    
    @staticmethod
    def get_module_info() -> Dict[str, Any]:
        """Retourne les informations du module"""        return {
            "name": "Data Management Validation Module",
            "version": "1.0.0",
            "author": "Fahed Mlaiel",
            "email": "mlaiel@live.de",
            "description": "Enterprise validation system for multi-format content supporting musicians, influencers, photographers, bloggers, and comedians",
            "components": {
                "content_validator": "Advanced multimedia content analysis",
                "format_validator": "File format validation and integrity",
                "business_validator": "Business rules and creator quotas",
                "security_validator": "Security and malware scanning",
                "fingerprint_validator": "AI fingerprinting validation",
                "quality_assessor": "Content quality assessment",
                "metadata_extractor": "Advanced metadata extraction",
                "compliance_checker": "Legal and platform compliance",
                "workflow_validator": "Multi-step workflow validation",
                "rules_engine": "Dynamic validation rules engine",
                "metrics": "Validation metrics and analytics"
            },
            "supported_formats": {
                "audio": ["mp3", "wav", "flac", "ogg", "m4a", "aiff"],
                "video": ["mp4", "avi", "mov", "mkv", "webm"],
                "image": ["jpg", "jpeg", "png", "gif", "webp", "tiff", "raw"],
                "text": ["txt", "md", "html", "pdf", "docx", "rtf"]
            },
            "creator_types": ["musician", "influencer", "photographer", "blogger", "comedian"],
            "validation_levels": ["basic", "standard", "strict", "enterprise"]
        }
    
    @staticmethod
    def get_available_validators() -> List[str]:
        """Retourne la liste des validateurs disponibles"""        return [
            "ContentValidator",
            "FormatValidator", 
            "BusinessValidator",
            "SecurityValidator",
            "FingerprintValidator",
            "QualityAssessor",
            "MetadataExtractor",
            "ComplianceChecker",
            "WorkflowValidator",
            "RulesEngine"
        ]
    
    @staticmethod
    def get_component_dependencies() -> Dict[str, List[str]]:
        """Retourne les dépendances entre composants"""        return {
            "ValidationManager": [
                "ContentValidator",
                "FormatValidator",
                "BusinessValidator", 
                "SecurityValidator"
            ],
            "WorkflowValidator": [
                "ContentValidator",
                "FingerprintValidator",
                "QualityAssessor",
                "ComplianceChecker"
            ],
            "QualityAssessor": [
                "MetadataExtractor"
            ],
            "ValidationMetrics": [
                "All validators"
            ]
        }

def create_validation_suite(
    config: Optional[ValidationConfig] = None,
    enable_async: bool = True,
    enable_metrics: bool = True,
    enable_caching: bool = True
) -> Dict[str, Any]:
    """Crée une suite de validation complète configurée"""    
    # Configuration par défaut si non fournie
    if config is None:
        config = ValidationConfig()
    
    # Initialisation des composants principaux
    suite = {
        "config": config,
        "sync_validators": {},
        "async_validators": {},
        "metrics": None,
        "enabled_features": {
            "async": enable_async,
            "metrics": enable_metrics,
            "caching": enable_caching
        }
    }
    
    # Validateurs synchrones
    suite["sync_validators"] = {
        "main": ValidationManager(config),
        "content": ContentValidator(),
        "format": FormatValidator(),
        "business": BusinessValidator(config),
        "security": SecurityValidator(),
        "fingerprint": FingerprintValidator(),
        "quality": QualityAssessor(),
        "metadata": MetadataExtractor(),
        "compliance": ComplianceChecker(),
        "workflow": WorkflowValidator(),
        "rules": RulesEngine()
    }
    
    # Validateurs asynchrones
    if enable_async:
        suite["async_validators"] = {
            "content": AsyncContentValidator(),
            "format": AsyncFormatValidator(),
            "business": AsyncBusinessValidator(config),
            "security": AsyncSecurityValidator(),
            "fingerprint": AsyncFingerprintValidator(),
            "quality": AsyncQualityAssessor(),
            "metadata": AsyncMetadataExtractor(),
            "compliance": AsyncComplianceChecker(),
            "rules": AsyncRulesEngine()
        }
    
    # Système de métriques
    if enable_metrics:
        suite["metrics"] = ValidationMetrics()
    
    logger.info("Suite de validation créée avec succès")
    return suite

def validate_file_comprehensive(
    file_path: str,
    creator_type: str,
    content_type: str,
    validation_level: ValidationLevel = ValidationLevel.STANDARD,
    enable_fingerprinting: bool = True,
    enable_quality_assessment: bool = True,
    enable_compliance_check: bool = True
) -> Dict[str, Any]:
    """Validation complète d'un fichier avec tous les composants"""    
    results = {
        "file_path": file_path,
        "creator_type": creator_type,
        "content_type": content_type,
        "validation_level": validation_level.value,
        "timestamp": Path(file_path).stat().st_mtime if Path(file_path).exists() else None,
        "results": {},
        "overall_valid": True,
        "summary": {}
    }
    
    try:
        # Validation principale
        main_validator = ValidationManager()
        main_result = main_validator.validate_file(file_path, creator_type, content_type, validation_level)
        results["results"]["main_validation"] = {
            "is_valid": main_result.is_valid,
            "score": main_result.score,
            "errors": main_result.errors,
            "warnings": main_result.warnings,
            "metadata": main_result.metadata
        }
        
        if not main_result.is_valid:
            results["overall_valid"] = False
        
        # Fingerprinting (si activé)
        if enable_fingerprinting:
            fingerprint_validator = FingerprintValidator()
            fingerprint_result = fingerprint_validator.validate_fingerprint(file_path, content_type)
            results["results"]["fingerprinting"] = {
                "is_unique": fingerprint_result.is_unique,
                "quality": fingerprint_result.fingerprint_quality,
                "duplicates": len(fingerprint_result.duplicate_matches),
                "similar": len(fingerprint_result.similar_matches)
            }
        
        # Évaluation qualité (si activée)
        if enable_quality_assessment:
            quality_assessor = QualityAssessor()
            quality_result = quality_assessor.assess_content_quality(file_path, content_type, creator_type)
            results["results"]["quality_assessment"] = {
                "overall_score": quality_result.overall_score,
                "overall_level": quality_result.overall_level.value,
                "dimension_scores": {
                    dim.value: score.score 
                    for dim, score in quality_result.dimension_scores.items()
                },
                "improvements": quality_result.improvement_suggestions
            }
        
        # Vérification conformité (si activée)
        if enable_compliance_check:
            compliance_checker = ComplianceChecker()
            compliance_result = compliance_checker.check_compliance(file_path, content_type)
            results["results"]["compliance"] = {
                "overall_compliant": compliance_result.overall_compliant,
                "compliance_score": compliance_result.compliance_score,
                "issues": [
                    {
                        "category": issue.category.value,
                        "severity": issue.severity.value,
                        "description": issue.description
                    }
                    for issue in compliance_result.issues
                ]
            }
            
            if not compliance_result.overall_compliant:
                results["overall_valid"] = False
        
        # Résumé global
        results["summary"] = {
            "validation_score": main_result.score,
            "quality_score": results["results"].get("quality_assessment", {}).get("overall_score", 0.0),
            "compliance_score": results["results"].get("compliance", {}).get("compliance_score", 1.0),
            "uniqueness": results["results"].get("fingerprinting", {}).get("is_unique", True),
            "recommendation": _get_overall_recommendation(results)
        }
        
    except Exception as e:
        logger.error(f"Erreur validation complète {file_path}: {e}")
        results["overall_valid"] = False
        results["error"] = str(e)
    
    return results

def _get_overall_recommendation(results: Dict[str, Any]) -> str:
    """Génère une recommandation globale basée sur tous les résultats"""    
    if not results["overall_valid"]:
        return "REJECTED - Does not meet validation criteria"
    
    summary = results.get("summary", {})
    validation_score = summary.get("validation_score", 0.0)
    quality_score = summary.get("quality_score", 0.0)
    compliance_score = summary.get("compliance_score", 1.0)
    is_unique = summary.get("uniqueness", True)
    
    # Score combiné
    combined_score = (validation_score + quality_score + compliance_score) / 3.0
    
    if not is_unique:
        return "REJECTED - Duplicate content detected"
    elif combined_score >= 0.9:
        return "EXCELLENT - Ready for professional distribution"
    elif combined_score >= 0.7:
        return "GOOD - Suitable for publication with minor improvements"
    elif combined_score >= 0.5:
        return "FAIR - Needs improvement before publication"
    else:
        return "POOR - Significant improvements required"

def get_validation_statistics() -> Dict[str, Any]:
    """Retourne les statistiques de validation du module"""    try:
        metrics = validation_metrics
        dashboard = metrics.get_real_time_dashboard()
        
        return {
            "module_info": ValidationModuleInfo.get_module_info(),
            "real_time_stats": dashboard,
            "available_validators": ValidationModuleInfo.get_available_validators(),
            "component_dependencies": ValidationModuleInfo.get_component_dependencies()
        }
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {e}")
        return {
            "module_info": ValidationModuleInfo.get_module_info(),
            "error": str(e)
        }

# Configuration par défaut du module
DEFAULT_MODULE_CONFIG = {
    "enable_all_validators": True,
    "enable_async": True,
    "enable_metrics": True,
    "enable_caching": True,
    "default_validation_level": "standard",
    "auto_fingerprinting": True,
    "auto_quality_assessment": True,
    "auto_compliance_check": True
}

# Export consolidé
__all__ = [
    # Validateurs principaux
    "ContentValidator", "AsyncContentValidator",
    "FormatValidator", "AsyncFormatValidator", 
    "BusinessValidator", "AsyncBusinessValidator",
    "SecurityValidator", "AsyncSecurityValidator",
    "FingerprintValidator", "AsyncFingerprintValidator",
    "QualityAssessor", "AsyncQualityAssessor",
    "MetadataExtractor", "AsyncMetadataExtractor",
    "ComplianceChecker", "AsyncComplianceChecker",
    "WorkflowValidator",
    "RulesEngine", "AsyncRulesEngine",
    "ValidationMetrics",
    
    # Gestionnaire principal
    "ValidationManager", "ValidationConfig", "ValidationResult", "ValidationLevel",
    "validation_manager",
    
    # Types et résultats
    "ContentValidationResult",
    "FingerprintValidationResult", "FingerprintResult", "SimilarityMatch",
    "QualityAssessmentResult", "QualityScore", "QualityDimension", "QualityLevel",
    "ContentMetadata", "TechnicalMetadata", "CreativeMetadata",
    "ComplianceResult", "ComplianceIssue",
    "WorkflowResult", "WorkflowConfiguration",
    "RulesEvaluationResult", "ValidationRule",
    "ValidationMetric", "ValidationEvent",
    
    # Enums
    "FingerprintType", "ComplianceLevel", "ComplianceCategory",
    "WorkflowStatus", "CreatorType", "RuleType", "RuleOperator",
    "MetricType", "AggregationType",
    
    # Utilitaires du module
    "ValidationModuleInfo",
    "create_validation_suite",
    "validate_file_comprehensive", 
    "get_validation_statistics",
    "DEFAULT_MODULE_CONFIG"
]

# Initialisation du module
logger.info("Module de validation initialisé - IA Influencer Agent Platform Enterprise")
logger.info(f"Auteur: Fahed Mlaiel (mlaiel@live.de)")
logger.info(f"Composants disponibles: {len(__all__)} classes et fonctions")
