"""
Platform Manager - Multi-Platform Social Media Integration Hub
Advanced platform management with unified API and intelligent routing

Created by: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Ultra-Industrial Content Protection & Monetization Platform

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code and concept are the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission 
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Development Team Specialties:
- Lead AI Developer & ML Engineer
- Backend Senior Architect
- Database Administrator (DBA) 
- Security & Microservices Expert
- Audio Processing Specialist
- DevOps & Infrastructure Engineer
- AI Prompt Engineering Expert
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from abc import ABC, abstractmethod
import aiohttp
import hashlib
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported social media platform types"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    DISCORD = "discord"

class ContentType(Enum):
    """Content types for different platforms"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    LIVE = "live"

class PostStatus(Enum):
    """Post publication status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"
    BLOCKED = "blocked"

@dataclass
class PlatformConfig:
    """Platform configuration and credentials"""
    platform_type: PlatformType
    api_key: str
    api_secret: str
    access_token: str
    refresh_token: Optional[str] = None
    webhook_url: Optional[str] = None
    rate_limits: Dict[str, int] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    encrypted: bool = False
    
@dataclass
class ContentPost:
    """Unified content post structure"""
    id: str
    platform: PlatformType
    content_type: ContentType
    title: str
    description: str
    media_urls: List[str]
    hashtags: List[str]
    mentions: List[str]
    location: Optional[str] = None
    schedule_time: Optional[datetime] = None
    status: PostStatus = PostStatus.DRAFT
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class PlatformAdapter(ABC):
    """Abstract base class for platform-specific adapters"""
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.platform_type = config.platform_type
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimiter(config.rate_limits)
        
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
        
    @abstractmethod
    async def publish_content(self, post: ContentPost) -> Dict[str, Any]:
        """Publish content to the platform"""
        pass
        
    @abstractmethod
    async def get_analytics(self, post_id: str, metrics: List[str]) -> Dict[str, Any]:
        """Get post analytics"""
        pass
        
    @abstractmethod
    async def delete_content(self, post_id: str) -> bool:
        """Delete content from platform"""
        pass

class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, limits: Dict[str, int]):
        self.limits = limits  # {'requests_per_minute': 60, 'requests_per_hour': 1000}
        self.call_history: Dict[str, List[datetime]] = {}
        
    async def wait_if_needed(self, endpoint: str = "default"):
        """Wait if rate limit would be exceeded"""
        now = datetime.utcnow()
        
        if endpoint not in self.call_history:
            self.call_history[endpoint] = []
        
        history = self.call_history[endpoint]
        
        # Clean old entries
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        history[:] = [call_time for call_time in history if call_time > hour_ago]
        
        # Check limits
        recent_minute = [call_time for call_time in history if call_time > minute_ago]
        
        requests_per_minute = self.limits.get('requests_per_minute', float('inf'))
        requests_per_hour = self.limits.get('requests_per_hour', float('inf'))
        
        if len(recent_minute) >= requests_per_minute:
            wait_time = 60 - (now - min(recent_minute)).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                
        if len(history) >= requests_per_hour:
            wait_time = 3600 - (now - min(history)).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Record this call
        history.append(now)

class CredentialManager:
    """Secure credential management with encryption"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
    def encrypt_credentials(self, config: PlatformConfig) -> PlatformConfig:
        """Encrypt sensitive credentials"""
        if not config.encrypted:
            config.api_key = self.cipher.encrypt(config.api_key.encode()).decode()
            config.api_secret = self.cipher.encrypt(config.api_secret.encode()).decode()
            config.access_token = self.cipher.encrypt(config.access_token.encode()).decode()
            if config.refresh_token:
                config.refresh_token = self.cipher.encrypt(config.refresh_token.encode()).decode()
            config.encrypted = True
        return config
        
    def decrypt_credentials(self, config: PlatformConfig) -> PlatformConfig:
        """Decrypt sensitive credentials"""
        if config.encrypted:
            config.api_key = self.cipher.decrypt(config.api_key.encode()).decode()
            config.api_secret = self.cipher.decrypt(config.api_secret.encode()).decode()
            config.access_token = self.cipher.decrypt(config.access_token.encode()).decode()
            if config.refresh_token:
                config.refresh_token = self.cipher.decrypt(config.refresh_token.encode()).decode()
            config.encrypted = False
        return config

class PlatformManager:
    """
    Advanced Multi-Platform Social Media Manager
    Handles unified content distribution, analytics, and platform-specific optimizations
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.adapters: Dict[PlatformType, PlatformAdapter] = {}
        self.credential_manager = CredentialManager(encryption_key)
        self.publish_queue: List[ContentPost] = []
        self.analytics_cache: Dict[str, Dict[str, Any]] = {}
        self.webhook_handlers: Dict[PlatformType, Callable] = {}
        self.cross_platform_rules: List[Dict[str, Any]] = []
        
    async def register_platform(self, config: PlatformConfig, adapter_class: type):
        """Register a new platform with its adapter"""
        try:
            # Encrypt credentials
            encrypted_config = self.credential_manager.encrypt_credentials(config)
            
            # Create adapter instance
            adapter = adapter_class(encrypted_config)
            
            # Test authentication
            decrypted_config = self.credential_manager.decrypt_credentials(encrypted_config)
            adapter.config = decrypted_config
            
            auth_success = await adapter.authenticate()
            if not auth_success:
                raise ValueError(f"Authentication failed for {config.platform_type.value}")
            
            # Re-encrypt and store
            adapter.config = self.credential_manager.encrypt_credentials(decrypted_config)
            self.adapters[config.platform_type] = adapter
            
            logger.info(f"Platform {config.platform_type.value} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register platform {config.platform_type.value}: {str(e)}")
            raise
    
    async def publish_content(self, post: ContentPost, platforms: Optional[List[PlatformType]] = None) -> Dict[PlatformType, Dict[str, Any]]:
        """Publish content to specified platforms or all registered platforms"""
        if platforms is None:
            platforms = list(self.adapters.keys())
        
        results = {}
        tasks = []
        
        for platform in platforms:
            if platform in self.adapters:
                # Create platform-specific version of content
                platform_post = await self._adapt_content_for_platform(post, platform)
                task = self._publish_to_platform(platform_post, platform)
                tasks.append((platform, task))
        
        # Execute all publications concurrently
        for platform, task in tasks:
            try:
                result = await task
                results[platform] = {
                    'success': True,
                    'data': result,
                    'timestamp': datetime.utcnow().isoformat()
                }
            except Exception as e:
                results[platform] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                logger.error(f"Failed to publish to {platform.value}: {str(e)}")
        
        return results
    
    async def _publish_to_platform(self, post: ContentPost, platform: PlatformType) -> Dict[str, Any]:
        """Publish content to a specific platform"""
        adapter = self.adapters[platform]
        
        # Decrypt credentials temporarily
        original_config = adapter.config
        adapter.config = self.credential_manager.decrypt_credentials(adapter.config)
        
        try:
            # Wait for rate limiting
            await adapter.rate_limiter.wait_if_needed("publish")
            
            # Publish content
            result = await adapter.publish_content(post)
            
            # Update post status
            post.status = PostStatus.PUBLISHED if result.get('success') else PostStatus.FAILED
            post.updated_at = datetime.utcnow()
            
            return result
            
        finally:
            # Re-encrypt credentials
            adapter.config = self.credential_manager.encrypt_credentials(adapter.config)
    
    async def _adapt_content_for_platform(self, post: ContentPost, platform: PlatformType) -> ContentPost:
        """Adapt content for specific platform requirements"""
        adapted_post = ContentPost(
            id=f"{post.id}_{platform.value}",
            platform=platform,
            content_type=post.content_type,
            title=post.title,
            description=post.description,
            media_urls=post.media_urls.copy(),
            hashtags=post.hashtags.copy(),
            mentions=post.mentions.copy(),
            location=post.location,
            schedule_time=post.schedule_time,
            status=post.status,
            metadata=post.metadata.copy(),
            created_at=post.created_at,
            updated_at=datetime.utcnow()
        )
        
        # Platform-specific adaptations
        if platform == PlatformType.TWITTER:
            adapted_post.description = self._truncate_for_twitter(adapted_post.description)
            adapted_post.hashtags = adapted_post.hashtags[:10]  # Twitter limit
            
        elif platform == PlatformType.INSTAGRAM:
            adapted_post.hashtags = adapted_post.hashtags[:30]  # Instagram limit
            
        elif platform == PlatformType.LINKEDIN:
            adapted_post.description = self._format_for_linkedin(adapted_post.description)
            
        # Apply cross-platform rules
        for rule in self.cross_platform_rules:
            if rule.get('platform') == platform or rule.get('platform') == 'all':
                adapted_post = await self._apply_cross_platform_rule(adapted_post, rule)
        
        return adapted_post
    
    def _truncate_for_twitter(self, text: str, max_length: int = 280) -> str:
        """Truncate text for Twitter character limit"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _format_for_linkedin(self, text: str) -> str:
        """Format text for LinkedIn professional style"""
        # Add professional formatting, line breaks for readability
        formatted = text.replace('. ', '.\n\n')
        return formatted
    
    async def _apply_cross_platform_rule(self, post: ContentPost, rule: Dict[str, Any]) -> ContentPost:
        """Apply cross-platform content rules"""
        if rule.get('type') == 'hashtag_mapping':
            platform_hashtags = rule.get('hashtag_map', {}).get(post.platform.value, {})
            for original, replacement in platform_hashtags.items():
                post.hashtags = [hashtag.replace(original, replacement) for hashtag in post.hashtags]
        
        elif rule.get('type') == 'content_filter':
            filters = rule.get('filters', [])
            for filter_rule in filters:
                if filter_rule.get('platform') == post.platform.value:
                    # Apply content filtering
                    post.description = self._apply_content_filter(post.description, filter_rule)
        
        return post
    
    def _apply_content_filter(self, text: str, filter_rule: Dict[str, Any]) -> str:
        """Apply content filtering rules"""
        if 'remove_words' in filter_rule:
            for word in filter_rule['remove_words']:
                text = text.replace(word, '')
        
        if 'replace_words' in filter_rule:
            for original, replacement in filter_rule['replace_words'].items():
                text = text.replace(original, replacement)
        
        return text.strip()
    
    async def get_unified_analytics(self, post_id: str, platforms: Optional[List[PlatformType]] = None) -> Dict[str, Any]:
        """Get unified analytics across platforms"""
        if platforms is None:
            platforms = list(self.adapters.keys())
        
        unified_metrics = {
            'total_views': 0,
            'total_likes': 0,
            'total_shares': 0,
            'total_comments': 0,
            'engagement_rate': 0.0,
            'platform_breakdown': {},
            'updated_at': datetime.utcnow().isoformat()
        }
        
        for platform in platforms:
            if platform in self.adapters:
                try:
                    adapter = self.adapters[platform]
                    
                    # Decrypt credentials temporarily
                    original_config = adapter.config
                    adapter.config = self.credential_manager.decrypt_credentials(adapter.config)
                    
                    try:
                        platform_post_id = f"{post_id}_{platform.value}"
                        metrics = await adapter.get_analytics(platform_post_id, 
                                                             ['views', 'likes', 'shares', 'comments'])
                        
                        unified_metrics['platform_breakdown'][platform.value] = metrics
                        
                        # Aggregate metrics
                        unified_metrics['total_views'] += metrics.get('views', 0)
                        unified_metrics['total_likes'] += metrics.get('likes', 0)
                        unified_metrics['total_shares'] += metrics.get('shares', 0)
                        unified_metrics['total_comments'] += metrics.get('comments', 0)
                        
                    finally:
                        # Re-encrypt credentials
                        adapter.config = self.credential_manager.encrypt_credentials(adapter.config)
                        
                except Exception as e:
                    logger.error(f"Failed to get analytics for {platform.value}: {str(e)}")
                    unified_metrics['platform_breakdown'][platform.value] = {'error': str(e)}
        
        # Calculate overall engagement rate
        total_engagement = (unified_metrics['total_likes'] + 
                          unified_metrics['total_shares'] + 
                          unified_metrics['total_comments'])
        
        if unified_metrics['total_views'] > 0:
            unified_metrics['engagement_rate'] = total_engagement / unified_metrics['total_views']
        
        return unified_metrics
    
    async def schedule_content(self, post: ContentPost, platforms: List[PlatformType], 
                             schedule_time: datetime) -> str:
        """Schedule content for future publication"""
        post.schedule_time = schedule_time
        post.status = PostStatus.SCHEDULED
        
        # Add to publish queue
        scheduled_post = {
            'id': post.id,
            'post': post,
            'platforms': platforms,
            'schedule_time': schedule_time,
            'created_at': datetime.utcnow()
        }
        
        self.publish_queue.append(post)
        
        logger.info(f"Content {post.id} scheduled for {schedule_time.isoformat()}")
        return post.id
    
    async def process_scheduled_posts(self):
        """Process posts that are ready to be published"""
        now = datetime.utcnow()
        ready_posts = []
        
        for i, post in enumerate(self.publish_queue):
            if post.status == PostStatus.SCHEDULED and post.schedule_time <= now:
                ready_posts.append((i, post))
        
        # Publish ready posts
        for index, post in reversed(ready_posts):  # Reverse to maintain indices
            try:
                platforms = [post.platform] if post.platform else list(self.adapters.keys())
                await self.publish_content(post, platforms)
                self.publish_queue.pop(index)
                logger.info(f"Published scheduled post {post.id}")
                
            except Exception as e:
                logger.error(f"Failed to publish scheduled post {post.id}: {str(e)}")
                post.status = PostStatus.FAILED
    
    def add_cross_platform_rule(self, rule: Dict[str, Any]):
        """Add a cross-platform content adaptation rule"""
        self.cross_platform_rules.append(rule)
        logger.info(f"Added cross-platform rule: {rule.get('type', 'unknown')}")
    
    def register_webhook_handler(self, platform: PlatformType, handler: Callable):
        """Register webhook handler for platform events"""
        self.webhook_handlers[platform] = handler
        logger.info(f"Registered webhook handler for {platform.value}")
    
    async def handle_webhook(self, platform: PlatformType, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhook from platform"""
        if platform in self.webhook_handlers:
            try:
                return await self.webhook_handlers[platform](data)
            except Exception as e:
                logger.error(f"Webhook handler failed for {platform.value}: {str(e)}")
                return {'success': False, 'error': str(e)}
        else:
            logger.warning(f"No webhook handler registered for {platform.value}")
            return {'success': False, 'error': 'No handler registered'}
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all registered platforms"""
        return {
            'total_platforms': len(self.adapters),
            'platforms': {
                platform.value: {
                    'registered': True,
                    'features': adapter.config.features,
                    'rate_limits': adapter.config.rate_limits
                }
                for platform, adapter in self.adapters.items()
            },
            'scheduled_posts': len([p for p in self.publish_queue if p.status == PostStatus.SCHEDULED]),
            'cross_platform_rules': len(self.cross_platform_rules)
        }
