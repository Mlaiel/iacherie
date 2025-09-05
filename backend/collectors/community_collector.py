"""Community Collector
==================

Consolidated community collector combining functionality from:
- Discord (servers, channels, messages, voice activity)
- Reddit (subreddits, posts, comments, user activity)
- Other community platforms (future expansion)

This module consolidates community platform collectors into a unified
community monitoring solution for brand mentions and creator discussions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any, Union
from datetime import datetime, timedelta

from .base_collector import BaseCollector, CollectorResult, CollectionConfig

logger = logging.getLogger(__name__)

# Individual platform collector classes (simplified implementations)
class DiscordCollector(BaseCollector):
    """Discord content collector."""
    def __init__(self, **kwargs):
        super().__init__("discord", rate_limit=50)
    
    async def search_content(self, query: str, config: CollectionConfig) -> List[CollectorResult]:
        return []
    async def get_content_details(self, content_id: str) -> Optional[CollectorResult]:
        return None
    async def get_user_content(self, user_id: str, config: CollectionConfig) -> List[CollectorResult]:
        return []
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig) -> AsyncGenerator[CollectorResult, None]:
        return
        yield
    async def get_trending_content(self, config: CollectionConfig) -> List[CollectorResult]:
        return []

class RedditCollector(BaseCollector):
    """Reddit content collector."""
    def __init__(self, **kwargs):
        super().__init__("reddit", rate_limit=60)
    
    async def search_content(self, query: str, config: CollectionConfig) -> List[CollectorResult]:
        return []
    async def get_content_details(self, content_id: str) -> Optional[CollectorResult]:
        return None
    async def get_user_content(self, user_id: str, config: CollectionConfig) -> List[CollectorResult]:
        return []
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig) -> AsyncGenerator[CollectorResult, None]:
        return
        yield
    async def get_trending_content(self, config: CollectionConfig) -> List[CollectorResult]:
        return []

class CommunityCollector(BaseCollector):
    """
    Unified community collector for comprehensive community monitoring.
    
    Consolidates Discord, Reddit, and other community platform collectors
    into a single interface for efficient community content collection.
    """
    
    def __init__(self, platform_configs: Optional[Dict[str, Dict]] = None):
        """Initialize with platform-specific configurations."""
        super().__init__("community", rate_limit=100)
        
        # Initialize individual platform collectors
        configs = platform_configs or {}
        
        self.discord = DiscordCollector(**configs.get('discord', {}))
        self.reddit = RedditCollector(**configs.get('reddit', {}))
        
        self.collectors = {
            'discord': self.discord,
            'reddit': self.reddit
        }
        
        logger.info("Initialized unified community collector")
    
    async def search_content(self, query: str, config: CollectionConfig,
                           platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Search community content across all or specified platforms.
        
        Args:
            query: Search query
            config: Collection configuration
            platforms: List of platforms to search (default: all)
            
        Returns:
            List of collected community content from all platforms
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
        
        results = []
        tasks = []
        
        # Create search tasks for each platform
        for platform in platforms:
            if platform in self.collectors:
                task = self.collectors[platform].search_content(query, config)
                tasks.append((platform, task))
        
        # Execute searches concurrently
        for platform, task in tasks:
            try:
                platform_results = await task
                results.extend(platform_results)
                logger.info(f"Collected {len(platform_results)} community results from {platform}")
            except Exception as e:
                logger.error(f"Community search failed for {platform}: {e}")
        
        return results
    
    async def get_content_details(self, content_id: str, platform: str = None) -> Optional[CollectorResult]:
        """
        Get detailed information about specific community content.
        
        Args:
            content_id: ID of community content to retrieve
            platform: Specific platform (auto-detect if None)
            
        Returns:
            Detailed community content information
        """
        if platform and platform in self.collectors:
            return await self.collectors[platform].get_content_details(content_id)
        
        # Try all platforms if platform not specified
        for platform_name, collector in self.collectors.items():
            try:
                result = await collector.get_content_details(content_id)
                if result:
                    return result
            except Exception as e:
                logger.debug(f"Community content not found on {platform_name}: {e}")
        
        return None
    
    async def get_user_content(self, user_id: str, config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get community content from specific user across platforms.
        
        Args:
            user_id: User identifier
            config: Collection configuration
            platforms: List of platforms to search
            
        Returns:
            List of user community content from all platforms
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
        
        results = []
        tasks = []
        
        for platform in platforms:
            if platform in self.collectors:
                task = self.collectors[platform].get_user_content(user_id, config)
                tasks.append((platform, task))
        
        for platform, task in tasks:
            try:
                platform_results = await task
                results.extend(platform_results)
            except Exception as e:
                logger.error(f"User community content collection failed for {platform}: {e}")
        
        return results
    
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> AsyncGenerator[CollectorResult, None]:
        """
        Monitor hashtags/keywords in community content across platforms in real-time.
        
        Args:
            hashtags: List of hashtags/keywords to monitor
            config: Collection configuration
            platforms: List of platforms to monitor
            
        Yields:
            Real-time community content matching hashtags/keywords
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
        
        # Create async generators for each platform
        generators = []
        for platform in platforms:
            if platform in self.collectors:
                try:
                    gen = self.collectors[platform].monitor_hashtags(hashtags, config)
                    generators.append(gen)
                except Exception as e:
                    logger.error(f"Community hashtag monitoring failed for {platform}: {e}")
        
        # Yield results from all generators as they become available
        while generators:
            for i, gen in enumerate(generators[:]):
                try:
                    result = await gen.__anext__()
                    yield result
                except StopAsyncIteration:
                    generators.remove(gen)
                except Exception as e:
                    logger.error(f"Community hashtag monitoring error: {e}")
                    generators.remove(gen)
    
    async def get_trending_content(self, config: CollectionConfig,
                                 platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get trending community content across platforms.
        
        Args:
            config: Collection configuration
            platforms: List of platforms to check
            
        Returns:
            List of trending community content from all platforms
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
        
        results = []
        tasks = []
        
        for platform in platforms:
            if platform in self.collectors:
                task = self.collectors[platform].get_trending_content(config)
                tasks.append((platform, task))
        
        for platform, task in tasks:
            try:
                platform_results = await task
                results.extend(platform_results)
            except Exception as e:
                logger.error(f"Trending community content collection failed for {platform}: {e}")
        
        return results
    
    async def monitor_brand_mentions(self, brand_keywords: List[str], 
                                   config: CollectionConfig) -> List[CollectorResult]:
        """
        Monitor brand/creator mentions across community platforms.
        
        Args:
            brand_keywords: List of brand/creator keywords to monitor
            config: Collection configuration
            
        Returns:
            List of community content mentioning brands/creators
        """
        mentions = []
        
        for platform_name, collector in self.collectors.items():
            try:
                # Search for brand mentions
                for keyword in brand_keywords:
                    platform_mentions = await collector.search_content(keyword, config)
                    
                    # Filter for actual mentions (not just keyword matches)
                    relevant_mentions = []
                    for mention in platform_mentions:
                        content_text = f"{mention.title} {mention.description}".lower()
                        if any(keyword.lower() in content_text for keyword in brand_keywords):
                            mention.metadata['mention_type'] = 'brand_mention'
                            mention.metadata['mentioned_keywords'] = [
                                kw for kw in brand_keywords 
                                if kw.lower() in content_text
                            ]
                            relevant_mentions.append(mention)
                    
                    mentions.extend(relevant_mentions)
                    
                logger.info(f"Found {len(relevant_mentions)} brand mentions on {platform_name}")
                
            except Exception as e:
                logger.error(f"Brand mention monitoring failed for {platform_name}: {e}")
        
        return mentions
    
    async def analyze_sentiment(self, content_list: List[CollectorResult]) -> Dict[str, Any]:
        """
        Analyze sentiment of community discussions.
        
        Args:
            content_list: List of community content to analyze
            
        Returns:
            Sentiment analysis results
        """
        sentiment_data = {
            'total_content': len(content_list),
            'platform_breakdown': {},
            'overall_sentiment': 'neutral',
            'sentiment_scores': []
        }
        
        # Group content by platform
        platform_content = {}
        for content in content_list:
            platform = content.platform
            if platform not in platform_content:
                platform_content[platform] = []
            platform_content[platform].append(content)
        
        # Analyze sentiment for each platform
        for platform, content in platform_content.items():
            platform_sentiment = {
                'content_count': len(content),
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'avg_sentiment': 0.0
            }
            
            total_sentiment = 0.0
            for item in content:
                # Use existing sentiment score or default to neutral
                sentiment_score = item.sentiment_score or 0.0
                total_sentiment += sentiment_score
                
                if sentiment_score > 0.1:
                    platform_sentiment['positive_count'] += 1
                elif sentiment_score < -0.1:
                    platform_sentiment['negative_count'] += 1
                else:
                    platform_sentiment['neutral_count'] += 1
            
            platform_sentiment['avg_sentiment'] = total_sentiment / len(content) if content else 0.0
            sentiment_data['platform_breakdown'][platform] = platform_sentiment
            sentiment_data['sentiment_scores'].extend([
                item.sentiment_score or 0.0 for item in content
            ])
        
        # Calculate overall sentiment
        if sentiment_data['sentiment_scores']:
            avg_sentiment = sum(sentiment_data['sentiment_scores']) / len(sentiment_data['sentiment_scores'])
            if avg_sentiment > 0.1:
                sentiment_data['overall_sentiment'] = 'positive'
            elif avg_sentiment < -0.1:
                sentiment_data['overall_sentiment'] = 'negative'
            else:
                sentiment_data['overall_sentiment'] = 'neutral'
        
        return sentiment_data
    
    async def track_community_engagement(self, topic: str, days: int = 7) -> Dict[str, Any]:
        """
        Track community engagement around a specific topic.
        
        Args:
            topic: Topic to track
            days: Number of days to analyze
            
        Returns:
            Community engagement analytics
        """
        engagement_data = {
            'topic': topic,
            'analysis_period_days': days,
            'platforms': {},
            'overall_metrics': {
                'total_posts': 0,
                'total_comments': 0,
                'total_engagement': 0,
                'engagement_trend': 'stable'
            }
        }
        
        config = CollectionConfig(max_results=200)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for platform_name, collector in self.collectors.items():
            try:
                # Search for topic-related content
                topic_content = await collector.search_content(topic, config)
                
                # Filter by date range
                recent_content = [
                    content for content in topic_content
                    if datetime.fromtimestamp(content.timestamp) >= cutoff_date
                ]
                
                if recent_content:
                    total_engagement = sum(
                        content.engagement_metrics.get('total_engagement', 0)
                        for content in recent_content
                        if content.engagement_metrics
                    )
                    
                    total_comments = sum(
                        content.engagement_metrics.get('comments', 0)
                        for content in recent_content
                        if content.engagement_metrics
                    )
                    
                    platform_metrics = {
                        'posts_count': len(recent_content),
                        'total_engagement': total_engagement,
                        'total_comments': total_comments,
                        'avg_engagement_per_post': total_engagement / len(recent_content),
                        'daily_post_rate': len(recent_content) / days
                    }
                    
                    engagement_data['platforms'][platform_name] = platform_metrics
                    engagement_data['overall_metrics']['total_posts'] += len(recent_content)
                    engagement_data['overall_metrics']['total_comments'] += total_comments
                    engagement_data['overall_metrics']['total_engagement'] += total_engagement
                
            except Exception as e:
                logger.error(f"Community engagement tracking failed for {platform_name}: {e}")
                engagement_data['platforms'][platform_name] = {'error': str(e)}
        
        return engagement_data
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all community platform collectors."""
        status = {
            'unified_collector': {
                'status': self.status.value,
                'total_collected': self.total_collected,
                'stats': self.stats
            },
            'platforms': {}
        }
        
        for platform_name, collector in self.collectors.items():
            status['platforms'][platform_name] = collector.get_platform_info()
        
        return status