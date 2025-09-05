"""Data Validators Module - Industrial-Grade Validation System
===========================================================

Comprehensive validation framework for the IA Influencer Agent Platform
providing enterprise-level data integrity, security, and compliance validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Validation Capabilities:
- Multi-format content validation (audio, video, image, text)
- Integrated schema and metadata validation
- Combined security and compliance validation
- Business logic and quality assessment
- File integrity and performance monitoring
- Orchestrated validation chains
"""

# Import from original content validator (unchanged)
from .content_validator import (
    ContentValidator,
    ContentType,
    ValidationLevel,
    ValidationStatus,
    ContentMetadata,
    ValidationResult,
    ValidationIssue
)

# Import from consolidated security & compliance validator
from .security_compliance_validator import (
    SecurityComplianceValidator,
    SecurityLevel,
    ThreatType,
    ComplianceFramework,
    PlatformPolicy,
    ComplianceStatus,
    SecurityThreat,
    SecurityValidationResult,
    ComplianceViolation,
    ComplianceValidationResult,
    validate_security,
    validate_compliance
)

# Import from consolidated business & quality validator
from .business_quality_validator import (
    BusinessQualityValidator,
    BusinessRuleType,
    RuleSeverity,
    ValidationContext,
    QualityDimension,
    QualityMetric,
    QualityLevel,
    BusinessRule,
    BusinessValidationResult,
    QualityScore,
    QualityValidationResult,
    validate_business_rules,
    assess_content_quality
)

# Import from consolidated schema & metadata validator
from .schema_metadata_validator import (
    SchemaMetadataValidator,
    ValidationLevel as SchemaValidationLevel,
    SchemaType,
    ValidationStatus as SchemaValidationStatus,
    MetadataFormat,
    MetadataQuality,
    MetadataValidationType,
    SchemaValidationError,
    SchemaValidationResult,
    MetadataField,
    MetadataValidationIssue,
    MetadataValidationResult,
    CreatorProfile,
    ContentMetadata as SchemaContentMetadata,
    PlatformConfiguration,
    validate_schema,
    extract_metadata
)

# Import from consolidated file & performance validator
from .file_performance_validator import (
    FilePerformanceValidator,
    FileValidationType,
    ValidationSeverity,
    FileStatus,
    PerformanceMetricType,
    PerformanceLevel,
    OptimizationType,
    FileValidationIssue,
    FileValidationResult,
    PerformanceMetric,
    PerformanceIssue,
    PerformanceValidationResult,
    validate_file,
    assess_performance
)

# Import from renamed validation chain
from .validation_chain import (
    ChainValidator,
    ValidationChain,
    ChainResult,
    ValidationStep,
    ValidationPipeline
)

# Import from renamed validation index
from .validation_index import (
    ValidationEngine,
    ValidatorRegistry,
    ValidationManager,
    ValidationConfig
)

# Version information
__version__ = "2.0.0"  # Updated for consolidated architecture
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Main validation engine instance
validation_engine = ValidationEngine()

# Public API exports - Updated for consolidated architecture
__all__ = [
    # Core consolidated validators
    "ContentValidator",
    "SecurityComplianceValidator", 
    "BusinessQualityValidator",
    "SchemaMetadataValidator",
    "FilePerformanceValidator",
    "ChainValidator",
    
    # Validation engine
    "ValidationEngine",
    "ValidatorRegistry",
    "ValidationManager",
    "ValidationConfig",
    "validation_engine",
    
    # Types and enums - Core
    "ContentType",
    "ValidationLevel",
    "ValidationStatus",
    
    # Types and enums - Security & Compliance
    "SecurityLevel",
    "ThreatType",
    "ComplianceFramework",
    "PlatformPolicy",
    "ComplianceStatus",
    
    # Types and enums - Business & Quality
    "BusinessRuleType",
    "RuleSeverity",
    "ValidationContext",
    "QualityDimension",
    "QualityMetric",
    "QualityLevel",
    
    # Types and enums - Schema & Metadata
    "SchemaType",
    "MetadataFormat",
    "MetadataQuality",
    "MetadataValidationType",
    
    # Types and enums - File & Performance
    "FileValidationType",
    "ValidationSeverity",
    "FileStatus",
    "PerformanceMetricType",
    "PerformanceLevel",
    "OptimizationType",
    
    # Result classes - Core
    "ValidationResult",
    "ValidationIssue",
    "ContentMetadata",
    
    # Result classes - Security & Compliance
    "SecurityThreat",
    "SecurityValidationResult",
    "ComplianceViolation",
    "ComplianceValidationResult",
    
    # Result classes - Business & Quality
    "BusinessRule",
    "BusinessValidationResult",
    "QualityScore",
    "QualityValidationResult",
    
    # Result classes - Schema & Metadata
    "SchemaValidationError",
    "SchemaValidationResult",
    "MetadataField",
    "MetadataValidationIssue",
    "MetadataValidationResult",
    "CreatorProfile",
    "PlatformConfiguration",
    
    # Result classes - File & Performance
    "FileValidationIssue",
    "FileValidationResult",
    "PerformanceMetric",
    "PerformanceIssue",
    "PerformanceValidationResult",
    
    # Chain components
    "ValidationChain",
    "ChainResult",
    "ValidationStep",
    "ValidationPipeline",
    
    # Convenience functions
    "validate_security",
    "validate_compliance",
    "validate_business_rules",
    "assess_content_quality",
    "validate_schema",
    "extract_metadata",
    "validate_file",
    "assess_performance",
    
    # Version info
    "__version__",
    "__author__",
    "__email__"
]

# Module-level configuration - Updated for consolidated architecture
DEFAULT_CONFIG = {
    "strict_mode": True,
    "cache_enabled": True,
    "parallel_processing": True,
    "max_workers": 4,
    "timeout": 30,
    "log_level": "INFO",
    "consolidated_architecture": True,
    "ai_enhancement": True,
    "auto_optimization": True
}

def configure_validators(config: dict = None) -> None:
    """
    Configure global validator settings for consolidated architecture.
    
    Args:
        config: Configuration dictionary
    """
    global validation_engine
    if config:
        validation_engine.update_config(config)

def get_validator_info() -> dict:
    """
    Get information about available consolidated validators.
    
    Returns:
        Dictionary with validator information
    """
    return {
        "version": __version__,
        "author": __author__,
        "architecture": "consolidated",
        "total_files": 12,  # After consolidation
        "consolidated_validators": [
            "SecurityComplianceValidator",
            "BusinessQualityValidator", 
            "SchemaMetadataValidator",
            "FilePerformanceValidator"
        ],
        "unchanged_validators": [
            "ContentValidator"
        ],
        "renamed_components": [
            "validation_chain (formerly chain_validator)",
            "validation_index (formerly index)"
        ],
        "config": validation_engine.config.dict() if hasattr(validation_engine, 'config') else DEFAULT_CONFIG
    }