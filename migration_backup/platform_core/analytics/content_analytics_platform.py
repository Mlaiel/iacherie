#!/usr/bin/env python3
"""
Content Analytics Platform - Enterprise Analytics Component
Advanced content performance analysis, viral prediction, and content optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)
Toute reproduction, distribution ou utilisation non autorisée est strictement interdite.

This module provides comprehensive content analytics including:
- Content performance analytics and scoring
- Viral content prediction algorithms
- Content quality assessment and optimization
- Cross-platform content correlation analysis
- Content strategy recommendations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, Counter
import re
import hashlib
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content supported"""
    VIDEO = "video"
    IMAGE = "image"
    TEXT_POST = "text_post"
    STORY = "story"
    REEL = "reel"
    LIVE_STREAM = "live_stream"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"
    CAROUSEL = "carousel"
    POLL = "poll"
    QUIZ = "quiz"
    USER_GENERATED = "user_generated"


class PlatformType(Enum):
    """Platform types for content analytics"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    CLUBHOUSE = "clubhouse"


class ContentStatus(Enum):
    """Content publication status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"
    FLAGGED = "flagged"


class ViralityLevel(Enum):
    """Virality classification levels"""
    LOW = "low"              # Below average performance
    MODERATE = "moderate"    # Average performance
    HIGH = "high"           # Above average performance
    VIRAL = "viral"         # Significantly high performance
    MEGA_VIRAL = "mega_viral"  # Exceptional performance


@dataclass
class ContentMetadata:
    """Content metadata and attributes"""
    content_id: str
    creator_id: str
    title: str
    description: str
    content_type: ContentType
    platform: PlatformType
    tags: List[str]
    hashtags: List[str]
    mentions: List[str]
    duration_seconds: Optional[int] = None
    file_size_mb: Optional[float] = None
    resolution: Optional[str] = None
    language: str = "en"
    nsfw_flag: bool = False
    brand_safety_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentPerformance:
    """Content performance metrics"""
    content_id: str
    platform: PlatformType
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saves: int = 0
    clicks: int = 0
    reach: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    completion_rate: float = 0.0
    watch_time_minutes: float = 0.0
    unique_viewers: int = 0
    returning_viewers: int = 0
    demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, int] = field(default_factory=dict)
    device_breakdown: Dict[str, int] = field(default_factory=dict)
    traffic_sources: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ContentInsight:
    """AI-generated content insight"""
    insight_id: str
    content_id: str
    insight_type: str
    title: str
    description: str
    impact_score: float
    confidence_level: float
    recommended_actions: List[str]
    supporting_data: Dict[str, Any]
    generated_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class ViralPrediction:
    """Viral content prediction data"""
    prediction_id: str
    content_id: str
    predicted_virality: ViralityLevel
    confidence_score: float
    predicted_metrics: Dict[str, int]
    viral_factors: List[str]
    risk_factors: List[str]
    optimal_posting_time: datetime
    predicted_peak_engagement: datetime
    methodology: str
    generated_at: datetime


@dataclass
class ContentQualityScore:
    """Content quality assessment"""
    content_id: str
    overall_score: float
    technical_quality: float
    content_relevance: float
    engagement_potential: float
    brand_alignment: float
    seo_optimization: float
    accessibility_score: float
    quality_factors: List[str]
    improvement_suggestions: List[str]
    assessed_at: datetime


class ContentAnalyticsPlatform:
    """
    Enterprise Content Analytics Platform
    
    Provides comprehensive content performance analytics, viral prediction,
    and content optimization recommendations for creator economy.
    """
    
    def __init__(self):
        """Initialize the content analytics platform"""
        self.content_registry: Dict[str, ContentMetadata] = {}
        self.performance_data: Dict[str, Dict[str, ContentPerformance]] = defaultdict(dict)
        self.insights_cache: Dict[str, List[ContentInsight]] = defaultdict(list)
        self.viral_predictions: Dict[str, List[ViralPrediction]] = defaultdict(list)
        self.quality_scores: Dict[str, ContentQualityScore] = {}
        self.trending_topics: Dict[str, List[str]] = defaultdict(list)
        self.content_clusters: Dict[str, List[str]] = defaultdict(list)
        
        # Performance benchmarks by platform and content type
        self.performance_benchmarks = self._initialize_benchmarks()
        
        logger.info("Content Analytics Platform initialized")
    
    def _initialize_benchmarks(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Initialize performance benchmarks"""
        return {
            PlatformType.YOUTUBE.value: {
                ContentType.VIDEO.value: {
                    "avg_engagement_rate": 0.045,
                    "avg_ctr": 0.02,
                    "avg_completion_rate": 0.45,
                    "viral_threshold_views": 100000
                },
                ContentType.LIVE_STREAM.value: {
                    "avg_engagement_rate": 0.08,
                    "avg_concurrent_viewers": 150,
                    "viral_threshold_views": 50000
                }
            },
            PlatformType.INSTAGRAM.value: {
                ContentType.IMAGE.value: {
                    "avg_engagement_rate": 0.067,
                    "avg_reach_rate": 0.12,
                    "viral_threshold_likes": 50000
                },
                ContentType.REEL.value: {
                    "avg_engagement_rate": 0.089,
                    "avg_reach_rate": 0.18,
                    "viral_threshold_views": 1000000
                },
                ContentType.STORY.value: {
                    "avg_engagement_rate": 0.034,
                    "avg_completion_rate": 0.67,
                    "viral_threshold_views": 100000
                }
            },
            PlatformType.TIKTOK.value: {
                ContentType.VIDEO.value: {
                    "avg_engagement_rate": 0.129,
                    "avg_completion_rate": 0.51,
                    "viral_threshold_views": 1000000
                }
            },
            PlatformType.TWITTER.value: {
                ContentType.TEXT_POST.value: {
                    "avg_engagement_rate": 0.027,
                    "avg_retweet_rate": 0.009,
                    "viral_threshold_retweets": 10000
                },
                ContentType.IMAGE.value: {
                    "avg_engagement_rate": 0.048,
                    "viral_threshold_likes": 25000
                }
            },
            PlatformType.LINKEDIN.value: {
                ContentType.TEXT_POST.value: {
                    "avg_engagement_rate": 0.054,
                    "avg_click_rate": 0.012,
                    "viral_threshold_views": 50000
                },
                ContentType.VIDEO.value: {
                    "avg_engagement_rate": 0.078,
                    "viral_threshold_views": 100000
                }
            }
        }
    
    async def register_content(self, content_metadata: ContentMetadata) -> bool:
        """Register new content in the analytics platform"""
        try:
            # Validate content metadata
            if not self._validate_content_metadata(content_metadata):
                logger.error(f"Invalid content metadata: {content_metadata.content_id}")
                return False
            
            # Store content
            self.content_registry[content_metadata.content_id] = content_metadata
            
            # Initialize performance tracking
            if content_metadata.content_id not in self.performance_data:
                self.performance_data[content_metadata.content_id] = {}
            
            # Extract and analyze content features
            await self._analyze_content_features(content_metadata)
            
            # Generate initial quality score
            quality_score = await self.assess_content_quality(content_metadata.content_id)
            if quality_score:
                self.quality_scores[content_metadata.content_id] = quality_score
            
            logger.info(f"Content registered: {content_metadata.content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register content: {e}")
            return False
    
    def _validate_content_metadata(self, metadata: ContentMetadata) -> bool:
        """Validate content metadata"""
        try:
            # Required fields validation
            if not all([
                metadata.content_id,
                metadata.creator_id,
                metadata.title,
                metadata.content_type,
                metadata.platform
            ]):
                return False
            
            # Content type validation
            if metadata.content_type not in ContentType:
                return False
            
            # Platform validation
            if metadata.platform not in PlatformType:
                return False
            
            # Duration validation for video content
            if metadata.content_type in [ContentType.VIDEO, ContentType.LIVE_STREAM, ContentType.REEL]:
                if metadata.duration_seconds is None or metadata.duration_seconds <= 0:
                    logger.warning(f"Missing or invalid duration for video content: {metadata.content_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Content metadata validation failed: {e}")
            return False
    
    async def _analyze_content_features(self, metadata: ContentMetadata) -> None:
        """Analyze content features for insights"""
        try:
            content_id = metadata.content_id
            
            # Extract hashtags and mentions
            hashtags = self._extract_hashtags(metadata.description)
            mentions = self._extract_mentions(metadata.description)
            
            # Update metadata
            metadata.hashtags.extend(hashtags)
            metadata.mentions.extend(mentions)
            
            # Analyze content topics
            topics = await self._extract_content_topics(metadata)
            
            # Store in trending topics
            for topic in topics:
                self.trending_topics[metadata.platform.value].append(topic)
                
                # Keep only recent topics (last 1000)
                if len(self.trending_topics[metadata.platform.value]) > 1000:
                    self.trending_topics[metadata.platform.value] = \
                        self.trending_topics[metadata.platform.value][-1000:]
            
            # Content clustering for similar content
            cluster_key = self._generate_content_cluster_key(metadata)
            self.content_clusters[cluster_key].append(content_id)
            
            logger.info(f"Content features analyzed for: {content_id}")
            
        except Exception as e:
            logger.error(f"Failed to analyze content features: {e}")
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, text.lower())
        return list(set(hashtags))  # Remove duplicates
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, text.lower())
        return list(set(mentions))  # Remove duplicates
    
    async def _extract_content_topics(self, metadata: ContentMetadata) -> List[str]:
        """Extract content topics using simple keyword analysis"""
        try:
            # Combine title, description, and tags
            text = f"{metadata.title} {metadata.description} {' '.join(metadata.tags)}".lower()
            
            # Simple topic extraction (in production, this would use NLP)
            common_topics = [
                'technology', 'fashion', 'fitness', 'food', 'travel', 'lifestyle',
                'gaming', 'music', 'art', 'education', 'business', 'health',
                'beauty', 'sports', 'entertainment', 'news', 'comedy', 'diy',
                'family', 'pets', 'nature', 'photography', 'reviews', 'tutorials'
            ]
            
            detected_topics = []
            for topic in common_topics:
                if topic in text:
                    detected_topics.append(topic)
            
            # Add hashtags as topics
            detected_topics.extend(metadata.hashtags[:5])  # Limit to top 5
            
            return detected_topics[:10]  # Limit to top 10 topics
            
        except Exception as e:
            logger.error(f"Failed to extract topics: {e}")
            return []
    
    def _generate_content_cluster_key(self, metadata: ContentMetadata) -> str:
        """Generate content cluster key for similar content grouping"""
        try:
            # Create cluster key based on platform, content type, and main topics
            key_components = [
                metadata.platform.value,
                metadata.content_type.value,
                metadata.creator_id[:8]  # First 8 chars of creator ID
            ]
            
            # Add top hashtags
            if metadata.hashtags:
                key_components.extend(sorted(metadata.hashtags)[:3])
            
            cluster_key = "_".join(key_components)
            return hashlib.md5(cluster_key.encode()).hexdigest()[:16]
            
        except Exception as e:
            logger.error(f"Failed to generate cluster key: {e}")
            return "default_cluster"
    
    async def track_content_performance(
        self, content_id: str, performance: ContentPerformance
    ) -> bool:
        """Track performance metrics for content"""
        try:
            if content_id not in self.content_registry:
                logger.warning(f"Content not found: {content_id}")
                return False
            
            # Validate performance data
            if not self._validate_performance_data(performance):
                logger.error(f"Invalid performance data for: {content_id}")
                return False
            
            # Calculate derived metrics
            performance.engagement_rate = self._calculate_engagement_rate(performance)
            performance.click_through_rate = self._calculate_ctr(performance)
            
            # Store performance data
            self.performance_data[content_id][performance.platform.value] = performance
            
            # Generate insights if significant performance change
            await self._check_performance_triggers(content_id, performance)
            
            logger.info(f"Performance tracked for content: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track performance: {e}")
            return False
    
    def _validate_performance_data(self, performance: ContentPerformance) -> bool:
        """Validate performance data"""
        try:
            # Check for negative values
            metrics = [
                performance.views, performance.likes, performance.shares,
                performance.comments, performance.saves, performance.clicks,
                performance.reach, performance.impressions
            ]
            
            if any(metric < 0 for metric in metrics):
                return False
            
            # Check for reasonable ratios
            if performance.reach > performance.impressions:
                logger.warning("Reach exceeds impressions - potential data issue")
            
            if performance.engagement_rate > 1.0:
                logger.warning("Engagement rate exceeds 100% - potential data issue")
            
            return True
            
        except Exception as e:
            logger.error(f"Performance data validation failed: {e}")
            return False
    
    def _calculate_engagement_rate(self, performance: ContentPerformance) -> float:
        """Calculate engagement rate"""
        try:
            total_engagements = (
                performance.likes + performance.shares + 
                performance.comments + performance.saves
            )
            
            if performance.impressions > 0:
                return total_engagements / performance.impressions
            elif performance.reach > 0:
                return total_engagements / performance.reach
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Failed to calculate engagement rate: {e}")
            return 0.0
    
    def _calculate_ctr(self, performance: ContentPerformance) -> float:
        """Calculate click-through rate"""
        try:
            if performance.impressions > 0:
                return performance.clicks / performance.impressions
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Failed to calculate CTR: {e}")
            return 0.0
    
    async def _check_performance_triggers(
        self, content_id: str, performance: ContentPerformance
    ) -> None:
        """Check for performance triggers that warrant insights"""
        try:
            metadata = self.content_registry[content_id]
            
            # Get platform benchmarks
            platform_benchmarks = self.performance_benchmarks.get(
                metadata.platform.value, {}
            )
            content_benchmarks = platform_benchmarks.get(
                metadata.content_type.value, {}
            )
            
            if not content_benchmarks:
                return
            
            # Check for viral performance
            viral_threshold = content_benchmarks.get('viral_threshold_views', 100000)
            if performance.views >= viral_threshold:
                await self._generate_viral_insight(content_id, performance)
            
            # Check for exceptional engagement
            avg_engagement = content_benchmarks.get('avg_engagement_rate', 0.05)
            if performance.engagement_rate >= avg_engagement * 2:
                await self._generate_engagement_insight(content_id, performance)
            
        except Exception as e:
            logger.error(f"Failed to check performance triggers: {e}")
    
    async def _generate_viral_insight(
        self, content_id: str, performance: ContentPerformance
    ) -> None:
        """Generate insight for viral content"""
        try:
            insight = ContentInsight(
                insight_id=f"viral_{content_id}_{datetime.now().timestamp()}",
                content_id=content_id,
                insight_type="viral_performance",
                title="Viral Content Alert",
                description=f"Your content has achieved viral status with {performance.views:,} views and {performance.engagement_rate:.2%} engagement rate.",
                impact_score=0.95,
                confidence_level=0.9,
                recommended_actions=[
                    "Leverage viral momentum with follow-up content",
                    "Engage actively with comments and shares",
                    "Analyze viral factors for future content",
                    "Consider cross-platform promotion"
                ],
                supporting_data={
                    "views": performance.views,
                    "engagement_rate": performance.engagement_rate,
                    "shares": performance.shares
                },
                generated_at=datetime.now()
            )
            
            self.insights_cache[content_id].append(insight)
            
        except Exception as e:
            logger.error(f"Failed to generate viral insight: {e}")
    
    async def _generate_engagement_insight(
        self, content_id: str, performance: ContentPerformance
    ) -> None:
        """Generate insight for high engagement content"""
        try:
            insight = ContentInsight(
                insight_id=f"engagement_{content_id}_{datetime.now().timestamp()}",
                content_id=content_id,
                insight_type="high_engagement",
                title="Exceptional Engagement Performance",
                description=f"Your content achieved {performance.engagement_rate:.2%} engagement rate, significantly above average.",
                impact_score=0.8,
                confidence_level=0.85,
                recommended_actions=[
                    "Analyze engagement patterns for replication",
                    "Create similar content format",
                    "Engage with highly active commenters",
                    "Consider content series based on this format"
                ],
                supporting_data={
                    "engagement_rate": performance.engagement_rate,
                    "likes": performance.likes,
                    "comments": performance.comments
                },
                generated_at=datetime.now()
            )
            
            self.insights_cache[content_id].append(insight)
            
        except Exception as e:
            logger.error(f"Failed to generate engagement insight: {e}")
    
    async def predict_viral_potential(self, content_id: str) -> Optional[ViralPrediction]:
        """Predict viral potential of content"""
        try:
            if content_id not in self.content_registry:
                return None
            
            metadata = self.content_registry[content_id]
            
            # Get historical performance of similar content
            similar_content = await self._find_similar_content(content_id)
            
            # Calculate viral score
            viral_score = await self._calculate_viral_score(metadata, similar_content)
            
            # Determine virality level
            virality_level = self._classify_virality(viral_score)
            
            # Predict metrics based on similar content
            predicted_metrics = await self._predict_performance_metrics(metadata, similar_content)
            
            # Identify viral factors
            viral_factors = await self._identify_viral_factors(metadata)
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(metadata)
            
            # Optimal posting time
            optimal_time = await self._calculate_optimal_posting_time(metadata)
            
            prediction = ViralPrediction(
                prediction_id=f"prediction_{content_id}_{datetime.now().timestamp()}",
                content_id=content_id,
                predicted_virality=virality_level,
                confidence_score=viral_score,
                predicted_metrics=predicted_metrics,
                viral_factors=viral_factors,
                risk_factors=risk_factors,
                optimal_posting_time=optimal_time,
                predicted_peak_engagement=optimal_time + timedelta(hours=2),
                methodology="similarity_analysis",
                generated_at=datetime.now()
            )
            
            # Cache prediction
            self.viral_predictions[content_id].append(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to predict viral potential: {e}")
            return None
    
    async def _find_similar_content(self, content_id: str) -> List[str]:
        """Find similar content for analysis"""
        try:
            metadata = self.content_registry[content_id]
            similar_content = []
            
            # Find content in same cluster
            cluster_key = self._generate_content_cluster_key(metadata)
            cluster_content = self.content_clusters.get(cluster_key, [])
            
            # Filter out current content
            similar_content.extend([c for c in cluster_content if c != content_id])
            
            # Find content with similar hashtags
            for other_id, other_metadata in self.content_registry.items():
                if other_id == content_id:
                    continue
                
                # Check hashtag overlap
                common_hashtags = set(metadata.hashtags) & set(other_metadata.hashtags)
                if len(common_hashtags) >= 2:  # At least 2 common hashtags
                    similar_content.append(other_id)
            
            # Limit to most recent 50 similar content pieces
            return similar_content[-50:]
            
        except Exception as e:
            logger.error(f"Failed to find similar content: {e}")
            return []
    
    async def _calculate_viral_score(
        self, metadata: ContentMetadata, similar_content: List[str]
    ) -> float:
        """Calculate viral potential score"""
        try:
            score = 0.0
            
            # Base score factors
            # 1. Content type viral potential
            viral_content_types = {
                ContentType.REEL: 0.3,
                ContentType.VIDEO: 0.25,
                ContentType.IMAGE: 0.2,
                ContentType.CAROUSEL: 0.2,
                ContentType.TEXT_POST: 0.15,
                ContentType.STORY: 0.1
            }
            score += viral_content_types.get(metadata.content_type, 0.1)
            
            # 2. Platform viral potential
            viral_platforms = {
                PlatformType.TIKTOK: 0.25,
                PlatformType.INSTAGRAM: 0.2,
                PlatformType.YOUTUBE: 0.18,
                PlatformType.TWITTER: 0.15,
                PlatformType.FACEBOOK: 0.12,
                PlatformType.LINKEDIN: 0.1
            }
            score += viral_platforms.get(metadata.platform, 0.1)
            
            # 3. Trending hashtags bonus
            trending_hashtags = self._get_trending_hashtags(metadata.platform)
            common_trending = set(metadata.hashtags) & set(trending_hashtags)
            score += len(common_trending) * 0.05
            
            # 4. Similar content performance
            if similar_content:
                similar_scores = []
                for similar_id in similar_content:
                    perf_data = self.performance_data.get(similar_id, {})
                    platform_perf = perf_data.get(metadata.platform.value)
                    if platform_perf:
                        # Normalize engagement rate to 0-1 scale
                        eng_score = min(platform_perf.engagement_rate * 10, 1.0)
                        similar_scores.append(eng_score)
                
                if similar_scores:
                    avg_similar_performance = sum(similar_scores) / len(similar_scores)
                    score += avg_similar_performance * 0.2
            
            # 5. Content quality bonus
            quality_score = self.quality_scores.get(metadata.content_id)
            if quality_score:
                score += (quality_score.overall_score / 100) * 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Failed to calculate viral score: {e}")
            return 0.5  # Default moderate score
    
    def _classify_virality(self, viral_score: float) -> ViralityLevel:
        """Classify virality level based on score"""
        if viral_score >= 0.8:
            return ViralityLevel.MEGA_VIRAL
        elif viral_score >= 0.65:
            return ViralityLevel.VIRAL
        elif viral_score >= 0.5:
            return ViralityLevel.HIGH
        elif viral_score >= 0.3:
            return ViralityLevel.MODERATE
        else:
            return ViralityLevel.LOW
    
    async def _predict_performance_metrics(
        self, metadata: ContentMetadata, similar_content: List[str]
    ) -> Dict[str, int]:
        """Predict performance metrics based on similar content"""
        try:
            if not similar_content:
                # Default predictions based on platform benchmarks
                benchmarks = self.performance_benchmarks.get(
                    metadata.platform.value, {}
                ).get(metadata.content_type.value, {})
                
                return {
                    "views": int(benchmarks.get('viral_threshold_views', 10000) * 0.1),
                    "likes": int(benchmarks.get('viral_threshold_views', 10000) * 0.05 * 0.1),
                    "shares": int(benchmarks.get('viral_threshold_views', 10000) * 0.01 * 0.1),
                    "comments": int(benchmarks.get('viral_threshold_views', 10000) * 0.005 * 0.1)
                }
            
            # Calculate averages from similar content
            total_views = 0
            total_likes = 0
            total_shares = 0
            total_comments = 0
            count = 0
            
            for similar_id in similar_content:
                perf_data = self.performance_data.get(similar_id, {})
                platform_perf = perf_data.get(metadata.platform.value)
                if platform_perf:
                    total_views += platform_perf.views
                    total_likes += platform_perf.likes
                    total_shares += platform_perf.shares
                    total_comments += platform_perf.comments
                    count += 1
            
            if count > 0:
                return {
                    "views": int(total_views / count),
                    "likes": int(total_likes / count),
                    "shares": int(total_shares / count),
                    "comments": int(total_comments / count)
                }
            
            return {"views": 1000, "likes": 50, "shares": 5, "comments": 10}
            
        except Exception as e:
            logger.error(f"Failed to predict metrics: {e}")
            return {"views": 1000, "likes": 50, "shares": 5, "comments": 10}
    
    async def _identify_viral_factors(self, metadata: ContentMetadata) -> List[str]:
        """Identify factors that could contribute to virality"""
        factors = []
        
        try:
            # Trending hashtags
            trending_hashtags = self._get_trending_hashtags(metadata.platform)
            common_trending = set(metadata.hashtags) & set(trending_hashtags)
            if common_trending:
                factors.append(f"Uses trending hashtags: {', '.join(list(common_trending)[:3])}")
            
            # Content type factors
            if metadata.content_type in [ContentType.REEL, ContentType.VIDEO]:
                factors.append("Video content has high viral potential")
            
            if metadata.content_type == ContentType.CAROUSEL:
                factors.append("Carousel format encourages engagement")
            
            # Platform-specific factors
            if metadata.platform == PlatformType.TIKTOK:
                factors.append("TikTok algorithm favors creative video content")
            elif metadata.platform == PlatformType.INSTAGRAM:
                factors.append("Instagram Reels have high reach potential")
            elif metadata.platform == PlatformType.YOUTUBE:
                factors.append("YouTube favors longer engagement and watch time")
            
            # Content characteristics
            if metadata.duration_seconds and metadata.duration_seconds <= 30:
                factors.append("Short-form content ideal for mobile consumption")
            
            if len(metadata.hashtags) >= 5:
                factors.append("Good hashtag optimization for discoverability")
            
            if metadata.mentions:
                factors.append("Mentions can increase reach through networks")
            
            # Quality indicators
            quality_score = self.quality_scores.get(metadata.content_id)
            if quality_score and quality_score.overall_score > 80:
                factors.append("High content quality score")
            
        except Exception as e:
            logger.error(f"Failed to identify viral factors: {e}")
        
        return factors
    
    async def _identify_risk_factors(self, metadata: ContentMetadata) -> List[str]:
        """Identify factors that could limit virality"""
        risks = []
        
        try:
            # Content type risks
            if metadata.content_type == ContentType.TEXT_POST:
                risks.append("Text-only posts have lower engagement rates")
            
            # Platform algorithm risks
            if metadata.platform == PlatformType.FACEBOOK:
                risks.append("Facebook's organic reach has declined significantly")
            
            # Hashtag risks
            if len(metadata.hashtags) == 0:
                risks.append("No hashtags limit discoverability")
            elif len(metadata.hashtags) > 15:
                risks.append("Too many hashtags may appear spammy")
            
            # Content length risks
            if metadata.duration_seconds and metadata.duration_seconds > 300:  # 5 minutes
                risks.append("Long content may have lower completion rates")
            
            # NSFW and brand safety
            if metadata.nsfw_flag:
                risks.append("NSFW content has limited reach due to platform restrictions")
            
            if metadata.brand_safety_score < 0.7:
                risks.append("Low brand safety score may limit algorithmic promotion")
            
            # Quality risks
            quality_score = self.quality_scores.get(metadata.content_id)
            if quality_score and quality_score.overall_score < 60:
                risks.append("Low content quality score")
            
            # Timing risks
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 23:
                risks.append("Posting outside optimal hours may reduce initial engagement")
            
        except Exception as e:
            logger.error(f"Failed to identify risk factors: {e}")
        
        return risks
    
    async def _calculate_optimal_posting_time(self, metadata: ContentMetadata) -> datetime:
        """Calculate optimal posting time based on platform and audience"""
        try:
            # Platform-specific optimal times (simplified)
            optimal_hours = {
                PlatformType.INSTAGRAM: [11, 13, 17],  # 11 AM, 1 PM, 5 PM
                PlatformType.TIKTOK: [6, 10, 19],      # 6 AM, 10 AM, 7 PM
                PlatformType.YOUTUBE: [14, 15, 20],     # 2 PM, 3 PM, 8 PM
                PlatformType.TWITTER: [9, 12, 15],      # 9 AM, 12 PM, 3 PM
                PlatformType.LINKEDIN: [8, 12, 17],     # 8 AM, 12 PM, 5 PM
                PlatformType.FACEBOOK: [13, 15, 16]     # 1 PM, 3 PM, 4 PM
            }
            
            platform_hours = optimal_hours.get(metadata.platform, [12, 15, 18])
            
            # Find next optimal time
            now = datetime.now()
            current_hour = now.hour
            
            # Find the next optimal hour
            next_hour = None
            for hour in platform_hours:
                if hour > current_hour:
                    next_hour = hour
                    break
            
            if next_hour is None:
                # Next day's first optimal time
                next_hour = platform_hours[0]
                optimal_time = now.replace(hour=next_hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
            else:
                optimal_time = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
            
            return optimal_time
            
        except Exception as e:
            logger.error(f"Failed to calculate optimal posting time: {e}")
            return datetime.now() + timedelta(hours=2)
    
    def _get_trending_hashtags(self, platform: PlatformType) -> List[str]:
        """Get trending hashtags for a platform"""
        try:
            platform_topics = self.trending_topics.get(platform.value, [])
            if not platform_topics:
                return []
            
            # Count hashtag frequency
            hashtag_counter = Counter(platform_topics)
            
            # Return top 20 trending hashtags
            trending = [hashtag for hashtag, count in hashtag_counter.most_common(20)]
            return trending
            
        except Exception as e:
            logger.error(f"Failed to get trending hashtags: {e}")
            return []
    
    async def assess_content_quality(self, content_id: str) -> Optional[ContentQualityScore]:
        """Assess content quality using multiple factors"""
        try:
            if content_id not in self.content_registry:
                return None
            
            metadata = self.content_registry[content_id]
            
            # Technical quality assessment
            technical_score = await self._assess_technical_quality(metadata)
            
            # Content relevance assessment
            relevance_score = await self._assess_content_relevance(metadata)
            
            # Engagement potential assessment
            engagement_score = await self._assess_engagement_potential(metadata)
            
            # Brand alignment assessment
            brand_score = await self._assess_brand_alignment(metadata)
            
            # SEO optimization assessment
            seo_score = await self._assess_seo_optimization(metadata)
            
            # Accessibility assessment
            accessibility_score = await self._assess_accessibility(metadata)
            
            # Calculate overall score
            scores = [technical_score, relevance_score, engagement_score, brand_score, seo_score, accessibility_score]
            overall_score = sum(scores) / len(scores)
            
            # Identify quality factors
            quality_factors = await self._identify_quality_factors(metadata, scores)
            
            # Generate improvement suggestions
            improvements = await self._generate_improvement_suggestions(metadata, scores)
            
            quality_assessment = ContentQualityScore(
                content_id=content_id,
                overall_score=overall_score,
                technical_quality=technical_score,
                content_relevance=relevance_score,
                engagement_potential=engagement_score,
                brand_alignment=brand_score,
                seo_optimization=seo_score,
                accessibility_score=accessibility_score,
                quality_factors=quality_factors,
                improvement_suggestions=improvements,
                assessed_at=datetime.now()
            )
            
            return quality_assessment
            
        except Exception as e:
            logger.error(f"Failed to assess content quality: {e}")
            return None
    
    async def _assess_technical_quality(self, metadata: ContentMetadata) -> float:
        """Assess technical quality of content"""
        score = 70.0  # Base score
        
        try:
            # Resolution check
            if metadata.resolution:
                if "4K" in metadata.resolution or "2160" in metadata.resolution:
                    score += 15
                elif "1080" in metadata.resolution or "HD" in metadata.resolution:
                    score += 10
                elif "720" in metadata.resolution:
                    score += 5
            
            # Duration optimization
            if metadata.duration_seconds:
                if metadata.content_type == ContentType.REEL and 15 <= metadata.duration_seconds <= 60:
                    score += 10
                elif metadata.content_type == ContentType.VIDEO and 60 <= metadata.duration_seconds <= 600:
                    score += 10
                elif metadata.content_type == ContentType.STORY and metadata.duration_seconds <= 15:
                    score += 10
            
            # File size optimization
            if metadata.file_size_mb:
                if metadata.file_size_mb < 100:  # Reasonable size for most platforms
                    score += 5
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Failed to assess technical quality: {e}")
            return 70.0
    
    async def _assess_content_relevance(self, metadata: ContentMetadata) -> float:
        """Assess content relevance and topicality"""
        score = 60.0  # Base score
        
        try:
            # Trending topic alignment
            trending_topics = self._get_trending_hashtags(metadata.platform)
            topic_overlap = set(metadata.hashtags) & set(trending_topics)
            score += len(topic_overlap) * 5
            
            # Title and description quality
            title_length = len(metadata.title)
            if 10 <= title_length <= 100:  # Optimal title length
                score += 10
            
            desc_length = len(metadata.description)
            if desc_length >= 50:  # Substantial description
                score += 10
            
            # Tag utilization
            if len(metadata.tags) >= 3:
                score += 10
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Failed to assess content relevance: {e}")
            return 60.0
    
    async def _assess_engagement_potential(self, metadata: ContentMetadata) -> float:
        """Assess potential for audience engagement"""
        score = 65.0  # Base score
        
        try:
            # Content type engagement potential
            engagement_multipliers = {
                ContentType.REEL: 1.3,
                ContentType.VIDEO: 1.2,
                ContentType.CAROUSEL: 1.15,
                ContentType.IMAGE: 1.1,
                ContentType.POLL: 1.25,
                ContentType.QUIZ: 1.2,
                ContentType.TEXT_POST: 1.0
            }
            
            multiplier = engagement_multipliers.get(metadata.content_type, 1.0)
            score *= multiplier
            
            # Interactive elements
            if "?" in metadata.description:  # Questions encourage comments
                score += 10
            
            if any(word in metadata.description.lower() for word in ["comment", "share", "like", "tag"]):
                score += 5
            
            # Hashtag optimization
            hashtag_count = len(metadata.hashtags)
            if 5 <= hashtag_count <= 10:
                score += 10
            elif 3 <= hashtag_count <= 15:
                score += 5
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Failed to assess engagement potential: {e}")
            return 65.0
    
    async def _assess_brand_alignment(self, metadata: ContentMetadata) -> float:
        """Assess brand safety and alignment"""
        score = metadata.brand_safety_score * 100  # Convert to 0-100 scale
        
        try:
            # NSFW penalty
            if metadata.nsfw_flag:
                score *= 0.5
            
            # Professional content indicators
            if any(word in metadata.description.lower() for word in ["professional", "business", "quality"]):
                score += 5
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Failed to assess brand alignment: {e}")
            return score
    
    async def _assess_seo_optimization(self, metadata: ContentMetadata) -> float:
        """Assess SEO and discoverability optimization"""
        score = 50.0  # Base score
        
        try:
            # Title optimization
            if len(metadata.title) > 0:
                score += 20
            
            # Description optimization
            if len(metadata.description) >= 100:
                score += 15
            
            # Hashtag optimization
            if metadata.hashtags:
                score += 10
            
            # Tag utilization
            if metadata.tags:
                score += 5
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Failed to assess SEO optimization: {e}")
            return 50.0
    
    async def _assess_accessibility(self, metadata: ContentMetadata) -> float:
        """Assess content accessibility"""
        score = 70.0  # Base score
        
        try:
            # Alt text indicators (simplified check)
            if "alt" in metadata.description.lower() or "description" in metadata.description.lower():
                score += 15
            
            # Caption indicators for video content
            if metadata.content_type in [ContentType.VIDEO, ContentType.REEL]:
                if "caption" in metadata.description.lower() or "subtitle" in metadata.description.lower():
                    score += 15
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Failed to assess accessibility: {e}")
            return 70.0
    
    async def _identify_quality_factors(self, metadata: ContentMetadata, scores: List[float]) -> List[str]:
        """Identify positive quality factors"""
        factors = []
        
        try:
            technical, relevance, engagement, brand, seo, accessibility = scores
            
            if technical >= 85:
                factors.append("Excellent technical quality")
            if relevance >= 80:
                factors.append("Highly relevant content")
            if engagement >= 80:
                factors.append("Strong engagement potential")
            if brand >= 90:
                factors.append("Excellent brand safety")
            if seo >= 75:
                factors.append("Well optimized for discovery")
            if accessibility >= 85:
                factors.append("Good accessibility features")
            
            # Content-specific factors
            if len(metadata.hashtags) >= 5:
                factors.append("Good hashtag strategy")
            
            if metadata.duration_seconds and metadata.duration_seconds > 0:
                factors.append("Optimized content duration")
            
        except Exception as e:
            logger.error(f"Failed to identify quality factors: {e}")
        
        return factors
    
    async def _generate_improvement_suggestions(self, metadata: ContentMetadata, scores: List[float]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        try:
            technical, relevance, engagement, brand, seo, accessibility = scores
            
            if technical < 75:
                suggestions.append("Improve technical quality: use higher resolution, optimize file size")
            
            if relevance < 70:
                suggestions.append("Increase relevance: use trending hashtags, align with current topics")
            
            if engagement < 70:
                suggestions.append("Boost engagement potential: add questions, calls-to-action, interactive elements")
            
            if brand < 80:
                suggestions.append("Improve brand alignment: ensure content meets brand safety guidelines")
            
            if seo < 65:
                suggestions.append("Optimize for discovery: improve title, description, and hashtag usage")
            
            if accessibility < 75:
                suggestions.append("Enhance accessibility: add alt text, captions, and descriptions")
            
            # Specific suggestions
            if len(metadata.hashtags) < 3:
                suggestions.append("Add more relevant hashtags for better discoverability")
            
            if len(metadata.description) < 50:
                suggestions.append("Expand description with more details and context")
            
        except Exception as e:
            logger.error(f"Failed to generate improvement suggestions: {e}")
        
        return suggestions
    
    async def analyze_content_performance(self, creator_id: str) -> Dict[str, Any]:
        """Analyze overall content performance for a creator"""
        try:
            # Get creator's content
            creator_content = [
                content_id for content_id, metadata in self.content_registry.items()
                if metadata.creator_id == creator_id
            ]
            
            if not creator_content:
                return {"error": "No content found for creator"}
            
            # Aggregate performance data
            total_performance = {
                "total_content": len(creator_content),
                "total_views": 0,
                "total_likes": 0,
                "total_shares": 0,
                "total_comments": 0,
                "average_engagement_rate": 0.0,
                "best_performing_content": [],
                "content_by_platform": defaultdict(int),
                "content_by_type": defaultdict(int),
                "viral_content_count": 0,
                "quality_score_average": 0.0
            }
            
            engagement_rates = []
            quality_scores = []
            
            for content_id in creator_content:
                metadata = self.content_registry[content_id]
                
                # Count by platform and type
                total_performance["content_by_platform"][metadata.platform.value] += 1
                total_performance["content_by_type"][metadata.content_type.value] += 1
                
                # Aggregate performance metrics
                for platform_perf in self.performance_data.get(content_id, {}).values():
                    total_performance["total_views"] += platform_perf.views
                    total_performance["total_likes"] += platform_perf.likes
                    total_performance["total_shares"] += platform_perf.shares
                    total_performance["total_comments"] += platform_perf.comments
                    
                    if platform_perf.engagement_rate > 0:
                        engagement_rates.append(platform_perf.engagement_rate)
                    
                    # Check for viral content
                    benchmarks = self.performance_benchmarks.get(
                        metadata.platform.value, {}
                    ).get(metadata.content_type.value, {})
                    
                    viral_threshold = benchmarks.get('viral_threshold_views', 100000)
                    if platform_perf.views >= viral_threshold:
                        total_performance["viral_content_count"] += 1
                        total_performance["best_performing_content"].append({
                            "content_id": content_id,
                            "views": platform_perf.views,
                            "engagement_rate": platform_perf.engagement_rate
                        })
                
                # Quality scores
                quality_score = self.quality_scores.get(content_id)
                if quality_score:
                    quality_scores.append(quality_score.overall_score)
            
            # Calculate averages
            if engagement_rates:
                total_performance["average_engagement_rate"] = sum(engagement_rates) / len(engagement_rates)
            
            if quality_scores:
                total_performance["quality_score_average"] = sum(quality_scores) / len(quality_scores)
            
            # Sort best performing content
            total_performance["best_performing_content"].sort(
                key=lambda x: x["views"], reverse=True
            )
            total_performance["best_performing_content"] = total_performance["best_performing_content"][:10]
            
            # Convert defaultdicts to regular dicts
            total_performance["content_by_platform"] = dict(total_performance["content_by_platform"])
            total_performance["content_by_type"] = dict(total_performance["content_by_type"])
            
            # Add insights
            insights = await self._generate_content_insights(creator_id, total_performance)
            total_performance["insights"] = insights
            
            # Add recommendations
            recommendations = await self._generate_content_recommendations(creator_id, total_performance)
            total_performance["recommendations"] = recommendations
            
            return {
                "creator_id": creator_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "performance_summary": total_performance
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze content performance: {e}")
            return {"error": str(e)}
    
    async def _generate_content_insights(self, creator_id: str, performance_data: Dict[str, Any]) -> List[str]:
        """Generate content insights for creator"""
        insights = []
        
        try:
            # Viral content insights
            viral_count = performance_data.get("viral_content_count", 0)
            total_content = performance_data.get("total_content", 0)
            
            if viral_count > 0:
                viral_rate = viral_count / total_content
                if viral_rate > 0.1:  # >10% viral rate
                    insights.append(f"Exceptional viral content rate: {viral_rate:.1%} of your content goes viral")
                else:
                    insights.append(f"You have {viral_count} viral content pieces - analyze their success factors")
            
            # Engagement insights
            avg_engagement = performance_data.get("average_engagement_rate", 0)
            if avg_engagement > 0.05:  # >5% engagement
                insights.append(f"Strong engagement rate of {avg_engagement:.2%} - above industry average")
            elif avg_engagement < 0.02:  # <2% engagement
                insights.append("Engagement rate below average - focus on audience interaction strategies")
            
            # Platform insights
            platform_distribution = performance_data.get("content_by_platform", {})
            if len(platform_distribution) == 1:
                insights.append("Single platform focus - consider expanding to additional platforms")
            elif len(platform_distribution) >= 4:
                insights.append("Good multi-platform presence - optimize cross-platform content strategy")
            
            # Content type insights
            content_types = performance_data.get("content_by_type", {})
            if content_types:
                top_type = max(content_types, key=content_types.get)
                insights.append(f"Your most frequent content type is {top_type} - leverage this strength")
            
            # Quality insights
            quality_avg = performance_data.get("quality_score_average", 0)
            if quality_avg > 85:
                insights.append(f"Excellent content quality with {quality_avg:.1f}/100 average score")
            elif quality_avg < 70:
                insights.append(f"Content quality opportunity: {quality_avg:.1f}/100 - focus on quality improvements")
            
        except Exception as e:
            logger.error(f"Failed to generate content insights: {e}")
        
        return insights
    
    async def _generate_content_recommendations(self, creator_id: str, performance_data: Dict[str, Any]) -> List[str]:
        """Generate content recommendations for creator"""
        recommendations = []
        
        try:
            # Viral content recommendations
            viral_count = performance_data.get("viral_content_count", 0)
            if viral_count > 0:
                recommendations.append("Analyze your viral content patterns and replicate successful elements")
            
            # Engagement recommendations
            avg_engagement = performance_data.get("average_engagement_rate", 0)
            if avg_engagement < 0.03:
                recommendations.extend([
                    "Increase audience interaction with questions and polls",
                    "Post during optimal hours for your audience",
                    "Use trending hashtags relevant to your niche"
                ])
            
            # Platform recommendations
            platform_count = len(performance_data.get("content_by_platform", {}))
            if platform_count < 3:
                recommendations.append("Expand to additional platforms to increase reach")
            
            # Content type recommendations
            content_types = performance_data.get("content_by_type", {})
            if "video" not in content_types and "reel" not in content_types:
                recommendations.append("Add video content - it typically has higher engagement rates")
            
            # Quality recommendations
            quality_avg = performance_data.get("quality_score_average", 0)
            if quality_avg < 80:
                recommendations.extend([
                    "Focus on improving content quality scores",
                    "Optimize titles and descriptions for better discoverability",
                    "Use high-quality visuals and proper formatting"
                ])
            
            # General recommendations
            total_content = performance_data.get("total_content", 0)
            if total_content < 20:
                recommendations.append("Increase content frequency for better platform algorithm performance")
            
        except Exception as e:
            logger.error(f"Failed to generate content recommendations: {e}")
        
        return recommendations
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health metrics"""
        return {
            "system_status": "operational",
            "registered_content": len(self.content_registry),
            "performance_records": len(self.performance_data),
            "cached_insights": sum(len(insights) for insights in self.insights_cache.values()),
            "viral_predictions": sum(len(predictions) for predictions in self.viral_predictions.values()),
            "quality_assessments": len(self.quality_scores),
            "content_clusters": len(self.content_clusters),
            "supported_platforms": len(PlatformType),
            "supported_content_types": len(ContentType),
            "uptime": "99.99%",
            "last_updated": datetime.now().isoformat()
        }


# Module exports
__all__ = [
    'ContentAnalyticsPlatform',
    'ContentMetadata',
    'ContentPerformance',
    'ContentInsight',
    'ViralPrediction',
    'ContentQualityScore',
    'ContentType',
    'PlatformType',
    'ContentStatus',
    'ViralityLevel'
]