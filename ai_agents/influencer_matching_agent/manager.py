"""Influencer Matching Manager - Ultra-Advanced Enterprise System

Advanced enterprise-level influencer matching orchestration system for managing complex
creator discovery workflows, brand alignment analysis, and collaboration optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from .core.matching_engine import MatchingEngine, MatchingJob, MatchingResult, CollaborationType

logger = logging.getLogger(__name__)

class InfluencerMatchingSystemStatus(Enum):
    """
System status levels"""

    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class MatchingCampaign:
    """Influencer matching campaign configuration"""
    campaign_id: str
    name: str
    brand_requirements: Dict[str, Any]
    collaboration_types: List[str]
    target_platforms: List[str]
    budget_allocation: Dict[str, float]
    goals: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "draft"

@dataclass
class MatchingMetrics:
    """Influencer matching performance metrics"""
    total_matches_found: int = 0
    successful_collaborations: int = 0
    average_matching_score: float = 0.0
    campaign_count: int = 0
    success_rate: float = 0.0
    processing_time: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class InfluencerMatchingManager:
    """
    Enterprise Influencer Matching Management System
    
    Advanced orchestration system for influencer discovery and matching with:
    - AI-powered creator compatibility analysis
    - Multi-platform creator discovery
    - Brand alignment optimization
    - Collaboration prediction and optimization
    - Performance monitoring and reporting
    """
    
    def __init__(self, manager_id: str = "influencer_matching_manager", config: Optional[Dict[str, Any]] = None):
        self.manager_id = manager_id
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize core components
        self.matching_engine = MatchingEngine(config.get('engine_config', {}))
        self.active_campaigns: Dict[str, MatchingCampaign] = {}
        self.campaign_results: Dict[str, Dict[str, Any]] = {}
        self.system_metrics = MatchingMetrics()
        
        # Configuration
        self.max_concurrent_campaigns = config.get('max_concurrent_campaigns', 10)
        self.auto_optimization = config.get('auto_optimization', True)
        
        # System status
        self.status = InfluencerMatchingSystemStatus.INITIALIZING
        self.startup_time = datetime.now()
        
        self.logger.info(f"Influencer Matching Manager {manager_id} initialized")

    async def initialize(self) -> None:
        """Initialize the influencer matching system"""
        try:
            self.logger.info("Initializing Influencer Matching Manager...")
            self.status = InfluencerMatchingSystemStatus.READY
            self.logger.info("Influencer Matching Manager initialization completed")
        except Exception as e:
            self.status = InfluencerMatchingSystemStatus.ERROR
            self.logger.error(f"Initialization failed: {str(e)}")
            raise

    async def find_creators(
        self,
        brand_requirements: Dict[str, Any],
        collaboration_type: str = "sponsored_post",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Find influencers matching brand requirements
        
        Args:
            brand_requirements: Brand requirements and preferences
            collaboration_type: Type of collaboration desired
            options: Additional matching options
            
        Returns:
            Matching results with compatible creators
        """
        try:
            # Perform influencer matching
            result = await self.matching_engine.find_matching_creators(
                brand_requirements=brand_requirements,
                collaboration_type=collaboration_type,
                options=options
            )
            
            if not result.success:
                return {
                    'success': False,
                    'error': result.error_message,
                    'creators': []
                }
            
            # Process and enhance results
            processed_creators = []
            for creator in result.matched_creators:
                creator_data = {
                    'creator_id': creator['creator_id'],
                    'name': creator['name'],
                    'handle': creator['handle'],
                    'platforms': creator['platforms'],
                    'follower_counts': creator['follower_counts'],
                    'engagement_rates': creator['engagement_rates'],
                    'content_categories': creator['content_categories'],
                    'matching_score': result.matching_scores.get(creator['creator_id'], 0),
                    'brand_safety_score': creator['brand_safety_score'],
                    'authenticity_score': creator['authenticity_score'],
                    'estimated_rates': creator['rates']
                }
                processed_creators.append(creator_data)
            
            # Sort by matching score
            processed_creators.sort(key=lambda x: x['matching_score'], reverse=True)
            
            # Update system metrics
            self.system_metrics.total_matches_found += len(processed_creators)
            self.system_metrics.last_updated = datetime.now()
            
            return {
                'success': True,
                'creators': processed_creators,
                'matching_summary': {
                    'total_found': len(processed_creators),
                    'top_score': processed_creators[0]['matching_score'] if processed_creators else 0,
                    'average_score': sum(c['matching_score'] for c in processed_creators) / len(processed_creators) if processed_creators else 0
                },
                'recommendations': result.recommendations,
                'processing_time': result.processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Creator matching failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'creators': []
            }

    async def create_campaign(
        self,
        campaign_config: Dict[str, Any],
        auto_start: bool = False
    ) -> MatchingCampaign:
        """Create a new influencer matching campaign"""
        campaign_id = f"matching_campaign_{datetime.now().timestamp()}"
        
        campaign = MatchingCampaign(
            campaign_id=campaign_id,
            name=campaign_config.get('name', f'Campaign {campaign_id}'),
            brand_requirements=campaign_config.get('brand_requirements', {}),
            collaboration_types=campaign_config.get('collaboration_types', ['sponsored_post']),
            target_platforms=campaign_config.get('target_platforms', []),
            budget_allocation=campaign_config.get('budget_allocation', {}),
            goals=campaign_config.get('goals', [])
        )
        
        self.active_campaigns[campaign_id] = campaign
        
        if auto_start:
            await self.start_campaign(campaign_id)
        
        self.logger.info(f"Matching campaign {campaign_id} created")
        return campaign

    async def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Start an influencer matching campaign"""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        try:
            campaign.status = "running"
            start_time = datetime.now()
            
            # Find creators for each collaboration type
            all_results = {}
            for collab_type in campaign.collaboration_types:
                result = await self.find_creators(
                    brand_requirements=campaign.brand_requirements,
                    collaboration_type=collab_type,
                    options={'platforms': campaign.target_platforms}
                )
                all_results[collab_type] = result
            
            # Store campaign results
            campaign_results = {
                'campaign_id': campaign_id,
                'results_by_type': all_results,
                'execution_time': (datetime.now() - start_time).total_seconds(),
                'status': 'completed'
            }
            
            self.campaign_results[campaign_id] = campaign_results
            campaign.status = "completed"
            
            # Update system metrics
            self.system_metrics.campaign_count += 1
            
            self.logger.info(f"Matching campaign {campaign_id} completed successfully")
            return campaign_results
            
        except Exception as e:
            campaign.status = "failed"
            self.logger.error(f"Campaign {campaign_id} failed: {str(e)}")
            return {'campaign_id': campaign_id, 'error': str(e), 'status': 'failed'}

    async def analyze_creator_compatibility(
        self,
        creator_id: str,
        brand_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze detailed compatibility between a creator and brand"""
        # This would interface with the matching engine's analyze_creator_compatibility method
        # For now, return a simplified analysis
        return {
            'creator_id': creator_id,
            'overall_compatibility': 0.85,
            'category_alignment': 0.9,
            'audience_overlap': 0.8,
            'engagement_quality': 0.85,
            'brand_safety': 0.95,
            'authenticity': 0.88,
            'strengths': [
                "High audience engagement rates",
                "Excellent brand safety record",
                "Strong content category alignment"
            ],
            'concerns': [],
            'recommendations': [
                "Ideal candidate for long-term partnership",
                "Consider exclusive collaboration terms"
            ]
        }

    async def get_campaign_status(self, campaign_id: str) -> Optional[str]:
        """Get the status of a campaign"""
        campaign = self.active_campaigns.get(campaign_id)
        return campaign.status if campaign else None

    async def get_campaign_results(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
Get the results of a completed campaign"""
        return self.campaign_results.get(campaign_id)

    async def get_system_metrics(self) -> MatchingMetrics:
        """
Get current system metrics"""
        return self.system_metrics

    def get_active_campaigns(self) -> Dict[str, MatchingCampaign]:
        """
Get all active campaigns"""
        return self.active_campaigns.copy()

    async def get_creator_database_stats(self) -> Dict[str, Any]:
        """
Get statistics about the creator database"""
        # This would interface with the matching engine
        return {
            'total_creators': 50,  # Placeholder
            'tier_distribution': {'nano': 20, 'micro': 20, 'macro': 8, 'mega': 2},
            'platform_distribution': {'instagram': 45, 'youtube': 35, 'tiktok': 30, 'twitter': 25},
            'category_distribution': {'lifestyle': 15, 'technology': 10, 'fashion': 12, 'gaming': 8}
        }