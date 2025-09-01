"""🎯 Quality Metrics Package - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + DEVOPS_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Comprehensive quality metrics package for code quality assessment,
technical debt tracking, security analysis, and compliance monitoring.
================================================================
"""

from .metrics_orchestrator import (
    QualityMetricsOrchestrator,
    QualityMetric,
    QualityReport,
    QualityMetricType,
    QualityLevel,
    quality_orchestrator
)

from .technical_debt_tracker import (
    TechnicalDebtTracker,
    DebtItem,
    DebtSummary,
    DebtType,
    DebtSeverity,
    technical_debt_tracker
)

from .api_breaking_detector import (
    APIBreakingChangesDetector,
    APIEndpoint,
    APIChange,
    APIContract,
    ChangeType,
    BreakingSeverity,
    api_breaking_detector
)

from .security_scorecard import (
    SecurityScorecardEngine,
    SecurityScorecard,
    SecurityMetric,
    SecurityFinding,
    SecurityDomain,
    SecurityLevel,
    security_scorecard
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel (mlaiel@live.de)"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    # Orchestrator
    "QualityMetricsOrchestrator",
    "QualityMetric",
    "QualityReport", 
    "QualityMetricType",
    "QualityLevel",
    "quality_orchestrator",
    
    # Technical Debt
    "TechnicalDebtTracker",
    "DebtItem",
    "DebtSummary",
    "DebtType", 
    "DebtSeverity",
    "technical_debt_tracker",
    
    # API Breaking Changes
    "APIBreakingChangesDetector",
    "APIEndpoint",
    "APIChange",
    "APIContract",
    "ChangeType",
    "BreakingSeverity", 
    "api_breaking_detector",
    
    # Security Scorecard
    "SecurityScorecardEngine",
    "SecurityScorecard",
    "SecurityMetric",
    "SecurityFinding",
    "SecurityDomain",
    "SecurityLevel",
    "security_scorecard"
]

# Global convenience functions
async def run_quality_analysis(project_path=None, environment="development"):
    """Run comprehensive quality analysis"""
    return await quality_orchestrator.run_comprehensive_analysis(
        project_path=project_path,
        environment=environment
    )

async def analyze_technical_debt(project_path=None):
    """Analyze technical debt"""
    tracker = TechnicalDebtTracker(project_path)
    return await tracker.analyze_technical_debt()

async def detect_api_breaking_changes(baseline_path=None, project_path=None):
    """Detect API breaking changes"""
    detector = APIBreakingChangesDetector(project_path)
    return await detector.detect_breaking_changes(baseline_path)

async def generate_security_scorecard(project_path=None):
    """Generate security scorecard"""
    engine = SecurityScorecardEngine(project_path)
    return await engine.generate_scorecard()

# Package metadata
PACKAGE_INFO = {
    "name": "Ainflue Quality Metrics",
    "version": __version__,
    "description": "Comprehensive quality metrics and analysis system",
    "author": __author__,
    "copyright": __copyright__,
    "components": {
        "Quality Orchestrator": "Coordinates all quality checks and metrics",
        "Technical Debt Tracker": "Identifies and tracks technical debt",
        "API Breaking Detector": "Detects breaking changes in API contracts",
        "Security Scorecard": "Comprehensive security posture assessment"
    },
    "features": [
        "Code coverage analysis with mandatory thresholds",
        "Code quality gates with SonarQube-equivalent features", 
        "Dependency vulnerability scanning with alerts",
        "Automated performance benchmarking with baselines",
        "License compliance scanning for dependencies",
        "Technical debt tracking with automated metrics",
        "Code complexity analysis with alert thresholds",
        "Documentation coverage with automatic validation",
        "API breaking changes detection",
        "Security scorecard with improvement tracking"
    ]
}

def get_package_info():
    """Get package information"""
    return PACKAGE_INFO