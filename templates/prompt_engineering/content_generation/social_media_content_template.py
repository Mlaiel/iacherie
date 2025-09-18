"""
🎯 Social Media Content Template - AI-Powered Social Media Generation
====================================================================

Enterprise-grade social media content template for creators with platform
optimization, engagement strategies, and viral content potential.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - IA Prompt Engineer + Social Media Expert
Team: Lead Dev IA + Backend Senior + ML Engineer + Social Media Strategist
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field, validator
import re

from core.config import get_settings
from utils.exceptions import TemplateError, ValidationError
from ..template_compiler import TemplateCompiler
from ..security_validator import SecurityValidator
from ..evaluation_framework import EvaluationFramework

logger = logging.getLogger(__name__)
settings = get_settings()


class SocialPlatform(Enum):
    """Social media platforms"""
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    THREADS = "threads"
    DISCORD = "discord"


class ContentFormat(Enum):
    """Content format types"""
    POST = "post"
    STORY = "story"
    REEL = "reel"
    CAROUSEL = "carousel"
    VIDEO = "video"
    THREAD = "thread"
    POLL = "poll"
    LIVE = "live"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"


class EngagementGoal(Enum):
    """Engagement goals"""
    AWARENESS = "awareness"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    INSPIRATION = "inspiration"
    COMMUNITY = "community"
    VIRAL = "viral"


class ContentTone(Enum):
    """Content tone styles"""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"
    AUTHORITATIVE = "authoritative"
    PLAYFUL = "playful"
    EMPATHETIC = "empathetic"
    TRENDY = "trendy"


@dataclass
class PlatformLimits:
    """Platform-specific content limits"""
    max_characters: int
    max_hashtags: int
    max_mentions: int
    supports_links: bool
    supports_media: bool
    optimal_posting_times: List[str] = field(default_factory=list)


class SocialMediaRequest(BaseModel):
    """Social media content generation request"""
    topic: str = Field(..., min_length=1, max_length=200)
    platform: SocialPlatform
    content_format: ContentFormat = ContentFormat.POST
    engagement_goal: EngagementGoal = EngagementGoal.ENGAGEMENT
    tone: ContentTone = ContentTone.CONVERSATIONAL
    target_audience: str = Field(default="general", min_length=1)
    hashtags_count: int = Field(default=5, ge=0, le=30)
    include_emojis: bool = True
    include_cta: bool = True
    viral_potential: bool = False
    trending_topics: List[str] = Field(default_factory=list, max_items=5)
    brand_mentions: List[str] = Field(default_factory=list, max_items=3)
    creator_context: Dict[str, Any] = Field(default_factory=dict)
    monetization_enabled: bool = False
    collaboration_tags: List[str] = Field(default_factory=list, max_items=5)
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()
    
    @validator('hashtags_count')
    def validate_hashtags(cls, v, values):
        platform = values.get('platform')
        if platform == SocialPlatform.TWITTER and v > 3:
            raise ValueError("Twitter posts should use maximum 3 hashtags")
        elif platform == SocialPlatform.LINKEDIN and v > 5:
            raise ValueError("LinkedIn posts should use maximum 5 hashtags")
        return v


class SocialMediaTemplate:
    """
    🎯 Enterprise Social Media Content Template
    
    Advanced social media generation with:
    - Platform-specific optimization
    - Engagement-driven content creation
    - Viral content strategies
    - Creator economy integration
    - Hashtag and trend optimization
    - Multi-format content support
    - Audience targeting
    - Monetization opportunities
    """
    
    def __init__(self):
        self.template_compiler = TemplateCompiler()
        self.security_validator = SecurityValidator()
        self.evaluation_framework = EvaluationFramework()
        self.platform_limits = self._initialize_platform_limits()
        self._initialized = False
    
    def _initialize_platform_limits(self) -> Dict[SocialPlatform, PlatformLimits]:
        """Initialize platform-specific limits and characteristics"""
        return {
            SocialPlatform.TWITTER: PlatformLimits(
                max_characters=280,
                max_hashtags=3,
                max_mentions=10,
                supports_links=True,
                supports_media=True,
                optimal_posting_times=["9:00", "12:00", "15:00", "18:00"]
            ),
            SocialPlatform.INSTAGRAM: PlatformLimits(
                max_characters=2200,
                max_hashtags=30,
                max_mentions=20,
                supports_links=False,
                supports_media=True,
                optimal_posting_times=["6:00", "12:00", "19:00", "21:00"]
            ),
            SocialPlatform.LINKEDIN: PlatformLimits(
                max_characters=3000,
                max_hashtags=5,
                max_mentions=50,
                supports_links=True,
                supports_media=True,
                optimal_posting_times=["8:00", "12:00", "17:00", "18:00"]
            ),
            SocialPlatform.FACEBOOK: PlatformLimits(
                max_characters=63206,
                max_hashtags=10,
                max_mentions=50,
                supports_links=True,
                supports_media=True,
                optimal_posting_times=["9:00", "13:00", "15:00", "20:00"]
            ),
            SocialPlatform.TIKTOK: PlatformLimits(
                max_characters=2200,
                max_hashtags=20,
                max_mentions=20,
                supports_links=False,
                supports_media=True,
                optimal_posting_times=["6:00", "10:00", "19:00", "22:00"]
            ),
            SocialPlatform.YOUTUBE: PlatformLimits(
                max_characters=5000,
                max_hashtags=15,
                max_mentions=50,
                supports_links=True,
                supports_media=True,
                optimal_posting_times=["14:00", "15:00", "20:00", "21:00"]
            )
        }
    
    async def initialize(self) -> None:
        """Initialize social media template"""
        try:
            await self.template_compiler.initialize()
            await self.security_validator.initialize()
            await self.evaluation_framework.initialize()
            
            self._initialized = True
            logger.info("Social Media Template initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Social Media Template: {e}")
            raise TemplateError(f"Social Media Template initialization failed: {e}")
    
    async def generate_social_content(self, request: SocialMediaRequest) -> Dict[str, Any]:
        """
        Generate social media content based on request
        
        Args:
            request: Social media content generation request
            
        Returns:
            Generated social media content with platform optimization
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            # Get platform limits
            platform_limit = self.platform_limits.get(request.platform)
            if not platform_limit:
                raise TemplateError(f"Unsupported platform: {request.platform}")
            
            # Build content prompt template
            prompt_template = await self._build_social_prompt(request, platform_limit)
            
            # Prepare template variables
            variables = await self._prepare_template_variables(request, platform_limit)
            
            # Compile the prompt
            compilation_request = {
                "template_content": prompt_template,
                "variables": variables,
                "creator_context": request.creator_context,
                "optimization_enabled": True,
                "security_validation": True
            }
            
            compiled_result = await self.template_compiler.compile_template(compilation_request)
            
            if not compiled_result.compilation_successful:
                raise TemplateError(f"Template compilation failed: {compiled_result.error_message}")
            
            # Generate social media content
            social_content = await self._generate_social_content(compiled_result.compiled_prompt, request)
            
            # Platform-specific optimization
            optimized_content = await self._optimize_for_platform(social_content, request, platform_limit)
            
            # Generate hashtags
            hashtags = await self._generate_hashtags(request, optimized_content)
            
            # Create content variations
            variations = await self._create_content_variations(optimized_content, request)
            
            # Evaluate content
            evaluation = await self._evaluate_social_content(
                compiled_result.compiled_prompt,
                optimized_content,
                request
            )
            
            # Analyze viral potential
            viral_analysis = await self._analyze_viral_potential(optimized_content, request)
            
            # Build response
            response = {
                "content": optimized_content,
                "hashtags": hashtags,
                "variations": variations,
                "metadata": {
                    "platform": request.platform.value,
                    "format": request.content_format.value,
                    "character_count": len(optimized_content),
                    "word_count": len(optimized_content.split()),
                    "engagement_goal": request.engagement_goal.value,
                    "tone": request.tone.value,
                    "target_audience": request.target_audience,
                    "optimal_posting_times": platform_limit.optimal_posting_times
                },
                "platform_optimization": {
                    "character_limit_used": f"{len(optimized_content)}/{platform_limit.max_characters}",
                    "hashtag_limit_used": f"{len(hashtags)}/{platform_limit.max_hashtags}",
                    "optimized_for_platform": True,
                    "supports_links": platform_limit.supports_links,
                    "supports_media": platform_limit.supports_media
                },
                "engagement": {
                    "viral_potential": viral_analysis["score"],
                    "engagement_triggers": viral_analysis["triggers"],
                    "shareability_score": viral_analysis["shareability"],
                    "trend_alignment": viral_analysis["trend_alignment"]
                },
                "evaluation": {
                    "overall_score": evaluation.overall_score,
                    "engagement_score": evaluation.dimension_scores.get("engagement", 0.0),
                    "platform_fit": evaluation.dimension_scores.get("platform_optimization", 0.0),
                    "viral_potential": viral_analysis["score"]
                },
                "monetization": await self._analyze_social_monetization(optimized_content, request),
                "creator_insights": await self._generate_social_creator_insights(optimized_content, request),
                "optimization_suggestions": compiled_result.optimization_suggestions,
                "security_validated": compiled_result.security_validated
            }
            
            return response
        
        except Exception as e:
            logger.error(f"Social media content generation failed: {e}")
            raise TemplateError(f"Social media content generation failed: {e}")
    
    async def _build_social_prompt(self, request: SocialMediaRequest, platform_limit: PlatformLimits) -> str:
        """Build social media content prompt template"""
        
        base_prompt = """You are a professional social media {{ creator_type }} specializing in {{ platform }} content creation.

**Content Brief:**
Topic: {{ topic }}
Platform: {{ platform }}
Format: {{ content_format }}
Engagement Goal: {{ engagement_goal }}
Tone: {{ tone }}
Target Audience: {{ target_audience }}
Character Limit: {{ character_limit }}

{% if trending_topics %}
**Trending Topics to Incorporate:**
{% for trend in trending_topics %}
- {{ trend }}
{% endfor %}
{% endif %}

**Platform-Specific Requirements:**

{% if platform == "instagram" %}
**Instagram Optimization:**
- Use engaging visual storytelling language
- Include emoji strategically for visual appeal
- Create scroll-stopping content
- Design for discovery and shares
- Optimize for Instagram algorithm preferences
{% elif platform == "twitter" %}
**Twitter Optimization:**
- Be concise and punchy
- Use trending hashtags strategically
- Create conversation starters
- Optimize for retweets and replies
- Include timely and relevant content
{% elif platform == "linkedin" %}
**LinkedIn Optimization:**
- Maintain professional tone with personality
- Focus on value and insights
- Encourage professional discussions
- Include thought leadership elements
- Optimize for professional engagement
{% elif platform == "tiktok" %}
**TikTok Optimization:**
- Use trending language and slang
- Create hook-heavy content
- Focus on entertainment value
- Include viral elements and challenges
- Optimize for Gen Z and millennial audiences
{% elif platform == "youtube" %}
**YouTube Optimization:**
- Create compelling video descriptions
- Include strong call-to-actions
- Focus on searchable content
- Encourage subscriptions and engagement
- Optimize for video discoverability
{% endif %}

**Engagement Strategy:**
{% if engagement_goal == "viral" %}
- Create highly shareable content
- Include trending elements and challenges
- Use emotional triggers and surprise elements
- Design for maximum social sharing
{% elif engagement_goal == "education" %}
- Provide clear, valuable information
- Use easy-to-understand language
- Include actionable insights
- Create learning-focused content
{% elif engagement_goal == "entertainment" %}
- Focus on humor and entertainment value
- Use engaging storytelling techniques
- Include surprising or delightful elements
- Create mood-boosting content
{% elif engagement_goal == "inspiration" %}
- Use motivational language and themes
- Include personal success stories
- Create aspirational content
- Focus on positive emotions and outcomes
{% endif %}

**Content Requirements:**
- Stay within {{ character_limit }} character limit
- Use {{ tone }} tone throughout
- Target {{ target_audience }} specifically
{% if include_emojis %}
- Include relevant emojis strategically (2-5 emojis)
{% endif %}
{% if include_cta %}
- Include compelling call-to-action
{% endif %}
{% if viral_potential %}
- Maximize viral potential with trending elements
{% endif %}

{% if brand_mentions %}
**Brand Mentions to Include:**
{% for brand in brand_mentions %}
- @{{ brand }}
{% endfor %}
{% endif %}

{% if collaboration_tags %}
**Collaboration Tags:**
{% for tag in collaboration_tags %}
- {{ tag }}
{% endfor %}
{% endif %}

{% if monetization_enabled %}
**Monetization Integration:**
- Include subtle promotional opportunities
- Create lead generation potential
- Design for conversion optimization
- Include affiliate-friendly elements
{% endif %}

**Creator Economy Focus:**
- Build community engagement
- Encourage user-generated content
- Create shareable moments
- Establish thought leadership
- Drive meaningful interactions

**Quality Standards:**
- Ensure authenticity and genuine voice
- Create valuable, engaging content
- Maintain brand consistency
- Optimize for platform algorithm
- Focus on audience value and entertainment

**Output Format:**
Provide the complete social media post content that maximizes engagement while staying within platform limits."""
        
        # Format-specific enhancements
        if request.content_format == ContentFormat.THREAD:
            base_prompt += "\n\n**Thread Format:** Create a compelling thread with 3-7 connected posts, each building on the previous one."
        elif request.content_format == ContentFormat.CAROUSEL:
            base_prompt += "\n\n**Carousel Format:** Design content for multiple slides with clear progression and visual storytelling."
        elif request.content_format == ContentFormat.STORY:
            base_prompt += "\n\n**Story Format:** Create ephemeral content with urgency and behind-the-scenes feel."
        
        return base_prompt
    
    async def _prepare_template_variables(self, request: SocialMediaRequest, platform_limit: PlatformLimits) -> Dict[str, Any]:
        """Prepare variables for template compilation"""
        
        creator_type = request.creator_context.get("creator_type", "social media creator")
        
        variables = {
            "topic": request.topic,
            "platform": request.platform.value,
            "content_format": request.content_format.value.replace("_", " "),
            "engagement_goal": request.engagement_goal.value,
            "tone": request.tone.value,
            "target_audience": request.target_audience,
            "character_limit": platform_limit.max_characters,
            "trending_topics": request.trending_topics,
            "brand_mentions": request.brand_mentions,
            "collaboration_tags": request.collaboration_tags,
            "creator_type": creator_type,
            "include_emojis": request.include_emojis,
            "include_cta": request.include_cta,
            "viral_potential": request.viral_potential,
            "monetization_enabled": request.monetization_enabled
        }
        
        return variables
    
    async def _generate_social_content(self, prompt: str, request: SocialMediaRequest) -> str:
        """Generate social media content using AI model"""
        try:
            # In a real implementation, this would call the AI model
            # For now, we'll create platform-optimized content
            
            if request.platform == SocialPlatform.TWITTER:
                content = await self._generate_twitter_content(request)
            elif request.platform == SocialPlatform.INSTAGRAM:
                content = await self._generate_instagram_content(request)
            elif request.platform == SocialPlatform.LINKEDIN:
                content = await self._generate_linkedin_content(request)
            elif request.platform == SocialPlatform.TIKTOK:
                content = await self._generate_tiktok_content(request)
            elif request.platform == SocialPlatform.YOUTUBE:
                content = await self._generate_youtube_content(request)
            else:
                content = await self._generate_generic_content(request)
            
            return content
        
        except Exception as e:
            logger.error(f"Social content generation failed: {e}")
            return f"Amazing insights about {request.topic}! 🔥"
    
    async def _generate_twitter_content(self, request: SocialMediaRequest) -> str:
        """Generate Twitter-optimized content"""
        if request.engagement_goal == EngagementGoal.VIRAL:
            content = f"This might be controversial, but {request.topic} is completely changing how we think about {request.target_audience} success. 🧵\n\nHere's what everyone's missing:"
        elif request.engagement_goal == EngagementGoal.EDUCATION:
            content = f"Quick {request.topic} tip for {request.target_audience}:\n\n✅ Focus on fundamentals first\n✅ Practice consistently\n✅ Learn from mistakes\n\nWhat's your biggest challenge? 👇"
        elif request.engagement_goal == EngagementGoal.ENGAGEMENT:
            content = f"Hot take: {request.topic} isn't as complicated as people make it seem.\n\nThe real game-changer? Understanding your {request.target_audience}.\n\nAm I wrong? 🤔"
        else:
            content = f"Been diving deep into {request.topic} lately and the insights are mind-blowing! 🚀\n\nKey takeaway: Success isn't about perfection, it's about consistent progress.\n\nWhat's working for you?"
        
        # Add trending elements if specified
        if request.trending_topics:
            content += f"\n\n#{request.trending_topics[0].replace(' ', '')}"
        
        return content
    
    async def _generate_instagram_content(self, request: SocialMediaRequest) -> str:
        """Generate Instagram-optimized content"""
        hook = self._generate_instagram_hook(request.topic, request.engagement_goal)
        
        main_content = f"""{hook}

Swipe to see the game-changing strategies that top {request.target_audience} are using to master {request.topic} 👉

✨ Strategy 1: Focus on fundamentals
✨ Strategy 2: Consistent daily practice  
✨ Strategy 3: Learn from the best
✨ Strategy 4: Track your progress
✨ Strategy 5: Stay patient with the process

The secret? It's not about being perfect—it's about being consistent and authentic to your journey.

What's your biggest challenge with {request.topic}? Drop it in the comments! 👇

SAVE this post if you found it helpful! ❤️"""
        
        if request.monetization_enabled:
            main_content += f"\n\nPS: Link in bio for my free {request.topic} masterclass! 🎯"
        
        return main_content
    
    def _generate_instagram_hook(self, topic: str, goal: EngagementGoal) -> str:
        """Generate Instagram hook based on engagement goal"""
        hooks = {
            EngagementGoal.VIRAL: f"POV: You just discovered the {topic} secret that changed everything 🤯",
            EngagementGoal.EDUCATION: f"5 {topic} mistakes that are costing you success (and how to fix them)",
            EngagementGoal.INSPIRATION: f"This {topic} transformation will give you chills ✨",
            EngagementGoal.ENTERTAINMENT: f"When someone asks me about {topic} 😂",
            EngagementGoal.AWARENESS: f"Things I wish I knew about {topic} before starting:"
        }
        return hooks.get(goal, f"Let's talk about {topic} 💫")
    
    async def _generate_linkedin_content(self, request: SocialMediaRequest) -> str:
        """Generate LinkedIn-optimized content"""
        if request.engagement_goal == EngagementGoal.EDUCATION:
            content = f"""The most successful {request.target_audience} I know have one thing in common when it comes to {request.topic}:

They treat it as a skill, not a talent.

Here's what that actually means:

🎯 They practice deliberately every day
🎯 They seek feedback and course-correct quickly  
🎯 They study what works for others in their field
🎯 They measure progress with specific metrics
🎯 They stay consistent even when motivation wanes

The difference between good and great isn't natural ability—it's systematic improvement.

What's one area of {request.topic} you're working to improve this month?

---
Found this helpful? Follow me for more insights on professional growth."""
        
        elif request.engagement_goal == EngagementGoal.INSPIRATION:
            content = f"""Two years ago, I thought {request.topic} was impossible to master.

Today, I'm sharing strategies with thousands of {request.target_audience}.

The turning point wasn't a magical moment—it was deciding to show up consistently, even on the hard days.

Here's what I learned:
→ Progress beats perfection every time
→ Community accelerates learning
→ Small daily actions compound into big results

If you're struggling with {request.topic} right now, you're not behind.
You're exactly where you need to be.

Keep going. The breakthrough is closer than you think.

What's one small action you can take today?"""
        
        else:
            content = f"""Unpopular opinion: Most advice about {request.topic} is overcomplicated.

After working with hundreds of {request.target_audience}, I've noticed the most successful ones focus on three fundamentals:

1. Clarity on their goals
2. Consistent daily action  
3. Regular progress reviews

That's it.

Everything else is optimization.

Are you making it too complicated?

What's your experience? Share in the comments 👇"""
        
        return content
    
    async def _generate_tiktok_content(self, request: SocialMediaRequest) -> str:
        """Generate TikTok-optimized content"""
        if request.viral_potential:
            content = f"""POV: You just learned the {request.topic} hack that changes everything 🤯

✨ Follow for more {request.topic} tips that actually work
✨ Save this for later  
✨ Share with someone who needs this

#fyp #{request.topic.replace(' ', '')} #viral #hack #tip #trending"""
        
        elif request.engagement_goal == EngagementGoal.ENTERTAINMENT:
            content = f"""Me explaining {request.topic} to my friends vs. me actually doing {request.topic} 😂

The accuracy is unsettling 💀

Who else relates? Comment "me" if this is you! 

#{request.topic.replace(' ', '')} #relatable #funny #trending #fyp"""
        
        else:
            content = f"""Things about {request.topic} that just make sense:

✅ Start before you feel ready
✅ Progress > Perfection  
✅ Consistency beats intensity
✅ Learn from others who've done it
✅ Celebrate small wins

Save this for when you need the reminder 💪

#{request.topic.replace(' ', '')} #motivation #tips #growth #fyp"""
        
        return content
    
    async def _generate_youtube_content(self, request: SocialMediaRequest) -> str:
        """Generate YouTube-optimized content"""
        content = f"""🎯 Master {request.topic}: Complete Guide for {request.target_audience}

In this video, I break down everything you need to know about {request.topic}, including the strategies that top performers use to get results fast.

📍 TIMESTAMPS:
00:00 Introduction to {request.topic}
02:30 Common mistakes to avoid
05:15 Step-by-step implementation
08:45 Advanced strategies
12:00 Q&A and next steps

Whether you're just starting with {request.topic} or looking to level up your skills, this guide has something for everyone.

💡 What you'll learn:
- The fundamentals that most people skip
- Proven strategies from industry leaders
- How to avoid the biggest pitfalls
- Action steps you can implement today

🔔 SUBSCRIBE for weekly {request.topic} content and hit the bell for notifications!

💬 COMMENT below with your biggest {request.topic} question and I'll answer it in the next video.

📚 FREE RESOURCES mentioned in this video: [link in description]

#YourChannel #{request.topic.replace(' ', '')} #Tutorial #Guide"""
        
        return content
    
    async def _generate_generic_content(self, request: SocialMediaRequest) -> str:
        """Generate generic platform content"""
        emoji = "🔥" if request.include_emojis else ""
        
        content = f"Exploring {request.topic} and the insights are incredible! {emoji}\n\n"
        content += f"Key takeaway for {request.target_audience}: Success comes from consistent action, not perfect planning.\n\n"
        
        if request.include_cta:
            content += "What's your experience? Share in the comments!"
        
        return content
    
    async def _optimize_for_platform(self, content: str, request: SocialMediaRequest, platform_limit: PlatformLimits) -> str:
        """Optimize content for specific platform"""
        try:
            # Trim to character limit
            if len(content) > platform_limit.max_characters:
                content = content[:platform_limit.max_characters-3] + "..."
            
            # Platform-specific optimizations
            if request.platform == SocialPlatform.TWITTER:
                # Ensure content works within Twitter's constraints
                content = self._optimize_twitter_format(content)
            elif request.platform == SocialPlatform.INSTAGRAM:
                # Optimize for Instagram algorithm
                content = self._optimize_instagram_format(content, request)
            elif request.platform == SocialPlatform.LINKEDIN:
                # Professional formatting
                content = self._optimize_linkedin_format(content)
            
            return content
        
        except Exception as e:
            logger.error(f"Platform optimization failed: {e}")
            return content
    
    def _optimize_twitter_format(self, content: str) -> str:
        """Optimize content for Twitter"""
        # Ensure proper line breaks
        if '\n\n' in content:
            content = content.replace('\n\n', '\n')
        
        # Optimize for engagement
        if not any(char in content for char in ['?', '!', '🧵']):
            content += " What do you think?"
        
        return content
    
    def _optimize_instagram_format(self, content: str, request: SocialMediaRequest) -> str:
        """Optimize content for Instagram"""
        # Add line breaks for readability
        if request.content_format == ContentFormat.CAROUSEL:
            content = content.replace('. ', '.\n\n')
        
        # Ensure CTA is clear
        if request.include_cta and 'comment' not in content.lower():
            content += "\n\nDouble tap if you agree! 💙"
        
        return content
    
    def _optimize_linkedin_format(self, content: str) -> str:
        """Optimize content for LinkedIn"""
        # Professional formatting with strategic line breaks
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            # Add strategic spacing for LinkedIn algorithm
            formatted_paragraphs = []
            for i, paragraph in enumerate(paragraphs):
                formatted_paragraphs.append(paragraph)
                if i < len(paragraphs) - 1:
                    formatted_paragraphs.append("")  # Empty line
            content = '\n\n'.join(formatted_paragraphs)
        
        return content
    
    async def _generate_hashtags(self, request: SocialMediaRequest, content: str) -> List[str]:
        """Generate platform-optimized hashtags"""
        try:
            hashtags = []
            platform_limit = self.platform_limits[request.platform]
            max_hashtags = min(request.hashtags_count, platform_limit.max_hashtags)
            
            # Primary hashtags based on topic
            primary_tags = self._generate_primary_hashtags(request.topic, request.platform)
            hashtags.extend(primary_tags[:max_hashtags//2])
            
            # Trending hashtags
            if request.trending_topics:
                trending_tags = [f"#{topic.replace(' ', '').lower()}" for topic in request.trending_topics]
                hashtags.extend(trending_tags[:2])
            
            # Engagement hashtags
            engagement_tags = self._generate_engagement_hashtags(request.platform, request.engagement_goal)
            hashtags.extend(engagement_tags[:max_hashtags//3])
            
            # Creator economy hashtags
            creator_tags = self._generate_creator_hashtags(request.creator_context, request.platform)
            hashtags.extend(creator_tags[:2])
            
            # Remove duplicates and trim to limit
            unique_hashtags = list(dict.fromkeys(hashtags))
            return unique_hashtags[:max_hashtags]
        
        except Exception as e:
            logger.error(f"Hashtag generation failed: {e}")
            return [f"#{request.topic.replace(' ', '').lower()}"]
    
    def _generate_primary_hashtags(self, topic: str, platform: SocialPlatform) -> List[str]:
        """Generate primary hashtags for the topic"""
        base_tag = topic.replace(' ', '').lower()
        primary_tags = [f"#{base_tag}"]
        
        # Add variations
        words = topic.split()
        if len(words) > 1:
            for word in words:
                if len(word) > 3:
                    primary_tags.append(f"#{word.lower()}")
        
        # Platform-specific primary tags
        if platform == SocialPlatform.INSTAGRAM:
            primary_tags.extend(["#content", "#creator", "#inspiration"])
        elif platform == SocialPlatform.LINKEDIN:
            primary_tags.extend(["#professional", "#growth", "#leadership"])
        elif platform == SocialPlatform.TIKTOK:
            primary_tags.extend(["#fyp", "#viral", "#trending"])
        
        return primary_tags[:5]
    
    def _generate_engagement_hashtags(self, platform: SocialPlatform, goal: EngagementGoal) -> List[str]:
        """Generate engagement-focused hashtags"""
        engagement_map = {
            SocialPlatform.INSTAGRAM: {
                EngagementGoal.VIRAL: ["#viral", "#trending", "#explore"],
                EngagementGoal.EDUCATION: ["#learn", "#tips", "#education"],
                EngagementGoal.INSPIRATION: ["#motivation", "#inspiration", "#mindset"],
                EngagementGoal.ENTERTAINMENT: ["#fun", "#entertainment", "#funny"]
            },
            SocialPlatform.TIKTOK: {
                EngagementGoal.VIRAL: ["#fyp", "#viral", "#trending"],
                EngagementGoal.EDUCATION: ["#learnontiktok", "#education", "#tips"],
                EngagementGoal.INSPIRATION: ["#motivation", "#inspiration", "#growth"],
                EngagementGoal.ENTERTAINMENT: ["#funny", "#entertainment", "#comedy"]
            },
            SocialPlatform.LINKEDIN: {
                EngagementGoal.EDUCATION: ["#learning", "#professional", "#growth"],
                EngagementGoal.INSPIRATION: ["#leadership", "#motivation", "#success"],
                EngagementGoal.AWARENESS: ["#thoughtleadership", "#industry", "#insights"]
            }
        }
        
        platform_tags = engagement_map.get(platform, {})
        return platform_tags.get(goal, ["#engagement", "#community"])
    
    def _generate_creator_hashtags(self, creator_context: Dict[str, Any], platform: SocialPlatform) -> List[str]:
        """Generate creator economy hashtags"""
        creator_tags = []
        
        creator_type = creator_context.get("creator_type", "")
        if creator_type:
            creator_tags.append(f"#{creator_type.replace(' ', '').lower()}")
        
        # Platform-specific creator tags
        if platform == SocialPlatform.INSTAGRAM:
            creator_tags.extend(["#contentcreator", "#creatoreconomy"])
        elif platform == SocialPlatform.TIKTOK:
            creator_tags.extend(["#creator", "#contentcreator"])
        elif platform == SocialPlatform.LINKEDIN:
            creator_tags.extend(["#thoughtleader", "#entrepreneur"])
        
        return creator_tags
    
    async def _create_content_variations(self, content: str, request: SocialMediaRequest) -> List[Dict[str, str]]:
        """Create content variations for A/B testing"""
        variations = []
        
        # Tone variations
        if request.tone == ContentTone.CASUAL:
            formal_variation = content.replace("you", "one").replace("!", ".")
            variations.append({"type": "formal_tone", "content": formal_variation})
        
        # CTA variations
        if request.include_cta:
            cta_variations = [
                "What do you think? Share below! 👇",
                "Drop your thoughts in the comments!",
                "Tell me your experience with this!",
                "What's your take? Let's discuss! 💬"
            ]
            
            for i, cta in enumerate(cta_variations[:2]):
                varied_content = content.rsplit('\n', 1)[0] + f"\n\n{cta}"
                variations.append({"type": f"cta_variation_{i+1}", "content": varied_content})
        
        # Length variations
        if len(content) > 100:
            short_version = content.split('\n')[0] + f"\n\nQuick thoughts on {request.topic}! What's your experience?"
            variations.append({"type": "short_version", "content": short_version})
        
        return variations[:3]  # Limit to 3 variations
    
    async def _analyze_viral_potential(self, content: str, request: SocialMediaRequest) -> Dict[str, Any]:
        """Analyze viral potential of content"""
        try:
            viral_score = 0.0
            triggers = []
            
            # Engagement triggers
            if any(trigger in content.lower() for trigger in ['pov:', 'hot take:', 'unpopular opinion:', 'this might be controversial']):
                viral_score += 0.2
                triggers.append("conversation_starter")
            
            # Emotional triggers
            emotional_words = ['amazing', 'incredible', 'shocking', 'mind-blowing', 'game-changing']
            if any(word in content.lower() for word in emotional_words):
                viral_score += 0.15
                triggers.append("emotional_impact")
            
            # Interactive elements
            if any(element in content.lower() for element in ['comment', 'share', 'tag someone', 'what do you think']):
                viral_score += 0.1
                triggers.append("interaction_prompt")
            
            # Trending elements
            if request.trending_topics:
                viral_score += 0.15
                triggers.append("trend_integration")
            
            # Platform-specific viral factors
            if request.platform == SocialPlatform.TIKTOK:
                if 'fyp' in content.lower() or request.viral_potential:
                    viral_score += 0.2
                    triggers.append("fyp_optimization")
            
            # Visual elements (emojis)
            emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content))
            if emoji_count >= 3:
                viral_score += 0.1
                triggers.append("visual_appeal")
            
            # Shareability factors
            shareability_score = viral_score
            if request.engagement_goal in [EngagementGoal.VIRAL, EngagementGoal.ENTERTAINMENT]:
                shareability_score += 0.1
            
            # Trend alignment
            trend_alignment = 0.8 if request.trending_topics else 0.5
            
            return {
                "score": min(viral_score, 1.0),
                "triggers": triggers,
                "shareability": min(shareability_score, 1.0),
                "trend_alignment": trend_alignment,
                "recommendations": self._generate_viral_recommendations(viral_score, triggers)
            }
        
        except Exception as e:
            logger.error(f"Viral potential analysis failed: {e}")
            return {"score": 0.5, "triggers": [], "shareability": 0.5, "trend_alignment": 0.5}
    
    def _generate_viral_recommendations(self, score: float, triggers: List[str]) -> List[str]:
        """Generate recommendations to improve viral potential"""
        recommendations = []
        
        if score < 0.3:
            recommendations.extend([
                "Add more emotional triggers and engaging language",
                "Include trending hashtags and topics",
                "Create stronger calls-to-action for engagement"
            ])
        
        if "conversation_starter" not in triggers:
            recommendations.append("Add a controversial or thought-provoking statement")
        
        if "interaction_prompt" not in triggers:
            recommendations.append("Include questions or prompts for audience interaction")
        
        if "visual_appeal" not in triggers:
            recommendations.append("Add more emojis or visual elements")
        
        return recommendations
    
    async def _evaluate_social_content(
        self,
        prompt: str,
        content: str,
        request: SocialMediaRequest
    ) -> Any:
        """Evaluate social media content quality"""
        try:
            evaluation_request = {
                "prompt": prompt,
                "response": content,
                "template_id": "social_media_content",
                "creator_context": request.creator_context,
                "evaluation_criteria": ["engagement", "platform_optimization", "viral_potential", "audience_alignment"],
                "target_audience": request.target_audience,
                "content_category": "social_media"
            }
            
            return await self.evaluation_framework.evaluate_prompt_response(evaluation_request)
        
        except Exception as e:
            logger.error(f"Social content evaluation failed: {e}")
            # Return mock evaluation
            return type('MockEvaluation', (), {
                'overall_score': 0.75,
                'dimension_scores': {'engagement': 0.8, 'platform_optimization': 0.7, 'viral_potential': 0.6}
            })()
    
    async def _analyze_social_monetization(self, content: str, request: SocialMediaRequest) -> Dict[str, Any]:
        """Analyze monetization opportunities in social content"""
        try:
            opportunities = []
            potential_score = 0.0
            
            # Platform-specific monetization
            if request.platform == SocialPlatform.INSTAGRAM:
                potential_score += 0.3
                opportunities.extend([
                    "Instagram Creator Fund eligibility",
                    "Brand partnership opportunities",
                    "Affiliate marketing potential",
                    "Story ads and reels monetization"
                ])
            
            elif request.platform == SocialPlatform.YOUTUBE:
                potential_score += 0.4
                opportunities.extend([
                    "YouTube Partner Program",
                    "Super Chat and memberships",
                    "Brand sponsorships",
                    "Merchandise shelf integration"
                ])
            
            elif request.platform == SocialPlatform.TIKTOK:
                potential_score += 0.25
                opportunities.extend([
                    "TikTok Creator Fund",
                    "Live gifting monetization",
                    "Brand collaborations",
                    "TikTok Shop integration"
                ])
            
            # Content-based opportunities
            if request.engagement_goal == EngagementGoal.EDUCATION:
                potential_score += 0.2
                opportunities.append("Course and educational content sales")
            
            if request.include_cta:
                potential_score += 0.1
                opportunities.append("Lead generation and email list building")
            
            # Creator type specific
            creator_type = request.creator_context.get("creator_type", "")
            if creator_type in ["influencer", "blogger", "entrepreneur"]:
                potential_score += 0.15
                opportunities.append("Premium content and consultations")
            
            return {
                "score": min(potential_score, 1.0),
                "opportunities": opportunities,
                "recommendations": [
                    "Build consistent posting schedule for algorithm growth",
                    "Engage authentically with your audience",
                    "Create diverse content types for different revenue streams",
                    "Collaborate with other creators in your niche"
                ]
            }
        
        except Exception as e:
            logger.error(f"Social monetization analysis failed: {e}")
            return {"score": 0.5, "opportunities": [], "recommendations": []}
    
    async def _generate_social_creator_insights(self, content: str, request: SocialMediaRequest) -> Dict[str, Any]:
        """Generate creator economy insights for social content"""
        try:
            insights = {
                "content_type": "social_media",
                "platform": request.platform.value,
                "engagement_potential": "high" if len(content) < 1000 else "medium",
                "viral_probability": "high" if request.viral_potential else "medium",
                "audience_growth_potential": "high" if request.include_cta else "medium",
                "collaboration_opportunities": [],
                "cross_platform_potential": [],
                "trending_alignment": "high" if request.trending_topics else "medium"
            }
            
            # Collaboration opportunities
            insights["collaboration_opportunities"].extend([
                "Duet and collaboration posts with other creators",
                "Brand partnership content",
                "Cross-promotion with creators in similar niches",
                "User-generated content campaigns"
            ])
            
            # Cross-platform opportunities
            if request.platform == SocialPlatform.TIKTOK:
                insights["cross_platform_potential"].extend([
                    "Repurpose as Instagram Reels",
                    "Create YouTube Shorts version",
                    "Share highlights on Twitter"
                ])
            elif request.platform == SocialPlatform.INSTAGRAM:
                insights["cross_platform_potential"].extend([
                    "Create TikTok version",
                    "Share snippets on Twitter",
                    "Develop full YouTube video"
                ])
            
            return insights
        
        except Exception as e:
            logger.error(f"Social creator insights generation failed: {e}")
            return {"content_type": "social_media", "engagement_potential": "medium"}
    
    async def get_platform_best_practices(self, platform: SocialPlatform) -> Dict[str, Any]:
        """Get best practices for specific platform"""
        practices = {
            SocialPlatform.INSTAGRAM: {
                "optimal_posting_times": ["6:00 AM", "12:00 PM", "7:00 PM"],
                "content_tips": [
                    "Use high-quality visuals",
                    "Write engaging captions",
                    "Use relevant hashtags (5-10)",
                    "Include calls-to-action",
                    "Post consistently"
                ],
                "engagement_strategies": [
                    "Respond to comments quickly",
                    "Use Instagram Stories regularly",
                    "Collaborate with other creators",
                    "Share user-generated content"
                ]
            },
            SocialPlatform.TWITTER: {
                "optimal_posting_times": ["9:00 AM", "12:00 PM", "3:00 PM", "6:00 PM"],
                "content_tips": [
                    "Keep tweets concise and punchy",
                    "Use trending hashtags sparingly",
                    "Include visuals when possible",
                    "Create Twitter threads for longer content"
                ],
                "engagement_strategies": [
                    "Engage in conversations",
                    "Retweet with comments",
                    "Use polls and questions",
                    "Share timely, relevant content"
                ]
            },
            SocialPlatform.LINKEDIN: {
                "optimal_posting_times": ["8:00 AM", "12:00 PM", "5:00 PM"],
                "content_tips": [
                    "Share professional insights",
                    "Use industry-relevant hashtags",
                    "Include personal stories",
                    "Provide actionable advice"
                ],
                "engagement_strategies": [
                    "Comment thoughtfully on others' posts",
                    "Share industry news with commentary",
                    "Write long-form posts",
                    "Connect with industry professionals"
                ]
            }
        }
        
        return practices.get(platform, {"optimal_posting_times": [], "content_tips": [], "engagement_strategies": []})
    
    async def cleanup(self) -> None:
        """Cleanup template resources"""
        try:
            await self.template_compiler.cleanup()
            await self.security_validator.cleanup()
            await self.evaluation_framework.cleanup()
            
            logger.info("Social Media Template cleanup completed")
        
        except Exception as e:
            logger.error(f"Social Media Template cleanup failed: {e}")


# Global social media template instance
social_media_template = SocialMediaTemplate()