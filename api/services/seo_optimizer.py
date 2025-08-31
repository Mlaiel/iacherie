"""Enterprise SEO Optimization Service - AI-Powered Content Discovery
Advanced keyword research, content optimization, and multi-platform SEO strategies

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + SEO Expert + Content Strategist + ML Engineer

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are proprietary to Fahed Mlaiel.
Unauthorized copying, distribution, or use without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
import json
from collections import Counter
import math

import redis
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from slugify import slugify
from textstat import flesch_reading_ease, flesch_kincaid_grade
import openai
from sqlalchemy.orm import Session

from backend.app.models.domain import ContentAsset, Creator, SEOMetrics, TrendingKeywords
from backend.app.core.exceptions import SEOError

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass


class Platform(Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    REDDIT = "reddit"


class SEOStrategy(Enum):
    VIRAL_OPTIMIZATION = "viral_optimization"
    NICHE_TARGETING = "niche_targeting"
    TRENDING_KEYWORDS = "trending_keywords"
    LONG_TAIL_SEO = "long_tail_seo"
    BRAND_BUILDING = "brand_building"


@dataclass
class SEOAnalysis:
    overall_score: float
    keyword_score: float
    content_score: float
    readability_score: float
    trending_score: float
    recommendations: List[str]
    optimized_title: str
    optimized_description: str
    target_keywords: List[str]
    hashtags: List[str]
    alt_text: str


@dataclass
class PlatformOptimization:
    platform: Platform
    optimized_title: str
    optimized_description: str
    hashtags: List[str]
    posting_schedule: List[str]
    audience_targeting: Dict[str, Any]
    engagement_tips: List[str]


@dataclass
class KeywordResearch:
    primary_keywords: List[str]
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    trending_keywords: List[str]
    competitor_keywords: List[str]
    search_volume: Dict[str, int]
    difficulty_scores: Dict[str, float]
    suggested_content_ideas: List[str]


class EnterpriseSEOOptimizerService:
    """    Professional SEO optimization service providing AI-powered content optimization,
    keyword research, and multi-platform SEO strategies
    """    
    # Platform-specific optimization parameters
    PLATFORM_CONFIGS = {
        Platform.YOUTUBE: {
            'title_length': 60,
            'description_length': 5000,
            'tags_limit': 15,
            'hashtags_limit': 15,
            'optimal_keywords': 3
        },
        Platform.INSTAGRAM: {
            'caption_length': 2200,
            'hashtags_limit': 30,
            'optimal_hashtags': 20,
            'story_text_limit': 100
        },
        Platform.TIKTOK: {
            'caption_length': 150,
            'hashtags_limit': 20,
            'optimal_hashtags': 10,
            'trending_focus': True
        },
        Platform.TWITTER: {
            'text_length': 280,
            'hashtags_limit': 10,
            'optimal_hashtags': 3,
            'trending_topics': True
        },
        Platform.FACEBOOK: {
            'text_length': 500,
            'title_length': 100,
            'hashtags_limit': 20,
            'link_optimization': True
        },
        Platform.LINKEDIN: {
            'post_length': 1300,
            'title_length': 120,
            'professional_tone': True,
            'industry_keywords': True
        }
    }
    
    # SEO scoring weights
    SEO_WEIGHTS = {
        'keyword_density': 0.25,
        'title_optimization': 0.20,
        'content_quality': 0.20,
        'trending_relevance': 0.15,
        'readability': 0.10,
        'metadata_completeness': 0.10
    }
    
    # Content type specific keywords
    CONTENT_TYPE_KEYWORDS = {
        'audio': ['music', 'sound', 'audio', 'track', 'song', 'podcast', 'voice', 'beat'],
        'video': ['video', 'clip', 'movie', 'film', 'content', 'watch', 'visual', 'cinematic'],
        'image': ['photo', 'image', 'picture', 'art', 'visual', 'design', 'creative', 'aesthetic'],
        'text': ['article', 'story', 'content', 'writing', 'blog', 'post', 'text', 'read']
    }
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.stemmer = PorterStemmer()
        
        # Initialize stop words
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        
        # SEO settings
        self.cache_ttl = 1800  # 30 minutes
        self.trending_keywords_cache = 3600  # 1 hour
        
        # AI models (would be properly initialized)
        self.openai_client = None  # Would initialize with API key

    async def analyze_content_seo(
        self,
        title: str,
        description: str = "",
        tags: List[str] = None,
        content_type: str = "text"
    ) -> SEOAnalysis:
        """        Comprehensive SEO analysis of content using AI algorithms
        """        try:
            tags = tags or []
            
            # Analyze different SEO components
            keyword_analysis = await self._analyze_keywords(title, description, tags, content_type)
            content_analysis = await self._analyze_content_quality(title, description)
            readability_analysis = await self._analyze_readability(title, description)
            trending_analysis = await self._analyze_trending_relevance(keyword_analysis['keywords'], content_type)
            
            # Calculate overall scores
            keyword_score = keyword_analysis['score']
            content_score = content_analysis['score']
            readability_score = readability_analysis['score']
            trending_score = trending_analysis['score']
            
            # Calculate weighted overall score
            overall_score = (
                keyword_score * self.SEO_WEIGHTS['keyword_density'] +
                content_score * self.SEO_WEIGHTS['content_quality'] +
                readability_score * self.SEO_WEIGHTS['readability'] +
                trending_score * self.SEO_WEIGHTS['trending_relevance'] +
                0.8 * self.SEO_WEIGHTS['title_optimization'] +  # Base title score
                0.7 * self.SEO_WEIGHTS['metadata_completeness']  # Base metadata score
            ) * 100
            
            # Generate optimized content
            optimized_title = await self._optimize_title(title, keyword_analysis['keywords'], content_type)
            optimized_description = await self._optimize_description(
                description, keyword_analysis['keywords'], content_type
            )
            
            # Generate hashtags and keywords
            target_keywords = keyword_analysis['keywords'][:10]
            hashtags = await self._generate_hashtags(target_keywords, trending_analysis['trending_keywords'])
            alt_text = await self._generate_alt_text(title, description, content_type)
            
            # Generate recommendations
            recommendations = await self._generate_seo_recommendations(
                keyword_score, content_score, readability_score, trending_score
            )
            
            analysis = SEOAnalysis(
                overall_score=round(overall_score, 2),
                keyword_score=round(keyword_score * 100, 2),
                content_score=round(content_score * 100, 2),
                readability_score=round(readability_score * 100, 2),
                trending_score=round(trending_score * 100, 2),
                recommendations=recommendations,
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                target_keywords=target_keywords,
                hashtags=hashtags,
                alt_text=alt_text
            )
            
            # Cache analysis
            await self._cache_seo_analysis(title, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {str(e)}")
            raise SEOError(f"Failed to analyze SEO: {str(e)}")

    async def _analyze_keywords(
        self,
        title: str,
        description: str,
        tags: List[str],
        content_type: str
    ) -> Dict[str, Any]:
        """Analyze and extract relevant keywords"""        
        # Combine all text
        all_text = f"{title} {description} {' '.join(tags)}".lower()
        
        # Tokenize and clean
        words = word_tokenize(all_text)
        words = [word for word in words if word.isalpha() and word not in self.stop_words and len(word) > 2]
        
        # Add content-type specific keywords
        content_keywords = self.CONTENT_TYPE_KEYWORDS.get(content_type, [])
        
        # Count word frequency
        word_freq = Counter(words)
        
        # Calculate TF-IDF like scores (simplified)
        total_words = len(words)
        keyword_scores = {}
        
        for word, count in word_freq.items():
            tf = count / total_words
            # Boost for content-type relevance
            boost = 2.0 if word in content_keywords else 1.0
            keyword_scores[word] = tf * boost
        
        # Sort by relevance
        top_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)[:20]
        keywords = [word for word, score in top_keywords]
        
        # Calculate keyword optimization score
        keyword_density = sum(count for count in word_freq.values()) / max(total_words, 1)
        content_type_coverage = len([w for w in keywords if w in content_keywords]) / len(content_keywords)
        
        score = min(1.0, (keyword_density * 0.5) + (content_type_coverage * 0.5))
        
        return {
            'keywords': keywords,
            'keyword_scores': dict(top_keywords),
            'keyword_density': keyword_density,
            'score': score
        }

    async def _analyze_content_quality(self, title: str, description: str) -> Dict[str, Any]:
        """Analyze content quality for SEO"""        
        quality_factors = []
        
        # Title quality
        if title:
            title_length = len(title)
            if 30 <= title_length <= 60:
                quality_factors.append(1.0)
            elif 20 <= title_length <= 80:
                quality_factors.append(0.8)
            else:
                quality_factors.append(0.6)
        else:
            quality_factors.append(0.2)
        
        # Description quality
        if description:
            desc_length = len(description)
            if 150 <= desc_length <= 300:
                quality_factors.append(1.0)
            elif 100 <= desc_length <= 500:
                quality_factors.append(0.8)
            else:
                quality_factors.append(0.6)
            
            # Check for call-to-action words
            cta_words = ['subscribe', 'like', 'share', 'follow', 'watch', 'listen', 'click', 'visit']
            has_cta = any(word in description.lower() for word in cta_words)
            quality_factors.append(1.0 if has_cta else 0.7)
        else:
            quality_factors.extend([0.3, 0.5])
        
        # Calculate overall quality score
        score = sum(quality_factors) / len(quality_factors) if quality_factors else 0.5
        
        return {
            'score': score,
            'title_quality': quality_factors[0] if quality_factors else 0.5,
            'description_quality': quality_factors[1] if len(quality_factors) > 1 else 0.5
        }

    async def _analyze_readability(self, title: str, description: str) -> Dict[str, Any]:
        """Analyze content readability"""        
        text = f"{title} {description}"
        
        if len(text.strip()) == 0:
            return {'score': 0.5, 'grade_level': 10, 'ease_score': 50}
        
        try:
            # Calculate readability scores
            ease_score = flesch_reading_ease(text)
            grade_level = flesch_kincaid_grade(text)
            
            # Normalize scores
            # Flesch Reading Ease: 60-70 is ideal for general audience
            if 60 <= ease_score <= 70:
                readability_score = 1.0
            elif 50 <= ease_score <= 80:
                readability_score = 0.8
            else:
                readability_score = 0.6
            
            # Penalize if too complex (grade level > 12)
            if grade_level > 12:
                readability_score *= 0.8
            
            return {
                'score': readability_score,
                'grade_level': grade_level,
                'ease_score': ease_score
            }
            
        except Exception as e:
            logger.warning(f"Readability analysis failed: {str(e)}")
            return {'score': 0.7, 'grade_level': 8, 'ease_score': 65}

    async def _analyze_trending_relevance(self, keywords: List[str], content_type: str) -> Dict[str, Any]:
        """Analyze trending relevance of keywords"""        
        # Get trending keywords from cache
        trending_keywords = await self._get_trending_keywords(content_type)
        
        # Calculate overlap with trending topics
        keyword_set = set(keywords[:10])  # Top 10 keywords
        trending_set = set(trending_keywords[:20])  # Top 20 trending
        
        overlap = len(keyword_set.intersection(trending_set))
        overlap_ratio = overlap / max(len(keyword_set), 1)
        
        # Boost score if using current trending topics
        trending_score = min(1.0, overlap_ratio * 2.0)  # Up to 100% if many overlaps
        
        return {
            'score': trending_score,
            'trending_keywords': list(trending_set),
            'overlap_count': overlap,
            'overlap_ratio': overlap_ratio
        }

    async def _get_trending_keywords(self, content_type: str) -> List[str]:
        """Get trending keywords for content type"""        
        cache_key = f"trending_keywords:{content_type}"
        cached = self.redis_client.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Generate trending keywords (would integrate with real trend APIs)
        trending_keywords = {
            'audio': ['viral', 'trending', 'remix', 'cover', 'original', 'beat', 'instrumental', 'vocals'],
            'video': ['viral', 'tutorial', 'review', 'vlog', 'shorts', 'trending', 'challenge', 'reaction'],
            'image': ['aesthetic', 'viral', 'trending', 'art', 'design', 'photography', 'creative', 'inspiration'],
            'text': ['viral', 'trending', 'tips', 'guide', 'story', 'news', 'opinion', 'analysis']
        }
        
        keywords = trending_keywords.get(content_type, trending_keywords['text'])
        
        # Cache trending keywords
        self.redis_client.setex(cache_key, self.trending_keywords_cache, json.dumps(keywords))
        
        return keywords

    async def _optimize_title(self, original_title: str, keywords: List[str], content_type: str) -> str:
        """Generate SEO-optimized title"""        
        if not original_title.strip():
            original_title = f"Amazing {content_type} content"
        
        # Ensure title includes primary keywords
        primary_keyword = keywords[0] if keywords else content_type
        
        # Check if primary keyword is already in title
        if primary_keyword.lower() not in original_title.lower():
            # Add keyword naturally
            if len(original_title) < 40:
                optimized = f"{primary_keyword.title()}: {original_title}"
            else:
                optimized = f"{original_title} - {primary_keyword.title()}"
        else:
            optimized = original_title
        
        # Ensure optimal length (50-60 characters for most platforms)
        if len(optimized) > 60:
            optimized = optimized[:57] + "..."
        
        # Add engaging elements
        engaging_words = ['Ultimate', 'Amazing', 'Epic', 'Best', 'Top', 'Must-See', 'Incredible']
        if not any(word.lower() in optimized.lower() for word in engaging_words) and len(optimized) < 50:
            optimized = f"Amazing {optimized}"
        
        return optimized

    async def _optimize_description(
        self,
        original_description: str,
        keywords: List[str],
        content_type: str
    ) -> str:
        """Generate SEO-optimized description"""        
        if not original_description.strip():
            original_description = f"High-quality {content_type} content created with passion."
        
        # Ensure keywords are included naturally
        primary_keywords = keywords[:3]
        description_lower = original_description.lower()
        
        missing_keywords = [kw for kw in primary_keywords if kw.lower() not in description_lower]
        
        if missing_keywords:
            keyword_phrase = ", ".join(missing_keywords)
            if len(original_description) < 200:
                optimized = f"{original_description}\n\nFeaturing: {keyword_phrase}"
            else:
                # Insert keywords naturally in the middle
                sentences = sent_tokenize(original_description)
                if len(sentences) > 1:
                    mid_point = len(sentences) // 2
                    sentences.insert(mid_point, f"This content focuses on {keyword_phrase}.")
                    optimized = " ".join(sentences)
                else:
                    optimized = original_description
        else:
            optimized = original_description
        
        # Add call-to-action if missing
        cta_words = ['subscribe', 'like', 'share', 'follow', 'watch', 'listen']
        if not any(word in optimized.lower() for word in cta_words):
            cta_suggestions = {
                'audio': "🎵 Listen and share your thoughts!",
                'video': "👍 Like and subscribe for more content!",
                'image': "💖 Like and follow for more amazing visuals!",
                'text': "📖 Read and share your thoughts in comments!"
            }
            cta = cta_suggestions.get(content_type, "👍 Like and share!")
            optimized = f"{optimized}\n\n{cta}"
        
        return optimized

    async def _generate_hashtags(self, keywords: List[str], trending_keywords: List[str]) -> List[str]:
        """Generate optimal hashtags from keywords"""        
        hashtags = []
        
        # Convert keywords to hashtags
        for keyword in keywords[:15]:  # Top 15 keywords
            # Clean and format hashtag
            hashtag = re.sub(r'[^a-zA-Z0-9]', '', keyword.title())
            if hashtag and len(hashtag) > 2:
                hashtags.append(f"#{hashtag}")
        
        # Add trending hashtags
        for trending in trending_keywords[:10]:
            hashtag = f"#{re.sub(r'[^a-zA-Z0-9]', '', trending.title())}"
            if hashtag not in hashtags and len(hashtag) > 3:
                hashtags.append(hashtag)
        
        # Add generic popular hashtags
        generic_hashtags = [
            "#Viral", "#Trending", "#Content", "#Creator", "#Original",
            "#Quality", "#Amazing", "#MustSee", "#Discover", "#Creative"
        ]
        
        for generic in generic_hashtags:
            if generic not in hashtags and len(hashtags) < 25:
                hashtags.append(generic)
        
        return hashtags[:30]  # Limit to 30 hashtags

    async def _generate_alt_text(self, title: str, description: str, content_type: str) -> str:
        """Generate SEO-optimized alt text"""        
        if content_type != 'image':
            return ""
        
        # Use title as base, add context from description
        alt_text = title[:50] if title else f"{content_type} content"
        
        # Add descriptive elements
        if description:
            # Extract descriptive words
            descriptive_words = ['colorful', 'beautiful', 'artistic', 'creative', 'stunning', 'amazing', 'unique']
            desc_lower = description.lower()
            found_descriptors = [word for word in descriptive_words if word in desc_lower]
            
            if found_descriptors:
                alt_text = f"{found_descriptors[0].title()} {alt_text}"
        
        # Ensure proper length (125 characters max for accessibility)
        if len(alt_text) > 125:
            alt_text = alt_text[:122] + "..."
        
        return alt_text

    async def _generate_seo_recommendations(
        self,
        keyword_score: float,
        content_score: float,
        readability_score: float,
        trending_score: float
    ) -> List[str]:
        """Generate personalized SEO recommendations"""        
        recommendations = []
        
        if keyword_score < 0.7:
            recommendations.append("Include more relevant keywords naturally in your title and description")
        
        if content_score < 0.7:
            recommendations.append("Improve title length (30-60 characters) and add engaging call-to-action")
        
        if readability_score < 0.6:
            recommendations.append("Simplify language for better readability and broader audience appeal")
        
        if trending_score < 0.5:
            recommendations.append("Incorporate current trending keywords to increase discoverability")
        
        # General best practices
        recommendations.extend([
            "Use relevant hashtags to improve content discovery",
            "Post during peak audience hours for maximum engagement",
            "Engage with comments to boost algorithmic performance"
        ])
        
        return recommendations[:7]  # Return top 7 recommendations

    async def optimize_for_platform(
        self,
        title: str,
        description: str,
        tags: List[str],
        platform: str
    ) -> PlatformOptimization:
        """        Optimize content for specific platform requirements
        """        try:
            platform_enum = Platform(platform.lower())
            config = self.PLATFORM_CONFIGS.get(platform_enum, {})
            
            # Get base SEO analysis
            seo_analysis = await self.analyze_content_seo(title, description, tags)
            
            # Platform-specific optimizations
            if platform_enum == Platform.YOUTUBE:
                optimized = await self._optimize_for_youtube(title, description, seo_analysis, config)
            elif platform_enum == Platform.INSTAGRAM:
                optimized = await self._optimize_for_instagram(title, description, seo_analysis, config)
            elif platform_enum == Platform.TIKTOK:
                optimized = await self._optimize_for_tiktok(title, description, seo_analysis, config)
            elif platform_enum == Platform.TWITTER:
                optimized = await self._optimize_for_twitter(title, description, seo_analysis, config)
            else:
                optimized = await self._optimize_for_generic_platform(title, description, seo_analysis, config)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Platform optimization failed: {str(e)}")
            raise SEOError(f"Failed to optimize for {platform}: {str(e)}")

    async def _optimize_for_youtube(
        self,
        title: str,
        description: str,
        seo_analysis: SEOAnalysis,
        config: Dict[str, Any]
    ) -> PlatformOptimization:
        """Optimize content for YouTube"""        
        # YouTube-specific title optimization
        yt_title = seo_analysis.optimized_title
        if len(yt_title) > config['title_length']:
            yt_title = yt_title[:config['title_length'] - 3] + "..."
        
        # YouTube-specific description with timestamps, links, etc.
        yt_description = f"{seo_analysis.optimized_description}\n\n"
        yt_description += "🔔 Subscribe for more content!\n"
        yt_description += "👍 Like if you enjoyed this video\n"
        yt_description += "💬 Comment your thoughts below\n\n"
        yt_description += f"Tags: {', '.join(seo_analysis.target_keywords[:10])}"
        
        # YouTube hashtags (limit 15)
        yt_hashtags = seo_analysis.hashtags[:config['hashtags_limit']]
        
        return PlatformOptimization(
            platform=Platform.YOUTUBE,
            optimized_title=yt_title,
            optimized_description=yt_description[:config['description_length']],
            hashtags=yt_hashtags,
            posting_schedule=["Tuesday 2 PM", "Friday 6 PM", "Sunday 10 AM"],
            audience_targeting={
                "demographics": "18-35",
                "interests": seo_analysis.target_keywords,
                "geographic": "global"
            },
            engagement_tips=[
                "Upload consistently 2-3 times per week",
                "Create eye-catching thumbnails",
                "Use end screens to promote other videos",
                "Engage with comments within first hour"
            ]
        )

    async def _optimize_for_instagram(
        self,
        title: str,
        description: str,
        seo_analysis: SEOAnalysis,
        config: Dict[str, Any]
    ) -> PlatformOptimization:
        """Optimize content for Instagram"""        
        # Instagram uses description as caption
        ig_caption = f"{seo_analysis.optimized_description}\n\n"
        ig_caption += "✨ Follow for more amazing content!\n"
        ig_caption += f"{' '.join(seo_analysis.hashtags[:config['optimal_hashtags']])}"
        
        # Instagram Stories optimization
        ig_title = title[:50] if len(title) > 50 else title
        
        return PlatformOptimization(
            platform=Platform.INSTAGRAM,
            optimized_title=ig_title,
            optimized_description=ig_caption[:config['caption_length']],
            hashtags=seo_analysis.hashtags[:config['hashtags_limit']],
            posting_schedule=["Monday 11 AM", "Wednesday 2 PM", "Saturday 9 AM"],
            audience_targeting={
                "demographics": "16-34",
                "interests": seo_analysis.target_keywords,
                "behavior": "visual_content_consumers"
            },
            engagement_tips=[
                "Post high-quality visuals consistently",
                "Use Instagram Stories daily",
                "Engage with followers' content",
                "Use location tags when relevant"
            ]
        )

    async def _optimize_for_tiktok(
        self,
        title: str,
        description: str,
        seo_analysis: SEOAnalysis,
        config: Dict[str, Any]
    ) -> PlatformOptimization:
        """Optimize content for TikTok"""        
        # TikTok prefers short, punchy descriptions
        tt_description = title[:100] if len(title) <= 100 else f"{title[:97]}..."
        
        # Add trending hashtags for TikTok
        trending_hashtags = ["#FYP", "#Trending", "#Viral", "#ForYou"]
        tt_hashtags = trending_hashtags + seo_analysis.hashtags[:config['optimal_hashtags']]
        
        tt_description += f" {' '.join(tt_hashtags[:config['hashtags_limit']])}"
        
        return PlatformOptimization(
            platform=Platform.TIKTOK,
            optimized_title=title,
            optimized_description=tt_description[:config['caption_length']],
            hashtags=tt_hashtags,
            posting_schedule=["Daily 6-10 PM", "Peak: Tuesday 6 PM", "Weekend mornings"],
            audience_targeting={
                "demographics": "13-25",
                "trending_sounds": True,
                "viral_challenges": True
            },
            engagement_tips=[
                "Post 1-3 times daily for best reach",
                "Use trending sounds and effects",
                "Jump on trending challenges quickly",
                "Keep videos under 60 seconds for best performance"
            ]
        )

    async def _optimize_for_twitter(
        self,
        title: str,
        description: str,
        seo_analysis: SEOAnalysis,
        config: Dict[str, Any]
    ) -> PlatformOptimization:
        """Optimize content for Twitter"""        
        # Twitter text optimization
        tweet_text = f"{title}\n\n{description[:200]}..."
        tweet_text += f" {' '.join(seo_analysis.hashtags[:config['optimal_hashtags']])}"
        
        return PlatformOptimization(
            platform=Platform.TWITTER,
            optimized_title=title,
            optimized_description=tweet_text[:config['text_length']],
            hashtags=seo_analysis.hashtags[:config['hashtags_limit']],
            posting_schedule=["Monday-Friday 12-3 PM", "Evening 6-9 PM"],
            audience_targeting={
                "demographics": "18-49",
                "interests": seo_analysis.target_keywords,
                "trending_topics": True
            },
            engagement_tips=[
                "Tweet 3-5 times daily",
                "Engage in trending conversations",
                "Use Twitter Spaces for live interaction",
                "Retweet and comment on relevant content"
            ]
        )

    async def _optimize_for_generic_platform(
        self,
        title: str,
        description: str,
        seo_analysis: SEOAnalysis,
        config: Dict[str, Any]
    ) -> PlatformOptimization:
        """Generic platform optimization"""        
        return PlatformOptimization(
            platform=Platform.FACEBOOK,  # Default
            optimized_title=seo_analysis.optimized_title,
            optimized_description=seo_analysis.optimized_description,
            hashtags=seo_analysis.hashtags[:20],
            posting_schedule=["Best times: 1-3 PM weekdays"],
            audience_targeting={
                "demographics": "18-65",
                "interests": seo_analysis.target_keywords
            },
            engagement_tips=[
                "Post consistently",
                "Engage with audience",
                "Use relevant hashtags",
                "Monitor analytics"
            ]
        )

    async def perform_keyword_research(
        self,
        seed_keywords: List[str],
        content_type: str = "text"
    ) -> KeywordResearch:
        """        Perform comprehensive keyword research using AI algorithms
        """        try:
            # Expand seed keywords
            expanded_keywords = []
            for seed in seed_keywords:
                variations = await self._generate_keyword_variations(seed, content_type)
                expanded_keywords.extend(variations)
            
            # Remove duplicates and clean
            all_keywords = list(set([kw.lower().strip() for kw in expanded_keywords if len(kw.strip()) > 2]))
            
            # Classify keywords
            primary_keywords = seed_keywords[:5]
            secondary_keywords = [kw for kw in all_keywords[:15] if kw not in primary_keywords]
            long_tail_keywords = await self._generate_long_tail_keywords(primary_keywords, content_type)
            trending_keywords = await self._get_trending_keywords(content_type)
            
            # Simulate search volume and difficulty (would use real APIs)
            search_volume = {kw: max(100, hash(kw) % 10000) for kw in all_keywords[:20]}
            difficulty_scores = {kw: min(1.0, abs(hash(kw) % 100) / 100) for kw in all_keywords[:20]}
            
            # Generate content ideas
            content_ideas = await self._generate_content_ideas(primary_keywords, content_type)
            
            return KeywordResearch(
                primary_keywords=primary_keywords,
                secondary_keywords=secondary_keywords[:10],
                long_tail_keywords=long_tail_keywords,
                trending_keywords=trending_keywords[:10],
                competitor_keywords=[],  # Would implement competitor analysis
                search_volume=search_volume,
                difficulty_scores=difficulty_scores,
                suggested_content_ideas=content_ideas
            )
            
        except Exception as e:
            logger.error(f"Keyword research failed: {str(e)}")
            raise SEOError(f"Keyword research failed: {str(e)}")

    async def _generate_keyword_variations(self, seed_keyword: str, content_type: str) -> List[str]:
        """Generate keyword variations"""        variations = [seed_keyword]
        
        # Add content type variations
        content_suffixes = {
            'audio': ['music', 'sound', 'track', 'beat', 'song'],
            'video': ['video', 'clip', 'tutorial', 'guide', 'review'],
            'image': ['photo', 'image', 'art', 'design', 'picture'],
            'text': ['article', 'guide', 'tips', 'story', 'blog']
        }
        
        suffixes = content_suffixes.get(content_type, content_suffixes['text'])
        
        for suffix in suffixes:
            variations.extend([
                f"{seed_keyword} {suffix}",
                f"{suffix} {seed_keyword}",
                f"best {seed_keyword} {suffix}",
                f"how to {seed_keyword}",
                f"{seed_keyword} tutorial"
            ])
        
        return variations[:20]  # Limit variations

    async def _generate_long_tail_keywords(self, primary_keywords: List[str], content_type: str) -> List[str]:
        """Generate long-tail keyword phrases"""        long_tail = []
        
        modifiers = [
            "best", "top", "ultimate", "complete", "beginner", "advanced",
            "how to", "step by step", "guide to", "tips for", "secrets of"
        ]
        
        for primary in primary_keywords[:3]:
            for modifier in modifiers[:5]:
                long_tail.append(f"{modifier} {primary} {content_type}")
                long_tail.append(f"{primary} {modifier} guide")
        
        return long_tail[:15]

    async def _generate_content_ideas(self, keywords: List[str], content_type: str) -> List[str]:
        """Generate content ideas based on keywords"""        ideas = []
        
        content_templates = {
            'audio': [
                "How to create {} music",
                "Best {} beats for 2024",
                "Ultimate {} production guide",
                "{} mixing techniques revealed"
            ],
            'video': [
                "Complete {} tutorial",
                "Top 10 {} tips",
                "{} explained for beginners",
                "Advanced {} techniques"
            ],
            'image': [
                "Amazing {} photography tips",
                "{} design inspiration",
                "How to create stunning {} art",
                "{} editing masterclass"
            ],
            'text': [
                "Ultimate {} guide",
                "{} tips and tricks",
                "Everything about {}",
                "{} for beginners"
            ]
        }
        
        templates = content_templates.get(content_type, content_templates['text'])
        
        for keyword in keywords[:5]:
            for template in templates:
                ideas.append(template.format(keyword.title()))
        
        return ideas[:10]

    async def _cache_seo_analysis(self, title: str, analysis: SEOAnalysis) -> None:
        """Cache SEO analysis results"""        try:
            cache_key = f"seo_analysis:{hashlib.md5(title.encode()).hexdigest()}"
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(asdict(analysis), default=str)
            )
        except Exception as e:
            logger.warning(f"Failed to cache SEO analysis: {str(e)}")

    # Legacy method for backward compatibility
    def optimize(self, asset: ContentAsset) -> dict:
        """Legacy optimize method - deprecated, use analyze_content_seo instead"""        logger.warning("Using deprecated optimize method. Switch to analyze_content_seo")
        
        base = f"{asset.title} {asset.media_type} creator{asset.creator_id}"
        keywords: List[str] = list({w.lower() for w in base.split() if len(w) > 2})
        description = f"High-quality {asset.media_type} content: {asset.title} by creator {asset.creator_id}."
        return {
            "keywords": keywords[:12],
            "description": description,
            "slug": slugify(asset.title),
        }


# Create alias for backward compatibility
SEOService = EnterpriseSEOOptimizerService
SEOOptimizerService = EnterpriseSEOOptimizerService
