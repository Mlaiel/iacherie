"""
Experimentation Module
Enterprise A/B testing and statistical experimentation framework

Components:
- A/B Testing framework for model comparison
- Experiment orchestration and tracking
- Statistical validation and significance testing
- Multivariate testing and personalization
- Cohort analysis and conversion tracking

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .experiment_orchestrator import ExperimentOrchestrator
from .hypothesis_validator import HypothesisValidator
from .cohort_analyzer import CohortAnalyzer
from .conversion_tracker import ConversionTracker
from .significance_tester import SignificanceTester
from .experiment_reporting import ExperimentReporting
from .feature_flag_experiment import FeatureFlagExperiment
from .multivariate_testing import MultivariateTestingEngine
from .personalization_engine import PersonalizationEngine
from .experiment_metadata_manager import ExperimentMetadataManager

__version__ = "1.0.0"
__all__ = [
    "ExperimentOrchestrator",
    "HypothesisValidator", 
    "CohortAnalyzer",
    "ConversionTracker",
    "SignificanceTester",
    "ExperimentReporting",
    "FeatureFlagExperiment",
    "MultivariateTestingEngine",
    "PersonalizationEngine",
    "ExperimentMetadataManager"
]