"""
Template Management System - Advanced Response Templates

Enterprise-grade template management for dynamic response generation
with business logic integration and content creator specialization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
import re
from datetime import datetime

from pydantic import BaseModel, Field, validator
import jinja2
from jinja2 import Environment, DictLoader, TemplateNotFound

from ...core.exceptions import TemplateError, ValidationError
from ...core.cache import CacheManager
from ...core.monitoring import MetricsCollector


class TemplateCategory(Enum):
    """Template category enumeration"""
    WELCOME = "welcome"
    HELP = "help"
    GUIDANCE = "guidance"
    MONETIZATION = "monetization"
    PROTECTION = "protection"
    COLLABORATION = "collaboration"
    PLATFORM_SPECIFIC = "platform_specific"
    ERROR_HANDLING = "error_handling"
    CONFIRMATION = "confirmation"
    RECOMMENDATION = "recommendation"
    EDUCATIONAL = "educational"
    BUSINESS_WORKFLOW = "business_workflow"


class ContentCreatorType(Enum):
    """Content creator type enumeration"""
    MUSICIAN = "musician"
    INFLUENCER = "influencer"
    PHOTOGRAPHER = "photographer"
    COMEDIAN = "comedian"
    BLOGGER = "blogger"
    PODCASTER = "podcaster"
    VIDEO_CREATOR = "video_creator"
    GENERAL = "general"


class TemplateVariables(BaseModel):
    """Template variables structure"""
    user_name: Optional[str] = None
    user_type: str = "content_creator"
    content_format: Optional[str] = None
    platform_context: Optional[str] = None
    business_context: Optional[str] = None
    specific_topic: Optional[str] = None
    user_level: str = "intermediate"
    language: str = "en"
    personalization_data: Dict[str, Any] = Field(default_factory=dict)
    dynamic_content: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('user_type')
    def validate_user_type(cls, v):
        valid_types = [e.value for e in ContentCreatorType]
        if v not in valid_types:
            return "general"
        return v


class ResponseTemplate(BaseModel):
    """Response template data structure"""
    template_id: str
    category: TemplateCategory
    content_creator_type: ContentCreatorType
    template_content: str
    variables: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=50, ge=1, le=100)
    language: str = "en"
    business_context: Optional[str] = None
    platform_specific: Optional[str] = None
    effectiveness_score: float = Field(default=0.8, ge=0.0, le=1.0)
    usage_count: int = Field(default=0, ge=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('template_content')
    def validate_template_content(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Template content must be meaningful")
        return v


class TemplateLibrary:
    """Enterprise template library with categorization and optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = CacheManager()
        self.metrics = MetricsCollector()
        self.templates: Dict[str, ResponseTemplate] = {}
        self.jinja_env = Environment(loader=DictLoader({}))
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default template library"""
        default_templates = self._get_default_templates()
        
        for template_data in default_templates:
            template = ResponseTemplate(**template_data)
            self.templates[template.template_id] = template
            
        # Update Jinja environment
        self._update_jinja_environment()
    
    def _get_default_templates(self) -> List[Dict[str, Any]]:
        """Get default template definitions"""



        return [
            # Welcome Templates
            {
                "template_id": "welcome_musician",
                "category": TemplateCategory.WELCOME,
                "content_creator_type": ContentCreatorType.MUSICIAN,
                "template_content": "Welcome to IA Influencer Agent, {{ user_name or 'talented musician' }}! I'm here to help you optimize your music creation, protect your tracks, and maximize your revenue across platforms like {{ platform_context or 'Spotify, YouTube, and social media' }}. What would you like to focus on today?",
                "variables": ["user_name", "platform_context"],
                "metadata": {"tone": "encouraging", "length": "medium"},
                "priority": 90,
                "business_context": "onboarding"
            },
            {
                "template_id": "welcome_influencer", 
                "category": TemplateCategory.WELCOME,
                "content_creator_type": ContentCreatorType.INFLUENCER,
                "template_content": "Hello {{ user_name or 'amazing creator' }}! As an influencer, you have incredible potential to build meaningful connections and monetize your content. I'll help you optimize your {{ content_format or 'content' }} strategy, protect your brand, and unlock new collaboration opportunities. Ready to elevate your influence?",
                "variables": ["user_name", "content_format"],
                "metadata": {"tone": "enthusiastic", "length": "medium"},
                "priority": 90,
                "business_context": "onboarding"
            },
            {
                "template_id": "welcome_photographer",
                "category": TemplateCategory.WELCOME,
                "content_creator_type": ContentCreatorType.PHOTOGRAPHER,
                "template_content": "Welcome, {{ user_name or 'creative photographer' }}! Your visual storytelling deserves the best protection and monetization strategies. I can help you safeguard your images, optimize licensing opportunities, and expand your reach across {{ platform_context or 'photography platforms' }}. Let's capture success together!",
                "variables": ["user_name", "platform_context"],
                "metadata": {"tone": "professional", "length": "medium"},
                "priority": 90,
                "business_context": "onboarding"
            },
            {
                "template_id": "welcome_comedian",
                "category": TemplateCategory.WELCOME,
                "content_creator_type": ContentCreatorType.COMEDIAN,
                "template_content": "Hey there, {{ user_name or 'hilarious comedian' }}! Comedy is serious business, and I'm here to help you protect your material, grow your audience, and monetize your humor across platforms. Whether it's {{ content_format or 'stand-up videos, sketches, or podcasts' }}, let's turn your talent into sustainable success!",
                "variables": ["user_name", "content_format"],
                "metadata": {"tone": "friendly", "length": "medium"},
                "priority": 90,
                "business_context": "onboarding"
            },
            
            # Monetization Templates
            {
                "template_id": "monetization_strategy_musician",
                "category": TemplateCategory.MONETIZATION,
                "content_creator_type": ContentCreatorType.MUSICIAN,
                "template_content": "For musicians like you, effective monetization involves multiple revenue streams: 1) Streaming optimization on {{ platform_context or 'Spotify, Apple Music, and YouTube Music' }}, 2) Licensing your tracks for {{ specific_topic or 'sync opportunities' }}, 3) Direct fan support through platforms, 4) Live performance promotion, and 5) Merchandise sales. I can help you set up tracking for each stream and optimize your earnings. Which area interests you most?",
                "variables": ["platform_context", "specific_topic"],
                "metadata": {"tone": "informative", "length": "detailed"},
                "priority": 85,
                "business_context": "monetization"
            },
            {
                "template_id": "monetization_strategy_influencer",
                "category": TemplateCategory.MONETIZATION,
                "content_creator_type": ContentCreatorType.INFLUENCER,
                "template_content": "As an influencer, your monetization strategy should focus on: 1) Brand partnerships aligned with your {{ specific_topic or 'niche' }}, 2) Sponsored content that maintains authenticity, 3) Affiliate marketing for products you genuinely use, 4) Creating premium content or courses, and 5) Building your own product line. I'll help you identify the best opportunities and negotiate fair rates based on your {{ dynamic_content.engagement_rate or 'engagement metrics' }}.",
                "variables": ["specific_topic", "dynamic_content"],
                "metadata": {"tone": "strategic", "length": "detailed"},
                "priority": 85,
                "business_context": "monetization"
            },
            
            # Protection Templates
            {
                "template_id": "content_protection_audio",
                "category": TemplateCategory.PROTECTION,
                "content_creator_type": ContentCreatorType.MUSICIAN,
                "template_content": "Protecting your {{ content_format or 'audio' }} content is crucial for your intellectual property rights. I recommend implementing: 1) AI-powered fingerprinting for automatic detection of unauthorized usage, 2) Copyright registration for legal protection, 3) Watermarking for track identification, 4) Automated monitoring across platforms like {{ platform_context or 'YouTube, SoundCloud, and social media' }}, and 5) DMCA takedown automation. Would you like me to help you set up these protection measures?",
                "variables": ["content_format", "platform_context"],
                "metadata": {"tone": "protective", "length": "detailed"},
                "priority": 88,
                "business_context": "protection"
            },
            {
                "template_id": "content_protection_visual",
                "category": TemplateCategory.PROTECTION,
                "content_creator_type": ContentCreatorType.PHOTOGRAPHER,
                "template_content": "Your {{ content_format or 'visual' }} content deserves comprehensive protection. Here's what I recommend: 1) Image fingerprinting using perceptual hashing technology, 2) Visible and invisible watermarking strategies, 3) Reverse image search monitoring, 4) Copyright metadata embedding, and 5) Automated usage tracking across {{ platform_context or 'stock platforms and social media' }}. This multi-layered approach ensures your creative work is properly attributed and compensated.",
                "variables": ["content_format", "platform_context"],
                "metadata": {"tone": "authoritative", "length": "detailed"},
                "priority": 88,
                "business_context": "protection"
            },
            
            # Collaboration Templates
            {
                "template_id": "collaboration_opportunities_musician",
                "category": TemplateCategory.COLLABORATION,
                "content_creator_type": ContentCreatorType.MUSICIAN,
                "template_content": "Collaboration can exponentially grow your reach and creativity! For musicians, I suggest: 1) Featuring with artists in complementary genres, 2) Remix exchanges to tap into different audiences, 3) Soundtrack collaborations for {{ specific_topic or 'content creators and filmmakers' }}, 4) Cross-platform promotions with influencers, and 5) Producer partnerships for new sounds. I can help you find suitable collaborators and structure fair revenue-sharing agreements. What type of collaboration interests you most?",
                "variables": ["specific_topic"],
                "metadata": {"tone": "collaborative", "length": "detailed"},
                "priority": 80,
                "business_context": "collaboration"
            },
            {
                "template_id": "collaboration_opportunities_influencer",
                "category": TemplateCategory.COLLABORATION,
                "content_creator_type": ContentCreatorType.INFLUENCER,
                "template_content": "Collaborations can amplify your influence significantly! Consider these strategies: 1) Cross-promotion with creators in your {{ specific_topic or 'niche' }}, 2) Joint content series that benefit both audiences, 3) Brand collaboration campaigns, 4) Event partnerships and co-hosting, and 5) Product collaboration opportunities. I'll help you identify creators with compatible audiences and values, ensuring authentic partnerships that drive real engagement.",
                "variables": ["specific_topic"],
                "metadata": {"tone": "networking", "length": "detailed"},
                "priority": 80,
                "business_context": "collaboration"
            },
            
            # Platform-Specific Templates
            {
                "template_id": "spotify_optimization",
                "category": TemplateCategory.PLATFORM_SPECIFIC,
                "content_creator_type": ContentCreatorType.MUSICIAN,
                "template_content": "Optimizing for Spotify requires strategic thinking: 1) Perfect your {{ specific_topic or 'track metadata and tags' }}, 2) Time your releases for maximum algorithmic pickup, 3) Create playlist-worthy content, 4) Engage with Spotify's artist tools and analytics, 5) Build your follower base through consistent releases, and 6) Pitch to playlist curators effectively. Your current {{ dynamic_content.monthly_listeners or 'listener base' }} shows great potential for growth with the right strategy!",
                "variables": ["specific_topic", "dynamic_content"],
                "metadata": {"tone": "strategic", "length": "detailed"},
                "priority": 85,
                "platform_specific": "spotify"
            },
            {
                "template_id": "youtube_optimization",
                "category": TemplateCategory.PLATFORM_SPECIFIC,
                "content_creator_type": ContentCreatorType.GENERAL,
                "template_content": "YouTube success depends on understanding the algorithm: 1) Optimize your {{ specific_topic or 'video titles and thumbnails' }} for click-through rates, 2) Create compelling hooks in the first 15 seconds, 3) Maintain audience retention with engaging content structure, 4) Use end screens and cards strategically, 5) Engage actively with your community, and 6) Consistent upload scheduling. I can analyze your current {{ dynamic_content.performance_metrics or 'performance data' }} to suggest specific improvements.",
                "variables": ["specific_topic", "dynamic_content"],
                "metadata": {"tone": "analytical", "length": "detailed"},
                "priority": 85,
                "platform_specific": "youtube"
            },
            {
                "template_id": "instagram_optimization",
                "category": TemplateCategory.PLATFORM_SPECIFIC,
                "content_creator_type": ContentCreatorType.INFLUENCER,
                "template_content": "Instagram's visual-first platform requires a strategic approach: 1) Develop a cohesive aesthetic for your {{ content_format or 'content' }} feed, 2) Optimize posting times based on your audience insights, 3) Use relevant hashtags strategically (mix of popular and niche), 4) Leverage Stories and Reels for increased visibility, 5) Engage authentically with your community, and 6) Collaborate with complementary creators. Your {{ dynamic_content.follower_count or 'audience' }} engagement patterns suggest focusing on {{ specific_topic or 'video content' }} for growth.",
                "variables": ["content_format", "dynamic_content", "specific_topic"],
                "metadata": {"tone": "trendy", "length": "detailed"},
                "priority": 85,
                "platform_specific": "instagram"
            },
            
            # Help and Guidance Templates
            {
                "template_id": "help_content_workflow",
                "category": TemplateCategory.HELP,
                "content_creator_type": ContentCreatorType.GENERAL,
                "template_content": "I'm here to guide you through the complete {{ user_type }} workflow: 1) **Content Creation**: Optimize your {{ content_format or 'content' }} for quality and engagement, 2) **Protection Setup**: Implement AI-powered fingerprinting and monitoring, 3) **SEO Optimization**: Enhance discoverability across platforms, 4) **Distribution Strategy**: Multi-platform publishing with platform-specific optimization, 5) **Performance Monitoring**: Track analytics and adjust strategies, and 6) **Monetization Activation**: Set up and optimize revenue streams. Which step would you like to dive into first?",
                "variables": ["user_type", "content_format"],
                "metadata": {"tone": "helpful", "length": "structured"},
                "priority": 75
            },
            {
                "template_id": "help_getting_started",
                "category": TemplateCategory.HELP,
                "content_creator_type": ContentCreatorType.GENERAL,
                "template_content": "Getting started as a {{ user_type }} can feel overwhelming, but I'll make it simple: **Step 1**: Define your content niche and target audience, **Step 2**: Set up your {{ content_format or 'content' }} creation workflow, **Step 3**: Implement content protection from day one, **Step 4**: Establish your presence on key platforms like {{ platform_context or 'social media and streaming services' }}, **Step 5**: Create a consistent posting schedule, **Step 6**: Monitor performance and iterate. I'm here to help with each step. What's your current biggest challenge?",
                "variables": ["user_type", "content_format", "platform_context"],
                "metadata": {"tone": "encouraging", "length": "structured"},
                "priority": 80
            },
            
            # Error Handling Templates
            {
                "template_id": "error_generic",
                "category": TemplateCategory.ERROR_HANDLING,
                "content_creator_type": ContentCreatorType.GENERAL,
                "template_content": "I apologize, but I encountered an issue processing your request about {{ specific_topic or 'your content strategy' }}. Don't worry - I'm still here to help! Please try rephrasing your question, or let me know if you'd like assistance with: content optimization, protection strategies, monetization planning, or collaboration opportunities. As a {{ user_type }}, I have plenty of specific guidance I can offer.",
                "variables": ["specific_topic", "user_type"],
                "metadata": {"tone": "apologetic", "length": "short"},
                "priority": 60,
                "business_context": "error_recovery"
            },
            {
                "template_id": "clarification_needed",
                "category": TemplateCategory.ERROR_HANDLING,
                "content_creator_type": ContentCreatorType.GENERAL,
                "template_content": "I want to give you the most helpful response possible! Could you provide a bit more detail about {{ specific_topic or 'what you're looking for' }}? For example, are you interested in: improving your {{ content_format or 'content' }} quality, setting up protection measures, exploring monetization options, or finding collaboration opportunities? The more specific you are, the better I can tailor my advice to your {{ user_type }} journey.",
                "variables": ["specific_topic", "content_format", "user_type"],
                "metadata": {"tone": "clarifying", "length": "medium"},
                "priority": 65
            },
            
            # Business Workflow Templates
            {
                "template_id": "workflow_content_upload",
                "category": TemplateCategory.BUSINESS_WORKFLOW,
                "content_creator_type": ContentCreatorType.GENERAL,
                "template_content": "Here's your optimized content upload workflow: **Pre-Upload**: 1) Finalize your {{ content_format or 'content' }} with quality checks, 2) Generate fingerprint for protection tracking, 3) Prepare platform-specific metadata and descriptions, 4) Create engaging thumbnails/cover art. **Upload Process**: 1) Distribute across platforms like {{ platform_context or 'your target platforms' }}, 2) Apply SEO optimization for discoverability, 3) Activate protection monitoring, 4) Set up performance tracking. **Post-Upload**: 1) Monitor initial performance metrics, 2) Engage with early audience feedback, 3) Adjust promotional strategy based on data. Ready to upload your {{ specific_topic or 'latest creation' }}?",
                "variables": ["content_format", "platform_context", "specific_topic"],
                "metadata": {"tone": "procedural", "length": "comprehensive"},
                "priority": 85,
                "business_context": "workflow"
            },
            
            # Confirmation Templates
            {
                "template_id": "action_confirmation",
                "category": TemplateCategory.CONFIRMATION,
                "content_creator_type": ContentCreatorType.GENERAL,
                "template_content": "Perfect! I've {{ dynamic_content.action_taken or 'processed your request' }}. Your {{ content_format or 'content' }} {{ dynamic_content.status_update or 'strategy is now optimized' }}. {% if dynamic_content.next_steps %}Next steps: {{ dynamic_content.next_steps }}{% endif %} If you need any adjustments or have questions about the process, just let me know. As your AI assistant, I'm here to ensure your {{ user_type }} success!",
                "variables": ["dynamic_content", "content_format", "user_type"],
                "metadata": {"tone": "confirmatory", "length": "short"},
                "priority": 70
            }
        ]
    
    def _update_jinja_environment(self):
        """Update Jinja environment with current templates"""
        template_dict = {
            template.template_id: template.template_content 
            for template in self.templates.values()
        }
        self.jinja_env = Environment(loader=DictLoader(template_dict))
    
    async def get_template(self, template_id: str) -> Optional[ResponseTemplate]:
        """Get template by ID"""
        template = self.templates.get(template_id)
        if template:
            # Update usage count
            template.usage_count += 1
            await self.metrics.track_template_usage(template_id)
        return template
    
    async def find_templates(
        self,
        category: Optional[TemplateCategory] = None,
        content_creator_type: Optional[ContentCreatorType] = None,
        business_context: Optional[str] = None,
        platform_specific: Optional[str] = None,
        language: str = "en"
    ) -> List[ResponseTemplate]:
        """Find templates matching criteria"""
        matching_templates = []
        
        for template in self.templates.values():
            if category and template.category != category:
                continue
            if content_creator_type and template.content_creator_type not in [content_creator_type, ContentCreatorType.GENERAL]:
                continue
            if business_context and template.business_context != business_context:
                continue
            if platform_specific and template.platform_specific != platform_specific:
                continue
            if template.language != language:
                continue
                
            matching_templates.append(template)
        
        # Sort by priority and effectiveness
        matching_templates.sort(
            key=lambda t: (t.priority, t.effectiveness_score), 
            reverse=True
        )
        
        return matching_templates
    
    async def add_template(self, template: ResponseTemplate) -> bool:
        """Add new template to library"""



        try:
            self.templates[template.template_id] = template
            self._update_jinja_environment()
            await self.metrics.track_template_addition(template.template_id)
            return True
        except Exception as e:
            self.logger.error(f"Failed to add template {template.template_id}: {str(e)}")
            return False
    
    async def update_template_effectiveness(self, template_id: str, effectiveness_score: float):
        """Update template effectiveness based on user feedback"""
        if template_id in self.templates:
            self.templates[template_id].effectiveness_score = effectiveness_score
            await self.metrics.track_template_effectiveness(template_id, effectiveness_score)
    
    async def get_template_statistics(self) -> Dict[str, Any]:
        """Get template library statistics"""
        total_templates = len(self.templates)
        category_counts = {}
        creator_type_counts = {}
        
        for template in self.templates.values():
            category_counts[template.category.value] = category_counts.get(template.category.value, 0) + 1
            creator_type_counts[template.content_creator_type.value] = creator_type_counts.get(template.content_creator_type.value, 0) + 1
        
        avg_effectiveness = sum(t.effectiveness_score for t in self.templates.values()) / total_templates
        most_used = max(self.templates.values(), key=lambda t: t.usage_count)
        
        return {
            "total_templates": total_templates,
            "category_distribution": category_counts,
            "creator_type_distribution": creator_type_counts,
            "average_effectiveness": avg_effectiveness,
            "most_used_template": {
                "id": most_used.template_id,
                "usage_count": most_used.usage_count
            }
        }


class DynamicTemplateSelector:
    """Intelligent template selection based on context and performance"""
    
    def __init__(self, template_library: TemplateLibrary):
        self.library = template_library
        self.logger = logging.getLogger(__name__)
        self.cache = CacheManager()
        self.metrics = MetricsCollector()
    
    async def select_optimal_template(
        self,
        variables: TemplateVariables,
        context_priority: Dict[str, float],
        user_history: Optional[List[str]] = None
    ) -> Optional[ResponseTemplate]:
        """
        Select optimal template based on context and performance data
        
        Args:
            variables: Template variables with user context
            context_priority: Priority weights for different contexts
            user_history: Previous template IDs used for this user
            
        Returns:
            Best matching template or None
        """



        try:
            # Determine search criteria
            category = self._determine_category(variables, context_priority)
            creator_type = ContentCreatorType(variables.user_type)
            
            # Find candidate templates
            candidates = await self.library.find_templates(
                category=category,
                content_creator_type=creator_type,
                business_context=variables.business_context,
                platform_specific=variables.platform_context,
                language=variables.language
            )
            
            if not candidates:
                # Fallback to general templates
                candidates = await self.library.find_templates(
                    content_creator_type=ContentCreatorType.GENERAL,
                    language=variables.language
                )
            
            if not candidates:
                return None
            
            # Score and rank candidates
            scored_candidates = []
            for template in candidates:
                score = await self._calculate_template_score(
                    template, variables, context_priority, user_history
                )
                scored_candidates.append((template, score))
            
            # Sort by score and return best
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            best_template = scored_candidates[0][0]
            
            await self.metrics.track_template_selection(best_template.template_id, scored_candidates[0][1])
            return best_template
            
        except Exception as e:
            self.logger.error(f"Template selection failed: {str(e)}")
            return None
    
    def _determine_category(
        self, 
        variables: TemplateVariables, 
        context_priority: Dict[str, float]
    ) -> Optional[TemplateCategory]:
        """Determine most appropriate template category"""
        # Use context priority to determine category
        max_priority = max(context_priority.values()) if context_priority else 0
        
        if max_priority == 0:
            return None
        
        category_mapping = {
            "welcome": TemplateCategory.WELCOME,
            "help": TemplateCategory.HELP,
            "monetization": TemplateCategory.MONETIZATION,
            "protection": TemplateCategory.PROTECTION,
            "collaboration": TemplateCategory.COLLABORATION,
            "platform": TemplateCategory.PLATFORM_SPECIFIC,
            "guidance": TemplateCategory.GUIDANCE,
            "workflow": TemplateCategory.BUSINESS_WORKFLOW,
            "error": TemplateCategory.ERROR_HANDLING,
            "confirmation": TemplateCategory.CONFIRMATION
        }
        
        for context, priority in context_priority.items():
            if priority == max_priority and context in category_mapping:
                return category_mapping[context]
        
        return TemplateCategory.HELP  # Default fallback
    
    async def _calculate_template_score(
        self,
        template: ResponseTemplate,
        variables: TemplateVariables,
        context_priority: Dict[str, float],
        user_history: Optional[List[str]]
    ) -> float:
        """Calculate comprehensive template score"""
        score_components = {
            "base_effectiveness": template.effectiveness_score * 0.3,
            "priority_match": template.priority / 100.0 * 0.2,
            "context_alignment": await self._calculate_context_alignment(template, variables, context_priority) * 0.25,
            "personalization_fit": await self._calculate_personalization_fit(template, variables) * 0.15,
            "novelty_bonus": await self._calculate_novelty_score(template, user_history) * 0.1
        }
        
        total_score = sum(score_components.values())
        return min(total_score, 1.0)  # Cap at 1.0
    
    async def _calculate_context_alignment(
        self,
        template: ResponseTemplate,
        variables: TemplateVariables,
        context_priority: Dict[str, float]
    ) -> float:
        """Calculate how well template aligns with current context"""
        alignment_score = 0.0
        
        # Business context alignment
        if template.business_context and template.business_context == variables.business_context:
            alignment_score += 0.4
        
        # Platform alignment  
        if template.platform_specific and template.platform_specific == variables.platform_context:
            alignment_score += 0.3
        
        # Creator type exact match
        if template.content_creator_type.value == variables.user_type:
            alignment_score += 0.3
        elif template.content_creator_type == ContentCreatorType.GENERAL:
            alignment_score += 0.1
        
        return min(alignment_score, 1.0)
    
    async def _calculate_personalization_fit(
        self,
        template: ResponseTemplate,
        variables: TemplateVariables
    ) -> float:
        """Calculate personalization fit score"""
        personalization_data = variables.personalization_data
        if not personalization_data:
            return 0.5  # Neutral score
        
        fit_score = 0.0
        
        # Tone preference match
        preferred_tone = personalization_data.get("preferred_tone", "professional")
        template_tone = template.metadata.get("tone", "neutral")
        if preferred_tone == template_tone:
            fit_score += 0.4
        elif template_tone == "neutral":
            fit_score += 0.2
        
        # Length preference match
        preferred_length = personalization_data.get("preferred_length", "medium")
        template_length = template.metadata.get("length", "medium")
        if preferred_length == template_length:
            fit_score += 0.3
        
        # Complexity level match
        user_level = variables.user_level
        if user_level in template.metadata.get("suitable_levels", [user_level]):
            fit_score += 0.3
        
        return min(fit_score, 1.0)
    
    async def _calculate_novelty_score(
        self,
        template: ResponseTemplate,
        user_history: Optional[List[str]]
    ) -> float:
        """Calculate novelty score to avoid repetition"""
        if not user_history:
            return 1.0  # Full novelty for new users
        
        if template.template_id in user_history:
            # Reduce score based on how recently it was used
            recent_usage_positions = [
                i for i, tid in enumerate(reversed(user_history[-10:]))  # Last 10 interactions
                if tid == template.template_id
            ]
            
            if recent_usage_positions:
                most_recent_position = min(recent_usage_positions)
                novelty_score = max(0.1, (most_recent_position + 1) / 10.0)
                return novelty_score
        
        return 1.0  # Full novelty if not recently used


class TemplateCustomizer:
    """Advanced template customization and variable injection"""
    
    def __init__(self, template_library: TemplateLibrary):
        self.library = template_library
        self.logger = logging.getLogger(__name__)
        self.jinja_env = template_library.jinja_env
    
    async def customize_template(
        self,
        template: ResponseTemplate,
        variables: TemplateVariables,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Customize template with variables and context
        
        Args:
            template: Template to customize
            variables: Variables to inject
            additional_context: Additional context data
            
        Returns:
            Customized template content
        """



        try:
            # Prepare template variables
            template_vars = await self._prepare_template_variables(variables, additional_context)
            
            # Render template
            jinja_template = self.jinja_env.get_template(template.template_id)
            customized_content = jinja_template.render(**template_vars)
            
            # Post-process content
            processed_content = await self._post_process_content(customized_content, variables)
            
            return processed_content
            
        except TemplateNotFound:
            self.logger.error(f"Template {template.template_id} not found in Jinja environment")
            return template.template_content  # Return raw content as fallback
        except Exception as e:
            self.logger.error(f"Template customization failed: {str(e)}")
            return template.template_content  # Return raw content as fallback
    
    async def _prepare_template_variables(
        self,
        variables: TemplateVariables,
        additional_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare comprehensive template variables"""
        template_vars = variables.dict()
        
        # Add additional context
        if additional_context:
            template_vars.update(additional_context)
        
        # Add computed variables
        template_vars.update({
            "formatted_user_type": variables.user_type.replace('_', ' ').title(),
            "is_new_user": variables.personalization_data.get("is_new_user", True),
            "has_premium": variables.personalization_data.get("has_premium", False),
            "current_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "platform_list": self._format_platform_list(variables.platform_context),
            "content_type_display": self._format_content_type(variables.content_format)
        })
        
        # Add business logic helpers
        template_vars.update({
            "monetization_focus": self._determine_monetization_focus(variables),
            "protection_priority": self._determine_protection_priority(variables),
            "collaboration_potential": self._assess_collaboration_potential(variables)
        })
        
        return template_vars
    
    async def _post_process_content(self, content: str, variables: TemplateVariables) -> str:
        """Post-process rendered content for final optimization"""
        processed = content
        
        # Clean up extra whitespace
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        # Ensure proper sentence endings
        if not processed.endswith(('.', '!', '?')):
            processed += '.'
        
        # Apply language-specific post-processing
        if variables.language == "en":
            processed = self._apply_english_grammar_fixes(processed)
        
        # Apply personalization enhancements
        processed = await self._apply_personalization_enhancements(processed, variables)
        
        return processed
    
    def _format_platform_list(self, platform_context: Optional[str]) -> str:
        """Format platform context for display"""
        if not platform_context:
            return "major platforms"
        
        platforms = platform_context.split(',')
        if len(platforms) == 1:
            return platforms[0].strip()
        elif len(platforms) == 2:
            return f"{platforms[0].strip()} and {platforms[1].strip()}"
        else:
            return f"{', '.join(p.strip() for p in platforms[:-1])}, and {platforms[-1].strip()}"
    
    def _format_content_type(self, content_format: Optional[str]) -> str:
        """Format content type for display"""
        if not content_format:
            return "content"
        
        format_mappings = {
            "audio": "music and audio content",
            "video": "video content",
            "image": "visual content and photography",
            "text": "written content and articles",
            "mixed": "multi-format content"
        }
        
        return format_mappings.get(content_format, content_format)
    
    def _determine_monetization_focus(self, variables: TemplateVariables) -> str:
        """Determine primary monetization focus for user type"""
        focus_map = {
            "musician": "streaming royalties and licensing",
            "influencer": "brand partnerships and sponsored content",
            "photographer": "stock licensing and client work",
            "comedian": "performance bookings and merchandise",
            "blogger": "ad revenue and affiliate marketing",
            "podcaster": "sponsorships and premium content"
        }
        
        return focus_map.get(variables.user_type, "content monetization")
    
    def _determine_protection_priority(self, variables: TemplateVariables) -> str:
        """Determine protection priority for user type"""
        priority_map = {
            "musician": "audio fingerprinting and copyright protection",
            "photographer": "image watermarking and usage tracking",
            "comedian": "content theft prevention and attribution",
            "blogger": "plagiarism detection and content ownership",
            "video_creator": "video fingerprinting and unauthorized distribution prevention"
        }
        
        return priority_map.get(variables.user_type, "intellectual property protection")
    
    def _assess_collaboration_potential(self, variables: TemplateVariables) -> str:
        """Assess collaboration potential for user type"""
        potential_map = {
            "musician": "high potential for cross-genre collaborations and remixes",
            "influencer": "excellent opportunities for brand and creator partnerships",
            "photographer": "strong potential for creative collaborations and shoots",
            "comedian": "great opportunities for writing and performance partnerships",
            "blogger": "good potential for guest posting and content exchanges"
        }
        
        return potential_map.get(variables.user_type, "good collaboration opportunities")
    
    def _apply_english_grammar_fixes(self, content: str) -> str:
        """Apply basic English grammar fixes"""
        # Fix common issues
        fixes = [
            (r'\s+([.!?])', r'\1'),  # Remove space before punctuation
            (r'([.!?])\s*([A-Z])', r'\1 \2'),  # Ensure space after punctuation
            (r'\bi\b', 'I'),  # Capitalize standalone 'i'
            (r'\s+', ' ')  # Normalize whitespace
        ]
        
        processed = content
        for pattern, replacement in fixes:
            processed = re.sub(pattern, replacement, processed)
        
        return processed
    
    async def _apply_personalization_enhancements(self, content: str, variables: TemplateVariables) -> str:
        """Apply personalization-based content enhancements"""
        personalization = variables.personalization_data
        
        # Adjust tone based on preferences
        preferred_tone = personalization.get("preferred_tone", "professional")
        
        if preferred_tone == "casual":
            content = self._make_more_casual(content)
        elif preferred_tone == "formal":
            content = self._make_more_formal(content)
        elif preferred_tone == "enthusiastic":
            content = self._add_enthusiasm(content)
        
        return content
    
    def _make_more_casual(self, content: str) -> str:
        """Make content more casual in tone"""
        casual_replacements = {
            "utilize": "use",
            "facilitate": "help with",
            "implement": "set up",
            "optimize": "improve",
            "commence": "start"
        }
        
        processed = content
        for formal, casual in casual_replacements.items():
            processed = re.sub(f"\\b{formal}\\b", casual, processed, flags=re.IGNORECASE)
        
        return processed
    
    def _make_more_formal(self, content: str) -> str:
        """Make content more formal in tone"""
        formal_replacements = {
            "help": "assist",
            "use": "utilize",
            "start": "commence",
            "improve": "enhance",
            "set up": "establish"
        }
        
        processed = content
        for casual, formal in formal_replacements.items():
            processed = re.sub(f"\\b{casual}\\b", formal, processed, flags=re.IGNORECASE)
        
        return processed
    
    def _add_enthusiasm(self, content: str) -> str:
        """Add enthusiasm to content"""
        if not re.search(r'[!]', content):
            # Add exclamation to end if none present
            content = re.sub(r'([.])$', '!', content)
        
        # Add enthusiastic phrases
        enthusiastic_additions = [
            ("I can help", "I'd love to help"),
            ("recommend", "highly recommend"),
            ("good", "excellent"),
            ("will help", "will absolutely help")
        ]
        
        processed = content
        for original, enthusiastic in enthusiastic_additions:
            processed = re.sub(f"\\b{original}\\b", enthusiastic, processed, flags=re.IGNORECASE)
        
        return processed


class TemplateManager:
    """Central template management system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.library = TemplateLibrary()
        self.selector = DynamicTemplateSelector(self.library)
        self.customizer = TemplateCustomizer(self.library)
        self.cache = CacheManager()
        self.metrics = MetricsCollector()
    
    async def generate_response_from_template(
        self,
        variables: TemplateVariables,
        context_priority: Dict[str, float],
        user_history: Optional[List[str]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Generate complete response using template system
        
        Args:
            variables: Template variables
            context_priority: Context priority weights
            user_history: User's template history
            additional_context: Additional context data
            
        Returns:
            Generated response text or None
        """



        try:
            # Check cache first
            cache_key = self._generate_cache_key(variables, context_priority)
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                await self.metrics.track_template_cache_hit()
                return cached_response
            
            # Select optimal template
            template = await self.selector.select_optimal_template(
                variables, context_priority, user_history
            )
            
            if not template:
                self.logger.warning("No suitable template found")
                return None
            
            # Customize template
            response = await self.customizer.customize_template(
                template, variables, additional_context
            )
            
            # Cache the response
            await self.cache.set(cache_key, response, expire=1800)  # 30 minutes
            
            # Track metrics
            await self.metrics.track_template_response_generation(template.template_id, len(response))
            
            return response
            
        except Exception as e:
            self.logger.error(f"Template response generation failed: {str(e)}")
            return None
    
    async def get_template_recommendations(
        self,
        variables: TemplateVariables,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get template recommendations for given context"""



        try:
            creator_type = ContentCreatorType(variables.user_type)
            candidates = await self.library.find_templates(
                content_creator_type=creator_type,
                language=variables.language
            )
            
            recommendations = []
            for template in candidates[:limit]:
                recommendations.append({
                    "template_id": template.template_id,
                    "category": template.category.value,
                    "description": template.metadata.get("description", "Template for " + template.category.value),
                    "effectiveness_score": template.effectiveness_score,
                    "usage_count": template.usage_count,
                    "suitable_for": template.content_creator_type.value
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get template recommendations: {str(e)}")
            return []
    
    async def update_template_performance(
        self,
        template_id: str,
        user_feedback: Dict[str, Any]
    ):
        """Update template performance based on user feedback"""



        try:
            if template_id in self.library.templates:
                # Calculate new effectiveness score based on feedback
                current_score = self.library.templates[template_id].effectiveness_score
                feedback_score = user_feedback.get("rating", 0.5)  # 0-1 scale
                
                # Weighted average: 80% current, 20% new feedback
                new_score = (current_score * 0.8) + (feedback_score * 0.2)
                
                await self.library.update_template_effectiveness(template_id, new_score)
                await self.metrics.track_template_feedback(template_id, feedback_score)
                
        except Exception as e:
            self.logger.error(f"Failed to update template performance: {str(e)}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive template system statistics"""



        try:
            library_stats = await self.library.get_template_statistics()
            
            # Add additional metrics
            cache_stats = await self.cache.get_stats() if hasattr(self.cache, 'get_stats') else {}
            
            return {
                "library_stats": library_stats,
                "cache_stats": cache_stats,
                "system_health": "operational"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {str(e)}")
            return {"error": str(e)}
    
    def _generate_cache_key(self, variables: TemplateVariables, context_priority: Dict[str, float]) -> str:
        """Generate cache key for template response"""
        key_components = [
            variables.user_type,
            variables.content_format or "none",
            variables.business_context or "none",
            variables.platform_context or "none",
            str(sorted(context_priority.items())),
            variables.language
        ]
        
        return f"template_response:{hash('|'.join(key_components))}"


class ResponseTemplateEngine:
    """High-level template engine interface"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
        self.logger = logging.getLogger(__name__)
    
    async def generate_contextual_response(
        self,
        user_type: str,
        content_format: Optional[str] = None,
        platform_context: Optional[str] = None,
        business_context: Optional[str] = None,
        user_name: Optional[str] = None,
        context_weights: Optional[Dict[str, float]] = None,
        personalization_data: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Optional[str]:
        """Generate contextual response using template system"""
        
        # Prepare variables
        variables = TemplateVariables(
            user_name=user_name,
            user_type=user_type,
            content_format=content_format,
            platform_context=platform_context,
            business_context=business_context,
            language=language,
            personalization_data=personalization_data or {}
        )
        
        # Default context weights
        default_weights = {
            "help": 0.7,
            "monetization": 0.3,
            "protection": 0.3,
            "collaboration": 0.2,
            "platform": 0.4
        }
        
        context_priority = context_weights or default_weights
        
        # Generate response
        return await self.template_manager.generate_response_from_template(
            variables, context_priority
        )


# Export main classes
__all__ = [
    "TemplateManager",
    "DynamicTemplateSelector",
    "TemplateCustomizer", 
    "TemplateLibrary",
    "ResponseTemplateEngine",
    "TemplateCategory",
    "ContentCreatorType",
    "TemplateVariables",
    "ResponseTemplate"
]
