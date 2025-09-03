"""Collaboration Engine - AI-Powered Creator Collaboration Services

Main collaboration engine providing intelligent creator matching, 
project management, and revenue distribution capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .matching.ai_matchmaker import AIMatchmaker
from .matching.skill_analyzer import SkillAnalyzer  
from .matching.compatibility_score import CompatibilityScore

from .workspace.project_manager import ProjectManager
from .workspace.real_time_collab import RealTimeCollab
from .workspace.version_control import VersionControl

from .contracts.smart_contracts import SmartContracts
from .contracts.revenue_splitter import RevenueSplitter

# Module version
__version__ = "1.0.0"

# Module description
__description__ = "AI-Powered Creator Collaboration Engine"

# Export all main classes
__all__ = [
    # Matching
    'AIMatchmaker',
    'SkillAnalyzer', 
    'CompatibilityScore',
    
    # Workspace
    'ProjectManager',
    'RealTimeCollab',
    'VersionControl',
    
    # Contracts
    'SmartContracts',
    'RevenueSplitter'
]


class CollaborationEngine:
    """
    Unified Collaboration Engine that orchestrates all collaboration services
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        
        # Initialize matching services
        self.ai_matchmaker = AIMatchmaker(self.config.get('matching', {}))
        self.skill_analyzer = SkillAnalyzer(self.config.get('skills', {}))
        self.compatibility_score = CompatibilityScore(self.config.get('compatibility', {}))
        
        # Initialize workspace services
        self.project_manager = ProjectManager(self.config.get('projects', {}))
        self.real_time_collab = RealTimeCollab(self.config.get('realtime', {}))
        self.version_control = VersionControl(self.config.get('versioning', {}))
        
        # Initialize contract services
        self.smart_contracts = SmartContracts(self.config.get('contracts', {}))
        self.revenue_splitter = RevenueSplitter(self.config.get('revenue', {}))
    
    async def initialize(self):
        """Initialize all collaboration services"""
        # Initialize matching services
        await self.ai_matchmaker.initialize()
        await self.skill_analyzer.initialize()
        await self.compatibility_score.initialize()
        
        # Initialize workspace services
        await self.project_manager.initialize()
        await self.real_time_collab.initialize()
        await self.version_control.initialize()
        
        # Initialize contract services
        await self.smart_contracts.initialize()
        await self.revenue_splitter.initialize()
    
    async def shutdown(self):
        """Shutdown all collaboration services"""
        services = [
            self.ai_matchmaker, self.skill_analyzer, self.compatibility_score,
            self.project_manager, self.real_time_collab, self.version_control,
            self.smart_contracts, self.revenue_splitter
        ]
        
        for service in services:
            if hasattr(service, 'shutdown'):
                await service.shutdown()