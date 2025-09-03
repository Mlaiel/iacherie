"""SMS Sender Service

Service layer for SMS notification delivery.
Integrates with the core notification infrastructure to provide 
a clean service interface for SMS notifications.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import from core notification system
try:
    from notifications.sms import SMSNotifier, SMSMessage, SMSProvider
except ImportError:
    try:
        # Fallback for relative imports
        from ....notifications.sms import SMSNotifier, SMSMessage, SMSProvider
    except ImportError:
        # Mock for testing when dependencies are not available
        from enum import Enum
        
        class SMSProvider(Enum):
            TWILIO = "twilio"
            AWS_SNS = "aws_sns"
        
        class SMSMessage:
            def __init__(self, phone_number, message, priority, country_code, timestamp):
                self.phone_number = phone_number
                self.message = message
                self.priority = priority
                self.country_code = country_code
                self.timestamp = timestamp
        
        class SMSNotifier:
            def __init__(self, provider, config):
                self.provider = provider
                self.config = config
            async def send_sms(self, message):
                return {"delivery_id": "mock_sms_123"}

logger = logging.getLogger(__name__)


class SMSSenderService:
    """
    Service layer for SMS notification management.
    
    Provides a clean interface for sending SMS notifications
    with business logic integration and service-level orchestration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize SMS sender service.
        
        Args:
            config: Optional configuration for SMS service
        """
        self.config = config or {}
        self._sms_notifier = SMSNotifier(
            provider=self.config.get('provider', SMSProvider.TWILIO),
            config=self.config
        )
        logger.info("SMSSenderService initialized")
    
    async def send_notification(
        self,
        phone_number: str,
        message: str,
        priority: str = "normal",
        country_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS notification through the service layer.
        
        Args:
            phone_number: Recipient phone number
            message: SMS message content
            priority: Message priority level
            country_code: Optional country code for validation
            
        Returns:
            Dict with delivery status and metadata
        """
        try:
            # Create SMS message
            sms_message = SMSMessage(
                phone_number=phone_number,
                message=message,
                priority=priority,
                country_code=country_code,
                timestamp=datetime.utcnow()
            )
            
            # Send through core notifier
            result = await self._sms_notifier.send_sms(sms_message)
            
            logger.info(f"SMS sent successfully to {phone_number}")
            return {
                "success": True,
                "phone_number": phone_number,
                "delivery_id": result.get("delivery_id"),
                "provider": self.config.get('provider', 'twilio'),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return {
                "success": False,
                "phone_number": phone_number,
                "error": str(e),
                "provider": self.config.get('provider', 'twilio'),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def send_bulk_notifications(
        self,
        phone_numbers: List[str],
        message: str,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Send bulk SMS notifications.
        
        Args:
            phone_numbers: List of recipient phone numbers
            message: SMS message content
            priority: Message priority level
            
        Returns:
            Dict with bulk delivery results
        """
        results = []
        for phone_number in phone_numbers:
            result = await self.send_notification(
                phone_number=phone_number,
                message=message,
                priority=priority
            )
            results.append(result)
        
        successful = len([r for r in results if r["success"]])
        failed = len(results) - successful
        
        return {
            "total": len(phone_numbers),
            "successful": successful,
            "failed": failed,
            "provider": self.config.get('provider', 'twilio'),
            "results": results
        }
    
    async def send_verification_code(
        self,
        phone_number: str,
        code: str,
        template_name: str = "verification"
    ) -> Dict[str, Any]:
        """
        Send SMS verification code.
        
        Args:
            phone_number: Recipient phone number
            code: Verification code
            template_name: Template identifier for verification
            
        Returns:
            Dict with delivery status and metadata
        """
        # Format verification message
        message = f"Your verification code is: {code}. Do not share this code with anyone."
        
        return await self.send_notification(
            phone_number=phone_number,
            message=message,
            priority="high"
        )
    
    async def send_alert_notification(
        self,
        phone_number: str,
        alert_type: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send alert SMS notification.
        
        Args:
            phone_number: Recipient phone number
            alert_type: Type of alert (security, content, etc.)
            message: Alert message content
            
        Returns:
            Dict with delivery status and metadata
        """
        # Add alert prefix
        formatted_message = f"[ALERT - {alert_type.upper()}] {message}"
        
        return await self.send_notification(
            phone_number=phone_number,
            message=formatted_message,
            priority="urgent"
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get SMS service status."""
        return {
            "service": "SMSSenderService",
            "status": "active",
            "provider": self.config.get('provider', 'twilio'),
            "supported_providers": [provider.value for provider in SMSProvider],
            "timestamp": datetime.utcnow().isoformat()
        }