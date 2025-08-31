"""Telegram Platform Integration

Telegram Bot API integration for messaging and content sharing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""import asyncio
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


class TelegramPlatform(PlatformBase):
    """Telegram platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize Telegram platform"""        super().__init__(config)
        self.bot_token = self.config.credentials.get('bot_token')
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Telegram Bot Token"""        try:
            if not self.bot_token:
                logger.error("Telegram requires bot_token")
                return False
            
            # Test bot token by getting bot info
            session = await self._get_session()
            
            async with session.get(f"{self.api_base}/getMe") as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('ok'):
                        bot_info = result.get('result', {})
                        self.config.credentials['bot_id'] = bot_info.get('id')
                        self.config.credentials['bot_username'] = bot_info.get('username')
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info(f"Telegram authentication successful for bot: {bot_info.get('username')}")
                        return True
                    else:
                        logger.error("Telegram bot token validation failed")
                        return False
                else:
                    logger.error("Telegram authentication request failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Telegram authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Telegram token (not applicable for bot tokens)"""        return await self.authenticate()
    
    async def _make_request(self, method: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make request to Telegram Bot API"""        try:
            session = await self._get_session()
            
            url = f"{self.api_base}/{method}"
            
            async with session.post(url, **kwargs) as response:
                if response.status == 429:
                    # Telegram rate limiting
                    retry_after = int(response.headers.get('retry-after', 1))
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, **kwargs)
                
                elif response.status == 200:
                    result = await response.json()
                    if result.get('ok'):
                        return result
                    else:
                        error_desc = result.get('description', 'Unknown error')
                        logger.error(f"Telegram API error: {error_desc}")
                        self.increment_error_count()
                        return None
                
                else:
                    error_text = await response.text()
                    logger.error(f"Telegram API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Telegram request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Send message/media to Telegram chat"""        try:
            chat_id = metadata.tags[0] if metadata.tags else None
            if not chat_id:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Telegram requires chat_id in metadata.tags"
                )
            
            # Prepare message based on content type
            if content_path and not content_path.startswith('http'):
                # Local file upload
                if content_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    # Photo
                    result = await self._send_photo(chat_id, content_path, metadata)
                elif content_path.lower().endswith(('.mp4', '.avi', '.mov')):
                    # Video
                    result = await self._send_video(chat_id, content_path, metadata)
                elif content_path.lower().endswith(('.mp3', '.wav', '.ogg')):
                    # Audio
                    result = await self._send_audio(chat_id, content_path, metadata)
                else:
                    # Document
                    result = await self._send_document(chat_id, content_path, metadata)
            elif content_path and content_path.startswith('http'):
                # URL - send as text with URL
                text = f"{metadata.title}\n{metadata.description or ''}\n{content_path}".strip()
                result = await self._send_message(chat_id, text)
            else:
                # Text only
                text = f"{metadata.title}\n{metadata.description or ''}".strip()
                result = await self._send_message(chat_id, text)
            
            if result and result.get('result'):
                message = result['result']
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=str(message.get('message_id')),
                    url=f"https://t.me/{self.config.credentials.get('bot_username', 'bot')}/{message.get('message_id')}",
                    metadata={
                        'chat_id': chat_id,
                        'message_id': message.get('message_id'),
                        'date': message.get('date'),
                        'message_type': 'photo' if 'photo' in message else 'video' if 'video' in message else 'text'
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Telegram message sending failed"
                )
                
        except Exception as e:
            logger.error(f"Telegram upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _send_message(self, chat_id: str, text: str) -> Optional[Dict[str, Any]]:
        """Send text message"""        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        return await self._make_request('sendMessage', json=data)
    
    async def _send_photo(self, chat_id: str, photo_path: str, metadata: ContentMetadata) -> Optional[Dict[str, Any]]:
        """Send photo message"""        caption = f"{metadata.title}\n{metadata.description or ''}".strip()[:1024]  # Telegram caption limit
        
        data = {
            'chat_id': chat_id,
            'photo': photo_path,  # For local files, would need multipart upload
            'caption': caption,
            'parse_mode': 'Markdown'
        }
        return await self._make_request('sendPhoto', json=data)
    
    async def _send_video(self, chat_id: str, video_path: str, metadata: ContentMetadata) -> Optional[Dict[str, Any]]:
        """Send video message"""        caption = f"{metadata.title}\n{metadata.description or ''}".strip()[:1024]
        
        data = {
            'chat_id': chat_id,
            'video': video_path,
            'caption': caption,
            'parse_mode': 'Markdown'
        }
        return await self._make_request('sendVideo', json=data)
    
    async def _send_audio(self, chat_id: str, audio_path: str, metadata: ContentMetadata) -> Optional[Dict[str, Any]]:
        """Send audio message"""        data = {
            'chat_id': chat_id,
            'audio': audio_path,
            'title': metadata.title,
            'caption': metadata.description or '',
            'parse_mode': 'Markdown'
        }
        return await self._make_request('sendAudio', json=data)
    
    async def _send_document(self, chat_id: str, document_path: str, metadata: ContentMetadata) -> Optional[Dict[str, Any]]:
        """Send document message"""        caption = f"{metadata.title}\n{metadata.description or ''}".strip()[:1024]
        
        data = {
            'chat_id': chat_id,
            'document': document_path,
            'caption': caption,
            'parse_mode': 'Markdown'
        }
        return await self._make_request('sendDocument', json=data)
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Telegram message analytics (limited)"""        try:
            # Telegram doesn't provide built-in analytics for messages
            # We can only get basic message info
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=0,  # Telegram doesn't track views for regular messages
                likes=0,  # No likes in Telegram
                shares=0,  # Telegram doesn't track shares
                comments=0,  # No comments system in Telegram
                metadata={
                    'note': 'Telegram does not provide message analytics. Only basic info available.',
                    'analytics_type': 'basic',
                    'message_id': content_id
                }
            )
                
        except Exception as e:
            logger.error(f"Telegram analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content in Telegram (not available via Bot API)"""        try:
            # Telegram Bot API doesn't provide search functionality
            logger.warning("Telegram Bot API doesn't support content search")
            return []
            
        except Exception as e:
            logger.error(f"Telegram search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's messages from Telegram (limited by Bot API)"""        try:
            # Telegram Bot API doesn't provide access to user's message history
            logger.warning("Telegram Bot API doesn't provide access to user message history")
            return []
            
        except Exception as e:
            logger.error(f"Error getting Telegram user content: {e}")
            return []
    
    async def delete_content(self, content_id: str, chat_id: str = None) -> bool:
        """Delete Telegram message"""        try:
            if not chat_id:
                logger.error("Telegram message deletion requires chat_id")
                return False
            
            data = {
                'chat_id': chat_id,
                'message_id': int(content_id)
            }
            
            result = await self._make_request('deleteMessage', json=data)
            
            if result and result.get('ok'):
                logger.info(f"Successfully deleted Telegram message {content_id}")
                return True
            else:
                logger.error("Failed to delete Telegram message")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting Telegram content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata, chat_id: str = None) -> bool:
        """Update Telegram message"""        try:
            if not chat_id:
                logger.error("Telegram message update requires chat_id")
                return False
            
            # Only text messages can be edited
            text = f"{metadata.title}\n{metadata.description or ''}".strip()
            
            data = {
                'chat_id': chat_id,
                'message_id': int(content_id),
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            result = await self._make_request('editMessageText', json=data)
            
            if result and result.get('ok'):
                logger.info(f"Successfully updated Telegram message {content_id}")
                return True
            else:
                logger.error("Failed to update Telegram message")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Telegram content: {e}")
            return False
    
    async def get_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get Telegram chat information"""        try:
            data = {'chat_id': chat_id}
            result = await self._make_request('getChat', json=data)
            
            if result and result.get('result'):
                chat = result['result']
                return {
                    'id': chat.get('id'),
                    'type': chat.get('type'),
                    'title': chat.get('title'),
                    'username': chat.get('username'),
                    'first_name': chat.get('first_name'),
                    'last_name': chat.get('last_name'),
                    'description': chat.get('description'),
                    'member_count': await self._get_chat_member_count(chat_id)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting chat info: {e}")
            return None
    
    async def _get_chat_member_count(self, chat_id: str) -> int:
        """Get chat member count"""        try:
            data = {'chat_id': chat_id}
            result = await self._make_request('getChatMemberCount', json=data)
            
            if result and result.get('result'):
                return result['result']
            
            return 0
            
        except Exception as e:
            logger.error(f"Error getting member count: {e}")
            return 0
    
    async def get_updates(self, offset: int = None) -> List[Dict[str, Any]]:
        """Get bot updates"""        try:
            data = {}
            if offset:
                data['offset'] = offset
            
            result = await self._make_request('getUpdates', json=data)
            
            if result and result.get('result'):
                return result['result']
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    async def send_poll(self, chat_id: str, question: str, options: List[str], 
                       is_anonymous: bool = True) -> Optional[str]:
        """Send poll to Telegram chat"""        try:
            data = {
                'chat_id': chat_id,
                'question': question,
                'options': json.dumps(options),
                'is_anonymous': is_anonymous
            }
            
            result = await self._make_request('sendPoll', json=data)
            
            if result and result.get('result'):
                message_id = result['result'].get('message_id')
                logger.info(f"Successfully sent poll to chat {chat_id}")
                return str(message_id)
            else:
                logger.error("Failed to send poll")
                return None
                
        except Exception as e:
            logger.error(f"Error sending poll: {e}")
            return None
    
    async def forward_message(self, from_chat_id: str, to_chat_id: str, message_id: int) -> Optional[str]:
        """Forward message between chats"""        try:
            data = {
                'chat_id': to_chat_id,
                'from_chat_id': from_chat_id,
                'message_id': message_id
            }
            
            result = await self._make_request('forwardMessage', json=data)
            
            if result and result.get('result'):
                new_message_id = result['result'].get('message_id')
                logger.info(f"Successfully forwarded message from {from_chat_id} to {to_chat_id}")
                return str(new_message_id)
            else:
                logger.error("Failed to forward message")
                return None
                
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            return None
    
    async def set_webhook(self, webhook_url: str) -> bool:
        """Set webhook for bot updates"""        try:
            data = {'url': webhook_url}
            result = await self._make_request('setWebhook', json=data)
            
            if result and result.get('ok'):
                logger.info(f"Successfully set webhook: {webhook_url}")
                return True
            else:
                logger.error("Failed to set webhook")
                return False
                
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    async def delete_webhook(self) -> bool:
        """Delete webhook"""        try:
            result = await self._make_request('deleteWebhook')
            
            if result and result.get('ok'):
                logger.info("Successfully deleted webhook")
                return True
            else:
                logger.error("Failed to delete webhook")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return False
    
    async def get_bot_commands(self) -> List[Dict[str, Any]]:
        """Get bot commands"""        try:
            result = await self._make_request('getMyCommands')
            
            if result and result.get('result'):
                return result['result']
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting bot commands: {e}")
            return []
    
    async def set_bot_commands(self, commands: List[Dict[str, str]]) -> bool:
        """Set bot commands"""        try:
            data = {'commands': json.dumps(commands)}
            result = await self._make_request('setMyCommands', json=data)
            
            if result and result.get('ok'):
                logger.info("Successfully set bot commands")
                return True
            else:
                logger.error("Failed to set bot commands")
                return False
                
        except Exception as e:
            logger.error(f"Error setting bot commands: {e}")
            return False
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
