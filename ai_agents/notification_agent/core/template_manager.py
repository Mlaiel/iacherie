"""Advanced Template Manager - Intelligent Notification Template Management System

This module provides sophisticated notification template management for the IA Influencer Agent platform,
handling AI-driven template generation, personalization, multi-language support, and dynamic content adaptation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import re
from jinja2 import Environment, BaseLoader, TemplateError, select_autoescape
from collections import defaultdict

from ...models.notification_models import (
    NotificationModel, NotificationChannel, NotificationTemplate,
    TemplateVariable, TemplateMetrics
)
from ...ai.templating.template_generator import AITemplateGenerator
from ...ai.personalization.template_personalizer import TemplatePersonalizer
from ...business.template_business import TemplateBusinessLogic
from ...database.template_repository import TemplateRepository
from ...monitoring.template_monitoring import TemplateMonitoringService


class TemplateType(Enum):
    """Comprehensive template types for IA Influencer platform"""    CONTENT_UPLOAD_CONFIRMATION = "content_upload_confirmation"
    AI_PROTECTION_ALERT = "ai_protection_alert"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    COLLABORATION_INVITATION = "collaboration_invitation"
    COLLABORATION_MATCH = "collaboration_match"
    MONETIZATION_OPPORTUNITY = "monetization_opportunity"
    SEO_OPTIMIZATION_REPORT = "seo_optimization_report"
    DISTRIBUTION_STATUS = "distribution_status"
    SECURITY_ALERT = "security_alert"
    PAYMENT_NOTIFICATION = "payment_notification"
    USER_ENGAGEMENT_REPORT = "user_engagement_report"
    PLATFORM_UPDATE = "platform_update"
    ANALYTICS_DIGEST = "analytics_digest"
    WELCOME_SERIES = "welcome_series"
    RETENTION_CAMPAIGN = "retention_campaign"


class TemplateFormat(Enum):
    """Template output formats"""    HTML = "html"
    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"
    JSON = "json"
    RICH_TEXT = "rich_text"


class TemplateLanguage(Enum):
    """Supported template languages"""    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"


@dataclass
class TemplateContext:
    """Rich context for template rendering"""    user_id: str
    user_profile: Dict[str, Any] = field(default_factory=dict)
    content_data: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    personalization_data: Dict[str, Any] = field(default_factory=dict)
    localization_data: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    collaboration_context: Dict[str, Any] = field(default_factory=dict)
    monetization_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemplateConfiguration:
    """Advanced template configuration"""    template_id: str
    template_type: TemplateType
    supported_formats: List[TemplateFormat]
    supported_languages: List[TemplateLanguage]
    personalization_enabled: bool = True
    ai_enhancement_enabled: bool = True
    a_b_testing_enabled: bool = True
    dynamic_content_enabled: bool = True
    multi_channel_optimized: bool = True
    performance_tracking_enabled: bool = True
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RenderedTemplate:
    """Rendered template with metadata"""    template_id: str
    rendered_content: Dict[str, str]  # Format -> content mapping
    metadata: Dict[str, Any]
    personalization_applied: bool
    language: TemplateLanguage
    channel_optimizations: Dict[NotificationChannel, Dict[str, str]]
    performance_hints: Dict[str, Any]
    render_time_ms: float
    ai_confidence: float


class TemplateManager:
    """    Advanced notification template management system
    
    Features:
    - AI-driven template generation and personalization
    - Multi-language and multi-format support
    - Dynamic content adaptation based on user context
    - A/B testing and performance optimization
    - Channel-specific template optimization
    - Real-time template performance analytics
    - Business logic integration for content creators
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.ai_generator = AITemplateGenerator(config.get('ai_generator', {}))
        self.personalizer = TemplatePersonalizer(config.get('personalizer', {}))
        self.business_logic = TemplateBusinessLogic(config.get('business_logic', {}))
        self.repository = TemplateRepository(config.get('database', {}))
        self.monitoring = TemplateMonitoringService(config.get('monitoring', {}))
        
        # Template engine
        self.jinja_env = self._initialize_jinja_environment()
        
        # Template storage
        self.template_cache: Dict[str, NotificationTemplate] = {}
        self.rendered_cache: Dict[str, RenderedTemplate] = {}
        
        # A/B testing framework
        self.ab_test_manager = self._initialize_ab_testing()
        
        # Performance tracking
        self.template_metrics: Dict[str, TemplateMetrics] = {}
        self.performance_analytics = defaultdict(list)
        
        # Multi-language support
        self.translation_service = self._initialize_translation_service()
        
        # Template variants for different channels
        self.channel_templates: Dict[NotificationChannel, Dict[str, str]] = defaultdict(dict)
        
    def _initialize_jinja_environment(self) -> Environment:
        """Initialize Jinja2 template environment with custom filters and functions"""        try:
            env = Environment(
                loader=BaseLoader(),
                autoescape=select_autoescape(['html', 'xml']),
                enable_async=True
            )
            
            # Add custom filters
            env.filters['format_currency'] = self._format_currency_filter
            env.filters['format_date'] = self._format_date_filter
            env.filters['truncate_smart'] = self._truncate_smart_filter
            env.filters['capitalize_smart'] = self._capitalize_smart_filter
            env.filters['sanitize_html'] = self._sanitize_html_filter
            
            # Add custom functions
            env.globals['get_user_preference'] = self._get_user_preference
            env.globals['get_localized_string'] = self._get_localized_string
            env.globals['generate_tracking_url'] = self._generate_tracking_url
            env.globals['get_ai_recommendation'] = self._get_ai_recommendation
            
            return env
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Jinja environment: {str(e)}")
            return Environment(loader=BaseLoader())
            
    def _initialize_ab_testing(self):
        """Initialize A/B testing framework"""        from ...analytics.ab_testing import ABTestManager
        return ABTestManager(self.config.get('ab_testing', {}))
        
    def _initialize_translation_service(self):
        """Initialize translation service for multi-language support"""        from ...ai.translation.translation_service import TranslationService
        return TranslationService(self.config.get('translation', {}))
        
    async def start_manager(self):
        """Start template manager with all background services"""        try:
            self.logger.info("Starting TemplateManager")
            
            # Load templates from repository
            await self._load_templates_from_repository()
            
            # Start background tasks
            self.background_tasks = [
                asyncio.create_task(self._optimize_template_performance()),
                asyncio.create_task(self._cleanup_expired_cache()),
                asyncio.create_task(self._update_template_metrics()),
                asyncio.create_task(self._generate_template_insights())
            ]
            
            # Initialize monitoring
            await self.monitoring.start_monitoring()
            
            self.logger.info("TemplateManager started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start TemplateManager: {str(e)}")
            return False
            
    async def stop_manager(self):
        """Stop template manager gracefully"""        try:
            self.logger.info("Stopping TemplateManager")
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
                
            # Save updated templates
            await self._save_templates_to_repository()
            
            # Stop monitoring
            await self.monitoring.stop_monitoring()
            
            self.logger.info("TemplateManager stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping TemplateManager: {str(e)}")
            return False
            
    async def create_template(
        self,
        template_type: TemplateType,
        base_content: Dict[str, str],
        configuration: TemplateConfiguration
    ) -> str:
        """Create new template with AI enhancement"""        try:
            template_id = str(uuid.uuid4())
            
            # Generate AI-enhanced content
            enhanced_content = await self.ai_generator.enhance_template_content(
                template_type, base_content, configuration
            )
            
            # Create template variants for different channels
            channel_variants = await self._create_channel_variants(
                enhanced_content, configuration
            )
            
            # Generate multi-language versions
            language_variants = await self._create_language_variants(
                enhanced_content, configuration.supported_languages
            )
            
            # Create template object
            template = NotificationTemplate(
                id=template_id,
                type=template_type.value,
                content=enhanced_content,
                channel_variants=channel_variants,
                language_variants=language_variants,
                configuration=configuration,
                created_at=datetime.utcnow(),
                version=configuration.version
            )
            
            # Store template
            self.template_cache[template_id] = template
            await self.repository.save_template(template)
            
            # Initialize metrics
            self.template_metrics[template_id] = TemplateMetrics(
                template_id=template_id,
                usage_count=0,
                success_rate=0.0,
                engagement_rate=0.0,
                conversion_rate=0.0
            )
            
            self.logger.info(f"Template created successfully: {template_id}")
            return template_id
            
        except Exception as e:
            self.logger.error(f"Failed to create template: {str(e)}")
            raise
            
    async def render_template(
        self,
        template_id: str,
        context: TemplateContext,
        target_format: TemplateFormat = TemplateFormat.HTML,
        target_language: TemplateLanguage = TemplateLanguage.ENGLISH,
        target_channel: Optional[NotificationChannel] = None
    ) -> RenderedTemplate:
        """Render template with advanced personalization and optimization"""        try:
            start_time = datetime.utcnow()
            
            # Get template
            template = await self._get_template(template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
                
            # Apply A/B testing if enabled
            if template.configuration.a_b_testing_enabled:
                template = await self.ab_test_manager.get_test_variant(template_id, context.user_id)
                
            # Apply personalization
            personalized_content = await self._apply_personalization(template, context)
            
            # Apply localization
            localized_content = await self._apply_localization(
                personalized_content, target_language, context
            )
            
            # Apply channel-specific optimization
            if target_channel:
                optimized_content = await self._apply_channel_optimization(
                    localized_content, target_channel, template
                )
            else:
                optimized_content = localized_content
                
            # Render final content
            rendered_content = await self._render_content(
                optimized_content, context, target_format
            )
            
            # Generate channel-specific versions
            channel_optimizations = await self._generate_channel_optimizations(
                rendered_content, template, context
            )
            
            # Calculate render time
            render_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create rendered template result
            rendered_template = RenderedTemplate(
                template_id=template_id,
                rendered_content={target_format.value: rendered_content},
                metadata={
                    'template_type': template.type,
                    'personalization_applied': template.configuration.personalization_enabled,
                    'ai_enhanced': template.configuration.ai_enhancement_enabled,
                    'context_user_id': context.user_id
                },
                personalization_applied=template.configuration.personalization_enabled,
                language=target_language,
                channel_optimizations=channel_optimizations,
                performance_hints=await self._generate_performance_hints(template, context),
                render_time_ms=render_time,
                ai_confidence=0.9  # Placeholder
            )
            
            # Cache rendered template
            cache_key = f"{template_id}_{context.user_id}_{target_format.value}_{target_language.value}"
            self.rendered_cache[cache_key] = rendered_template
            
            # Update metrics
            await self._update_template_usage_metrics(template_id)
            
            self.logger.debug(f"Template rendered: {template_id} ({render_time:.2f}ms)")
            return rendered_template
            
        except Exception as e:
            self.logger.error(f"Template rendering failed: {str(e)}")
            raise
            
    async def get_template_performance(self, template_id: str) -> Dict[str, Any]:
        """Get comprehensive template performance analytics"""        try:
            metrics = self.template_metrics.get(template_id)
            if not metrics:
                return {"error": "Template metrics not found"}
                
            # Get historical performance data
            historical_data = await self.monitoring.get_template_performance_history(template_id)
            
            # Calculate performance trends
            trends = await self._calculate_performance_trends(template_id, historical_data)
            
            # Get A/B test results if available
            ab_test_results = await self.ab_test_manager.get_test_results(template_id)
            
            return {
                "template_id": template_id,
                "current_metrics": {
                    "usage_count": metrics.usage_count,
                    "success_rate": metrics.success_rate,
                    "engagement_rate": metrics.engagement_rate,
                    "conversion_rate": metrics.conversion_rate,
                    "last_updated": metrics.last_updated.isoformat()
                },
                "performance_trends": trends,
                "ab_test_results": ab_test_results,
                "recommendations": await self._generate_optimization_recommendations(template_id)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get template performance: {str(e)}")
            return {"error": str(e)}
            
    async def optimize_template(
        self,
        template_id: str,
        optimization_goals: List[str]
    ) -> bool:
        """AI-driven template optimization based on performance data"""        try:
            # Get current template and performance data
            template = await self._get_template(template_id)
            if not template:
                return False
                
            performance_data = await self.get_template_performance(template_id)
            
            # Generate optimized content using AI
            optimized_content = await self.ai_generator.optimize_template_content(
                template, performance_data, optimization_goals
            )
            
            # Create optimized template version
            new_version = f"{template.version}_optimized_{datetime.utcnow().strftime('%Y%m%d')}"
            optimized_template = template
            optimized_template.content = optimized_content
            optimized_template.version = new_version
            optimized_template.updated_at = datetime.utcnow()
            
            # Set up A/B test between original and optimized versions
            if template.configuration.a_b_testing_enabled:
                await self.ab_test_manager.create_test(
                    template_id,
                    [template, optimized_template],
                    test_duration_days=7
                )
            else:
                # Replace original template with optimized version
                self.template_cache[template_id] = optimized_template
                await self.repository.update_template(optimized_template)
                
            self.logger.info(f"Template optimized: {template_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Template optimization failed: {str(e)}")
            return False
            
    async def _get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get template from cache or repository"""        try:
            # Check cache first
            if template_id in self.template_cache:
                return self.template_cache[template_id]
                
            # Load from repository
            template = await self.repository.get_template(template_id)
            if template:
                self.template_cache[template_id] = template
                
            return template
            
        except Exception as e:
            self.logger.error(f"Failed to get template {template_id}: {str(e)}")
            return None
            
    async def _create_channel_variants(
        self,
        content: Dict[str, str],
        configuration: TemplateConfiguration
    ) -> Dict[str, Dict[str, str]]:
        """Create channel-specific template variants"""        try:
            variants = {}
            
            # Email variant
            variants['email'] = await self._create_email_variant(content)
            
            # SMS variant  
            variants['sms'] = await self._create_sms_variant(content)
            
            # Push notification variant
            variants['push'] = await self._create_push_variant(content)
            
            # In-app variant
            variants['in_app'] = await self._create_in_app_variant(content)
            
            return variants
            
        except Exception as e:
            self.logger.error(f"Failed to create channel variants: {str(e)}")
            return {}
            
    async def _create_email_variant(self, content: Dict[str, str]) -> Dict[str, str]:
        """Create email-optimized template variant"""        return {
            'subject': content.get('title', 'Notification'),
            'html_body': f"""            <html>
                <body>
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h1 style="color: #333;">{content.get('title', '')}</h1>
                        <p>{content.get('message', '')}</p>
                        {f'<p><a href="{content.get("action_url", "")}" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">{content.get("action_text", "Learn More")}</a></p>' if content.get('action_url') else ''}
                        <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
                        <p style="color: #666; font-size: 12px;">
                            This message was sent by IA Influencer Agent. 
                            <a href="#unsubscribe" style="color: #666;">Unsubscribe</a>
                        </p>
                    </div>
                </body>
            </html>
            """,
            'text_body': f"""            {content.get('title', '')}
            
            {content.get('message', '')}
            
            {f'Action: {content.get("action_url", "")}' if content.get('action_url') else ''}
            
            ---
            This message was sent by IA Influencer Agent.
            """        }
        
    async def _create_sms_variant(self, content: Dict[str, str]) -> Dict[str, str]:
        """Create SMS-optimized template variant"""        message = content.get('title', '') + ': ' + content.get('message', '')
        
        # Truncate to SMS limits
        if len(message) > 160:
            message = message[:157] + "..."
            
        return {
            'message': message,
            'short_url': content.get('action_url', '')[:50] if content.get('action_url') else ''
        }
        
    async def _create_push_variant(self, content: Dict[str, str]) -> Dict[str, str]:
        """Create push notification optimized template variant"""        return {
            'title': content.get('title', '')[:50],  # Push title limit
            'body': content.get('message', '')[:200],  # Push body limit
            'icon': content.get('icon', '/default-icon.png'),
            'action_url': content.get('action_url', ''),
            'badge': content.get('badge', '1')
        }
        
    async def _create_in_app_variant(self, content: Dict[str, str]) -> Dict[str, str]:
        """Create in-app notification optimized template variant"""        return {
            'title': content.get('title', ''),
            'message': content.get('message', ''),
            'rich_content': content.get('rich_content', {}),
            'actions': content.get('actions', []),
            'priority_indicator': content.get('priority', 'medium')
        }
        
    async def _create_language_variants(
        self,
        content: Dict[str, str],
        languages: List[TemplateLanguage]
    ) -> Dict[str, Dict[str, str]]:
        """Create multi-language template variants"""        try:
            variants = {}
            
            for language in languages:
                if language == TemplateLanguage.ENGLISH:
                    # English is the base language
                    variants[language.value] = content
                else:
                    # Translate to target language
                    translated_content = await self.translation_service.translate_content(
                        content, target_language=language.value
                    )
                    variants[language.value] = translated_content
                    
            return variants
            
        except Exception as e:
            self.logger.error(f"Failed to create language variants: {str(e)}")
            return {'en': content}  # Fallback to English only
            
    async def _apply_personalization(
        self,
        template: NotificationTemplate,
        context: TemplateContext
    ) -> Dict[str, str]:
        """Apply AI-driven personalization to template content"""        try:
            if not template.configuration.personalization_enabled:
                return template.content
                
            # Get user-specific personalization data
            personalized_content = await self.personalizer.personalize_content(
                template.content,
                context.user_profile,
                context.personalization_data,
                context.ai_insights
            )
            
            return personalized_content
            
        except Exception as e:
            self.logger.error(f"Personalization failed: {str(e)}")
            return template.content
            
    async def _apply_localization(
        self,
        content: Dict[str, str],
        target_language: TemplateLanguage,
        context: TemplateContext
    ) -> Dict[str, str]:
        """Apply localization and cultural adaptation"""        try:
            if target_language == TemplateLanguage.ENGLISH:
                return content
                
            # Translate content
            localized_content = await self.translation_service.localize_content(
                content,
                target_language.value,
                context.localization_data
            )
            
            return localized_content
            
        except Exception as e:
            self.logger.error(f"Localization failed: {str(e)}")
            return content
            
    async def _apply_channel_optimization(
        self,
        content: Dict[str, str],
        channel: NotificationChannel,
        template: NotificationTemplate
    ) -> Dict[str, str]:
        """Apply channel-specific content optimization"""        try:
            # Get channel-specific variant
            channel_variant = template.channel_variants.get(channel.value, content)
            
            # Apply channel-specific optimizations
            if channel == NotificationChannel.EMAIL:
                return await self._optimize_for_email(channel_variant)
            elif channel == NotificationChannel.SMS:
                return await self._optimize_for_sms(channel_variant)
            elif channel == NotificationChannel.PUSH:
                return await self._optimize_for_push(channel_variant)
            else:
                return channel_variant
                
        except Exception as e:
            self.logger.error(f"Channel optimization failed: {str(e)}")
            return content
            
    async def _optimize_for_email(self, content: Dict[str, str]) -> Dict[str, str]:
        """Optimize content specifically for email delivery"""        optimized = content.copy()
        
        # Ensure proper email structure
        if 'html_body' not in optimized and 'message' in optimized:
            optimized['html_body'] = f"<p>{optimized['message']}</p>"
            
        if 'text_body' not in optimized and 'message' in optimized:
            optimized['text_body'] = optimized['message']
            
        # Add email-specific elements
        if 'subject' not in optimized and 'title' in optimized:
            optimized['subject'] = optimized['title']
            
        return optimized
        
    async def _optimize_for_sms(self, content: Dict[str, str]) -> Dict[str, str]:
        """Optimize content specifically for SMS delivery"""        optimized = content.copy()
        
        # Ensure message fits SMS constraints
        if 'message' in optimized and len(optimized['message']) > 160:
            optimized['message'] = optimized['message'][:157] + "..."
            
        return optimized
        
    async def _optimize_for_push(self, content: Dict[str, str]) -> Dict[str, str]:
        """Optimize content specifically for push notifications"""        optimized = content.copy()
        
        # Ensure push notification constraints
        if 'title' in optimized and len(optimized['title']) > 50:
            optimized['title'] = optimized['title'][:47] + "..."
            
        if 'body' in optimized and len(optimized['body']) > 200:
            optimized['body'] = optimized['body'][:197] + "..."
            
        return optimized
        
    async def _render_content(
        self,
        content: Dict[str, str],
        context: TemplateContext,
        target_format: TemplateFormat
    ) -> str:
        """Render final content using Jinja2 template engine"""        try:
            # Get content for target format
            template_content = content.get(target_format.value, content.get('message', ''))
            
            # Create Jinja2 template
            template = self.jinja_env.from_string(template_content)
            
            # Prepare context variables
            render_context = {
                'user': context.user_profile,
                'content': context.content_data,
                'business': context.business_context,
                'personalization': context.personalization_data,
                'localization': context.localization_data,
                'ai_insights': context.ai_insights,
                'collaboration': context.collaboration_context,
                'monetization': context.monetization_context,
                'current_time': datetime.utcnow(),
                'format': target_format.value
            }
            
            # Render template
            rendered_content = await template.render_async(**render_context)
            
            return rendered_content
            
        except TemplateError as e:
            self.logger.error(f"Jinja2 template rendering failed: {str(e)}")
            return content.get('message', 'Error rendering template')
        except Exception as e:
            self.logger.error(f"Content rendering failed: {str(e)}")
            return content.get('message', 'Error rendering template')
            
    async def _generate_channel_optimizations(
        self,
        rendered_content: str,
        template: NotificationTemplate,
        context: TemplateContext
    ) -> Dict[NotificationChannel, Dict[str, str]]:
        """Generate optimized versions for all supported channels"""        try:
            optimizations = {}
            
            # Generate optimization for each channel
            for channel in NotificationChannel:
                try:
                    channel_content = await self._apply_channel_optimization(
                        {'message': rendered_content}, channel, template
                    )
                    optimizations[channel] = channel_content
                except Exception as e:
                    self.logger.error(f"Failed to optimize for {channel.value}: {str(e)}")
                    optimizations[channel] = {'message': rendered_content}
                    
            return optimizations
            
        except Exception as e:
            self.logger.error(f"Failed to generate channel optimizations: {str(e)}")
            return {}
            
    async def _generate_performance_hints(
        self,
        template: NotificationTemplate,
        context: TemplateContext
    ) -> Dict[str, Any]:
        """Generate performance optimization hints"""        try:
            hints = {
                'recommended_channels': [],
                'optimal_send_time': None,
                'personalization_effectiveness': 0.8,
                'expected_engagement_rate': 0.15,
                'content_quality_score': 0.9
            }
            
            # Analyze user profile for channel recommendations
            user_preferences = context.user_profile.get('notification_preferences', {})
            if 'preferred_channels' in user_preferences:
                hints['recommended_channels'] = user_preferences['preferred_channels']
            else:
                # Default recommendations based on template type
                if template.type == 'security_alert':
                    hints['recommended_channels'] = ['sms', 'email', 'push']
                elif template.type == 'collaboration_match':
                    hints['recommended_channels'] = ['email', 'push']
                else:
                    hints['recommended_channels'] = ['email']
                    
            # Determine optimal send time
            user_timezone = context.user_profile.get('timezone', 'UTC')
            user_activity_patterns = context.user_profile.get('activity_patterns', {})
            
            if user_activity_patterns:
                # Use user's historical activity data
                peak_hours = user_activity_patterns.get('peak_hours', [9, 14, 18])
                hints['optimal_send_time'] = peak_hours[0] if peak_hours else 9
            else:
                # Use general best practices
                hints['optimal_send_time'] = 10  # 10 AM general optimal time
                
            return hints
            
        except Exception as e:
            self.logger.error(f"Performance hints generation failed: {str(e)}")
            return {}
            
    async def _update_template_usage_metrics(self, template_id: str):
        """Update template usage metrics"""        try:
            if template_id in self.template_metrics:
                self.template_metrics[template_id].usage_count += 1
                self.template_metrics[template_id].last_updated = datetime.utcnow()
                
                # Record usage in monitoring service
                await self.monitoring.record_template_usage(template_id)
                
        except Exception as e:
            self.logger.error(f"Failed to update template metrics: {str(e)}")
            
    # Jinja2 custom filters and functions
    def _format_currency_filter(self, amount: float, currency: str = 'USD') -> str:
        """Format currency values"""        try:
            if currency == 'USD':
                return f"${amount:,.2f}"
            elif currency == 'EUR':
                return f"€{amount:,.2f}"
            else:
                return f"{amount:,.2f} {currency}"
        except Exception:
            return str(amount)
            
    def _format_date_filter(self, date: datetime, format_str: str = '%Y-%m-%d') -> str:
        """Format date values"""        try:
            if isinstance(date, str):
                date = datetime.fromisoformat(date)
            return date.strftime(format_str)
        except Exception:
            return str(date)
            
    def _truncate_smart_filter(self, text: str, length: int = 100) -> str:
        """Smart truncation that preserves word boundaries"""        try:
            if len(text) <= length:
                return text
            
            # Find the last space before the length limit
            truncated = text[:length]
            last_space = truncated.rfind(' ')
            
            if last_space > 0:
                return truncated[:last_space] + "..."
            else:
                return truncated + "..."
        except Exception:
            return text
            
    def _capitalize_smart_filter(self, text: str) -> str:
        """Smart capitalization that handles various cases"""        try:
            # Split by common delimiters and capitalize each part
            words = re.split(r'([\s\-_]+)', text)
            capitalized = [word.capitalize() if word.isalpha() else word for word in words]
            return ''.join(capitalized)
        except Exception:
            return text
            
    def _sanitize_html_filter(self, text: str) -> str:
        """Sanitize HTML content"""        try:
            # Remove potentially dangerous HTML tags
            import html
            sanitized = html.escape(text)
            return sanitized
        except Exception:
            return text
            
    async def _get_user_preference(self, user_id: str, preference_key: str, default=None):
        """Get user preference value"""        try:
            # This would typically query a user preferences service
            # For now, return default
            return default
        except Exception:
            return default
            
    async def _get_localized_string(self, key: str, language: str = 'en', **kwargs):
        """Get localized string"""        try:
            # This would typically query a localization service
            # For now, return the key
            return key
        except Exception:
            return key
            
    def _generate_tracking_url(self, base_url: str, campaign: str, user_id: str) -> str:
        """Generate tracking URL for analytics"""        try:
            import urllib.parse
            
            tracking_params = {
                'utm_campaign': campaign,
                'utm_source': 'ia_influencer_agent',
                'user_id': user_id,
                'timestamp': str(int(datetime.utcnow().timestamp()))
            }
            
            query_string = urllib.parse.urlencode(tracking_params)
            separator = '&' if '?' in base_url else '?'
            
            return f"{base_url}{separator}{query_string}"
        except Exception:
            return base_url
            
    async def _get_ai_recommendation(self, context_type: str, user_data: Dict[str, Any]):
        """Get AI-driven recommendation"""        try:
            # This would typically call an AI recommendation service
            # For now, return a placeholder
            return f"AI recommendation for {context_type}"
        except Exception:
            return ""
            
    # Background task methods
    async def _optimize_template_performance(self):
        """Background task to optimize template performance"""        while True:
            try:
                # Analyze template performance and optimize underperforming templates
                for template_id, metrics in self.template_metrics.items():
                    if metrics.usage_count > 10 and metrics.engagement_rate < 0.1:
                        # Template is underperforming, optimize it
                        await self.optimize_template(template_id, ['engagement', 'conversion'])
                        
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Template optimization task error: {str(e)}")
                await asyncio.sleep(3600)
                
    async def _cleanup_expired_cache(self):
        """Background task to cleanup expired cache entries"""        while True:
            try:
                current_time = datetime.utcnow()
                expired_keys = []
                
                # Find expired rendered templates (cache for 1 hour)
                for key, rendered_template in self.rendered_cache.items():
                    # Extract timestamp from cache (would need to store timestamp in real implementation)
                    # For now, assume all cache entries older than 1 hour are expired
                    # This is a simplified implementation
                    pass
                    
                # Remove expired entries
                for key in expired_keys:
                    del self.rendered_cache[key]
                    
                if expired_keys:
                    self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
                # Sleep for 30 minutes
                await asyncio.sleep(1800)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cache cleanup task error: {str(e)}")
                await asyncio.sleep(1800)
                
    async def _update_template_metrics(self):
        """Background task to update template metrics"""        while True:
            try:
                # Update metrics for all templates
                for template_id in self.template_metrics.keys():
                    # Get fresh metrics from monitoring service
                    fresh_metrics = await self.monitoring.get_template_metrics(template_id)
                    if fresh_metrics:
                        self.template_metrics[template_id] = fresh_metrics
                        
                # Sleep for 15 minutes
                await asyncio.sleep(900)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics update task error: {str(e)}")
                await asyncio.sleep(900)
                
    async def _generate_template_insights(self):
        """Background task to generate template insights"""        while True:
            try:
                # Generate insights for template performance
                insights = {
                    'top_performing_templates': [],
                    'underperforming_templates': [],
                    'optimization_opportunities': [],
                    'trending_content_patterns': []
                }
                
                # Analyze template metrics
                sorted_templates = sorted(
                    self.template_metrics.items(),
                    key=lambda x: x[1].engagement_rate,
                    reverse=True
                )
                
                # Top performing (top 10%)
                top_count = max(1, len(sorted_templates) // 10)
                insights['top_performing_templates'] = [
                    template_id for template_id, _ in sorted_templates[:top_count]
                ]
                
                # Underperforming (bottom 20% with significant usage)
                bottom_candidates = [
                    (template_id, metrics) for template_id, metrics in sorted_templates
                    if metrics.usage_count > 5
                ]
                bottom_count = max(1, len(bottom_candidates) // 5)
                insights['underperforming_templates'] = [
                    template_id for template_id, _ in bottom_candidates[-bottom_count:]
                ]
                
                # Store insights
                await self.monitoring.store_template_insights(insights)
                
                # Sleep for 6 hours
                await asyncio.sleep(21600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Template insights generation error: {str(e)}")
                await asyncio.sleep(21600)
                
    async def _load_templates_from_repository(self):
        """Load all templates from repository into cache"""        try:
            templates = await self.repository.get_all_templates()
            
            for template in templates:
                self.template_cache[template.id] = template
                
                # Initialize metrics if not exists
                if template.id not in self.template_metrics:
                    self.template_metrics[template.id] = TemplateMetrics(
                        template_id=template.id,
                        usage_count=0,
                        success_rate=0.0,
                        engagement_rate=0.0,
                        conversion_rate=0.0
                    )
                    
            self.logger.info(f"Loaded {len(templates)} templates from repository")
            
        except Exception as e:
            self.logger.error(f"Failed to load templates from repository: {str(e)}")
            
    async def _save_templates_to_repository(self):
        """Save all cached templates to repository"""        try:
            save_count = 0
            
            for template in self.template_cache.values():
                await self.repository.update_template(template)
                save_count += 1
                
            self.logger.info(f"Saved {save_count} templates to repository")
            
        except Exception as e:
            self.logger.error(f"Failed to save templates to repository: {str(e)}")
            
    async def _calculate_performance_trends(
        self,
        template_id: str,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate performance trends for a template"""        try:
            if not historical_data:
                return {}
                
            # Calculate trends (simplified implementation)
            trends = {
                'usage_trend': 'stable',
                'engagement_trend': 'stable',
                'conversion_trend': 'stable',
                'performance_score_trend': 'stable'
            }
            
            # Analyze recent vs historical performance
            if len(historical_data) >= 2:
                recent = historical_data[-1]
                older = historical_data[0]
                
                # Usage trend
                if recent['usage_count'] > older['usage_count'] * 1.1:
                    trends['usage_trend'] = 'increasing'
                elif recent['usage_count'] < older['usage_count'] * 0.9:
                    trends['usage_trend'] = 'decreasing'
                    
                # Engagement trend
                if recent['engagement_rate'] > older['engagement_rate'] * 1.05:
                    trends['engagement_trend'] = 'improving'
                elif recent['engagement_rate'] < older['engagement_rate'] * 0.95:
                    trends['engagement_trend'] = 'declining'
                    
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to calculate performance trends: {str(e)}")
            return {}
            
    async def _generate_optimization_recommendations(
        self,
        template_id: str
    ) -> List[str]:
        """Generate optimization recommendations for a template"""        try:
            recommendations = []
            
            metrics = self.template_metrics.get(template_id)
            if not metrics:
                return recommendations
                
            # Low engagement recommendations
            if metrics.engagement_rate < 0.1:
                recommendations.extend([
                    "Consider more personalized content",
                    "Try different subject lines or headlines",
                    "Add interactive elements or call-to-actions",
                    "Review content relevance for target audience"
                ])
                
            # Low conversion recommendations
            if metrics.conversion_rate < 0.05:
                recommendations.extend([
                    "Strengthen call-to-action messaging",
                    "Simplify the user journey",
                    "Test different value propositions",
                    "Improve content clarity and focus"
                ])
                
            # High usage but low performance
            if metrics.usage_count > 50 and metrics.engagement_rate < 0.15:
                recommendations.append("High-volume template needs optimization - consider A/B testing")
                
            # General recommendations if no specific issues
            if not recommendations:
                recommendations.extend([
                    "Template performing well - consider minor optimizations",
                    "Test alternative content variations",
                    "Monitor for seasonal performance patterns"
                ])
                
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization recommendations: {str(e)}")
            return []


class MessageGenerator:
    """    Advanced message generation system with AI-powered content creation
    """    
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
        self.logger = logging.getLogger(__name__)
        
    async def generate_message_from_template(
        self,
        template_id: str,
        context: TemplateContext,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate complete message from template with full optimization"""        try:
            # Set defaults from preferences
            target_format = TemplateFormat(preferences.get('format', 'html')) if preferences else TemplateFormat.HTML
            target_language = TemplateLanguage(preferences.get('language', 'en')) if preferences else TemplateLanguage.ENGLISH
            target_channel = NotificationChannel(preferences.get('channel')) if preferences and preferences.get('channel') else None
            
            # Render template
            rendered_template = await self.template_manager.render_template(
                template_id, context, target_format, target_language, target_channel
            )
            
            return {
                'success': True,
                'template_id': template_id,
                'content': rendered_template.rendered_content,
                'channel_optimizations': rendered_template.channel_optimizations,
                'metadata': rendered_template.metadata,
                'performance_hints': rendered_template.performance_hints,
                'render_time_ms': rendered_template.render_time_ms
            }
            
        except Exception as e:
            self.logger.error(f"Message generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'template_id': template_id
            }
            
    async def generate_dynamic_message(
        self,
        message_type: str,
        context: TemplateContext,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate dynamic message without predefined template"""        try:
            # Create dynamic template based on message type
            dynamic_template_id = await self._create_dynamic_template(message_type, context)
            
            # Generate message using dynamic template
            return await self.generate_message_from_template(
                dynamic_template_id, context, preferences
            )
            
        except Exception as e:
            self.logger.error(f"Dynamic message generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message_type': message_type
            }
            
    async def _create_dynamic_template(
        self,
        message_type: str,
        context: TemplateContext
    ) -> str:
        """Create dynamic template based on message type and context"""        try:
            # Map message type to template type
            template_type_mapping = {
                'welcome': TemplateType.WELCOME_SERIES,
                'collaboration_invite': TemplateType.COLLABORATION_INVITATION,
                'security_alert': TemplateType.SECURITY_ALERT,
                'monetization_opportunity': TemplateType.MONETIZATION_OPPORTUNITY,
                'content_upload': TemplateType.CONTENT_UPLOAD_CONFIRMATION
            }
            
            template_type = template_type_mapping.get(message_type, TemplateType.PLATFORM_UPDATE)
            
            # Generate basic content
            base_content = await self._generate_base_content(message_type, context)
            
            # Create template configuration
            config = TemplateConfiguration(
                template_id=f"dynamic_{message_type}_{datetime.utcnow().timestamp()}",
                template_type=template_type,
                supported_formats=[TemplateFormat.HTML, TemplateFormat.PLAIN_TEXT],
                supported_languages=[TemplateLanguage.ENGLISH],
                personalization_enabled=True,
                ai_enhancement_enabled=True
            )
            
            # Create template
            template_id = await self.template_manager.create_template(
                template_type, base_content, config
            )
            
            return template_id
            
        except Exception as e:
            self.logger.error(f"Dynamic template creation failed: {str(e)}")
            raise
            
    async def _generate_base_content(
        self,
        message_type: str,
        context: TemplateContext
    ) -> Dict[str, str]:
        """Generate base content for dynamic templates"""        content_templates = {
            'welcome': {
                'title': 'Welcome to IA Influencer Agent!',
                'message': 'Hello {{ user.name | default("Creator") }}! Welcome to our platform. We\'re excited to help you protect and monetize your content.',
                'action_text': 'Get Started',
                'action_url': 'https://app.ia-influencer.com/onboarding'
            },
            'collaboration_invite': {
                'title': 'New Collaboration Opportunity',
                'message': 'Hi {{ user.name | default("Creator") }}! We found a collaboration opportunity that matches your interests in {{ collaboration.category | default("your field") }}.',
                'action_text': 'View Opportunity',
                'action_url': '{{ collaboration.url | default("#") }}'
            },
            'security_alert': {
                'title': 'Security Alert: Action Required',
                'message': 'We detected {{ security.alert_type | default("unusual activity") }} on your account. Please review and take action immediately.',
                'action_text': 'Review Security',
                'action_url': 'https://app.ia-influencer.com/security'
            },
            'monetization_opportunity': {
                'title': 'New Monetization Opportunity',
                'message': 'Great news! Your content "{{ content.title | default("your recent upload") }}" has monetization potential of ${{ monetization.estimated_revenue | default("0") }}.',
                'action_text': 'Enable Monetization',
                'action_url': '{{ monetization.setup_url | default("#") }}'
            }
        }
        
        return content_templates.get(message_type, {
            'title': 'Notification',
            'message': 'You have a new notification from IA Influencer Agent.',
            'action_text': 'View Details',
            'action_url': 'https://app.ia-influencer.com/notifications'
        })


@dataclass
class TemplateConfiguration:
    """Advanced template configuration"""    id: str
    name: str
    description: str
    template_type: TemplateType
    supported_channels: List[NotificationChannel]
    supported_formats: List[TemplateFormat]
    supported_languages: List[TemplateLanguage]
    variables: List[TemplateVariable]
    personalization_rules: Dict[str, Any]
    ai_generation_config: Dict[str, Any]
    business_rules: Dict[str, Any]
    content_variants: Dict[str, Dict[str, str]]  # channel -> format -> template
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metrics: TemplateMetrics = field(default_factory=lambda: TemplateMetrics())


@dataclass
class RenderedTemplate:
    """Result of template rendering"""    template_id: str
    rendered_content: Dict[str, str]  # format -> content
    used_variables: Dict[str, Any]
    personalization_applied: List[str]
    language: TemplateLanguage
    channel: NotificationChannel
    rendering_time: float
    ai_confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemplateLoader(BaseLoader):
    """Custom Jinja2 template loader for notification templates"""    
    def __init__(self, templates: Dict[str, str]):
        self.templates = templates
        
    def get_source(self, environment, template):
        if template not in self.templates:
            raise TemplateError(f"Template not found: {template}")
            
        source = self.templates[template]
        return source, None, lambda: True


class TemplateManager:
    """    Advanced notification template management system
    
    Features:
    - AI-driven template generation and optimization
    - Multi-language and multi-format support
    - Dynamic personalization based on user profiles
    - A/B testing for template effectiveness
    - Business logic integration for content creators
    - Real-time template performance monitoring
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.repository = TemplateRepository(config.get('database_config', {}))
        self.ai_generator = AITemplateGenerator(config.get('ai_generator_config', {}))
        self.personalizer = TemplatePersonalizer(config.get('personalizer_config', {}))
        self.business_logic = TemplateBusinessLogic(config.get('business_config', {}))
        self.monitoring = TemplateMonitoringService(config.get('monitoring_config', {}))
        
        # Template storage and caching
        self.templates: Dict[str, TemplateConfiguration] = {}
        self.template_cache: Dict[str, RenderedTemplate] = {}
        self.cache_ttl = config.get('cache_ttl', 3600)  # 1 hour default
        
        # Template rendering engine
        self.jinja_env = Environment(
            loader=TemplateLoader({}),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Performance tracking
        self.performance_metrics = {
            'total_rendered': 0,
            'total_generated': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_rendering_time': 0.0,
            'personalization_success_rate': 0.0
        }
        
        # A/B testing framework
        self.ab_tests: Dict[str, Dict[str, Any]] = {}
        self.test_results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Multi-language support
        self.language_models = {}
        self.translation_cache = {}
        
    async def initialize_manager(self):
        """Initialize the template manager with all components"""        try:
            self.logger.info("Initializing TemplateManager with AI-driven capabilities")
            
            # Initialize repository
            await self.repository.initialize()
            
            # Initialize AI components
            await self.ai_generator.initialize()
            await self.personalizer.initialize()
            
            # Load existing templates
            await self._load_templates()
            
            # Initialize language models
            await self._initialize_language_models()
            
            # Start monitoring
            await self.monitoring.start_monitoring()
            
            # Start background tasks
            self.background_tasks = [
                asyncio.create_task(self._optimize_templates()),
                asyncio.create_task(self._cleanup_cache()),
                asyncio.create_task(self._process_ab_tests()),
                asyncio.create_task(self._update_performance_metrics())
            ]
            
            self.logger.info("TemplateManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TemplateManager: {str(e)}")
            return False
            
    async def create_template(
        self,
        name: str,
        template_type: TemplateType,
        supported_channels: List[NotificationChannel],
        template_content: Optional[Dict[str, str]] = None,
        personalization_rules: Optional[Dict[str, Any]] = None,
        ai_generated: bool = True
    ) -> str:
        """        Create new notification template with AI assistance
        
        Args:
            name: Template name
            template_type: Type of template
            supported_channels: Channels this template supports
            template_content: Optional predefined content
            personalization_rules: Rules for personalization
            ai_generated: Whether to use AI generation
            
        Returns:
            template_id: Unique template identifier
        """        try:
            template_id = str(uuid.uuid4())
            
            # Generate template content using AI if not provided
            if not template_content and ai_generated:
                template_content = await self._ai_generate_template_content(
                    template_type, supported_channels
                )
                
            # Create template variables
            variables = await self._extract_template_variables(template_content)
            
            # Create template configuration
            template_config = TemplateConfiguration(
                id=template_id,
                name=name,
                description=f"AI-generated template for {template_type.value}",
                template_type=template_type,
                supported_channels=supported_channels,
                supported_formats=[TemplateFormat.HTML, TemplateFormat.PLAIN_TEXT],
                supported_languages=[TemplateLanguage.ENGLISH],  # Default, can be extended
                variables=variables,
                personalization_rules=personalization_rules or {},
                ai_generation_config=self.ai_generator.get_config_for_type(template_type),
                business_rules=await self.business_logic.get_rules_for_type(template_type),
                content_variants=template_content or {}
            )
            
            # Store template
            self.templates[template_id] = template_config
            await self.repository.save_template(template_config)
            
            # Update Jinja2 loader
            await self._update_template_loader()
            
            self.performance_metrics['total_generated'] += 1
            
            self.logger.info(f"Template created: {template_id} ({name})")
            return template_id
            
        except Exception as e:
            self.logger.error(f"Failed to create template: {str(e)}")
            raise
            
    async def render_template(
        self,
        template_id: str,
        context: TemplateContext,
        channel: NotificationChannel,
        format_type: TemplateFormat = TemplateFormat.HTML,
        language: TemplateLanguage = TemplateLanguage.ENGLISH
    ) -> RenderedTemplate:
        """        Render template with advanced personalization and localization
        
        Args:
            template_id: Template to render
            context: Rich context for rendering
            channel: Target channel
            format_type: Output format
            language: Target language
            
        Returns:
            Rendered template with metadata
        """        try:
            start_time = datetime.utcnow()
            
            # Check cache first
            cache_key = self._generate_cache_key(
                template_id, context, channel, format_type, language
            )
            
            cached_result = self.template_cache.get(cache_key)
            if cached_result and self._is_cache_valid(cached_result):
                self.performance_metrics['cache_hits'] += 1
                return cached_result
                
            self.performance_metrics['cache_misses'] += 1
            
            # Get template configuration
            template_config = self.templates.get(template_id)
            if not template_config:
                raise ValueError(f"Template not found: {template_id}")
                
            # Validate channel and format support
            if channel not in template_config.supported_channels:
                raise ValueError(f"Template does not support channel: {channel.value}")
                
            if format_type not in template_config.supported_formats:
                raise ValueError(f"Template does not support format: {format_type.value}")
                
            # Apply personalization
            personalized_context = await self.personalizer.personalize_context(
                context, template_config, channel
            )
            
            # Apply business logic
            business_enhanced_context = await self.business_logic.enhance_context(
                personalized_context, template_config
            )
            
            # Handle localization
            if language != TemplateLanguage.ENGLISH:
                business_enhanced_context = await self._localize_context(
                    business_enhanced_context, language
                )
                
            # Render template
            rendered_content = await self._render_jinja_template(
                template_config, business_enhanced_context, channel, format_type
            )
            
            # Calculate rendering time
            rendering_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create rendered template object
            rendered_template = RenderedTemplate(
                template_id=template_id,
                rendered_content={format_type.value: rendered_content},
                used_variables=self._extract_used_variables(business_enhanced_context),
                personalization_applied=personalized_context.get('personalization_applied', []),
                language=language,
                channel=channel,
                rendering_time=rendering_time,
                ai_confidence=self.personalizer.get_last_confidence_score(),
                metadata={
                    'template_name': template_config.name,
                    'template_type': template_config.template_type.value,
                    'rendered_at': datetime.utcnow().isoformat()
                }
            )
            
            # Cache result
            self.template_cache[cache_key] = rendered_template
            
            # Update metrics
            self.performance_metrics['total_rendered'] += 1
            self._update_rendering_time_metric(rendering_time)
            
            # Record for monitoring
            await self.monitoring.record_template_rendering(
                template_id, rendered_template
            )
            
            return rendered_template
            
        except Exception as e:
            self.logger.error(f"Template rendering failed: {str(e)}")
            raise
            
    async def personalize_template_content(
        self,
        template_id: str,
        user_profile: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Apply advanced personalization to template content
        
        Args:
            template_id: Template to personalize
            user_profile: User profile data
            context: Additional context
            
        Returns:
            Personalized content variations
        """        try:
            template_config = self.templates.get(template_id)
            if not template_config:
                raise ValueError(f"Template not found: {template_id}")
                
            # Apply AI-driven personalization
            personalized_variants = await self.personalizer.generate_personalized_variants(
                template_config, user_profile, context
            )
            
            # Apply business logic rules
            business_filtered_variants = await self.business_logic.filter_personalized_content(
                personalized_variants, user_profile, template_config
            )
            
            return business_filtered_variants
            
        except Exception as e:
            self.logger.error(f"Template personalization failed: {str(e)}")
            return {}
            
    async def create_ab_test(
        self,
        test_name: str,
        template_variants: List[str],
        test_config: Dict[str, Any]
    ) -> str:
        """        Create A/B test for template effectiveness
        
        Args:
            test_name: Name of the A/B test
            template_variants: List of template IDs to test
            test_config: Test configuration
            
        Returns:
            test_id: Unique test identifier
        """        try:
            test_id = str(uuid.uuid4())
            
            # Validate template variants
            for template_id in template_variants:
                if template_id not in self.templates:
                    raise ValueError(f"Template not found: {template_id}")
                    
            # Create A/B test configuration
            ab_test_config = {
                'test_id': test_id,
                'test_name': test_name,
                'template_variants': template_variants,
                'test_config': test_config,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active',
                'participants': 0,
                'results': {}
            }
            
            self.ab_tests[test_id] = ab_test_config
            
            # Save to repository
            await self.repository.save_ab_test(ab_test_config)
            
            self.logger.info(f"A/B test created: {test_id} ({test_name})")
            return test_id
            
        except Exception as e:
            self.logger.error(f"Failed to create A/B test: {str(e)}")
            raise
            
    async def get_template_for_ab_test(
        self,
        test_id: str,
        user_id: str
    ) -> Optional[str]:
        """        Get template variant for A/B test participant
        
        Args:
            test_id: A/B test ID
            user_id: User ID for consistent assignment
            
        Returns:
            template_id: Template variant for this user
        """        try:
            ab_test = self.ab_tests.get(test_id)
            if not ab_test or ab_test['status'] != 'active':
                return None
                
            # Consistent assignment based on user ID hash
            user_hash = hash(user_id) % len(ab_test['template_variants'])
            template_id = ab_test['template_variants'][user_hash]
            
            # Record participation
            ab_test['participants'] += 1
            
            return template_id
            
        except Exception as e:
            self.logger.error(f"Failed to get A/B test template: {str(e)}")
            return None
            
    async def record_ab_test_result(
        self,
        test_id: str,
        template_id: str,
        user_id: str,
        action: str,
        value: float = 1.0
    ) -> bool:
        """        Record A/B test result for analysis
        
        Args:
            test_id: A/B test ID
            template_id: Template variant used
            user_id: User who performed action
            action: Action performed (e.g., 'click', 'conversion')
            value: Value of the action
            
        Returns:
            success: Whether result was recorded
        """        try:
            ab_test = self.ab_tests.get(test_id)
            if not ab_test:
                return False
                
            # Record result
            result_record = {
                'test_id': test_id,
                'template_id': template_id,
                'user_id': user_id,
                'action': action,
                'value': value,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.test_results[test_id].append(result_record)
            
            # Update test results summary
            if template_id not in ab_test['results']:
                ab_test['results'][template_id] = {
                    'total_actions': 0,
                    'total_value': 0.0,
                    'action_types': defaultdict(int)
                }
                
            ab_test['results'][template_id]['total_actions'] += 1
            ab_test['results'][template_id]['total_value'] += value
            ab_test['results'][template_id]['action_types'][action] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record A/B test result: {str(e)}")
            return False
            
    async def analyze_ab_test_results(
        self,
        test_id: str
    ) -> Dict[str, Any]:
        """        Analyze A/B test results and determine winner
        
        Args:
            test_id: A/B test ID
            
        Returns:
            Analysis results with winner determination
        """        try:
            ab_test = self.ab_tests.get(test_id)
            if not ab_test:
                return {"error": "A/B test not found"}
                
            results = ab_test['results']
            if not results:
                return {"error": "No results available"}
                
            # Calculate performance metrics for each variant
            variant_performance = {}
            
            for template_id, variant_results in results.items():
                total_actions = variant_results['total_actions']
                total_value = variant_results['total_value']
                
                if total_actions > 0:
                    average_value = total_value / total_actions
                    variant_performance[template_id] = {
                        'total_actions': total_actions,
                        'total_value': total_value,
                        'average_value': average_value,
                        'action_breakdown': dict(variant_results['action_types']),
                        'performance_score': average_value * total_actions  # Combined metric
                    }
                    
            # Determine winner
            winner = None
            best_score = 0
            
            for template_id, performance in variant_performance.items():
                if performance['performance_score'] > best_score:
                    best_score = performance['performance_score']
                    winner = template_id
                    
            # Calculate statistical significance (simplified)
            confidence_level = 0.0
            if len(variant_performance) == 2:  # Only for two-variant tests
                confidence_level = await self._calculate_statistical_significance(
                    list(variant_performance.values())
                )
                
            analysis_results = {
                'test_id': test_id,
                'test_name': ab_test['test_name'],
                'participants': ab_test['participants'],
                'variant_performance': variant_performance,
                'winner': winner,
                'winner_performance': variant_performance.get(winner, {}),
                'confidence_level': confidence_level,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'recommendation': await self._generate_ab_test_recommendation(
                    winner, variant_performance, confidence_level
                )
            }
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"A/B test analysis failed: {str(e)}")
            return {"error": str(e)}
            
    async def get_template_analytics(
        self,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Get comprehensive template analytics
        
        Args:
            template_id: Specific template ID (all templates if None)
            
        Returns:
            Template analytics data
        """        try:
            if template_id:
                # Single template analytics
                template_config = self.templates.get(template_id)
                if not template_config:
                    return {"error": "Template not found"}
                    
                return {
                    'template_id': template_id,
                    'template_name': template_config.name,
                    'template_type': template_config.template_type.value,
                    'metrics': template_config.metrics.__dict__,
                    'performance': await self.monitoring.get_template_performance(template_id),
                    'personalization_stats': await self.personalizer.get_template_stats(template_id)
                }
            else:
                # System-wide analytics
                total_templates = len(self.templates)
                active_templates = sum(1 for t in self.templates.values() if t.is_active)
                
                return {
                    'system_metrics': self.performance_metrics.copy(),
                    'template_count': {
                        'total': total_templates,
                        'active': active_templates,
                        'inactive': total_templates - active_templates
                    },
                    'template_types': self._analyze_template_types(),
                    'ab_tests': {
                        'total': len(self.ab_tests),
                        'active': sum(1 for test in self.ab_tests.values() if test['status'] == 'active')
                    },
                    'language_support': self._analyze_language_support(),
                    'channel_support': self._analyze_channel_support()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get template analytics: {str(e)}")
            return {"error": str(e)}
            
    async def _ai_generate_template_content(
        self,
        template_type: TemplateType,
        supported_channels: List[NotificationChannel]
    ) -> Dict[str, str]:
        """Generate template content using AI"""        try:
            # Define generation parameters based on template type and channels
            generation_params = {
                'template_type': template_type.value,
                'channels': [ch.value for ch in supported_channels],
                'business_context': 'ia_influencer_platform',
                'tone': await self._determine_template_tone(template_type),
                'personalization_level': 'high'
            }
            
            # Generate content variants for each channel
            content_variants = {}
            
            for channel in supported_channels:
                # Generate HTML version
                html_content = await self.ai_generator.generate_template(
                    template_type, channel, TemplateFormat.HTML, generation_params
                )
                
                # Generate plain text version
                text_content = await self.ai_generator.generate_template(
                    template_type, channel, TemplateFormat.PLAIN_TEXT, generation_params
                )
                
                content_variants[channel.value] = {
                    'html': html_content,
                    'plain_text': text_content
                }
                
            return content_variants
            
        except Exception as e:
            self.logger.error(f"AI template generation failed: {str(e)}")
            return {}
            
    async def _determine_template_tone(self, template_type: TemplateType) -> str:
        """Determine appropriate tone for template type"""        tone_mapping = {
            TemplateType.SECURITY_ALERT: 'urgent_professional',
            TemplateType.COPYRIGHT_INFRINGEMENT: 'formal_legal',
            TemplateType.COLLABORATION_INVITATION: 'friendly_professional',
            TemplateType.MONETIZATION_OPPORTUNITY: 'exciting_professional',
            TemplateType.WELCOME_SERIES: 'warm_friendly',
            TemplateType.CONTENT_UPLOAD_CONFIRMATION: 'encouraging_professional',
            TemplateType.ANALYTICS_DIGEST: 'informative_professional'
        }
        
        return tone_mapping.get(template_type, 'professional')
        
    async def _extract_template_variables(
        self,
        template_content: Dict[str, str]
    ) -> List[TemplateVariable]:
        """Extract variables from template content"""        try:
            variables = set()
            
            # Pattern to match Jinja2 variables: {{ variable_name }}
            variable_pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
            
            # Extract from all content variants
            for channel_content in template_content.values():
                if isinstance(channel_content, dict):
                    for format_content in channel_content.values():
                        found_vars = re.findall(variable_pattern, format_content)
                        variables.update(found_vars)
                else:
                    found_vars = re.findall(variable_pattern, channel_content)
                    variables.update(found_vars)
                    
            # Create TemplateVariable objects
            template_variables = []
            for var_name in variables:
                template_variables.append(
                    TemplateVariable(
                        name=var_name,
                        type=self._infer_variable_type(var_name),
                        required=self._is_variable_required(var_name),
                        default_value=None,
                        description=f"Auto-extracted variable: {var_name}"
                    )
                )
                
            return template_variables
            
        except Exception as e:
            self.logger.error(f"Variable extraction failed: {str(e)}")
            return []
            
    def _infer_variable_type(self, var_name: str) -> str:
        """Infer variable type from name"""        if any(keyword in var_name.lower() for keyword in ['name', 'title', 'subject']):
            return 'string'
        elif any(keyword in var_name.lower() for keyword in ['count', 'number', 'amount']):
            return 'integer'
        elif any(keyword in var_name.lower() for keyword in ['date', 'time', 'timestamp']):
            return 'datetime'
        elif any(keyword in var_name.lower() for keyword in ['url', 'link', 'href']):
            return 'url'
        elif any(keyword in var_name.lower() for keyword in ['email', 'mail']):
            return 'email'
        else:
            return 'string'  # Default type
            
    def _is_variable_required(self, var_name: str) -> bool:
        """Determine if variable is required based on name"""        required_keywords = ['name', 'id', 'user', 'title', 'subject']
        return any(keyword in var_name.lower() for keyword in required_keywords)


class MessageGenerator:
    """    Advanced message generator with AI-powered content creation
    """    
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
        self.logger = logging.getLogger(__name__)
        self.generation_cache = {}
        
    async def generate_personalized_message(
        self,
        template_type: TemplateType,
        user_profile: Dict[str, Any],
        context: Dict[str, Any],
        channel: NotificationChannel,
        language: TemplateLanguage = TemplateLanguage.ENGLISH
    ) -> Dict[str, Any]:
        """        Generate fully personalized message using AI and templates
        
        Args:
            template_type: Type of message to generate
            user_profile: User profile for personalization
            context: Message context
            channel: Target delivery channel
            language: Target language
            
        Returns:
            Generated personalized message
        """        try:
            # Find appropriate template
            template_id = await self._find_best_template(
                template_type, channel, user_profile
            )
            
            if not template_id:
                # Generate new template if none exists
                template_id = await self.template_manager.create_template(
                    name=f"AI Generated {template_type.value}",
                    template_type=template_type,
                    supported_channels=[channel],
                    ai_generated=True
                )
                
            # Create template context
            template_context = TemplateContext(
                user_id=user_profile.get('user_id', 'unknown'),
                user_profile=user_profile,
                content_data=context.get('content_data', {}),
                business_context=context.get('business_context', {}),
                personalization_data=context.get('personalization_data', {}),
                ai_insights=context.get('ai_insights', {})
            )
            
            # Render template
            rendered_template = await self.template_manager.render_template(
                template_id=template_id,
                context=template_context,
                channel=channel,
                format_type=TemplateFormat.HTML,
                language=language
            )
            
            # Generate additional variants if needed
            variants = await self._generate_message_variants(
                rendered_template, user_profile, context
            )
            
            return {
                'primary_message': rendered_template.rendered_content,
                'variants': variants,
                'personalization_applied': rendered_template.personalization_applied,
                'template_id': template_id,
                'confidence': rendered_template.ai_confidence,
                'metadata': rendered_template.metadata
            }
            
        except Exception as e:
            self.logger.error(f"Message generation failed: {str(e)}")
            return {
                'error': str(e),
                'fallback_message': await self._generate_fallback_message(
                    template_type, channel
                )
            }
            
    async def _find_best_template(
        self,
        template_type: TemplateType,
        channel: NotificationChannel,
        user_profile: Dict[str, Any]
    ) -> Optional[str]:
        """Find the best template for given criteria"""        try:
            # Get all templates of the specified type
            matching_templates = [
                template_id for template_id, config in self.template_manager.templates.items()
                if config.template_type == template_type and channel in config.supported_channels
            ]
            
            if not matching_templates:
                return None
                
            # If multiple templates, select based on performance or A/B test
            if len(matching_templates) == 1:
                return matching_templates[0]
            else:
                # Select based on metrics or A/B test assignment
                best_template = await self._select_best_performing_template(
                    matching_templates, user_profile
                )
                return best_template
                
        except Exception as e:
            self.logger.error(f"Template selection failed: {str(e)}")
            return None
            
    async def _generate_message_variants(
        self,
        base_template: RenderedTemplate,
        user_profile: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate message variants for testing"""        try:
            variants = []
            
            # Generate tone variations
            tone_variants = await self.template_manager.ai_generator.generate_tone_variants(
                base_template.rendered_content,
                ['formal', 'casual', 'enthusiastic', 'urgent']
            )
            
            variants.extend(tone_variants)
            
            # Generate length variations
            length_variants = await self.template_manager.ai_generator.generate_length_variants(
                base_template.rendered_content,
                ['short', 'medium', 'long']
            )
            
            variants.extend(length_variants)
            
            return variants[:5]  # Limit to 5 variants
            
        except Exception as e:
            self.logger.error(f"Variant generation failed: {str(e)}")
            return []
            
    async def _generate_fallback_message(
        self,
        template_type: TemplateType,
        channel: NotificationChannel
    ) -> Dict[str, str]:
        """Generate simple fallback message"""        fallback_messages = {
            TemplateType.CONTENT_UPLOAD_CONFIRMATION: {
                'subject': 'Content Upload Successful',
                'message': 'Your content has been successfully uploaded to the IA Influencer platform.'
            },
            TemplateType.COLLABORATION_INVITATION: {
                'subject': 'New Collaboration Opportunity',
                'message': 'You have a new collaboration opportunity waiting for you.'
            },
            TemplateType.SECURITY_ALERT: {
                'subject': 'Security Alert',
                'message': 'Important security notification regarding your account.'
            }
        }
        
        return fallback_messages.get(template_type, {
            'subject': 'Notification',
            'message': 'You have a new notification from IA Influencer.'
        })
