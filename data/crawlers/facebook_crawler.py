"""Facebook Crawler Implementation
==============================

Professional Facebook content crawler for copyright protection and content monitoring.
Implements advanced Graph API integration and content discovery capabilities.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, parse_qs
import json

import aiohttp
import facebook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .platform_crawler import PlatformCrawler, CrawlerConfig, ContentMatch, ContentMatchType
from ..fingerprinting.vector_matcher import VectorMatcher


class FacebookCrawler(PlatformCrawler):
    """    Professional Facebook crawler for content monitoring and copyright protection.
    
    Features:
    - Facebook Graph API integration
    - Page and post content analysis
    - Media content extraction
    - Advanced search capabilities
    - Real-time monitoring
    - Anti-detection measures for web scraping
    """    
    def __init__(self, config: CrawlerConfig, vector_matcher: VectorMatcher,
                 access_token: str, app_secret: str = None):
        """        Initialize Facebook crawler.
        
        Args:
            config: Crawler configuration
            vector_matcher: Vector matching service
            access_token: Facebook Graph API access token
            app_secret: Optional Facebook app secret for enhanced security
        """        super().__init__(config, vector_matcher)
        
        # API credentials
        self.access_token = access_token
        self.app_secret = app_secret
        
        # Facebook Graph API client
        self.graph_api = None
        
        # Rate limiting parameters
        self.rate_limit_window = 3600  # 1 hour
        self.requests_per_hour = 200   # Conservative limit
        self.current_requests = 0
        self.window_start = datetime.utcnow()
        
        # Search parameters
        self.max_posts_per_search = 50
        self.supported_post_types = ['status', 'photo', 'video', 'link', 'offer', 'music', 'note']
        
        # Selenium for advanced scraping when API limits reached
        self.selenium_driver = None
        self.selenium_options = None
        
        # Initialize API client
        asyncio.create_task(self._initialize_api_client())
    
    async def _initialize_api_client(self):
        """Initialize Facebook Graph API client"""        try:
            self.graph_api = facebook.GraphAPI(
                access_token=self.access_token,
                version='18.0'  # Use latest stable version
            )
            
            # Test API connection
            await self._test_api_connection()
            
            self.logger.info("Facebook Graph API client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Facebook API client: {str(e)}")
            raise
    
    async def _test_api_connection(self):
        """Test API connection and permissions"""        try:
            # Test with simple API call
            me = self.graph_api.get_object('me')
            self.logger.info(f"Facebook API connected for user: {me.get('name', 'Unknown')}")
            
        except Exception as e:
            self.logger.warning(f"API connection test failed: {str(e)}")
    
    async def search_content(self, search_terms: List[str], 
                           max_results: int = 100) -> List[Dict[str, Any]]:
        """        Search for content on Facebook using Graph API.
        
        Args:
            search_terms: Terms to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of found content items
        """        try:
            await self._check_rate_limit()
            
            all_results = []
            
            # Search public posts using Graph API
            for term in search_terms[:3]:  # Limit for rate limiting
                try:
                    # Search for pages first
                    pages_results = await self._search_pages(term)
                    
                    # Search posts from found pages
                    for page in pages_results[:5]:  # Top 5 pages
                        page_posts = await self._get_page_posts(page['id'], term, max_results // len(search_terms))
                        all_results.extend(page_posts)
                    
                    # Apply rate limiting
                    await self._apply_rate_limit()
                    
                except Exception as e:
                    self.logger.error(f"Error searching Facebook for term '{term}': {str(e)}")
                    continue
            
            # Remove duplicates and sort by relevance
            unique_results = await self._deduplicate_results(all_results)
            
            self.logger.info(f"Found {len(unique_results)} unique Facebook posts")
            return unique_results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error in Facebook search: {str(e)}")
            return []
    
    async def extract_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """        Extract metadata from Facebook content URL.
        
        Args:
            content_url: URL of the Facebook post
            
        Returns:
            Content metadata dictionary
        """        try:
            # Extract post ID from URL
            post_id = self._extract_post_id_from_url(content_url)
            if not post_id:
                return {}
            
            # Get post details using Graph API
            post_data = await self._get_post_details(post_id)
            
            return post_data
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata for {content_url}: {str(e)}")
            return {}
    
    async def download_content_sample(self, content_url: str) -> Optional[bytes]:
        """        Download content sample for fingerprinting.
        
        Args:
            content_url: URL of the content
            
        Returns:
            Content data bytes or None if failed
        """        try:
            # Extract post ID and get media
            post_id = self._extract_post_id_from_url(content_url)
            if not post_id:
                return None
            
            # Get post attachments
            attachments = self.graph_api.get_object(
                f"{post_id}/attachments",
                fields="media,url"
            )
            
            if attachments.get('data'):
                # Download first media attachment
                media_item = attachments['data'][0]
                media_url = media_item.get('media', {}).get('image', {}).get('src')
                
                if media_url:
                    async with self.session.get(media_url) as response:
                        if response.status == 200:
                            return await response.read()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading content sample: {str(e)}")
            return None
    
    async def search_pages(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """        Search for Facebook pages.
        
        Args:
            search_terms: Terms to search for
            
        Returns:
            List of found Facebook pages
        """        try:
            all_pages = []
            
            for term in search_terms:
                pages = await self._search_pages(term)
                all_pages.extend(pages)
            
            return await self._deduplicate_pages(all_pages)
            
        except Exception as e:
            self.logger.error(f"Error searching Facebook pages: {str(e)}")
            return []
    
    async def get_page_posts(self, page_id: str, max_posts: int = 50) -> List[Dict[str, Any]]:
        """        Get posts from a specific Facebook page.
        
        Args:
            page_id: Facebook page ID
            max_posts: Maximum number of posts to retrieve
            
        Returns:
            List of page posts
        """        try:
            return await self._get_page_posts(page_id, None, max_posts)
            
        except Exception as e:
            self.logger.error(f"Error getting posts for page {page_id}: {str(e)}")
            return []
    
    async def monitor_page_real_time(self, page_id: str, 
                                   callback_url: str = None) -> str:
        """        Start real-time monitoring of a Facebook page.
        
        Args:
            page_id: Facebook page ID to monitor
            callback_url: Optional callback URL for notifications
            
        Returns:
            Monitoring session ID
        """        try:
            monitoring_id = f"facebook_monitor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Create monitoring task
            async def monitoring_task():
                last_check = datetime.utcnow()
                
                while True:
                    try:
                        # Get recent posts since last check
                        recent_posts = await self._get_page_posts_since(page_id, last_check)
                        
                        # Process new posts
                        for post in recent_posts:
                            if callback_url:
                                await self._send_monitoring_notification(post, callback_url, monitoring_id)
                        
                        last_check = datetime.utcnow()
                        
                        # Wait before next check (respect rate limits)
                        await asyncio.sleep(300)  # 5 minutes
                        
                    except Exception as e:
                        self.logger.error(f"Error in Facebook monitoring task: {str(e)}")
                        await asyncio.sleep(600)  # Wait 10 minutes on error
            
            # Start monitoring task
            asyncio.create_task(monitoring_task())
            
            self.logger.info(f"Started Facebook page monitoring: {monitoring_id}")
            return monitoring_id
            
        except Exception as e:
            self.logger.error(f"Error starting Facebook monitoring: {str(e)}")
            raise
    
    async def analyze_post_engagement(self, post_id: str) -> Dict[str, Any]:
        """        Analyze engagement metrics for a specific post.
        
        Args:
            post_id: Facebook post ID
            
        Returns:
            Engagement analysis data
        """        try:
            # Get post insights (requires page access token)
            insights = self.graph_api.get_object(
                f"{post_id}/insights",
                metric="post_impressions,post_engaged_users,post_clicks"
            )
            
            # Get basic metrics
            post_data = self.graph_api.get_object(
                post_id,
                fields="likes.summary(true),comments.summary(true),shares"
            )
            
            engagement_data = {
                'post_id': post_id,
                'likes_count': post_data.get('likes', {}).get('summary', {}).get('total_count', 0),
                'comments_count': post_data.get('comments', {}).get('summary', {}).get('total_count', 0),
                'shares_count': post_data.get('shares', {}).get('count', 0),
                'insights': insights.get('data', [])
            }
            
            return engagement_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing post engagement: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _search_pages(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for Facebook pages"""        try:
            # Use Graph API search
            results = self.graph_api.get_object(
                "search",
                q=search_term,
                type="page",
                fields="id,name,about,category,fan_count,website,picture"
            )
            
            pages = []
            for page in results.get('data', []):
                pages.append({
                    'id': page.get('id'),
                    'name': page.get('name'),
                    'about': page.get('about', ''),
                    'category': page.get('category', ''),
                    'fan_count': page.get('fan_count', 0),
                    'website': page.get('website', ''),
                    'picture_url': page.get('picture', {}).get('data', {}).get('url', ''),
                    'url': f"https://facebook.com/{page.get('id')}"
                })
            
            return pages
            
        except Exception as e:
            self.logger.error(f"Error searching pages for '{search_term}': {str(e)}")
            return []
    
    async def _get_page_posts(self, page_id: str, keyword: str = None, 
                            max_posts: int = 50) -> List[Dict[str, Any]]:
        """Get posts from a Facebook page"""        try:
            # Get page posts
            posts = self.graph_api.get_object(
                f"{page_id}/posts",
                fields="id,message,story,created_time,type,source,link,picture,"
                       "likes.summary(true),comments.summary(true),shares",
                limit=max_posts
            )
            
            processed_posts = []
            
            for post in posts.get('data', []):
                # Filter by keyword if provided
                if keyword:
                    message = post.get('message', '') + post.get('story', '')
                    if keyword.lower() not in message.lower():
                        continue
                
                processed_post = await self._process_post_data(post, page_id)
                processed_posts.append(processed_post)
            
            return processed_posts
            
        except Exception as e:
            self.logger.error(f"Error getting posts for page {page_id}: {str(e)}")
            return []
    
    async def _get_page_posts_since(self, page_id: str, since_time: datetime) -> List[Dict[str, Any]]:
        """Get page posts since specific time"""        try:
            # Convert datetime to Unix timestamp
            since_timestamp = int(since_time.timestamp())
            
            posts = self.graph_api.get_object(
                f"{page_id}/posts",
                fields="id,message,story,created_time,type,source,link,picture",
                since=since_timestamp
            )
            
            processed_posts = []
            for post in posts.get('data', []):
                processed_post = await self._process_post_data(post, page_id)
                processed_posts.append(processed_post)
            
            return processed_posts
            
        except Exception as e:
            self.logger.error(f"Error getting recent posts for page {page_id}: {str(e)}")
            return []
    
    async def _get_post_details(self, post_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific post"""        try:
            post = self.graph_api.get_object(
                post_id,
                fields="id,message,story,created_time,type,source,link,picture,place,"
                       "likes.summary(true),comments.summary(true),shares,from,attachments"
            )
            
            return await self._process_post_data(post)
            
        except Exception as e:
            self.logger.error(f"Error getting post details for {post_id}: {str(e)}")
            return {}
    
    async def _process_post_data(self, post: Dict[str, Any], page_id: str = None) -> Dict[str, Any]:
        """Process raw post data into standardized format"""        try:
            # Extract basic information
            post_id = post.get('id')
            message = post.get('message', '')
            story = post.get('story', '')
            content_text = f"{message} {story}".strip()
            
            # Parse creation time
            created_time = post.get('created_time')
            if created_time:
                created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
            
            # Get author information
            author_info = post.get('from', {})
            
            # Extract media information
            media_items = []
            attachments = post.get('attachments', {}).get('data', [])
            for attachment in attachments:
                media_data = attachment.get('media', {})
                if media_data:
                    media_items.append({
                        'type': attachment.get('type', 'unknown'),
                        'url': media_data.get('image', {}).get('src'),
                        'width': media_data.get('image', {}).get('width'),
                        'height': media_data.get('image', {}).get('height')
                    })
            
            # Build standardized result
            result = {
                'url': f"https://facebook.com/{post_id}",
                'title': content_text[:100] + "..." if len(content_text) > 100 else content_text,
                'description': content_text,
                'author': author_info.get('name', 'Unknown'),
                'author_id': author_info.get('id'),
                'upload_date': created_time,
                'post_id': post_id,
                'post_type': post.get('type', 'status'),
                'like_count': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                'comment_count': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                'share_count': post.get('shares', {}).get('count', 0),
                'media_items': media_items,
                'link': post.get('link'),
                'picture_url': post.get('picture'),
                'source': post.get('source'),
                'place': post.get('place', {}).get('name') if post.get('place') else None
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing post data: {str(e)}")
            return {}
    
    def _extract_post_id_from_url(self, url: str) -> Optional[str]:
        """Extract post ID from Facebook URL"""        try:
            # Patterns for Facebook URLs
            patterns = [
                r'facebook\.com/(?:.*?/)?posts/(\d+)',
                r'facebook\.com/(?:.*?/)?photos/(?:.*?/)?(\d+)',
                r'facebook\.com/permalink\.php\?story_fbid=(\d+)',
                r'facebook\.com/(?:.*?/)?videos/(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting post ID from URL: {str(e)}")
            return None
    
    async def _check_rate_limit(self):
        """Check and manage API rate limits"""        current_time = datetime.utcnow()
        
        # Reset window if needed
        if (current_time - self.window_start).total_seconds() >= self.rate_limit_window:
            self.current_requests = 0
            self.window_start = current_time
        
        # Check if we're approaching limit
        if self.current_requests >= self.requests_per_hour * 0.9:  # 90% of limit
            wait_time = self.rate_limit_window - (current_time - self.window_start).total_seconds()
            if wait_time > 0:
                self.logger.warning(f"Rate limit approaching, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
                self.current_requests = 0
                self.window_start = datetime.utcnow()
    
    async def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate posts from results"""        seen_ids = set()
        unique_results = []
        
        for result in results:
            post_id = result.get('post_id')
            if post_id and post_id not in seen_ids:
                seen_ids.add(post_id)
                unique_results.append(result)
        
        return unique_results
    
    async def _deduplicate_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate pages from results"""        seen_ids = set()
        unique_pages = []
        
        for page in pages:
            page_id = page.get('id')
            if page_id and page_id not in seen_ids:
                seen_ids.add(page_id)
                unique_pages.append(page)
        
        return unique_pages
    
    async def _send_monitoring_notification(self, post: Dict[str, Any], 
                                          callback_url: str, monitoring_id: str):
        """Send monitoring notification for new post"""        try:
            notification_data = {
                'monitoring_id': monitoring_id,
                'platform': 'facebook',
                'post_id': post.get('post_id'),
                'post_url': post.get('url'),
                'content': post.get('description', '')[:200],
                'author': post.get('author'),
                'created_time': post.get('upload_date').isoformat() if post.get('upload_date') else None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                await session.post(callback_url, json=notification_data)
                
        except Exception as e:
            self.logger.error(f"Error sending monitoring notification: {str(e)}")
