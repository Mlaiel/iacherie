"""🚀 Model Registry Module - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/model_registry/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE MODEL REGISTRY
Gestion complète du cycle de vie des modèles ML
- MLflow registry avec versioning automatique
- Model promotion et deployment tracking
- Rollback et A/B testing support
- Metadata et lineage management
"""

from .mlflow_registry import (
    MLflowModelRegistry,
    ModelRegistryConfig,
    ModelMetadata,
    DeploymentInfo,
    ModelStage,
    RegistryStatus,
    ModelRegistryFactory
)

from .model_version_controller import (
    ModelVersionController,
    VersionInfo,
    VersionControlConfig,
    VersionOperation
)

from .model_encryption_manager import (
    ModelEncryptionManager,
    EncryptionLevel,
    KeyType,
    EncryptionConfig,
    SecurityMetrics
)

from .model_access_controller import (
    ModelAccessController,
    Permission,
    Role,
    AccessLevel,
    User,
    AccessRequest,
    AuditLog
)

from .model_compliance_validator import (
    ModelComplianceValidator,
    ComplianceStandard,
    ComplianceLevel,
    ViolationType,
    ComplianceRule,
    ComplianceViolation,
    ComplianceAssessment,
    ModelMetadata as ComplianceModelMetadata
)

from .model_bias_detector import (
    ModelBiasDetector,
    BiasType,
    ProtectedAttribute,
    BiasLevel,
    FairnessMetric,
    BiasTestResult,
    CreatorBiasAnalysis,
    BiasAssessment,
    ModelPrediction
)

# NEW PHASE 15 MODULES - Model Lifecycle Management
from .model_performance_tracker import (
    ModelPerformanceTracker,
    PerformanceMetric as RegistryPerformanceMetric,
    ModelPerformanceSnapshot,
    PerformanceTrend,
    DegradationAlert,
    PerformanceStatus,
    TrackerConfig,
    create_model_performance_tracker
)

from .model_format_converter import (
    ModelFormatConverter,
    ConversionConfig,
    ConversionResult,
    ModelMetadata as ConverterModelMetadata,
    ModelFormat,
    OptimizationLevel,
    TargetPlatform,
    CreatorType as ConverterCreatorType,
    create_model_format_converter,
    create_conversion_config
)

__all__ = [
    # MLflow Registry (Existing)
    'MLflowModelRegistry',
    'ModelRegistryConfig',
    'ModelMetadata',
    'DeploymentInfo',
    'ModelStage',
    'RegistryStatus',
    'ModelRegistryFactory',
    
    # Version Control (Existing)
    "ModelVersionController",
    "VersionInfo",
    "VersionControlConfig", 
    "VersionOperation",
    
    # Encryption & Security (Existing)
    "ModelEncryptionManager",
    "EncryptionLevel",
    "KeyType",
    "EncryptionConfig",
    "SecurityMetrics",
    
    # Access Control & RBAC (NEW - PHASE 2)
    "ModelAccessController",
    "Permission",
    "Role",
    "AccessLevel",
    "User",
    "AccessRequest",
    "AuditLog",
    
    # Compliance & Governance (NEW - PHASE 2)
    "ModelComplianceValidator",
    "ComplianceStandard",
    "ComplianceLevel",
    "ViolationType",
    "ComplianceRule",
    "ComplianceViolation",
    "ComplianceAssessment",
    "ComplianceModelMetadata",
    
    # Bias Detection & Ethical AI (NEW - PHASE 2)
    "ModelBiasDetector",
    "BiasType",
    "ProtectedAttribute",
    "BiasLevel",
    "FairnessMetric",
    "BiasTestResult",
    "CreatorBiasAnalysis",
    "BiasAssessment",
    "ModelPrediction",
    
    # NEW PHASE 15 - Model Lifecycle Management
    "ModelPerformanceTracker",
    "RegistryPerformanceMetric",
    "ModelPerformanceSnapshot",
    "PerformanceTrend",
    "DegradationAlert",
    "PerformanceStatus",
    "TrackerConfig",
    "create_model_performance_tracker",
    
    # Model Format Converter (NEW PHASE 15)
    "ModelFormatConverter",
    "ConversionConfig",
    "ConversionResult",
    "ConverterModelMetadata",
    "ModelFormat",
    "OptimizationLevel",
    "TargetPlatform",
    "ConverterCreatorType",
    "create_model_format_converter",
    "create_conversion_config"
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. Tous droits réservés."