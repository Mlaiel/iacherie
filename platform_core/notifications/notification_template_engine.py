"""🚀 Notification Template Engine - AI Personalization Enterprise
================================================================
Module: platform_core/notifications/notification_template_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 NOTIFICATION TEMPLATE ENGINE - AI PERSONALIZATION
- Templates dynamiques avec variables contextuelles
- Personnalisation IA selon behavior créateurs
- Multi-langue avec traduction automatique
- A/B testing templates automatique
- Machine learning pour optimization engagement
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from jinja2 import Template, Environment, FileSystemLoader, StrictUndefined
import openai
from deep_translator import GoogleTranslator
import redis.asyncio as redis
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Template types for different notification channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class PersonalizationLevel(Enum):
    """AI personalization levels."""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PREMIUM = "premium"


class TemplateStatus(Enum):
    """Template status."""
    DRAFT = "draft"
    ACTIVE = "active"
    TESTING = "testing"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class LanguageCode(Enum):
    """Supported language codes."""
    EN = "en"
    FR = "fr"
    DE = "de"
    ES = "es"
    AR = "ar"
    ZH = "zh"
    JA = "ja"
    RU = "ru"


@dataclass
class TemplateVariable:
    """Template variable definition."""
    name: str
    type: str  # string, number, boolean, date, object, array
    required: bool = True
    default_value: Any = None
    description: Optional[str] = None
    validation_pattern: Optional[str] = None
    ai_enhanced: bool = False  # Whether to apply AI enhancement to this variable


@dataclass
class PersonalizationRule:
    """AI personalization rule."""
    id: str
    name: str
    condition: str  # JSON path or expression
    transformation: str  # AI transformation prompt
    priority: int = 1
    active: bool = True


@dataclass
class TemplateVersion:
    """Template version for A/B testing."""
    id: str
    version_number: str
    content: str
    weight: float = 1.0  # Traffic allocation weight
    performance_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True


@dataclass
class MultiLanguageTemplate:
    """Multi-language template content."""
    template_id: str
    language: LanguageCode
    subject: Optional[str] = None
    title: Optional[str] = None
    content: str = ""
    translated_at: Optional[datetime] = None
    auto_translated: bool = False
    reviewed: bool = False


@dataclass
class TemplatePerformanceMetrics:
    """Template performance analytics."""
    template_id: str
    version_id: Optional[str] = None
    sent_count: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    conversion_count: int = 0
    bounce_count: int = 0
    complaint_count: int = 0
    engagement_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationTemplate:
    """Comprehensive notification template."""
    id: str
    name: str
    description: str
    type: TemplateType
    category: str
    subject_template: Optional[str] = None
    title_template: Optional[str] = None
    content_template: str = ""
    variables: List[TemplateVariable] = field(default_factory=list)
    personalization_rules: List[PersonalizationRule] = field(default_factory=list)
    personalization_level: PersonalizationLevel = PersonalizationLevel.STANDARD
    versions: List[TemplateVersion] = field(default_factory=list)
    languages: List[MultiLanguageTemplate] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: TemplateStatus = TemplateStatus.DRAFT
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    performance: Optional[TemplatePerformanceMetrics] = None


@dataclass
class RenderContext:
    """Template rendering context."""
    user_id: str
    user_data: Dict[str, Any] = field(default_factory=dict)
    behavioral_data: Dict[str, Any] = field(default_factory=dict)
    contextual_data: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    language: LanguageCode = LanguageCode.EN
    timezone: Optional[str] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None


@dataclass
class RenderResult:
    """Template rendering result."""
    template_id: str
    version_id: Optional[str] = None
    language: LanguageCode = LanguageCode.EN
    subject: Optional[str] = None
    title: Optional[str] = None
    content: str = ""
    personalization_applied: List[str] = field(default_factory=list)
    ai_enhancements: List[str] = field(default_factory=list)
    variables_used: Dict[str, Any] = field(default_factory=dict)
    render_time_ms: float = 0.0
    quality_score: float = 0.0


class AIPersonalizationEngine:
    """AI-powered personalization engine for templates."""
    
    def __init__(self, openai_api_key: str):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.user_embeddings: Dict[str, np.ndarray] = {}
        
    async def enhance_content(self, content: str, user_context: RenderContext, 
                            enhancement_type: str = "tone") -> str:
        """Enhance content using AI based on user context."""
        try:
            # Build enhancement prompt based on user data
            prompt = self._build_enhancement_prompt(content, user_context, enhancement_type)
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert content personalization assistant for a creator economy platform."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            enhanced_content = response.choices[0].message.content.strip()
            return enhanced_content
            
        except Exception as e:
            logger.error(f"AI content enhancement failed: {e}")
            return content
    
    def _build_enhancement_prompt(self, content: str, context: RenderContext, 
                                enhancement_type: str) -> str:
        """Build AI enhancement prompt."""
        user_profile = self._extract_user_profile(context)
        
        if enhancement_type == "tone":
            return f"""
            Personalize this notification content to match the user's profile and preferences:
            
            Original Content: "{content}"
            
            User Profile:
            - Engagement Level: {user_profile.get('engagement_level', 'medium')}
            - Content Preferences: {user_profile.get('content_preferences', [])}
            - Communication Style: {user_profile.get('communication_style', 'professional')}
            - Activity Pattern: {user_profile.get('activity_pattern', 'regular')}
            
            Instructions:
            1. Adjust tone to match user's communication style
            2. Use terminology familiar to their content niche
            3. Maintain the core message while personalizing delivery
            4. Keep the same length as original
            5. Ensure the content remains professional and engaging
            
            Return only the enhanced content without explanations.
            """
        
        elif enhancement_type == "timing":
            return f"""
            Optimize this notification content for optimal engagement timing:
            
            Original Content: "{content}"
            
            User Timing Context:
            - Active Hours: {user_profile.get('active_hours', '9-17')}
            - Timezone: {context.timezone or 'UTC'}
            - Response Patterns: {user_profile.get('response_patterns', 'immediate')}
            
            Adjust the content to be more compelling for this timing context.
            Return only the optimized content.
            """
        
        return content
    
    def _extract_user_profile(self, context: RenderContext) -> Dict[str, Any]:
        """Extract user profile for AI enhancement."""
        profile = {}
        
        # Extract engagement level
        behavioral_data = context.behavioral_data
        if behavioral_data.get('email_open_rate', 0) > 0.7:
            profile['engagement_level'] = 'high'
        elif behavioral_data.get('email_open_rate', 0) > 0.3:
            profile['engagement_level'] = 'medium'
        else:
            profile['engagement_level'] = 'low'
        
        # Extract communication style from preferences
        preferences = context.preferences
        profile['communication_style'] = preferences.get('communication_style', 'professional')
        
        # Extract content preferences
        profile['content_preferences'] = context.user_data.get('content_categories', [])
        
        # Extract activity pattern
        if behavioral_data.get('daily_active_sessions', 0) > 5:
            profile['activity_pattern'] = 'high'
        elif behavioral_data.get('daily_active_sessions', 0) > 2:
            profile['activity_pattern'] = 'regular'
        else:
            profile['activity_pattern'] = 'low'
        
        return profile
    
    async def predict_engagement(self, content: str, user_context: RenderContext) -> float:
        """Predict user engagement likelihood using ML."""
        try:
            # Extract features from content and user context
            content_features = self._extract_content_features(content)
            user_features = self._extract_user_features(user_context)
            
            # Simple engagement prediction (in production, use trained ML model)
            base_score = 0.5
            
            # Content quality factors
            if len(content.split()) > 10:  # Reasonable length
                base_score += 0.1
            if any(word in content.lower() for word in ['exclusive', 'limited', 'new', 'update']):
                base_score += 0.1
            if '!' in content:  # Excitement
                base_score += 0.05
            
            # User behavior factors
            behavioral_data = user_context.behavioral_data
            open_rate = behavioral_data.get('email_open_rate', 0.3)
            click_rate = behavioral_data.get('click_rate', 0.1)
            
            engagement_score = base_score * (1 + open_rate) * (1 + click_rate * 2)
            
            return min(engagement_score, 1.0)
            
        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}")
            return 0.5
    
    def _extract_content_features(self, content: str) -> Dict[str, float]:
        """Extract features from content for ML analysis."""
        features = {}
        
        # Basic text metrics
        features['length'] = len(content)
        features['word_count'] = len(content.split())
        features['sentence_count'] = len([s for s in content.split('.') if s.strip()])
        features['exclamation_count'] = content.count('!')
        features['question_count'] = content.count('?')
        
        # Sentiment indicators (simplified)
        positive_words = ['great', 'awesome', 'amazing', 'excellent', 'fantastic', 'wonderful']
        negative_words = ['sorry', 'unfortunately', 'problem', 'issue', 'error', 'failed']
        
        features['positive_sentiment'] = sum(1 for word in positive_words if word in content.lower())
        features['negative_sentiment'] = sum(1 for word in negative_words if word in content.lower())
        
        return features
    
    def _extract_user_features(self, context: RenderContext) -> Dict[str, float]:
        """Extract user features for ML analysis."""
        features = {}
        
        behavioral_data = context.behavioral_data
        features['open_rate'] = behavioral_data.get('email_open_rate', 0.3)
        features['click_rate'] = behavioral_data.get('click_rate', 0.1)
        features['session_count'] = behavioral_data.get('daily_active_sessions', 1)
        
        # Device and platform preferences
        features['mobile_user'] = 1.0 if context.device_type == 'mobile' else 0.0
        features['desktop_user'] = 1.0 if context.device_type == 'desktop' else 0.0
        
        return features


class TranslationEngine:
    """Multi-language translation engine."""
    
    def __init__(self):
        self.translators = {
            lang.value: GoogleTranslator(source='en', target=lang.value)
            for lang in LanguageCode if lang != LanguageCode.EN
        }
        
    async def translate_template(self, template: NotificationTemplate, 
                               target_language: LanguageCode) -> MultiLanguageTemplate:
        """Translate template to target language."""
        try:
            if target_language == LanguageCode.EN:
                # Return original English content
                return MultiLanguageTemplate(
                    template_id=template.id,
                    language=LanguageCode.EN,
                    subject=template.subject_template,
                    title=template.title_template,
                    content=template.content_template,
                    auto_translated=False,
                    reviewed=True
                )
            
            translator = self.translators.get(target_language.value)
            if not translator:
                raise ValueError(f"Translation not supported for language: {target_language.value}")
            
            # Translate content while preserving template variables
            translated_content = await self._translate_with_variables(
                template.content_template, translator
            )
            
            translated_subject = None
            if template.subject_template:
                translated_subject = await self._translate_with_variables(
                    template.subject_template, translator
                )
            
            translated_title = None
            if template.title_template:
                translated_title = await self._translate_with_variables(
                    template.title_template, translator
                )
            
            return MultiLanguageTemplate(
                template_id=template.id,
                language=target_language,
                subject=translated_subject,
                title=translated_title,
                content=translated_content,
                translated_at=datetime.utcnow(),
                auto_translated=True,
                reviewed=False
            )
            
        except Exception as e:
            logger.error(f"Translation failed for {target_language.value}: {e}")
            raise
    
    async def _translate_with_variables(self, text: str, translator) -> str:
        """Translate text while preserving template variables."""
        try:
            # Find all template variables ({{variable_name}})
            variable_pattern = r'\{\{([^}]+)\}\}'
            variables = re.findall(variable_pattern, text)
            
            # Replace variables with placeholders during translation
            placeholder_map = {}
            translated_text = text
            
            for i, var in enumerate(variables):
                placeholder = f"__VAR_{i}__"
                placeholder_map[placeholder] = f"{{{{{var}}}}}"
                translated_text = translated_text.replace(f"{{{{{var}}}}}", placeholder)
            
            # Translate the text
            if translated_text.strip():
                translated = await asyncio.to_thread(translator.translate, translated_text)
            else:
                translated = translated_text
            
            # Restore variables
            for placeholder, original_var in placeholder_map.items():
                translated = translated.replace(placeholder, original_var)
            
            return translated
            
        except Exception as e:
            logger.error(f"Variable-aware translation failed: {e}")
            return text


class TemplateOptimizer:
    """A/B testing and optimization engine for templates."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def create_ab_test(self, template: NotificationTemplate, 
                           variant_content: str, variant_name: str, 
                           traffic_split: float = 0.5) -> str:
        """Create A/B test variant for template."""
        try:
            # Create new version
            variant_id = str(uuid.uuid4())
            variant_version = TemplateVersion(
                id=variant_id,
                version_number=variant_name,
                content=variant_content,
                weight=traffic_split,
                created_at=datetime.utcnow()
            )
            
            # Adjust original version weight
            if template.versions:
                template.versions[0].weight = 1.0 - traffic_split
            
            template.versions.append(variant_version)
            
            # Store A/B test configuration
            ab_test_config = {
                'template_id': template.id,
                'variant_id': variant_id,
                'traffic_split': traffic_split,
                'start_date': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            await self.redis.hset(f"ab_test:{template.id}", mapping=ab_test_config)
            
            logger.info(f"A/B test created for template {template.id} with {traffic_split*100}% traffic")
            return variant_id
            
        except Exception as e:
            logger.error(f"A/B test creation failed: {e}")
            raise
    
    async def select_version_for_user(self, template: NotificationTemplate, 
                                    user_id: str) -> TemplateVersion:
        """Select template version for user using A/B testing."""
        try:
            if not template.versions:
                # Create default version
                default_version = TemplateVersion(
                    id=str(uuid.uuid4()),
                    version_number="default",
                    content=template.content_template,
                    weight=1.0
                )
                return default_version
            
            # Use user ID hash for consistent assignment
            user_hash = hash(user_id) % 100
            
            # Select version based on weights
            cumulative_weight = 0
            for version in template.versions:
                if version.active:
                    cumulative_weight += version.weight * 100
                    if user_hash < cumulative_weight:
                        return version
            
            # Fallback to first active version
            for version in template.versions:
                if version.active:
                    return version
            
            # Fallback to first version
            return template.versions[0]
            
        except Exception as e:
            logger.error(f"Version selection failed: {e}")
            return template.versions[0] if template.versions else None
    
    async def track_performance(self, template_id: str, version_id: str, 
                              event_type: str, user_id: str) -> None:
        """Track template performance metrics."""
        try:
            # Track event
            event_key = f"template_events:{template_id}:{version_id}:{event_type}"
            await self.redis.incr(event_key)
            
            # Track daily events
            today = datetime.utcnow().strftime('%Y-%m-%d')
            daily_key = f"template_daily:{template_id}:{version_id}:{event_type}:{today}"
            await self.redis.incr(daily_key)
            
            # Store individual event for analysis
            event_data = {
                'template_id': template_id,
                'version_id': version_id,
                'event_type': event_type,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.redis.lpush(f"template_event_log:{template_id}", json.dumps(event_data))
            
        except Exception as e:
            logger.error(f"Performance tracking failed: {e}")
    
    async def calculate_performance_score(self, template_id: str, version_id: str) -> float:
        """Calculate performance score for template version."""
        try:
            # Get event counts
            sent_count = await self.redis.get(f"template_events:{template_id}:{version_id}:sent") or 0
            opened_count = await self.redis.get(f"template_events:{template_id}:{version_id}:opened") or 0
            clicked_count = await self.redis.get(f"template_events:{template_id}:{version_id}:clicked") or 0
            converted_count = await self.redis.get(f"template_events:{template_id}:{version_id}:converted") or 0
            
            sent_count = int(sent_count)
            opened_count = int(opened_count)
            clicked_count = int(clicked_count)
            converted_count = int(converted_count)
            
            if sent_count == 0:
                return 0.0
            
            # Calculate rates
            open_rate = opened_count / sent_count
            click_rate = clicked_count / sent_count if sent_count > 0 else 0
            conversion_rate = converted_count / sent_count if sent_count > 0 else 0
            
            # Weighted performance score
            performance_score = (
                open_rate * 0.3 +
                click_rate * 0.4 +
                conversion_rate * 0.3
            )
            
            return min(performance_score, 1.0)
            
        except Exception as e:
            logger.error(f"Performance calculation failed: {e}")
            return 0.0
    
    async def optimize_template(self, template: NotificationTemplate) -> Dict[str, Any]:
        """Provide optimization recommendations for template."""
        try:
            recommendations = []
            
            # Analyze current performance
            if template.versions:
                for version in template.versions:
                    score = await self.calculate_performance_score(template.id, version.id)
                    version.performance_score = score
            
            # Content analysis
            content = template.content_template
            
            # Length recommendations
            if len(content) > 500:
                recommendations.append({
                    'type': 'content_length',
                    'message': 'Consider shortening content for better engagement',
                    'priority': 'medium'
                })
            
            # Call-to-action analysis
            cta_words = ['click', 'visit', 'download', 'sign up', 'get started', 'learn more']
            if not any(word in content.lower() for word in cta_words):
                recommendations.append({
                    'type': 'call_to_action',
                    'message': 'Add a clear call-to-action to improve click rates',
                    'priority': 'high'
                })
            
            # Personalization opportunities
            if '{{' not in content:
                recommendations.append({
                    'type': 'personalization',
                    'message': 'Add personalization variables to increase engagement',
                    'priority': 'medium'
                })
            
            # Performance comparison
            if len(template.versions) > 1:
                versions_by_score = sorted(template.versions, key=lambda v: v.performance_score, reverse=True)
                best_version = versions_by_score[0]
                
                if best_version.performance_score > 0.1:
                    recommendations.append({
                        'type': 'ab_test_winner',
                        'message': f'Version "{best_version.version_number}" is performing {best_version.performance_score:.1%} better',
                        'priority': 'high'
                    })
            
            return {
                'template_id': template.id,
                'recommendations': recommendations,
                'overall_score': template.performance.engagement_score if template.performance else 0.0,
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Template optimization analysis failed: {e}")
            return {'template_id': template.id, 'recommendations': [], 'overall_score': 0.0}


class NotificationTemplateEngine:
    """Enterprise notification template engine with AI personalization."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis = redis.Redis(**config.get('redis', {}))
        
        # Initialize AI engine if OpenAI key provided
        self.ai_engine = None
        if config.get('openai_api_key'):
            self.ai_engine = AIPersonalizationEngine(config['openai_api_key'])
        
        # Initialize translation engine
        self.translation_engine = TranslationEngine()
        
        # Initialize optimizer
        self.optimizer = TemplateOptimizer(self.redis)
        
        # Jinja2 environment for template rendering
        self.jinja_env = Environment(
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Template storage
        self.templates: Dict[str, NotificationTemplate] = {}
        
        # Performance tracking
        self.performance_data: Dict[str, Any] = {}
    
    async def create_template(self, template: NotificationTemplate) -> bool:
        """Create new notification template."""
        try:
            # Validate template
            validation_result = await self._validate_template(template)
            if not validation_result['is_valid']:
                raise ValueError(f"Template validation failed: {validation_result['errors']}")
            
            # Store template
            template.id = template.id or str(uuid.uuid4())
            template.created_at = datetime.utcnow()
            template.updated_at = datetime.utcnow()
            
            # Create default version
            if not template.versions:
                default_version = TemplateVersion(
                    id=str(uuid.uuid4()),
                    version_number="v1.0",
                    content=template.content_template,
                    weight=1.0
                )
                template.versions.append(default_version)
            
            # Store in Redis
            await self._store_template(template)
            
            # Cache in memory
            self.templates[template.id] = template
            
            logger.info(f"Template {template.id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Template creation failed: {e}")
            return False
    
    async def render_template(self, template_id: str, context: RenderContext) -> RenderResult:
        """Render template with AI personalization."""
        start_time = datetime.utcnow()
        
        try:
            # Load template
            template = await self._load_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Select version for A/B testing
            selected_version = await self.optimizer.select_version_for_user(template, context.user_id)
            
            # Get language-specific template
            language_template = await self._get_language_template(template, context.language)
            
            # Prepare variables
            render_variables = await self._prepare_render_variables(template, context)
            
            # Apply AI personalization if enabled
            ai_enhancements = []
            if self.ai_engine and template.personalization_level != PersonalizationLevel.BASIC:
                enhanced_content = await self._apply_ai_personalization(
                    language_template.content, context, template.personalization_rules
                )
                language_template.content = enhanced_content
                ai_enhancements.append("content_personalization")
            
            # Render templates
            rendered_subject = None
            if language_template.subject:
                subject_template = self.jinja_env.from_string(language_template.subject)
                rendered_subject = subject_template.render(**render_variables)
            
            rendered_title = None
            if language_template.title:
                title_template = self.jinja_env.from_string(language_template.title)
                rendered_title = title_template.render(**render_variables)
            
            content_template = self.jinja_env.from_string(language_template.content)
            rendered_content = content_template.render(**render_variables)
            
            # Calculate quality score
            quality_score = await self._calculate_quality_score(rendered_content, context)
            
            # Calculate render time
            render_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Track rendering
            await self.optimizer.track_performance(template_id, selected_version.id, "rendered", context.user_id)
            
            return RenderResult(
                template_id=template_id,
                version_id=selected_version.id,
                language=context.language,
                subject=rendered_subject,
                title=rendered_title,
                content=rendered_content,
                personalization_applied=[rule.name for rule in template.personalization_rules if rule.active],
                ai_enhancements=ai_enhancements,
                variables_used=render_variables,
                render_time_ms=render_time,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return RenderResult(
                template_id=template_id,
                content=f"Error rendering template: {str(e)}",
                quality_score=0.0
            )
    
    async def _validate_template(self, template: NotificationTemplate) -> Dict[str, Any]:
        """Validate template structure and content."""
        errors = []
        warnings = []
        
        # Required fields
        if not template.name:
            errors.append("Template name is required")
        if not template.content_template:
            errors.append("Template content is required")
        
        # Variable validation
        template_content = template.content_template
        if template.subject_template:
            template_content += " " + template.subject_template
        if template.title_template:
            template_content += " " + template.title_template
        
        # Find variables in content
        variable_pattern = r'\{\{([^}]+)\}\}'
        found_variables = set(re.findall(variable_pattern, template_content))
        
        # Check if all variables are defined
        defined_variables = set(var.name for var in template.variables)
        undefined_variables = found_variables - defined_variables
        
        if undefined_variables:
            warnings.append(f"Undefined variables found: {', '.join(undefined_variables)}")
        
        # Check for unused variables
        unused_variables = defined_variables - found_variables
        if unused_variables:
            warnings.append(f"Unused variables defined: {', '.join(unused_variables)}")
        
        # Content quality checks
        if len(template.content_template) < 10:
            warnings.append("Template content is very short")
        
        if len(template.content_template) > 2000:
            warnings.append("Template content is very long")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def _load_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Load template from storage."""
        try:
            # Check memory cache first
            if template_id in self.templates:
                return self.templates[template_id]
            
            # Load from Redis
            template_data = await self.redis.hgetall(f"template:{template_id}")
            if template_data:
                template = self._deserialize_template(template_data)
                self.templates[template_id] = template
                return template
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load template {template_id}: {e}")
            return None
    
    async def _store_template(self, template: NotificationTemplate) -> None:
        """Store template in Redis."""
        try:
            template_data = self._serialize_template(template)
            await self.redis.hset(f"template:{template.id}", mapping=template_data)
            
            # Add to template index
            await self.redis.sadd("template_index", template.id)
            
        except Exception as e:
            logger.error(f"Failed to store template: {e}")
            raise
    
    def _serialize_template(self, template: NotificationTemplate) -> Dict[str, str]:
        """Serialize template for storage."""
        try:
            data = {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'type': template.type.value,
                'category': template.category,
                'subject_template': template.subject_template or '',
                'title_template': template.title_template or '',
                'content_template': template.content_template,
                'status': template.status.value,
                'created_by': template.created_by,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat(),
                'personalization_level': template.personalization_level.value,
                'variables': json.dumps([{
                    'name': var.name,
                    'type': var.type,
                    'required': var.required,
                    'default_value': var.default_value,
                    'description': var.description,
                    'validation_pattern': var.validation_pattern,
                    'ai_enhanced': var.ai_enhanced
                } for var in template.variables]),
                'personalization_rules': json.dumps([{
                    'id': rule.id,
                    'name': rule.name,
                    'condition': rule.condition,
                    'transformation': rule.transformation,
                    'priority': rule.priority,
                    'active': rule.active
                } for rule in template.personalization_rules]),
                'versions': json.dumps([{
                    'id': version.id,
                    'version_number': version.version_number,
                    'content': version.content,
                    'weight': version.weight,
                    'performance_score': version.performance_score,
                    'created_at': version.created_at.isoformat(),
                    'active': version.active
                } for version in template.versions]),
                'languages': json.dumps([{
                    'template_id': lang.template_id,
                    'language': lang.language.value,
                    'subject': lang.subject,
                    'title': lang.title,
                    'content': lang.content,
                    'translated_at': lang.translated_at.isoformat() if lang.translated_at else None,
                    'auto_translated': lang.auto_translated,
                    'reviewed': lang.reviewed
                } for lang in template.languages]),
                'tags': json.dumps(template.tags),
                'metadata': json.dumps(template.metadata)
            }
            
            return {k: str(v) for k, v in data.items()}
            
        except Exception as e:
            logger.error(f"Template serialization failed: {e}")
            return {}
    
    def _deserialize_template(self, data: Dict[str, str]) -> NotificationTemplate:
        """Deserialize template from storage."""
        try:
            # Parse JSON fields
            variables_data = json.loads(data.get('variables', '[]'))
            variables = [TemplateVariable(**var_data) for var_data in variables_data]
            
            rules_data = json.loads(data.get('personalization_rules', '[]'))
            personalization_rules = [PersonalizationRule(**rule_data) for rule_data in rules_data]
            
            versions_data = json.loads(data.get('versions', '[]'))
            versions = []
            for version_data in versions_data:
                version_data['created_at'] = datetime.fromisoformat(version_data['created_at'])
                versions.append(TemplateVersion(**version_data))
            
            languages_data = json.loads(data.get('languages', '[]'))
            languages = []
            for lang_data in languages_data:
                if lang_data.get('translated_at'):
                    lang_data['translated_at'] = datetime.fromisoformat(lang_data['translated_at'])
                lang_data['language'] = LanguageCode(lang_data['language'])
                languages.append(MultiLanguageTemplate(**lang_data))
            
            return NotificationTemplate(
                id=data['id'],
                name=data['name'],
                description=data['description'],
                type=TemplateType(data['type']),
                category=data['category'],
                subject_template=data.get('subject_template') or None,
                title_template=data.get('title_template') or None,
                content_template=data['content_template'],
                variables=variables,
                personalization_rules=personalization_rules,
                personalization_level=PersonalizationLevel(data.get('personalization_level', 'standard')),
                versions=versions,
                languages=languages,
                tags=json.loads(data.get('tags', '[]')),
                metadata=json.loads(data.get('metadata', '{}')),
                status=TemplateStatus(data['status']),
                created_by=data['created_by'],
                created_at=datetime.fromisoformat(data['created_at']),
                updated_at=datetime.fromisoformat(data['updated_at'])
            )
            
        except Exception as e:
            logger.error(f"Template deserialization failed: {e}")
            raise
    
    async def _get_language_template(self, template: NotificationTemplate, 
                                   language: LanguageCode) -> MultiLanguageTemplate:
        """Get or create language-specific template."""
        try:
            # Look for existing language template
            for lang_template in template.languages:
                if lang_template.language == language:
                    return lang_template
            
            # If not found, create or translate
            if language == LanguageCode.EN:
                # Create English template from base
                return MultiLanguageTemplate(
                    template_id=template.id,
                    language=LanguageCode.EN,
                    subject=template.subject_template,
                    title=template.title_template,
                    content=template.content_template,
                    auto_translated=False,
                    reviewed=True
                )
            else:
                # Translate to target language
                translated = await self.translation_engine.translate_template(template, language)
                template.languages.append(translated)
                await self._store_template(template)
                return translated
                
        except Exception as e:
            logger.error(f"Failed to get language template: {e}")
            # Fallback to English
            return MultiLanguageTemplate(
                template_id=template.id,
                language=LanguageCode.EN,
                subject=template.subject_template,
                title=template.title_template,
                content=template.content_template,
                auto_translated=False,
                reviewed=True
            )
    
    async def _prepare_render_variables(self, template: NotificationTemplate, 
                                      context: RenderContext) -> Dict[str, Any]:
        """Prepare variables for template rendering."""
        variables = {}
        
        # Add context data
        variables.update(context.user_data)
        variables.update(context.contextual_data)
        
        # Add system variables
        variables['current_date'] = datetime.utcnow().strftime('%Y-%m-%d')
        variables['current_time'] = datetime.utcnow().strftime('%H:%M')
        variables['user_timezone'] = context.timezone or 'UTC'
        variables['user_language'] = context.language.value
        
        # Process template variables with defaults and AI enhancement
        for var in template.variables:
            if var.name not in variables:
                if var.default_value is not None:
                    variables[var.name] = var.default_value
                elif var.required:
                    variables[var.name] = f"[{var.name}]"  # Placeholder for missing required var
            
            # Apply AI enhancement if enabled
            if var.ai_enhanced and self.ai_engine and var.name in variables:
                enhanced_value = await self.ai_engine.enhance_content(
                    str(variables[var.name]), context, "personalization"
                )
                variables[var.name] = enhanced_value
        
        return variables
    
    async def _apply_ai_personalization(self, content: str, context: RenderContext, 
                                      rules: List[PersonalizationRule]) -> str:
        """Apply AI personalization rules to content."""
        try:
            if not self.ai_engine:
                return content
            
            enhanced_content = content
            
            # Apply personalization rules
            for rule in rules:
                if rule.active and self._evaluate_condition(rule.condition, context):
                    enhanced_content = await self.ai_engine.enhance_content(
                        enhanced_content, context, rule.transformation
                    )
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"AI personalization failed: {e}")
            return content
    
    def _evaluate_condition(self, condition: str, context: RenderContext) -> bool:
        """Evaluate personalization rule condition."""
        try:
            # Simple condition evaluation (in production, use proper expression parser)
            if 'engagement_level' in condition:
                behavioral_data = context.behavioral_data
                engagement_level = behavioral_data.get('engagement_level', 'medium')
                return engagement_level in condition
            
            if 'device_type' in condition:
                return context.device_type and context.device_type in condition
            
            # Default to true for now
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    async def _calculate_quality_score(self, content: str, context: RenderContext) -> float:
        """Calculate content quality score."""
        try:
            if not self.ai_engine:
                return 0.7  # Default score
            
            return await self.ai_engine.predict_engagement(content, context)
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return 0.5


# Factory function for creating service instance
def create_template_engine(config: Dict[str, Any]) -> NotificationTemplateEngine:
    """Create and configure notification template engine."""
    return NotificationTemplateEngine(config)


# Export main classes and functions
__all__ = [
    'NotificationTemplateEngine',
    'NotificationTemplate',
    'TemplateVariable',
    'PersonalizationRule',
    'TemplateVersion',
    'MultiLanguageTemplate',
    'RenderContext',
    'RenderResult',
    'TemplateType',
    'PersonalizationLevel',
    'TemplateStatus',
    'LanguageCode',
    'AIPersonalizationEngine',
    'TranslationEngine',
    'TemplateOptimizer',
    'create_template_engine'
]