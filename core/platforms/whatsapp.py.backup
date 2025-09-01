"""WhatsApp Business Platform Integration

WhatsApp Business API integration for messaging and business communication.

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


class WhatsAppPlatform(PlatformBase):
    """WhatsApp Business platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """Initialize WhatsApp Business platform"""
        super().__init__(config)
        self.api_base = "https://graph.facebook.com/v18.0"
        self.phone_number_id = self.config.credentials.get('phone_number_id')
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with WhatsApp Business API"""
        try:
            access_token = self.config.credentials.get('access_token')
            
            if access_token and self.phone_number_id:
                # Test token validity
                session = await self._get_session()
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.get(f"{self.api_base}/{self.phone_number_id}", headers=headers) as response:
                    if response.status == 200:
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("WhatsApp Business authentication successful")
                        return True
                    else:
                        logger.error("WhatsApp Business token validation failed")
                        return False
            else:
                logger.error("WhatsApp Business requires access_token and phone_number_id")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp Business authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh WhatsApp Business token"""
        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to WhatsApp Business API"""
        try:
            session = await self._get_session()
            
            # Add authentication headers
            headers = kwargs.get('headers', {})
            if self.config.credentials.get('access_token'):
                headers['Authorization'] = f'Bearer {self.config.credentials["access_token"]}'
            
            headers['Content-Type'] = 'application/json'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    logger.error("WhatsApp Business authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"WhatsApp Business API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"WhatsApp Business request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Send WhatsApp Business message"""
        try:
            recipient = metadata.tags[0] if metadata.tags else None
            if not recipient:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="WhatsApp requires recipient phone number in metadata.tags"
                )
            
            # Prepare message based on content type
            message_data = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "text",
                "text": {
                    "body": f"{metadata.title}\n{metadata.description or ''}".strip()
                }
            }
            
            if content_path:
                if content_path.startswith('http'):
                    # Media URL
                    if any(ext in content_path.lower() for ext in ['.jpg', '.jpeg', '.png']):
                        message_data["type"] = "image"
                        message_data["image"] = {"link": content_path}
                        if metadata.description:
                            message_data["image"]["caption"] = metadata.description
                    elif any(ext in content_path.lower() for ext in ['.mp4', '.3gp']):
                        message_data["type"] = "video"
                        message_data["video"] = {"link": content_path}
                        if metadata.description:
                            message_data["video"]["caption"] = metadata.description
                    elif any(ext in content_path.lower() for ext in ['.mp3', '.aac', '.amr']):
                        message_data["type"] = "audio"
                        message_data["audio"] = {"link": content_path}
            
            result = await self._make_request('POST', f'/{self.phone_number_id}/messages', json=message_data)
            
            if result and result.get('messages'):
                message_id = result['messages'][0].get('id')
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=message_id,
                    url=None,  # WhatsApp doesn't provide public URLs
                    metadata={
                        'recipient': recipient,
                        'message_id': message_id,
                        'message_type': message_data['type']
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="WhatsApp message sending failed"
                )
                
        except Exception as e:
            logger.error(f"WhatsApp upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get WhatsApp Business analytics"""
        try:
            # WhatsApp Business provides limited analytics
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=0,  # Not available
                likes=0,  # Not applicable
                shares=0,  # Not tracked
                comments=0,  # Not applicable for business messages
                metadata={
                    'note': 'WhatsApp Business provides limited analytics',
                    'delivery_status': 'unknown'  # Would need webhook to track
                }
            )
                
        except Exception as e:
            logger.error(f"WhatsApp analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content (not available in WhatsApp Business)"""
        logger.warning("WhatsApp Business doesn't support content search")
        return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user content (not available in WhatsApp Business)"""
        logger.warning("WhatsApp Business doesn't provide access to message history")
        return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content (not available in WhatsApp Business)"""
        logger.warning("WhatsApp Business doesn't support message deletion via API")
        return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update content (not available in WhatsApp Business)"""
        logger.warning("WhatsApp Business doesn't support message editing")
        return False
    
    async def send_template_message(self, recipient: str, template_name: str, 
                                  language_code: str = "en", parameters: List[str] = None) -> Optional[str]:
        """Send WhatsApp template message"""
        try:
            message_data = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language_code}
                }
            }
            
            if parameters:
                message_data["template"]["components"] = [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": param} for param in parameters]
                }]
            
            result = await self._make_request('POST', f'/{self.phone_number_id}/messages', json=message_data)
            
            if result and result.get('messages'):
                return result['messages'][0].get('id')
            
            return None
            
        except Exception as e:
            logger.error(f"Error sending template message: {e}")
            return None
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
