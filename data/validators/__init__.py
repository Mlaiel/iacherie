"""Data Validators Module - Industrial-Grade Validation System
===========================================================

Comprehensive validation framework for the IA Influencer Agent Platform
providing enterprise-level data integrity, security, and compliance validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Validation Capabilities:
- Multi-format content validation (audio, video, image, text)
- Schema and data structure validation
- Security and safety validation
- Business rule enforcement
- Quality assessment and scoring
- Platform compliance checking
- Performance validation
- Metadata validation
"""
from .content_validator import (
    ContentValidator,
    ContentType,
    ValidationLevel,
    ValidationStatus,
    ContentMetadata,
    ValidationResult,
    ValidationIssue
)

from .schema_validator import (
    SchemaValidator,
    SchemaType,
    SchemaValidationResult,
    PydanticValidator,
    JSONSchemaValidator
)

from .security_validator import (
    SecurityValidator,
    SecurityThreat,
    SecurityLevel,
    SecurityValidationResult,
    ThreatDetector,
    InputSanitizer
)

from .business_validator import (
    BusinessValidator,
    BusinessRule,
    BusinessRuleResult,
    CreatorProfileValidator,
    ContentLicensingValidator,
    MonetizationValidator
)

from .file_validator import (
    FileValidator,
    FileIntegrityResult,
    FileSignatureValidator,
    ChecksumValidator,
    CompressionValidator
)

from .metadata_validator import (
    MetadataValidator,
    MetadataStandard,
    MetadataValidationResult,
    ID3Validator,
    EXIFValidator,
    XMPValidator
)

from .quality_validator import (
    QualityValidator,
    QualityMetrics,
    QualityAssessmentResult,
    AudioQualityAnalyzer,
    VideoQualityAnalyzer,
    ImageQualityAnalyzer
)

from .compliance_validator import (
    ComplianceValidator,
    ComplianceStandard,
    ComplianceResult,
    PlatformComplianceChecker,
    LegalComplianceValidator
)

from .performance_validator import (
    PerformanceValidator,
    PerformanceMetrics,
    PerformanceResult,
    BenchmarkValidator,
    OptimizationValidator
)

from .chain_validator import (
    ChainValidator,
    ValidationChain,
    ChainResult,
    ValidationStep,
    ValidationPipeline
)

from .index import (
    ValidationEngine,
    ValidatorRegistry,
    ValidationManager,
    ValidationConfig
)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Main validation engine instance
validation_engine = ValidationEngine()

# Public API exports
__all__ = [
    # Core validators
    "ContentValidator",
    "SchemaValidator", 
    "SecurityValidator",
    "BusinessValidator",
    "FileValidator",
    "MetadataValidator",
    "QualityValidator",
    "ComplianceValidator",
    "PerformanceValidator",
    "ChainValidator",
    
    # Validation engine
    "ValidationEngine",
    "ValidatorRegistry",
    "ValidationManager",
    "ValidationConfig",
    "validation_engine",
    
    # Types and enums
    "ContentType",
    "ValidationLevel",
    "ValidationStatus",
    "SchemaType", 
    "SecurityThreat",
    "SecurityLevel",
    "BusinessRule",
    "MetadataStandard",
    "ComplianceStandard",
    
    # Result classes
    "ValidationResult",
    "ValidationIssue",
    "SchemaValidationResult",
    "SecurityValidationResult",
    "BusinessRuleResult",
    "FileIntegrityResult",
    "MetadataValidationResult",
    "QualityAssessmentResult",
    "ComplianceResult",
    "PerformanceResult",
    "ChainResult",
    
    # Specialized components
    "ContentMetadata",
    "QualityMetrics",
    "PerformanceMetrics",
    "ValidationChain",
    "ValidationStep",
    "ValidationPipeline",
    "ThreatDetector",
    "InputSanitizer",
    "PydanticValidator",
    "JSONSchemaValidator",
    "CreatorProfileValidator",
    "ContentLicensingValidator",
    "MonetizationValidator",
    "FileSignatureValidator",
    "ChecksumValidator",
    "CompressionValidator",
    "ID3Validator",
    "EXIFValidator",
    "XMPValidator",
    "AudioQualityAnalyzer",
    "VideoQualityAnalyzer",
    "ImageQualityAnalyzer",
    "PlatformComplianceChecker",
    "LegalComplianceValidator",
    "BenchmarkValidator",
    "OptimizationValidator",
    
    # Version info
    "__version__",
    "__author__",
    "__email__"
]

# Module-level configuration
DEFAULT_CONFIG = {
    "strict_mode": True,
    "cache_enabled": True,
    "parallel_processing": True,
    "max_workers": 4,
    "timeout": 30,
    "log_level": "INFO"
}

def configure_validators(config: dict = None) -> None:
    """    Configure global validator settings.
    
    Args:
        config: Configuration dictionary
    """    global validation_engine
    if config:
        validation_engine.update_config(config)

def get_validator_info() -> dict:
    """    Get information about available validators.
    
    Returns:
        Dictionary with validator information
    """    return {
        "version": __version__,
        "author": __author__,
        "validators": list(validation_engine.registry.get_available_validators()),
        "config": validation_engine.config.dict()
    }