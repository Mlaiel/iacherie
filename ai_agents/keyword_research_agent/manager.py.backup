"""Keyword Research Manager - Ultra-Advanced Enterprise System

Advanced enterprise-level keyword research orchestration system for managing complex
keyword analysis workflows, multi-platform optimization, and ROI tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from .core.keyword_engine import KeywordEngine, KeywordJob, KeywordResult, KeywordData

logger = logging.getLogger(__name__)

class KeywordResearchSystemStatus(Enum):
    """System status levels"""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class KeywordResearchCampaign:
    """Keyword research campaign configuration"""
    campaign_id: str
    name: str
    seed_keywords: List[str]
    target_platforms: List[str]
    target_language: str = "en"
    target_location: str = "global"
    content_type: str = "general"
    goals: List[str] = field(default_factory=list)
    budget: Optional[float] = None
    timeline: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "draft"

@dataclass
class KeywordResearchMetrics:
    """Keyword research performance metrics"""
    total_keywords_discovered: int = 0
    high_volume_keywords: int = 0
    low_competition_keywords: int = 0
    long_tail_keywords: int = 0
    average_difficulty_score: float = 0.0
    campaign_count: int = 0
    success_rate: float = 0.0
    processing_time: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class KeywordResearchManager:
    """
    Enterprise Keyword Research Management System
    
    Advanced orchestration system for keyword research campaigns with:
    - Multi-platform keyword discovery
    - Intelligent competition analysis
    - Real-time search volume tracking
    - Automated optimization suggestions
    - Performance monitoring and reporting
    """
    
    def __init__(self, manager_id: str = "keyword_research_manager", config: Optional[Dict[str, Any]] = None):
        self.manager_id = manager_id
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize core components
        self.keyword_engine = KeywordEngine(config.get('engine_config', {}))
        self.active_campaigns: Dict[str, KeywordResearchCampaign] = {}
        self.campaign_results: Dict[str, Dict[str, Any]] = {}
        self.system_metrics = KeywordResearchMetrics()
        
        # Configuration
        self.max_concurrent_campaigns = config.get('max_concurrent_campaigns', 10)
        self.default_campaign_duration = config.get('default_campaign_duration', 30)  # days
        self.auto_optimization = config.get('auto_optimization', True)
        
        # System status
        self.status = KeywordResearchSystemStatus.INITIALIZING
        self.startup_time = datetime.now()
        
        self.logger.info(f"Keyword Research Manager {manager_id} initialized")

    async def initialize(self) -> None:
        """Initialize the keyword research system"""
        try:
            self.logger.info("Initializing Keyword Research Manager...")
            
            # Validate configuration
            await self._validate_configuration()
            
            # Set up monitoring
            await self._setup_monitoring()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.status = KeywordResearchSystemStatus.READY
            self.logger.info("Keyword Research Manager initialization completed")
            
        except Exception as e:
            self.status = KeywordResearchSystemStatus.ERROR
            self.logger.error(f"Initialization failed: {str(e)}")
            raise

    async def create_campaign(
        self,
        campaign_config: Dict[str, Any],
        auto_start: bool = False
    ) -> KeywordResearchCampaign:
        """
        Create a new keyword research campaign
        
        Args:
            campaign_config: Campaign configuration
            auto_start: Whether to start the campaign immediately
            
        Returns:
            Created campaign object
        """
        campaign_id = f"campaign_{datetime.now().timestamp()}"
        
        campaign = KeywordResearchCampaign(
            campaign_id=campaign_id,
            name=campaign_config.get('name', f'Campaign {campaign_id}'),
            seed_keywords=campaign_config.get('seed_keywords', []),
            target_platforms=campaign_config.get('target_platforms', ['google']),
            target_language=campaign_config.get('target_language', 'en'),
            target_location=campaign_config.get('target_location', 'global'),
            content_type=campaign_config.get('content_type', 'general'),
            goals=campaign_config.get('goals', []),
            budget=campaign_config.get('budget'),
            timeline=campaign_config.get('timeline')
        )
        
        self.active_campaigns[campaign_id] = campaign
        
        if auto_start:
            await self.start_campaign(campaign_id)
        
        self.logger.info(f"Campaign {campaign_id} created")
        return campaign

    async def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Start a keyword research campaign
        
        Args:
            campaign_id: ID of the campaign to start
            
        Returns:
            Campaign execution results
        """
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        try:
            campaign.status = "running"
            start_time = datetime.now()
            
            # Perform keyword research
            research_result = await self.keyword_engine.research_keywords(
                seed_keywords=campaign.seed_keywords,
                options={
                    'language': campaign.target_language,
                    'location': campaign.target_location,
                    'content_type': campaign.content_type,
                    'platforms': campaign.target_platforms
                }
            )
            
            # Process and analyze results
            processed_results = await self._process_campaign_results(campaign, research_result)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(processed_results)
            
            # Update campaign results
            campaign_results = {
                'campaign_id': campaign_id,
                'research_data': processed_results,
                'optimization_suggestions': optimization_suggestions,
                'execution_time': (datetime.now() - start_time).total_seconds(),
                'status': 'completed'
            }
            
            self.campaign_results[campaign_id] = campaign_results
            campaign.status = "completed"
            
            # Update system metrics
            await self._update_system_metrics(campaign_results)
            
            self.logger.info(f"Campaign {campaign_id} completed successfully")
            return campaign_results
            
        except Exception as e:
            campaign.status = "failed"
            error_results = {
                'campaign_id': campaign_id,
                'error': str(e),
                'status': 'failed'
            }
            self.campaign_results[campaign_id] = error_results
            self.logger.error(f"Campaign {campaign_id} failed: {str(e)}")
            return error_results

    async def analyze_keywords(
        self,
        keywords: List[str],
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform detailed keyword analysis
        
        Args:
            keywords: List of keywords to analyze
            analysis_options: Analysis configuration options
            
        Returns:
            Comprehensive keyword analysis results
        """
        options = analysis_options or {}
        
        # Perform keyword research
        research_result = await self.keyword_engine.research_keywords(
            seed_keywords=keywords,
            options=options
        )
        
        if not research_result.success:
            return {
                'success': False,
                'error': research_result.error_message,
                'keywords': []
            }
        
        # Process and categorize keywords
        processed_keywords = []
        for keyword_data in research_result.keywords:
            keyword = keyword_data['keyword']
            
            processed_keyword = {
                'keyword': keyword,
                'search_volume': research_result.search_volume_data.get(keyword, {}).get('monthly_volume', 0),
                'competition': research_result.competition_analysis.get(keyword, {}).get('competition_score', 0),
                'difficulty': research_result.difficulty_scores.get(keyword, 0),
                'trend': research_result.trend_data.get(keyword, {}).get('trend_direction', 'unknown'),
                'intent': keyword_data.get('intent', 'unknown'),
                'type': keyword_data.get('type', 'unknown'),
                'opportunities': self._identify_keyword_opportunities(keyword_data, research_result)
            }
            processed_keywords.append(processed_keyword)
        
        # Sort by opportunity score
        processed_keywords.sort(key=lambda x: len(x['opportunities']), reverse=True)
        
        return {
            'success': True,
            'keywords': processed_keywords,
            'summary': {
                'total_keywords': len(processed_keywords),
                'high_opportunity': len([k for k in processed_keywords if len(k['opportunities']) >= 3]),
                'low_competition': len([k for k in processed_keywords if k['competition'] < 0.3]),
                'high_volume': len([k for k in processed_keywords if k['search_volume'] > 1000])
            },
            'suggestions': research_result.suggestions
        }

    def _identify_keyword_opportunities(
        self,
        keyword_data: Dict[str, Any],
        research_result: KeywordResult
    ) -> List[str]:
        """Identify opportunities for a specific keyword"""
        opportunities = []
        keyword = keyword_data['keyword']
        
        # Check search volume vs competition
        volume_data = research_result.search_volume_data.get(keyword, {})
        competition_data = research_result.competition_analysis.get(keyword, {})
        
        monthly_volume = volume_data.get('monthly_volume', 0)
        competition_score = competition_data.get('competition_score', 0)
        
        if monthly_volume > 1000 and competition_score < 0.3:
            opportunities.append("high_volume_low_competition")
        
        if keyword_data.get('type') == 'long_tail':
            opportunities.append("long_tail_opportunity")
        
        if keyword_data.get('intent') == 'transactional':
            opportunities.append("commercial_opportunity")
        
        # Check trend data
        trend_data = research_result.trend_data.get(keyword, {})
        if trend_data.get('trend_direction') == 'growing':
            opportunities.append("trending_up")
        
        return opportunities

    async def get_campaign_status(self, campaign_id: str) -> Optional[str]:
        """Get the status of a campaign"""
        campaign = self.active_campaigns.get(campaign_id)
        return campaign.status if campaign else None

    async def get_campaign_results(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get the results of a completed campaign"""
        return self.campaign_results.get(campaign_id)

    async def get_system_metrics(self) -> KeywordResearchMetrics:
        """Get current system metrics"""
        return self.system_metrics

    async def _process_campaign_results(
        self,
        campaign: KeywordResearchCampaign,
        research_result: KeywordResult
    ) -> Dict[str, Any]:
        """Process campaign results for optimization"""
        processed_data = {
            'total_keywords': len(research_result.keywords),
            'keyword_categories': {},
            'performance_insights': {},
            'platform_optimization': {}
        }
        
        # Categorize keywords
        for keyword_data in research_result.keywords:
            keyword_type = keyword_data.get('type', 'unknown')
            intent = keyword_data.get('intent', 'unknown')
            
            if keyword_type not in processed_data['keyword_categories']:
                processed_data['keyword_categories'][keyword_type] = []
            processed_data['keyword_categories'][keyword_type].append(keyword_data)
        
        # Generate platform-specific recommendations
        for platform in campaign.target_platforms:
            processed_data['platform_optimization'][platform] = {
                'recommended_keywords': research_result.keywords[:10],  # Top 10
                'optimization_strategy': f"Focus on {platform}-specific optimization",
                'content_suggestions': [
                    f"Create content targeting {platform} audience",
                    f"Optimize for {platform} search algorithms"
                ]
            }
        
        return processed_data

    async def _generate_optimization_suggestions(
        self,
        processed_results: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization suggestions based on results"""
        suggestions = []
        
        total_keywords = processed_results.get('total_keywords', 0)
        
        if total_keywords > 50:
            suggestions.append("Consider focusing on top 20-30 high-opportunity keywords")
        
        keyword_categories = processed_results.get('keyword_categories', {})
        if 'long_tail' in keyword_categories and len(keyword_categories['long_tail']) > 10:
            suggestions.append("Strong long-tail keyword opportunities detected")
        
        suggestions.extend([
            "Monitor keyword performance weekly",
            "Create content clusters around main topics",
            "Track competitor keyword strategies",
            "Optimize for mobile search patterns"
        ])
        
        return suggestions

    async def _update_system_metrics(self, campaign_results: Dict[str, Any]) -> None:
        """Update system performance metrics"""
        if campaign_results.get('status') == 'completed':
            research_data = campaign_results.get('research_data', {})
            
            self.system_metrics.total_keywords_discovered += research_data.get('total_keywords', 0)
            self.system_metrics.campaign_count += 1
            self.system_metrics.success_rate = (
                self.system_metrics.campaign_count / 
                max(1, len(self.campaign_results))
            )
            self.system_metrics.last_updated = datetime.now()

    async def _validate_configuration(self) -> None:
        """Validate system configuration"""
        required_configs = ['max_concurrent_campaigns']
        for config_key in required_configs:
            if config_key not in self.config:
                self.logger.warning(f"Missing configuration: {config_key}")

    async def _setup_monitoring(self) -> None:
        """Set up system monitoring"""
        self.logger.info("Setting up keyword research monitoring")

    async def _start_background_tasks(self) -> None:
        """Start background processing tasks"""
        self.logger.info("Starting background tasks")

    def get_active_campaigns(self) -> Dict[str, KeywordResearchCampaign]:
        """Get all active campaigns"""
        return self.active_campaigns.copy()

    async def cancel_campaign(self, campaign_id: str) -> bool:
        """Cancel a running campaign"""
        campaign = self.active_campaigns.get(campaign_id)
        if campaign and campaign.status == "running":
            campaign.status = "cancelled"
            self.logger.info(f"Campaign {campaign_id} cancelled")
            return True
        return False