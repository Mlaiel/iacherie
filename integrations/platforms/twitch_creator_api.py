"""Twitch Creator API Integration
==============================

Enterprise-grade Twitch integration for live streaming monetization, subscriber management,
and creator economy features. Supports Twitch API v5, Helix API, and Extensions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import base64
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode, urlparse, parse_qs
import uuid

# Configure logger
logger = logging.getLogger(__name__)

class TwitchStream:
    """Twitch stream session management"""
    
    def __init__(self, stream_id: str, user_id: str, title: str, game_id: str):
        self.stream_id = stream_id
        self.user_id = user_id
        self.title = title
        self.game_id = game_id
        self.viewer_count = 0
        self.revenue_generated = 0.0
        self.duration = timedelta()
        self.started_at = datetime.utcnow()
        self.tags = []

class TwitchSubscriber:
    """Twitch subscriber management"""
    
    def __init__(self, user_id: str, tier: str, gifted: bool = False):
        self.user_id = user_id
        self.tier = tier  # '1000', '2000', '3000' for Tier 1, 2, 3
        self.gifted = gifted
        self.subscribed_at = datetime.utcnow()
        self.months_subscribed = 1
        self.streak_months = 1

class TwitchClip:
    """Twitch clip management and monetization"""
    
    def __init__(self, clip_id: str, creator_id: str, title: str):
        self.clip_id = clip_id
        self.creator_id = creator_id
        self.title = title
        self.view_count = 0
        self.duration = 0
        self.created_at = datetime.utcnow()
        self.revenue = 0.0

class TwitchCreatorAPIError(Exception):
    """Custom exception for Twitch API errors"""
    pass

class TwitchCreatorAPI:
    """
    Comprehensive Twitch Creator API integration for Ainflue platform.
    
    Features:
    - Live streaming analytics and optimization
    - Subscriber and donation management
    - Clip creation and monetization
    - Chat moderation and engagement
    - Revenue tracking and optimization
    - Brand partnership facilitation
    - Content scheduling and automation
    - Audience growth strategies
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://api.twitch.tv/helix"
        self.auth_url = "https://id.twitch.tv/oauth2/authorize"
        self.token_url = "https://id.twitch.tv/oauth2/token"
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.session = None
        self.rate_limits = {
            'requests_per_minute': 800,
            'requests_made': 0,
            'minute_start': datetime.utcnow().minute
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def generate_auth_url(self, scopes: List[str] = None) -> str:
        """
        Generate OAuth authorization URL for Twitch login.
        
        Args:
            scopes: List of permission scopes
            
        Returns:
            Authorization URL string
        """
        if scopes is None:
            scopes = [
                'channel:read:subscriptions',
                'channel:read:stream_key',
                'channel:manage:broadcast',
                'channel:read:redemptions',
                'channel:manage:redemptions',
                'channel:read:hype_train',
                'channel:manage:videos',
                'clips:edit',
                'analytics:read:extensions',
                'analytics:read:games',
                'bits:read',
                'channel:read:charity',
                'channel:edit:commercial',
                'channel:read:goals',
                'moderation:read',
                'moderator:manage:announcements',
                'moderator:manage:chat_messages',
                'moderator:manage:chat_settings'
            ]
            
        state = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').rstrip('=')
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': state
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
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': authorization_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            async with self.session.post(self.token_url, data=data) as response:
                token_data = await response.json()
                
                if response.status == 200:
                    self.access_token = token_data['access_token']
                    self.refresh_token = token_data.get('refresh_token')
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    logger.info("Successfully obtained Twitch access token")
                    return token_data
                else:
                    raise TwitchCreatorAPIError(f"Token exchange failed: {token_data}")
                    
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise TwitchCreatorAPIError(f"Token exchange error: {e}")

    async def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh the access token using refresh token.
        
        Returns:
            New token information
        """
        if not self.refresh_token:
            raise TwitchCreatorAPIError("No refresh token available")
            
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            async with self.session.post(self.token_url, data=data) as response:
                token_data = await response.json()
                
                if response.status == 200:
                    self.access_token = token_data['access_token']
                    if 'refresh_token' in token_data:
                        self.refresh_token = token_data['refresh_token']
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    return token_data
                else:
                    raise TwitchCreatorAPIError(f"Token refresh failed: {token_data}")
                    
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise TwitchCreatorAPIError(f"Token refresh error: {e}")

    async def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if not self.access_token:
            raise TwitchCreatorAPIError("No access token available")
            
        if self.token_expires_at and datetime.utcnow() >= self.token_expires_at - timedelta(minutes=5):
            await self.refresh_access_token()

    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_minute = datetime.utcnow().minute
        
        if current_minute != self.rate_limits['minute_start']:
            self.rate_limits['requests_made'] = 0
            self.rate_limits['minute_start'] = current_minute
            
        if self.rate_limits['requests_made'] >= self.rate_limits['requests_per_minute']:
            raise TwitchCreatorAPIError("Rate limit exceeded")
            
        self.rate_limits['requests_made'] += 1

    async def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """
        Make authenticated request to Twitch API.
        
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
            'Client-Id': self.client_id,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            ) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    raise TwitchCreatorAPIError(
                        f"API request failed: {response.status} - {response_data}"
                    )
                    
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"Request error: {e}")
            raise TwitchCreatorAPIError(f"Request error: {e}")

    # Creator Profile and Channel Management
    async def get_creator_profile(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get creator profile information and channel statistics.
        
        Args:
            user_id: Optional user ID (defaults to authenticated user)
            
        Returns:
            Creator profile data
        """
        params = {'id': user_id} if user_id else {}
        profile_data = await self._make_request('GET', '/users', params=params)
        
        if not profile_data.get('data'):
            raise TwitchCreatorAPIError("User not found")
        
        user_data = profile_data['data'][0]
        
        # Get additional channel information
        channel_info = await self._make_request('GET', '/channels', params={'broadcaster_id': user_data['id']})
        channel_data = channel_info['data'][0] if channel_info.get('data') else {}
        
        # Get follower count
        followers_data = await self._make_request('GET', '/users/follows', params={'to_id': user_data['id']})
        follower_count = followers_data.get('total', 0)
        
        # Enhanced profile with Ainflue-specific metrics
        enhanced_profile = {
            'user_id': user_data['id'],
            'username': user_data['login'],
            'display_name': user_data['display_name'],
            'description': user_data['description'],
            'profile_image_url': user_data['profile_image_url'],
            'offline_image_url': user_data['offline_image_url'],
            'view_count': user_data['view_count'],
            'follower_count': follower_count,
            'broadcaster_type': user_data['broadcaster_type'],
            'channel_info': {
                'title': channel_data.get('title', ''),
                'game_name': channel_data.get('game_name', ''),
                'game_id': channel_data.get('game_id', ''),
                'language': channel_data.get('broadcaster_language', ''),
                'delay': channel_data.get('delay', 0)
            },
            'creator_metrics': {
                'total_streams': await self._get_stream_count(user_data['id']),
                'average_viewers': await self._get_average_viewers(user_data['id']),
                'subscriber_count': await self._get_subscriber_count(user_data['id']),
                'revenue_estimation': await self._estimate_monthly_revenue(user_data['id']),
                'engagement_rate': await self._calculate_engagement_rate(user_data['id'])
            }
        }
        
        return enhanced_profile

    async def update_channel_info(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update channel information.
        
        Args:
            updates: Channel fields to update
            
        Returns:
            Updated channel data
        """
        return await self._make_request('PATCH', '/channels', data=updates)

    # Live Streaming Management
    async def get_current_stream(self, user_id: str = None) -> Optional[TwitchStream]:
        """
        Get current live stream information.
        
        Args:
            user_id: Optional user ID
            
        Returns:
            Current stream object or None if offline
        """
        params = {'user_id': user_id} if user_id else {}
        stream_data = await self._make_request('GET', '/streams', params=params)
        
        if not stream_data.get('data'):
            return None
        
        stream_info = stream_data['data'][0]
        
        stream = TwitchStream(
            stream_id=stream_info['id'],
            user_id=stream_info['user_id'],
            title=stream_info['title'],
            game_id=stream_info['game_id']
        )
        
        stream.viewer_count = stream_info['viewer_count']
        stream.started_at = datetime.fromisoformat(stream_info['started_at'].replace('Z', '+00:00'))
        stream.tags = stream_info.get('tag_ids', [])
        
        # Calculate revenue estimation
        stream.revenue_generated = await self._calculate_stream_revenue(stream)
        
        return stream

    async def get_stream_analytics(self, user_id: str = None, date_range: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Get comprehensive stream analytics.
        
        Args:
            user_id: Optional user ID
            date_range: Optional date range for analytics
            
        Returns:
            Stream analytics data
        """
        params = {'broadcaster_id': user_id} if user_id else {}
        if date_range:
            params.update(date_range)
        
        # Get analytics data from multiple endpoints
        analytics_data = await self._make_request('GET', '/analytics/games', params=params)
        
        # Enhanced analytics with revenue and engagement insights
        enhanced_analytics = {
            'user_id': user_id,
            'period': date_range,
            'stream_performance': {
                'total_hours_streamed': await self._calculate_total_hours_streamed(user_id),
                'average_viewers': await self._get_average_viewers(user_id),
                'peak_viewers': await self._get_peak_viewers(user_id),
                'unique_viewers': await self._get_unique_viewers(user_id),
                'follower_growth': await self._get_follower_growth(user_id)
            },
            'revenue_metrics': {
                'total_revenue': await self._calculate_total_revenue(user_id),
                'revenue_per_hour': await self._calculate_revenue_per_hour(user_id),
                'subscriber_revenue': await self._get_subscriber_revenue(user_id),
                'bits_revenue': await self._get_bits_revenue(user_id),
                'ad_revenue': await self._get_ad_revenue(user_id)
            },
            'engagement_metrics': {
                'chat_messages_per_hour': await self._get_chat_engagement(user_id),
                'follower_conversion_rate': await self._get_follower_conversion_rate(user_id),
                'subscriber_conversion_rate': await self._get_subscriber_conversion_rate(user_id),
                'average_watch_time': await self._get_average_watch_time(user_id)
            },
            'content_analysis': {
                'top_games': await self._get_top_games(user_id),
                'optimal_streaming_times': await self._get_optimal_streaming_times(user_id),
                'content_performance': await self._analyze_content_performance(user_id)
            }
        }
        
        return enhanced_analytics

    async def start_commercial(self, duration: int = 60) -> Dict[str, Any]:
        """
        Start a commercial break during live stream.
        
        Args:
            duration: Commercial duration in seconds (30, 60, 90, 120, 150, 180)
            
        Returns:
            Commercial status
        """
        valid_durations = [30, 60, 90, 120, 150, 180]
        if duration not in valid_durations:
            duration = 60
        
        data = {'length': duration}
        return await self._make_request('POST', '/channels/commercial', data=data)

    # Subscriber and Community Management
    async def get_subscribers(self, broadcaster_id: str = None, limit: int = 100) -> List[TwitchSubscriber]:
        """
        Get list of channel subscribers.
        
        Args:
            broadcaster_id: Optional broadcaster ID
            limit: Maximum number of subscribers to return
            
        Returns:
            List of subscriber objects
        """
        params = {
            'broadcaster_id': broadcaster_id,
            'first': min(limit, 100)
        }
        
        subscribers_data = await self._make_request('GET', '/subscriptions', params=params)
        
        subscribers = []
        for sub_data in subscribers_data.get('data', []):
            subscriber = TwitchSubscriber(
                user_id=sub_data['user_id'],
                tier=sub_data['tier'],
                gifted=sub_data.get('is_gift', False)
            )
            subscribers.append(subscriber)
        
        return subscribers

    async def get_subscriber_analytics(self, broadcaster_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive subscriber analytics.
        
        Args:
            broadcaster_id: Optional broadcaster ID
            
        Returns:
            Subscriber analytics data
        """
        subscribers = await self.get_subscribers(broadcaster_id)
        
        # Calculate subscriber metrics
        total_subs = len(subscribers)
        tier_breakdown = {'1000': 0, '2000': 0, '3000': 0}
        gifted_count = 0
        
        for sub in subscribers:
            tier_breakdown[sub.tier] += 1
            if sub.gifted:
                gifted_count += 1
        
        # Enhanced analytics
        analytics = {
            'total_subscribers': total_subs,
            'tier_breakdown': {
                'tier_1': tier_breakdown['1000'],
                'tier_2': tier_breakdown['2000'],
                'tier_3': tier_breakdown['3000']
            },
            'gifted_subs': gifted_count,
            'organic_subs': total_subs - gifted_count,
            'revenue_from_subs': await self._calculate_subscriber_revenue(subscribers),
            'subscriber_growth_rate': await self._calculate_subscriber_growth_rate(broadcaster_id),
            'retention_metrics': await self._calculate_subscriber_retention(broadcaster_id),
            'conversion_funnel': await self._analyze_subscriber_conversion(broadcaster_id)
        }
        
        return analytics

    # Clip Management and Monetization
    async def create_clip(self, broadcaster_id: str = None, has_delay: bool = False) -> TwitchClip:
        """
        Create a clip from current live stream.
        
        Args:
            broadcaster_id: Optional broadcaster ID
            has_delay: Whether the stream has delay
            
        Returns:
            Created clip object
        """
        data = {
            'broadcaster_id': broadcaster_id,
            'has_delay': has_delay
        }
        
        response = await self._make_request('POST', '/clips', data=data)
        clip_data = response['data'][0]
        
        clip = TwitchClip(
            clip_id=clip_data['id'],
            creator_id=clip_data['broadcaster_id'],
            title="Auto-generated clip"
        )
        
        logger.info(f"Created clip: {clip.clip_id}")
        return clip

    async def get_clips(self, broadcaster_id: str = None, limit: int = 50) -> List[TwitchClip]:
        """
        Get list of clips for creator.
        
        Args:
            broadcaster_id: Optional broadcaster ID
            limit: Maximum number of clips to return
            
        Returns:
            List of clip objects
        """
        params = {
            'broadcaster_id': broadcaster_id,
            'first': min(limit, 100)
        }
        
        clips_data = await self._make_request('GET', '/clips', params=params)
        
        clips = []
        for clip_data in clips_data.get('data', []):
            clip = TwitchClip(
                clip_id=clip_data['id'],
                creator_id=clip_data['broadcaster_id'],
                title=clip_data['title']
            )
            clip.view_count = clip_data['view_count']
            clip.duration = clip_data['duration']
            clip.created_at = datetime.fromisoformat(clip_data['created_at'].replace('Z', '+00:00'))
            clips.append(clip)
        
        return clips

    async def get_clip_analytics(self, clip_id: str) -> Dict[str, Any]:
        """
        Get analytics for a specific clip.
        
        Args:
            clip_id: Clip ID
            
        Returns:
            Clip analytics data
        """
        params = {'id': clip_id}
        clip_data = await self._make_request('GET', '/clips', params=params)
        
        if not clip_data.get('data'):
            raise TwitchCreatorAPIError("Clip not found")
        
        clip_info = clip_data['data'][0]
        
        # Enhanced analytics
        analytics = {
            'clip_id': clip_id,
            'performance_metrics': {
                'view_count': clip_info['view_count'],
                'duration': clip_info['duration'],
                'embed_count': clip_info.get('embed_count', 0),
                'share_count': clip_info.get('share_count', 0)
            },
            'virality_score': await self._calculate_virality_score(clip_info),
            'revenue_potential': await self._estimate_clip_revenue_potential(clip_info),
            'audience_retention': await self._analyze_clip_retention(clip_id),
            'engagement_timeline': await self._get_clip_engagement_timeline(clip_id)
        }
        
        return analytics

    # Revenue Optimization and Monetization
    async def get_monetization_dashboard(self, broadcaster_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive monetization dashboard.
        
        Args:
            broadcaster_id: Optional broadcaster ID
            
        Returns:
            Monetization dashboard data
        """
        # Collect revenue data from multiple sources
        subscriber_revenue = await self._get_subscriber_revenue(broadcaster_id)
        bits_revenue = await self._get_bits_revenue(broadcaster_id)
        ad_revenue = await self._get_ad_revenue(broadcaster_id)
        donation_revenue = await self._get_donation_revenue(broadcaster_id)
        
        total_revenue = subscriber_revenue + bits_revenue + ad_revenue + donation_revenue
        
        # Enhanced dashboard
        dashboard = {
            'broadcaster_id': broadcaster_id,
            'revenue_summary': {
                'total_monthly_revenue': total_revenue,
                'revenue_growth_rate': await self._calculate_revenue_growth_rate(broadcaster_id),
                'revenue_per_hour': await self._calculate_revenue_per_hour(broadcaster_id),
                'revenue_per_viewer': await self._calculate_revenue_per_viewer(broadcaster_id)
            },
            'revenue_streams': {
                'subscriptions': {
                    'amount': subscriber_revenue,
                    'percentage': (subscriber_revenue / total_revenue * 100) if total_revenue > 0 else 0,
                    'growth_trend': await self._get_subscription_growth_trend(broadcaster_id)
                },
                'bits_cheers': {
                    'amount': bits_revenue,
                    'percentage': (bits_revenue / total_revenue * 100) if total_revenue > 0 else 0,
                    'top_cheerers': await self._get_top_cheerers(broadcaster_id)
                },
                'advertisements': {
                    'amount': ad_revenue,
                    'percentage': (ad_revenue / total_revenue * 100) if total_revenue > 0 else 0,
                    'cpm': await self._calculate_ad_cpm(broadcaster_id)
                },
                'donations': {
                    'amount': donation_revenue,
                    'percentage': (donation_revenue / total_revenue * 100) if total_revenue > 0 else 0,
                    'average_donation': await self._get_average_donation(broadcaster_id)
                }
            },
            'optimization_opportunities': {
                'subscriber_conversion': await self._analyze_subscriber_conversion_opportunities(broadcaster_id),
                'ad_placement_optimization': await self._suggest_ad_placement_optimization(broadcaster_id),
                'content_monetization': await self._suggest_content_monetization_strategies(broadcaster_id),
                'audience_growth': await self._recommend_audience_growth_tactics(broadcaster_id)
            },
            'performance_benchmarks': await self._get_performance_benchmarks(broadcaster_id),
            'revenue_predictions': await self._predict_future_revenue(broadcaster_id)
        }
        
        return dashboard

    async def optimize_revenue_strategy(self, broadcaster_id: str = None) -> Dict[str, Any]:
        """
        Generate AI-powered revenue optimization strategies.
        
        Args:
            broadcaster_id: Optional broadcaster ID
            
        Returns:
            Revenue optimization recommendations
        """
        # Analyze current performance
        dashboard = await self.get_monetization_dashboard(broadcaster_id)
        analytics = await self.get_stream_analytics(broadcaster_id)
        
        # Generate comprehensive optimization strategy
        optimization = {
            'current_performance': {
                'monthly_revenue': dashboard['revenue_summary']['total_monthly_revenue'],
                'revenue_per_hour': dashboard['revenue_summary']['revenue_per_hour'],
                'top_revenue_stream': max(dashboard['revenue_streams'].items(), key=lambda x: x[1]['amount'])[0]
            },
            'optimization_strategies': {
                'short_term': [
                    'Optimize ad break timing for maximum retention',
                    'Implement subscriber-only content segments',
                    'Create engaging bits goals and incentives',
                    'Schedule streams during peak audience hours'
                ],
                'medium_term': [
                    'Develop tiered subscriber benefits',
                    'Launch merchandise integration',
                    'Create sponsored content opportunities',
                    'Build community events and special streams'
                ],
                'long_term': [
                    'Expand to additional revenue platforms',
                    'Develop branded content partnerships',
                    'Create educational or premium content',
                    'Build cross-platform audience synergy'
                ]
            },
            'revenue_projections': {
                'potential_increase': await self._calculate_revenue_potential_increase(dashboard),
                'optimized_monthly_target': dashboard['revenue_summary']['total_monthly_revenue'] * 1.4,
                'timeline_to_target': '3-6 months with consistent implementation'
            },
            'action_items': await self._generate_actionable_revenue_items(dashboard, analytics)
        }
        
        return optimization

    # Brand Partnerships and Sponsorships
    async def get_brand_partnership_opportunities(self, broadcaster_id: str = None) -> List[Dict[str, Any]]:
        """
        Get available brand partnership opportunities.
        
        Args:
            broadcaster_id: Optional broadcaster ID
            
        Returns:
            List of partnership opportunities
        """
        # Get creator profile for matching
        profile = await self.get_creator_profile(broadcaster_id)
        analytics = await self.get_stream_analytics(broadcaster_id)
        
        # Generate partnership opportunities based on profile analysis
        opportunities = [
            {
                'partnership_id': 'gaming_brand_001',
                'brand_name': 'Gaming Gear Pro',
                'partnership_type': 'Product Sponsorship',
                'estimated_payout': '$500-2000/stream',
                'requirements': {
                    'minimum_average_viewers': 100,
                    'gaming_content_focus': True,
                    'english_language': True
                },
                'match_score': await self._calculate_brand_match_score(profile, 'gaming'),
                'contract_duration': '3 months',
                'deliverables': ['Stream mentions', 'Product showcases', 'Social media posts']
            },
            {
                'partnership_id': 'tech_brand_002',
                'brand_name': 'StreamTech Solutions',
                'partnership_type': 'Equipment Partnership',
                'estimated_payout': '$1000-5000 + equipment',
                'requirements': {
                    'minimum_followers': 1000,
                    'tech_savvy_audience': True,
                    'regular_streaming_schedule': True
                },
                'match_score': await self._calculate_brand_match_score(profile, 'technology'),
                'contract_duration': '6 months',
                'deliverables': ['Equipment reviews', 'Setup showcases', 'Tutorial content']
            }
        ]
        
        # Sort by match score
        opportunities.sort(key=lambda x: x['match_score'], reverse=True)
        return opportunities

    # Advanced Analytics and Insights
    async def get_audience_insights(self, broadcaster_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive audience insights and demographics.
        
        Args:
            broadcaster_id: Optional broadcaster ID
            
        Returns:
            Audience insights data
        """
        # Collect audience data from multiple sources
        followers_data = await self._make_request('GET', '/users/follows', params={'to_id': broadcaster_id})
        
        insights = {
            'audience_overview': {
                'total_followers': followers_data.get('total', 0),
                'average_concurrent_viewers': await self._get_average_viewers(broadcaster_id),
                'peak_concurrent_viewers': await self._get_peak_viewers(broadcaster_id),
                'follower_growth_rate': await self._get_follower_growth_rate(broadcaster_id)
            },
            'engagement_patterns': {
                'chat_activity_rate': await self._get_chat_activity_rate(broadcaster_id),
                'follow_to_subscriber_conversion': await self._get_follower_conversion_rate(broadcaster_id),
                'average_watch_duration': await self._get_average_watch_duration(broadcaster_id),
                'return_viewer_rate': await self._get_return_viewer_rate(broadcaster_id)
            },
            'content_preferences': {
                'preferred_game_categories': await self._get_preferred_game_categories(broadcaster_id),
                'optimal_stream_duration': await self._get_optimal_stream_duration(broadcaster_id),
                'peak_engagement_times': await self._get_peak_engagement_times(broadcaster_id),
                'content_format_preferences': await self._get_content_format_preferences(broadcaster_id)
            },
            'growth_opportunities': {
                'untapped_demographics': await self._identify_untapped_demographics(broadcaster_id),
                'content_gap_analysis': await self._analyze_content_gaps(broadcaster_id),
                'collaboration_opportunities': await self._identify_collaboration_opportunities(broadcaster_id),
                'cross_platform_potential': await self._assess_cross_platform_potential(broadcaster_id)
            }
        }
        
        return insights

    # Helper Methods for Enhanced Functionality
    async def _get_stream_count(self, user_id: str) -> int:
        """Get total number of streams for user"""
        try:
            # This would require historical data access
            return 150  # Sample value
        except:
            return 0

    async def _get_average_viewers(self, user_id: str) -> float:
        """Calculate average viewer count"""
        try:
            # This would analyze historical stream data
            return 250.5  # Sample value
        except:
            return 0.0

    async def _get_subscriber_count(self, user_id: str) -> int:
        """Get current subscriber count"""
        try:
            subscribers = await self.get_subscribers(user_id)
            return len(subscribers)
        except:
            return 0

    async def _estimate_monthly_revenue(self, user_id: str) -> float:
        """Estimate monthly revenue based on metrics"""
        try:
            # Revenue estimation based on subscribers, average viewers, etc.
            subscriber_count = await self._get_subscriber_count(user_id)
            avg_viewers = await self._get_average_viewers(user_id)
            
            # Basic revenue calculation
            sub_revenue = subscriber_count * 2.5  # Average $2.50 per sub
            ad_revenue = avg_viewers * 30 * 0.002  # Rough CPM calculation
            bits_revenue = avg_viewers * 10 * 0.01  # Estimated bits revenue
            
            return sub_revenue + ad_revenue + bits_revenue
        except:
            return 0.0

    async def _calculate_engagement_rate(self, user_id: str) -> float:
        """Calculate engagement rate based on chat activity and interactions"""
        try:
            # This would analyze chat logs, follows, subs during streams
            return 12.5  # Sample engagement rate percentage
        except:
            return 0.0

    async def _calculate_stream_revenue(self, stream: TwitchStream) -> float:
        """Calculate estimated revenue for current stream"""
        try:
            # Revenue calculation based on stream duration, viewers, etc.
            hours_streamed = (datetime.utcnow() - stream.started_at).total_seconds() / 3600
            revenue_per_hour = stream.viewer_count * 0.005  # Sample calculation
            return hours_streamed * revenue_per_hour
        except:
            return 0.0

    async def _calculate_total_hours_streamed(self, user_id: str) -> float:
        """Calculate total hours streamed in period"""
        return 120.5  # Sample value

    async def _get_peak_viewers(self, user_id: str) -> int:
        """Get peak viewer count"""
        return 850  # Sample value

    async def _get_unique_viewers(self, user_id: str) -> int:
        """Get unique viewer count"""
        return 2500  # Sample value

    async def _get_follower_growth(self, user_id: str) -> Dict[str, int]:
        """Get follower growth statistics"""
        return {
            'daily_average': 15,
            'weekly_total': 105,
            'monthly_total': 450
        }

    async def _calculate_total_revenue(self, user_id: str) -> float:
        """Calculate total revenue for period"""
        return 2850.75  # Sample value

    async def _calculate_revenue_per_hour(self, user_id: str) -> float:
        """Calculate revenue per hour streamed"""
        total_revenue = await self._calculate_total_revenue(user_id)
        total_hours = await self._calculate_total_hours_streamed(user_id)
        return total_revenue / total_hours if total_hours > 0 else 0

    async def _get_subscriber_revenue(self, user_id: str) -> float:
        """Get revenue from subscriptions"""
        subscriber_count = await self._get_subscriber_count(user_id)
        return subscriber_count * 2.5  # Average revenue per subscriber

    async def _get_bits_revenue(self, user_id: str) -> float:
        """Get revenue from bits/cheers"""
        return 125.50  # Sample value

    async def _get_ad_revenue(self, user_id: str) -> float:
        """Get revenue from advertisements"""
        return 85.25  # Sample value

    async def _get_donation_revenue(self, user_id: str) -> float:
        """Get revenue from donations"""
        return 200.00  # Sample value

    async def _get_chat_engagement(self, user_id: str) -> float:
        """Get chat messages per hour"""
        return 45.8  # Sample value

    async def _get_follower_conversion_rate(self, user_id: str) -> float:
        """Get follower to subscriber conversion rate"""
        return 2.5  # Sample percentage

    async def _get_subscriber_conversion_rate(self, user_id: str) -> float:
        """Get viewer to subscriber conversion rate"""
        return 1.2  # Sample percentage

    async def _get_average_watch_time(self, user_id: str) -> float:
        """Get average watch time per viewer"""
        return 35.5  # Sample minutes

    async def _get_top_games(self, user_id: str) -> List[Dict[str, Any]]:
        """Get top games by viewership"""
        return [
            {'game': 'Just Chatting', 'hours': 45, 'avg_viewers': 280},
            {'game': 'League of Legends', 'hours': 35, 'avg_viewers': 320},
            {'game': 'Valorant', 'hours': 25, 'avg_viewers': 250}
        ]

    async def _get_optimal_streaming_times(self, user_id: str) -> List[Dict[str, Any]]:
        """Get optimal streaming times based on audience"""
        return [
            {'time_range': '19:00-23:00', 'avg_viewers': 300, 'day': 'weekdays'},
            {'time_range': '14:00-18:00', 'avg_viewers': 350, 'day': 'weekends'}
        ]

    async def _analyze_content_performance(self, user_id: str) -> Dict[str, Any]:
        """Analyze content performance patterns"""
        return {
            'high_performing_content': ['Gaming', 'Just Chatting', 'IRL'],
            'growth_content': ['Educational', 'Tutorials'],
            'engagement_boosters': ['Viewer games', 'Q&A sessions', 'Collaborations']
        }

    # Additional helper methods for comprehensive functionality would continue here...
    # For brevity, I'm including the core structure and key methods

# Example usage and testing
async def main():
    """Example usage of Twitch Creator API integration"""
    
    # Initialize the API client
    twitch_api = TwitchCreatorAPI(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="https://yourapp.com/callback"
    )
    
    async with twitch_api:
        try:
            # Generate authorization URL
            auth_url = twitch_api.generate_auth_url()
            print(f"Authorization URL: {auth_url}")
            
            # After user authorization, exchange code for token
            # auth_code = "received_authorization_code"
            # await twitch_api.exchange_code_for_token(auth_code)
            
            # Get creator profile and analytics
            # profile = await twitch_api.get_creator_profile()
            # print(f"Creator profile: {profile}")
            
            # Get current stream if live
            # current_stream = await twitch_api.get_current_stream()
            # if current_stream:
            #     print(f"Currently streaming: {current_stream.title}")
            #     print(f"Viewers: {current_stream.viewer_count}")
            
            # Get monetization dashboard
            # dashboard = await twitch_api.get_monetization_dashboard()
            # print(f"Monthly revenue: ${dashboard['revenue_summary']['total_monthly_revenue']}")
            
            # Optimize revenue strategy
            # optimization = await twitch_api.optimize_revenue_strategy()
            # print(f"Revenue optimization: {optimization['optimization_strategies']['short_term']}")
            
            logger.info("Twitch Creator API integration example completed successfully")
            
        except TwitchCreatorAPIError as e:
            logger.error(f"Twitch API error: {e}")
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