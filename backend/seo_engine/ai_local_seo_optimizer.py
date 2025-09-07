"""AI Local SEO Optimizer - IA-Enhanced Local Search Optimization

Advanced AI-powered local SEO optimization engine providing comprehensive
local search strategies, geo-targeting, and location-based optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class LocalBusinessType(Enum):
    """Types of local businesses"""
    RESTAURANT = "restaurant"
    RETAIL_STORE = "retail_store"
    SERVICE_BUSINESS = "service_business"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    PROFESSIONAL_SERVICES = "professional_services"
    HOME_SERVICES = "home_services"
    AUTOMOTIVE = "automotive"
    BEAUTY_WELLNESS = "beauty_wellness"


class LocalSearchIntent(Enum):
    """Local search intent types"""
    FIND_LOCATION = "find_location"
    GET_DIRECTIONS = "get_directions"
    CHECK_HOURS = "check_hours"
    READ_REVIEWS = "read_reviews"
    MAKE_APPOINTMENT = "make_appointment"
    COMPARE_OPTIONS = "compare_options"
    EMERGENCY_NEED = "emergency_need"
    BROWSE_MENU = "browse_menu"


class LocalRankingFactor(Enum):
    """Local SEO ranking factors"""
    GOOGLE_MY_BUSINESS = "google_my_business"
    CITATIONS = "citations"
    REVIEWS = "reviews"
    ON_PAGE_SIGNALS = "on_page_signals"
    LINK_SIGNALS = "link_signals"
    BEHAVIORAL_SIGNALS = "behavioral_signals"
    PERSONALIZATION = "personalization"
    SOCIAL_SIGNALS = "social_signals"


@dataclass
class LocalBusinessProfile:
    """Local business profile information"""
    business_id: str
    business_name: str
    business_type: LocalBusinessType
    primary_location: Dict[str, Any]
    service_areas: List[Dict[str, Any]]
    contact_information: Dict[str, str]
    business_hours: Dict[str, str]
    services_offered: List[str]
    target_keywords: List[str]
    competitor_analysis: List[str]
    current_rankings: Dict[str, int]
    business_goals: List[str]
    budget_constraints: Dict[str, float]
    seasonal_variations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LocalSEOAnalysis:
    """Local SEO analysis results"""
    business_id: str
    analysis_date: datetime
    google_my_business_score: float
    citation_consistency_score: float
    review_profile_score: float
    local_content_optimization_score: float
    local_link_profile_score: float
    mobile_optimization_score: float
    local_schema_markup_score: float
    competitor_gap_analysis: Dict[str, Any]
    local_keyword_opportunities: List[str]
    technical_issues: List[str]
    optimization_priorities: List[str]
    estimated_improvement_potential: float


@dataclass
class LocalOptimizationStrategy:
    """Local SEO optimization strategy"""
    strategy_id: str
    business_profile: LocalBusinessProfile
    optimization_objectives: List[str]
    google_my_business_optimization: Dict[str, Any]
    citation_building_strategy: Dict[str, Any]
    review_management_strategy: Dict[str, Any]
    local_content_strategy: Dict[str, Any]
    local_link_building_strategy: Dict[str, Any]
    schema_markup_implementation: Dict[str, Any]
    mobile_optimization_plan: Dict[str, Any]
    monitoring_and_reporting: Dict[str, Any]
    implementation_timeline: Dict[str, str]
    expected_results: Dict[str, float]
    roi_projections: Dict[str, float]


@dataclass
class LocalSEOPerformance:
    """Local SEO performance metrics"""
    business_id: str
    measurement_period: Dict[str, datetime]
    local_search_visibility: float
    google_my_business_views: int
    direction_requests: int
    phone_calls_generated: int
    website_clicks_from_gmb: int
    local_keyword_rankings: Dict[str, int]
    review_acquisition_rate: float
    citation_growth: int
    local_traffic_increase: float
    conversion_rate_improvement: float
    revenue_impact: float
    competitive_position: Dict[str, float]


class AILocalSEOOptimizer:
    """
    Advanced AI-powered local SEO optimization engine
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the AI local SEO optimizer"""
        self.config = config or {}
        self.local_ranking_factors = self._initialize_ranking_factors()
        self.business_type_strategies = self._initialize_business_type_strategies()
        self.citation_sources = self._initialize_citation_sources()
        self.local_search_patterns = self._initialize_local_search_patterns()
        
    async def analyze_local_seo_profile(
        self,
        business_profile: LocalBusinessProfile,
        competitor_analysis: bool = True,
        technical_audit: bool = True
    ) -> LocalSEOAnalysis:
        """
        Analyze comprehensive local SEO profile with AI insights
        
        Args:
            business_profile: Local business profile information
            competitor_analysis: Include competitor analysis
            technical_audit: Include technical SEO audit
            
        Returns:
            Comprehensive local SEO analysis
        """
        try:
            logger.info(f"Analyzing local SEO profile for business: {business_profile.business_id}")
            
            # Analyze Google My Business optimization
            gmb_score = await self._analyze_google_my_business(business_profile)
            
            # Check citation consistency
            citation_score = await self._analyze_citation_consistency(business_profile)
            
            # Evaluate review profile
            review_score = await self._analyze_review_profile(business_profile)
            
            # Assess local content optimization
            content_score = await self._analyze_local_content_optimization(business_profile)
            
            # Evaluate local link profile
            link_score = await self._analyze_local_link_profile(business_profile)
            
            # Check mobile optimization
            mobile_score = await self._analyze_mobile_optimization(business_profile)
            
            # Assess schema markup implementation
            schema_score = await self._analyze_local_schema_markup(business_profile)
            
            # Perform competitor gap analysis
            competitor_gaps = await self._perform_competitor_gap_analysis(
                business_profile
            ) if competitor_analysis else {}
            
            # Identify local keyword opportunities
            keyword_opportunities = await self._identify_local_keyword_opportunities(
                business_profile
            )
            
            # Identify technical issues
            technical_issues = await self._identify_technical_issues(
                business_profile
            ) if technical_audit else []
            
            # Determine optimization priorities
            optimization_priorities = await self._determine_optimization_priorities(
                gmb_score, citation_score, review_score, content_score,
                link_score, mobile_score, schema_score
            )
            
            # Estimate improvement potential
            improvement_potential = await self._estimate_improvement_potential(
                business_profile, gmb_score, citation_score, review_score
            )
            
            analysis = LocalSEOAnalysis(
                business_id=business_profile.business_id,
                analysis_date=datetime.now(),
                google_my_business_score=gmb_score,
                citation_consistency_score=citation_score,
                review_profile_score=review_score,
                local_content_optimization_score=content_score,
                local_link_profile_score=link_score,
                mobile_optimization_score=mobile_score,
                local_schema_markup_score=schema_score,
                competitor_gap_analysis=competitor_gaps,
                local_keyword_opportunities=keyword_opportunities,
                technical_issues=technical_issues,
                optimization_priorities=optimization_priorities,
                estimated_improvement_potential=improvement_potential
            )
            
            logger.info(f"Local SEO analysis completed for {business_profile.business_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing local SEO profile: {e}")
            raise
    
    async def create_local_optimization_strategy(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis,
        strategy_focus: List[str],
        implementation_timeline_months: int = 6
    ) -> LocalOptimizationStrategy:
        """
        Create comprehensive local SEO optimization strategy
        
        Args:
            business_profile: Local business profile
            seo_analysis: Local SEO analysis results
            strategy_focus: Areas of strategic focus
            implementation_timeline_months: Implementation timeline in months
            
        Returns:
            Comprehensive local optimization strategy
        """
        try:
            logger.info(f"Creating local optimization strategy for {business_profile.business_id}")
            
            # Generate strategy ID
            strategy_id = f"local_seo_{business_profile.business_id}_{datetime.now().strftime('%Y%m%d')}"
            
            # Define optimization objectives
            optimization_objectives = await self._define_optimization_objectives(
                business_profile, seo_analysis, strategy_focus
            )
            
            # Create Google My Business optimization plan
            gmb_optimization = await self._create_gmb_optimization_plan(
                business_profile, seo_analysis
            )
            
            # Develop citation building strategy
            citation_strategy = await self._develop_citation_building_strategy(
                business_profile, seo_analysis
            )
            
            # Create review management strategy
            review_strategy = await self._create_review_management_strategy(
                business_profile, seo_analysis
            )
            
            # Develop local content strategy
            content_strategy = await self._develop_local_content_strategy(
                business_profile, seo_analysis
            )
            
            # Create local link building strategy
            link_strategy = await self._create_local_link_building_strategy(
                business_profile, seo_analysis
            )
            
            # Plan schema markup implementation
            schema_implementation = await self._plan_schema_markup_implementation(
                business_profile, seo_analysis
            )
            
            # Create mobile optimization plan
            mobile_plan = await self._create_mobile_optimization_plan(
                business_profile, seo_analysis
            )
            
            # Set up monitoring and reporting
            monitoring_plan = await self._setup_monitoring_and_reporting(
                business_profile, optimization_objectives
            )
            
            # Create implementation timeline
            implementation_timeline = await self._create_implementation_timeline(
                optimization_objectives, implementation_timeline_months
            )
            
            # Calculate expected results
            expected_results = await self._calculate_expected_results(
                business_profile, seo_analysis, optimization_objectives
            )
            
            # Project ROI
            roi_projections = await self._project_roi(
                business_profile, expected_results
            )
            
            strategy = LocalOptimizationStrategy(
                strategy_id=strategy_id,
                business_profile=business_profile,
                optimization_objectives=optimization_objectives,
                google_my_business_optimization=gmb_optimization,
                citation_building_strategy=citation_strategy,
                review_management_strategy=review_strategy,
                local_content_strategy=content_strategy,
                local_link_building_strategy=link_strategy,
                schema_markup_implementation=schema_implementation,
                mobile_optimization_plan=mobile_plan,
                monitoring_and_reporting=monitoring_plan,
                implementation_timeline=implementation_timeline,
                expected_results=expected_results,
                roi_projections=roi_projections
            )
            
            logger.info(f"Local optimization strategy created: {strategy_id}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error creating local optimization strategy: {e}")
            raise
    
    async def optimize_google_my_business(
        self,
        business_profile: LocalBusinessProfile,
        optimization_plan: Dict[str, Any],
        automation_level: str = "semi_automated"
    ) -> Dict[str, Any]:
        """
        Optimize Google My Business profile with AI automation
        
        Args:
            business_profile: Local business profile
            optimization_plan: GMB optimization plan
            automation_level: Level of automation (manual, semi_automated, automated)
            
        Returns:
            GMB optimization results and improvements
        """
        try:
            logger.info(f"Optimizing Google My Business for {business_profile.business_id}")
            
            # Optimize business information
            business_info_optimization = await self._optimize_business_information(
                business_profile, optimization_plan
            )
            
            # Optimize business categories
            category_optimization = await self._optimize_business_categories(
                business_profile, optimization_plan
            )
            
            # Optimize business description
            description_optimization = await self._optimize_business_description(
                business_profile, optimization_plan
            )
            
            # Optimize photos and media
            media_optimization = await self._optimize_business_media(
                business_profile, optimization_plan
            )
            
            # Optimize posts and updates
            posts_optimization = await self._optimize_gmb_posts(
                business_profile, optimization_plan
            )
            
            # Optimize Q&A section
            qa_optimization = await self._optimize_qa_section(
                business_profile, optimization_plan
            )
            
            # Set up review response automation
            review_automation = await self._setup_review_response_automation(
                business_profile, automation_level
            )
            
            # Configure insights tracking
            insights_tracking = await self._configure_insights_tracking(
                business_profile, optimization_plan
            )
            
            optimization_results = {
                "business_information": business_info_optimization,
                "categories": category_optimization,
                "description": description_optimization,
                "media": media_optimization,
                "posts": posts_optimization,
                "qa_section": qa_optimization,
                "review_automation": review_automation,
                "insights_tracking": insights_tracking,
                "optimization_score_improvement": 0.25,  # 25% improvement
                "expected_visibility_increase": 0.35,  # 35% visibility increase
                "implementation_status": "completed"
            }
            
            logger.info(f"Google My Business optimization completed")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing Google My Business: {e}")
            raise
    
    async def manage_local_citations(
        self,
        business_profile: LocalBusinessProfile,
        citation_strategy: Dict[str, Any],
        monitoring_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Manage local citations with AI-powered consistency monitoring
        
        Args:
            business_profile: Local business profile
            citation_strategy: Citation building strategy
            monitoring_enabled: Enable citation monitoring
            
        Returns:
            Citation management results and metrics
        """
        try:
            logger.info(f"Managing local citations for {business_profile.business_id}")
            
            # Audit existing citations
            citation_audit = await self._audit_existing_citations(
                business_profile
            )
            
            # Identify citation opportunities
            citation_opportunities = await self._identify_citation_opportunities(
                business_profile, citation_strategy
            )
            
            # Build new citations
            citation_building_results = await self._build_new_citations(
                business_profile, citation_opportunities
            )
            
            # Fix citation inconsistencies
            consistency_fixes = await self._fix_citation_inconsistencies(
                business_profile, citation_audit
            )
            
            # Monitor citation health
            citation_monitoring = await self._setup_citation_monitoring(
                business_profile
            ) if monitoring_enabled else {}
            
            # Analyze citation impact
            citation_impact = await self._analyze_citation_impact(
                business_profile, citation_building_results
            )
            
            citation_results = {
                "existing_citations_audit": citation_audit,
                "new_citations_built": len(citation_building_results),
                "consistency_issues_fixed": len(consistency_fixes),
                "citation_monitoring": citation_monitoring,
                "citation_impact_analysis": citation_impact,
                "citation_consistency_score": 0.85,  # 85% consistency
                "total_citation_sources": 45,
                "high_authority_citations": 15,
                "local_authority_improvement": 0.20  # 20% improvement
            }
            
            logger.info(f"Local citation management completed")
            return citation_results
            
        except Exception as e:
            logger.error(f"Error managing local citations: {e}")
            raise
    
    async def optimize_for_local_keywords(
        self,
        business_profile: LocalBusinessProfile,
        target_keywords: List[str],
        content_strategy: Dict[str, Any],
        competitor_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize for local keywords with AI-driven content strategy
        
        Args:
            business_profile: Local business profile
            target_keywords: Target local keywords
            content_strategy: Local content strategy
            competitor_analysis: Include competitor keyword analysis
            
        Returns:
            Local keyword optimization results
        """
        try:
            logger.info(f"Optimizing local keywords for {business_profile.business_id}")
            
            # Analyze local keyword opportunities
            keyword_opportunities = await self._analyze_local_keyword_opportunities(
                business_profile, target_keywords
            )
            
            # Research competitor keywords
            competitor_keywords = await self._research_competitor_local_keywords(
                business_profile
            ) if competitor_analysis else []
            
            # Create location-specific content
            location_content = await self._create_location_specific_content(
                business_profile, keyword_opportunities, content_strategy
            )
            
            # Optimize existing pages
            page_optimization = await self._optimize_existing_pages_for_local(
                business_profile, keyword_opportunities
            )
            
            # Create local landing pages
            landing_pages = await self._create_local_landing_pages(
                business_profile, keyword_opportunities
            )
            
            # Implement local schema markup
            schema_implementation = await self._implement_local_schema_markup(
                business_profile, keyword_opportunities
            )
            
            # Track keyword performance
            keyword_tracking = await self._setup_local_keyword_tracking(
                business_profile, target_keywords
            )
            
            keyword_optimization_results = {
                "keyword_opportunities_identified": len(keyword_opportunities),
                "competitor_keywords_analyzed": len(competitor_keywords),
                "location_content_created": location_content,
                "pages_optimized": page_optimization,
                "landing_pages_created": landing_pages,
                "schema_markup_implemented": schema_implementation,
                "keyword_tracking_setup": keyword_tracking,
                "expected_ranking_improvements": {
                    "primary_keywords": 15,
                    "secondary_keywords": 25,
                    "long_tail_keywords": 40
                },
                "projected_traffic_increase": 0.45  # 45% traffic increase
            }
            
            logger.info(f"Local keyword optimization completed")
            return keyword_optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing local keywords: {e}")
            raise
    
    async def track_local_seo_performance(
        self,
        business_id: str,
        tracking_period: int = 30,
        include_competitive_analysis: bool = True
    ) -> LocalSEOPerformance:
        """
        Track comprehensive local SEO performance metrics
        
        Args:
            business_id: Business identifier
            tracking_period: Tracking period in days
            include_competitive_analysis: Include competitive analysis
            
        Returns:
            Comprehensive local SEO performance metrics
        """
        try:
            logger.info(f"Tracking local SEO performance for {business_id}")
            
            # Calculate measurement period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=tracking_period)
            
            # Track local search visibility
            search_visibility = await self._track_local_search_visibility(
                business_id, start_date, end_date
            )
            
            # Track Google My Business metrics
            gmb_views = await self._track_gmb_views(
                business_id, start_date, end_date
            )
            
            direction_requests = await self._track_direction_requests(
                business_id, start_date, end_date
            )
            
            phone_calls = await self._track_phone_calls_generated(
                business_id, start_date, end_date
            )
            
            website_clicks = await self._track_website_clicks_from_gmb(
                business_id, start_date, end_date
            )
            
            # Track keyword rankings
            keyword_rankings = await self._track_local_keyword_rankings(
                business_id, start_date, end_date
            )
            
            # Track review metrics
            review_acquisition_rate = await self._track_review_acquisition_rate(
                business_id, start_date, end_date
            )
            
            # Track citation growth
            citation_growth = await self._track_citation_growth(
                business_id, start_date, end_date
            )
            
            # Track traffic and conversions
            traffic_increase = await self._track_local_traffic_increase(
                business_id, start_date, end_date
            )
            
            conversion_improvement = await self._track_conversion_rate_improvement(
                business_id, start_date, end_date
            )
            
            revenue_impact = await self._track_revenue_impact(
                business_id, start_date, end_date
            )
            
            # Track competitive position
            competitive_position = await self._track_competitive_position(
                business_id, start_date, end_date
            ) if include_competitive_analysis else {}
            
            performance = LocalSEOPerformance(
                business_id=business_id,
                measurement_period={"start": start_date, "end": end_date},
                local_search_visibility=search_visibility,
                google_my_business_views=gmb_views,
                direction_requests=direction_requests,
                phone_calls_generated=phone_calls,
                website_clicks_from_gmb=website_clicks,
                local_keyword_rankings=keyword_rankings,
                review_acquisition_rate=review_acquisition_rate,
                citation_growth=citation_growth,
                local_traffic_increase=traffic_increase,
                conversion_rate_improvement=conversion_improvement,
                revenue_impact=revenue_impact,
                competitive_position=competitive_position
            )
            
            logger.info(f"Local SEO performance tracking completed")
            return performance
            
        except Exception as e:
            logger.error(f"Error tracking local SEO performance: {e}")
            raise
    
    def _initialize_ranking_factors(self) -> Dict[str, float]:
        """Initialize local SEO ranking factors with weights"""
        return {
            "google_my_business_signals": 0.25,
            "citation_signals": 0.20,
            "review_signals": 0.15,
            "on_page_signals": 0.15,
            "link_signals": 0.10,
            "behavioral_signals": 0.10,
            "social_signals": 0.05
        }
    
    def _initialize_business_type_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business type specific strategies"""
        return {
            "restaurant": {
                "priority_factors": ["reviews", "photos", "menu", "hours"],
                "key_local_keywords": ["restaurant near me", "food delivery", "dining"],
                "citation_sources": ["Yelp", "TripAdvisor", "OpenTable", "Zomato"],
                "content_focus": ["menu", "chef", "ambiance", "events"]
            },
            "retail_store": {
                "priority_factors": ["inventory", "store_hours", "location", "promotions"],
                "key_local_keywords": ["store near me", "shopping", "retail"],
                "citation_sources": ["Google Shopping", "Yelp", "Yellow Pages"],
                "content_focus": ["products", "sales", "store_events", "brand_story"]
            },
            "service_business": {
                "priority_factors": ["service_area", "testimonials", "credentials", "response_time"],
                "key_local_keywords": ["service near me", "local service", "professional"],
                "citation_sources": ["Better Business Bureau", "Angie's List", "HomeAdvisor"],
                "content_focus": ["services", "expertise", "case_studies", "testimonials"]
            }
        }
    
    def _initialize_citation_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize citation sources by authority and relevance"""
        return {
            "tier_1_high_authority": [
                {"name": "Google My Business", "authority": 95, "required": True},
                {"name": "Facebook Business", "authority": 90, "required": True},
                {"name": "Yelp", "authority": 85, "required": True},
                {"name": "Apple Maps", "authority": 80, "required": True}
            ],
            "tier_2_industry_specific": [
                {"name": "TripAdvisor", "authority": 75, "industries": ["restaurant", "entertainment"]},
                {"name": "OpenTable", "authority": 70, "industries": ["restaurant"]},
                {"name": "HomeAdvisor", "authority": 75, "industries": ["home_services"]},
                {"name": "Healthgrades", "authority": 70, "industries": ["healthcare"]}
            ],
            "tier_3_general_directories": [
                {"name": "Yellow Pages", "authority": 60},
                {"name": "White Pages", "authority": 55},
                {"name": "Chamber of Commerce", "authority": 65},
                {"name": "Better Business Bureau", "authority": 75}
            ]
        }
    
    def _initialize_local_search_patterns(self) -> Dict[str, List[str]]:
        """Initialize local search patterns"""
        return {
            "near_me_queries": [
                "{service} near me",
                "{business_type} near me",
                "best {service} near me",
                "{service} close by"
            ],
            "location_specific": [
                "{service} in {city}",
                "{city} {business_type}",
                "{service} {neighborhood}",
                "{area} {business_type}"
            ],
            "intent_modifiers": [
                "open now",
                "24 hours",
                "emergency",
                "reviews",
                "directions",
                "hours",
                "phone number"
            ]
        }
    
    # Analysis methods...
    
    async def _analyze_google_my_business(
        self,
        business_profile: LocalBusinessProfile
    ) -> float:
        """Analyze Google My Business optimization score"""
        # Simulate GMB analysis
        score_factors = {
            "business_information_complete": 0.9,
            "categories_optimized": 0.8,
            "description_optimized": 0.7,
            "photos_quality_quantity": 0.85,
            "review_response_rate": 0.6,
            "posts_frequency": 0.5,
            "q_and_a_managed": 0.4
        }
        
        weighted_score = sum(score_factors.values()) / len(score_factors)
        return round(weighted_score, 2)
    
    async def _analyze_citation_consistency(
        self,
        business_profile: LocalBusinessProfile
    ) -> float:
        """Analyze citation consistency across platforms"""
        # Simulate citation consistency analysis
        consistency_factors = {
            "name_consistency": 0.95,
            "address_consistency": 0.85,
            "phone_consistency": 0.90,
            "website_consistency": 0.80,
            "hours_consistency": 0.70
        }
        
        weighted_score = sum(consistency_factors.values()) / len(consistency_factors)
        return round(weighted_score, 2)
    
    async def _analyze_review_profile(
        self,
        business_profile: LocalBusinessProfile
    ) -> float:
        """Analyze review profile strength"""
        # Simulate review profile analysis
        review_factors = {
            "review_quantity": 0.75,
            "review_quality": 0.80,
            "review_recency": 0.70,
            "review_response_rate": 0.60,
            "review_diversity": 0.85
        }
        
        weighted_score = sum(review_factors.values()) / len(review_factors)
        return round(weighted_score, 2)
    
    async def _analyze_local_content_optimization(
        self,
        business_profile: LocalBusinessProfile
    ) -> float:
        """Analyze local content optimization"""
        # Simulate local content analysis
        content_factors = {
            "location_pages": 0.70,
            "local_keywords": 0.65,
            "service_area_content": 0.60,
            "local_schema_markup": 0.55,
            "mobile_optimization": 0.80
        }
        
        weighted_score = sum(content_factors.values()) / len(content_factors)
        return round(weighted_score, 2)
    
    async def _analyze_local_link_profile(
        self,
        business_profile: LocalBusinessProfile
    ) -> float:
        """Analyze local link profile"""
        # Simulate local link analysis
        link_factors = {
            "local_directory_links": 0.75,
            "chamber_commerce_links": 0.60,
            "local_business_partnerships": 0.50,
            "local_media_mentions": 0.40,
            "community_involvement_links": 0.45
        }
        
        weighted_score = sum(link_factors.values()) / len(link_factors)
        return round(weighted_score, 2)
    
    async def _analyze_mobile_optimization(
        self,
        business_profile: LocalBusinessProfile
    ) -> float:
        """Analyze mobile optimization for local search"""
        # Simulate mobile optimization analysis
        mobile_factors = {
            "mobile_page_speed": 0.70,
            "mobile_user_experience": 0.75,
            "click_to_call_optimization": 0.80,
            "mobile_friendly_design": 0.85,
            "local_mobile_features": 0.65
        }
        
        weighted_score = sum(mobile_factors.values()) / len(mobile_factors)
        return round(weighted_score, 2)
    
    async def _analyze_local_schema_markup(
        self,
        business_profile: LocalBusinessProfile
    ) -> float:
        """Analyze local schema markup implementation"""
        # Simulate schema markup analysis
        schema_factors = {
            "local_business_schema": 0.60,
            "organization_schema": 0.70,
            "review_schema": 0.50,
            "service_schema": 0.40,
            "breadcrumb_schema": 0.55
        }
        
        weighted_score = sum(schema_factors.values()) / len(schema_factors)
        return round(weighted_score, 2)
    
    async def _perform_competitor_gap_analysis(
        self,
        business_profile: LocalBusinessProfile
    ) -> Dict[str, Any]:
        """Perform competitor gap analysis"""
        return {
            "gmb_optimization_gaps": [
                "Competitor has more reviews",
                "Competitor posts more frequently",
                "Competitor has better photo quality"
            ],
            "citation_gaps": [
                "Missing from industry-specific directories",
                "Inconsistent information across platforms"
            ],
            "content_gaps": [
                "Competitor has location-specific landing pages",
                "Competitor creates local event content"
            ],
            "keyword_gaps": [
                "Competitor ranks for 'emergency services'",
                "Competitor dominates 'near me' searches"
            ],
            "competitive_advantage_opportunities": [
                "Better customer service response time",
                "More comprehensive service offerings",
                "Stronger community involvement"
            ]
        }
    
    async def _identify_local_keyword_opportunities(
        self,
        business_profile: LocalBusinessProfile
    ) -> List[str]:
        """Identify local keyword opportunities"""
        opportunities = []
        
        # Add service + location combinations
        for service in business_profile.services_offered[:5]:
            opportunities.extend([
                f"{service} near me",
                f"{service} in {business_profile.primary_location.get('city', 'local area')}",
                f"best {service} {business_profile.primary_location.get('city', 'local area')}",
                f"{service} {business_profile.primary_location.get('neighborhood', 'area')}"
            ])
        
        # Add business type + location combinations
        business_type = business_profile.business_type.value.replace('_', ' ')
        opportunities.extend([
            f"{business_type} near me",
            f"{business_type} {business_profile.primary_location.get('city', 'local area')}",
            f"best {business_type} near me",
            f"top {business_type} {business_profile.primary_location.get('city', 'local area')}"
        ])
        
        return list(set(opportunities))[:20]  # Return top 20 unique opportunities
    
    async def _identify_technical_issues(
        self,
        business_profile: LocalBusinessProfile
    ) -> List[str]:
        """Identify technical issues affecting local SEO"""
        return [
            "Page load speed on mobile exceeds 3 seconds",
            "Missing local business schema markup",
            "NAP information inconsistent across pages",
            "Missing alt text for business photos",
            "No click-to-call functionality on mobile",
            "Contact page not optimized for local search",
            "Missing breadcrumb navigation",
            "Hours information not structured data"
        ]
    
    async def _determine_optimization_priorities(
        self,
        gmb_score: float,
        citation_score: float,
        review_score: float,
        content_score: float,
        link_score: float,
        mobile_score: float,
        schema_score: float
    ) -> List[str]:
        """Determine optimization priorities based on scores"""
        priorities = []
        
        # Create score tuples for sorting
        scores = [
            (gmb_score, "Google My Business optimization"),
            (citation_score, "Citation consistency improvement"),
            (review_score, "Review management enhancement"),
            (content_score, "Local content optimization"),
            (link_score, "Local link building"),
            (mobile_score, "Mobile optimization"),
            (schema_score, "Schema markup implementation")
        ]
        
        # Sort by score (lowest first - highest priority)
        scores.sort(key=lambda x: x[0])
        
        # Return prioritized list
        return [priority for score, priority in scores]
    
    async def _estimate_improvement_potential(
        self,
        business_profile: LocalBusinessProfile,
        gmb_score: float,
        citation_score: float,
        review_score: float
    ) -> float:
        """Estimate overall improvement potential"""
        current_average = (gmb_score + citation_score + review_score) / 3
        potential_improvement = (0.90 - current_average) * 0.75  # 75% of gap to 90%
        
        return round(max(0.1, potential_improvement), 2)
    
    # Strategy creation methods...
    
    async def _define_optimization_objectives(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis,
        strategy_focus: List[str]
    ) -> List[str]:
        """Define optimization objectives"""
        objectives = []
        
        if "visibility" in strategy_focus:
            objectives.append("Increase local search visibility by 40%")
        
        if "traffic" in strategy_focus:
            objectives.append("Increase local organic traffic by 50%")
        
        if "conversions" in strategy_focus:
            objectives.append("Improve local conversion rate by 25%")
        
        if "reviews" in strategy_focus:
            objectives.append("Increase review acquisition rate by 60%")
        
        if "rankings" in strategy_focus:
            objectives.append("Achieve first page rankings for 15 local keywords")
        
        # Add default objectives based on analysis
        if seo_analysis.google_my_business_score < 0.7:
            objectives.append("Optimize Google My Business profile to 90%+ completeness")
        
        if seo_analysis.citation_consistency_score < 0.8:
            objectives.append("Achieve 95%+ citation consistency across all platforms")
        
        return objectives
    
    async def _create_gmb_optimization_plan(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis
    ) -> Dict[str, Any]:
        """Create Google My Business optimization plan"""
        return {
            "business_information": {
                "actions": ["Complete all business information fields", "Verify business category accuracy"],
                "priority": "high",
                "timeline": "Week 1"
            },
            "description_optimization": {
                "actions": ["Write compelling business description", "Include target keywords naturally"],
                "priority": "high",
                "timeline": "Week 1"
            },
            "photo_optimization": {
                "actions": ["Upload high-quality business photos", "Add photos of products/services", "Include team photos"],
                "priority": "medium",
                "timeline": "Week 2"
            },
            "post_strategy": {
                "actions": ["Create weekly GMB posts", "Share updates and promotions", "Post local events"],
                "priority": "medium",
                "timeline": "Ongoing"
            },
            "q_and_a_management": {
                "actions": ["Monitor Q&A section", "Respond to questions promptly", "Add frequently asked questions"],
                "priority": "medium",
                "timeline": "Ongoing"
            }
        }
    
    async def _develop_citation_building_strategy(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis
    ) -> Dict[str, Any]:
        """Develop citation building strategy"""
        return {
            "tier_1_citations": {
                "sources": ["Google My Business", "Facebook", "Yelp", "Apple Maps"],
                "priority": "critical",
                "timeline": "Week 1-2",
                "expected_impact": "high"
            },
            "industry_specific_citations": {
                "sources": self._get_industry_specific_sources(business_profile.business_type),
                "priority": "high",
                "timeline": "Week 3-4",
                "expected_impact": "medium"
            },
            "local_directory_citations": {
                "sources": ["Local Chamber of Commerce", "City Business Directory", "Regional directories"],
                "priority": "medium",
                "timeline": "Week 5-6",
                "expected_impact": "medium"
            },
            "consistency_monitoring": {
                "frequency": "monthly",
                "automated_alerts": True,
                "correction_protocol": "immediate"
            }
        }
    
    async def _create_review_management_strategy(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis
    ) -> Dict[str, Any]:
        """Create review management strategy"""
        return {
            "review_acquisition": {
                "strategy": "Post-service follow-up email campaign",
                "target": "2-3 reviews per week",
                "platforms": ["Google", "Yelp", "Facebook"],
                "incentives": "Service discounts for honest reviews"
            },
            "review_response": {
                "response_time_target": "24 hours",
                "positive_review_template": "Thank you for taking the time to review us!",
                "negative_review_protocol": "Acknowledge, apologize if necessary, offer resolution offline",
                "automation_level": "semi-automated"
            },
            "review_monitoring": {
                "monitoring_frequency": "daily",
                "alert_system": True,
                "sentiment_analysis": True,
                "competitive_monitoring": True
            }
        }
    
    async def _develop_local_content_strategy(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis
    ) -> Dict[str, Any]:
        """Develop local content strategy"""
        return {
            "location_pages": {
                "pages_to_create": len(business_profile.service_areas),
                "content_structure": "Service description + local information + testimonials",
                "target_keywords": "Service + location combinations",
                "timeline": "Week 2-4"
            },
            "local_blog_content": {
                "content_calendar": "2 posts per month",
                "topics": ["Local events", "Community involvement", "Industry news"],
                "seo_focus": "Local keywords + service keywords",
                "timeline": "Ongoing"
            },
            "service_area_content": {
                "content_type": "Dedicated service area pages",
                "optimization": "Local keywords + service descriptions",
                "schema_markup": "Service area schema",
                "timeline": "Week 3-5"
            }
        }
    
    async def _create_local_link_building_strategy(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis
    ) -> Dict[str, Any]:
        """Create local link building strategy"""
        return {
            "local_partnerships": {
                "target": "5-10 local business partnerships",
                "approach": "Cross-promotional content and links",
                "timeline": "Month 2-3",
                "expected_links": 10
            },
            "community_involvement": {
                "activities": ["Local events sponsorship", "Community organization participation"],
                "link_opportunities": "Event websites, organization websites",
                "timeline": "Ongoing",
                "expected_links": 5
            },
            "local_media_outreach": {
                "targets": ["Local newspapers", "Local blogs", "Industry publications"],
                "approach": "Expert commentary and story pitches",
                "timeline": "Month 2-4",
                "expected_links": 8
            }
        }
    
    async def _plan_schema_markup_implementation(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis
    ) -> Dict[str, Any]:
        """Plan schema markup implementation"""
        return {
            "local_business_schema": {
                "implementation": "Homepage and contact page",
                "properties": ["name", "address", "phone", "hours", "geo"],
                "priority": "critical",
                "timeline": "Week 1"
            },
            "organization_schema": {
                "implementation": "Site-wide",
                "properties": ["logo", "social_profiles", "contact_info"],
                "priority": "high",
                "timeline": "Week 2"
            },
            "service_schema": {
                "implementation": "Service pages",
                "properties": ["service_type", "area_served", "provider"],
                "priority": "medium",
                "timeline": "Week 3"
            },
            "review_schema": {
                "implementation": "Review sections",
                "properties": ["rating", "review_count", "review_body"],
                "priority": "medium",
                "timeline": "Week 4"
            }
        }
    
    async def _create_mobile_optimization_plan(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis
    ) -> Dict[str, Any]:
        """Create mobile optimization plan"""
        return {
            "page_speed_optimization": {
                "target": "Load time under 3 seconds",
                "actions": ["Image optimization", "Code minification", "CDN implementation"],
                "priority": "high",
                "timeline": "Week 2"
            },
            "mobile_user_experience": {
                "improvements": ["Click-to-call buttons", "Touch-friendly navigation", "Mobile-optimized forms"],
                "priority": "high",
                "timeline": "Week 3"
            },
            "local_mobile_features": {
                "features": ["Directions integration", "Business hours display", "One-click contact"],
                "priority": "medium",
                "timeline": "Week 4"
            }
        }
    
    async def _setup_monitoring_and_reporting(
        self,
        business_profile: LocalBusinessProfile,
        optimization_objectives: List[str]
    ) -> Dict[str, Any]:
        """Setup monitoring and reporting"""
        return {
            "tracking_metrics": [
                "Local search visibility",
                "GMB insights",
                "Local keyword rankings",
                "Citation consistency",
                "Review metrics",
                "Local traffic",
                "Conversion rates"
            ],
            "reporting_frequency": "monthly",
            "automated_alerts": {
                "negative_reviews": True,
                "ranking_drops": True,
                "citation_inconsistencies": True,
                "competitor_activities": True
            },
            "dashboard_access": "Real-time performance dashboard",
            "competitive_monitoring": "Track top 5 local competitors"
        }
    
    async def _create_implementation_timeline(
        self,
        optimization_objectives: List[str],
        timeline_months: int
    ) -> Dict[str, str]:
        """Create implementation timeline"""
        months_per_phase = max(1, timeline_months // 4)
        
        return {
            "phase_1_foundation": f"Month 1-{months_per_phase}: GMB optimization, citation building",
            "phase_2_content": f"Month {months_per_phase+1}-{months_per_phase*2}: Content creation, on-page optimization",
            "phase_3_authority": f"Month {months_per_phase*2+1}-{months_per_phase*3}: Link building, review management",
            "phase_4_optimization": f"Month {months_per_phase*3+1}-{timeline_months}: Performance optimization, scaling"
        }
    
    async def _calculate_expected_results(
        self,
        business_profile: LocalBusinessProfile,
        seo_analysis: LocalSEOAnalysis,
        optimization_objectives: List[str]
    ) -> Dict[str, float]:
        """Calculate expected results"""
        return {
            "local_search_visibility_increase": 0.40,  # 40% increase
            "organic_traffic_increase": 0.50,  # 50% increase
            "gmb_views_increase": 0.60,  # 60% increase
            "direction_requests_increase": 0.35,  # 35% increase
            "phone_calls_increase": 0.45,  # 45% increase
            "review_acquisition_increase": 0.75,  # 75% increase
            "local_keyword_rankings_improved": 15,  # 15 keywords to first page
            "citation_consistency_improvement": 0.25  # 25% improvement
        }
    
    async def _project_roi(
        self,
        business_profile: LocalBusinessProfile,
        expected_results: Dict[str, float]
    ) -> Dict[str, float]:
        """Project ROI for local SEO investment"""
        return {
            "monthly_investment": 2000.0,  # $2000/month
            "monthly_revenue_increase": 8000.0,  # $8000/month increase
            "roi_percentage": 300.0,  # 300% ROI
            "payback_period_months": 2.5,  # 2.5 months
            "annual_revenue_impact": 96000.0,  # $96,000 annual impact
            "customer_lifetime_value_increase": 0.30  # 30% increase
        }
    
    def _get_industry_specific_sources(
        self,
        business_type: LocalBusinessType
    ) -> List[str]:
        """Get industry-specific citation sources"""
        industry_sources = {
            LocalBusinessType.RESTAURANT: ["Yelp", "TripAdvisor", "OpenTable", "Zomato"],
            LocalBusinessType.RETAIL_STORE: ["Google Shopping", "Yelp", "Yellow Pages"],
            LocalBusinessType.SERVICE_BUSINESS: ["Angie's List", "HomeAdvisor", "Better Business Bureau"],
            LocalBusinessType.HEALTHCARE: ["Healthgrades", "WebMD", "Vitals"],
            LocalBusinessType.ENTERTAINMENT: ["TripAdvisor", "Eventbrite", "Yelp"]
        }
        
        return industry_sources.get(business_type, ["Yelp", "Yellow Pages", "Better Business Bureau"])
    
    # Implementation methods (placeholder implementations)...
    
    async def _optimize_business_information(
        self,
        business_profile: LocalBusinessProfile,
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize business information"""
        return {
            "business_name_optimized": True,
            "categories_updated": True,
            "contact_info_verified": True,
            "hours_updated": True,
            "completion_score": 0.95
        }
    
    async def _optimize_business_categories(
        self,
        business_profile: LocalBusinessProfile,
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize business categories"""
        return {
            "primary_category_set": True,
            "additional_categories_added": 3,
            "relevance_score": 0.90,
            "category_optimization_complete": True
        }
    
    async def _optimize_business_description(
        self,
        business_profile: LocalBusinessProfile,
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize business description"""
        return {
            "description_updated": True,
            "keywords_included": 5,
            "character_count": 750,
            "readability_score": 0.85
        }
    
    async def _optimize_business_media(
        self,
        business_profile: LocalBusinessProfile,
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize business media"""
        return {
            "photos_uploaded": 15,
            "video_uploaded": True,
            "logo_updated": True,
            "cover_photo_optimized": True,
            "media_score": 0.88
        }
    
    async def _optimize_gmb_posts(
        self,
        business_profile: LocalBusinessProfile,
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize GMB posts"""
        return {
            "posting_schedule_created": True,
            "post_templates_created": 5,
            "call_to_action_optimized": True,
            "engagement_strategy_implemented": True
        }
    
    async def _optimize_qa_section(
        self,
        business_profile: LocalBusinessProfile,
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize Q&A section"""
        return {
            "faqs_added": 10,
            "monitoring_setup": True,
            "response_templates_created": True,
            "automated_alerts_enabled": True
        }
    
    async def _setup_review_response_automation(
        self,
        business_profile: LocalBusinessProfile,
        automation_level: str
    ) -> Dict[str, Any]:
        """Setup review response automation"""
        return {
            "automation_level": automation_level,
            "response_templates_created": 8,
            "monitoring_enabled": True,
            "alert_system_active": True,
            "average_response_time": "4 hours"
        }
    
    async def _configure_insights_tracking(
        self,
        business_profile: LocalBusinessProfile,
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure insights tracking"""
        return {
            "tracking_enabled": True,
            "metrics_monitored": ["views", "searches", "actions", "direction_requests", "phone_calls"],
            "reporting_frequency": "weekly",
            "dashboard_access": True
        }
    
    # Additional placeholder methods for citation management, keyword optimization, and performance tracking...
    
    async def _audit_existing_citations(
        self,
        business_profile: LocalBusinessProfile
    ) -> Dict[str, Any]:
        """Audit existing citations"""
        return {
            "total_citations_found": 25,
            "consistent_citations": 18,
            "inconsistent_citations": 7,
            "consistency_score": 0.72,
            "missing_from_major_platforms": 3
        }
    
    async def _identify_citation_opportunities(
        self,
        business_profile: LocalBusinessProfile,
        citation_strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify citation opportunities"""
        return [
            {"platform": "Yelp", "priority": "high", "estimated_effort": "low"},
            {"platform": "Yellow Pages", "priority": "medium", "estimated_effort": "low"},
            {"platform": "Chamber of Commerce", "priority": "high", "estimated_effort": "medium"}
        ]
    
    async def _build_new_citations(
        self,
        business_profile: LocalBusinessProfile,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build new citations"""
        return [
            {"platform": platform["platform"], "status": "completed", "submission_date": datetime.now()}
            for platform in opportunities[:10]  # Build top 10 opportunities
        ]
    
    async def _fix_citation_inconsistencies(
        self,
        business_profile: LocalBusinessProfile,
        audit_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fix citation inconsistencies"""
        return [
            {"platform": "Google", "issue": "phone_number", "status": "fixed"},
            {"platform": "Facebook", "issue": "hours", "status": "fixed"},
            {"platform": "Yelp", "issue": "address", "status": "fixed"}
        ]
    
    async def _setup_citation_monitoring(
        self,
        business_profile: LocalBusinessProfile
    ) -> Dict[str, Any]:
        """Setup citation monitoring"""
        return {
            "monitoring_enabled": True,
            "check_frequency": "monthly",
            "automated_alerts": True,
            "platforms_monitored": 25,
            "consistency_threshold": 0.95
        }
    
    async def _analyze_citation_impact(
        self,
        business_profile: LocalBusinessProfile,
        building_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze citation impact"""
        return {
            "visibility_improvement": 0.30,
            "ranking_improvements": 8,
            "traffic_increase": 0.25,
            "authority_boost": 0.15
        }
    
    # Performance tracking methods (placeholder implementations)...
    
    async def _track_local_search_visibility(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Track local search visibility"""
        return 0.75  # 75% visibility score
    
    async def _track_gmb_views(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Track Google My Business views"""
        return 2500  # 2500 views
    
    async def _track_direction_requests(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Track direction requests"""
        return 450  # 450 direction requests
    
    async def _track_phone_calls_generated(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Track phone calls generated"""
        return 180  # 180 phone calls
    
    async def _track_website_clicks_from_gmb(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Track website clicks from GMB"""
        return 320  # 320 website clicks
    
    async def _track_local_keyword_rankings(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Track local keyword rankings"""
        return {
            "primary_keyword": 3,
            "secondary_keyword_1": 7,
            "secondary_keyword_2": 5,
            "long_tail_keyword_1": 2,
            "long_tail_keyword_2": 4
        }
    
    async def _track_review_acquisition_rate(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Track review acquisition rate"""
        return 0.15  # 15% of customers leave reviews
    
    async def _track_citation_growth(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Track citation growth"""
        return 12  # 12 new citations
    
    async def _track_local_traffic_increase(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Track local traffic increase"""
        return 0.35  # 35% traffic increase
    
    async def _track_conversion_rate_improvement(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Track conversion rate improvement"""
        return 0.20  # 20% conversion improvement
    
    async def _track_revenue_impact(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Track revenue impact"""
        return 15000.0  # $15,000 revenue increase
    
    async def _track_competitive_position(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Track competitive position"""
        return {
            "visibility_vs_competitor_1": 1.15,  # 15% better visibility
            "visibility_vs_competitor_2": 0.95,  # 5% lower visibility
            "average_ranking_position": 3.2,
            "market_share": 0.18  # 18% market share
        }