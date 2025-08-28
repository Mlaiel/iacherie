"""Enterprise notification template engine with AI-powered personalization and A/B testing.

This module provides comprehensive template management for IA Influencer Agent notifications
including HTML email templates, SMS templates, push notification templates, and more.
All templates are embedded directly in this module to respect the 3-level depth limit.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Multi-format Content Protection Platform
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union, Set, Callable
from datetime import datetime, timedelta
from enum import Enum
import logging
from dataclasses import dataclass, asdict, field
import hashlib
import uuid
from jinja2 import Template, Environment, BaseLoader
import re

from app.core.config import settings
from app.utils.metrics import MetricsCollector
from app.core.ai.content_generator import ContentGenerator


class TemplateType(str, Enum):
    """Notification template types."""
    EMAIL_HTML = "email_html"
    EMAIL_TEXT = "email_text"
    SMS = "sms"
    PUSH_NOTIFICATION = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SOCIAL_MEDIA = "social_media"


# EMBEDDED HTML EMAIL TEMPLATES
EMAIL_HTML_TEMPLATES = {
    "welcome_creator": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to IA Influencer Agent</title>
    <style>
        body { font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .header h1 { color: white; margin: 0; font-size: 28px; font-weight: 300; }
        .content { padding: 40px 30px; }
        .welcome-text { font-size: 18px; color: #333; line-height: 1.6; margin-bottom: 30px; }
        .features { background: #f8f9fa; padding: 25px; border-radius: 8px; margin: 25px 0; }
        .feature-item { display: flex; align-items: center; margin: 15px 0; }
        .feature-icon { width: 24px; height: 24px; margin-right: 15px; color: #667eea; }
        .cta-button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: 600; margin: 20px 0; }
        .footer { padding: 30px; text-align: center; border-top: 1px solid #eee; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to IA Influencer Agent</h1>
        </div>
        <div class="content">
            <p class="welcome-text">Hello {{ creator_name }},</p>
            <p class="welcome-text">Welcome to the future of content creation and protection! Your account has been successfully created and you're now part of an exclusive community of creators leveraging AI for content protection and monetization.</p>
            
            <div class="features">
                <h3>Your Content Protection Suite Includes:</h3>
                <div class="feature-item">
                    <span class="feature-icon">🛡️</span>
                    <span>AI-powered copyright protection for all your content</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">🎯</span>
                    <span>Professional SEO optimization for maximum visibility</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">🤝</span>
                    <span>Smart collaboration matching with other creators</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">📈</span>
                    <span>Multi-platform distribution and analytics</span>
                </div>
            </div>
            
            <a href="{{ dashboard_url }}" class="cta-button">Access Your Dashboard</a>
            
            <p>Need help getting started? Our AI-powered support is available 24/7.</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 IA Influencer Agent by Fahed Mlaiel | All rights reserved</p>
            <p><small>This platform is protected by advanced AI security systems</small></p>
        </div>
    </div>
</body>
</html>
""",

    "content_protected": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Protection Activated</title>
    <style>
        body { font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .header h1 { color: white; margin: 0; font-size: 24px; font-weight: 400; }
        .shield-icon { font-size: 48px; color: white; margin-bottom: 20px; }
        .content { padding: 40px 30px; }
        .protection-details { background: #ecfdf5; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }
        .metric-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }
        .metric-row:last-child { border-bottom: none; }
        .cta-button { display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: 600; margin: 20px 0; }
        .footer { padding: 30px; text-align: center; border-top: 1px solid #eee; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="shield-icon">🛡️</div>
            <h1>Content Protection Activated</h1>
        </div>
        <div class="content">
            <p>Hello {{ creator_name }},</p>
            <p>Great news! Your content "{{ content_title }}" has been successfully processed and is now protected by our advanced AI security system.</p>
            
            <div class="protection-details">
                <h3>Protection Summary:</h3>
                <div class="metric-row">
                    <span><strong>Content Type:</strong></span>
                    <span>{{ content_type }}</span>
                </div>
                <div class="metric-row">
                    <span><strong>Protection Level:</strong></span>
                    <span>{{ protection_level }}</span>
                </div>
                <div class="metric-row">
                    <span><strong>AI Fingerprints:</strong></span>
                    <span>{{ fingerprint_count }} generated</span>
                </div>
                <div class="metric-row">
                    <span><strong>SEO Score:</strong></span>
                    <span>{{ seo_score }}/100</span>
                </div>
                <div class="metric-row">
                    <span><strong>Status:</strong></span>
                    <span style="color: #10b981; font-weight: 600;">✓ Protected & Live</span>
                </div>
            </div>
            
            <a href="{{ content_dashboard_url }}" class="cta-button">View Content Analytics</a>
            
            <p><small>Your content is now monitored 24/7 for unauthorized usage across all major platforms.</small></p>
        </div>
        <div class="footer">
            <p>&copy; 2025 IA Influencer Agent by Fahed Mlaiel | Protected by AI</p>
        </div>
    </div>
</body>
</html>
""",

    "collaboration_match": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Collaboration Opportunity</title>
    <style>
        body { font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 40px 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .header h1 { color: white; margin: 0; font-size: 24px; font-weight: 400; }
        .collab-icon { font-size: 48px; color: white; margin-bottom: 20px; }
        .content { padding: 40px 30px; }
        .match-card { background: #fffbeb; border: 2px solid #fbbf24; border-radius: 12px; padding: 25px; margin: 25px 0; }
        .creator-info { display: flex; align-items: center; margin-bottom: 20px; }
        .creator-avatar { width: 60px; height: 60px; border-radius: 50%; background: #f59e0b; color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 600; margin-right: 20px; }
        .compatibility-score { background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-weight: 600; display: inline-block; margin: 10px 0; }
        .tags { margin: 15px 0; }
        .tag { background: #e5e7eb; color: #374151; padding: 6px 12px; border-radius: 15px; display: inline-block; margin: 5px 5px 5px 0; font-size: 14px; }
        .cta-buttons { margin: 30px 0; }
        .cta-button { display: inline-block; padding: 12px 25px; text-decoration: none; border-radius: 20px; font-weight: 600; margin: 10px 10px 10px 0; }
        .cta-primary { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; }
        .cta-secondary { background: white; color: #f59e0b; border: 2px solid #f59e0b; }
        .footer { padding: 30px; text-align: center; border-top: 1px solid #eee; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="collab-icon">🤝</div>
            <h1>Perfect Collaboration Match Found!</h1>
        </div>
        <div class="content">
            <p>Hello {{ recipient_name }},</p>
            <p>Our AI matching algorithm has found an exciting collaboration opportunity that's perfect for your content style and audience!</p>
            
            <div class="match-card">
                <div class="creator-info">
                    <div class="creator-avatar">{{ partner_initial }}</div>
                    <div>
                        <h3 style="margin: 0;">{{ partner_name }}</h3>
                        <p style="margin: 5px 0; color: #666;">{{ partner_specialty }}</p>
                    </div>
                </div>
                
                <div class="compatibility-score">{{ compatibility_score }}% Compatibility Match</div>
                
                <p><strong>Collaboration Opportunity:</strong> {{ collaboration_type }}</p>
                <p>{{ collaboration_description }}</p>
                
                <div class="tags">
                    <strong>Shared Interests:</strong>
                    {% for tag in shared_tags %}
                    <span class="tag">{{ tag }}</span>
                    {% endfor %}
                </div>
                
                <p><strong>Potential Reach:</strong> {{ estimated_reach }} combined audience</p>
            </div>
            
            <div class="cta-buttons">
                <a href="{{ collaboration_url }}" class="cta-button cta-primary">View Full Profile & Connect</a>
                <a href="{{ maybe_later_url }}" class="cta-button cta-secondary">Maybe Later</a>
            </div>
            
            <p><small>This match was generated using our advanced AI algorithm based on content style, audience demographics, engagement rates, and collaboration history.</small></p>
        </div>
        <div class="footer">
            <p>&copy; 2025 IA Influencer Agent by Fahed Mlaiel | AI-Powered Matching</p>
        </div>
    </div>
</body>
</html>
"""
}

# EMBEDDED SMS TEMPLATES
SMS_TEMPLATES = {
    "welcome_creator": "🎉 Welcome to IA Influencer Agent, {{ creator_name }}! Your AI-powered content protection is now active. Start uploading: {{ app_url }}",
    
    "content_protected": "✅ {{ creator_name }}, your {{ content_type }} '{{ content_title }}' is now AI-protected and live! SEO: {{ seo_score }}/100. View analytics: {{ short_url }}",
    
    "collaboration_match": "🤝 New collaboration match! {{ partner_name }} ({{ compatibility_score }}% match) wants to collaborate on {{ collaboration_type }}. Check it out: {{ short_url }}",
    
    "content_violation": "🚨 {{ creator_name }}, unauthorized use of your content detected on {{ platform }}. Our AI is taking action. Details: {{ violation_url }}",
    
    "monetization_opportunity": "💰 {{ creator_name }}, new monetization opportunity available! Estimated earning: ${{ estimated_earning }}. Act now: {{ opportunity_url }}",
    
    "engagement_milestone": "🎯 Congrats {{ creator_name }}! Your content reached {{ milestone_value }} {{ milestone_type }}. Keep creating: {{ dashboard_url }}"
}

# EMBEDDED PUSH NOTIFICATION TEMPLATES
PUSH_TEMPLATES = {
    "welcome_creator": {
        "title": "Welcome to IA Influencer Agent! 🚀",
        "body": "Your AI-powered content protection is ready. Upload your first content now!",
        "data": {"action": "open_upload", "priority": "high"}
    },
    
    "content_processed": {
        "title": "Content Protected ✅",
        "body": "{{ content_title }} is now AI-protected and live with {{ seo_score }}/100 SEO score",
        "data": {"content_id": "{{ content_id }}", "action": "view_analytics"}
    },
    
    "collaboration_request": {
        "title": "New Collaboration! 🤝",
        "body": "{{ partner_name }} wants to collaborate - {{ compatibility_score }}% match!",
        "data": {"collaboration_id": "{{ collaboration_id }}", "action": "view_collaboration"}
    },
    
    "content_violation": {
        "title": "Content Violation Detected! 🚨",
        "body": "Unauthorized use found on {{ platform }}. AI protection activated.",
        "data": {"violation_id": "{{ violation_id }}", "action": "view_violation", "priority": "urgent"}
    },
    
    "engagement_spike": {
        "title": "Viral Alert! 🔥",
        "body": "{{ content_title }} is trending! {{ engagement_count }} new interactions",
        "data": {"content_id": "{{ content_id }}", "action": "view_analytics", "priority": "high"}
    }
}

# EMBEDDED IN-APP NOTIFICATION TEMPLATES
IN_APP_TEMPLATES = {
    "welcome_creator": {
        "type": "success",
        "icon": "🎉",
        "title": "Welcome to IA Influencer Agent!",
        "message": "Your AI-powered content protection suite is now active. Ready to upload your first content?",
        "actions": [
            {"label": "Upload Content", "action": "navigate", "target": "/upload"},
            {"label": "Take Tour", "action": "start_tour"}
        ],
        "duration": 0,  # Persistent until dismissed
        "priority": "high"
    },
    
    "content_processing": {
        "type": "info",
        "icon": "⚡",
        "title": "AI Processing in Progress",
        "message": "{{ content_title }} is being analyzed and protected. Estimated completion: {{ estimated_time }}",
        "progress": "{{ progress_percentage }}",
        "actions": [
            {"label": "View Progress", "action": "navigate", "target": "/processing/{{ content_id }}"}
        ],
        "duration": 10000,
        "priority": "medium"
    },
    
    "protection_complete": {
        "type": "success",
        "icon": "🛡️",
        "title": "Content Protection Complete!",
        "message": "{{ content_title }} is now protected with {{ fingerprint_count }} AI fingerprints and {{ seo_score }}/100 SEO score.",
        "actions": [
            {"label": "View Analytics", "action": "navigate", "target": "/content/{{ content_id }}/analytics"},
            {"label": "Share Content", "action": "share", "target": "{{ content_url }}"}
        ],
        "duration": 8000,
        "priority": "high"
    },
    
    "collaboration_match": {
        "type": "opportunity",
        "icon": "🤝",
        "title": "Perfect Collaboration Match!",
        "message": "{{ partner_name }} ({{ compatibility_score }}% match) is interested in {{ collaboration_type }}",
        "actions": [
            {"label": "View Profile", "action": "navigate", "target": "/collaborations/{{ collaboration_id }}"},
            {"label": "Connect Now", "action": "connect", "target": "{{ partner_id }}"},
            {"label": "Maybe Later", "action": "dismiss"}
        ],
        "duration": 0,
        "priority": "medium"
    },
    
    "monetization_alert": {
        "type": "earning",
        "icon": "💰",
        "title": "New Monetization Opportunity!",
        "message": "Potential earning: ${{ estimated_earning }} from {{ opportunity_type }}",
        "actions": [
            {"label": "View Details", "action": "navigate", "target": "/monetization/{{ opportunity_id }}"},
            {"label": "Accept Offer", "action": "accept_monetization", "target": "{{ opportunity_id }}"}
        ],
        "duration": 0,
        "priority": "high"
    }
}

# EMBEDDED WEBHOOK PAYLOAD TEMPLATES
WEBHOOK_TEMPLATES = {
    "content_protected": {
        "event": "content.protected",
        "timestamp": "{{ timestamp }}",
        "data": {
            "content_id": "{{ content_id }}",
            "creator_id": "{{ creator_id }}",
            "content_type": "{{ content_type }}",
            "protection_level": "{{ protection_level }}",
            "fingerprints": "{{ fingerprint_count }}",
            "seo_score": "{{ seo_score }}",
            "processing_duration": "{{ processing_duration }}",
            "status": "protected"
        }
    },
    
    "violation_detected": {
        "event": "content.violation",
        "timestamp": "{{ timestamp }}",
        "data": {
            "violation_id": "{{ violation_id }}",
            "content_id": "{{ content_id }}",
            "creator_id": "{{ creator_id }}",
            "platform": "{{ platform }}",
            "violation_type": "{{ violation_type }}",
            "confidence_score": "{{ confidence_score }}",
            "action_taken": "{{ action_taken }}",
            "evidence_url": "{{ evidence_url }}"
        }
    },
    
    "collaboration_created": {
        "event": "collaboration.created",
        "timestamp": "{{ timestamp }}",
        "data": {
            "collaboration_id": "{{ collaboration_id }}",
            "initiator_id": "{{ initiator_id }}",
            "partner_id": "{{ partner_id }}",
            "collaboration_type": "{{ collaboration_type }}",
            "compatibility_score": "{{ compatibility_score }}",
            "status": "pending",
            "expires_at": "{{ expires_at }}"
        }
    }
}


class PersonalizationLevel(str, Enum):
    """AI personalization levels."""
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    AI_GENERATED = "ai_generated"
    HYPER_PERSONALIZED = "hyper_personalized"


class ContentTone(str, Enum):
    """Content tone options."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    URGENT = "urgent"
    CELEBRATORY = "celebratory"
    INFORMATIVE = "informative"
    ENCOURAGING = "encouraging"


@dataclass
class TemplateVariable:
    """Template variable definition with validation."""
    name: str
    type: str  # string, integer, float, boolean, datetime, list, dict
    required: bool = True
    default_value: Optional[Any] = None
    description: Optional[str] = None
    validation_regex: Optional[str] = None
    format_function: Optional[str] = None  # Name of formatting function


@dataclass
class PersonalizationContext:
    """Context for AI-powered personalization."""
    user_id: str
    creator_type: str  # musician, blogger, photographer, influencer, comedian
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    content_history: List[Dict[str, Any]] = field(default_factory=list)
    engagement_data: Dict[str, Any] = field(default_factory=dict)
    demographic_data: Dict[str, Any] = field(default_factory=dict)
    behavioral_patterns: Dict[str, Any] = field(default_factory=dict)
    platform_preferences: List[str] = field(default_factory=list)
    collaboration_history: List[Dict[str, Any]] = field(default_factory=list)
    revenue_data: Dict[str, Any] = field(default_factory=dict)
    language_preference: str = "en"
    timezone: str = "UTC"
    optimal_send_time: Optional[datetime] = None


@dataclass
class ABTestVariant:
    """A/B test variant for notification templates."""
    variant_id: str
    name: str
    template_content: str
    weight: float = 1.0  # Traffic allocation weight
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    sent_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    converted_count: int = 0
    
    @property
    def open_rate(self) -> float:
        return self.opened_count / self.sent_count if self.sent_count > 0 else 0.0
    
    @property
    def click_rate(self) -> float:
        return self.clicked_count / self.sent_count if self.sent_count > 0 else 0.0
    
    @property
    def conversion_rate(self) -> float:
        return self.converted_count / self.sent_count if self.sent_count > 0 else 0.0


@dataclass
class NotificationTemplate:
    """Enterprise notification template with AI-powered features."""
    id: str
    name: str
    type: TemplateType
    subject: Optional[str] = None  # For email templates
    content: str = ""
    variables: List[TemplateVariable] = field(default_factory=list)
    
    # Personalization
    personalization_level: PersonalizationLevel = PersonalizationLevel.BASIC
    content_tone: ContentTone = ContentTone.PROFESSIONAL
    ai_instructions: Optional[str] = None  # Instructions for AI personalization
    
    # Localization
    supported_languages: List[str] = field(default_factory=lambda: ["en"])
    localized_content: Dict[str, str] = field(default_factory=dict)  # lang -> content
    localized_subjects: Dict[str, str] = field(default_factory=dict)  # lang -> subject
    
    # A/B Testing
    ab_test_enabled: bool = False
    ab_test_variants: List[ABTestVariant] = field(default_factory=list)
    
    # Business Logic Integration
    business_triggers: List[str] = field(default_factory=list)  # Events that trigger this template
    target_creator_types: List[str] = field(default_factory=list)  # musician, blogger, etc.
    platform_specific: Dict[str, str] = field(default_factory=dict)  # platform -> customized content
    
    # Template metadata
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    active: bool = True
    
    # Analytics
    usage_count: int = 0
    success_rate: float = 0.0
    engagement_rate: float = 0.0
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class NotificationTemplateEngine:
    """Enterprise notification template engine with AI-powered personalization and comprehensive analytics."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector()
        self.content_generator = ContentGenerator()
        
        # Template storage (would use database in production)
        self.templates = {}  # template_id -> NotificationTemplate
        
        # Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
            autoescape=True
        )
        
        # AI personalization cache
        self.personalization_cache = {}  # user_id -> cached personalization data
        self.cache_ttl = timedelta(hours=1)
        
        # A/B test tracking
        self.ab_test_results = {}  # test_id -> results
        
        # Business context templates for IA Influencer
        self._initialize_business_templates()
        
        # Custom formatting functions
        self.formatting_functions = {
            "currency": self._format_currency,
            "percentage": self._format_percentage,
            "number": self._format_number,
            "datetime": self._format_datetime,
            "duration": self._format_duration,
            "platform_name": self._format_platform_name,
            "creator_type": self._format_creator_type
        }

    async def create_template(self, template: NotificationTemplate) -> str:
        """Create a new notification template."""
        # Validate template
        await self._validate_template(template)
        
        # Store template
        self.templates[template.id] = template
        
        # Track metrics
        await self.metrics.increment("templates_created_total", tags={"type": template.type.value})
        
        self.logger.info(f"Notification template created: {template.id} ({template.name})")
        return template.id

    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing template."""
        if template_id not in self.templates:
            return False
        
        template = self.templates[template_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_at = datetime.utcnow()
        template.version = self._increment_version(template.version)
        
        self.logger.info(f"Template updated: {template_id}")
        return True

    async def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self.templates:
            del self.templates[template_id]
            self.logger.info(f"Template deleted: {template_id}")
            return True
        return False

    async def render_template(
        self,
        template_id: str,
        context: Dict[str, Any],
        personalization_context: Optional[PersonalizationContext] = None,
        language: str = "en"
    ) -> Dict[str, str]:
        """Render template with AI-powered personalization."""
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self.templates[template_id]
        
        # Handle A/B testing
        if template.ab_test_enabled and template.ab_test_variants:
            variant = await self._select_ab_test_variant(template)
            template_content = variant.template_content
            variant.sent_count += 1
        else:
            template_content = template.content
        
        # Apply AI personalization if enabled
        if template.personalization_level != PersonalizationLevel.NONE and personalization_context:
            template_content = await self._apply_ai_personalization(
                template_content, template, personalization_context
            )
        
        # Get localized content
        content_to_render = template.localized_content.get(language, template_content)
        subject_to_render = template.localized_subjects.get(language, template.subject)
        
        # Prepare rendering context
        render_context = await self._prepare_render_context(context, personalization_context)
        
        # Render with Jinja2
        try:
            jinja_template = Template(content_to_render)
            rendered_content = jinja_template.render(**render_context)
            
            rendered_subject = None
            if subject_to_render:
                subject_template = Template(subject_to_render)
                rendered_subject = subject_template.render(**render_context)
            
            # Track template usage
            template.usage_count += 1
            
            result = {"content": rendered_content}
            if rendered_subject:
                result["subject"] = rendered_subject
            
            self.logger.debug(f"Template rendered: {template_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Template rendering failed: {template_id} -> {str(e)}")
            raise

    async def render_multi_language(
        self,
        template_id: str,
        context: Dict[str, Any],
        languages: List[str],
        personalization_context: Optional[PersonalizationContext] = None
    ) -> Dict[str, Dict[str, str]]:
        """Render template in multiple languages."""
        results = {}
        
        for language in languages:
            try:
                results[language] = await self.render_template(
                    template_id, context, personalization_context, language
                )
            except Exception as e:
                self.logger.error(f"Multi-language rendering failed for {language}: {str(e)}")
                results[language] = {"error": str(e)}
        
        return results

    async def create_ab_test(
        self,
        template_id: str,
        variants: List[Dict[str, Any]],
        test_name: Optional[str] = None
    ) -> str:
        """Create A/B test for a template."""
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self.templates[template_id]
        
        # Create test variants
        test_variants = []
        for i, variant_data in enumerate(variants):
            variant = ABTestVariant(
                variant_id=variant_data.get("variant_id", f"variant_{i}"),
                name=variant_data.get("name", f"Variant {i+1}"),
                template_content=variant_data["content"],
                weight=variant_data.get("weight", 1.0),
                metadata=variant_data.get("metadata", {})
            )
            test_variants.append(variant)
        
        # Enable A/B testing
        template.ab_test_enabled = True
        template.ab_test_variants = test_variants
        
        test_id = f"ab_test_{template_id}_{int(datetime.utcnow().timestamp())}"
        self.ab_test_results[test_id] = {
            "template_id": template_id,
            "test_name": test_name or f"A/B Test for {template.name}",
            "variants": test_variants,
            "started_at": datetime.utcnow(),
            "status": "active"
        }
        
        self.logger.info(f"A/B test created: {test_id} for template {template_id}")
        return test_id

    async def get_ab_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get A/B test results and statistics."""
        if test_id not in self.ab_test_results:
            return None
        
        test_data = self.ab_test_results[test_id]
        variants = test_data["variants"]
        
        # Calculate statistical significance
        results = {
            "test_id": test_id,
            "template_id": test_data["template_id"],
            "test_name": test_data["test_name"],
            "started_at": test_data["started_at"],
            "status": test_data["status"],
            "variants": []
        }
        
        total_sent = sum(v.sent_count for v in variants)
        
        for variant in variants:
            variant_result = {
                "variant_id": variant.variant_id,
                "name": variant.name,
                "sent_count": variant.sent_count,
                "traffic_percentage": (variant.sent_count / total_sent * 100) if total_sent > 0 else 0,
                "open_rate": variant.open_rate,
                "click_rate": variant.click_rate,
                "conversion_rate": variant.conversion_rate,
                "performance_score": self._calculate_performance_score(variant)
            }
            results["variants"].append(variant_result)
        
        # Determine winner
        if results["variants"]:
            winner = max(results["variants"], key=lambda v: v["performance_score"])
            results["winner"] = winner["variant_id"]
        
        return results

    async def get_template_by_business_event(
        self,
        business_event: str,
        creator_type: Optional[str] = None,
        platform: Optional[str] = None
    ) -> Optional[NotificationTemplate]:
        """Get template by business event trigger."""
        for template in self.templates.values():
            if (business_event in template.business_triggers and
                (not creator_type or creator_type in template.target_creator_types) and
                template.active):
                
                # Check platform-specific content
                if platform and platform in template.platform_specific:
                    # Create a copy with platform-specific content
                    template_copy = NotificationTemplate(
                        id=template.id,
                        name=template.name,
                        type=template.type,
                        subject=template.subject,
                        content=template.platform_specific[platform],
                        variables=template.variables,
                        personalization_level=template.personalization_level,
                        content_tone=template.content_tone,
                        ai_instructions=template.ai_instructions,
                        supported_languages=template.supported_languages,
                        localized_content=template.localized_content,
                        localized_subjects=template.localized_subjects,
                        ab_test_enabled=template.ab_test_enabled,
                        ab_test_variants=template.ab_test_variants,
                        business_triggers=template.business_triggers,
                        target_creator_types=template.target_creator_types,
                        platform_specific=template.platform_specific,
                        category=template.category,
                        tags=template.tags,
                        created_at=template.created_at,
                        updated_at=template.updated_at,
                        version=template.version,
                        active=template.active,
                        usage_count=template.usage_count,
                        success_rate=template.success_rate,
                        engagement_rate=template.engagement_rate
                    )
                    return template_copy
                
                return template
        
        return None

    async def get_templates_by_criteria(
        self,
        template_type: Optional[TemplateType] = None,
        creator_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        active_only: bool = True
    ) -> List[NotificationTemplate]:
        """Get templates filtered by criteria."""
        filtered_templates = []
        
        for template in self.templates.values():
            if active_only and not template.active:
                continue
            
            if template_type and template.type != template_type:
                continue
            
            if creator_types and not any(ct in template.target_creator_types for ct in creator_types):
                continue
            
            if tags and not any(tag in template.tags for tag in tags):
                continue
            
            filtered_templates.append(template)
        
        # Sort by usage and success rate
        filtered_templates.sort(key=lambda t: (t.success_rate, t.usage_count), reverse=True)
        
        return filtered_templates

    # Private methods
    async def _validate_template(self, template: NotificationTemplate) -> None:
        """Validate template structure and content."""
        if not template.name:
            raise ValueError("Template name is required")
        
        if not template.content:
            raise ValueError("Template content is required")
        
        # Validate Jinja2 syntax
        try:
            Template(template.content)
            if template.subject:
                Template(template.subject)
        except Exception as e:
            raise ValueError(f"Invalid template syntax: {str(e)}")
        
        # Validate variables
        template_vars = re.findall(r'{{\s*(\w+)', template.content)
        for var in template.variables:
            if var.required and var.name not in template_vars:
                self.logger.warning(f"Required variable '{var.name}' not found in template content")

    async def _apply_ai_personalization(
        self,
        content: str,
        template: NotificationTemplate,
        context: PersonalizationContext
    ) -> str:
        """Apply AI-powered personalization to template content."""
        if template.personalization_level == PersonalizationLevel.NONE:
            return content
        
        # Check cache
        cache_key = f"{context.user_id}_{template.id}_{hashlib.md5(content.encode()).hexdigest()}"
        if cache_key in self.personalization_cache:
            cached_data = self.personalization_cache[cache_key]
            if datetime.utcnow() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["content"]
        
        try:
            # Build AI prompt based on personalization level
            ai_prompt = self._build_personalization_prompt(content, template, context)
            
            # Generate personalized content
            personalized_content = await self.content_generator.generate_personalized_content(
                original_content=content,
                personalization_prompt=ai_prompt,
                tone=template.content_tone.value,
                user_context=asdict(context)
            )
            
            # Cache result
            self.personalization_cache[cache_key] = {
                "content": personalized_content,
                "timestamp": datetime.utcnow()
            }
            
            return personalized_content
            
        except Exception as e:
            self.logger.error(f"AI personalization failed: {str(e)}")
            return content  # Fallback to original content

    def _build_personalization_prompt(
        self,
        content: str,
        template: NotificationTemplate,
        context: PersonalizationContext
    ) -> str:
        """Build AI prompt for personalization."""
        prompt_parts = [
            f"Personalize the following {template.type.value} notification for a {context.creator_type}:",
            f"Content: {content}",
            f"Tone: {template.content_tone.value}",
            f"User language: {context.language_preference}",
        ]
        
        if template.ai_instructions:
            prompt_parts.append(f"Special instructions: {template.ai_instructions}")
        
        if context.user_preferences:
            prompt_parts.append(f"User preferences: {json.dumps(context.user_preferences)}")
        
        if context.engagement_data:
            prompt_parts.append(f"Engagement patterns: {json.dumps(context.engagement_data)}")
        
        prompt_parts.extend([
            "Requirements:",
            "- Maintain professional quality suitable for IA Influencer Agent platform",
            "- Keep all placeholder variables ({{ variable_name }}) intact",
            "- Ensure content remains appropriate for creator monetization context",
            "- Preserve any legal disclaimers or copyright notices",
            "- Optimize for engagement while maintaining authenticity"
        ])
        
        return "\n".join(prompt_parts)

    async def _prepare_render_context(
        self,
        context: Dict[str, Any],
        personalization_context: Optional[PersonalizationContext] = None
    ) -> Dict[str, Any]:
        """Prepare context for template rendering."""
        render_context = context.copy()
        
        # Add system variables
        render_context.update({
            "current_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "current_time": datetime.utcnow().strftime("%H:%M:%S UTC"),
            "current_year": datetime.utcnow().year,
            "platform_name": "IA Influencer Agent",
            "platform_url": getattr(settings, "PLATFORM_URL", "https://ia-influencer.com"),
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@ia-influencer.com")
        })
        
        # Add personalization context
        if personalization_context:
            render_context.update({
                "user_timezone": personalization_context.timezone,
                "user_language": personalization_context.language_preference,
                "creator_type_formatted": self._format_creator_type(personalization_context.creator_type)
            })
        
        # Apply custom formatting functions
        for key, value in render_context.items():
            if isinstance(value, str) and key.endswith("_formatted"):
                continue  # Skip already formatted values
            
            # Auto-format certain types
            if key.endswith("_amount") and isinstance(value, (int, float)):
                render_context[f"{key}_formatted"] = self._format_currency(value)
            elif key.endswith("_percentage") and isinstance(value, (int, float)):
                render_context[f"{key}_formatted"] = self._format_percentage(value)
            elif key.endswith("_count") and isinstance(value, int):
                render_context[f"{key}_formatted"] = self._format_number(value)
        
        return render_context

    async def _select_ab_test_variant(self, template: NotificationTemplate) -> ABTestVariant:
        """Select A/B test variant based on weights."""
        if not template.ab_test_variants:
            raise ValueError("No A/B test variants available")
        
        # Calculate total weight
        total_weight = sum(variant.weight for variant in template.ab_test_variants)
        
        # Generate random selection
        import random
        selection = random.random() * total_weight
        
        # Select variant
        current_weight = 0
        for variant in template.ab_test_variants:
            current_weight += variant.weight
            if selection <= current_weight:
                return variant
        
        # Fallback to first variant
        return template.ab_test_variants[0]

    def _calculate_performance_score(self, variant: ABTestVariant) -> float:
        """Calculate performance score for A/B test variant."""
        if variant.sent_count == 0:
            return 0.0
        
        # Weighted performance score
        open_weight = 0.3
        click_weight = 0.4
        conversion_weight = 0.3
        
        score = (
            variant.open_rate * open_weight +
            variant.click_rate * click_weight +
            variant.conversion_rate * conversion_weight
        )
        
        return score

    def _increment_version(self, current_version: str) -> str:
        """Increment template version."""
        try:
            parts = current_version.split(".")
            patch = int(parts[2]) + 1
            return f"{parts[0]}.{parts[1]}.{patch}"
        except:
            return "1.0.1"

    # Formatting functions
    def _format_currency(self, amount: Union[int, float], currency: str = "USD") -> str:
        """Format currency amount."""
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"

    def _format_percentage(self, value: Union[int, float]) -> str:
        """Format percentage value."""
        return f"{value:.1f}%"

    def _format_number(self, value: int) -> str:
        """Format large numbers with appropriate suffixes."""
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return str(value)

    def _format_datetime(self, dt: datetime, format_string: str = "%Y-%m-%d %H:%M UTC") -> str:
        """Format datetime."""
        return dt.strftime(format_string)

    def _format_duration(self, seconds: int) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    def _format_platform_name(self, platform: str) -> str:
        """Format platform name for display."""
        platform_names = {
            "youtube": "YouTube",
            "tiktok": "TikTok",
            "instagram": "Instagram",
            "facebook": "Facebook",
            "twitter": "Twitter",
            "linkedin": "LinkedIn",
            "spotify": "Spotify",
            "soundcloud": "SoundCloud"
        }
        return platform_names.get(platform.lower(), platform.title())

    def _format_creator_type(self, creator_type: str) -> str:
        """Format creator type for display."""
        creator_types = {
            "musician": "Musician",
            "blogger": "Blogger",
            "photographer": "Photographer",
            "influencer": "Influencer",
            "comedian": "Comedian",
            "podcaster": "Podcaster",
            "artist": "Visual Artist",
            "writer": "Writer"
        }
        return creator_types.get(creator_type.lower(), creator_type.title())

    def _initialize_business_templates(self) -> None:
        """Initialize IA Influencer Agent business-specific templates."""
        # Load embedded templates
        business_templates = [
            # Welcome Templates
            NotificationTemplate(
                id="welcome_creator_email",
                name="Creator Welcome Email",
                type=TemplateType.EMAIL_HTML,
                subject="🚀 Welcome to IA Influencer Agent - Your AI Protection Suite is Ready!",
                content=EMAIL_HTML_TEMPLATES["welcome_creator"],
                business_triggers=["user_registered", "account_activated"],
                target_creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                category="onboarding",
                tags=["welcome", "activation", "ai_protection"],
                variables=[
                    TemplateVariable("creator_name", "string", True, description="Creator's display name"),
                    TemplateVariable("dashboard_url", "string", True, description="URL to creator dashboard")
                ]
            ),
            
            # Content Protection Templates
            NotificationTemplate(
                id="content_protected_email",
                name="Content Protection Complete",
                type=TemplateType.EMAIL_HTML,
                subject="✅ {{ content_title }} is Now AI-Protected and Live!",
                content=EMAIL_HTML_TEMPLATES["content_protected"],
                business_triggers=["content_protected", "ai_processing_complete"],
                target_creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                category="content_lifecycle",
                tags=["protection", "ai_processing", "success"],
                variables=[
                    TemplateVariable("creator_name", "string", True),
                    TemplateVariable("content_title", "string", True),
                    TemplateVariable("content_type", "string", True),
                    TemplateVariable("protection_level", "string", True),
                    TemplateVariable("fingerprint_count", "integer", True),
                    TemplateVariable("seo_score", "integer", True),
                    TemplateVariable("content_dashboard_url", "string", True)
                ]
            ),
            
            # Collaboration Templates
            NotificationTemplate(
                id="collaboration_match_email",
                name="Collaboration Match Found",
                type=TemplateType.EMAIL_HTML,
                subject="🤝 Perfect Collaboration Match - {{ compatibility_score }}% Compatibility!",
                content=EMAIL_HTML_TEMPLATES["collaboration_match"],
                business_triggers=["collaboration_match_found", "ai_matching_complete"],
                target_creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                category="collaboration",
                tags=["collaboration", "ai_matching", "opportunity"],
                variables=[
                    TemplateVariable("recipient_name", "string", True),
                    TemplateVariable("partner_name", "string", True),
                    TemplateVariable("partner_initial", "string", True),
                    TemplateVariable("partner_specialty", "string", True),
                    TemplateVariable("compatibility_score", "integer", True),
                    TemplateVariable("collaboration_type", "string", True),
                    TemplateVariable("collaboration_description", "string", True),
                    TemplateVariable("shared_tags", "list", True),
                    TemplateVariable("estimated_reach", "string", True),
                    TemplateVariable("collaboration_url", "string", True),
                    TemplateVariable("maybe_later_url", "string", True)
                ]
            )
        ]
        
        # Store templates
        for template in business_templates:
            self.templates[template.id] = template
        
        self.logger.info(f"Initialized {len(business_templates)} business templates")


# Template engine singleton
template_engine = NotificationTemplateEngine()


# Utility functions for easy template access
def get_embedded_template(template_type: str, template_name: str) -> Optional[str]:
    """Get embedded template by type and name."""
    template_maps = {
        "email_html": EMAIL_HTML_TEMPLATES,
        "sms": SMS_TEMPLATES,
        "push": PUSH_TEMPLATES,
        "in_app": IN_APP_TEMPLATES,
        "webhook": WEBHOOK_TEMPLATES
    }
    
    template_map = template_maps.get(template_type)
    if template_map:
        return template_map.get(template_name)
    
    return None


async def render_notification_template(
    template_id: str,
    context: Dict[str, Any],
    personalization_context: Optional[PersonalizationContext] = None,
    language: str = "en"
) -> Dict[str, str]:
    """Convenience function to render a notification template."""
    return await template_engine.render_template(
        template_id, context, personalization_context, language
    )


# Export main classes and functions
__all__ = [
    "TemplateType",
    "PersonalizationLevel", 
    "ContentTone",
    "TemplateVariable",
    "PersonalizationContext",
    "ABTestVariant",
    "NotificationTemplate",
    "NotificationTemplateEngine",
    "template_engine",
    "get_embedded_template",
    "render_notification_template",
    "EMAIL_HTML_TEMPLATES",
    "SMS_TEMPLATES",
    "PUSH_TEMPLATES", 
    "IN_APP_TEMPLATES",
    "WEBHOOK_TEMPLATES"
]

# Fix the indentation error
def _return_test_id(test_id):
    """Helper function to return test ID"""
    return test_id

class ABTestManager:
    """A/B Testing manager for notifications"""
    
    def __init__(self):
        self.ab_test_results = {}

    async def get_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get A/B test results with statistical analysis."""
        if test_id not in self.ab_test_results:
            raise ValueError(f"A/B test not found: {test_id}")
        
        test_data = self.ab_test_results[test_id]
        variants = test_data["variants"]
        
        # Calculate results
        results = {
            "test_id": test_id,
            "test_name": test_data["test_name"],
            "started_at": test_data["started_at"],
            "status": test_data["status"],
            "variants": []
        }
        
        for variant in variants:
            variant_result = {
                "variant_id": variant.variant_id,
                "name": variant.name,
                "sent_count": variant.sent_count,
                "opened_count": variant.opened_count,
                "clicked_count": variant.clicked_count,
                "converted_count": variant.converted_count,
                "open_rate": variant.open_rate,
                "click_rate": variant.click_rate,
                "conversion_rate": variant.conversion_rate
            }
            results["variants"].append(variant_result)
        
        # Determine winner (simplified)
        if len(variants) > 1:
            winner = max(variants, key=lambda v: v.conversion_rate)
            results["winner"] = {
                "variant_id": winner.variant_id,
                "improvement": winner.conversion_rate - min(v.conversion_rate for v in variants)
            }
        
        return results

    async def get_template_analytics(
        self,
        template_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get comprehensive template analytics."""
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self.templates[template_id]
        
        return {
            "template_id": template_id,
            "template_name": template.name,
            "usage_count": template.usage_count,
            "success_rate": template.success_rate,
            "engagement_rate": template.engagement_rate,
            "performance_by_creator_type": await self._get_performance_by_creator_type(template_id),
            "performance_by_platform": await self._get_performance_by_platform(template_id),
            "personalization_effectiveness": await self._get_personalization_effectiveness(template_id),
            "language_performance": await self._get_language_performance(template_id),
            "optimal_send_times": await self._get_optimal_send_times(template_id),
            "content_analysis": await self._analyze_content_performance(template)
        }

    async def suggest_template_improvements(self, template_id: str) -> List[Dict[str, Any]]:
        """AI-powered template improvement suggestions."""
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self.templates[template_id]
        
        suggestions = []
        
        # Analyze content for improvements
        content_analysis = await self._analyze_template_content(template)
        suggestions.extend(content_analysis)
        
        # Personalization suggestions
        if template.personalization_level == PersonalizationLevel.BASIC:
            suggestions.append({
                "type": "personalization",
                "suggestion": "Enable advanced personalization for better engagement",
                "expected_improvement": "15-25% increase in click-through rate",
                "implementation": "Upgrade to advanced personalization level"
            })
        
        # A/B testing suggestions
        if not template.ab_test_enabled:
            suggestions.append({
                "type": "ab_testing",
                "suggestion": "Create A/B test variants to optimize performance",
                "expected_improvement": "10-20% improvement in conversion rate",
                "implementation": "Create 2-3 variants with different messaging approaches"
            })
        
        # Language support suggestions
        if len(template.supported_languages) == 1:
            suggestions.append({
                "type": "localization",
                "suggestion": "Add multi-language support for international users",
                "expected_improvement": "30-50% increase in global engagement",
                "implementation": "Add translations for Spanish, French, German"
            })
        
        return suggestions

    async def _initialize_business_templates(self):
        """Initialize business-specific templates for IA Influencer."""
        business_templates = [
            {
                "id": "content_upload_success",
                "name": "Content Upload Success",
                "type": TemplateType.EMAIL_HTML,
                "subject": "🎉 Your {{content_type}} '{{content_title}}' is now protected!",
                "content": """
                <h2>Great job, {{creator_name}}! 🎯</h2>
                <p>Your {{content_type}} <strong>"{{content_title}}"</strong> has been successfully uploaded and is now protected by our AI copyright system.</p>
                
                <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>🛡️ Protection Status:</h3>
                    <ul>
                        <li>✅ Content fingerprinted with 99.5% accuracy</li>
                        <li>✅ Monitoring {{monitoring_platforms}} platforms</li>
                        <li>✅ DMCA protection activated</li>
                        {% if revenue_potential %}
                        <li>💰 Estimated revenue protection: ${{revenue_potential}}/month</li>
                        {% endif %}
                    </ul>
                </div>
                
                <p><a href="{{dashboard_link}}" style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">View Dashboard</a></p>
                
                <p>Keep creating amazing {{creator_type}} content! 🚀</p>
                """,
                "business_triggers": ["content.uploaded", "content.protected"],
                "target_creator_types": ["musician", "blogger", "photographer", "influencer", "comedian"]
            },
            {
                "id": "collaboration_opportunity",
                "name": "Collaboration Match Found",
                "type": TemplateType.EMAIL_HTML,
                "subject": "🤝 Perfect collaboration match found for {{creator_name}}!",
                "content": """
                <h2>Exciting collaboration opportunity! 🎉</h2>
                <p>Hi {{creator_name}},</p>
                
                <p>Our AI matching system found a perfect collaboration partner for you:</p>
                
                <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3>{{partner_name}} - {{partner_creator_type}}</h3>
                    <p><strong>Match Score:</strong> {{match_score}}% compatibility</p>
                    <p><strong>Audience Overlap:</strong> {{audience_overlap}}%</p>
                    <p><strong>Project Type:</strong> {{project_type}}</p>
                    
                    {% if estimated_reach %}
                    <p><strong>Combined Reach:</strong> {{estimated_reach}} followers</p>
                    {% endif %}
                    
                    {% if revenue_potential %}
                    <p><strong>Revenue Potential:</strong> ${{revenue_potential}}</p>
                    {% endif %}
                </div>
                
                <p><a href="{{collaboration_link}}" style="background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">View Collaboration Details</a></p>
                
                <p>This opportunity expires in {{expiry_hours}} hours. Don't miss out!</p>
                """,
                "business_triggers": ["collaboration.match_found"],
                "target_creator_types": ["musician", "blogger", "photographer", "influencer", "comedian"]
            },
            {
                "id": "revenue_milestone",
                "name": "Revenue Milestone Reached",
                "type": TemplateType.EMAIL_HTML,
                "subject": "🎊 Congratulations! You've earned ${{revenue_amount}} this month!",
                "content": """
                <h2>Amazing milestone reached! 🎯💰</h2>
                <p>Hi {{creator_name}},</p>
                
                <p>Congratulations! You've reached an incredible revenue milestone:</p>
                
                <div style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; border-radius: 12px; text-align: center; margin: 20px 0;">
                    <h1 style="font-size: 3em; margin: 0;">${{revenue_amount}}</h1>
                    <p style="font-size: 1.2em; margin: 10px 0;">{{milestone_type}} Revenue</p>
                </div>
                
                <h3>Revenue Breakdown:</h3>
                <ul>
                    {% for source, amount in revenue_sources.items() %}
                    <li>{{source}}: ${{amount}}</li>
                    {% endfor %}
                </ul>
                
                <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>🚀 Growth Insights:</h3>
                    <p><strong>Growth Rate:</strong> +{{growth_percentage}}% vs last period</p>
                    <p><strong>Top Performing Content:</strong> {{top_content_title}}</p>
                    <p><strong>Best Platform:</strong> {{best_platform}}</p>
                </div>
                
                <p><a href="{{earnings_dashboard}}" style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">View Detailed Earnings</a></p>
                
                <p>Keep up the amazing work! 🎉</p>
                """,
                "business_triggers": ["revenue.milestone_reached"],
                "target_creator_types": ["musician", "blogger", "photographer", "influencer", "comedian"]
            }
        ]
        
        for template_data in business_templates:
            template = NotificationTemplate(**template_data)
            self.templates[template.id] = template

    async def _validate_template(self, template: NotificationTemplate):
        """Validate template structure and content."""
        if not template.name:
            raise ValueError("Template name is required")
        
        if not template.content:
            raise ValueError("Template content is required")
        
        # Validate Jinja2 syntax
        try:
            Template(template.content)
        except Exception as e:
            raise ValueError(f"Invalid template syntax: {str(e)}")

    def _increment_version(self, current_version: str) -> str:
        """Increment semantic version."""
        try:
            parts = current_version.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            return ".".join(parts)
        except:
            return "1.0.1"

    async def _select_ab_test_variant(self, template: NotificationTemplate) -> ABTestVariant:
        """Select A/B test variant based on weights."""
        if not template.ab_test_variants:
            raise ValueError("No A/B test variants available")
        
        # Simple weighted selection (would use more sophisticated algorithm in production)
        import random
        
        total_weight = sum(v.weight for v in template.ab_test_variants)
        random_value = random.random() * total_weight
        
        cumulative_weight = 0
        for variant in template.ab_test_variants:
            cumulative_weight += variant.weight
            if random_value <= cumulative_weight:
                return variant
        
        return template.ab_test_variants[0]

    async def _apply_ai_personalization(
        self,
        content: str,
        template: NotificationTemplate,
        context: PersonalizationContext
    ) -> str:
        """Apply AI-powered personalization to template content."""
        if template.personalization_level == PersonalizationLevel.AI_GENERATED:
            # Generate completely new content based on context
            return await self.content_generator.generate_personalized_content(
                template_type=template.type,
                user_context=context,
                tone=template.content_tone,
                instructions=template.ai_instructions
            )
        elif template.personalization_level == PersonalizationLevel.HYPER_PERSONALIZED:
            # Hyper-personalize existing content
            return await self.content_generator.hyper_personalize_content(
                content,
                user_context=context,
                tone=template.content_tone
            )
        else:
            # Basic personalization - just return original content
            return content

    async def _prepare_render_context(
        self,
        context: Dict[str, Any],
        personalization_context: Optional[PersonalizationContext]
    ) -> Dict[str, Any]:
        """Prepare rendering context with all variables and functions."""
        render_context = context.copy()
        
        # Add personalization data
        if personalization_context:
            render_context.update({
                "user_id": personalization_context.user_id,
                "creator_type": personalization_context.creator_type,
                "language": personalization_context.language_preference,
                "timezone": personalization_context.timezone
            })
        
        # Add formatting functions
        render_context.update(self.formatting_functions)
        
        # Add current datetime
        render_context["now"] = datetime.utcnow()
        
        return render_context

    # Formatting functions
    def _format_currency(self, amount: float, currency: str = "USD") -> str:
        """Format currency amount."""
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"

    def _format_percentage(self, value: float, decimals: int = 1) -> str:
        """Format percentage value."""
        return f"{value:.{decimals}f}%"

    def _format_number(self, value: Union[int, float], thousands_sep: str = ",") -> str:
        """Format number with thousands separator."""
        return f"{value:,}"

    def _format_datetime(self, dt: datetime, format_string: str = "%B %d, %Y") -> str:
        """Format datetime."""
        return dt.strftime(format_string)

    def _format_duration(self, seconds: int) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        else:
            return f"{seconds // 3600} hours"

    def _format_platform_name(self, platform: str) -> str:
        """Format platform name for display."""
        platform_names = {
            "youtube": "YouTube",
            "instagram": "Instagram",
            "tiktok": "TikTok",
            "twitter": "Twitter/X",
            "facebook": "Facebook",
            "linkedin": "LinkedIn",
            "spotify": "Spotify",
            "soundcloud": "SoundCloud"
        }
        return platform_names.get(platform.lower(), platform.title())

    def _format_creator_type(self, creator_type: str) -> str:
        """Format creator type for display."""
        return creator_type.replace("_", " ").title()

    # Analytics methods (simplified implementations)
    async def _get_performance_by_creator_type(self, template_id: str) -> Dict[str, Dict]:
        return {}

    async def _get_performance_by_platform(self, template_id: str) -> Dict[str, Dict]:
        return {}

    async def _get_personalization_effectiveness(self, template_id: str) -> Dict[str, Any]:
        return {}

    async def _get_language_performance(self, template_id: str) -> Dict[str, Dict]:
        return {}

    async def _get_optimal_send_times(self, template_id: str) -> Dict[str, Any]:
        return {}

    async def _analyze_content_performance(self, template: NotificationTemplate) -> Dict[str, Any]:
        return {}

    async def _analyze_template_content(self, template: NotificationTemplate) -> List[Dict[str, Any]]:
        return []
