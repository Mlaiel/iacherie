"""Twitter API v2 Integration
==========================

Complete Twitter API v2 integration for social media management and analytics.
Handles tweets, users, spaces, lists, and comprehensive analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlencode

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class Tweet:
    """
Twitter tweet information"""
    tweet_id: str
    text: str
    author_id: str
    created_at: datetime
    conversation_id: str = None
    in_reply_to_user_id: str = None
    referenced_tweets: List[Dict[str, Any]] = None
    public_metrics: Dict[str, int] = None
    entities: Dict[str, Any] = None
    context_annotations: List[Dict[str, Any]] = None
    attachments: Dict[str, Any] = None


@dataclass
class TwitterUser:
    """
Twitter user information"""
    user_id: str
    username: str
    name: str
    created_at: datetime
    description: str = None
    location: str = None
    pinned_tweet_id: str = None
    profile_image_url: str = None
    protected: bool = False
    public_metrics: Dict[str, int] = None
    url: str = None
    verified: bool = False
    verified_type: str = None


@dataclass
class TwitterAnalytics:
    """
Twitter analytics data"""
    user_id: str
    date_range: Dict[str, str]
    tweet_count: int = 0
    impression_count: int = 0
    profile_visits: int = 0
    mentions: int = 0
    followers_gained: int = 0
    followers_lost: int = 0


class TwitterAPIv2:
    """
Twitter API v2 integration"""
    
    def __init__(self, rate_limiter -> None: Optional[APIRateLimiter] = None) -> None:
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://api.twitter.com/2"
        
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.rate_limiter.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
Async context manager exit"""
        if self.session:
            await self.session.close()
        await self.rate_limiter.__aexit__(exc_type, exc_val, exc_tb)
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        tokens: OAuthTokens,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
Make authenticated API request with rate limiting"""
        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("twitter", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("twitter", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {tokens.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=headers) as response:
                    await self.rate_limiter.record_request("twitter", endpoint, None, response.status)
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        raise Exception("Rate limit exceeded")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers, params=params) as response:
                    await self.rate_limiter.record_request("twitter", endpoint, None, response.status)
                    
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=headers, params=params) as response:
                    await self.rate_limiter.record_request("twitter", endpoint, None, response.status)
                    
                    if response.status in [200, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Twitter API request failed: {e}")
            raise
            
    async def get_me(self, tokens: OAuthTokens) -> TwitterUser:
        """Get authenticated user's information"""
        user_fields = [
            "id", "username", "name", "created_at", "description",
            "location", "pinned_tweet_id", "profile_image_url", "protected",
            "public_metrics", "url", "verified", "verified_type"
        ]
        
        params = {"user.fields": ",".join(user_fields)}
        
        response = await self._make_request("GET", "users/me", tokens, params=params)
        
        user_data = response.get("data", {})
        
        user = TwitterUser(
            user_id=user_data["id"],
            username=user_data["username"],
            name=user_data["name"],
            created_at=datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00")),
            description=user_data.get("description"),
            location=user_data.get("location"),
            pinned_tweet_id=user_data.get("pinned_tweet_id"),
            profile_image_url=user_data.get("profile_image_url"),
            protected=user_data.get("protected", False),
            public_metrics=user_data.get("public_metrics", {}),
            url=user_data.get("url"),
            verified=user_data.get("verified", False),
            verified_type=user_data.get("verified_type")
        )
        
        return user
        
    async def get_user_by_username(self, tokens: OAuthTokens, username: str) -> TwitterUser:
        """Get user by username"""
        user_fields = [
            "id", "username", "name", "created_at", "description",
            "location", "pinned_tweet_id", "profile_image_url", "protected",
            "public_metrics", "url", "verified", "verified_type"
        ]
        
        params = {"user.fields": ",".join(user_fields)}
        
        response = await self._make_request("GET", f"users/by/username/{username}", tokens, params=params)
        
        user_data = response.get("data", {})
        
        user = TwitterUser(
            user_id=user_data["id"],
            username=user_data["username"],
            name=user_data["name"],
            created_at=datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00")),
            description=user_data.get("description"),
            location=user_data.get("location"),
            pinned_tweet_id=user_data.get("pinned_tweet_id"),
            profile_image_url=user_data.get("profile_image_url"),
            protected=user_data.get("protected", False),
            public_metrics=user_data.get("public_metrics", {}),
            url=user_data.get("url"),
            verified=user_data.get("verified", False),
            verified_type=user_data.get("verified_type")
        )
        
        return user
        
    async def create_tweet(
        self,
        tokens: OAuthTokens,
        text: str,
        reply_to_tweet_id: Optional[str] = None,
        media_ids: Optional[List[str]] = None,
        poll_options: Optional[List[str]] = None,
        poll_duration_minutes: int = 1440
    ) -> Tweet:
        """Create a new tweet"""
        
        data = {"text": text}
        
        if reply_to_tweet_id:
            data["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}
            
        if media_ids:
            data["media"] = {"media_ids": media_ids}
            
        if poll_options and len(poll_options) >= 2:
            data["poll"] = {
                "options": poll_options[:4],  # Max 4 options
                "duration_minutes": poll_duration_minutes
            }
            
        response = await self._make_request("POST", "tweets", tokens, data=data)
        
        tweet_data = response.get("data", {})
        
        tweet = Tweet(
            tweet_id=tweet_data["id"],
            text=tweet_data["text"],
            author_id="",  # Will be set to current user
            created_at=datetime.now()  # API doesn't return this in create response
        )
        
        logger.info(f"Created tweet: {tweet.tweet_id}")
        return tweet
        
    async def delete_tweet(self, tokens: OAuthTokens, tweet_id: str) -> bool:
        """Delete a tweet"""
        
        try:
            response = await self._make_request("DELETE", f"tweets/{tweet_id}", tokens)
            deleted = response.get("data", {}).get("deleted", False)
            
            if deleted:
                logger.info(f"Deleted tweet: {tweet_id}")
                
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete tweet {tweet_id}: {e}")
            return False
            
    async def get_tweets(
        self,
        tokens: OAuthTokens,
        tweet_ids: Union[str, List[str]],
        tweet_fields: Optional[List[str]] = None,
        user_fields: Optional[List[str]] = None,
        expansions: Optional[List[str]] = None
    ) -> List[Tweet]:
        """Get tweets by IDs"""
        
        if isinstance(tweet_ids, str):
            tweet_ids = [tweet_ids]
            
        default_tweet_fields = [
            "id", "text", "author_id", "created_at", "conversation_id",
            "in_reply_to_user_id", "referenced_tweets", "public_metrics",
            "entities", "context_annotations", "attachments"
        ]
        
        params = {
            "ids": ",".join(tweet_ids[:100]),  # Max 100 per request
            "tweet.fields": ",".join(tweet_fields or default_tweet_fields)
        }
        
        if user_fields:
            params["user.fields"] = ",".join(user_fields)
        if expansions:
            params["expansions"] = ",".join(expansions)
            
        response = await self._make_request("GET", "tweets", tokens, params=params)
        
        tweets = []
        for tweet_data in response.get("data", []):
            tweet = Tweet(
                tweet_id=tweet_data["id"],
                text=tweet_data["text"],
                author_id=tweet_data["author_id"],
                created_at=datetime.fromisoformat(tweet_data["created_at"].replace("Z", "+00:00")),
                conversation_id=tweet_data.get("conversation_id"),
                in_reply_to_user_id=tweet_data.get("in_reply_to_user_id"),
                referenced_tweets=tweet_data.get("referenced_tweets", []),
                public_metrics=tweet_data.get("public_metrics", {}),
                entities=tweet_data.get("entities"),
                context_annotations=tweet_data.get("context_annotations", []),
                attachments=tweet_data.get("attachments")
            )
            tweets.append(tweet)
            
        return tweets
        
    async def get_user_tweets(
        self,
        tokens: OAuthTokens,
        user_id: str,
        max_results: int = 10,
        exclude: Optional[List[str]] = None,
        pagination_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get tweets from a user"""
        
        tweet_fields = [
            "id", "text", "author_id", "created_at", "public_metrics",
            "entities", "context_annotations", "referenced_tweets"
        ]
        
        params = {
            "max_results": min(max_results, 100),
            "tweet.fields": ",".join(tweet_fields)
        }
        
        if exclude:
            params["exclude"] = ",".join(exclude)
        if pagination_token:
            params["pagination_token"] = pagination_token
            
        return await self._make_request("GET", f"users/{user_id}/tweets", tokens, params=params)
        
    async def search_tweets(
        self,
        tokens: OAuthTokens,
        query: str,
        max_results: int = 10,
        sort_order: str = "relevancy",  # "relevancy" or "recency"
        next_token: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Search for tweets"""
        
        tweet_fields = [
            "id", "text", "author_id", "created_at", "public_metrics",
            "entities", "context_annotations", "referenced_tweets"
        ]
        
        params = {
            "query": query,
            "max_results": min(max_results, 100),
            "sort_order": sort_order,
            "tweet.fields": ",".join(tweet_fields)
        }
        
        if next_token:
            params["next_token"] = next_token
        if start_time:
            params["start_time"] = start_time.isoformat() + "Z"
        if end_time:
            params["end_time"] = end_time.isoformat() + "Z"
            
        return await self._make_request("GET", "tweets/search/recent", tokens, params=params)
        
    async def like_tweet(self, tokens: OAuthTokens, user_id: str, tweet_id: str) -> bool:
        """Like a tweet"""
        
        data = {"tweet_id": tweet_id}
        
        try:
            response = await self._make_request("POST", f"users/{user_id}/likes", tokens, data=data)
            liked = response.get("data", {}).get("liked", False)
            
            if liked:
                logger.info(f"Liked tweet: {tweet_id}")
                
            return liked
            
        except Exception as e:
            logger.error(f"Failed to like tweet {tweet_id}: {e}")
            return False
            
    async def unlike_tweet(self, tokens: OAuthTokens, user_id: str, tweet_id: str) -> bool:
        """Unlike a tweet"""
        
        try:
            response = await self._make_request("DELETE", f"users/{user_id}/likes/{tweet_id}", tokens)
            unliked = response.get("data", {}).get("liked", True) == False
            
            if unliked:
                logger.info(f"Unliked tweet: {tweet_id}")
                
            return unliked
            
        except Exception as e:
            logger.error(f"Failed to unlike tweet {tweet_id}: {e}")
            return False
            
    async def retweet(self, tokens: OAuthTokens, user_id: str, tweet_id: str) -> bool:
        """Retweet a tweet"""
        
        data = {"tweet_id": tweet_id}
        
        try:
            response = await self._make_request("POST", f"users/{user_id}/retweets", tokens, data=data)
            retweeted = response.get("data", {}).get("retweeted", False)
            
            if retweeted:
                logger.info(f"Retweeted: {tweet_id}")
                
            return retweeted
            
        except Exception as e:
            logger.error(f"Failed to retweet {tweet_id}: {e}")
            return False
            
    async def unretweet(self, tokens: OAuthTokens, user_id: str, tweet_id: str) -> bool:
        """Remove retweet"""
        
        try:
            response = await self._make_request("DELETE", f"users/{user_id}/retweets/{tweet_id}", tokens)
            unretweeted = response.get("data", {}).get("retweeted", True) == False
            
            if unretweeted:
                logger.info(f"Unretweeted: {tweet_id}")
                
            return unretweeted
            
        except Exception as e:
            logger.error(f"Failed to unretweet {tweet_id}: {e}")
            return False
            
    async def follow_user(self, tokens: OAuthTokens, user_id: str, target_user_id: str) -> bool:
        """Follow a user"""
        
        data = {"target_user_id": target_user_id}
        
        try:
            response = await self._make_request("POST", f"users/{user_id}/following", tokens, data=data)
            following = response.get("data", {}).get("following", False)
            
            if following:
                logger.info(f"Following user: {target_user_id}")
                
            return following
            
        except Exception as e:
            logger.error(f"Failed to follow user {target_user_id}: {e}")
            return False
            
    async def unfollow_user(self, tokens: OAuthTokens, user_id: str, target_user_id: str) -> bool:
        """Unfollow a user"""
        
        try:
            response = await self._make_request("DELETE", f"users/{user_id}/following/{target_user_id}", tokens)
            unfollowed = response.get("data", {}).get("following", True) == False
            
            if unfollowed:
                logger.info(f"Unfollowed user: {target_user_id}")
                
            return unfollowed
            
        except Exception as e:
            logger.error(f"Failed to unfollow user {target_user_id}: {e}")
            return False
            
    async def get_followers(
        self,
        tokens: OAuthTokens,
        user_id: str,
        max_results: int = 100,
        pagination_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's followers"""
        
        user_fields = ["id", "username", "name", "public_metrics", "verified"]
        
        params = {
            "max_results": min(max_results, 1000),
            "user.fields": ",".join(user_fields)
        }
        
        if pagination_token:
            params["pagination_token"] = pagination_token
            
        return await self._make_request("GET", f"users/{user_id}/followers", tokens, params=params)
        
    async def get_following(
        self,
        tokens: OAuthTokens,
        user_id: str,
        max_results: int = 100,
        pagination_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get users that a user is following"""
        
        user_fields = ["id", "username", "name", "public_metrics", "verified"]
        
        params = {
            "max_results": min(max_results, 1000),
            "user.fields": ",".join(user_fields)
        }
        
        if pagination_token:
            params["pagination_token"] = pagination_token
            
        return await self._make_request("GET", f"users/{user_id}/following", tokens, params=params)
        
    async def get_mentions(
        self,
        tokens: OAuthTokens,
        user_id: str,
        max_results: int = 10,
        pagination_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get tweets mentioning the user"""
        
        tweet_fields = [
            "id", "text", "author_id", "created_at", "public_metrics",
            "entities", "context_annotations", "referenced_tweets"
        ]
        
        params = {
            "max_results": min(max_results, 100),
            "tweet.fields": ",".join(tweet_fields)
        }
        
        if pagination_token:
            params["pagination_token"] = pagination_token
            
        return await self._make_request("GET", f"users/{user_id}/mentions", tokens, params=params)