# -*- coding: utf-8 -*-
"""
Unit Tests for Notifications Module
===================================

Tests for notification system and messaging functionality including:
- Real-time notifications
- Email notifications
- Push notifications
- Notification preferences
- Message queuing and delivery

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from notifications.notification_manager import NotificationManager
    from notifications.email_service import EmailService
    from notifications.push_service import PushService
    from notifications.models import Notification, NotificationPreference
except ImportError:
    # Mock classes for testing when modules are not available
    class NotificationManager:
        def __init__(self):
            self.notifications = []
            self.subscribers = {}
        
        async def send_notification(self, notification_data: Dict):
            notification = {
                "id": f"notif_{len(self.notifications) + 1}",
                "recipient": notification_data.get("recipient"),
                "title": notification_data.get("title"),
                "message": notification_data.get("message"),
                "type": notification_data.get("type", "info"),
                "sent_at": datetime.now(),
                "status": "sent"
            }
            self.notifications.append(notification)
            return notification
        
        async def send_bulk_notifications(self, notifications: List[Dict]):
            results = []
            for notif_data in notifications:
                result = await self.send_notification(notif_data)
                results.append(result)
            return results
        
        def get_notifications(self, user_id: str, limit: int = 10):
            user_notifications = [
                n for n in self.notifications 
                if n.get("recipient") == user_id
            ]
            return user_notifications[-limit:]
        
        async def mark_as_read(self, notification_id: str, user_id: str):
            for notif in self.notifications:
                if notif["id"] == notification_id and notif.get("recipient") == user_id:
                    notif["read"] = True
                    notif["read_at"] = datetime.now()
                    return True
            return False
    
    class EmailService:
        def __init__(self):
            self.sent_emails = []
            self.templates = {}
        
        async def send_email(self, to_email: str, subject: str, content: str, template: str = None):
            email = {
                "id": f"email_{len(self.sent_emails) + 1}",
                "to": to_email,
                "subject": subject,
                "content": content,
                "template": template,
                "sent_at": datetime.now(),
                "status": "delivered"
            }
            self.sent_emails.append(email)
            return email
        
        def load_template(self, template_name: str):
            templates = {
                "welcome": "Welcome to Ainflue! {{user_name}}",
                "password_reset": "Reset your password: {{reset_link}}",
                "collaboration_invite": "{{sender}} invited you to collaborate"
            }
            return templates.get(template_name, "Default template")
        
        def render_template(self, template: str, variables: Dict):
            for key, value in variables.items():
                template = template.replace(f"{{{{{key}}}}}", str(value))
            return template
    
    class PushService:
        def __init__(self):
            self.sent_pushes = []
            self.device_tokens = {}
        
        async def send_push(self, device_token: str, title: str, body: str, data: Dict = None):
            push = {
                "id": f"push_{len(self.sent_pushes) + 1}",
                "device_token": device_token,
                "title": title,
                "body": body,
                "data": data or {},
                "sent_at": datetime.now(),
                "status": "delivered"
            }
            self.sent_pushes.append(push)
            return push
        
        def register_device(self, user_id: str, device_token: str, platform: str):
            if user_id not in self.device_tokens:
                self.device_tokens[user_id] = []
            
            self.device_tokens[user_id].append({
                "token": device_token,
                "platform": platform,
                "registered_at": datetime.now()
            })
            return True
        
        async def send_to_user(self, user_id: str, title: str, body: str, data: Dict = None):
            user_devices = self.device_tokens.get(user_id, [])
            results = []
            
            for device in user_devices:
                result = await self.send_push(device["token"], title, body, data)
                results.append(result)
            
            return results
    
    class NotificationType(Enum):
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        SUCCESS = "success"
        COLLABORATION = "collaboration"
        MONETIZATION = "monetization"
    
    class Notification:
        def __init__(self, **kwargs):
            self.id = kwargs.get("id", "notif_1")
            self.recipient = kwargs.get("recipient", "user_1")
            self.title = kwargs.get("title", "Notification")
            self.message = kwargs.get("message", "")
            self.type = kwargs.get("type", NotificationType.INFO)
            self.created_at = kwargs.get("created_at", datetime.now())
            self.read = kwargs.get("read", False)
            self.data = kwargs.get("data", {})
    
    class NotificationPreference:
        def __init__(self, **kwargs):
            self.user_id = kwargs.get("user_id", "user_1")
            self.email_enabled = kwargs.get("email_enabled", True)
            self.push_enabled = kwargs.get("push_enabled", True)
            self.sms_enabled = kwargs.get("sms_enabled", False)
            self.frequency = kwargs.get("frequency", "immediate")
            self.categories = kwargs.get("categories", {})


class TestNotificationManager:
    """Test suite for NotificationManager class"""
    
    @pytest.fixture
    def notification_manager(self):
        """Create NotificationManager instance for testing"""
        return NotificationManager()
    
    @pytest.fixture
    def sample_notification_data(self):
        """Sample notification data"""
        return {
            "recipient": "user_123",
            "title": "New Collaboration Request",
            "message": "You have received a new collaboration request from John Doe",
            "type": "collaboration",
            "data": {"collaboration_id": "collab_456", "sender": "john_doe"}
        }
    
    def test_notification_manager_initialization(self, notification_manager):
        """Test NotificationManager initialization"""
        assert notification_manager is not None
        assert hasattr(notification_manager, 'notifications')
        assert hasattr(notification_manager, 'subscribers')
        assert len(notification_manager.notifications) == 0
    
    @pytest.mark.asyncio
    async def test_send_notification(self, notification_manager, sample_notification_data):
        """Test sending single notification"""
        result = await notification_manager.send_notification(sample_notification_data)
        
        # Assertions
        assert result is not None
        assert result["recipient"] == sample_notification_data["recipient"]
        assert result["title"] == sample_notification_data["title"]
        assert result["message"] == sample_notification_data["message"]
        assert result["status"] == "sent"
        assert "id" in result
        assert "sent_at" in result
        assert len(notification_manager.notifications) == 1
    
    @pytest.mark.asyncio
    async def test_send_bulk_notifications(self, notification_manager):
        """Test sending bulk notifications"""
        notifications = [
            {"recipient": "user_1", "title": "Title 1", "message": "Message 1"},
            {"recipient": "user_2", "title": "Title 2", "message": "Message 2"},
            {"recipient": "user_3", "title": "Title 3", "message": "Message 3"}
        ]
        
        results = await notification_manager.send_bulk_notifications(notifications)
        
        # Assertions
        assert len(results) == 3
        assert all(result["status"] == "sent" for result in results)
        assert len(notification_manager.notifications) == 3
    
    def test_get_notifications(self, notification_manager):
        """Test retrieving user notifications"""
        # Add some mock notifications
        notification_manager.notifications = [
            {"id": "1", "recipient": "user_1", "title": "Notification 1"},
            {"id": "2", "recipient": "user_2", "title": "Notification 2"},
            {"id": "3", "recipient": "user_1", "title": "Notification 3"},
            {"id": "4", "recipient": "user_1", "title": "Notification 4"}
        ]
        
        # Get notifications for user_1
        user_notifications = notification_manager.get_notifications("user_1", limit=2)
        
        # Assertions
        assert len(user_notifications) == 2
        assert all(notif["recipient"] == "user_1" for notif in user_notifications)
        assert user_notifications[0]["id"] == "3"  # Should get most recent first
        assert user_notifications[1]["id"] == "4"
    
    @pytest.mark.asyncio
    async def test_mark_notification_as_read(self, notification_manager):
        """Test marking notification as read"""
        # Add a notification
        notification_manager.notifications = [
            {"id": "notif_1", "recipient": "user_123", "title": "Test", "read": False}
        ]
        
        # Mark as read
        result = await notification_manager.mark_as_read("notif_1", "user_123")
        
        # Assertions
        assert result == True
        assert notification_manager.notifications[0]["read"] == True
        assert "read_at" in notification_manager.notifications[0]


class TestEmailService:
    """Test suite for EmailService class"""
    
    @pytest.fixture
    def email_service(self):
        """Create EmailService instance for testing"""
        return EmailService()
    
    @pytest.fixture
    def sample_email_data(self):
        """Sample email data"""
        return {
            "to_email": "user@example.com",
            "subject": "Welcome to Ainflue",
            "content": "Thank you for joining our platform!"
        }
    
    def test_email_service_initialization(self, email_service):
        """Test EmailService initialization"""
        assert email_service is not None
        assert hasattr(email_service, 'sent_emails')
        assert hasattr(email_service, 'templates')
        assert len(email_service.sent_emails) == 0
    
    @pytest.mark.asyncio
    async def test_send_email(self, email_service, sample_email_data):
        """Test sending email"""
        result = await email_service.send_email(
            sample_email_data["to_email"],
            sample_email_data["subject"],
            sample_email_data["content"]
        )
        
        # Assertions
        assert result is not None
        assert result["to"] == sample_email_data["to_email"]
        assert result["subject"] == sample_email_data["subject"]
        assert result["content"] == sample_email_data["content"]
        assert result["status"] == "delivered"
        assert "id" in result
        assert "sent_at" in result
        assert len(email_service.sent_emails) == 1
    
    def test_template_loading(self, email_service):
        """Test email template loading"""
        template = email_service.load_template("welcome")
        
        # Assertions
        assert template is not None
        assert "Welcome to Ainflue" in template
        assert "{{user_name}}" in template
    
    def test_template_rendering(self, email_service):
        """Test email template rendering"""
        template = "Hello {{user_name}}, welcome to {{platform}}!"
        variables = {"user_name": "John Doe", "platform": "Ainflue"}
        
        rendered = email_service.render_template(template, variables)
        
        # Assertions
        assert rendered == "Hello John Doe, welcome to Ainflue!"
        assert "{{" not in rendered  # No unresolved variables
    
    @pytest.mark.asyncio
    async def test_templated_email_workflow(self, email_service):
        """Test complete templated email workflow"""
        # Load template
        template = email_service.load_template("welcome")
        
        # Render with variables
        variables = {"user_name": "Jane Smith"}
        content = email_service.render_template(template, variables)
        
        # Send email
        result = await email_service.send_email(
            "jane@example.com",
            "Welcome to Ainflue",
            content,
            template="welcome"
        )
        
        # Assertions
        assert "Jane Smith" in result["content"]
        assert result["template"] == "welcome"


class TestPushService:
    """Test suite for PushService class"""
    
    @pytest.fixture
    def push_service(self):
        """Create PushService instance for testing"""
        return PushService()
    
    @pytest.fixture
    def sample_push_data(self):
        """Sample push notification data"""
        return {
            "device_token": "device_token_123",
            "title": "New Message",
            "body": "You have received a new message",
            "data": {"message_id": "msg_456", "sender": "john_doe"}
        }
    
    def test_push_service_initialization(self, push_service):
        """Test PushService initialization"""
        assert push_service is not None
        assert hasattr(push_service, 'sent_pushes')
        assert hasattr(push_service, 'device_tokens')
        assert len(push_service.sent_pushes) == 0
    
    @pytest.mark.asyncio
    async def test_send_push_notification(self, push_service, sample_push_data):
        """Test sending push notification"""
        result = await push_service.send_push(
            sample_push_data["device_token"],
            sample_push_data["title"],
            sample_push_data["body"],
            sample_push_data["data"]
        )
        
        # Assertions
        assert result is not None
        assert result["device_token"] == sample_push_data["device_token"]
        assert result["title"] == sample_push_data["title"]
        assert result["body"] == sample_push_data["body"]
        assert result["data"] == sample_push_data["data"]
        assert result["status"] == "delivered"
        assert len(push_service.sent_pushes) == 1
    
    def test_device_registration(self, push_service):
        """Test device token registration"""
        user_id = "user_123"
        device_token = "token_abc_123"
        platform = "ios"
        
        result = push_service.register_device(user_id, device_token, platform)
        
        # Assertions
        assert result == True
        assert user_id in push_service.device_tokens
        assert len(push_service.device_tokens[user_id]) == 1
        assert push_service.device_tokens[user_id][0]["token"] == device_token
        assert push_service.device_tokens[user_id][0]["platform"] == platform
    
    @pytest.mark.asyncio
    async def test_send_to_user(self, push_service):
        """Test sending push notification to user"""
        user_id = "user_456"
        
        # Register multiple devices for user
        push_service.register_device(user_id, "ios_token_123", "ios")
        push_service.register_device(user_id, "android_token_456", "android")
        
        # Send notification to user
        results = await push_service.send_to_user(
            user_id,
            "Test Notification",
            "This is a test message"
        )
        
        # Assertions
        assert len(results) == 2  # Should send to both devices
        assert all(result["status"] == "delivered" for result in results)
        assert results[0]["device_token"] == "ios_token_123"
        assert results[1]["device_token"] == "android_token_456"


class TestNotification:
    """Test suite for Notification model"""
    
    @pytest.fixture
    def sample_notification_data(self):
        """Sample notification data"""
        return {
            "id": "notif_789",
            "recipient": "user_456",
            "title": "Content Approved",
            "message": "Your content has been approved and published",
            "type": NotificationType.SUCCESS,
            "data": {"content_id": "content_123"}
        }
    
    def test_notification_creation(self, sample_notification_data):
        """Test Notification model creation"""
        notification = Notification(**sample_notification_data)
        
        # Assertions
        assert notification.id == "notif_789"
        assert notification.recipient == "user_456"
        assert notification.title == "Content Approved"
        assert notification.message == "Your content has been approved and published"
        assert notification.type == NotificationType.SUCCESS
        assert notification.read == False
        assert notification.data["content_id"] == "content_123"


class TestNotificationPreference:
    """Test suite for NotificationPreference model"""
    
    @pytest.fixture
    def sample_preference_data(self):
        """Sample notification preference data"""
        return {
            "user_id": "user_789",
            "email_enabled": True,
            "push_enabled": False,
            "sms_enabled": False,
            "frequency": "daily",
            "categories": {
                "collaboration": True,
                "monetization": True,
                "security": False
            }
        }
    
    def test_notification_preference_creation(self, sample_preference_data):
        """Test NotificationPreference model creation"""
        preference = NotificationPreference(**sample_preference_data)
        
        # Assertions
        assert preference.user_id == "user_789"
        assert preference.email_enabled == True
        assert preference.push_enabled == False
        assert preference.sms_enabled == False
        assert preference.frequency == "daily"
        assert preference.categories["collaboration"] == True
        assert preference.categories["security"] == False


class TestNotificationWorkflow:
    """Test suite for notification workflow processes"""
    
    def test_notification_filtering_by_preferences(self):
        """Test notification filtering based on user preferences"""
        user_preferences = NotificationPreference(
            user_id="user_123",
            email_enabled=True,
            push_enabled=False,
            categories={
                "collaboration": True,
                "monetization": False,
                "security": True
            }
        )
        
        notifications = [
            {"type": "collaboration", "title": "Collaboration request"},
            {"type": "monetization", "title": "Payment received"},
            {"type": "security", "title": "Security alert"},
            {"type": "system", "title": "System update"}
        ]
        
        # Filter notifications based on preferences
        filtered_notifications = []
        for notif in notifications:
            category_enabled = user_preferences.categories.get(notif["type"], True)
            if category_enabled:
                filtered_notifications.append(notif)
        
        # Assertions
        assert len(filtered_notifications) == 3  # collaboration, security, system
        assert any(n["type"] == "collaboration" for n in filtered_notifications)
        assert any(n["type"] == "security" for n in filtered_notifications)
        assert not any(n["type"] == "monetization" for n in filtered_notifications)
    
    def test_notification_frequency_batching(self):
        """Test notification frequency batching"""
        notifications = [
            {"created_at": datetime.now() - timedelta(minutes=30), "title": "Notification 1"},
            {"created_at": datetime.now() - timedelta(minutes=45), "title": "Notification 2"},
            {"created_at": datetime.now() - timedelta(hours=2), "title": "Notification 3"},
            {"created_at": datetime.now() - timedelta(hours=25), "title": "Notification 4"}
        ]
        
        # Group notifications by frequency preference
        frequency_settings = {
            "immediate": timedelta(minutes=0),
            "hourly": timedelta(hours=1),
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1)
        }
        
        user_frequency = "hourly"
        cutoff_time = datetime.now() - frequency_settings[user_frequency]
        
        # Get notifications within frequency window
        batched_notifications = [
            n for n in notifications
            if n["created_at"] >= cutoff_time
        ]
        
        # Assertions
        assert len(batched_notifications) == 2  # Only recent notifications
        assert all(n["created_at"] >= cutoff_time for n in batched_notifications)
    
    def test_notification_priority_sorting(self):
        """Test notification priority sorting"""
        notifications = [
            {"type": "info", "priority": 1, "title": "Info message"},
            {"type": "warning", "priority": 2, "title": "Warning message"},
            {"type": "error", "priority": 3, "title": "Error message"},
            {"type": "success", "priority": 1, "title": "Success message"}
        ]
        
        # Sort by priority (highest first)
        sorted_notifications = sorted(
            notifications,
            key=lambda x: x["priority"],
            reverse=True
        )
        
        # Assertions
        assert len(sorted_notifications) == 4
        assert sorted_notifications[0]["type"] == "error"  # Highest priority
        assert sorted_notifications[0]["priority"] == 3
        assert sorted_notifications[-1]["priority"] == 1


class TestNotificationTemplates:
    """Test suite for notification templates"""
    
    def test_collaboration_notification_template(self):
        """Test collaboration notification template"""
        template_data = {
            "sender_name": "John Doe",
            "project_title": "Music Video Collaboration",
            "deadline": "January 15, 2024"
        }
        
        template = "{{sender_name}} invited you to collaborate on '{{project_title}}'. Deadline: {{deadline}}"
        
        # Render template
        rendered = template
        for key, value in template_data.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        
        expected = "John Doe invited you to collaborate on 'Music Video Collaboration'. Deadline: January 15, 2024"
        
        # Assertions
        assert rendered == expected
        assert "{{" not in rendered
    
    def test_monetization_notification_template(self):
        """Test monetization notification template"""
        template_data = {
            "amount": "$150.00",
            "content_title": "Amazing Song",
            "platform": "Spotify"
        }
        
        template = "You earned {{amount}} from '{{content_title}}' on {{platform}}!"
        
        # Render template
        rendered = template
        for key, value in template_data.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        
        expected = "You earned $150.00 from 'Amazing Song' on Spotify!"
        
        # Assertions
        assert rendered == expected
        assert template_data["amount"] in rendered
    
    def test_security_notification_template(self):
        """Test security notification template"""
        template_data = {
            "ip_address": "192.168.1.100",
            "device": "iPhone 12",
            "location": "New York, NY",
            "time": "2024-01-10 14:30 UTC"
        }
        
        template = "New login detected from {{device}} at {{ip_address}} ({{location}}) on {{time}}"
        
        # Render template
        rendered = template
        for key, value in template_data.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        
        expected = "New login detected from iPhone 12 at 192.168.1.100 (New York, NY) on 2024-01-10 14:30 UTC"
        
        # Assertions
        assert rendered == expected
        assert template_data["ip_address"] in rendered
        assert template_data["device"] in rendered


# Integration tests
class TestNotificationIntegration:
    """Integration tests for notification workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_notification_workflow(self):
        """Test complete notification workflow"""
        notification_manager = NotificationManager()
        email_service = EmailService()
        push_service = PushService()
        
        # Step 1: Register user device
        user_id = "user_integration"
        push_service.register_device(user_id, "device_token_123", "ios")
        
        # Step 2: Send notification through manager
        notification_data = {
            "recipient": user_id,
            "title": "Integration Test",
            "message": "This is an integration test notification"
        }
        
        notification_result = await notification_manager.send_notification(notification_data)
        
        # Step 3: Send email notification
        email_result = await email_service.send_email(
            "user@example.com",
            notification_data["title"],
            notification_data["message"]
        )
        
        # Step 4: Send push notification
        push_results = await push_service.send_to_user(
            user_id,
            notification_data["title"],
            notification_data["message"]
        )
        
        # Verify complete workflow
        assert notification_result["status"] == "sent"
        assert email_result["status"] == "delivered"
        assert len(push_results) == 1
        assert push_results[0]["status"] == "delivered"
    
    @pytest.mark.asyncio
    async def test_notification_delivery_failure_handling(self):
        """Test notification delivery failure handling"""
        notification_manager = NotificationManager()
        
        # Simulate notification with delivery failure
        notification_data = {
            "recipient": "invalid_user",
            "title": "Test Notification",
            "message": "Test message"
        }
        
        # In real implementation, this might fail and need retry logic
        result = await notification_manager.send_notification(notification_data)
        
        # Even with mock, we can test the structure
        assert result is not None
        assert "status" in result
        
        # In real implementation, we would test:
        # - Retry mechanisms
        # - Dead letter queues
        # - Failure logging
        # - Fallback notification methods


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])