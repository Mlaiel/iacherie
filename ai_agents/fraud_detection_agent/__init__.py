"""
Fraud Detection Agent - Industrial-Grade Content Fraud Detection System

Advanced AI-powered fraud detection and prevention system for content protection,
revenue authentication, and platform abuse detection in the IA-Influencer ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.

Team Expertise:
- Lead AI Developer: Advanced ML fraud detection algorithms
- Backend Senior: Enterprise-grade fraud prevention architecture  
- ML Engineer: Real-time anomaly detection and behavioral analysis
- Database Admin: High-performance fraud pattern storage and analytics
- Security Expert: Multi-layer fraud prevention and threat intelligence
- Microservices Architect: Scalable distributed fraud detection system
- Audio Engineer: Audio deepfake and manipulation detection
- DevOps Engineer: Real-time monitoring and fraud alert infrastructure
- IA Prompt Engineer: Natural language fraud pattern recognition
"""

from .core import FraudDetectionAgent
from .behavioral_analyzer import BehaviorAnalyzer
from .pattern_detector import PatternDetector
from .revenue_validator import RevenueValidator
from .deepfake_detector import DeepfakeDetector
from .anomaly_engine import AnomalyDetectionEngine
from .threat_intelligence import ThreatIntelligenceEngine

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "FraudDetectionAgent",
    "BehaviorAnalyzer", 
    "PatternDetector",
    "RevenueValidator",
    "DeepfakeDetector", 
    "AnomalyDetectionEngine",
    "ThreatIntelligenceEngine"
]
