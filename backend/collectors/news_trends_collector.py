"""News Trends Collector
=====================

Consolidated news and trends collector combining functionality from:
- News (media monitoring, press mentions, news articles)
- Trends (trending topics, emerging trends, viral content)
- Industry insights and market intelligence

This module consolidates news and trends collectors into a unified
news monitoring solution for creators and brand awareness.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any, Union
from datetime import datetime, timedelta

from .base_collector import BaseCollector, CollectorResult, CollectionConfig
from .news import NewsCollector
from .trends import TrendsCollector

logger = logging.getLogger(__name__)

class NewsTrendsCollector(BaseCollector):
    """
    Unified news and trends collector for comprehensive media monitoring.
    
    Consolidates News and Trends collectors into a single interface
    for efficient news and trending content collection.
    """
    
    def __init__(self, platform_configs: Optional[Dict[str, Dict]] = None):
        """Initialize with platform-specific configurations."""
        super().__init__("news_trends", rate_limit=80)
        
        # Initialize individual platform collectors
        configs = platform_configs or {}
        
        self.news = NewsCollector(**configs.get('news', {}))
        self.trends = TrendsCollector(**configs.get('trends', {}))
        
        self.collectors = {
            'news': self.news,
            'trends': self.trends
        }
        
        logger.info("Initialized unified news and trends collector")
    
    async def search_content(self, query: str, config: CollectionConfig,
                           platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Search news and trends content across all or specified platforms.
        
        Args:
            query: Search query
            config: Collection configuration
            platforms: List of platforms to search (default: all)
            
        Returns:
            List of collected news and trends content from all platforms
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
                logger.info(f"Collected {len(platform_results)} news/trends results from {platform}")
            except Exception as e:
                logger.error(f"News/trends search failed for {platform}: {e}")
        
        return results
    
    async def get_content_details(self, content_id: str, platform: str = None) -> Optional[CollectorResult]:
        """
        Get detailed information about specific news/trends content.
        
        Args:
            content_id: ID of content to retrieve
            platform: Specific platform (auto-detect if None)
            
        Returns:
            Detailed news/trends content information
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
                logger.debug(f"News/trends content not found on {platform_name}: {e}")
        
        return None
    
    async def get_user_content(self, user_id: str, config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get news/trends content from specific source across platforms.
        
        Args:
            user_id: Source/publisher identifier
            config: Collection configuration
            platforms: List of platforms to search
            
        Returns:
            List of source news/trends content from all platforms
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
                logger.error(f"Source news/trends content collection failed for {platform}: {e}")
        
        return results
    
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> AsyncGenerator[CollectorResult, None]:
        """
        Monitor hashtags in news and trends content across platforms in real-time.
        
        Args:
            hashtags: List of hashtags to monitor
            config: Collection configuration
            platforms: List of platforms to monitor
            
        Yields:
            Real-time news/trends content matching hashtags
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
                    logger.error(f"News/trends hashtag monitoring failed for {platform}: {e}")
        
        # Yield results from all generators as they become available
        while generators:
            for i, gen in enumerate(generators[:]):
                try:
                    result = await gen.__anext__()
                    yield result
                except StopAsyncIteration:
                    generators.remove(gen)
                except Exception as e:
                    logger.error(f"News/trends hashtag monitoring error: {e}")
                    generators.remove(gen)
    
    async def get_trending_content(self, config: CollectionConfig,
                                 platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get trending news and topics across platforms.
        
        Args:
            config: Collection configuration
            platforms: List of platforms to check
            
        Returns:
            List of trending news and topics from all platforms
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
                logger.error(f"Trending news/trends collection failed for {platform}: {e}")
        
        return results
    
    async def monitor_brand_mentions(self, brand_keywords: List[str], 
                                   config: CollectionConfig) -> List[CollectorResult]:
        """
        Monitor brand/creator mentions in news and trending topics.
        
        Args:
            brand_keywords: List of brand/creator keywords to monitor
            config: Collection configuration
            
        Returns:
            List of news/trends content mentioning brands/creators
        """
        mentions = []
        
        for platform_name, collector in self.collectors.items():
            try:
                # Search for brand mentions
                for keyword in brand_keywords:
                    platform_mentions = await collector.search_content(keyword, config)
                    
                    # Filter for actual mentions and add metadata
                    for mention in platform_mentions:
                        content_text = f"{mention.title} {mention.description}".lower()
                        if any(keyword.lower() in content_text for keyword in brand_keywords):
                            mention.metadata['mention_type'] = 'news_mention'
                            mention.metadata['mentioned_keywords'] = [
                                kw for kw in brand_keywords 
                                if kw.lower() in content_text
                            ]
                            mention.metadata['source_type'] = platform_name
                            mentions.append(mention)
                
                logger.info(f"Found {len([m for m in mentions if m.metadata.get('source_type') == platform_name])} mentions in {platform_name}")
                
            except Exception as e:
                logger.error(f"Brand mention monitoring failed for {platform_name}: {e}")
        
        return mentions
    
    async def analyze_news_sentiment(self, topic: str, config: CollectionConfig) -> Dict[str, Any]:
        """
        Analyze news sentiment around a specific topic.
        
        Args:
            topic: Topic to analyze sentiment for
            config: Collection configuration
            
        Returns:
            News sentiment analysis results
        """
        sentiment_data = {
            'topic': topic,
            'analysis_timestamp': datetime.now().isoformat(),
            'platforms': {},
            'overall_sentiment': {
                'positive_articles': 0,
                'negative_articles': 0,
                'neutral_articles': 0,
                'total_articles': 0,
                'average_sentiment': 0.0,
                'sentiment_trend': 'neutral'
            }
        }
        
        for platform_name, collector in self.collectors.items():
            try:
                # Search for topic-related content
                topic_content = await collector.search_content(topic, config)
                
                if topic_content:
                    platform_sentiment = {
                        'articles_count': len(topic_content),
                        'positive_count': 0,
                        'negative_count': 0,
                        'neutral_count': 0,
                        'avg_sentiment': 0.0,
                        'top_articles': []
                    }
                    
                    total_sentiment = 0.0
                    for article in topic_content:
                        sentiment_score = article.sentiment_score or 0.0
                        total_sentiment += sentiment_score
                        
                        if sentiment_score > 0.1:
                            platform_sentiment['positive_count'] += 1
                        elif sentiment_score < -0.1:
                            platform_sentiment['negative_count'] += 1
                        else:
                            platform_sentiment['neutral_count'] += 1
                        
                        # Collect top articles by engagement
                        if article.engagement_metrics:
                            engagement = article.engagement_metrics.get('total_engagement', 0)
                            platform_sentiment['top_articles'].append({
                                'title': article.title,
                                'url': article.url,
                                'engagement': engagement,
                                'sentiment': sentiment_score,
                                'timestamp': article.timestamp
                            })
                    
                    platform_sentiment['avg_sentiment'] = total_sentiment / len(topic_content)
                    
                    # Sort top articles by engagement
                    platform_sentiment['top_articles'].sort(
                        key=lambda x: x['engagement'], reverse=True
                    )
                    platform_sentiment['top_articles'] = platform_sentiment['top_articles'][:5]
                    
                    sentiment_data['platforms'][platform_name] = platform_sentiment
                    
                    # Update overall sentiment
                    sentiment_data['overall_sentiment']['positive_articles'] += platform_sentiment['positive_count']
                    sentiment_data['overall_sentiment']['negative_articles'] += platform_sentiment['negative_count']
                    sentiment_data['overall_sentiment']['neutral_articles'] += platform_sentiment['neutral_count']
                    sentiment_data['overall_sentiment']['total_articles'] += len(topic_content)
                
            except Exception as e:
                logger.error(f"News sentiment analysis failed for {platform_name}: {e}")
                sentiment_data['platforms'][platform_name] = {'error': str(e)}
        
        # Calculate overall average sentiment
        if sentiment_data['overall_sentiment']['total_articles'] > 0:
            total_weighted_sentiment = sum(
                platform_data.get('avg_sentiment', 0) * platform_data.get('articles_count', 0)
                for platform_data in sentiment_data['platforms'].values()
                if isinstance(platform_data, dict) and 'avg_sentiment' in platform_data
            )
            sentiment_data['overall_sentiment']['average_sentiment'] = (
                total_weighted_sentiment / sentiment_data['overall_sentiment']['total_articles']
            )
            
            # Determine sentiment trend
            avg_sentiment = sentiment_data['overall_sentiment']['average_sentiment']
            if avg_sentiment > 0.1:
                sentiment_data['overall_sentiment']['sentiment_trend'] = 'positive'
            elif avg_sentiment < -0.1:
                sentiment_data['overall_sentiment']['sentiment_trend'] = 'negative'
            else:
                sentiment_data['overall_sentiment']['sentiment_trend'] = 'neutral'
        
        return sentiment_data
    
    async def detect_emerging_trends(self, config: CollectionConfig, 
                                   time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """
        Detect emerging trends across news and trending platforms.
        
        Args:
            config: Collection configuration
            time_window_hours: Time window for trend detection
            
        Returns:
            List of emerging trends with metadata
        """
        emerging_trends = []
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Collect trending content from all platforms
        all_trending = await self.get_trending_content(config)
        
        # Filter recent content
        recent_content = [
            content for content in all_trending
            if datetime.fromtimestamp(content.timestamp) >= cutoff_time
        ]
        
        if not recent_content:
            logger.warning("No recent trending content found for trend detection")
            return emerging_trends
        
        # Analyze keywords and topics
        keyword_counts = {}
        topic_engagement = {}
        
        for content in recent_content:
            # Extract keywords from hashtags
            if content.hashtags:
                for hashtag in content.hashtags:
                    keyword_counts[hashtag] = keyword_counts.get(hashtag, 0) + 1
                    
                    # Track engagement for this keyword
                    if hashtag not in topic_engagement:
                        topic_engagement[hashtag] = []
                    
                    if content.engagement_metrics:
                        topic_engagement[hashtag].append(
                            content.engagement_metrics.get('total_engagement', 0)
                        )
            
            # Extract keywords from title
            title_words = content.title.lower().split()
            for word in title_words:
                if len(word) > 3:  # Filter short words
                    keyword_counts[word] = keyword_counts.get(word, 0) + 1
        
        # Identify trending keywords
        min_mentions = max(3, len(recent_content) // 10)  # At least 3 mentions or 10% of content
        trending_keywords = [
            keyword for keyword, count in keyword_counts.items()
            if count >= min_mentions
        ]
        
        for keyword in trending_keywords:
            # Calculate trend metrics
            mentions_count = keyword_counts[keyword]
            avg_engagement = 0
            
            if keyword in topic_engagement and topic_engagement[keyword]:
                avg_engagement = sum(topic_engagement[keyword]) / len(topic_engagement[keyword])
            
            # Calculate trend velocity (mentions per hour)
            trend_velocity = mentions_count / time_window_hours
            
            # Create trend object
            trend = {
                'keyword': keyword,
                'mentions_count': mentions_count,
                'avg_engagement': avg_engagement,
                'trend_velocity': trend_velocity,
                'trend_score': (mentions_count * avg_engagement) / max(time_window_hours, 1),
                'time_window_hours': time_window_hours,
                'detected_timestamp': datetime.now().isoformat(),
                'related_content': [
                    {
                        'title': content.title,
                        'url': content.url,
                        'platform': content.platform,
                        'engagement': content.engagement_metrics.get('total_engagement', 0) if content.engagement_metrics else 0
                    }
                    for content in recent_content
                    if (content.hashtags and keyword in content.hashtags) or 
                       keyword in content.title.lower()
                ][:5]  # Top 5 related content pieces
            }
            
            emerging_trends.append(trend)
        
        # Sort by trend score
        emerging_trends.sort(key=lambda x: x['trend_score'], reverse=True)
        
        return emerging_trends
    
    async def get_industry_insights(self, industry: str, config: CollectionConfig) -> Dict[str, Any]:
        """
        Get industry-specific news insights and trends.
        
        Args:
            industry: Industry to analyze
            config: Collection configuration
            
        Returns:
            Industry insights and analysis
        """
        insights = {
            'industry': industry,
            'analysis_timestamp': datetime.now().isoformat(),
            'news_coverage': {},
            'trending_topics': [],
            'key_developments': [],
            'sentiment_overview': {}
        }
        
        # Search for industry-related content
        industry_keywords = [industry, f"{industry} industry", f"{industry} market", f"{industry} trends"]
        
        all_content = []
        for keyword in industry_keywords:
            content = await self.search_content(keyword, config)
            all_content.extend(content)
        
        if all_content:
            # Analyze news coverage by platform
            for platform_name in self.collectors.keys():
                platform_content = [c for c in all_content if c.platform == platform_name]
                insights['news_coverage'][platform_name] = {
                    'articles_count': len(platform_content),
                    'avg_engagement': sum(
                        c.engagement_metrics.get('total_engagement', 0) 
                        for c in platform_content 
                        if c.engagement_metrics
                    ) / len(platform_content) if platform_content else 0
                }
            
            # Extract trending topics
            keyword_counts = {}
            for content in all_content:
                if content.hashtags:
                    for hashtag in content.hashtags:
                        keyword_counts[hashtag] = keyword_counts.get(hashtag, 0) + 1
            
            insights['trending_topics'] = sorted(
                keyword_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            # Identify key developments (high-engagement content)
            high_engagement_content = sorted(
                all_content,
                key=lambda x: x.engagement_metrics.get('total_engagement', 0) if x.engagement_metrics else 0,
                reverse=True
            )[:5]
            
            insights['key_developments'] = [
                {
                    'title': content.title,
                    'url': content.url,
                    'platform': content.platform,
                    'engagement': content.engagement_metrics.get('total_engagement', 0) if content.engagement_metrics else 0,
                    'timestamp': content.timestamp
                }
                for content in high_engagement_content
            ]
            
            # Sentiment overview
            sentiment_analysis = await self.analyze_news_sentiment(industry, config)
            insights['sentiment_overview'] = sentiment_analysis.get('overall_sentiment', {})
        
        return insights
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all news and trends platform collectors."""
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