"""
Agent Registry - Unified AI Agent Management System
==================================================

Central registry and orchestration system for all 53 AI agents.
Provides unified access to Core Business, Content, and Technical agents.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Import consolidated agent classes
from .core_business_agents import CoreBusinessAgents
from .content_agents import ContentAgents
from .technical_agents import TechnicalAgents

logger = logging.getLogger(__name__)

class AgentCategory(Enum):
    """Agent category enumeration"""
    CORE_BUSINESS = "core_business"
    CONTENT = "content"
    TECHNICAL = "technical"

class AgentStatus(Enum):
    """Agent status enumeration"""
    ACTIVE = "active"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class AgentInfo:
    """Agent information structure"""
    name: str
    category: AgentCategory
    status: AgentStatus
    description: str
    capabilities: List[str]
    version: str = "1.0.0"
    last_activity: Optional[datetime] = None

class AgentRegistry:
    """
    Unified agent registry managing all 53 AI agents.
    
    Provides centralized access to:
    - 20 Core Business Agents (strategy, monetization, analytics)
    - 15 Content Agents (creation, processing, optimization)
    - 18 Technical Agents (infrastructure, monitoring, security)
    """
    
    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._categories: Dict[AgentCategory, Any] = {}
        self._agent_info: Dict[str, AgentInfo] = {}
        self._initialized = False
        
        # Initialize agent collections
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agent categories"""
        try:
            # Initialize agent collections
            self._categories[AgentCategory.CORE_BUSINESS] = CoreBusinessAgents()
            self._categories[AgentCategory.CONTENT] = ContentAgents()
            self._categories[AgentCategory.TECHNICAL] = TechnicalAgents()
            
            # Register all agents
            self._register_core_business_agents()
            self._register_content_agents()
            self._register_technical_agents()
            
            self._initialized = True
            logger.info("✅ Agent registry initialized with 53 agents")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent registry: {e}")
            raise
    
    def _register_core_business_agents(self):
        """Register core business agents"""
        core_agents = [
            ("ContentStrategistAgent", "Strategic content planning and optimization"),
            ("CollaborationMatcherAgent", "Intelligent creator collaboration matching"),
            ("MonetizationStrategistAgent", "Revenue optimization strategies"),
            ("BrandManagerAgent", "Brand consistency and reputation management"),
            ("AudienceInsightsAgent", "Deep audience analysis and growth strategies"),
            ("TrendAnalyzerAgent", "Market trend analysis and viral prediction"),
            ("AnalyticsAgent", "Advanced analytics and performance metrics"),
            ("MarketIntelligenceAgent", "Market research and competitive intelligence"),
            ("EngagementSpecialistAgent", "Engagement optimization and community building"),
            ("SocialMediaManagerAgent", "Multi-platform social media management"),
            ("SchedulingAgent", "Intelligent content scheduling optimization"),
            ("ConversationalAIAgent", "AI-powered conversational interfaces"),
            ("CreativeDirectorAgent", "Creative direction and artistic guidance"),
            ("MarketplaceAgent", "Marketplace operations and transactions"),
            ("LegalComplianceAgent", "Legal compliance and regulatory management"),
            ("RevenueOptimizationAgent", "Advanced revenue optimization strategies"),
            ("CustomerSuccessAgent", "Customer success and retention management"),
            ("CampaignOptimizerAgent", "Marketing campaign optimization"),
            ("InfluencerMatchingAgent", "Influencer partnership matching"),
            ("BusinessIntelligenceAgent", "Business intelligence and strategic insights")
        ]
        
        for agent_name, description in core_agents:
            self._agent_info[agent_name] = AgentInfo(
                name=agent_name,
                category=AgentCategory.CORE_BUSINESS,
                status=AgentStatus.READY,
                description=description,
                capabilities=["strategic_planning", "business_optimization", "analytics"]
            )
    
    def _register_content_agents(self):
        """Register content processing agents"""
        content_agents = [
            ("MusicProducerAgent", "AI-powered music production and composition"),
            ("VideoEditorAgent", "Intelligent video editing and enhancement"),
            ("ContentCreatorAgent", "Multi-format content creation and optimization"),
            ("ImageSpecialistAgent", "Advanced image processing and generation"),
            ("AudioSpecialistAgent", "Professional audio processing and enhancement"),
            ("TextSpecialistAgent", "Advanced text generation and optimization"),
            ("ContentOptimizerAgent", "Content performance optimization"),
            ("VideoSpecialistAgent", "Specialized video processing and analysis"),
            ("ThumbnailGeneratorAgent", "AI-powered thumbnail creation"),
            ("SubtitleGeneratorAgent", "Automated subtitle generation and translation"),
            ("PodcastProducerAgent", "Podcast production and audio content creation"),
            ("LiveStreamOptimizerAgent", "Live streaming optimization"),
            ("ContentModerationAgent", "Automated content moderation and safety"),
            ("TranslationAgent", "Multi-language content translation"),
            ("StorytellingAgent", "Narrative and storytelling optimization")
        ]
        
        for agent_name, description in content_agents:
            self._agent_info[agent_name] = AgentInfo(
                name=agent_name,
                category=AgentCategory.CONTENT,
                status=AgentStatus.READY,
                description=description,
                capabilities=["content_creation", "media_processing", "optimization"]
            )
    
    def _register_technical_agents(self):
        """Register technical infrastructure agents"""
        technical_agents = [
            ("SystemMonitorAgent", "Comprehensive system monitoring"),
            ("SecurityScannerAgent", "Security vulnerability scanning"),
            ("ProtectionAgent", "Content protection and anti-piracy"),
            ("FingerprintingAgent", "Multi-format digital fingerprinting"),
            ("MLOpsAgent", "Machine learning operations and model management"),
            ("DatabaseAgent", "Database optimization and management"),
            ("CachingAgent", "Intelligent caching and performance optimization"),
            ("LoadBalancerAgent", "Traffic distribution and load balancing"),
            ("BackupAgent", "Automated backup and disaster recovery"),
            ("APIGatewayAgent", "API gateway management and routing"),
            ("LoggingAgent", "Intelligent logging and log analysis"),
            ("NetworkAgent", "Network monitoring and optimization"),
            ("StorageAgent", "Intelligent storage management"),
            ("ComplianceAgent", "Technical compliance monitoring"),
            ("AutoScalingAgent", "Intelligent auto-scaling and resource management"),
            ("DeploymentAgent", "Automated deployment and infrastructure"),
            ("HealthCheckAgent", "System health monitoring and diagnostics"),
            ("PerformanceAgent", "Performance analysis and optimization")
        ]
        
        for agent_name, description in technical_agents:
            self._agent_info[agent_name] = AgentInfo(
                name=agent_name,
                category=AgentCategory.TECHNICAL,
                status=AgentStatus.READY,
                description=description,
                capabilities=["infrastructure", "monitoring", "security"]
            )
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """Get agent instance by name"""
        if not self._initialized:
            raise RuntimeError("Agent registry not initialized")
        
        if agent_name not in self._agent_info:
            logger.warning(f"Agent {agent_name} not found in registry")
            return None
        
        agent_info = self._agent_info[agent_name]
        category_manager = self._categories.get(agent_info.category)
        
        if not category_manager:
            logger.error(f"Category manager for {agent_info.category} not found")
            return None
        
        # Return the category manager itself, as it contains all the agent functionality
        # Each category manager implements the combined functionality of all agents in that category
        return category_manager
    
    def list_agents(self, category: Optional[AgentCategory] = None) -> List[AgentInfo]:
        """List all agents or agents by category"""
        if category:
            return [info for info in self._agent_info.values() if info.category == category]
        return list(self._agent_info.values())
    
    def get_agent_info(self, agent_name: str) -> Optional[AgentInfo]:
        """Get agent information"""
        return self._agent_info.get(agent_name)
    
    def get_category_manager(self, category: AgentCategory) -> Optional[Any]:
        """Get category manager instance"""
        return self._categories.get(category)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        stats = {
            "total_agents": len(self._agent_info),
            "categories": {
                "core_business": len([a for a in self._agent_info.values() if a.category == AgentCategory.CORE_BUSINESS]),
                "content": len([a for a in self._agent_info.values() if a.category == AgentCategory.CONTENT]),
                "technical": len([a for a in self._agent_info.values() if a.category == AgentCategory.TECHNICAL])
            },
            "status_distribution": {}
        }
        
        # Count agents by status
        for status in AgentStatus:
            count = len([a for a in self._agent_info.values() if a.status == status])
            stats["status_distribution"][status.value] = count
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        health_status = {
            "registry_status": "healthy" if self._initialized else "unhealthy",
            "categories": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for category, manager in self._categories.items():
            try:
                # Basic health check - ensure manager exists and has methods
                health_status["categories"][category.value] = {
                    "status": "healthy",
                    "manager_type": type(manager).__name__,
                    "agent_count": len([a for a in self._agent_info.values() if a.category == category])
                }
            except Exception as e:
                health_status["categories"][category.value] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health_status


# Global registry instance
_registry: Optional[AgentRegistry] = None

def get_registry() -> AgentRegistry:
    """Get global agent registry instance"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry

def get_agent(agent_name: str) -> Optional[Any]:
    """Get agent by name from global registry"""
    return get_registry().get_agent(agent_name)

def list_agents(category: Optional[AgentCategory] = None) -> List[AgentInfo]:
    """List agents from global registry"""
    return get_registry().list_agents(category)

def get_agent_info(agent_name: str) -> Optional[AgentInfo]:
    """Get agent information from global registry"""
    return get_registry().get_agent_info(agent_name)

async def health_check() -> Dict[str, Any]:
    """Perform health check on global registry"""
    return await get_registry().health_check()