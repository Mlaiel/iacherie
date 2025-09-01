"""Advanced Content Creator Prompts System
Professional prompts for multi-format content creators (musicians, bloggers, photographers, influencers, comedians)

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de)
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted under German and International copyright law.
"""
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ContentCreatorType(Enum):
    """Content creator types supported by the platform"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    YOUTUBER = "youtuber"
    ARTIST = "artist"

class ContentFormat(Enum):
    """Content formats supported"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"

class PromptCategory(Enum):
    """Prompt categories for content creation"""
    CREATION = "creation"
    PROTECTION = "protection"
    OPTIMIZATION = "optimization"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"

@dataclass
class PromptContext:
    """Context for prompt generation"""
    creator_type: ContentCreatorType
    content_format: ContentFormat
    category: PromptCategory
    user_preferences: Dict[str, Any]
    platform_requirements: Dict[str, Any]
    market_trends: Dict[str, Any]

class ContentCreatorPrompts:
    """Professional Content Creator Prompts System"""
    
    def __init__(self):
        """Initialize the content creator prompts system"""
        self.prompts_cache = {}
        self.personalization_engine = PersonalizationEngine()
        self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> None:
        """Load and initialize prompt templates"""
        self.base_prompts = {
            ContentCreatorType.MUSICIAN: {
                PromptCategory.CREATION: [
                    {
                        "id": "music_composition_ai",
                        "template": """
                        As an advanced AI music composition assistant, help create a {genre} track with the following specifications:
                        
                        Musical Elements:
                        - Genre: {genre}
                        - Tempo: {tempo} BPM
                        - Key: {key}
                        - Mood: {mood}
                        - Duration: {duration}
                        
                        Creative Requirements:
                        - Instrument arrangement: {instruments}
                        - Song structure: {structure}
                        - Lyrical theme: {theme}
                        - Target audience: {audience}
                        
                        Technical Specifications:
                        - Audio quality: Professional studio quality
                        - Format: WAV, 24-bit, 48kHz
                        - Mixing style: {mixing_style}
                        - Mastering requirements: Spotify-ready loudness (-14 LUFS)
                        
                        Copyright Protection:
                        - Generate unique fingerprint for copyright protection
                        - Ensure originality score > 95%
                        - Create metadata for rights management
                        
                        Output Requirements:
                        1. Detailed composition plan
                        2. Chord progressions and melody lines
                        3. Arrangement suggestions
                        4. Production timeline
                        5. Copyright protection strategy
                        """,
                        "variables": ["genre", "tempo", "key", "mood", "duration", "instruments", "structure", "theme", "audience", "mixing_style"],
                        "quality_score": 95
                    },
                    {
                        "id": "lyrics_generation_pro",
                        "template": """
                        Create professional song lyrics with the following parameters:
                        
                        Song Details:
                        - Title: {title}
                        - Genre: {genre}
                        - Theme: {theme}
                        - Emotion: {emotion}
                        - Target demographic: {demographic}
                        
                        Lyrical Requirements:
                        - Verse count: {verse_count}
                        - Chorus structure: {chorus_structure}
                        - Bridge inclusion: {bridge}
                        - Language: {language}
                        - Rhyme scheme: {rhyme_scheme}
                        
                        Content Guidelines:
                        - Message: {message}
                        - Storytelling style: {story_style}
                        - Cultural references: {cultural_refs}
                        - Avoid: {avoid_content}
                        
                        Technical Specifications:
                        - Syllable count optimization for melody
                        - Vocal range considerations: {vocal_range}
                        - Rhythm pattern matching
                        - Hook potential analysis
                        
                        Output Format:
                        1. Complete lyrics with structure markers
                        2. Phonetic annotations for pronunciation
                        3. Emotional delivery notes
                        4. Alternative word suggestions
                        5. Copyright clearance recommendations
                        """,
                        "variables": ["title", "genre", "theme", "emotion", "demographic", "verse_count", "chorus_structure", "bridge", "language", "rhyme_scheme", "message", "story_style", "cultural_refs", "avoid_content", "vocal_range"],
                        "quality_score": 92
                    }
                ],
                PromptCategory.PROTECTION: [
                    {
                        "id": "audio_fingerprinting",
                        "template": """
                        Generate advanced audio fingerprinting protection for musical content:
                        
                        Audio Analysis:
                        - File: {audio_file}
                        - Duration: {duration}
                        - Sample rate: {sample_rate}
                        - Bit depth: {bit_depth}
                        - Channels: {channels}
                        
                        Fingerprinting Requirements:
                        - Extract spectral features
                        - Generate chromaprint signature
                        - Create perceptual hash
                        - Identify unique audio DNA
                        - Generate protection watermark
                        
                        Protection Level: {protection_level}
                        - Basic: Standard fingerprinting
                        - Advanced: Multi-layer protection
                        - Enterprise: Blockchain integration
                        
                        Monitoring Setup:
                        - Platform coverage: {platforms}
                        - Detection sensitivity: {sensitivity}
                        - Alert frequency: {alert_frequency}
                        - Action on detection: {action_type}
                        
                        Legal Framework:
                        - Copyright registration: {copyright_reg}
                        - DMCA preparation: {dmca_ready}
                        - Rights management: {rights_mgmt}
                        - Revenue tracking: {revenue_track}
                        
                        Output Requirements:
                        1. Unique audio fingerprint
                        2. Protection certificate
                        3. Monitoring configuration
                        4. Legal documentation template
                        5. Revenue tracking setup
                        """,
                        "variables": ["audio_file", "duration", "sample_rate", "bit_depth", "channels", "protection_level", "platforms", "sensitivity", "alert_frequency", "action_type", "copyright_reg", "dmca_ready", "rights_mgmt", "revenue_track"],
                        "quality_score": 98
                    }
                ]
            },
            
            ContentCreatorType.BLOGGER: {
                PromptCategory.CREATION: [
                    {
                        "id": "blog_content_ai",
                        "template": """
                        Create engaging blog content with professional SEO optimization:
                        
                        Content Specifications:
                        - Topic: {topic}
                        - Target audience: {audience}
                        - Content type: {content_type}
                        - Word count: {word_count}
                        - Tone: {tone}
                        
                        SEO Requirements:
                        - Primary keyword: {primary_keyword}
                        - Secondary keywords: {secondary_keywords}
                        - Meta description: {meta_desc}
                        - Title optimization: {title_seo}
                        - Internal linking strategy: {internal_links}
                        
                        Content Structure:
                        - Introduction hook: {intro_style}
                        - Main sections: {sections}
                        - Conclusion call-to-action: {cta}
                        - Visual elements: {visuals}
                        
                        Engagement Features:
                        - Interactive elements: {interactive}
                        - Social sharing optimization: {social_opt}
                        - Comment engagement strategy: {comment_strategy}
                        - Newsletter integration: {newsletter}
                        
                        Content Protection:
                        - Plagiarism prevention: {plagiarism_protection}
                        - Content fingerprinting: {content_fingerprint}
                        - Copyright notice: {copyright_notice}
                        - Attribution requirements: {attribution}
                        
                        Output Requirements:
                        1. Complete blog post with HTML structure
                        2. SEO metadata package
                        3. Social media excerpts
                        4. Content protection setup
                        5. Performance tracking configuration
                        """,
                        "variables": ["topic", "audience", "content_type", "word_count", "tone", "primary_keyword", "secondary_keywords", "meta_desc", "title_seo", "internal_links", "intro_style", "sections", "cta", "visuals", "interactive", "social_opt", "comment_strategy", "newsletter", "plagiarism_protection", "content_fingerprint", "copyright_notice", "attribution"],
                        "quality_score": 94
                    }
                ]
            },
            
            ContentCreatorType.PHOTOGRAPHER: {
                PromptCategory.CREATION: [
                    {
                        "id": "photo_optimization_ai",
                        "template": """
                        Professional photo optimization and protection system:
                        
                        Image Analysis:
                        - File format: {format}
                        - Resolution: {resolution}
                        - Color space: {color_space}
                        - EXIF data: {exif_data}
                        - File size: {file_size}
                        
                        Enhancement Requirements:
                        - Lighting optimization: {lighting}
                        - Color correction: {color_correction}
                        - Sharpness enhancement: {sharpness}
                        - Noise reduction: {noise_reduction}
                        - Style transfer: {style}
                        
                        Professional Standards:
                        - Print quality: {print_quality}
                        - Web optimization: {web_opt}
                        - Mobile compatibility: {mobile_opt}
                        - Social media formats: {social_formats}
                        
                        Protection System:
                        - Watermark generation: {watermark}
                        - Digital signature: {signature}
                        - IPTC metadata: {iptc_data}
                        - Rights management: {rights}
                        - Usage tracking: {tracking}
                        
                        Distribution Strategy:
                        - Portfolio platforms: {portfolio_platforms}
                        - Stock photography: {stock_sites}
                        - Social media: {social_media}
                        - Client delivery: {client_delivery}
                        
                        Output Requirements:
                        1. Optimized image variants
                        2. Protection implementation
                        3. Metadata package
                        4. Distribution configuration
                        5. Revenue tracking setup
                        """,
                        "variables": ["format", "resolution", "color_space", "exif_data", "file_size", "lighting", "color_correction", "sharpness", "noise_reduction", "style", "print_quality", "web_opt", "mobile_opt", "social_formats", "watermark", "signature", "iptc_data", "rights", "tracking", "portfolio_platforms", "stock_sites", "social_media", "client_delivery"],
                        "quality_score": 96
                    }
                ]
            }
        }
    
    def generate_prompt(self, context: PromptContext, custom_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a personalized prompt based on context"""
        try:
            # Get base prompt template
            base_prompts = self.base_prompts.get(context.creator_type, {})
            category_prompts = base_prompts.get(context.category, [])
            
            if not category_prompts:
                logger.warning(f"No prompts found for {context.creator_type} - {context.category}")
                return self._generate_fallback_prompt(context)
            
            # Select best prompt based on context
            selected_prompt = self._select_optimal_prompt(category_prompts, context)
            
            # Personalize prompt
            personalized_prompt = self.personalization_engine.personalize(
                selected_prompt, context, custom_params
            )
            
            # Add quality metrics
            personalized_prompt["generation_timestamp"] = datetime.utcnow().isoformat()
            personalized_prompt["context_hash"] = self._generate_context_hash(context)
            
            return personalized_prompt
            
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            return self._generate_fallback_prompt(context)
    
    def _select_optimal_prompt(self, prompts: List[Dict], context: PromptContext) -> Dict:
        """Select the optimal prompt based on context and quality scores"""
        # Sort by quality score and relevance
        scored_prompts = []
        for prompt in prompts:
            relevance_score = self._calculate_relevance_score(prompt, context)
            total_score = prompt.get("quality_score", 0) * 0.7 + relevance_score * 0.3
            scored_prompts.append((total_score, prompt))
        
        scored_prompts.sort(reverse=True)
        return scored_prompts[0][1] if scored_prompts else prompts[0]
    
    def _calculate_relevance_score(self, prompt: Dict, context: PromptContext) -> float:
        """Calculate relevance score based on context matching"""
        # Implementation for relevance scoring
        base_score = 70.0
        
        # Add scoring logic based on context parameters
        if context.content_format.value in prompt.get("template", ""):
            base_score += 10.0
        
        if context.user_preferences:
            preference_matches = sum(1 for pref in context.user_preferences 
                                   if pref in prompt.get("template", ""))
            base_score += min(preference_matches * 5.0, 20.0)
        
        return min(base_score, 100.0)
    
    def _generate_fallback_prompt(self, context: PromptContext) -> Dict[str, Any]:
        """Generate fallback prompt when no specific prompt is available"""
        return {
            "id": "fallback_generic",
            "template": f"""
            Create professional {context.content_format.value} content for {context.creator_type.value}:
            
            Content Requirements:
            - Format: {context.content_format.value}
            - Creator type: {context.creator_type.value}
            - Category: {context.category.value}
            
            Please provide:
            1. Content creation guidelines
            2. Quality standards
            3. Protection recommendations
            4. Distribution strategy
            5. Performance metrics
            """,
            "variables": [],
            "quality_score": 60,
            "is_fallback": True
        }
    
    def _generate_context_hash(self, context: PromptContext) -> str:
        """Generate hash for context caching"""
        import hashlib
        context_string = f"{context.creator_type.value}_{context.content_format.value}_{context.category.value}"
        return hashlib.md5(context_string.encode()).hexdigest()[:12]

class PersonalizationEngine:
    """Advanced personalization engine for prompts"""
    
    def __init__(self):
        """Initialize personalization engine"""
        self.user_models = {}
        self.learning_data = {}
    
    def personalize(self, prompt: Dict, context: PromptContext, custom_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Personalize prompt based on user context and preferences"""
        personalized = prompt.copy()
        
        # Apply user preferences
        if context.user_preferences:
            personalized = self._apply_user_preferences(personalized, context.user_preferences)
        
        # Apply platform requirements
        if context.platform_requirements:
            personalized = self._apply_platform_requirements(personalized, context.platform_requirements)
        
        # Apply market trends
        if context.market_trends:
            personalized = self._apply_market_trends(personalized, context.market_trends)
        
        # Apply custom parameters
        if custom_params:
            personalized = self._apply_custom_parameters(personalized, custom_params)
        
        return personalized
    
    def _apply_user_preferences(self, prompt: Dict, preferences: Dict) -> Dict:
        """Apply user preferences to prompt"""
        # Implementation for user preference application
        modified_prompt = prompt.copy()
        
        # Update template with preference-based modifications
        template = modified_prompt.get("template", "")
        for pref_key, pref_value in preferences.items():
            if f"{{{pref_key}}}" in template:
                template = template.replace(f"{{{pref_key}}}", str(pref_value))
        
        modified_prompt["template"] = template
        modified_prompt["applied_preferences"] = preferences
        
        return modified_prompt
    
    def _apply_platform_requirements(self, prompt: Dict, requirements: Dict) -> Dict:
        """Apply platform-specific requirements"""
        modified_prompt = prompt.copy()
        modified_prompt["platform_requirements"] = requirements
        
        # Modify template based on platform requirements
        if "max_length" in requirements:
            modified_prompt["max_length"] = requirements["max_length"]
        
        if "format_requirements" in requirements:
            modified_prompt["format_requirements"] = requirements["format_requirements"]
        
        return modified_prompt
    
    def _apply_market_trends(self, prompt: Dict, trends: Dict) -> Dict:
        """Apply current market trends to prompt"""
        modified_prompt = prompt.copy()
        modified_prompt["market_trends"] = trends
        
        # Integrate trending elements
        if "trending_keywords" in trends:
            template = modified_prompt.get("template", "")
            trending_section = f"\n\nTrending Elements:\n- Keywords: {', '.join(trends['trending_keywords'])}"
            modified_prompt["template"] = template + trending_section
        
        return modified_prompt
    
    def _apply_custom_parameters(self, prompt: Dict, custom_params: Dict) -> Dict:
        """Apply custom parameters to prompt"""
        modified_prompt = prompt.copy()
        modified_prompt["custom_parameters"] = custom_params
        
        # Replace template variables with custom values
        template = modified_prompt.get("template", "")
        for param_key, param_value in custom_params.items():
            template = template.replace(f"{{{param_key}}}", str(param_value))
        
        modified_prompt["template"] = template
        
        return modified_prompt

# Professional prompt templates registry
CONTENT_CREATOR_PROMPTS_REGISTRY = {
    "musician_creation": ContentCreatorPrompts(),
    "blogger_creation": ContentCreatorPrompts(),
    "photographer_creation": ContentCreatorPrompts(),
    "influencer_creation": ContentCreatorPrompts(),
    "comedian_creation": ContentCreatorPrompts()
}

def get_content_creator_prompts() -> ContentCreatorPrompts:
    """Get the main content creator prompts instance"""
    return ContentCreatorPrompts()

def create_prompt_context(
    creator_type: str,
    content_format: str,
    category: str,
    user_preferences: Optional[Dict] = None,
    platform_requirements: Optional[Dict] = None,
    market_trends: Optional[Dict] = None
) -> PromptContext:
    """Create a prompt context for content generation"""
    return PromptContext(
        creator_type=ContentCreatorType(creator_type),
        content_format=ContentFormat(content_format),
        category=PromptCategory(category),
        user_preferences=user_preferences or {},
        platform_requirements=platform_requirements or {},
        market_trends=market_trends or {}
    )
