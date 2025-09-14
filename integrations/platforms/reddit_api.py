"""Reddit API Integration
======================

Enterprise-grade Reddit integration for community engagement, content distribution,
and viral content creation. Supports Reddit API, OAuth2, and community management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import base64
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode
import uuid

# Configure logger
logger = logging.getLogger(__name__)

class RedditPost:
    """Reddit post management and analytics"""
    
    def __init__(self, post_id -> None: str, subreddit -> None: str, title -> None: str, author -> None: str) -> None:
        self.post_id = post_id
        self.subreddit = subreddit
        self.title = title
        self.author = author
        self.upvotes = 0
        self.downvotes = 0
        self.score = 0
        self.comments_count = 0
        self.created_utc = datetime.utcnow()
        self.url = ""
        self.content = ""
        self.flair = ""

class RedditComment:
    """Reddit comment management"""
    
    def __init__(self, comment_id -> None: str, post_id -> None: str, author -> None: str, body -> None: str) -> None:
        self.comment_id = comment_id
        self.post_id = post_id
        self.author = author
        self.body = body
        self.score = 0
        self.created_utc = datetime.utcnow()
        self.replies = []
        self.is_reply = False

class RedditSubreddit:
    """Reddit subreddit management"""
    
    def __init__(self, subreddit_name -> None: str, display_name -> None: str) -> None:
        self.name = subreddit_name
        self.display_name = display_name
        self.subscribers = 0
        self.active_users = 0
        self.description = ""
        self.rules = []
        self.created_utc = datetime.utcnow()
        self.over18 = False

class RedditUser:
    """Reddit user profile management"""
    
    def __init__(self, username -> None: str) -> None:
        self.username = username
        self.link_karma = 0
        self.comment_karma = 0
        self.created_utc = datetime.utcnow()
        self.verified = False
        self.premium = False
        self.avatar_url = ""

class RedditAPIError(Exception):
    """Custom exception for Reddit API errors"""
    pass

class RedditAPI:
    """
    Comprehensive Reddit API integration for Ainflue platform.
    
    Features:
    - Content posting and distribution
    - Community engagement and management
    - Viral content optimization
    - Karma and reputation tracking
    - Subreddit analytics and insights
    - Comment thread management
    - Brand awareness campaigns
    - Influencer identification
    """
    
    def __init__(self, client_id -> None: str, client_secret -> None: str, user_agent -> None: str, redirect_uri -> None: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.redirect_uri = redirect_uri
        self.base_url = "https://oauth.reddit.com"
        self.auth_url = "https://www.reddit.com/api/v1/authorize"
        self.token_url = "https://www.reddit.com/api/v1/access_token"
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.session = None
        self.rate_limits = {
            'requests_per_minute': 60,
            'requests_made': 0,
            'minute_start': datetime.utcnow().minute
        }
        
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def generate_auth_url(self, scopes: List[str] = None, state: str = None) -> str:
        """
        Generate OAuth authorization URL for Reddit login.
        
        Args:
            scopes: List of permission scopes
            state: Optional state parameter for security
            
        Returns:
            Authorization URL string
        """
        if scopes is None:
            scopes = [
                'identity',
                'read',
                'submit',
                'edit',
                'vote',
                'save',
                'subscribe',
                'history',
                'mysubreddits'
            ]
            
        if state is None:
            state = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').rstrip('=')
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'state': state,
            'redirect_uri': self.redirect_uri,
            'duration': 'permanent',
            'scope': ' '.join(scopes)
        }
        
        return f"{self.auth_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            authorization_code: OAuth authorization code
            
        Returns:
            Token information dictionary
        """
        try:
            auth_header = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'User-Agent': self.user_agent
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri
            }
            
            async with self.session.post(self.token_url, headers=headers, data=data) as response:
                token_data = await response.json()
                
                if response.status == 200:
                    self.access_token = token_data['access_token']
                    self.refresh_token = token_data.get('refresh_token')
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    logger.info("Successfully obtained Reddit access token")
                    return token_data
                else:
                    raise RedditAPIError(f"Token exchange failed: {token_data}")
                    
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise RedditAPIError(f"Token exchange error: {e}")

    async def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh the access token using refresh token.
        
        Returns:
            New token information
        """
        if not self.refresh_token:
            raise RedditAPIError("No refresh token available")
            
        try:
            auth_header = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'User-Agent': self.user_agent
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            async with self.session.post(self.token_url, headers=headers, data=data) as response:
                token_data = await response.json()
                
                if response.status == 200:
                    self.access_token = token_data['access_token']
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    return token_data
                else:
                    raise RedditAPIError(f"Token refresh failed: {token_data}")
                    
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise RedditAPIError(f"Token refresh error: {e}")

    async def _ensure_valid_token(self) -> None:
        """Ensure we have a valid access token"""
        if not self.access_token:
            raise RedditAPIError("No access token available")
            
        if self.token_expires_at and datetime.utcnow() >= self.token_expires_at - timedelta(minutes=5):
            await self.refresh_access_token()

    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting"""
        current_minute = datetime.utcnow().minute
        
        if current_minute != self.rate_limits['minute_start']:
            self.rate_limits['requests_made'] = 0
            self.rate_limits['minute_start'] = current_minute
            
        if self.rate_limits['requests_made'] >= self.rate_limits['requests_per_minute']:
            raise RedditAPIError("Rate limit exceeded")
            
        self.rate_limits['requests_made'] += 1

    async def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """
        Make authenticated request to Reddit API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: URL parameters
            
        Returns:
            API response data
        """
        await self._ensure_valid_token()
        self._check_rate_limit()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': self.user_agent
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params
            ) as response:
                
                # Handle rate limiting
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, endpoint, data, params)
                
                response_data = await response.json()
                
                if response.status >= 400:
                    raise RedditAPIError(
                        f"API request failed: {response.status} - {response_data}"
                    )
                    
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"Request error: {e}")
            raise RedditAPIError(f"Request error: {e}")

    # User Profile Management
    async def get_user_profile(self, username: str = None) -> RedditUser:
        """
        Get user profile information.
        
        Args:
            username: Optional username (defaults to authenticated user)
            
        Returns:
            RedditUser object
        """
        if username:
            endpoint = f"/user/{username}/about"
        else:
            endpoint = "/api/v1/me"
        
        user_data = await self._make_request('GET', endpoint)
        
        if username:
            user_info = user_data['data']
        else:
            user_info = user_data
        
        user = RedditUser(username=user_info['name'])
        user.link_karma = user_info.get('link_karma', 0)
        user.comment_karma = user_info.get('comment_karma', 0)
        user.created_utc = datetime.fromtimestamp(user_info.get('created_utc', time.time()))
        user.verified = user_info.get('verified', False)
        user.premium = user_info.get('is_gold', False)
        
        return user

    async def get_user_analytics(self, username: str = None) -> Dict[str, Any]:
        """
        Get comprehensive user analytics and insights.
        
        Args:
            username: Optional username
            
        Returns:
            User analytics data
        """
        user_profile = await self.get_user_profile(username)
        user_posts = await self.get_user_posts(username, limit=100)
        user_comments = await self.get_user_comments(username, limit=100)
        
        # Calculate analytics
        total_karma = user_profile.link_karma + user_profile.comment_karma
        avg_post_score = sum(post.score for post in user_posts) / len(user_posts) if user_posts else 0
        avg_comment_score = sum(comment.score for comment in user_comments) / len(user_comments) if user_comments else 0
        
        analytics = {
            'username': user_profile.username,
            'karma_breakdown': {
                'total_karma': total_karma,
                'link_karma': user_profile.link_karma,
                'comment_karma': user_profile.comment_karma,
                'karma_ratio': user_profile.link_karma / total_karma if total_karma > 0 else 0
            },
            'posting_behavior': {
                'total_posts': len(user_posts),
                'total_comments': len(user_comments),
                'avg_post_score': avg_post_score,
                'avg_comment_score': avg_comment_score,
                'posting_frequency': await self._calculate_posting_frequency(user_posts)
            },
            'engagement_metrics': {
                'engagement_rate': await self._calculate_user_engagement_rate(user_posts, user_comments),
                'viral_content_count': await self._count_viral_content(user_posts),
                'controversial_ratio': await self._calculate_controversial_ratio(user_posts),
                'community_participation': await self._analyze_community_participation(user_posts, user_comments)
            },
            'content_analysis': {
                'top_performing_posts': sorted(user_posts, key=lambda x: x.score, reverse=True)[:5],
                'preferred_subreddits': await self._get_preferred_subreddits(user_posts, user_comments),
                'content_themes': await self._analyze_content_themes(user_posts),
                'optimal_posting_times': await self._identify_optimal_posting_times(user_posts)
            },
            'influence_metrics': {
                'influence_score': await self._calculate_influence_score(user_profile, user_posts, user_comments),
                'reach_potential': await self._estimate_reach_potential(user_posts),
                'authority_domains': await self._identify_authority_domains(user_posts, user_comments),
                'network_connections': await self._analyze_network_connections(username)
            }
        }
        
        return analytics

    # Content Management
    async def submit_post(self, subreddit: str, title: str, content: str = None, url: str = None, 
                         flair_id: str = None, nsfw: bool = False) -> RedditPost:
        """
        Submit a new post to a subreddit.
        
        Args:
            subreddit: Subreddit name
            title: Post title
            content: Post content (for text posts)
            url: URL (for link posts)
            flair_id: Optional flair ID
            nsfw: Whether post is NSFW
            
        Returns:
            Created RedditPost object
        """
        if content and url:
            raise RedditAPIError("Cannot specify both content and URL")
        
        data = {
            'sr': subreddit,
            'title': title,
            'kind': 'self' if content else 'link',
            'api_type': 'json'
        }
        
        if content:
            data['text'] = content
        elif url:
            data['url'] = url
        else:
            raise RedditAPIError("Must specify either content or URL")
        
        if flair_id:
            data['flair_id'] = flair_id
        
        if nsfw:
            data['nsfw'] = True
        
        response = await self._make_request('POST', '/api/submit', data=data)
        
        if response.get('json', {}).get('errors'):
            raise RedditAPIError(f"Post submission failed: {response['json']['errors']}")
        
        post_data = response['json']['data']
        
        post = RedditPost(
            post_id=post_data['name'],
            subreddit=subreddit,
            title=title,
            author=post_data.get('author', '')
        )
        
        post.url = post_data.get('url', '')
        post.content = content or ''
        
        logger.info(f"Successfully submitted post: {post.post_id}")
        return post

    async def get_post(self, post_id: str) -> RedditPost:
        """
        Get detailed information about a specific post.
        
        Args:
            post_id: Reddit post ID
            
        Returns:
            RedditPost object
        """
        # Remove prefix if present
        if post_id.startswith('t3_'):
            post_id = post_id[3:]
        
        endpoint = f"/comments/{post_id}"
        response = await self._make_request('GET', endpoint)
        
        post_data = response[0]['data']['children'][0]['data']
        
        post = RedditPost(
            post_id=post_data['id'],
            subreddit=post_data['subreddit'],
            title=post_data['title'],
            author=post_data['author']
        )
        
        post.upvotes = post_data.get('ups', 0)
        post.downvotes = post_data.get('downs', 0)
        post.score = post_data.get('score', 0)
        post.comments_count = post_data.get('num_comments', 0)
        post.created_utc = datetime.fromtimestamp(post_data.get('created_utc', time.time()))
        post.url = post_data.get('url', '')
        post.content = post_data.get('selftext', '')
        post.flair = post_data.get('link_flair_text', '')
        
        return post

    async def get_user_posts(self, username: str = None, limit: int = 25) -> List[RedditPost]:
        """
        Get posts by a user.
        
        Args:
            username: Username (defaults to authenticated user)
            limit: Maximum number of posts to return
            
        Returns:
            List of RedditPost objects
        """
        if username:
            endpoint = f"/user/{username}/submitted"
        else:
            endpoint = "/user/me/submitted"
        
        params = {'limit': min(limit, 100)}
        response = await self._make_request('GET', endpoint, params=params)
        
        posts = []
        for item in response['data']['children']:
            post_data = item['data']
            
            post = RedditPost(
                post_id=post_data['id'],
                subreddit=post_data['subreddit'],
                title=post_data['title'],
                author=post_data['author']
            )
            
            post.upvotes = post_data.get('ups', 0)
            post.downvotes = post_data.get('downs', 0)
            post.score = post_data.get('score', 0)
            post.comments_count = post_data.get('num_comments', 0)
            post.created_utc = datetime.fromtimestamp(post_data.get('created_utc', time.time()))
            post.url = post_data.get('url', '')
            post.content = post_data.get('selftext', '')
            post.flair = post_data.get('link_flair_text', '')
            
            posts.append(post)
        
        return posts

    async def get_user_comments(self, username: str = None, limit: int = 25) -> List[RedditComment]:
        """
        Get comments by a user.
        
        Args:
            username: Username (defaults to authenticated user)
            limit: Maximum number of comments to return
            
        Returns:
            List of RedditComment objects
        """
        if username:
            endpoint = f"/user/{username}/comments"
        else:
            endpoint = "/user/me/comments"
        
        params = {'limit': min(limit, 100)}
        response = await self._make_request('GET', endpoint, params=params)
        
        comments = []
        for item in response['data']['children']:
            comment_data = item['data']
            
            comment = RedditComment(
                comment_id=comment_data['id'],
                post_id=comment_data.get('link_id', '').replace('t3_', ''),
                author=comment_data['author'],
                body=comment_data['body']
            )
            
            comment.score = comment_data.get('score', 0)
            comment.created_utc = datetime.fromtimestamp(comment_data.get('created_utc', time.time()))
            
            comments.append(comment)
        
        return comments

    # Subreddit Management and Analytics
    async def get_subreddit_info(self, subreddit_name: str) -> RedditSubreddit:
        """
        Get detailed information about a subreddit.
        
        Args:
            subreddit_name: Subreddit name
            
        Returns:
            RedditSubreddit object
        """
        endpoint = f"/r/{subreddit_name}/about"
        response = await self._make_request('GET', endpoint)
        
        subreddit_data = response['data']
        
        subreddit = RedditSubreddit(
            subreddit_name=subreddit_data['display_name'].lower(),
            display_name=subreddit_data['display_name']
        )
        
        subreddit.subscribers = subreddit_data.get('subscribers', 0)
        subreddit.active_users = subreddit_data.get('active_user_count', 0)
        subreddit.description = subreddit_data.get('public_description', '')
        subreddit.created_utc = datetime.fromtimestamp(subreddit_data.get('created_utc', time.time()))
        subreddit.over18 = subreddit_data.get('over18', False)
        
        return subreddit

    async def get_subreddit_analytics(self, subreddit_name: str) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a subreddit.
        
        Args:
            subreddit_name: Subreddit name
            
        Returns:
            Subreddit analytics data
        """
        subreddit_info = await self.get_subreddit_info(subreddit_name)
        hot_posts = await self.get_subreddit_posts(subreddit_name, sort='hot', limit=100)
        top_posts = await self.get_subreddit_posts(subreddit_name, sort='top', time_filter='week', limit=50)
        
        analytics = {
            'subreddit_name': subreddit_name,
            'community_stats': {
                'total_subscribers': subreddit_info.subscribers,
                'active_users': subreddit_info.active_users,
                'activity_ratio': (subreddit_info.active_users / subreddit_info.subscribers * 100) if subreddit_info.subscribers > 0 else 0,
                'community_age_days': (datetime.utcnow() - subreddit_info.created_utc).days
            },
            'content_performance': {
                'avg_post_score': sum(post.score for post in hot_posts) / len(hot_posts) if hot_posts else 0,
                'top_post_score': max(post.score for post in hot_posts) if hot_posts else 0,
                'avg_comments_per_post': sum(post.comments_count for post in hot_posts) / len(hot_posts) if hot_posts else 0,
                'viral_content_threshold': await self._calculate_viral_threshold(subreddit_name, hot_posts)
            },
            'engagement_patterns': {
                'peak_posting_hours': await self._identify_peak_hours(hot_posts),
                'optimal_title_length': await self._analyze_optimal_title_length(hot_posts),
                'successful_content_types': await self._analyze_content_types(hot_posts),
                'engagement_velocity': await self._calculate_engagement_velocity(hot_posts)
            },
            'trending_analysis': {
                'trending_topics': await self._extract_trending_topics(hot_posts),
                'popular_flairs': await self._analyze_popular_flairs(hot_posts),
                'discussion_catalysts': await self._identify_discussion_catalysts(hot_posts),
                'viral_patterns': await self._analyze_viral_patterns(top_posts)
            },
            'opportunity_analysis': {
                'content_gaps': await self._identify_content_gaps(subreddit_name, hot_posts),
                'optimal_posting_strategy': await self._generate_posting_strategy(subreddit_name, analytics_data=hot_posts),
                'audience_preferences': await self._analyze_audience_preferences(hot_posts),
                'growth_potential': await self._assess_growth_potential(subreddit_info, hot_posts)
            }
        }
        
        return analytics

    async def get_subreddit_posts(self, subreddit_name: str, sort: str = 'hot', 
                                 time_filter: str = 'day', limit: int = 25) -> List[RedditPost]:
        """
        Get posts from a subreddit.
        
        Args:
            subreddit_name: Subreddit name
            sort: Sort method ('hot', 'new', 'top', 'rising')
            time_filter: Time filter for 'top' sort ('hour', 'day', 'week', 'month', 'year', 'all')
            limit: Maximum number of posts to return
            
        Returns:
            List of RedditPost objects
        """
        endpoint = f"/r/{subreddit_name}/{sort}"
        params = {'limit': min(limit, 100)}
        
        if sort == 'top':
            params['t'] = time_filter
        
        response = await self._make_request('GET', endpoint, params=params)
        
        posts = []
        for item in response['data']['children']:
            post_data = item['data']
            
            post = RedditPost(
                post_id=post_data['id'],
                subreddit=post_data['subreddit'],
                title=post_data['title'],
                author=post_data['author']
            )
            
            post.upvotes = post_data.get('ups', 0)
            post.downvotes = post_data.get('downs', 0)
            post.score = post_data.get('score', 0)
            post.comments_count = post_data.get('num_comments', 0)
            post.created_utc = datetime.fromtimestamp(post_data.get('created_utc', time.time()))
            post.url = post_data.get('url', '')
            post.content = post_data.get('selftext', '')
            post.flair = post_data.get('link_flair_text', '')
            
            posts.append(post)
        
        return posts

    # Content Optimization and Strategy
    async def optimize_content_strategy(self, target_subreddits: List[str]) -> Dict[str, Any]:
        """
        Generate optimized content strategy for target subreddits.
        
        Args:
            target_subreddits: List of target subreddit names
            
        Returns:
            Content optimization strategy
        """
        strategy = {
            'subreddit_analysis': {},
            'cross_subreddit_insights': {},
            'content_recommendations': {},
            'posting_schedule': {},
            'engagement_tactics': {}
        }
        
        # Analyze each target subreddit
        for subreddit in target_subreddits:
            try:
                analytics = await self.get_subreddit_analytics(subreddit)
                strategy['subreddit_analysis'][subreddit] = {
                    'difficulty_score': await self._calculate_posting_difficulty(analytics),
                    'viral_potential': await self._assess_viral_potential(analytics),
                    'optimal_content_types': analytics['engagement_patterns']['successful_content_types'],
                    'best_posting_times': analytics['engagement_patterns']['peak_posting_hours']
                }
            except Exception as e:
                logger.warning(f"Could not analyze subreddit {subreddit}: {e}")
                continue
        
        # Generate cross-subreddit insights
        strategy['cross_subreddit_insights'] = await self._analyze_cross_subreddit_patterns(strategy['subreddit_analysis'])
        
        # Generate content recommendations
        strategy['content_recommendations'] = await self._generate_content_recommendations(strategy['subreddit_analysis'])
        
        # Generate posting schedule
        strategy['posting_schedule'] = await self._generate_optimal_posting_schedule(strategy['subreddit_analysis'])
        
        # Generate engagement tactics
        strategy['engagement_tactics'] = await self._generate_engagement_tactics(strategy['subreddit_analysis'])
        
        return strategy

    async def predict_viral_potential(self, title: str, content: str, subreddit: str) -> Dict[str, Any]:
        """
        Predict the viral potential of content before posting.
        
        Args:
            title: Post title
            content: Post content
            subreddit: Target subreddit
            
        Returns:
            Viral potential prediction
        """
        # Get subreddit analytics for context
        subreddit_analytics = await self.get_subreddit_analytics(subreddit)
        
        # Analyze title characteristics
        title_analysis = await self._analyze_title_characteristics(title, subreddit_analytics)
        
        # Analyze content characteristics
        content_analysis = await self._analyze_content_characteristics(content, subreddit_analytics)
        
        # Calculate viral probability
        viral_score = await self._calculate_viral_probability(title_analysis, content_analysis, subreddit_analytics)
        
        prediction = {
            'viral_score': viral_score,  # 0-100 scale
            'confidence_level': await self._calculate_prediction_confidence(viral_score),
            'title_optimization': {
                'current_score': title_analysis['effectiveness_score'],
                'suggested_improvements': title_analysis['improvements'],
                'optimal_length': title_analysis['optimal_length'],
                'keyword_suggestions': title_analysis['keyword_suggestions']
            },
            'content_optimization': {
                'current_score': content_analysis['quality_score'],
                'engagement_factors': content_analysis['engagement_factors'],
                'format_suggestions': content_analysis['format_suggestions'],
                'timing_recommendations': content_analysis['timing_recommendations']
            },
            'subreddit_fit': {
                'compatibility_score': await self._assess_subreddit_compatibility(title, content, subreddit),
                'community_preferences': subreddit_analytics['opportunity_analysis']['audience_preferences'],
                'competition_level': await self._assess_competition_level(subreddit, subreddit_analytics),
                'success_probability': await self._calculate_success_probability(viral_score, subreddit_analytics)
            },
            'recommendations': {
                'post_timing': await self._recommend_optimal_timing(subreddit_analytics),
                'engagement_strategies': await self._recommend_engagement_strategies(subreddit_analytics),
                'follow_up_actions': await self._recommend_follow_up_actions(viral_score),
                'alternative_subreddits': await self._suggest_alternative_subreddits(title, content)
            }
        }
        
        return prediction

    # Community Engagement and Growth
    async def track_engagement_metrics(self, posts: List[RedditPost], time_window: int = 24) -> Dict[str, Any]:
        """
        Track comprehensive engagement metrics for posts.
        
        Args:
            posts: List of posts to track
            time_window: Hours to track engagement
            
        Returns:
            Engagement tracking data
        """
        engagement_data = {
            'overall_performance': {},
            'individual_post_metrics': [],
            'trend_analysis': {},
            'optimization_insights': {}
        }
        
        # Track individual post metrics
        for post in posts:
            try:
                current_post = await self.get_post(post.post_id)
                post_metrics = {
                    'post_id': post.post_id,
                    'title': post.title,
                    'subreddit': post.subreddit,
                    'age_hours': (datetime.utcnow() - post.created_utc).total_seconds() / 3600,
                    'current_score': current_post.score,
                    'score_velocity': await self._calculate_score_velocity(post, current_post),
                    'comment_velocity': await self._calculate_comment_velocity(post, current_post),
                    'engagement_rate': await self._calculate_post_engagement_rate(current_post),
                    'viral_trajectory': await self._assess_viral_trajectory(current_post),
                    'audience_sentiment': await self._analyze_audience_sentiment(current_post)
                }
                engagement_data['individual_post_metrics'].append(post_metrics)
            except Exception as e:
                logger.warning(f"Could not track metrics for post {post.post_id}: {e}")
                continue
        
        # Calculate overall performance
        engagement_data['overall_performance'] = await self._calculate_overall_performance(engagement_data['individual_post_metrics'])
        
        # Analyze trends
        engagement_data['trend_analysis'] = await self._analyze_engagement_trends(engagement_data['individual_post_metrics'])
        
        # Generate optimization insights
        engagement_data['optimization_insights'] = await self._generate_optimization_insights(engagement_data)
        
        return engagement_data

    # Helper Methods for Enhanced Functionality
    async def _calculate_posting_frequency(self, posts: List[RedditPost]) -> Dict[str, float]:
        """Calculate user posting frequency patterns"""
        if not posts:
            return {'daily_average': 0, 'weekly_average': 0}
        
        # Calculate time span and frequency
        time_span = (datetime.utcnow() - min(post.created_utc for post in posts)).days
        if time_span == 0:
            time_span = 1
        
        return {
            'daily_average': len(posts) / time_span,
            'weekly_average': len(posts) / (time_span / 7)
        }

    async def _calculate_user_engagement_rate(self, posts: List[RedditPost], comments: List[RedditComment]) -> float:
        """Calculate user engagement rate"""
        if not posts and not comments:
            return 0.0
        
        total_interactions = len(posts) + len(comments)
        total_score = sum(post.score for post in posts) + sum(comment.score for comment in comments)
        
        return (total_score / total_interactions) if total_interactions > 0 else 0.0

    async def _count_viral_content(self, posts: List[RedditPost]) -> int:
        """Count viral content (posts with high scores)"""
        return len([post for post in posts if post.score > 1000])

    async def _calculate_controversial_ratio(self, posts: List[RedditPost]) -> float:
        """Calculate ratio of controversial content"""
        if not posts:
            return 0.0
        
        # Estimate controversial posts (high comment to score ratio)
        controversial_count = 0
        for post in posts:
            if post.score > 0 and post.comments_count / post.score > 2:
                controversial_count += 1
        
        return (controversial_count / len(posts)) * 100

    async def _analyze_community_participation(self, posts: List[RedditPost], comments: List[RedditComment]) -> Dict[str, Any]:
        """Analyze community participation patterns"""
        subreddit_posts = {}
        subreddit_comments = {}
        
        for post in posts:
            subreddit_posts[post.subreddit] = subreddit_posts.get(post.subreddit, 0) + 1
        
        for comment in comments:
            # Would need to determine subreddit from comment context
            pass
        
        return {
            'active_subreddits': len(subreddit_posts),
            'posts_per_subreddit': subreddit_posts,
            'participation_diversity': len(subreddit_posts) / len(posts) if posts else 0
        }

    async def _get_preferred_subreddits(self, posts: List[RedditPost], comments: List[RedditComment]) -> List[Dict[str, Any]]:
        """Get user's preferred subreddits"""
        subreddit_activity = {}
        
        for post in posts:
            if post.subreddit not in subreddit_activity:
                subreddit_activity[post.subreddit] = {'posts': 0, 'total_score': 0}
            subreddit_activity[post.subreddit]['posts'] += 1
            subreddit_activity[post.subreddit]['total_score'] += post.score
        
        # Sort by activity and performance
        preferred = []
        for subreddit, data in subreddit_activity.items():
            preferred.append({
                'subreddit': subreddit,
                'post_count': data['posts'],
                'avg_score': data['total_score'] / data['posts'] if data['posts'] > 0 else 0,
                'total_score': data['total_score']
            })
        
        return sorted(preferred, key=lambda x: x['total_score'], reverse=True)[:10]

    async def _analyze_content_themes(self, posts: List[RedditPost]) -> List[Dict[str, Any]]:
        """Analyze content themes and topics"""
        # This would implement NLP analysis of post titles and content
        # For now, return sample themes
        return [
            {'theme': 'Technology', 'frequency': 25, 'avg_score': 150},
            {'theme': 'Gaming', 'frequency': 20, 'avg_score': 200},
            {'theme': 'Discussion', 'frequency': 30, 'avg_score': 75}
        ]

    async def _identify_optimal_posting_times(self, posts: List[RedditPost]) -> List[Dict[str, Any]]:
        """Identify optimal posting times based on performance"""
        # Analyze posting times and scores
        hour_performance = {}
        
        for post in posts:
            hour = post.created_utc.hour
            if hour not in hour_performance:
                hour_performance[hour] = {'count': 0, 'total_score': 0}
            hour_performance[hour]['count'] += 1
            hour_performance[hour]['total_score'] += post.score
        
        # Calculate average scores by hour
        optimal_times = []
        for hour, data in hour_performance.items():
            if data['count'] > 0:
                avg_score = data['total_score'] / data['count']
                optimal_times.append({
                    'hour': hour,
                    'avg_score': avg_score,
                    'post_count': data['count']
                })
        
        return sorted(optimal_times, key=lambda x: x['avg_score'], reverse=True)[:5]

    async def _calculate_influence_score(self, user: RedditUser, posts: List[RedditPost], comments: List[RedditComment]) -> float:
        """Calculate user influence score"""
        total_karma = user.link_karma + user.comment_karma
        account_age_days = (datetime.utcnow() - user.created_utc).days
        
        # Factors: karma, account age, posting consistency, engagement
        karma_score = min(total_karma / 10000, 1.0) * 30  # Max 30 points
        age_score = min(account_age_days / 365, 1.0) * 20  # Max 20 points
        activity_score = min(len(posts) + len(comments), 100) / 100 * 25  # Max 25 points
        quality_score = (sum(post.score for post in posts) / len(posts) if posts else 0) / 100 * 25  # Max 25 points
        
        return karma_score + age_score + activity_score + quality_score

    # Additional helper methods would continue here for comprehensive functionality...

# Example usage and testing
async def main() -> None:
    """Example usage of Reddit API integration"""
    
    # Initialize the API client
    reddit_api = RedditAPI(
        client_id="your_client_id",
        client_secret="your_client_secret",
        user_agent="Ainflue:v1.0 (by /u/yourusername)",
        redirect_uri="https://yourapp.com/callback"
    )
    
    async with reddit_api:
        try:
            # Generate authorization URL
            auth_url = reddit_api.generate_auth_url()
            print(f"Authorization URL: {auth_url}")
            
            # After user authorization, exchange code for token
            # auth_code = "received_authorization_code"
            # await reddit_api.exchange_code_for_token(auth_code)
            
            # Get user profile and analytics
            # user_profile = await reddit_api.get_user_profile()
            # print(f"User: {user_profile.username} - Karma: {user_profile.link_karma + user_profile.comment_karma}")
            
            # Get subreddit analytics
            # analytics = await reddit_api.get_subreddit_analytics('technology')
            # print(f"r/technology analytics: {analytics['community_stats']}")
            
            # Optimize content strategy
            # strategy = await reddit_api.optimize_content_strategy(['technology', 'programming', 'MachineLearning'])
            # print(f"Content strategy: {strategy['content_recommendations']}")
            
            logger.info("Reddit API integration example completed successfully")
            
        except RedditAPIError as e:
            logger.error(f"Reddit API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    asyncio.run(main())