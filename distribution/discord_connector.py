"""
Discord Platform Connector
==========================

Enterprise-grade Discord API connector for Ainflue Distribution Platform.
Supports Discord bots, webhooks, slash commands, and community management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import logging
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

class DiscordChannelType(Enum):
    """Discord channel types"""
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_ANNOUNCEMENT = 5
    ANNOUNCEMENT_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_FORUM = 15

class DiscordMessageType(Enum):
    """Discord message types"""
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    USER_JOIN = 7
    GUILD_BOOST = 8
    REPLY = 19
    CHAT_INPUT_COMMAND = 20

class DiscordEmbedType(Enum):
    """Discord embed types"""
    RICH = "rich"
    IMAGE = "image"
    VIDEO = "video"
    GIFV = "gifv"
    ARTICLE = "article"
    LINK = "link"

@dataclass
class DiscordCredentials:
    """Discord bot credentials"""
    bot_token: str
    application_id: str
    public_key: str
    webhook_url: Optional[str] = None
    guild_id: Optional[str] = None

@dataclass
class DiscordEmbed:
    """Discord embed structure"""
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[datetime] = None
    color: Optional[int] = None
    footer: Optional[Dict[str, str]] = None
    image: Optional[Dict[str, str]] = None
    thumbnail: Optional[Dict[str, str]] = None
    video: Optional[Dict[str, str]] = None
    provider: Optional[Dict[str, str]] = None
    author: Optional[Dict[str, str]] = None
    fields: List[Dict[str, Union[str, bool]]] = field(default_factory=list)

@dataclass
class DiscordMessage:
    """Discord message structure"""
    content: Optional[str] = None
    embeds: List[DiscordEmbed] = field(default_factory=list)
    tts: bool = False
    allowed_mentions: Optional[Dict[str, Any]] = None
    message_reference: Optional[Dict[str, str]] = None
    components: List[Dict[str, Any]] = field(default_factory=list)
    sticker_ids: List[str] = field(default_factory=list)
    files: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DiscordPublishResult:
    """Result of Discord publish operation"""
    success: bool
    message_id: Optional[str] = None
    channel_id: Optional[str] = None
    message_url: Optional[str] = None
    timestamp: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class DiscordConnector:
    """Discord platform connector with bot and webhook support"""
    
    BASE_URL = "https://discord.com/api/v10"
    CDN_URL = "https://cdn.discordapp.com"
    
    def __init__(self, credentials: DiscordCredentials):
        """Initialize Discord connector"""
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.bot_user: Optional[Dict[str, Any]] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self._authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _authenticate(self):
        """Authenticate with Discord API"""
        try:
            headers = {
                "Authorization": f"Bot {self.credentials.bot_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{self.BASE_URL}/users/@me",
                headers=headers
            ) as response:
                if response.status == 200:
                    self.bot_user = await response.json()
                    logger.info(f"Discord bot authenticated: {self.bot_user.get('username')}")
                else:
                    error_data = await response.text()
                    raise Exception(f"Discord authentication failed: {error_data}")
                    
        except Exception as e:
            logger.error(f"Discord authentication error: {e}")
            raise
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Discord API"""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        headers = {
            "Authorization": f"Bot {self.credentials.bot_token}",
            "User-Agent": "Ainflue-Bot (https://ainflue.com, 1.0)"
        }
        
        # Handle multipart data for file uploads
        if files:
            form_data = aiohttp.FormData()
            
            if data:
                form_data.add_field('payload_json', json.dumps(data))
            
            for key, file_data in files.items():
                form_data.add_field(
                    key, 
                    file_data['content'], 
                    filename=file_data.get('filename', 'file'),
                    content_type=file_data.get('content_type', 'application/octet-stream')
                )
            
            data_to_send = form_data
        else:
            headers["Content-Type"] = "application/json"
            data_to_send = data
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data_to_send if files else None,
                json=data if not files else None,
                params=params
            ) as response:
                
                if response.status == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 1))
                    logger.warning(f"Discord rate limit hit, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    
                    # Retry the request
                    return await self._make_request(method, endpoint, data, files, params)
                
                response.raise_for_status()
                
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    return {"status": "success", "data": await response.text()}
                
        except aiohttp.ClientError as e:
            logger.error(f"Discord API request failed: {e}")
            raise
    
    async def send_message(
        self, 
        channel_id: str, 
        message: DiscordMessage
    ) -> DiscordPublishResult:
        """Send message to Discord channel"""
        try:
            # Prepare message data
            message_data = {}
            
            if message.content:
                message_data["content"] = message.content
            
            if message.embeds:
                message_data["embeds"] = [
                    self._embed_to_dict(embed) for embed in message.embeds
                ]
            
            if message.tts:
                message_data["tts"] = message.tts
            
            if message.allowed_mentions:
                message_data["allowed_mentions"] = message.allowed_mentions
            
            if message.components:
                message_data["components"] = message.components
            
            # Handle file attachments
            files = {}
            if message.files:
                for i, file_data in enumerate(message.files):
                    files[f"file{i}"] = file_data
            
            response = await self._make_request(
                "POST", 
                f"/channels/{channel_id}/messages",
                data=message_data,
                files=files if files else None
            )
            
            return DiscordPublishResult(
                success=True,
                message_id=response.get("id"),
                channel_id=channel_id,
                message_url=f"https://discord.com/channels/{self.credentials.guild_id}/{channel_id}/{response.get('id')}",
                timestamp=datetime.fromisoformat(response.get("timestamp", "").replace("Z", "+00:00")),
                metadata=response
            )
            
        except Exception as e:
            logger.error(f"Failed to send Discord message: {e}")
            return DiscordPublishResult(
                success=False,
                error=str(e),
                channel_id=channel_id
            )
    
    async def send_webhook_message(
        self, 
        webhook_url: str, 
        message: DiscordMessage,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> DiscordPublishResult:
        """Send message via Discord webhook"""
        try:
            # Parse webhook URL to get ID and token
            webhook_parts = webhook_url.split("/")
            webhook_id = webhook_parts[-2]
            webhook_token = webhook_parts[-1]
            
            # Prepare webhook data
            webhook_data = {}
            
            if username:
                webhook_data["username"] = username
            
            if avatar_url:
                webhook_data["avatar_url"] = avatar_url
            
            if message.content:
                webhook_data["content"] = message.content
            
            if message.embeds:
                webhook_data["embeds"] = [
                    self._embed_to_dict(embed) for embed in message.embeds
                ]
            
            if message.tts:
                webhook_data["tts"] = message.tts
            
            # Use webhook endpoint (no bot token required)
            url = f"{self.BASE_URL}/webhooks/{webhook_id}/{webhook_token}"
            
            async with self.session.post(
                url,
                json=webhook_data
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                return DiscordPublishResult(
                    success=True,
                    message_id=result.get("id"),
                    channel_id=result.get("channel_id"),
                    timestamp=datetime.fromisoformat(result.get("timestamp", "").replace("Z", "+00:00")),
                    metadata=result
                )
                
        except Exception as e:
            logger.error(f"Failed to send Discord webhook message: {e}")
            return DiscordPublishResult(
                success=False,
                error=str(e)
            )
    
    def _embed_to_dict(self, embed: DiscordEmbed) -> Dict[str, Any]:
        """Convert DiscordEmbed to dictionary"""
        embed_dict = {}
        
        if embed.title:
            embed_dict["title"] = embed.title
        if embed.description:
            embed_dict["description"] = embed.description
        if embed.url:
            embed_dict["url"] = embed.url
        if embed.timestamp:
            embed_dict["timestamp"] = embed.timestamp.isoformat()
        if embed.color:
            embed_dict["color"] = embed.color
        if embed.footer:
            embed_dict["footer"] = embed.footer
        if embed.image:
            embed_dict["image"] = embed.image
        if embed.thumbnail:
            embed_dict["thumbnail"] = embed.thumbnail
        if embed.video:
            embed_dict["video"] = embed.video
        if embed.provider:
            embed_dict["provider"] = embed.provider
        if embed.author:
            embed_dict["author"] = embed.author
        if embed.fields:
            embed_dict["fields"] = embed.fields
            
        return embed_dict
    
    async def create_slash_command(
        self, 
        name: str, 
        description: str,
        options: List[Dict[str, Any]] = None,
        guild_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a slash command"""
        command_data = {
            "name": name,
            "description": description,
            "type": 1  # CHAT_INPUT
        }
        
        if options:
            command_data["options"] = options
        
        endpoint = f"/applications/{self.credentials.application_id}"
        if guild_id:
            endpoint += f"/guilds/{guild_id}"
        endpoint += "/commands"
        
        return await self._make_request("POST", endpoint, data=command_data)
    
    async def get_guild_channels(self, guild_id: str) -> List[Dict[str, Any]]:
        """Get all channels in a guild"""
        return await self._make_request("GET", f"/guilds/{guild_id}/channels")
    
    async def create_thread(
        self, 
        channel_id: str, 
        name: str,
        auto_archive_duration: int = 1440,  # 24 hours
        message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a thread in a channel"""
        thread_data = {
            "name": name,
            "auto_archive_duration": auto_archive_duration
        }
        
        if message_id:
            endpoint = f"/channels/{channel_id}/messages/{message_id}/threads"
        else:
            endpoint = f"/channels/{channel_id}/threads"
            thread_data["type"] = DiscordChannelType.PUBLIC_THREAD.value
        
        return await self._make_request("POST", endpoint, data=thread_data)
    
    async def get_channel_messages(
        self, 
        channel_id: str, 
        limit: int = 50,
        before: Optional[str] = None,
        after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get messages from a channel"""
        params = {"limit": limit}
        
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        
        return await self._make_request("GET", f"/channels/{channel_id}/messages", params=params)
    
    async def add_reaction(self, channel_id: str, message_id: str, emoji: str) -> bool:
        """Add reaction to a message"""
        try:
            await self._make_request(
                "PUT", 
                f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add reaction: {e}")
            return False
    
    async def pin_message(self, channel_id: str, message_id: str) -> bool:
        """Pin a message in a channel"""
        try:
            await self._make_request(
                "PUT", 
                f"/channels/{channel_id}/pins/{message_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to pin message: {e}")
            return False
    
    async def get_guild_analytics(self, guild_id: str) -> Dict[str, Any]:
        """Get guild analytics and insights"""
        try:
            # Get guild info
            guild = await self._make_request("GET", f"/guilds/{guild_id}")
            
            # Get guild members count
            guild_preview = await self._make_request("GET", f"/guilds/{guild_id}/preview")
            
            # Get channels
            channels = await self.get_guild_channels(guild_id)
            
            return {
                "guild_info": guild,
                "member_count": guild_preview.get("approximate_member_count", 0),
                "presence_count": guild_preview.get("approximate_presence_count", 0),
                "channel_count": len(channels),
                "text_channels": len([c for c in channels if c.get("type") == DiscordChannelType.GUILD_TEXT.value]),
                "voice_channels": len([c for c in channels if c.get("type") == DiscordChannelType.GUILD_VOICE.value]),
                "categories": len([c for c in channels if c.get("type") == DiscordChannelType.GUILD_CATEGORY.value])
            }
            
        except Exception as e:
            logger.error(f"Failed to get guild analytics: {e}")
            return {"error": str(e)}
    
    async def validate_connection(self) -> bool:
        """Validate Discord connection"""
        try:
            if not self.bot_user:
                await self._authenticate()
            
            return self.bot_user is not None
            
        except Exception as e:
            logger.error(f"Discord connection validation failed: {e}")
            return False
    
    async def get_platform_limits(self) -> Dict[str, Any]:
        """Get Discord platform limits and guidelines"""
        return {
            "max_message_length": 2000,
            "max_embed_title_length": 256,
            "max_embed_description_length": 4096,
            "max_embed_fields": 25,
            "max_embed_field_name_length": 256,
            "max_embed_field_value_length": 1024,
            "max_embeds_per_message": 10,
            "max_file_size_mb": 8,  # 8MB for regular users, 50MB for Nitro
            "max_files_per_message": 10,
            "rate_limits": {
                "messages_per_channel_per_second": 5,
                "global_requests_per_second": 50,
                "webhook_requests_per_second": 30
            },
            "supported_file_types": [
                "png", "jpg", "jpeg", "gif", "webp", "mp4", "mov", "webm",
                "mp3", "ogg", "wav", "flac", "pdf", "txt", "docx", "xlsx"
            ]
        }


# Export main components
__all__ = [
    "DiscordConnector",
    "DiscordCredentials",
    "DiscordMessage", 
    "DiscordEmbed",
    "DiscordPublishResult",
    "DiscordChannelType",
    "DiscordMessageType",
    "DiscordEmbedType"
]