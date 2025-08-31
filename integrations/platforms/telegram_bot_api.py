"""
Telegram Bot API Integration
============================

Complete Telegram Bot API integration for channel monitoring, message management, and analytics.
Handles bot commands, channel analytics, subscriber management, and real-time monitoring.

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
import hashlib
import hmac

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class TelegramChat:
    """Telegram chat/channel information"""
    chat_id: str
    chat_type: str  # "private", "group", "supergroup", "channel"
    title: str
    username: str = None
    description: str = None
    invite_link: str = None
    member_count: int = 0
    photo_url: str = None
    pinned_message_id: str = None
    permissions: Dict[str, bool] = None
    is_verified: bool = False


@dataclass
class TelegramMessage:
    """Telegram message information"""
    message_id: str
    chat_id: str
    sender_id: str
    sender_username: str
    text: str
    date: datetime
    edit_date: Optional[datetime] = None
    reply_to_message_id: str = None
    forward_from_chat_id: str = None
    media_type: str = None  # "photo", "video", "document", "audio", etc.
    media_url: str = None
    views: int = 0
    reactions: List[Dict[str, Any]] = None


@dataclass
class TelegramUser:
    """Telegram user information"""
    user_id: str
    username: str
    first_name: str
    last_name: str = None
    is_bot: bool = False
    is_premium: bool = False
    language_code: str = None
    profile_photo_url: str = None
    bio: str = None


@dataclass
class TelegramChannel:
    """Telegram channel information"""
    channel_id: str
    title: str
    username: str
    description: str
    subscriber_count: int = 0
    photo_url: str = None
    invite_link: str = None
    is_verified: bool = False
    is_scam: bool = False
    is_fake: bool = False
    message_count: int = 0
    last_message_date: Optional[datetime] = None


@dataclass
class TelegramAnalytics:
    """Telegram channel/chat analytics"""
    chat_id: str
    date_range: Dict[str, str]
    total_messages: int = 0
    total_views: int = 0
    total_forwards: int = 0
    subscriber_growth: int = 0
    active_users: int = 0
    engagement_rate: float = 0.0
    top_posts: List[Dict[str, Any]] = None
    peak_activity_hours: List[int] = None
    subscriber_demographics: Dict[str, Any] = None


class TelegramBotAPI:
    """Telegram Bot API integration"""
    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://api.telegram.org/bot"
        self.webhook_handlers: Dict[str, List[Callable]] = {}
        self.polling_active = False
        self.last_update_id = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.rate_limiter.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.polling_active = False
        if self.session:
            await self.session.close()
        await self.rate_limiter.__aexit__(exc_type, exc_val, exc_tb)
        
    async def _make_request(
        self,
        method: str,
        bot_token: str,
        api_method: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make API request to Telegram Bot API"""
        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("telegram", api_method)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("telegram", api_method)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{self.base_url}{bot_token}/{api_method}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    await self.rate_limiter.record_request("telegram", api_method, None, response.status)
                    
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            return result["result"]
                        else:
                            raise Exception(f"Telegram API error: {result.get('description', 'Unknown error')}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP error: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                if files:
                    # Multipart form data for file uploads
                    form_data = aiohttp.FormData()
                    if data:
                        for key, value in data.items():
                            form_data.add_field(key, str(value))
                    for key, file_info in files.items():
                        form_data.add_field(key, file_info["content"], filename=file_info["filename"])
                    
                    async with self.session.post(url, data=form_data, params=params) as response:
                        await self.rate_limiter.record_request("telegram", api_method, None, response.status)
                        
                        if response.status == 200:
                            result = await response.json()
                            if result.get("ok"):
                                return result["result"]
                            else:
                                raise Exception(f"Telegram API error: {result.get('description', 'Unknown error')}")
                        else:
                            error_text = await response.text()
                            raise Exception(f"HTTP error: {response.status} - {error_text}")
                else:
                    # JSON data
                    headers = {"Content-Type": "application/json"}
                    request_data = data or {}
                    if params:
                        request_data.update(params)
                        
                    async with self.session.post(url, json=request_data, headers=headers) as response:
                        await self.rate_limiter.record_request("telegram", api_method, None, response.status)
                        
                        if response.status == 200:
                            result = await response.json()
                            if result.get("ok"):
                                return result["result"]
                            else:
                                raise Exception(f"Telegram API error: {result.get('description', 'Unknown error')}")
                        else:
                            error_text = await response.text()
                            raise Exception(f"HTTP error: {response.status} - {error_text}")
                            
        except Exception as e:
            logger.error(f"Telegram API request failed: {e}")
            raise
            
    async def get_me(self, bot_token: str) -> TelegramUser:
        """Get bot information"""
        
        response = await self._make_request("GET", bot_token, "getMe")
        
        user = TelegramUser(
            user_id=str(response["id"]),
            username=response.get("username", ""),
            first_name=response["first_name"],
            last_name=response.get("last_name"),
            is_bot=response.get("is_bot", True)
        )
        
        return user
        
    async def get_chat(self, bot_token: str, chat_id: str) -> TelegramChat:
        """Get chat information"""
        
        params = {"chat_id": chat_id}
        response = await self._make_request("GET", bot_token, "getChat", params=params)
        
        chat = TelegramChat(
            chat_id=str(response["id"]),
            chat_type=response["type"],
            title=response.get("title", ""),
            username=response.get("username"),
            description=response.get("description"),
            invite_link=response.get("invite_link"),
            member_count=response.get("member_count", 0),
            pinned_message_id=str(response.get("pinned_message", {}).get("message_id", "")) if response.get("pinned_message") else None
        )
        
        return chat
        
    async def get_chat_member_count(self, bot_token: str, chat_id: str) -> int:
        """Get the number of members in a chat"""
        
        params = {"chat_id": chat_id}
        response = await self._make_request("GET", bot_token, "getChatMemberCount", params=params)
        
        return int(response)
        
    async def get_chat_administrators(self, bot_token: str, chat_id: str) -> List[Dict[str, Any]]:
        """Get chat administrators"""
        
        params = {"chat_id": chat_id}
        response = await self._make_request("GET", bot_token, "getChatAdministrators", params=params)
        
        return response
        
    async def send_message(
        self,
        bot_token: str,
        chat_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
        disable_web_page_preview: bool = False,
        disable_notification: bool = False
    ) -> TelegramMessage:
        """Send a text message"""
        
        data = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification
        }
        
        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
            
        response = await self._make_request("POST", bot_token, "sendMessage", data=data)
        
        message = TelegramMessage(
            message_id=str(response["message_id"]),
            chat_id=str(response["chat"]["id"]),
            sender_id=str(response["from"]["id"]),
            sender_username=response["from"].get("username", ""),
            text=response["text"],
            date=datetime.fromtimestamp(response["date"])
        )
        
        logger.info(f"Sent Telegram message: {message.message_id}")
        return message
        
    async def send_photo(
        self,
        bot_token: str,
        chat_id: str,
        photo_url: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> TelegramMessage:
        """Send a photo"""
        
        data = {
            "chat_id": chat_id,
            "photo": photo_url
        }
        
        if caption:
            data["caption"] = caption
        if parse_mode:
            data["parse_mode"] = parse_mode
            
        response = await self._make_request("POST", bot_token, "sendPhoto", data=data)
        
        message = TelegramMessage(
            message_id=str(response["message_id"]),
            chat_id=str(response["chat"]["id"]),
            sender_id=str(response["from"]["id"]),
            sender_username=response["from"].get("username", ""),
            text=response.get("caption", ""),
            date=datetime.fromtimestamp(response["date"]),
            media_type="photo",
            media_url=response["photo"][-1]["file_id"] if response.get("photo") else None
        )
        
        logger.info(f"Sent Telegram photo: {message.message_id}")
        return message
        
    async def send_video(
        self,
        bot_token: str,
        chat_id: str,
        video_url: str,
        caption: Optional[str] = None,
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> TelegramMessage:
        """Send a video"""
        
        data = {
            "chat_id": chat_id,
            "video": video_url
        }
        
        if caption:
            data["caption"] = caption
        if duration:
            data["duration"] = duration
        if width:
            data["width"] = width
        if height:
            data["height"] = height
            
        response = await self._make_request("POST", bot_token, "sendVideo", data=data)
        
        message = TelegramMessage(
            message_id=str(response["message_id"]),
            chat_id=str(response["chat"]["id"]),
            sender_id=str(response["from"]["id"]),
            sender_username=response["from"].get("username", ""),
            text=response.get("caption", ""),
            date=datetime.fromtimestamp(response["date"]),
            media_type="video",
            media_url=response["video"]["file_id"] if response.get("video") else None
        )
        
        logger.info(f"Sent Telegram video: {message.message_id}")
        return message
        
    async def edit_message_text(
        self,
        bot_token: str,
        chat_id: str,
        message_id: str,
        text: str,
        parse_mode: Optional[str] = None
    ) -> TelegramMessage:
        """Edit a text message"""
        
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        
        if parse_mode:
            data["parse_mode"] = parse_mode
            
        response = await self._make_request("POST", bot_token, "editMessageText", data=data)
        
        message = TelegramMessage(
            message_id=str(response["message_id"]),
            chat_id=str(response["chat"]["id"]),
            sender_id=str(response["from"]["id"]),
            sender_username=response["from"].get("username", ""),
            text=response["text"],
            date=datetime.fromtimestamp(response["date"]),
            edit_date=datetime.fromtimestamp(response["edit_date"]) if response.get("edit_date") else None
        )
        
        return message
        
    async def delete_message(self, bot_token: str, chat_id: str, message_id: str) -> bool:
        """Delete a message"""
        
        data = {
            "chat_id": chat_id,
            "message_id": message_id
        }
        
        try:
            await self._make_request("POST", bot_token, "deleteMessage", data=data)
            logger.info(f"Deleted Telegram message: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete message {message_id}: {e}")
            return False
            
    async def forward_message(
        self,
        bot_token: str,
        chat_id: str,
        from_chat_id: str,
        message_id: str,
        disable_notification: bool = False
    ) -> TelegramMessage:
        """Forward a message"""
        
        data = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification
        }
        
        response = await self._make_request("POST", bot_token, "forwardMessage", data=data)
        
        message = TelegramMessage(
            message_id=str(response["message_id"]),
            chat_id=str(response["chat"]["id"]),
            sender_id=str(response["from"]["id"]),
            sender_username=response["from"].get("username", ""),
            text=response.get("text", ""),
            date=datetime.fromtimestamp(response["date"]),
            forward_from_chat_id=from_chat_id
        )
        
        logger.info(f"Forwarded Telegram message: {message.message_id}")
        return message
        
    async def pin_chat_message(
        self,
        bot_token: str,
        chat_id: str,
        message_id: str,
        disable_notification: bool = False
    ) -> bool:
        """Pin a message in a chat"""
        
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification
        }
        
        try:
            await self._make_request("POST", bot_token, "pinChatMessage", data=data)
            logger.info(f"Pinned message {message_id} in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pin message {message_id}: {e}")
            return False
            
    async def unpin_chat_message(self, bot_token: str, chat_id: str, message_id: Optional[str] = None) -> bool:
        """Unpin a message in a chat"""
        
        data = {"chat_id": chat_id}
        if message_id:
            data["message_id"] = message_id
            
        try:
            await self._make_request("POST", bot_token, "unpinChatMessage", data=data)
            logger.info(f"Unpinned message in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unpin message in chat {chat_id}: {e}")
            return False
            
    async def kick_chat_member(
        self,
        bot_token: str,
        chat_id: str,
        user_id: str,
        until_date: Optional[datetime] = None
    ) -> bool:
        """Kick a member from a chat"""
        
        data = {
            "chat_id": chat_id,
            "user_id": user_id
        }
        
        if until_date:
            data["until_date"] = int(until_date.timestamp())
            
        try:
            await self._make_request("POST", bot_token, "kickChatMember", data=data)
            logger.info(f"Kicked member {user_id} from chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to kick member {user_id}: {e}")
            return False
            
    async def unban_chat_member(self, bot_token: str, chat_id: str, user_id: str) -> bool:
        """Unban a member from a chat"""
        
        data = {
            "chat_id": chat_id,
            "user_id": user_id
        }
        
        try:
            await self._make_request("POST", bot_token, "unbanChatMember", data=data)
            logger.info(f"Unbanned member {user_id} from chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unban member {user_id}: {e}")
            return False
            
    async def set_webhook(
        self,
        bot_token: str,
        url: str,
        certificate: Optional[str] = None,
        ip_address: Optional[str] = None,
        max_connections: int = 40,
        allowed_updates: Optional[List[str]] = None
    ) -> bool:
        """Set webhook for receiving updates"""
        
        data = {
            "url": url,
            "max_connections": max_connections
        }
        
        if certificate:
            data["certificate"] = certificate
        if ip_address:
            data["ip_address"] = ip_address
        if allowed_updates:
            data["allowed_updates"] = allowed_updates
            
        try:
            await self._make_request("POST", bot_token, "setWebhook", data=data)
            logger.info(f"Set webhook: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            return False
            
    async def delete_webhook(self, bot_token: str) -> bool:
        """Delete webhook"""
        
        try:
            await self._make_request("POST", bot_token, "deleteWebhook")
            logger.info("Deleted webhook")
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return False
            
    async def get_updates(
        self,
        bot_token: str,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 0,
        allowed_updates: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get updates using long polling"""
        
        params = {
            "limit": min(limit, 100),
            "timeout": timeout
        }
        
        if offset:
            params["offset"] = offset
        if allowed_updates:
            params["allowed_updates"] = allowed_updates
            
        response = await self._make_request("GET", bot_token, "getUpdates", params=params)
        return response
        
    def add_webhook_handler(self, update_type: str, handler: Callable):
        """Add a webhook handler for specific update types"""
        if update_type not in self.webhook_handlers:
            self.webhook_handlers[update_type] = []
        self.webhook_handlers[update_type].append(handler)
        
    async def handle_webhook_update(self, update_data: Dict[str, Any]):
        """Handle incoming webhook update"""
        
        try:
            # Determine update type
            update_type = None
            if "message" in update_data:
                update_type = "message"
            elif "edited_message" in update_data:
                update_type = "edited_message"
            elif "channel_post" in update_data:
                update_type = "channel_post"
            elif "edited_channel_post" in update_data:
                update_type = "edited_channel_post"
            elif "inline_query" in update_data:
                update_type = "inline_query"
            elif "callback_query" in update_data:
                update_type = "callback_query"
                
            # Call handlers
            if update_type and update_type in self.webhook_handlers:
                for handler in self.webhook_handlers[update_type]:
                    try:
                        await handler(update_data[update_type])
                    except Exception as e:
                        logger.error(f"Error in webhook handler for {update_type}: {e}")
                        
        except Exception as e:
            logger.error(f"Error handling webhook update: {e}")
            
    async def start_polling(self, bot_token: str):
        """Start polling for updates"""
        
        self.polling_active = True
        logger.info("Started Telegram polling")
        
        while self.polling_active:
            try:
                updates = await self.get_updates(
                    bot_token,
                    offset=self.last_update_id + 1,
                    timeout=10
                )
                
                for update in updates:
                    self.last_update_id = update["update_id"]
                    await self.handle_webhook_update(update)
                    
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    def stop_polling(self):
        """Stop polling for updates"""
        self.polling_active = False
        logger.info("Stopped Telegram polling")
        
    async def get_channel_analytics(
        self,
        bot_token: str,
        channel_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> TelegramAnalytics:
        """Get analytics for a Telegram channel (custom implementation)"""
        
        try:
            # Get basic channel info
            chat = await self.get_chat(bot_token, channel_id)
            member_count = await self.get_chat_member_count(bot_token, channel_id)
            
            # Note: Telegram Bot API doesn't provide detailed analytics
            # This would require additional tools or services for comprehensive analytics
            
            analytics = TelegramAnalytics(
                chat_id=channel_id,
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                },
                subscriber_growth=member_count - chat.member_count if chat.member_count else 0,
                active_users=member_count
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get channel analytics for {channel_id}: {e}")
            return TelegramAnalytics(
                chat_id=channel_id,
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                }
            )
            
    def verify_webhook_signature(self, data: bytes, signature: str, bot_token: str) -> bool:
        """Verify webhook signature for security"""
        
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        expected_signature = hmac.new(secret_key, data, hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)