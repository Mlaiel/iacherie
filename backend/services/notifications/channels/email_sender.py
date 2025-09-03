"""Email Sender Service

Service layer for email notification delivery.
Integrates with the core notification infrastructure to provide 
a clean service interface for email notifications.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import from core notification system
try:
    from notifications.email import EmailNotifier
except ImportError:
    # Fallback for relative imports
    from ....notifications.email import EmailNotifier

logger = logging.getLogger(__name__)


class EmailSenderService:
    """
    Service layer for email notification management.
    
    Provides a clean interface for sending email notifications
    with business logic integration and service-level orchestration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize email sender service.
        
        Args:
            config: Optional configuration for email service
        """
        self.config = config or {}
        self._email_notifier = EmailNotifier(
            provider=self.config.get('provider', 'smtp')
        )
        logger.info("EmailSenderService initialized")
    
    async def send_notification(
        self,
        recipient: str,
        subject: str,
        content: str,
        template_id: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Send email notification through the service layer.
        
        Args:
            recipient: Email address of recipient
            subject: Email subject line
            content: Email content body
            template_id: Optional template identifier
            attachments: Optional list of attachments
            priority: Message priority level
            
        Returns:
            Dict with delivery status and metadata
        """
        try:
            # Prepare email data
            email_data = {
                "to": recipient,
                "subject": subject,
                "content": content,
                "template_id": template_id,
                "attachments": attachments or [],
                "priority": priority,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send through core notifier
            result = await self._email_notifier.send_notification(email_data)
            
            logger.info(f"Email sent successfully to {recipient}")
            return {
                "success": True,
                "recipient": recipient,
                "delivery_id": result.get("delivery_id"),
                "timestamp": email_data["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return {
                "success": False,
                "recipient": recipient,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def send_bulk_notifications(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send bulk email notifications.
        
        Args:
            recipients: List of email addresses
            subject: Email subject line
            content: Email content body
            template_id: Optional template identifier
            
        Returns:
            Dict with bulk delivery results
        """
        results = []
        for recipient in recipients:
            result = await self.send_notification(
                recipient=recipient,
                subject=subject,
                content=content,
                template_id=template_id
            )
            results.append(result)
        
        successful = len([r for r in results if r["success"]])
        failed = len(results) - successful
        
        return {
            "total": len(recipients),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get email service status."""
        return {
            "service": "EmailSenderService",
            "status": "active",
            "provider": self.config.get('provider', 'smtp'),
            "timestamp": datetime.utcnow().isoformat()
        }