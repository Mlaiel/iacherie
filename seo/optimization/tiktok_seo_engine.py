"""
TikTok SEO Engine for Ainflue Platform
======================================

Advanced TikTok optimization for creator content discovery and visibility.
Optimizes content for TikTok's algorithm and search functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
from datetime import datetime, timedelta
import hashlib
from collections import Counter, defaultdict
import aiohttp

logger = logging.getLogger(__name__)

class TikTokContentType(Enum):
    """TikTok content types."""
    VIDEO = "video"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    DUET = "duet"
    STITCH = "stitch"
    EFFECT = "effect"
    SOUND = "sound"

class TikTokAudience(Enum):
    """TikTok audience categories."""
    GEN_Z = "gen_z"
    MILLENNIALS = "millennials"
    PARENTS = "parents"
    CREATORS = "creators"
    BUSINESSES = "businesses"
    GLOBAL = "global"
    TEENS = "teens"

class TrendCategory(Enum):
    """TikTok trend categories."""
    DANCE = "dance"
    COMEDY = "comedy"
    EDUCATION = "education"
    DIY = "diy"
    FOOD = "food"
    FITNESS = "fitness"
    FASHION = "fashion"
    MUSIC = "music"
    TECH = "tech"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    ART = "art"

@dataclass
class TikTokHashtag:
    """TikTok hashtag data."""
    hashtag: str
    usage_count: int
    engagement_rate: float
    trending_score: float
    difficulty: str
    category: TrendCategory
    best_posting_times: List[str]
    related_hashtags: List[str]
    audience_demographics: Dict[str, float]
    performance_history: List[Dict[str, Any]]
    created_at: datetime

@dataclass
class TikTokContentOptimization:
    """TikTok content optimization result."""
    optimization_id: str
    content_id: str
    content_type: TikTokContentType
    optimized_caption: str
    optimized_hashtags: List[str]
    trending_sounds: List[str]
    recommended_effects: List[str]
    posting_schedule: Dict[str, str]
    audience_targeting: Dict[str, Any]
    engagement_predictions: Dict[str, float]
    virality_score: float
    optimization_tips: List[str]
    competitive_analysis: Dict[str, Any]
    created_at: datetime

@dataclass
class TikTokTrend:
    """TikTok trend analysis."""
    trend_id: str
    trend_name: str
    category: TrendCategory
    hashtags: List[str]
    sounds: List[str]
    effects: List[str]
    engagement_volume: int
    growth_rate: float
    difficulty: str
    duration_estimate: str
    geographic_focus: List[str]
    creator_opportunities: List[str]
    brand_safety: str
    predicted_lifespan: int
    created_at: datetime

@dataclass
class TikTokCompetitorAnalysis:
    """TikTok competitor analysis."""
    analysis_id: str
    competitor_username: str
    follower_count: int
    average_views: int
    engagement_rate: float
    posting_frequency: float
    top_content_types: List[str]
    successful_hashtags: List[str]
    content_themes: List[str]
    audience_overlap: float
    growth_trends: Dict[str, float]
    content_gaps: List[str]
    recommendations: List[str]
    analyzed_at: datetime

class TikTokSEOEngine:
    """
    Advanced TikTok SEO Engine
    
    Features:
    - Hashtag research and optimization
    - Trend analysis and prediction
    - Content optimization for TikTok algorithm
    - Competitor analysis and benchmarking
    - Viral content prediction
    - Audience targeting optimization
    - Sound and effect recommendations
    - Posting schedule optimization
    """
    
    def __init__(self, db_pool -> None: asyncpg.Pool, api_keys -> None: Dict[str, str]) -> None:
        self.db_pool = db_pool
        self.api_keys = api_keys
        self.session = None
        
        # TikTok-specific optimization patterns
        self.viral_patterns = self._load_viral_patterns()
        self.engagement_factors = self._load_engagement_factors()
        self.trending_indicators = self._load_trending_indicators()
        
    async def __aenter__(self) -> None:
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()
    
    def _load_viral_patterns(self) -> Dict[str, List[str]]:
        """Load viral content patterns for TikTok."""
        return {
            'hook_phrases': [
                'POV:', 'Wait for it...', 'This changed my life', 'You need to try this',
                'Nobody talks about this', 'Plot twist:', 'Day in my life',
                'Things I wish I knew', 'Red flags', 'Green flags'
            ],
            'call_to_actions': [
                'Follow for more', 'Save this for later', 'Share with someone who needs this',
                'Tag a friend', 'Duet this', 'Stitch this', 'Try this yourself'
            ],
            'trending_formats': [
                'Before and after', 'Tutorial', 'Storytime', 'Reaction',
                'Challenge', 'Day in the life', 'Behind the scenes',
                'Tips and tricks', 'Myth busting', 'Product review'
            ]
        }
    
    def _load_engagement_factors(self) -> Dict[str, float]:
        """Load TikTok engagement factors and their weights."""
        return {
            'watch_time': 0.35,
            'likes': 0.20,
            'comments': 0.15,
            'shares': 0.15,
            'completion_rate': 0.10,
            'early_engagement': 0.05
        }
    
    def _load_trending_indicators(self) -> Dict[str, List[str]]:
        """Load trending indicators for different categories."""
        return {
            'music_trends': ['remix', 'cover', 'dance', 'singing', 'instrumental'],
            'challenge_trends': ['challenge', 'trend', 'viral', 'participate'],
            'educational_trends': ['learn', 'tutorial', 'howto', 'tips', 'guide'],
            'entertainment_trends': ['funny', 'comedy', 'humor', 'entertainment', 'laugh']
        }
    
    async def optimize_tiktok_content(
        self,
        content_id: str,
        original_caption: str,
        content_type: TikTokContentType,
        target_audience: TikTokAudience,
        niche: str,
        content_duration: Optional[int] = None
    ) -> TikTokContentOptimization:
        """
        Optimize content for TikTok algorithm and discovery.
        
        Args:
            content_id: Content identifier
            original_caption: Original caption text
            content_type: Type of TikTok content
            target_audience: Target audience category
            niche: Content niche or category
            content_duration: Video duration in seconds
            
        Returns:
            TikTokContentOptimization object
        """
        try:
            optimization_id = f"tiktok_opt_{content_id}_{int(datetime.utcnow().timestamp())}"
            
            # Analyze current caption
            current_hashtags = self._extract_hashtags(original_caption)
            
            # Research optimal hashtags
            optimized_hashtags = await self._research_optimal_hashtags(
                niche, target_audience, current_hashtags
            )
            
            # Optimize caption
            optimized_caption = await self._optimize_caption(
                original_caption, optimized_hashtags, content_type, target_audience
            )
            
            # Get trending sounds recommendations
            trending_sounds = await self._get_trending_sounds(niche, target_audience)
            
            # Get effect recommendations
            recommended_effects = await self._get_recommended_effects(content_type, niche)
            
            # Calculate optimal posting schedule
            posting_schedule = await self._calculate_posting_schedule(target_audience)
            
            # Analyze audience targeting
            audience_targeting = await self._analyze_audience_targeting(
                optimized_hashtags, target_audience, niche
            )
            
            # Predict engagement metrics
            engagement_predictions = await self._predict_engagement(
                optimized_caption, optimized_hashtags, content_type, 
                target_audience, content_duration
            )
            
            # Calculate virality score
            virality_score = self._calculate_virality_score(
                optimized_caption, optimized_hashtags, content_type, engagement_predictions
            )
            
            # Generate optimization tips
            optimization_tips = await self._generate_optimization_tips(
                original_caption, optimized_caption, content_type, engagement_predictions
            )
            
            # Perform competitive analysis
            competitive_analysis = await self._analyze_competitive_landscape(
                niche, optimized_hashtags
            )
            
            optimization = TikTokContentOptimization(
                optimization_id=optimization_id,
                content_id=content_id,
                content_type=content_type,
                optimized_caption=optimized_caption,
                optimized_hashtags=optimized_hashtags,
                trending_sounds=trending_sounds,
                recommended_effects=recommended_effects,
                posting_schedule=posting_schedule,
                audience_targeting=audience_targeting,
                engagement_predictions=engagement_predictions,
                virality_score=virality_score,
                optimization_tips=optimization_tips,
                competitive_analysis=competitive_analysis,
                created_at=datetime.utcnow()
            )
            
            # Store optimization
            await self._store_tiktok_optimization(optimization)
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing TikTok content: {e}")
            raise
    
    async def analyze_tiktok_trends(
        self,
        categories: List[TrendCategory],
        geographic_focus: str = "global",
        time_period: int = 7
    ) -> List[TikTokTrend]:
        """
        Analyze current and emerging TikTok trends.
        
        Args:
            categories: Trend categories to analyze
            geographic_focus: Geographic region focus
            time_period: Analysis period in days
            
        Returns:
            List of TikTokTrend objects
        """
        try:
            trends = []
            
            for category in categories:
                # Analyze trending hashtags for category
                trending_hashtags = await self._analyze_trending_hashtags(
                    category, geographic_focus, time_period
                )
                
                # Analyze trending sounds
                trending_sounds = await self._analyze_trending_sounds(
                    category, time_period
                )
                
                # Analyze trending effects
                trending_effects = await self._analyze_trending_effects(
                    category, time_period
                )
                
                # Calculate trend metrics
                engagement_volume = await self._calculate_trend_engagement(
                    trending_hashtags, time_period
                )
                
                growth_rate = await self._calculate_trend_growth_rate(
                    trending_hashtags, time_period
                )
                
                # Assess trend difficulty and opportunity
                difficulty = self._assess_trend_difficulty(trending_hashtags, engagement_volume)
                duration_estimate = self._estimate_trend_duration(
                    category, growth_rate, engagement_volume
                )
                
                # Generate creator opportunities
                creator_opportunities = await self._identify_creator_opportunities(
                    category, trending_hashtags, trending_sounds
                )
                
                # Assess brand safety
                brand_safety = self._assess_brand_safety(trending_hashtags, category)
                
                # Predict trend lifespan
                predicted_lifespan = self._predict_trend_lifespan(
                    growth_rate, engagement_volume, category
                )
                
                trend = TikTokTrend(
                    trend_id=f"trend_{category.value}_{int(datetime.utcnow().timestamp())}",
                    trend_name=f"{category.value.title()} Trend",
                    category=category,
                    hashtags=trending_hashtags,
                    sounds=trending_sounds,
                    effects=trending_effects,
                    engagement_volume=engagement_volume,
                    growth_rate=growth_rate,
                    difficulty=difficulty,
                    duration_estimate=duration_estimate,
                    geographic_focus=[geographic_focus],
                    creator_opportunities=creator_opportunities,
                    brand_safety=brand_safety,
                    predicted_lifespan=predicted_lifespan,
                    created_at=datetime.utcnow()
                )
                
                trends.append(trend)
                
                # Store trend analysis
                await self._store_tiktok_trend(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing TikTok trends: {e}")
            return []
    
    async def research_tiktok_hashtags(
        self,
        seed_keywords: List[str],
        niche: str,
        target_audience: TikTokAudience,
        competition_level: str = "medium"
    ) -> List[TikTokHashtag]:
        """
        Research optimal hashtags for TikTok content.
        
        Args:
            seed_keywords: Base keywords to expand
            niche: Content niche
            target_audience: Target audience
            competition_level: Desired competition level
            
        Returns:
            List of TikTokHashtag objects
        """
        try:
            hashtags = []
            
            # Generate hashtag variations
            hashtag_variations = self._generate_hashtag_variations(seed_keywords, niche)
            
            for hashtag in hashtag_variations:
                # Analyze hashtag metrics
                usage_count = await self._get_hashtag_usage_count(hashtag)
                engagement_rate = await self._calculate_hashtag_engagement_rate(hashtag)
                trending_score = await self._calculate_hashtag_trending_score(hashtag)
                
                # Assess difficulty
                difficulty = self._assess_hashtag_difficulty(
                    usage_count, engagement_rate, competition_level
                )
                
                # Determine category
                category = self._classify_hashtag_category(hashtag, niche)
                
                # Get optimal posting times
                best_posting_times = await self._get_hashtag_posting_times(
                    hashtag, target_audience
                )
                
                # Find related hashtags
                related_hashtags = await self._find_related_hashtags(hashtag, niche)
                
                # Analyze audience demographics
                audience_demographics = await self._analyze_hashtag_audience(
                    hashtag, target_audience
                )
                
                # Get performance history
                performance_history = await self._get_hashtag_performance_history(
                    hashtag, days=30
                )
                
                tiktok_hashtag = TikTokHashtag(
                    hashtag=hashtag,
                    usage_count=usage_count,
                    engagement_rate=engagement_rate,
                    trending_score=trending_score,
                    difficulty=difficulty,
                    category=category,
                    best_posting_times=best_posting_times,
                    related_hashtags=related_hashtags,
                    audience_demographics=audience_demographics,
                    performance_history=performance_history,
                    created_at=datetime.utcnow()
                )
                
                hashtags.append(tiktok_hashtag)
                
                # Store hashtag data
                await self._store_tiktok_hashtag(tiktok_hashtag)
            
            # Sort by optimization potential
            hashtags.sort(key=lambda h: h.trending_score * h.engagement_rate, reverse=True)
            
            return hashtags
            
        except Exception as e:
            logger.error(f"Error researching TikTok hashtags: {e}")
            return []
    
    async def analyze_tiktok_competitors(
        self,
        competitor_usernames: List[str],
        analysis_depth: str = "standard"
    ) -> List[TikTokCompetitorAnalysis]:
        """
        Analyze TikTok competitors for insights and opportunities.
        
        Args:
            competitor_usernames: List of competitor usernames
            analysis_depth: Depth of analysis (basic, standard, deep)
            
        Returns:
            List of TikTokCompetitorAnalysis objects
        """
        try:
            analyses = []
            
            for username in competitor_usernames:
                analysis_id = f"tiktok_comp_{username}_{int(datetime.utcnow().timestamp())}"
                
                # Get basic metrics
                follower_count = await self._get_follower_count(username)
                average_views = await self._calculate_average_views(username)
                engagement_rate = await self._calculate_competitor_engagement_rate(username)
                posting_frequency = await self._calculate_posting_frequency(username)
                
                # Analyze content patterns
                top_content_types = await self._analyze_content_types(username)
                successful_hashtags = await self._extract_successful_hashtags(username)
                content_themes = await self._identify_content_themes(username)
                
                # Calculate audience overlap
                audience_overlap = await self._calculate_audience_overlap(username)
                
                # Analyze growth trends
                growth_trends = await self._analyze_growth_trends(username)
                
                # Identify content gaps
                content_gaps = await self._identify_content_gaps(username)
                
                # Generate recommendations
                recommendations = await self._generate_competitor_recommendations(
                    username, successful_hashtags, content_themes, content_gaps
                )
                
                analysis = TikTokCompetitorAnalysis(
                    analysis_id=analysis_id,
                    competitor_username=username,
                    follower_count=follower_count,
                    average_views=average_views,
                    engagement_rate=engagement_rate,
                    posting_frequency=posting_frequency,
                    top_content_types=top_content_types,
                    successful_hashtags=successful_hashtags,
                    content_themes=content_themes,
                    audience_overlap=audience_overlap,
                    growth_trends=growth_trends,
                    content_gaps=content_gaps,
                    recommendations=recommendations,
                    analyzed_at=datetime.utcnow()
                )
                
                analyses.append(analysis)
                
                # Store analysis
                await self._store_competitor_analysis(analysis)
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error analyzing TikTok competitors: {e}")
            return []
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text.lower())
        return [tag[1:] for tag in hashtags]  # Remove # symbol
    
    async def _research_optimal_hashtags(
        self,
        niche: str,
        target_audience: TikTokAudience,
        current_hashtags: List[str]
    ) -> List[str]:
        """Research optimal hashtags for content."""
        # Generate niche-specific hashtags
        niche_hashtags = self._generate_niche_hashtags(niche)
        
        # Generate audience-specific hashtags
        audience_hashtags = self._generate_audience_hashtags(target_audience)
        
        # Combine with current hashtags
        all_hashtags = list(set(current_hashtags + niche_hashtags + audience_hashtags))
        
        # Filter and rank hashtags
        optimal_hashtags = await self._filter_and_rank_hashtags(all_hashtags, niche)
        
        # Limit to optimal number (TikTok recommendation: 3-5 hashtags)
        return optimal_hashtags[:5]
    
    def _generate_niche_hashtags(self, niche: str) -> List[str]:
        """Generate hashtags specific to content niche."""
        niche_maps = {
            'fitness': ['fitness', 'workout', 'gym', 'health', 'fitnessmotivation', 'exercise'],
            'food': ['food', 'foodie', 'cooking', 'recipe', 'foodlover', 'chef'],
            'fashion': ['fashion', 'style', 'outfit', 'ootd', 'fashionista', 'trendy'],
            'beauty': ['beauty', 'makeup', 'skincare', 'beautytips', 'makeupartist'],
            'tech': ['tech', 'technology', 'gadgets', 'innovation', 'techreview'],
            'education': ['education', 'learn', 'knowledge', 'study', 'educational'],
            'music': ['music', 'musician', 'song', 'singing', 'musical', 'artist'],
            'dance': ['dance', 'dancing', 'choreography', 'dancer', 'dancevideo'],
            'comedy': ['comedy', 'funny', 'humor', 'jokes', 'comedic', 'laugh'],
            'lifestyle': ['lifestyle', 'life', 'daily', 'dayinmylife', 'livingmybestlife']
        }
        
        return niche_maps.get(niche.lower(), [niche.lower()])
    
    def _generate_audience_hashtags(self, target_audience: TikTokAudience) -> List[str]:
        """Generate hashtags targeting specific audience."""
        audience_maps = {
            TikTokAudience.GEN_Z: ['genz', 'viral', 'trending', 'mood', 'vibes'],
            TikTokAudience.MILLENNIALS: ['millennial', 'adulting', 'nostalgia', 'throwback'],
            TikTokAudience.PARENTS: ['parenting', 'momlife', 'dadlife', 'family', 'kids'],
            TikTokAudience.CREATORS: ['creator', 'contentcreator', 'influence', 'creative'],
            TikTokAudience.BUSINESSES: ['business', 'entrepreneur', 'marketing', 'growth'],
            TikTokAudience.GLOBAL: ['viral', 'trending', 'worldwide', 'global'],
            TikTokAudience.TEENS: ['teen', 'teenager', 'highschool', 'young', 'youth']
        }
        
        return audience_maps.get(target_audience, ['trending'])
    
    async def _optimize_caption(
        self,
        original_caption: str,
        hashtags: List[str],
        content_type: TikTokContentType,
        target_audience: TikTokAudience
    ) -> str:
        """Optimize caption for TikTok algorithm."""
        # Add viral hook if not present
        if not any(hook in original_caption for hook in self.viral_patterns['hook_phrases']):
            hook = self._select_appropriate_hook(content_type, target_audience)
            original_caption = f"{hook} {original_caption}"
        
        # Add call-to-action if not present
        if not any(cta in original_caption.lower() for cta in 
                   [phrase.lower() for phrase in self.viral_patterns['call_to_actions']]):
            cta = self._select_appropriate_cta(content_type, target_audience)
            original_caption = f"{original_caption} {cta}"
        
        # Add optimized hashtags
        hashtag_string = ' '.join([f'#{tag}' for tag in hashtags])
        optimized_caption = f"{original_caption}\n\n{hashtag_string}"
        
        return optimized_caption
    
    def _select_appropriate_hook(
        self,
        content_type: TikTokContentType,
        target_audience: TikTokAudience
    ) -> str:
        """Select appropriate hook based on content type and audience."""
        hooks_by_type = {
            TikTokContentType.VIDEO: ['POV:', 'Wait for it...', 'This changed my life'],
            TikTokContentType.DUET: ['Dueting this because...', 'Adding to this...'],
            TikTokContentType.STITCH: ['Stitching this to add...', 'Building on this...']
        }
        
        hooks = hooks_by_type.get(content_type, self.viral_patterns['hook_phrases'])
        return hooks[0]  # Return first appropriate hook
    
    def _select_appropriate_cta(
        self,
        content_type: TikTokContentType,
        target_audience: TikTokAudience
    ) -> str:
        """Select appropriate call-to-action."""
        ctas_by_audience = {
            TikTokAudience.GEN_Z: ['Follow for more', 'Tag a friend'],
            TikTokAudience.CREATORS: ['Save this for later', 'Try this yourself'],
            TikTokAudience.BUSINESSES: ['Share with your team', 'Follow for business tips']
        }
        
        ctas = ctas_by_audience.get(target_audience, self.viral_patterns['call_to_actions'])
        return ctas[0]
    
    def _calculate_virality_score(
        self,
        caption: str,
        hashtags: List[str],
        content_type: TikTokContentType,
        engagement_predictions: Dict[str, float]
    ) -> float:
        """Calculate predicted virality score (0-100)."""
        score = 0.0
        
        # Caption optimization score (30%)
        caption_score = 0
        if any(hook in caption for hook in self.viral_patterns['hook_phrases']):
            caption_score += 10
        if any(cta in caption for cta in self.viral_patterns['call_to_actions']):
            caption_score += 10
        if len(caption.split()) <= 100:  # Optimal caption length
            caption_score += 10
        
        score += caption_score * 0.3
        
        # Hashtag optimization score (25%)
        hashtag_score = min(len(hashtags) * 5, 25)  # Up to 5 hashtags
        score += hashtag_score * 0.25
        
        # Content type score (20%)
        content_type_scores = {
            TikTokContentType.VIDEO: 25,
            TikTokContentType.DUET: 20,
            TikTokContentType.STITCH: 20,
            TikTokContentType.LIVE_STREAM: 15
        }
        score += content_type_scores.get(content_type, 10) * 0.20
        
        # Engagement prediction score (25%)
        avg_engagement = sum(engagement_predictions.values()) / len(engagement_predictions)
        score += avg_engagement * 0.25
        
        return min(score, 100.0)
    
    async def _store_tiktok_optimization(self, optimization -> None: TikTokContentOptimization) -> None:
        """Store TikTok optimization in database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO tiktok_content_optimizations 
                    (optimization_id, content_id, content_type, optimized_caption,
                     optimized_hashtags, trending_sounds, recommended_effects,
                     posting_schedule, audience_targeting, engagement_predictions,
                     virality_score, optimization_tips, competitive_analysis, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """, 
                    optimization.optimization_id, optimization.content_id,
                    optimization.content_type.value, optimization.optimized_caption,
                    json.dumps(optimization.optimized_hashtags),
                    json.dumps(optimization.trending_sounds),
                    json.dumps(optimization.recommended_effects),
                    json.dumps(optimization.posting_schedule),
                    json.dumps(optimization.audience_targeting),
                    json.dumps(optimization.engagement_predictions),
                    optimization.virality_score,
                    json.dumps(optimization.optimization_tips),
                    json.dumps(optimization.competitive_analysis),
                    optimization.created_at
                )
        except Exception as e:
            logger.error(f"Error storing TikTok optimization: {e}")
    
    async def get_tiktok_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive TikTok SEO dashboard."""
        try:
            # Get recent optimizations
            recent_optimizations = await self._get_recent_optimizations(creator_id)
            
            # Get trending opportunities
            trending_opportunities = await self._get_trending_opportunities(creator_id)
            
            # Get performance metrics
            performance_metrics = await self._get_performance_metrics(creator_id)
            
            # Get competitor insights
            competitor_insights = await self._get_competitor_insights(creator_id)
            
            return {
                'creator_id': creator_id,
                'recent_optimizations': recent_optimizations,
                'trending_opportunities': trending_opportunities,
                'performance_metrics': performance_metrics,
                'competitor_insights': competitor_insights,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting TikTok dashboard: {e}")
            return {}

# Export classes
__all__ = [
    'TikTokSEOEngine',
    'TikTokContentOptimization',
    'TikTokHashtag',
    'TikTokTrend',
    'TikTokCompetitorAnalysis',
    'TikTokContentType',
    'TikTokAudience',
    'TrendCategory'
]