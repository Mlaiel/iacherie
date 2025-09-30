"""
Video Script Template for AI-Powered Content Generation

Enterprise-grade video script prompt engineering template optimized for the Creator Economy.
Provides advanced prompt structures for generating high-quality video scripts across
multiple formats, platforms, and styles with built-in optimization for engagement and monetization.

Author: AI Expert Team Lead by Fahed Mlaiel
Contact: contact@fahedmlaiel.fr | https://fahedmlaiel.fr
Copyright (c) 2024 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact for licensing terms
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoFormat(Enum):
    """Supported video formats"""
    YOUTUBE_LONG = "youtube_long"        # 10+ minutes
    YOUTUBE_SHORT = "youtube_short"      # <60 seconds
    TIKTOK = "tiktok"                   # 15-60 seconds
    INSTAGRAM_REEL = "instagram_reel"    # 15-90 seconds
    INSTAGRAM_STORY = "instagram_story"  # 15 seconds each
    FACEBOOK_VIDEO = "facebook_video"    # 1-240 minutes
    LINKEDIN_VIDEO = "linkedin_video"    # 30 seconds-10 minutes
    TWITTER_VIDEO = "twitter_video"      # <140 seconds
    EDUCATIONAL = "educational"          # Variable length
    ADVERTISEMENT = "advertisement"      # 15-30 seconds
    DOCUMENTARY = "documentary"          # 20+ minutes
    EXPLAINER = "explainer"             # 1-5 minutes
    TUTORIAL = "tutorial"               # 5-30 minutes
    WEBINAR = "webinar"                 # 30-60 minutes
    PODCAST_VIDEO = "podcast_video"      # 30+ minutes

class VideoStyle(Enum):
    """Video style options"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    PROMOTIONAL = "promotional"
    STORYTELLING = "storytelling"
    DOCUMENTARY = "documentary"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    VLOG = "vlog"
    INTERVIEW = "interview"
    PRESENTATION = "presentation"
    COMEDY = "comedy"
    DRAMATIC = "dramatic"

class VideoTone(Enum):
    """Video tone options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    EDUCATIONAL = "educational"
    HUMOROUS = "humorous"
    SERIOUS = "serious"
    INSPIRATIONAL = "inspirational"
    CONVERSATIONAL = "conversational"
    AUTHORITATIVE = "authoritative"
    FRIENDLY = "friendly"

@dataclass
class VideoScriptPrompt:
    """Video script prompt configuration"""
    format: VideoFormat
    style: VideoStyle
    tone: VideoTone
    topic: str
    duration_minutes: float
    target_audience: str
    platform: str = ""
    main_message: str = ""
    call_to_action: str = ""
    visual_elements: List[str] = field(default_factory=list)
    audio_cues: List[str] = field(default_factory=list)
    presenter_info: str = ""
    brand_guidelines: str = ""
    monetization_strategy: str = ""
    seo_keywords: List[str] = field(default_factory=list)
    engagement_hooks: List[str] = field(default_factory=list)
    thumbnail_concept: str = ""
    series_context: str = ""

class VideoScriptTemplate:
    """
    Advanced video script template for AI content generation
    
    Optimized for Creator Economy with platform-specific formatting, engagement optimization,
    and monetization strategies. Supports all major video platforms and formats.
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.creator_economy_features = True
        self.platform_optimization = True
        self.engagement_optimization = True
        
        # Platform-specific requirements
        self.platform_specs = {
            "youtube": {
                "max_title_length": 100,
                "optimal_description": 250,
                "engagement_features": ["subscribe", "like", "comment", "bell"],
                "monetization": ["ads", "memberships", "super_chat", "merch"]
            },
            "tiktok": {
                "max_title_length": 150,
                "optimal_description": 150,
                "engagement_features": ["like", "comment", "share", "follow"],
                "monetization": ["creator_fund", "live_gifts", "brand_partnerships"]
            },
            "instagram": {
                "max_title_length": 125,
                "optimal_description": 125,
                "engagement_features": ["like", "comment", "share", "save"],
                "monetization": ["sponsored_posts", "reels_play_bonus", "badges"]
            },
            "linkedin": {
                "max_title_length": 150,
                "optimal_description": 300,
                "engagement_features": ["like", "comment", "share", "connect"],
                "monetization": ["sponsored_content", "lead_generation"]
            }
        }
        
        # Format-specific structures
        self.format_structures = {
            VideoFormat.YOUTUBE_LONG: self._get_youtube_long_structure(),
            VideoFormat.YOUTUBE_SHORT: self._get_youtube_short_structure(),
            VideoFormat.TIKTOK: self._get_tiktok_structure(),
            VideoFormat.INSTAGRAM_REEL: self._get_instagram_reel_structure(),
            VideoFormat.EDUCATIONAL: self._get_educational_structure(),
            VideoFormat.TUTORIAL: self._get_tutorial_structure(),
            VideoFormat.ADVERTISEMENT: self._get_advertisement_structure(),
            VideoFormat.EXPLAINER: self._get_explainer_structure(),
        }
        
    def generate_prompt(self, config: VideoScriptPrompt) -> Dict[str, Any]:
        """
        Generate optimized video script prompt
        
        Args:
            config: Video script configuration
            
        Returns:
            Dictionary containing optimized prompt and metadata
        """
        try:
            # Get format-specific structure
            structure = self.format_structures.get(config.format, self._get_default_structure())
            
            # Build comprehensive prompt
            prompt_components = {
                "system_prompt": self._build_system_prompt(config),
                "user_prompt": self._build_user_prompt(config, structure),
                "format_instructions": self._build_format_instructions(config),
                "engagement_optimization": self._build_engagement_optimization(config),
                "platform_optimization": self._build_platform_optimization(config),
                "monetization_guidance": self._build_monetization_guidance(config),
                "visual_audio_direction": self._build_visual_audio_direction(config),
                "seo_optimization": self._build_seo_optimization(config)
            }
            
            # Combine into final prompt
            final_prompt = self._combine_prompt_components(prompt_components)
            
            # Generate metadata
            metadata = self._generate_metadata(config)
            
            logger.info(f"Generated video script prompt for {config.format.value} format")
            
            return {
                "prompt": final_prompt,
                "metadata": metadata,
                "config": config,
                "optimization_score": self._calculate_optimization_score(config),
                "engagement_potential": self._estimate_engagement_potential(config),
                "monetization_potential": self._estimate_monetization_potential(config),
                "platform_compliance": self._check_platform_compliance(config)
            }
            
        except Exception as e:
            logger.error(f"Error generating video script prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, config: VideoScriptPrompt) -> str:
        """Build system prompt for video script generation"""
        return f"""You are an expert video script writer specializing in {config.format.value} content for the Creator Economy.

Your expertise includes:
- Master-level video scriptwriting with platform optimization
- Creator Economy monetization and audience growth strategies
- {config.platform.title() if config.platform else 'Multi-platform'} algorithm optimization and best practices
- Engagement psychology and viewer retention techniques
- Visual storytelling and audio-visual direction
- Brand building and thought leadership content

Create a {config.style.value} style script with a {config.tone.value} tone for {config.target_audience} audience.
Duration target: {config.duration_minutes} minutes ({config.duration_minutes * 60:.0f} seconds).

Focus on:
- Maximum viewer retention and engagement
- Platform algorithm optimization for discovery
- Clear call-to-action integration
- Monetization opportunity maximization
- Brand building and authority establishment
- Viral potential and shareability factors"""

    def _build_user_prompt(self, config: VideoScriptPrompt, structure: Dict) -> str:
        """Build user prompt with specific requirements"""
        visual_info = f"\nVisual Elements: {', '.join(config.visual_elements)}" if config.visual_elements else ""
        audio_info = f"\nAudio Cues: {', '.join(config.audio_cues)}" if config.audio_cues else ""
        presenter_info = f"\nPresenter: {config.presenter_info}" if config.presenter_info else ""
        brand_info = f"\nBrand Guidelines: {config.brand_guidelines}" if config.brand_guidelines else ""
        series_info = f"\nSeries Context: {config.series_context}" if config.series_context else ""
        
        return f"""{structure['intro']}

Topic: {config.topic}
Main Message: {config.main_message or 'To be determined from topic'}
Duration: {config.duration_minutes} minutes
Platform: {config.platform.title() if config.platform else 'Multi-platform'}
Target Audience: {config.target_audience}{presenter_info}{visual_info}{audio_info}{brand_info}{series_info}

Script Structure Requirements:
{structure['structure']}

Content Requirements:
{structure['requirements']}

Creator Economy Optimization:
- Design for maximum algorithmic reach and discovery
- Include strategic engagement triggers throughout
- Create shareable moments and quotable content
- Build presenter authority and expertise demonstration
- Include natural monetization touchpoints
- Optimize for cross-platform content repurposing"""

    def _build_format_instructions(self, config: VideoScriptPrompt) -> str:
        """Build format-specific instructions"""
        duration_seconds = config.duration_minutes * 60
        
        format_guidance = {
            VideoFormat.YOUTUBE_LONG: f"Long-form YouTube optimization for {duration_seconds:.0f} seconds",
            VideoFormat.YOUTUBE_SHORT: f"YouTube Shorts vertical format, {duration_seconds:.0f} seconds max",
            VideoFormat.TIKTOK: f"TikTok vertical format, {duration_seconds:.0f} seconds, trend-aware",
            VideoFormat.INSTAGRAM_REEL: f"Instagram Reels vertical format, {duration_seconds:.0f} seconds",
            VideoFormat.EDUCATIONAL: f"Educational format with clear learning objectives, {duration_seconds:.0f} seconds",
            VideoFormat.TUTORIAL: f"Step-by-step tutorial format, {duration_seconds:.0f} seconds",
            VideoFormat.ADVERTISEMENT: f"Commercial advertisement format, {duration_seconds:.0f} seconds",
            VideoFormat.EXPLAINER: f"Explainer video format with clear explanations, {duration_seconds:.0f} seconds"
        }
        
        return f"""
FORMAT INSTRUCTIONS:

{format_guidance.get(config.format, f'Standard video format, {duration_seconds:.0f} seconds')}

Script Formatting:
- Use clear scene descriptions and visual directions
- Include specific timing markers for key moments
- Specify on-screen text and graphics requirements
- Include audio cues and music suggestions
- Mark engagement trigger points clearly
- Indicate call-to-action placement and timing

Technical Specifications:
- Format for {config.format.value} platform requirements
- Optimize pacing for {config.tone.value} tone
- Structure for {config.style.value} style presentation
- Include thumbnail moment identification
- Mark potential clip/snippet extraction points"""

    def _build_engagement_optimization(self, config: VideoScriptPrompt) -> str:
        """Build engagement optimization instructions"""
        hooks = f"Include these engagement hooks: {', '.join(config.engagement_hooks)}" if config.engagement_hooks else ""
        
        return f"""
ENGAGEMENT OPTIMIZATION:

Viewer Retention Strategy:
- Hook viewers within first 3-5 seconds
- Include pattern interrupts every 10-15 seconds for short form
- Use visual variety and dynamic pacing
- Create anticipation and curiosity gaps
- Include surprise elements and unexpected moments

Platform Algorithm Optimization:
- Optimize for average view duration and completion rate
- Include engagement triggers (questions, polls, comments)
- Create shareable moments and quotable content
- Use trending topics and relevant hashtags
- Design for replay value and multiple viewings

Psychological Triggers:
- Use curiosity gaps and open loops strategically
- Include social proof and authority indicators
- Create emotional connection with audience
- Use storytelling techniques for retention
- Include interactive elements where possible{f' - {hooks}' if hooks else ''}

Call-to-Action Strategy:
{config.call_to_action or '- Include organic CTAs that feel natural to content flow'}
- Time CTAs strategically for maximum response
- Use multiple CTA types throughout video
- Create urgency and scarcity where appropriate"""

    def _build_platform_optimization(self, config: VideoScriptPrompt) -> str:
        """Build platform-specific optimization"""
        if not config.platform:
            return "PLATFORM OPTIMIZATION: General multi-platform optimization"
            
        platform = config.platform.lower()
        specs = self.platform_specs.get(platform, {})
        
        return f"""
PLATFORM OPTIMIZATION for {platform.upper()}:

Platform-Specific Features:
- Engagement features: {', '.join(specs.get('engagement_features', []))}
- Monetization options: {', '.join(specs.get('monetization', []))}
- Title optimization: Max {specs.get('max_title_length', 100)} characters
- Description optimization: ~{specs.get('optimal_description', 250)} characters

Algorithm Optimization:
- Create content that encourages platform-specific engagement
- Use platform-native features and trending elements
- Optimize for discovery through platform search
- Include platform-specific keywords and hashtags
- Design for platform user behavior patterns

Content Guidelines:
- Follow platform community standards
- Optimize for platform's primary consumption method
- Include platform-specific visual and audio requirements
- Use platform-appropriate tone and style
- Leverage platform-specific monetization features"""

    def _build_monetization_guidance(self, config: VideoScriptPrompt) -> str:
        """Build monetization guidance"""
        strategy = config.monetization_strategy or "General creator monetization"
        
        return f"""
MONETIZATION GUIDANCE:

Strategy: {strategy}

Direct Monetization:
- Include natural product/service mentions where appropriate
- Create content suitable for sponsorship integration
- Design for premium content or membership tiers
- Include affiliate marketing opportunities naturally
- Build toward subscription or follow-up content

Indirect Monetization:
- Establish expertise and thought leadership
- Build personal brand recognition and authority
- Create content that demonstrates skills and knowledge
- Include portfolio/work showcase opportunities
- Design for lead generation and client attraction

Platform Monetization:
- Optimize for platform revenue sharing programs
- Include features that trigger platform monetization
- Create content eligible for platform creator funds
- Design for live streaming and real-time monetization
- Build audience for cross-platform monetization

Long-term Value:
- Create evergreen content with lasting value
- Build content that can be repurposed across platforms
- Establish series or recurring content opportunities
- Create content that builds audience loyalty and retention"""

    def _build_visual_audio_direction(self, config: VideoScriptPrompt) -> str:
        """Build visual and audio direction"""
        visual_elements = f"Specified visual elements: {', '.join(config.visual_elements)}" if config.visual_elements else "Standard visual elements"
        audio_cues = f"Specified audio cues: {', '.join(config.audio_cues)}" if config.audio_cues else "Standard audio design"
        thumbnail = f"Thumbnail concept: {config.thumbnail_concept}" if config.thumbnail_concept else "Create compelling thumbnail moment"
        
        return f"""
VISUAL & AUDIO DIRECTION:

Visual Direction:
{visual_elements}
- Include specific camera angles and shot types
- Specify on-screen graphics and text overlays
- Include visual transitions and effects suggestions
- Mark key visual moments for engagement
- Design for mobile-first viewing experience

Audio Direction:
{audio_cues}
- Include background music style and mood
- Specify sound effects and audio cues
- Include voice-over direction and pacing
- Mark audio emphasis points for engagement
- Consider accessibility with captions and audio descriptions

Production Notes:
{thumbnail}
- Include lighting and setup requirements
- Specify any props or visual aids needed
- Include wardrobe or branding considerations
- Mark potential B-roll and supplementary footage needs
- Consider post-production editing requirements"""

    def _build_seo_optimization(self, config: VideoScriptPrompt) -> str:
        """Build SEO optimization instructions"""
        if not config.seo_keywords:
            return "SEO OPTIMIZATION: Focus on natural keyword integration and searchable content themes."
            
        return f"""
SEO OPTIMIZATION:

Target Keywords: {', '.join(config.seo_keywords)}

Keyword Integration:
- Include primary keywords in opening hook
- Use keywords naturally in script dialogue
- Include keywords in visual text overlays
- Use semantic variations throughout content
- Include keywords in call-to-action segments

Discoverability:
- Address common search queries related to topic
- Include trending topics and cultural references
- Use searchable questions and problem-solving content
- Create content around popular search terms
- Include evergreen keywords for long-term discovery

Metadata Optimization:
- Optimize title for search and click-through
- Create compelling description with keywords
- Include relevant hashtags and tags
- Use category-appropriate keywords
- Consider international and local search terms"""

    def _combine_prompt_components(self, components: Dict[str, str]) -> str:
        """Combine all prompt components into final prompt"""
        return f"""{components['system_prompt']}

{components['user_prompt']}

{components['format_instructions']}

{components['engagement_optimization']}

{components['platform_optimization']}

{components['monetization_guidance']}

{components['visual_audio_direction']}

{components['seo_optimization']}

Now create the complete video script following all these guidelines. Include scene descriptions, timing markers, visual directions, audio cues, and engagement optimization throughout."""

    def _generate_metadata(self, config: VideoScriptPrompt) -> Dict[str, Any]:
        """Generate metadata for the prompt"""
        return {
            "template_version": self.template_version,
            "format": config.format.value,
            "style": config.style.value,
            "tone": config.tone.value,
            "duration_minutes": config.duration_minutes,
            "duration_seconds": config.duration_minutes * 60,
            "target_audience": config.target_audience,
            "platform": config.platform,
            "estimated_words": self._estimate_word_count(config.duration_minutes),
            "estimated_scenes": self._estimate_scene_count(config.duration_minutes, config.format),
            "seo_keyword_count": len(config.seo_keywords),
            "engagement_hooks_count": len(config.engagement_hooks),
            "monetization_enabled": bool(config.monetization_strategy or config.call_to_action),
            "creation_timestamp": datetime.now().isoformat(),
            "creator_economy_optimized": True
        }

    def _calculate_optimization_score(self, config: VideoScriptPrompt) -> float:
        """Calculate optimization score based on configuration"""
        score = 0.5  # Base score
        
        # Add points for configuration completeness
        if config.seo_keywords:
            score += 0.1
        if config.engagement_hooks:
            score += 0.1
        if config.monetization_strategy:
            score += 0.1
        if config.call_to_action:
            score += 0.1
        if config.platform:
            score += 0.1
        if config.visual_elements:
            score += 0.05
        if config.thumbnail_concept:
            score += 0.05
        
        return min(score, 1.0)

    def _estimate_engagement_potential(self, config: VideoScriptPrompt) -> str:
        """Estimate engagement potential"""
        score = self._calculate_optimization_score(config)
        
        if score >= 0.8:
            return "High"
        elif score >= 0.6:
            return "Medium-High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low-Medium"

    def _estimate_monetization_potential(self, config: VideoScriptPrompt) -> str:
        """Estimate monetization potential"""
        if config.monetization_strategy and config.call_to_action and config.platform:
            return "High"
        elif (config.monetization_strategy or config.call_to_action) and config.platform:
            return "Medium-High"
        elif config.monetization_strategy or config.call_to_action or config.platform:
            return "Medium"
        else:
            return "Low"

    def _check_platform_compliance(self, config: VideoScriptPrompt) -> Dict[str, bool]:
        """Check platform compliance"""
        if not config.platform:
            return {"compliant": True, "notes": "No specific platform requirements"}
            
        platform = config.platform.lower()
        specs = self.platform_specs.get(platform, {})
        
        duration_ok = True
        if platform == "tiktok" and config.duration_minutes > 1:
            duration_ok = False
        elif platform == "instagram" and config.format == VideoFormat.INSTAGRAM_REEL and config.duration_minutes > 1.5:
            duration_ok = False
            
        return {
            "compliant": duration_ok,
            "duration_check": duration_ok,
            "platform_supported": platform in self.platform_specs,
            "notes": f"Platform: {platform}, Duration: {config.duration_minutes}m"
        }

    def _estimate_word_count(self, duration_minutes: float) -> int:
        """Estimate word count for script based on duration"""
        # Average speaking rate: 150-160 words per minute
        return int(duration_minutes * 155)

    def _estimate_scene_count(self, duration_minutes: float, format: VideoFormat) -> int:
        """Estimate scene count based on duration and format"""
        if format in [VideoFormat.TIKTOK, VideoFormat.YOUTUBE_SHORT, VideoFormat.INSTAGRAM_REEL]:
            return max(1, int(duration_minutes * 3))  # Faster pacing for short form
        else:
            return max(1, int(duration_minutes * 1.5))  # Slower pacing for long form

    # Format-specific structures
    def _get_youtube_long_structure(self) -> Dict:
        return {
            "intro": "Create a comprehensive YouTube long-form video script optimized for Creator Economy success.",
            "structure": [
                "- Hook (0-15 seconds): Compelling opening that promises value",
                "- Introduction (15-45 seconds): Channel branding and video preview", 
                "- Main Content (varies): Core content with engagement optimization",
                "- Mid-video CTAs (throughout): Subscribe prompts and engagement",
                "- Conclusion (final 30-60 seconds): Summary and strong CTA",
                "- End screen (final 20 seconds): Channel promotion and next video"
            ],
            "requirements": [
                "- Optimize for watch time and audience retention",
                "- Include chapter markers for long content",
                "- Use pattern interrupts to maintain engagement",
                "- Include multiple CTAs throughout video",
                "- End with compelling next video suggestion"
            ]
        }

    def _get_youtube_short_structure(self) -> Dict:
        return {
            "intro": "Create a viral YouTube Shorts script optimized for maximum engagement and algorithmic reach.",
            "structure": [
                "- Hook (0-3 seconds): Immediate attention grabber",
                "- Content delivery (3-45 seconds): Core message with high energy",
                "- Payoff/Conclusion (45-60 seconds): Satisfying resolution and CTA"
            ],
            "requirements": [
                "- Vertical format optimization (9:16 aspect ratio)",
                "- High energy and fast pacing throughout",
                "- Strong visual hook in first frame",
                "- Include trending audio or music cues",
                "- End with engagement prompt (like, follow, comment)"
            ]
        }

    def _get_tiktok_structure(self) -> Dict:
        return {
            "intro": "Create a TikTok video script optimized for viral potential and Creator Economy growth.",
            "structure": [
                "- Hook (0-3 seconds): Scroll-stopping opening",
                "- Build-up (3-30 seconds): Content development with entertainment value",
                "- Climax (30-45 seconds): Peak moment or revelation", 
                "- Resolution (45-60 seconds): Conclusion with strong CTA"
            ],
            "requirements": [
                "- Incorporate trending sounds and challenges where appropriate",
                "- Use TikTok-native features (effects, filters, text overlays)",
                "- Create content designed for repeat viewing",
                "- Include hashtag strategy for discoverability",
                "- Design for mobile-first, sound-on viewing"
            ]
        }

    def _get_instagram_reel_structure(self) -> Dict:
        return {
            "intro": "Create an Instagram Reel script optimized for discovery and engagement.",
            "structure": [
                "- Hook (0-3 seconds): Visual attention grabber",
                "- Content (3-60 seconds): Educational or entertaining core content",
                "- CTA (final 5-10 seconds): Clear call-to-action"
            ],
            "requirements": [
                "- Use Instagram-native features and effects",
                "- Include text overlays for accessibility",
                "- Create visually appealing content for feed display",
                "- Use relevant hashtags and location tags",
                "- Design for both sound-on and sound-off viewing"
            ]
        }

    def _get_educational_structure(self) -> Dict:
        return {
            "intro": "Create an educational video script that teaches while engaging and building authority.",
            "structure": [
                "- Learning objective introduction (0-30 seconds)",
                "- Main teaching content with clear structure",
                "- Examples and practical applications",
                "- Summary and key takeaways",
                "- Next steps and additional resources"
            ],
            "requirements": [
                "- Clear learning objectives and outcomes",
                "- Structured content with logical progression",
                "- Include examples and real-world applications",
                "- Use visual aids and demonstrations",
                "- Provide actionable takeaways for viewers"
            ]
        }

    def _get_tutorial_structure(self) -> Dict:
        return {
            "intro": "Create a step-by-step tutorial script that guides viewers through a process.",
            "structure": [
                "- Problem/goal introduction",
                "- Tools and requirements overview",
                "- Step-by-step instructions with clear numbering",
                "- Common mistakes and troubleshooting",
                "- Final result showcase and next steps"
            ],
            "requirements": [
                "- Clear, numbered steps that are easy to follow",
                "- Include all necessary tools and materials",
                "- Show actual demonstration of each step",
                "- Address common questions and problems",
                "- Provide downloadable resources where applicable"
            ]
        }

    def _get_advertisement_structure(self) -> Dict:
        return {
            "intro": "Create a compelling advertisement script that drives action while feeling authentic.",
            "structure": [
                "- Attention-grabbing hook (0-5 seconds)",
                "- Problem identification and relatability (5-15 seconds)",
                "- Solution presentation with benefits (15-25 seconds)",
                "- Strong call-to-action with urgency (25-30 seconds)"
            ],
            "requirements": [
                "- Focus on benefits over features",
                "- Include social proof and credibility indicators",
                "- Create urgency without being pushy",
                "- Use authentic, conversational tone",
                "- Include clear, specific call-to-action"
            ]
        }

    def _get_explainer_structure(self) -> Dict:
        return {
            "intro": "Create an explainer video script that simplifies complex topics.",
            "structure": [
                "- Topic introduction and relevance",
                "- Problem or concept explanation",
                "- Solution or understanding breakdown",
                "- Real-world applications and examples",
                "- Summary and actionable insights"
            ],
            "requirements": [
                "- Break down complex concepts into simple terms",
                "- Use analogies and metaphors for clarity",
                "- Include visual representations of ideas",
                "- Provide real-world context and applications",
                "- End with clear understanding confirmation"
            ]
        }

    def _get_default_structure(self) -> Dict:
        return {
            "intro": "Create an engaging video script optimized for your specified format and audience.",
            "structure": [
                "- Compelling opening hook",
                "- Clear content structure and flow",
                "- Engaging main content with value delivery",
                "- Strong conclusion with call-to-action"
            ],
            "requirements": [
                "- Maintain viewer engagement throughout",
                "- Include clear value proposition",
                "- Use appropriate pacing for format",
                "- Include strategic calls-to-action",
                "- Optimize for target platform and audience"
            ]
        }

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = VideoScriptPrompt(
        format=VideoFormat.YOUTUBE_LONG,
        style=VideoStyle.EDUCATIONAL,
        tone=VideoTone.PROFESSIONAL,
        topic="How to Build a Successful Creator Economy Business",
        duration_minutes=12.0,
        target_audience="aspiring content creators and entrepreneurs",
        platform="youtube",
        main_message="Building a sustainable creator business requires strategy, consistency, and authentic audience connection",
        call_to_action="Subscribe for more creator economy insights and download our free Creator Business Toolkit",
        visual_elements=["screen recordings", "graphics", "talking head segments"],
        audio_cues=["upbeat intro music", "transition sounds", "background ambient"],
        presenter_info="Industry expert with 5+ years creator economy experience",
        monetization_strategy="Lead generation for coaching services and digital products",
        seo_keywords=["creator economy", "content creator business", "youtube monetization"],
        engagement_hooks=["surprising statistics", "personal success stories"],
        thumbnail_concept="Split screen showing 'before/after' creator success transformation",
        series_context="Part of 'Creator Business Mastery' educational series"
    )
    
    # Generate prompt
    template = VideoScriptTemplate()
    result = template.generate_prompt(config)
    
    print("=== VIDEO SCRIPT TEMPLATE EXAMPLE ===")
    print(f"Optimization Score: {result['optimization_score']:.2f}")
    print(f"Engagement Potential: {result['engagement_potential']}")
    print(f"Monetization Potential: {result['monetization_potential']}")
    print(f"Platform Compliance: {result['platform_compliance']}")
    print(f"Estimated Words: {result['metadata']['estimated_words']}")
    print(f"Estimated Scenes: {result['metadata']['estimated_scenes']}")
    print("\n" + "="*50)
    print(result['prompt'])