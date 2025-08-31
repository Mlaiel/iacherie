"""Analytics Parsers Module
========================

Specialized parsers for extracting analytics data from various platforms.
Handles Google Analytics, social media insights, and performance metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""
import asyncio
import json
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union

import aiohttp
from bs4 import BeautifulSoup

from .exceptions import AnalyticsParsingError, AuthenticationError, RateLimitError
from .parser_config import ParserConfig


class BaseAnalyticsParser(ABC):
    """Abstract base class for analytics parsers"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.analytics_config = config.analytics
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def parse_analytics(self, **kwargs) -> Dict[str, Any]:
        """Parse analytics data from platform"""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the platform name for this analytics parser"""
        pass
    
    def _calculate_date_range(self, days: Optional[int] = None) -> tuple:
        """Calculate date range for analytics queries"""
        if days is None:
            days = self.analytics_config.date_range_days
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        return start_date, end_date
    
    def _format_date_for_api(self, date: datetime, format_type: str = "iso") -> str:
        """Format date for specific API requirements"""
        if format_type == "iso":
            return date.strftime("%Y-%m-%d")
        elif format_type == "unix":
            return str(int(date.timestamp()))
        elif format_type == "iso_datetime":
            return date.isoformat()
        else:
            return date.strftime("%Y-%m-%d")


class GoogleAnalyticsParser(BaseAnalyticsParser):
    """Parser for Google Analytics data"""
    
    def get_platform_name(self) -> str:
        return "google_analytics"
    
    async def parse_analytics(self, property_id: str, **kwargs) -> Dict[str, Any]:
        """Parse Google Analytics 4 data"""
        try:
            start_date, end_date = self._calculate_date_range(kwargs.get('days'))
            
            # GA4 API request structure
            request_body = {
                "dateRanges": [{
                    "startDate": self._format_date_for_api(start_date),
                    "endDate": self._format_date_for_api(end_date)
                }],
                "metrics": [
                    {"name": "sessions"},
                    {"name": "screenPageViews"},
                    {"name": "bounceRate"},
                    {"name": "sessionDuration"},
                    {"name": "engagementRate"},
                    {"name": "newUsers"},
                    {"name": "totalUsers"}
                ],
                "dimensions": [
                    {"name": "date"},
                    {"name": "country"},
                    {"name": "deviceCategory"},
                    {"name": "sessionSource"},
                    {"name": "sessionMedium"}
                ]
            }
            
            # Make API request to GA4
            analytics_data = await self._make_ga4_request(property_id, request_body)
            
            # Parse and structure the response
            parsed_data = await self._parse_ga4_response(analytics_data)
            
            return {
                'platform': self.get_platform_name(),
                'property_id': property_id,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'data': parsed_data,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise AnalyticsParsingError(
                f"Google Analytics parsing failed: {str(e)}",
                analytics_platform="google_analytics",
                parser_type="GoogleAnalyticsParser"
            )
    
    async def _make_ga4_request(self, property_id: str, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to Google Analytics 4 API"""
        url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"
        
        headers = {
            "Authorization": f"Bearer {self.config.platform['google'].access_token}",
            "Content-Type": "application/json"
        }
        
        async with self.session.post(url, json=request_body, headers=headers) as response:
            if response.status == 401:
                raise AuthenticationError(
                    "Google Analytics authentication failed",
                    platform="google_analytics",
                    auth_type="oauth2"
                )
            
            if response.status == 429:
                raise RateLimitError(
                    "Google Analytics rate limit exceeded",
                    platform="google_analytics"
                )
            
            response.raise_for_status()
            return await response.json()
    
    async def _parse_ga4_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Google Analytics 4 API response"""
        parsed = {
            'overview': {},
            'time_series': [],
            'demographics': {},
            'traffic_sources': {},
            'devices': {}
        }
        
        if 'rows' not in data:
            return parsed
        
        # Extract metric headers
        metric_headers = [header['name'] for header in data.get('metricHeaders', [])]
        dimension_headers = [header['name'] for header in data.get('dimensionHeaders', [])]
        
        # Process rows
        total_sessions = 0
        total_pageviews = 0
        countries = {}
        sources = {}
        devices = {}
        daily_data = {}
        
        for row in data['rows']:
            dimensions = row.get('dimensionValues', [])
            metrics = row.get('metricValues', [])
            
            # Create dimension dict
            dim_dict = {dimension_headers[i]: dimensions[i]['value'] 
                       for i in range(len(dimensions))}
            
            # Create metrics dict
            metric_dict = {metric_headers[i]: float(metrics[i]['value']) 
                          for i in range(len(metrics))}
            
            # Aggregate data
            sessions = metric_dict.get('sessions', 0)
            pageviews = metric_dict.get('screenPageViews', 0)
            
            total_sessions += sessions
            total_pageviews += pageviews
            
            # Aggregate by country
            country = dim_dict.get('country', 'Unknown')
            if country not in countries:
                countries[country] = {'sessions': 0, 'pageviews': 0}
            countries[country]['sessions'] += sessions
            countries[country]['pageviews'] += pageviews
            
            # Aggregate by source
            source = dim_dict.get('sessionSource', 'Unknown')
            if source not in sources:
                sources[source] = {'sessions': 0, 'pageviews': 0}
            sources[source]['sessions'] += sessions
            sources[source]['pageviews'] += pageviews
            
            # Aggregate by device
            device = dim_dict.get('deviceCategory', 'Unknown')
            if device not in devices:
                devices[device] = {'sessions': 0, 'pageviews': 0}
            devices[device]['sessions'] += sessions
            devices[device]['pageviews'] += pageviews
            
            # Daily time series
            date = dim_dict.get('date', '')
            if date and date not in daily_data:
                daily_data[date] = {
                    'sessions': 0,
                    'pageviews': 0,
                    'bounce_rate': 0,
                    'avg_session_duration': 0
                }
            if date:
                daily_data[date]['sessions'] += sessions
                daily_data[date]['pageviews'] += pageviews
                daily_data[date]['bounce_rate'] = metric_dict.get('bounceRate', 0)
                daily_data[date]['avg_session_duration'] = metric_dict.get('sessionDuration', 0)
        
        # Structure final data
        parsed['overview'] = {
            'total_sessions': total_sessions,
            'total_pageviews': total_pageviews,
            'avg_bounce_rate': sum(day['bounce_rate'] for day in daily_data.values()) / len(daily_data) if daily_data else 0,
            'avg_session_duration': sum(day['avg_session_duration'] for day in daily_data.values()) / len(daily_data) if daily_data else 0
        }
        
        parsed['time_series'] = [
            {'date': date, **data} for date, data in sorted(daily_data.items())
        ]
        
        parsed['demographics']['countries'] = dict(sorted(countries.items(), key=lambda x: x[1]['sessions'], reverse=True)[:10])
        parsed['traffic_sources'] = dict(sorted(sources.items(), key=lambda x: x[1]['sessions'], reverse=True)[:10])
        parsed['devices'] = devices
        
        return parsed


class FacebookInsightsParser(BaseAnalyticsParser):
    """Parser for Facebook Insights data"""
    
    def get_platform_name(self) -> str:
        return "facebook_insights"
    
    async def parse_analytics(self, page_id: str, **kwargs) -> Dict[str, Any]:
        """Parse Facebook Insights data"""
        try:
            start_date, end_date = self._calculate_date_range(kwargs.get('days'))
            
            insights_data = await self._get_facebook_insights(page_id, start_date, end_date)
            parsed_data = await self._parse_facebook_insights(insights_data)
            
            return {
                'platform': self.get_platform_name(),
                'page_id': page_id,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'data': parsed_data,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise AnalyticsParsingError(
                f"Facebook Insights parsing failed: {str(e)}",
                analytics_platform="facebook",
                parser_type="FacebookInsightsParser"
            )
    
    async def _get_facebook_insights(self, page_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get insights data from Facebook Graph API"""
        metrics = [
            'page_views_total',
            'page_posts_impressions',
            'page_posts_impressions_unique',
            'page_posts_impressions_paid',
            'page_posts_impressions_organic',
            'page_fan_adds',
            'page_fan_removes',
            'page_engaged_users'
        ]
        
        url = f"https://graph.facebook.com/v18.0/{page_id}/insights"
        params = {
            'metric': ','.join(metrics),
            'since': self._format_date_for_api(start_date),
            'until': self._format_date_for_api(end_date),
            'period': 'day',
            'access_token': self.config.platform['facebook'].access_token
        }
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def _parse_facebook_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Facebook Insights API response"""
        parsed = {
            'overview': {},
            'time_series': [],
            'engagement': {},
            'reach': {}
        }
        
        # Process insights data
        insights = data.get('data', [])
        
        metric_data = {}
        for insight in insights:
            metric_name = insight.get('name', '')
            values = insight.get('values', [])
            
            metric_data[metric_name] = {}
            for value_item in values:
                date = value_item.get('end_time', '')[:10]  # Extract date part
                metric_data[metric_name][date] = value_item.get('value', 0)
        
        # Calculate overview metrics
        total_views = sum(metric_data.get('page_views_total', {}).values())
        total_impressions = sum(metric_data.get('page_posts_impressions', {}).values())
        total_fan_adds = sum(metric_data.get('page_fan_adds', {}).values())
        total_engaged_users = sum(metric_data.get('page_engaged_users', {}).values())
        
        parsed['overview'] = {
            'total_page_views': total_views,
            'total_impressions': total_impressions,
            'total_fan_adds': total_fan_adds,
            'total_engaged_users': total_engaged_users,
            'engagement_rate': (total_engaged_users / total_impressions * 100) if total_impressions > 0 else 0
        }
        
        # Create time series data
        all_dates = set()
        for metric_values in metric_data.values():
            all_dates.update(metric_values.keys())
        
        for date in sorted(all_dates):
            day_data = {'date': date}
            for metric_name, values in metric_data.items():
                day_data[metric_name] = values.get(date, 0)
            parsed['time_series'].append(day_data)
        
        return parsed


class TwitterAnalyticsParser(BaseAnalyticsParser):
    """Parser for Twitter Analytics data"""
    
    def get_platform_name(self) -> str:
        return "twitter_analytics"
    
    async def parse_analytics(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Parse Twitter Analytics data"""
        try:
            start_date, end_date = self._calculate_date_range(kwargs.get('days'))
            
            # Twitter API v2 doesn't provide comprehensive analytics
            # This would need to be implemented with Twitter's analytics API
            # or by scraping the analytics dashboard
            
            analytics_data = await self._get_twitter_metrics(user_id, start_date, end_date)
            parsed_data = await self._parse_twitter_metrics(analytics_data)
            
            return {
                'platform': self.get_platform_name(),
                'user_id': user_id,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'data': parsed_data,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise AnalyticsParsingError(
                f"Twitter Analytics parsing failed: {str(e)}",
                analytics_platform="twitter",
                parser_type="TwitterAnalyticsParser"
            )
    
    async def _get_twitter_metrics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get Twitter metrics (placeholder implementation)"""
        # This would implement actual Twitter analytics API calls
        return {
            'tweets': [],
            'user_metrics': {},
            'engagement_metrics': {}
        }
    
    async def _parse_twitter_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Twitter metrics data"""
        return {
            'overview': {
                'total_tweets': 0,
                'total_impressions': 0,
                'total_engagements': 0,
                'followers_gained': 0
            },
            'engagement': {},
            'time_series': []
        }


class YouTubeAnalyticsParser(BaseAnalyticsParser):
    """Parser for YouTube Analytics data"""
    
    def get_platform_name(self) -> str:
        return "youtube_analytics"
    
    async def parse_analytics(self, channel_id: str, **kwargs) -> Dict[str, Any]:
        """Parse YouTube Analytics data"""
        try:
            start_date, end_date = self._calculate_date_range(kwargs.get('days'))
            
            analytics_data = await self._get_youtube_analytics(channel_id, start_date, end_date)
            parsed_data = await self._parse_youtube_analytics(analytics_data)
            
            return {
                'platform': self.get_platform_name(),
                'channel_id': channel_id,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'data': parsed_data,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise AnalyticsParsingError(
                f"YouTube Analytics parsing failed: {str(e)}",
                analytics_platform="youtube",
                parser_type="YouTubeAnalyticsParser"
            )
    
    async def _get_youtube_analytics(self, channel_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get YouTube Analytics data"""
        url = "https://youtubeanalytics.googleapis.com/v2/reports"
        
        params = {
            'ids': f'channel=={channel_id}',
            'startDate': self._format_date_for_api(start_date),
            'endDate': self._format_date_for_api(end_date),
            'metrics': 'views,redViews,comments,likes,dislikes,videosAddedToPlaylists,videosRemovedFromPlaylists,shares,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,subscribersLost',
            'dimensions': 'day'
        }
        
        headers = {
            'Authorization': f'Bearer {self.config.platform["youtube"].access_token}'
        }
        
        async with self.session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    async def _parse_youtube_analytics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse YouTube Analytics API response"""
        parsed = {
            'overview': {},
            'time_series': [],
            'engagement': {},
            'audience_retention': {}
        }
        
        if 'rows' not in data:
            return parsed
        
        column_headers = data.get('columnHeaders', [])
        metric_names = [header['name'] for header in column_headers]
        
        total_views = 0
        total_watch_time = 0
        total_subscribers_gained = 0
        total_engagement = 0
        
        for row in data['rows']:
            day_data = dict(zip(metric_names, row))
            
            # Accumulate totals
            views = day_data.get('views', 0)
            watch_time = day_data.get('estimatedMinutesWatched', 0)
            subscribers_gained = day_data.get('subscribersGained', 0)
            likes = day_data.get('likes', 0)
            comments = day_data.get('comments', 0)
            shares = day_data.get('shares', 0)
            
            total_views += views
            total_watch_time += watch_time
            total_subscribers_gained += subscribers_gained
            total_engagement += (likes + comments + shares)
            
            parsed['time_series'].append(day_data)
        
        # Calculate overview metrics
        parsed['overview'] = {
            'total_views': total_views,
            'total_watch_time_minutes': total_watch_time,
            'total_subscribers_gained': total_subscribers_gained,
            'total_engagement': total_engagement,
            'avg_view_duration': sum(row.get('averageViewDuration', 0) for row in data['rows']) / len(data['rows']) if data['rows'] else 0,
            'avg_view_percentage': sum(row.get('averageViewPercentage', 0) for row in data['rows']) / len(data['rows']) if data['rows'] else 0
        }
        
        return parsed


class InstagramInsightsParser(BaseAnalyticsParser):
    """Parser for Instagram Insights data"""
    
    def get_platform_name(self) -> str:
        return "instagram_insights"
    
    async def parse_analytics(self, account_id: str, **kwargs) -> Dict[str, Any]:
        """Parse Instagram Insights data"""
        try:
            start_date, end_date = self._calculate_date_range(kwargs.get('days'))
            
            insights_data = await self._get_instagram_insights(account_id, start_date, end_date)
            parsed_data = await self._parse_instagram_insights(insights_data)
            
            return {
                'platform': self.get_platform_name(),
                'account_id': account_id,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'data': parsed_data,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise AnalyticsParsingError(
                f"Instagram Insights parsing failed: {str(e)}",
                analytics_platform="instagram",
                parser_type="InstagramInsightsParser"
            )
    
    async def _get_instagram_insights(self, account_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get Instagram Insights data"""
        metrics = [
            'impressions',
            'reach',
            'profile_views',
            'website_clicks',
            'follower_count'
        ]
        
        url = f"https://graph.facebook.com/v18.0/{account_id}/insights"
        params = {
            'metric': ','.join(metrics),
            'period': 'day',
            'since': self._format_date_for_api(start_date, 'unix'),
            'until': self._format_date_for_api(end_date, 'unix'),
            'access_token': self.config.platform['instagram'].access_token
        }
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def _parse_instagram_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Instagram Insights API response"""
        parsed = {
            'overview': {},
            'time_series': [],
            'engagement': {},
            'audience': {}
        }
        
        insights = data.get('data', [])
        
        # Process insights similar to Facebook
        metric_data = {}
        for insight in insights:
            metric_name = insight.get('name', '')
            values = insight.get('values', [])
            
            metric_data[metric_name] = {}
            for value_item in values:
                date = value_item.get('end_time', '')[:10]
                metric_data[metric_name][date] = value_item.get('value', 0)
        
        # Calculate overview
        total_impressions = sum(metric_data.get('impressions', {}).values())
        total_reach = sum(metric_data.get('reach', {}).values())
        total_profile_views = sum(metric_data.get('profile_views', {}).values())
        
        parsed['overview'] = {
            'total_impressions': total_impressions,
            'total_reach': total_reach,
            'total_profile_views': total_profile_views,
            'reach_rate': (total_reach / total_impressions * 100) if total_impressions > 0 else 0
        }
        
        return parsed


class TikTokAnalyticsParser(BaseAnalyticsParser):
    """Parser for TikTok Analytics data"""
    
    def get_platform_name(self) -> str:
        return "tiktok_analytics"
    
    async def parse_analytics(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Parse TikTok Analytics data"""
        try:
            start_date, end_date = self._calculate_date_range(kwargs.get('days'))
            
            # TikTok analytics would require their business API
            analytics_data = await self._get_tiktok_analytics(user_id, start_date, end_date)
            parsed_data = await self._parse_tiktok_analytics(analytics_data)
            
            return {
                'platform': self.get_platform_name(),
                'user_id': user_id,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'data': parsed_data,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise AnalyticsParsingError(
                f"TikTok Analytics parsing failed: {str(e)}",
                analytics_platform="tiktok",
                parser_type="TikTokAnalyticsParser"
            )
    
    async def _get_tiktok_analytics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get TikTok Analytics data (placeholder)"""
        # Implementation would use TikTok Business API
        return {}
    
    async def _parse_tiktok_analytics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse TikTok Analytics data"""
        return {
            'overview': {},
            'time_series': [],
            'engagement': {},
            'audience': {}
        }


class SpotifyAnalyticsParser(BaseAnalyticsParser):
    """Parser for Spotify for Artists analytics data"""
    
    def get_platform_name(self) -> str:
        return "spotify_analytics"
    
    async def parse_analytics(self, artist_id: str, **kwargs) -> Dict[str, Any]:
        """Parse Spotify analytics data"""
        try:
            start_date, end_date = self._calculate_date_range(kwargs.get('days'))
            
            analytics_data = await self._get_spotify_analytics(artist_id, start_date, end_date)
            parsed_data = await self._parse_spotify_analytics(analytics_data)
            
            return {
                'platform': self.get_platform_name(),
                'artist_id': artist_id,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'data': parsed_data,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise AnalyticsParsingError(
                f"Spotify Analytics parsing failed: {str(e)}",
                analytics_platform="spotify",
                parser_type="SpotifyAnalyticsParser"
            )
    
    async def _get_spotify_analytics(self, artist_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get Spotify analytics data"""
        # This would require Spotify for Artists API access
        # Currently, there's no public API for detailed analytics
        return {}
    
    async def _parse_spotify_analytics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Spotify analytics data"""
        return {
            'overview': {
                'total_streams': 0,
                'monthly_listeners': 0,
                'followers': 0,
                'top_tracks': []
            },
            'time_series': [],
            'demographics': {},
            'playlists': {}
        }
