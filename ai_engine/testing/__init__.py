"""AI/ML Testing Specialization Module

This module provides comprehensive testing capabilities for AI/ML models including:
- Model accuracy validation (>99% on production datasets)
- Data drift detection and monitoring
- Bias testing and fairness validation
- A/B testing frameworks for continuous experimentation
- Adversarial testing for AI security

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .accuracy_validation import (
    ProductionAccuracyValidator,
    AccuracyMetrics,
    AccuracyThreshold
)
from .bias_testing import (
    FairnessValidator,
    BiasMetrics,
    FairnessTest
)
from .adversarial_testing import (
    AdversarialSecurityTester,
    AdversarialAttack,
    SecurityMetrics
)
from .drift_monitoring import (
    EnhancedDriftMonitor,
    DriftAlert,
    MonitoringConfig
)
from .ab_testing_integration import (
    MLExperimentFramework,
    ExperimentConfig,
    ExperimentResults
)

__all__ = [
    "ProductionAccuracyValidator",
    "AccuracyMetrics",
    "AccuracyThreshold",
    "FairnessValidator",
    "BiasMetrics",
    "FairnessTest",
    "AdversarialSecurityTester",
    "AdversarialAttack",
    "SecurityMetrics",
    "EnhancedDriftMonitor",
    "DriftAlert",
    "MonitoringConfig",
    "MLExperimentFramework",
    "ExperimentConfig",
    "ExperimentResults"
]
