"""
Push Notification Service
Handles push notifications via Firebase Cloud Messaging (FCM)
"""

import os
from typing import Optional, List, Dict, Any
import json


class PushNotificationService:
    """Send push notifications to mobile devices"""
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_PUSH_NOTIFICATIONS', 'true').lower() == 'true'
        self.firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH', './config/firebase-credentials.json')
        self.firebase_project_id = os.getenv('FIREBASE_PROJECT_ID', '')
        
        # In production, initialize Firebase Admin SDK
        # import firebase_admin
        # from firebase_admin import credentials, messaging
        # cred = credentials.Certificate(self.firebase_credentials_path)
        # firebase_admin.initialize_app(cred)
    
    async def send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ) -> bool:
        """
        Send push notification to a single device
        
        Args:
            device_token: FCM device token
            title: Notification title
            body: Notification body
            data: Additional data payload
            priority: Notification priority (normal, high)
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            print(f"Push notifications disabled. Would send: {title}")
            return False
        
        try:
            # In production:
            # from firebase_admin import messaging
            # message = messaging.Message(
            #     notification=messaging.Notification(
            #         title=title,
            #         body=body,
            #     ),
            #     data=data or {},
            #     token=device_token,
            #     android=messaging.AndroidConfig(
            #         priority=priority,
            #     ),
            # )
            # response = messaging.send(message)
            
            print(f"[PUSH] To: {device_token[:10]}... | Title: {title} | Body: {body}")
            return True
            
        except Exception as e:
            print(f"Error sending push notification: {e}")
            return False
    
    async def send_push_to_multiple(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """
        Send push notification to multiple devices
        
        Args:
            device_tokens: List of FCM device tokens
            title: Notification title
            body: Notification body
            data: Additional data payload
            
        Returns:
            Dict with success_count and failure_count
        """
        if not self.enabled:
            return {"success_count": 0, "failure_count": len(device_tokens)}
        
        success_count = 0
        failure_count = 0
        
        for token in device_tokens:
            success = await self.send_push_notification(token, title, body, data)
            if success:
                success_count += 1
            else:
                failure_count += 1
        
        return {
            "success_count": success_count,
            "failure_count": failure_count
        }
    
    async def send_topic_notification(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification to a topic (all subscribed devices)
        
        Args:
            topic: Topic name (e.g., 'ia2good-alerts', 'medcare-appointments')
            title: Notification title
            body: Notification body
            data: Additional data payload
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            print(f"Push notifications disabled. Would send to topic: {topic}")
            return False
        
        try:
            # In production:
            # from firebase_admin import messaging
            # message = messaging.Message(
            #     notification=messaging.Notification(
            #         title=title,
            #         body=body,
            #     ),
            #     data=data or {},
            #     topic=topic,
            # )
            # response = messaging.send(message)
            
            print(f"[PUSH TOPIC] Topic: {topic} | Title: {title}")
            return True
            
        except Exception as e:
            print(f"Error sending topic notification: {e}")
            return False
    
    async def subscribe_to_topic(self, device_tokens: List[str], topic: str) -> bool:
        """
        Subscribe devices to a topic
        
        Args:
            device_tokens: List of device tokens
            topic: Topic to subscribe to
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            # In production:
            # from firebase_admin import messaging
            # response = messaging.subscribe_to_topic(device_tokens, topic)
            
            print(f"[PUSH] Subscribed {len(device_tokens)} devices to topic: {topic}")
            return True
            
        except Exception as e:
            print(f"Error subscribing to topic: {e}")
            return False
