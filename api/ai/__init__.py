"""
IA Influencer Agent - AI Module
Advanced artificial intelligence processing system for multi-format content analysis and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result 
in legal action.

© 2025 Fahed Mlaiel. All rights reserved.
"""

# Import main AI modules
from .nlp import TextAnalyzer
from .vision import VisionProcessor
from .recommendation import RecommendationEngine

# Import advanced AI processing modules
from .content_analysis import (
    ContentType,
    ContentMetadata,
    ContentAnalysisEngine,
    ContentProcessor
)

from .rights_protection import (
    ProtectionLevel,
    ViolationType,
    DigitalFingerprint,
    ProtectionResult,
    ViolationAlert,
    AdvancedFingerprintGenerator,
    ViolationDetector,
    RightsProtectionEngine
)

from .seo_optimization import (
    SEOPlatform,
    ContentFormat as SEOContentFormat,
    SEOKeyword,
    SEOMetadata,
    SEOAnalytics,
    KeywordAnalyzer,
    ContentOptimizer as SEOContentOptimizer,
    PerformanceAnalyzer
)

from .collaboration_matching import (
    CreatorType,
    CollaborationType,
    CompatibilityFactor,
    CreatorProfile,
    CollaborationOpportunity,
    MatchResult,
    CreatorAnalyzer,
    CompatibilityCalculator,
    CollaborationMatcher
)

from .distribution_intelligence import (
    Platform,
    ContentFormat as DistributionContentFormat,
    DistributionStrategy,
    PlatformRequirements,
    ContentVariant,
    DistributionPlan,
    DistributionResult,
    PlatformAnalyzer,
    ContentOptimizer as DistributionContentOptimizer,
    DistributionScheduler,
    DistributionEngine
)

# Export main classes
__all__ = [
    # Core AI modules
    'TextAnalyzer',
    'VisionProcessor', 
    'RecommendationEngine',
    
    # Content Analysis
    'ContentType',
    'ContentMetadata',
    'ContentAnalysisEngine',
    'ContentProcessor',
    
    # Rights Protection
    'ProtectionLevel',
    'ViolationType',
    'DigitalFingerprint',
    'ProtectionResult',
    'ViolationAlert',
    'AdvancedFingerprintGenerator',
    'ViolationDetector',
    'RightsProtectionEngine',
    
    # SEO Optimization
    'SEOPlatform',
    'SEOContentFormat',
    'SEOKeyword',
    'SEOMetadata',
    'SEOAnalytics',
    'KeywordAnalyzer',
    'SEOContentOptimizer',
    'PerformanceAnalyzer',
    
    # Collaboration Matching
    'CreatorType',
    'CollaborationType',
    'CompatibilityFactor',
    'CreatorProfile',
    'CollaborationOpportunity',
    'MatchResult',
    'CreatorAnalyzer',
    'CompatibilityCalculator',
    'CollaborationMatcher',
    
    # Distribution Intelligence
    'Platform',
    'DistributionContentFormat',
    'DistributionStrategy',
    'PlatformRequirements',
    'ContentVariant',
    'DistributionPlan',
    'DistributionResult',
    'PlatformAnalyzer',
    'DistributionContentOptimizer',
    'DistributionScheduler',
    'DistributionEngine'
]
