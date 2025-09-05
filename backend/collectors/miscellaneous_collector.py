"""Miscellaneous Collector
======================

Consolidated miscellaneous collector combining functionality from:
- Misc (specialized sources, custom APIs, alternative platforms)
- Third-party APIs and data sources
- Industry-specific collectors
- Future platform expansions

This module consolidates miscellaneous collectors into a unified
flexible monitoring solution for specialized and emerging platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any, Union
from datetime import datetime, timedelta

from .base_collector import BaseCollector, CollectorResult, CollectionConfig
from .misc import MiscCollector

logger = logging.getLogger(__name__)

class MiscellaneousCollector(BaseCollector):
    """
    Unified miscellaneous collector for specialized and emerging platforms.
    
    Consolidates Misc and other specialized collectors into a single interface
    for flexible content collection from various sources.
    """
    
    def __init__(self, platform_configs: Optional[Dict[str, Dict]] = None):
        """Initialize with platform-specific configurations."""
        super().__init__("miscellaneous", rate_limit=60)
        
        # Initialize individual platform collectors
        configs = platform_configs or {}
        
        self.misc = MiscCollector(**configs.get('misc', {}))
        
        # Registry for additional specialized collectors
        self.specialized_collectors = {}
        
        self.collectors = {
            'misc': self.misc
        }
        
        # Add any additional specialized collectors from config
        for platform_name, platform_config in configs.items():
            if platform_name not in self.collectors and platform_name != 'misc':
                try:
                    # Dynamic collector registration for future expansions
                    self.register_specialized_collector(platform_name, platform_config)
                except Exception as e:
                    logger.warning(f"Failed to register specialized collector {platform_name}: {e}")
        
        logger.info("Initialized unified miscellaneous collector")
    
    def register_specialized_collector(self, platform_name: str, config: Dict[str, Any]):
        """Register a new specialized collector dynamically."""
        # This allows for future expansion without code changes
        # Platform-specific collectors can be registered at runtime
        
        # For now, we'll store the config for future use
        self.specialized_collectors[platform_name] = {
            'config': config,
            'registered_at': datetime.now().isoformat(),
            'status': 'registered'
        }
        
        logger.info(f"Registered specialized collector: {platform_name}")
    
    async def search_content(self, query: str, config: CollectionConfig,
                           platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Search miscellaneous content across all or specified platforms.
        
        Args:
            query: Search query
            config: Collection configuration
            platforms: List of platforms to search (default: all)
            
        Returns:
            List of collected miscellaneous content from all platforms
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
                logger.info(f"Collected {len(platform_results)} miscellaneous results from {platform}")
            except Exception as e:
                logger.error(f"Miscellaneous search failed for {platform}: {e}")
        
        return results
    
    async def get_content_details(self, content_id: str, platform: str = None) -> Optional[CollectorResult]:
        """
        Get detailed information about specific miscellaneous content.
        
        Args:
            content_id: ID of content to retrieve
            platform: Specific platform (auto-detect if None)
            
        Returns:
            Detailed miscellaneous content information
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
                logger.debug(f"Miscellaneous content not found on {platform_name}: {e}")
        
        return None
    
    async def get_user_content(self, user_id: str, config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get miscellaneous content from specific user across platforms.
        
        Args:
            user_id: User identifier
            config: Collection configuration
            platforms: List of platforms to search
            
        Returns:
            List of user miscellaneous content from all platforms
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
                logger.error(f"User miscellaneous content collection failed for {platform}: {e}")
        
        return results
    
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> AsyncGenerator[CollectorResult, None]:
        """
        Monitor hashtags in miscellaneous content across platforms in real-time.
        
        Args:
            hashtags: List of hashtags to monitor
            config: Collection configuration
            platforms: List of platforms to monitor
            
        Yields:
            Real-time miscellaneous content matching hashtags
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
                    logger.error(f"Miscellaneous hashtag monitoring failed for {platform}: {e}")
        
        # Yield results from all generators as they become available
        while generators:
            for i, gen in enumerate(generators[:]):
                try:
                    result = await gen.__anext__()
                    yield result
                except StopAsyncIteration:
                    generators.remove(gen)
                except Exception as e:
                    logger.error(f"Miscellaneous hashtag monitoring error: {e}")
                    generators.remove(gen)
    
    async def get_trending_content(self, config: CollectionConfig,
                                 platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get trending miscellaneous content across platforms.
        
        Args:
            config: Collection configuration
            platforms: List of platforms to check
            
        Returns:
            List of trending miscellaneous content from all platforms
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
                logger.error(f"Trending miscellaneous content collection failed for {platform}: {e}")
        
        return results
    
    async def collect_from_custom_api(self, api_config: Dict[str, Any], 
                                    query: str, config: CollectionConfig) -> List[CollectorResult]:
        """
        Collect content from custom API sources.
        
        Args:
            api_config: Custom API configuration
            query: Search query
            config: Collection configuration
            
        Returns:
            List of content from custom API
        """
        results = []
        
        try:
            # Validate API configuration
            required_fields = ['endpoint', 'method']
            if not all(field in api_config for field in required_fields):
                logger.error("Custom API config missing required fields: endpoint, method")
                return results
            
            # Use misc collector to handle custom API calls
            custom_results = await self.misc.collect_from_custom_source(
                source_type='custom_api',
                source_config=api_config,
                query=query,
                config=config
            )
            
            results.extend(custom_results)
            logger.info(f"Collected {len(custom_results)} results from custom API")
            
        except Exception as e:
            logger.error(f"Custom API collection failed: {e}")
        
        return results
    
    async def monitor_rss_feeds(self, feed_urls: List[str], 
                              config: CollectionConfig) -> List[CollectorResult]:
        """
        Monitor RSS feeds for new content.
        
        Args:
            feed_urls: List of RSS feed URLs to monitor
            config: Collection configuration
            
        Returns:
            List of content from RSS feeds
        """
        results = []
        
        for feed_url in feed_urls:
            try:
                # Use misc collector to handle RSS feeds
                feed_results = await self.misc.collect_from_rss_feed(feed_url, config)
                results.extend(feed_results)
                logger.info(f"Collected {len(feed_results)} items from RSS feed: {feed_url}")
                
            except Exception as e:
                logger.error(f"RSS feed monitoring failed for {feed_url}: {e}")
        
        return results
    
    async def scrape_website_content(self, website_config: Dict[str, Any], 
                                   config: CollectionConfig) -> List[CollectorResult]:
        """
        Scrape content from websites using custom configurations.
        
        Args:
            website_config: Website scraping configuration
            config: Collection configuration
            
        Returns:
            List of scraped content
        """
        results = []
        
        try:
            # Validate website configuration
            required_fields = ['url', 'selectors']
            if not all(field in website_config for field in required_fields):
                logger.error("Website config missing required fields: url, selectors")
                return results
            
            # Use misc collector to handle website scraping
            scraped_results = await self.misc.scrape_website(website_config, config)
            results.extend(scraped_results)
            logger.info(f"Scraped {len(scraped_results)} items from website: {website_config['url']}")
            
        except Exception as e:
            logger.error(f"Website scraping failed: {e}")
        
        return results
    
    async def aggregate_cross_platform_data(self, user_identifier: str, 
                                          config: CollectionConfig) -> Dict[str, Any]:
        """
        Aggregate data about a user/creator across all miscellaneous platforms.
        
        Args:
            user_identifier: User/creator identifier
            config: Collection configuration
            
        Returns:
            Aggregated cross-platform data
        """
        aggregated_data = {
            'user_identifier': user_identifier,
            'platforms': {},
            'summary': {
                'total_platforms': 0,
                'total_content': 0,
                'total_engagement': 0,
                'latest_activity': None
            },
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        for platform_name, collector in self.collectors.items():
            try:
                # Get user content from each platform
                user_content = await collector.get_user_content(user_identifier, config)
                
                if user_content:
                    platform_data = {
                        'content_count': len(user_content),
                        'total_engagement': sum(
                            content.engagement_metrics.get('total_engagement', 0)
                            for content in user_content
                            if content.engagement_metrics
                        ),
                        'latest_post': max(user_content, key=lambda x: x.timestamp).timestamp,
                        'content_types': list(set(content.content_type for content in user_content)),
                        'avg_engagement': 0
                    }
                    
                    if platform_data['content_count'] > 0:
                        platform_data['avg_engagement'] = (
                            platform_data['total_engagement'] / platform_data['content_count']
                        )
                    
                    aggregated_data['platforms'][platform_name] = platform_data
                    
                    # Update summary
                    aggregated_data['summary']['total_platforms'] += 1
                    aggregated_data['summary']['total_content'] += platform_data['content_count']
                    aggregated_data['summary']['total_engagement'] += platform_data['total_engagement']
                    
                    if (aggregated_data['summary']['latest_activity'] is None or 
                        platform_data['latest_post'] > aggregated_data['summary']['latest_activity']):
                        aggregated_data['summary']['latest_activity'] = platform_data['latest_post']
                
            except Exception as e:
                logger.error(f"Cross-platform aggregation failed for {platform_name}: {e}")
                aggregated_data['platforms'][platform_name] = {'error': str(e)}
        
        return aggregated_data
    
    async def detect_platform_opportunities(self, niche: str, 
                                          config: CollectionConfig) -> List[Dict[str, Any]]:
        """
        Detect opportunities on miscellaneous platforms for a specific niche.
        
        Args:
            niche: Niche/industry to analyze
            config: Collection configuration
            
        Returns:
            List of platform opportunities
        """
        opportunities = []
        
        for platform_name, collector in self.collectors.items():
            try:
                # Search for niche-related content
                niche_content = await collector.search_content(niche, config)
                
                if niche_content:
                    # Analyze platform potential
                    total_engagement = sum(
                        content.engagement_metrics.get('total_engagement', 0)
                        for content in niche_content
                        if content.engagement_metrics
                    )
                    
                    avg_engagement = total_engagement / len(niche_content) if niche_content else 0
                    
                    opportunity = {
                        'platform': platform_name,
                        'niche': niche,
                        'opportunity_score': self._calculate_opportunity_score(niche_content),
                        'content_volume': len(niche_content),
                        'avg_engagement': avg_engagement,
                        'competition_level': self._assess_competition_level(niche_content),
                        'recommended_strategy': self._suggest_strategy(platform_name, niche_content),
                        'sample_content': [
                            {
                                'title': content.title,
                                'url': content.url,
                                'engagement': content.engagement_metrics.get('total_engagement', 0) if content.engagement_metrics else 0
                            }
                            for content in sorted(niche_content, 
                                                key=lambda x: x.engagement_metrics.get('total_engagement', 0) if x.engagement_metrics else 0, 
                                                reverse=True)[:3]
                        ]
                    }
                    
                    opportunities.append(opportunity)
                
            except Exception as e:
                logger.error(f"Platform opportunity detection failed for {platform_name}: {e}")
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return opportunities
    
    def _calculate_opportunity_score(self, content_list: List[CollectorResult]) -> float:
        """Calculate opportunity score based on content analysis."""
        if not content_list:
            return 0.0
        
        # Factors: engagement rate, content volume, recency
        total_engagement = sum(
            content.engagement_metrics.get('total_engagement', 0)
            for content in content_list
            if content.engagement_metrics
        )
        
        avg_engagement = total_engagement / len(content_list)
        
        # Recency factor (newer content gets higher score)
        recent_content = [
            content for content in content_list
            if datetime.fromtimestamp(content.timestamp) > datetime.now() - timedelta(days=30)
        ]
        recency_factor = len(recent_content) / len(content_list)
        
        # Volume factor (more content = more opportunity)
        volume_factor = min(1.0, len(content_list) / 100)  # Normalize to 0-1
        
        # Combine factors
        opportunity_score = (avg_engagement * 0.5 + recency_factor * 0.3 + volume_factor * 0.2)
        
        return min(1.0, opportunity_score / 1000)  # Normalize to 0-1 scale
    
    def _assess_competition_level(self, content_list: List[CollectorResult]) -> str:
        """Assess competition level based on content analysis."""
        if len(content_list) < 10:
            return 'low'
        elif len(content_list) < 50:
            return 'medium'
        else:
            return 'high'
    
    def _suggest_strategy(self, platform: str, content_list: List[CollectorResult]) -> str:
        """Suggest strategy based on platform and content analysis."""
        avg_engagement = sum(
            content.engagement_metrics.get('total_engagement', 0)
            for content in content_list
            if content.engagement_metrics
        ) / len(content_list) if content_list else 0
        
        if avg_engagement > 1000:
            return "Focus on high-quality, engaging content with unique value proposition"
        elif avg_engagement > 100:
            return "Consistent posting with community engagement and trend awareness"
        else:
            return "Niche-specific content with strong SEO and cross-platform promotion"
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all miscellaneous platform collectors."""
        status = {
            'unified_collector': {
                'status': self.status.value,
                'total_collected': self.total_collected,
                'stats': self.stats
            },
            'platforms': {},
            'specialized_collectors': self.specialized_collectors
        }
        
        for platform_name, collector in self.collectors.items():
            status['platforms'][platform_name] = collector.get_platform_info()
        
        return status