"""
Competitor SEO Monitor - SEO Optimization Module
===============================================

Advanced competitor SEO monitoring system for tracking and analyzing
competitor search performance, strategies, and opportunities.

Features:
- Real-time competitor ranking tracking
- Content gap analysis
- Backlink profile monitoring
- SEO strategy analysis
- Competitive intelligence alerts
- Market share tracking

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class CompetitorTier(Enum):
    """Competitor tier classification"""
    DIRECT = "direct"           # Direct competitors
    INDIRECT = "indirect"       # Indirect competitors  
    ASPIRATIONAL = "aspirational"  # Leaders to aspire to
    EMERGING = "emerging"       # New/growing competitors

class MonitoringFrequency(Enum):
    """Monitoring frequency options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class CompetitiveAdvantage(Enum):
    """Types of competitive advantages"""
    CONTENT_QUALITY = "content_quality"
    BACKLINK_PROFILE = "backlink_profile"
    TECHNICAL_SEO = "technical_seo"
    KEYWORD_COVERAGE = "keyword_coverage"
    USER_EXPERIENCE = "user_experience"
    BRAND_AUTHORITY = "brand_authority"

@dataclass
class CompetitorProfile:
    """Comprehensive competitor profile"""
    competitor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    domain: str = ""
    tier: CompetitorTier = CompetitorTier.DIRECT
    
    # Business information
    industry: str = ""
    target_audience: str = ""
    business_model: str = ""
    estimated_size: str = ""  # startup, small, medium, large, enterprise
    
    # SEO metrics
    domain_authority: float = 0.0
    organic_traffic: int = 0
    organic_keywords: int = 0
    backlink_count: int = 0
    referring_domains: int = 0
    
    # Content metrics
    content_pages: int = 0
    blog_posts_per_month: int = 0
    video_content_count: int = 0
    social_media_presence: Dict[str, str] = field(default_factory=dict)
    
    # Tracking configuration
    monitoring_frequency: MonitoringFrequency = MonitoringFrequency.WEEKLY
    priority_keywords: List[str] = field(default_factory=list)
    
    # Metadata
    added_at: datetime = field(default_factory=datetime.now)
    last_analyzed: Optional[datetime] = None

@dataclass
class CompetitorRanking:
    """Competitor ranking data"""
    competitor_id: str = ""
    keyword: str = ""
    search_engine: str = "google"
    
    # Ranking metrics
    current_position: int = 0
    previous_position: int = 0
    position_change: int = 0
    best_position: int = 0
    worst_position: int = 0
    
    # Traffic metrics
    estimated_traffic: int = 0
    click_through_rate: float = 0.0
    search_volume: int = 0
    
    # Content analysis
    ranking_url: str = ""
    page_title: str = ""
    meta_description: str = ""
    content_length: int = 0
    content_score: float = 0.0
    
    # Metadata
    tracked_at: datetime = field(default_factory=datetime.now)

@dataclass
class ContentGap:
    """Identified content gap opportunity"""
    gap_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    keyword: str = ""
    topic: str = ""
    
    # Gap analysis
    competitor_coverage: Dict[str, bool] = field(default_factory=dict)  # competitor_id -> has_content
    our_coverage: bool = False
    gap_severity: str = "medium"  # low, medium, high, critical
    
    # Opportunity metrics
    search_volume: int = 0
    keyword_difficulty: float = 0.0
    estimated_traffic_potential: int = 0
    business_value_score: float = 0.0
    
    # Competitive analysis
    top_competitor_url: str = ""
    top_competitor_score: float = 0.0
    average_content_length: int = 0
    average_backlinks: int = 0
    
    # Recommendations
    content_type_recommended: str = ""  # blog_post, video, infographic, etc.
    target_content_length: int = 0
    recommended_approach: str = ""
    required_expertise_level: str = "medium"  # low, medium, high, expert
    
    # Metadata
    identified_at: datetime = field(default_factory=datetime.now)

@dataclass
class CompetitiveAlert:
    """Competitive intelligence alert"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    competitor_id: str = ""
    alert_type: str = ""  # ranking_change, new_content, backlink_gain, etc.
    severity: str = "medium"  # low, medium, high, critical
    
    # Alert details
    title: str = ""
    description: str = ""
    impact_assessment: str = ""
    
    # Data
    affected_keywords: List[str] = field(default_factory=list)
    metrics_change: Dict[str, float] = field(default_factory=dict)
    
    # Response
    recommended_actions: List[str] = field(default_factory=list)
    urgency_level: str = "normal"  # low, normal, high, urgent
    
    # Metadata
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

class CompetitorSEOMonitor:
    """Main competitor SEO monitoring system"""
    
    def __init__(self):
        self.competitors: Dict[str, CompetitorProfile] = {}
        self.competitor_rankings: Dict[str, List[CompetitorRanking]] = defaultdict(list)
        self.content_gaps: List[ContentGap] = []
        self.competitive_alerts: List[CompetitiveAlert] = []
        
        # Configuration
        self.monitoring_active = False
        self.analysis_keywords = self._initialize_analysis_keywords()
        self.monitoring_schedule = self._initialize_monitoring_schedule()
        
        # Initialize with default competitors
        self._initialize_default_competitors()
        
    def _initialize_analysis_keywords(self) -> List[str]:
        """Initialize keywords for competitive analysis"""
        return [
            "content creation", "music production", "video editing",
            "social media marketing", "influencer marketing", "creator economy",
            "youtube optimization", "tiktok growth", "instagram engagement",
            "content strategy", "viral content", "audience building"
        ]
        
    def _initialize_monitoring_schedule(self) -> Dict[str, Any]:
        """Initialize monitoring schedule configuration"""
        return {
            "ranking_check_frequency": 24,  # hours
            "content_analysis_frequency": 168,  # hours (weekly)
            "backlink_check_frequency": 168,  # hours (weekly)
            "alert_check_frequency": 1,  # hours
            "full_analysis_frequency": 720  # hours (monthly)
        }
        
    def _initialize_default_competitors(self):
        """Initialize with default competitor profiles"""
        default_competitors = [
            {
                "name": "CreatorHub",
                "domain": "creatorhub.io",
                "tier": CompetitorTier.DIRECT,
                "industry": "content_creation",
                "target_audience": "content_creators",
                "business_model": "saas",
                "estimated_size": "medium"
            },
            {
                "name": "VideoMaster",
                "domain": "videomaster.com",
                "tier": CompetitorTier.DIRECT,
                "industry": "video_tools",
                "target_audience": "video_creators",
                "business_model": "freemium",
                "estimated_size": "large"
            },
            {
                "name": "SocialGrowth",
                "domain": "socialgrowth.co",
                "tier": CompetitorTier.INDIRECT,
                "industry": "social_media",
                "target_audience": "marketers",
                "business_model": "subscription",
                "estimated_size": "small"
            },
            {
                "name": "CreatorStudio",
                "domain": "creatorstudio.app",
                "tier": CompetitorTier.ASPIRATIONAL,
                "industry": "creator_tools",
                "target_audience": "professional_creators",
                "business_model": "enterprise",
                "estimated_size": "enterprise"
            }
        ]
        
        for comp_data in default_competitors:
            competitor = CompetitorProfile(
                name=comp_data["name"],
                domain=comp_data["domain"],
                tier=comp_data["tier"],
                industry=comp_data["industry"],
                target_audience=comp_data["target_audience"],
                business_model=comp_data["business_model"],
                estimated_size=comp_data["estimated_size"],
                priority_keywords=self.analysis_keywords[:5]  # Top 5 keywords
            )
            
            # Simulate initial SEO metrics
            competitor.domain_authority = self._estimate_domain_authority(comp_data["estimated_size"])
            competitor.organic_traffic = self._estimate_organic_traffic(comp_data["estimated_size"])
            competitor.organic_keywords = self._estimate_keyword_count(comp_data["estimated_size"])
            competitor.backlink_count = self._estimate_backlinks(comp_data["estimated_size"])
            
            self.competitors[competitor.competitor_id] = competitor
            
    def _estimate_domain_authority(self, size: str) -> float:
        """Estimate domain authority based on company size"""
        size_da_map = {
            "startup": 25.0,
            "small": 35.0,
            "medium": 50.0,
            "large": 70.0,
            "enterprise": 85.0
        }
        import random
        base_da = size_da_map.get(size, 40.0)
        return base_da + random.uniform(-5, 10)
        
    def _estimate_organic_traffic(self, size: str) -> int:
        """Estimate organic traffic based on company size"""
        size_traffic_map = {
            "startup": 5000,
            "small": 25000,
            "medium": 100000,
            "large": 500000,
            "enterprise": 2000000
        }
        import random
        base_traffic = size_traffic_map.get(size, 50000)
        return int(base_traffic * random.uniform(0.7, 1.5))
        
    def _estimate_keyword_count(self, size: str) -> int:
        """Estimate keyword count based on company size"""
        size_keywords_map = {
            "startup": 500,
            "small": 2000,
            "medium": 8000,
            "large": 25000,
            "enterprise": 100000
        }
        import random
        base_keywords = size_keywords_map.get(size, 5000)
        return int(base_keywords * random.uniform(0.8, 1.3))
        
    def _estimate_backlinks(self, size: str) -> int:
        """Estimate backlink count based on company size"""
        size_backlinks_map = {
            "startup": 1000,
            "small": 5000,
            "medium": 25000,
            "large": 100000,
            "enterprise": 500000
        }
        import random
        base_backlinks = size_backlinks_map.get(size, 10000)
        return int(base_backlinks * random.uniform(0.6, 1.8))
        
    async def start_monitoring(self):
        """Start competitive SEO monitoring"""
        self.monitoring_active = True
        
        monitoring_tasks = [
            self._monitor_competitor_rankings(),
            self._analyze_content_gaps(),
            self._detect_competitive_changes(),
            self._generate_competitive_alerts(),
            self._update_competitor_profiles()
        ]
        
        await asyncio.gather(*monitoring_tasks)
        
    async def stop_monitoring(self):
        """Stop competitive SEO monitoring"""
        self.monitoring_active = False
        logger.info("Competitor SEO monitoring stopped")
        
    async def _monitor_competitor_rankings(self):
        """Monitor competitor rankings for target keywords"""
        while self.monitoring_active:
            try:
                for competitor_id, competitor in self.competitors.items():
                    for keyword in competitor.priority_keywords:
                        ranking = await self._check_competitor_ranking(competitor_id, keyword)
                        if ranking:
                            self.competitor_rankings[competitor_id].append(ranking)
                            
                            # Keep only last 100 rankings per competitor
                            if len(self.competitor_rankings[competitor_id]) > 100:
                                self.competitor_rankings[competitor_id].pop(0)
                                
                            await self._analyze_ranking_change(ranking)
                            
                await asyncio.sleep(self.monitoring_schedule["ranking_check_frequency"] * 3600)
                
            except Exception as e:
                logger.error(f"Error monitoring competitor rankings: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
                
    async def _check_competitor_ranking(self, competitor_id: str, keyword: str) -> Optional[CompetitorRanking]:
        """Check competitor ranking for specific keyword (simulated)"""
        import random
        
        competitor = self.competitors.get(competitor_id)
        if not competitor:
            return None
            
        # Simulate ranking based on competitor strength
        da_factor = competitor.domain_authority / 100
        size_factor = {
            "startup": 0.3,
            "small": 0.5,
            "medium": 0.7,
            "large": 0.9,
            "enterprise": 1.0
        }.get(competitor.estimated_size, 0.6)
        
        # Calculate probable ranking position
        ranking_factor = (da_factor + size_factor) / 2
        base_position = int(50 - (ranking_factor * 40))  # Better competitors rank higher
        current_position = max(1, base_position + random.randint(-10, 15))
        
        # Get previous ranking for comparison
        previous_rankings = [
            r for r in self.competitor_rankings[competitor_id] 
            if r.keyword == keyword
        ]
        previous_position = previous_rankings[-1].current_position if previous_rankings else current_position + random.randint(-5, 5)
        
        # Simulate other metrics
        search_volume = random.randint(1000, 50000)
        ctr = max(0.01, 0.3 / current_position)  # Higher positions get better CTR
        estimated_traffic = int(search_volume * ctr)
        
        return CompetitorRanking(
            competitor_id=competitor_id,
            keyword=keyword,
            search_engine="google",
            current_position=current_position,
            previous_position=previous_position,
            position_change=previous_position - current_position,
            best_position=min(current_position, previous_position),
            worst_position=max(current_position, previous_position),
            estimated_traffic=estimated_traffic,
            click_through_rate=ctr,
            search_volume=search_volume,
            ranking_url=f"https://{competitor.domain}/content/{keyword.replace(' ', '-')}",
            page_title=f"{keyword.title()} - {competitor.name}",
            content_length=random.randint(800, 3000),
            content_score=random.uniform(0.6, 0.95)
        )
        
    async def _analyze_ranking_change(self, ranking: CompetitorRanking):
        """Analyze significant ranking changes"""
        
        if abs(ranking.position_change) >= 5:  # Significant change threshold
            competitor = self.competitors[ranking.competitor_id]
            
            if ranking.position_change > 0:  # Improvement (position number decreased)
                alert_type = "ranking_improvement"
                severity = "medium" if ranking.position_change >= 10 else "low"
                description = f"{competitor.name} improved {ranking.position_change} positions for '{ranking.keyword}'"
            else:  # Decline (position number increased)
                alert_type = "ranking_decline"
                severity = "low"  # Competitor decline is good for us
                description = f"{competitor.name} dropped {abs(ranking.position_change)} positions for '{ranking.keyword}'"
                
            await self._create_competitive_alert(
                competitor_id=ranking.competitor_id,
                alert_type=alert_type,
                severity=severity,
                title=f"Ranking Change: {competitor.name}",
                description=description,
                affected_keywords=[ranking.keyword],
                metrics_change={"position_change": ranking.position_change}
            )
            
    async def _analyze_content_gaps(self):
        """Analyze content gaps compared to competitors"""
        while self.monitoring_active:
            try:
                gaps = await self._identify_content_gaps()
                
                # Add new gaps to the list
                for gap in gaps:
                    # Check if gap already exists
                    existing_gap = next(
                        (g for g in self.content_gaps 
                         if g.keyword == gap.keyword and g.topic == gap.topic), 
                        None
                    )
                    
                    if not existing_gap:
                        self.content_gaps.append(gap)
                        
                        # Create alert for high-value gaps
                        if gap.gap_severity in ["high", "critical"]:
                            await self._create_gap_alert(gap)
                            
                # Remove old gaps (older than 90 days)
                cutoff_date = datetime.now() - timedelta(days=90)
                self.content_gaps = [
                    gap for gap in self.content_gaps 
                    if gap.identified_at > cutoff_date
                ]
                
                await asyncio.sleep(self.monitoring_schedule["content_analysis_frequency"] * 3600)
                
            except Exception as e:
                logger.error(f"Error analyzing content gaps: {e}")
                await asyncio.sleep(3600)
                
    async def _identify_content_gaps(self) -> List[ContentGap]:
        """Identify content gaps based on competitor analysis"""
        gaps = []
        
        # Analyze each keyword for content coverage
        for keyword in self.analysis_keywords:
            # Check which competitors have content for this keyword
            competitor_coverage = {}
            
            for competitor_id, competitor in self.competitors.items():
                # Simulate content analysis
                has_content = await self._check_competitor_content(competitor, keyword)
                competitor_coverage[competitor_id] = has_content
                
            # Check our content coverage (simulated)
            our_coverage = await self._check_our_content_coverage(keyword)
            
            # Identify gaps
            competitors_with_content = sum(1 for has_content in competitor_coverage.values() if has_content)
            total_competitors = len(competitor_coverage)
            
            if competitors_with_content >= total_competitors * 0.6 and not our_coverage:
                # Significant gap - most competitors have content but we don't
                gap_severity = "high" if competitors_with_content >= total_competitors * 0.8 else "medium"
                
                # Get top competitor for reference
                top_competitor = await self._get_top_competitor_for_keyword(keyword)
                
                gap = ContentGap(
                    keyword=keyword,
                    topic=keyword.replace(' ', '_'),
                    competitor_coverage=competitor_coverage,
                    our_coverage=our_coverage,
                    gap_severity=gap_severity,
                    search_volume=await self._get_search_volume(keyword),
                    keyword_difficulty=await self._get_keyword_difficulty(keyword),
                    estimated_traffic_potential=await self._estimate_traffic_potential(keyword),
                    business_value_score=await self._calculate_business_value(keyword),
                    top_competitor_url=top_competitor.get("url", "") if top_competitor else "",
                    top_competitor_score=top_competitor.get("score", 0) if top_competitor else 0,
                    average_content_length=await self._get_average_content_length(keyword),
                    content_type_recommended=await self._recommend_content_type(keyword),
                    target_content_length=await self._recommend_content_length(keyword),
                    recommended_approach=await self._recommend_approach(keyword),
                    required_expertise_level="medium"
                )
                
                gaps.append(gap)
                
        return gaps
        
    async def _check_competitor_content(self, competitor: CompetitorProfile, keyword: str) -> bool:
        """Check if competitor has content for keyword (simulated)"""
        import random
        
        # Simulate based on competitor strength and keyword relevance
        strength_factor = competitor.domain_authority / 100
        
        # Some keywords are more likely to have content
        keyword_coverage_probability = {
            "content creation": 0.9,
            "music production": 0.7,
            "video editing": 0.8,
            "social media marketing": 0.85,
            "youtube optimization": 0.6
        }
        
        base_probability = keyword_coverage_probability.get(keyword, 0.5)
        final_probability = base_probability * (0.5 + strength_factor * 0.5)
        
        return random.random() < final_probability
        
    async def _check_our_content_coverage(self, keyword: str) -> bool:
        """Check our content coverage for keyword (simulated)"""
        import random
        
        # Simulate our content coverage (assuming we have limited coverage)
        coverage_rates = {
            "content creation": 0.8,
            "music production": 0.9,
            "video editing": 0.6,
            "social media marketing": 0.4,
            "youtube optimization": 0.7
        }
        
        return random.random() < coverage_rates.get(keyword, 0.3)
        
    async def _get_top_competitor_for_keyword(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Get top-performing competitor for keyword"""
        
        competitor_scores = []
        
        for competitor_id, competitor in self.competitors.items():
            # Get recent rankings for this competitor and keyword
            recent_rankings = [
                r for r in self.competitor_rankings[competitor_id]
                if r.keyword == keyword and r.tracked_at > datetime.now() - timedelta(days=30)
            ]
            
            if recent_rankings:
                avg_position = statistics.mean([r.current_position for r in recent_rankings])
                score = 100 - avg_position  # Lower position = higher score
                
                competitor_scores.append({
                    "competitor_id": competitor_id,
                    "competitor": competitor,
                    "score": score,
                    "avg_position": avg_position,
                    "url": f"https://{competitor.domain}/content/{keyword.replace(' ', '-')}"
                })
                
        if competitor_scores:
            top_competitor = max(competitor_scores, key=lambda x: x["score"])
            return {
                "competitor_id": top_competitor["competitor_id"],
                "name": top_competitor["competitor"].name,
                "score": top_competitor["score"],
                "position": top_competitor["avg_position"],
                "url": top_competitor["url"]
            }
            
        return None
        
    async def _get_search_volume(self, keyword: str) -> int:
        """Get search volume for keyword (simulated)"""
        import random
        
        # Simulate search volumes
        volume_ranges = {
            "content creation": (20000, 50000),
            "music production": (15000, 35000),
            "video editing": (25000, 60000),
            "social media marketing": (40000, 100000),
            "youtube optimization": (5000, 15000)
        }
        
        min_vol, max_vol = volume_ranges.get(keyword, (1000, 10000))
        return random.randint(min_vol, max_vol)
        
    async def _get_keyword_difficulty(self, keyword: str) -> float:
        """Get keyword difficulty score (simulated)"""
        import random
        
        # Simulate difficulty based on keyword competitiveness
        difficulty_map = {
            "content creation": 75.0,
            "music production": 65.0,
            "video editing": 70.0,
            "social media marketing": 85.0,
            "youtube optimization": 60.0
        }
        
        base_difficulty = difficulty_map.get(keyword, 50.0)
        return base_difficulty + random.uniform(-10, 10)
        
    async def _estimate_traffic_potential(self, keyword: str) -> int:
        """Estimate traffic potential for keyword"""
        search_volume = await self._get_search_volume(keyword)
        keyword_difficulty = await self._get_keyword_difficulty(keyword)
        
        # Assume we can achieve position 15-25 initially
        estimated_position = 20
        ctr = max(0.01, 0.1 / estimated_position)
        
        # Adjust for difficulty
        difficulty_factor = 1.0 - (keyword_difficulty / 100 * 0.5)
        
        return int(search_volume * ctr * difficulty_factor)
        
    async def _calculate_business_value(self, keyword: str) -> float:
        """Calculate business value score for keyword"""
        
        # Business value factors
        relevance_scores = {
            "content creation": 0.95,
            "music production": 0.90,
            "video editing": 0.85,
            "social media marketing": 0.80,
            "youtube optimization": 0.88
        }
        
        commercial_intent = {
            "content creation": 0.7,
            "music production": 0.8,
            "video editing": 0.9,
            "social media marketing": 0.6,
            "youtube optimization": 0.7
        }
        
        relevance = relevance_scores.get(keyword, 0.5)
        intent = commercial_intent.get(keyword, 0.5)
        
        return (relevance * 0.6 + intent * 0.4)
        
    async def _get_average_content_length(self, keyword: str) -> int:
        """Get average content length for keyword in competitor content"""
        import random
        
        # Simulate based on keyword type
        length_ranges = {
            "content creation": (2000, 4000),
            "music production": (1500, 3500),
            "video editing": (2500, 5000),
            "social media marketing": (1800, 3000),
            "youtube optimization": (2200, 4500)
        }
        
        min_len, max_len = length_ranges.get(keyword, (1000, 2500))
        return random.randint(min_len, max_len)
        
    async def _recommend_content_type(self, keyword: str) -> str:
        """Recommend content type for keyword"""
        
        content_type_map = {
            "content creation": "comprehensive_guide",
            "music production": "tutorial_series",
            "video editing": "step_by_step_tutorial",
            "social media marketing": "strategy_guide",
            "youtube optimization": "best_practices_guide"
        }
        
        return content_type_map.get(keyword, "blog_post")
        
    async def _recommend_content_length(self, keyword: str) -> int:
        """Recommend content length for keyword"""
        avg_length = await self._get_average_content_length(keyword)
        
        # Recommend 20% longer than average competitor content
        return int(avg_length * 1.2)
        
    async def _recommend_approach(self, keyword: str) -> str:
        """Recommend approach for creating content"""
        
        approaches = {
            "content creation": "Create comprehensive resource with actionable tips",
            "music production": "Step-by-step tutorial with audio examples",
            "video editing": "Visual tutorial with before/after examples",
            "social media marketing": "Data-driven strategy guide with case studies",
            "youtube optimization": "Technical guide with real examples"
        }
        
        return approaches.get(keyword, "Create high-quality, comprehensive content")
        
    async def _create_gap_alert(self, gap: ContentGap):
        """Create alert for significant content gap"""
        
        severity = "high" if gap.gap_severity == "critical" else "medium"
        
        description = (
            f"Content gap identified for '{gap.keyword}'. "
            f"Multiple competitors have coverage but we don't. "
            f"Estimated traffic potential: {gap.estimated_traffic_potential}"
        )
        
        actions = [
            f"Create {gap.content_type_recommended} for '{gap.keyword}'",
            f"Target content length: {gap.target_content_length} words",
            f"Focus on: {gap.recommended_approach}",
            "Analyze top competitor content for insights"
        ]
        
        await self._create_competitive_alert(
            competitor_id="",  # Not specific to one competitor
            alert_type="content_gap",
            severity=severity,
            title=f"Content Gap: {gap.keyword}",
            description=description,
            affected_keywords=[gap.keyword],
            recommended_actions=actions
        )
        
    async def _create_competitive_alert(self,
                                      competitor_id: str,
                                      alert_type: str,
                                      severity: str,
                                      title: str,
                                      description: str,
                                      affected_keywords: List[str],
                                      metrics_change: Dict[str, float] = None,
                                      recommended_actions: List[str] = None):
        """Create competitive intelligence alert"""
        
        alert = CompetitiveAlert(
            competitor_id=competitor_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            affected_keywords=affected_keywords,
            metrics_change=metrics_change or {},
            recommended_actions=recommended_actions or [],
            urgency_level="normal" if severity in ["low", "medium"] else "high"
        )
        
        self.competitive_alerts.append(alert)
        logger.info(f"Competitive alert created: {title}")
        
    async def _detect_competitive_changes(self):
        """Detect significant competitive changes"""
        while self.monitoring_active:
            try:
                await self._analyze_market_share_changes()
                await self._detect_new_competitors()
                await self._analyze_content_velocity()
                
                await asyncio.sleep(self.monitoring_schedule["alert_check_frequency"] * 3600)
                
            except Exception as e:
                logger.error(f"Error detecting competitive changes: {e}")
                await asyncio.sleep(3600)
                
    async def _analyze_market_share_changes(self):
        """Analyze changes in market share"""
        
        # Calculate current market share for each competitor
        for competitor_id, competitor in self.competitors.items():
            recent_rankings = [
                r for r in self.competitor_rankings[competitor_id]
                if r.tracked_at > datetime.now() - timedelta(days=7)
            ]
            
            if len(recent_rankings) >= 5:
                current_avg_position = statistics.mean([r.current_position for r in recent_rankings])
                
                # Compare with previous week
                previous_rankings = [
                    r for r in self.competitor_rankings[competitor_id]
                    if datetime.now() - timedelta(days=14) < r.tracked_at <= datetime.now() - timedelta(days=7)
                ]
                
                if len(previous_rankings) >= 5:
                    previous_avg_position = statistics.mean([r.current_position for r in previous_rankings])
                    position_change = previous_avg_position - current_avg_position
                    
                    # Significant improvement (position number decreased significantly)
                    if position_change >= 5:
                        await self._create_competitive_alert(
                            competitor_id=competitor_id,
                            alert_type="market_share_gain",
                            severity="medium",
                            title=f"{competitor.name} Gaining Market Share",
                            description=f"Average ranking improved by {position_change:.1f} positions",
                            affected_keywords=[r.keyword for r in recent_rankings[:3]],
                            metrics_change={"avg_position_change": position_change}
                        )
                        
    async def _detect_new_competitors(self):
        """Detect potential new competitors (simulated)"""
        import random
        
        # Simulate occasionally detecting new competitors
        if random.random() < 0.1:  # 10% chance per check
            new_competitor_domains = [
                "newcreator.tools", "contentpro.ai", "viralgrow.app",
                "creatormax.io", "socialboost.co"
            ]
            
            domain = random.choice(new_competitor_domains)
            
            await self._create_competitive_alert(
                competitor_id="",
                alert_type="new_competitor",
                severity="low",
                title="Potential New Competitor Detected",
                description=f"New domain '{domain}' showing activity in our keyword space",
                affected_keywords=self.analysis_keywords[:2],
                recommended_actions=[
                    f"Research {domain} business model and strategy",
                    "Analyze their content approach",
                    "Monitor their growth trajectory"
                ]
            )
            
    async def _analyze_content_velocity(self):
        """Analyze competitor content publishing velocity"""
        
        for competitor_id, competitor in self.competitors.items():
            # Simulate content velocity analysis
            import random
            
            estimated_posts_per_week = random.randint(1, 10)
            
            # Alert if competitor significantly increases content velocity
            if estimated_posts_per_week > 7:  # High velocity threshold
                await self._create_competitive_alert(
                    competitor_id=competitor_id,
                    alert_type="content_velocity_increase",
                    severity="medium",
                    title=f"{competitor.name} Increasing Content Velocity",
                    description=f"Publishing approximately {estimated_posts_per_week} posts per week",
                    affected_keywords=[],
                    recommended_actions=[
                        "Consider increasing our content output",
                        "Analyze their content strategy",
                        "Focus on content quality to compete"
                    ]
                )
                
    async def _generate_competitive_alerts(self):
        """Generate and manage competitive alerts"""
        while self.monitoring_active:
            try:
                # Clean up old alerts
                cutoff_date = datetime.now() - timedelta(days=30)
                self.competitive_alerts = [
                    alert for alert in self.competitive_alerts
                    if alert.triggered_at > cutoff_date
                ]
                
                await asyncio.sleep(3600)  # Check hourly
                
            except Exception as e:
                logger.error(f"Error managing competitive alerts: {e}")
                await asyncio.sleep(3600)
                
    async def _update_competitor_profiles(self):
        """Update competitor profiles with latest data"""
        while self.monitoring_active:
            try:
                for competitor_id, competitor in self.competitors.items():
                    await self._refresh_competitor_metrics(competitor)
                    competitor.last_analyzed = datetime.now()
                    
                await asyncio.sleep(self.monitoring_schedule["full_analysis_frequency"] * 3600)
                
            except Exception as e:
                logger.error(f"Error updating competitor profiles: {e}")
                await asyncio.sleep(3600)
                
    async def _refresh_competitor_metrics(self, competitor: CompetitorProfile):
        """Refresh competitor SEO metrics (simulated)"""
        import random
        
        # Simulate metric updates with realistic changes
        competitor.domain_authority = max(0, min(100, competitor.domain_authority + random.uniform(-2, 3)))
        competitor.organic_traffic = max(0, int(competitor.organic_traffic * random.uniform(0.9, 1.15)))
        competitor.organic_keywords = max(0, int(competitor.organic_keywords * random.uniform(0.95, 1.1)))
        competitor.backlink_count = max(0, int(competitor.backlink_count * random.uniform(0.98, 1.05)))
        
    def get_competitive_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive competitive analysis report"""
        
        # Overall competitive landscape
        total_competitors = len(self.competitors)
        direct_competitors = len([c for c in self.competitors.values() if c.tier == CompetitorTier.DIRECT])
        
        # Recent alerts summary
        recent_alerts = [
            alert for alert in self.competitive_alerts
            if alert.triggered_at > datetime.now() - timedelta(days=7)
        ]
        
        critical_alerts = [a for a in recent_alerts if a.severity == "critical"]
        high_alerts = [a for a in recent_alerts if a.severity == "high"]
        
        # Content gaps summary
        high_priority_gaps = [g for g in self.content_gaps if g.gap_severity in ["high", "critical"]]
        total_traffic_potential = sum([g.estimated_traffic_potential for g in high_priority_gaps])
        
        # Competitor performance summary
        competitor_performance = {}
        for competitor_id, competitor in self.competitors.items():
            recent_rankings = [
                r for r in self.competitor_rankings[competitor_id]
                if r.tracked_at > datetime.now() - timedelta(days=30)
            ]
            
            if recent_rankings:
                avg_position = statistics.mean([r.current_position for r in recent_rankings])
                total_traffic = sum([r.estimated_traffic for r in recent_rankings])
                
                competitor_performance[competitor.name] = {
                    "average_ranking": avg_position,
                    "estimated_traffic": total_traffic,
                    "domain_authority": competitor.domain_authority,
                    "tier": competitor.tier.value
                }
                
        # Top opportunities
        top_opportunities = sorted(high_priority_gaps, key=lambda x: x.estimated_traffic_potential, reverse=True)[:5]
        
        return {
            "competitive_landscape": {
                "total_competitors": total_competitors,
                "direct_competitors": direct_competitors,
                "monitoring_keywords": len(self.analysis_keywords)
            },
            "recent_alerts": {
                "total_alerts": len(recent_alerts),
                "critical_alerts": len(critical_alerts),
                "high_priority_alerts": len(high_alerts),
                "alert_types": Counter([a.alert_type for a in recent_alerts])
            },
            "content_gaps": {
                "total_gaps": len(self.content_gaps),
                "high_priority_gaps": len(high_priority_gaps),
                "total_traffic_potential": total_traffic_potential,
                "top_opportunities": [
                    {
                        "keyword": gap.keyword,
                        "traffic_potential": gap.estimated_traffic_potential,
                        "difficulty": gap.keyword_difficulty,
                        "recommended_content": gap.content_type_recommended
                    }
                    for gap in top_opportunities
                ]
            },
            "competitor_performance": competitor_performance,
            "insights": self._generate_competitive_insights()
        }
        
    def _generate_competitive_insights(self) -> List[str]:
        """Generate competitive insights"""
        insights = []
        
        # Alert insights
        recent_alerts = [
            alert for alert in self.competitive_alerts
            if alert.triggered_at > datetime.now() - timedelta(days=7)
        ]
        
        if len(recent_alerts) > 5:
            insights.append("High competitive activity detected - monitor closely")
        elif len(recent_alerts) == 0:
            insights.append("Stable competitive environment")
            
        # Gap insights
        high_priority_gaps = [g for g in self.content_gaps if g.gap_severity in ["high", "critical"]]
        
        if len(high_priority_gaps) > 10:
            insights.append("Significant content gaps identified - prioritize content creation")
        elif len(high_priority_gaps) < 3:
            insights.append("Good content coverage compared to competitors")
            
        # Performance insights
        strong_competitors = [
            c for c in self.competitors.values() 
            if c.domain_authority > 70 and c.tier == CompetitorTier.DIRECT
        ]
        
        if len(strong_competitors) > 2:
            insights.append("Multiple strong direct competitors - focus on differentiation")
            
        return insights

# Export main classes
__all__ = [
    'CompetitorSEOMonitor',
    'CompetitorProfile',
    'CompetitorRanking',
    'ContentGap',
    'CompetitiveAlert',
    'CompetitorTier',
    'MonitoringFrequency',
    'CompetitiveAdvantage'
]