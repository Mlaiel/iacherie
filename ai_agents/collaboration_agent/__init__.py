"""
Collaboration Agent Module - AI-Powered Creator Matching & Partnership System

Advanced intelligent collaboration system that matches creators based on content analysis,
style compatibility, audience overlap, and collaboration history for optimal partnerships.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .collaboration_agent import CollaborationAgent
from .collaboration_manager import CollaborationAgentManager
from .matching_engine import (
    CreatorMatcher,
    StyleAnalyzer,
    AudienceAnalyzer,
    CompatibilityScorer
)
from .workflow_manager import (
    CollaborationWorkflow,
    ProjectManager,
    TaskCoordinator
)

__all__ = [
    'CollaborationAgent',
    'CollaborationAgentManager',
    'CreatorMatcher',
    'StyleAnalyzer',
    'AudienceAnalyzer',
    'CompatibilityScorer',
    'CollaborationWorkflow',
    'ProjectManager',
    'TaskCoordinator'
]
