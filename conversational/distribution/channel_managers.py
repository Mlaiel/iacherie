"""Channel Managers

Platform-specific distribution managers for handling unique requirements and APIs.
Each manager handles the specific characteristics and optimization for its platform.

Author: Fahed Mlaiel
Email: mlaiel@live.de
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

import aiohttp
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.exceptions import PlatformError, DistributionError
from ....models.content import ContentModel
from ....utils.rate_limiter import RateLimiter
from .platform_manager import PlatformCredentials, DistributionRequest


logger = logging.getLogger(__name__)


class BasePlatformManager(ABC):
    """Base class for all platform managers"""    
    def __init__(self, db: Session):
        self.db = db
        self.rate_limiter = RateLimiter()
        self.session_pool: Dict[str, aiohttp.ClientSession] = {}
        
    @abstractmethod
    async def distribute_content(
        self,
        credentials: PlatformCredentials,
        content: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Distribute content to the platform"""        pass
    
    @abstractmethod
    async def get_content_metrics(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> Dict[str, Any]:
        """Get metrics for specific content"""        pass
    
    @abstractmethod
    async def delete_content(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> bool:
        """Delete content from platform"""        pass
    
    async def get_session(self, platform: str) -> aiohttp.ClientSession:
        """Get or create HTTP session for platform"""        if platform not in self.session_pool:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session_pool[platform] = aiohttp.ClientSession(timeout=timeout)
        return self.session_pool[platform]
    
    async def close_sessions(self):
        """Close all HTTP sessions"""        for session in self.session_pool.values():
            await session.close()
        self.session_pool.clear()


class YouTubeChannelManager(BasePlatformManager):
    """YouTube platform manager with advanced features"""    
    def __init__(self, db: Session):
        super().__init__(db)
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
        
    async def distribute_content(
        self,
        credentials: PlatformCredentials,
        content: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Upload video to YouTube"""        try:
            # Rate limiting
            await self.rate_limiter.acquire("youtube", credentials.user_id)
            
            session = await self.get_session("youtube")
            
            # Prepare video metadata
            video_metadata = {
                "snippet": {
                    "title": content.get("title", "")[:100],  # YouTube title limit
                    "description": content.get("description", "")[:5000],  # Description limit
                    "tags": content.get("hashtags", [])[:500],  # Tags limit
                    "categoryId": self._get_category_id(content.get("category")),
                    "defaultLanguage": content.get("language", "en"),
                    "defaultAudioLanguage": content.get("language", "en")
                },
                "status": {
                    "privacyStatus": request.schedule_time and "private" or "public",
                    "embeddable": True,
                    "license": "youtube",
                    "publicStatsViewable": True,
                    "publishAt": request.schedule_time.isoformat() if request.schedule_time else None
                },
                "recordingDetails": {
                    "recordingDate": datetime.now().isoformat()
                }
            }
            
            # Prepare upload
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            # Upload video file
            file_url = content.get("file_url")
            if not file_url:
                raise DistributionError("No video file URL provided")
            
            # Download file for upload
            async with session.get(file_url) as response:
                if response.status != 200:
                    raise DistributionError(f"Failed to download video file: {response.status}")
                video_data = await response.read()
            
            # Multipart upload
            form_data = aiohttp.FormData()
            form_data.add_field('snippet', str(video_metadata))
            form_data.add_field('media', video_data, filename="video.mp4", content_type="video/mp4")
            
            upload_params = {
                "part": "snippet,status,recordingDetails",
                "key": credentials.api_key
            }
            
            async with session.post(
                self.upload_url,
                headers={"Authorization": f"Bearer {credentials.access_token}"},
                data=form_data,
                params=upload_params
            ) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise DistributionError(f"YouTube upload failed: {response.status} - {error_text}")
                
                result = await response.json()
                
                return {
                    "success": True,
                    "platform_content_id": result.get("id"),
                    "url": f"https://www.youtube.com/watch?v={result.get('id')}",
                    "platform_response": result,
                    "metadata": {
                        "title": result.get("snippet", {}).get("title"),
                        "description": result.get("snippet", {}).get("description"),
                        "published_at": result.get("snippet", {}).get("publishedAt"),
                        "privacy_status": result.get("status", {}).get("privacyStatus")
                    }
                }
                
        except Exception as e:
            logger.error(f"YouTube distribution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform_content_id": None,
                "url": None
            }
    
    async def get_content_metrics(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> Dict[str, Any]:
        """Get YouTube video analytics"""        try:
            session = await self.get_session("youtube")
            
            # Get video statistics
            params = {
                "part": "statistics,snippet,contentDetails",
                "id": content_id,
                "key": credentials.api_key
            }
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.get(f"{self.api_base_url}/videos", params=params, headers=headers) as response:
                if response.status != 200:
                    raise PlatformError(f"Failed to get YouTube metrics: {response.status}")
                
                data = await response.json()
                items = data.get("items", [])
                
                if not items:
                    return {"error": "Video not found"}
                
                video = items[0]
                stats = video.get("statistics", {})
                snippet = video.get("snippet", {})
                
                return {
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "shares": int(stats.get("favoriteCount", 0)),  # Approximation
                    "engagement_rate": self._calculate_youtube_engagement(stats),
                    "duration": video.get("contentDetails", {}).get("duration"),
                    "published_at": snippet.get("publishedAt"),
                    "title": snippet.get("title"),
                    "platform": "youtube"
                }
                
        except Exception as e:
            logger.error(f"YouTube metrics retrieval failed: {e}")
            return {"error": str(e)}
    
    async def delete_content(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> bool:
        """Delete YouTube video"""        try:
            session = await self.get_session("youtube")
            
            params = {
                "id": content_id,
                "key": credentials.api_key
            }
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.delete(f"{self.api_base_url}/videos", params=params, headers=headers) as response:
                return response.status == 204
                
        except Exception as e:
            logger.error(f"YouTube content deletion failed: {e}")
            return False
    
    def _get_category_id(self, category: Optional[str]) -> str:
        """Map content category to YouTube category ID"""        category_map = {
            "music": "10",
            "entertainment": "24",
            "education": "27",
            "gaming": "20",
            "technology": "28",
            "sports": "17",
            "news": "25",
            "comedy": "23",
            "film": "1",
            "lifestyle": "22"
        }
        return category_map.get(category.lower() if category else "", "22")  # Default to People & Blogs
    
    def _calculate_youtube_engagement(self, stats: Dict[str, Any]) -> float:
        """Calculate YouTube engagement rate"""        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        
        if views == 0:
            return 0.0
        
        engagement = (likes + comments) / views * 100
        return round(engagement, 2)


class InstagramChannelManager(BasePlatformManager):
    """Instagram platform manager"""    
    def __init__(self, db: Session):
        super().__init__(db)
        self.api_base_url = "https://graph.facebook.com/v18.0"
        
    async def distribute_content(
        self,
        credentials: PlatformCredentials,
        content: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Post content to Instagram"""        try:
            await self.rate_limiter.acquire("instagram", credentials.user_id)
            
            session = await self.get_session("instagram")
            
            # Determine content type
            content_type = content.get("type", "image")
            
            if content_type == "video":
                return await self._upload_instagram_video(session, credentials, content, request)
            else:
                return await self._upload_instagram_image(session, credentials, content, request)
                
        except Exception as e:
            logger.error(f"Instagram distribution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform_content_id": None,
                "url": None
            }
    
    async def _upload_instagram_image(
        self,
        session: aiohttp.ClientSession,
        credentials: PlatformCredentials,
        content: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Upload image to Instagram"""        
        # Step 1: Create media container
        container_params = {
            "image_url": content.get("file_url"),
            "caption": self._format_instagram_caption(content),
            "access_token": credentials.access_token
        }
        
        async with session.post(
            f"{self.api_base_url}/{credentials.account_id}/media",
            data=container_params
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise DistributionError(f"Instagram container creation failed: {error_text}")
            
            container_result = await response.json()
            container_id = container_result.get("id")
        
        # Step 2: Publish media
        publish_params = {
            "creation_id": container_id,
            "access_token": credentials.access_token
        }
        
        async with session.post(
            f"{self.api_base_url}/{credentials.account_id}/media_publish",
            data=publish_params
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise DistributionError(f"Instagram publish failed: {error_text}")
            
            publish_result = await response.json()
            media_id = publish_result.get("id")
            
            return {
                "success": True,
                "platform_content_id": media_id,
                "url": f"https://www.instagram.com/p/{media_id}",
                "platform_response": publish_result,
                "metadata": {
                    "caption": content.get("description"),
                    "hashtags": content.get("hashtags"),
                    "published_at": datetime.now().isoformat()
                }
            }
    
    async def _upload_instagram_video(
        self,
        session: aiohttp.ClientSession,
        credentials: PlatformCredentials,
        content: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Upload video to Instagram (Reels)"""        
        container_params = {
            "video_url": content.get("file_url"),
            "caption": self._format_instagram_caption(content),
            "media_type": "REELS",
            "access_token": credentials.access_token
        }
        
        async with session.post(
            f"{self.api_base_url}/{credentials.account_id}/media",
            data=container_params
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise DistributionError(f"Instagram video container creation failed: {error_text}")
            
            container_result = await response.json()
            container_id = container_result.get("id")
        
        # Wait for video processing
        await asyncio.sleep(10)
        
        # Publish video
        publish_params = {
            "creation_id": container_id,
            "access_token": credentials.access_token
        }
        
        async with session.post(
            f"{self.api_base_url}/{credentials.account_id}/media_publish",
            data=publish_params
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise DistributionError(f"Instagram video publish failed: {error_text}")
            
            publish_result = await response.json()
            media_id = publish_result.get("id")
            
            return {
                "success": True,
                "platform_content_id": media_id,
                "url": f"https://www.instagram.com/reel/{media_id}",
                "platform_response": publish_result,
                "metadata": {
                    "caption": content.get("description"),
                    "hashtags": content.get("hashtags"),
                    "media_type": "REELS",
                    "published_at": datetime.now().isoformat()
                }
            }
    
    def _format_instagram_caption(self, content: Dict[str, Any]) -> str:
        """Format caption for Instagram"""        caption = content.get("description", "")
        hashtags = content.get("hashtags", [])
        
        # Instagram caption limit
        if len(caption) > 2000:
            caption = caption[:1900] + "..."
        
        # Add hashtags
        if hashtags:
            hashtag_text = " ".join([f"#{tag.lstrip('#')}" for tag in hashtags[:30]])  # Max 30 hashtags
            caption += f"\n\n{hashtag_text}"
        
        return caption
    
    async def get_content_metrics(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> Dict[str, Any]:
        """Get Instagram post metrics"""        try:
            session = await self.get_session("instagram")
            
            params = {
                "fields": "like_count,comments_count,media_type,media_url,permalink,timestamp",
                "access_token": credentials.access_token
            }
            
            async with session.get(f"{self.api_base_url}/{content_id}", params=params) as response:
                if response.status != 200:
                    raise PlatformError(f"Failed to get Instagram metrics: {response.status}")
                
                data = await response.json()
                
                likes = data.get("like_count", 0)
                comments = data.get("comments_count", 0)
                
                return {
                    "views": 0,  # Instagram doesn't provide view count for images
                    "likes": likes,
                    "comments": comments,
                    "shares": 0,  # Not available via API
                    "engagement_rate": 0,  # Would need follower count
                    "media_type": data.get("media_type"),
                    "published_at": data.get("timestamp"),
                    "url": data.get("permalink"),
                    "platform": "instagram"
                }
                
        except Exception as e:
            logger.error(f"Instagram metrics retrieval failed: {e}")
            return {"error": str(e)}
    
    async def delete_content(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> bool:
        """Delete Instagram post"""        try:
            session = await self.get_session("instagram")
            
            params = {"access_token": credentials.access_token}
            
            async with session.delete(f"{self.api_base_url}/{content_id}", params=params) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Instagram content deletion failed: {e}")
            return False


class TikTokChannelManager(BasePlatformManager):
    """TikTok platform manager"""    
    def __init__(self, db: Session):
        super().__init__(db)
        self.api_base_url = "https://open-api.tiktok.com"
        
    async def distribute_content(
        self,
        credentials: PlatformCredentials,
        content: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Upload video to TikTok"""        try:
            await self.rate_limiter.acquire("tiktok", credentials.user_id)
            
            session = await self.get_session("tiktok")
            
            # TikTok requires video upload
            if content.get("type") != "video":
                raise DistributionError("TikTok only supports video content")
            
            # Step 1: Initialize upload
            init_params = {
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": content.get("file_size", 0),
                    "chunk_size": 10000000,  # 10MB chunks
                    "total_chunk_count": 1
                }
            }
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with session.post(
                f"{self.api_base_url}/v2/post/publish/video/init/",
                json=init_params,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise DistributionError(f"TikTok upload init failed: {error_text}")
                
                init_result = await response.json()
                upload_url = init_result.get("data", {}).get("upload_url")
                publish_id = init_result.get("data", {}).get("publish_id")
            
            # Step 2: Upload video file
            video_url = content.get("file_url")
            async with session.get(video_url) as video_response:
                if video_response.status != 200:
                    raise DistributionError("Failed to download video for TikTok upload")
                
                video_data = await video_response.read()
            
            # Upload to TikTok
            async with session.put(upload_url, data=video_data) as upload_response:
                if upload_response.status not in [200, 201]:
                    raise DistributionError(f"TikTok video upload failed: {upload_response.status}")
            
            # Step 3: Publish video
            publish_params = {
                "post_info": {
                    "title": content.get("title", "")[:150],  # TikTok title limit
                    "privacy_level": "SELF_ONLY" if request.schedule_time else "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "publish_id": publish_id
                }
            }
            
            async with session.post(
                f"{self.api_base_url}/v2/post/publish/",
                json=publish_params,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise DistributionError(f"TikTok publish failed: {error_text}")
                
                publish_result = await response.json()
                share_id = publish_result.get("data", {}).get("share_id")
                
                return {
                    "success": True,
                    "platform_content_id": share_id,
                    "url": f"https://www.tiktok.com/@{credentials.account_id}/video/{share_id}",
                    "platform_response": publish_result,
                    "metadata": {
                        "title": content.get("title"),
                        "publish_id": publish_id,
                        "published_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"TikTok distribution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform_content_id": None,
                "url": None
            }
    
    async def get_content_metrics(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> Dict[str, Any]:
        """Get TikTok video metrics"""        try:
            session = await self.get_session("tiktok")
            
            params = {
                "fields": "like_count,comment_count,share_count,view_count"
            }
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.get(
                f"{self.api_base_url}/v2/video/query/",
                params={**params, "video_ids": content_id},
                headers=headers
            ) as response:
                if response.status != 200:
                    raise PlatformError(f"Failed to get TikTok metrics: {response.status}")
                
                data = await response.json()
                videos = data.get("data", {}).get("videos", [])
                
                if not videos:
                    return {"error": "Video not found"}
                
                video = videos[0]
                
                views = video.get("view_count", 0)
                likes = video.get("like_count", 0)
                comments = video.get("comment_count", 0)
                shares = video.get("share_count", 0)
                
                engagement_rate = ((likes + comments + shares) / views * 100) if views > 0 else 0
                
                return {
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "engagement_rate": round(engagement_rate, 2),
                    "published_at": video.get("create_time"),
                    "platform": "tiktok"
                }
                
        except Exception as e:
            logger.error(f"TikTok metrics retrieval failed: {e}")
            return {"error": str(e)}
    
    async def delete_content(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> bool:
        """Delete TikTok video"""        try:
            session = await self.get_session("tiktok")
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.post(
                f"{self.api_base_url}/v2/post/publish/video/delete/",
                json={"video_id": content_id},
                headers=headers
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"TikTok content deletion failed: {e}")
            return False


class TwitterChannelManager(BasePlatformManager):
    """Twitter/X platform manager"""    
    def __init__(self, db: Session):
        super().__init__(db)
        self.api_base_url = "https://api.twitter.com/2"
        
    async def distribute_content(
        self,
        credentials: PlatformCredentials,
        content: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Post content to Twitter"""        try:
            await self.rate_limiter.acquire("twitter", credentials.user_id)
            
            session = await self.get_session("twitter")
            
            # Format tweet text
            tweet_text = self._format_twitter_text(content)
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            # Handle media upload if present
            media_ids = []
            if content.get("file_url"):
                media_id = await self._upload_twitter_media(session, credentials, content)
                if media_id:
                    media_ids.append(media_id)
            
            # Create tweet
            tweet_data = {
                "text": tweet_text
            }
            
            if media_ids:
                tweet_data["media"] = {"media_ids": media_ids}
            
            async with session.post(
                f"{self.api_base_url}/tweets",
                json=tweet_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise DistributionError(f"Twitter post failed: {error_text}")
                
                result = await response.json()
                tweet_id = result.get("data", {}).get("id")
                
                return {
                    "success": True,
                    "platform_content_id": tweet_id,
                    "url": f"https://twitter.com/{credentials.username}/status/{tweet_id}",
                    "platform_response": result,
                    "metadata": {
                        "text": tweet_text,
                        "media_count": len(media_ids),
                        "published_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Twitter distribution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform_content_id": None,
                "url": None
            }
    
    async def _upload_twitter_media(
        self,
        session: aiohttp.ClientSession,
        credentials: PlatformCredentials,
        content: Dict[str, Any]
    ) -> Optional[str]:
        """Upload media to Twitter"""        try:
            file_url = content.get("file_url")
            
            # Download media
            async with session.get(file_url) as response:
                if response.status != 200:
                    return None
                
                media_data = await response.read()
                content_type = response.headers.get("content-type", "")
            
            # Upload to Twitter media endpoint
            upload_url = "https://upload.twitter.com/1.1/media/upload.json"
            
            form_data = aiohttp.FormData()
            form_data.add_field("media", media_data, content_type=content_type)
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.post(upload_url, data=form_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("media_id_string")
                
                return None
                
        except Exception as e:
            logger.error(f"Twitter media upload failed: {e}")
            return None
    
    def _format_twitter_text(self, content: Dict[str, Any]) -> str:
        """Format text for Twitter with character limits"""        text = content.get("description", "") or content.get("title", "")
        hashtags = content.get("hashtags", [])
        
        # Twitter character limit
        max_length = 280
        
        # Reserve space for hashtags
        hashtag_text = " ".join([f"#{tag.lstrip('#')}" for tag in hashtags[:5]])  # Max 5 hashtags
        hashtag_length = len(hashtag_text) + 2 if hashtag_text else 0  # +2 for \n\n
        
        # Truncate main text if needed
        available_length = max_length - hashtag_length
        if len(text) > available_length:
            text = text[:available_length-3] + "..."
        
        # Combine text and hashtags
        if hashtag_text:
            return f"{text}\n\n{hashtag_text}"
        else:
            return text
    
    async def get_content_metrics(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> Dict[str, Any]:
        """Get Twitter tweet metrics"""        try:
            session = await self.get_session("twitter")
            
            params = {
                "tweet.fields": "public_metrics,created_at,author_id",
                "expansions": "author_id"
            }
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.get(f"{self.api_base_url}/tweets/{content_id}", params=params, headers=headers) as response:
                if response.status != 200:
                    raise PlatformError(f"Failed to get Twitter metrics: {response.status}")
                
                data = await response.json()
                tweet = data.get("data", {})
                metrics = tweet.get("public_metrics", {})
                
                return {
                    "views": metrics.get("impression_count", 0),
                    "likes": metrics.get("like_count", 0),
                    "comments": metrics.get("reply_count", 0),
                    "shares": metrics.get("retweet_count", 0),
                    "engagement_rate": self._calculate_twitter_engagement(metrics),
                    "published_at": tweet.get("created_at"),
                    "platform": "twitter"
                }
                
        except Exception as e:
            logger.error(f"Twitter metrics retrieval failed: {e}")
            return {"error": str(e)}
    
    def _calculate_twitter_engagement(self, metrics: Dict[str, Any]) -> float:
        """Calculate Twitter engagement rate"""        impressions = metrics.get("impression_count", 0)
        likes = metrics.get("like_count", 0)
        replies = metrics.get("reply_count", 0)
        retweets = metrics.get("retweet_count", 0)
        
        if impressions == 0:
            return 0.0
        
        engagement = (likes + replies + retweets) / impressions * 100
        return round(engagement, 2)
    
    async def delete_content(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> bool:
        """Delete Twitter tweet"""        try:
            session = await self.get_session("twitter")
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.delete(f"{self.api_base_url}/tweets/{content_id}", headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Twitter content deletion failed: {e}")
            return False


class SpotifyChannelManager(BasePlatformManager):
    """Spotify platform manager for podcast content"""    
    def __init__(self, db: Session):
        super().__init__(db)
        self.api_base_url = "https://api.spotify.com/v1"
        
    async def distribute_content(
        self,
        credentials: PlatformCredentials,
        content: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Upload podcast episode to Spotify"""        try:
            await self.rate_limiter.acquire("spotify", credentials.user_id)
            
            session = await self.get_session("spotify")
            
            # Spotify requires audio content
            if content.get("type") != "audio":
                raise DistributionError("Spotify only supports audio content")
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            # Create episode
            episode_data = {
                "name": content.get("title", "")[:100],
                "description": content.get("description", "")[:1000],
                "audio_preview_url": content.get("file_url"),
                "language": content.get("language", "en"),
                "explicit": content.get("explicit", False),
                "type": "episode"
            }
            
            async with session.post(
                f"{self.api_base_url}/shows/{credentials.show_id}/episodes",
                json=episode_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise DistributionError(f"Spotify episode creation failed: {error_text}")
                
                result = await response.json()
                episode_id = result.get("id")
                
                return {
                    "success": True,
                    "platform_content_id": episode_id,
                    "url": result.get("external_urls", {}).get("spotify"),
                    "platform_response": result,
                    "metadata": {
                        "name": result.get("name"),
                        "description": result.get("description"),
                        "duration_ms": result.get("duration_ms"),
                        "published_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Spotify distribution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform_content_id": None,
                "url": None
            }
    
    async def get_content_metrics(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> Dict[str, Any]:
        """Get Spotify episode metrics"""        try:
            session = await self.get_session("spotify")
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.get(f"{self.api_base_url}/episodes/{content_id}", headers=headers) as response:
                if response.status != 200:
                    raise PlatformError(f"Failed to get Spotify metrics: {response.status}")
                
                data = await response.json()
                
                return {
                    "views": 0,  # Spotify doesn't provide play counts via API
                    "likes": 0,  # Not available
                    "comments": 0,  # Not available
                    "shares": 0,  # Not available
                    "engagement_rate": 0,
                    "duration_ms": data.get("duration_ms"),
                    "published_at": data.get("release_date"),
                    "name": data.get("name"),
                    "platform": "spotify"
                }
                
        except Exception as e:
            logger.error(f"Spotify metrics retrieval failed: {e}")
            return {"error": str(e)}
    
    async def delete_content(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> bool:
        """Delete Spotify episode"""        try:
            session = await self.get_session("spotify")
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.delete(f"{self.api_base_url}/episodes/{content_id}", headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Spotify content deletion failed: {e}")
            return False


class LinkedInChannelManager(BasePlatformManager):
    """LinkedIn platform manager"""    
    def __init__(self, db: Session):
        super().__init__(db)
        self.api_base_url = "https://api.linkedin.com/v2"
        
    async def distribute_content(
        self,
        credentials: PlatformCredentials,
        content: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Post content to LinkedIn"""        try:
            await self.rate_limiter.acquire("linkedin", credentials.user_id)
            
            session = await self.get_session("linkedin")
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Handle media upload if present
            media_urn = None
            if content.get("file_url"):
                media_urn = await self._upload_linkedin_media(session, credentials, content)
            
            # Create post
            post_data = {
                "author": f"urn:li:person:{credentials.person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": self._format_linkedin_text(content)
                        },
                        "shareMediaCategory": "ARTICLE" if not media_urn else "IMAGE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            if media_urn:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "description": {
                            "text": content.get("description", "")
                        },
                        "media": media_urn,
                        "title": {
                            "text": content.get("title", "")
                        }
                    }
                ]
            
            async with session.post(
                f"{self.api_base_url}/ugcPosts",
                json=post_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise DistributionError(f"LinkedIn post failed: {error_text}")
                
                result = await response.json()
                post_id = result.get("id")
                
                return {
                    "success": True,
                    "platform_content_id": post_id,
                    "url": f"https://www.linkedin.com/feed/update/{post_id}",
                    "platform_response": result,
                    "metadata": {
                        "text": post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"],
                        "media_included": media_urn is not None,
                        "published_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"LinkedIn distribution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform_content_id": None,
                "url": None
            }
    
    async def _upload_linkedin_media(
        self,
        session: aiohttp.ClientSession,
        credentials: PlatformCredentials,
        content: Dict[str, Any]
    ) -> Optional[str]:
        """Upload media to LinkedIn"""        try:
            # Register upload
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{credentials.person_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with session.post(
                f"{self.api_base_url}/assets?action=registerUpload",
                json=register_data,
                headers=headers
            ) as response:
                if response.status != 200:
                    return None
                
                register_result = await response.json()
                upload_url = register_result.get("value", {}).get("uploadMechanism", {}).get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
                asset_id = register_result.get("value", {}).get("asset")
            
            if not upload_url:
                return None
            
            # Upload file
            file_url = content.get("file_url")
            async with session.get(file_url) as file_response:
                if file_response.status != 200:
                    return None
                
                file_data = await file_response.read()
            
            async with session.put(upload_url, data=file_data) as upload_response:
                if upload_response.status == 201:
                    return asset_id
                
                return None
                
        except Exception as e:
            logger.error(f"LinkedIn media upload failed: {e}")
            return None
    
    def _format_linkedin_text(self, content: Dict[str, Any]) -> str:
        """Format text for LinkedIn"""        text = content.get("description", "") or content.get("title", "")
        hashtags = content.get("hashtags", [])
        
        # LinkedIn character limit
        max_length = 3000
        
        # Add hashtags
        if hashtags:
            hashtag_text = " ".join([f"#{tag.lstrip('#')}" for tag in hashtags[:10]])  # Max 10 hashtags
            text += f"\n\n{hashtag_text}"
        
        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text
    
    async def get_content_metrics(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> Dict[str, Any]:
        """Get LinkedIn post metrics"""        try:
            session = await self.get_session("linkedin")
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            # LinkedIn metrics are limited via API
            async with session.get(f"{self.api_base_url}/ugcPosts/{content_id}", headers=headers) as response:
                if response.status != 200:
                    raise PlatformError(f"Failed to get LinkedIn metrics: {response.status}")
                
                data = await response.json()
                
                return {
                    "views": 0,  # Not available via API
                    "likes": 0,  # Requires separate API call
                    "comments": 0,  # Requires separate API call
                    "shares": 0,  # Requires separate API call
                    "engagement_rate": 0,
                    "published_at": data.get("created", {}).get("time"),
                    "platform": "linkedin"
                }
                
        except Exception as e:
            logger.error(f"LinkedIn metrics retrieval failed: {e}")
            return {"error": str(e)}
    
    async def delete_content(
        self,
        credentials: PlatformCredentials,
        content_id: str
    ) -> bool:
        """Delete LinkedIn post"""        try:
            session = await self.get_session("linkedin")
            
            headers = {"Authorization": f"Bearer {credentials.access_token}"}
            
            async with session.delete(f"{self.api_base_url}/ugcPosts/{content_id}", headers=headers) as response:
                return response.status == 204
                
        except Exception as e:
            logger.error(f"LinkedIn content deletion failed: {e}")
            return False
