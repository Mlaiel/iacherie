"""Marketplace Collector
====================

Consolidated marketplace collector combining functionality from:
- Ecommerce (product listings, pricing, reviews)
- Pinterest (visual discovery, product pins, shopping)
- Creator marketplaces (sponsorship opportunities, brand collaborations)

This module consolidates marketplace collectors into a unified
marketplace monitoring solution for creators and brand partnerships.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any, Union
from datetime import datetime, timedelta

from .base_collector import BaseCollector, CollectorResult, CollectionConfig
from .ecommerce import EcommerceCollector
from .pinterest_collector import PinterestCollector

logger = logging.getLogger(__name__)

class MarketplaceCollector(BaseCollector):
    """
    Unified marketplace collector for comprehensive marketplace monitoring.
    
    Consolidates Ecommerce, Pinterest, and other marketplace collectors
    into a single interface for efficient marketplace content collection.
    """
    
    def __init__(self, platform_configs: Optional[Dict[str, Dict]] = None):
        """Initialize with platform-specific configurations."""
        super().__init__("marketplace", rate_limit=120)
        
        # Initialize individual platform collectors
        configs = platform_configs or {}
        
        self.ecommerce = EcommerceCollector(**configs.get('ecommerce', {}))
        self.pinterest = PinterestCollector(**configs.get('pinterest', {}))
        
        self.collectors = {
            'ecommerce': self.ecommerce,
            'pinterest': self.pinterest
        }
        
        logger.info("Initialized unified marketplace collector")
    
    async def search_content(self, query: str, config: CollectionConfig,
                           platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Search marketplace content across all or specified platforms.
        
        Args:
            query: Search query
            config: Collection configuration
            platforms: List of platforms to search (default: all)
            
        Returns:
            List of collected marketplace content from all platforms
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
                logger.info(f"Collected {len(platform_results)} marketplace results from {platform}")
            except Exception as e:
                logger.error(f"Marketplace search failed for {platform}: {e}")
        
        return results
    
    async def get_content_details(self, content_id: str, platform: str = None) -> Optional[CollectorResult]:
        """
        Get detailed information about specific marketplace content.
        
        Args:
            content_id: ID of marketplace content to retrieve
            platform: Specific platform (auto-detect if None)
            
        Returns:
            Detailed marketplace content information
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
                logger.debug(f"Marketplace content not found on {platform_name}: {e}")
        
        return None
    
    async def get_user_content(self, user_id: str, config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get marketplace content from specific user/creator across platforms.
        
        Args:
            user_id: User/creator identifier
            config: Collection configuration
            platforms: List of platforms to search
            
        Returns:
            List of user marketplace content from all platforms
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
                logger.error(f"User marketplace content collection failed for {platform}: {e}")
        
        return results
    
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> AsyncGenerator[CollectorResult, None]:
        """
        Monitor hashtags in marketplace content across platforms in real-time.
        
        Args:
            hashtags: List of hashtags to monitor
            config: Collection configuration
            platforms: List of platforms to monitor
            
        Yields:
            Real-time marketplace content matching hashtags
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
                    logger.error(f"Marketplace hashtag monitoring failed for {platform}: {e}")
        
        # Yield results from all generators as they become available
        while generators:
            for i, gen in enumerate(generators[:]):
                try:
                    result = await gen.__anext__()
                    yield result
                except StopAsyncIteration:
                    generators.remove(gen)
                except Exception as e:
                    logger.error(f"Marketplace hashtag monitoring error: {e}")
                    generators.remove(gen)
    
    async def get_trending_content(self, config: CollectionConfig,
                                 platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get trending marketplace content across platforms.
        
        Args:
            config: Collection configuration
            platforms: List of platforms to check
            
        Returns:
            List of trending marketplace content from all platforms
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
                logger.error(f"Trending marketplace content collection failed for {platform}: {e}")
        
        return results
    
    async def track_product_prices(self, product_keywords: List[str], 
                                 config: CollectionConfig) -> List[Dict[str, Any]]:
        """
        Track product prices across marketplace platforms.
        
        Args:
            product_keywords: List of product keywords to track
            config: Collection configuration
            
        Returns:
            List of product pricing information
        """
        price_data = []
        
        for platform_name, collector in self.collectors.items():
            try:
                for keyword in product_keywords:
                    # Search for products
                    products = await collector.search_content(keyword, config)
                    
                    for product in products:
                        # Extract pricing information
                        price_info = {
                            'platform': platform_name,
                            'product_id': product.content_id,
                            'title': product.title,
                            'url': product.url,
                            'price': product.metadata.get('price', 0),
                            'currency': product.metadata.get('currency', 'USD'),
                            'availability': product.metadata.get('availability', 'unknown'),
                            'rating': product.metadata.get('rating', 0),
                            'reviews_count': product.metadata.get('reviews_count', 0),
                            'keyword': keyword,
                            'tracked_timestamp': datetime.now().isoformat()
                        }
                        
                        # Platform-specific price extraction
                        if platform_name == 'ecommerce':
                            price_info.update({
                                'seller': product.metadata.get('seller', 'unknown'),
                                'shipping_cost': product.metadata.get('shipping_cost', 0),
                                'discount': product.metadata.get('discount', 0)
                            })
                        elif platform_name == 'pinterest':
                            price_info.update({
                                'pin_count': product.engagement_metrics.get('pins', 0) if product.engagement_metrics else 0,
                                'board_category': product.metadata.get('board_category', 'unknown')
                            })
                        
                        price_data.append(price_info)
                
                logger.info(f"Tracked {len([p for p in price_data if p['platform'] == platform_name])} products on {platform_name}")
                
            except Exception as e:
                logger.error(f"Product price tracking failed for {platform_name}: {e}")
        
        return price_data
    
    async def find_creator_opportunities(self, creator_niche: str, 
                                       config: CollectionConfig) -> List[Dict[str, Any]]:
        """
        Find marketplace opportunities for creators in specific niches.
        
        Args:
            creator_niche: Creator's niche/category
            config: Collection configuration
            
        Returns:
            List of marketplace opportunities
        """
        opportunities = []
        
        # Search for niche-related products and trends
        niche_keywords = [creator_niche, f"{creator_niche} creator", f"{creator_niche} influencer"]
        
        for platform_name, collector in self.collectors.items():
            try:
                for keyword in niche_keywords:
                    content = await collector.search_content(keyword, config)
                    
                    for item in content:
                        opportunity = {
                            'platform': platform_name,
                            'opportunity_type': 'product_collaboration',
                            'title': item.title,
                            'description': item.description,
                            'url': item.url,
                            'niche_relevance': self._calculate_niche_relevance(item, creator_niche),
                            'engagement_potential': self._calculate_engagement_potential(item),
                            'found_timestamp': datetime.now().isoformat()
                        }
                        
                        # Platform-specific opportunity details
                        if platform_name == 'ecommerce':
                            opportunity.update({
                                'commission_rate': item.metadata.get('commission_rate', 0),
                                'product_category': item.metadata.get('category', 'unknown'),
                                'seller_rating': item.metadata.get('seller_rating', 0)
                            })
                        elif platform_name == 'pinterest':
                            opportunity.update({
                                'visual_appeal': item.metadata.get('visual_score', 0),
                                'trending_score': item.metadata.get('trending_score', 0),
                                'board_saves': item.engagement_metrics.get('saves', 0) if item.engagement_metrics else 0
                            })
                        
                        # Only include relevant opportunities
                        if opportunity['niche_relevance'] > 0.3:
                            opportunities.append(opportunity)
                
            except Exception as e:
                logger.error(f"Creator opportunity search failed for {platform_name}: {e}")
        
        # Sort by relevance and engagement potential
        opportunities.sort(
            key=lambda x: (x['niche_relevance'] + x['engagement_potential']) / 2, 
            reverse=True
        )
        
        return opportunities
    
    async def analyze_visual_trends(self, category: str, config: CollectionConfig) -> Dict[str, Any]:
        """
        Analyze visual trends in marketplace content.
        
        Args:
            category: Product/content category to analyze
            config: Collection configuration
            
        Returns:
            Visual trends analysis
        """
        trends_data = {
            'category': category,
            'platforms': {},
            'overall_trends': {
                'top_colors': [],
                'popular_styles': [],
                'trending_keywords': []
            }
        }
        
        for platform_name, collector in self.collectors.items():
            try:
                # Search for category content
                category_content = await collector.search_content(category, config)
                
                if category_content:
                    platform_trends = {
                        'content_count': len(category_content),
                        'popular_keywords': [],
                        'engagement_leaders': [],
                        'visual_elements': []
                    }
                    
                    # Analyze keywords and visual elements
                    all_keywords = []
                    for content in category_content:
                        if content.hashtags:
                            all_keywords.extend(content.hashtags)
                        
                        # Extract visual elements from metadata
                        if 'visual_elements' in content.metadata:
                            platform_trends['visual_elements'].extend(
                                content.metadata['visual_elements']
                            )
                        
                        # Identify high-engagement content
                        if content.engagement_metrics:
                            engagement_score = content.engagement_metrics.get('total_engagement', 0)
                            if engagement_score > 1000:  # Threshold for high engagement
                                platform_trends['engagement_leaders'].append({
                                    'title': content.title,
                                    'engagement': engagement_score,
                                    'url': content.url
                                })
                    
                    # Find most popular keywords
                    keyword_counts = {}
                    for keyword in all_keywords:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
                    
                    platform_trends['popular_keywords'] = sorted(
                        keyword_counts.items(), 
                        key=lambda x: x[1], 
                        reverse=True
                    )[:10]
                    
                    trends_data['platforms'][platform_name] = platform_trends
                
            except Exception as e:
                logger.error(f"Visual trends analysis failed for {platform_name}: {e}")
                trends_data['platforms'][platform_name] = {'error': str(e)}
        
        return trends_data
    
    def _calculate_niche_relevance(self, content: CollectorResult, niche: str) -> float:
        """Calculate how relevant content is to a specific niche."""
        relevance_score = 0.0
        niche_lower = niche.lower()
        
        # Check title relevance
        if niche_lower in content.title.lower():
            relevance_score += 0.4
        
        # Check description relevance
        if niche_lower in content.description.lower():
            relevance_score += 0.3
        
        # Check hashtags relevance
        if content.hashtags:
            matching_hashtags = [tag for tag in content.hashtags if niche_lower in tag.lower()]
            relevance_score += min(0.3, len(matching_hashtags) * 0.1)
        
        return min(1.0, relevance_score)
    
    def _calculate_engagement_potential(self, content: CollectorResult) -> float:
        """Calculate engagement potential for marketplace content."""
        if not content.engagement_metrics:
            return 0.0
        
        total_engagement = content.engagement_metrics.get('total_engagement', 0)
        views = content.engagement_metrics.get('views', 1)
        
        # Simple engagement rate calculation
        engagement_rate = total_engagement / views if views > 0 else 0
        
        # Normalize to 0-1 scale
        return min(1.0, engagement_rate * 10)
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all marketplace platform collectors."""
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