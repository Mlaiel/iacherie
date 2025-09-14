"""Platform SEO Adapter - Multi-Platform SEO Optimization

This module provides platform-specific SEO adaptation for different social media
and content platforms, optimizing content for each platform's unique requirements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms for SEO optimization"""
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    BLOG = "blog"
    WEBSITE = "website"


@dataclass
class PlatformSEOConfig:
    """Platform-specific SEO configuration"""
    max_title_length: int
    max_description_length: int
    max_hashtags: int
    optimal_content_length: Tuple[int, int]  # (min, max) words
    requires_hashtags: bool
    supports_rich_media: bool
    algorithm_factors: Dict[str, float]
    character_limit: Optional[int] = None


@dataclass
class PlatformOptimizationResult:
    """Result of platform-specific optimization"""
    platform: Platform
    optimized_title: str
    optimized_description: str
    optimized_content: str
    hashtags: List[str]
    metadata: Dict[str, Any]
    seo_score: float
    recommendations: List[str]


class BasePlatformAdapter(ABC):
    """Base class for platform-specific SEO adapters"""
    
    @abstractmethod
    def get_config(self) -> PlatformSEOConfig:
        """Get platform-specific configuration"""
        pass
    
    @abstractmethod
    def optimize_content(self, content: str, keywords: List[str]) -> str:
        """Optimize content for the platform"""
        pass
    
    @abstractmethod
    def generate_hashtags(self, content: str, keywords: List[str]) -> List[str]:
        """Generate platform-appropriate hashtags"""
        pass
    
    @abstractmethod
    def calculate_seo_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate platform-specific SEO score"""
        pass


class InstagramAdapter(BasePlatformAdapter):
    """Instagram SEO adapter"""
    
    def get_config(self) -> PlatformSEOConfig:
        return PlatformSEOConfig(
            max_title_length=125,
            max_description_length=2200,
            max_hashtags=30,
            optimal_content_length=(50, 150),
            requires_hashtags=True,
            supports_rich_media=True,
            algorithm_factors={
                "engagement_rate": 0.3,
                "hashtag_relevance": 0.25,
                "visual_quality": 0.2,
                "posting_time": 0.15,
                "caption_quality": 0.1
            }
        )
    
    def optimize_content(self, content: str, keywords: List[str]) -> str:
        """Optimize content for Instagram"""
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            if line.strip():
                # Add line breaks for mobile readability
                if len(line) > 80:
                    words = line.split()
                    current_line = []
                    for word in words:
                        if len(' '.join(current_line + [word])) <= 80:
                            current_line.append(word)
                        else:
                            optimized_lines.append(' '.join(current_line))
                            current_line = [word]
                    if current_line:
                        optimized_lines.append(' '.join(current_line))
                else:
                    optimized_lines.append(line)
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def generate_hashtags(self, content: str, keywords: List[str]) -> List[str]:
        """Generate Instagram hashtags"""
        hashtags = []
        
        # Add keyword-based hashtags
        for keyword in keywords:
            hashtag = f"#{keyword.replace(' ', '').lower()}"
            if hashtag not in hashtags:
                hashtags.append(hashtag)
        
        # Add trending/popular hashtags
        popular_hashtags = [
            "#contentcreator", "#digitalmarketing", "#socialmedia",
            "#marketing", "#branding", "#content", "#creative",
            "#business", "#entrepreneur", "#growth"
        ]
        
        for hashtag in popular_hashtags:
            if len(hashtags) < 25 and hashtag not in hashtags:
                hashtags.append(hashtag)
        
        return hashtags[:30]  # Instagram limit
    
    def calculate_seo_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate Instagram SEO score"""
        score = 0.0
        config = self.get_config()
        
        # Content length score
        word_count = len(content.split())
        if config.optimal_content_length[0] <= word_count <= config.optimal_content_length[1]:
            score += 25
        
        # Hashtag score
        hashtag_count = metadata.get('hashtag_count', 0)
        if 10 <= hashtag_count <= 30:
            score += 25
        
        # Engagement potential score
        if any(word in content.lower() for word in ['tips', 'how to', 'tutorial', 'guide']):
            score += 20
        
        # Visual description score
        if any(word in content.lower() for word in ['see', 'look', 'photo', 'image', 'video']):
            score += 15
        
        # Call-to-action score
        if any(phrase in content.lower() for phrase in ['follow', 'like', 'comment', 'share', 'tag']):
            score += 15
        
        return min(100.0, score)


class YouTubeAdapter(BasePlatformAdapter):
    """YouTube SEO adapter"""
    
    def get_config(self) -> PlatformSEOConfig:
        return PlatformSEOConfig(
            max_title_length=100,
            max_description_length=5000,
            max_hashtags=15,
            optimal_content_length=(200, 500),
            requires_hashtags=False,
            supports_rich_media=True,
            algorithm_factors={
                "watch_time": 0.35,
                "click_through_rate": 0.25,
                "keyword_relevance": 0.2,
                "engagement": 0.15,
                "video_quality": 0.05
            }
        )
    
    def optimize_content(self, content: str, keywords: List[str]) -> str:
        """Optimize content for YouTube"""
        # Add timestamps if content is structured
        lines = content.split('\n')
        optimized_lines = []
        
        for i, line in enumerate(lines):
            if line.strip() and line.strip().endswith(':'):
                # Potential section header - add timestamp
                minutes = i * 2  # Rough estimate
                timestamp = f"{minutes//60:02d}:{minutes%60:02d}"
                optimized_lines.append(f"{timestamp} - {line}")
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def generate_hashtags(self, content: str, keywords: List[str]) -> List[str]:
        """Generate YouTube hashtags"""
        hashtags = []
        
        # Add keyword-based hashtags
        for keyword in keywords:
            hashtag = f"#{keyword.replace(' ', '').lower()}"
            if hashtag not in hashtags:
                hashtags.append(hashtag)
        
        # Add YouTube-specific hashtags
        youtube_hashtags = [
            "#youtube", "#video", "#tutorial", "#howto",
            "#education", "#entertainment", "#vlog", "#content"
        ]
        
        for hashtag in youtube_hashtags:
            if len(hashtags) < 12 and hashtag not in hashtags:
                hashtags.append(hashtag)
        
        return hashtags[:15]  # YouTube recommended limit
    
    def calculate_seo_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate YouTube SEO score"""
        score = 0.0
        
        # Title optimization score
        title = metadata.get('title', '')
        if any(keyword.lower() in title.lower() for keyword in metadata.get('keywords', [])):
            score += 20
        
        # Description length score
        if 200 <= len(content.split()) <= 500:
            score += 20
        
        # Keyword placement score
        first_paragraph = content.split('\n')[0] if content else ''
        if any(keyword.lower() in first_paragraph.lower() for keyword in metadata.get('keywords', [])):
            score += 20
        
        # Structure score (timestamps, sections)
        if ':' in content and any(char.isdigit() for char in content):
            score += 15
        
        # Call-to-action score
        if any(phrase in content.lower() for phrase in ['subscribe', 'like', 'comment', 'bell']):
            score += 15
        
        # Link score
        if 'http' in content or 'www.' in content:
            score += 10
        
        return min(100.0, score)


class TwitterAdapter(BasePlatformAdapter):
    """Twitter SEO adapter"""
    
    def get_config(self) -> PlatformSEOConfig:
        return PlatformSEOConfig(
            max_title_length=280,
            max_description_length=280,
            max_hashtags=2,
            optimal_content_length=(15, 35),
            requires_hashtags=False,
            supports_rich_media=True,
            character_limit=280,
            algorithm_factors={
                "engagement_rate": 0.4,
                "recency": 0.3,
                "hashtag_relevance": 0.15,
                "user_authority": 0.1,
                "media_presence": 0.05
            }
        )
    
    def optimize_content(self, content: str, keywords: List[str]) -> str:
        """Optimize content for Twitter"""
        # Ensure content fits character limit
        if len(content) > 250:  # Leave room for hashtags
            sentences = content.split('.')
            optimized = sentences[0] + '.'
            
            # Add more sentences if they fit
            for sentence in sentences[1:]:
                if len(optimized + sentence + '.') <= 250:
                    optimized += sentence + '.'
                else:
                    break
            
            return optimized.strip()
        
        return content
    
    def generate_hashtags(self, content: str, keywords: List[str]) -> List[str]:
        """Generate Twitter hashtags"""
        hashtags = []
        
        # Twitter works best with 1-2 focused hashtags
        if keywords:
            main_keyword = keywords[0].replace(' ', '').lower()
            hashtags.append(f"#{main_keyword}")
        
        # Add one trending hashtag if space allows
        trending_hashtags = ["#marketing", "#business", "#tech", "#innovation"]
        for hashtag in trending_hashtags:
            if len(hashtags) < 2 and hashtag not in hashtags:
                hashtags.append(hashtag)
                break
        
        return hashtags[:2]
    
    def calculate_seo_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate Twitter SEO score"""
        score = 0.0
        
        # Character count optimization
        content_length = len(content)
        if 50 <= content_length <= 280:
            score += 25
        
        # Engagement potential
        if any(char in content for char in ['?', '!']):
            score += 20
        
        # Mention/hashtag balance
        hashtag_count = len([word for word in content.split() if word.startswith('#')])
        if hashtag_count <= 2:
            score += 20
        
        # URL presence
        if any(word.startswith('http') for word in content.split()):
            score += 15
        
        # Call-to-action
        if any(word in content.lower() for word in ['retweet', 'follow', 'check', 'read']):
            score += 20
        
        return min(100.0, score)


class LinkedInAdapter(BasePlatformAdapter):
    """LinkedIn SEO adapter"""
    
    def get_config(self) -> PlatformSEOConfig:
        return PlatformSEOConfig(
            max_title_length=150,
            max_description_length=3000,
            max_hashtags=5,
            optimal_content_length=(150, 300),
            requires_hashtags=False,
            supports_rich_media=True,
            algorithm_factors={
                "professional_relevance": 0.3,
                "engagement_quality": 0.25,
                "industry_keywords": 0.2,
                "user_connections": 0.15,
                "content_format": 0.1
            }
        )
    
    def optimize_content(self, content: str, keywords: List[str]) -> str:
        """Optimize content for LinkedIn"""
        # Add professional tone and structure
        if not content.startswith(('As a', 'In my experience', 'I recently', 'Today')):
            content = f"I recently learned about {keywords[0] if keywords else 'this topic'}. {content}"
        
        # Add professional call-to-action
        if not any(phrase in content.lower() for phrase in ['thoughts?', 'agree?', 'experience']):
            content += "\n\nWhat are your thoughts on this?"
        
        return content
    
    def generate_hashtags(self, content: str, keywords: List[str]) -> List[str]:
        """Generate LinkedIn hashtags"""
        hashtags = []
        
        # Professional hashtags
        for keyword in keywords:
            hashtag = f"#{keyword.replace(' ', '').lower()}"
            if hashtag not in hashtags:
                hashtags.append(hashtag)
        
        # LinkedIn-specific professional hashtags
        professional_hashtags = [
            "#leadership", "#business", "#professional", "#career",
            "#networking", "#industry", "#innovation", "#growth"
        ]
        
        for hashtag in professional_hashtags:
            if len(hashtags) < 5 and hashtag not in hashtags:
                hashtags.append(hashtag)
        
        return hashtags[:5]
    
    def calculate_seo_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate LinkedIn SEO score"""
        score = 0.0
        
        # Professional tone score
        professional_words = ['experience', 'insights', 'strategy', 'industry', 'business']
        if any(word in content.lower() for word in professional_words):
            score += 25
        
        # Engagement invitation score
        if any(phrase in content.lower() for phrase in ['thoughts?', 'agree?', 'what do you think']):
            score += 20
        
        # Content length score
        word_count = len(content.split())
        if 150 <= word_count <= 300:
            score += 20
        
        # Industry keyword score
        if any(keyword.lower() in content.lower() for keyword in metadata.get('keywords', [])):
            score += 20
        
        # Structure score
        if content.count('\n') >= 2:  # Paragraph breaks
            score += 15
        
        return min(100.0, score)


class PlatformSEOAdapter:
    """
    Main adapter class that provides platform-specific SEO optimization
    """
    
    def __init__(self) -> None:
        """Initialize the platform SEO adapter with all supported platforms"""
        self.adapters = {
            Platform.INSTAGRAM: InstagramAdapter(),
            Platform.YOUTUBE: YouTubeAdapter(),
            Platform.TWITTER: TwitterAdapter(),
            Platform.LINKEDIN: LinkedInAdapter(),
            # Add more platforms as needed
        }
    
    def optimize_for_platform(
        self,
        content: str,
        platform: Platform,
        keywords: List[str],
        title: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PlatformOptimizationResult:
        """
        Optimize content for a specific platform
        
        Args:
            content: Original content
            platform: Target platform
            keywords: Target keywords
            title: Content title
            metadata: Additional metadata
            
        Returns:
            PlatformOptimizationResult with optimized content
        """
        try:
            if platform not in self.adapters:
                raise ValueError(f"Platform {platform} not supported")
            
            adapter = self.adapters[platform]
            config = adapter.get_config()
            
            # Optimize content
            optimized_content = adapter.optimize_content(content, keywords)
            
            # Generate hashtags
            hashtags = adapter.generate_hashtags(optimized_content, keywords)
            
            # Optimize title and description
            optimized_title = self._optimize_title(title or content[:50], config, keywords)
            optimized_description = self._optimize_description(
                optimized_content, config, keywords
            )
            
            # Prepare metadata
            full_metadata = {
                'keywords': keywords,
                'title': optimized_title,
                'hashtag_count': len(hashtags),
                'platform': platform.value,
                **(metadata or {})
            }
            
            # Calculate SEO score
            seo_score = adapter.calculate_seo_score(optimized_content, full_metadata)
            
            # Generate recommendations
            recommendations = self._generate_platform_recommendations(
                optimized_content, platform, config, seo_score
            )
            
            return PlatformOptimizationResult(
                platform=platform,
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                optimized_content=optimized_content,
                hashtags=hashtags,
                metadata=full_metadata,
                seo_score=seo_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error optimizing for platform {platform}: {str(e)}")
            raise
    
    def optimize_for_multiple_platforms(
        self,
        content: str,
        platforms: List[Platform],
        keywords: List[str],
        title: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[Platform, PlatformOptimizationResult]:
        """
        Optimize content for multiple platforms
        
        Args:
            content: Original content
            platforms: List of target platforms
            keywords: Target keywords
            title: Content title
            metadata: Additional metadata
            
        Returns:
            Dictionary mapping platforms to optimization results
        """
        results = {}
        
        for platform in platforms:
            try:
                results[platform] = self.optimize_for_platform(
                    content, platform, keywords, title, metadata
                )
            except Exception as e:
                logger.error(f"Failed to optimize for {platform}: {str(e)}")
                continue
        
        return results
    
    def _optimize_title(
        self, 
        title: str, 
        config: PlatformSEOConfig, 
        keywords: List[str]
    ) -> str:
        """Optimize title for platform"""
        if len(title) > config.max_title_length:
            title = title[:config.max_title_length - 3] + "..."
        
        # Ensure main keyword is in title
        if keywords and keywords[0].lower() not in title.lower():
            available_space = config.max_title_length - len(title) - 3
            if len(keywords[0]) <= available_space:
                title = f"{keywords[0]} - {title}"
        
        return title
    
    def _optimize_description(
        self, 
        content: str, 
        config: PlatformSEOConfig, 
        keywords: List[str]
    ) -> str:
        """Optimize description for platform"""
        if len(content) <= config.max_description_length:
            return content
        
        # Truncate but try to end at sentence boundary
        truncated = content[:config.max_description_length - 3]
        last_sentence_end = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        
        if last_sentence_end > config.max_description_length * 0.7:
            return truncated[:last_sentence_end + 1]
        else:
            return truncated + "..."
    
    def _generate_platform_recommendations(
        self,
        content: str,
        platform: Platform,
        config: PlatformSEOConfig,
        seo_score: float
    ) -> List[str]:
        """Generate platform-specific recommendations"""
        recommendations = []
        
        word_count = len(content.split())
        
        # Length recommendations
        if word_count < config.optimal_content_length[0]:
            recommendations.append(
                f"Content is too short for {platform.value}. "
                f"Aim for {config.optimal_content_length[0]}-{config.optimal_content_length[1]} words."
            )
        elif word_count > config.optimal_content_length[1]:
            recommendations.append(
                f"Content is too long for {platform.value}. "
                f"Consider shortening to {config.optimal_content_length[1]} words or less."
            )
        
        # Platform-specific recommendations
        if platform == Platform.INSTAGRAM and config.requires_hashtags:
            if '#' not in content:
                recommendations.append("Add relevant hashtags to improve discoverability.")
        
        if platform == Platform.TWITTER and len(content) > 250:
            recommendations.append("Content too long for Twitter. Consider creating a thread.")
        
        if platform == Platform.LINKEDIN and not any(word in content.lower() for word in ['experience', 'industry', 'professional']):
            recommendations.append("Add professional language to improve LinkedIn engagement.")
        
        # SEO score recommendations
        if seo_score < 70:
            recommendations.append("Consider improving content structure and keyword usage.")
        
        return recommendations
    
    def get_supported_platforms(self) -> List[Platform]:
        """Get list of supported platforms"""
        return list(self.adapters.keys())
    
    def get_platform_config(self, platform: Platform) -> PlatformSEOConfig:
        """Get configuration for a specific platform"""
        if platform not in self.adapters:
            raise ValueError(f"Platform {platform} not supported")
        return self.adapters[platform].get_config()


# Export for module usage
__all__ = [
    "PlatformSEOAdapter", 
    "Platform", 
    "PlatformSEOConfig", 
    "PlatformOptimizationResult",
    "BasePlatformAdapter"
]