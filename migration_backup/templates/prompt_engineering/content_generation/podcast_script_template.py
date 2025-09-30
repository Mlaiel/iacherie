"""
Podcast Script Template for AI-Powered Content Generation

Enterprise-grade podcast script prompt engineering template optimized for the Creator Economy.
Provides advanced prompt structures for generating high-quality podcast scripts across
multiple formats, styles, and platforms with built-in optimization for engagement and monetization.

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

class PodcastFormat(Enum):
    """Supported podcast formats"""
    INTERVIEW = "interview"
    SOLO_MONOLOGUE = "solo_monologue"
    PANEL_DISCUSSION = "panel_discussion"
    NARRATIVE_STORYTELLING = "narrative_storytelling"
    EDUCATIONAL = "educational"
    NEWS_COMMENTARY = "news_commentary"
    COMEDY = "comedy"
    TRUE_CRIME = "true_crime"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    HEALTH_WELLNESS = "health_wellness"
    ENTERTAINMENT = "entertainment"
    DOCUMENTARY = "documentary"
    ROUNDTABLE = "roundtable"

class PodcastLength(Enum):
    """Podcast episode length options"""
    MICRO = "micro"          # 5-15 minutes
    SHORT = "short"          # 15-30 minutes
    STANDARD = "standard"    # 30-60 minutes
    LONG = "long"           # 60-90 minutes
    EXTENDED = "extended"    # 90+ minutes

class PodcastTone(Enum):
    """Podcast tone options"""
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    INVESTIGATIVE = "investigative"
    INSPIRATIONAL = "inspirational"
    HUMOROUS = "humorous"
    SERIOUS = "serious"
    INTIMATE = "intimate"

@dataclass
class PodcastScriptPrompt:
    """Podcast script prompt configuration"""
    format: PodcastFormat
    length: PodcastLength
    tone: PodcastTone
    topic: str
    duration_minutes: float
    target_audience: str
    host_info: str = ""
    guest_info: str = ""
    show_description: str = ""
    episode_number: Optional[int] = None
    season_number: Optional[int] = None
    main_talking_points: List[str] = field(default_factory=list)
    research_sources: List[str] = field(default_factory=list)
    call_to_action: str = ""
    sponsor_segments: List[str] = field(default_factory=list)
    monetization_strategy: str = ""
    seo_keywords: List[str] = field(default_factory=list)
    engagement_elements: List[str] = field(default_factory=list)
    audience_interaction: str = ""
    series_context: str = ""
    platform_distribution: List[str] = field(default_factory=list)

class PodcastScriptTemplate:
    """
    Advanced podcast script template for AI content generation
    
    Optimized for Creator Economy with platform-specific formatting, engagement optimization,
    monetization strategies, and audience building. Supports all major podcast formats and platforms.
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.creator_economy_features = True
        self.multi_platform_optimization = True
        self.monetization_optimization = True
        
        # Platform distribution specifications
        self.platform_specs = {
            "spotify": {
                "max_title_length": 60,
                "description_length": 4000,
                "features": ["chapters", "polls", "q_and_a", "video_podcasts"],
                "monetization": ["spotify_ad_studio", "premium_subscriptions", "fan_funding"]
            },
            "apple_podcasts": {
                "max_title_length": 60,
                "description_length": 4000,
                "features": ["chapters", "transcripts", "bonus_content"],
                "monetization": ["subscriptions", "premium_episodes", "tip_jar"]
            },
            "youtube": {
                "max_title_length": 100,
                "description_length": 5000,
                "features": ["video_podcasts", "chapters", "live_streaming", "shorts_clips"],
                "monetization": ["ads", "memberships", "super_chat", "merch_shelf"]
            },
            "google_podcasts": {
                "max_title_length": 60,
                "description_length": 4000,
                "features": ["transcripts", "automatic_chapters"],
                "monetization": ["google_ad_manager", "listener_support"]
            }
        }
        
        # Format-specific structures
        self.format_structures = {
            PodcastFormat.INTERVIEW: self._get_interview_structure(),
            PodcastFormat.SOLO_MONOLOGUE: self._get_solo_structure(),
            PodcastFormat.PANEL_DISCUSSION: self._get_panel_structure(),
            PodcastFormat.NARRATIVE_STORYTELLING: self._get_narrative_structure(),
            PodcastFormat.EDUCATIONAL: self._get_educational_structure(),
            PodcastFormat.NEWS_COMMENTARY: self._get_news_structure(),
            PodcastFormat.COMEDY: self._get_comedy_structure(),
            PodcastFormat.TRUE_CRIME: self._get_true_crime_structure(),
            PodcastFormat.BUSINESS: self._get_business_structure(),
        }
        
    def generate_prompt(self, config: PodcastScriptPrompt) -> Dict[str, Any]:
        """
        Generate optimized podcast script prompt
        
        Args:
            config: Podcast script configuration
            
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
                "monetization_guidance": self._build_monetization_guidance(config),
                "audio_production_notes": self._build_audio_production_notes(config),
                "platform_optimization": self._build_platform_optimization(config),
                "seo_optimization": self._build_seo_optimization(config)
            }
            
            # Combine into final prompt
            final_prompt = self._combine_prompt_components(prompt_components)
            
            # Generate metadata
            metadata = self._generate_metadata(config)
            
            logger.info(f"Generated podcast script prompt for {config.format.value} format")
            
            return {
                "prompt": final_prompt,
                "metadata": metadata,
                "config": config,
                "optimization_score": self._calculate_optimization_score(config),
                "engagement_potential": self._estimate_engagement_potential(config),
                "monetization_potential": self._estimate_monetization_potential(config),
                "platform_distribution_strategy": self._generate_distribution_strategy(config)
            }
            
        except Exception as e:
            logger.error(f"Error generating podcast script prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, config: PodcastScriptPrompt) -> str:
        """Build system prompt for podcast script generation"""
        episode_info = f"Episode {config.episode_number}" if config.episode_number else "New episode"
        season_info = f"Season {config.season_number}" if config.season_number else ""
        
        return f"""You are an expert podcast script writer and audio content creator specializing in {config.format.value} podcasts for the Creator Economy.

Your expertise includes:
- Professional podcast production and scriptwriting
- Audio storytelling and engagement optimization
- Creator Economy monetization and audience growth
- Multi-platform podcast distribution strategies
- Audience retention and listener experience optimization
- Podcast SEO and discoverability best practices

Creating: {episode_info} {season_info}
Format: {config.format.value}
Length: {config.length.value} ({config.duration_minutes} minutes)
Tone: {config.tone.value}
Target Audience: {config.target_audience}

Focus on:
- Maximum listener retention and engagement
- Natural conversation flow and authenticity
- Strategic monetization integration
- Cross-platform content optimization
- Community building and audience development
- Podcast algorithm optimization for discovery"""

    def _build_user_prompt(self, config: PodcastScriptPrompt, structure: Dict) -> str:
        """Build user prompt with specific requirements"""
        host_info = f"\nHost Information: {config.host_info}" if config.host_info else ""
        guest_info = f"\nGuest Information: {config.guest_info}" if config.guest_info else ""
        talking_points = f"\nMain Talking Points: {', '.join(config.main_talking_points)}" if config.main_talking_points else ""
        research_sources = f"\nResearch Sources: {', '.join(config.research_sources)}" if config.research_sources else ""
        show_context = f"\nShow Description: {config.show_description}" if config.show_description else ""
        series_context = f"\nSeries Context: {config.series_context}" if config.series_context else ""
        
        return f"""{structure['intro']}

Topic: {config.topic}
Duration: {config.duration_minutes} minutes
Target Audience: {config.target_audience}{host_info}{guest_info}{show_context}{series_context}{talking_points}{research_sources}

Podcast Structure:
{structure['structure']}

Content Requirements:
{structure['requirements']}

Creator Economy Optimization:
- Design for maximum listener retention and engagement
- Include natural sponsor integration opportunities
- Create shareable audio moments and quotable segments
- Build host authority and expertise demonstration
- Include strategic audience interaction points
- Optimize for podcast platform algorithms and discovery
- Design content for cross-platform repurposing (video, social clips, blog posts)"""

    def _build_format_instructions(self, config: PodcastScriptPrompt) -> str:
        """Build format-specific instructions"""
        duration_minutes = config.duration_minutes
        
        format_guidance = {
            PodcastFormat.INTERVIEW: f"Interview format with natural conversation flow, {duration_minutes} minutes",
            PodcastFormat.SOLO_MONOLOGUE: f"Solo presentation with engaging monologue structure, {duration_minutes} minutes",
            PodcastFormat.PANEL_DISCUSSION: f"Multi-person panel with balanced participation, {duration_minutes} minutes",
            PodcastFormat.NARRATIVE_STORYTELLING: f"Story-driven narrative with compelling arc, {duration_minutes} minutes",
            PodcastFormat.EDUCATIONAL: f"Educational content with clear learning objectives, {duration_minutes} minutes",
            PodcastFormat.NEWS_COMMENTARY: f"News analysis and commentary format, {duration_minutes} minutes",
            PodcastFormat.COMEDY: f"Comedy podcast with humor and entertainment focus, {duration_minutes} minutes"
        }
        
        return f"""
FORMAT INSTRUCTIONS:

{format_guidance.get(config.format, f'Standard podcast format, {duration_minutes} minutes')}

Script Structure:
- Include detailed speaker cues and timing markers
- Specify music and sound effect placement
- Include chapter markers for platform optimization
- Mark sponsor integration points naturally
- Include audience engagement triggers
- Specify energy level and pacing changes

Technical Requirements:
- Format for professional audio production
- Include audio engineering notes and cues
- Specify microphone and recording requirements
- Include post-production editing guidelines
- Mark potential audio clip extraction points
- Consider accessibility with transcript-friendly formatting"""

    def _build_engagement_optimization(self, config: PodcastScriptPrompt) -> str:
        """Build engagement optimization instructions"""
        engagement_elements = f"Include these engagement elements: {', '.join(config.engagement_elements)}" if config.engagement_elements else ""
        audience_interaction = f"Audience interaction strategy: {config.audience_interaction}" if config.audience_interaction else ""
        
        return f"""
ENGAGEMENT OPTIMIZATION:

Listener Retention Strategy:
- Hook listeners within first 30 seconds with compelling preview
- Use storytelling techniques and narrative arcs
- Include pattern interrupts and energy changes every 5-7 minutes
- Create curiosity gaps and cliffhangers throughout
- Use personal anecdotes and relatable examples

Audio Engagement Techniques:
- Vary vocal tone, pace, and energy levels
- Use strategic pauses and emphasis for impact
- Include sound effects and music transitions
- Create intimate, conversational atmosphere
- Use direct listener address ("you," personal pronouns)

Platform Algorithm Optimization:
- Optimize for completion rate and listen-through
- Include engagement triggers that encourage platform interaction
- Create shareable moments and quotable segments
- Use trending topics and relevant keywords naturally
- Design for repeat listening and subscriber retention

Interactive Elements:
{engagement_elements}
{audience_interaction}
- Include calls for listener feedback and comments
- Create opportunities for audience questions and participation
- Use polls, Q&A segments, and community building
- Encourage social media sharing and discussion"""

    def _build_monetization_guidance(self, config: PodcastScriptPrompt) -> str:
        """Build monetization guidance"""
        strategy = config.monetization_strategy or "Multi-stream creator monetization"
        sponsors = f"Sponsor segments: {', '.join(config.sponsor_segments)}" if config.sponsor_segments else "Natural sponsor integration opportunities"
        
        return f"""
MONETIZATION GUIDANCE:

Strategy: {strategy}

Sponsor Integration:
{sponsors}
- Include natural product mentions and testimonials
- Create authentic sponsor content that adds value
- Use host-read ads with personal endorsements
- Include mid-roll and post-roll advertising opportunities
- Balance sponsor content with editorial content

Direct Monetization:
- Include premium content teasers for subscription models
- Create exclusive content opportunities for supporters
- Include merchandise mentions and product placement
- Use affiliate marketing integration naturally
- Build toward live event and workshop opportunities

Platform Monetization:
- Optimize for platform-specific revenue programs
- Include features that trigger platform monetization
- Create content eligible for premium tiers
- Design for cross-platform revenue optimization
- Build audience for live streaming and real-time support

Call-to-Action Strategy:
{config.call_to_action or '- Include organic CTAs for newsletter, social media, and community'}
- Use strategic placement throughout episode
- Create urgency and value proposition
- Include multiple CTA types and opportunities
- Track and optimize CTA performance"""

    def _build_audio_production_notes(self, config: PodcastScriptPrompt) -> str:
        """Build audio production and technical notes"""
        return f"""
AUDIO PRODUCTION NOTES:

Recording Setup:
- Use professional-grade microphones and audio interface
- Record in acoustically treated environment
- Maintain consistent audio levels throughout
- Use separate tracks for each speaker
- Include room tone for editing consistency

Music and Sound Design:
- Include intro/outro music with proper licensing
- Use transition music between segments
- Add sound effects for storytelling and emphasis
- Include background music where appropriate
- Ensure all audio elements support the narrative

Post-Production Guidelines:
- Edit for natural conversation flow and pacing
- Remove filler words and long pauses strategically
- Balance audio levels between speakers
- Add chapter markers for platform optimization
- Create multiple audio formats for distribution

Quality Standards:
- Maintain broadcast-quality audio throughout
- Use noise reduction and audio enhancement
- Ensure consistent volume and dynamic range
- Include backup recording methods
- Plan for live vs. edited podcast distribution"""

    def _build_platform_optimization(self, config: PodcastScriptPrompt) -> str:
        """Build platform-specific optimization"""
        if not config.platform_distribution:
            return "PLATFORM OPTIMIZATION: Multi-platform podcast distribution optimization"
            
        platforms_info = []
        for platform in config.platform_distribution:
            platform_lower = platform.lower()
            specs = self.platform_specs.get(platform_lower, {})
            if specs:
                platforms_info.append(f"- {platform}: {', '.join(specs.get('features', []))}")
        
        return f"""
PLATFORM OPTIMIZATION:

Target Platforms: {', '.join(config.platform_distribution)}

Platform-Specific Features:
{chr(10).join(platforms_info) if platforms_info else '- Optimize for general podcast platform features'}

Content Optimization:
- Create chapter markers for enhanced navigation
- Include detailed show notes and timestamps
- Use platform-specific keywords and tags
- Optimize episode titles and descriptions
- Include relevant hashtags and categories

Discovery Optimization:
- Use trending topics and seasonal content
- Include guest name recognition and authority
- Create searchable content themes and topics
- Use keyword-rich episode titles and descriptions
- Build cross-platform promotional content

Cross-Platform Strategy:
- Create video versions for YouTube and Spotify
- Extract audio clips for social media promotion
- Build blog post content from episode transcripts
- Create Instagram Stories and TikTok content
- Develop email newsletter content from episodes"""

    def _build_seo_optimization(self, config: PodcastScriptPrompt) -> str:
        """Build SEO optimization instructions"""
        if not config.seo_keywords:
            return "SEO OPTIMIZATION: Focus on natural keyword integration and searchable podcast themes."
            
        return f"""
SEO OPTIMIZATION:

Target Keywords: {', '.join(config.seo_keywords)}

Keyword Integration:
- Include primary keywords in episode title and opening
- Use keywords naturally in conversation and content
- Include semantic variations throughout episode
- Use keywords in chapter titles and timestamps
- Include keywords in show notes and descriptions

Podcast SEO Strategy:
- Create searchable episode titles with target keywords
- Use long-tail keywords for niche topic discovery
- Include guest names and credentials for search value
- Use trending topics and current events keywords
- Create evergreen content with lasting search value

Discoverability Enhancement:
- Address common questions and search queries
- Include industry terminology and jargon appropriately
- Use location-based keywords where relevant
- Include brand names and product mentions strategically
- Create content that answers specific listener problems"""

    def _combine_prompt_components(self, components: Dict[str, str]) -> str:
        """Combine all prompt components into final prompt"""
        return f"""{components['system_prompt']}

{components['user_prompt']}

{components['format_instructions']}

{components['engagement_optimization']}

{components['monetization_guidance']}

{components['audio_production_notes']}

{components['platform_optimization']}

{components['seo_optimization']}

Now create the complete podcast script following all these guidelines. Include speaker cues, timing markers, music/sound cues, chapter markers, and engagement optimization throughout. Format for professional podcast production."""

    def _generate_metadata(self, config: PodcastScriptPrompt) -> Dict[str, Any]:
        """Generate metadata for the prompt"""
        return {
            "template_version": self.template_version,
            "format": config.format.value,
            "length": config.length.value,
            "tone": config.tone.value,
            "duration_minutes": config.duration_minutes,
            "target_audience": config.target_audience,
            "episode_number": config.episode_number,
            "season_number": config.season_number,
            "estimated_words": self._estimate_word_count(config.duration_minutes),
            "estimated_segments": self._estimate_segment_count(config.duration_minutes, config.format),
            "seo_keyword_count": len(config.seo_keywords),
            "engagement_elements_count": len(config.engagement_elements),
            "sponsor_segments_count": len(config.sponsor_segments),
            "platform_count": len(config.platform_distribution),
            "monetization_enabled": bool(config.monetization_strategy or config.sponsor_segments),
            "creation_timestamp": datetime.now().isoformat(),
            "creator_economy_optimized": True
        }

    def _calculate_optimization_score(self, config: PodcastScriptPrompt) -> float:
        """Calculate optimization score based on configuration"""
        score = 0.5  # Base score
        
        # Add points for configuration completeness
        if config.seo_keywords:
            score += 0.1
        if config.engagement_elements:
            score += 0.1
        if config.monetization_strategy:
            score += 0.1
        if config.sponsor_segments:
            score += 0.1
        if config.platform_distribution:
            score += 0.1
        if config.main_talking_points:
            score += 0.05
        if config.research_sources:
            score += 0.05
        
        return min(score, 1.0)

    def _estimate_engagement_potential(self, config: PodcastScriptPrompt) -> str:
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

    def _estimate_monetization_potential(self, config: PodcastScriptPrompt) -> str:
        """Estimate monetization potential"""
        if config.monetization_strategy and config.sponsor_segments and config.platform_distribution:
            return "High"
        elif (config.monetization_strategy or config.sponsor_segments) and config.platform_distribution:
            return "Medium-High"
        elif config.monetization_strategy or config.sponsor_segments or config.platform_distribution:
            return "Medium"
        else:
            return "Low"

    def _generate_distribution_strategy(self, config: PodcastScriptPrompt) -> Dict[str, Any]:
        """Generate platform distribution strategy"""
        if not config.platform_distribution:
            return {"strategy": "Multi-platform distribution recommended"}
            
        strategy = {
            "primary_platforms": config.platform_distribution,
            "content_adaptations": [],
            "cross_promotion": []
        }
        
        for platform in config.platform_distribution:
            platform_lower = platform.lower()
            if platform_lower == "youtube":
                strategy["content_adaptations"].append("Create video version with visual elements")
                strategy["cross_promotion"].append("Extract clips for YouTube Shorts")
            elif platform_lower == "spotify":
                strategy["content_adaptations"].append("Include Spotify-specific features like polls")
                strategy["cross_promotion"].append("Create Spotify-exclusive bonus content")
            elif platform_lower == "apple_podcasts":
                strategy["content_adaptations"].append("Optimize for Apple Podcasts search")
                strategy["cross_promotion"].append("Create Apple Podcasts exclusive episodes")
        
        return strategy

    def _estimate_word_count(self, duration_minutes: float) -> int:
        """Estimate word count for script based on duration"""
        # Average speaking rate: 140-180 words per minute for podcasts
        return int(duration_minutes * 160)

    def _estimate_segment_count(self, duration_minutes: float, format: PodcastFormat) -> int:
        """Estimate segment count based on duration and format"""
        if format == PodcastFormat.NEWS_COMMENTARY:
            return max(1, int(duration_minutes / 5))  # 5-minute segments
        elif format == PodcastFormat.INTERVIEW:
            return max(1, int(duration_minutes / 10))  # 10-minute segments
        else:
            return max(1, int(duration_minutes / 8))  # 8-minute average segments

    # Format-specific structures
    def _get_interview_structure(self) -> Dict:
        return {
            "intro": "Create an engaging interview podcast script with natural conversation flow and strategic questioning.",
            "structure": [
                "- Pre-interview setup and technical check",
                "- Show introduction and guest presentation",
                "- Guest introduction and background",
                "- Main interview segments with natural transitions", 
                "- Rapid-fire or personal questions segment",
                "- Guest promotion and contact information",
                "- Show conclusion and call-to-action"
            ],
            "requirements": [
                "- Prepare thoughtful, open-ended questions",
                "- Include follow-up questions and conversation development",
                "- Allow for natural conversation flow and spontaneity",
                "- Include guest expertise showcase and value delivery",
                "- End with clear guest promotion and next steps"
            ]
        }

    def _get_solo_structure(self) -> Dict:
        return {
            "intro": "Create an engaging solo podcast script with compelling monologue and audience connection.",
            "structure": [
                "- Personal opening and audience connection",
                "- Topic introduction and episode preview",
                "- Main content delivery with personal insights",
                "- Stories, examples, and practical applications",
                "- Key takeaways and actionable advice",
                "- Audience engagement and community building",
                "- Strong conclusion with call-to-action"
            ],
            "requirements": [
                "- Maintain conversational tone throughout",
                "- Include personal stories and experiences",
                "- Use varied vocal energy and pacing",
                "- Include direct audience address and connection",
                "- Provide actionable value and insights"
            ]
        }

    def _get_panel_structure(self) -> Dict:
        return {
            "intro": "Create a dynamic panel discussion script with balanced participation and engaging debate.",
            "structure": [
                "- Panel introduction and participant backgrounds",
                "- Topic introduction and context setting",
                "- Structured discussion with moderated segments",
                "- Open debate and diverse perspective sharing",
                "- Audience Q&A or interaction segment",
                "- Panel member final thoughts and insights",
                "- Contact information and follow-up resources"
            ],
            "requirements": [
                "- Ensure balanced speaking time for all participants",
                "- Include diverse perspectives and viewpoints",
                "- Use moderation to maintain focus and flow",
                "- Encourage respectful debate and discussion",
                "- Include clear participant identification for listeners"
            ]
        }

    def _get_narrative_structure(self) -> Dict:
        return {
            "intro": "Create a compelling narrative podcast script with strong storytelling and emotional engagement.",
            "structure": [
                "- Compelling opening hook and story setup",
                "- Character introduction and context building",
                "- Story development with rising action",
                "- Climax and key revelations or turning points",
                "- Resolution and story conclusion",
                "- Reflection and broader implications",
                "- Audience engagement and series connection"
            ],
            "requirements": [
                "- Use strong narrative arc and storytelling techniques",
                "- Include vivid descriptions and scene setting",
                "- Create emotional connection with characters and events",
                "- Use music and sound effects to enhance storytelling",
                "- Include cliffhangers for series continuation"
            ]
        }

    def _get_educational_structure(self) -> Dict:
        return {
            "intro": "Create an educational podcast script that teaches effectively while maintaining engagement.",
            "structure": [
                "- Learning objectives and episode overview",
                "- Background information and context",
                "- Main educational content with clear explanations",
                "- Examples, case studies, and practical applications",
                "- Knowledge check and comprehension questions",
                "- Summary of key learning points",
                "- Additional resources and next steps"
            ],
            "requirements": [
                "- Present complex information in digestible segments",
                "- Use analogies and examples for clarity",
                "- Include interactive elements and questions",
                "- Provide actionable takeaways and applications",
                "- Reference credible sources and research"
            ]
        }

    def _get_news_structure(self) -> Dict:
        return {
            "intro": "Create a news commentary podcast script with current events analysis and expert perspective.",
            "structure": [
                "- News headlines and episode overview",
                "- Main story analysis with context and background",
                "- Expert commentary and perspective",
                "- Implications and future outlook",
                "- Related stories and connections",
                "- Audience opinion and community discussion",
                "- Conclusion and upcoming coverage preview"
            ],
            "requirements": [
                "- Provide factual, well-researched information",
                "- Include multiple perspectives and balanced analysis",
                "- Use credible sources and fact-checking",
                "- Maintain objectivity while offering insight",
                "- Include current events context and background"
            ]
        }

    def _get_comedy_structure(self) -> Dict:
        return {
            "intro": "Create a comedy podcast script with humor, entertainment, and audience engagement.",
            "structure": [
                "- Humorous opening and mood setting",
                "- Topic introduction with comedic angle",
                "- Main comedy segments with varied humor styles",
                "- Interactive elements and audience participation",
                "- Guest comedy or community contributions",
                "- Running gags and callback references",
                "- Strong comedic conclusion and audience engagement"
            ],
            "requirements": [
                "- Maintain appropriate humor for target audience",
                "- Use varied comedy styles and techniques",
                "- Include timing and delivery instructions",
                "- Create memorable moments and quotable content",
                "- Balance humor with respect and inclusivity"
            ]
        }

    def _get_true_crime_structure(self) -> Dict:
        return {
            "intro": "Create a true crime podcast script with compelling investigation and respectful storytelling.",
            "structure": [
                "- Case introduction and overview",
                "- Background information and context",
                "- Chronological event presentation",
                "- Investigation details and evidence",
                "- Analysis and expert commentary",
                "- Current status and updates",
                "- Respectful conclusion and victim remembrance"
            ],
            "requirements": [
                "- Handle sensitive material with respect and dignity",
                "- Use factual, well-researched information",
                "- Include trigger warnings where appropriate",
                "- Focus on victims and justice rather than sensationalism",
                "- Cite credible sources and maintain accuracy"
            ]
        }

    def _get_business_structure(self) -> Dict:
        return {
            "intro": "Create a business podcast script with actionable insights and professional value.",
            "structure": [
                "- Business topic introduction and relevance",
                "- Market context and current trends",
                "- Strategic insights and analysis",
                "- Case studies and real-world examples",
                "- Actionable advice and implementation steps",
                "- Expert interviews or guest perspectives",
                "- Key takeaways and business applications"
            ],
            "requirements": [
                "- Provide actionable business insights and strategies",
                "- Include current market data and trends",
                "- Use credible business sources and research",
                "- Offer practical implementation advice",
                "- Build authority and thought leadership"
            ]
        }

    def _get_default_structure(self) -> Dict:
        return {
            "intro": "Create an engaging podcast script optimized for your specified format and audience.",
            "structure": [
                "- Compelling opening and topic introduction",
                "- Main content delivery with clear structure",
                "- Engaging segments with variety and pacing",
                "- Interactive elements and audience connection",
                "- Strong conclusion with clear value delivery",
                "- Call-to-action and community building"
            ],
            "requirements": [
                "- Maintain listener engagement throughout",
                "- Include clear value proposition and delivery",
                "- Use appropriate pacing for format and length",
                "- Include strategic calls-to-action",
                "- Optimize for target audience and platform"
            ]
        }

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = PodcastScriptPrompt(
        format=PodcastFormat.INTERVIEW,
        length=PodcastLength.STANDARD,
        tone=PodcastTone.CONVERSATIONAL,
        topic="Building a Million-Dollar Creator Business: From Zero to Success",
        duration_minutes=45.0,
        target_audience="aspiring entrepreneurs and content creators",
        host_info="Experienced business podcast host with creator economy expertise",
        guest_info="Successful creator who built 7-figure business from social media",
        show_description="Weekly interviews with successful creators and entrepreneurs",
        episode_number=42,
        season_number=2,
        main_talking_points=["creator business models", "scaling strategies", "monetization techniques", "audience building"],
        research_sources=["guest's social media analytics", "industry reports", "creator economy studies"],
        call_to_action="Subscribe for weekly creator interviews and get our free Creator Business Toolkit",
        sponsor_segments=["productivity software", "creator tools platform"],
        monetization_strategy="Combination of sponsorships, affiliate marketing, and premium content",
        seo_keywords=["creator economy", "entrepreneur interview", "business building"],
        engagement_elements=["audience questions", "rapid-fire round", "personal stories"],
        audience_interaction="Live Q&A submission through social media",
        series_context="Part of Creator Success Series featuring top entrepreneurs",
        platform_distribution=["spotify", "apple_podcasts", "youtube", "google_podcasts"]
    )
    
    # Generate prompt
    template = PodcastScriptTemplate()
    result = template.generate_prompt(config)
    
    print("=== PODCAST SCRIPT TEMPLATE EXAMPLE ===")
    print(f"Optimization Score: {result['optimization_score']:.2f}")
    print(f"Engagement Potential: {result['engagement_potential']}")
    print(f"Monetization Potential: {result['monetization_potential']}")
    print(f"Estimated Words: {result['metadata']['estimated_words']}")
    print(f"Platform Distribution: {result['platform_distribution_strategy']}")
    print("\n" + "="*50)
    print(result['prompt'])