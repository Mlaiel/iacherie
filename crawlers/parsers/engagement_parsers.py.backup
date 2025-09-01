"""Engagement Parsers Module
========================

Specialized parsers for extracting engagement metrics from social media platforms.
Handles likes, comments, shares, reactions, and interaction analysis.

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
from collections import defaultdict

import aiohttp
from bs4 import BeautifulSoup

from .exceptions import EngagementParsingError, AuthenticationError, RateLimitError
from .parser_config import ParserConfig


class BaseEngagementParser(ABC):
    """Abstract base class for engagement parsers"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.engagement_config = config.engagement
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
    async def parse_engagement(self, content_id: str, **kwargs) -> Dict[str, Any]:
        """Parse engagement data for specific content"""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the platform name for this engagement parser"""
        pass
    
    def _calculate_engagement_rate(self, interactions: int, impressions: int) -> float:
        """Calculate engagement rate as percentage"""
        if impressions == 0:
            return 0.0
        return (interactions / impressions) * 100
    
    def _classify_engagement_level(self, engagement_rate: float) -> str:
        """Classify engagement level based on rate"""
        if engagement_rate >= 10:
            return "excellent"
        elif engagement_rate >= 5:
            return "good"
        elif engagement_rate >= 2:
            return "average"
        elif engagement_rate >= 1:
            return "low"
        else:
            return "very_low"
    
    def _analyze_sentiment(self, comments: List[str]) -> Dict[str, Any]:
        """Basic sentiment analysis of comments"""
        if not comments:
            return {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
        
        positive_words = ['good', 'great', 'amazing', 'awesome', 'love', 'excellent', 'fantastic', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting', 'stupid']
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for comment in comments:
            comment_lower = comment.lower()
            positive_score = sum(1 for word in positive_words if word in comment_lower)
            negative_score = sum(1 for word in negative_words if word in comment_lower)
            
            if positive_score > negative_score:
                sentiment_counts['positive'] += 1
            elif negative_score > positive_score:
                sentiment_counts['negative'] += 1
            else:
                sentiment_counts['neutral'] += 1
        
        sentiment_counts['total'] = len(comments)
        return sentiment_counts


class YouTubeEngagementParser(BaseEngagementParser):
    """Parser for YouTube engagement metrics"""
    
    def get_platform_name(self) -> str:
        return "youtube"
    
    async def parse_engagement(self, video_id: str, **kwargs) -> Dict[str, Any]:
        """Parse YouTube video engagement"""
        try:
            video_data = await self._get_video_data(video_id)
            comments_data = await self._get_comments_data(video_id)
            
            parsed_engagement = await self._parse_youtube_engagement(video_data, comments_data)
            
            return {
                'platform': self.get_platform_name(),
                'content_id': video_id,
                'content_type': 'video',
                'data': parsed_engagement,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise EngagementParsingError(
                f"YouTube engagement parsing failed: {str(e)}",
                platform="youtube",
                content_id=video_id,
                parser_type="YouTubeEngagementParser"
            )
    
    async def _get_video_data(self, video_id: str) -> Dict[str, Any]:
        """Get video statistics from YouTube Data API"""
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'id': video_id,
            'part': 'statistics,snippet',
            'key': self.config.platform['youtube'].api_key
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 403:
                raise AuthenticationError(
                    "YouTube API quota exceeded or invalid key",
                    platform="youtube",
                    auth_type="api_key"
                )
            
            response.raise_for_status()
            data = await response.json()
            
            if not data.get('items'):
                raise EngagementParsingError(
                    f"Video not found: {video_id}",
                    platform="youtube",
                    content_id=video_id
                )
            
            return data['items'][0]
    
    async def _get_comments_data(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get comments from YouTube Data API"""
        url = "https://www.googleapis.com/youtube/v3/commentThreads"
        params = {
            'videoId': video_id,
            'part': 'snippet',
            'maxResults': min(max_results, 100),
            'order': 'relevance',
            'key': self.config.platform['youtube'].api_key
        }
        
        all_comments = []
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                for item in data.get('items', []):
                    comment_snippet = item['snippet']['topLevelComment']['snippet']
                    all_comments.append({
                        'text': comment_snippet['textDisplay'],
                        'author': comment_snippet['authorDisplayName'],
                        'likes': comment_snippet.get('likeCount', 0),
                        'published_at': comment_snippet['publishedAt'],
                        'reply_count': item['snippet'].get('totalReplyCount', 0)
                    })
                
        except Exception as e:
            # Comments might be disabled, continue without them
            pass
        
        return all_comments
    
    async def _parse_youtube_engagement(self, video_data: Dict[str, Any], comments_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse YouTube engagement metrics"""
        statistics = video_data.get('statistics', {})
        snippet = video_data.get('snippet', {})
        
        # Basic metrics
        views = int(statistics.get('viewCount', 0))
        likes = int(statistics.get('likeCount', 0))
        comment_count = int(statistics.get('commentCount', 0))
        
        # Calculate engagement metrics
        total_interactions = likes + comment_count
        engagement_rate = self._calculate_engagement_rate(total_interactions, views)
        engagement_level = self._classify_engagement_level(engagement_rate)
        
        # Analyze comments
        comment_texts = [comment['text'] for comment in comments_data]
        sentiment_analysis = self._analyze_sentiment(comment_texts)
        
        # Comment engagement analysis
        comment_likes = sum(comment['likes'] for comment in comments_data)
        avg_comment_likes = comment_likes / len(comments_data) if comments_data else 0
        
        # Top commenters
        author_comments = defaultdict(int)
        for comment in comments_data:
            author_comments[comment['author']] += 1
        
        top_commenters = sorted(author_comments.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'overview': {
                'views': views,
                'likes': likes,
                'comments': comment_count,
                'total_interactions': total_interactions,
                'engagement_rate': round(engagement_rate, 2),
                'engagement_level': engagement_level
            },
            'interactions': {
                'likes_per_view': round(likes / views * 1000, 2) if views > 0 else 0,
                'comments_per_view': round(comment_count / views * 1000, 2) if views > 0 else 0,
                'avg_comment_likes': round(avg_comment_likes, 2)
            },
            'comments_analysis': {
                'total_comments_analyzed': len(comments_data),
                'sentiment': sentiment_analysis,
                'top_commenters': [{'author': author, 'comment_count': count} for author, count in top_commenters],
                'avg_comment_length': sum(len(comment['text']) for comment in comments_data) / len(comments_data) if comments_data else 0
            },
            'content_info': {
                'title': snippet.get('title', ''),
                'published_at': snippet.get('publishedAt', ''),
                'duration': snippet.get('duration', ''),
                'category': snippet.get('categoryId', ''),
                'tags': snippet.get('tags', [])
            }
        }


class InstagramEngagementParser(BaseEngagementParser):
    """Parser for Instagram engagement metrics"""
    
    def get_platform_name(self) -> str:
        return "instagram"
    
    async def parse_engagement(self, media_id: str, **kwargs) -> Dict[str, Any]:
        """Parse Instagram media engagement"""
        try:
            media_data = await self._get_media_data(media_id)
            comments_data = await self._get_media_comments(media_id)
            
            parsed_engagement = await self._parse_instagram_engagement(media_data, comments_data)
            
            return {
                'platform': self.get_platform_name(),
                'content_id': media_id,
                'content_type': media_data.get('media_type', 'unknown'),
                'data': parsed_engagement,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise EngagementParsingError(
                f"Instagram engagement parsing failed: {str(e)}",
                platform="instagram",
                content_id=media_id,
                parser_type="InstagramEngagementParser"
            )
    
    async def _get_media_data(self, media_id: str) -> Dict[str, Any]:
        """Get media data from Instagram Basic Display API"""
        url = f"https://graph.instagram.com/{media_id}"
        params = {
            'fields': 'id,media_type,media_url,permalink,timestamp,caption,like_count,comments_count',
            'access_token': self.config.platform['instagram'].access_token
        }
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def _get_media_comments(self, media_id: str) -> List[Dict[str, Any]]:
        """Get comments for Instagram media"""
        url = f"https://graph.instagram.com/{media_id}/comments"
        params = {
            'fields': 'id,text,timestamp,username,like_count',
            'access_token': self.config.platform['instagram'].access_token
        }
        
        all_comments = []
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                all_comments = data.get('data', [])
                
        except Exception as e:
            # Comments might not be accessible
            pass
        
        return all_comments
    
    async def _parse_instagram_engagement(self, media_data: Dict[str, Any], comments_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse Instagram engagement metrics"""
        likes = media_data.get('like_count', 0)
        comments_count = media_data.get('comments_count', 0)
        
        # For Instagram, we don't have view count, so we use likes + comments as base
        total_interactions = likes + comments_count
        
        # Analyze comments
        comment_texts = [comment['text'] for comment in comments_data]
        sentiment_analysis = self._analyze_sentiment(comment_texts)
        
        # Comment engagement
        comment_likes = sum(comment.get('like_count', 0) for comment in comments_data)
        avg_comment_likes = comment_likes / len(comments_data) if comments_data else 0
        
        # Hashtag analysis
        caption = media_data.get('caption', '')
        hashtags = re.findall(r'#\w+', caption) if caption else []
        mentions = re.findall(r'@\w+', caption) if caption else []
        
        return {
            'overview': {
                'likes': likes,
                'comments': comments_count,
                'total_interactions': total_interactions,
                'media_type': media_data.get('media_type', 'unknown')
            },
            'interactions': {
                'like_to_comment_ratio': round(likes / comments_count, 2) if comments_count > 0 else 0,
                'avg_comment_likes': round(avg_comment_likes, 2)
            },
            'comments_analysis': {
                'total_comments_analyzed': len(comments_data),
                'sentiment': sentiment_analysis,
                'avg_comment_length': sum(len(comment['text']) for comment in comments_data) / len(comments_data) if comments_data else 0
            },
            'content_analysis': {
                'hashtags': hashtags,
                'hashtag_count': len(hashtags),
                'mentions': mentions,
                'mention_count': len(mentions),
                'caption_length': len(caption) if caption else 0
            },
            'content_info': {
                'media_url': media_data.get('media_url', ''),
                'permalink': media_data.get('permalink', ''),
                'timestamp': media_data.get('timestamp', ''),
                'caption': caption
            }
        }


class FacebookEngagementParser(BaseEngagementParser):
    """Parser for Facebook engagement metrics"""
    
    def get_platform_name(self) -> str:
        return "facebook"
    
    async def parse_engagement(self, post_id: str, **kwargs) -> Dict[str, Any]:
        """Parse Facebook post engagement"""
        try:
            post_data = await self._get_post_data(post_id)
            comments_data = await self._get_post_comments(post_id)
            reactions_data = await self._get_post_reactions(post_id)
            
            parsed_engagement = await self._parse_facebook_engagement(post_data, comments_data, reactions_data)
            
            return {
                'platform': self.get_platform_name(),
                'content_id': post_id,
                'content_type': 'post',
                'data': parsed_engagement,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise EngagementParsingError(
                f"Facebook engagement parsing failed: {str(e)}",
                platform="facebook",
                content_id=post_id,
                parser_type="FacebookEngagementParser"
            )
    
    async def _get_post_data(self, post_id: str) -> Dict[str, Any]:
        """Get post data from Facebook Graph API"""
        url = f"https://graph.facebook.com/v18.0/{post_id}"
        params = {
            'fields': 'id,message,created_time,shares,likes.summary(true),comments.summary(true),reactions.summary(true)',
            'access_token': self.config.platform['facebook'].access_token
        }
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def _get_post_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """Get comments for Facebook post"""
        url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
        params = {
            'fields': 'id,message,created_time,from,like_count',
            'limit': 100,
            'access_token': self.config.platform['facebook'].access_token
        }
        
        all_comments = []
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                all_comments = data.get('data', [])
                
        except Exception as e:
            pass
        
        return all_comments
    
    async def _get_post_reactions(self, post_id: str) -> Dict[str, int]:
        """Get reaction breakdown for Facebook post"""
        reactions = {}
        reaction_types = ['LIKE', 'LOVE', 'WOW', 'HAHA', 'SAD', 'ANGRY', 'THANKFUL']
        
        for reaction_type in reaction_types:
            url = f"https://graph.facebook.com/v18.0/{post_id}/reactions"
            params = {
                'type': reaction_type,
                'summary': 'total_count',
                'access_token': self.config.platform['facebook'].access_token
            }
            
            try:
                async with self.session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    reactions[reaction_type.lower()] = data.get('summary', {}).get('total_count', 0)
            except Exception as e:
                reactions[reaction_type.lower()] = 0
        
        return reactions
    
    async def _parse_facebook_engagement(self, post_data: Dict[str, Any], comments_data: List[Dict[str, Any]], reactions_data: Dict[str, int]) -> Dict[str, Any]:
        """Parse Facebook engagement metrics"""
        # Extract basic metrics
        total_reactions = sum(reactions_data.values())
        comments_count = post_data.get('comments', {}).get('summary', {}).get('total_count', 0)
        shares_count = post_data.get('shares', {}).get('count', 0)
        
        total_interactions = total_reactions + comments_count + shares_count
        
        # Analyze comments
        comment_texts = [comment.get('message', '') for comment in comments_data if comment.get('message')]
        sentiment_analysis = self._analyze_sentiment(comment_texts)
        
        # Comment engagement
        comment_likes = sum(comment.get('like_count', 0) for comment in comments_data)
        avg_comment_likes = comment_likes / len(comments_data) if comments_data else 0
        
        return {
            'overview': {
                'total_reactions': total_reactions,
                'comments': comments_count,
                'shares': shares_count,
                'total_interactions': total_interactions
            },
            'reactions': reactions_data,
            'reaction_analysis': {
                'most_common_reaction': max(reactions_data.items(), key=lambda x: x[1])[0] if reactions_data else None,
                'positive_reactions': reactions_data.get('like', 0) + reactions_data.get('love', 0) + reactions_data.get('wow', 0),
                'negative_reactions': reactions_data.get('sad', 0) + reactions_data.get('angry', 0)
            },
            'comments_analysis': {
                'total_comments_analyzed': len(comments_data),
                'sentiment': sentiment_analysis,
                'avg_comment_likes': round(avg_comment_likes, 2),
                'avg_comment_length': sum(len(comment.get('message', '')) for comment in comments_data) / len(comments_data) if comments_data else 0
            },
            'content_info': {
                'message': post_data.get('message', ''),
                'created_time': post_data.get('created_time', ''),
                'post_id': post_data.get('id', '')
            }
        }


class TwitterEngagementParser(BaseEngagementParser):
    """Parser for Twitter engagement metrics"""
    
    def get_platform_name(self) -> str:
        return "twitter"
    
    async def parse_engagement(self, tweet_id: str, **kwargs) -> Dict[str, Any]:
        """Parse Twitter tweet engagement"""
        try:
            tweet_data = await self._get_tweet_data(tweet_id)
            parsed_engagement = await self._parse_twitter_engagement(tweet_data)
            
            return {
                'platform': self.get_platform_name(),
                'content_id': tweet_id,
                'content_type': 'tweet',
                'data': parsed_engagement,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise EngagementParsingError(
                f"Twitter engagement parsing failed: {str(e)}",
                platform="twitter",
                content_id=tweet_id,
                parser_type="TwitterEngagementParser"
            )
    
    async def _get_tweet_data(self, tweet_id: str) -> Dict[str, Any]:
        """Get tweet data from Twitter API v2"""
        url = f"https://api.twitter.com/2/tweets/{tweet_id}"
        params = {
            'expansions': 'author_id,referenced_tweets.id',
            'tweet.fields': 'created_at,text,public_metrics,context_annotations,entities',
            'user.fields': 'name,username,verified,public_metrics'
        }
        
        headers = {
            'Authorization': f'Bearer {self.config.platform["twitter"].bearer_token}'
        }
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status == 401:
                raise AuthenticationError(
                    "Twitter API authentication failed",
                    platform="twitter",
                    auth_type="bearer_token"
                )
            
            response.raise_for_status()
            return await response.json()
    
    async def _parse_twitter_engagement(self, tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Twitter engagement metrics"""
        data = tweet_data.get('data', {})
        public_metrics = data.get('public_metrics', {})
        
        # Basic metrics
        retweets = public_metrics.get('retweet_count', 0)
        likes = public_metrics.get('like_count', 0)
        replies = public_metrics.get('reply_count', 0)
        quotes = public_metrics.get('quote_count', 0)
        impressions = public_metrics.get('impression_count', 0)
        
        total_interactions = retweets + likes + replies + quotes
        engagement_rate = self._calculate_engagement_rate(total_interactions, impressions)
        engagement_level = self._classify_engagement_level(engagement_rate)
        
        # Analyze tweet content
        text = data.get('text', '')
        hashtags = re.findall(r'#\w+', text)
        mentions = re.findall(r'@\w+', text)
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        return {
            'overview': {
                'impressions': impressions,
                'retweets': retweets,
                'likes': likes,
                'replies': replies,
                'quotes': quotes,
                'total_interactions': total_interactions,
                'engagement_rate': round(engagement_rate, 2),
                'engagement_level': engagement_level
            },
            'interaction_ratios': {
                'likes_per_impression': round(likes / impressions * 1000, 2) if impressions > 0 else 0,
                'retweets_per_impression': round(retweets / impressions * 1000, 2) if impressions > 0 else 0,
                'replies_per_impression': round(replies / impressions * 1000, 2) if impressions > 0 else 0,
                'like_to_retweet_ratio': round(likes / retweets, 2) if retweets > 0 else 0
            },
            'content_analysis': {
                'text_length': len(text),
                'hashtags': hashtags,
                'hashtag_count': len(hashtags),
                'mentions': mentions,
                'mention_count': len(mentions),
                'urls': urls,
                'url_count': len(urls)
            },
            'content_info': {
                'text': text,
                'created_at': data.get('created_at', ''),
                'tweet_id': data.get('id', '')
            }
        }


class TikTokEngagementParser(BaseEngagementParser):
    """Parser for TikTok engagement metrics"""
    
    def get_platform_name(self) -> str:
        return "tiktok"
    
    async def parse_engagement(self, video_id: str, **kwargs) -> Dict[str, Any]:
        """Parse TikTok video engagement"""
        try:
            # TikTok API access is limited, this would require business API
            video_data = await self._get_tiktok_video_data(video_id)
            parsed_engagement = await self._parse_tiktok_engagement(video_data)
            
            return {
                'platform': self.get_platform_name(),
                'content_id': video_id,
                'content_type': 'video',
                'data': parsed_engagement,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise EngagementParsingError(
                f"TikTok engagement parsing failed: {str(e)}",
                platform="tiktok",
                content_id=video_id,
                parser_type="TikTokEngagementParser"
            )
    
    async def _get_tiktok_video_data(self, video_id: str) -> Dict[str, Any]:
        """Get TikTok video data (placeholder implementation)"""
        # This would require TikTok Business API access
        return {}
    
    async def _parse_tiktok_engagement(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse TikTok engagement metrics"""
        return {
            'overview': {
                'views': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'total_interactions': 0,
                'engagement_rate': 0.0,
                'engagement_level': 'unknown'
            },
            'content_info': {}
        }


class LinkedInEngagementParser(BaseEngagementParser):
    """Parser for LinkedIn engagement metrics"""
    
    def get_platform_name(self) -> str:
        return "linkedin"
    
    async def parse_engagement(self, post_id: str, **kwargs) -> Dict[str, Any]:
        """Parse LinkedIn post engagement"""
        try:
            post_data = await self._get_linkedin_post_data(post_id)
            parsed_engagement = await self._parse_linkedin_engagement(post_data)
            
            return {
                'platform': self.get_platform_name(),
                'content_id': post_id,
                'content_type': 'post',
                'data': parsed_engagement,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise EngagementParsingError(
                f"LinkedIn engagement parsing failed: {str(e)}",
                platform="linkedin",
                content_id=post_id,
                parser_type="LinkedInEngagementParser"
            )
    
    async def _get_linkedin_post_data(self, post_id: str) -> Dict[str, Any]:
        """Get LinkedIn post data"""
        # LinkedIn API implementation would go here
        return {}
    
    async def _parse_linkedin_engagement(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LinkedIn engagement metrics"""
        return {
            'overview': {
                'impressions': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'clicks': 0,
                'total_interactions': 0,
                'engagement_rate': 0.0,
                'engagement_level': 'unknown'
            },
            'professional_metrics': {
                'industry_engagement': {},
                'seniority_engagement': {},
                'function_engagement': {}
            },
            'content_info': {}
        }
