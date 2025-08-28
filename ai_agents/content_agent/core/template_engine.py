"""
Template Engine - Advanced Content Template Management and Format Adaptation System

Ultra-advanced template engine for content creation with intelligent format adaptation,
dynamic templating, and multi-platform optimization.

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
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import uuid
from pathlib import Path
import yaml
from jinja2 import Environment, BaseLoader, select_autoescape, Template
from markupsafe import Markup
import markdown
from bs4 import BeautifulSoup
import cssutils
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException

from ...core.database import get_async_session
from ...core.config import get_settings
from ...models.content import Content, ContentType, ContentTemplate, TemplateCategory
from ...models.users import User, UserProfile, BrandProfile

logger = logging.getLogger(__name__)
settings = get_settings()


class TemplateType(str, Enum):
    """Types of content templates"""
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA_POST = "social_media_post"
    EMAIL_NEWSLETTER = "email_newsletter"
    LANDING_PAGE = "landing_page"
    VIDEO_SCRIPT = "video_script"
    PODCAST_SCRIPT = "podcast_script"
    PRESS_RELEASE = "press_release"
    PRODUCT_DESCRIPTION = "product_description"
    AD_COPY = "ad_copy"
    SOCIAL_MEDIA_STORY = "social_media_story"
    CAROUSEL_POST = "carousel_post"
    INFOGRAPHIC_TEXT = "infographic_text"
    WEBINAR_OUTLINE = "webinar_outline"
    COURSE_MODULE = "course_module"
    CASE_STUDY = "case_study"


class OutputFormat(str, Enum):
    """Output format options"""
    HTML = "html"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"
    SOCIAL_MEDIA = "social_media"
    EMAIL_HTML = "email_html"
    WEB_PAGE = "web_page"
    MOBILE_OPTIMIZED = "mobile_optimized"


class Platform(str, Enum):
    """Target platforms for content"""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    WEBSITE = "website"
    BLOG = "blog"
    EMAIL = "email"
    PRINT = "print"
    MOBILE_APP = "mobile_app"


@dataclass
class TemplateVariable:
    """Template variable definition"""
    name: str
    type: str  # text, number, boolean, date, list, object
    required: bool = True
    default: Any = None
    description: str = ""
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    options: List[Any] = field(default_factory=list)  # For enum-like variables


@dataclass
class ContentTemplate:
    """Comprehensive content template structure"""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    template_type: TemplateType = TemplateType.BLOG_POST
    category: str = "general"
    template_content: str = ""
    variables: List[TemplateVariable] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    platform_specific: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    style_config: Dict[str, Any] = field(default_factory=dict)
    seo_config: Dict[str, Any] = field(default_factory=dict)
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    usage_count: int = 0
    rating: float = 0.0
    is_public: bool = False
    is_premium: bool = False


@dataclass
class TemplateRenderContext:
    """Context for template rendering"""
    variables: Dict[str, Any] = field(default_factory=dict)
    platform: Optional[Platform] = None
    output_format: OutputFormat = OutputFormat.HTML
    style_overrides: Dict[str, Any] = field(default_factory=dict)
    brand_settings: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None
    seo_settings: Optional[Dict[str, Any]] = None


class TemplateEngine:
    """Advanced content template engine with intelligent adaptation"""
    
    def __init__(self):
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Custom filters and functions
        self._register_custom_filters()
        self._register_custom_functions()
        
        # Template storage
        self.templates = {}
        self.template_cache = {}
        
        # Platform configurations
        self.platform_configs = self._load_platform_configs()
        
        # Load built-in templates
        self._load_builtin_templates()
        
        logger.info("TemplateEngine initialized with Jinja2 and custom filters")

    def _register_custom_filters(self):
        """Register custom Jinja2 filters"""
        
        @self.jinja_env.filter('truncate_words')
        def truncate_words(text: str, count: int = 50, suffix: str = '...') -> str:
            """Truncate text to specified word count"""
            words = text.split()
            if len(words) <= count:
                return text
            return ' '.join(words[:count]) + suffix
        
        @self.jinja_env.filter('title_case')
        def title_case(text: str) -> str:
            """Convert text to title case"""
            return text.title()
        
        @self.jinja_env.filter('hashtags')
        def hashtags(text: str, max_tags: int = 10) -> str:
            """Extract and format hashtags"""
            words = re.findall(r'\b\w+\b', text.lower())
            unique_words = list(dict.fromkeys(words))  # Preserve order, remove duplicates
            tags = ['#' + word for word in unique_words[:max_tags] if len(word) > 3]
            return ' '.join(tags)
        
        @self.jinja_env.filter('markdown_to_html')
        def markdown_to_html(text: str) -> Markup:
            """Convert markdown to HTML"""
            html = markdown.markdown(text, extensions=['extra', 'codehilite'])
            return Markup(html)
        
        @self.jinja_env.filter('platform_optimize')
        def platform_optimize(text: str, platform: str) -> str:
            """Optimize text for specific platform"""
            platform_limits = {
                'twitter': 280,
                'instagram': 2200,
                'linkedin': 3000,
                'facebook': 63206
            }
            
            limit = platform_limits.get(platform.lower(), len(text))
            if len(text) <= limit:
                return text
            
            return text[:limit-3] + '...'
        
        @self.jinja_env.filter('seo_optimize')
        def seo_optimize(text: str, keywords: List[str] = None) -> str:
            """Basic SEO optimization of text"""
            if not keywords:
                return text
            
            # Simple keyword integration (in production, this would be more sophisticated)
            optimized = text
            for keyword in keywords[:3]:  # Limit to top 3 keywords
                if keyword.lower() not in optimized.lower():
                    optimized = f"{keyword} - {optimized}"
            
            return optimized

    def _register_custom_functions(self):
        """Register custom Jinja2 global functions"""
        
        @self.jinja_env.global_function
        def current_date(format: str = '%Y-%m-%d') -> str:
            """Get current date in specified format"""
            return datetime.now().strftime(format)
        
        @self.jinja_env.global_function
        def word_count(text: str) -> int:
            """Count words in text"""
            return len(text.split())
        
        @self.jinja_env.global_function
        def reading_time(text: str, wpm: int = 200) -> int:
            """Estimate reading time in minutes"""
            return max(1, len(text.split()) // wpm)
        
        @self.jinja_env.global_function
        def generate_id(prefix: str = 'item') -> str:
            """Generate unique ID"""
            return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def _load_platform_configs(self) -> Dict[Platform, Dict[str, Any]]:
        """Load platform-specific configurations"""
        return {
            Platform.INSTAGRAM: {
                'max_caption_length': 2200,
                'max_hashtags': 30,
                'optimal_hashtags': 11,
                'image_ratios': ['1:1', '4:5', '16:9'],
                'supports_links': False,
                'story_duration': 15,
                'reel_duration': 90
            },
            Platform.TWITTER: {
                'max_text_length': 280,
                'max_hashtags': 2,
                'thread_support': True,
                'supports_polls': True,
                'image_ratios': ['16:9', '1:1'],
                'video_max_duration': 140
            },
            Platform.LINKEDIN: {
                'max_text_length': 3000,
                'professional_tone': True,
                'supports_documents': True,
                'image_ratios': ['1.91:1', '1:1'],
                'article_support': True
            },
            Platform.FACEBOOK: {
                'max_text_length': 63206,
                'supports_all_media': True,
                'event_support': True,
                'poll_support': True,
                'image_ratios': ['1.91:1', '1:1', '4:5']
            },
            Platform.TIKTOK: {
                'video_only': True,
                'max_caption_length': 300,
                'max_video_duration': 180,
                'trending_hashtags': True,
                'vertical_video': True,
                'aspect_ratio': '9:16'
            },
            Platform.YOUTUBE: {
                'max_title_length': 100,
                'max_description_length': 5000,
                'thumbnail_required': True,
                'supports_chapters': True,
                'supports_end_screens': True
            }
        }

    def _load_builtin_templates(self):
        """Load built-in content templates"""
        
        # Blog Post Template
        blog_template = ContentTemplate(
            name="Professional Blog Post",
            description="Comprehensive blog post template with SEO optimization",
            template_type=TemplateType.BLOG_POST,
            category="content_marketing",
            template_content="""
# {{ title }}

{% if featured_image %}
![{{ title }}]({{ featured_image }})
{% endif %}

## Introduction

{{ introduction | markdown_to_html }}

{% for section in main_sections %}
## {{ section.heading }}

{{ section.content | markdown_to_html }}

{% if section.image %}
![{{ section.heading }}]({{ section.image }})
{% endif %}
{% endfor %}

## Conclusion

{{ conclusion | markdown_to_html }}

{% if call_to_action %}
## {{ call_to_action.heading | default("Take Action") }}

{{ call_to_action.content | markdown_to_html }}

{% if call_to_action.button_text %}
[{{ call_to_action.button_text }}]({{ call_to_action.button_url }})
{% endif %}
{% endif %}

---

*Published on {{ current_date() }} | Reading time: {{ reading_time(introduction + conclusion) }} minutes*

{% if seo_keywords %}
**Keywords**: {{ seo_keywords | join(', ') }}
{% endif %}
""",
            variables=[
                TemplateVariable("title", "text", True, "", "Blog post title"),
                TemplateVariable("introduction", "text", True, "", "Introduction paragraph"),
                TemplateVariable("main_sections", "list", True, [], "Main content sections"),
                TemplateVariable("conclusion", "text", True, "", "Conclusion paragraph"),
                TemplateVariable("featured_image", "text", False, "", "Featured image URL"),
                TemplateVariable("call_to_action", "object", False, {}, "Call to action section"),
                TemplateVariable("seo_keywords", "list", False, [], "SEO keywords")
            ],
            tags=["blog", "seo", "professional", "marketing"]
        )
        
        # Social Media Post Template
        social_template = ContentTemplate(
            name="Engaging Social Media Post",
            description="Versatile social media post template for multiple platforms",
            template_type=TemplateType.SOCIAL_MEDIA_POST,
            category="social_media",
            template_content="""
{% if hook %}{{ hook }}

{% endif %}{{ main_content | platform_optimize(platform) }}

{% if call_to_action %}
{{ call_to_action }}
{% endif %}

{% if hashtags %}
{{ hashtags | join(' ') }}
{% endif %}

{% if mention_users %}
{% for user in mention_users %}@{{ user }} {% endfor %}
{% endif %}
""",
            variables=[
                TemplateVariable("hook", "text", False, "", "Attention-grabbing hook"),
                TemplateVariable("main_content", "text", True, "", "Main post content"),
                TemplateVariable("call_to_action", "text", False, "", "Call to action"),
                TemplateVariable("hashtags", "list", False, [], "Relevant hashtags"),
                TemplateVariable("mention_users", "list", False, [], "Users to mention"),
                TemplateVariable("platform", "text", True, "instagram", "Target platform")
            ],
            platform_specific={
                Platform.INSTAGRAM: {
                    "max_length": 2200,
                    "optimal_hashtags": 11,
                    "supports_carousel": True
                },
                Platform.TWITTER: {
                    "max_length": 280,
                    "max_hashtags": 2,
                    "thread_capable": True
                }
            },
            tags=["social", "engagement", "versatile"]
        )
        
        # Email Newsletter Template
        email_template = ContentTemplate(
            name="Professional Email Newsletter",
            description="HTML email newsletter template with responsive design",
            template_type=TemplateType.EMAIL_NEWSLETTER,
            category="email_marketing",
            template_content="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject_line }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
        .header { text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 20px; }
        .content { line-height: 1.6; }
        .cta-button { display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {% if logo_url %}
            <img src="{{ logo_url }}" alt="{{ company_name }}" style="max-height: 60px;">
            {% endif %}
            <h1>{{ newsletter_title }}</h1>
        </div>
        
        <div class="content">
            <h2>{{ main_headline }}</h2>
            
            {{ opening_message | markdown_to_html }}
            
            {% for article in articles %}
            <div style="margin: 30px 0; padding: 20px; border-left: 4px solid #007bff;">
                <h3>{{ article.title }}</h3>
                <p>{{ article.summary }}</p>
                {% if article.read_more_url %}
                <a href="{{ article.read_more_url }}" class="cta-button">Read More</a>
                {% endif %}
            </div>
            {% endfor %}
            
            {% if main_cta %}
            <div style="text-align: center; margin: 40px 0;">
                <a href="{{ main_cta.url }}" class="cta-button">{{ main_cta.text }}</a>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>© {{ current_date('%Y') }} {{ company_name }}. All rights reserved.</p>
            <p>You're receiving this email because you subscribed to our newsletter.</p>
            <p><a href="{{ unsubscribe_url }}">Unsubscribe</a> | <a href="{{ preferences_url }}">Update Preferences</a></p>
        </div>
    </div>
</body>
</html>
""",
            variables=[
                TemplateVariable("subject_line", "text", True, "", "Email subject line"),
                TemplateVariable("newsletter_title", "text", True, "", "Newsletter title"),
                TemplateVariable("main_headline", "text", True, "", "Main headline"),
                TemplateVariable("opening_message", "text", True, "", "Opening message"),
                TemplateVariable("articles", "list", True, [], "Newsletter articles"),
                TemplateVariable("main_cta", "object", False, {}, "Main call to action"),
                TemplateVariable("company_name", "text", True, "", "Company name"),
                TemplateVariable("logo_url", "text", False, "", "Logo URL"),
                TemplateVariable("unsubscribe_url", "text", True, "", "Unsubscribe URL"),
                TemplateVariable("preferences_url", "text", True, "", "Preferences URL")
            ],
            tags=["email", "newsletter", "html", "responsive"]
        )
        
        # Store built-in templates
        self.templates[blog_template.template_id] = blog_template
        self.templates[social_template.template_id] = social_template
        self.templates[email_template.template_id] = email_template
        
        logger.info(f"Loaded {len(self.templates)} built-in templates")

    async def render_template(self, template_id: str, context: TemplateRenderContext) -> str:
        """Render template with given context"""
        try:
            # Get template
            template = await self._get_template(template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            # Validate variables
            self._validate_template_variables(template, context.variables)
            
            # Prepare rendering context
            render_context = self._prepare_render_context(template, context)
            
            # Render template
            jinja_template = self.jinja_env.from_string(template.template_content)
            rendered_content = jinja_template.render(**render_context)
            
            # Apply platform-specific optimizations
            if context.platform:
                rendered_content = self._apply_platform_optimizations(
                    rendered_content, context.platform, template
                )
            
            # Apply output format
            formatted_content = self._apply_output_format(
                rendered_content, context.output_format, context
            )
            
            # Update template usage
            await self._update_template_usage(template_id)
            
            logger.info(f"Template rendered successfully: {template_id}")
            return formatted_content
            
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            raise HTTPException(status_code=500, detail=f"Template rendering failed: {str(e)}")

    async def _get_template(self, template_id: str) -> Optional[ContentTemplate]:
        """Get template by ID"""
        if template_id in self.templates:
            return self.templates[template_id]
        
        # Try loading from database
        try:
            async with get_async_session() as session:
                # Query template from database (would implement proper model)
                # For now, return None
                return None
        except Exception as e:
            logger.error(f"Failed to load template from database: {e}")
            return None

    def _validate_template_variables(self, template: ContentTemplate, variables: Dict[str, Any]):
        """Validate template variables"""
        for var in template.variables:
            if var.required and var.name not in variables:
                raise ValueError(f"Required variable '{var.name}' is missing")
            
            if var.name in variables:
                value = variables[var.name]
                
                # Type validation
                if var.type == "text" and not isinstance(value, str):
                    raise ValueError(f"Variable '{var.name}' must be text")
                elif var.type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(f"Variable '{var.name}' must be a number")
                elif var.type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Variable '{var.name}' must be boolean")
                elif var.type == "list" and not isinstance(value, list):
                    raise ValueError(f"Variable '{var.name}' must be a list")
                elif var.type == "object" and not isinstance(value, dict):
                    raise ValueError(f"Variable '{var.name}' must be an object")
                
                # Validation rules
                if var.validation_rules:
                    self._apply_validation_rules(var.name, value, var.validation_rules)

    def _apply_validation_rules(self, var_name: str, value: Any, rules: Dict[str, Any]):
        """Apply validation rules to variable value"""
        if "min_length" in rules and isinstance(value, str):
            if len(value) < rules["min_length"]:
                raise ValueError(f"Variable '{var_name}' must be at least {rules['min_length']} characters")
        
        if "max_length" in rules and isinstance(value, str):
            if len(value) > rules["max_length"]:
                raise ValueError(f"Variable '{var_name}' must be no more than {rules['max_length']} characters")
        
        if "pattern" in rules and isinstance(value, str):
            if not re.match(rules["pattern"], value):
                raise ValueError(f"Variable '{var_name}' does not match required pattern")
        
        if "min_value" in rules and isinstance(value, (int, float)):
            if value < rules["min_value"]:
                raise ValueError(f"Variable '{var_name}' must be at least {rules['min_value']}")
        
        if "max_value" in rules and isinstance(value, (int, float)):
            if value > rules["max_value"]:
                raise ValueError(f"Variable '{var_name}' must be no more than {rules['max_value']}")

    def _prepare_render_context(self, template: ContentTemplate, context: TemplateRenderContext) -> Dict[str, Any]:
        """Prepare the complete rendering context"""
        render_context = context.variables.copy()
        
        # Add default values for missing optional variables
        for var in template.variables:
            if not var.required and var.name not in render_context and var.default is not None:
                render_context[var.name] = var.default
        
        # Add platform information
        if context.platform:
            render_context['platform'] = context.platform.value
            render_context['platform_config'] = self.platform_configs.get(context.platform, {})
        
        # Add brand settings
        if context.brand_settings:
            render_context.update(context.brand_settings)
        
        # Add user preferences
        if context.user_preferences:
            render_context['user'] = context.user_preferences
        
        # Add SEO settings
        if context.seo_settings:
            render_context['seo'] = context.seo_settings
        
        return render_context

    def _apply_platform_optimizations(self, content: str, platform: Platform, 
                                    template: ContentTemplate) -> str:
        """Apply platform-specific optimizations"""
        platform_config = self.platform_configs.get(platform, {})
        
        # Apply platform-specific settings from template
        if platform in template.platform_specific:
            platform_settings = template.platform_specific[platform]
            
            # Text length optimization
            if 'max_length' in platform_settings:
                max_length = platform_settings['max_length']
                if len(content) > max_length:
                    content = content[:max_length-3] + '...'
            
            # Hashtag optimization
            if 'optimal_hashtags' in platform_settings:
                optimal_count = platform_settings['optimal_hashtags']
                # This would involve more sophisticated hashtag optimization
        
        return content

    def _apply_output_format(self, content: str, output_format: OutputFormat, 
                           context: TemplateRenderContext) -> str:
        """Apply output format transformation"""
        if output_format == OutputFormat.HTML:
            return self._ensure_html_format(content)
        elif output_format == OutputFormat.MARKDOWN:
            return self._convert_to_markdown(content)
        elif output_format == OutputFormat.PLAIN_TEXT:
            return self._convert_to_plain_text(content)
        elif output_format == OutputFormat.JSON:
            return self._convert_to_json(content, context)
        elif output_format == OutputFormat.EMAIL_HTML:
            return self._optimize_for_email(content)
        elif output_format == OutputFormat.MOBILE_OPTIMIZED:
            return self._optimize_for_mobile(content)
        else:
            return content

    def _ensure_html_format(self, content: str) -> str:
        """Ensure content is in proper HTML format"""
        if not content.strip().startswith('<'):
            # Convert markdown-like content to HTML
            content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return content

    def _convert_to_markdown(self, content: str) -> str:
        """Convert HTML content to markdown"""
        if '<' in content:
            # Use BeautifulSoup to parse HTML and convert to markdown
            soup = BeautifulSoup(content, 'html.parser')
            return self._html_to_markdown(soup)
        return content

    def _html_to_markdown(self, soup: BeautifulSoup) -> str:
        """Convert BeautifulSoup HTML to markdown"""
        # Basic HTML to Markdown conversion
        text = soup.get_text()
        
        # Handle common HTML elements
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(tag.name[1])
            markdown_header = '#' * level + ' ' + tag.get_text().strip()
            text = text.replace(tag.get_text(), markdown_header)
        
        return text

    def _convert_to_plain_text(self, content: str) -> str:
        """Convert content to plain text"""
        if '<' in content:
            soup = BeautifulSoup(content, 'html.parser')
            return soup.get_text().strip()
        return content

    def _convert_to_json(self, content: str, context: TemplateRenderContext) -> str:
        """Convert content to JSON format"""
        return json.dumps({
            'content': content,
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'platform': context.platform.value if context.platform else None,
                'output_format': context.output_format.value,
                'word_count': len(content.split()),
                'character_count': len(content)
            }
        }, indent=2)

    def _optimize_for_email(self, content: str) -> str:
        """Optimize HTML content for email clients"""
        # Add email-specific optimizations
        if not content.startswith('<!DOCTYPE'):
            # Wrap in basic email structure if needed
            content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                </style>
            </head>
            <body>
                <div class="container">
                    {content}
                </div>
            </body>
            </html>
            """
        
        return content

    def _optimize_for_mobile(self, content: str) -> str:
        """Optimize content for mobile devices"""
        # Add mobile-specific optimizations
        if '<' in content:  # HTML content
            # Add mobile viewport and responsive CSS
            mobile_css = """
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                @media (max-width: 768px) {
                    body { font-size: 16px; line-height: 1.5; }
                    .container { padding: 10px; }
                    img { max-width: 100%; height: auto; }
                }
            </style>
            """
            
            if '<head>' in content:
                content = content.replace('<head>', f'<head>{mobile_css}')
            else:
                content = mobile_css + content
        
        return content

    async def _update_template_usage(self, template_id: str):
        """Update template usage statistics"""
        try:
            if template_id in self.templates:
                self.templates[template_id].usage_count += 1
                
            # Update in database
            async with get_async_session() as session:
                # Update usage count in database
                logger.debug(f"Updated usage count for template: {template_id}")
                
        except Exception as e:
            logger.error(f"Failed to update template usage: {e}")

    async def create_template(self, template: ContentTemplate, user_id: str) -> str:
        """Create a new content template"""
        try:
            # Validate template
            self._validate_new_template(template)
            
            # Set metadata
            template.created_by = user_id
            template.created_at = datetime.now(timezone.utc)
            template.updated_at = template.created_at
            
            # Store in memory
            self.templates[template.template_id] = template
            
            # Store in database
            await self._store_template_in_database(template)
            
            logger.info(f"Template created: {template.template_id}")
            return template.template_id
            
        except Exception as e:
            logger.error(f"Template creation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Template creation failed: {str(e)}")

    def _validate_new_template(self, template: ContentTemplate):
        """Validate new template"""
        if not template.name:
            raise ValueError("Template name is required")
        
        if not template.template_content:
            raise ValueError("Template content is required")
        
        if len(template.template_content) < 10:
            raise ValueError("Template content is too short")
        
        # Validate Jinja2 syntax
        try:
            self.jinja_env.from_string(template.template_content)
        except Exception as e:
            raise ValueError(f"Invalid template syntax: {str(e)}")

    async def _store_template_in_database(self, template: ContentTemplate):
        """Store template in database"""
        try:
            async with get_async_session() as session:
                # Store template (would implement proper database model)
                logger.info(f"Template stored in database: {template.template_id}")
                
        except Exception as e:
            logger.error(f"Failed to store template in database: {e}")

    async def list_templates(self, user_id: Optional[str] = None, 
                           category: Optional[str] = None,
                           template_type: Optional[TemplateType] = None,
                           public_only: bool = False) -> List[ContentTemplate]:
        """List available templates with filters"""
        try:
            templates = list(self.templates.values())
            
            # Apply filters
            if user_id and not public_only:
                templates = [t for t in templates if t.created_by == user_id or t.is_public]
            elif public_only:
                templates = [t for t in templates if t.is_public]
            
            if category:
                templates = [t for t in templates if t.category == category]
            
            if template_type:
                templates = [t for t in templates if t.template_type == template_type]
            
            # Sort by usage and rating
            templates.sort(key=lambda t: (t.rating, t.usage_count), reverse=True)
            
            return templates
            
        except Exception as e:
            logger.error(f"Template listing failed: {e}")
            return []

    async def duplicate_template(self, template_id: str, user_id: str, 
                               new_name: Optional[str] = None) -> str:
        """Duplicate an existing template"""
        try:
            original_template = await self._get_template(template_id)
            if not original_template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            # Create duplicate
            duplicate = ContentTemplate(
                name=new_name or f"{original_template.name} (Copy)",
                description=original_template.description,
                template_type=original_template.template_type,
                category=original_template.category,
                template_content=original_template.template_content,
                variables=original_template.variables.copy(),
                metadata=original_template.metadata.copy(),
                platform_specific=original_template.platform_specific.copy(),
                style_config=original_template.style_config.copy(),
                seo_config=original_template.seo_config.copy(),
                tags=original_template.tags.copy(),
                is_public=False,  # Copies are private by default
                is_premium=False
            )
            
            return await self.create_template(duplicate, user_id)
            
        except Exception as e:
            logger.error(f"Template duplication failed: {e}")
            raise HTTPException(status_code=500, detail=f"Template duplication failed: {str(e)}")

    async def get_template_preview(self, template_id: str, 
                                 sample_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate template preview with sample data"""
        try:
            template = await self._get_template(template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            # Use sample data or generate defaults
            preview_data = sample_data or self._generate_sample_data(template)
            
            # Create render context
            context = TemplateRenderContext(
                variables=preview_data,
                output_format=OutputFormat.HTML
            )
            
            # Render preview
            preview_html = await self.render_template(template_id, context)
            
            # Also generate plain text version
            context.output_format = OutputFormat.PLAIN_TEXT
            preview_text = await self.render_template(template_id, context)
            
            return {
                'html': preview_html,
                'text': preview_text,
                'sample_data': preview_data
            }
            
        except Exception as e:
            logger.error(f"Template preview generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")

    def _generate_sample_data(self, template: ContentTemplate) -> Dict[str, Any]:
        """Generate sample data for template variables"""
        sample_data = {}
        
        for var in template.variables:
            if var.type == "text":
                if "title" in var.name.lower():
                    sample_data[var.name] = "Sample Title"
                elif "description" in var.name.lower():
                    sample_data[var.name] = "This is a sample description for the template preview."
                elif "content" in var.name.lower():
                    sample_data[var.name] = "This is sample content to demonstrate how the template will look when rendered with actual data."
                else:
                    sample_data[var.name] = f"Sample {var.name.replace('_', ' ').title()}"
            
            elif var.type == "number":
                sample_data[var.name] = 42
            
            elif var.type == "boolean":
                sample_data[var.name] = True
            
            elif var.type == "list":
                if "hashtag" in var.name.lower():
                    sample_data[var.name] = ["#sample", "#template", "#content"]
                elif "keyword" in var.name.lower():
                    sample_data[var.name] = ["keyword1", "keyword2", "keyword3"]
                else:
                    sample_data[var.name] = ["Item 1", "Item 2", "Item 3"]
            
            elif var.type == "object":
                sample_data[var.name] = {
                    "title": "Sample Object Title",
                    "content": "Sample object content",
                    "url": "https://example.com"
                }
            
            elif var.default is not None:
                sample_data[var.name] = var.default
        
        return sample_data


class FormatAdapter:
    """Advanced format adaptation system for cross-platform content optimization"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.format_processors = self._initialize_format_processors()
        
        logger.info("FormatAdapter initialized")

    def _initialize_format_processors(self) -> Dict[str, Any]:
        """Initialize format-specific processors"""
        return {
            'html_processor': self._create_html_processor(),
            'markdown_processor': self._create_markdown_processor(),
            'social_processor': self._create_social_processor(),
            'email_processor': self._create_email_processor()
        }

    def _create_html_processor(self):
        """Create HTML format processor"""
        def process_html(content: str, options: Dict[str, Any] = None) -> str:
            # Add semantic HTML structure
            if not content.startswith('<'):
                content = f"<div>{content}</div>"
            
            # Add accessibility attributes
            soup = BeautifulSoup(content, 'html.parser')
            
            # Add alt text to images without it
            for img in soup.find_all('img'):
                if not img.get('alt'):
                    img['alt'] = "Content image"
            
            # Add proper heading structure
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                if not heading.get('id'):
                    heading['id'] = heading.get_text().lower().replace(' ', '-')
            
            return str(soup)
        
        return process_html

    def _create_markdown_processor(self):
        """Create Markdown format processor"""
        def process_markdown(content: str, options: Dict[str, Any] = None) -> str:
            # Ensure proper markdown formatting
            lines = content.split('\n')
            processed_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # Ensure proper heading spacing
                    if line.startswith('#'):
                        processed_lines.append('')
                        processed_lines.append(line)
                        processed_lines.append('')
                    else:
                        processed_lines.append(line)
            
            return '\n'.join(processed_lines).strip()
        
        return process_markdown

    def _create_social_processor(self):
        """Create social media format processor"""
        def process_social(content: str, platform: Platform, options: Dict[str, Any] = None) -> str:
            platform_config = self.template_engine.platform_configs.get(platform, {})
            
            # Apply character limits
            max_length = platform_config.get('max_text_length', len(content))
            if len(content) > max_length:
                content = content[:max_length-3] + '...'
            
            # Platform-specific formatting
            if platform == Platform.TWITTER:
                # Optimize for Twitter
                content = self._optimize_for_twitter(content)
            elif platform == Platform.INSTAGRAM:
                # Optimize for Instagram
                content = self._optimize_for_instagram(content)
            elif platform == Platform.LINKEDIN:
                # Optimize for LinkedIn
                content = self._optimize_for_linkedin(content)
            
            return content
        
        return process_social

    def _create_email_processor(self):
        """Create email format processor"""
        def process_email(content: str, options: Dict[str, Any] = None) -> str:
            # Email-specific optimizations
            if '<html>' not in content.lower():
                # Wrap in email-friendly HTML
                content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        a {{ color: #007bff; text-decoration: none; }}
                        img {{ max-width: 100%; height: auto; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        {content}
                    </div>
                </body>
                </html>
                """
            
            return content
        
        return process_email

    def _optimize_for_twitter(self, content: str) -> str:
        """Optimize content for Twitter"""
        # Add Twitter-specific optimizations
        # Ensure hashtags are properly formatted
        content = re.sub(r'#(\w+)', r'#\1', content)
        
        # Ensure mentions are properly formatted
        content = re.sub(r'@(\w+)', r'@\1', content)
        
        return content

    def _optimize_for_instagram(self, content: str) -> str:
        """Optimize content for Instagram"""
        # Add Instagram-specific optimizations
        # Ensure proper line breaks for readability
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            if len(line) > 80:  # Break long lines
                words = line.split()
                current_line = []
                for word in words:
                    if len(' '.join(current_line + [word])) > 80:
                        optimized_lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        current_line.append(word)
                if current_line:
                    optimized_lines.append(' '.join(current_line))
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)

    def _optimize_for_linkedin(self, content: str) -> str:
        """Optimize content for LinkedIn"""
        # Add LinkedIn-specific optimizations
        # Ensure professional tone and structure
        return content

    async def adapt_content(self, content: str, source_format: OutputFormat,
                          target_format: OutputFormat, platform: Optional[Platform] = None,
                          options: Optional[Dict[str, Any]] = None) -> str:
        """Adapt content from one format to another"""
        try:
            adapted_content = content
            
            # Apply source format processing if needed
            if source_format == OutputFormat.HTML and target_format != OutputFormat.HTML:
                # Convert from HTML
                adapted_content = self._convert_from_html(adapted_content, target_format)
            elif source_format == OutputFormat.MARKDOWN and target_format != OutputFormat.MARKDOWN:
                # Convert from Markdown
                adapted_content = self._convert_from_markdown(adapted_content, target_format)
            
            # Apply target format processing
            if target_format == OutputFormat.HTML:
                adapted_content = self.format_processors['html_processor'](adapted_content, options)
            elif target_format == OutputFormat.MARKDOWN:
                adapted_content = self.format_processors['markdown_processor'](adapted_content, options)
            elif target_format == OutputFormat.SOCIAL_MEDIA and platform:
                adapted_content = self.format_processors['social_processor'](adapted_content, platform, options)
            elif target_format == OutputFormat.EMAIL_HTML:
                adapted_content = self.format_processors['email_processor'](adapted_content, options)
            
            logger.info(f"Content adapted: {source_format.value} -> {target_format.value}")
            return adapted_content
            
        except Exception as e:
            logger.error(f"Content adaptation failed: {e}")
            return content  # Return original if adaptation fails

    def _convert_from_html(self, content: str, target_format: OutputFormat) -> str:
        """Convert HTML content to other formats"""
        soup = BeautifulSoup(content, 'html.parser')
        
        if target_format == OutputFormat.PLAIN_TEXT:
            return soup.get_text().strip()
        elif target_format == OutputFormat.MARKDOWN:
            return self.template_engine._html_to_markdown(soup)
        else:
            return content

    def _convert_from_markdown(self, content: str, target_format: OutputFormat) -> str:
        """Convert Markdown content to other formats"""
        if target_format == OutputFormat.HTML:
            return markdown.markdown(content, extensions=['extra', 'codehilite'])
        elif target_format == OutputFormat.PLAIN_TEXT:
            # Remove markdown formatting
            plain_text = re.sub(r'#{1,6}\s*', '', content)  # Remove headers
            plain_text = re.sub(r'\*\*(.*?)\*\*', r'\1', plain_text)  # Remove bold
            plain_text = re.sub(r'\*(.*?)\*', r'\1', plain_text)  # Remove italic
            plain_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', plain_text)  # Remove links
            return plain_text.strip()
        else:
            return content
