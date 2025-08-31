"""IA-Influencer-Agent - AI Agents Module

Ultra-advanced industrial-grade AI agents system for content creators protection and monetization.
Integrates multi-format content processing, intelligent rights management, and automated collaboration matching.

Project Architecture:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → AI protection rights → SEO pro → Matching collaboration → Multi-platform distribution

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
from typing import Dict, List, Optional, Any
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

# Import base classes
from .base import BaseAgent, AgentRequest, AgentResponse
from .agent_manager import AgentManager, agent_manager

# Import core content and collaboration agents
from .content_agent import ContentAgent
from .collaboration_agent import CollaborationAgent
from .protection_agent import ProtectionAgent
from .monetization_agent import MonetizationAgent
from .seo_agent import SEOAgent
from .distribution_agent import DistributionAgent

# Import all collaboration agents (12 total)
from .marketplace_agent import MarketplaceAgent
from .project_management_agent import ProjectManagementAgent
from .communication_agent import CommunicationAgent
from .file_sharing_agent import FileSharingAgent
from .version_control_agent import VersionControlAgent
from .quality_assurance_agent import QualityAssuranceAgent
from .contract_generation_agent import ContractGenerationAgent
from .dispute_resolution_agent import DisputeResolutionAgent
from .skill_matching_agent import SkillMatchingAgent
from .timeline_management_agent import TimelineManagementAgent
from .revenue_sharing_agent import RevenueSharingAgent

# Import processing and AI agents
from .audio_agent import AudioAgent
from .video_agent import VideoAgent
from .image_agent import ImageAgent
from .text_agent import TextAgent
from .nlp_agent import NLPAgent
from .vision_agent import VisionAgent
from .music_agent import MusicAgent
from .ml_agent import MLAgent
from .vector_agent import VectorAgent

# Import platform and business agents
from .platform_agent import PlatformAgent
from .spotify_agent import SpotifyAgent
from .social_media_agent import SocialMediaAgent
from .revenue_agent import RevenueAgent
from .brand_agent import BrandAgent

# Import monitoring and analytics agents
from .analytics_agent import AnalyticsAgent
from .fingerprinting_agent import FingerprintingAgent
from .crawling_agent import CrawlingAgent
from .competitor_monitoring_agent import CompetitorMonitoringAgent
from .market_intelligence_agent import MarketIntelligenceAgent
from .predictive_analytics_agent import PredictiveAnalyticsAgent

# Import compliance and legal agents
from .compliance_agent import ComplianceAgent
from .legal_agent import LegalAgent
from .gdpr_compliance_agent import GDPRComplianceAgent
from .dmca_agent import DMCAAgent
from .audit_trail_agent import AuditTrailAgent
from .fraud_detection_agent import FraudDetectionAgent

# Import content management agents
from .moderation_agent import ModerationAgent
from .quality_agent import QualityAgent
from .recommendation_agent import RecommendationAgent
from .trend_agent import TrendAgent
from .engagement_agent import EngagementAgent

# Import operational agents
from .workflow_agent import WorkflowAgent
from .scheduling_agent import SchedulingAgent
from .notification_agent import NotificationAgent
from .support_agent import SupportAgent
from .creator_onboarding_agent import CreatorOnboardingAgent

# Import infrastructure and technical agents
from .api_gateway_agent import APIGatewayAgent
from .caching_agent import CachingAgent
from .storage_agent import StorageAgent
from .auto_scaling_agent import AutoScalingAgent
from .optimization_agent import OptimizationAgent
from .webhook_agent import WebhookAgent

# Import payment and licensing agents
from .payment_processing_agent import PaymentProcessingAgent
from .licensing_agent import LicensingAgent

# Import blockchain and advanced tech agents
from .blockchain_agent import BlockchainAgent

# Import intelligence and orchestration agents
from .intelligence_agent import IntelligenceAgent

logger = logging.getLogger(__name__)

# Agent registry for dynamic instantiation - Updated with ALL existing agents
AGENT_REGISTRY = {
    # Core content and collaboration agents
    'content_agent': ContentAgent,
    'collaboration_agent': CollaborationAgent,
    'protection_agent': ProtectionAgent,
    'monetization_agent': MonetizationAgent,
    'seo_agent': SEOAgent,
    'distribution_agent': DistributionAgent,
    
    # All 12 Collaboration Agents
    'marketplace_agent': MarketplaceAgent,
    'project_management_agent': ProjectManagementAgent,
    'communication_agent': CommunicationAgent,
    'file_sharing_agent': FileSharingAgent,
    'version_control_agent': VersionControlAgent,
    'quality_assurance_agent': QualityAssuranceAgent,
    'contract_generation_agent': ContractGenerationAgent,
    'dispute_resolution_agent': DisputeResolutionAgent,
    'skill_matching_agent': SkillMatchingAgent,
    'timeline_management_agent': TimelineManagementAgent,
    'revenue_sharing_agent': RevenueSharingAgent,
    
    # Processing and AI agents
    'audio_agent': AudioAgent,
    'video_agent': VideoAgent,
    'image_agent': ImageAgent,
    'text_agent': TextAgent,
    'nlp_agent': NLPAgent,
    'vision_agent': VisionAgent,
    'music_agent': MusicAgent,
    'ml_agent': MLAgent,
    'vector_agent': VectorAgent,
    
    # Platform and business agents
    'platform_agent': PlatformAgent,
    'spotify_agent': SpotifyAgent,
    'social_media_agent': SocialMediaAgent,
    'revenue_agent': RevenueAgent,
    'brand_agent': BrandAgent,
    
    # Monitoring and analytics agents
    'analytics_agent': AnalyticsAgent,
    'fingerprinting_agent': FingerprintingAgent,
    'crawling_agent': CrawlingAgent,
    'competitor_monitoring_agent': CompetitorMonitoringAgent,
    'market_intelligence_agent': MarketIntelligenceAgent,
    'predictive_analytics_agent': PredictiveAnalyticsAgent,
    
    # Compliance and legal agents
    'compliance_agent': ComplianceAgent,
    'legal_agent': LegalAgent,
    'gdpr_compliance_agent': GDPRComplianceAgent,
    'dmca_agent': DMCAAgent,
    'audit_trail_agent': AuditTrailAgent,
    'fraud_detection_agent': FraudDetectionAgent,
    
    # Content management agents
    'moderation_agent': ModerationAgent,
    'quality_agent': QualityAgent,
    'recommendation_agent': RecommendationAgent,
    'trend_agent': TrendAgent,
    'engagement_agent': EngagementAgent,
    
    # Operational agents
    'workflow_agent': WorkflowAgent,
    'scheduling_agent': SchedulingAgent,
    'notification_agent': NotificationAgent,
    'support_agent': SupportAgent,
    'creator_onboarding_agent': CreatorOnboardingAgent,
    
    # Infrastructure and technical agents
    'api_gateway_agent': APIGatewayAgent,
    'caching_agent': CachingAgent,
    'storage_agent': StorageAgent,
    'auto_scaling_agent': AutoScalingAgent,
    'optimization_agent': OptimizationAgent,
    'webhook_agent': WebhookAgent,
    
    # Payment and licensing agents
    'payment_processing_agent': PaymentProcessingAgent,
    'licensing_agent': LicensingAgent,
    
    # Blockchain and advanced tech agents
    'blockchain_agent': BlockchainAgent,
    
    # Intelligence and orchestration agents
    'intelligence_agent': IntelligenceAgent
}

# Manager registry for specialized agent management
MANAGER_REGISTRY = {
    'analytics_agent': 'AnalyticsAgentManager',
    'moderation_agent': 'ModerationAgentManager', 
    'recommendation_agent': 'RecommendationAgentManager',
    'support_agent': 'SupportAgentManager',
    'social_media_agent': 'SocialMediaAgentManager',
    'vector_agent': 'VectorAgentManager',
    'webhook_agent': 'WebhookAgentManager',
    'workflow_agent': 'WorkflowAgentManager',
    'fingerprinting_agent': 'FingerprintingAgentManager',
    'intelligence_agent': 'IntelligenceAgentManager'
}

class AgentFactory:
    """Factory for creating agent instances"""
    
    @staticmethod
    async def create_agent(
        agent_type: str, 
        agent_id: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[BaseAgent]:
        """Create agent instance by type"""
        if agent_type not in AGENT_REGISTRY:
            logger.error(f"Unknown agent type: {agent_type}")
            return None
        
        try:
            agent_class = AGENT_REGISTRY[agent_type]
            agent = agent_class(agent_id=agent_id, config=config)
            
            # Initialize the agent
            if await agent.initialize():
                logger.info(f"Successfully created {agent_type} with ID {agent_id}")
                return agent
            else:
                logger.error(f"Failed to initialize {agent_type} with ID {agent_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create {agent_type}: {e}")
            return None
    
    @staticmethod
    def create_manager(manager_type: str) -> Optional[Any]:
        """Create manager instance by type"""
        if manager_type not in MANAGER_REGISTRY:
            logger.warning(f"No specialized manager for {manager_type}, using default")
            return None
        
        try:
            manager_class = MANAGER_REGISTRY[manager_type]
            return manager_class()
            
        except Exception as e:
            logger.error(f"Failed to create manager {manager_type}: {e}")
            return None

async def initialize_agent_system():
    """Initialize the complete agent system"""
    try:
        # Start the global agent manager
        await agent_manager.start()
        
        # Register agent classes with the manager
        for agent_type, agent_class in AGENT_REGISTRY.items():
            await agent_manager.register_agent_pool(
                agent_type=agent_type,
                agent_class=agent_class
            )
        
        logger.info("Agent system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize agent system: {e}")
        return False

async def shutdown_agent_system():
    """Shutdown the complete agent system"""
    try:
        await agent_manager.stop()
        logger.info("Agent system shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during agent system shutdown: {e}")

# Utility functions
def get_available_agent_types() -> List[str]:
    """Get list of available agent types"""
    return list(AGENT_REGISTRY.keys())

def get_agent_info(agent_type: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific agent type"""
    if agent_type not in AGENT_REGISTRY:
        return None
    
    agent_class = AGENT_REGISTRY[agent_type]
    return {
        'type': agent_type,
        'class_name': agent_class.__name__,
        'module': agent_class.__module__,
        'description': agent_class.__doc__.split('\n')[0] if agent_class.__doc__ else "No description",
        'has_specialized_manager': agent_type in MANAGER_REGISTRY
    }

# Export main components
__all__ = [
    # Base classes
    'BaseAgent',
    'AgentRequest', 
    'AgentResponse',
    
    # Agent manager
    'AgentManager',
    'agent_manager',
    
    # Core content and collaboration agents
    'ContentAgent',
    'CollaborationAgent',
    'ProtectionAgent',
    'MonetizationAgent',
    'SEOAgent',
    'DistributionAgent',
    
    # All 12 Collaboration Agents
    'MarketplaceAgent',
    'ProjectManagementAgent',
    'CommunicationAgent',
    'FileSharingAgent',
    'VersionControlAgent',
    'QualityAssuranceAgent',
    'ContractGenerationAgent',
    'DisputeResolutionAgent',
    'SkillMatchingAgent',
    'TimelineManagementAgent',
    'RevenueSharingAgent',
    
    # Processing and AI agents
    'AudioAgent',
    'VideoAgent',
    'ImageAgent',
    'TextAgent',
    'NLPAgent',
    'VisionAgent',
    'MusicAgent',
    'MLAgent',
    'VectorAgent',
    
    # Platform and business agents
    'PlatformAgent',
    'SpotifyAgent',
    'SocialMediaAgent',
    'RevenueAgent',
    'BrandAgent',
    
    # Monitoring and analytics agents
    'AnalyticsAgent',
    'FingerprintingAgent',
    'CrawlingAgent',
    'CompetitorMonitoringAgent',
    'MarketIntelligenceAgent',
    'PredictiveAnalyticsAgent',
    
    # Compliance and legal agents
    'ComplianceAgent',
    'LegalAgent',
    'GDPRComplianceAgent',
    'DMCAAgent',
    'AuditTrailAgent',
    'FraudDetectionAgent',
    
    # Content management agents
    'ModerationAgent',
    'QualityAgent',
    'RecommendationAgent',
    'TrendAgent',
    'EngagementAgent',
    
    # Operational agents
    'WorkflowAgent',
    'SchedulingAgent',
    'NotificationAgent',
    'SupportAgent',
    'CreatorOnboardingAgent',
    
    # Infrastructure and technical agents
    'APIGatewayAgent',
    'CachingAgent',
    'StorageAgent',
    'AutoScalingAgent',
    'OptimizationAgent',
    'WebhookAgent',
    
    # Payment and licensing agents
    'PaymentProcessingAgent',
    'LicensingAgent',
    
    # Blockchain and advanced tech agents
    'BlockchainAgent',
    
    # Intelligence and orchestration agents
    'IntelligenceAgent',
    
    # Factory and utilities
    'AgentFactory',
    'AGENT_REGISTRY',
    'MANAGER_REGISTRY',
    'initialize_agent_system',
    'shutdown_agent_system',
    'get_available_agent_types',
    'get_agent_info'
]