"""🎯 ENTERPRISE QUALITY ASSURANCE MODULE - AINFLUE PLATFORM
================================================================

Point d'entrée principal pour l'écosystème de contrôle qualité enterprise
ultra-avancé orchestrant la validation complète multi-niveaux.

© 2025 Fahed Mlaiel - Architecture Quality Assurance Propriétaire
Contact: mlaiel@live.de

🏗️ ARCHITECTURE ENTERPRISE 9 MODULES:
├── test_orchestration/ - Orchestration tests multi-niveaux
├── analysis_engines/ - Moteurs analyse intelligence qualité
├── testing_engines/ - Moteurs testing enterprise avancés
├── validation_engines/ - Moteurs validation standards & compliance
├── quality_scoring/ - Scoring qualité IA prédictif
├── performance_monitoring/ - Monitoring performance temps réel
├── technical_debt/ - Tracking dette technique automatisé
├── service_mocking/ - Service mocking enterprise
└── reporting/ - Reporting & analytics qualité executive
================================================================
"""

# Core enterprise quality orchestrator
from .index import (
    quality_orchestrator,
    QualityModuleType,
    AinfluenceEnterpriseQualityOrchestrator
)

# Sub-modules (imported dynamically when available)
try:
    from .test_orchestration import master_orchestrator
except ImportError:
    master_orchestrator = None

try:
    from .test_orchestration import run_ainflue_quality_tests
except ImportError:
    run_ainflue_quality_tests = None

__all__ = [
    "quality_orchestrator",
    "QualityModuleType", 
    "AinfluenceEnterpriseQualityOrchestrator",
    "master_orchestrator",
    "run_ainflue_quality_tests"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Global convenience functions
async def run_enterprise_quality_analysis(project_path=None, environment="development"):
    """Run comprehensive enterprise quality analysis"""
    return await quality_orchestrator.run_enterprise_quality_workflow({
        "project_path": project_path,
        "environment": environment
    })

def get_package_info():
    """Get package information"""
    return {
        "name": "Ainflue Enterprise Quality Assurance",
        "version": __version__,
        "description": "Enterprise quality assurance orchestration system",
        "author": __author__,
        "email": __email__,
        "architecture": "9 specialized enterprise modules",
        "features": [
            "Orchestration tests parallèles intelligents",
            "Quality gates automatisés avec IA", 
            "Monitoring performance temps réel",
            "Scoring qualité IA prédictif",
            "Validation compliance enterprise",
            "Reporting executive multi-niveaux",
            "Intégration workflow créateurs Ainflue"
        ]
    }