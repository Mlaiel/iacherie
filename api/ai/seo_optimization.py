"""IA Influencer Agent - SEO Optimization Module
Industrial-grade SEO optimization system for multi-format content.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result 
in legal action.

© 2025 Fahed Mlaiel. All rights reserved.
"""import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio
import re
from collections import Counter
import math

logger = logging.getLogger(__name__)

class SEOPlatform(Enum):
    """Supported platforms for SEO optimization"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    GOOGLE_SEARCH = "google_search"
    BLOG_PLATFORMS = "blog_platforms"

class ContentFormat(Enum):
    """Content formats for SEO"""    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"

@dataclass
class SEOKeyword:
    """SEO keyword with metrics"""    keyword: str
    search_volume: int
    competition: float
    relevance_score: float
    trend_direction: str
    suggested_placement: List[str]

@dataclass
class SEOMetadata:
    """Optimized SEO metadata"""    title: str
    description: str
    tags: List[str]
    keywords: List[SEOKeyword]
    hashtags: List[str]
    category: str
    thumbnail_suggestions: List[str]
    optimal_posting_times: List[datetime]

@dataclass
class SEOAnalytics:
    """SEO performance analytics"""    seo_score: float
    keyword_density: Dict[str, float]
    readability_score: float
    engagement_prediction: float
    ranking_potential: Dict[SEOPlatform, float]
    optimization_suggestions: List[str]

class KeywordAnalyzer:
    """Advanced keyword research and analysis system"""    
    def __init__(self):
        self.trending_keywords = {
            'music': ['viral music', 'trending beats', 'original music', 'indie artist'],
            'video': ['viral video', 'trending content', 'creator content', 'entertainment'],
            'photography': ['professional photography', 'portrait photography', 'creative shots'],
            'blog': ['trending topics', 'lifestyle blog', 'professional insights'],
            'comedy': ['funny content', 'comedy sketches', 'humor', 'entertainment'],
            'podcast': ['podcast episodes', 'audio content', 'interviews', 'discussions']
        }
        
        self.platform_keywords = {
            SEOPlatform.YOUTUBE: ['youtube', 'video', 'subscribe', 'content creator'],
            SEOPlatform.INSTAGRAM: ['instagram', 'insta', 'photo', 'story', 'reel'],
            SEOPlatform.TIKTOK: ['tiktok', 'viral', 'trending', 'fyp', 'for you'],
            SEOPlatform.SPOTIFY: ['spotify', 'music', 'playlist', 'artist', 'stream'],
            SEOPlatform.SOUNDCLOUD: ['soundcloud', 'indie music', 'underground', 'beats']
        }
    
    async def analyze_content_keywords(
        self, 
        content_text: str, 
        metadata: Dict[str, Any],
        target_platforms: List[SEOPlatform]
    ) -> List[SEOKeyword]:
        """Analyze and extract optimal keywords from content"""        try:
            # Extract base keywords from content
            base_keywords = await self._extract_base_keywords(content_text)
            
            # Get trending keywords for content type
            content_type = metadata.get('content_type', 'general')
            trending = self.trending_keywords.get(content_type, [])
            
            # Combine with platform-specific keywords
            platform_keywords = []
            for platform in target_platforms:
                platform_keywords.extend(self.platform_keywords.get(platform, []))
            
            # Analyze keyword metrics
            analyzed_keywords = []
            all_keywords = set(base_keywords + trending + platform_keywords)
            
            for keyword in all_keywords:
                seo_keyword = await self._analyze_keyword_metrics(keyword, target_platforms)
                if seo_keyword.relevance_score > 0.3:  # Filter low-relevance keywords
                    analyzed_keywords.append(seo_keyword)
            
            # Sort by relevance and search volume
            analyzed_keywords.sort(key=lambda x: (x.relevance_score, x.search_volume), reverse=True)
            
            return analyzed_keywords[:20]  # Top 20 keywords
            
        except Exception as e:
            logger.error(f"Keyword analysis failed: {str(e)}")
            return []
    
    async def _extract_base_keywords(self, text: str) -> List[str]:
        """Extract base keywords from content text"""        if not text:
            return []
        
        # Clean text
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = clean_text.split()
        
        # Filter stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Extract n-grams
        bigrams = [f"{filtered_words[i]} {filtered_words[i+1]}" 
                  for i in range(len(filtered_words)-1)]
        
        # Combine single words and bigrams
        all_keywords = list(word_counts.keys()) + bigrams
        
        return all_keywords[:50]  # Top 50 base keywords
    
    async def _analyze_keyword_metrics(
        self, 
        keyword: str, 
        platforms: List[SEOPlatform]
    ) -> SEOKeyword:
        """Analyze metrics for a specific keyword"""        # Simulate keyword metrics (in production, use real SEO APIs)
        search_volume = self._estimate_search_volume(keyword)
        competition = self._estimate_competition(keyword)
        relevance_score = self._calculate_relevance_score(keyword, platforms)
        trend_direction = self._analyze_trend_direction(keyword)
        suggested_placement = self._suggest_keyword_placement(keyword, platforms)
        
        return SEOKeyword(
            keyword=keyword,
            search_volume=search_volume,
            competition=competition,
            relevance_score=relevance_score,
            trend_direction=trend_direction,
            suggested_placement=suggested_placement
        )
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate monthly search volume for keyword"""        # Simulate search volume estimation
        base_volume = len(keyword) * 100
        
        # Boost for trending terms
        trending_terms = ['viral', 'trending', 'creator', 'content', 'music', 'video']
        if any(term in keyword.lower() for term in trending_terms):
            base_volume *= 5
        
        return min(base_volume, 100000)  # Cap at 100k
    
    def _estimate_competition(self, keyword: str) -> float:
        """Estimate keyword competition level"""        # Simulate competition analysis
        if len(keyword.split()) == 1:  # Single words are more competitive
            return 0.8
        elif len(keyword.split()) == 2:  # Bigrams moderate competition
            return 0.6
        else:  # Long-tail keywords less competitive
            return 0.3
    
    def _calculate_relevance_score(self, keyword: str, platforms: List[SEOPlatform]) -> float:
        """Calculate keyword relevance score"""        base_score = 0.5
        
        # Boost for platform-specific keywords
        for platform in platforms:
            platform_keywords = self.platform_keywords.get(platform, [])
            if any(pk in keyword.lower() for pk in platform_keywords):
                base_score += 0.3
        
        # Boost for content-related keywords
        content_terms = ['content', 'creator', 'original', 'professional', 'quality']
        if any(term in keyword.lower() for term in content_terms):
            base_score += 0.2
        
        return min(base_score, 1.0)
    
    def _analyze_trend_direction(self, keyword: str) -> str:
        """Analyze keyword trend direction"""        # Simulate trend analysis
        trending_terms = ['ai', 'viral', 'trending', 'new', '2025']
        if any(term in keyword.lower() for term in trending_terms):
            return 'rising'
        else:
            return 'stable'
    
    def _suggest_keyword_placement(self, keyword: str, platforms: List[SEOPlatform]) -> List[str]:
        """Suggest optimal keyword placement"""        placements = ['title']  # Always suggest title
        
        if len(keyword.split()) <= 2:
            placements.extend(['description', 'tags'])
        
        if SEOPlatform.INSTAGRAM in platforms or SEOPlatform.TIKTOK in platforms:
            placements.append('hashtags')
        
        return placements

class ContentOptimizer:
    """Advanced content optimization for SEO"""    
    def __init__(self):
        self.keyword_analyzer = KeywordAnalyzer()
        self.title_templates = {
            ContentFormat.VIDEO: [
                "{keyword} - {emotion} {content_type}",
                "How to {action} with {keyword}",
                "{number} {keyword} Tips for {audience}",
                "The Ultimate {keyword} Guide"
            ],
            ContentFormat.AUDIO: [
                "{keyword} - {genre} Music",
                "New {keyword} Track by {artist}",
                "{keyword} Beats for {mood}"
            ],
            ContentFormat.IMAGE: [
                "Professional {keyword} Photography",
                "{keyword} - {style} Portrait",
                "Creative {keyword} Shots"
            ]
        }
    
    async def optimize_content_metadata(
        self, 
        content_data: bytes,
        metadata: Dict[str, Any],
        target_platforms: List[SEOPlatform]
    ) -> SEOMetadata:
        """Generate optimized SEO metadata for content"""        try:
            # Extract content text for analysis
            content_text = await self._extract_content_text(content_data, metadata)
            
            # Analyze keywords
            keywords = await self.keyword_analyzer.analyze_content_keywords(
                content_text, metadata, target_platforms
            )
            
            # Generate optimized title
            optimized_title = await self._generate_optimized_title(
                metadata, keywords, target_platforms
            )
            
            # Generate optimized description
            optimized_description = await self._generate_optimized_description(
                metadata, keywords, content_text
            )
            
            # Generate tags
            tags = await self._generate_optimized_tags(keywords, target_platforms)
            
            # Generate hashtags
            hashtags = await self._generate_hashtags(keywords, target_platforms)
            
            # Suggest category
            category = await self._suggest_category(metadata, keywords)
            
            # Generate thumbnail suggestions
            thumbnail_suggestions = await self._generate_thumbnail_suggestions(metadata, keywords)
            
            # Calculate optimal posting times
            optimal_times = await self._calculate_optimal_posting_times(target_platforms)
            
            return SEOMetadata(
                title=optimized_title,
                description=optimized_description,
                tags=tags,
                keywords=keywords,
                hashtags=hashtags,
                category=category,
                thumbnail_suggestions=thumbnail_suggestions,
                optimal_posting_times=optimal_times
            )
            
        except Exception as e:
            logger.error(f"Content optimization failed: {str(e)}")
            raise
    
    async def _extract_content_text(self, content_data: bytes, metadata: Dict[str, Any]) -> str:
        """Extract text from content for analysis"""        # Try to extract text from various sources
        text_sources = []
        
        # From metadata
        if metadata.get('title'):
            text_sources.append(metadata['title'])
        if metadata.get('description'):
            text_sources.append(metadata['description'])
        
        # From filename
        if metadata.get('filename'):
            filename = metadata['filename'].replace('_', ' ').replace('-', ' ')
            text_sources.append(filename)
        
        # If it's a text file, try to decode content
        if metadata.get('content_type') == 'text':
            try:
                content_text = content_data.decode('utf-8')
                text_sources.append(content_text[:1000])  # First 1000 chars
            except UnicodeDecodeError:
                pass
        
        return ' '.join(text_sources)
    
    async def _generate_optimized_title(
        self, 
        metadata: Dict[str, Any], 
        keywords: List[SEOKeyword],
        platforms: List[SEOPlatform]
    ) -> str:
        """Generate SEO-optimized title"""        original_title = metadata.get('title', '')
        
        if not keywords:
            return original_title or "Professional Content"
        
        # Get top keyword
        top_keyword = keywords[0].keyword
        
        # Determine content format
        content_format = self._determine_content_format(metadata)
        
        # Use template if available
        templates = self.title_templates.get(content_format, [])
        if templates:
            template = templates[0]  # Use first template
            optimized_title = template.format(
                keyword=top_keyword,
                emotion="Amazing",
                content_type="Content",
                action="Create",
                number="10",
                audience="Creators",
                genre="Original",
                artist=metadata.get('creator_name', 'Artist'),
                mood="Inspiration",
                style="Professional"
            )
        else:
            # Fallback optimization
            if original_title:
                optimized_title = f"{top_keyword} - {original_title}"
            else:
                optimized_title = f"Professional {top_keyword} Content"
        
        # Ensure title length is optimal for platforms
        max_length = self._get_max_title_length(platforms)
        if len(optimized_title) > max_length:
            optimized_title = optimized_title[:max_length-3] + "..."
        
        return optimized_title
    
    async def _generate_optimized_description(
        self, 
        metadata: Dict[str, Any], 
        keywords: List[SEOKeyword],
        content_text: str
    ) -> str:
        """Generate SEO-optimized description"""        original_description = metadata.get('description', '')
        
        if not keywords:
            return original_description or "Professional content created with passion."
        
        # Get top 5 keywords
        top_keywords = [kw.keyword for kw in keywords[:5]]
        
        # Build description template
        description_parts = []
        
        # Opening hook
        description_parts.append(f"Discover amazing {top_keywords[0]} content!")
        
        # Main content description
        if original_description:
            description_parts.append(original_description)
        elif content_text:
            # Use first sentence of content
            sentences = content_text.split('.')
            if sentences:
                description_parts.append(sentences[0] + '.')
        
        # SEO keyword integration
        keyword_phrase = f"Professional {', '.join(top_keywords[:3])} for creators and enthusiasts."
        description_parts.append(keyword_phrase)
        
        # Call to action
        description_parts.append("Follow for more amazing content!")
        
        return ' '.join(description_parts)
    
    async def _generate_optimized_tags(
        self, 
        keywords: List[SEOKeyword], 
        platforms: List[SEOPlatform]
    ) -> List[str]:
        """Generate optimized tags"""        tags = []
        
        # Add top keywords as tags
        for keyword in keywords[:15]:  # Top 15 keywords
            if ' ' in keyword.keyword:
                # Split multi-word keywords into individual tags
                tags.extend(keyword.keyword.split())
            else:
                tags.append(keyword.keyword)
        
        # Add platform-specific tags
        for platform in platforms:
            if platform == SEOPlatform.YOUTUBE:
                tags.extend(['youtube', 'content', 'creator'])
            elif platform == SEOPlatform.INSTAGRAM:
                tags.extend(['instagram', 'photo', 'creative'])
            elif platform == SEOPlatform.TIKTOK:
                tags.extend(['tiktok', 'viral', 'trending'])
        
        # Remove duplicates and limit
        unique_tags = list(set(tags))
        return unique_tags[:25]  # Most platforms limit tags
    
    async def _generate_hashtags(
        self, 
        keywords: List[SEOKeyword], 
        platforms: List[SEOPlatform]
    ) -> List[str]:
        """Generate optimized hashtags"""        hashtags = []
        
        # Convert top keywords to hashtags
        for keyword in keywords[:10]:
            hashtag = '#' + keyword.keyword.replace(' ', '').lower()
            hashtags.append(hashtag)
        
        # Add trending hashtags
        trending_hashtags = [
            '#content', '#creator', '#original', '#professional', 
            '#quality', '#creative', '#artist', '#influencer'
        ]
        hashtags.extend(trending_hashtags)
        
        # Platform-specific hashtags
        if SEOPlatform.INSTAGRAM in platforms:
            hashtags.extend(['#instagram', '#insta', '#photo'])
        if SEOPlatform.TIKTOK in platforms:
            hashtags.extend(['#tiktok', '#fyp', '#viral'])
        
        # Remove duplicates
        unique_hashtags = list(set(hashtags))
        return unique_hashtags[:30]  # Instagram limit
    
    async def _suggest_category(self, metadata: Dict[str, Any], keywords: List[SEOKeyword]) -> str:
        """Suggest optimal content category"""        content_type = metadata.get('content_type', '').lower()
        
        # Map content types to categories
        category_mapping = {
            'music': 'Music',
            'video': 'Entertainment',
            'image': 'Photography',
            'blog': 'Education',
            'podcast': 'Podcasts',
            'comedy': 'Comedy'
        }
        
        # Check if content type matches categories
        for ctype, category in category_mapping.items():
            if ctype in content_type:
                return category
        
        # Analyze keywords for category hints
        if keywords:
            top_keyword = keywords[0].keyword.lower()
            for ctype, category in category_mapping.items():
                if ctype in top_keyword:
                    return category
        
        return 'Entertainment'  # Default category
    
    async def _generate_thumbnail_suggestions(
        self, 
        metadata: Dict[str, Any], 
        keywords: List[SEOKeyword]
    ) -> List[str]:
        """Generate thumbnail optimization suggestions"""        suggestions = []
        
        # Basic suggestions
        suggestions.append("Use bright, contrasting colors")
        suggestions.append("Include text overlay with main keyword")
        suggestions.append("Show faces or expressions if applicable")
        
        # Keyword-based suggestions
        if keywords:
            top_keyword = keywords[0].keyword
            suggestions.append(f"Include visual elements related to '{top_keyword}'")
        
        # Format-specific suggestions
        content_type = metadata.get('content_type', '').lower()
        if 'music' in content_type:
            suggestions.append("Show musical instruments or audio waveforms")
        elif 'video' in content_type:
            suggestions.append("Use action shots or dynamic poses")
        
        return suggestions
    
    async def _calculate_optimal_posting_times(
        self, 
        platforms: List[SEOPlatform]
    ) -> List[datetime]:
        """Calculate optimal posting times for platforms"""        # Simulate optimal posting times based on platform analytics
        base_time = datetime.utcnow().replace(hour=18, minute=0, second=0, microsecond=0)
        
        optimal_times = []
        
        for platform in platforms:
            if platform == SEOPlatform.INSTAGRAM:
                # Best times for Instagram
                optimal_times.append(base_time.replace(hour=11))
                optimal_times.append(base_time.replace(hour=14))
                optimal_times.append(base_time.replace(hour=17))
            elif platform == SEOPlatform.TIKTOK:
                # Best times for TikTok
                optimal_times.append(base_time.replace(hour=9))
                optimal_times.append(base_time.replace(hour=12))
                optimal_times.append(base_time.replace(hour=19))
            elif platform == SEOPlatform.YOUTUBE:
                # Best times for YouTube
                optimal_times.append(base_time.replace(hour=15))
                optimal_times.append(base_time.replace(hour=20))
        
        return list(set(optimal_times))  # Remove duplicates
    
    def _determine_content_format(self, metadata: Dict[str, Any]) -> ContentFormat:
        """Determine content format from metadata"""        content_type = metadata.get('content_type', '').lower()
        filename = metadata.get('filename', '').lower()
        
        if 'video' in content_type or any(ext in filename for ext in ['.mp4', '.avi', '.mkv']):
            return ContentFormat.VIDEO
        elif 'audio' in content_type or any(ext in filename for ext in ['.mp3', '.wav', '.flac']):
            return ContentFormat.AUDIO
        elif 'image' in content_type or any(ext in filename for ext in ['.jpg', '.png', '.jpeg']):
            return ContentFormat.IMAGE
        else:
            return ContentFormat.TEXT
    
    def _get_max_title_length(self, platforms: List[SEOPlatform]) -> int:
        """Get maximum title length for platforms"""        # Return minimum of all platform limits
        platform_limits = {
            SEOPlatform.YOUTUBE: 100,
            SEOPlatform.INSTAGRAM: 125,
            SEOPlatform.TIKTOK: 150,
            SEOPlatform.TWITTER: 280
        }
        
        if not platforms:
            return 100  # Default limit
        
        limits = [platform_limits.get(p, 100) for p in platforms]
        return min(limits)

class PerformanceAnalyzer:
    """SEO performance analysis and optimization suggestions"""    
    def __init__(self):
        self.scoring_weights = {
            'keyword_optimization': 0.3,
            'content_quality': 0.25,
            'engagement_potential': 0.2,
            'technical_seo': 0.15,
            'social_signals': 0.1
        }
    
    async def analyze_seo_performance(
        self, 
        metadata: SEOMetadata, 
        content_metrics: Dict[str, Any]
    ) -> SEOAnalytics:
        """Analyze comprehensive SEO performance"""        try:
            # Calculate individual scores
            keyword_score = await self._analyze_keyword_optimization(metadata)
            content_score = await self._analyze_content_quality(metadata, content_metrics)
            engagement_score = await self._predict_engagement(metadata, content_metrics)
            technical_score = await self._analyze_technical_seo(metadata)
            social_score = await self._analyze_social_signals(metadata)
            
            # Calculate overall SEO score
            overall_score = (
                keyword_score * self.scoring_weights['keyword_optimization'] +
                content_score * self.scoring_weights['content_quality'] +
                engagement_score * self.scoring_weights['engagement_potential'] +
                technical_score * self.scoring_weights['technical_seo'] +
                social_score * self.scoring_weights['social_signals']
            )
            
            # Calculate keyword density
            keyword_density = await self._calculate_keyword_density(metadata)
            
            # Calculate readability
            readability_score = await self._calculate_readability(metadata)
            
            # Predict platform rankings
            ranking_potential = await self._predict_platform_rankings(metadata)
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(
                keyword_score, content_score, engagement_score, technical_score, social_score
            )
            
            return SEOAnalytics(
                seo_score=overall_score,
                keyword_density=keyword_density,
                readability_score=readability_score,
                engagement_prediction=engagement_score,
                ranking_potential=ranking_potential,
                optimization_suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"SEO performance analysis failed: {str(e)}")
            raise
    
    async def _analyze_keyword_optimization(self, metadata: SEOMetadata) -> float:
        """Analyze keyword optimization score"""        if not metadata.keywords:
            return 0.3
        
        # Check keyword placement in title and description
        title_keywords = sum(1 for kw in metadata.keywords if kw.keyword.lower() in metadata.title.lower())
        desc_keywords = sum(1 for kw in metadata.keywords if kw.keyword.lower() in metadata.description.lower())
        
        # Score based on keyword presence and quality
        title_score = min(title_keywords / max(len(metadata.keywords), 1), 1.0) * 0.6
        desc_score = min(desc_keywords / max(len(metadata.keywords), 1), 1.0) * 0.4
        
        return title_score + desc_score
    
    async def _analyze_content_quality(self, metadata: SEOMetadata, content_metrics: Dict[str, Any]) -> float:
        """Analyze content quality score"""        quality_indicators = []
        
        # Title quality
        if len(metadata.title) > 30:  # Good title length
            quality_indicators.append(0.8)
        else:
            quality_indicators.append(0.5)
        
        # Description quality
        if len(metadata.description) > 100:  # Good description length
            quality_indicators.append(0.8)
        else:
            quality_indicators.append(0.5)
        
        # Tags diversity
        if len(metadata.tags) >= 10:
            quality_indicators.append(0.9)
        else:
            quality_indicators.append(0.6)
        
        return sum(quality_indicators) / len(quality_indicators)
    
    async def _predict_engagement(self, metadata: SEOMetadata, content_metrics: Dict[str, Any]) -> float:
        """Predict engagement potential"""        engagement_factors = []
        
        # Hashtag optimization
        if len(metadata.hashtags) >= 10:
            engagement_factors.append(0.8)
        else:
            engagement_factors.append(0.5)
        
        # Keyword trending potential
        trending_keywords = sum(1 for kw in metadata.keywords if kw.trend_direction == 'rising')
        trend_score = min(trending_keywords / max(len(metadata.keywords), 1), 1.0)
        engagement_factors.append(trend_score)
        
        return sum(engagement_factors) / len(engagement_factors)
    
    async def _analyze_technical_seo(self, metadata: SEOMetadata) -> float:
        """Analyze technical SEO factors"""        technical_scores = []
        
        # Metadata completeness
        completeness = sum([
            1 if metadata.title else 0,
            1 if metadata.description else 0,
            1 if metadata.tags else 0,
            1 if metadata.category else 0
        ]) / 4
        technical_scores.append(completeness)
        
        # Optimization suggestions implementation
        if metadata.thumbnail_suggestions:
            technical_scores.append(0.8)
        else:
            technical_scores.append(0.4)
        
        return sum(technical_scores) / len(technical_scores)
    
    async def _analyze_social_signals(self, metadata: SEOMetadata) -> float:
        """Analyze social media optimization"""        if not metadata.hashtags:
            return 0.3
        
        # Social hashtag optimization
        social_hashtags = len([h for h in metadata.hashtags if any(
            social in h.lower() for social in ['instagram', 'tiktok', 'youtube', 'viral']
        )])
        
        return min(social_hashtags / 10, 1.0)  # Normalize to 1.0
    
    async def _calculate_keyword_density(self, metadata: SEOMetadata) -> Dict[str, float]:
        """Calculate keyword density in content"""        if not metadata.keywords:
            return {}
        
        # Combine all text content
        all_text = f"{metadata.title} {metadata.description} {' '.join(metadata.tags)}"
        total_words = len(all_text.split())
        
        if total_words == 0:
            return {}
        
        keyword_density = {}
        for keyword in metadata.keywords[:10]:  # Top 10 keywords
            keyword_count = all_text.lower().count(keyword.keyword.lower())
            density = (keyword_count / total_words) * 100
            keyword_density[keyword.keyword] = round(density, 2)
        
        return keyword_density
    
    async def _calculate_readability(self, metadata: SEOMetadata) -> float:
        """Calculate content readability score"""        text = metadata.description
        if not text:
            return 0.5
        
        # Simple readability calculation
        sentences = len([s for s in text.split('.') if s.strip()])
        words = len(text.split())
        
        if sentences == 0:
            return 0.5
        
        avg_sentence_length = words / sentences
        
        # Score based on sentence length (optimal: 15-20 words)
        if 15 <= avg_sentence_length <= 20:
            return 0.9
        elif 10 <= avg_sentence_length <= 25:
            return 0.7
        else:
            return 0.5
    
    async def _predict_platform_rankings(self, metadata: SEOMetadata) -> Dict[SEOPlatform, float]:
        """Predict ranking potential on different platforms"""        rankings = {}
        
        # Analyze content for each platform
        for platform in SEOPlatform:
            platform_score = 0.5  # Base score
            
            # Platform-specific keyword optimization
            platform_keywords = ['youtube', 'instagram', 'tiktok', 'music', 'content']
            if any(pk in ' '.join([kw.keyword for kw in metadata.keywords]).lower() 
                   for pk in platform_keywords):
                platform_score += 0.2
            
            # Hashtag optimization for social platforms
            if platform in [SEOPlatform.INSTAGRAM, SEOPlatform.TIKTOK] and metadata.hashtags:
                platform_score += 0.3
            
            rankings[platform] = min(platform_score, 1.0)
        
        return rankings
    
    async def _generate_optimization_suggestions(
        self, 
        keyword_score: float, 
        content_score: float, 
        engagement_score: float, 
        technical_score: float, 
        social_score: float
    ) -> List[str]:
        """Generate actionable optimization suggestions"""        suggestions = []
        
        if keyword_score < 0.7:
            suggestions.append("Improve keyword placement in title and description")
            suggestions.append("Research and add more relevant keywords")
        
        if content_score < 0.7:
            suggestions.append("Expand content description for better context")
            suggestions.append("Add more diverse and specific tags")
        
        if engagement_score < 0.7:
            suggestions.append("Use more trending hashtags")
            suggestions.append("Focus on rising keywords")
        
        if technical_score < 0.7:
            suggestions.append("Complete all metadata fields")
            suggestions.append("Implement thumbnail optimization suggestions")
        
        if social_score < 0.7:
            suggestions.append("Add platform-specific hashtags")
            suggestions.append("Optimize for social media sharing")
        
        return suggestions

# Export main classes
__all__ = [
    'SEOPlatform',
    'ContentFormat',
    'SEOKeyword',
    'SEOMetadata',
    'SEOAnalytics',
    'KeywordAnalyzer',
    'ContentOptimizer',
    'PerformanceAnalyzer'
]
