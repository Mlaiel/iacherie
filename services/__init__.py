# Services module initialization
"""Ainflue Services Module

This module contains all business services for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT INTELLECTUAL PROPERTY WARNING ⚠️
This software and all associated code are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
UNAUTHORIZED ACCESS, COPYING, MODIFICATION, DISTRIBUTION, REVERSE ENGINEERING, 
OR COMMERCIALIZATION without explicit written permission is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

For legitimate licensing inquiries: mlaiel@live.de
"""

# Advanced IA Matching Services (New)
from .advanced_matching_service import (
    AdvancedMatchingService,
    MatchingStrategy,
    CreativeMatchType,
    CreatorProfile,
    CompatibilityScore,
    CollaborationPrediction,
    ProactiveSuggestion
)

from .graph_database import (
    CreatorGraphDatabase,
    RelationshipType,
    NetworkNode,
    RelationshipEdge,
    NetworkCommunity
)

# Existing Services (Import what's available)
try:
    from .collaboration_engine import CollaborationEngine
except ImportError:
    CollaborationEngine = None

try:
    from .remix_generator import RemixGenerator
except ImportError:
    RemixGenerator = None

try:
    from .gamification_system import GamificationSystem
except ImportError:
    GamificationSystem = None

try:
    from .recommendation_engine import RecommendationEngine
except ImportError:
    RecommendationEngine = None

__all__ = [
    # Advanced IA Matching Services
    "AdvancedMatchingService",
    "MatchingStrategy",
    "CreativeMatchType", 
    "CreatorProfile",
    "CompatibilityScore",
    "CollaborationPrediction",
    "ProactiveSuggestion",
    "CreatorGraphDatabase",
    "RelationshipType",
    "NetworkNode",
    "RelationshipEdge",
    "NetworkCommunity",
    # Legacy Services
    "CollaborationEngine",
    "RemixGenerator",
    "GamificationSystem", 
    "RecommendationEngine"
]