"""
SEO Agent - Advanced Search Engine Optimization System

Industrial-grade SEO optimization agent with AI-powered content analysis, keyword research,
competitive intelligence, and multi-platform search engine optimization capabilities.

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
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import json
import re
from urllib.parse import urlparse, parse_qs
import aiohttp
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from ..base import BaseAgent, AgentResponse
try:
    from core.exceptions import SEOError, ValidationError, RateLimitError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    SEOError, ValidationError, RateLimitError = globals().get('SEOError, ValidationError, RateLimitError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...ml.seo_models import KeywordRankingModel, ContentOptimizationModel, TrendPredictionModel
from ...utils.text_analysis import TextAnalyzer, SemanticAnalyzer
from ...utils.web_scraping import WebScraper, SEOAnalysisEngine
from ...integrations.search_apis import SearchAPIManager, GoogleSearchAPI, BingSearchAPI
from ...security.encryption import ContentProtector
from ...monitoring.performance import MetricsCollector
from .config import SEOAgentConfig

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """Advanced SEO optimization strategy types"""
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    METADATA_OPTIMIZATION = "metadata_optimization"
    CONTENT_STRUCTURE = "content_structure"
    TECHNICAL_SEO = "technical_seo"
    LOCAL_SEO = "local_seo"
    MOBILE_OPTIMIZATION = "mobile_optimization"
    SCHEMA_MARKUP = "schema_markup"
    LINK_BUILDING = "link_building"
    SOCIAL_SIGNALS = "social_signals"
    USER_EXPERIENCE = "user_experience"
    VOICE_SEARCH = "voice_search"
    VIDEO_SEO = "video_seo"
    IMAGE_SEO = "image_seo"
    AUDIO_SEO = "audio_seo"
    INTERNATIONAL_SEO = "international_seo"
    FEATURED_SNIPPETS = "featured_snippets"
    ENTITY_OPTIMIZATION = "entity_optimization"
    AI_CONTENT_OPTIMIZATION = "ai_content_optimization"

class ContentType(Enum):
    """Multi-format content types for specialized SEO optimization"""
    MUSIC_TRACK = "music_track"
    MUSIC_ALBUM = "music_album"
    MUSIC_PLAYLIST = "music_playlist"
    VIDEO_CONTENT = "video_content"
    VIDEO_SERIES = "video_series"
    LIVE_STREAM = "live_stream"
    PODCAST_EPISODE = "podcast_episode"
    PODCAST_SERIES = "podcast_series"
    BLOG_POST = "blog_post"
    BLOG_CATEGORY = "blog_category"
    SOCIAL_POST = "social_post"
    SOCIAL_CAMPAIGN = "social_campaign"
    PROFILE_PAGE = "profile_page"
    PORTFOLIO_PAGE = "portfolio_page"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    EVENT_PAGE = "event_page"
    NEWS_ARTICLE = "news_article"
    TUTORIAL_CONTENT = "tutorial_content"
    DOCUMENTARY = "documentary"
    SHORT_FORM_VIDEO = "short_form_video"

class SEOPriority(IntEnum):
    """SEO optimization priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MAINTENANCE = 5

class SearchEngineType(Enum):
    """Supported search engines for optimization"""
    GOOGLE = "google"
    BING = "bing"
    YANDEX = "yandex"
    BAIDU = "baidu"
    DUCKDUCKGO = "duckduckgo"
    YAHOO = "yahoo"
    ASK = "ask"

class KeywordIntent(Enum):
    """Search intent classification for keyword targeting"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"
    LOCAL = "local"
    BRANDED = "branded"
    TRENDING = "trending"

class CompetitorTier(Enum):
    """Competitor classification levels"""
    DIRECT_COMPETITOR = "direct_competitor"
    INDIRECT_COMPETITOR = "indirect_competitor"
    MARKET_LEADER = "market_leader"
    EMERGING_COMPETITOR = "emerging_competitor"
    NICHE_PLAYER = "niche_player"

@dataclass
class SEOMetrics:
    """Comprehensive SEO performance metrics"""
    organic_traffic: int = 0
    keyword_rankings: Dict[str, int] = field(default_factory=dict)
    click_through_rate: float = 0.0
    bounce_rate: float = 0.0
    session_duration: float = 0.0
    pages_per_session: float = 0.0
    conversion_rate: float = 0.0
    backlink_count: int = 0
    domain_authority: float = 0.0
    page_authority: float = 0.0
    search_visibility: float = 0.0
    featured_snippets: int = 0
    local_pack_rankings: int = 0
    mobile_usability_score: float = 0.0
    page_speed_score: float = 0.0
    core_web_vitals: Dict[str, float] = field(default_factory=dict)

@dataclass
class SEOAnalysis:
    """Comprehensive SEO analysis results with actionable insights"""
    content_id: str
    content_type: ContentType
    url: Optional[str]
    current_score: float
    potential_score: float
    improvement_percentage: float
    optimization_opportunities: List[Dict[str, Any]]
    keyword_analysis: Dict[str, Any]
    competitor_analysis: Dict[str, Any]
    technical_issues: List[Dict[str, Any]]
    content_quality_score: float
    user_experience_score: float
    mobile_friendliness_score: float
    page_speed_insights: Dict[str, Any]
    schema_markup_status: Dict[str, Any]
    backlink_profile: Dict[str, Any]
    social_signals: Dict[str, Any]
    local_seo_factors: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    priority_actions: List[Dict[str, Any]]
    estimated_traffic_impact: Dict[str, Any]
    roi_projection: Dict[str, Any]
    analyzed_at: datetime
    analysis_duration: float
    confidence_score: float

@dataclass
class KeywordData:
    """Advanced keyword research and intelligence data"""
    keyword: str
    search_volume: int
    competition_level: float
    cost_per_click: float
    keyword_difficulty: float
    relevance_score: float
    trending_score: float
    seasonality_data: Dict[str, Any]
    search_intent: KeywordIntent
    related_keywords: List[str]
    long_tail_variations: List[str]
    question_variations: List[str]
    competitor_keywords: List[str]
    search_features: List[str]
    local_search_volume: Dict[str, int]
    demographic_data: Dict[str, Any]
    device_breakdown: Dict[str, float]
    conversion_potential: float
    content_gap_opportunities: List[str]
    suggested_content_types: List[ContentType]
    last_updated: datetime

@dataclass
class CompetitorInsight:
    """Detailed competitor SEO intelligence"""
    domain: str
    competitor_tier: CompetitorTier
    domain_authority: float
    organic_traffic: int
    ranking_keywords: Dict[str, int]
    top_content: List[Dict[str, Any]]
    backlink_profile: Dict[str, Any]
    content_strategy: Dict[str, Any]
    technical_advantages: List[str]
    content_gaps: List[str]
    opportunity_keywords: List[str]
    threat_assessment: Dict[str, Any]
    competitive_advantage: List[str]
    weakness_analysis: List[str]
    analyzed_at: datetime

@dataclass
class OptimizationRecommendation:
    """Actionable SEO optimization recommendation"""
    recommendation_id: str
    optimization_type: OptimizationType
    priority: SEOPriority
    title: str
    description: str
    implementation_steps: List[str]
    expected_impact: Dict[str, Any]
    effort_required: str
    technical_requirements: List[str]
    resources_needed: List[str]
    timeline_estimate: str
    success_metrics: List[str]
    risk_assessment: Dict[str, Any]
    dependencies: List[str]
    cost_benefit_analysis: Dict[str, Any]
    created_at: datetime
    implemented: bool = False
    implementation_date: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None

class SEOAgent(BaseAgent):
    """
    Industrial-grade SEO optimization agent with comprehensive AI-powered capabilities.
    
    Advanced Features:
    - Multi-engine keyword research and competitive analysis
    - AI-powered content optimization and structure enhancement
    - Real-time SEO performance monitoring and alerting
    - Automated technical SEO auditing and fixing
    - Advanced schema markup and structured data implementation
    - International and local SEO optimization strategies
    - Voice search and featured snippet optimization
    - Comprehensive competitor intelligence and gap analysis
    - ROI-focused optimization recommendations with impact projections
    - Multi-format content optimization for creators and influencers
    - Enterprise-level reporting and analytics dashboard
    """
    
    def __init__(self, agent_id: str = "seo_agent_industrial", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        
        # Initialize configuration
        self.seo_config = SEOAgentConfig(config or {})
        
        # Core AI models and analyzers
        self.keyword_ranking_model = KeywordRankingModel()
        self.content_optimization_model = ContentOptimizationModel()
        self.trend_prediction_model = TrendPredictionModel()
        
        # Analysis engines
        self.text_analyzer = TextAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.seo_analysis_engine = SEOAnalysisEngine()
        
        # API integrations
        self.search_api_manager = SearchAPIManager()
        self.web_scraper = WebScraper()
        
        # Security and monitoring
        self.content_protector = ContentProtector()
        self.metrics_collector = MetricsCollector()
        
        # Internal state management
        self.active_campaigns: Dict[str, Dict[str, Any]] = {}
        self.keyword_cache: Dict[str, KeywordData] = {}
        self.competitor_cache: Dict[str, CompetitorInsight] = {}
        self.optimization_history: List[OptimizationRecommendation] = []
        
        # Performance tracking
        self.performance_metrics = SEOMetrics()
        self.analysis_cache_ttl = 3600  # 1 hour cache
        
        # Thread pool for concurrent processing
        self.executor = ThreadPoolExecutor(max_workers=self.seo_config.max_concurrent_requests)
        
        logger.info(f"SEO Agent initialized with ID: {agent_id}")

    async def initialize(self) -> bool:
        """Initialize all SEO agent components and dependencies"""
        try:
            # Initialize AI models
            await self._initialize_ai_models()
            
            # Initialize API connections
            await self._initialize_api_connections()
            
            # Load existing data
            await self._load_historical_data()
            
            # Verify system health
            health_check = await self._perform_health_check()
            
            if not health_check:
                raise SEOError("SEO Agent initialization failed - health check failed")
            
            logger.info("SEO Agent successfully initialized and ready for operations")
            return True
            
        except Exception as e:
            logger.error(f"SEO Agent initialization failed: {str(e)}")
            raise SEOError(f"Initialization failed: {str(e)}")

    async def analyze_content_seo(
        self, 
        content: Dict[str, Any],
        analysis_depth: str = "comprehensive",
        target_keywords: Optional[List[str]] = None,
        competitor_urls: Optional[List[str]] = None
    ) -> SEOAnalysis:
        """
        Perform comprehensive SEO analysis of content with AI-powered insights
        
        Args:
            content: Content data to analyze
            analysis_depth: Level of analysis (basic, standard, comprehensive, expert)
            target_keywords: Specific keywords to optimize for
            competitor_urls: Competitor URLs for comparative analysis
            
        Returns:
            Detailed SEO analysis with actionable recommendations
        """
        start_time = time.time()
        
        try:
            # Validate input
            await self._validate_content_input(content)
            
            # Extract content metadata
            content_metadata = await self._extract_content_metadata(content)
            
            # Perform parallel analysis tasks
            analysis_tasks = [
                self._analyze_keyword_optimization(content, target_keywords),
                self._analyze_content_structure(content),
                self._analyze_technical_seo(content),
                self._analyze_competitor_landscape(content, competitor_urls),
                self._analyze_user_experience(content),
                self._analyze_mobile_optimization(content),
                self._analyze_page_speed(content),
                self._analyze_schema_markup(content),
                self._analyze_backlink_opportunities(content),
                self._analyze_social_signals(content)
            ]
            
            # Execute analysis tasks concurrently
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Process and combine results
            combined_analysis = await self._combine_analysis_results(
                content_metadata, analysis_results, analysis_depth
            )
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(combined_analysis)
            
            # Calculate scores and projections
            scores = await self._calculate_seo_scores(combined_analysis)
            roi_projection = await self._calculate_roi_projection(combined_analysis, recommendations)
            
            # Create comprehensive analysis object
            seo_analysis = SEOAnalysis(
                content_id=content.get('id', f"content_{int(time.time())}"),
                content_type=ContentType(content.get('type', 'blog_post')),
                url=content.get('url'),
                current_score=scores['current_score'],
                potential_score=scores['potential_score'],
                improvement_percentage=scores['improvement_percentage'],
                optimization_opportunities=combined_analysis['opportunities'],
                keyword_analysis=combined_analysis['keyword_analysis'],
                competitor_analysis=combined_analysis['competitor_analysis'],
                technical_issues=combined_analysis['technical_issues'],
                content_quality_score=scores['content_quality'],
                user_experience_score=scores['user_experience'],
                mobile_friendliness_score=scores['mobile_friendliness'],
                page_speed_insights=combined_analysis['page_speed'],
                schema_markup_status=combined_analysis['schema_markup'],
                backlink_profile=combined_analysis['backlink_profile'],
                social_signals=combined_analysis['social_signals'],
                local_seo_factors=combined_analysis.get('local_seo', {}),
                recommendations=recommendations,
                priority_actions=self._extract_priority_actions(recommendations),
                estimated_traffic_impact=combined_analysis['traffic_impact'],
                roi_projection=roi_projection,
                analyzed_at=datetime.now(),
                analysis_duration=time.time() - start_time,
                confidence_score=scores['confidence']
            )
            
            # Cache the analysis
            await self._cache_analysis_result(seo_analysis)
            
            # Track metrics
            self.metrics_collector.track_analysis_completed(seo_analysis)
            
            logger.info(f"SEO analysis completed for content {seo_analysis.content_id} in {seo_analysis.analysis_duration:.2f}s")
            
            return seo_analysis
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {str(e)}")
            raise SEOError(f"Content analysis failed: {str(e)}")

    async def research_keywords(
        self,
        seed_keywords: List[str],
        content_type: ContentType,
        target_audience: Optional[Dict[str, Any]] = None,
        location: Optional[str] = None,
        language: str = "en",
        depth: str = "comprehensive"
    ) -> Dict[str, KeywordData]:
        """
        Perform advanced keyword research with AI-powered insights and competitive analysis
        
        Args:
            seed_keywords: Initial keywords to expand from
            content_type: Type of content for targeted research
            target_audience: Audience demographics and preferences
            location: Geographic targeting for local SEO
            language: Content language for keyword research
            depth: Research depth level
            
        Returns:
            Dictionary of keyword data with comprehensive metrics
        """
        start_time = time.time()
        
        try:
            # Validate and prepare inputs
            validated_keywords = await self._validate_seed_keywords(seed_keywords)
            
            # Perform parallel keyword research tasks
            research_tasks = [
                self._research_primary_keywords(validated_keywords, content_type),
                self._research_long_tail_keywords(validated_keywords, content_type),
                self._research_competitor_keywords(validated_keywords, content_type),
                self._research_question_keywords(validated_keywords, content_type),
                self._research_trending_keywords(validated_keywords, content_type),
                self._research_local_keywords(validated_keywords, location),
                self._research_semantic_keywords(validated_keywords, content_type)
            ]
            
            # Execute research tasks concurrently
            research_results = await asyncio.gather(*research_tasks, return_exceptions=True)
            
            # Process and combine keyword data
            all_keywords = await self._combine_keyword_research_results(research_results)
            
            # Enhance keywords with additional data
            enhanced_keywords = {}
            for keyword, base_data in all_keywords.items():
                try:
                    enhanced_data = await self._enhance_keyword_data(
                        keyword, base_data, content_type, target_audience, language
                    )
                    enhanced_keywords[keyword] = enhanced_data
                    
                    # Cache the keyword data
                    self.keyword_cache[keyword] = enhanced_data
                    
                except Exception as e:
                    logger.warning(f"Failed to enhance keyword '{keyword}': {str(e)}")
                    enhanced_keywords[keyword] = base_data
            
            # Apply filtering and ranking
            filtered_keywords = await self._filter_and_rank_keywords(
                enhanced_keywords, content_type, depth
            )
            
            # Track metrics
            self.metrics_collector.track_keyword_research_completed(
                len(seed_keywords), len(filtered_keywords), time.time() - start_time
            )
            
            logger.info(f"Keyword research completed: {len(filtered_keywords)} keywords in {time.time() - start_time:.2f}s")
            
            return filtered_keywords
            
        except Exception as e:
            logger.error(f"Keyword research failed: {str(e)}")
            raise SEOError(f"Keyword research failed: {str(e)}")

    async def optimize_content_structure(
        self,
        content: Dict[str, Any],
        target_keywords: List[str],
        optimization_goals: List[OptimizationType]
    ) -> Dict[str, Any]:
        """
        AI-powered content structure optimization for maximum SEO impact
        
        Args:
            content: Content to optimize
            target_keywords: Keywords to optimize for
            optimization_goals: Specific optimization objectives
            
        Returns:
            Optimized content with SEO enhancements
        """
        try:
            # Analyze current content structure
            structure_analysis = await self._analyze_content_structure_detailed(content)
            
            # Generate optimization plan
            optimization_plan = await self._create_content_optimization_plan(
                structure_analysis, target_keywords, optimization_goals
            )
            
            # Apply optimizations
            optimized_content = await self._apply_content_optimizations(
                content, optimization_plan
            )
            
            # Validate optimizations
            validation_results = await self._validate_content_optimizations(
                optimized_content, target_keywords
            )
            
            return {
                'optimized_content': optimized_content,
                'optimization_report': validation_results,
                'improvement_metrics': await self._calculate_improvement_metrics(
                    content, optimized_content
                ),
                'applied_optimizations': optimization_plan['applied_changes'],
                'next_steps': optimization_plan['next_steps']
            }
            
        except Exception as e:
            logger.error(f"Content optimization failed: {str(e)}")
            raise SEOError(f"Content optimization failed: {str(e)}")

    async def monitor_seo_performance(
        self,
        content_ids: List[str],
        metrics_to_track: List[str] = None,
        reporting_frequency: str = "daily"
    ) -> Dict[str, Any]:
        """
        Continuous SEO performance monitoring with automated alerts
        
        Args:
            content_ids: List of content IDs to monitor
            metrics_to_track: Specific metrics to monitor
            reporting_frequency: How often to generate reports
            
        Returns:
            Performance monitoring dashboard data
        """
        try:
            # Initialize monitoring for content pieces
            monitoring_config = await self._setup_performance_monitoring(
                content_ids, metrics_to_track, reporting_frequency
            )
            
            # Collect current performance data
            current_performance = await self._collect_performance_data(content_ids)
            
            # Analyze trends and patterns
            trend_analysis = await self._analyze_performance_trends(current_performance)
            
            # Generate alerts if needed
            alerts = await self._check_performance_alerts(current_performance, trend_analysis)
            
            # Create monitoring dashboard data
            dashboard_data = {
                'monitoring_status': 'active',
                'tracked_content': len(content_ids),
                'current_performance': current_performance,
                'trend_analysis': trend_analysis,
                'alerts': alerts,
                'next_update': datetime.now() + timedelta(days=1),
                'reporting_config': monitoring_config
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Performance monitoring setup failed: {str(e)}")
            raise SEOError(f"Performance monitoring failed: {str(e)}")

    # Internal helper methods continue...
        
        # Optimization components
        self.metadata_optimizer = MetadataOptimizer()
        self.content_optimizer = ContentStructureOptimizer()
        self.link_builder = LinkBuilder()
        
        # AI models
        self.keyword_ranking_model = None
        self.content_optimization_model = None
        
        # Analysis tools
        self.text_analyzer = TextAnalyzer()
        self.web_scraper = WebScraper()
        
        # External integrations
        self.search_apis = SearchAPIManager()
        
        # SEO data cache
        self.keyword_cache = {}
        self.analysis_cache = {}
        self.ranking_cache = {}
        
        # SEO configuration
        self.target_languages = ['en', 'de', 'fr', 'es']
        self.optimization_weights = {
            'keyword_relevance': 0.25,
            'content_quality': 0.20,
            'technical_seo': 0.20,
            'user_engagement': 0.15,
            'social_signals': 0.10,
            'backlink_profile': 0.10
        }
    
    async def initialize(self):
        """Initialize SEO models and components"""
        try:
            # Initialize AI models
            self.keyword_ranking_model = KeywordRankingModel()
            await self.keyword_ranking_model.load_model()
            
            self.content_optimization_model = ContentOptimizationModel()
            await self.content_optimization_model.load_model()
            
            # Initialize components
            await self.keyword_analyzer.initialize()
            await self.trend_analyzer.initialize()
            await self.competitor_analyzer.initialize()
            
            # Initialize optimizers
            await self.metadata_optimizer.initialize()
            await self.content_optimizer.initialize()
            await self.link_builder.initialize()
            
            # Initialize analysis tools
            await self.text_analyzer.initialize()
            await self.web_scraper.initialize()
            
            # Initialize external APIs
            await self.search_apis.initialize()
            
            logger.info("SEO Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEO Agent: {e}")
            raise SEOError(f"Initialization failed: {e}")
    
    async def process(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process SEO optimization requests.
        
        Args:
            request: Dictionary containing:
                - action: SEO action (analyze, optimize, research_keywords, etc.)
                - content_id: Content ID for optimization
                - content_type: Type of content to optimize
                - target_keywords: Keywords to optimize for
                - optimization_goals: SEO optimization objectives
        
        Returns:
            AgentResponse with SEO results
        """
        start_time = time.time()
        
        try:
            action = request.get('action', 'analyze_content')
            
            if action == 'analyze_content':
                result = await self._analyze_content_seo(request)
            elif action == 'research_keywords':
                result = await self._research_keywords(request)
            elif action == 'optimize_content':
                result = await self._optimize_content_seo(request)
            elif action == 'audit_technical':
                result = await self._audit_technical_seo(request)
            elif action == 'analyze_competitors':
                result = await self._analyze_competitors(request)
            elif action == 'monitor_rankings':
                result = await self._monitor_search_rankings(request)
            elif action == 'generate_schema':
                result = await self._generate_schema_markup(request)
            elif action == 'build_links':
                result = await self._build_content_links(request)
            else:
                raise ValidationError(f"Unknown action: {action}")
            
            execution_time = time.time() - start_time
            self.update_metrics(execution_time, True)
            
            return AgentResponse(
                success=True,
                data=result,
                message=f"SEO {action} completed successfully",
                agent_type=self.agent_id,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_metrics(execution_time, False)
            
            logger.error(f"SEO processing error: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                agent_type=self.agent_id,
                execution_time=execution_time
            )
    
    async def _analyze_content_seo(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for SEO opportunities"""
        
        content_id = request.get('content_id')
        content_data = request.get('content_data', {})
        target_keywords = request.get('target_keywords', [])
        
        if not content_id:
            raise ValidationError("Content ID is required")
        
        # Analyze content structure and quality
        content_analysis = await self._analyze_content_structure(content_data)
        
        # Perform keyword analysis
        keyword_analysis = await self._analyze_content_keywords(
            content_data, target_keywords
        )
        
        # Check metadata optimization
        metadata_analysis = await self._analyze_metadata(content_data)
        
        # Analyze technical SEO factors
        technical_analysis = await self._analyze_technical_factors(content_data)
        
        # Calculate overall SEO score
        seo_score = await self._calculate_seo_score(
            content_analysis, keyword_analysis, metadata_analysis, technical_analysis
        )
        
        # Generate optimization recommendations
        recommendations = await self._generate_seo_recommendations(
            content_analysis, keyword_analysis, metadata_analysis, technical_analysis
        )
        
        # Identify optimization opportunities
        opportunities = await self._identify_optimization_opportunities(
            seo_score, recommendations
        )
        
        return {
            'content_id': content_id,
            'seo_score': seo_score,
            'content_analysis': content_analysis,
            'keyword_analysis': keyword_analysis,
            'metadata_analysis': metadata_analysis,
            'technical_analysis': technical_analysis,
            'recommendations': recommendations,
            'opportunities': opportunities,
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    async def _research_keywords(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Research keywords for content optimization"""
        
        seed_keywords = request.get('seed_keywords', [])
        content_topic = request.get('content_topic', '')
        target_audience = request.get('target_audience', {})
        language = request.get('language', 'en')
        
        if not seed_keywords and not content_topic:
            raise ValidationError("Either seed keywords or content topic is required")
        
        # Generate initial keyword list
        if content_topic:
            topic_keywords = await self._generate_topic_keywords(content_topic, language)
            seed_keywords.extend(topic_keywords)
        
        # Research keyword data
        keyword_data = []
        for keyword in seed_keywords:
            try:
                data = await self._research_single_keyword(keyword, language)
                keyword_data.append(data)
            except Exception as e:
                logger.error(f"Keyword research error for '{keyword}': {e}")
        
        # Find related keywords
        related_keywords = await self._find_related_keywords(seed_keywords, language)
        
        # Analyze keyword difficulty and opportunity
        keyword_opportunities = await self._analyze_keyword_opportunities(
            keyword_data + related_keywords, target_audience
        )
        
        # Generate keyword strategy
        keyword_strategy = await self._generate_keyword_strategy(
            keyword_opportunities, target_audience
        )
        
        return {
            'seed_keywords': seed_keywords,
            'researched_keywords': keyword_data,
            'related_keywords': related_keywords,
            'keyword_opportunities': keyword_opportunities,
            'keyword_strategy': keyword_strategy,
            'language': language,
            'researched_at': datetime.utcnow().isoformat()
        }
    
    async def _optimize_content_seo(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for better SEO performance"""
        
        content_id = request.get('content_id')
        content_data = request.get('content_data', {})
        target_keywords = request.get('target_keywords', [])
        optimization_goals = request.get('optimization_goals', [])
        
        if not content_id:
            raise ValidationError("Content ID is required")
        
        # Analyze current content
        current_analysis = await self._analyze_content_seo({
            'content_id': content_id,
            'content_data': content_data,
            'target_keywords': target_keywords
        })
        
        # Generate optimized content
        optimizations = {}
        
        # Optimize title and headings
        if 'title_optimization' in optimization_goals or not optimization_goals:
            title_optimization = await self.content_optimizer.optimize_title(
                content_data, target_keywords
            )
            optimizations['title'] = title_optimization
        
        # Optimize metadata
        if 'metadata_optimization' in optimization_goals or not optimization_goals:
            metadata_optimization = await self.metadata_optimizer.optimize_metadata(
                content_data, target_keywords
            )
            optimizations['metadata'] = metadata_optimization
        
        # Optimize content structure
        if 'content_structure' in optimization_goals or not optimization_goals:
            structure_optimization = await self.content_optimizer.optimize_structure(
                content_data, target_keywords
            )
            optimizations['structure'] = structure_optimization
        
        # Generate schema markup
        if 'schema_markup' in optimization_goals or not optimization_goals:
            schema_markup = await self._generate_schema_markup({
                'content_data': content_data,
                'content_type': request.get('content_type')
            })
            optimizations['schema'] = schema_markup
        
        # Calculate optimization impact
        optimization_impact = await self._calculate_optimization_impact(
            current_analysis, optimizations
        )
        
        return {
            'content_id': content_id,
            'current_analysis': current_analysis,
            'optimizations': optimizations,
            'optimization_impact': optimization_impact,
            'optimized_at': datetime.utcnow().isoformat()
        }
    
    async def _audit_technical_seo(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform technical SEO audit"""
        
        url = request.get('url', '')
        content_id = request.get('content_id')
        
        if not url and not content_id:
            raise ValidationError("Either URL or content ID is required")
        
        audit_results = {
            'url': url,
            'content_id': content_id,
            'audit_timestamp': datetime.utcnow().isoformat()
        }
        
        # Page speed analysis
        page_speed = await self._analyze_page_speed(url)
        audit_results['page_speed'] = page_speed
        
        # Mobile friendliness check
        mobile_check = await self._check_mobile_friendliness(url)
        audit_results['mobile_friendliness'] = mobile_check
        
        # HTML validation
        html_validation = await self._validate_html(url)
        audit_results['html_validation'] = html_validation
        
        # Schema markup validation
        schema_validation = await self._validate_schema_markup(url)
        audit_results['schema_validation'] = schema_validation
        
        # SSL certificate check
        ssl_check = await self._check_ssl_certificate(url)
        audit_results['ssl_certificate'] = ssl_check
        
        # Crawlability analysis
        crawlability = await self._analyze_crawlability(url)
        audit_results['crawlability'] = crawlability
        
        # Internal linking analysis
        internal_links = await self._analyze_internal_links(url)
        audit_results['internal_links'] = internal_links
        
        # Generate technical SEO score
        technical_score = await self._calculate_technical_seo_score(audit_results)
        audit_results['technical_score'] = technical_score
        
        # Generate fix recommendations
        fix_recommendations = await self._generate_technical_fix_recommendations(
            audit_results
        )
        audit_results['fix_recommendations'] = fix_recommendations
        
        return audit_results
    
    async def _analyze_competitors(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze SEO competitor performance"""
        
        target_keywords = request.get('target_keywords', [])
        competitor_urls = request.get('competitor_urls', [])
        industry = request.get('industry', '')
        
        if not target_keywords:
            raise ValidationError("Target keywords are required")
        
        competitor_analysis = {
            'target_keywords': target_keywords,
            'analyzed_competitors': [],
            'keyword_gaps': [],
            'content_gaps': [],
            'opportunities': [],
            'analyzed_at': datetime.utcnow().isoformat()
        }
        
        # Auto-discover competitors if not provided
        if not competitor_urls:
            competitor_urls = await self._discover_competitors(target_keywords, industry)
        
        # Analyze each competitor
        for competitor_url in competitor_urls:
            try:
                competitor_data = await self._analyze_single_competitor(
                    competitor_url, target_keywords
                )
                competitor_analysis['analyzed_competitors'].append(competitor_data)
            except Exception as e:
                logger.error(f"Competitor analysis error for {competitor_url}: {e}")
        
        # Identify keyword gaps
        keyword_gaps = await self._identify_keyword_gaps(
            target_keywords, competitor_analysis['analyzed_competitors']
        )
        competitor_analysis['keyword_gaps'] = keyword_gaps
        
        # Identify content gaps
        content_gaps = await self._identify_content_gaps(
            competitor_analysis['analyzed_competitors']
        )
        competitor_analysis['content_gaps'] = content_gaps
        
        # Generate competitive opportunities
        opportunities = await self._generate_competitive_opportunities(
            keyword_gaps, content_gaps, competitor_analysis['analyzed_competitors']
        )
        competitor_analysis['opportunities'] = opportunities
        
        return competitor_analysis
    
    async def _monitor_search_rankings(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor search engine rankings for keywords"""
        
        keywords = request.get('keywords', [])
        url = request.get('url', '')
        search_engines = request.get('search_engines', ['google', 'bing'])
        locations = request.get('locations', ['US'])
        
        if not keywords or not url:
            raise ValidationError("Keywords and URL are required")
        
        ranking_results = {
            'url': url,
            'keywords': keywords,
            'rankings': {},
            'ranking_changes': {},
            'monitored_at': datetime.utcnow().isoformat()
        }
        
        # Check rankings for each search engine and location
        for search_engine in search_engines:
            ranking_results['rankings'][search_engine] = {}
            
            for location in locations:
                location_rankings = {}
                
                for keyword in keywords:
                    try:
                        ranking = await self._check_keyword_ranking(
                            keyword, url, search_engine, location
                        )
                        location_rankings[keyword] = ranking
                        
                    except Exception as e:
                        logger.error(f"Ranking check error for '{keyword}': {e}")
                        location_rankings[keyword] = {'error': str(e)}
                
                ranking_results['rankings'][search_engine][location] = location_rankings
        
        # Calculate ranking changes
        ranking_changes = await self._calculate_ranking_changes(
            url, ranking_results['rankings']
        )
        ranking_results['ranking_changes'] = ranking_changes
        
        # Generate ranking insights
        ranking_insights = await self._generate_ranking_insights(
            ranking_results['rankings'], ranking_changes
        )
        ranking_results['insights'] = ranking_insights
        
        return ranking_results
    
    async def _generate_schema_markup(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured data schema markup"""
        
        content_data = request.get('content_data', {})
        content_type = request.get('content_type')
        schema_types = request.get('schema_types', [])
        
        if not content_data:
            raise ValidationError("Content data is required")
        
        # Determine schema types based on content
        if not schema_types:
            schema_types = await self._determine_schema_types(content_data, content_type)
        
        generated_schemas = {}
        
        for schema_type in schema_types:
            try:
                schema_markup = await self._generate_specific_schema(
                    schema_type, content_data
                )
                generated_schemas[schema_type] = schema_markup
                
            except Exception as e:
                logger.error(f"Schema generation error for {schema_type}: {e}")
                generated_schemas[schema_type] = {'error': str(e)}
        
        # Validate generated schemas
        validation_results = await self._validate_generated_schemas(generated_schemas)
        
        return {
            'content_type': content_type,
            'schema_types': schema_types,
            'generated_schemas': generated_schemas,
            'validation_results': validation_results,
    # ================== ADVANCED INTERNAL METHODS ==================

    async def _initialize_ai_models(self) -> None:
        """Initialize and load all AI models for SEO analysis"""
        try:
            await self.keyword_ranking_model.load_model()
            await self.content_optimization_model.load_model()
            await self.trend_prediction_model.load_model()
            logger.info("All AI models successfully initialized")
        except Exception as e:
            logger.error(f"AI model initialization failed: {str(e)}")
            raise

    async def _initialize_api_connections(self) -> None:
        """Initialize all external API connections"""
        try:
            await self.search_api_manager.initialize()
            await self.web_scraper.initialize()
            logger.info("All API connections established")
        except Exception as e:
            logger.error(f"API initialization failed: {str(e)}")
            raise

    async def _load_historical_data(self) -> None:
        """Load historical SEO data and analysis results"""
        try:
            # Load cached keyword data
            cached_keywords = await self._load_cached_keywords()
            self.keyword_cache.update(cached_keywords)
            
            # Load competitor insights
            cached_competitors = await self._load_cached_competitors()
            self.competitor_cache.update(cached_competitors)
            
            logger.info("Historical data successfully loaded")
        except Exception as e:
            logger.warning(f"Historical data loading failed: {str(e)}")

    async def _perform_health_check(self) -> bool:
        """Comprehensive system health check"""
        try:
            # Check AI models
            model_status = await self._check_ai_model_health()
            
            # Check API connections
            api_status = await self._check_api_health()
            
            # Check database connections
            db_status = await self._check_database_health()
            
            # Check system resources
            resource_status = await self._check_system_resources()
            
            all_healthy = all([model_status, api_status, db_status, resource_status])
            
            if not all_healthy:
                logger.warning("Some system components are not healthy")
            
            return all_healthy
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    async def _validate_content_input(self, content: Dict[str, Any]) -> None:
        """Validate content input for SEO analysis"""
        required_fields = ['type', 'title', 'content']
        
        for field in required_fields:
            if field not in content:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate content type
        try:
            ContentType(content['type'])
        except ValueError:
            raise ValidationError(f"Invalid content type: {content['type']}")
        
        # Validate content length
        if len(content.get('content', '')) < 100:
            logger.warning("Content is very short, analysis may be limited")

    async def _extract_content_metadata(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive content metadata"""
        return {
            'content_id': content.get('id', f"content_{int(time.time())}"),
            'title': content.get('title', ''),
            'description': content.get('description', ''),
            'url': content.get('url', ''),
            'content_type': content.get('type', 'blog_post'),
            'language': content.get('language', 'en'),
            'author': content.get('author', ''),
            'publish_date': content.get('publish_date'),
            'last_modified': content.get('last_modified'),
            'word_count': len(content.get('content', '').split()),
            'character_count': len(content.get('content', '')),
            'tags': content.get('tags', []),
            'categories': content.get('categories', []),
            'media_elements': content.get('media', {}),
            'custom_fields': content.get('custom_fields', {})
        }

    async def _analyze_keyword_optimization(
        self, 
        content: Dict[str, Any], 
        target_keywords: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Analyze keyword optimization with AI-powered insights"""
        try:
            content_text = content.get('content', '')
            title = content.get('title', '')
            
            if not target_keywords:
                # Extract keywords using AI
                target_keywords = await self._extract_content_keywords(content_text, title)
            
            # Analyze keyword presence and optimization
            keyword_analysis = {}
            for keyword in target_keywords:
                analysis = await self._analyze_single_keyword_optimization(
                    keyword, content_text, title, content
                )
                keyword_analysis[keyword] = analysis
            
            # Calculate overall keyword optimization score
            optimization_score = await self._calculate_keyword_optimization_score(keyword_analysis)
            
            return {
                'target_keywords': target_keywords,
                'keyword_analysis': keyword_analysis,
                'optimization_score': optimization_score,
                'keyword_density_analysis': await self._analyze_keyword_density(content_text, target_keywords),
                'keyword_distribution': await self._analyze_keyword_distribution(content_text, target_keywords),
                'semantic_keywords': await self._find_semantic_keywords(content_text, target_keywords),
                'missing_keywords': await self._identify_missing_keywords(content, target_keywords),
                'optimization_opportunities': await self._identify_keyword_opportunities(content, target_keywords)
            }
            
        except Exception as e:
            logger.error(f"Keyword optimization analysis failed: {str(e)}")
            return {'error': str(e), 'optimization_score': 0.0}

    async def _analyze_content_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced content structure analysis"""
        try:
            content_text = content.get('content', '')
            title = content.get('title', '')
            headings = content.get('headings', [])
            
            structure_analysis = {
                'title_analysis': await self._analyze_title_seo(title),
                'heading_structure': await self._analyze_heading_hierarchy(headings, content_text),
                'content_organization': await self._analyze_content_organization(content_text),
                'readability_metrics': await self._calculate_readability_metrics(content_text),
                'content_length_analysis': await self._analyze_content_length(content_text, content.get('type')),
                'paragraph_structure': await self._analyze_paragraph_structure(content_text),
                'sentence_structure': await self._analyze_sentence_structure(content_text),
                'content_flow': await self._analyze_content_flow(content_text, headings),
                'internal_linking': await self._analyze_internal_linking(content),
                'media_optimization': await self._analyze_media_elements(content.get('media', {})),
                'call_to_action': await self._analyze_call_to_action(content_text),
                'content_freshness': await self._analyze_content_freshness(content)
            }
            
            # Calculate overall structure score
            structure_score = await self._calculate_structure_score(structure_analysis)
            structure_analysis['overall_score'] = structure_score
            
            return structure_analysis
            
        except Exception as e:
            logger.error(f"Content structure analysis failed: {str(e)}")
            return {'error': str(e), 'overall_score': 0.0}

    async def _analyze_technical_seo(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive technical SEO analysis"""
        try:
            url = content.get('url', '')
            
            technical_analysis = {
                'url_structure': await self._analyze_url_structure(url),
                'meta_tags': await self._analyze_meta_tags(content),
                'schema_markup': await self._analyze_schema_markup(content),
                'page_speed': await self._analyze_page_speed(url),
                'mobile_optimization': await self._analyze_mobile_optimization(url),
                'ssl_security': await self._check_ssl_security(url),
                'crawlability': await self._analyze_crawlability(url),
                'indexability': await self._analyze_indexability(content),
                'duplicate_content': await self._check_duplicate_content(content),
                'canonical_tags': await self._analyze_canonical_tags(content),
                'robots_meta': await self._analyze_robots_meta(content),
                'structured_data': await self._validate_structured_data(content),
                'accessibility': await self._analyze_accessibility(url),
                'core_web_vitals': await self._measure_core_web_vitals(url)
            }
            
            # Identify technical issues
            technical_issues = await self._identify_technical_issues(technical_analysis)
            technical_analysis['issues'] = technical_issues
            
            # Calculate technical SEO score
            technical_score = await self._calculate_technical_score(technical_analysis)
            technical_analysis['technical_score'] = technical_score
            
            return technical_analysis
            
        except Exception as e:
            logger.error(f"Technical SEO analysis failed: {str(e)}")
            return {'error': str(e), 'technical_score': 0.0}

    async def _analyze_competitor_landscape(
        self, 
        content: Dict[str, Any], 
        competitor_urls: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Advanced competitor analysis with AI-powered insights"""
        try:
            if not competitor_urls:
                # Discover competitors using AI
                competitor_urls = await self._discover_competitors(content)
            
            competitor_analysis = {}
            
            for url in competitor_urls[:10]:  # Limit to top 10 competitors
                try:
                    analysis = await self._analyze_single_competitor(url, content)
                    competitor_analysis[url] = analysis
                except Exception as e:
                    logger.warning(f"Failed to analyze competitor {url}: {str(e)}")
                    continue
            
            # Perform comparative analysis
            comparative_insights = await self._perform_comparative_analysis(
                content, competitor_analysis
            )
            
            # Identify opportunities and threats
            opportunities = await self._identify_competitive_opportunities(
                content, competitor_analysis
            )
            
            threats = await self._identify_competitive_threats(
                content, competitor_analysis
            )
            
            return {
                'competitors_analyzed': len(competitor_analysis),
                'competitor_profiles': competitor_analysis,
                'comparative_insights': comparative_insights,
                'opportunities': opportunities,
                'threats': threats,
                'market_position': await self._determine_market_position(content, competitor_analysis),
                'gap_analysis': await self._perform_content_gap_analysis(content, competitor_analysis),
                'competitive_keywords': await self._extract_competitive_keywords(competitor_analysis),
                'benchmarking_data': await self._create_benchmarking_data(content, competitor_analysis)
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {str(e)}")
            return {'error': str(e), 'competitors_analyzed': 0}

    async def _analyze_user_experience(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """User experience analysis for SEO impact"""
        try:
            url = content.get('url', '')
            
            ux_analysis = {
                'page_load_time': await self._measure_page_load_time(url),
                'mobile_usability': await self._test_mobile_usability(url),
                'navigation_structure': await self._analyze_navigation(url),
                'content_accessibility': await self._analyze_content_accessibility(content),
                'user_engagement_signals': await self._analyze_engagement_signals(content),
                'bounce_rate_factors': await self._identify_bounce_rate_factors(content),
                'conversion_optimization': await self._analyze_conversion_elements(content),
                'visual_design_impact': await self._analyze_visual_design(url),
                'interactive_elements': await self._analyze_interactive_elements(url),
                'content_readability': await self._analyze_content_readability(content.get('content', ''))
            }
            
            # Calculate UX score
            ux_score = await self._calculate_ux_score(ux_analysis)
            ux_analysis['ux_score'] = ux_score
            
            return ux_analysis
            
        except Exception as e:
            logger.error(f"User experience analysis failed: {str(e)}")
            return {'error': str(e), 'ux_score': 0.0}

    async def _research_primary_keywords(
        self, 
        seed_keywords: List[str], 
        content_type: ContentType
    ) -> Dict[str, KeywordData]:
        """Research primary keywords using multiple sources"""
        primary_keywords = {}
        
        for keyword in seed_keywords:
            try:
                # Get keyword data from multiple sources
                google_data = await self._get_google_keyword_data(keyword)
                bing_data = await self._get_bing_keyword_data(keyword)
                trend_data = await self._get_keyword_trend_data(keyword)
                
                # Combine and analyze data
                combined_data = await self._combine_keyword_sources(
                    keyword, google_data, bing_data, trend_data, content_type
                )
                
                primary_keywords[keyword] = combined_data
                
            except Exception as e:
                logger.warning(f"Failed to research primary keyword '{keyword}': {str(e)}")
                continue
        
        return primary_keywords

    async def _enhance_keyword_data(
        self, 
        keyword: str, 
        base_data: KeywordData, 
        content_type: ContentType,
        target_audience: Optional[Dict[str, Any]],
        language: str
    ) -> KeywordData:
        """Enhance keyword data with additional intelligence"""
        try:
            # Get seasonal trends
            seasonality = await self._analyze_keyword_seasonality(keyword)
            
            # Analyze search intent
            search_intent = await self._classify_search_intent(keyword, content_type)
            
            # Get demographic data
            demographics = await self._get_keyword_demographics(keyword, target_audience)
            
            # Analyze device breakdown
            device_data = await self._get_device_breakdown(keyword)
            
            # Calculate conversion potential
            conversion_potential = await self._calculate_conversion_potential(
                keyword, content_type, search_intent
            )
            
            # Find content gaps
            content_gaps = await self._identify_content_gaps(keyword, content_type)
            
            # Update the KeywordData object
            enhanced_data = KeywordData(
                keyword=keyword,
                search_volume=base_data.search_volume,
                competition_level=base_data.competition_level,
                cost_per_click=base_data.cost_per_click,
                keyword_difficulty=base_data.keyword_difficulty,
                relevance_score=base_data.relevance_score,
                trending_score=base_data.trending_score,
                seasonality_data=seasonality,
                search_intent=search_intent,
                related_keywords=base_data.related_keywords,
                long_tail_variations=await self._generate_long_tail_variations(keyword),
                question_variations=await self._generate_question_variations(keyword),
                competitor_keywords=base_data.competitor_keywords,
                search_features=await self._identify_search_features(keyword),
                local_search_volume=await self._get_local_search_volume(keyword),
                demographic_data=demographics,
                device_breakdown=device_data,
                conversion_potential=conversion_potential,
                content_gap_opportunities=content_gaps,
                suggested_content_types=await self._suggest_content_types(keyword, search_intent),
                last_updated=datetime.now()
            )
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Failed to enhance keyword data for '{keyword}': {str(e)}")
            return base_data

    # Additional helper methods for comprehensive functionality
    async def _combine_analysis_results(
        self, 
        metadata: Dict[str, Any], 
        results: List[Any], 
        depth: str
    ) -> Dict[str, Any]:
        """Combine all analysis results into comprehensive report"""
        # Process each analysis result and combine intelligently
        combined = {
            'metadata': metadata,
            'keyword_analysis': results[0] if not isinstance(results[0], Exception) else {},
            'content_structure': results[1] if not isinstance(results[1], Exception) else {},
            'technical_seo': results[2] if not isinstance(results[2], Exception) else {},
            'competitor_analysis': results[3] if not isinstance(results[3], Exception) else {},
            'user_experience': results[4] if not isinstance(results[4], Exception) else {},
            'mobile_optimization': results[5] if not isinstance(results[5], Exception) else {},
            'page_speed': results[6] if not isinstance(results[6], Exception) else {},
            'schema_markup': results[7] if not isinstance(results[7], Exception) else {},
            'backlink_profile': results[8] if not isinstance(results[8], Exception) else {},
            'social_signals': results[9] if not isinstance(results[9], Exception) else {},
        }
        
        # Add depth-specific analysis
        if depth == "expert":
            combined.update(await self._add_expert_analysis(combined))
        
        return combined

    async def shutdown(self) -> None:
        """Gracefully shutdown the SEO agent"""
        try:
            # Save current state
            await self._save_agent_state()
            
            # Close external connections
            await self.search_api_manager.close()
            await self.web_scraper.close()
            
            # Shutdown thread pool
            self.executor.shutdown(wait=True)
            
            logger.info("SEO Agent successfully shut down")
            
        except Exception as e:
            logger.error(f"Error during SEO Agent shutdown: {str(e)}")

# Export the main agent class
__all__ = ['SEOAgent', 'SEOAnalysis', 'KeywordData', 'OptimizationType', 'ContentType', 
           'SEOPriority', 'SearchEngineType', 'KeywordIntent', 'CompetitorTier',
           'SEOMetrics', 'CompetitorInsight', 'OptimizationRecommendation']
        
        if not headings:
            return {'has_headings': False}
        
        # Count heading levels (assuming format like "H1: Title")
        heading_levels = {}
        for heading in headings:
            level = heading[:2] if heading.startswith('H') else 'Unknown'
            heading_levels[level] = heading_levels.get(level, 0) + 1
        
        return {
            'has_headings': True,
            'total_headings': len(headings),
            'heading_levels': heading_levels,
            'proper_hierarchy': self._check_heading_hierarchy(heading_levels)
        }
    
    def _check_heading_hierarchy(self, heading_levels: Dict[str, int]) -> bool:
        """Check if heading hierarchy is proper"""
        # Simple check: should have H1, and no gaps in hierarchy
        has_h1 = 'H1' in heading_levels
        
        # Check for gaps (e.g., H1 -> H3 without H2)
        levels = sorted([int(level[1]) for level in heading_levels.keys() if level.startswith('H')])
        has_gaps = len(levels) > 1 and max(levels) - min(levels) + 1 != len(levels)
        
        return has_h1 and not has_gaps
    
    async def _calculate_keyword_density(self, text_content: str) -> Dict[str, float]:
        """Calculate keyword density for content"""
        if not text_content:
            return {}
        
        # Simple keyword density calculation
        words = text_content.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        word_counts = Counter(words)
        keyword_density = {}
        
        # Calculate density for words that appear more than once
        for word, count in word_counts.items():
            if count > 1 and len(word) > 3:  # Only significant words
                density = (count / total_words) * 100
                keyword_density[word] = round(density, 2)
        
        return keyword_density
    
    async def _assess_content_quality(self, content_data: Dict[str, Any]) -> float:
        """Assess overall content quality"""
        score = 0.0
        factors = 0
        
        # Title quality
        title = content_data.get('title', '')
        if title:
            score += min(len(title.split()) / 10, 1.0)  # Optimal title length
            factors += 1
        
        # Content length
        content = content_data.get('text_content', '')
        if content:
            word_count = len(content.split())
            if 300 <= word_count <= 2500:  # Optimal content length
                score += 1.0
            elif word_count > 100:
                score += 0.7
            elif word_count > 50:
                score += 0.5
            factors += 1
        
        # Image presence
        if content_data.get('images'):
            score += 0.8
            factors += 1
        
        # Headings structure
        headings = content_data.get('headings', [])
        if headings:
            score += min(len(headings) / 5, 1.0)  # Good heading count
            factors += 1
        
        return score / factors if factors > 0 else 0.0
    
    async def _analyze_content_keywords(
        self, 
        content_data: Dict[str, Any], 
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """Analyze keyword usage in content"""
        content_text = content_data.get('text_content', '')
        title = content_data.get('title', '')
        
        analysis = {
            'target_keywords_found': [],
            'keyword_positions': {},
            'keyword_densities': {},
            'title_keyword_usage': {},
            'heading_keyword_usage': {},
            'total_keyword_score': 0.0
        }
        
        if not content_text:
            return analysis
        
        content_lower = content_text.lower()
        title_lower = title.lower()
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            # Check presence
            if keyword_lower in content_lower:
                analysis['target_keywords_found'].append(keyword)
            
            # Calculate density
            keyword_count = content_lower.count(keyword_lower)
            total_words = len(content_text.split())
            if total_words > 0:
                density = (keyword_count / total_words) * 100
                analysis['keyword_densities'][keyword] = round(density, 2)
            
            # Check title usage
            analysis['title_keyword_usage'][keyword] = keyword_lower in title_lower
            
            # Find positions (first few occurrences)
            positions = []
            start = 0
            for _ in range(min(3, keyword_count)):  # First 3 positions
                pos = content_lower.find(keyword_lower, start)
                if pos != -1:
                    positions.append(pos)
                    start = pos + len(keyword_lower)
            analysis['keyword_positions'][keyword] = positions
        
        # Calculate overall keyword score
        found_ratio = len(analysis['target_keywords_found']) / len(target_keywords) if target_keywords else 0
        title_usage_ratio = sum(analysis['title_keyword_usage'].values()) / len(target_keywords) if target_keywords else 0
        analysis['total_keyword_score'] = (found_ratio * 0.7) + (title_usage_ratio * 0.3)
        
        return analysis
    
    async def _analyze_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metadata quality"""
        analysis = {
            'has_title': bool(content_data.get('title')),
            'title_length': len(content_data.get('title', '')),
            'has_description': bool(content_data.get('description')),
            'description_length': len(content_data.get('description', '')),
            'has_keywords': bool(content_data.get('keywords')),
            'has_og_tags': bool(content_data.get('og_tags')),
            'has_canonical': bool(content_data.get('canonical_url')),
            'metadata_score': 0.0
        }
        
        # Calculate metadata score
        score_factors = []
        
        # Title optimization
        title_length = analysis['title_length']
        if 30 <= title_length <= 60:
            score_factors.append(1.0)
        elif 20 <= title_length <= 70:
            score_factors.append(0.8)
        elif title_length > 0:
            score_factors.append(0.5)
        else:
            score_factors.append(0.0)
        
        # Description optimization
        desc_length = analysis['description_length']
        if 120 <= desc_length <= 160:
            score_factors.append(1.0)
        elif 100 <= desc_length <= 180:
            score_factors.append(0.8)
        elif desc_length > 0:
            score_factors.append(0.5)
        else:
            score_factors.append(0.0)
        
        # Other metadata factors
        score_factors.append(1.0 if analysis['has_keywords'] else 0.0)
        score_factors.append(1.0 if analysis['has_og_tags'] else 0.0)
        score_factors.append(1.0 if analysis['has_canonical'] else 0.0)
        
        analysis['metadata_score'] = sum(score_factors) / len(score_factors) if score_factors else 0.0
        
        return analysis
    
    async def _analyze_technical_factors(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical SEO factors"""
        analysis = {
            'has_images': bool(content_data.get('images')),
            'images_with_alt': 0,
            'total_images': 0,
            'has_internal_links': bool(content_data.get('internal_links')),
            'internal_links_count': len(content_data.get('internal_links', [])),
            'has_external_links': bool(content_data.get('external_links')),
            'external_links_count': len(content_data.get('external_links', [])),
            'mobile_friendly': content_data.get('mobile_friendly', True),
            'page_speed': content_data.get('page_speed', 50),
            'technical_score': 0.0
        }
        
        # Analyze images
        images = content_data.get('images', [])
        if images:
            analysis['total_images'] = len(images)
            analysis['images_with_alt'] = sum(1 for img in images if img.get('alt_text'))
        
        # Calculate technical score
        score_factors = []
        
        # Image optimization
        if analysis['total_images'] > 0:
            alt_ratio = analysis['images_with_alt'] / analysis['total_images']
            score_factors.append(alt_ratio)
        else:
            score_factors.append(0.5)  # Neutral for no images
        
        # Link structure
        if analysis['internal_links_count'] > 0:
            score_factors.append(min(analysis['internal_links_count'] / 5, 1.0))
        else:
            score_factors.append(0.3)
        
        # Mobile and speed
        score_factors.append(1.0 if analysis['mobile_friendly'] else 0.0)
        score_factors.append(analysis['page_speed'] / 100)
        
        analysis['technical_score'] = sum(score_factors) / len(score_factors) if score_factors else 0.0
        
        return analysis
    
    async def _calculate_seo_score(
        self,
        content_analysis: Dict[str, Any],
        keyword_analysis: Dict[str, Any],
        metadata_analysis: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall SEO score"""
        scores = [
            content_analysis.get('content_quality_score', 0) * self.optimization_weights.get('content_quality', 0.2),
            keyword_analysis.get('total_keyword_score', 0) * self.optimization_weights.get('keyword_relevance', 0.25),
            metadata_analysis.get('metadata_score', 0) * self.optimization_weights.get('technical_seo', 0.2),
            technical_analysis.get('technical_score', 0) * self.optimization_weights.get('technical_seo', 0.2),
        ]
        
        # Add engagement and social signals if available
        scores.append(0.7 * self.optimization_weights.get('user_engagement', 0.15))  # Placeholder
        
        return min(sum(scores), 1.0)  # Cap at 1.0
    
    async def _generate_seo_recommendations(
        self,
        content_analysis: Dict[str, Any],
        keyword_analysis: Dict[str, Any],
        metadata_analysis: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate SEO improvement recommendations"""
        recommendations = []
        
        # Content recommendations
        if content_analysis.get('word_count', 0) < 300:
            recommendations.append({
                'type': 'content_length',
                'priority': 8,
                'message': 'Content is too short. Aim for at least 300 words for better SEO.',
                'action': 'Expand content with valuable information'
            })
        
        # Keyword recommendations
        if keyword_analysis.get('total_keyword_score', 0) < 0.5:
            recommendations.append({
                'type': 'keyword_optimization',
                'priority': 9,
                'message': 'Low keyword optimization. Include target keywords more naturally.',
                'action': 'Review keyword placement in title, headings, and content'
            })
        
        # Metadata recommendations
        if not metadata_analysis.get('has_description'):
            recommendations.append({
                'type': 'meta_description',
                'priority': 7,
                'message': 'Missing meta description.',
                'action': 'Add compelling meta description (120-160 characters)'
            })
        
        # Technical recommendations
        if technical_analysis.get('images_with_alt', 0) < technical_analysis.get('total_images', 1):
            recommendations.append({
                'type': 'image_alt_text',
                'priority': 6,
                'message': 'Some images missing alt text.',
                'action': 'Add descriptive alt text to all images'
            })
        
        # Heading recommendations
        if not content_analysis.get('heading_structure', {}).get('has_headings'):
            recommendations.append({
                'type': 'heading_structure',
                'priority': 7,
                'message': 'No headings found. Use H1-H6 tags to structure content.',
                'action': 'Add proper heading hierarchy to organize content'
            })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return recommendations
    
    async def _identify_optimization_opportunities(
        self,
        seo_score: float,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities"""
        opportunities = []
        
        # High-impact opportunities based on score
        if seo_score < 0.3:
            opportunities.append({
                'type': 'comprehensive_optimization',
                'impact': 'high',
                'effort': 'high',
                'description': 'Complete SEO overhaul needed',
                'estimated_improvement': 0.5
            })
        elif seo_score < 0.6:
            opportunities.append({
                'type': 'targeted_improvements',
                'impact': 'medium',
                'effort': 'medium',
                'description': 'Focus on key SEO elements',
                'estimated_improvement': 0.3
            })
        else:
            opportunities.append({
                'type': 'fine_tuning',
                'impact': 'low',
                'effort': 'low',
                'description': 'Minor optimizations for better performance',
                'estimated_improvement': 0.1
            })
        
        # Specific opportunities from recommendations
        for rec in recommendations[:5]:  # Top 5 recommendations
            opportunities.append({
                'type': rec['type'],
                'impact': 'high' if rec['priority'] >= 8 else 'medium' if rec['priority'] >= 6 else 'low',
                'effort': 'low',  # Most recommendations are easy to implement
                'description': rec['message'],
                'action': rec['action']
            })
        
        return opportunities
    
    # Continue with additional helper methods...
    async def _generate_topic_keywords(self, topic: str, language: str) -> List[str]:
        """Generate keywords related to a topic"""
        # Simple topic keyword generation - in production, use ML models
        base_keywords = [topic.lower()]
        
        # Add common variations
        variations = [
            f"what is {topic}",
            f"how to {topic}",
            f"{topic} guide",
            f"{topic} tips",
            f"best {topic}",
            f"{topic} tutorial",
            f"{topic} examples"
        ]
        
        return base_keywords + variations
    
    async def _research_single_keyword(self, keyword: str, language: str) -> Dict[str, Any]:
        """Research a single keyword"""
        # Mock research data - integrate with real APIs in production
        return {
            'keyword': keyword,
            'search_volume': np.random.randint(100, 10000),
            'competition': np.random.random(),
            'cpc': round(np.random.uniform(0.5, 5.0), 2),
            'difficulty': np.random.choice(['easy', 'medium', 'hard']),
            'trend': np.random.choice(['rising', 'stable', 'declining'])
        }
    
    async def _find_related_keywords(self, keywords: List[str], language: str) -> List[Dict[str, Any]]:
        """Find related keywords"""
        related = []
        
        for keyword in keywords[:5]:  # Limit to avoid too many API calls
            # Generate related keywords based on base keyword
            related_variations = [
                f"{keyword} benefits",
                f"{keyword} problems",
                f"{keyword} solutions",
                f"{keyword} comparison",
                f"{keyword} alternatives"
            ]
            
            for related_kw in related_variations:
                related.append({
                    'keyword': related_kw,
                    'relation_score': np.random.uniform(0.5, 1.0),
                    'search_volume': np.random.randint(50, 5000)
                })
        
        return related[:20]  # Return top 20
    
    # Additional helper methods for completeness...
    async def _analyze_keyword_opportunities(
        self, 
        keyword_data: List[Dict[str, Any]], 
        target_audience: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze keyword opportunities"""
        opportunities = []
        
        for kw_data in keyword_data:
            opportunity_score = self._calculate_opportunity_score(kw_data)
            if opportunity_score > 0.6:  # Good opportunity threshold
                opportunities.append({
                    **kw_data,
                    'opportunity_score': opportunity_score,
                    'reason': self._get_opportunity_reason(kw_data)
                })
        
        return sorted(opportunities, key=lambda x: x['opportunity_score'], reverse=True)
    
    def _calculate_opportunity_score(self, keyword_data: Dict[str, Any]) -> float:
        """Calculate opportunity score for a keyword"""
        # Simple scoring - in production use more sophisticated models
        volume_score = min(keyword_data.get('search_volume', 0) / 10000, 1.0)
        competition_score = 1.0 - keyword_data.get('competition', 1.0)
        trend_score = 1.0 if keyword_data.get('trend') == 'rising' else 0.5
        
        return (volume_score * 0.4) + (competition_score * 0.4) + (trend_score * 0.2)
    
    def _get_opportunity_reason(self, keyword_data: Dict[str, Any]) -> str:
        """Get human-readable reason for opportunity"""
        reasons = []
        
        if keyword_data.get('search_volume', 0) > 1000:
            reasons.append("high search volume")
        
        if keyword_data.get('competition', 1.0) < 0.5:
            reasons.append("low competition")
        
        if keyword_data.get('trend') == 'rising':
            reasons.append("rising trend")
        
        return "; ".join(reasons) if reasons else "balanced metrics"
    
    async def _generate_keyword_strategy(
        self, 
        opportunities: List[Dict[str, Any]], 
        target_audience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate keyword strategy"""
        return {
            'primary_keywords': [op['keyword'] for op in opportunities[:3]],
            'secondary_keywords': [op['keyword'] for op in opportunities[3:10]],
            'long_tail_keywords': [op['keyword'] for op in opportunities[10:20] if len(op['keyword'].split()) > 3],
            'content_gaps': ['Content gap analysis would be implemented here'],
            'strategy_notes': [
                'Focus on primary keywords for main content',
                'Use secondary keywords for supporting content',
                'Target long-tail keywords for specific topics'
            ]
        }
    
    # Additional missing methods to complete the implementation
    async def _calculate_optimization_impact(
        self,
        current_analysis: Dict[str, Any],
        optimizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate the impact of optimizations"""
        current_score = current_analysis.get('seo_score', 0)
        
        # Estimate improvement based on optimization types
        improvement_factors = {
            'title': 0.15,
            'metadata': 0.20,
            'structure': 0.25,
            'schema': 0.10
        }
        
        total_improvement = sum(
            improvement_factors.get(opt_type, 0.1)
            for opt_type in optimizations.keys()
        )
        
        projected_score = min(current_score + total_improvement, 1.0)
        
        return {
            'current_score': current_score,
            'projected_score': projected_score,
            'improvement': projected_score - current_score,
            'improvement_percentage': ((projected_score - current_score) / current_score * 100) if current_score > 0 else 0,
            'optimization_breakdown': {
                opt_type: improvement_factors.get(opt_type, 0.1)
                for opt_type in optimizations.keys()
            }
        }
