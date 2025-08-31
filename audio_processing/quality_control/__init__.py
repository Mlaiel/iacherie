"""🎯 Audio Quality Control - Professional Quality Management System

Advanced audio quality control system for comprehensive audio content validation,
monitoring, and optimization. Includes real-time quality assessment, automated
quality gates, and professional grade quality standards enforcement.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.

Unauthorized use, copying, modification, distribution or reproduction of this code 
or concept without explicit written authorization from Fahed Mlaiel (mlaiel@live.de) 
is strictly prohibited and subject to legal prosecution under German and international law.
"""
from .controller import QualityController
from .validator import AudioQualityValidator
from .monitor import QualityMonitor
from .standards import QualityStandards, QualityProfile, QualityRule
from .metrics import QualityMetrics, QualityReport, QualityScore
from .gates import QualityGate, QualityGateResult
from .optimization import QualityOptimizer
from .compliance import ComplianceChecker
from .dashboard import QualityDashboard

__all__ = [
    'QualityController',
    'AudioQualityValidator', 
    'QualityMonitor',
    'QualityStandards',
    'QualityProfile',
    'QualityRule',
    'QualityMetrics',
    'QualityReport', 
    'QualityScore',
    'QualityGate',
    'QualityGateResult',
    'QualityOptimizer',
    'ComplianceChecker',
    'QualityDashboard'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
