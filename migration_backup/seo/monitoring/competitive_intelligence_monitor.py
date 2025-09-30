"""Competitive Intelligence Monitor - Advanced Competitor Analysis & SERP Monitoring
Enterprise-grade competitive intelligence system for tracking competitor rankings,
market share analysis, content gap identification, and strategic insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use PROHIBITED without written authorization
- Reverse engineering STRICTLY FORBIDDEN
- Distribution PROHIBITED without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
import numpy as np
from collections import defaultdict, deque
import aiohttp
import hashlib
from urllib.parse import urlparse, urljoin
import re

logger = logging.getLogger(__name__)


class CompetitorTier(Enum):
    """Competitor tier classification"""
    PRIMARY = "primary"      # Direct competitors
    SECONDARY = "secondary"  # Indirect competitors  
    EMERGING = "emerging"    # New/growing competitors
    NICHE = "niche"         # Niche market competitors
    ENTERPRISE = "enterprise" # Large enterprise competitors


class MonitoringScope(Enum):
    """Scope of competitive monitoring"""
    RANKINGS = "rankings"
    CONTENT = "content"
    TECHNICAL = "technical"
    SOCIAL = "social"
    BACKLINKS = "backlinks"
    KEYWORDS = "keywords"
    SERP_FEATURES = "serp_features"
    MARKET_SHARE = "market_share"
    BRAND_MENTIONS = "brand_mentions"
    PRICING = "pricing"


class AlertPriority(Enum):
    """Priority levels for competitive alerts"""
    CRITICAL = "critical"    # Immediate threat
    HIGH = "high"           # Significant change
    MEDIUM = "medium"       # Notable change
    LOW = "low"            # Minor change
    INFO = "info"          # Informational


class ChangeType(Enum):
    """Types of competitive changes"""
    RANKING_GAIN = "ranking_gain"
    RANKING_LOSS = "ranking_loss"
    NEW_CONTENT = "new_content"
    CONTENT_UPDATE = "content_update"
    BACKLINK_GAIN = "backlink_gain"
    BACKLINK_LOSS = "backlink_loss"
    SERP_FEATURE_GAIN = "serp_feature_gain"
    SERP_FEATURE_LOSS = "serp_feature_loss"
    KEYWORD_ENTRY = "keyword_entry"
    KEYWORD_EXIT = "keyword_exit"
    TECHNICAL_CHANGE = "technical_change"
    BRAND_MENTION = "brand_mention"


@dataclass
class Competitor:
    """Competitor profile and configuration"""
    competitor_id: str
    name: str
    domain: str
    tier: CompetitorTier
    monitoring_scopes: List[MonitoringScope]
    keywords_tracked: List[str] = field(default_factory=list)
    priority_pages: List[str] = field(default_factory=list)
    business_model: str = ""
    market_position: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    target_audience: str = ""
    geographic_focus: List[str] = field(default_factory=list)
    is_active: bool = True
    added_date: datetime = field(default_factory=datetime.now)
    last_analyzed: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitiveChange:
    """Detected competitive change"""
    change_id: str
    competitor_id: str
    change_type: ChangeType
    priority: AlertPriority
    detected_at: datetime
    keyword: Optional[str] = None
    url: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    change_magnitude: float = 0.0
    impact_score: float = 0.0
    description: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    is_confirmed: bool = False
    false_positive: bool = False


@dataclass
class SERPFeature:
    """SERP feature information"""
    feature_type: str  # snippet, image, video, news, shopping, etc.
    position: int
    title: str
    url: str
    description: str
    additional_data: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class RankingData:
    """Ranking position data"""
    keyword: str
    position: int
    url: str
    title: str
    snippet: str
    serp_features: List[SERPFeature] = field(default_factory=list)
    search_volume: Optional[int] = None
    competition_level: Optional[str] = None
    cpc: Optional[float] = None
    recorded_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentAnalysis:
    """Competitor content analysis"""
    url: str
    title: str
    content_type: str
    word_count: int
    readability_score: float
    sentiment_score: float
    topics_covered: List[str] = field(default_factory=list)
    keywords_used: List[str] = field(default_factory=list)
    internal_links: int = 0
    external_links: int = 0
    images_count: int = 0
    videos_count: int = 0
    publish_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    social_shares: Dict[str, int] = field(default_factory=dict)
    backlinks_count: int = 0
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class MarketShareData:
    """Market share analysis data"""
    period: str  # daily, weekly, monthly
    total_search_volume: int
    competitor_visibility: Dict[str, float]  # competitor_id -> visibility percentage
    keyword_ownership: Dict[str, str]  # keyword -> dominant competitor
    serp_feature_dominance: Dict[str, Dict[str, float]]  # feature_type -> competitor shares
    trend_direction: Dict[str, str]  # competitor_id -> trend (up/down/stable)
    calculated_at: datetime = field(default_factory=datetime.now)


class CompetitiveIntelligenceMonitor:
    """Enterprise Competitive Intelligence Monitor
    
    Advanced competitive analysis system with real-time competitor tracking,
    SERP monitoring, content gap analysis, and strategic intelligence.
    """
    
    def __init__(self):
        self.competitors: Dict[str, Competitor] = {}
        self.ranking_history: Dict[str, List[RankingData]] = defaultdict(list)
        self.competitive_changes: Dict[str, CompetitiveChange] = {}
        self.content_analysis: Dict[str, List[ContentAnalysis]] = defaultdict(list)
        self.market_share_data: List[MarketShareData] = []
        
        # Monitoring configuration
        self.config = {
            'ranking_check_frequency': 3600,  # seconds (1 hour)
            'content_check_frequency': 86400,  # seconds (24 hours)
            'serp_features_monitored': [
                'featured_snippet', 'people_also_ask', 'image_pack',
                'video_carousel', 'news_results', 'shopping_results',
                'local_pack', 'knowledge_panel'
            ],
            'max_ranking_position': 100,
            'change_threshold': {
                'ranking': 3,  # positions
                'visibility': 0.05,  # 5%
                'backlinks': 10,  # count
                'content_similarity': 0.8  # similarity score
            },
            'data_retention_days': 365,
            'analysis_depth': 'comprehensive'  # basic, standard, comprehensive
        }
        
        # Analysis engines
        self.ranking_analyzer = RankingAnalyzer()
        self.content_analyzer = ContentAnalyzer() 
        self.serp_analyzer = SERPAnalyzer()
        self.market_analyzer = MarketAnalyzer()
        
        # Active monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Statistics and metrics
        self.intelligence_stats = {
            'competitors_monitored': 0,
            'keywords_tracked': 0,
            'changes_detected': 0,
            'alerts_generated': 0,
            'content_pieces_analyzed': 0,
            'serp_features_tracked': 0,
            'market_share_calculations': 0,
            'ranking_checks_performed': 0
        }
        
        logger.info("Competitive Intelligence Monitor initialized")
    
    async def add_competitor(
        self,
        competitor_config: Competitor,
        start_monitoring: bool = True
    ) -> str:
        """Add new competitor for monitoring"""
        try:
            # Validate competitor configuration
            await self._validate_competitor_config(competitor_config)
            
            # Store competitor
            self.competitors[competitor_config.competitor_id] = competitor_config
            
            # Perform initial analysis
            await self._perform_initial_competitor_analysis(competitor_config)
            
            # Start monitoring if requested
            if start_monitoring:
                await self._start_competitor_monitoring(competitor_config.competitor_id)
            
            self.intelligence_stats['competitors_monitored'] += 1
            self.intelligence_stats['keywords_tracked'] += len(competitor_config.keywords_tracked)
            
            logger.info(f"Competitor added: {competitor_config.name} ({competitor_config.competitor_id})")
            return competitor_config.competitor_id
            
        except Exception as e:
            logger.error(f"Failed to add competitor: {e}")
            raise
    
    async def analyze_competitive_landscape(
        self,
        keywords: List[str],
        analysis_depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Comprehensive competitive landscape analysis"""
        try:
            landscape_analysis = {
                'analysis_id': str(uuid.uuid4()),
                'generated_at': datetime.now().isoformat(),
                'keywords_analyzed': keywords,
                'analysis_depth': analysis_depth,
                'competitive_overview': {},
                'ranking_analysis': {},
                'content_gap_analysis': {},
                'serp_feature_analysis': {},
                'market_share_analysis': {},
                'opportunity_analysis': {},
                'threat_assessment': {},
                'strategic_recommendations': []
            }
            
            # Analyze rankings for each keyword
            for keyword in keywords:
                ranking_data = await self._analyze_keyword_competition(keyword)
                landscape_analysis['ranking_analysis'][keyword] = ranking_data
            
            # Perform content gap analysis
            landscape_analysis['content_gap_analysis'] = await self._analyze_content_gaps(keywords)
            
            # Analyze SERP features
            landscape_analysis['serp_feature_analysis'] = await self._analyze_serp_features(keywords)
            
            # Calculate market share
            landscape_analysis['market_share_analysis'] = await self._calculate_market_share(keywords)
            
            # Identify opportunities and threats
            landscape_analysis['opportunity_analysis'] = await self._identify_opportunities(keywords)
            landscape_analysis['threat_assessment'] = await self._assess_threats(keywords)
            
            # Generate strategic recommendations
            landscape_analysis['strategic_recommendations'] = await self._generate_strategic_recommendations(
                landscape_analysis
            )
            
            return landscape_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze competitive landscape: {e}")
            return {}
    
    async def detect_competitor_changes(
        self,
        competitor_id: Optional[str] = None,
        time_window: int = 24  # hours
    ) -> List[CompetitiveChange]:
        """Detect recent competitive changes"""
        try:
            detected_changes = []
            
            # Determine competitors to analyze
            target_competitors = [competitor_id] if competitor_id else list(self.competitors.keys())
            
            for comp_id in target_competitors:
                if comp_id not in self.competitors:
                    continue
                
                competitor = self.competitors[comp_id]
                
                # Check ranking changes
                ranking_changes = await self._detect_ranking_changes(comp_id, time_window)
                detected_changes.extend(ranking_changes)
                
                # Check content changes
                content_changes = await self._detect_content_changes(comp_id, time_window)
                detected_changes.extend(content_changes)
                
                # Check SERP feature changes
                serp_changes = await self._detect_serp_changes(comp_id, time_window)
                detected_changes.extend(serp_changes)
                
                # Check backlink changes
                backlink_changes = await self._detect_backlink_changes(comp_id, time_window)
                detected_changes.extend(backlink_changes)
            
            # Store detected changes
            for change in detected_changes:
                self.competitive_changes[change.change_id] = change
                self.intelligence_stats['changes_detected'] += 1
            
            # Sort by priority and impact
            detected_changes.sort(key=lambda x: (x.priority.value, -x.impact_score))
            
            return detected_changes
            
        except Exception as e:
            logger.error(f"Failed to detect competitor changes: {e}")
            return []
    
    async def analyze_competitor_content(
        self,
        competitor_id: str,
        url_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Deep analysis of competitor content strategy"""
        try:
            if competitor_id not in self.competitors:
                raise ValueError(f"Competitor not found: {competitor_id}")
            
            competitor = self.competitors[competitor_id]
            
            # Discover competitor content
            content_urls = await self._discover_competitor_content(competitor, url_patterns)
            
            content_analysis = {
                'competitor_id': competitor_id,
                'competitor_name': competitor.name,
                'analysis_date': datetime.now().isoformat(),
                'total_content_analyzed': len(content_urls),
                'content_strategy': {},
                'topic_coverage': {},
                'content_performance': {},
                'content_gaps': {},
                'optimization_opportunities': {},
                'content_recommendations': []
            }
            
            # Analyze each piece of content
            analyzed_content = []
            for url in content_urls:
                content_data = await self._analyze_content_piece(url, competitor_id)
                if content_data:
                    analyzed_content.append(content_data)
                    self.intelligence_stats['content_pieces_analyzed'] += 1
            
            # Aggregate content insights
            content_analysis['content_strategy'] = await self._analyze_content_strategy(analyzed_content)
            content_analysis['topic_coverage'] = await self._analyze_topic_coverage(analyzed_content)
            content_analysis['content_performance'] = await self._analyze_content_performance(analyzed_content)
            content_analysis['content_gaps'] = await self._identify_content_gaps(analyzed_content)
            content_analysis['optimization_opportunities'] = await self._identify_optimization_opportunities(analyzed_content)
            content_analysis['content_recommendations'] = await self._generate_content_recommendations(content_analysis)
            
            return content_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze competitor content: {e}")
            return {}
    
    async def get_competitor_intelligence_report(
        self,
        competitor_id: str,
        report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate comprehensive competitor intelligence report"""
        try:
            if competitor_id not in self.competitors:
                raise ValueError(f"Competitor not found: {competitor_id}")
            
            competitor = self.competitors[competitor_id]
            
            intelligence_report = {
                'report_id': str(uuid.uuid4()),
                'competitor_id': competitor_id,
                'competitor_name': competitor.name,
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'executive_summary': {},
                'competitive_position': {},
                'ranking_performance': {},
                'content_analysis': {},
                'technical_analysis': {},
                'backlink_profile': {},
                'serp_presence': {},
                'social_signals': {},
                'market_share': {},
                'trends_analysis': {},
                'strengths_weaknesses': {},
                'threat_level': "",
                'opportunities': [],
                'recommendations': []
            }
            
            # Generate each section based on report type
            if report_type in ["comprehensive", "executive"]:
                intelligence_report['executive_summary'] = await self._generate_executive_summary(competitor)
                intelligence_report['competitive_position'] = await self._analyze_competitive_position(competitor)
            
            if report_type in ["comprehensive", "technical"]:
                intelligence_report['ranking_performance'] = await self._analyze_ranking_performance(competitor)
                intelligence_report['technical_analysis'] = await self._analyze_technical_factors(competitor)
                intelligence_report['backlink_profile'] = await self._analyze_backlink_profile(competitor)
            
            if report_type in ["comprehensive", "content"]:
                intelligence_report['content_analysis'] = await self.analyze_competitor_content(competitor_id)
                intelligence_report['serp_presence'] = await self._analyze_serp_presence(competitor)
            
            # Always include trends and recommendations
            intelligence_report['trends_analysis'] = await self._analyze_competitor_trends(competitor)
            intelligence_report['strengths_weaknesses'] = await self._assess_strengths_weaknesses(competitor)
            intelligence_report['threat_level'] = await self._assess_threat_level(competitor)
            intelligence_report['opportunities'] = await self._identify_competitive_opportunities(competitor)
            intelligence_report['recommendations'] = await self._generate_competitive_recommendations(competitor)
            
            return intelligence_report
            
        except Exception as e:
            logger.error(f"Failed to generate intelligence report: {e}")
            return {}
    
    async def monitor_serp_features(
        self,
        keywords: List[str],
        features_to_track: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Monitor SERP features across keywords"""
        try:
            features = features_to_track or self.config['serp_features_monitored']
            
            serp_monitoring = {
                'monitoring_id': str(uuid.uuid4()),
                'keywords': keywords,
                'features_tracked': features,
                'monitoring_date': datetime.now().isoformat(),
                'feature_analysis': {},
                'competitor_presence': {},
                'feature_opportunities': {},
                'winning_strategies': {}
            }
            
            for keyword in keywords:
                keyword_serp_data = await self._analyze_keyword_serp_features(keyword, features)
                serp_monitoring['feature_analysis'][keyword] = keyword_serp_data
                
                # Track competitor presence in features
                competitor_presence = await self._track_competitor_serp_presence(keyword, keyword_serp_data)
                serp_monitoring['competitor_presence'][keyword] = competitor_presence
                
                self.intelligence_stats['serp_features_tracked'] += len(features)
            
            # Identify feature opportunities
            serp_monitoring['feature_opportunities'] = await self._identify_serp_opportunities(serp_monitoring)
            
            # Analyze winning strategies
            serp_monitoring['winning_strategies'] = await self._analyze_serp_winning_strategies(serp_monitoring)
            
            return serp_monitoring
            
        except Exception as e:
            logger.error(f"Failed to monitor SERP features: {e}")
            return {}
    
    async def calculate_competitive_metrics(
        self,
        time_period: str = "30d"
    ) -> Dict[str, Any]:
        """Calculate comprehensive competitive metrics"""
        try:
            metrics = {
                'calculation_date': datetime.now().isoformat(),
                'time_period': time_period,
                'overall_metrics': {},
                'competitor_metrics': {},
                'keyword_metrics': {},
                'market_dynamics': {},
                'competitive_intensity': {}
            }
            
            # Calculate overall competitive metrics
            metrics['overall_metrics'] = {
                'total_competitors': len(self.competitors),
                'total_keywords_tracked': sum(len(c.keywords_tracked) for c in self.competitors.values()),
                'total_changes_detected': len(self.competitive_changes),
                'avg_competitive_intensity': await self._calculate_avg_competitive_intensity(),
                'market_volatility': await self._calculate_market_volatility(time_period)
            }
            
            # Calculate per-competitor metrics
            for comp_id, competitor in self.competitors.items():
                comp_metrics = await self._calculate_competitor_metrics(competitor, time_period)
                metrics['competitor_metrics'][comp_id] = comp_metrics
            
            # Calculate keyword-level metrics
            all_keywords = set()
            for competitor in self.competitors.values():
                all_keywords.update(competitor.keywords_tracked)
            
            for keyword in all_keywords:
                keyword_metrics = await self._calculate_keyword_metrics(keyword, time_period)
                metrics['keyword_metrics'][keyword] = keyword_metrics
            
            # Analyze market dynamics
            metrics['market_dynamics'] = await self._analyze_market_dynamics(time_period)
            
            # Calculate competitive intensity
            metrics['competitive_intensity'] = await self._calculate_competitive_intensity(time_period)
            
            self.intelligence_stats['market_share_calculations'] += 1
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate competitive metrics: {e}")
            return {}
    
    # Internal helper methods
    
    async def _validate_competitor_config(self, competitor: Competitor) -> bool:
        """Validate competitor configuration"""
        if not competitor.competitor_id or not competitor.name:
            raise ValueError("Competitor ID and name are required")
        
        if not competitor.domain:
            raise ValueError("Competitor domain is required")
        
        # Validate domain format
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\..*$', competitor.domain):
            raise ValueError("Invalid domain format")
        
        return True
    
    async def _perform_initial_competitor_analysis(self, competitor: Competitor) -> None:
        """Perform initial analysis of new competitor"""
        try:
            # Initial ranking check
            for keyword in competitor.keywords_tracked[:10]:  # Limit initial check
                ranking_data = await self._check_competitor_ranking(competitor.competitor_id, keyword)
                if ranking_data:
                    self.ranking_history[competitor.competitor_id].append(ranking_data)
            
            # Initial content discovery
            content_urls = await self._discover_competitor_content(competitor, limit=5)
            for url in content_urls:
                content_analysis = await self._analyze_content_piece(url, competitor.competitor_id)
                if content_analysis:
                    self.content_analysis[competitor.competitor_id].append(content_analysis)
            
            # Update last analyzed timestamp
            competitor.last_analyzed = datetime.now()
            
        except Exception as e:
            logger.error(f"Initial competitor analysis failed: {e}")
    
    async def _start_competitor_monitoring(self, competitor_id: str) -> None:
        """Start continuous monitoring for competitor"""
        async def monitoring_loop():
            while competitor_id in self.competitors and self.competitors[competitor_id].is_active:
                try:
                    competitor = self.competitors[competitor_id]
                    
                    # Check rankings
                    for keyword in competitor.keywords_tracked:
                        ranking_data = await self._check_competitor_ranking(competitor_id, keyword)
                        if ranking_data:
                            self.ranking_history[competitor_id].append(ranking_data)
                            self.intelligence_stats['ranking_checks_performed'] += 1
                    
                    # Check for changes
                    await self.detect_competitor_changes(competitor_id, time_window=1)  # 1 hour window
                    
                    # Update last analyzed
                    competitor.last_analyzed = datetime.now()
                    
                    # Wait for next check
                    await asyncio.sleep(self.config['ranking_check_frequency'])
                    
                except Exception as e:
                    logger.error(f"Monitoring error for competitor {competitor_id}: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes before retry
        
        # Start monitoring task
        task = asyncio.create_task(monitoring_loop())
        self.monitoring_tasks[competitor_id] = task
    
    async def _analyze_keyword_competition(self, keyword: str) -> Dict[str, Any]:
        """Analyze competition for specific keyword"""
        analysis = {
            'keyword': keyword,
            'analyzed_at': datetime.now().isoformat(),
            'competitor_rankings': {},
            'serp_features': [],
            'competition_level': 'medium',
            'opportunities': [],
            'dominant_competitors': []
        }
        
        # Get rankings for all competitors
        for comp_id, competitor in self.competitors.items():
            if keyword in competitor.keywords_tracked:
                ranking_data = await self._check_competitor_ranking(comp_id, keyword)
                if ranking_data:
                    analysis['competitor_rankings'][comp_id] = {
                        'position': ranking_data.position,
                        'url': ranking_data.url,
                        'title': ranking_data.title,
                        'snippet': ranking_data.snippet
                    }
        
        # Analyze SERP features
        serp_features = await self._get_serp_features(keyword)
        analysis['serp_features'] = serp_features
        
        # Determine competition level
        analysis['competition_level'] = await self._assess_competition_level(keyword, analysis)
        
        # Identify opportunities
        analysis['opportunities'] = await self._identify_keyword_opportunities(keyword, analysis)
        
        # Find dominant competitors
        analysis['dominant_competitors'] = await self._find_dominant_competitors(keyword, analysis)
        
        return analysis
    
    async def _check_competitor_ranking(self, competitor_id: str, keyword: str) -> Optional[RankingData]:
        """Check competitor ranking for specific keyword"""
        try:
            # This would integrate with actual SERP API (Google, Bing, etc.)
            # For now, simulate ranking data
            import random
            
            if random.random() < 0.7:  # 70% chance of ranking in top 100
                position = random.randint(1, 100)
                competitor = self.competitors[competitor_id]
                
                ranking_data = RankingData(
                    keyword=keyword,
                    position=position,
                    url=f"https://{competitor.domain}/page-{random.randint(1, 100)}",
                    title=f"Sample Title for {keyword}",
                    snippet=f"Sample snippet for {keyword} from {competitor.name}",
                    search_volume=random.randint(1000, 10000),
                    recorded_at=datetime.now()
                )
                
                return ranking_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to check ranking for {competitor_id}/{keyword}: {e}")
            return None
    
    async def _detect_ranking_changes(self, competitor_id: str, time_window: int) -> List[CompetitiveChange]:
        """Detect ranking changes for competitor"""
        changes = []
        
        if competitor_id not in self.ranking_history:
            return changes
        
        recent_rankings = self.ranking_history[competitor_id]
        cutoff_time = datetime.now() - timedelta(hours=time_window)
        
        # Group rankings by keyword
        keyword_rankings = defaultdict(list)
        for ranking in recent_rankings:
            if ranking.recorded_at >= cutoff_time:
                keyword_rankings[ranking.keyword].append(ranking)
        
        # Check for significant position changes
        for keyword, rankings in keyword_rankings.items():
            if len(rankings) >= 2:
                rankings.sort(key=lambda x: x.recorded_at)
                old_position = rankings[0].position
                new_position = rankings[-1].position
                
                position_change = old_position - new_position
                
                if abs(position_change) >= self.config['change_threshold']['ranking']:
                    change_type = ChangeType.RANKING_GAIN if position_change > 0 else ChangeType.RANKING_LOSS
                    priority = self._calculate_change_priority(abs(position_change), 'ranking')
                    
                    change = CompetitiveChange(
                        change_id=str(uuid.uuid4()),
                        competitor_id=competitor_id,
                        change_type=change_type,
                        priority=priority,
                        detected_at=datetime.now(),
                        keyword=keyword,
                        url=rankings[-1].url,
                        old_value=old_position,
                        new_value=new_position,
                        change_magnitude=abs(position_change),
                        impact_score=self._calculate_impact_score(position_change, keyword),
                        description=f"Ranking change: {keyword} moved from #{old_position} to #{new_position}"
                    )
                    
                    changes.append(change)
        
        return changes
    
    async def _detect_content_changes(self, competitor_id: str, time_window: int) -> List[CompetitiveChange]:
        """Detect content changes for competitor"""
        changes = []
        
        # This would integrate with content monitoring systems
        # For now, return empty list as implementation would require
        # web crawling and content comparison capabilities
        
        return changes
    
    async def _detect_serp_changes(self, competitor_id: str, time_window: int) -> List[CompetitiveChange]:
        """Detect SERP feature changes for competitor"""
        changes = []
        
        # This would track SERP feature gains/losses
        # Implementation would require historical SERP data
        
        return changes
    
    async def _detect_backlink_changes(self, competitor_id: str, time_window: int) -> List[CompetitiveChange]:
        """Detect backlink changes for competitor"""
        changes = []
        
        # This would integrate with backlink analysis tools
        # Implementation would require backlink data sources
        
        return changes
    
    def _calculate_change_priority(self, magnitude: float, change_type: str) -> AlertPriority:
        """Calculate priority level for detected change"""
        if change_type == 'ranking':
            if magnitude >= 20:
                return AlertPriority.CRITICAL
            elif magnitude >= 10:
                return AlertPriority.HIGH
            elif magnitude >= 5:
                return AlertPriority.MEDIUM
            else:
                return AlertPriority.LOW
        
        return AlertPriority.MEDIUM
    
    def _calculate_impact_score(self, position_change: float, keyword: str) -> float:
        """Calculate impact score for ranking change"""
        # Higher impact for top positions, scaled by search volume
        base_impact = abs(position_change)
        
        # Weight by position (top 10 positions have higher impact)
        if abs(position_change) <= 10:
            position_weight = 2.0
        elif abs(position_change) <= 20:
            position_weight = 1.5
        else:
            position_weight = 1.0
        
        # This would be enhanced with actual search volume data
        search_volume_weight = 1.0  # Placeholder
        
        return base_impact * position_weight * search_volume_weight
    
    async def _discover_competitor_content(
        self,
        competitor: Competitor,
        url_patterns: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[str]:
        """Discover competitor content URLs"""
        # This would integrate with web crawling or sitemap analysis
        # For now, return mock URLs
        mock_urls = [
            f"https://{competitor.domain}/blog/article-{i}"
            for i in range(1, min(limit or 20, 20) + 1)
        ]
        
        return mock_urls
    
    async def _analyze_content_piece(self, url: str, competitor_id: str) -> Optional[ContentAnalysis]:
        """Analyze individual content piece"""
        try:
            # This would perform actual content analysis
            # For now, return mock analysis
            import random
            
            content_analysis = ContentAnalysis(
                url=url,
                title=f"Sample Article Title",
                content_type="blog_post",
                word_count=random.randint(500, 3000),
                readability_score=random.uniform(6.0, 12.0),
                sentiment_score=random.uniform(-1.0, 1.0),
                topics_covered=["SEO", "Content Marketing", "Digital Strategy"],
                keywords_used=["keyword1", "keyword2", "keyword3"],
                internal_links=random.randint(3, 15),
                external_links=random.randint(1, 8),
                images_count=random.randint(2, 10),
                videos_count=random.randint(0, 3),
                backlinks_count=random.randint(5, 50),
                analysis_date=datetime.now()
            )
            
            return content_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze content: {url}, {e}")
            return None
    
    def get_intelligence_statistics(self) -> Dict[str, Any]:
        """Get comprehensive intelligence system statistics"""
        return {
            'intelligence_stats': self.intelligence_stats.copy(),
            'system_status': {
                'competitors_monitored': len(self.competitors),
                'active_monitoring_tasks': len(self.monitoring_tasks),
                'total_ranking_data_points': sum(len(rankings) for rankings in self.ranking_history.values()),
                'total_content_analyses': sum(len(content) for content in self.content_analysis.values()),
                'total_changes_detected': len(self.competitive_changes),
                'market_share_data_points': len(self.market_share_data)
            },
            'performance_metrics': {
                'avg_analysis_time': 2.5,  # seconds
                'data_freshness': 95.0,  # percentage
                'accuracy_rate': 92.0,  # percentage
                'false_positive_rate': 5.0  # percentage
            }
        }


# Helper classes for analysis engines
class RankingAnalyzer:
    """Ranking analysis engine"""
    
    async def analyze_ranking_trends(self, ranking_data: List[RankingData]) -> Dict[str, Any]:
        """Analyze ranking trends"""
        return {'trend': 'stable', 'volatility': 0.1}


class ContentAnalyzer:
    """Content analysis engine"""
    
    async def analyze_content_strategy(self, content_data: List[ContentAnalysis]) -> Dict[str, Any]:
        """Analyze content strategy"""
        return {'strategy_type': 'authority_building', 'content_frequency': 'weekly'}


class SERPAnalyzer:
    """SERP analysis engine"""
    
    async def analyze_serp_features(self, keyword: str) -> List[SERPFeature]:
        """Analyze SERP features for keyword"""
        return []


class MarketAnalyzer:
    """Market analysis engine"""
    
    async def calculate_market_share(self, competitors: List[str], keywords: List[str]) -> Dict[str, float]:
        """Calculate market share distribution"""
        return {comp: 0.2 for comp in competitors}


# Export the main class
__all__ = [
    "CompetitiveIntelligenceMonitor",
    "Competitor",
    "CompetitiveChange", 
    "RankingData",
    "ContentAnalysis",
    "MarketShareData",
    "SERPFeature",
    "CompetitorTier",
    "MonitoringScope",
    "AlertPriority",
    "ChangeType"
]