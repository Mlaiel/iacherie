"""Discord Platform Integration

Discord API integration for community engagement and content sharing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class DiscordPlatform(PlatformBase):
    """Discord platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize Discord platform"""        super().__init__(config)
        self.api_base = "https://discord.com/api/v10"
        self.session: Optional[aiohttp.ClientSession] = None
        self.bot_token = self.config.credentials.get('bot_token')
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Discord Bot Token"""        try:
            if not self.bot_token:
                logger.error("Discord requires bot_token")
                return False
            
            # Test bot token by getting bot user info
            session = await self._get_session()
            headers = {
                'Authorization': f'Bot {self.bot_token}',
                'Content-Type': 'application/json'
            }
            
            async with session.get(f"{self.api_base}/users/@me", headers=headers) as response:
                if response.status == 200:
                    bot_info = await response.json()
                    self.config.credentials['bot_id'] = bot_info.get('id')
                    self.config.credentials['bot_username'] = bot_info.get('username')
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info(f"Discord authentication successful for bot: {bot_info.get('username')}")
                    return True
                else:
                    logger.error("Discord bot token validation failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Discord authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Discord token (not applicable for bot tokens)"""        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Discord API"""        try:
            session = await self._get_session()
            
            # Add authentication headers
            headers = kwargs.get('headers', {})
            if self.bot_token:
                headers['Authorization'] = f'Bot {self.bot_token}'
            
            headers['Content-Type'] = 'application/json'
            headers['User-Agent'] = 'IA-Influencer-Agent (https://github.com/mlaiel/ia-influencer, 1.0)'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    # Discord rate limiting
                    retry_after = float(response.headers.get('retry-after', 1))
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    logger.error("Discord authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201, 204]:
                    if response.status == 204:
                        return {'success': True}
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Discord API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Discord request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Send message to Discord channel"""        try:
            channel_id = metadata.tags[0] if metadata.tags else None
            if not channel_id:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Discord requires channel_id in metadata.tags"
                )
            
            # Prepare message data
            message_data = {
                'content': f"**{metadata.title}**\n{metadata.description or ''}" if metadata.title else metadata.description or ""
            }
            
            # Handle file attachments
            if content_path and not content_path.startswith('http'):
                # For local files, need to upload as attachment
                # This is simplified - full implementation would handle file upload
                message_data['content'] += f"\n[File: {content_path}]"
            elif content_path and content_path.startswith('http'):
                # Add URL to message
                message_data['content'] += f"\n{content_path}"
            
            # Handle embeds for rich content
            if metadata.title and metadata.description:
                message_data['embeds'] = [{
                    'title': metadata.title,
                    'description': metadata.description,
                    'url': content_path if content_path and content_path.startswith('http') else None,
                    'color': 0x7289DA  # Discord blurple
                }]
                # Remove title/description from content to avoid duplication
                message_data['content'] = content_path if content_path and content_path.startswith('http') else ""
            
            result = await self._make_request('POST', f'/channels/{channel_id}/messages', json=message_data)
            
            if result and result.get('id'):
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=result['id'],
                    url=f"https://discord.com/channels/{result.get('guild_id', '@me')}/{channel_id}/{result['id']}",
                    metadata={
                        'channel_id': channel_id,
                        'guild_id': result.get('guild_id'),
                        'author': result.get('author', {}),
                        'timestamp': result.get('timestamp'),
                        'message_type': result.get('type', 0)
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Discord message sending failed"
                )
                
        except Exception as e:
            logger.error(f"Discord upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Discord message analytics"""        try:
            # Discord doesn't provide built-in analytics
            # We can get message reactions and basic info
            
            # First, find the message - need channel_id
            # This is a limitation - we need to know which channel the message is in
            # For this implementation, we'll try to get message info directly
            
            # Note: This requires knowing the channel_id where the message was posted
            # In a real implementation, you'd store this mapping
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=0,  # Discord doesn't track views
                likes=0,  # We'll count reactions as likes
                shares=0,  # Discord doesn't track shares
                comments=0,  # We'll count replies in threads
                metadata={
                    'note': 'Discord analytics are limited. Reactions and thread replies would need specific channel access.',
                    'analytics_type': 'basic'
                }
            )
                
        except Exception as e:
            logger.error(f"Discord analytics error: {e}")
            raise
    
    async def get_message_analytics(self, channel_id: str, message_id: str) -> Dict[str, Any]:
        """Get specific message analytics"""        try:
            # Get message details
            message = await self._make_request('GET', f'/channels/{channel_id}/messages/{message_id}')
            
            if message:
                # Count reactions
                total_reactions = 0
                reaction_details = {}
                
                for reaction in message.get('reactions', []):
                    count = reaction.get('count', 0)
                    emoji = reaction.get('emoji', {})
                    emoji_name = emoji.get('name', 'unknown')
                    
                    total_reactions += count
                    reaction_details[emoji_name] = count
                
                return {
                    'message_id': message_id,
                    'channel_id': channel_id,
                    'content': message.get('content', ''),
                    'timestamp': message.get('timestamp'),
                    'reactions': reaction_details,
                    'total_reactions': total_reactions,
                    'pinned': message.get('pinned', False),
                    'edited_timestamp': message.get('edited_timestamp'),
                    'attachments_count': len(message.get('attachments', [])),
                    'embeds_count': len(message.get('embeds', []))
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting message analytics: {e}")
            return {}
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search messages in Discord (requires guild access)"""        try:
            # Discord search requires specific guild/channel access
            # This is a placeholder implementation
            logger.warning("Discord search requires specific guild/channel access")
            return []
            
        except Exception as e:
            logger.error(f"Discord search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's messages from Discord (limited by API)"""        try:
            # Discord doesn't provide an endpoint to get all user messages
            # You need to search within specific channels/guilds
            logger.warning("Discord user content requires channel-specific searches")
            return []
            
        except Exception as e:
            logger.error(f"Error getting Discord user content: {e}")
            return []
    
    async def delete_content(self, content_id: str, channel_id: str = None) -> bool:
        """Delete Discord message"""        try:
            if not channel_id:
                logger.error("Discord message deletion requires channel_id")
                return False
            
            result = await self._make_request('DELETE', f'/channels/{channel_id}/messages/{content_id}')
            
            if result and result.get('success'):
                logger.info(f"Successfully deleted Discord message {content_id}")
                return True
            else:
                logger.error("Failed to delete Discord message")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting Discord content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata, channel_id: str = None) -> bool:
        """Update Discord message"""        try:
            if not channel_id:
                logger.error("Discord message update requires channel_id")
                return False
            
            update_data = {}
            
            if metadata.title or metadata.description:
                content = f"**{metadata.title}**\n{metadata.description or ''}" if metadata.title else metadata.description or ""
                update_data['content'] = content
            
            if metadata.title and metadata.description:
                update_data['embeds'] = [{
                    'title': metadata.title,
                    'description': metadata.description,
                    'color': 0x7289DA
                }]
            
            if update_data:
                result = await self._make_request('PATCH', f'/channels/{channel_id}/messages/{content_id}', 
                                                json=update_data)
                
                if result and result.get('id'):
                    logger.info(f"Successfully updated Discord message {content_id}")
                    return True
                else:
                    logger.error("Failed to update Discord message")
                    return False
            
            return True  # No updates needed
                
        except Exception as e:
            logger.error(f"Error updating Discord content: {e}")
            return False
    
    async def get_guild_info(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get Discord guild (server) information"""        try:
            result = await self._make_request('GET', f'/guilds/{guild_id}')
            
            if result:
                return {
                    'id': result.get('id'),
                    'name': result.get('name'),
                    'description': result.get('description'),
                    'icon': result.get('icon'),
                    'banner': result.get('banner'),
                    'member_count': result.get('approximate_member_count'),
                    'presence_count': result.get('approximate_presence_count'),
                    'owner_id': result.get('owner_id'),
                    'verification_level': result.get('verification_level'),
                    'nsfw_level': result.get('nsfw_level'),
                    'premium_tier': result.get('premium_tier'),
                    'preferred_locale': result.get('preferred_locale')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting guild info: {e}")
            return None
    
    async def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get Discord channel information"""        try:
            result = await self._make_request('GET', f'/channels/{channel_id}')
            
            if result:
                return {
                    'id': result.get('id'),
                    'name': result.get('name'),
                    'type': result.get('type'),
                    'topic': result.get('topic'),
                    'nsfw': result.get('nsfw'),
                    'rate_limit_per_user': result.get('rate_limit_per_user'),
                    'guild_id': result.get('guild_id'),
                    'position': result.get('position'),
                    'permission_overwrites': result.get('permission_overwrites', [])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return None
    
    async def get_guild_channels(self, guild_id: str) -> List[Dict[str, Any]]:
        """Get channels in a Discord guild"""        try:
            result = await self._make_request('GET', f'/guilds/{guild_id}/channels')
            
            if result:
                channels = []
                for channel in result:
                    channels.append({
                        'id': channel.get('id'),
                        'name': channel.get('name'),
                        'type': channel.get('type'),
                        'position': channel.get('position'),
                        'topic': channel.get('topic'),
                        'nsfw': channel.get('nsfw'),
                        'parent_id': channel.get('parent_id')
                    })
                return channels
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting guild channels: {e}")
            return []
    
    async def create_channel(self, guild_id: str, name: str, channel_type: int = 0, 
                           topic: str = None) -> Optional[str]:
        """Create a new Discord channel"""        try:
            channel_data = {
                'name': name,
                'type': channel_type
            }
            
            if topic:
                channel_data['topic'] = topic
            
            result = await self._make_request('POST', f'/guilds/{guild_id}/channels', json=channel_data)
            
            if result and result.get('id'):
                logger.info(f"Successfully created Discord channel: {name}")
                return result['id']
            else:
                logger.error(f"Failed to create Discord channel: {name}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Discord channel: {e}")
            return None
    
    async def add_reaction(self, channel_id: str, message_id: str, emoji: str) -> bool:
        """Add reaction to Discord message"""        try:
            # Encode emoji for URL
            import urllib.parse
            encoded_emoji = urllib.parse.quote(emoji)
            
            result = await self._make_request('PUT', 
                f'/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me')
            
            if result and result.get('success'):
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error adding reaction: {e}")
            return False
    
    async def send_dm(self, user_id: str, message: str) -> Optional[str]:
        """Send direct message to Discord user"""        try:
            # Create DM channel first
            dm_data = {'recipient_id': user_id}
            dm_result = await self._make_request('POST', '/users/@me/channels', json=dm_data)
            
            if not dm_result or not dm_result.get('id'):
                logger.error("Failed to create DM channel")
                return None
            
            channel_id = dm_result['id']
            
            # Send message
            message_data = {'content': message}
            result = await self._make_request('POST', f'/channels/{channel_id}/messages', json=message_data)
            
            if result and result.get('id'):
                logger.info(f"Successfully sent DM to user {user_id}")
                return result['id']
            else:
                logger.error("Failed to send DM")
                return None
                
        except Exception as e:
            logger.error(f"Error sending DM: {e}")
            return None
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
