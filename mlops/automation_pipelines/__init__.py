"""
Automation Pipelines Module
Enterprise CI/CD and automation pipelines for MLOps

Components:
- Continuous Integration/Deployment for ML models
- Automated testing and validation pipelines
- Quality gates and model validation
- Automated retraining and deployment
- Pipeline orchestration and monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .ci_cd_orchestrator import CICDOrchestrator
from .automated_retraining import AutomatedRetrainingEngine
from .artifact_builder import ArtifactBuilder
from .integration_test_runner import IntegrationTestRunner
from .performance_test_framework import PerformanceTestFramework
from .penetration_testing_suite import PenetrationTestingSuite
from .pipeline_validator import PipelineValidator
from .regression_test_engine import RegressionTestEngine
from .rollback_automation import RollbackAutomation
from .helm_chart_manager import HelmChartManager
from .continuous_integration import ContinuousIntegrationEngine
from .continuous_deployment import ContinuousDeploymentEngine
from .quality_gate_engine import QualityGateEngine
from .pipeline_orchestration import PipelineOrchestrator
from .automation_metrics import AutomationMetricsCollector
from .deployment_strategy_manager import DeploymentStrategyManager

__version__ = "1.0.0"
__all__ = [
    "CICDOrchestrator",
    "AutomatedRetrainingEngine",
    "ArtifactBuilder",
    "IntegrationTestRunner", 
    "PerformanceTestFramework",
    "PenetrationTestingSuite",
    "PipelineValidator",
    "RegressionTestEngine",
    "RollbackAutomation",
    "HelmChartManager",
    "ContinuousIntegrationEngine",
    "ContinuousDeploymentEngine", 
    "QualityGateEngine",
    "PipelineOrchestrator",
    "AutomationMetricsCollector",
    "DeploymentStrategyManager"
]