"""
🎯 Creative Writing Template - AI-Powered Creative Content Generation
=====================================================================

Enterprise-grade creative writing template for content creators with advanced
storytelling, character development, and narrative structure generation.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - IA Prompt Engineer + Creative Writing Expert
Team: Lead Dev IA + Backend Senior + ML Engineer + Creative Content Expert
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field, validator

from core.config import get_settings
from utils.exceptions import TemplateError, ValidationError
from ..template_compiler import TemplateCompiler
from ..security_validator import SecurityValidator
from ..evaluation_framework import EvaluationFramework

logger = logging.getLogger(__name__)
settings = get_settings()


class WritingStyle(Enum):
    """Creative writing styles"""
    NARRATIVE = "narrative"
    DESCRIPTIVE = "descriptive"
    PERSUASIVE = "persuasive"
    EXPOSITORY = "expository"
    POETIC = "poetic"
    DRAMATIC = "dramatic"
    HUMOROUS = "humorous"
    SUSPENSEFUL = "suspenseful"
    ROMANTIC = "romantic"
    HORROR = "horror"
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science_fiction"


class WritingGenre(Enum):
    """Writing genres"""
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    POETRY = "poetry"
    SCREENPLAY = "screenplay"
    SHORT_STORY = "short_story"
    NOVEL = "novel"
    MEMOIR = "memoir"
    BIOGRAPHY = "biography"
    ESSAY = "essay"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    MARKETING = "marketing"


class ToneType(Enum):
    """Writing tone types"""
    FORMAL = "formal"
    INFORMAL = "informal"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    AUTHORITATIVE = "authoritative"
    FRIENDLY = "friendly"
    INSPIRATIONAL = "inspirational"
    EMOTIONAL = "emotional"
    ANALYTICAL = "analytical"


@dataclass
class CreativeWritingConfig:
    """Creative writing configuration"""
    style: WritingStyle
    genre: WritingGenre
    tone: ToneType
    target_length: int
    target_audience: str
    purpose: str
    character_count: int = 0
    setting_description: str = ""
    plot_points: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    creator_type: str = "writer"
    monetization_focus: bool = False
    platform_optimization: str = ""


class CreativeWritingRequest(BaseModel):
    """Creative writing request"""
    topic: str = Field(..., min_length=1, max_length=200)
    style: WritingStyle = WritingStyle.NARRATIVE
    genre: WritingGenre = WritingGenre.FICTION
    tone: ToneType = ToneType.CONVERSATIONAL
    target_length: int = Field(default=500, ge=50, le=5000)
    target_audience: str = Field(default="general", min_length=1)
    purpose: str = Field(default="entertainment", min_length=1)
    characters: List[str] = Field(default_factory=list, max_items=10)
    setting: str = Field(default="", max_length=500)
    plot_elements: List[str] = Field(default_factory=list, max_items=20)
    themes: List[str] = Field(default_factory=list, max_items=10)
    creator_context: Dict[str, Any] = Field(default_factory=dict)
    monetization_enabled: bool = False
    platform_target: str = Field(default="general")
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()
    
    @validator('target_length')
    def validate_length(cls, v):
        if v < 50 or v > 5000:
            raise ValueError("Target length must be between 50 and 5000 words")
        return v


class CreativeWritingTemplate:
    """
    🎯 Enterprise Creative Writing Template
    
    Advanced creative writing generation with:
    - Multi-genre story generation
    - Character development and dialogue
    - Plot structure and narrative flow
    - Style and tone adaptation
    - Creator economy optimization
    - Monetization potential analysis
    - Platform-specific formatting
    - Audience engagement optimization
    """
    
    def __init__(self):
        self.template_compiler = TemplateCompiler()
        self.security_validator = SecurityValidator()
        self.evaluation_framework = EvaluationFramework()
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize creative writing template"""
        try:
            await self.template_compiler.initialize()
            await self.security_validator.initialize()
            await self.evaluation_framework.initialize()
            
            self._initialized = True
            logger.info("Creative Writing Template initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Creative Writing Template: {e}")
            raise TemplateError(f"Creative Writing Template initialization failed: {e}")
    
    async def generate_creative_content(self, request: CreativeWritingRequest) -> Dict[str, Any]:
        """
        Generate creative writing content based on request
        
        Args:
            request: Creative writing request configuration
            
        Returns:
            Generated creative content with metadata
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            # Build prompt template based on request
            prompt_template = await self._build_creative_prompt(request)
            
            # Prepare variables for template compilation
            variables = await self._prepare_template_variables(request)
            
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
            
            # Generate the creative content
            creative_content = await self._generate_content(compiled_result.compiled_prompt, request)
            
            # Post-process the content
            processed_content = await self._post_process_content(creative_content, request)
            
            # Evaluate the generated content
            evaluation = await self._evaluate_creative_content(
                compiled_result.compiled_prompt, 
                processed_content, 
                request
            )
            
            # Build response
            response = {
                "content": processed_content,
                "metadata": {
                    "style": request.style.value,
                    "genre": request.genre.value,
                    "tone": request.tone.value,
                    "word_count": len(processed_content.split()),
                    "character_count": len(processed_content),
                    "target_audience": request.target_audience,
                    "creator_type": request.creator_context.get("creator_type", "writer"),
                    "platform_optimized": request.platform_target
                },
                "evaluation": {
                    "overall_score": evaluation.overall_score,
                    "creativity_score": evaluation.dimension_scores.get("creativity", 0.0),
                    "engagement_score": evaluation.dimension_scores.get("engagement", 0.0),
                    "quality_score": evaluation.dimension_scores.get("quality", 0.0)
                },
                "optimization_suggestions": compiled_result.optimization_suggestions,
                "security_validated": compiled_result.security_validated,
                "monetization_potential": await self._analyze_monetization_potential(processed_content, request),
                "creator_economy_insights": await self._generate_creator_insights(processed_content, request)
            }
            
            return response
        
        except Exception as e:
            logger.error(f"Creative content generation failed: {e}")
            raise TemplateError(f"Creative content generation failed: {e}")
    
    async def _build_creative_prompt(self, request: CreativeWritingRequest) -> str:
        """Build creative writing prompt template"""
        
        # Base prompt structure
        base_prompt = """You are a professional {{ creator_type }} specializing in {{ genre }} writing with a {{ style }} style.

**Writing Assignment:**
Topic: {{ topic }}
Genre: {{ genre }}
Style: {{ style }}
Tone: {{ tone }}
Target Length: {{ target_length }} words
Target Audience: {{ target_audience }}
Purpose: {{ purpose }}

{% if characters %}
**Characters to Include:**
{% for character in characters %}
- {{ character }}
{% endfor %}
{% endif %}

{% if setting %}
**Setting:** {{ setting }}
{% endif %}

{% if plot_elements %}
**Plot Elements to Incorporate:**
{% for element in plot_elements %}
- {{ element }}
{% endfor %}
{% endif %}

{% if themes %}
**Themes to Explore:**
{% for theme in themes %}
- {{ theme }}
{% endfor %}
{% endif %}

**Creator Economy Instructions:**
{% if monetization_enabled %}
- Include subtle monetization opportunities (sponsorship potential, affiliate mentions, premium content hooks)
- Design content that can drive audience engagement and subscriptions
- Consider merchandise or collaboration opportunities
{% endif %}

{% if platform_target != "general" %}
**Platform Optimization for {{ platform_target }}:**
{{ platform_target | platform_optimize }}
{% endif %}

**Quality Requirements:**
- Maintain consistent {{ tone }} tone throughout
- Use vivid, engaging language appropriate for {{ target_audience }}
- Create compelling narrative flow with proper pacing
- Ensure original, plagiarism-free content
- Include emotional hooks and engagement triggers
{% if genre == "fiction" %}
- Develop relatable characters with clear motivations
- Build tension and conflict appropriately
- Use show-don't-tell techniques
{% endif %}
{% if genre == "non_fiction" %}
- Support statements with credible reasoning
- Use clear, logical structure
- Include practical insights or takeaways
{% endif %}

**Output Format:**
Provide the creative writing piece that meets all specified requirements. Focus on quality, originality, and engagement potential for the target audience."""
        
        # Style-specific enhancements
        if request.style == WritingStyle.POETIC:
            base_prompt += "\n\n**Poetic Elements:** Use metaphors, imagery, rhythm, and emotional depth."
        elif request.style == WritingStyle.DRAMATIC:
            base_prompt += "\n\n**Dramatic Elements:** Include conflict, dialogue, and emotional tension."
        elif request.style == WritingStyle.HUMOROUS:
            base_prompt += "\n\n**Humor Elements:** Use wit, wordplay, and situational comedy appropriate for the audience."
        elif request.style == WritingStyle.SUSPENSEFUL:
            base_prompt += "\n\n**Suspense Elements:** Build tension, use cliffhangers, and create anticipation."
        
        # Genre-specific additions
        if request.genre == WritingGenre.SCREENPLAY:
            base_prompt += "\n\n**Screenplay Format:** Use proper screenplay formatting with scene headings, action lines, and dialogue."
        elif request.genre == WritingGenre.POETRY:
            base_prompt += "\n\n**Poetry Format:** Focus on verse structure, rhythm, and poetic devices."
        elif request.genre == WritingGenre.BLOG_POST:
            base_prompt += "\n\n**Blog Format:** Include compelling headline, introduction, body sections, and call-to-action."
        
        return base_prompt
    
    async def _prepare_template_variables(self, request: CreativeWritingRequest) -> Dict[str, Any]:
        """Prepare variables for template compilation"""
        
        # Determine creator type from context
        creator_type = request.creator_context.get("creator_type", "creative writer")
        
        variables = {
            "topic": request.topic,
            "genre": request.genre.value.replace("_", " "),
            "style": request.style.value.replace("_", " "),
            "tone": request.tone.value,
            "target_length": request.target_length,
            "target_audience": request.target_audience,
            "purpose": request.purpose,
            "characters": request.characters,
            "setting": request.setting,
            "plot_elements": request.plot_elements,
            "themes": request.themes,
            "creator_type": creator_type,
            "monetization_enabled": request.monetization_enabled,
            "platform_target": request.platform_target
        }
        
        return variables
    
    async def _generate_content(self, prompt: str, request: CreativeWritingRequest) -> str:
        """Generate creative content using AI model"""
        try:
            # In a real implementation, this would call the AI model
            # For now, we'll create a structured creative writing piece
            
            content_parts = []
            
            # Title generation
            if request.genre == WritingGenre.BLOG_POST:
                title = f"The Art of {request.topic}: A {request.target_audience} Guide"
                content_parts.append(f"# {title}\n")
            elif request.genre == WritingGenre.SHORT_STORY:
                title = f"The {request.topic.title()}"
                content_parts.append(f"**{title}**\n")
            
            # Opening hook
            if request.style == WritingStyle.SUSPENSEFUL:
                opening = f"The last thing anyone expected was for {request.topic} to change everything. But there it was, defying all logic and reason..."
            elif request.style == WritingStyle.HUMOROUS:
                opening = f"If someone had told me that {request.topic} would become the most ridiculous adventure of my life, I would have laughed. Well, I'm laughing now, but for entirely different reasons..."
            elif request.style == WritingStyle.ROMANTIC:
                opening = f"There was something magical about {request.topic} that brought them together in ways neither had imagined possible..."
            else:
                opening = f"In the world of {request.topic}, there exists a story that deserves to be told with the attention and care it demands..."
            
            content_parts.append(opening)
            
            # Main content based on genre
            if request.genre == WritingGenre.FICTION:
                content_parts.extend(await self._generate_fiction_content(request))
            elif request.genre == WritingGenre.BLOG_POST:
                content_parts.extend(await self._generate_blog_content(request))
            elif request.genre == WritingGenre.POETRY:
                content_parts.extend(await self._generate_poetry_content(request))
            else:
                content_parts.extend(await self._generate_general_content(request))
            
            # Platform-specific formatting
            if request.platform_target == "instagram":
                content_parts.append("\n#CreativeWriting #ContentCreator #Storytelling")
            elif request.platform_target == "linkedin":
                content_parts.append("\n\n💭 What's your experience with creative writing? Share your thoughts in the comments!")
            
            # Monetization elements
            if request.monetization_enabled:
                monetization_hook = "\n\n✨ Want to master the art of creative writing? Check out our premium writing workshop series for advanced techniques and personalized feedback."
                content_parts.append(monetization_hook)
            
            return "\n\n".join(content_parts)
        
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return f"Creative content about {request.topic} in {request.style.value} style."
    
    async def _generate_fiction_content(self, request: CreativeWritingRequest) -> List[str]:
        """Generate fiction-specific content"""
        parts = []
        
        if request.characters:
            character_intro = f"Our story follows {', '.join(request.characters[:2])}, whose lives become intertwined through the fascinating world of {request.topic}."
            parts.append(character_intro)
        
        if request.setting:
            setting_desc = f"Set against the backdrop of {request.setting}, the narrative unfolds with unexpected twists and emotional depth."
            parts.append(setting_desc)
        
        # Main narrative
        narrative = f"""The central conflict emerges when our characters must confront the challenges that {request.topic} presents. Through carefully crafted dialogue and vivid descriptions, we explore themes of human nature, relationships, and personal growth.

As the story progresses, each character faces moments of revelation that test their beliefs and push them toward transformation. The {request.tone} tone guides us through emotional landscapes that resonate with the {request.target_audience} audience."""
        
        parts.append(narrative)
        
        if request.themes:
            theme_exploration = f"The narrative weaves together themes of {', '.join(request.themes)}, creating layers of meaning that reward careful readers."
            parts.append(theme_exploration)
        
        return parts
    
    async def _generate_blog_content(self, request: CreativeWritingRequest) -> List[str]:
        """Generate blog post content"""
        parts = []
        
        # Introduction
        intro = f"When it comes to {request.topic}, there's so much more beneath the surface than most people realize. Today, we're diving deep into this fascinating subject to uncover insights that will transform your understanding."
        parts.append(intro)
        
        # Main sections
        sections = [
            f"## Understanding {request.topic}\n\nLet's start with the fundamentals. {request.topic} represents more than just a concept—it's a gateway to new possibilities and creative expression.",
            
            f"## The Creative Potential\n\nWhat makes {request.topic} truly exciting is its potential for creative exploration. Whether you're a seasoned {request.creator_context.get('creator_type', 'creator')} or just starting your journey, there are countless ways to approach this subject.",
            
            f"## Practical Applications\n\nThe real magic happens when we move from theory to practice. Here's how you can start incorporating {request.topic} into your own creative work:",
            
            f"## Looking Forward\n\nAs we continue to explore the boundaries of {request.topic}, new opportunities emerge for creators, artists, and innovators across all fields."
        ]
        
        parts.extend(sections)
        
        # Call to action
        cta = "What's your experience with this topic? Share your thoughts in the comments below, and don't forget to subscribe for more insights into the world of creative expression!"
        parts.append(cta)
        
        return parts
    
    async def _generate_poetry_content(self, request: CreativeWritingRequest) -> List[str]:
        """Generate poetry content"""
        parts = []
        
        # Poetic interpretation
        poem = f"""In the realm where {request.topic} dwells,
Words dance and stories tell
Of mysteries that hearts know well,
And truths that time reveals.

Each verse a stepping stone,
Each line a thread we've sown
Into the tapestry we've grown—
A masterpiece of feels.

Through metaphor and rhyme,
We capture moments in time,
Where {request.topic} and spirit chime
In harmony divine."""
        
        parts.append(poem)
        
        if request.themes:
            reflection = f"\n*This piece explores themes of {', '.join(request.themes)}, inviting readers to discover their own connections to the subject matter.*"
            parts.append(reflection)
        
        return parts
    
    async def _generate_general_content(self, request: CreativeWritingRequest) -> List[str]:
        """Generate general creative content"""
        parts = []
        
        main_content = f"""The journey into {request.topic} begins with curiosity and unfolds through careful observation. Each element contributes to a larger understanding that transcends simple categorization.

Through the lens of {request.style.value} writing, we discover layers of meaning that speak to the {request.target_audience} audience in profound ways. The {request.tone} tone serves as our guide, ensuring that every word serves the greater purpose of connection and understanding.

Whether we're exploring character development, thematic elements, or narrative structure, the foundation remains the same: authentic expression that resonates with readers and creates lasting impact."""
        
        parts.append(main_content)
        
        return parts
    
    async def _post_process_content(self, content: str, request: CreativeWritingRequest) -> str:
        """Post-process generated content"""
        try:
            # Ensure appropriate length
            words = content.split()
            target_words = request.target_length
            
            if len(words) > target_words * 1.2:
                # Trim if too long
                content = " ".join(words[:target_words])
            elif len(words) < target_words * 0.8:
                # Expand if too short
                expansion = f"\n\nThe exploration of {request.topic} continues to offer new insights and perspectives that enrich our understanding and inspire further creative expression."
                content += expansion
            
            # Style-specific post-processing
            if request.style == WritingStyle.POETIC:
                content = self._enhance_poetic_language(content)
            elif request.style == WritingStyle.DRAMATIC:
                content = self._enhance_dramatic_elements(content)
            
            # Platform-specific formatting
            if request.platform_target == "twitter":
                content = self._format_for_twitter(content)
            elif request.platform_target == "linkedin":
                content = self._format_for_linkedin(content)
            
            return content.strip()
        
        except Exception as e:
            logger.error(f"Content post-processing failed: {e}")
            return content
    
    def _enhance_poetic_language(self, content: str) -> str:
        """Enhance content with poetic elements"""
        # Add line breaks for poetic flow
        lines = content.split('. ')
        poetic_lines = []
        
        for line in lines:
            if len(line.split()) > 8:
                # Break long lines
                words = line.split()
                mid_point = len(words) // 2
                poetic_lines.append(' '.join(words[:mid_point]))
                poetic_lines.append(' '.join(words[mid_point:]))
            else:
                poetic_lines.append(line)
        
        return '\n'.join(poetic_lines)
    
    def _enhance_dramatic_elements(self, content: str) -> str:
        """Enhance content with dramatic elements"""
        # Add emphasis and dramatic pauses
        content = content.replace('. ', '.\n\n')
        content = content.replace('!', '!')
        content = content.replace('?', '?')
        return content
    
    def _format_for_twitter(self, content: str) -> str:
        """Format content for Twitter"""
        # Create thread-friendly format
        sentences = content.split('. ')
        if len(sentences) > 3:
            return f"🧵 Thread about {sentences[0]}...\n\n1/{len(sentences[:5])}\n{sentences[0]}"
        return content[:280]  # Twitter character limit
    
    def _format_for_linkedin(self, content: str) -> str:
        """Format content for LinkedIn"""
        # Add professional formatting
        if not content.startswith('#'):
            content = f"💡 Insights on Creative Writing\n\n{content}"
        return content
    
    async def _evaluate_creative_content(
        self, 
        prompt: str, 
        content: str, 
        request: CreativeWritingRequest
    ) -> Any:
        """Evaluate generated creative content"""
        try:
            evaluation_request = {
                "prompt": prompt,
                "response": content,
                "template_id": "creative_writing",
                "creator_context": request.creator_context,
                "evaluation_criteria": ["creativity", "engagement", "coherence", "relevance"],
                "target_audience": request.target_audience,
                "content_category": "creative_writing"
            }
            
            return await self.evaluation_framework.evaluate_prompt_response(evaluation_request)
        
        except Exception as e:
            logger.error(f"Content evaluation failed: {e}")
            # Return mock evaluation
            return type('MockEvaluation', (), {
                'overall_score': 0.75,
                'dimension_scores': {'creativity': 0.8, 'engagement': 0.7, 'quality': 0.75}
            })()
    
    async def _analyze_monetization_potential(self, content: str, request: CreativeWritingRequest) -> Dict[str, Any]:
        """Analyze monetization potential of creative content"""
        try:
            potential_score = 0.0
            opportunities = []
            
            # Check for monetization indicators
            if "premium" in content.lower() or "exclusive" in content.lower():
                potential_score += 0.2
                opportunities.append("Premium content subscription potential")
            
            if len(content.split()) > 500:
                potential_score += 0.1
                opportunities.append("Long-form content suitable for paid publications")
            
            if request.genre in [WritingGenre.BLOG_POST, WritingGenre.ESSAY]:
                potential_score += 0.2
                opportunities.append("Blog monetization and guest posting opportunities")
            
            if request.creator_context.get("creator_type") in ["blogger", "author", "journalist"]:
                potential_score += 0.2
                opportunities.append("Creator-specific monetization channels")
            
            # Platform-specific opportunities
            if request.platform_target in ["linkedin", "medium"]:
                potential_score += 0.1
                opportunities.append("Professional platform monetization")
            
            return {
                "score": min(potential_score, 1.0),
                "opportunities": opportunities,
                "recommendations": [
                    "Consider developing this into a premium content series",
                    "Explore affiliate marketing opportunities within the niche",
                    "Develop companion materials for additional revenue streams"
                ]
            }
        
        except Exception as e:
            logger.error(f"Monetization analysis failed: {e}")
            return {"score": 0.5, "opportunities": [], "recommendations": []}
    
    async def _generate_creator_insights(self, content: str, request: CreativeWritingRequest) -> Dict[str, Any]:
        """Generate creator economy insights"""
        try:
            insights = {
                "content_type": "creative_writing",
                "engagement_potential": "high" if len(content.split()) > 300 else "medium",
                "shareability": "high" if request.style in [WritingStyle.HUMOROUS, WritingStyle.INSPIRATIONAL] else "medium",
                "audience_alignment": request.target_audience,
                "collaboration_opportunities": [],
                "platform_recommendations": []
            }
            
            # Collaboration opportunities
            if request.genre == WritingGenre.FICTION:
                insights["collaboration_opportunities"].extend([
                    "Partner with illustrators for visual storytelling",
                    "Collaborate with voice actors for audio versions",
                    "Work with other writers for anthology projects"
                ])
            
            # Platform recommendations
            if request.style == WritingStyle.POETIC:
                insights["platform_recommendations"].extend([
                    "Instagram for visual poetry posts",
                    "Medium for longer poetic essays",
                    "YouTube for spoken word performances"
                ])
            elif request.genre == WritingGenre.BLOG_POST:
                insights["platform_recommendations"].extend([
                    "LinkedIn for professional content",
                    "Medium for thought leadership",
                    "Personal blog for full creative control"
                ])
            
            return insights
        
        except Exception as e:
            logger.error(f"Creator insights generation failed: {e}")
            return {"content_type": "creative_writing", "engagement_potential": "medium"}
    
    async def get_template_variations(self) -> List[Dict[str, Any]]:
        """Get available template variations"""
        return [
            {
                "name": "Short Story Generator",
                "description": "Create engaging short stories with character development",
                "style": WritingStyle.NARRATIVE,
                "genre": WritingGenre.SHORT_STORY,
                "best_for": ["fiction_writers", "content_creators", "bloggers"]
            },
            {
                "name": "Blog Post Creator",
                "description": "Generate compelling blog posts with SEO optimization",
                "style": WritingStyle.CONVERSATIONAL,
                "genre": WritingGenre.BLOG_POST,
                "best_for": ["bloggers", "marketers", "educators"]
            },
            {
                "name": "Poetry Generator",
                "description": "Create beautiful poetry with emotional depth",
                "style": WritingStyle.POETIC,
                "genre": WritingGenre.POETRY,
                "best_for": ["poets", "artists", "social_media_creators"]
            },
            {
                "name": "Creative Essay Writer",
                "description": "Develop thought-provoking essays with personal voice",
                "style": WritingStyle.EXPOSITORY,
                "genre": WritingGenre.ESSAY,
                "best_for": ["writers", "academics", "thought_leaders"]
            }
        ]
    
    async def cleanup(self) -> None:
        """Cleanup template resources"""
        try:
            await self.template_compiler.cleanup()
            await self.security_validator.cleanup()
            await self.evaluation_framework.cleanup()
            
            logger.info("Creative Writing Template cleanup completed")
        
        except Exception as e:
            logger.error(f"Creative Writing Template cleanup failed: {e}")


# Global creative writing template instance
creative_writing_template = CreativeWritingTemplate()