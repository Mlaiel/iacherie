"""Creator Services Interface
Main entry point for Ainflue Platform creator-specific services.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """CreatorType class implementation"""
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

class ContentType(Enum):
    """ContentType class implementation"""
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    MIXED = "mixed"

@dataclass
class CreatorProfile:
    """Creator profile configuration"""
    creator_id: str
    creator_type: CreatorType
    name: str
    specialties: List[str]
    platforms: List[str]
    audience_size: Optional[int] = None
    engagement_rate: Optional[float] = None
    metadata: Optional[Dict] = None

@dataclass
class ContentProject:
    """Content creation project"""
    project_id: str
    creator_id: str
    content_type: ContentType
    title: str
    description: Optional[str] = None
    requirements: Optional[Dict] = None
    created_at: Optional[datetime] = None
    deadline: Optional[datetime] = None

class CreatorServicesOrchestrator:
    """Main orchestrator for creator-specific services"""
    
    def __init__(self) -> None:
        self.musician_tools = None
        self.photographer_tools = None
        self.blogger_tools = None
        self.influencer_tools = None
        self.comedian_tools = None
        self.creator_profiler = None
        self.skill_mapper = None
        self.growth_tracker = None
        self.active_creators: Dict[str, CreatorProfile] = {}
        self.active_projects: Dict[str, ContentProject] = {}
    
    async def initialize(self) -> None:
        """Initialize all creator services"""
        logger.info("Initializing Creator Services Orchestrator...")
        
        # Initialize creator tools
        await self._initialize_musician_tools()
        await self._initialize_photographer_tools()
        await self._initialize_blogger_tools()
        await self._initialize_influencer_tools()
        await self._initialize_comedian_tools()
        
        # Initialize supporting services
        await self._initialize_creator_profiler()
        await self._initialize_skill_mapper()
        await self._initialize_growth_tracker()
        
        logger.info("Creator Services Orchestrator initialized successfully")
    
    async def _initialize_musician_tools(self) -> None:
        """Initialize musician-specific tools"""
        from .musician_tools import MusicianTools
        self.musician_tools = MusicianTools()
        await self.musician_tools.initialize()
        logger.info("✅ Musician tools initialized")
    
    async def _initialize_photographer_tools(self) -> None:
        """Initialize photographer-specific tools"""
        from .photographer_tools import PhotographerTools
        self.photographer_tools = PhotographerTools()
        await self.photographer_tools.initialize()
        logger.info("✅ Photographer tools initialized")
    
    async def _initialize_blogger_tools(self) -> None:
        """Initialize blogger-specific tools"""
        from .blogger_tools import BloggerTools
        self.blogger_tools = BloggerTools()
        await self.blogger_tools.initialize()
        logger.info("✅ Blogger tools initialized")
    
    async def _initialize_influencer_tools(self) -> None:
        """Initialize influencer-specific tools"""
        from .influencer_tools import InfluencerTools
        self.influencer_tools = InfluencerTools()
        await self.influencer_tools.initialize()
        logger.info("✅ Influencer tools initialized")
    
    async def _initialize_comedian_tools(self) -> None:
        """Initialize comedian-specific tools"""
        from .comedian_tools import ComedianTools
        self.comedian_tools = ComedianTools()
        await self.comedian_tools.initialize()
        logger.info("✅ Comedian tools initialized")
    
    async def _initialize_creator_profiler(self) -> None:
        """Initialize creator profiler"""
        from .creator_profiler import CreatorProfiler
        self.creator_profiler = CreatorProfiler()
        await self.creator_profiler.initialize()
        logger.info("✅ Creator profiler initialized")
    
    async def _initialize_skill_mapper(self) -> None:
        """Initialize skill mapper"""
        from .skill_mapper import SkillMapper
        self.skill_mapper = SkillMapper()
        await self.skill_mapper.initialize()
        logger.info("✅ Skill mapper initialized")
    
    async def _initialize_growth_tracker(self) -> None:
        """Initialize growth tracker"""
        from .growth_tracker import GrowthTracker
        self.growth_tracker = GrowthTracker()
        await self.growth_tracker.initialize()
        logger.info("✅ Growth tracker initialized")
    
    async def register_creator(self, profile: CreatorProfile) -> str:
        """Register a new creator"""
        try:
            # Store creator profile
            self.active_creators[profile.creator_id] = profile
            
            # Profile the creator
            await self.creator_profiler.analyze_creator(profile)
            
            # Map skills
            await self.skill_mapper.map_creator_skills(profile)
            
            # Initialize growth tracking
            await self.growth_tracker.start_tracking(profile.creator_id)
            
            logger.info(f"✅ Creator registered: {profile.name} ({profile.creator_type.value})")
            return profile.creator_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register creator {profile.name}: {e}")
            raise
    
    async def create_content_project(self, project: ContentProject) -> str:
        """Create a new content project"""
        try:
            # Store project
            self.active_projects[project.project_id] = project
            
            # Get creator profile
            creator = self.active_creators.get(project.creator_id)
            if not creator:
                raise ValueError(f"Creator not found: {project.creator_id}")
            
            # Initialize project with appropriate tools
            if creator.creator_type == CreatorType.MUSICIAN:
                await self.musician_tools.initialize_project(project)
            elif creator.creator_type == CreatorType.PHOTOGRAPHER:
                await self.photographer_tools.initialize_project(project)
            elif creator.creator_type == CreatorType.BLOGGER:
                await self.blogger_tools.initialize_project(project)
            elif creator.creator_type == CreatorType.INFLUENCER:
                await self.influencer_tools.initialize_project(project)
            elif creator.creator_type == CreatorType.COMEDIAN:
                await self.comedian_tools.initialize_project(project)
            
            logger.info(f"✅ Content project created: {project.title}")
            return project.project_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create content project: {e}")
            raise
    
    async def get_creator_recommendations(self, creator_id: str) -> Dict[str, Any]:
        """Get AI-powered recommendations for a creator"""
        try:
            creator = self.active_creators.get(creator_id)
            if not creator:
                raise ValueError(f"Creator not found: {creator_id}")
            
            recommendations = {}
            
            # Get tool-specific recommendations
            if creator.creator_type == CreatorType.MUSICIAN:
                recommendations = await self.musician_tools.get_recommendations(creator)
            elif creator.creator_type == CreatorType.PHOTOGRAPHER:
                recommendations = await self.photographer_tools.get_recommendations(creator)
            elif creator.creator_type == CreatorType.BLOGGER:
                recommendations = await self.blogger_tools.get_recommendations(creator)
            elif creator.creator_type == CreatorType.INFLUENCER:
                recommendations = await self.influencer_tools.get_recommendations(creator)
            elif creator.creator_type == CreatorType.COMEDIAN:
                recommendations = await self.comedian_tools.get_recommendations(creator)
            
            # Add general recommendations
            growth_insights = await self.growth_tracker.get_growth_insights(creator_id)
            skill_recommendations = await self.skill_mapper.get_skill_recommendations(creator_id)
            
            recommendations.update({
                "growth_insights": growth_insights,
                "skill_recommendations": skill_recommendations,
                "creator_type": creator.creator_type.value,
                "generated_at": datetime.now().isoformat()
            })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to get recommendations for {creator_id}: {e}")
            raise
    
    async def get_creator_analytics(self, creator_id: str, time_range: str = "30d") -> Dict[str, Any]:
        """Get comprehensive analytics for a creator"""
        try:
            creator = self.active_creators.get(creator_id)
            if not creator:
                raise ValueError(f"Creator not found: {creator_id}")
            
            analytics = {
                "creator_id": creator_id,
                "creator_type": creator.creator_type.value,
                "time_range": time_range,
                "generated_at": datetime.now().isoformat()
            }
            
            # Get tool-specific analytics
            if creator.creator_type == CreatorType.MUSICIAN:
                tool_analytics = await self.musician_tools.get_analytics(creator_id, time_range)
            elif creator.creator_type == CreatorType.PHOTOGRAPHER:
                tool_analytics = await self.photographer_tools.get_analytics(creator_id, time_range)
            elif creator.creator_type == CreatorType.BLOGGER:
                tool_analytics = await self.blogger_tools.get_analytics(creator_id, time_range)
            elif creator.creator_type == CreatorType.INFLUENCER:
                tool_analytics = await self.influencer_tools.get_analytics(creator_id, time_range)
            elif creator.creator_type == CreatorType.COMEDIAN:
                tool_analytics = await self.comedian_tools.get_analytics(creator_id, time_range)
            else:
                tool_analytics = {}
            
            # Get growth analytics
            growth_analytics = await self.growth_tracker.get_analytics(creator_id, time_range)
            
            analytics.update({
                "tool_specific": tool_analytics,
                "growth_metrics": growth_analytics,
                "projects_count": len([p for p in self.active_projects.values() if p.creator_id == creator_id])
            })
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Failed to get analytics for {creator_id}: {e}")
            raise
    
    async def get_creator_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a creator"""
        try:
            creator = self.active_creators.get(creator_id)
            if not creator:
                raise ValueError(f"Creator not found: {creator_id}")
            
            dashboard_data = {
                "creator_profile": creator,
                "active_projects": [p for p in self.active_projects.values() if p.creator_id == creator_id],
                "recommendations": await self.get_creator_recommendations(creator_id),
                "analytics": await self.get_creator_analytics(creator_id),
                "skill_assessment": await self.skill_mapper.get_skill_assessment(creator_id),
                "growth_status": await self.growth_tracker.get_current_status(creator_id),
                "generated_at": datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Failed to generate dashboard for {creator_id}: {e}")
            raise
    
    async def get_platform_overview(self) -> Dict[str, Any]:
        """Get platform-wide creator services overview"""
        try:
            overview = {
                "total_creators": len(self.active_creators),
                "creator_breakdown": {creator_type.value: 0 for creator_type in CreatorType},
                "active_projects": len(self.active_projects),
                "content_breakdown": {content_type.value: 0 for content_type in ContentType},
                "generated_at": datetime.now().isoformat()
            }
            
            # Count creators by type
            for creator in self.active_creators.values():
                overview["creator_breakdown"][creator.creator_type.value] += 1
            
            # Count projects by content type
            for project in self.active_projects.values():
                overview["content_breakdown"][project.content_type.value] += 1
            
            return overview
            
        except Exception as e:
            logger.error(f"❌ Failed to generate platform overview: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all creator services"""
        logger.info("Shutting down Creator Services Orchestrator...")
        
        services = [
            ("musician_tools", self.musician_tools),
            ("photographer_tools", self.photographer_tools),
            ("blogger_tools", self.blogger_tools),
            ("influencer_tools", self.influencer_tools),
            ("comedian_tools", self.comedian_tools),
            ("creator_profiler", self.creator_profiler),
            ("skill_mapper", self.skill_mapper),
            ("growth_tracker", self.growth_tracker)
        ]
        
        for service_name, service in services:
            try:
                if service and hasattr(service, 'shutdown'):
                    await service.shutdown()
                    logger.info(f"✅ {service_name} shutdown")
            except Exception as e:
                logger.error(f"❌ Error shutting down {service_name}: {e}")
        
        logger.info("✅ Creator Services Orchestrator shutdown complete")

# Global creator services orchestrator instance
creator_services_orchestrator = CreatorServicesOrchestrator()

async def initialize_creator_services() -> None:
    """Initialize creator services"""
    await creator_services_orchestrator.initialize()

async def shutdown_creator_services() -> None:
    """Shutdown creator services"""
    await creator_services_orchestrator.shutdown()

__all__ = [
    'CreatorType', 'ContentType', 'CreatorProfile', 'ContentProject',
    'CreatorServicesOrchestrator', 'creator_services_orchestrator',
    'initialize_creator_services', 'shutdown_creator_services'
]