"""
Story Narrative Template for AI-Powered Content Generation

Enterprise-grade story narrative prompt engineering template optimized for the Creator Economy.
Provides advanced prompt structures for generating high-quality narrative stories across
multiple formats, genres, and platforms with built-in optimization for engagement and monetization.

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

class NarrativeGenre(Enum):
    """Story narrative genres"""
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science_fiction"
    MYSTERY = "mystery"
    THRILLER = "thriller"
    ROMANCE = "romance"
    HORROR = "horror"
    HISTORICAL = "historical"
    CONTEMPORARY = "contemporary"
    LITERARY = "literary"
    ADVENTURE = "adventure"
    DRAMA = "drama"
    COMEDY = "comedy"
    MAGICAL_REALISM = "magical_realism"
    DYSTOPIAN = "dystopian"
    COMING_OF_AGE = "coming_of_age"
    SLICE_OF_LIFE = "slice_of_life"

class NarrativeFormat(Enum):
    """Story format types"""
    SHORT_STORY = "short_story"
    NOVELLA = "novella"
    SERIAL_EPISODE = "serial_episode"
    FLASH_FICTION = "flash_fiction"
    MICRO_FICTION = "micro_fiction"
    CHAPTER = "chapter"
    VIGNETTE = "vignette"
    SCREENPLAY = "screenplay"
    AUDIO_STORY = "audio_story"
    SOCIAL_MEDIA_STORY = "social_media_story"
    INTERACTIVE_STORY = "interactive_story"

class NarrativeTone(Enum):
    """Narrative tone options"""
    SERIOUS = "serious"
    HUMOROUS = "humorous"
    DARK = "dark"
    LIGHT = "light"
    MYSTERIOUS = "mysterious"
    ROMANTIC = "romantic"
    SUSPENSEFUL = "suspenseful"
    NOSTALGIC = "nostalgic"
    OPTIMISTIC = "optimistic"
    MELANCHOLIC = "melancholic"
    SATIRICAL = "satirical"
    WHIMSICAL = "whimsical"

class PointOfView(Enum):
    """Narrative point of view"""
    FIRST_PERSON = "first_person"
    SECOND_PERSON = "second_person"
    THIRD_PERSON_LIMITED = "third_person_limited"
    THIRD_PERSON_OMNISCIENT = "third_person_omniscient"
    MULTIPLE_POV = "multiple_pov"

@dataclass
class StoryNarrativePrompt:
    """Story narrative prompt configuration"""
    genre: NarrativeGenre
    format: NarrativeFormat
    tone: NarrativeTone
    point_of_view: PointOfView
    title: str
    word_count_target: int
    premise: str
    main_character: str = ""
    supporting_characters: List[str] = field(default_factory=list)
    setting: str = ""
    time_period: str = ""
    central_conflict: str = ""
    themes: List[str] = field(default_factory=list)
    target_audience: str = ""
    content_warnings: List[str] = field(default_factory=list)
    series_context: str = ""
    platform_optimization: str = ""
    monetization_strategy: str = ""
    engagement_hooks: List[str] = field(default_factory=list)
    cultural_elements: List[str] = field(default_factory=list)
    research_notes: str = ""
    style_references: List[str] = field(default_factory=list)
    ending_type: str = ""
    cliffhanger_elements: List[str] = field(default_factory=list)

class StoryNarrativeTemplate:
    """
    Advanced story narrative template for AI content generation
    
    Optimized for Creator Economy with platform-specific formatting, serialization support,
    and monetization strategies. Supports all major narrative formats and distribution platforms.
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.creator_economy_features = True
        self.serialization_support = True
        self.multi_platform_optimization = True
        
        # Platform specifications for story distribution
        self.platform_specs = {
            "medium": {
                "optimal_length": "1000-2500 words",
                "format": "blog_style",
                "features": ["chapters", "member_only", "highlights", "responses"],
                "monetization": ["member_subscriptions", "tips", "publications"]
            },
            "substack": {
                "optimal_length": "800-2000 words",
                "format": "newsletter_style",
                "features": ["email_delivery", "comments", "subscriber_only"],
                "monetization": ["paid_subscriptions", "premium_content"]
            },
            "wattpad": {
                "optimal_length": "1500-3000 words per chapter",
                "format": "serialized_chapters",
                "features": ["chapter_breaks", "comments", "voting", "reading_lists"],
                "monetization": ["premium_stories", "brand_partnerships", "publishing_deals"]
            },
            "kindle_vella": {
                "optimal_length": "600-5000 words per episode",
                "format": "episodic_serial",
                "features": ["tokens", "episode_breaks", "reader_engagement"],
                "monetization": ["token_purchases", "bonus_episodes"]
            },
            "social_media": {
                "optimal_length": "100-500 words",
                "format": "micro_stories",
                "features": ["hashtags", "comments", "shares", "threads"],
                "monetization": ["creator_funds", "brand_partnerships", "tip_jars"]
            },
            "podcast": {
                "optimal_length": "2000-4000 words (15-30 minutes)",
                "format": "audio_narrative",
                "features": ["voice_acting", "sound_effects", "music"],
                "monetization": ["sponsorships", "premium_episodes", "listener_support"]
            }
        }
        
        # Genre-specific story elements
        self.genre_elements = {
            NarrativeGenre.FANTASY: {
                "common_elements": ["magic systems", "world-building", "mythical creatures", "quests"],
                "character_types": ["heroes", "wizards", "magical beings", "mentors"],
                "conflict_types": ["good vs evil", "power struggles", "prophecies", "coming of age"]
            },
            NarrativeGenre.SCIENCE_FICTION: {
                "common_elements": ["advanced technology", "space travel", "future societies", "scientific concepts"],
                "character_types": ["scientists", "explorers", "AI beings", "time travelers"],
                "conflict_types": ["technology vs humanity", "exploration dangers", "ethical dilemmas"]
            },
            NarrativeGenre.MYSTERY: {
                "common_elements": ["clues", "red herrings", "investigation", "plot twists"],
                "character_types": ["detectives", "suspects", "witnesses", "victims"],
                "conflict_types": ["puzzle solving", "justice vs truth", "moral ambiguity"]
            },
            NarrativeGenre.ROMANCE: {
                "common_elements": ["relationship development", "emotional conflict", "intimacy", "happy endings"],
                "character_types": ["lovers", "rivals", "matchmakers", "obstacles"],
                "conflict_types": ["miscommunication", "external obstacles", "personal growth"]
            }
        }
        
    def generate_prompt(self, config: StoryNarrativePrompt) -> Dict[str, Any]:
        """
        Generate optimized story narrative prompt
        
        Args:
            config: Story narrative configuration
            
        Returns:
            Dictionary containing optimized prompt and metadata
        """
        try:
            # Get platform specifications
            platform_spec = self.platform_specs.get(config.platform_optimization, {})
            
            # Get genre elements
            genre_elements = self.genre_elements.get(config.genre, {})
            
            # Build comprehensive prompt
            prompt_components = {
                "system_prompt": self._build_system_prompt(config),
                "user_prompt": self._build_user_prompt(config, platform_spec),
                "story_structure": self._build_story_structure(config),
                "character_development": self._build_character_development(config),
                "world_building": self._build_world_building(config, genre_elements),
                "narrative_techniques": self._build_narrative_techniques(config),
                "engagement_optimization": self._build_engagement_optimization(config),
                "platform_optimization": self._build_platform_optimization(config, platform_spec),
                "monetization_integration": self._build_monetization_integration(config)
            }
            
            # Combine into final prompt
            final_prompt = self._combine_prompt_components(prompt_components)
            
            # Generate metadata
            metadata = self._generate_metadata(config)
            
            logger.info(f"Generated story narrative prompt for {config.genre.value} {config.format.value}")
            
            return {
                "prompt": final_prompt,
                "metadata": metadata,
                "config": config,
                "optimization_score": self._calculate_optimization_score(config),
                "engagement_potential": self._estimate_engagement_potential(config),
                "serialization_potential": self._estimate_serialization_potential(config),
                "commercial_viability": self._estimate_commercial_viability(config)
            }
            
        except Exception as e:
            logger.error(f"Error generating story narrative prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, config: StoryNarrativePrompt) -> str:
        """Build system prompt for story narrative generation"""
        return f"""You are a master storyteller and narrative writer specializing in {config.genre.value} stories for the Creator Economy.

Your expertise includes:
- Professional creative writing and narrative construction across all genres
- Character development and dialogue mastery
- World-building and atmospheric storytelling
- Creator Economy content strategy and audience engagement
- Platform-specific story optimization and serialization
- Reader psychology and engagement optimization

Creating: {config.title}
Genre: {config.genre.value}
Format: {config.format.value}
Tone: {config.tone.value}
POV: {config.point_of_view.value}
Target Length: {config.word_count_target} words
Target Audience: {config.target_audience or 'General fiction readers'}

Focus on:
- Creating compelling, commercially viable narratives
- Maximum reader engagement and retention
- Platform optimization for discovery and monetization
- Series potential and serialization opportunities
- Building author brand and reader loyalty
- Professional-quality prose and storytelling craft"""

    def _build_user_prompt(self, config: StoryNarrativePrompt, platform_spec: Dict) -> str:
        """Build user prompt with story specifications"""
        character_info = f"\nMain Character: {config.main_character}" if config.main_character else ""
        supporting_info = f"\nSupporting Characters: {', '.join(config.supporting_characters)}" if config.supporting_characters else ""
        setting_info = f"\nSetting: {config.setting}" if config.setting else ""
        time_info = f"\nTime Period: {config.time_period}" if config.time_period else ""
        conflict_info = f"\nCentral Conflict: {config.central_conflict}" if config.central_conflict else ""
        themes_info = f"\nThemes: {', '.join(config.themes)}" if config.themes else ""
        series_info = f"\nSeries Context: {config.series_context}" if config.series_context else ""
        research_info = f"\nResearch Notes: {config.research_notes}" if config.research_notes else ""
        style_info = f"\nStyle References: {', '.join(config.style_references)}" if config.style_references else ""
        warnings_info = f"\nContent Warnings: {', '.join(config.content_warnings)}" if config.content_warnings else ""
        
        return f"""Story Premise: {config.premise}
Word Count Target: {config.word_count_target} words
Platform: {config.platform_optimization or 'Multi-platform'}
Optimal Length: {platform_spec.get('optimal_length', 'Standard story length')}{character_info}{supporting_info}{setting_info}{time_info}{conflict_info}{themes_info}{series_info}{research_info}{style_info}{warnings_info}

Story Requirements:
- Write in {config.point_of_view.value} perspective with {config.tone.value} tone
- Follow {config.genre.value} genre conventions while maintaining originality
- Include compelling character arcs and emotional depth
- Create engaging plot with proper pacing and structure
- End with {config.ending_type or 'satisfying resolution'}
- Target {config.target_audience or 'general fiction audience'}

Creator Economy Optimization:
- Design for maximum reader engagement and retention
- Include hooks and cliffhangers for serialization potential
- Create memorable characters and quotable moments
- Build world and characters suitable for series expansion
- Include elements that encourage reader comments and discussion
- Optimize for platform algorithms and discovery features
- Create content suitable for cross-platform adaptation and repurposing"""

    def _build_story_structure(self, config: StoryNarrativePrompt) -> str:
        """Build story structure based on format and length"""
        if config.format == NarrativeFormat.FLASH_FICTION:
            structure = """
STORY STRUCTURE (Flash Fiction):
1. Immediate hook and situation setup (first 50 words)
2. Character and conflict introduction (words 50-150)
3. Rising action and tension escalation (words 150-400)
4. Climax and turning point (words 400-450)
5. Resolution and impact (words 450-500)

Focus: Maximum impact in minimal words, single powerful moment"""
            
        elif config.format == NarrativeFormat.SHORT_STORY:
            structure = """
STORY STRUCTURE (Short Story):
1. Opening hook and character introduction (10-15% of story)
2. Inciting incident and conflict establishment (15-25%)
3. Rising action and complication development (25-60%)
4. Climax and crisis point (60-75%)
5. Falling action and consequences (75-90%)
6. Resolution and denouement (90-100%)

Focus: Complete character arc, single central conflict, satisfying resolution"""
            
        elif config.format == NarrativeFormat.SERIAL_EPISODE:
            structure = """
STORY STRUCTURE (Serial Episode):
1. Recap/hook from previous episode (first 5-10%)
2. New situation or complication introduction (10-25%)
3. Character development and plot advancement (25-70%)
4. Rising tension and obstacles (70-85%)
5. Cliffhanger or episode resolution (85-100%)

Focus: Forward momentum, episode satisfaction, series continuity"""
            
        else:  # Standard structure
            structure = """
STORY STRUCTURE (Standard Narrative):
1. Compelling opening and world establishment
2. Character introduction and goal setting
3. Rising action with escalating complications
4. Midpoint crisis and character development
5. Climactic confrontation and resolution
6. Satisfying conclusion and character growth

Focus: Complete narrative arc with strong emotional journey"""
        
        return f"""{structure}

Pacing Guidelines:
- Vary sentence and paragraph length for rhythm
- Use scene breaks and white space strategically
- Balance action, dialogue, and description
- Create breathing room between intense moments
- Build tension gradually toward climactic moments

Engagement Elements:
- Include compelling hooks every 500-800 words
- Create curiosity gaps and unanswered questions
- Use foreshadowing and dramatic irony
- Include surprising but logical plot developments
- End sections with hooks to encourage continued reading"""

    def _build_character_development(self, config: StoryNarrativePrompt) -> str:
        """Build character development guidelines"""
        return f"""
CHARACTER DEVELOPMENT:

Main Character: {config.main_character or 'To be developed'}
- Create three-dimensional character with clear motivation, goal, and internal conflict
- Show character growth and change throughout the story
- Include unique voice, mannerisms, and personality traits
- Give character both strengths and meaningful flaws
- Create relatable struggles and authentic emotional responses

Supporting Characters:
{', '.join(config.supporting_characters) if config.supporting_characters else 'Supporting cast to be developed'}
- Each character should serve a specific story function
- Give supporting characters their own goals and motivations
- Create distinct voices and personalities for each character
- Use supporting characters to reveal aspects of the main character
- Include diverse perspectives and backgrounds appropriately

Character Relationships:
- Develop realistic, complex relationships between characters
- Show relationships evolving and changing throughout the story
- Use dialogue to reveal character and advance plot
- Include subtext and underlying tensions in interactions
- Create chemistry and believable emotional connections

Character Voice and Dialogue:
- Maintain consistent character voice throughout
- Use dialogue to reveal character personality and background
- Include natural speech patterns and individual mannerisms
- Balance dialogue with action and description
- Use dialogue tags and action beats effectively"""

    def _build_world_building(self, config: StoryNarrativePrompt, genre_elements: Dict) -> str:
        """Build world-building guidelines"""
        setting = config.setting or "World to be established"
        time_period = config.time_period or "Time period to be determined"
        cultural_elements = f"Cultural elements: {', '.join(config.cultural_elements)}" if config.cultural_elements else ""
        
        return f"""
WORLD-BUILDING:

Setting: {setting}
Time Period: {time_period}
{cultural_elements}

Physical Environment:
- Create vivid, immersive settings that support the story
- Include sensory details that bring locations to life
- Establish the rules and logic of the story world
- Use setting to reflect character emotions and themes
- Include enough detail to ground readers without overwhelming

Cultural and Social Context:
- Establish social norms, customs, and expectations
- Include relevant historical or cultural background
- Show how the world's rules affect character choices
- Create authentic dialogue and behavior for the setting
- Address diversity and representation thoughtfully

Genre-Specific Elements:
{genre_elements.get('common_elements', [])}
- Incorporate genre conventions while adding original elements
- Establish the rules of magic, technology, or special systems
- Create believable explanations for extraordinary elements
- Use genre elements to enhance rather than overshadow character and plot
- Balance familiar elements with fresh, innovative approaches

Atmospheric Details:
- Use weather, lighting, and environmental details to create mood
- Include sounds, smells, and textures to engage all senses
- Create contrast between different locations and scenes
- Use setting changes to mark story progression and character development
- Make the environment feel lived-in and authentic"""

    def _build_narrative_techniques(self, config: StoryNarrativePrompt) -> str:
        """Build narrative techniques and style guidelines"""
        return f"""
NARRATIVE TECHNIQUES:

Point of View: {config.point_of_view.value}
- Maintain consistent POV throughout the story
- Use POV limitations and advantages strategically
- Show rather than tell whenever possible
- Include internal thoughts and emotions appropriately
- Balance introspection with external action

Tone and Style: {config.tone.value}
- Maintain consistent tone that serves the story
- Use sentence structure and word choice to support mood
- Include appropriate humor, tension, or emotional weight
- Balance literary quality with accessibility
- Create a distinctive author voice

Literary Devices:
- Use metaphors and similes to enhance description
- Include symbolism and themes naturally within the narrative
- Use foreshadowing to create anticipation and cohesion
- Include irony and dramatic tension where appropriate
- Use repetition and motifs to reinforce themes

Pacing and Rhythm:
- Vary sentence and paragraph length for optimal flow
- Use dialogue, action, and description in balanced proportions
- Create natural scene breaks and chapter divisions
- Build tension gradually toward climactic moments
- Include moments of reflection and character development

Show vs. Tell:
- Demonstrate character traits through actions and dialogue
- Use concrete details instead of abstract statements
- Let readers draw conclusions from evidence presented
- Include sensory details to create immersive experiences
- Balance exposition with dramatic scenes"""

    def _build_engagement_optimization(self, config: StoryNarrativePrompt) -> str:
        """Build engagement optimization strategies"""
        hooks = f"Engagement hooks: {', '.join(config.engagement_hooks)}" if config.engagement_hooks else ""
        cliffhangers = f"Cliffhanger elements: {', '.join(config.cliffhanger_elements)}" if config.cliffhanger_elements else ""
        
        return f"""
ENGAGEMENT OPTIMIZATION:

Reader Psychology:
- Create immediate emotional investment in characters
- Use curiosity gaps and unanswered questions strategically
- Include relatable conflicts and universal themes
- Build anticipation through foreshadowing and setup
- Create satisfying payoffs for setup elements

Retention Strategies:
{hooks}
- Include compelling hooks at story opening and section breaks
- Create cliffhangers and page-turners at chapter/section ends
- Use short paragraphs and varied sentence structure for readability
- Include surprising but logical plot developments
- Balance familiar elements with unexpected twists

Emotional Engagement:
- Create characters readers care about and root for
- Include high emotional stakes and meaningful consequences
- Use conflict to create tension and investment
- Include moments of triumph, loss, and character growth
- Create cathartic emotional releases and satisfying resolutions

Interactive Elements:
{cliffhangers}
- Include discussion-worthy themes and moral questions
- Create moments that encourage reader speculation
- Include cultural references and relatable situations
- Use current events or trending topics where appropriate
- Design story elements that encourage social media sharing"""

    def _build_platform_optimization(self, config: StoryNarrativePrompt, platform_spec: Dict) -> str:
        """Build platform-specific optimization"""
        if not config.platform_optimization:
            return "PLATFORM OPTIMIZATION: Multi-platform narrative optimization for maximum reach"
            
        platform = config.platform_optimization.lower()
        
        return f"""
PLATFORM OPTIMIZATION for {platform.upper()}:

Format Requirements:
- Optimal Length: {platform_spec.get('optimal_length', 'Platform appropriate')}
- Format Style: {platform_spec.get('format', 'Standard narrative')}
- Platform Features: {', '.join(platform_spec.get('features', []))}

Content Optimization:
- Structure for platform consumption patterns and user behavior
- Include platform-specific engagement elements
- Use appropriate formatting for platform presentation
- Optimize for mobile reading and platform interfaces
- Include social sharing and discussion triggers

Discovery Optimization:
- Use relevant keywords and tags for platform search
- Include trending topics and popular themes where appropriate
- Create compelling titles and descriptions for platform algorithms
- Use platform-specific hashtags and categorization
- Build author brand recognition and platform presence

Monetization Integration:
- Design content for platform revenue opportunities
- Include strategic calls-to-action for platform features
- Create content suitable for premium tiers or subscriptions
- Build audience for platform-specific monetization tools
- Develop series potential for ongoing platform engagement"""

    def _build_monetization_integration(self, config: StoryNarrativePrompt) -> str:
        """Build monetization integration strategies"""
        strategy = config.monetization_strategy or "Multi-revenue stream narrative development"
        
        return f"""
MONETIZATION INTEGRATION:

Strategy: {strategy}

Direct Monetization:
- Create high-quality content suitable for paid subscriptions
- Design stories with series and sequel potential
- Include cliffhangers and hooks for continued engagement
- Build compelling character and world development for franchise potential
- Create content suitable for adaptation (audio, video, graphic novel)

Platform Revenue:
- Optimize for platform creator funds and revenue sharing
- Create content eligible for premium tiers and subscriber benefits
- Design for platform-specific monetization features
- Build audience for live reading events and interactive content
- Develop relationships with platform curators and influencers

Brand Building:
- Establish distinctive author voice and storytelling style
- Create memorable characters and world-building elements
- Include themes and messages that resonate with target audience
- Build author platform and reader community
- Develop signature elements that become associated with author brand

Long-term Value:
- Create evergreen content with lasting appeal
- Build intellectual property with multiple revenue streams
- Establish reader loyalty and recurring engagement
- Develop content suitable for educational and library markets
- Create networking opportunities with industry professionals

Reader Investment:
- Build emotional investment that translates to financial support
- Create community around stories and characters
- Include reader interaction opportunities and feedback integration
- Develop fan engagement and user-generated content
- Build anticipation for future releases and projects"""

    def _combine_prompt_components(self, components: Dict[str, str]) -> str:
        """Combine all prompt components into final prompt"""
        return f"""{components['system_prompt']}

{components['user_prompt']}

{components['story_structure']}

{components['character_development']}

{components['world_building']}

{components['narrative_techniques']}

{components['engagement_optimization']}

{components['platform_optimization']}

{components['monetization_integration']}

Now create the complete story narrative following all these guidelines. Include rich character development, immersive world-building, engaging plot progression, and professional prose quality."""

    def _generate_metadata(self, config: StoryNarrativePrompt) -> Dict[str, Any]:
        """Generate metadata for the story"""
        return {
            "template_version": self.template_version,
            "genre": config.genre.value,
            "format": config.format.value,
            "tone": config.tone.value,
            "point_of_view": config.point_of_view.value,
            "word_count_target": config.word_count_target,
            "estimated_reading_time": self._estimate_reading_time(config.word_count_target),
            "target_audience": config.target_audience,
            "has_series_potential": bool(config.series_context or config.cliffhanger_elements),
            "themes_count": len(config.themes),
            "characters_count": len(config.supporting_characters) + (1 if config.main_character else 0),
            "content_warnings_count": len(config.content_warnings),
            "engagement_hooks_count": len(config.engagement_hooks),
            "platform": config.platform_optimization,
            "monetization_enabled": bool(config.monetization_strategy),
            "creation_timestamp": datetime.now().isoformat(),
            "creator_economy_optimized": True
        }

    def _calculate_optimization_score(self, config: StoryNarrativePrompt) -> float:
        """Calculate optimization score based on configuration"""
        score = 0.5  # Base score
        
        # Add points for configuration completeness
        if config.main_character:
            score += 0.1
        if config.supporting_characters:
            score += 0.05
        if config.setting:
            score += 0.05
        if config.central_conflict:
            score += 0.1
        if config.themes:
            score += 0.05
        if config.engagement_hooks:
            score += 0.1
        if config.platform_optimization:
            score += 0.1
        if config.monetization_strategy:
            score += 0.05
        
        return min(score, 1.0)

    def _estimate_engagement_potential(self, config: StoryNarrativePrompt) -> str:
        """Estimate engagement potential"""
        score = self._calculate_optimization_score(config)
        
        # Boost for engagement-friendly elements
        if config.engagement_hooks:
            score += 0.05
        if config.cliffhanger_elements:
            score += 0.05
        if config.format in [NarrativeFormat.SERIAL_EPISODE, NarrativeFormat.SOCIAL_MEDIA_STORY]:
            score += 0.05
            
        if score >= 0.8:
            return "High"
        elif score >= 0.6:
            return "Medium-High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low-Medium"

    def _estimate_serialization_potential(self, config: StoryNarrativePrompt) -> str:
        """Estimate serialization potential"""
        if config.series_context and config.cliffhanger_elements:
            return "High"
        elif config.series_context or config.cliffhanger_elements:
            return "Medium-High"
        elif config.format == NarrativeFormat.SERIAL_EPISODE:
            return "Medium"
        else:
            return "Low"

    def _estimate_commercial_viability(self, config: StoryNarrativePrompt) -> str:
        """Estimate commercial viability"""
        score = 0.3  # Base commercial score
        
        # Popular genres
        if config.genre in [NarrativeGenre.ROMANCE, NarrativeGenre.MYSTERY, NarrativeGenre.FANTASY]:
            score += 0.2
        
        # Commercial formats
        if config.format in [NarrativeFormat.SERIAL_EPISODE, NarrativeFormat.NOVELLA]:
            score += 0.15
            
        # Platform optimization
        if config.platform_optimization:
            score += 0.15
            
        # Monetization strategy
        if config.monetization_strategy:
            score += 0.2
            
        if score >= 0.7:
            return "High"
        elif score >= 0.5:
            return "Medium-High"
        elif score >= 0.3:
            return "Medium"
        else:
            return "Low"

    def _estimate_reading_time(self, word_count: int) -> str:
        """Estimate reading time based on word count"""
        minutes = word_count / 200  # Average reading speed
        
        if minutes < 1:
            return "Less than 1 minute"
        elif minutes < 60:
            return f"{int(minutes)} minutes"
        else:
            hours = minutes / 60
            return f"{hours:.1f} hours"

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = StoryNarrativePrompt(
        genre=NarrativeGenre.SCIENCE_FICTION,
        format=NarrativeFormat.SERIAL_EPISODE,
        tone=NarrativeTone.SUSPENSEFUL,
        point_of_view=PointOfView.THIRD_PERSON_LIMITED,
        title="The Last Signal - Episode 1: Discovery",
        word_count_target=2500,
        premise="A deep space communication specialist discovers a mysterious signal that appears to be humanity's last transmission from Earth, but it's dated 50 years in the future",
        main_character="Dr. Elena Vasquez, 34-year-old xenolinguist aboard research station Kepler-442b",
        supporting_characters=["Commander Ash Chen", "AI Assistant ARIA", "Chief Engineer Yuki Tanaka"],
        setting="Remote research station orbiting exoplanet Kepler-442b, 1,200 light-years from Earth",
        time_period="2387 CE, during humanity's first deep space colonization wave",
        central_conflict="Elena must decode the future transmission while questioning the implications for humanity's fate",
        themes=["time paradox", "scientific ethics", "isolation vs connection", "humanity's future"],
        target_audience="Science fiction enthusiasts, serial fiction readers",
        series_context="First episode of planned 12-episode season exploring time loops and causality",
        platform_optimization="kindle_vella",
        monetization_strategy="Episodic token-based revenue with premium bonus content",
        engagement_hooks=["mysterious signal revelation", "time paradox discovery", "cliffhanger ending"],
        cultural_elements=["diverse international crew", "future linguistic evolution"],
        research_notes="Consulted astrophysics papers on interstellar communication and time dilation",
        style_references=["Andy Weir", "Liu Cixin", "Martha Wells"],
        ending_type="cliffhanger leading to episode 2",
        cliffhanger_elements=["signal source revelation", "timeline implications", "crew safety threat"]
    )
    
    # Generate prompt
    template = StoryNarrativeTemplate()
    result = template.generate_prompt(config)
    
    print("=== STORY NARRATIVE TEMPLATE EXAMPLE ===")
    print(f"Optimization Score: {result['optimization_score']:.2f}")
    print(f"Engagement Potential: {result['engagement_potential']}")
    print(f"Serialization Potential: {result['serialization_potential']}")
    print(f"Commercial Viability: {result['commercial_viability']}")
    print(f"Estimated Reading Time: {result['metadata']['estimated_reading_time']}")
    print("\n" + "="*50)
    print(result['prompt'])