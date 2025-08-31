#!/usr/bin/env python3
"""IA Influencer Agent - Advanced Creator Matching Business Module
==============================================================

Professional Multi-Format Creator Matching & Collaboration System
Ultra-Advanced Industrial Production-Ready Business Logic

Version: 3.0.0
Created by: Fahed Mlaiel (mlaiel@live.de)
Expert Team Specialties:
- Lead Dev + AI Architect Developer
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)  
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps & Infrastructure Engineer
- AI Prompt Engineering Expert

⚠️ STRICT COPYRIGHT WARNING ⚠️
(c) 2025 Fahed Mlaiel. ALL RIGHTS RESERVED.

This software, concept and intellectual property are protected by international copyright laws.
Any unauthorized use, reproduction, distribution or appropriation of this code, ideas or 
concepts without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
strictly prohibited and will result in immediate legal action.

CONSEQUENCES OF UNAUTHORIZED USE:
- Immediate legal proceedings under German and international copyright law
- Financial damages and compensation claims  
- Criminal prosecution for intellectual property theft
- Permanent legal documentation and public disclosure of violation

AUTHORIZED USE: Contact mlaiel@live.de for licensing and authorization.
"""

from .matching_engine import (
    CreatorMatchingEngine,
    CompatibilityAnalyzer,
    CollaborationMatcher,
    MatchingPreferences
)

from .matching_models import (
    CreatorProfile,
    MatchResult,
    CollaborationOpportunity,
    MatchingCriteria,
    CreatorCompatibility,
    CollaborationProposal,
    MatchingScore,
    CreatorNetwork
)

from .matching_services import (
    MatchingService,
    CollaborationService,
    NetworkAnalysisService,
    RecommendationService,
    PartnershipService
)

from .matching_analytics import (
    MatchingAnalytics,
    CollaborationMetrics,
    NetworkInsights,
    PerformanceTracker,
    SuccessPredictor
)

from .matching_processors import (
    ProfileProcessor,
    CompatibilityProcessor,
    NetworkProcessor,
    RecommendationProcessor,
    AnalyticsProcessor
)

from .opportunity_finder import (
    OpportunityFinder,
    CollaborationScout,
    PartnershipDetector,
    NetworkExpander,
    MarketAnalyzer
)

from .network_intelligence import (
    NetworkIntelligence,
    CreatorNetworkBuilder,
    InfluenceMapper,
    CommunityDetector,
    RelationshipAnalyzer
)

from .collaboration_manager import (
    CollaborationManager,
    PartnershipCoordinator,
    ProjectManager,
    WorkflowOrchestrator,
    ResourceAllocator
)

from .matching_algorithms import (
    SemanticMatcher,
    BehavioralMatcher,
    ContentStyleMatcher,
    AudienceMatcher,
    RevenueCompatibilityMatcher
)

from .quality_assessor import (
    QualityAssessor,
    ContentQualityAnalyzer,
    ProfileValidator,
    MatchQualityChecker,
    ComplianceValidator
)

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    # Core Matching Engine
    "CreatorMatchingEngine",
    "CompatibilityAnalyzer", 
    "CollaborationMatcher",
    "MatchingPreferences",
    
    # Data Models
    "CreatorProfile",
    "MatchResult",
    "CollaborationOpportunity",
    "MatchingCriteria",
    "CreatorCompatibility",
    "CollaborationProposal",
    "MatchingScore",
    "CreatorNetwork",
    
    # Business Services
    "MatchingService",
    "CollaborationService",
    "NetworkAnalysisService",
    "RecommendationService",
    "PartnershipService",
    
    # Analytics & Intelligence
    "MatchingAnalytics",
    "CollaborationMetrics",
    "NetworkInsights",
    "PerformanceTracker",
    "SuccessPredictor",
    
    # Data Processors
    "ProfileProcessor",
    "CompatibilityProcessor",
    "NetworkProcessor",
    "RecommendationProcessor",
    "AnalyticsProcessor",
    
    # Opportunity Detection
    "OpportunityFinder",
    "CollaborationScout",
    "PartnershipDetector",
    "NetworkExpander",
    "MarketAnalyzer",
    
    # Network Intelligence
    "NetworkIntelligence",
    "CreatorNetworkBuilder",
    "InfluenceMapper",
    "CommunityDetector",
    "RelationshipAnalyzer",
    
    # Collaboration Management
    "CollaborationManager",
    "PartnershipCoordinator",
    "ProjectManager",
    "WorkflowOrchestrator",
    "ResourceAllocator",
    
    # Matching Algorithms
    "SemanticMatcher",
    "BehavioralMatcher",
    "ContentStyleMatcher",
    "AudienceMatcher",
    "RevenueCompatibilityMatcher",
    
    # Quality Control
    "QualityAssessor",
    "ContentQualityAnalyzer",
    "ProfileValidator",
    "MatchQualityChecker",
    "ComplianceValidator"
]
