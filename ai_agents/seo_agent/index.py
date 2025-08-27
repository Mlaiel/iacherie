"""
SEO Agent Index - Industrial-Grade Central Entry Point for SEO System

Main orchestration hub providing unified access to all enterprise SEO components,
advanced workflow automation, and comprehensive SEO intelligence systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Project Team Specializations:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + AI Prompt Engineer
- Expert: Fahed Mlaiel <mlaiel@live.de>

🚨 STRONG WARNING FOR COPYRIGHT VIOLATORS:
Any attempt to steal, copy, reverse-engineer, or commercialize this code without explicit written authorization 
will result in immediate legal action under German and international intellectual property law.
Contact mlaiel@live.de for licensing inquiries only.
"""

import asyncio
import logging
import time
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import json
from collections import defaultdict, OrderedDict
from contextlib import asynccontextmanager
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

from .seo_agent import SEOAgent, ContentType, OptimizationType, SEOAnalysis, KeywordData
from .seo_manager import SEOAgentManager, CampaignType, CampaignStatus, SEOCampaign
from .keyword_research import KeywordAnalyzer, TrendAnalyzer, CompetitorAnalyzer
from .content_optimization import MetadataOptimizer, ContentStructureOptimizer, LinkBuilder
from .metrics import SEOMetricsCollector
from .reporting import SEOReportGenerator
from .config import SEOAgentConfig

from ..base import BaseAgent, AgentResponse
from ...core.exceptions import SEOError, ValidationError, RateLimitError
from ...core.config import settings
from ...database.models import SEOAnalysisModel, SEOCampaignModel
from ...security.encryption import DataProtector
from ...monitoring.alerts import AlertManager
from ...utils.caching import DistributedCache

logger = logging.getLogger(__name__)

class SEOSystemPriority(IntEnum):
    """System-wide priority levels for SEO operations"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class SEOOperationType(Enum):
    """Types of SEO operations for workflow management"""
    CONTENT_ANALYSIS = "content_analysis"
    KEYWORD_RESEARCH = "keyword_research"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    TECHNICAL_AUDIT = "technical_audit"
    CONTENT_OPTIMIZATION = "content_optimization"
    CAMPAIGN_MANAGEMENT = "campaign_management"
    PERFORMANCE_MONITORING = "performance_monitoring"
    REPORT_GENERATION = "report_generation"

@dataclass
class SEOWorkflowTask:
    """Advanced SEO workflow task with dependency management"""
    task_id: str
    operation_type: SEOOperationType
    priority: SEOSystemPriority
    content_ids: List[str]
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    assigned_agent: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SEOSystem:
    """
    Enterprise-Grade SEO System Orchestrator
    
    Industrial-strength central hub for coordinating all SEO operations across the platform.
    Provides unified access to all SEO components with advanced workflow management,
    resource allocation, and performance optimization.
    
    Advanced Enterprise Features:
    - Multi-tenant SEO management with resource isolation
    - Dynamic load balancing and resource allocation
    - Advanced workflow orchestration with dependency management
    - Real-time performance monitoring and auto-scaling
    - Comprehensive audit trails and compliance tracking
    - AI-powered optimization recommendations and automation
    - Cross-platform SEO strategy coordination
    - Enterprise security and access control integration
    - Advanced reporting and business intelligence
    - Multi-language and international SEO support
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the enterprise SEO system"""
        self.config = SEOAgentConfig(config or {})
        
        # Core system components
        self.seo_agent_pool: Dict[str, SEOAgent] = {}
        self.seo_manager = SEOAgentManager()
        self.keyword_analyzer = KeywordAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.metadata_optimizer = MetadataOptimizer()
        self.content_optimizer = ContentStructureOptimizer()
        self.link_builder = LinkBuilder()
        self.metrics_collector = SEOMetricsCollector()
        self.report_generator = SEOReportGenerator()
        
        # System infrastructure
        self.data_protector = DataProtector()
        self.alert_manager = AlertManager()
        self.distributed_cache = DistributedCache()
        
        # Workflow and task management
        self.workflow_queue: OrderedDict[str, SEOWorkflowTask] = OrderedDict()
        self.active_tasks: Dict[str, SEOWorkflowTask] = {}
        self.completed_tasks: Dict[str, SEOWorkflowTask] = {}
        
        # Resource management
        self.max_concurrent_tasks = self.config.max_concurrent_operations
        self.resource_allocation: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Performance tracking
        self.system_metrics: Dict[str, Any] = {}
        self.performance_history: List[Dict[str, Any]] = []
        
        # Thread pools for different types of operations
        self.io_executor = ThreadPoolExecutor(max_workers=20, thread_name_prefix="seo_io")
        self.compute_executor = ProcessPoolExecutor(max_workers=4)
        
        # System state
        self.system_status = "initializing"
        self.last_health_check = datetime.now()
        
        logger.info("SEO System initialized with enterprise configuration")

    async def initialize(self) -> bool:
        """Initialize all system components and prepare for operations"""
        try:
            logger.info("Starting SEO System initialization...")
            
            # Initialize core components
            await self._initialize_core_components()
            
            # Initialize infrastructure
            await self._initialize_infrastructure()
            
            # Initialize workflow engine
            await self._initialize_workflow_engine()
            
            # Perform system health check
            health_status = await self._perform_comprehensive_health_check()
            
            if not health_status:
                raise SEOError("System health check failed during initialization")
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.system_status = "operational"
            logger.info("SEO System successfully initialized and operational")
            
            return True
            
        except Exception as e:
            logger.error(f"SEO System initialization failed: {str(e)}")
            self.system_status = "failed"
            raise SEOError(f"System initialization failed: {str(e)}")

    async def analyze_content(
        self,
        content: Union[Dict[str, Any], List[Dict[str, Any]]],
        analysis_options: Optional[Dict[str, Any]] = None,
        priority: SEOSystemPriority = SEOSystemPriority.MEDIUM
    ) -> Union[SEOAnalysis, List[SEOAnalysis]]:
        """
        Comprehensive content SEO analysis with enterprise-level capabilities
        
        Args:
            content: Single content item or list of content items to analyze
            analysis_options: Advanced analysis configuration options
            priority: System priority for this analysis
            
        Returns:
            SEO analysis result(s) with comprehensive insights and recommendations
        """
        try:
            # Validate input
            if isinstance(content, list):
                return await self._analyze_multiple_content(content, analysis_options, priority)
            else:
                return await self._analyze_single_content(content, analysis_options, priority)
                
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            raise SEOError(f"Content analysis failed: {str(e)}")

    async def research_keywords(
        self,
        seed_keywords: List[str],
        content_type: ContentType,
        research_options: Optional[Dict[str, Any]] = None,
        priority: SEOSystemPriority = SEOSystemPriority.MEDIUM
    ) -> Dict[str, KeywordData]:
        """
        Advanced keyword research with competitive intelligence and trend analysis
        
        Args:
            seed_keywords: Initial keywords to expand from
            content_type: Type of content for targeted research
            research_options: Advanced research configuration
            priority: System priority for this research
            
        Returns:
            Comprehensive keyword intelligence data
        """
        try:
            # Create workflow task for keyword research
            task = await self._create_workflow_task(
                operation_type=SEOOperationType.KEYWORD_RESEARCH,
                priority=priority,
                parameters={
                    'seed_keywords': seed_keywords,
                    'content_type': content_type,
                    'options': research_options or {}
                }
            )
            
            # Execute keyword research workflow
            result = await self._execute_workflow_task(task)
            
            return result['keyword_data']
            
        except Exception as e:
            logger.error(f"Keyword research failed: {str(e)}")
            raise SEOError(f"Keyword research failed: {str(e)}")

    async def optimize_content(
        self,
        content: Dict[str, Any],
        optimization_goals: List[OptimizationType],
        target_keywords: Optional[List[str]] = None,
        priority: SEOSystemPriority = SEOSystemPriority.MEDIUM
    ) -> Dict[str, Any]:
        """
        AI-powered content optimization with comprehensive enhancement strategies
        
        Args:
            content: Content to optimize
            optimization_goals: Specific optimization objectives
            target_keywords: Keywords to optimize for
            priority: System priority for this optimization
            
        Returns:
            Optimized content with enhancement details and metrics
        """
        try:
            # Get optimal agent for this content type
            agent = await self._get_optimal_agent(content.get('type', 'blog_post'))
            
            # Perform comprehensive optimization
            optimization_result = await agent.optimize_content_structure(
                content=content,
                target_keywords=target_keywords or [],
                optimization_goals=optimization_goals
            )
            
            # Track optimization metrics
            await self._track_optimization_metrics(content, optimization_result)
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Content optimization failed: {str(e)}")
            raise SEOError(f"Content optimization failed: {str(e)}")

    async def create_seo_campaign(
        self,
        campaign_config: Dict[str, Any],
        auto_start: bool = False
    ) -> SEOCampaign:
        """
        Create and orchestrate comprehensive SEO campaigns
        
        Args:
            campaign_config: Detailed campaign configuration
            auto_start: Whether to automatically start the campaign
            
        Returns:
            Created SEO campaign with full tracking and management
        """
        try:
            # Delegate to SEO manager
            campaign = await self.seo_manager.create_seo_campaign(
                campaign_config=campaign_config,
                auto_start=auto_start
            )
            
            # Register campaign for system monitoring
            await self._register_campaign_monitoring(campaign)
            
            return campaign
            
        except Exception as e:
            logger.error(f"Campaign creation failed: {str(e)}")
            raise SEOError(f"Campaign creation failed: {str(e)}")

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status and health metrics
        
        Returns:
            Detailed system status including performance metrics and health indicators
        """
        try:
            # Collect current system metrics
            current_metrics = await self._collect_system_metrics()
            
            # Analyze system performance
            performance_analysis = await self._analyze_system_performance()
            
            # Check resource utilization
            resource_utilization = await self._check_resource_utilization()
            
            # Get workflow status
            workflow_status = await self._get_workflow_status()
            
            return {
                'system_status': self.system_status,
                'uptime': (datetime.now() - self.last_health_check).total_seconds(),
                'active_agents': len(self.seo_agent_pool),
                'active_campaigns': len(self.seo_manager.active_campaigns),
                'pending_tasks': len(self.workflow_queue),
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'system_metrics': current_metrics,
                'performance_analysis': performance_analysis,
                'resource_utilization': resource_utilization,
                'workflow_status': workflow_status,
                'last_health_check': self.last_health_check,
                'version': self.config.system_version
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}")
            raise SEOError(f"System status retrieval failed: {str(e)}")

    # ================== INTERNAL SYSTEM METHODS ==================

    async def _initialize_core_components(self) -> None:
        """Initialize all core SEO components"""
        try:
            # Initialize SEO manager
            await self.seo_manager.initialize()
            
            # Initialize analyzers
            await self.keyword_analyzer.initialize()
            await self.trend_analyzer.initialize()
            await self.competitor_analyzer.initialize()
            
            # Initialize optimizers
            await self.metadata_optimizer.initialize()
            await self.content_optimizer.initialize()
            await self.link_builder.initialize()
            
            # Initialize metrics and reporting
            await self.metrics_collector.initialize()
            await self.report_generator.initialize()
            
            logger.info("All core components initialized successfully")
            
        except Exception as e:
            logger.error(f"Core component initialization failed: {str(e)}")
            raise

    async def _analyze_single_content(
        self,
        content: Dict[str, Any],
        options: Optional[Dict[str, Any]],
        priority: SEOSystemPriority
    ) -> SEOAnalysis:
        """Analyze a single content item with advanced options"""
        try:
            # Get or create optimal agent for this content
            agent = await self._get_optimal_agent(content.get('type', 'blog_post'))
            
            # Perform comprehensive analysis
            analysis = await agent.analyze_content_seo(
                content=content,
                analysis_depth=options.get('depth', 'comprehensive') if options else 'comprehensive',
                target_keywords=options.get('target_keywords') if options else None,
                competitor_urls=options.get('competitor_urls') if options else None
            )
            
            # Cache analysis results
            await self._cache_analysis_result(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Single content analysis failed: {str(e)}")
            raise

    # Additional helper methods continue...
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the entire SEO system"""
        try:
            logger.info("Starting SEO System shutdown...")
            
            # Stop background tasks
            await self._stop_background_tasks()
            
            # Complete active tasks
            await self._complete_active_tasks()
            
            # Shutdown agents and components
            await self._shutdown_components()
            
            # Close executors
            self.io_executor.shutdown(wait=True)
            self.compute_executor.shutdown(wait=True)
            
            # Final cleanup
            await self._cleanup_system_resources()
            
            self.system_status = "shutdown"
            logger.info("SEO System successfully shut down")
            
        except Exception as e:
            logger.error(f"Error during system shutdown: {str(e)}")

# ================== CONVENIENCE FUNCTIONS ==================

async def analyze_content(
    content: Union[Dict[str, Any], List[Dict[str, Any]]],
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Union[SEOAnalysis, List[SEOAnalysis]]:
    """
    Convenience function for quick content SEO analysis
    
    Args:
        content: Content to analyze
        config: System configuration
        **kwargs: Additional analysis options
        
    Returns:
        SEO analysis results
    """
    seo_system = SEOSystem(config)
    await seo_system.initialize()
    
    try:
        return await seo_system.analyze_content(content, kwargs)
    finally:
        await seo_system.shutdown()

async def optimize_content(
    content: Dict[str, Any],
    optimization_goals: List[OptimizationType],
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for quick content optimization
    
    Args:
        content: Content to optimize
        optimization_goals: Optimization objectives
        config: System configuration
        **kwargs: Additional optimization options
        
    Returns:
        Optimization results
    """
    seo_system = SEOSystem(config)
    await seo_system.initialize()
    
    try:
        return await seo_system.optimize_content(
            content=content,
            optimization_goals=optimization_goals,
            target_keywords=kwargs.get('target_keywords'),
            priority=kwargs.get('priority', SEOSystemPriority.MEDIUM)
        )
    finally:
        await seo_system.shutdown()

async def research_keywords(
    seed_keywords: List[str],
    content_type: ContentType,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, KeywordData]:
    """
    Convenience function for keyword research
    
    Args:
        seed_keywords: Keywords to research
        content_type: Type of content
        config: System configuration
        **kwargs: Additional research options
        
    Returns:
        Keyword research results
    """
    seo_system = SEOSystem(config)
    await seo_system.initialize()
    
    try:
        return await seo_system.research_keywords(
            seed_keywords=seed_keywords,
            content_type=content_type,
            research_options=kwargs,
            priority=kwargs.get('priority', SEOSystemPriority.MEDIUM)
        )
    finally:
        await seo_system.shutdown()

# Export all public components
__all__ = [
    'SEOSystem',
    'SEOSystemPriority', 
    'SEOOperationType',
    'SEOWorkflowTask',
    'analyze_content',
    'optimize_content',
    'research_keywords'
]
        
        # Core components
        self.seo_agent = SEOAgent()
        self.seo_manager = SEOAgentManager(self.config)
        
        # Analysis components
        self.keyword_analyzer = KeywordAnalyzer(self.config)
        self.trend_analyzer = TrendAnalyzer(self.config)
        self.competitor_analyzer = CompetitorAnalyzer(self.config)
        
        # Optimization components
        self.metadata_optimizer = MetadataOptimizer(self.config)
        self.content_optimizer = ContentStructureOptimizer(self.config)
        self.link_builder = LinkBuilder(self.config)
        
        # System state
        self.initialized = False
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_optimizations': 0,
            'successful_campaigns': 0,
            'avg_seo_improvement': 0.0,
            'total_keywords_researched': 0,
            'system_uptime': datetime.utcnow()
        }
    
    async def initialize(self) -> bool:
        """
        Initialize the complete SEO system.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing SEO System...")
            
            # Initialize core components
            await self.seo_agent.initialize()
            await self.seo_manager.initialize()
            
            # Initialize analysis components
            await self.keyword_analyzer.initialize()
            await self.trend_analyzer.initialize()
            await self.competitor_analyzer.initialize()
            
            # Initialize optimization components
            await self.metadata_optimizer.initialize()
            await self.content_optimizer.initialize()
            await self.link_builder.initialize()
            
            self.initialized = True
            logger.info("SEO System initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"SEO System initialization failed: {e}")
            raise SEOError(f"System initialization failed: {e}")
    
    async def analyze_content_comprehensive(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        target_keywords: Optional[List[str]] = None,
        include_competitors: bool = True,
        include_trends: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive SEO analysis for content.
        
        Args:
            content_id: Unique identifier for content
            content_data: Content information and metadata
            target_keywords: Keywords to analyze for
            include_competitors: Whether to include competitor analysis
            include_trends: Whether to include trend analysis
        
        Returns:
            Comprehensive SEO analysis results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            logger.info(f"Starting comprehensive SEO analysis for content: {content_id}")
            
            # Prepare analysis tasks
            tasks = []
            
            # Core SEO analysis
            core_analysis_task = self.seo_agent.process({
                'action': 'analyze_content',
                'content_id': content_id,
                'content_data': content_data,
                'target_keywords': target_keywords or []
            })
            tasks.append(('core_analysis', core_analysis_task))
            
            # Keyword research if no target keywords provided
            if not target_keywords:
                keyword_research_task = self.keyword_analyzer.research_keywords(
                    seed_keywords=[content_data.get('title', '').split()[:3]],
                    topic=content_data.get('category', ''),
                    max_results=20
                )
                tasks.append(('keyword_research', keyword_research_task))
            
            # Trend analysis
            if include_trends and target_keywords:
                trend_analysis_task = self.trend_analyzer.analyze_keyword_trends(
                    target_keywords
                )
                tasks.append(('trend_analysis', trend_analysis_task))
            
            # Competitor analysis
            if include_competitors and target_keywords:
                # Get competitor URLs from content data or discover them
                competitor_urls = content_data.get('competitor_urls', [])
                if not competitor_urls:
                    # Auto-discover competitors based on keywords
                    competitor_urls = await self._auto_discover_competitors(
                        target_keywords, content_data.get('industry', '')
                    )
                
                if competitor_urls:
                    competitor_analysis_task = self.competitor_analyzer.analyze_competitors(
                        competitor_urls, target_keywords
                    )
                    tasks.append(('competitor_analysis', competitor_analysis_task))
            
            # Execute all analysis tasks in parallel
            results = {}
            for task_name, task in tasks:
                try:
                    result = await task
                    results[task_name] = result
                except Exception as e:
                    logger.error(f"Error in {task_name}: {e}")
                    results[task_name] = {'error': str(e)}
            
            # Consolidate results
            comprehensive_analysis = await self._consolidate_analysis_results(
                content_id, content_data, results
            )
            
            # Generate strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                comprehensive_analysis
            )
            
            # Calculate priority scores
            priority_scores = await self._calculate_optimization_priorities(
                comprehensive_analysis
            )
            
            final_analysis = {
                'content_id': content_id,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'comprehensive_analysis': comprehensive_analysis,
                'strategic_recommendations': strategic_recommendations,
                'priority_scores': priority_scores,
                'next_actions': await self._suggest_next_actions(comprehensive_analysis),
                'estimated_impact': await self._estimate_optimization_impact(comprehensive_analysis)
            }
            
            # Update performance metrics
            self.performance_metrics['total_optimizations'] += 1
            
            logger.info(f"Comprehensive SEO analysis completed for content: {content_id}")
            
            return final_analysis
            
        except Exception as e:
            logger.error(f"Comprehensive analysis error for {content_id}: {e}")
            raise SEOError(f"Comprehensive analysis failed: {e}")
    
    async def optimize_content_complete(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        optimization_level: str = "advanced",
        target_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform complete content optimization workflow.
        
        Args:
            content_id: Content identifier
            content_data: Content data to optimize
            optimization_level: Level of optimization (basic, intermediate, advanced, expert)
            target_keywords: Keywords to optimize for
        
        Returns:
            Complete optimization results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            logger.info(f"Starting complete optimization for content: {content_id}")
            
            # First, perform comprehensive analysis
            analysis_result = await self.analyze_content_comprehensive(
                content_id, content_data, target_keywords
            )
            
            # Extract optimization recommendations
            recommendations = analysis_result['strategic_recommendations']
            target_keywords = target_keywords or self._extract_recommended_keywords(analysis_result)
            
            # Perform optimizations in parallel
            optimization_tasks = []
            
            # Metadata optimization
            metadata_task = self.metadata_optimizer.optimize_metadata(
                content_data, target_keywords, 
                content_data.get('type', 'article'),
                content_data.get('brand_name', ''),
                optimization_level
            )
            optimization_tasks.append(('metadata', metadata_task))
            
            # Content structure optimization
            structure_task = self.content_optimizer.optimize_structure(
                content_data, target_keywords
            )
            optimization_tasks.append(('structure', structure_task))
            
            # Title optimization
            title_task = self.content_optimizer.optimize_title(
                content_data, target_keywords
            )
            optimization_tasks.append(('title', title_task))
            
            # Link building optimization
            related_content = content_data.get('related_content', [])
            if related_content:
                link_task = self.link_builder.build_content_links(
                    content_data, related_content, target_keywords
                )
                optimization_tasks.append(('links', link_task))
            
            # Execute optimization tasks
            optimization_results = {}
            for task_name, task in optimization_tasks:
                try:
                    result = await task
                    optimization_results[task_name] = result
                except Exception as e:
                    logger.error(f"Error in {task_name} optimization: {e}")
                    optimization_results[task_name] = {'error': str(e)}
            
            # Generate optimized content package
            optimized_content = await self._generate_optimized_content_package(
                content_id, content_data, optimization_results, target_keywords
            )
            
            # Calculate optimization impact
            impact_analysis = await self._calculate_detailed_optimization_impact(
                analysis_result, optimization_results
            )
            
            # Generate implementation guide
            implementation_guide = await self._generate_implementation_guide(
                optimization_results, optimization_level
            )
            
            complete_optimization = {
                'content_id': content_id,
                'optimization_timestamp': datetime.utcnow().isoformat(),
                'original_analysis': analysis_result,
                'optimization_results': optimization_results,
                'optimized_content': optimized_content,
                'impact_analysis': impact_analysis,
                'implementation_guide': implementation_guide,
                'quality_score_improvement': impact_analysis.get('quality_improvement', 0),
                'estimated_traffic_increase': impact_analysis.get('traffic_increase', 0)
            }
            
            logger.info(f"Complete optimization finished for content: {content_id}")
            
            return complete_optimization
            
        except Exception as e:
            logger.error(f"Complete optimization error for {content_id}: {e}")
            raise SEOError(f"Complete optimization failed: {e}")
    
    async def create_seo_campaign(
        self,
        campaign_config: Dict[str, Any],
        auto_start: bool = True
    ) -> Dict[str, Any]:
        """
        Create and optionally start an SEO campaign.
        
        Args:
            campaign_config: Campaign configuration
            auto_start: Whether to automatically start the campaign
        
        Returns:
            Campaign creation and execution results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create campaign through manager
            campaign_result = await self.seo_manager.create_campaign(campaign_config)
            campaign_id = campaign_result['campaign_id']
            
            # Auto-start if requested
            if auto_start:
                start_result = await self.seo_manager.start_campaign(campaign_id)
                campaign_result['start_result'] = start_result
            
            # Track workflow
            self.active_workflows[campaign_id] = {
                'type': 'seo_campaign',
                'status': 'active' if auto_start else 'created',
                'created_at': datetime.utcnow(),
                'config': campaign_config
            }
            
            return campaign_result
            
        except Exception as e:
            logger.error(f"SEO campaign creation error: {e}")
            raise SEOError(f"Campaign creation failed: {e}")
    
    async def research_keywords_comprehensive(
        self,
        seed_keywords: List[str],
        industry: str,
        language: str = 'en',
        competitor_urls: Optional[List[str]] = None,
        max_keywords: int = 100
    ) -> Dict[str, Any]:
        """
        Comprehensive keyword research with trend and competitive analysis.
        
        Args:
            seed_keywords: Initial keywords to expand from
            industry: Industry or niche context
            language: Target language
            competitor_urls: Competitor URLs for analysis
            max_keywords: Maximum keywords to research
        
        Returns:
            Comprehensive keyword research results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Parallel keyword research tasks
            tasks = []
            
            # Primary keyword research
            keyword_research_task = self.keyword_analyzer.research_keywords(
                seed_keywords=seed_keywords,
                topic=industry,
                language=language,
                max_results=max_keywords
            )
            tasks.append(('keyword_research', keyword_research_task))
            
            # Trend analysis
            trend_analysis_task = self.trend_analyzer.analyze_keyword_trends(
                seed_keywords, language=language
            )
            tasks.append(('trend_analysis', trend_analysis_task))
            
            # Emerging trends
            emerging_trends_task = self.trend_analyzer.detect_emerging_trends(
                industry, language
            )
            tasks.append(('emerging_trends', emerging_trends_task))
            
            # Competitor analysis if URLs provided
            if competitor_urls:
                competitor_task = self.competitor_analyzer.analyze_competitors(
                    competitor_urls, seed_keywords, language
                )
                tasks.append(('competitor_analysis', competitor_task))
            
            # Execute tasks
            results = {}
            for task_name, task in tasks:
                try:
                    result = await task
                    results[task_name] = result
                except Exception as e:
                    logger.error(f"Error in {task_name}: {e}")
                    results[task_name] = {'error': str(e)}
            
            # Consolidate keyword intelligence
            keyword_intelligence = await self._consolidate_keyword_intelligence(results)
            
            # Generate keyword strategy
            keyword_strategy = await self._generate_comprehensive_keyword_strategy(
                keyword_intelligence, industry, language
            )
            
            # Update performance metrics
            self.performance_metrics['total_keywords_researched'] += len(
                results.get('keyword_research', [])
            )
            
            return {
                'research_timestamp': datetime.utcnow().isoformat(),
                'seed_keywords': seed_keywords,
                'industry': industry,
                'language': language,
                'research_results': results,
                'keyword_intelligence': keyword_intelligence,
                'keyword_strategy': keyword_strategy,
                'total_keywords_found': len(keyword_intelligence.get('all_keywords', [])),
                'high_opportunity_keywords': len(keyword_intelligence.get('opportunities', []))
            }
            
        except Exception as e:
            logger.error(f"Comprehensive keyword research error: {e}")
            raise SEOError(f"Keyword research failed: {e}")
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive SEO system analytics and performance metrics."""
        if not self.initialized:
            await self.initialize()
        
        try:
            # System performance
            system_performance = {
                'uptime': (datetime.utcnow() - self.performance_metrics['system_uptime']).total_seconds(),
                'total_optimizations': self.performance_metrics['total_optimizations'],
                'successful_campaigns': self.performance_metrics['successful_campaigns'],
                'avg_seo_improvement': self.performance_metrics['avg_seo_improvement'],
                'total_keywords_researched': self.performance_metrics['total_keywords_researched']
            }
            
            # Active workflows
            active_workflows_status = {
                workflow_id: {
                    'type': workflow['type'],
                    'status': workflow['status'],
                    'runtime': (datetime.utcnow() - workflow['created_at']).total_seconds()
                }
                for workflow_id, workflow in self.active_workflows.items()
            }
            
            # Campaign analytics
            campaign_analytics = await self.seo_manager.get_performance_analytics()
            
            return {
                'system_performance': system_performance,
                'active_workflows': active_workflows_status,
                'campaign_analytics': campaign_analytics,
                'component_status': {
                    'seo_agent': 'active',
                    'seo_manager': 'active',
                    'keyword_analyzer': 'active',
                    'trend_analyzer': 'active',
                    'competitor_analyzer': 'active',
                    'metadata_optimizer': 'active',
                    'content_optimizer': 'active',
                    'link_builder': 'active'
                },
                'analytics_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System analytics error: {e}")
            raise SEOError(f"Analytics retrieval failed: {e}")
    
    # Helper methods
    async def _auto_discover_competitors(
        self, 
        keywords: List[str], 
        industry: str
    ) -> List[str]:
        """Auto-discover competitor URLs based on keywords and industry"""
        # Implementation would use search APIs to find top-ranking sites
        # For now, return empty list
        return []
    
    async def _consolidate_analysis_results(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Consolidate analysis results from multiple components"""
        
        consolidated = {
            'content_id': content_id,
            'overall_seo_score': 0.0,
            'component_scores': {},
            'key_findings': [],
            'optimization_opportunities': [],
            'competitive_position': {},
            'trend_insights': {}
        }
        
        # Extract core analysis
        if 'core_analysis' in results:
            core_data = results['core_analysis'].data if hasattr(results['core_analysis'], 'data') else results['core_analysis']
            consolidated['overall_seo_score'] = core_data.get('seo_score', 0)
            consolidated['component_scores']['content'] = core_data.get('content_analysis', {})
            consolidated['component_scores']['keywords'] = core_data.get('keyword_analysis', {})
            consolidated['component_scores']['metadata'] = core_data.get('metadata_analysis', {})
            consolidated['component_scores']['technical'] = core_data.get('technical_analysis', {})
            
            # Extract key findings
            recommendations = core_data.get('recommendations', [])
            consolidated['key_findings'] = [rec.get('message', '') for rec in recommendations[:5]]
            consolidated['optimization_opportunities'] = core_data.get('opportunities', [])
        
        # Add competitor insights
        if 'competitor_analysis' in results:
            consolidated['competitive_position'] = results['competitor_analysis']
        
        # Add trend insights
        if 'trend_analysis' in results:
            consolidated['trend_insights'] = results['trend_analysis']
        
        return consolidated
    
    async def _generate_strategic_recommendations(
        self, 
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate high-level strategic SEO recommendations"""
        
        recommendations = []
        seo_score = analysis.get('overall_seo_score', 0)
        
        # Strategic recommendations based on score
        if seo_score < 0.3:
            recommendations.append({
                'type': 'strategic',
                'priority': 10,
                'category': 'foundation',
                'title': 'SEO Foundation Rebuild Required',
                'description': 'Current SEO score is critically low. Complete optimization overhaul needed.',
                'actions': [
                    'Comprehensive keyword research and strategy',
                    'Content structure and quality improvement',
                    'Technical SEO audit and fixes',
                    'Metadata optimization across all content'
                ],
                'estimated_timeline': '4-6 weeks',
                'impact': 'high'
            })
        elif seo_score < 0.6:
            recommendations.append({
                'type': 'strategic',
                'priority': 8,
                'category': 'optimization',
                'title': 'Targeted SEO Improvements',
                'description': 'Good foundation but significant optimization opportunities exist.',
                'actions': [
                    'Focus on high-impact keyword optimization',
                    'Improve content structure and readability',
                    'Enhance metadata and social tags',
                    'Build strategic internal linking'
                ],
                'estimated_timeline': '2-3 weeks',
                'impact': 'medium-high'
            })
        else:
            recommendations.append({
                'type': 'strategic',
                'priority': 6,
                'category': 'refinement',
                'title': 'SEO Fine-tuning and Advanced Tactics',
                'description': 'Strong SEO foundation. Focus on advanced optimization techniques.',
                'actions': [
                    'Advanced keyword clustering and topics',
                    'Schema markup enhancement',
                    'E-A-T signal optimization',
                    'Competitive advantage building'
                ],
                'estimated_timeline': '1-2 weeks',
                'impact': 'medium'
            })
        
        # Add competitive recommendations
        if analysis.get('competitive_position'):
            recommendations.append({
                'type': 'competitive',
                'priority': 7,
                'category': 'market_position',
                'title': 'Competitive SEO Strategy',
                'description': 'Leverage competitive intelligence for market advantage.',
                'actions': [
                    'Target competitor keyword gaps',
                    'Create superior content for competitive keywords',
                    'Build authority in underserved niches',
                    'Monitor and respond to competitor SEO moves'
                ]
            })
        
        return recommendations
    
    async def _calculate_optimization_priorities(
        self, 
        analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate priority scores for different optimization areas"""
        
        priorities = {}
        component_scores = analysis.get('component_scores', {})
        
        # Calculate priorities based on component scores
        content_score = component_scores.get('content', {}).get('content_quality_score', 0.5)
        keyword_score = component_scores.get('keywords', {}).get('total_keyword_score', 0.5)
        metadata_score = component_scores.get('metadata', {}).get('metadata_score', 0.5)
        technical_score = component_scores.get('technical', {}).get('technical_score', 0.5)
        
        # Higher priority for lower scores (more improvement needed)
        priorities['content_optimization'] = max(0, 1.0 - content_score)
        priorities['keyword_optimization'] = max(0, 1.0 - keyword_score)
        priorities['metadata_optimization'] = max(0, 1.0 - metadata_score)
        priorities['technical_optimization'] = max(0, 1.0 - technical_score)
        
        return priorities
    
    async def _suggest_next_actions(
        self, 
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest immediate next actions based on analysis"""
        
        actions = []
        priorities = await self._calculate_optimization_priorities(analysis)
        
        # Sort priorities and suggest top actions
        sorted_priorities = sorted(priorities.items(), key=lambda x: x[1], reverse=True)
        
        for priority_area, score in sorted_priorities[:3]:
            if score > 0.3:  # Only suggest if significant improvement needed
                actions.append({
                    'area': priority_area,
                    'priority_score': round(score, 2),
                    'action': self._get_action_for_priority_area(priority_area),
                    'estimated_effort': self._estimate_effort_for_area(priority_area),
                    'expected_impact': self._estimate_impact_for_area(priority_area, score)
                })
        
        return actions
    
    def _get_action_for_priority_area(self, area: str) -> str:
        """Get specific action recommendation for priority area"""
        actions = {
            'content_optimization': 'Improve content quality, structure, and depth',
            'keyword_optimization': 'Research and implement target keywords strategically',
            'metadata_optimization': 'Optimize titles, descriptions, and meta tags',
            'technical_optimization': 'Fix technical SEO issues and improve page performance'
        }
        return actions.get(area, 'General optimization needed')
    
    def _estimate_effort_for_area(self, area: str) -> str:
        """Estimate effort level for optimization area"""
        efforts = {
            'content_optimization': 'Medium-High',
            'keyword_optimization': 'Medium',
            'metadata_optimization': 'Low-Medium',
            'technical_optimization': 'Medium-High'
        }
        return efforts.get(area, 'Medium')
    
    def _estimate_impact_for_area(self, area: str, priority_score: float) -> str:
        """Estimate expected impact for optimization area"""
        if priority_score > 0.7:
            return 'High'
        elif priority_score > 0.5:
            return 'Medium-High'
        elif priority_score > 0.3:
            return 'Medium'
        else:
            return 'Low-Medium'
    
    async def _estimate_optimization_impact(
        self, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate the potential impact of optimizations"""
        
        current_score = analysis.get('overall_seo_score', 0)
        priorities = await self._calculate_optimization_priorities(analysis)
        
        # Calculate potential improvement
        total_potential_improvement = sum(priorities.values()) * 0.25  # 25% improvement per priority area
        projected_score = min(current_score + total_potential_improvement, 1.0)
        
        return {
            'current_seo_score': round(current_score, 2),
            'projected_seo_score': round(projected_score, 2),
            'potential_improvement': round(projected_score - current_score, 2),
            'improvement_percentage': round(((projected_score - current_score) / current_score * 100) if current_score > 0 else 0, 1),
            'estimated_traffic_increase': round((projected_score - current_score) * 100, 0),  # Rough traffic estimate
            'optimization_confidence': 'high' if sum(priorities.values()) > 2 else 'medium' if sum(priorities.values()) > 1 else 'low'
        }


# Convenience functions for direct access
async def analyze_content(
    content_id: str,
    content_data: Dict[str, Any],
    target_keywords: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Quick content analysis function"""
    seo_system = SEOSystem()
    return await seo_system.analyze_content_comprehensive(
        content_id, content_data, target_keywords, **kwargs
    )

async def optimize_content(
    content_id: str,
    content_data: Dict[str, Any],
    optimization_level: str = "advanced",
    target_keywords: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Quick content optimization function"""
    seo_system = SEOSystem()
    return await seo_system.optimize_content_complete(
        content_id, content_data, optimization_level, target_keywords
    )

async def research_keywords(
    seed_keywords: List[str],
    industry: str,
    language: str = 'en',
    **kwargs
) -> Dict[str, Any]:
    """Quick keyword research function"""
    seo_system = SEOSystem()
    return await seo_system.research_keywords_comprehensive(
        seed_keywords, industry, language, **kwargs
    )

# Export main system class
__all__ = [
    'SEOSystem',
    'analyze_content',
    'optimize_content', 
    'research_keywords'
]
