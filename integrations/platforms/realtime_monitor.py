"""
Real-Time Social Media Monitoring
=================================

Real-time streaming and monitoring capabilities for social media platforms.
Handles live data streams, keyword monitoring, and intelligent content detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import websockets
import re
from urllib.parse import urlencode

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class StreamEvent:
    """Real-time stream event"""
    platform: str
    event_type: str  # "tweet", "mention", "hashtag", "retweet", etc.
    content_id: str
    author_id: str
    author_username: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    keywords_matched: List[str] = None
    sentiment_score: float = 0.0
    is_copyright_related: bool = False


@dataclass
class MonitoringRule:
    """Content monitoring rule"""
    rule_id: str
    platform: str
    keywords: List[str]
    hashtags: List[str] = None
    users: List[str] = None
    languages: List[str] = None
    is_active: bool = True
    callback_url: Optional[str] = None
    alert_threshold: int = 10  # Alert after N matches
    created_at: datetime = None


class RealTimeMonitor:
    """Real-time social media monitoring system"""
    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.active_streams: Dict[str, Any] = {}
        self.monitoring_rules: Dict[str, MonitoringRule] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.copyright_keywords = [
            "copyright", "dmca", "stolen", "unauthorized", "pirated",
            "illegal download", "infringement", "takedown"
        ]
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.rate_limiter.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Close all active streams
        for stream_id, stream_info in self.active_streams.items():
            if "websocket" in stream_info and not stream_info["websocket"].closed:
                await stream_info["websocket"].close()
                
        if self.session:
            await self.session.close()
        await self.rate_limiter.__aexit__(exc_type, exc_val, exc_tb)
        
    def add_monitoring_rule(self, rule: MonitoringRule):
        """Add a content monitoring rule"""
        self.monitoring_rules[rule.rule_id] = rule
        logger.info(f"Added monitoring rule: {rule.rule_id} for platform {rule.platform}")
        
    def remove_monitoring_rule(self, rule_id: str):
        """Remove a monitoring rule"""
        if rule_id in self.monitoring_rules:
            del self.monitoring_rules[rule_id]
            logger.info(f"Removed monitoring rule: {rule_id}")
            
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler for stream events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    async def start_twitter_stream(self, tokens: OAuthTokens, rules: List[Dict[str, Any]]) -> str:
        """Start Twitter real-time stream with filtered rules"""
        
        stream_id = f"twitter_stream_{datetime.now().timestamp()}"
        
        # Twitter API v2 filtered stream endpoint
        base_url = "https://api.twitter.com/2/tweets/search/stream"
        
        headers = {
            "Authorization": f"{tokens.token_type} {tokens.access_token}",
            "Accept": "application/json"
        }
        
        # Add rules to Twitter stream
        rules_url = f"{base_url}/rules"
        
        # Delete existing rules first
        try:
            existing_rules_response = await self.session.get(rules_url, headers=headers)
            if existing_rules_response.status == 200:
                existing_rules = await existing_rules_response.json()
                if existing_rules.get("data"):
                    delete_payload = {
                        "delete": {
                            "ids": [rule["id"] for rule in existing_rules["data"]]
                        }
                    }
                    await self.session.post(rules_url, json=delete_payload, headers=headers)
        except Exception as e:
            logger.warning(f"Could not delete existing Twitter rules: {e}")
            
        # Add new rules
        add_payload = {"add": rules}
        rules_response = await self.session.post(rules_url, json=add_payload, headers=headers)
        
        if rules_response.status != 201:
            error_text = await rules_response.text()
            raise Exception(f"Failed to add Twitter stream rules: {error_text}")
            
        # Start streaming
        stream_params = {
            "tweet.fields": "created_at,author_id,context_annotations,conversation_id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source",
            "user.fields": "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified",
            "expansions": "author_id,referenced_tweets.id,referenced_tweets.id.author_id"
        }
        
        stream_url = f"{base_url}?{urlencode(stream_params)}"
        
        # Start async task for streaming
        stream_task = asyncio.create_task(
            self._handle_twitter_stream(stream_url, headers, stream_id)
        )
        
        self.active_streams[stream_id] = {
            "platform": "twitter",
            "task": stream_task,
            "rules": rules,
            "started_at": datetime.now()
        }
        
        logger.info(f"Started Twitter stream: {stream_id}")
        return stream_id
        
    async def _handle_twitter_stream(self, stream_url: str, headers: Dict[str, str], stream_id: str):
        """Handle Twitter streaming connection"""
        
        try:
            async with self.session.get(stream_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Twitter stream failed: {response.status} - {error_text}")
                    return
                    
                logger.info(f"Twitter stream {stream_id} connected successfully")
                
                async for line in response.content:
                    if line:
                        try:
                            tweet_data = json.loads(line.decode('utf-8'))
                            
                            if "data" in tweet_data:
                                await self._process_twitter_tweet(tweet_data, stream_id)
                                
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.error(f"Error processing Twitter stream data: {e}")
                            
        except Exception as e:
            logger.error(f"Twitter stream {stream_id} error: {e}")
        finally:
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
                
    async def _process_twitter_tweet(self, tweet_data: Dict[str, Any], stream_id: str):
        """Process incoming Twitter tweet from stream"""
        
        data = tweet_data["data"]
        includes = tweet_data.get("includes", {})
        
        # Get author info
        author_info = {}
        if includes.get("users"):
            for user in includes["users"]:
                if user["id"] == data["author_id"]:
                    author_info = user
                    break
                    
        # Create stream event
        event = StreamEvent(
            platform="twitter",
            event_type="tweet",
            content_id=data["id"],
            author_id=data["author_id"],
            author_username=author_info.get("username", ""),
            content=data["text"],
            timestamp=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            metadata={
                "public_metrics": data.get("public_metrics", {}),
                "context_annotations": data.get("context_annotations", []),
                "lang": data.get("lang", ""),
                "possibly_sensitive": data.get("possibly_sensitive", False),
                "author_info": author_info
            }
        )
        
        # Check for copyright-related content
        event.is_copyright_related = self._detect_copyright_content(event.content)
        
        # Calculate sentiment (simple keyword-based approach)
        event.sentiment_score = self._calculate_sentiment(event.content)
        
        # Check against monitoring rules
        matched_rules = self._check_monitoring_rules(event)
        if matched_rules:
            event.keywords_matched = matched_rules
            
        # Call event handlers
        await self._trigger_event_handlers("tweet", event)
        
        # Special handling for copyright detection
        if event.is_copyright_related:
            await self._trigger_event_handlers("copyright_detected", event)
            
    def _detect_copyright_content(self, text: str) -> bool:
        """Detect potential copyright-related content"""
        
        text_lower = text.lower()
        for keyword in self.copyright_keywords:
            if keyword in text_lower:
                return True
                
        # Check for patterns like "download from", "free download", etc.
        copyright_patterns = [
            r"free\s+download",
            r"download\s+from",
            r"watch\s+free",
            r"stream\s+free",
            r"unauthorized\s+copy"
        ]
        
        for pattern in copyright_patterns:
            if re.search(pattern, text_lower):
                return True
                
        return False
        
    def _calculate_sentiment(self, text: str) -> float:
        """Simple sentiment analysis"""
        
        positive_words = ["great", "awesome", "love", "amazing", "fantastic", "good", "excellent"]
        negative_words = ["bad", "terrible", "hate", "awful", "horrible", "worst", "sucks"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
            
        sentiment = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, sentiment))  # Clamp to [-1, 1]
        
    def _check_monitoring_rules(self, event: StreamEvent) -> List[str]:
        """Check event against monitoring rules"""
        
        matched_keywords = []
        
        for rule in self.monitoring_rules.values():
            if not rule.is_active or rule.platform != event.platform:
                continue
                
            # Check keywords
            content_lower = event.content.lower()
            for keyword in rule.keywords:
                if keyword.lower() in content_lower:
                    matched_keywords.append(keyword)
                    
            # Check hashtags
            if rule.hashtags:
                for hashtag in rule.hashtags:
                    if f"#{hashtag.lower()}" in content_lower:
                        matched_keywords.append(f"#{hashtag}")
                        
            # Check users
            if rule.users:
                if event.author_username.lower() in [u.lower() for u in rule.users]:
                    matched_keywords.append(f"@{event.author_username}")
                    
        return matched_keywords
        
    async def _trigger_event_handlers(self, event_type: str, event: StreamEvent):
        """Trigger event handlers for specific event type"""
        
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
                    
    async def start_instagram_monitoring(self, tokens: OAuthTokens, hashtags: List[str]) -> str:
        """Start Instagram hashtag monitoring"""
        
        # Instagram doesn't have real-time streaming API
        # This would use periodic polling of hashtag endpoints
        
        monitor_id = f"instagram_monitor_{datetime.now().timestamp()}"
        
        monitor_task = asyncio.create_task(
            self._poll_instagram_hashtags(tokens, hashtags, monitor_id)
        )
        
        self.active_streams[monitor_id] = {
            "platform": "instagram",
            "task": monitor_task,
            "hashtags": hashtags,
            "started_at": datetime.now()
        }
        
        logger.info(f"Started Instagram monitoring: {monitor_id}")
        return monitor_id
        
    async def _poll_instagram_hashtags(self, tokens: OAuthTokens, hashtags: List[str], monitor_id: str):
        """Poll Instagram hashtags for new content"""
        
        from .instagram_business_api import InstagramBusinessAPI
        
        instagram_api = InstagramBusinessAPI(self.rate_limiter)
        await instagram_api.__aenter__()
        
        try:
            last_check = datetime.now() - timedelta(hours=1)
            
            while monitor_id in self.active_streams:
                for hashtag in hashtags:
                    try:
                        # Get hashtag info and recent media
                        hashtag_info = await instagram_api.get_hashtag_info(tokens, hashtag)
                        if hashtag_info:
                            hashtag_id = hashtag_info["id"]
                            top_media = await instagram_api.get_hashtag_top_media(tokens, hashtag_id, limit=10)
                            
                            for media in top_media:
                                media_timestamp = datetime.fromisoformat(media["timestamp"].replace("Z", "+00:00"))
                                
                                if media_timestamp > last_check:
                                    event = StreamEvent(
                                        platform="instagram",
                                        event_type="hashtag_post",
                                        content_id=media["id"],
                                        author_id="",
                                        author_username="",
                                        content=media.get("caption", ""),
                                        timestamp=media_timestamp,
                                        metadata={"hashtag": hashtag, "media_type": media.get("media_type")},
                                        keywords_matched=[hashtag]
                                    )
                                    
                                    await self._trigger_event_handlers("instagram_post", event)
                                    
                    except Exception as e:
                        logger.warning(f"Error monitoring Instagram hashtag {hashtag}: {e}")
                        
                last_check = datetime.now()
                await asyncio.sleep(300)  # Check every 5 minutes
                
        finally:
            await instagram_api.__aexit__(None, None, None)
            
    async def stop_stream(self, stream_id: str) -> bool:
        """Stop a monitoring stream"""
        
        if stream_id in self.active_streams:
            stream_info = self.active_streams[stream_id]
            
            # Cancel the task
            if "task" in stream_info:
                stream_info["task"].cancel()
                
            # Close websocket if present
            if "websocket" in stream_info and not stream_info["websocket"].closed:
                await stream_info["websocket"].close()
                
            del self.active_streams[stream_id]
            logger.info(f"Stopped stream: {stream_id}")
            return True
            
        return False
        
    async def get_stream_status(self) -> Dict[str, Any]:
        """Get status of all active streams"""
        
        status = {
            "active_streams": len(self.active_streams),
            "monitoring_rules": len(self.monitoring_rules),
            "streams": {}
        }
        
        for stream_id, stream_info in self.active_streams.items():
            status["streams"][stream_id] = {
                "platform": stream_info["platform"],
                "started_at": stream_info["started_at"].isoformat(),
                "running_time": str(datetime.now() - stream_info["started_at"]),
                "is_active": not stream_info.get("task", {}).done() if "task" in stream_info else True
            }
            
        return status
        
    async def get_monitoring_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get monitoring statistics for a date range"""
        
        # This would typically query a database for stored events
        # For now, return basic structure
        
        stats = {
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "total_events": 0,
            "events_by_platform": {},
            "copyright_alerts": 0,
            "top_keywords": [],
            "sentiment_distribution": {
                "positive": 0,
                "neutral": 0,
                "negative": 0
            }
        }
        
        return stats