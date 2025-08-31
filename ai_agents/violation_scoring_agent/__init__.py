"""Violation Scoring Agent - AI-Powered Violation Assessment System

Advanced AI-powered violation scoring system with machine learning algorithms
for intelligent violation detection, severity assessment, and automated response.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Features:
- AI-powered violation scoring
- Multi-factor severity assessment
- Automated response recommendations
- Historical pattern analysis
- Risk level calculation
"""

from .manager import ViolationScoringManager
from .core.scoring_engine import ScoringEngine
from .core.pattern_analyzer import PatternAnalyzer
from .core.risk_assessor import RiskAssessor
from .models.scoring_models import (
    ViolationScore,
    ScoringRequest,
    ScoringResult,
    RiskLevel,
    ViolationPattern
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "ViolationScoringManager",
    "ScoringEngine",
    "PatternAnalyzer",
    "RiskAssessor",
    "ViolationScore",
    "ScoringRequest", 
    "ScoringResult",
    "RiskLevel",
    "ViolationPattern"
]