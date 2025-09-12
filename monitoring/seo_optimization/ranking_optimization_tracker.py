"""
🔍 MONITORING SEO OPTIMIZATION - Ranking Optimization Tracker
Advanced SEO ranking optimization and monitoring for Ainflue platform
SEO + AI Engineer + Content Strategy Implementation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from collections import defaultdict
import re
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Platform(Enum):
    """Platforms for SEO optimization"""
    GOOGLE = "google"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    QUORA = "quora"

class RankingFactor(Enum):
    """SEO ranking factors"""
    KEYWORD_RELEVANCE = "keyword_relevance"
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT_SIGNALS = "engagement_signals"
    SOCIAL_SIGNALS = "social_signals"
    FRESHNESS = "freshness"
    AUTHORITY_SCORE = "authority_score"
    USER_EXPERIENCE = "user_experience"
    TECHNICAL_SEO = "technical_seo"
    MOBILE_OPTIMIZATION = "mobile_optimization"
    LOADING_SPEED = "loading_speed"

class SearchIntent(Enum):
    """Types of search intent"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"
    LOCAL = "local"
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"

class OptimizationStatus(Enum):
    """Status of optimization efforts"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MONITORING = "monitoring"
    NEEDS_IMPROVEMENT = "needs_improvement"
    FAILED = "failed"

@dataclass
class Keyword:
    """Keyword data structure"""
    keyword: str
    search_volume: int
    difficulty: float
    cpc: float
    search_intent: SearchIntent
    related_keywords: List[str] = field(default_factory=list)
    seasonal_trends: Dict[str, float] = field(default_factory=dict)

@dataclass
class ContentRanking:
    """Content ranking data"""
    content_id: str
    url: str
    platform: Platform
    title: str
    keywords: List[str]
    current_rank: int
    previous_rank: Optional[int]
    best_rank: int
    click_through_rate: float
    impressions: int
    clicks: int
    conversion_rate: float
    last_updated: datetime
    ranking_history: List[Tuple[datetime, int]] = field(default_factory=list)

@dataclass
class SEOOptimization:
    """SEO optimization task"""
    optimization_id: str
    content_id: str
    target_keywords: List[str]
    optimization_strategies: List[str]
    status: OptimizationStatus
    priority: int
    expected_impact: float
    actual_impact: Optional[float]
    start_date: datetime
    completion_date: Optional[datetime]
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)

@dataclass
class CompetitorAnalysis:
    """Competitor ranking analysis"""
    competitor_id: str
    domain: str
    content_url: str
    keywords: List[str]
    ranking_positions: Dict[str, int]
    estimated_traffic: int
    authority_score: float
    content_gaps: List[str]
    competitive_advantages: List[str]

@dataclass
class RankingAlert:
    """Ranking change alert"""
    alert_id: str
    content_id: str
    keyword: str
    platform: Platform
    rank_change: int
    current_rank: int
    previous_rank: int
    severity: str
    timestamp: datetime
    recommended_actions: List[str] = field(default_factory=list)

class RankingOptimizationTracker:
    """
    🔍 Advanced Ranking Optimization Tracker for Ainflue Platform
    
    AI-powered SEO optimization with:
    - Multi-platform ranking monitoring and optimization
    - Intelligent keyword research and opportunity discovery
    - Competitor analysis and gap identification
    - Content optimization recommendations with AI insights
    - Real-time ranking alerts and change detection
    - Advanced SERP feature tracking and optimization
    - Voice search optimization and featured snippet targeting
    - Local SEO optimization for creator discovery
    """
    
    def __init__(self, db_url: str = None, api_keys: Dict[str, str] = None):
        """Initialize ranking optimization tracker"""
        self.db_url = db_url
        self.api_keys = api_keys or {}
        
        # Data storage
        self.content_rankings: Dict[str, ContentRanking] = {}
        self.keywords_database: Dict[str, Keyword] = {}
        self.active_optimizations: Dict[str, SEOOptimization] = {}
        self.competitor_data: Dict[str, CompetitorAnalysis] = {}
        self.ranking_alerts: List[RankingAlert] = []
        
        # Tracking metrics
        self.ranking_performance: Dict[Platform, Dict[str, float]] = defaultdict(dict)
        self.optimization_effectiveness: Dict[str, float] = {}
        self.keyword_opportunities: Dict[str, List[str]] = defaultdict(list)
        
        # AI models for optimization
        self.ranking_prediction_model = None
        self.content_optimization_model = None
        
        # Configuration
        self.tracking_interval_hours = 6
        self.alert_thresholds = {
            'rank_drop_major': 10,
            'rank_drop_critical': 20,
            'ctr_drop_threshold': 0.3,
            'impression_drop_threshold': 0.4
        }
        
        logger.info("🔍 Ranking Optimization Tracker initialized")

    async def track_content_rankings(
        self,
        content_id: str,
        url: str,
        platform: Platform,
        target_keywords: List[str],
        title: str = ""
    ) -> bool:
        """
        📊 Start tracking content rankings for specific keywords
        
        Monitor ranking positions across platforms and keywords
        """
        try:
            logger.info(f"📊 Starting ranking tracking: {content_id} on {platform.value}")
            
            # Get current rankings
            current_rankings = await self._fetch_current_rankings(url, target_keywords, platform)
            
            if not current_rankings:
                logger.warning(f"No rankings found for {content_id}")
                return False
            
            # Calculate initial metrics
            total_impressions = sum(data.get('impressions', 0) for data in current_rankings.values())
            total_clicks = sum(data.get('clicks', 0) for data in current_rankings.values())
            avg_ctr = total_clicks / max(1, total_impressions)
            
            # Find best current rank
            ranks = [data.get('rank', 999) for data in current_rankings.values() if data.get('rank')]
            best_rank = min(ranks) if ranks else 999
            avg_rank = sum(ranks) / len(ranks) if ranks else 999
            
            # Create content ranking entry
            ranking = ContentRanking(
                content_id=content_id,
                url=url,
                platform=platform,
                title=title,
                keywords=target_keywords,
                current_rank=int(avg_rank),
                previous_rank=None,
                best_rank=best_rank,
                click_through_rate=avg_ctr,
                impressions=total_impressions,
                clicks=total_clicks,
                conversion_rate=0.0,  # Would be calculated from analytics
                last_updated=datetime.now(),
                ranking_history=[(datetime.now(), int(avg_rank))]
            )
            
            self.content_rankings[content_id] = ranking
            
            logger.info(f"✅ Ranking tracking started: {content_id} (avg rank: {avg_rank:.1f})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error tracking content rankings: {e}")
            return False

    async def _fetch_current_rankings(
        self,
        url: str,
        keywords: List[str],
        platform: Platform
    ) -> Dict[str, Dict[str, Any]]:
        """Fetch current ranking data for keywords"""
        try:
            rankings = {}
            
            # Simulate ranking data fetch - would integrate with real SEO APIs
            for keyword in keywords:
                # Generate realistic ranking data
                base_rank = max(1, int(np.random.lognormal(2.5, 1.2)))  # Log-normal distribution for ranks
                impressions = max(10, int(np.random.gamma(2, 500)))
                ctr = max(0.001, np.random.beta(2, 20))  # Realistic CTR distribution
                clicks = int(impressions * ctr)
                
                # Platform-specific adjustments
                if platform == Platform.YOUTUBE:
                    # YouTube typically has different ranking patterns
                    base_rank = max(1, int(np.random.exponential(15)))
                    ctr *= 1.5  # Higher CTR for video content
                elif platform == Platform.INSTAGRAM:
                    # Instagram hashtag rankings
                    base_rank = max(1, int(np.random.exponential(25)))
                elif platform == Platform.GOOGLE:
                    # Traditional web search rankings
                    if base_rank <= 10:
                        ctr *= 1.2  # First page bonus
                
                rankings[keyword] = {
                    'rank': base_rank,
                    'impressions': impressions,
                    'clicks': clicks,
                    'ctr': ctr,
                    'position_type': 'organic',  # Could be 'featured_snippet', 'local_pack', etc.
                    'serp_features': self._detect_serp_features(keyword, platform)
                }
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error fetching rankings: {e}")
            return {}

    def _detect_serp_features(self, keyword: str, platform: Platform) -> List[str]:
        """Detect SERP features for keyword"""
        features = []
        
        # Simulate SERP feature detection
        if platform == Platform.GOOGLE:
            # Common SERP features
            if 'how' in keyword.lower() or 'what' in keyword.lower():
                if np.random.random() < 0.3:
                    features.append('featured_snippet')
            
            if 'best' in keyword.lower() or 'top' in keyword.lower():
                if np.random.random() < 0.4:
                    features.append('shopping_results')
            
            if any(word in keyword.lower() for word in ['near', 'local', 'around']):
                if np.random.random() < 0.6:
                    features.append('local_pack')
            
            if np.random.random() < 0.2:
                features.append('people_also_ask')
            
            if np.random.random() < 0.15:
                features.append('video_results')
        
        elif platform == Platform.YOUTUBE:
            features.extend(['video_results', 'related_videos'])
            if np.random.random() < 0.3:
                features.append('trending_section')
        
        return features

    async def update_ranking_data(
        self,
        content_id: str
    ) -> bool:
        """
        🔄 Update ranking data for tracked content
        
        Refresh ranking positions and detect changes
        """
        try:
            if content_id not in self.content_rankings:
                logger.error(f"Content {content_id} not being tracked")
                return False
            
            ranking = self.content_rankings[content_id]
            logger.info(f"🔄 Updating ranking data: {content_id}")
            
            # Get updated rankings
            current_rankings = await self._fetch_current_rankings(
                ranking.url, ranking.keywords, ranking.platform
            )
            
            if not current_rankings:
                return False
            
            # Calculate new metrics
            total_impressions = sum(data.get('impressions', 0) for data in current_rankings.values())
            total_clicks = sum(data.get('clicks', 0) for data in current_rankings.values())
            new_ctr = total_clicks / max(1, total_impressions)
            
            # Calculate new average rank
            ranks = [data.get('rank', 999) for data in current_rankings.values() if data.get('rank')]
            new_avg_rank = sum(ranks) / len(ranks) if ranks else 999
            new_best_rank = min(ranks) if ranks else ranking.best_rank
            
            # Update ranking data
            previous_rank = ranking.current_rank
            ranking.previous_rank = previous_rank
            ranking.current_rank = int(new_avg_rank)
            ranking.best_rank = min(ranking.best_rank, new_best_rank)
            ranking.click_through_rate = new_ctr
            ranking.impressions = total_impressions
            ranking.clicks = total_clicks
            ranking.last_updated = datetime.now()
            
            # Add to history
            ranking.ranking_history.append((datetime.now(), int(new_avg_rank)))
            
            # Keep only recent history
            if len(ranking.ranking_history) > 100:
                ranking.ranking_history = ranking.ranking_history[-50:]
            
            # Check for significant changes and create alerts
            await self._check_ranking_alerts(content_id, ranking, previous_rank)
            
            # Update platform performance metrics
            await self._update_platform_performance(ranking.platform, ranking)
            
            logger.info(f"✅ Ranking updated: {content_id} (rank: {new_avg_rank:.1f})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating ranking data: {e}")
            return False

    async def _check_ranking_alerts(
        self,
        content_id: str,
        ranking: ContentRanking,
        previous_rank: int
    ) -> None:
        """Check for ranking changes that require alerts"""
        try:
            rank_change = ranking.current_rank - previous_rank
            
            # Major rank drop
            if rank_change >= self.alert_thresholds['rank_drop_major']:
                severity = 'critical' if rank_change >= self.alert_thresholds['rank_drop_critical'] else 'warning'
                
                alert = RankingAlert(
                    alert_id=f"rank_drop_{content_id}_{int(time.time())}",
                    content_id=content_id,
                    keyword=', '.join(ranking.keywords[:2]),  # First 2 keywords
                    platform=ranking.platform,
                    rank_change=rank_change,
                    current_rank=ranking.current_rank,
                    previous_rank=previous_rank,
                    severity=severity,
                    timestamp=datetime.now(),
                    recommended_actions=self._generate_ranking_recovery_actions(ranking, rank_change)
                )
                
                self.ranking_alerts.append(alert)
            
            # Significant rank improvement
            elif rank_change <= -5:  # Negative because lower rank number is better
                alert = RankingAlert(
                    alert_id=f"rank_improve_{content_id}_{int(time.time())}",
                    content_id=content_id,
                    keyword=', '.join(ranking.keywords[:2]),
                    platform=ranking.platform,
                    rank_change=rank_change,
                    current_rank=ranking.current_rank,
                    previous_rank=previous_rank,
                    severity='positive',
                    timestamp=datetime.now(),
                    recommended_actions=[
                        "Analyze what factors contributed to this improvement",
                        "Apply successful strategies to other content",
                        "Monitor to ensure rank stability"
                    ]
                )
                
                self.ranking_alerts.append(alert)
            
            # Keep only recent alerts
            cutoff_time = datetime.now() - timedelta(days=30)
            self.ranking_alerts = [
                alert for alert in self.ranking_alerts
                if alert.timestamp >= cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Error checking ranking alerts: {e}")

    def _generate_ranking_recovery_actions(
        self,
        ranking: ContentRanking,
        rank_change: int
    ) -> List[str]:
        """Generate recommended actions for ranking recovery"""
        actions = []
        
        try:
            # Severity-based actions
            if rank_change >= 20:
                actions.extend([
                    "URGENT: Check for manual penalties or algorithm updates",
                    "Audit content for policy violations",
                    "Review recent technical changes to the site"
                ])
            elif rank_change >= 10:
                actions.extend([
                    "Analyze competitor content that may be outranking yours",
                    "Check for technical SEO issues (crawl errors, speed)",
                    "Review content freshness and update if needed"
                ])
            else:
                actions.extend([
                    "Monitor for algorithmic fluctuations",
                    "Consider content optimization improvements",
                    "Check social signals and engagement metrics"
                ])
            
            # Platform-specific actions
            if ranking.platform == Platform.GOOGLE:
                actions.extend([
                    "Check Google Search Console for issues",
                    "Review Core Web Vitals scores",
                    "Analyze SERP features for target keywords"
                ])
            elif ranking.platform == Platform.YOUTUBE:
                actions.extend([
                    "Review video engagement metrics (watch time, CTR)",
                    "Optimize video title and thumbnail",
                    "Check for changes in YouTube algorithm updates"
                ])
            elif ranking.platform == Platform.INSTAGRAM:
                actions.extend([
                    "Review hashtag performance and strategy",
                    "Check engagement rate and posting frequency",
                    "Analyze Instagram algorithm changes"
                ])
            
            # CTR-based actions
            if ranking.click_through_rate < 0.02:
                actions.append("Optimize title and meta description for better CTR")
            
            return actions
            
        except Exception as e:
            logger.error(f"Error generating recovery actions: {e}")
            return ["Review ranking factors and competitor analysis"]

    async def _update_platform_performance(
        self,
        platform: Platform,
        ranking: ContentRanking
    ) -> None:
        """Update platform performance metrics"""
        try:
            perf = self.ranking_performance[platform]
            
            # Calculate rolling averages
            current_avg_rank = perf.get('avg_rank', ranking.current_rank)
            current_avg_ctr = perf.get('avg_ctr', ranking.click_through_rate)
            
            # Update with exponential moving average
            alpha = 0.1  # Smoothing factor
            perf['avg_rank'] = current_avg_rank * (1 - alpha) + ranking.current_rank * alpha
            perf['avg_ctr'] = current_avg_ctr * (1 - alpha) + ranking.click_through_rate * alpha
            perf['total_impressions'] = perf.get('total_impressions', 0) + ranking.impressions
            perf['total_clicks'] = perf.get('total_clicks', 0) + ranking.clicks
            perf['last_updated'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error updating platform performance: {e}")

    async def research_keyword_opportunities(
        self,
        seed_keywords: List[str],
        content_type: str = "general",
        target_difficulty: Tuple[float, float] = (0.1, 0.7)
    ) -> List[Keyword]:
        """
        🔍 Research keyword opportunities
        
        Find high-potential keywords for content optimization
        """
        try:
            logger.info(f"🔍 Researching keyword opportunities from {len(seed_keywords)} seed keywords")
            
            keyword_opportunities = []
            
            for seed_keyword in seed_keywords:
                # Generate related keywords
                related_keywords = await self._generate_related_keywords(seed_keyword, content_type)
                
                for keyword_text in related_keywords:
                    # Skip if already in database
                    if keyword_text in self.keywords_database:
                        continue
                    
                    # Generate keyword metrics
                    keyword_data = await self._analyze_keyword_metrics(keyword_text)
                    
                    # Filter by difficulty
                    if (target_difficulty[0] <= keyword_data['difficulty'] <= target_difficulty[1] and
                        keyword_data['search_volume'] >= 100):
                        
                        keyword = Keyword(
                            keyword=keyword_text,
                            search_volume=keyword_data['search_volume'],
                            difficulty=keyword_data['difficulty'],
                            cpc=keyword_data['cpc'],
                            search_intent=keyword_data['search_intent'],
                            related_keywords=keyword_data['related_keywords'],
                            seasonal_trends=keyword_data['seasonal_trends']
                        )
                        
                        keyword_opportunities.append(keyword)
                        self.keywords_database[keyword_text] = keyword
            
            # Sort by opportunity score
            keyword_opportunities.sort(
                key=lambda k: self._calculate_keyword_opportunity_score(k),
                reverse=True
            )
            
            logger.info(f"✅ Found {len(keyword_opportunities)} keyword opportunities")
            return keyword_opportunities[:50]  # Return top 50
            
        except Exception as e:
            logger.error(f"❌ Error researching keyword opportunities: {e}")
            return []

    async def _generate_related_keywords(
        self,
        seed_keyword: str,
        content_type: str
    ) -> List[str]:
        """Generate related keywords from seed keyword"""
        try:
            related_keywords = []
            
            # Simulate keyword expansion - would use real keyword tools in production
            base_terms = seed_keyword.split()
            
            # Add question-based keywords
            question_words = ['how', 'what', 'why', 'when', 'where', 'which']
            for qword in question_words:
                related_keywords.append(f"{qword} {seed_keyword}")
                related_keywords.append(f"{seed_keyword} {qword}")
            
            # Add modifier keywords
            modifiers = {
                'general': ['best', 'top', 'guide', 'tips', 'tutorial', 'review'],
                'creator': ['creator', 'influencer', 'content', 'viral', 'trending'],
                'music': ['music', 'song', 'artist', 'album', 'playlist'],
                'video': ['video', 'youtube', 'tutorial', 'review', 'vlog']
            }
            
            relevant_modifiers = modifiers.get(content_type, modifiers['general'])
            for modifier in relevant_modifiers:
                related_keywords.append(f"{modifier} {seed_keyword}")
                related_keywords.append(f"{seed_keyword} {modifier}")
            
            # Add long-tail variations
            longtail_patterns = [
                f"{seed_keyword} for beginners",
                f"{seed_keyword} step by step",
                f"{seed_keyword} complete guide",
                f"learn {seed_keyword}",
                f"{seed_keyword} examples",
                f"{seed_keyword} tools",
                f"{seed_keyword} strategy",
                f"{seed_keyword} 2025"
            ]
            related_keywords.extend(longtail_patterns)
            
            # Clean and deduplicate
            related_keywords = list(set([
                kw.lower().strip() for kw in related_keywords
                if len(kw) <= 100 and len(kw.split()) <= 8
            ]))
            
            return related_keywords[:30]  # Limit to 30 per seed
            
        except Exception as e:
            logger.error(f"Error generating related keywords: {e}")
            return []

    async def _analyze_keyword_metrics(self, keyword: str) -> Dict[str, Any]:
        """Analyze keyword metrics"""
        try:
            # Simulate keyword metrics analysis
            word_count = len(keyword.split())
            
            # Search volume (inverse correlation with word count)
            base_volume = max(50, int(np.random.lognormal(6, 1.5)))
            if word_count > 3:
                base_volume = int(base_volume * (0.7 ** (word_count - 3)))
            
            # Difficulty (correlation with commercial intent and volume)
            base_difficulty = np.random.beta(2, 3)  # Skewed toward easier keywords
            
            # Adjust difficulty based on commercial terms
            commercial_terms = ['buy', 'price', 'cost', 'purchase', 'sale', 'deal']
            if any(term in keyword.lower() for term in commercial_terms):
                base_difficulty = min(1.0, base_difficulty + 0.3)
            
            # CPC (correlation with commercial intent)
            base_cpc = np.random.gamma(1.5, 0.8)
            if any(term in keyword.lower() for term in commercial_terms):
                base_cpc *= 2.5
            
            # Search intent classification
            search_intent = self._classify_search_intent(keyword)
            
            # Related keywords
            related_keywords = []
            for i in range(5):
                variation = keyword.replace(' ', f' {np.random.choice(["best", "top", "free", "online", "guide"])[:1]} ')
                related_keywords.append(variation)
            
            # Seasonal trends (simplified)
            seasonal_trends = {
                'jan': np.random.uniform(0.8, 1.2),
                'feb': np.random.uniform(0.8, 1.2),
                'mar': np.random.uniform(0.8, 1.2),
                'apr': np.random.uniform(0.8, 1.2),
                'may': np.random.uniform(0.8, 1.2),
                'jun': np.random.uniform(0.8, 1.2),
                'jul': np.random.uniform(0.8, 1.2),
                'aug': np.random.uniform(0.8, 1.2),
                'sep': np.random.uniform(0.8, 1.2),
                'oct': np.random.uniform(0.8, 1.2),
                'nov': np.random.uniform(0.8, 1.2),
                'dec': np.random.uniform(0.8, 1.2)
            }
            
            return {
                'search_volume': int(base_volume),
                'difficulty': base_difficulty,
                'cpc': base_cpc,
                'search_intent': search_intent,
                'related_keywords': related_keywords,
                'seasonal_trends': seasonal_trends
            }
            
        except Exception as e:
            logger.error(f"Error analyzing keyword metrics: {e}")
            return {
                'search_volume': 100,
                'difficulty': 0.5,
                'cpc': 1.0,
                'search_intent': SearchIntent.INFORMATIONAL,
                'related_keywords': [],
                'seasonal_trends': {}
            }

    def _classify_search_intent(self, keyword: str) -> SearchIntent:
        """Classify search intent for keyword"""
        keyword_lower = keyword.lower()
        
        # Transactional intent
        transactional_words = ['buy', 'purchase', 'order', 'sale', 'deal', 'discount', 'price', 'cost']
        if any(word in keyword_lower for word in transactional_words):
            return SearchIntent.TRANSACTIONAL
        
        # Commercial intent
        commercial_words = ['best', 'top', 'review', 'compare', 'vs', 'alternative']
        if any(word in keyword_lower for word in commercial_words):
            return SearchIntent.COMMERCIAL
        
        # Navigational intent
        navigational_words = ['login', 'sign in', 'website', 'official', 'homepage']
        if any(word in keyword_lower for word in navigational_words):
            return SearchIntent.NAVIGATIONAL
        
        # Local intent
        local_words = ['near me', 'local', 'nearby', 'location', 'address']
        if any(word in keyword_lower for word in local_words):
            return SearchIntent.LOCAL
        
        # Educational intent
        educational_words = ['how to', 'tutorial', 'guide', 'learn', 'course', 'lesson']
        if any(word in keyword_lower for word in educational_words):
            return SearchIntent.EDUCATIONAL
        
        # Entertainment intent
        entertainment_words = ['funny', 'viral', 'trending', 'meme', 'entertainment']
        if any(word in keyword_lower for word in entertainment_words):
            return SearchIntent.ENTERTAINMENT
        
        # Default to informational
        return SearchIntent.INFORMATIONAL

    def _calculate_keyword_opportunity_score(self, keyword: Keyword) -> float:
        """Calculate opportunity score for keyword"""
        try:
            # Normalize search volume (log scale)
            volume_score = min(1.0, np.log(keyword.search_volume + 1) / np.log(10000))
            
            # Difficulty score (inverse - easier is better)
            difficulty_score = 1.0 - keyword.difficulty
            
            # CPC score (higher CPC indicates commercial value)
            cpc_score = min(1.0, keyword.cpc / 10)
            
            # Intent score (commercial and transactional are more valuable)
            intent_scores = {
                SearchIntent.TRANSACTIONAL: 1.0,
                SearchIntent.COMMERCIAL: 0.9,
                SearchIntent.LOCAL: 0.8,
                SearchIntent.EDUCATIONAL: 0.7,
                SearchIntent.INFORMATIONAL: 0.6,
                SearchIntent.ENTERTAINMENT: 0.5,
                SearchIntent.NAVIGATIONAL: 0.3
            }
            intent_score = intent_scores.get(keyword.search_intent, 0.5)
            
            # Combine scores with weights
            opportunity_score = (
                volume_score * 0.3 +
                difficulty_score * 0.3 +
                cpc_score * 0.2 +
                intent_score * 0.2
            )
            
            return opportunity_score
            
        except Exception as e:
            logger.error(f"Error calculating opportunity score: {e}")
            return 0.0

    async def analyze_competitor_rankings(
        self,
        keywords: List[str],
        platform: Platform = Platform.GOOGLE,
        top_n: int = 10
    ) -> List[CompetitorAnalysis]:
        """
        🏆 Analyze competitor rankings for target keywords
        
        Identify top competitors and their ranking strategies
        """
        try:
            logger.info(f"🏆 Analyzing competitor rankings for {len(keywords)} keywords on {platform.value}")
            
            competitor_analyses = []
            competitor_data = defaultdict(lambda: {
                'keywords': [],
                'rankings': {},
                'total_estimated_traffic': 0,
                'content_urls': []
            })
            
            # Simulate competitor analysis
            for keyword in keywords:
                # Generate top competitors for this keyword
                top_competitors = await self._get_top_competitors_for_keyword(keyword, platform, top_n)
                
                for rank, competitor in enumerate(top_competitors, 1):
                    domain = competitor['domain']
                    competitor_data[domain]['keywords'].append(keyword)
                    competitor_data[domain]['rankings'][keyword] = rank
                    competitor_data[domain]['total_estimated_traffic'] += competitor.get('estimated_traffic', 0)
                    competitor_data[domain]['content_urls'].append(competitor.get('url', ''))
            
            # Create competitor analysis objects
            for domain, data in competitor_data.items():
                if len(data['keywords']) >= 2:  # Only analyze competitors with multiple keyword rankings
                    
                    # Calculate authority score
                    avg_ranking = np.mean(list(data['rankings'].values()))
                    authority_score = max(0.1, 1.0 - (avg_ranking - 1) / 20)  # Normalize rank to 0-1 scale
                    
                    # Identify content gaps and advantages
                    content_gaps = await self._identify_content_gaps(data['keywords'], domain)
                    competitive_advantages = await self._identify_competitive_advantages(data, domain)
                    
                    analysis = CompetitorAnalysis(
                        competitor_id=f"comp_{domain.replace('.', '_')}",
                        domain=domain,
                        content_url=data['content_urls'][0] if data['content_urls'] else '',
                        keywords=data['keywords'],
                        ranking_positions=data['rankings'],
                        estimated_traffic=data['total_estimated_traffic'],
                        authority_score=authority_score,
                        content_gaps=content_gaps,
                        competitive_advantages=competitive_advantages
                    )
                    
                    competitor_analyses.append(analysis)
                    self.competitor_data[analysis.competitor_id] = analysis
            
            # Sort by authority score
            competitor_analyses.sort(key=lambda x: x.authority_score, reverse=True)
            
            logger.info(f"✅ Analyzed {len(competitor_analyses)} competitors")
            return competitor_analyses
            
        except Exception as e:
            logger.error(f"❌ Error analyzing competitor rankings: {e}")
            return []

    async def _get_top_competitors_for_keyword(
        self,
        keyword: str,
        platform: Platform,
        top_n: int
    ) -> List[Dict[str, Any]]:
        """Get top competitors for specific keyword"""
        try:
            competitors = []
            
            # Simulate competitor data - would use real SERP data in production
            domains = [
                'competitor1.com', 'competitor2.com', 'leadingsite.org',
                'topbrand.net', 'expertguide.com', 'bestreviews.co',
                'ultimateguide.io', 'professionaltips.com', 'masterclass.com',
                'industry-leader.com'
            ]
            
            # Generate top N competitors with realistic metrics
            for i in range(min(top_n, len(domains))):
                domain = domains[i]
                
                # Simulate traffic based on ranking position
                base_traffic = max(10, int(np.random.exponential(200) * (top_n - i) / top_n))
                
                competitor = {
                    'domain': domain,
                    'url': f"https://{domain}/content/{keyword.replace(' ', '-')}",
                    'estimated_traffic': base_traffic,
                    'ranking_position': i + 1,
                    'title': f"Ultimate Guide to {keyword.title()}",
                    'meta_description': f"Comprehensive guide about {keyword} with expert tips and strategies."
                }
                
                competitors.append(competitor)
            
            return competitors
            
        except Exception as e:
            logger.error(f"Error getting top competitors: {e}")
            return []

    async def _identify_content_gaps(self, keywords: List[str], domain: str) -> List[str]:
        """Identify content gaps for competitor analysis"""
        try:
            gaps = []
            
            # Analyze keyword coverage
            keyword_themes = defaultdict(int)
            for keyword in keywords:
                words = keyword.lower().split()
                for word in words:
                    if len(word) > 3:  # Ignore short words
                        keyword_themes[word] += 1
            
            # Identify missing themes
            all_themes = ['tutorial', 'guide', 'tips', 'best', 'how', 'review', 'comparison', 'advanced']
            for theme in all_themes:
                if keyword_themes.get(theme, 0) == 0:
                    gaps.append(f"Missing {theme} content")
            
            # Search intent gaps
            intent_coverage = defaultdict(int)
            for keyword in keywords:
                keyword_obj = self.keywords_database.get(keyword)
                if keyword_obj:
                    intent_coverage[keyword_obj.search_intent] += 1
            
            all_intents = [SearchIntent.INFORMATIONAL, SearchIntent.COMMERCIAL, SearchIntent.TRANSACTIONAL]
            for intent in all_intents:
                if intent_coverage.get(intent, 0) == 0:
                    gaps.append(f"Missing {intent.value} content")
            
            return gaps[:5]  # Return top 5 gaps
            
        except Exception as e:
            logger.error(f"Error identifying content gaps: {e}")
            return []

    async def _identify_competitive_advantages(self, competitor_data: Dict, domain: str) -> List[str]:
        """Identify competitive advantages of competitor"""
        try:
            advantages = []
            
            # High-ranking keywords
            high_ranking_keywords = [
                keyword for keyword, rank in competitor_data['rankings'].items()
                if rank <= 3
            ]
            
            if len(high_ranking_keywords) >= 3:
                advantages.append(f"Strong rankings for {len(high_ranking_keywords)} keywords")
            
            # Authority indicators
            if competitor_data.get('total_estimated_traffic', 0) > 5000:
                advantages.append("High organic traffic volume")
            
            # Domain authority
            if '.edu' in domain or '.gov' in domain:
                advantages.append("High domain authority (educational/government)")
            elif domain in ['wikipedia.org', 'youtube.com', 'reddit.com']:
                advantages.append("Platform authority advantage")
            
            # Content variety
            unique_urls = set(competitor_data.get('content_urls', []))
            if len(unique_urls) > 5:
                advantages.append("Diverse content portfolio")
            
            if not advantages:
                advantages.append("Consistent ranking performance")
            
            return advantages
            
        except Exception as e:
            logger.error(f"Error identifying competitive advantages: {e}")
            return []

    async def create_optimization_plan(
        self,
        content_id: str,
        target_keywords: List[str],
        priority: int = 5
    ) -> str:
        """
        📋 Create SEO optimization plan for content
        
        Generate actionable optimization strategies
        """
        try:
            logger.info(f"📋 Creating optimization plan for: {content_id}")
            
            if content_id not in self.content_rankings:
                logger.error(f"Content {content_id} not being tracked")
                return ""
            
            ranking = self.content_rankings[content_id]
            optimization_id = f"opt_{content_id}_{int(time.time())}"
            
            # Analyze current performance
            current_metrics = {
                'avg_rank': ranking.current_rank,
                'ctr': ranking.click_through_rate,
                'impressions': ranking.impressions,
                'clicks': ranking.clicks
            }
            
            # Generate optimization strategies
            strategies = []
            
            # Title and meta optimization
            if ranking.click_through_rate < 0.05:
                strategies.append("Optimize title and meta description for better CTR")
            
            # Content quality improvements
            if ranking.current_rank > 20:
                strategies.extend([
                    "Conduct comprehensive content audit and enhancement",
                    "Add relevant internal and external links",
                    "Improve content structure with headers and bullet points"
                ])
            
            # Technical SEO
            strategies.extend([
                "Optimize page loading speed and Core Web Vitals",
                "Ensure mobile responsiveness",
                "Implement structured data markup"
            ])
            
            # Keyword-specific strategies
            for keyword in target_keywords:
                keyword_obj = self.keywords_database.get(keyword)
                if keyword_obj:
                    if keyword_obj.search_intent == SearchIntent.COMMERCIAL:
                        strategies.append(f"Add comparison and review elements for '{keyword}'")
                    elif keyword_obj.search_intent == SearchIntent.INFORMATIONAL:
                        strategies.append(f"Expand informational content depth for '{keyword}'")
            
            # Platform-specific strategies
            if ranking.platform == Platform.YOUTUBE:
                strategies.extend([
                    "Optimize video thumbnail and title for click-through rate",
                    "Improve video retention and watch time",
                    "Add relevant video tags and descriptions"
                ])
            elif ranking.platform == Platform.INSTAGRAM:
                strategies.extend([
                    "Optimize hashtag strategy for target keywords",
                    "Improve post engagement through better captions",
                    "Use Instagram Stories and Reels for keyword visibility"
                ])
            
            # Calculate expected impact
            expected_impact = self._calculate_expected_optimization_impact(ranking, strategies)
            
            # Create optimization object
            optimization = SEOOptimization(
                optimization_id=optimization_id,
                content_id=content_id,
                target_keywords=target_keywords,
                optimization_strategies=strategies,
                status=OptimizationStatus.NOT_STARTED,
                priority=priority,
                expected_impact=expected_impact,
                actual_impact=None,
                start_date=datetime.now(),
                completion_date=None,
                metrics_before=current_metrics
            )
            
            self.active_optimizations[optimization_id] = optimization
            
            logger.info(f"✅ Optimization plan created: {optimization_id} (expected impact: {expected_impact:.2f})")
            return optimization_id
            
        except Exception as e:
            logger.error(f"❌ Error creating optimization plan: {e}")
            return ""

    def _calculate_expected_optimization_impact(
        self,
        ranking: ContentRanking,
        strategies: List[str]
    ) -> float:
        """Calculate expected impact of optimization strategies"""
        try:
            base_impact = 0.1  # 10% base improvement
            
            # Strategy-specific impacts
            strategy_impacts = {
                'title': 0.15,
                'meta': 0.10,
                'content': 0.25,
                'technical': 0.20,
                'mobile': 0.15,
                'speed': 0.18,
                'links': 0.12,
                'structure': 0.08
            }
            
            total_impact = base_impact
            for strategy in strategies:
                strategy_lower = strategy.lower()
                for keyword, impact in strategy_impacts.items():
                    if keyword in strategy_lower:
                        total_impact += impact
                        break
            
            # Adjust based on current performance
            if ranking.current_rank > 50:
                total_impact *= 1.5  # More room for improvement
            elif ranking.current_rank <= 10:
                total_impact *= 0.7  # Less room for improvement
            
            # Platform adjustments
            if ranking.platform == Platform.YOUTUBE:
                total_impact *= 1.2  # Video content often has higher optimization potential
            elif ranking.platform == Platform.INSTAGRAM:
                total_impact *= 0.9  # More limited optimization options
            
            return min(0.8, total_impact)  # Cap at 80% improvement
            
        except Exception as e:
            logger.error(f"Error calculating expected impact: {e}")
            return 0.1

    async def generate_ranking_report(
        self,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        📊 Generate comprehensive ranking performance report
        
        Analysis of ranking performance across all tracked content
        """
        try:
            logger.info(f"📊 Generating ranking report ({time_period_days} days)")
            
            cutoff_date = datetime.now() - timedelta(days=time_period_days)
            
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'time_period_days': time_period_days,
                'executive_summary': {},
                'platform_performance': {},
                'content_performance': {},
                'keyword_opportunities': {},
                'competitor_insights': {},
                'optimization_effectiveness': {},
                'recommendations': [],
                'action_items': []
            }
            
            # Executive summary
            total_content = len(self.content_rankings)
            total_keywords = sum(len(ranking.keywords) for ranking in self.content_rankings.values())
            
            # Calculate performance metrics
            avg_rank = np.mean([ranking.current_rank for ranking in self.content_rankings.values()]) if self.content_rankings else 0
            avg_ctr = np.mean([ranking.click_through_rate for ranking in self.content_rankings.values()]) if self.content_rankings else 0
            total_impressions = sum(ranking.impressions for ranking in self.content_rankings.values())
            total_clicks = sum(ranking.clicks for ranking in self.content_rankings.values())
            
            # Rank improvements
            improved_rankings = [
                ranking for ranking in self.content_rankings.values()
                if ranking.previous_rank and ranking.current_rank < ranking.previous_rank
            ]
            
            report['executive_summary'] = {
                'total_content_tracked': total_content,
                'total_keywords_tracked': total_keywords,
                'average_ranking': avg_rank,
                'average_ctr': avg_ctr,
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'content_with_improvements': len(improved_rankings),
                'active_optimizations': len(self.active_optimizations),
                'ranking_alerts_generated': len([
                    alert for alert in self.ranking_alerts
                    if alert.timestamp >= cutoff_date
                ])
            }
            
            # Platform performance analysis
            for platform, perf_data in self.ranking_performance.items():
                platform_content = [
                    ranking for ranking in self.content_rankings.values()
                    if ranking.platform == platform
                ]
                
                if platform_content:
                    report['platform_performance'][platform.value] = {
                        'content_count': len(platform_content),
                        'avg_rank': perf_data.get('avg_rank', 0),
                        'avg_ctr': perf_data.get('avg_ctr', 0),
                        'total_impressions': perf_data.get('total_impressions', 0),
                        'total_clicks': perf_data.get('total_clicks', 0),
                        'top_performing_content': sorted(
                            platform_content,
                            key=lambda x: x.current_rank
                        )[:3]
                    }
            
            # Content performance analysis
            top_performers = sorted(
                self.content_rankings.values(),
                key=lambda x: x.current_rank
            )[:10]
            
            report['content_performance'] = {
                'top_performing_content': [
                    {
                        'content_id': ranking.content_id,
                        'title': ranking.title,
                        'platform': ranking.platform.value,
                        'current_rank': ranking.current_rank,
                        'best_rank': ranking.best_rank,
                        'ctr': ranking.click_through_rate,
                        'keywords': ranking.keywords[:3]  # Top 3 keywords
                    }
                    for ranking in top_performers
                ],
                'improvement_opportunities': [
                    {
                        'content_id': ranking.content_id,
                        'current_rank': ranking.current_rank,
                        'potential_improvement': max(0, ranking.current_rank - ranking.best_rank)
                    }
                    for ranking in self.content_rankings.values()
                    if ranking.current_rank > ranking.best_rank + 5
                ][:10]
            }
            
            # Keyword opportunities
            high_opportunity_keywords = [
                keyword for keyword in self.keywords_database.values()
                if self._calculate_keyword_opportunity_score(keyword) > 0.7
            ]
            
            report['keyword_opportunities'] = {
                'high_opportunity_count': len(high_opportunity_keywords),
                'top_opportunities': [
                    {
                        'keyword': keyword.keyword,
                        'search_volume': keyword.search_volume,
                        'difficulty': keyword.difficulty,
                        'opportunity_score': self._calculate_keyword_opportunity_score(keyword)
                    }
                    for keyword in sorted(
                        high_opportunity_keywords,
                        key=lambda k: self._calculate_keyword_opportunity_score(k),
                        reverse=True
                    )[:10]
                ]
            }
            
            # Competitor insights
            top_competitors = sorted(
                self.competitor_data.values(),
                key=lambda x: x.authority_score,
                reverse=True
            )[:5]
            
            report['competitor_insights'] = {
                'top_competitors': [
                    {
                        'domain': comp.domain,
                        'authority_score': comp.authority_score,
                        'keywords_ranking': len(comp.keywords),
                        'estimated_traffic': comp.estimated_traffic,
                        'competitive_advantages': comp.competitive_advantages[:3]
                    }
                    for comp in top_competitors
                ]
            }
            
            # Optimization effectiveness
            completed_optimizations = [
                opt for opt in self.active_optimizations.values()
                if opt.status == OptimizationStatus.COMPLETED and opt.actual_impact is not None
            ]
            
            if completed_optimizations:
                avg_actual_impact = np.mean([opt.actual_impact for opt in completed_optimizations])
                avg_expected_impact = np.mean([opt.expected_impact for opt in completed_optimizations])
                
                report['optimization_effectiveness'] = {
                    'completed_optimizations': len(completed_optimizations),
                    'avg_actual_impact': avg_actual_impact,
                    'avg_expected_impact': avg_expected_impact,
                    'prediction_accuracy': avg_actual_impact / max(0.01, avg_expected_impact),
                    'successful_optimizations': len([
                        opt for opt in completed_optimizations
                        if opt.actual_impact > 0.1
                    ])
                }
            
            # Generate recommendations
            recommendations = []
            
            if avg_rank > 30:
                recommendations.append("Focus on improving overall content quality and relevance")
            
            if avg_ctr < 0.03:
                recommendations.append("Optimize titles and meta descriptions to improve click-through rates")
            
            if len(high_opportunity_keywords) > 20:
                recommendations.append("Prioritize content creation for high-opportunity keywords")
            
            # Platform-specific recommendations
            for platform, perf in report['platform_performance'].items():
                if perf['avg_rank'] > 50:
                    recommendations.append(f"Improve {platform} SEO strategy - current performance below target")
            
            if not recommendations:
                recommendations.append("SEO performance is on track - continue current strategies")
            
            report['recommendations'] = recommendations
            
            # Action items
            action_items = []
            
            # High-priority alerts
            critical_alerts = [
                alert for alert in self.ranking_alerts
                if alert.severity == 'critical' and alert.timestamp >= cutoff_date
            ]
            
            if critical_alerts:
                action_items.append(f"URGENT: Address {len(critical_alerts)} critical ranking drops")
            
            # Underperforming optimizations
            underperforming_opts = [
                opt for opt in completed_optimizations
                if opt.actual_impact < opt.expected_impact * 0.5
            ]
            
            if underperforming_opts:
                action_items.append(f"Review {len(underperforming_opts)} underperforming optimizations")
            
            # Competitor threats
            strong_competitors = [comp for comp in top_competitors if comp.authority_score > 0.8]
            if strong_competitors:
                action_items.append(f"Analyze strategies of {len(strong_competitors)} high-authority competitors")
            
            if not action_items:
                action_items.append("Continue regular monitoring and optimization")
            
            report['action_items'] = action_items
            
            logger.info(f"✅ Ranking report generated: {avg_rank:.1f} avg rank, {avg_ctr:.3f} avg CTR")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating ranking report: {e}")
            return {}

# Usage example
async def main():
    """Test the ranking optimization tracker"""
    try:
        # Initialize tracker
        tracker = RankingOptimizationTracker()
        
        # Track content rankings
        success = await tracker.track_content_rankings(
            "content_123",
            "https://example.com/content/123",
            Platform.GOOGLE,
            ["content marketing", "social media strategy", "digital marketing tips"],
            "Ultimate Guide to Content Marketing"
        )
        print(f"Ranking tracking started: {success}")
        
        # Update rankings
        if success:
            updated = await tracker.update_ranking_data("content_123")
            print(f"Rankings updated: {updated}")
        
        # Research keyword opportunities
        opportunities = await tracker.research_keyword_opportunities(
            ["content marketing", "social media"],
            "creator"
        )
        print(f"Found {len(opportunities)} keyword opportunities")
        
        # Analyze competitors
        competitors = await tracker.analyze_competitor_rankings(
            ["content marketing", "social media strategy"],
            Platform.GOOGLE
        )
        print(f"Analyzed {len(competitors)} competitors")
        
        # Create optimization plan
        opt_id = await tracker.create_optimization_plan(
            "content_123",
            ["content marketing", "social media strategy"]
        )
        print(f"Optimization plan created: {opt_id}")
        
        # Generate report
        report = await tracker.generate_ranking_report()
        avg_rank = report.get('executive_summary', {}).get('average_ranking', 0)
        print(f"Report generated: {avg_rank:.1f} average ranking")
        
    except Exception as e:
        print(f"Error in ranking optimization tracking: {e}")

if __name__ == "__main__":
    asyncio.run(main())