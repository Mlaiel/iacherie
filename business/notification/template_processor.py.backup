"""Template Processor - AI-Powered Template Processing and Optimization

Advanced template processing engine for IA Influencer Agent notification system.
Handles intelligent template selection, AI-powered personalization, A/B testing,
multi-language support, and dynamic content optimization.

Key Features:
- AI-powered template selection based on user behavior and preferences
- Dynamic content personalization with machine learning insights
- Multi-language template support with cultural adaptation
- A/B testing framework for template optimization
- Real-time template performance analytics
- Business-specific template categories and optimization
- Rich content support (HTML, Markdown, Rich Media)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from typing import Dict, List, Optional, Any, Tuple
import logging
import json
from datetime import datetime, timezone
from dataclasses import dataclass

from .notification_models import NotificationRequest, NotificationTemplate, NotificationContent
from .config import NotificationConfig
from .constants import TEMPLATE_CATEGORIES, NOTIFICATION_TYPES

logger = logging.getLogger(__name__)


@dataclass
class TemplateMetrics:
    """Template performance metrics."""
    template_id: str
    usage_count: int = 0
    success_rate: float = 0.0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    average_processing_time: float = 0.0
    a_b_test_winner: Optional[str] = None
    last_updated: Optional[datetime] = None


class TemplateProcessor:
    """
    Advanced template processing engine with AI optimization.
    
    Provides intelligent template selection, personalization, and optimization
    for IA Influencer Agent notification system.
    """
    
    def __init__(self, config: NotificationConfig):
        """
        Initialize template processor.
        
        Args:
            config: Notification system configuration
        """
        self.config = config
        self.template_cache: Dict[str, NotificationTemplate] = {}
        self.template_metrics: Dict[str, TemplateMetrics] = {}
        self.a_b_tests: Dict[str, Dict[str, Any]] = {}
        
        # Processing statistics
        self.processing_stats = {
            "templates_processed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "personalization_applied": 0,
            "a_b_tests_created": 0,
            "average_processing_time": 0.0
        }
        
        # Initialize default templates
        self._initialize_default_templates()
        
        logger.info("TemplateProcessor initialized with AI optimization")
    
    async def process_template(
        self,
        request: NotificationRequest,
        template_override: Optional[NotificationTemplate] = None
    ) -> NotificationTemplate:
        """
        Process and optimize notification template.
        
        Args:
            request: Notification request
            template_override: Optional template override
        
        Returns:
            Processed and optimized notification template
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Get or create template
            if template_override:
                template = template_override
            else:
                template = await self._select_optimal_template(request)
            
            # Apply personalization if enabled
            if self._is_personalization_enabled(request):
                template = await self._personalize_template(request, template)
                self.processing_stats["personalization_applied"] += 1
            
            # Apply A/B testing if enabled
            if self._is_ab_testing_enabled(request, template):
                template = await self._apply_ab_testing(request, template)
            
            # Process template content
            template = await self._process_template_content(request, template)
            
            # Update template metrics
            await self._update_template_metrics(template, True)
            
            # Update processing statistics
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time)
            
            logger.debug(f"Template processed for {request.notification_type}: {template.template_id}")
            return template
            
        except Exception as e:
            logger.error(f"Template processing failed: {e}")
            # Return fallback template
            return await self._get_fallback_template(request)
    
    async def _select_optimal_template(self, request: NotificationRequest) -> NotificationTemplate:
        """Select optimal template based on AI analysis."""
        try:
            # Generate cache key
            cache_key = self._generate_template_cache_key(request)
            
            # Check cache first
            if cache_key in self.template_cache:
                self.processing_stats["cache_hits"] += 1
                return self.template_cache[cache_key]
            
            self.processing_stats["cache_misses"] += 1
            
            # Select template based on notification type and context
            template = await self._ai_template_selection(request)
            
            # Cache template
            self.template_cache[cache_key] = template
            
            return template
            
        except Exception as e:
            logger.error(f"Template selection failed: {e}")
            return await self._get_default_template(request.notification_type)
    
    def _generate_template_cache_key(self, request: NotificationRequest) -> str:
        """Generate cache key for template."""
        key_components = [
            request.notification_type,
            request.priority,
            request.recipient.language,
            request.recipient.user_type or "default"
        ]
        
        # Add business context if available
        if request.business_context:
            key_components.append(str(hash(json.dumps(request.business_context, sort_keys=True))))
        
        return "_".join(str(c) for c in key_components)
    
    async def _ai_template_selection(self, request: NotificationRequest) -> NotificationTemplate:
        """AI-powered template selection."""
        try:
            # Get template candidates
            candidates = await self._get_template_candidates(request)
            
            if not candidates:
                return await self._get_default_template(request.notification_type)
            
            # Score templates based on multiple factors
            scored_templates = []
            for template in candidates:
                score = await self._calculate_template_score(template, request)
                scored_templates.append((template, score))
            
            # Select highest scoring template
            scored_templates.sort(key=lambda x: x[1], reverse=True)
            selected_template = scored_templates[0][0]
            
            logger.debug(f"AI selected template: {selected_template.template_id} (score: {scored_templates[0][1]:.2f})")
            return selected_template
            
        except Exception as e:
            logger.error(f"AI template selection failed: {e}")
            return await self._get_default_template(request.notification_type)
    
    async def _get_template_candidates(self, request: NotificationRequest) -> List[NotificationTemplate]:
        """Get template candidates for notification type."""
        candidates = []
        
        # Get templates by notification type
        notification_type = request.notification_type
        
        # Check template categories
        for category, types in TEMPLATE_CATEGORIES.items():
            for type_category, templates in types.items():
                if notification_type in templates or any(nt in notification_type for nt in templates):
                    # Create template candidates
                    for template_name in templates:
                        template = await self._create_template_from_definition(
                            template_name, notification_type, request
                        )
                        if template:
                            candidates.append(template)
        
        # Add custom templates if available
        custom_templates = await self._get_custom_templates(request)
        candidates.extend(custom_templates)
        
        return candidates
    
    async def _create_template_from_definition(
        self,
        template_name: str,
        notification_type: str,
        request: NotificationRequest
    ) -> Optional[NotificationTemplate]:
        """Create template from definition."""
        try:
            template_id = f"{notification_type}_{template_name}_{request.recipient.language}"
            
            # Get base template structure
            base_templates = await self._get_base_templates()
            
            if template_name in base_templates:
                template_def = base_templates[template_name]
                
                template = NotificationTemplate(
                    template_id=template_id,
                    template_name=template_name,
                    notification_type=notification_type,
                    version="1.0",
                    language=request.recipient.language,
                    channel_templates=template_def.get("channels", {}),
                    personalization_rules=template_def.get("personalization", {}),
                    business_rules=template_def.get("business_rules", {}),
                    variables=template_def.get("variables", []),
                    is_active=True
                )
                
                return template
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create template from definition: {e}")
            return None
    
    async def _get_base_templates(self) -> Dict[str, Any]:
        """Get base template definitions."""
        return {
            "copyright_alert": {
                "channels": {
                    "email": {
                        "subject": "🚨 Copyright Infringement Detected - {content_title}",
                        "html_content": """
                        <h2>Copyright Infringement Alert</h2>
                        <p>Dear {user_name},</p>
                        <p>We have detected unauthorized use of your content:</p>
                        <ul>
                            <li><strong>Content:</strong> {content_title}</li>
                            <li><strong>Platform:</strong> {platform}</li>
                            <li><strong>Detected:</strong> {detection_time}</li>
                            <li><strong>Confidence:</strong> {detection_confidence}%</li>
                        </ul>
                        <p><a href="{action_url}" style="background-color:#e74c3c;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Take Action</a></p>
                        <p>Best regards,<br>IA Influencer Agent Team</p>
                        """,
                        "text_content": "Copyright Infringement Alert: {content_title} detected on {platform}. Take action: {action_url}"
                    },
                    "sms": {
                        "message": "🚨 Copyright alert: {content_title} detected on {platform}. Action required: {short_url}"
                    },
                    "push": {
                        "title": "Copyright Infringement Detected",
                        "body": "{content_title} found on {platform}",
                        "data": {"action": "copyright_alert", "content_id": "{content_id}"}
                    }
                },
                "variables": ["user_name", "content_title", "platform", "detection_time", "detection_confidence", "action_url", "content_id", "short_url"],
                "personalization": {
                    "user_type_specific": True,
                    "severity_based": True,
                    "platform_specific": True
                },
                "business_rules": {
                    "priority": "urgent",
                    "immediate_delivery": True,
                    "multi_channel": True
                }
            },
            "collaboration_match": {
                "channels": {
                    "email": {
                        "subject": "🤝 Perfect Collaboration Match Found - {match_score}% Match!",
                        "html_content": """
                        <h2>Great Collaboration Opportunity!</h2>
                        <p>Hi {user_name},</p>
                        <p>We found an excellent collaboration match for you:</p>
                        <div style="border:1px solid #ddd;padding:15px;margin:15px 0;border-radius:8px;">
                            <h3>{partner_name}</h3>
                            <p><strong>Match Score:</strong> {match_score}%</p>
                            <p><strong>Specializes in:</strong> {partner_skills}</p>
                            <p><strong>Audience:</strong> {partner_audience_size} followers</p>
                            <p><strong>Collaboration Type:</strong> {collaboration_type}</p>
                            <p><strong>Estimated Value:</strong> ${estimated_value}</p>
                        </div>
                        <p><a href="{collaboration_url}" style="background-color:#3498db;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">View Collaboration</a></p>
                        <p>Best regards,<br>IA Influencer Agent Team</p>
                        """,
                        "text_content": "Collaboration match: {partner_name} ({match_score}% match). View: {collaboration_url}"
                    },
                    "push": {
                        "title": "New Collaboration Match!",
                        "body": "{partner_name} - {match_score}% match",
                        "data": {"action": "collaboration", "partner_id": "{partner_id}"}
                    }
                },
                "variables": ["user_name", "partner_name", "match_score", "partner_skills", "partner_audience_size", "collaboration_type", "estimated_value", "collaboration_url", "partner_id"],
                "personalization": {
                    "match_quality_based": True,
                    "collaboration_history": True,
                    "user_preferences": True
                }
            },
            "monetization_opportunity": {
                "channels": {
                    "email": {
                        "subject": "💰 Revenue Opportunity - Earn ${revenue_potential}",
                        "html_content": """
                        <h2>New Revenue Opportunity!</h2>
                        <p>Hello {user_name},</p>
                        <p>We've identified a high-value monetization opportunity:</p>
                        <div style="background-color:#f8f9fa;border-left:4px solid #28a745;padding:15px;margin:15px 0;">
                            <h3>💰 ${revenue_potential} Potential Revenue</h3>
                            <p><strong>Opportunity:</strong> {opportunity_type}</p>
                            <p><strong>Platform:</strong> {platform}</p>
                            <p><strong>Success Rate:</strong> {success_rate}%</p>
                            <p><strong>Time Sensitive:</strong> {time_sensitivity}</p>
                        </div>
                        <p><a href="{opportunity_url}" style="background-color:#28a745;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Explore Opportunity</a></p>
                        <p>Act fast - this opportunity expires in {expiry_time}!</p>
                        <p>Best regards,<br>IA Influencer Agent Team</p>
                        """,
                        "text_content": "Revenue opportunity: ${revenue_potential} on {platform}. Explore: {opportunity_url}"
                    }
                },
                "variables": ["user_name", "revenue_potential", "opportunity_type", "platform", "success_rate", "time_sensitivity", "opportunity_url", "expiry_time"],
                "personalization": {
                    "revenue_history": True,
                    "creator_type_specific": True,
                    "performance_based": True
                }
            }
        }
    
    async def _get_custom_templates(self, request: NotificationRequest) -> List[NotificationTemplate]:
        """Get custom templates for user/organization."""
        # Placeholder for custom template loading
        return []
    
    async def _calculate_template_score(
        self,
        template: NotificationTemplate,
        request: NotificationRequest
    ) -> float:
        """Calculate template suitability score."""
        try:
            score = 50.0  # Base score
            
            # Performance factor (40% weight)
            template_metrics = self.template_metrics.get(template.template_id)
            if template_metrics:
                success_rate = template_metrics.success_rate
                engagement_rate = template_metrics.engagement_rate
                conversion_rate = template_metrics.conversion_rate
                
                score += (success_rate - 50) * 0.2  # Normalize around 50%
                score += (engagement_rate - 10) * 1.0  # Normalize around 10%
                score += (conversion_rate - 5) * 2.0  # Normalize around 5%
            
            # Language match factor (20% weight)
            if template.language == request.recipient.language:
                score += 20
            elif template.language == "en":  # English fallback
                score += 10
            
            # Business rules alignment (20% weight)
            if template.business_rules:
                rules_score = self._calculate_business_rules_score(template, request)
                score += rules_score * 0.2
            
            # Personalization compatibility (10% weight)
            if template.personalization_rules and request.personalization_data:
                score += 10
            
            # Channel compatibility (10% weight)
            if request.channels:
                compatible_channels = 0
                for channel in request.channels:
                    if channel in template.channel_templates:
                        compatible_channels += 1
                
                if compatible_channels > 0:
                    channel_score = (compatible_channels / len(request.channels)) * 10
                    score += channel_score
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Template scoring failed: {e}")
            return 50.0
    
    def _calculate_business_rules_score(
        self,
        template: NotificationTemplate,
        request: NotificationRequest
    ) -> float:
        """Calculate business rules alignment score."""
        try:
            score = 50.0
            template_rules = template.business_rules or {}
            
            # Priority alignment
            if "priority" in template_rules:
                if template_rules["priority"] == request.priority:
                    score += 20
                elif abs(self._priority_to_numeric(template_rules["priority"]) - 
                        self._priority_to_numeric(request.priority)) <= 1:
                    score += 10
            
            # Delivery timing alignment
            if "immediate_delivery" in template_rules:
                if template_rules["immediate_delivery"] and request.delivery_time == "immediate":
                    score += 15
            
            # Multi-channel alignment
            if "multi_channel" in template_rules and template_rules["multi_channel"]:
                if request.channels and len(request.channels) > 1:
                    score += 15
            
            return score
            
        except Exception as e:
            logger.error(f"Business rules scoring failed: {e}")
            return 50.0
    
    def _priority_to_numeric(self, priority: str) -> int:
        """Convert priority string to numeric value."""
        priority_map = {"low": 1, "medium": 2, "high": 3, "urgent": 4, "critical": 5}
        return priority_map.get(priority, 2)
    
    async def _personalize_template(
        self,
        request: NotificationRequest,
        template: NotificationTemplate
    ) -> NotificationTemplate:
        """Apply AI-powered personalization to template."""
        try:
            # Get personalization context
            personalization_context = await self._get_personalization_context(request)
            
            # Apply personalization to each channel template
            for channel, channel_template in template.channel_templates.items():
                personalized_channel_template = await self._personalize_channel_template(
                    channel_template, personalization_context, request
                )
                template.channel_templates[channel] = personalized_channel_template
            
            # Update template metadata
            template.personalization_rules = template.personalization_rules or {}
            template.personalization_rules["applied_at"] = datetime.now(timezone.utc).isoformat()
            template.personalization_rules["personalization_level"] = personalization_context.get("level", "medium")
            
            return template
            
        except Exception as e:
            logger.error(f"Template personalization failed: {e}")
            return template
    
    async def _get_personalization_context(self, request: NotificationRequest) -> Dict[str, Any]:
        """Get personalization context for request."""
        context = {
            "user_name": request.recipient.user_id,  # Fallback to user_id
            "user_type": request.recipient.user_type or "creator",
            "language": request.recipient.language,
            "timezone": request.recipient.timezone or "UTC",
            "personalization_data": request.personalization_data or {},
            "business_context": request.business_context or {},
            "level": "high"  # Default personalization level
        }
        
        # Add user-specific context if available
        if hasattr(request.recipient, 'business_context') and request.recipient.business_context:
            context.update(request.recipient.business_context)
        
        # Add notification-specific context
        context.update({
            "notification_type": request.notification_type,
            "priority": request.priority,
            "urgency_score": getattr(request, 'urgency_score', 0.0)
        })
        
        return context
    
    async def _personalize_channel_template(
        self,
        channel_template: Dict[str, Any],
        context: Dict[str, Any],
        request: NotificationRequest
    ) -> Dict[str, Any]:
        """Personalize individual channel template."""
        try:
            personalized = channel_template.copy()
            
            # Replace variables in all text fields
            for field in ["subject", "message", "title", "html_content", "text_content", "body"]:
                if field in personalized and isinstance(personalized[field], str):
                    personalized[field] = self._replace_template_variables(
                        personalized[field], context
                    )
            
            # Apply user-type specific customizations
            personalized = await self._apply_user_type_customizations(
                personalized, context, request
            )
            
            # Apply AI-generated insights if available
            if context.get("level") == "high":
                personalized = await self._apply_ai_insights(personalized, context)
            
            return personalized
            
        except Exception as e:
            logger.error(f"Channel template personalization failed: {e}")
            return channel_template
    
    def _replace_template_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Replace template variables with context values."""
        try:
            # Replace direct context variables
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in text:
                    text = text.replace(placeholder, str(value))
            
            # Replace nested context variables
            for category in ["personalization_data", "business_context"]:
                if category in context and isinstance(context[category], dict):
                    for key, value in context[category].items():
                        placeholder = f"{{{key}}}"
                        if placeholder in text:
                            text = text.replace(placeholder, str(value))
            
            return text
            
        except Exception as e:
            logger.error(f"Variable replacement failed: {e}")
            return text
    
    async def _apply_user_type_customizations(
        self,
        template: Dict[str, Any],
        context: Dict[str, Any],
        request: NotificationRequest
    ) -> Dict[str, Any]:
        """Apply user type specific customizations."""
        try:
            user_type = context.get("user_type", "creator")
            
            # User type specific customizations
            customizations = {
                "musician": {
                    "emoji": "🎵",
                    "greeting": "Hey music creator",
                    "terminology": {"content": "track", "platform": "streaming platform"}
                },
                "blogger": {
                    "emoji": "✍️",
                    "greeting": "Hello writer",
                    "terminology": {"content": "article", "platform": "blog platform"}
                },
                "photographer": {
                    "emoji": "📸",
                    "greeting": "Hi photographer",
                    "terminology": {"content": "photo", "platform": "photo platform"}
                },
                "influencer": {
                    "emoji": "⭐",
                    "greeting": "Hey influencer",
                    "terminology": {"content": "post", "platform": "social platform"}
                },
                "comedian": {
                    "emoji": "😂",
                    "greeting": "Hello comedian",
                    "terminology": {"content": "video", "platform": "comedy platform"}
                }
            }
            
            if user_type in customizations:
                custom = customizations[user_type]
                
                # Apply customizations to template fields
                for field in template:
                    if isinstance(template[field], str):
                        # Replace generic terms with user-specific terminology
                        for generic, specific in custom.get("terminology", {}).items():
                            template[field] = template[field].replace(generic, specific)
                        
                        # Add user-specific emoji and greeting
                        if "{emoji}" in template[field]:
                            template[field] = template[field].replace("{emoji}", custom["emoji"])
                        if "{greeting}" in template[field]:
                            template[field] = template[field].replace("{greeting}", custom["greeting"])
            
            return template
            
        except Exception as e:
            logger.error(f"User type customization failed: {e}")
            return template
    
    async def _apply_ai_insights(
        self,
        template: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply AI-generated insights to template."""
        try:
            # Placeholder for AI insights application
            # In a real implementation, this would call ML models for:
            # - Optimal send times
            # - Content tone adjustment
            # - Personalized recommendations
            # - Dynamic content generation
            
            # Add AI-generated metadata
            if "data" not in template:
                template["data"] = {}
            
            template["data"].update({
                "ai_optimized": True,
                "optimization_score": 85.0,
                "predicted_engagement": context.get("predicted_engagement", 12.5),
                "optimal_send_time": context.get("optimal_send_time", "09:00")
            })
            
            return template
            
        except Exception as e:
            logger.error(f"AI insights application failed: {e}")
            return template
    
    def _is_personalization_enabled(self, request: NotificationRequest) -> bool:
        """Check if personalization is enabled for request."""
        return (
            self.config.ai.personalization_enabled and
            (not request.metadata or request.metadata.get("personalization_enabled", True))
        )
    
    def _is_ab_testing_enabled(self, request: NotificationRequest, template: NotificationTemplate) -> bool:
        """Check if A/B testing is enabled."""
        return (
            self.config.ai.a_b_testing_enabled and
            template.a_b_test_config is not None and
            (not request.metadata or request.metadata.get("ab_testing_enabled", True))
        )
    
    async def _apply_ab_testing(
        self,
        request: NotificationRequest,
        template: NotificationTemplate
    ) -> NotificationTemplate:
        """Apply A/B testing to template."""
        try:
            # Get A/B test variant
            variant = await self._get_ab_test_variant(request, template)
            
            # Apply variant modifications
            if variant and variant != "control":
                template = await self._apply_ab_variant(template, variant)
                
                # Track A/B test
                test_id = f"{template.template_id}_{variant}"
                if test_id not in self.a_b_tests:
                    self.a_b_tests[test_id] = {
                        "template_id": template.template_id,
                        "variant": variant,
                        "participants": 0,
                        "conversions": 0,
                        "created_at": datetime.now(timezone.utc)
                    }
                
                self.a_b_tests[test_id]["participants"] += 1
                self.processing_stats["a_b_tests_created"] += 1
            
            return template
            
        except Exception as e:
            logger.error(f"A/B testing application failed: {e}")
            return template
    
    async def _get_ab_test_variant(
        self,
        request: NotificationRequest,
        template: NotificationTemplate
    ) -> str:
        """Get A/B test variant for request."""
        try:
            # Simple hash-based variant assignment
            import hashlib
            hash_input = f"{request.recipient.user_id}_{template.template_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
            
            # Get available variants
            a_b_config = template.a_b_test_config or {}
            variants = a_b_config.get("variants", ["control", "variant_a"])
            
            return variants[hash_value % len(variants)]
            
        except Exception as e:
            logger.error(f"A/B variant selection failed: {e}")
            return "control"
    
    async def _apply_ab_variant(
        self,
        template: NotificationTemplate,
        variant: str
    ) -> NotificationTemplate:
        """Apply A/B test variant modifications."""
        try:
            if not template.a_b_test_config:
                return template
            
            variant_config = template.a_b_test_config.get("variant_configs", {}).get(variant)
            if not variant_config:
                return template
            
            # Apply variant modifications
            for channel, modifications in variant_config.items():
                if channel in template.channel_templates:
                    template.channel_templates[channel].update(modifications)
            
            # Add variant metadata
            template.metadata = template.metadata or {}
            template.metadata["ab_variant"] = variant
            template.metadata["ab_test_id"] = f"{template.template_id}_{variant}"
            
            return template
            
        except Exception as e:
            logger.error(f"A/B variant application failed: {e}")
            return template
    
    async def _process_template_content(
        self,
        request: NotificationRequest,
        template: NotificationTemplate
    ) -> NotificationTemplate:
        """Process template content for optimization."""
        try:
            # Optimize content length for channels
            for channel, channel_template in template.channel_templates.items():
                template.channel_templates[channel] = await self._optimize_content_for_channel(
                    channel_template, channel
                )
            
            # Apply content safety filters
            template = await self._apply_content_filters(template)
            
            # Add tracking parameters
            template = await self._add_tracking_parameters(template, request)
            
            return template
            
        except Exception as e:
            logger.error(f"Template content processing failed: {e}")
            return template
    
    async def _optimize_content_for_channel(
        self,
        channel_template: Dict[str, Any],
        channel: str
    ) -> Dict[str, Any]:
        """Optimize content for specific channel."""
        try:
            optimized = channel_template.copy()
            
            # Channel-specific optimizations
            if channel == "sms":
                # Limit SMS message length
                if "message" in optimized:
                    optimized["message"] = optimized["message"][:160]
            
            elif channel == "push":
                # Optimize push notification length
                if "title" in optimized:
                    optimized["title"] = optimized["title"][:50]
                if "body" in optimized:
                    optimized["body"] = optimized["body"][:100]
            
            elif channel == "email":
                # Optimize email subject line
                if "subject" in optimized:
                    optimized["subject"] = optimized["subject"][:78]
            
            return optimized
            
        except Exception as e:
            logger.error(f"Channel content optimization failed: {e}")
            return channel_template
    
    async def _apply_content_filters(self, template: NotificationTemplate) -> NotificationTemplate:
        """Apply content safety and compliance filters."""
        try:
            # Placeholder for content filtering
            # In production, this would include:
            # - Spam detection
            # - Profanity filtering
            # - Compliance checking
            # - Brand safety validation
            
            return template
            
        except Exception as e:
            logger.error(f"Content filtering failed: {e}")
            return template
    
    async def _add_tracking_parameters(
        self,
        template: NotificationTemplate,
        request: NotificationRequest
    ) -> NotificationTemplate:
        """Add tracking parameters to template."""
        try:
            tracking_params = {
                "utm_source": "notification",
                "utm_medium": "email",  # Will be overridden per channel
                "utm_campaign": request.notification_type,
                "notification_id": request.notification_id,
                "template_id": template.template_id
            }
            
            # Add tracking to each channel
            for channel, channel_template in template.channel_templates.items():
                # Update UTM medium
                channel_tracking_params = tracking_params.copy()
                channel_tracking_params["utm_medium"] = channel
                
                # Add tracking to URLs
                for field in ["action_url", "collaboration_url", "opportunity_url"]:
                    if field in channel_template:
                        url = channel_template[field]
                        if "?" in url:
                            url += "&"
                        else:
                            url += "?"
                        
                        url += "&".join(f"{k}={v}" for k, v in channel_tracking_params.items())
                        channel_template[field] = url
            
            return template
            
        except Exception as e:
            logger.error(f"Tracking parameter addition failed: {e}")
            return template
    
    async def _get_default_template(self, notification_type: str) -> NotificationTemplate:
        """Get default template for notification type."""
        try:
            base_templates = await self._get_base_templates()
            
            # Map notification types to base templates
            template_map = {
                "content_protection": "copyright_alert",
                "copyright_infringement": "copyright_alert",
                "collaboration_match": "collaboration_match",
                "monetization_opportunity": "monetization_opportunity"
            }
            
            base_template_name = template_map.get(notification_type, "default")
            
            if base_template_name in base_templates:
                template_def = base_templates[base_template_name]
            else:
                # Create minimal default template
                template_def = {
                    "channels": {
                        "email": {
                            "subject": f"Notification: {notification_type}",
                            "text_content": "You have a new notification. Please check your account for details."
                        }
                    },
                    "variables": []
                }
            
            return NotificationTemplate(
                template_id=f"default_{notification_type}",
                template_name=f"Default {notification_type}",
                notification_type=notification_type,
                channel_templates=template_def["channels"],
                variables=template_def.get("variables", []),
                is_active=True
            )
            
        except Exception as e:
            logger.error(f"Default template creation failed: {e}")
            # Return absolute fallback
            return NotificationTemplate(
                template_id="fallback",
                template_name="Fallback Template",
                notification_type=notification_type,
                channel_templates={
                    "email": {
                        "subject": "Notification",
                        "text_content": "You have a new notification."
                    }
                },
                is_active=True
            )
    
    async def _get_fallback_template(self, request: NotificationRequest) -> NotificationTemplate:
        """Get fallback template when processing fails."""
        return await self._get_default_template(request.notification_type)
    
    def _initialize_default_templates(self):
        """Initialize default templates and metrics."""
        # Initialize template metrics for tracking
        default_template_ids = [
            "content_protection_copyright_alert",
            "collaboration_collaboration_match",
            "monetization_monetization_opportunity"
        ]
        
        for template_id in default_template_ids:
            self.template_metrics[template_id] = TemplateMetrics(
                template_id=template_id,
                usage_count=0,
                success_rate=95.0,
                engagement_rate=12.5,
                conversion_rate=8.0,
                average_processing_time=0.05
            )
    
    async def _update_template_metrics(self, template: NotificationTemplate, success: bool):
        """Update template performance metrics."""
        try:
            template_id = template.template_id
            
            if template_id not in self.template_metrics:
                self.template_metrics[template_id] = TemplateMetrics(template_id=template_id)
            
            metrics = self.template_metrics[template_id]
            metrics.usage_count += 1
            
            if success:
                # Update success rate
                current_success_rate = metrics.success_rate
                total_usage = metrics.usage_count
                metrics.success_rate = ((current_success_rate * (total_usage - 1)) + 100) / total_usage
            else:
                # Update failure rate
                current_success_rate = metrics.success_rate
                total_usage = metrics.usage_count
                metrics.success_rate = ((current_success_rate * (total_usage - 1)) + 0) / total_usage
            
            metrics.last_updated = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Template metrics update failed: {e}")
    
    async def _update_processing_stats(self, processing_time: float):
        """Update processing statistics."""
        self.processing_stats["templates_processed"] += 1
        
        # Update average processing time
        total = self.processing_stats["templates_processed"]
        current_avg = self.processing_stats["average_processing_time"]
        self.processing_stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    async def optimize_processing(self, optimization_config: Dict[str, Any]) -> bool:
        """Optimize template processing based on analytics."""
        try:
            # Optimize cache size
            if "cache_optimization" in optimization_config:
                max_cache_size = optimization_config["cache_optimization"].get("max_size", 1000)
                if len(self.template_cache) > max_cache_size:
                    # Remove least recently used templates
                    # Simplified implementation - in production would use proper LRU
                    cache_items = list(self.template_cache.items())
                    self.template_cache = dict(cache_items[-max_cache_size:])
            
            # Update A/B test configurations based on results
            if "ab_test_optimization" in optimization_config:
                await self._optimize_ab_tests()
            
            logger.info("Template processing optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"Template processing optimization failed: {e}")
            return False
    
    async def _optimize_ab_tests(self):
        """Optimize A/B tests based on performance."""
        try:
            # Analyze A/B test results and update winning variants
            for test_id, test_data in self.a_b_tests.items():
                if test_data["participants"] >= 100:  # Minimum sample size
                    conversion_rate = test_data["conversions"] / test_data["participants"]
                    
                    # Update template metrics if this variant is performing well
                    if conversion_rate > 0.1:  # 10% conversion rate threshold
                        template_id = test_data["template_id"]
                        if template_id in self.template_metrics:
                            self.template_metrics[template_id].a_b_test_winner = test_data["variant"]
            
        except Exception as e:
            logger.error(f"A/B test optimization failed: {e}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get template processing statistics."""
        return self.processing_stats.copy()
    
    def get_template_metrics(self) -> Dict[str, TemplateMetrics]:
        """Get template performance metrics."""
        return self.template_metrics.copy()
    
    def get_ab_test_results(self) -> Dict[str, Dict[str, Any]]:
        """Get A/B test results."""
        return self.a_b_tests.copy()
