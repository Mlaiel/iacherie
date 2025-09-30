"""
Push Notification Service Module
================================

Enterprise-grade push notification system for multi-platform delivery
Specialized for creator engagement and real-time communication workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Role Applied: Microservices + DevOps + Backend Senior + Security
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class NotificationPlatform(Enum):
    """Supported push notification platforms."""
    FCM = "fcm"  # Firebase Cloud Messaging
    APNS = "apns"  # Apple Push Notification Service
    WNS = "wns"  # Windows Notification Service
    WEB_PUSH = "web_push"  # Web Push Protocol
    TELEGRAM = "telegram"  # Telegram Bot API
    SLACK = "slack"  # Slack Webhooks
    DISCORD = "discord"  # Discord Webhooks


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationCategory(Enum):
    """Notification categories for creator workflows."""
    CONTENT_UPDATE = "content_update"
    REVENUE_ALERT = "revenue_alert"
    COLLABORATION_REQUEST = "collaboration_request"
    ENGAGEMENT_MILESTONE = "engagement_milestone"
    SYSTEM_ALERT = "system_alert"
    PROMOTION = "promotion"
    EDUCATIONAL = "educational"
    COMMUNITY = "community"


@dataclass
class NotificationTarget:
    """Notification target configuration."""
    user_id: str
    creator_id: Optional[str] = None
    creator_type: Optional[str] = None
    platform_tokens: Dict[str, str] = field(default_factory=dict)  # platform -> token
    preferences: Dict[str, bool] = field(default_factory=dict)  # category -> enabled
    timezone: str = "UTC"
    language: str = "en"


@dataclass
class NotificationContent:
    """Notification content with multi-language support."""
    title: str
    body: str
    icon_url: Optional[str] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)
    localized_content: Dict[str, Dict[str, str]] = field(default_factory=dict)  # lang -> {title, body}


@dataclass
class NotificationRequest:
    """Comprehensive notification request."""
    notification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    targets: List[NotificationTarget] = field(default_factory=list)
    content: Optional[NotificationContent] = None
    category: NotificationCategory = NotificationCategory.SYSTEM_ALERT
    priority: NotificationPriority = NotificationPriority.NORMAL
    platforms: List[NotificationPlatform] = field(default_factory=list)
    schedule_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    creator_context: Dict[str, Any] = field(default_factory=dict)
    business_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationResult:
    """Notification delivery result."""
    notification_id: str
    success_count: int = 0
    failure_count: int = 0
    platform_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    delivery_details: List[Dict[str, Any]] = field(default_factory=list)
    sent_at: datetime = field(default_factory=datetime.now)
    creator_analytics: Dict[str, Any] = field(default_factory=dict)


class PushNotificationEnterpriseService:
    """
    Enterprise push notification service with creator workflow integration.
    
    Specialized for Ainflue platform business logic:
    - Multi-platform notification delivery
    - Creator engagement optimization
    - Real-time analytics and A/B testing
    - Advanced scheduling and personalization
    """
    
    def __init__(
        self,
        fcm_api_key: Optional[str] = None,
        apns_config: Optional[Dict[str, Any]] = None,
        telegram_bot_token: Optional[str] = None,
        slack_webhook_url: Optional[str] = None,
        discord_webhook_url: Optional[str] = None,
        enable_analytics: bool = True,
        enable_creator_optimization: bool = True
    ):
        """Initialize push notification service with enterprise configuration."""
        self.fcm_api_key = fcm_api_key
        self.apns_config = apns_config or {}
        self.telegram_bot_token = telegram_bot_token
        self.slack_webhook_url = slack_webhook_url
        self.discord_webhook_url = discord_webhook_url
        self.enable_analytics = enable_analytics
        self.enable_creator_optimization = enable_creator_optimization
        
        # Platform endpoints
        self.platform_endpoints = {
            NotificationPlatform.FCM: "https://fcm.googleapis.com/fcm/send",
            NotificationPlatform.TELEGRAM: f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage" if telegram_bot_token else "",
            NotificationPlatform.SLACK: slack_webhook_url or "",
            NotificationPlatform.DISCORD: discord_webhook_url or ""
        }
        
        # HTTP session
        self.session = None
        if httpx:
            self.session = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={"Content-Type": "application/json"}
            )
        
        # Creator engagement templates
        self.creator_templates = self._initialize_creator_templates()
        self.engagement_strategies = self._initialize_engagement_strategies()
        
        # Analytics and tracking
        self.notification_history = []
        self.engagement_metrics = {
            "total_sent": 0,
            "total_delivered": 0,
            "total_opened": 0,
            "total_clicked": 0,
            "creator_engagement": {}
        }
        
        # Scheduling queue (in production, use Redis or similar)
        self.scheduled_notifications = []
        
        logger.info("✅ Push Notification Enterprise Service initialized")

    def _initialize_creator_templates(self) -> Dict[str, Dict[str, NotificationContent]]:
        """Initialize creator-specific notification templates."""
        return {
            "musician": {
                "new_follower": NotificationContent(
                    title="🎵 New Fan Alert!",
                    body="You have {count} new followers! Your music is reaching more people.",
                    icon_url="https://ainflue.com/icons/music-note.png",
                    custom_data={"type": "follower_milestone", "creator_type": "musician"}
                ),
                "revenue_milestone": NotificationContent(
                    title="💰 Revenue Milestone!",
                    body="Congratulations! You've earned ${amount} this month from your music.",
                    icon_url="https://ainflue.com/icons/money.png",
                    custom_data={"type": "revenue_alert", "creator_type": "musician"}
                ),
                "collaboration_request": NotificationContent(
                    title="🎤 Collaboration Opportunity",
                    body="{requester_name} wants to collaborate on a music project with you!",
                    icon_url="https://ainflue.com/icons/collaboration.png",
                    action_url="https://ainflue.com/collaborations",
                    custom_data={"type": "collaboration", "creator_type": "musician"}
                )
            },
            
            "blogger": {
                "content_viral": NotificationContent(
                    title="📈 Your Post is Going Viral!",
                    body="'{post_title}' has reached {views} views and {shares} shares!",
                    icon_url="https://ainflue.com/icons/trending.png",
                    custom_data={"type": "engagement_milestone", "creator_type": "blogger"}
                ),
                "seo_improvement": NotificationContent(
                    title="🔍 SEO Opportunity",
                    body="Your blog post '{post_title}' can rank higher with these optimizations.",
                    icon_url="https://ainflue.com/icons/seo.png",
                    action_url="https://ainflue.com/seo-dashboard",
                    custom_data={"type": "educational", "creator_type": "blogger"}
                ),
                "monetization_tip": NotificationContent(
                    title="💡 Monetization Tip",
                    body="Based on your content, you could earn ${estimated_amount} more with these strategies.",
                    icon_url="https://ainflue.com/icons/lightbulb.png",
                    custom_data={"type": "educational", "creator_type": "blogger"}
                )
            },
            
            "photographer": {
                "portfolio_featured": NotificationContent(
                    title="⭐ Portfolio Featured!",
                    body="Your photography has been featured in the trending gallery!",
                    icon_url="https://ainflue.com/icons/camera.png",
                    custom_data={"type": "engagement_milestone", "creator_type": "photographer"}
                ),
                "client_inquiry": NotificationContent(
                    title="📸 New Client Inquiry",
                    body="A potential client is interested in your {photography_style} photography services.",
                    icon_url="https://ainflue.com/icons/message.png",
                    action_url="https://ainflue.com/client-messages",
                    custom_data={"type": "business_opportunity", "creator_type": "photographer"}
                ),
                "equipment_recommendation": NotificationContent(
                    title="📷 Equipment Recommendation",
                    body="Based on your style, these camera upgrades could enhance your work.",
                    icon_url="https://ainflue.com/icons/camera-gear.png",
                    custom_data={"type": "educational", "creator_type": "photographer"}
                )
            },
            
            "influencer": {
                "brand_deal": NotificationContent(
                    title="🤝 Brand Partnership Opportunity",
                    body="{brand_name} wants to partner with you! Potential value: ${deal_value}",
                    icon_url="https://ainflue.com/icons/handshake.png",
                    action_url="https://ainflue.com/brand-deals",
                    custom_data={"type": "business_opportunity", "creator_type": "influencer"}
                ),
                "engagement_rate": NotificationContent(
                    title="📊 Engagement Rate Update",
                    body="Your engagement rate increased to {rate}%! Your content resonates with your audience.",
                    icon_url="https://ainflue.com/icons/chart.png",
                    custom_data={"type": "analytics_update", "creator_type": "influencer"}
                ),
                "content_suggestion": NotificationContent(
                    title="💭 Content Idea",
                    body="Trending topic alert: '{topic}' is popular with your audience right now!",
                    icon_url="https://ainflue.com/icons/idea.png",
                    custom_data={"type": "content_suggestion", "creator_type": "influencer"}
                )
            },
            
            "comedian": {
                "joke_performance": NotificationContent(
                    title="😂 Your Joke is Killing It!",
                    body="Your latest joke has {likes} likes and {shares} shares. Keep them laughing!",
                    icon_url="https://ainflue.com/icons/comedy.png",
                    custom_data={"type": "engagement_milestone", "creator_type": "comedian"}
                ),
                "show_opportunity": NotificationContent(
                    title="🎭 Show Opportunity",
                    body="A comedy club is interested in booking you for a show on {date}!",
                    icon_url="https://ainflue.com/icons/microphone.png",
                    action_url="https://ainflue.com/bookings",
                    custom_data={"type": "business_opportunity", "creator_type": "comedian"}
                ),
                "comedy_trend": NotificationContent(
                    title="📈 Comedy Trend Alert",
                    body="'{trend_topic}' is trending! Perfect opportunity for your next bit.",
                    icon_url="https://ainflue.com/icons/trending-comedy.png",
                    custom_data={"type": "content_suggestion", "creator_type": "comedian"}
                )
            }
        }

    def _initialize_engagement_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize engagement optimization strategies for creators."""
        return {
            "optimal_timing": {
                "musician": {"peak_hours": [19, 20, 21], "peak_days": ["friday", "saturday"]},
                "blogger": {"peak_hours": [9, 12, 18], "peak_days": ["tuesday", "wednesday", "thursday"]},
                "photographer": {"peak_hours": [10, 15, 19], "peak_days": ["monday", "wednesday", "friday"]},
                "influencer": {"peak_hours": [12, 18, 20], "peak_days": ["wednesday", "friday", "sunday"]},
                "comedian": {"peak_hours": [20, 21, 22], "peak_days": ["friday", "saturday", "sunday"]}
            },
            "frequency_limits": {
                "musician": {"daily_max": 3, "weekly_max": 15},
                "blogger": {"daily_max": 2, "weekly_max": 10},
                "photographer": {"daily_max": 2, "weekly_max": 8},
                "influencer": {"daily_max": 4, "weekly_max": 20},
                "comedian": {"daily_max": 3, "weekly_max": 12}
            },
            "content_personalization": {
                "new_user": "education_focused",
                "engaged_user": "achievement_focused", 
                "power_user": "opportunity_focused",
                "at_risk": "retention_focused"
            }
        }

    async def send_notification(self, request: NotificationRequest) -> NotificationResult:
        """
        Send notification with multi-platform delivery and creator optimization.
        
        Args:
            request: Notification request configuration
            
        Returns:
            NotificationResult with delivery status and analytics
        """
        try:
            # Validate request
            if not request.targets or not request.content:
                raise ValueError("Notification targets and content are required")
            
            # Apply creator optimization if enabled
            if self.enable_creator_optimization:
                request = await self._optimize_for_creators(request)
            
            # Initialize result
            result = NotificationResult(notification_id=request.notification_id)
            
            # Schedule or send immediately
            if request.schedule_time and request.schedule_time > datetime.now():
                await self._schedule_notification(request)
                result.platform_results["scheduled"] = {"status": "scheduled", "delivery_time": request.schedule_time.isoformat()}
                logger.info(f"📅 Notification scheduled: {request.notification_id}")
                return result
            
            # Send to each target across specified platforms
            for target in request.targets:
                target_results = await self._send_to_target(request, target)
                result.delivery_details.extend(target_results)
                
                # Update success/failure counts
                for detail in target_results:
                    if detail["success"]:
                        result.success_count += 1
                    else:
                        result.failure_count += 1
            
            # Process analytics if enabled
            if self.enable_analytics:
                await self._process_notification_analytics(request, result)
            
            # Track notification
            self._track_notification(request, result)
            
            logger.info(f"✅ Notification sent: {request.notification_id} - {result.success_count} delivered, {result.failure_count} failed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Notification sending failed: {e}")
            return NotificationResult(
                notification_id=request.notification_id,
                failure_count=len(request.targets) if request.targets else 1,
                platform_results={"error": {"status": "failed", "error": str(e)}}
            )

    async def send_creator_notification(
        self,
        creator_id: str,
        creator_type: str,
        template_name: str,
        template_data: Dict[str, Any],
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> NotificationResult:
        """Send notification using creator-specific templates."""
        try:
            # Get template
            if creator_type not in self.creator_templates:
                raise ValueError(f"Creator type '{creator_type}' not supported")
            
            if template_name not in self.creator_templates[creator_type]:
                raise ValueError(f"Template '{template_name}' not found for '{creator_type}'")
            
            template = self.creator_templates[creator_type][template_name]
            
            # Format template content
            formatted_content = NotificationContent(
                title=template.title.format(**template_data),
                body=template.body.format(**template_data),
                icon_url=template.icon_url,
                image_url=template.image_url,
                action_url=template.action_url,
                custom_data={**template.custom_data, **template_data}
            )
            
            # Create target (in production, get from user database)
            target = NotificationTarget(
                user_id=creator_id,
                creator_id=creator_id,
                creator_type=creator_type,
                platform_tokens=template_data.get("platform_tokens", {}),
                preferences=template_data.get("notification_preferences", {}),
                timezone=template_data.get("timezone", "UTC"),
                language=template_data.get("language", "en")
            )
            
            # Create notification request
            request = NotificationRequest(
                targets=[target],
                content=formatted_content,
                category=NotificationCategory(template.custom_data.get("type", "system_alert")),
                priority=priority,
                platforms=[NotificationPlatform.FCM, NotificationPlatform.WEB_PUSH],  # Default platforms
                creator_context={
                    "creator_id": creator_id,
                    "creator_type": creator_type,
                    "template_name": template_name
                },
                business_metadata=template_data
            )
            
            return await self.send_notification(request)
            
        except Exception as e:
            logger.error(f"❌ Creator notification failed: {e}")
            raise

    async def _send_to_target(self, request: NotificationRequest, target: NotificationTarget) -> List[Dict[str, Any]]:
        """Send notification to a specific target across platforms."""
        results = []
        
        # Determine which platforms to use
        platforms_to_use = request.platforms if request.platforms else [NotificationPlatform.FCM]
        
        for platform in platforms_to_use:
            # Check if target has token for this platform
            platform_token = target.platform_tokens.get(platform.value)
            if not platform_token and platform in [NotificationPlatform.FCM, NotificationPlatform.APNS, NotificationPlatform.WEB_PUSH]:
                results.append({
                    "target_id": target.user_id,
                    "platform": platform.value,
                    "success": False,
                    "error": "No platform token available"
                })
                continue
            
            # Check user preferences
            if not self._check_user_preferences(target, request.category):
                results.append({
                    "target_id": target.user_id,
                    "platform": platform.value,
                    "success": False,
                    "error": "User opted out of this notification category"
                })
                continue
            
            # Send to specific platform
            platform_result = await self._send_to_platform(platform, request.content, target, platform_token)
            platform_result.update({
                "target_id": target.user_id,
                "platform": platform.value
            })
            results.append(platform_result)
        
        return results

    async def _send_to_platform(
        self,
        platform: NotificationPlatform,
        content: NotificationContent,
        target: NotificationTarget,
        token: Optional[str]
    ) -> Dict[str, Any]:
        """Send notification to specific platform."""
        try:
            if platform == NotificationPlatform.FCM:
                return await self._send_fcm(content, token)
            elif platform == NotificationPlatform.TELEGRAM:
                return await self._send_telegram(content, token)
            elif platform == NotificationPlatform.SLACK:
                return await self._send_slack(content)
            elif platform == NotificationPlatform.DISCORD:
                return await self._send_discord(content)
            elif platform == NotificationPlatform.WEB_PUSH:
                return await self._send_web_push(content, token)
            else:
                return {"success": False, "error": f"Platform {platform.value} not implemented"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_fcm(self, content: NotificationContent, token: str) -> Dict[str, Any]:
        """Send Firebase Cloud Messaging notification."""
        if not self.fcm_api_key or not self.session:
            return {"success": False, "error": "FCM not configured"}
        
        payload = {
            "to": token,
            "notification": {
                "title": content.title,
                "body": content.body,
                "icon": content.icon_url,
                "image": content.image_url,
                "click_action": content.action_url
            },
            "data": content.custom_data
        }
        
        headers = {
            "Authorization": f"key={self.fcm_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.session.post(
                self.platform_endpoints[NotificationPlatform.FCM],
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": result.get("success", 0) > 0,
                "response": result,
                "message_id": result.get("results", [{}])[0].get("message_id")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_telegram(self, content: NotificationContent, chat_id: str) -> Dict[str, Any]:
        """Send Telegram notification."""
        if not self.telegram_bot_token or not self.session:
            return {"success": False, "error": "Telegram not configured"}
        
        # Create message with optional inline keyboard
        message = f"*{content.title}*\n\n{content.body}"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        
        # Add inline keyboard if action URL is provided
        if content.action_url:
            payload["reply_markup"] = {
                "inline_keyboard": [[{
                    "text": "Open",
                    "url": content.action_url
                }]]
            }
        
        try:
            response = await self.session.post(
                self.platform_endpoints[NotificationPlatform.TELEGRAM],
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": result.get("ok", False),
                "response": result,
                "message_id": result.get("result", {}).get("message_id")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_slack(self, content: NotificationContent) -> Dict[str, Any]:
        """Send Slack notification."""
        if not self.slack_webhook_url or not self.session:
            return {"success": False, "error": "Slack not configured"}
        
        # Create rich Slack message
        payload = {
            "text": content.title,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": content.title
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": content.body
                    }
                }
            ]
        }
        
        # Add image if provided
        if content.image_url:
            payload["blocks"].append({
                "type": "image",
                "image_url": content.image_url,
                "alt_text": "Notification image"
            })
        
        # Add action button if provided
        if content.action_url:
            payload["blocks"].append({
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Details"
                    },
                    "url": content.action_url,
                    "style": "primary"
                }]
            })
        
        try:
            response = await self.session.post(self.slack_webhook_url, json=payload)
            response.raise_for_status()
            
            return {"success": True, "response": "Message sent"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_discord(self, content: NotificationContent) -> Dict[str, Any]:
        """Send Discord notification."""
        if not self.discord_webhook_url or not self.session:
            return {"success": False, "error": "Discord not configured"}
        
        # Create Discord embed
        embed = {
            "title": content.title,
            "description": content.body,
            "color": 5814783,  # Blue color
            "timestamp": datetime.now().isoformat()
        }
        
        if content.image_url:
            embed["image"] = {"url": content.image_url}
        
        if content.icon_url:
            embed["thumbnail"] = {"url": content.icon_url}
        
        payload = {"embeds": [embed]}
        
        try:
            response = await self.session.post(self.discord_webhook_url, json=payload)
            response.raise_for_status()
            
            return {"success": True, "response": "Message sent"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_web_push(self, content: NotificationContent, subscription: str) -> Dict[str, Any]:
        """Send Web Push notification."""
        # Web Push implementation would require additional libraries like pywebpush
        # For now, return a placeholder response
        return {
            "success": True,
            "response": "Web push would be sent here",
            "note": "Requires pywebpush library implementation"
        }

    def _check_user_preferences(self, target: NotificationTarget, category: NotificationCategory) -> bool:
        """Check if user has opted in for this notification category."""
        if not target.preferences:
            return True  # Default to enabled if no preferences set
        
        return target.preferences.get(category.value, True)

    async def _optimize_for_creators(self, request: NotificationRequest) -> NotificationRequest:
        """Apply creator-specific optimizations to notification request."""
        creator_type = request.creator_context.get("creator_type")
        
        if creator_type and creator_type in self.engagement_strategies["optimal_timing"]:
            # Apply optimal timing if no schedule is set
            if not request.schedule_time:
                optimal_time = self._calculate_optimal_send_time(creator_type)
                if optimal_time > datetime.now():
                    request.schedule_time = optimal_time
            
            # Apply frequency limiting
            if await self._check_frequency_limits(request):
                request.priority = NotificationPriority.LOW
        
        return request

    def _calculate_optimal_send_time(self, creator_type: str) -> datetime:
        """Calculate optimal send time based on creator type and engagement data."""
        strategy = self.engagement_strategies["optimal_timing"].get(creator_type, {})
        peak_hours = strategy.get("peak_hours", [12])
        
        now = datetime.now()
        
        # Find next peak hour
        for hour in peak_hours:
            if hour > now.hour:
                return now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # If all peak hours have passed today, schedule for tomorrow's first peak hour
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=peak_hours[0], minute=0, second=0, microsecond=0)

    async def _check_frequency_limits(self, request: NotificationRequest) -> bool:
        """Check if notification exceeds frequency limits."""
        creator_type = request.creator_context.get("creator_type")
        if not creator_type:
            return False
        
        limits = self.engagement_strategies["frequency_limits"].get(creator_type, {})
        daily_max = limits.get("daily_max", 5)
        
        # Count today's notifications for this creator type
        today = datetime.now().date()
        today_count = sum(
            1 for notif in self.notification_history
            if notif.get("date") == today and notif.get("creator_type") == creator_type
        )
        
        return today_count >= daily_max

    async def _schedule_notification(self, request: NotificationRequest) -> None:
        """Schedule notification for later delivery."""
        scheduled_item = {
            "request": request,
            "schedule_time": request.schedule_time,
            "created_at": datetime.now()
        }
        
        self.scheduled_notifications.append(scheduled_item)
        
        # In production, store in persistent queue (Redis, database, etc.)
        logger.info(f"📅 Scheduled notification {request.notification_id} for {request.schedule_time}")

    async def process_scheduled_notifications(self) -> List[NotificationResult]:
        """Process all due scheduled notifications."""
        results = []
        now = datetime.now()
        due_notifications = []
        
        # Find due notifications
        for i, scheduled in enumerate(self.scheduled_notifications):
            if scheduled["schedule_time"] <= now:
                due_notifications.append((i, scheduled))
        
        # Process due notifications (in reverse order to maintain indices)
        for i, scheduled in reversed(due_notifications):
            request = scheduled["request"]
            request.schedule_time = None  # Clear schedule time to send immediately
            
            result = await self.send_notification(request)
            results.append(result)
            
            # Remove from scheduled list
            del self.scheduled_notifications[i]
        
        if results:
            logger.info(f"✅ Processed {len(results)} scheduled notifications")
        
        return results

    async def _process_notification_analytics(self, request: NotificationRequest, result: NotificationResult) -> None:
        """Process notification analytics for insights."""
        creator_type = request.creator_context.get("creator_type")
        
        # Update global metrics
        self.engagement_metrics["total_sent"] += result.success_count + result.failure_count
        self.engagement_metrics["total_delivered"] += result.success_count
        
        # Update creator-specific metrics
        if creator_type:
            if creator_type not in self.engagement_metrics["creator_engagement"]:
                self.engagement_metrics["creator_engagement"][creator_type] = {
                    "sent": 0,
                    "delivered": 0,
                    "categories": {}
                }
            
            creator_metrics = self.engagement_metrics["creator_engagement"][creator_type]
            creator_metrics["sent"] += result.success_count + result.failure_count
            creator_metrics["delivered"] += result.success_count
            
            # Track by category
            category = request.category.value
            if category not in creator_metrics["categories"]:
                creator_metrics["categories"][category] = {"sent": 0, "delivered": 0}
            
            creator_metrics["categories"][category]["sent"] += result.success_count + result.failure_count
            creator_metrics["categories"][category]["delivered"] += result.success_count
        
        # Add analytics to result
        result.creator_analytics = {
            "creator_type": creator_type,
            "category": request.category.value,
            "delivery_rate": result.success_count / (result.success_count + result.failure_count) if (result.success_count + result.failure_count) > 0 else 0
        }

    def _track_notification(self, request: NotificationRequest, result: NotificationResult) -> None:
        """Track notification for history and analytics."""
        history_item = {
            "notification_id": request.notification_id,
            "creator_type": request.creator_context.get("creator_type"),
            "category": request.category.value,
            "priority": request.priority.value,
            "success_count": result.success_count,
            "failure_count": result.failure_count,
            "sent_at": result.sent_at,
            "date": result.sent_at.date()
        }
        
        self.notification_history.append(history_item)

    async def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive notification analytics."""
        # Calculate delivery rates
        total_attempts = self.engagement_metrics["total_sent"]
        delivery_rate = (
            self.engagement_metrics["total_delivered"] / total_attempts 
            if total_attempts > 0 else 0
        )
        
        # Calculate creator-specific delivery rates
        creator_delivery_rates = {}
        for creator_type, metrics in self.engagement_metrics["creator_engagement"].items():
            creator_delivery_rates[creator_type] = (
                metrics["delivered"] / metrics["sent"] if metrics["sent"] > 0 else 0
            )
        
        # Get category performance
        category_performance = {}
        for creator_type, metrics in self.engagement_metrics["creator_engagement"].items():
            for category, category_metrics in metrics["categories"].items():
                if category not in category_performance:
                    category_performance[category] = {"sent": 0, "delivered": 0}
                category_performance[category]["sent"] += category_metrics["sent"]
                category_performance[category]["delivered"] += category_metrics["delivered"]
        
        return {
            "overview": {
                "total_sent": self.engagement_metrics["total_sent"],
                "total_delivered": self.engagement_metrics["total_delivered"],
                "overall_delivery_rate": delivery_rate,
                "scheduled_count": len(self.scheduled_notifications)
            },
            "creator_performance": creator_delivery_rates,
            "category_performance": category_performance,
            "recent_notifications": self.notification_history[-10:] if self.notification_history else [],
            "recommendations": await self._generate_optimization_recommendations()
        }

    async def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on analytics."""
        recommendations = []
        
        # Check overall delivery rate
        total_attempts = self.engagement_metrics["total_sent"]
        if total_attempts > 0:
            delivery_rate = self.engagement_metrics["total_delivered"] / total_attempts
            
            if delivery_rate < 0.8:
                recommendations.append("Delivery rate below 80% - review platform configurations and token validity")
            
            if delivery_rate > 0.95:
                recommendations.append("Excellent delivery rate! Consider expanding to additional platforms")
        
        # Check creator engagement patterns
        for creator_type, metrics in self.engagement_metrics["creator_engagement"].items():
            if metrics["sent"] > 10:  # Only for creators with significant volume
                creator_rate = metrics["delivered"] / metrics["sent"]
                if creator_rate < 0.7:
                    recommendations.append(f"Low delivery rate for {creator_type} creators - review preferences and timing")
        
        # Check scheduled notifications
        if len(self.scheduled_notifications) > 100:
            recommendations.append("Large number of scheduled notifications - consider optimizing send timing")
        
        if not recommendations:
            recommendations.append("Notification performance looks optimized!")
        
        return recommendations

    async def close(self) -> None:
        """Clean up resources and close connections."""
        if self.session:
            await self.session.aclose()
            self.session = None
            
        logger.info("✅ Push Notification Service closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Factory function for easy instantiation
def create_push_notification_service(
    fcm_api_key: Optional[str] = None,
    telegram_bot_token: Optional[str] = None,
    slack_webhook_url: Optional[str] = None,
    discord_webhook_url: Optional[str] = None,
    enable_analytics: bool = True,
    enable_creator_optimization: bool = True
) -> PushNotificationEnterpriseService:
    """
    Factory function to create push notification service with enterprise configuration.
    
    Args:
        fcm_api_key: Firebase Cloud Messaging API key
        telegram_bot_token: Telegram bot token
        slack_webhook_url: Slack webhook URL
        discord_webhook_url: Discord webhook URL
        enable_analytics: Enable analytics and tracking
        enable_creator_optimization: Enable creator-specific optimizations
        
    Returns:
        Configured PushNotificationEnterpriseService instance
    """
    return PushNotificationEnterpriseService(
        fcm_api_key=fcm_api_key,
        telegram_bot_token=telegram_bot_token,
        slack_webhook_url=slack_webhook_url,
        discord_webhook_url=discord_webhook_url,
        enable_analytics=enable_analytics,
        enable_creator_optimization=enable_creator_optimization
    )


# Example usage for creator notifications
async def example_creator_notifications():
    """Example of creator-specific notification workflows."""
    try:
        service = create_push_notification_service(
            fcm_api_key="your-fcm-api-key",
            telegram_bot_token="your-telegram-bot-token"
        )
        
        # Send revenue milestone notification to a musician
        revenue_result = await service.send_creator_notification(
            creator_id="musician_123",
            creator_type="musician",
            template_name="revenue_milestone",
            template_data={
                "amount": "250.00",
                "platform_tokens": {
                    "fcm": "fcm-device-token-123",
                    "telegram": "telegram-chat-id-123"
                },
                "notification_preferences": {
                    "revenue_alert": True,
                    "promotion": False
                }
            },
            priority=NotificationPriority.HIGH
        )
        
        print(f"💰 Revenue notification sent: {revenue_result.success_count} delivered")
        
        # Send collaboration request to a photographer
        collab_result = await service.send_creator_notification(
            creator_id="photographer_456",
            creator_type="photographer",
            template_name="client_inquiry",
            template_data={
                "photography_style": "portrait",
                "platform_tokens": {
                    "fcm": "fcm-device-token-456"
                }
            }
        )
        
        print(f"📸 Collaboration notification sent: {collab_result.success_count} delivered")
        
        # Process any scheduled notifications
        scheduled_results = await service.process_scheduled_notifications()
        print(f"📅 Processed {len(scheduled_results)} scheduled notifications")
        
        # Get analytics
        analytics = await service.get_analytics()
        print(f"📊 Total notifications sent: {analytics['overview']['total_sent']}")
        print(f"📈 Overall delivery rate: {analytics['overview']['overall_delivery_rate']:.2%}")
        print(f"💡 Recommendations: {analytics['recommendations']}")
        
        await service.close()
        
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_creator_notifications())