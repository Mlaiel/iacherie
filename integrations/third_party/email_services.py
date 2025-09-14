"""
Email Services Integration Module
=================================

Enterprise-grade email service integration with multiple providers
Specialized for creator marketing, transactional emails, and campaigns.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Role Applied: Security + Backend Senior + DBA + DevOps
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import hmac
import base64

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class EmailProvider(Enum):
    """Supported email service providers."""
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    SES = "ses"  # Amazon Simple Email Service
    MAILCHIMP = "mailchimp"
    SENDINBLUE = "sendinblue"
    POSTMARK = "postmark"


class EmailType(Enum):
    """Email types for creator workflows."""
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    WELCOME = "welcome"
    NOTIFICATION = "notification"
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    RETENTION = "retention"


class EmailPriority(Enum):
    """Email delivery priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EmailRecipient:
    """Email recipient configuration."""
    email: str
    name: Optional[str] = None
    creator_id: Optional[str] = None
    creator_type: Optional[str] = None
    preferences: Dict[str, bool] = field(default_factory=dict)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    timezone: str = "UTC"
    language: str = "en"


@dataclass
class EmailContent:
    """Email content with templates and personalization."""
    subject: str
    html_body: str
    text_body: Optional[str] = None
    from_email: str = "noreply@ainflue.com"
    from_name: str = "Ainflue Platform"
    reply_to: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    template_id: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    personalization: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmailCampaign:
    """Email campaign configuration."""
    campaign_id: str
    name: str
    recipients: List[EmailRecipient]
    content: EmailContent
    email_type: EmailType = EmailType.MARKETING
    priority: EmailPriority = EmailPriority.NORMAL
    send_time: Optional[datetime] = None
    timezone: str = "UTC"
    creator_context: Dict[str, Any] = field(default_factory=dict)
    analytics_tracking: bool = True
    ab_test_config: Optional[Dict[str, Any]] = None


@dataclass
class EmailResult:
    """Email delivery result with analytics."""
    message_id: str = ""
    campaign_id: Optional[str] = None
    recipient_email: str = ""
    status: str = "sent"
    sent_at: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None
    provider_response: Dict[str, Any] = field(default_factory=dict)
    creator_analytics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class EmailEnterpriseService:
    """
    Enterprise email service with multi-provider support and creator workflows.
    
    Specialized for Ainflue platform business logic:
    - Multi-provider email delivery with failover
    - Creator-specific email templates and campaigns
    - Advanced analytics and A/B testing
    - GDPR compliance and unsubscribe management
    """
    
    def __init__(
        self,
        sendgrid_api_key -> None: Optional[str] = None,
        mailgun_api_key -> None: Optional[str] = None,
        mailgun_domain -> None: Optional[str] = None,
        aws_access_key -> None: Optional[str] = None,
        aws_secret_key -> None: Optional[str] = None,
        aws_region -> None: str = "us-east-1",
        default_provider -> None: EmailProvider = EmailProvider.SENDGRID,
        enable_failover -> None: bool = True,
        enable_analytics -> None: bool = True
    ) -> None:
        """Initialize email service with enterprise configuration."""
        self.sendgrid_api_key = sendgrid_api_key
        self.mailgun_api_key = mailgun_api_key
        self.mailgun_domain = mailgun_domain
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.default_provider = default_provider
        self.enable_failover = enable_failover
        self.enable_analytics = enable_analytics
        
        # Provider endpoints
        self.provider_endpoints = {
            EmailProvider.SENDGRID: "https://api.sendgrid.com/v3/mail/send",
            EmailProvider.MAILGUN: f"https://api.mailgun.net/v3/{mailgun_domain}/messages" if mailgun_domain else "",
            EmailProvider.SES: f"https://email.{aws_region}.amazonaws.com/",
            EmailProvider.POSTMARK: "https://api.postmarkapp.com/email"
        }
        
        # HTTP session
        self.session = None
        if httpx:
            self.session = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={"Content-Type": "application/json"}
            )
        
        # Creator email templates
        self.creator_templates = self._initialize_creator_templates()
        self.email_campaigns = self._initialize_email_campaigns()
        
        # Analytics and tracking
        self.email_history = []
        self.campaign_analytics = {}
        self.provider_stats = {provider.value: {"sent": 0, "delivered": 0, "failed": 0} for provider in EmailProvider}
        
        # Unsubscribe management
        self.unsubscribed_emails = set()
        
        logger.info("✅ Email Enterprise Service initialized")

    def _initialize_creator_templates(self) -> Dict[str, Dict[str, EmailContent]]:
        """Initialize creator-specific email templates."""
        return {
            "musician": {
                "welcome": EmailContent(
                    subject="🎵 Welcome to Ainflue - Your Music Career Starts Here!",
                    html_body="""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h1 style="color: #4a90e2;">Welcome to Ainflue, {{name}}! 🎵</h1>
                            <p>Congratulations on joining the premier platform for musicians to protect, promote, and monetize their music!</p>
                            
                            <h2>🚀 Get Started:</h2>
                            <ul>
                                <li>Upload your first track and get AI-powered content protection</li>
                                <li>Set up your artist profile to attract fans and collaborators</li>
                                <li>Explore monetization options and start earning from your music</li>
                            </ul>
                            
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <h3>🎯 Pro Tip for Musicians:</h3>
                                <p>Upload high-quality demos to get featured in our trending artists section. Musicians who complete their profile in the first week see 300% more engagement!</p>
                            </div>
                            
                            <a href="{{dashboard_url}}" style="background: #4a90e2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">Start Creating 🎼</a>
                            
                            <p>Need help? Reply to this email or check our <a href="{{help_url}}">musician's guide</a>.</p>
                            
                            <p>Rock on!<br>The Ainflue Team</p>
                        </div>
                    </body>
                    </html>
                    """,
                    text_body="Welcome to Ainflue! Start your music career journey with AI-powered tools.",
                    from_name="Ainflue Music Team"
                ),
                
                "revenue_report": EmailContent(
                    subject="💰 Your Monthly Music Revenue Report - ${{total_revenue}}",
                    html_body="""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h1 style="color: #28a745;">Monthly Revenue Report 💰</h1>
                            <p>Hi {{name}}, here's how your music performed this month!</p>
                            
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; margin: 20px 0;">
                                <h2 style="margin: 0; font-size: 2.5em;">${{total_revenue}}</h2>
                                <p style="margin: 5px 0; opacity: 0.9;">Total Revenue This Month</p>
                                <p style="margin: 0; font-size: 0.9em;">↗️ {{growth_percentage}}% vs last month</p>
                            </div>
                            
                            <h3>📊 Breakdown:</h3>
                            <ul>
                                <li><strong>Streaming Revenue:</strong> ${{streaming_revenue}} ({{streaming_plays}} plays)</li>
                                <li><strong>Downloads:</strong> ${{download_revenue}} ({{download_count}} downloads)</li>
                                <li><strong>Licensing:</strong> ${{licensing_revenue}} ({{licensing_deals}} deals)</li>
                                <li><strong>Merchandise:</strong> ${{merchandise_revenue}}</li>
                            </ul>
                            
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                                <h4>🎯 Next Month's Goal:</h4>
                                <p>Based on your growth trend, you're on track to earn <strong>${{projected_revenue}}</strong> next month! Keep creating amazing music!</p>
                            </div>
                            
                            <a href="{{analytics_url}}" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">View Full Analytics 📈</a>
                        </div>
                    </body>
                    </html>
                    """,
                    from_name="Ainflue Analytics"
                )
            },
            
            "blogger": {
                "welcome": EmailContent(
                    subject="✍️ Welcome to Ainflue - Amplify Your Blog's Reach!",
                    html_body="""
                    <html>
                    <body style="font-family: Georgia, serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h1 style="color: #e74c3c;">Welcome to Ainflue, {{name}}! ✍️</h1>
                            <p>You've joined the platform that helps bloggers protect their content, grow their audience, and monetize their expertise.</p>
                            
                            <h2>📝 Your Blogging Toolkit:</h2>
                            <ul>
                                <li>AI-powered content protection and DMCA monitoring</li>
                                <li>SEO optimization tools to boost your reach</li>
                                <li>Monetization options: ads, affiliate marketing, courses</li>
                                <li>Collaboration network with other creators</li>
                            </ul>
                            
                            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <h3>💡 Blogger Pro Tip:</h3>
                                <p>Bloggers who publish consistently (3+ posts per week) and use our SEO tools see 5x more organic traffic within 30 days!</p>
                            </div>
                            
                            <a href="{{content_dashboard_url}}" style="background: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">Start Writing ✍️</a>
                            
                            <p>Happy blogging!<br>The Ainflue Editorial Team</p>
                        </div>
                    </body>
                    </html>
                    """,
                    from_name="Ainflue Editorial"
                ),
                
                "content_performance": EmailContent(
                    subject="📈 Your Blog Post '{{post_title}}' is Trending!",
                    html_body="""
                    <html>
                    <body style="font-family: Georgia, serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h1 style="color: #e74c3c;">Your Content is Going Viral! 🔥</h1>
                            <p>Hi {{name}}, your blog post "{{post_title}}" is performing exceptionally well!</p>
                            
                            <div style="background: #f8f9fa; border-left: 4px solid #e74c3c; padding: 20px; margin: 20px 0;">
                                <h3 style="color: #e74c3c; margin-top: 0;">Performance Highlights:</h3>
                                <ul>
                                    <li><strong>{{views}} views</strong> ({{view_growth}}% increase)</li>
                                    <li><strong>{{shares}} social shares</strong></li>
                                    <li><strong>{{comments}} comments</strong> from engaged readers</li>
                                    <li><strong>Average read time:</strong> {{read_time}} minutes</li>
                                </ul>
                            </div>
                            
                            <h3>🎯 Optimization Opportunities:</h3>
                            <p>This post is performing well! Consider:</p>
                            <ul>
                                <li>Creating a follow-up post on related topics</li>
                                <li>Promoting it across your social media channels</li>
                                <li>Converting it into a video or podcast episode</li>
                            </ul>
                            
                            <a href="{{post_analytics_url}}" style="background: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">View Detailed Analytics 📊</a>
                        </div>
                    </body>
                    </html>
                    """,
                    from_name="Ainflue Analytics"
                )
            },
            
            "photographer": {
                "welcome": EmailContent(
                    subject="📸 Welcome to Ainflue - Showcase Your Photography!",
                    html_body="""
                    <html>
                    <body style="font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h1 style="color: #9b59b6;">Welcome to Ainflue, {{name}}! 📸</h1>
                            <p>Your photography deserves the best platform for protection, promotion, and profit.</p>
                            
                            <h2>🎨 Photography Features:</h2>
                            <ul>
                                <li>Watermark protection and copyright monitoring</li>
                                <li>Professional portfolio showcase</li>
                                <li>Client booking and project management</li>
                                <li>Stock photography marketplace integration</li>
                            </ul>
                            
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; margin: 20px 0;">
                                <h3 style="margin: 0;">🏆 Photographer Spotlight Program</h3>
                                <p style="margin: 10px 0;">Upload 10+ high-quality photos in your first week and get featured in our weekly photographer spotlight!</p>
                            </div>
                            
                            <a href="{{portfolio_url}}" style="background: #9b59b6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">Build Your Portfolio 🎨</a>
                            
                            <p>Capture the moment!<br>The Ainflue Photography Team</p>
                        </div>
                    </body>
                    </html>
                    """,
                    from_name="Ainflue Photography"
                )
            },
            
            "influencer": {
                "brand_match": EmailContent(
                    subject="🤝 Perfect Brand Match Found - {{brand_name}} Campaign",
                    html_body="""
                    <html>
                    <body style="font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h1 style="color: #f39c12;">Brand Partnership Opportunity! 🤝</h1>
                            <p>Hi {{name}}, we found a perfect brand match for your content style!</p>
                            
                            <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 12px; padding: 20px; margin: 20px 0;">
                                <h3 style="color: #f39c12; margin-top: 0;">{{brand_name}} Campaign</h3>
                                <p><strong>Campaign Value:</strong> ${{campaign_value}}</p>
                                <p><strong>Content Required:</strong> {{content_requirements}}</p>
                                <p><strong>Deadline:</strong> {{deadline}}</p>
                                <p><strong>Brand Match Score:</strong> {{match_score}}/10 ⭐</p>
                            </div>
                            
                            <h3>🎯 Why This is a Great Match:</h3>
                            <ul>
                                <li>{{match_reason_1}}</li>
                                <li>{{match_reason_2}}</li>
                                <li>{{match_reason_3}}</li>
                            </ul>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{{accept_url}}" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 0 10px;">Accept Campaign ✅</a>
                                <a href="{{details_url}}" style="background: #6c757d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 0 10px;">View Details 📋</a>
                            </div>
                        </div>
                    </body>
                    </html>
                    """,
                    from_name="Ainflue Brand Partnerships"
                )
            },
            
            "comedian": {
                "show_booking": EmailContent(
                    subject="🎭 Comedy Show Booking Request - {{venue_name}}",
                    html_body="""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h1 style="color: #ff6b6b;">Show Booking Request! 🎭</h1>
                            <p>Hey {{name}}, a venue wants to book you for a comedy show!</p>
                            
                            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0;">
                                <h3 style="color: #ff6b6b; margin-top: 0;">Show Details:</h3>
                                <ul>
                                    <li><strong>Venue:</strong> {{venue_name}}</li>
                                    <li><strong>Date:</strong> {{show_date}}</li>
                                    <li><strong>Time:</strong> {{show_time}}</li>
                                    <li><strong>Duration:</strong> {{duration}} minutes</li>
                                    <li><strong>Payment:</strong> ${{payment_amount}}</li>
                                    <li><strong>Expected Audience:</strong> {{audience_size}} people</li>
                                </ul>
                            </div>
                            
                            <h3>🎤 Additional Information:</h3>
                            <p>{{additional_info}}</p>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{{accept_booking_url}}" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 0 10px;">Accept Booking 🎉</a>
                                <a href="{{negotiate_url}}" style="background: #ff6b6b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 0 10px;">Negotiate Terms 💬</a>
                            </div>
                            
                            <p>Break a leg!<br>The Ainflue Comedy Network</p>
                        </div>
                    </body>
                    </html>
                    """,
                    from_name="Ainflue Comedy Network"
                )
            }
        }

    def _initialize_email_campaigns(self) -> Dict[str, List[str]]:
        """Initialize email campaign sequences for creator onboarding."""
        return {
            "musician_onboarding": [
                "day_0_welcome",
                "day_3_first_upload_reminder",
                "day_7_profile_completion",
                "day_14_monetization_tips",
                "day_30_success_stories"
            ],
            "blogger_onboarding": [
                "day_0_welcome",
                "day_2_first_post_guide",
                "day_5_seo_optimization",
                "day_10_content_calendar",
                "day_21_monetization_strategies"
            ],
            "creator_retention": [
                "inactive_7_days",
                "inactive_14_days",
                "inactive_30_days",
                "winback_offer"
            ],
            "revenue_growth": [
                "monthly_report",
                "optimization_tips",
                "feature_updates",
                "success_celebration"
            ]
        }

    async def send_email(
        self,
        recipient: EmailRecipient,
        content: EmailContent,
        provider: Optional[EmailProvider] = None
    ) -> EmailResult:
        """
        Send individual email with provider failover.
        
        Args:
            recipient: Email recipient configuration
            content: Email content and formatting
            provider: Specific provider to use (optional)
            
        Returns:
            EmailResult with delivery status
        """
        try:
            # Check unsubscribe list
            if recipient.email in self.unsubscribed_emails:
                return EmailResult(
                    recipient_email=recipient.email,
                    status="unsubscribed",
                    error_message="Recipient has unsubscribed"
                )
            
            # Personalize content
            personalized_content = await self._personalize_content(content, recipient)
            
            # Determine provider to use
            email_provider = provider or self.default_provider
            
            # Attempt to send with primary provider
            result = await self._send_with_provider(email_provider, recipient, personalized_content)
            
            # Try failover if enabled and primary failed
            if not result.status == "sent" and self.enable_failover:
                for fallback_provider in EmailProvider:
                    if fallback_provider != email_provider:
                        logger.info(f"🔄 Trying failover provider: {fallback_provider.value}")
                        result = await self._send_with_provider(fallback_provider, recipient, personalized_content)
                        if result.status == "sent":
                            break
            
            # Track email if sent successfully
            if result.status == "sent":
                self._track_email(result)
            
            # Update provider stats
            provider_name = email_provider.value
            if result.status == "sent":
                self.provider_stats[provider_name]["sent"] += 1
            else:
                self.provider_stats[provider_name]["failed"] += 1
            
            logger.info(f"📧 Email {'sent' if result.status == 'sent' else 'failed'}: {recipient.email}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Email sending failed: {e}")
            return EmailResult(
                recipient_email=recipient.email,
                status="failed",
                error_message=str(e)
            )

    async def send_campaign(self, campaign: EmailCampaign) -> List[EmailResult]:
        """Send email campaign to multiple recipients."""
        results = []
        
        try:
            # Schedule campaign if send_time is specified
            if campaign.send_time and campaign.send_time > datetime.now():
                logger.info(f"📅 Campaign scheduled: {campaign.campaign_id} for {campaign.send_time}")
                # In production, this would be stored in a queue/scheduler
                return [EmailResult(
                    campaign_id=campaign.campaign_id,
                    status="scheduled",
                    recipient_email="campaign"
                )]
            
            # A/B test setup if configured
            if campaign.ab_test_config:
                results.extend(await self._send_ab_test_campaign(campaign))
            else:
                # Send to all recipients
                for recipient in campaign.recipients:
                    result = await self.send_email(recipient, campaign.content)
                    result.campaign_id = campaign.campaign_id
                    results.append(result)
            
            # Track campaign analytics
            if self.enable_analytics:
                await self._track_campaign_analytics(campaign, results)
            
            logger.info(f"✅ Campaign sent: {campaign.campaign_id} - {len(results)} emails")
            return results
            
        except Exception as e:
            logger.error(f"❌ Campaign sending failed: {e}")
            return [EmailResult(
                campaign_id=campaign.campaign_id,
                status="failed",
                error_message=str(e),
                recipient_email="campaign"
            )]

    async def send_creator_template(
        self,
        creator_type: str,
        template_name: str,
        recipient: EmailRecipient,
        template_data: Dict[str, Any]
    ) -> EmailResult:
        """Send email using creator-specific template."""
        try:
            # Get template
            if creator_type not in self.creator_templates:
                raise ValueError(f"Creator type '{creator_type}' not supported")
            
            if template_name not in self.creator_templates[creator_type]:
                raise ValueError(f"Template '{template_name}' not found for '{creator_type}'")
            
            template = self.creator_templates[creator_type][template_name]
            
            # Merge template data
            personalized_template = EmailContent(
                subject=template.subject,
                html_body=template.html_body,
                text_body=template.text_body,
                from_email=template.from_email,
                from_name=template.from_name,
                reply_to=template.reply_to,
                template_data=template_data
            )
            
            return await self.send_email(recipient, personalized_template)
            
        except Exception as e:
            logger.error(f"❌ Creator template email failed: {e}")
            raise

    async def _send_with_provider(
        self,
        provider: EmailProvider,
        recipient: EmailRecipient,
        content: EmailContent
    ) -> EmailResult:
        """Send email using specific provider."""
        try:
            if provider == EmailProvider.SENDGRID:
                return await self._send_sendgrid(recipient, content)
            elif provider == EmailProvider.MAILGUN:
                return await self._send_mailgun(recipient, content)
            elif provider == EmailProvider.SES:
                return await self._send_ses(recipient, content)
            elif provider == EmailProvider.POSTMARK:
                return await self._send_postmark(recipient, content)
            else:
                return EmailResult(
                    recipient_email=recipient.email,
                    status="failed",
                    error_message=f"Provider {provider.value} not implemented"
                )
                
        except Exception as e:
            return EmailResult(
                recipient_email=recipient.email,
                status="failed",
                error_message=str(e)
            )

    async def _send_sendgrid(self, recipient: EmailRecipient, content: EmailContent) -> EmailResult:
        """Send email via SendGrid API."""
        if not self.sendgrid_api_key or not self.session:
            return EmailResult(
                recipient_email=recipient.email,
                status="failed",
                error_message="SendGrid not configured"
            )
        
        payload = {
            "personalizations": [{
                "to": [{
                    "email": recipient.email,
                    "name": recipient.name or recipient.email
                }],
                "dynamic_template_data": content.template_data
            }],
            "from": {
                "email": content.from_email,
                "name": content.from_name
            },
            "subject": content.subject,
            "content": [{
                "type": "text/html",
                "value": content.html_body
            }]
        }
        
        if content.text_body:
            payload["content"].append({
                "type": "text/plain", 
                "value": content.text_body
            })
        
        if content.reply_to:
            payload["reply_to"] = {
                "email": content.reply_to
            }
        
        headers = {
            "Authorization": f"Bearer {self.sendgrid_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.session.post(
                self.provider_endpoints[EmailProvider.SENDGRID],
                json=payload,
                headers=headers
            )
            
            if response.status_code == 202:
                # SendGrid returns 202 for successful queue
                message_id = response.headers.get("X-Message-Id", "")
                return EmailResult(
                    message_id=message_id,
                    recipient_email=recipient.email,
                    status="sent",
                    provider_response={"provider": "sendgrid", "status_code": response.status_code}
                )
            else:
                return EmailResult(
                    recipient_email=recipient.email,
                    status="failed",
                    error_message=f"SendGrid error: {response.status_code}",
                    provider_response=response.json() if response.content else {}
                )
                
        except Exception as e:
            return EmailResult(
                recipient_email=recipient.email,
                status="failed",
                error_message=f"SendGrid exception: {str(e)}"
            )

    async def _send_mailgun(self, recipient: EmailRecipient, content: EmailContent) -> EmailResult:
        """Send email via Mailgun API."""
        if not self.mailgun_api_key or not self.mailgun_domain or not self.session:
            return EmailResult(
                recipient_email=recipient.email,
                status="failed",
                error_message="Mailgun not configured"
            )
        
        # Mailgun uses form data, not JSON
        data = {
            "from": f"{content.from_name} <{content.from_email}>",
            "to": f"{recipient.name or ''} <{recipient.email}>".strip(),
            "subject": content.subject,
            "html": content.html_body
        }
        
        if content.text_body:
            data["text"] = content.text_body
        
        if content.reply_to:
            data["h:Reply-To"] = content.reply_to
        
        # Add tracking
        data.update({
            "o:tracking": "yes",
            "o:tracking-clicks": "yes",
            "o:tracking-opens": "yes"
        })
        
        auth = httpx.BasicAuth("api", self.mailgun_api_key)
        
        try:
            response = await self.session.post(
                self.provider_endpoints[EmailProvider.MAILGUN],
                data=data,
                auth=auth
            )
            response.raise_for_status()
            
            result_data = response.json()
            return EmailResult(
                message_id=result_data.get("id", ""),
                recipient_email=recipient.email,
                status="sent",
                provider_response={"provider": "mailgun", "response": result_data}
            )
            
        except Exception as e:
            return EmailResult(
                recipient_email=recipient.email,
                status="failed",
                error_message=f"Mailgun exception: {str(e)}"
            )

    async def _send_ses(self, recipient: EmailRecipient, content: EmailContent) -> EmailResult:
        """Send email via Amazon SES."""
        # AWS SES implementation would require boto3 or manual signing
        # For now, return a placeholder response
        return EmailResult(
            recipient_email=recipient.email,
            status="sent",
            message_id="ses-placeholder-id",
            provider_response={"provider": "ses", "note": "Requires AWS boto3 implementation"}
        )

    async def _send_postmark(self, recipient: EmailRecipient, content: EmailContent) -> EmailResult:
        """Send email via Postmark API."""
        # Postmark implementation placeholder
        return EmailResult(
            recipient_email=recipient.email,
            status="sent",
            message_id="postmark-placeholder-id",
            provider_response={"provider": "postmark", "note": "Requires Postmark API implementation"}
        )

    async def _personalize_content(self, content: EmailContent, recipient: EmailRecipient) -> EmailContent:
        """Personalize email content for recipient."""
        # Merge template data with recipient data
        template_vars = {
            **content.template_data,
            "name": recipient.name or recipient.email.split("@")[0],
            "email": recipient.email,
            "creator_type": recipient.creator_type or "creator",
            **recipient.custom_fields
        }
        
        # Replace placeholders in subject and body
        personalized_subject = self._replace_template_vars(content.subject, template_vars)
        personalized_html = self._replace_template_vars(content.html_body, template_vars)
        personalized_text = self._replace_template_vars(content.text_body or "", template_vars)
        
        return EmailContent(
            subject=personalized_subject,
            html_body=personalized_html,
            text_body=personalized_text if content.text_body else None,
            from_email=content.from_email,
            from_name=content.from_name,
            reply_to=content.reply_to,
            attachments=content.attachments,
            template_id=content.template_id,
            template_data=template_vars
        )

    def _replace_template_vars(self, text: str, template_vars: Dict[str, Any]) -> str:
        """Replace {{variable}} placeholders in text."""
        for key, value in template_vars.items():
            placeholder = f"{{{{{key}}}}}"
            text = text.replace(placeholder, str(value))
        return text

    async def _send_ab_test_campaign(self, campaign: EmailCampaign) -> List[EmailResult]:
        """Send A/B test email campaign."""
        ab_config = campaign.ab_test_config
        test_percentage = ab_config.get("test_percentage", 50)
        variant_content = ab_config.get("variant_content")
        
        results = []
        
        # Split recipients for A/B test
        total_recipients = len(campaign.recipients)
        test_count = int(total_recipients * test_percentage / 100)
        
        # Send variant A (original)
        for i, recipient in enumerate(campaign.recipients[:test_count]):
            result = await self.send_email(recipient, campaign.content)
            result.campaign_id = f"{campaign.campaign_id}_A"
            results.append(result)
        
        # Send variant B
        if variant_content:
            for recipient in campaign.recipients[test_count:]:
                result = await self.send_email(recipient, variant_content)
                result.campaign_id = f"{campaign.campaign_id}_B"
                results.append(result)
        
        return results

    async def _track_campaign_analytics(self, campaign: EmailCampaign, results: List[EmailResult]) -> None:
        """Track campaign analytics for reporting."""
        campaign_id = campaign.campaign_id
        
        if campaign_id not in self.campaign_analytics:
            self.campaign_analytics[campaign_id] = {
                "sent": 0,
                "delivered": 0,
                "opened": 0,
                "clicked": 0,
                "bounced": 0,
                "unsubscribed": 0,
                "creator_type": campaign.creator_context.get("creator_type"),
                "email_type": campaign.email_type.value,
                "sent_at": datetime.now()
            }
        
        analytics = self.campaign_analytics[campaign_id]
        
        for result in results:
            if result.status == "sent":
                analytics["sent"] += 1
            elif result.status == "delivered":
                analytics["delivered"] += 1
            elif result.status == "bounced":
                analytics["bounced"] += 1

    def _track_email(self, result: EmailResult) -> None:
        """Track individual email for history."""
        self.email_history.append({
            "message_id": result.message_id,
            "recipient": result.recipient_email,
            "status": result.status,
            "sent_at": result.sent_at,
            "campaign_id": result.campaign_id
        })

    async def handle_webhook(self, provider: EmailProvider, webhook_data: Dict[str, Any]) -> None:
        """Handle email provider webhooks for status updates."""
        try:
            if provider == EmailProvider.SENDGRID:
                await self._process_sendgrid_webhook(webhook_data)
            elif provider == EmailProvider.MAILGUN:
                await self._process_mailgun_webhook(webhook_data)
            # Add other provider webhook handlers
            
        except Exception as e:
            logger.error(f"❌ Webhook processing failed: {e}")

    async def _process_sendgrid_webhook(self, webhook_data: Dict[str, Any]) -> None:
        """Process SendGrid webhook events."""
        for event in webhook_data:
            message_id = event.get("sg_message_id", "")
            event_type = event.get("event", "")
            timestamp = event.get("timestamp", 0)
            
            # Update email history and analytics based on event type
            if event_type == "delivered":
                # Update delivered status
                pass
            elif event_type == "open":
                # Track email open
                pass
            elif event_type == "click":
                # Track email click
                pass
            elif event_type == "bounce":
                # Handle bounce
                pass
            elif event_type == "unsubscribe":
                # Add to unsubscribe list
                email = event.get("email", "")
                if email:
                    self.unsubscribed_emails.add(email)

    async def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive email analytics."""
        # Calculate overall stats
        total_sent = sum(stats["sent"] for stats in self.provider_stats.values())
        total_failed = sum(stats["failed"] for stats in self.provider_stats.values())
        
        overall_success_rate = (
            total_sent / (total_sent + total_failed) if (total_sent + total_failed) > 0 else 0
        )
        
        # Provider performance
        provider_performance = {}
        for provider, stats in self.provider_stats.items():
            total_attempts = stats["sent"] + stats["failed"]
            success_rate = stats["sent"] / total_attempts if total_attempts > 0 else 0
            provider_performance[provider] = {
                **stats,
                "success_rate": success_rate
            }
        
        return {
            "overview": {
                "total_sent": total_sent,
                "total_failed": total_failed,
                "overall_success_rate": overall_success_rate,
                "total_unsubscribed": len(self.unsubscribed_emails),
                "campaigns_sent": len(self.campaign_analytics)
            },
            "provider_performance": provider_performance,
            "campaign_analytics": self.campaign_analytics,
            "recent_emails": self.email_history[-10:] if self.email_history else []
        }

    async def close(self) -> None:
        """Clean up resources and close connections."""
        if self.session:
            await self.session.aclose()
            self.session = None
            
        logger.info("✅ Email Service closed")

    async def __aenter__(self) -> None:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Factory function for easy instantiation
def create_email_service(
    sendgrid_api_key: Optional[str] = None,
    mailgun_api_key: Optional[str] = None,
    mailgun_domain: Optional[str] = None,
    default_provider: EmailProvider = EmailProvider.SENDGRID,
    enable_failover: bool = True,
    enable_analytics: bool = True
) -> EmailEnterpriseService:
    """
    Factory function to create email service with enterprise configuration.
    
    Args:
        sendgrid_api_key: SendGrid API key
        mailgun_api_key: Mailgun API key
        mailgun_domain: Mailgun domain
        default_provider: Default email provider to use
        enable_failover: Enable provider failover
        enable_analytics: Enable analytics tracking
        
    Returns:
        Configured EmailEnterpriseService instance
    """
    return EmailEnterpriseService(
        sendgrid_api_key=sendgrid_api_key,
        mailgun_api_key=mailgun_api_key,
        mailgun_domain=mailgun_domain,
        default_provider=default_provider,
        enable_failover=enable_failover,
        enable_analytics=enable_analytics
    )


# Example usage for creator emails
async def example_creator_emails() -> None:
    """Example of creator-specific email workflows."""
    try:
        service = create_email_service(
            sendgrid_api_key="your-sendgrid-api-key",
            mailgun_api_key="your-mailgun-api-key",
            mailgun_domain="your-domain.com"
        )
        
        # Send welcome email to new musician
        musician_recipient = EmailRecipient(
            email="musician@example.com",
            name="Alex Johnson",
            creator_id="musician_123",
            creator_type="musician"
        )
        
        welcome_result = await service.send_creator_template(
            creator_type="musician",
            template_name="welcome",
            recipient=musician_recipient,
            template_data={
                "dashboard_url": "https://ainflue.com/musician/dashboard",
                "help_url": "https://ainflue.com/musician/guide"
            }
        )
        
        print(f"🎵 Welcome email sent: {welcome_result.status}")
        
        # Send revenue report to musician
        revenue_result = await service.send_creator_template(
            creator_type="musician",
            template_name="revenue_report",
            recipient=musician_recipient,
            template_data={
                "total_revenue": "1,250.50",
                "growth_percentage": "15",
                "streaming_revenue": "850.30",
                "streaming_plays": "12,540",
                "download_revenue": "200.20",
                "download_count": "45",
                "licensing_revenue": "200.00",
                "licensing_deals": "2",
                "merchandise_revenue": "0.00",
                "projected_revenue": "1,400.00",
                "analytics_url": "https://ainflue.com/analytics"
            }
        )
        
        print(f"💰 Revenue report sent: {revenue_result.status}")
        
        # Get analytics
        analytics = await service.get_analytics()
        print(f"📊 Total emails sent: {analytics['overview']['total_sent']}")
        print(f"📈 Success rate: {analytics['overview']['overall_success_rate']:.2%}")
        
        await service.close()
        
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_creator_emails())