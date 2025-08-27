"""
Trend Agent Module - Advanced Trend Analysis & Prediction System

Real-time trend detection, analysis, and prediction system for content optimization.
Handles trend monitoring, viral content analysis, and future trend prediction.

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

from .trend_agent import TrendAgent, TrendAgentManager
from .trend_analyzer import TrendAnalyzer, TrendPredictor
from .viral_detector import ViralDetector, ContentRanker
from .hashtag_analyzer import HashtagAnalyzer, TagOptimizer
from .market_intelligence import MarketIntelligence, CompetitorAnalyzer
from .index import (
    TrendAgentIndex,
    TrendServiceRequest,
    TrendServiceResponse,
    ServiceType,
    ServiceStatus,
    get_trend_index,
    analyze_trends,
    detect_viral_content,
    optimize_hashtags
)

__all__ = [
    # Core agents and components
    'TrendAgent',
    'TrendAgentManager', 
    'TrendAnalyzer',
    'TrendPredictor',
    'ViralDetector',
    'ContentRanker',
    'HashtagAnalyzer',
    'TagOptimizer',
    'MarketIntelligence',
    'CompetitorAnalyzer',
    
    # Index and orchestration
    'TrendAgentIndex',
    'TrendServiceRequest',
    'TrendServiceResponse',
    'ServiceType',
    'ServiceStatus',
    
    # Convenience functions
    'get_trend_index',
    'analyze_trends',
    'detect_viral_content',
    'optimize_hashtags'
]
