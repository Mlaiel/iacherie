"""
Discord Bot API Integration
===========================

Complete Discord Bot API integration for server monitoring, message management, and community insights.
Handles bot commands, server analytics, member management, and real-time monitoring.

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
from urllib.parse import urlencode
import websockets
import base64

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class DiscordGuild:
    """Discord server/guild information"""
    guild_id: str
    name: str
    description: str
    owner_id: str
    member_count: int
    channel_count: int
    role_count: int
    icon_url: str = None
    banner_url: str = None
    features: List[str] = None
    verification_level: int = 0
    preferred_locale: str = "en-US"
    created_at: datetime = None


@dataclass
class DiscordChannel:
    """Discord channel information"""
    channel_id: str
    guild_id: str
    name: str
    channel_type: int  # 0=text, 1=dm, 2=voice, etc.
    position: int = 0
    topic: str = None
    nsfw: bool = False
    last_message_id: str = None
    parent_id: str = None
    message_count: int = 0


@dataclass
class DiscordMessage:
    """Discord message information"""
    message_id: str
    channel_id: str
    guild_id: str
    author_id: str
    author_username: str
    content: str
    timestamp: datetime
    edited_timestamp: Optional[datetime] = None
    reactions: List[Dict[str, Any]] = None
    attachments: List[Dict[str, Any]] = None
    embeds: List[Dict[str, Any]] = None
    message_type: int = 0


@dataclass
class DiscordMember:
    """Discord server member information"""
    user_id: str
    guild_id: str
    username: str
    display_name: str
    joined_at: datetime
    roles: List[str] = None
    is_bot: bool = False
    is_premium: bool = False
    avatar_url: str = None
    status: str = "offline"  # online, idle, dnd, offline


@dataclass
class DiscordAnalytics:
    """Discord server analytics"""
    guild_id: str
    date_range: Dict[str, str]
    total_messages: int = 0
    active_members: int = 0
    new_members: int = 0
    left_members: int = 0
    message_growth: float = 0.0
    member_growth: float = 0.0
    top_channels: List[Dict[str, Any]] = None
    peak_activity_hours: List[int] = None


class DiscordBotAPI:
    """Discord Bot API integration"""
    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://discord.com/api/v10"
        self.gateway_url = None
        self.websocket = None
        self.heartbeat_interval = None
        self.sequence = None
        self.session_id = None
        self.event_handlers: Dict[str, List[Callable]] = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.rate_limiter.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.websocket:
            await self.websocket.close()
        if self.session:
            await self.session.close()
        await self.rate_limiter.__aexit__(exc_type, exc_val, exc_tb)
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        tokens: OAuthTokens,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("discord", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("discord", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{self.base_url}/{endpoint}"
        
        # Default headers
        request_headers = {
            "Authorization": f"Bot {tokens.access_token}",
            "Accept": "application/json",
            "User-Agent": "Ainflue Bot (https://github.com/Mlaiel/Ainflue, 1.0)"
        }
        
        if headers:
            request_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=request_headers) as response:
                    await self.rate_limiter.record_request("discord", endpoint, None, response.status)
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        # Discord rate limit handling
                        retry_after = int(response.headers.get("Retry-After", 1))
                        logger.warning(f"Discord rate limited, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        return await self._make_request(method, endpoint, tokens, params, data, headers)
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                request_headers["Content-Type"] = "application/json"
                async with self.session.post(url, json=data, headers=request_headers, params=params) as response:
                    await self.rate_limiter.record_request("discord", endpoint, None, response.status)
                    
                    if response.status in [200, 201, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    elif response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 1))
                        await asyncio.sleep(retry_after)
                        return await self._make_request(method, endpoint, tokens, params, data, headers)
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() in ["PUT", "PATCH", "DELETE"]:
                if data:
                    request_headers["Content-Type"] = "application/json"
                    
                async with self.session.request(
                    method, url, json=data, headers=request_headers, params=params
                ) as response:
                    await self.rate_limiter.record_request("discord", endpoint, None, response.status)
                    
                    if response.status in [200, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    elif response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 1))
                        await asyncio.sleep(retry_after)
                        return await self._make_request(method, endpoint, tokens, params, data, headers)
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Discord API request failed: {e}")
            raise
            
    async def get_bot_guilds(self, tokens: OAuthTokens, limit: int = 100) -> List[DiscordGuild]:
        """Get guilds where the bot is a member"""
        
        params = {"limit": min(limit, 200)}
        
        response = await self._make_request("GET", "users/@me/guilds", tokens, params=params)
        
        guilds = []
        for item in response:
            guild = DiscordGuild(
                guild_id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                owner_id=item.get("owner_id", ""),
                member_count=item.get("approximate_member_count", 0),
                icon_url=f"https://cdn.discordapp.com/icons/{item['id']}/{item['icon']}.png" if item.get("icon") else None,
                features=item.get("features", [])
            )
            guilds.append(guild)
            
        return guilds
        
    async def get_guild_details(self, tokens: OAuthTokens, guild_id: str) -> DiscordGuild:
        """Get detailed information about a guild"""
        
        params = {"with_counts": "true"}
        
        response = await self._make_request("GET", f"guilds/{guild_id}", tokens, params=params)
        
        guild = DiscordGuild(
            guild_id=response["id"],
            name=response["name"],
            description=response.get("description", ""),
            owner_id=response["owner_id"],
            member_count=response.get("approximate_member_count", 0),
            channel_count=len(response.get("channels", [])),
            role_count=len(response.get("roles", [])),
            icon_url=f"https://cdn.discordapp.com/icons/{response['id']}/{response['icon']}.png" if response.get("icon") else None,
            banner_url=f"https://cdn.discordapp.com/banners/{response['id']}/{response['banner']}.png" if response.get("banner") else None,
            features=response.get("features", []),
            verification_level=response.get("verification_level", 0),
            preferred_locale=response.get("preferred_locale", "en-US")
        )
        
        return guild
        
    async def get_guild_channels(self, tokens: OAuthTokens, guild_id: str) -> List[DiscordChannel]:
        """Get channels in a guild"""
        
        response = await self._make_request("GET", f"guilds/{guild_id}/channels", tokens)
        
        channels = []
        for item in response:
            channel = DiscordChannel(
                channel_id=item["id"],
                guild_id=guild_id,
                name=item["name"],
                channel_type=item["type"],
                position=item.get("position", 0),
                topic=item.get("topic"),
                nsfw=item.get("nsfw", False),
                last_message_id=item.get("last_message_id"),
                parent_id=item.get("parent_id")
            )
            channels.append(channel)
            
        return channels
        
    async def get_channel_messages(
        self,
        tokens: OAuthTokens,
        channel_id: str,
        limit: int = 50,
        before: Optional[str] = None,
        after: Optional[str] = None
    ) -> List[DiscordMessage]:
        """Get messages from a channel"""
        
        params = {"limit": min(limit, 100)}
        if before:
            params["before"] = before
        if after:
            params["after"] = after
            
        response = await self._make_request("GET", f"channels/{channel_id}/messages", tokens, params=params)
        
        messages = []
        for item in response:
            message = DiscordMessage(
                message_id=item["id"],
                channel_id=channel_id,
                guild_id=item.get("guild_id", ""),
                author_id=item["author"]["id"],
                author_username=item["author"]["username"],
                content=item["content"],
                timestamp=datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00")),
                edited_timestamp=datetime.fromisoformat(item["edited_timestamp"].replace("Z", "+00:00")) if item.get("edited_timestamp") else None,
                reactions=item.get("reactions", []),
                attachments=item.get("attachments", []),
                embeds=item.get("embeds", []),
                message_type=item.get("type", 0)
            )
            messages.append(message)
            
        return messages
        
    async def send_message(
        self,
        tokens: OAuthTokens,
        channel_id: str,
        content: str,
        embeds: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List[Dict[str, Any]]] = None
    ) -> DiscordMessage:
        """Send a message to a channel"""
        
        message_data = {"content": content}
        
        if embeds:
            message_data["embeds"] = embeds
            
        # TODO: Handle file uploads if needed
        
        response = await self._make_request("POST", f"channels/{channel_id}/messages", tokens, data=message_data)
        
        message = DiscordMessage(
            message_id=response["id"],
            channel_id=channel_id,
            guild_id=response.get("guild_id", ""),
            author_id=response["author"]["id"],
            author_username=response["author"]["username"],
            content=response["content"],
            timestamp=datetime.fromisoformat(response["timestamp"].replace("Z", "+00:00"))
        )
        
        logger.info(f"Sent Discord message: {message.message_id}")
        return message
        
    async def edit_message(
        self,
        tokens: OAuthTokens,
        channel_id: str,
        message_id: str,
        content: str,
        embeds: Optional[List[Dict[str, Any]]] = None
    ) -> DiscordMessage:
        """Edit a message"""
        
        edit_data = {"content": content}
        if embeds:
            edit_data["embeds"] = embeds
            
        response = await self._make_request("PATCH", f"channels/{channel_id}/messages/{message_id}", tokens, data=edit_data)
        
        message = DiscordMessage(
            message_id=response["id"],
            channel_id=channel_id,
            guild_id=response.get("guild_id", ""),
            author_id=response["author"]["id"],
            author_username=response["author"]["username"],
            content=response["content"],
            timestamp=datetime.fromisoformat(response["timestamp"].replace("Z", "+00:00")),
            edited_timestamp=datetime.fromisoformat(response["edited_timestamp"].replace("Z", "+00:00")) if response.get("edited_timestamp") else None
        )
        
        return message
        
    async def delete_message(self, tokens: OAuthTokens, channel_id: str, message_id: str) -> bool:
        """Delete a message"""
        
        try:
            await self._make_request("DELETE", f"channels/{channel_id}/messages/{message_id}", tokens)
            logger.info(f"Deleted Discord message: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete message {message_id}: {e}")
            return False
            
    async def get_guild_members(
        self,
        tokens: OAuthTokens,
        guild_id: str,
        limit: int = 100,
        after: Optional[str] = None
    ) -> List[DiscordMember]:
        """Get members of a guild"""
        
        params = {"limit": min(limit, 1000)}
        if after:
            params["after"] = after
            
        response = await self._make_request("GET", f"guilds/{guild_id}/members", tokens, params=params)
        
        members = []
        for item in response:
            member = DiscordMember(
                user_id=item["user"]["id"],
                guild_id=guild_id,
                username=item["user"]["username"],
                display_name=item.get("nick", item["user"]["username"]),
                joined_at=datetime.fromisoformat(item["joined_at"].replace("Z", "+00:00")),
                roles=item.get("roles", []),
                is_bot=item["user"].get("bot", False),
                is_premium=item.get("premium_since") is not None,
                avatar_url=f"https://cdn.discordapp.com/avatars/{item['user']['id']}/{item['user']['avatar']}.png" if item["user"].get("avatar") else None
            )
            members.append(member)
            
        return members
        
    async def kick_member(self, tokens: OAuthTokens, guild_id: str, user_id: str, reason: Optional[str] = None) -> bool:
        """Kick a member from the guild"""
        
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
            
        try:
            await self._make_request("DELETE", f"guilds/{guild_id}/members/{user_id}", tokens, headers=headers)
            logger.info(f"Kicked member {user_id} from guild {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to kick member {user_id}: {e}")
            return False
            
    async def ban_member(
        self,
        tokens: OAuthTokens,
        guild_id: str,
        user_id: str,
        reason: Optional[str] = None,
        delete_message_days: int = 0
    ) -> bool:
        """Ban a member from the guild"""
        
        ban_data = {"delete_message_days": min(delete_message_days, 7)}
        
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
            
        try:
            await self._make_request("PUT", f"guilds/{guild_id}/bans/{user_id}", tokens, data=ban_data, headers=headers)
            logger.info(f"Banned member {user_id} from guild {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to ban member {user_id}: {e}")
            return False
            
    async def create_role(
        self,
        tokens: OAuthTokens,
        guild_id: str,
        name: str,
        permissions: int = 0,
        color: int = 0,
        hoist: bool = False,
        mentionable: bool = False
    ) -> Dict[str, Any]:
        """Create a new role in the guild"""
        
        role_data = {
            "name": name,
            "permissions": str(permissions),
            "color": color,
            "hoist": hoist,
            "mentionable": mentionable
        }
        
        response = await self._make_request("POST", f"guilds/{guild_id}/roles", tokens, data=role_data)
        
        logger.info(f"Created role {response['id']} in guild {guild_id}")
        return response
        
    async def add_member_role(self, tokens: OAuthTokens, guild_id: str, user_id: str, role_id: str) -> bool:
        """Add a role to a member"""
        
        try:
            await self._make_request("PUT", f"guilds/{guild_id}/members/{user_id}/roles/{role_id}", tokens)
            logger.info(f"Added role {role_id} to member {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add role {role_id} to member {user_id}: {e}")
            return False
            
    async def remove_member_role(self, tokens: OAuthTokens, guild_id: str, user_id: str, role_id: str) -> bool:
        """Remove a role from a member"""
        
        try:
            await self._make_request("DELETE", f"guilds/{guild_id}/members/{user_id}/roles/{role_id}", tokens)
            logger.info(f"Removed role {role_id} from member {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove role {role_id} from member {user_id}: {e}")
            return False
            
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler for Discord gateway events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    async def start_gateway_connection(self, tokens: OAuthTokens):
        """Start Discord Gateway connection for real-time events"""
        
        # Get gateway URL
        gateway_response = await self._make_request("GET", "gateway/bot", tokens)
        self.gateway_url = gateway_response["url"]
        
        # Connect to gateway
        uri = f"{self.gateway_url}/?v=10&encoding=json"
        
        try:
            self.websocket = await websockets.connect(uri)
            logger.info("Connected to Discord Gateway")
            
            # Start listening for events
            await self._handle_gateway_events(tokens)
            
        except Exception as e:
            logger.error(f"Gateway connection failed: {e}")
            
    async def _handle_gateway_events(self, tokens: OAuthTokens):
        """Handle Discord Gateway events"""
        
        async for message in self.websocket:
            try:
                data = json.loads(message)
                opcode = data["op"]
                
                if opcode == 10:  # Hello
                    self.heartbeat_interval = data["d"]["heartbeat_interval"]
                    # Send identify
                    identify_payload = {
                        "op": 2,
                        "d": {
                            "token": tokens.access_token,
                            "intents": 513,  # GUILD_MESSAGES + GUILDS
                            "properties": {
                                "$os": "linux",
                                "$browser": "ainflue",
                                "$device": "ainflue"
                            }
                        }
                    }
                    await self.websocket.send(json.dumps(identify_payload))
                    
                    # Start heartbeat
                    asyncio.create_task(self._heartbeat())
                    
                elif opcode == 0:  # Dispatch
                    self.sequence = data["s"]
                    event_type = data["t"]
                    event_data = data["d"]
                    
                    if event_type == "READY":
                        self.session_id = event_data["session_id"]
                        logger.info("Discord bot ready")
                        
                    # Call event handlers
                    if event_type in self.event_handlers:
                        for handler in self.event_handlers[event_type]:
                            try:
                                await handler(event_data)
                            except Exception as e:
                                logger.error(f"Error in event handler for {event_type}: {e}")
                                
                elif opcode == 1:  # Heartbeat request
                    await self._send_heartbeat()
                    
            except Exception as e:
                logger.error(f"Error handling gateway event: {e}")
                
    async def _heartbeat(self):
        """Send periodic heartbeats to maintain connection"""
        if not self.heartbeat_interval:
            return
            
        while self.websocket and not self.websocket.closed:
            await asyncio.sleep(self.heartbeat_interval / 1000)
            await self._send_heartbeat()
            
    async def _send_heartbeat(self):
        """Send a heartbeat to Discord Gateway"""
        if self.websocket and not self.websocket.closed:
            heartbeat_payload = {
                "op": 1,
                "d": self.sequence
            }
            await self.websocket.send(json.dumps(heartbeat_payload))
            
    async def get_server_analytics(
        self,
        tokens: OAuthTokens,
        guild_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> DiscordAnalytics:
        """Get analytics for a Discord server (custom implementation)"""
        
        try:
            # Get recent messages across all channels to calculate activity
            channels = await self.get_guild_channels(tokens, guild_id)
            text_channels = [ch for ch in channels if ch.channel_type == 0]  # Text channels only
            
            total_messages = 0
            channel_activity = {}
            
            for channel in text_channels[:10]:  # Limit to first 10 channels to avoid rate limits
                try:
                    messages = await self.get_channel_messages(tokens, channel.channel_id, limit=100)
                    
                    # Filter messages by date range
                    filtered_messages = [
                        msg for msg in messages 
                        if start_date <= msg.timestamp <= end_date
                    ]
                    
                    total_messages += len(filtered_messages)
                    channel_activity[channel.name] = len(filtered_messages)
                    
                except Exception as e:
                    logger.warning(f"Could not get messages from channel {channel.channel_id}: {e}")
                    
            # Get member count (approximate active members)
            guild = await self.get_guild_details(tokens, guild_id)
            
            # Sort channels by activity
            top_channels = sorted(
                [{"name": name, "messages": count} for name, count in channel_activity.items()],
                key=lambda x: x["messages"],
                reverse=True
            )[:5]
            
            analytics = DiscordAnalytics(
                guild_id=guild_id,
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                },
                total_messages=total_messages,
                active_members=guild.member_count,  # Approximate
                top_channels=top_channels
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get server analytics for {guild_id}: {e}")
            return DiscordAnalytics(
                guild_id=guild_id,
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                }
            )