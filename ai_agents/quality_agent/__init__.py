"""
Quality Agent Module - Advanced Content Quality Assessment & Enhancement System

Comprehensive quality control, assessment, and enhancement system for all content types.
Handles quality scoring, automated improvement suggestions, and content optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from .quality_agent import QualityAgent, QualityAgentManager
from .quality_assessor import QualityAssessor, ContentScorer
from .quality_enhancer import QualityEnhancer, ImprovementEngine
from .standards_checker import StandardsChecker, ComplianceValidator
from .performance_analyzer import PerformanceAnalyzer, MetricsCalculator

__all__ = [
    'QualityAgent',
    'QualityAgentManager', 
    'QualityAssessor',
    'ContentScorer',
    'QualityEnhancer',
    'ImprovementEngine',
    'StandardsChecker',
    'ComplianceValidator',
    'PerformanceAnalyzer',
    'MetricsCalculator'
]
