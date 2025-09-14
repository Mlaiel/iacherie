"""Hashtag Optimizer

Advanced hashtag and metadata optimization system for maximizing content
discoverability and engagement across all social media platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import re
try:
    import aiohttp
except ImportError:
    aiohttp = None
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import json
import hashlib

# ML and NLP imports (optional)
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    np = TfidfVectorizer = cosine_similarity = None

from .platform_connectors import SocialPlatform


def safe_mean(values) -> None:
    """Calculate mean safely without numpy"""
    if not values:
        return 0.0
    return sum(values) / len(values)

def safe_random_uniform(low, high) -> None:
    """Generate random uniform value without numpy"""
    import random
    return random.uniform(low, high)

def safe_sqrt(value) -> None:
    """Calculate square root safely"""
    import math
    return math.sqrt(max(0, value))

logger = logging.getLogger(__name__)


class HashtagCategory(Enum):
    """Hashtag categories for organization"""
    TRENDING = "trending"
    NICHE = "niche"
    BRANDED = "branded"
    COMMUNITY = "community"
    LOCATION = "location"
    EVERGREEN = "evergreen"
    SEASONAL = "seasonal"
    CAMPAIGN = "campaign"


class HashtagDifficulty(Enum):
    """Hashtag competition difficulty levels"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


@dataclass
class HashtagData:
    """Detailed hashtag information"""
    tag: str
    platform: SocialPlatform
    category: HashtagCategory
    difficulty: HashtagDifficulty
    
    # Performance metrics
    usage_count: int = 0
    engagement_rate: float = 0.0
    reach_potential: int = 0
    competition_score: float = 0.0
    trend_score: float = 0.0
    
    # Platform-specific data
    platform_popularity: Dict[SocialPlatform, float] = field(default_factory=dict)
    related_hashtags: List[str] = field(default_factory=list)
    optimal_times: List[int] = field(default_factory=list)
    
    # Performance history
    historical_performance: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TrendingHashtags:
    """Trending hashtags information"""
    platform: SocialPlatform
    trending_tags: List[HashtagData]
    viral_tags: List[HashtagData]
    emerging_tags: List[HashtagData]
    declining_tags: List[HashtagData]
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class HashtagStrategy:
    """Complete hashtag strategy for content"""
    content_type: str
    target_audience: str
    content_keywords: List[str]
    
    # Platform-specific recommendations
    platform_strategies: Dict[SocialPlatform, List[HashtagData]] = field(default_factory=dict)
    
    # Mix composition
    trending_ratio: float = 0.3    # 30% trending
    niche_ratio: float = 0.4       # 40% niche
    branded_ratio: float = 0.2     # 20% branded
    community_ratio: float = 0.1   # 10% community
    
    # Performance prediction
    predicted_reach: Dict[SocialPlatform, int] = field(default_factory=dict)
    predicted_engagement: Dict[SocialPlatform, float] = field(default_factory=dict)
    confidence_score: float = 0.0


@dataclass
class OptimizedTags:
    """Optimized hashtag set for specific platform"""
    platform: SocialPlatform
    primary_tags: List[str]
    secondary_tags: List[str]
    branded_tags: List[str]
    total_count: int
    estimated_reach: int
    estimated_engagement_rate: float
    optimization_notes: List[str] = field(default_factory=list)


class HashtagOptimizer:
    """Advanced hashtag and metadata optimization system"""
    
    # Platform-specific hashtag limits and best practices
    PLATFORM_LIMITS = {
        SocialPlatform.INSTAGRAM: {
            "max_hashtags": 30,
            "optimal_count": 11,
            "placement": "caption_or_comment",
            "trending_weight": 0.3,
            "niche_weight": 0.5
        },
        SocialPlatform.TIKTOK: {
            "max_hashtags": 100,  # Character limit based
            "optimal_count": 5,
            "placement": "caption",
            "trending_weight": 0.6,
            "niche_weight": 0.3
        },
        SocialPlatform.TWITTER: {
            "max_hashtags": 10,
            "optimal_count": 3,
            "placement": "inline",
            "trending_weight": 0.4,
            "niche_weight": 0.4
        },
        SocialPlatform.YOUTUBE: {
            "max_hashtags": 15,
            "optimal_count": 10,
            "placement": "description",
            "trending_weight": 0.2,
            "niche_weight": 0.6
        },
        SocialPlatform.LINKEDIN: {
            "max_hashtags": 5,
            "optimal_count": 3,
            "placement": "end_of_post",
            "trending_weight": 0.1,
            "niche_weight": 0.8
        },
        SocialPlatform.FACEBOOK: {
            "max_hashtags": 20,
            "optimal_count": 5,
            "placement": "caption",
            "trending_weight": 0.2,
            "niche_weight": 0.6
        }
    }
    
    def __init__(self) -> None:
        self.session: Optional[aiohttp.ClientSession] = None
        self.hashtag_database: Dict[str, HashtagData] = {}
        self.trending_cache: Dict[SocialPlatform, TrendingHashtags] = {}
        self.performance_history: Dict[str, List[Dict]] = defaultdict(list)
        self.keyword_embeddings: Dict[str, list] = {}
        self.hashtag_relationships: Dict[str, List[str]] = defaultdict(list)
        
        # Initialize common hashtag database
        self._initialize_hashtag_database()
    
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _initialize_hashtag_database(self) -> None:
        """Initialize hashtag database with common tags"""
        common_hashtags = {
            # General engagement hashtags
            "love": HashtagCategory.EVERGREEN,
            "instagood": HashtagCategory.EVERGREEN,
            "photooftheday": HashtagCategory.EVERGREEN,
            "beautiful": HashtagCategory.EVERGREEN,
            "happy": HashtagCategory.EVERGREEN,
            "follow": HashtagCategory.COMMUNITY,
            "followme": HashtagCategory.COMMUNITY,
            "like4like": HashtagCategory.COMMUNITY,
            "tagsforlikes": HashtagCategory.COMMUNITY,
            
            # Content type hashtags
            "video": HashtagCategory.NICHE,
            "music": HashtagCategory.NICHE,
            "art": HashtagCategory.NICHE,
            "photography": HashtagCategory.NICHE,
            "fashion": HashtagCategory.NICHE,
            "food": HashtagCategory.NICHE,
            "travel": HashtagCategory.NICHE,
            "fitness": HashtagCategory.NICHE,
            "motivation": HashtagCategory.NICHE,
            "lifestyle": HashtagCategory.NICHE,
            
            # Platform-specific
            "reels": HashtagCategory.NICHE,
            "tiktok": HashtagCategory.BRANDED,
            "viral": HashtagCategory.TRENDING,
            "trending": HashtagCategory.TRENDING,
            "fyp": HashtagCategory.TRENDING,
            "foryou": HashtagCategory.TRENDING,
            "explore": HashtagCategory.COMMUNITY
        }
        
        for tag, category in common_hashtags.items():
            self.hashtag_database[tag] = HashtagData(
                tag=tag,
                platform=SocialPlatform.INSTAGRAM,  # Default platform
                category=category,
                difficulty=HashtagDifficulty.MEDIUM,
                usage_count=10000,
                engagement_rate=0.05,
                reach_potential=50000
            )
    
    async def optimize_hashtags(
        self,
        content_text: str,
        content_type: str,
        target_platforms: List[SocialPlatform],
        target_audience: Optional[str] = None,
        existing_hashtags: Optional[List[str]] = None,
        campaign_tags: Optional[List[str]] = None
    ) -> Dict[SocialPlatform, OptimizedTags]:
        """Optimize hashtags for content across multiple platforms"""
        try:
            # Extract keywords from content
            keywords = await self._extract_keywords(content_text, content_type)
            
            # Get trending hashtags for platforms
            trending_data = await self._get_trending_hashtags(target_platforms)
            
            # Generate hashtag strategy
            strategy = await self._create_hashtag_strategy(
                content_type=content_type,
                keywords=keywords,
                target_audience=target_audience or "general",
                existing_hashtags=existing_hashtags or [],
                campaign_tags=campaign_tags or [],
                trending_data=trending_data
            )
            
            # Optimize for each platform
            optimized_results = {}
            
            for platform in target_platforms:
                optimized_tags = await self._optimize_for_platform(
                    platform=platform,
                    strategy=strategy,
                    keywords=keywords,
                    trending_data=trending_data.get(platform)
                )
                
                optimized_results[platform] = optimized_tags
            
            logger.info(f"Hashtag optimization completed for {len(target_platforms)} platforms")
            return optimized_results
        
        except Exception as e:
            logger.error(f"Hashtag optimization failed: {str(e)}")
            return {}
    
    async def _extract_keywords(self, content_text: str, content_type: str) -> List[str]:
        """Extract relevant keywords from content text"""
        try:
            # Clean and normalize text
            text = re.sub(r'[^a-zA-Z0-9\s]', '', content_text.lower())
            words = text.split()
            
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'this', 'that', 'is', 'are', 'was', 'were', 'be'
            }
            
            # Filter words
            keywords = [
                word for word in words 
                if len(word) > 3 and word not in stop_words
            ]
            
            # Add content type keywords
            content_keywords = {
                "video": ["video", "watch", "content", "visual"],
                "audio": ["music", "sound", "audio", "listen"],
                "image": ["photo", "picture", "visual", "art"],
                "text": ["story", "post", "content", "read"]
            }
            
            if content_type in content_keywords:
                keywords.extend(content_keywords[content_type])
            
            # Remove duplicates and return top keywords
            unique_keywords = list(set(keywords))
            return unique_keywords[:10]  # Top 10 keywords
        
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return []
    
    async def _get_trending_hashtags(
        self,
        platforms: List[SocialPlatform]
    ) -> Dict[SocialPlatform, TrendingHashtags]:
        """Get trending hashtags for specified platforms"""
        try:
            trending_data = {}
            
            for platform in platforms:
                # Check cache first
                cached_data = self.trending_cache.get(platform)
                if cached_data and (datetime.now() - cached_data.updated_at) < timedelta(hours=1):
                    trending_data[platform] = cached_data
                    continue
                
                # Fetch new trending data
                platform_trending = await self._fetch_platform_trending(platform)
                if platform_trending:
                    self.trending_cache[platform] = platform_trending
                    trending_data[platform] = platform_trending
            
            return trending_data
        
        except Exception as e:
            logger.error(f"Trending hashtags retrieval failed: {str(e)}")
            return {}
    
    async def _fetch_platform_trending(self, platform: SocialPlatform) -> Optional[TrendingHashtags]:
        """Fetch trending hashtags for a specific platform"""
        try:
            # In a real implementation, this would call platform APIs
            # For now, return mock trending data
            
            trending_tags_data = {
                SocialPlatform.INSTAGRAM: [
                    "reels", "viral", "trending", "instagood", "photooftheday",
                    "love", "beautiful", "happy", "follow", "instadaily"
                ],
                SocialPlatform.TIKTOK: [
                    "fyp", "foryou", "viral", "trending", "tiktok",
                    "dance", "comedy", "music", "duet", "challenge"
                ],
                SocialPlatform.TWITTER: [
                    "breaking", "news", "trending", "viral", "thread",
                    "opinion", "politics", "sports", "tech", "crypto"
                ],
                SocialPlatform.YOUTUBE: [
                    "youtube", "subscribe", "viral", "trending", "music",
                    "gaming", "tutorial", "review", "vlog", "shorts"
                ],
                SocialPlatform.LINKEDIN: [
                    "professional", "career", "business", "networking", "leadership",
                    "innovation", "technology", "marketing", "sales", "growth"
                ]
            }
            
            tags = trending_tags_data.get(platform, [])
            
            # Create HashtagData objects
            trending_hashtags = []
            viral_hashtags = []
            emerging_hashtags = []
            
            for i, tag in enumerate(tags):
                hashtag_data = HashtagData(
                    tag=tag,
                    platform=platform,
                    category=HashtagCategory.TRENDING if i < 3 else HashtagCategory.NICHE,
                    difficulty=HashtagDifficulty.MEDIUM,
                    usage_count=100000 - (i * 10000),
                    engagement_rate=0.08 - (i * 0.005),
                    reach_potential=500000 - (i * 50000),
                    trend_score=1.0 - (i * 0.1)
                )
                
                if i < 3:
                    viral_hashtags.append(hashtag_data)
                elif i < 6:
                    trending_hashtags.append(hashtag_data)
                else:
                    emerging_hashtags.append(hashtag_data)
            
            return TrendingHashtags(
                platform=platform,
                trending_tags=trending_hashtags,
                viral_tags=viral_hashtags,
                emerging_tags=emerging_hashtags,
                declining_tags=[]
            )
        
        except Exception as e:
            logger.error(f"Platform trending fetch failed for {platform.value}: {str(e)}")
            return None
    
    async def _create_hashtag_strategy(
        self,
        content_type: str,
        keywords: List[str],
        target_audience: str,
        existing_hashtags: List[str],
        campaign_tags: List[str],
        trending_data: Dict[SocialPlatform, TrendingHashtags]
    ) -> HashtagStrategy:
        """Create comprehensive hashtag strategy"""
        try:
            strategy = HashtagStrategy(
                content_type=content_type,
                target_audience=target_audience,
                content_keywords=keywords
            )
            
            # Generate platform-specific strategies
            for platform, trending in trending_data.items():
                platform_hashtags = []
                
                # Add trending hashtags (30%)
                trending_count = int(self.PLATFORM_LIMITS[platform]["optimal_count"] * strategy.trending_ratio)
                platform_hashtags.extend(trending.viral_tags[:trending_count])
                
                # Add niche hashtags based on keywords (40%)
                niche_count = int(self.PLATFORM_LIMITS[platform]["optimal_count"] * strategy.niche_ratio)
                niche_hashtags = await self._find_niche_hashtags(keywords, platform, niche_count)
                platform_hashtags.extend(niche_hashtags)
                
                # Add branded/campaign hashtags (20%)
                branded_count = int(self.PLATFORM_LIMITS[platform]["optimal_count"] * strategy.branded_ratio)
                branded_hashtags = await self._create_branded_hashtags(campaign_tags, content_type, branded_count)
                platform_hashtags.extend(branded_hashtags)
                
                # Add community hashtags (10%)
                community_count = int(self.PLATFORM_LIMITS[platform]["optimal_count"] * strategy.community_ratio)
                community_hashtags = await self._find_community_hashtags(target_audience, platform, community_count)
                platform_hashtags.extend(community_hashtags)
                
                strategy.platform_strategies[platform] = platform_hashtags
                
                # Predict performance
                strategy.predicted_reach[platform] = sum(h.reach_potential for h in platform_hashtags)
                strategy.predicted_engagement[platform] = safe_mean([h.engagement_rate for h in platform_hashtags])
            
            # Calculate overall confidence score
            strategy.confidence_score = self._calculate_strategy_confidence(strategy)
            
            return strategy
        
        except Exception as e:
            logger.error(f"Hashtag strategy creation failed: {str(e)}")
            return HashtagStrategy(
                content_type=content_type,
                target_audience=target_audience,
                content_keywords=keywords
            )
    
    async def _find_niche_hashtags(
        self,
        keywords: List[str],
        platform: SocialPlatform,
        count: int
    ) -> List[HashtagData]:
        """Find niche hashtags based on content keywords"""
        try:
            niche_hashtags = []
            
            for keyword in keywords[:count]:
                # Create variations of the keyword
                variations = [
                    keyword,
                    f"{keyword}life",
                    f"{keyword}love",
                    f"{keyword}daily",
                    f"{keyword}gram",
                    f"{keyword}s"  # Plural
                ]
                
                for variation in variations:
                    if len(niche_hashtags) >= count:
                        break
                    
                    # Check if hashtag exists in database
                    if variation in self.hashtag_database:
                        hashtag_data = self.hashtag_database[variation]
                    else:
                        # Create new hashtag data
                        hashtag_data = HashtagData(
                            tag=variation,
                            platform=platform,
                            category=HashtagCategory.NICHE,
                            difficulty=HashtagDifficulty.EASY,
                            usage_count=5000,
                            engagement_rate=0.06,
                            reach_potential=25000
                        )
                        self.hashtag_database[variation] = hashtag_data
                    
                    niche_hashtags.append(hashtag_data)
                    
                    if len(niche_hashtags) >= count:
                        break
            
            return niche_hashtags[:count]
        
        except Exception as e:
            logger.error(f"Niche hashtag finding failed: {str(e)}")
            return []
    
    async def _create_branded_hashtags(
        self,
        campaign_tags: List[str],
        content_type: str,
        count: int
    ) -> List[HashtagData]:
        """Create branded hashtags for campaigns"""
        try:
            branded_hashtags = []
            
            # Use campaign tags first
            for tag in campaign_tags[:count]:
                hashtag_data = HashtagData(
                    tag=tag,
                    platform=SocialPlatform.INSTAGRAM,  # Default
                    category=HashtagCategory.BRANDED,
                    difficulty=HashtagDifficulty.EASY,
                    usage_count=1000,
                    engagement_rate=0.08,
                    reach_potential=10000
                )
                branded_hashtags.append(hashtag_data)
            
            # Create content-type specific branded tags
            if len(branded_hashtags) < count:
                content_branded = [
                    f"my{content_type}",
                    f"{content_type}content",
                    f"original{content_type}",
                    f"creative{content_type}"
                ]
                
                for tag in content_branded:
                    if len(branded_hashtags) >= count:
                        break
                    
                    hashtag_data = HashtagData(
                        tag=tag,
                        platform=SocialPlatform.INSTAGRAM,
                        category=HashtagCategory.BRANDED,
                        difficulty=HashtagDifficulty.EASY,
                        usage_count=500,
                        engagement_rate=0.07,
                        reach_potential=5000
                    )
                    branded_hashtags.append(hashtag_data)
            
            return branded_hashtags[:count]
        
        except Exception as e:
            logger.error(f"Branded hashtag creation failed: {str(e)}")
            return []
    
    async def _find_community_hashtags(
        self,
        target_audience: str,
        platform: SocialPlatform,
        count: int
    ) -> List[HashtagData]:
        """Find community hashtags for target audience"""
        try:
            community_maps = {
                "general": ["community", "together", "connect", "share"],
                "creators": ["creators", "contentcreator", "creatorlife", "creatercommunity"],
                "artists": ["artists", "artcommunity", "creative", "artistic"],
                "musicians": ["musicians", "musiccommunity", "musiclovers", "musiclife"],
                "fitness": ["fitnesscommunity", "fitfam", "workout", "health"],
                "food": ["foodie", "foodcommunity", "cooking", "recipes"],
                "travel": ["travelers", "wanderlust", "explore", "adventure"],
                "tech": ["tech", "techcommunity", "innovation", "startup"]
            }
            
            community_tags = community_maps.get(target_audience.lower(), community_maps["general"])
            community_hashtags = []
            
            for tag in community_tags[:count]:
                hashtag_data = HashtagData(
                    tag=tag,
                    platform=platform,
                    category=HashtagCategory.COMMUNITY,
                    difficulty=HashtagDifficulty.MEDIUM,
                    usage_count=15000,
                    engagement_rate=0.055,
                    reach_potential=75000
                )
                community_hashtags.append(hashtag_data)
            
            return community_hashtags[:count]
        
        except Exception as e:
            logger.error(f"Community hashtag finding failed: {str(e)}")
            return []
    
    async def _optimize_for_platform(
        self,
        platform: SocialPlatform,
        strategy: HashtagStrategy,
        keywords: List[str],
        trending_data: Optional[TrendingHashtags]
    ) -> OptimizedTags:
        """Optimize hashtags for a specific platform"""
        try:
            platform_config = self.PLATFORM_LIMITS.get(platform, {})
            optimal_count = platform_config.get("optimal_count", 10)
            max_count = platform_config.get("max_hashtags", 30)
            
            # Get platform strategy
            platform_hashtags = strategy.platform_strategies.get(platform, [])
            
            # Sort hashtags by performance potential
            sorted_hashtags = sorted(
                platform_hashtags,
                key=lambda h: h.engagement_rate * h.reach_potential,
                reverse=True
            )
            
            # Select primary hashtags (most important)
            primary_count = min(optimal_count, len(sorted_hashtags))
            primary_tags = [h.tag for h in sorted_hashtags[:primary_count]]
            
            # Select secondary hashtags (additional reach)
            secondary_count = min(max_count - primary_count, len(sorted_hashtags) - primary_count)
            secondary_tags = [h.tag for h in sorted_hashtags[primary_count:primary_count + secondary_count]]
            
            # Extract branded tags
            branded_tags = [
                h.tag for h in sorted_hashtags 
                if h.category == HashtagCategory.BRANDED
            ]
            
            # Calculate performance estimates
            primary_hashtag_data = sorted_hashtags[:primary_count]
            estimated_reach = sum(h.reach_potential for h in primary_hashtag_data)
            estimated_engagement = safe_mean([h.engagement_rate for h in primary_hashtag_data]) if primary_hashtag_data else 0.0
            
            # Generate optimization notes
            optimization_notes = self._generate_optimization_notes(
                platform, primary_hashtag_data, trending_data
            )
            
            return OptimizedTags(
                platform=platform,
                primary_tags=primary_tags,
                secondary_tags=secondary_tags,
                branded_tags=branded_tags,
                total_count=len(primary_tags) + len(secondary_tags),
                estimated_reach=estimated_reach,
                estimated_engagement_rate=estimated_engagement,
                optimization_notes=optimization_notes
            )
        
        except Exception as e:
            logger.error(f"Platform optimization failed for {platform.value}: {str(e)}")
            return OptimizedTags(
                platform=platform,
                primary_tags=[],
                secondary_tags=[],
                branded_tags=[],
                total_count=0,
                estimated_reach=0,
                estimated_engagement_rate=0.0
            )
    
    def _generate_optimization_notes(
        self,
        platform: SocialPlatform,
        hashtags: List[HashtagData],
        trending_data: Optional[TrendingHashtags]
    ) -> List[str]:
        """Generate optimization notes and recommendations"""
        notes = []
        
        # Platform-specific recommendations
        if platform == SocialPlatform.INSTAGRAM:
            notes.append("Mix trending and niche hashtags for optimal reach")
            notes.append("Consider adding hashtags in first comment to keep caption clean")
        elif platform == SocialPlatform.TIKTOK:
            notes.append("Focus on trending hashtags for viral potential")
            notes.append("Use hashtags that match current TikTok trends")
        elif platform == SocialPlatform.TWITTER:
            notes.append("Keep hashtags minimal and integrated into tweet text")
            notes.append("Use trending hashtags to join conversations")
        elif platform == SocialPlatform.LINKEDIN:
            notes.append("Use professional and industry-specific hashtags")
            notes.append("Limit to 3-5 relevant hashtags maximum")
        
        # Difficulty distribution analysis
        difficulties = [h.difficulty for h in hashtags]
        easy_count = sum(1 for d in difficulties if d == HashtagDifficulty.EASY)
        hard_count = sum(1 for d in difficulties if d in [HashtagDifficulty.HARD, HashtagDifficulty.VERY_HARD])
        
        if easy_count > len(hashtags) * 0.8:
            notes.append("Consider adding some competitive hashtags for broader reach")
        elif hard_count > len(hashtags) * 0.5:
            notes.append("Mix includes many competitive hashtags - consider easier alternatives")
        
        # Trending analysis
        if trending_data:
            trending_tags = [h.tag for h in trending_data.trending_tags]
            used_trending = [h.tag for h in hashtags if h.tag in trending_tags]
            
            if len(used_trending) == 0:
                notes.append("Consider including some trending hashtags for visibility")
            elif len(used_trending) > 3:
                notes.append("Heavy use of trending hashtags - ensure content quality matches")
        
        return notes[:5]  # Limit to 5 most important notes
    
    def _calculate_strategy_confidence(self, strategy: HashtagStrategy) -> float:
        """Calculate confidence score for hashtag strategy"""
        try:
            total_platforms = len(strategy.platform_strategies)
            if total_platforms == 0:
                return 0.0
            
            platform_scores = []
            
            for platform, hashtags in strategy.platform_strategies.items():
                if not hashtags:
                    platform_scores.append(0.0)
                    continue
                
                # Score based on hashtag quality and diversity
                avg_engagement = safe_mean([h.engagement_rate for h in hashtags])
                avg_reach = safe_mean([h.reach_potential for h in hashtags])
                
                # Category diversity score
                categories = set(h.category for h in hashtags)
                diversity_score = len(categories) / len(HashtagCategory)
                
                # Difficulty distribution score
                difficulties = [h.difficulty for h in hashtags]
                easy_ratio = sum(1 for d in difficulties if d in [HashtagDifficulty.EASY, HashtagDifficulty.VERY_EASY]) / len(difficulties)
                difficulty_score = 0.7 if 0.3 <= easy_ratio <= 0.7 else 0.4  # Optimal mix
                
                platform_score = (
                    avg_engagement * 0.4 +
                    (avg_reach / 100000) * 0.3 +  # Normalize reach
                    diversity_score * 0.2 +
                    difficulty_score * 0.1
                )
                
                platform_scores.append(min(platform_score, 1.0))  # Cap at 1.0
            
            return safe_mean(platform_scores)
        
        except Exception as e:
            logger.error(f"Confidence calculation failed: {str(e)}")
            return 0.0
    
    async def analyze_hashtag_performance(
        self,
        hashtags -> None: List[str],
        platform -> None: SocialPlatform,
        content_id -> None: str,
        metrics -> None: Dict[str, Any]
    ) -> None:
        """Analyze and store hashtag performance data"""
        try:
            performance_data = {
                "content_id": content_id,
                "platform": platform.value,
                "hashtags": hashtags,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store performance data for each hashtag
            for hashtag in hashtags:
                self.performance_history[hashtag].append(performance_data)
                
                # Update hashtag database with new performance data
                if hashtag in self.hashtag_database:
                    hashtag_data = self.hashtag_database[hashtag]
                    
                    # Update engagement rate (weighted average)
                    if "engagement_rate" in metrics:
                        old_rate = hashtag_data.engagement_rate
                        new_rate = metrics["engagement_rate"]
                        hashtag_data.engagement_rate = (old_rate * 0.7) + (new_rate * 0.3)
                    
                    # Update reach potential
                    if "reach" in metrics:
                        hashtag_data.reach_potential = max(hashtag_data.reach_potential, metrics["reach"])
                    
                    hashtag_data.last_updated = datetime.now()
            
            logger.info(f"Stored performance data for {len(hashtags)} hashtags")
        
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
    
    async def get_hashtag_recommendations(
        self,
        similar_content_ids: List[str],
        target_platform: SocialPlatform,
        count: int = 10
    ) -> List[HashtagData]:
        """Get hashtag recommendations based on similar content performance"""
        try:
            # Collect hashtags from similar content
            similar_hashtags = defaultdict(list)
            
            for content_id in similar_content_ids:
                for hashtag, history in self.performance_history.items():
                    content_performances = [
                        h for h in history 
                        if h["content_id"] == content_id and h["platform"] == target_platform.value
                    ]
                    
                    if content_performances:
                        # Calculate average performance for this hashtag
                        avg_engagement = safe_mean([
                            p["metrics"].get("engagement_rate", 0) 
                            for p in content_performances
                        ])
                        similar_hashtags[hashtag].append(avg_engagement)
            
            # Rank hashtags by average performance
            hashtag_scores = {}
            for hashtag, performances in similar_hashtags.items():
                avg_performance = safe_mean(performances)
                hashtag_scores[hashtag] = avg_performance
            
            # Sort by performance and get top recommendations
            top_hashtags = sorted(
                hashtag_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:count]
            
            # Return HashtagData objects
            recommendations = []
            for hashtag, score in top_hashtags:
                if hashtag in self.hashtag_database:
                    recommendations.append(self.hashtag_database[hashtag])
                else:
                    # Create new hashtag data
                    hashtag_data = HashtagData(
                        tag=hashtag,
                        platform=target_platform,
                        category=HashtagCategory.NICHE,
                        difficulty=HashtagDifficulty.MEDIUM,
                        engagement_rate=score,
                        reach_potential=int(score * 100000)
                    )
                    recommendations.append(hashtag_data)
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Hashtag recommendations failed: {str(e)}")
            return []
    
    async def get_competitor_hashtags(
        self,
        competitor_content: List[str],
        platform: SocialPlatform
    ) -> List[HashtagData]:
        """Analyze competitor hashtag usage"""
        try:
            # Extract hashtags from competitor content
            all_hashtags = []
            
            for content in competitor_content:
                # Find hashtags in content (words starting with #)
                hashtag_pattern = r'#(\w+)'
                found_hashtags = re.findall(hashtag_pattern, content.lower())
                all_hashtags.extend(found_hashtags)
            
            # Count hashtag frequency
            hashtag_counts = Counter(all_hashtags)
            
            # Create HashtagData objects for most used hashtags
            competitor_hashtags = []
            
            for hashtag, count in hashtag_counts.most_common(20):
                # Estimate performance based on usage frequency
                usage_score = min(count / len(competitor_content), 1.0)
                
                hashtag_data = HashtagData(
                    tag=hashtag,
                    platform=platform,
                    category=HashtagCategory.TRENDING if count > len(competitor_content) * 0.3 else HashtagCategory.NICHE,
                    difficulty=HashtagDifficulty.MEDIUM,
                    usage_count=count * 1000,  # Estimate
                    engagement_rate=0.04 + (usage_score * 0.03),  # 4-7% based on usage
                    reach_potential=int(usage_score * 200000)
                )
                
                competitor_hashtags.append(hashtag_data)
            
            return competitor_hashtags
        
        except Exception as e:
            logger.error(f"Competitor hashtag analysis failed: {str(e)}")
            return []
    
    async def generate_hashtag_report(
        self,
        content_id: str,
        platforms: List[SocialPlatform],
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive hashtag performance report"""
        try:
            period_start = datetime.now() - timedelta(days=period_days)
            
            report = {
                "content_id": content_id,
                "report_period": f"{period_days} days",
                "generated_at": datetime.now().isoformat(),
                "platform_performance": {},
                "top_performing_hashtags": [],
                "underperforming_hashtags": [],
                "recommendations": []
            }
            
            # Analyze performance by platform
            for platform in platforms:
                platform_data = {
                    "total_hashtags_used": 0,
                    "avg_engagement_rate": 0.0,
                    "total_reach": 0,
                    "best_hashtags": [],
                    "worst_hashtags": []
                }
                
                # Collect hashtag performance for this platform
                hashtag_performances = []
                
                for hashtag, history in self.performance_history.items():
                    platform_performances = [
                        h for h in history 
                        if (h["content_id"] == content_id and 
                            h["platform"] == platform.value and 
                            datetime.fromisoformat(h["timestamp"]) >= period_start)
                    ]
                    
                    if platform_performances:
                        avg_engagement = safe_mean([
                            p["metrics"].get("engagement_rate", 0)
                            for p in platform_performances
                        ])
                        total_reach = sum([
                            p["metrics"].get("reach", 0)
                            for p in platform_performances
                        ])
                        
                        hashtag_performances.append({
                            "hashtag": hashtag,
                            "engagement_rate": avg_engagement,
                            "reach": total_reach,
                            "usage_count": len(platform_performances)
                        })
                
                if hashtag_performances:
                    platform_data["total_hashtags_used"] = len(hashtag_performances)
                    platform_data["avg_engagement_rate"] = safe_mean([
                        h["engagement_rate"] for h in hashtag_performances
                    ])
                    platform_data["total_reach"] = sum([
                        h["reach"] for h in hashtag_performances
                    ])
                    
                    # Sort by engagement rate
                    sorted_hashtags = sorted(
                        hashtag_performances,
                        key=lambda x: x["engagement_rate"],
                        reverse=True
                    )
                    
                    platform_data["best_hashtags"] = sorted_hashtags[:5]
                    platform_data["worst_hashtags"] = sorted_hashtags[-3:]
                
                report["platform_performance"][platform.value] = platform_data
            
            # Generate overall recommendations
            all_performances = []
            for platform_data in report["platform_performance"].values():
                all_performances.extend(platform_data.get("best_hashtags", []))
            
            if all_performances:
                # Top performing hashtags overall
                global_best = sorted(
                    all_performances,
                    key=lambda x: x["engagement_rate"],
                    reverse=True
                )[:10]
                
                report["top_performing_hashtags"] = global_best
                
                # Generate recommendations
                report["recommendations"] = [
                    f"Focus on hashtags with >5% engagement rate",
                    f"Test variations of top-performing hashtag: {global_best[0]['hashtag']}",
                    "Mix trending and niche hashtags for optimal reach",
                    "Monitor competitor hashtag usage for new opportunities"
                ]
            
            return report
        
        except Exception as e:
            logger.error(f"Hashtag report generation failed: {str(e)}")
            return {"error": str(e)}
    
    def clear_cache(self) -> None:
        """Clear hashtag caches"""
        self.trending_cache.clear()
        logger.info("Hashtag optimizer caches cleared")
    
    async def get_optimizer_statistics(self) -> Dict[str, Any]:
        """Get optimizer performance statistics"""
        try:
            total_hashtags = len(self.hashtag_database)
            total_performance_records = sum(len(history) for history in self.performance_history.values())
            
            # Category distribution
            category_distribution = defaultdict(int)
            for hashtag_data in self.hashtag_database.values():
                category_distribution[hashtag_data.category.value] += 1
            
            # Platform distribution in trending cache
            platforms_cached = len(self.trending_cache)
            
            return {
                "total_hashtags_tracked": total_hashtags,
                "total_performance_records": total_performance_records,
                "category_distribution": dict(category_distribution),
                "platforms_with_trending_data": platforms_cached,
                "cache_sizes": {
                    "hashtag_database": total_hashtags,
                    "trending_cache": platforms_cached,
                    "performance_history": len(self.performance_history)
                }
            }
        
        except Exception as e:
            logger.error(f"Statistics generation failed: {str(e)}")
            return {}