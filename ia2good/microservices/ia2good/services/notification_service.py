"""
Real Notification Service for IA2Good Platform
Handles multi-channel notifications: Push, Email, SMS, In-App
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
import json
from jinja2 import Template

# Firebase Cloud Messaging (Push notifications)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️  Firebase not installed: pip install firebase-admin")

# SendGrid (Email)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("⚠️  SendGrid not installed: pip install sendgrid")

# Twilio (SMS)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️  Twilio not installed: pip install twilio")

from models.notification import (
    Notification,
    NotificationPreference,
    NotificationTemplate,
    NotificationLog,
    NotificationType,
    NotificationChannel,
    NotificationPriority
)


class NotificationService:
    """
    Real multi-channel notification service
    
    Features:
    - Push notifications (Firebase FCM)
    - Email notifications (SendGrid)
    - SMS notifications (Twilio)
    - In-app notifications (Database)
    - Template support with Jinja2
    - Delivery tracking
    - User preferences
    """
    
    def __init__(self):
        self.fcm_app = None
        self.sendgrid_client = None
        self.twilio_client = None
        
        self._init_firebase()
        self._init_sendgrid()
        self._init_twilio()
    
    def _init_firebase(self):
        """Initialize Firebase Cloud Messaging"""
        if not FIREBASE_AVAILABLE:
            return
        
        try:
            firebase_creds = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if firebase_creds and os.path.exists(firebase_creds):
                cred = credentials.Certificate(firebase_creds)
                self.fcm_app = firebase_admin.initialize_app(cred, name='ia2good')
                print("✅ Firebase FCM initialized")
            else:
                print("⚠️  FIREBASE_CREDENTIALS_PATH not set or file not found")
        except Exception as e:
            print(f"⚠️  Firebase initialization failed: {e}")
    
    def _init_sendgrid(self):
        """Initialize SendGrid email service"""
        if not SENDGRID_AVAILABLE:
            return
        
        api_key = os.getenv("SENDGRID_API_KEY")
        if api_key:
            self.sendgrid_client = SendGridAPIClient(api_key)
            print("✅ SendGrid initialized")
        else:
            print("⚠️  SENDGRID_API_KEY not set")
    
    def _init_twilio(self):
        """Initialize Twilio SMS service"""
        if not TWILIO_AVAILABLE:
            return
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if account_sid and auth_token:
            self.twilio_client = TwilioClient(account_sid, auth_token)
            print("✅ Twilio initialized")
        else:
            print("⚠️  TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not set")
    
    async def send_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        action_url: Optional[str] = None,
        channels: Optional[List[NotificationChannel]] = None,
        db = None
    ) -> Notification:
        """
        Send a notification through multiple channels
        
        Args:
            user_id: Recipient user ID
            notification_type: Type of notification
            title: Notification title
            body: Notification body
            data: Additional data payload
            priority: Notification priority
            entity_type: Related entity type
            entity_id: Related entity ID
            action_url: Deep link/URL
            channels: List of channels to send through
            db: Database session
            
        Returns:
            Notification object
        """
        
        # Get user preferences
        prefs = await self._get_user_preferences(user_id, db)
        
        if not prefs or not prefs.enabled:
            print(f"Notifications disabled for user {user_id}")
            return None
        
        # Check quiet hours
        if self._is_quiet_hours(prefs):
            print(f"User {user_id} in quiet hours, queueing for later delivery")
            # Queue notification for delivery after quiet hours end
            notification.scheduled_for = self._calculate_quiet_hours_end(prefs)
            if db:
                db.add(notification)
                db.commit()
            return notification
        
        # Determine channels based on user preferences
        if not channels:
            channels = self._determine_channels(notification_type, priority, prefs)
        
        # Create in-app notification
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            priority=priority,
            entity_type=entity_type,
            entity_id=entity_id,
            action_url=action_url,
            data=data or {},
            channels=[c.value for c in channels]
        )
        
        if db:
            db.add(notification)
            db.commit()
            db.refresh(notification)
        
        # Send through each channel
        results = []
        
        for channel in channels:
            try:
                if channel == NotificationChannel.PUSH:
                    result = await self._send_push(user_id, title, body, data, priority, prefs, db)
                    notification.push_sent = result.get('success', False)
                    notification.push_sent_at = datetime.utcnow() if result.get('success') else None
                    notification.push_delivery_status = result.get('status', 'failed')
                    results.append(('push', result))
                
                elif channel == NotificationChannel.EMAIL:
                    result = await self._send_email(user_id, title, body, data, prefs, db)
                    notification.email_sent = result.get('success', False)
                    notification.email_sent_at = datetime.utcnow() if result.get('success') else None
                    results.append(('email', result))
                
                elif channel == NotificationChannel.SMS:
                    result = await self._send_sms(user_id, title, body, prefs, db)
                    notification.sms_sent = result.get('success', False)
                    notification.sms_sent_at = datetime.utcnow() if result.get('success') else None
                    notification.sms_delivery_status = result.get('status', 'failed')
                    results.append(('sms', result))
            
            except Exception as e:
                print(f"Error sending {channel.value} notification: {e}")
                results.append((channel.value, {'success': False, 'error': str(e)}))
        
        if db:
            db.commit()
        
        return notification
    
    async def _send_push(
        self,
        user_id: UUID,
        title: str,
        body: str,
        data: Optional[Dict],
        priority: NotificationPriority,
        prefs: NotificationPreference,
        db
    ) -> Dict[str, Any]:
        """Send push notification via Firebase FCM"""
        
        if not self.fcm_app or not prefs.push_enabled:
            return {'success': False, 'status': 'disabled'}
        
        # Get device tokens
        device_tokens = prefs.device_tokens or []
        if not device_tokens:
            return {'success': False, 'status': 'no_tokens'}
        
        results = []
        
        for device in device_tokens:
            token = device.get('token')
            platform = device.get('platform', 'unknown')
            
            try:
                # Build FCM message
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data=data or {},
                    token=token,
                    android=messaging.AndroidConfig(
                        priority='high' if priority == NotificationPriority.URGENT else 'normal',
                        notification=messaging.AndroidNotification(
                            sound='default',
                            channel_id='ia2good_notifications'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        headers={'apns-priority': '10' if priority == NotificationPriority.URGENT else '5'},
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound='default',
                                badge=1
                            )
                        )
                    )
                )
                
                # Send message
                response = messaging.send(message, app=self.fcm_app)
                
                results.append({
                    'token': token[:10] + '...',
                    'platform': platform,
                    'success': True,
                    'message_id': response
                })
                
                # Log delivery
                if db:
                    log = NotificationLog(
                        channel=NotificationChannel.PUSH,
                        recipient=token[:20],
                        status='sent',
                        provider='FCM',
                        provider_message_id=response,
                        sent_at=datetime.utcnow()
                    )
                    db.add(log)
            
            except Exception as e:
                print(f"Error sending push to {token[:10]}: {e}")
                results.append({
                    'token': token[:10] + '...',
                    'platform': platform,
                    'success': False,
                    'error': str(e)
                })
        
        success_count = sum(1 for r in results if r.get('success'))
        
        return {
            'success': success_count > 0,
            'status': 'sent' if success_count > 0 else 'failed',
            'sent_count': success_count,
            'total_devices': len(device_tokens),
            'results': results
        }
    
    async def _send_email(
        self,
        user_id: UUID,
        title: str,
        body: str,
        data: Optional[Dict],
        prefs: NotificationPreference,
        db
    ) -> Dict[str, Any]:
        """Send email notification via SendGrid"""
        
        if not self.sendgrid_client or not prefs.email_enabled:
            return {'success': False, 'status': 'disabled'}
        
        if not prefs.email:
            return {'success': False, 'status': 'no_email'}
        
        try:
            # Build email
            from_email = Email(os.getenv("SENDGRID_FROM_EMAIL", "notifications@ia2good.com"))
            to_email = To(prefs.email)
            subject = title
            
            # HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9fafb; }}
                    .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🌍 IA2Good</h2>
                    </div>
                    <div class="content">
                        <h3>{title}</h3>
                        <p>{body}</p>
                        {f'<a href="{data.get("action_url")}" class="button">Voir les détails</a>' if data and data.get('action_url') else ''}
                    </div>
                    <div class="footer">
                        <p>Cette notification a été envoyée depuis IA2Good</p>
                        <p><a href="https://ia2good.com/preferences">Gérer mes préférences</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            content = Content("text/html", html_content)
            mail = Mail(from_email, to_email, subject, content)
            
            # Send email
            response = self.sendgrid_client.send(mail)
            
            # Log delivery
            if db:
                log = NotificationLog(
                    channel=NotificationChannel.EMAIL,
                    recipient=prefs.email,
                    status='sent',
                    provider='SendGrid',
                    provider_message_id=response.headers.get('X-Message-Id'),
                    sent_at=datetime.utcnow()
                )
                db.add(log)
            
            return {
                'success': True,
                'status': 'sent',
                'message_id': response.headers.get('X-Message-Id'),
                'status_code': response.status_code
            }
        
        except Exception as e:
            print(f"Error sending email to {prefs.email}: {e}")
            return {
                'success': False,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _send_sms(
        self,
        user_id: UUID,
        title: str,
        body: str,
        prefs: NotificationPreference,
        db
    ) -> Dict[str, Any]:
        """Send SMS notification via Twilio"""
        
        if not self.twilio_client or not prefs.sms_enabled:
            return {'success': False, 'status': 'disabled'}
        
        if not prefs.phone:
            return {'success': False, 'status': 'no_phone'}
        
        try:
            # Shorten message for SMS (160 chars)
            sms_body = f"{title}: {body}"
            if len(sms_body) > 160:
                sms_body = sms_body[:157] + "..."
            
            # Send SMS
            message = self.twilio_client.messages.create(
                body=sms_body,
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=prefs.phone
            )
            
            # Log delivery
            if db:
                log = NotificationLog(
                    channel=NotificationChannel.SMS,
                    recipient=prefs.phone,
                    status='sent',
                    provider='Twilio',
                    provider_message_id=message.sid,
                    sent_at=datetime.utcnow()
                )
                db.add(log)
            
            return {
                'success': True,
                'status': 'sent',
                'message_sid': message.sid,
                'price': message.price
            }
        
        except Exception as e:
            print(f"Error sending SMS to {prefs.phone}: {e}")
            return {
                'success': False,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _get_user_preferences(
        self,
        user_id: UUID,
        db
    ) -> Optional[NotificationPreference]:
        """Get user notification preferences"""
        
        if not db:
            return None
        
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        # Create default preferences if not exist
        if not prefs:
            prefs = NotificationPreference(
                user_id=user_id,
                enabled=True,
                in_app_enabled=True,
                push_enabled=True,
                email_enabled=True,
                sms_enabled=False
            )
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        
        return prefs
    
    def _is_quiet_hours(self, prefs: NotificationPreference) -> bool:
        """Check if user is in quiet hours (timezone-aware)"""
        
        if not prefs.quiet_hours_enabled:
            return False
        
        if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
            return False
        
        try:
            from datetime import time
            import pytz
            
            # Get user's timezone (default to UTC)
            tz = pytz.timezone(prefs.timezone or 'UTC')
            user_time = datetime.now(tz).time()
            
            # Parse quiet hours
            start = datetime.strptime(prefs.quiet_hours_start, "%H:%M").time()
            end = datetime.strptime(prefs.quiet_hours_end, "%H:%M").time()
            
            # Handle quiet hours spanning midnight
            if start <= end:
                return start <= user_time <= end
            else:
                return user_time >= start or user_time <= end
        
        except Exception as e:
            print(f"Error checking quiet hours: {e}")
            return False
    
    def _calculate_quiet_hours_end(self, prefs: NotificationPreference) -> datetime:
        """Calculate when quiet hours end (timezone-aware)"""
        
        try:
            import pytz
            from datetime import time, timedelta
            
            tz = pytz.timezone(prefs.timezone or 'UTC')
            now = datetime.now(tz)
            end_time = datetime.strptime(prefs.quiet_hours_end, "%H:%M").time()
            
            # Create datetime for today's quiet hours end
            end_datetime = datetime.combine(now.date(), end_time)
            end_datetime = tz.localize(end_datetime)
            
            # If end time has passed, schedule for tomorrow
            if end_datetime <= now:
                end_datetime += timedelta(days=1)
            
            return end_datetime.astimezone(pytz.UTC).replace(tzinfo=None)
        
        except Exception as e:
            print(f"Error calculating quiet hours end: {e}")
            # Default to 1 hour from now
            return datetime.utcnow() + timedelta(hours=1)
    
    def _determine_channels(
        self,
        notification_type: NotificationType,
        priority: NotificationPriority,
        prefs: NotificationPreference
    ) -> List[NotificationChannel]:
        """Determine which channels to use based on type, priority, and preferences"""
        
        channels = [NotificationChannel.IN_APP]  # Always create in-app notification
        
        # Check type-specific preferences
        type_prefs = prefs.type_preferences.get(notification_type.value, {})
        
        # Push notifications
        if prefs.push_enabled and type_prefs.get('push', True):
            channels.append(NotificationChannel.PUSH)
        
        # Email notifications
        if prefs.email_enabled and type_prefs.get('email', False):
            channels.append(NotificationChannel.EMAIL)
        
        # SMS notifications (only for urgent and if enabled)
        if priority == NotificationPriority.URGENT:
            if prefs.sms_enabled and type_prefs.get('sms', False):
                channels.append(NotificationChannel.SMS)
        
        return channels
    
    async def mark_as_read(
        self,
        notification_id: UUID,
        db
    ) -> bool:
        """Mark notification as read"""
        
        if not db:
            return False
        
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification:
            return False
        
        notification.read = True
        notification.read_at = datetime.utcnow()
        db.commit()
        
        return True
    
    async def mark_all_as_read(
        self,
        user_id: UUID,
        db
    ) -> int:
        """Mark all notifications as read for a user"""
        
        if not db:
            return 0
        
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).update({
            'read': True,
            'read_at': datetime.utcnow()
        })
        
        db.commit()
        return count
    
    async def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        db = None
    ) -> List[Notification]:
        """Get user notifications"""
        
        if not db:
            return []
        
        query = db.query(Notification).filter(
            Notification.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(Notification.read == False)
        
        notifications = query.order_by(
            Notification.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return notifications
    
    async def get_unread_count(
        self,
        user_id: UUID,
        db
    ) -> int:
        """Get count of unread notifications"""
        
        if not db:
            return 0
        
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).count()
        
        return count
    
    async def register_device_token(
        self,
        user_id: UUID,
        token: str,
        platform: str,
        db
    ) -> bool:
        """Register device token for push notifications"""
        
        if not db:
            return False
        
        prefs = await self._get_user_preferences(user_id, db)
        
        # Add or update device token
        device_tokens = prefs.device_tokens or []
        
        # Remove old token if exists
        device_tokens = [d for d in device_tokens if d.get('token') != token]
        
        # Add new token
        device_tokens.append({
            'token': token,
            'platform': platform,
            'added_at': datetime.utcnow().isoformat()
        })
        
        prefs.device_tokens = device_tokens
        db.commit()
        
        return True


# Singleton instance
notification_service = NotificationService()
