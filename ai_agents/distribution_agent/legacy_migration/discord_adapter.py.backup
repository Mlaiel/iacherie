"""Discord Platform Adapter for IA Influencer Agent Distribution System.
Handles community content distribution, server management, and engagement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass
import json

from ..core.base_adapter import BasePlatformAdapter
from ..models.distribution_models import (
    DistributionRequest, DistributionResult, ContentMetadata,
    PlatformAnalytics, RevenueData
)
from ..utils.exceptions import DistributionError, AuthenticationError

logger = logging.getLogger(__name__)

@dataclass
class DiscordCredentials:
    """Discord API credentials configuration."""
    bot_token: str
    client_id: str
    client_secret: str
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None

class DiscordAdapter(BasePlatformAdapter):
    """
    Advanced Discord platform adapter for community content distribution.
    Supports messages, embeds, file uploads, and server management.
    """
    
    PLATFORM_NAME = "discord"
    API_BASE_URL = "https://discord.com/api/v10"
    CDN_BASE_URL = "https://cdn.discordapp.com"
    
    MAX_MESSAGE_LENGTH = 2000
    MAX_EMBED_TITLE_LENGTH = 256
    MAX_EMBED_DESCRIPTION_LENGTH = 4096
    MAX_FILE_SIZE_MB = 25
    MAX_FILE_SIZE_MB_NITRO = 100
    SUPPORTED_FILE_FORMATS = ["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "webm", "mp3", "wav", "ogg"]
    
    def __init__(self, credentials: DiscordCredentials):
        super().__init__(self.PLATFORM_NAME)
        self.credentials = credentials
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bot {credentials.bot_token}",
            "Content-Type": "application/json"
        })
        self._verify_credentials()
    
    def _verify_credentials(self):
        """Verify Discord API credentials."""
        try:
            # Test bot connection
            response = self.session.get(f"{self.API_BASE_URL}/users/@me")
            
            if response.status_code != 200:
                raise AuthenticationError(f"Discord API error: {response.status_code}")
            
            bot_data = response.json()
            logger.info(f"Discord API connected for bot: {bot_data.get('username', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to verify Discord credentials: {e}")
            raise AuthenticationError(f"Discord authentication failed: {e}")
    
    async def authenticate_user(self, user_id: str) -> Dict[str, Any]:
        """Generate Discord OAuth URL for user authentication."""
        try:
            auth_params = {
                "response_type": "code",
                "client_id": self.credentials.client_id,
                "redirect_uri": "https://your-app.com/discord/callback",
                "scope": "identify guilds bot",
                "permissions": "8"  # Administrator permissions (adjust as needed)
            }
            
            auth_url = "https://discord.com/api/oauth2/authorize?" + "&".join([
                f"{key}={value}" for key, value in auth_params.items()
            ])
            
            return {
                "auth_url": auth_url,
                "platform": self.PLATFORM_NAME,
                "user_id": user_id,
                "expires_at": datetime.now() + timedelta(hours=2)
            }
            
        except Exception as e:
            logger.error(f"Discord user authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate user: {e}")
    
    async def validate_content(self, content_metadata: ContentMetadata) -> Dict[str, Any]:
        """Validate content meets Discord requirements."""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Message length validation
        message_length = len((content_metadata.title or "") + (content_metadata.description or ""))
        if message_length > self.MAX_MESSAGE_LENGTH:
            # If too long, we'll use embeds
            if len(content_metadata.description or "") > self.MAX_EMBED_DESCRIPTION_LENGTH:
                validation_results["warnings"].append(
                    f"Content is {message_length} characters. Will be truncated for Discord."
                )
        
        # File size validation
        if content_metadata.file_size_mb > self.MAX_FILE_SIZE_MB:
            validation_results["is_valid"] = False
            validation_results["errors"].append(
                f"File too large: {content_metadata.file_size_mb}MB. Max: {self.MAX_FILE_SIZE_MB}MB"
            )
        
        # File format validation
        if content_metadata.file_format and content_metadata.file_format.lower() not in self.SUPPORTED_FILE_FORMATS:
            validation_results["warnings"].append(
                f"File format {content_metadata.file_format} may not display properly in Discord"
            )
        
        return validation_results
    
    async def upload_content(self, distribution_request: DistributionRequest) -> DistributionResult:
        """Upload content to Discord channel."""
        try:
            # Validate content first
            validation = await self.validate_content(distribution_request.content_metadata)
            if not validation["is_valid"]:
                raise DistributionError(f"Content validation failed: {validation['errors']}")
            
            content_metadata = distribution_request.content_metadata
            
            # Determine target channel
            channel_id = self.credentials.channel_id or await self._get_default_channel()
            
            # Prepare message content
            message_data = await self._prepare_message_data(content_metadata)
            
            # Handle file upload if present
            files = None
            if hasattr(distribution_request, 'file_path') and distribution_request.file_path:
                files = await self._prepare_file_upload(distribution_request.file_path, content_metadata)
            
            # Send message
            result = await self._send_message(channel_id, message_data, files)
            
            if "error" in result:
                raise DistributionError(f"Discord API error: {result['error']}")
            
            message_id = result["id"]
            message_url = f"https://discord.com/channels/{self.credentials.guild_id}/{channel_id}/{message_id}"
            
            return DistributionResult(
                success=True,
                platform=self.PLATFORM_NAME,
                content_id=f"discord_{message_id}",
                platform_content_id=message_id,
                url=message_url,
                metadata={
                    "message_id": message_id,
                    "channel_id": channel_id,
                    "guild_id": self.credentials.guild_id,
                    "message_url": message_url
                }
            )
            
        except Exception as e:
            logger.error(f"Discord content upload failed: {e}")
            return DistributionResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error=str(e),
                metadata={"error_type": "upload_failed"}
            )
    
    async def _get_default_channel(self) -> str:
        """Get default channel for posting."""
        try:
            if not self.credentials.guild_id:
                raise DistributionError("No guild ID configured for Discord")
            
            # Get guild channels
            response = self.session.get(f"{self.API_BASE_URL}/guilds/{self.credentials.guild_id}/channels")
            
            if response.status_code == 200:
                channels = response.json()
                
                # Find first text channel
                for channel in channels:
                    if channel.get("type") == 0:  # Text channel
                        return channel["id"]
            
            raise DistributionError("No suitable channel found in Discord server")
            
        except Exception as e:
            logger.error(f"Failed to get Discord default channel: {e}")
            raise DistributionError("Failed to find Discord channel")
    
    async def _prepare_message_data(self, content_metadata: ContentMetadata) -> Dict:
        """Prepare message data for Discord."""
        # Check if we need to use embed for longer content
        message_text = ""
        embed = None
        
        total_length = len((content_metadata.title or "") + (content_metadata.description or ""))
        
        if total_length <= self.MAX_MESSAGE_LENGTH and not content_metadata.title:
            # Simple message
            message_text = content_metadata.description or ""
        else:
            # Use embed for structured content
            embed = {
                "title": content_metadata.title or "",
                "description": content_metadata.description or "",
                "color": 0x5865F2,  # Discord blurple
                "timestamp": datetime.now().isoformat()
            }
            
            # Add author if available
            if hasattr(content_metadata, 'author') and content_metadata.author:
                embed["author"] = {"name": content_metadata.author}
            
            # Add thumbnail if available
            if hasattr(content_metadata, 'thumbnail_url') and content_metadata.thumbnail_url:
                embed["thumbnail"] = {"url": content_metadata.thumbnail_url}
            
            # Add fields for additional info
            fields = []
            if hasattr(content_metadata, 'tags') and content_metadata.tags:
                fields.append({
                    "name": "Tags",
                    "value": ", ".join(content_metadata.tags[:10]),  # Limit tags
                    "inline": True
                })
            
            if hasattr(content_metadata, 'duration_seconds') and content_metadata.duration_seconds:
                duration_str = f"{content_metadata.duration_seconds // 60}:{content_metadata.duration_seconds % 60:02d}"
                fields.append({
                    "name": "Duration",
                    "value": duration_str,
                    "inline": True
                })
            
            if fields:
                embed["fields"] = fields
        
        message_data = {}
        if message_text:
            message_data["content"] = message_text
        if embed:
            message_data["embeds"] = [embed]
        
        return message_data
    
    async def _prepare_file_upload(self, file_path: str, content_metadata: ContentMetadata) -> Dict:
        """Prepare file for Discord upload."""
        try:
            import os
            filename = os.path.basename(file_path)
            
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            return {
                "file": (filename, file_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare Discord file upload: {e}")
            return {}
    
    async def _send_message(self, channel_id: str, message_data: Dict, files: Optional[Dict] = None) -> Dict:
        """Send message to Discord channel."""
        try:
            url = f"{self.API_BASE_URL}/channels/{channel_id}/messages"
            
            if files:
                # Multipart form for file upload
                files_dict = files
                response = self.session.post(
                    url,
                    data={"payload_json": json.dumps(message_data)},
                    files=files_dict,
                    headers={"Authorization": f"Bot {self.credentials.bot_token}"}  # Remove Content-Type for multipart
                )
            else:
                # JSON for text-only messages
                response = self.session.post(url, json=message_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to send Discord message: {response.text}"}
                
        except Exception as e:
            logger.error(f"Failed to send Discord message: {e}")
            return {"error": str(e)}
    
    async def get_analytics(self, content_id: str, date_range: tuple = None) -> PlatformAnalytics:
        """Retrieve analytics data for Discord message."""
        try:
            message_id = content_id.replace("discord_", "")
            channel_id = self.credentials.channel_id or await self._get_default_channel()
            
            # Get message details
            response = self.session.get(f"{self.API_BASE_URL}/channels/{channel_id}/messages/{message_id}")
            
            if response.status_code != 200:
                raise DistributionError(f"Failed to fetch Discord message: {response.text}")
            
            message_data = response.json()
            
            # Discord doesn't provide traditional analytics, so we estimate based on reactions
            reactions = message_data.get("reactions", [])
            
            total_reactions = sum(reaction.get("count", 0) for reaction in reactions)
            unique_reactors = len(reactions)  # Approximation
            
            # Get server member count for reach estimation
            server_members = await self._get_server_member_count()
            
            # Estimate views (Discord doesn't provide this)
            estimated_views = min(total_reactions * 10, server_members)  # Conservative estimate
            
            return PlatformAnalytics(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                views=estimated_views,
                likes=total_reactions,  # Reactions as likes
                shares=0,  # Discord doesn't have traditional shares
                comments=0,  # Would need to check thread/replies
                engagement_rate=(total_reactions / estimated_views * 100) if estimated_views > 0 else 0,
                reach=estimated_views,
                impressions=estimated_views,
                revenue=0.0,  # Discord doesn't have direct monetization
                date_range=date_range or (datetime.now() - timedelta(days=1), datetime.now()),
                additional_metrics={
                    "reaction_count": total_reactions,
                    "unique_reactors": unique_reactors,
                    "server_members": server_members,
                    "message_timestamp": message_data.get("timestamp"),
                    "message_edited": bool(message_data.get("edited_timestamp"))
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Discord analytics: {e}")
            raise DistributionError(f"Analytics retrieval failed: {e}")
    
    async def _get_server_member_count(self) -> int:
        """Get server member count."""
        try:
            if not self.credentials.guild_id:
                return 0
            
            response = self.session.get(f"{self.API_BASE_URL}/guilds/{self.credentials.guild_id}")
            
            if response.status_code == 200:
                guild_data = response.json()
                return guild_data.get("member_count", 0)
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to get Discord server member count: {e}")
            return 0
    
    async def get_revenue_data(self, content_id: str, date_range: tuple = None) -> RevenueData:
        """Estimate revenue from Discord content (server boosts, premium features)."""
        try:
            analytics = await self.get_analytics(content_id, date_range)
            
            # Discord doesn't have direct monetization for content
            # Revenue estimates based on community engagement and potential premium features
            
            engagement_value = analytics.likes * 0.05  # $0.05 per reaction
            community_value = analytics.additional_metrics.get("server_members", 0) * 0.01  # $0.01 per member reached
            
            estimated_revenue = engagement_value + community_value
            
            return RevenueData(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                gross_revenue=estimated_revenue,
                platform_fee=0.0,  # No platform fee for organic content
                net_revenue=estimated_revenue,
                currency="USD",
                period_start=date_range[0] if date_range else datetime.now() - timedelta(days=30),
                period_end=date_range[1] if date_range else datetime.now(),
                payment_status="estimated",
                additional_data={
                    "engagement_value": engagement_value,
                    "community_value": community_value,
                    "monetization_note": "Discord focuses on community building rather than direct monetization"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate Discord revenue: {e}")
            raise DistributionError(f"Revenue calculation failed: {e}")
    
    async def update_content_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """Update Discord message (limited editing available)."""
        try:
            message_id = content_id.replace("discord_", "")
            channel_id = self.credentials.channel_id or await self._get_default_channel()
            
            # Discord allows editing message content
            update_data = {}
            
            if "content" in metadata:
                update_data["content"] = metadata["content"]
            
            if "embed" in metadata:
                update_data["embeds"] = [metadata["embed"]]
            
            if not update_data:
                logger.warning(f"No updatable metadata provided for Discord message {content_id}")
                return False
            
            response = self.session.patch(
                f"{self.API_BASE_URL}/channels/{channel_id}/messages/{message_id}",
                json=update_data
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to update Discord metadata: {e}")
            return False
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Discord message."""
        try:
            message_id = content_id.replace("discord_", "")
            channel_id = self.credentials.channel_id or await self._get_default_channel()
            
            response = self.session.delete(f"{self.API_BASE_URL}/channels/{channel_id}/messages/{message_id}")
            
            if response.status_code == 204:
                logger.info(f"Successfully deleted Discord message: {content_id}")
                return True
            else:
                logger.error(f"Failed to delete Discord message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete Discord content: {e}")
            return False
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """Return platform-specific limits and requirements."""
        return {
            "max_message_length": self.MAX_MESSAGE_LENGTH,
            "max_embed_title_length": self.MAX_EMBED_TITLE_LENGTH,
            "max_embed_description_length": self.MAX_EMBED_DESCRIPTION_LENGTH,
            "max_file_size_mb": self.MAX_FILE_SIZE_MB,
            "max_file_size_mb_nitro": self.MAX_FILE_SIZE_MB_NITRO,
            "supported_file_formats": self.SUPPORTED_FILE_FORMATS,
            "max_embeds_per_message": 10,
            "max_fields_per_embed": 25,
            "rate_limits": {
                "messages_per_second": 5,
                "messages_per_channel_per_second": 1
            },
            "community_features": {
                "server_boosts": True,
                "premium_emojis": True,
                "voice_channels": True,
                "threads": True,
                "stage_channels": True
            },
            "bot_permissions_required": [
                "SEND_MESSAGES",
                "EMBED_LINKS",
                "ATTACH_FILES",
                "READ_MESSAGE_HISTORY",
                "USE_EXTERNAL_EMOJIS"
            ]
        }
