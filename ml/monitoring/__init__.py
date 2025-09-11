"""🚀 ML Monitoring Module - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/monitoring/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE DE MONITORING ML
Surveillance complète des modèles ML en production
- Performance monitoring en temps réel
- Data drift et model drift detection
- Système d'alertes intelligent
- Reporting et analytics avancés
"""

from .performance_monitor import (
    ModelPerformanceMonitor,
    MetricPoint,
    Alert,
    DriftAnalysis,
    PerformanceReport,
    AlertSeverity,
    MetricType,
    DriftType,
    MonitorFactory
)

# NEW PHASE 15 MODULES - Advanced Monitoring & Explainability
from .model_explainer import (
    ModelExplainer,
    ExplanationRequest,
    FeatureAttribution,
    ModelExplanation,
    ExplanationType,
    ExplainerMethod,
    ExplainerConfig,
    CreatorType as ExplainerCreatorType,
    create_model_explainer
)

from .performance_anomaly_detector import (
    PerformanceAnomalyDetector,
    PerformanceMetric as AnomalyPerformanceMetric,
    AnomalyDetection,
    AnomalyPattern,
    AnomalyType,
    AnomalySeverity,
    DetectionMethod,
    DetectorConfig,
    create_anomaly_detector
)

__all__ = [
    'ModelPerformanceMonitor',
    'MetricPoint',
    'Alert',
    'DriftAnalysis',
    'PerformanceReport',
    'AlertSeverity',
    'MetricType',
    'DriftType',
    'MonitorFactory',
    
    # NEW PHASE 15 - Advanced Monitoring & Explainability
    'ModelExplainer',
    'ExplanationRequest',
    'FeatureAttribution',
    'ModelExplanation',
    'ExplanationType',
    'ExplainerMethod',
    'ExplainerConfig',
    'ExplainerCreatorType',
    'create_model_explainer',
    'PerformanceAnomalyDetector',
    'AnomalyPerformanceMetric',
    'AnomalyDetection',
    'AnomalyPattern',
    'AnomalyType',
    'AnomalySeverity',
    'DetectionMethod',
    'DetectorConfig',
    'create_anomaly_detector'
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. Tous droits réservés."