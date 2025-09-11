"""🔬 ML Experiments Module - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/experiments/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE D'EXPÉRIMENTATION ML
Composants avancés de recherche et validation
- Experiment tracking et version control
- Statistical hypothesis validation
- Creator-specific research frameworks
- Advanced ML research capabilities
"""

from .experiment_tracking_system import (
    ExperimentTrackingSystem,
    ExperimentStatus,
    Experiment,
    ExperimentRun,
    Metric,
    Artifact,
    HyperparameterOptimizer
)

from .hypothesis_validation_framework import (
    HypothesisValidationFramework,
    HypothesisType,
    StatisticalTest,
    MultipleComparisonMethod,
    HypothesisTestResult,
    BayesianAnalysisResult,
    ExperimentValidation
)

__all__ = [
    # Experiment Tracking (Existing)
    'ExperimentTrackingSystem',
    'ExperimentStatus',
    'Experiment',
    'ExperimentRun',
    'Metric',
    'Artifact',
    'HyperparameterOptimizer',
    
    # Hypothesis Validation (NEW - PHASE 5)
    'HypothesisValidationFramework',
    'HypothesisType',
    'StatisticalTest',
    'MultipleComparisonMethod',
    'HypothesisTestResult',
    'BayesianAnalysisResult',
    'ExperimentValidation'
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. Tous droits réservés."
