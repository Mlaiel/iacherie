"""Data Governance Module

Complete data governance system for the IA Influencer Agent platform,
providing comprehensive policy management, compliance monitoring,
privacy protection, and data quality assurance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

from .policies import (
    PolicyManager,
    DataPolicy,
    PolicyCondition,
    PolicyAction,
    PolicyViolation,
    PolicyConditionEvaluator
)

from .compliance import (
    ComplianceManager,
    ComplianceFramework,
    ComplianceAssessment,
    GDPRCompliance,
    CCPACompliance,
    DMCACompliance
)

from .lifecycle import (
    LifecycleManager,
    DataLifecycleStage,
    RetentionPolicy,
    ArchivalStrategy,
    CloudArchivalStrategy,
    TapeArchivalStrategy
)

from .quality import (
    QualityManager,
    QualityDimension,
    QualityMetrics,
    QualityAssessment,
    AudioQualityChecker,
    VideoQualityChecker,
    ImageQualityChecker,
    TextQualityChecker
)

from .lineage import (
    LineageManager,
    DataLineage,
    LineageNode,
    LineageEdge,
    LineageGraph,
    LineageTracker
)

from .access import (
    AccessController,
    AccessPolicy,
    AccessRequest,
    AccessDecision,
    PolicyEngine,
    RoleManager,
    PermissionManager
)

from .privacy import (
    PrivacyManager,
    PIIType,
    PIIDetectionResult,
    AnonymizationRule,
    AnonymizationRecord,
    AnonymizationTechnique,
    PrivacyLevel,
    PIIDetector,
    AnonymizationEngine
)

from .monitoring import (
    GovernanceMonitor,
    MetricsCollector,
    AlertManager,
    GovernanceAlert,
    AlertSeverity,
    MonitoringThreshold,
    MetricType,
    GovernanceDashboard
)

from .reporting import (
    GovernanceReportManager,
    ReportType,
    ReportFormat,
    ReportRequest,
    ComplianceReport,
    ComplianceReportGenerator,
    PolicyViolationReportGenerator,
    ExecutiveSummaryGenerator
)

from .metadata import (
    MetadataManager,
    DataCatalogManager,
    SchemaManager,
    BusinessGlossaryManager,
    DataAssetMetadata,
    DataSchema,
    BusinessGlossaryTerm,
    DataCatalogEntry,
    MetadataLineage,
    DataType,
    SchemaType,
    SensitivityLevel
)

from .classification import (
    DataClassificationManager,
    ClassificationEngine,
    ClassificationResult,
    ClassificationRule,
    ClassificationLevel,
    ContentCategory,
    SensitivityLabel,
    ComplianceTag,
    ComplianceTaggingEngine,
    PatternClassifier,
    AIClassifier
)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"

# Module metadata
__all__ = [
    # Policy Management
    "PolicyManager",
    "DataPolicy",
    "PolicyCondition",
    "PolicyAction", 
    "PolicyViolation",
    "PolicyConditionEvaluator",
    
    # Compliance Management
    "ComplianceManager",
    "ComplianceFramework",
    "ComplianceAssessment",
    "GDPRCompliance",
    "CCPACompliance", 
    "DMCACompliance",
    
    # Lifecycle Management
    "LifecycleManager",
    "DataLifecycleStage",
    "RetentionPolicy",
    "ArchivalStrategy",
    "CloudArchivalStrategy",
    "TapeArchivalStrategy",
    
    # Quality Management
    "QualityManager",
    "QualityDimension",
    "QualityMetrics",
    "QualityAssessment",
    "AudioQualityChecker",
    "VideoQualityChecker",
    "ImageQualityChecker",
    "TextQualityChecker",
    
    # Lineage Management
    "LineageManager",
    "DataLineage",
    "LineageNode",
    "LineageEdge",
    "LineageGraph",
    "LineageTracker",
    
    # Access Control
    "AccessController",
    "AccessPolicy",
    "AccessRequest",
    "AccessDecision",
    "PolicyEngine",
    "RoleManager",
    "PermissionManager",
    
    # Privacy Management
    "PrivacyManager",
    "PIIType",
    "PIIDetectionResult",
    "AnonymizationRule",
    "AnonymizationRecord",
    "AnonymizationTechnique",
    "PrivacyLevel",
    "PIIDetector",
    "AnonymizationEngine",
    
    # Monitoring
    "GovernanceMonitor",
    "MetricsCollector",
    "AlertManager",
    "GovernanceAlert",
    "AlertSeverity",
    "MonitoringThreshold",
    "MetricType",
    "GovernanceDashboard",
    
    # Reporting
    "GovernanceReportManager",
    "ReportType",
    "ReportFormat",
    "ReportRequest",
    "ComplianceReport",
    "ComplianceReportGenerator",
    "PolicyViolationReportGenerator",
    "ExecutiveSummaryGenerator",
    
    # Metadata Management
    "MetadataManager",
    "DataCatalogManager",
    "SchemaManager",
    "BusinessGlossaryManager",
    "DataAssetMetadata",
    "DataSchema",
    "BusinessGlossaryTerm",
    "DataCatalogEntry",
    "MetadataLineage",
    "DataType",
    "SchemaType",
    "SensitivityLevel",
    
    # Classification
    "DataClassificationManager",
    "ClassificationEngine",
    "ClassificationResult",
    "ClassificationRule",
    "ClassificationLevel",
    "ContentCategory",
    "SensitivityLabel",
    "ComplianceTag",
    "ComplianceTaggingEngine",
    "PatternClassifier",
    "AIClassifier"
]