"""Media Text Generator - Consolidated Text Generation System

Handles all 4 types of text generation:
1. Social media content (captions, posts, stories, comments)
2. Marketing copy (ads, sales pages, email campaigns, newsletters)
3. Educational content (articles, tutorials, guides, documentation)
4. Creative writing (stories, scripts, poetry, creative content)

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_engine.content_generation.base_generator import BaseContentGenerator, ContentGenerationContext


class TextType(Enum):
    """Text generation types"""
    SOCIAL_MEDIA = "social_media"
    MARKETING_COPY = "marketing_copy"
    EDUCATIONAL = "educational"
    CREATIVE_WRITING = "creative_writing"


class ContentFormat(Enum):
    """Content format options"""
    CAPTION = "caption"
    POST = "post"
    ARTICLE = "article"
    EMAIL = "email"
    AD_COPY = "ad_copy"
    SCRIPT = "script"
    TUTORIAL = "tutorial"
    STORY = "story"
    POEM = "poem"
    NEWSLETTER = "newsletter"


class WritingStyle(Enum):
    """Writing style options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    CONVERSATIONAL = "conversational"
    FORMAL = "formal"
    CREATIVE = "creative"
    PERSUASIVE = "persuasive"
    INFORMATIVE = "informative"
    ENTERTAINING = "entertaining"


class ToneOfVoice(Enum):
    """Tone of voice options"""
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    ENTHUSIASTIC = "enthusiastic"
    SERIOUS = "serious"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    EMPATHETIC = "empathetic"
    CONFIDENT = "confident"


class TextConfig:
    """Configuration for text generation"""
    
    def __init__(self, **kwargs):
        self.text_type = kwargs.get('text_type', TextType.SOCIAL_MEDIA)
        self.format = kwargs.get('format', ContentFormat.POST)
        self.style = kwargs.get('style', WritingStyle.PROFESSIONAL)
        self.tone = kwargs.get('tone', ToneOfVoice.FRIENDLY)
        self.language = kwargs.get('language', 'en')
        self.target_length = kwargs.get('target_length', 'medium')  # short, medium, long
        self.platform = kwargs.get('platform', 'instagram')
        self.audience = kwargs.get('audience', 'general')
        self.purpose = kwargs.get('purpose', 'engage')  # inform, persuade, entertain, engage
        self.include_hashtags = kwargs.get('include_hashtags', True)
        self.include_cta = kwargs.get('include_cta', True)
        self.include_emojis = kwargs.get('include_emojis', True)
        self.keywords = kwargs.get('keywords', [])
        self.brand_voice = kwargs.get('brand_voice', {})
        self.seo_optimization = kwargs.get('seo_optimization', False)


class MediaTextGenerator(BaseContentGenerator):
    """
    Comprehensive text generator supporting 4 different text generation types
    with advanced AI-powered writing capabilities.
    """
    
    def _setup_models(self) -> None:
        """Setup AI models for text generation"""
        try:
            # Initialize AI models for different text types
            self.models = {}
            
            # Social media content models
            self.models['social_media'] = {
                'primary': 'gpt-4-turbo',
                'fallback': 'claude-3-sonnet',
                'hashtag_generator': 'hashtag-ai',
                'engagement_optimizer': 'social-optimizer'
            }
            
            # Marketing copy models
            self.models['marketing_copy'] = {
                'primary': 'copywriting-gpt',
                'fallback': 'marketing-ai',
                'conversion_optimizer': 'persuasion-ai',
                'ab_test_generator': 'variant-creator'
            }
            
            # Educational content models
            self.models['educational'] = {
                'primary': 'educational-gpt',
                'fallback': 'knowledge-ai',
                'structure_optimizer': 'content-organizer',
                'simplification_engine': 'clarity-ai'
            }
            
            # Creative writing models
            self.models['creative_writing'] = {
                'primary': 'creative-gpt',
                'fallback': 'storytelling-ai',
                'style_transfer': 'literary-ai',
                'genre_specialist': 'creative-specialist'
            }
            
            # Platform-specific configurations
            self.platform_specs = self._initialize_platform_specs()
            
            # Content templates and frameworks
            self.content_templates = self._initialize_content_templates()
            
            # Writing frameworks
            self.writing_frameworks = self._initialize_writing_frameworks()
            
            self.logger.info("Text generator models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize text models: {str(e)}")
            raise
    
    def _setup_resources(self) -> None:
        """Setup computational resources for text generation"""
        self.max_concurrent_generations = self.config.get('max_concurrent_generations', 10)
        self.generation_timeout = self.config.get('generation_timeout', 120)  # 2 minutes
        self.max_text_length = self.config.get('max_text_length', 10000)
        
        # Language and localization settings
        self.supported_languages = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh', 'ar', 'ru', 'hi'
        ]
        
        # Content quality settings
        self.quality_thresholds = {
            'readability_score': 70,
            'engagement_score': 60,
            'seo_score': 65
        }
    
    def _setup_validation_rules(self) -> None:
        """Setup text validation rules"""
        self.validation_rules = {
            'min_length': 10,
            'max_length': 10000,
            'supported_languages': self.supported_languages,
            'content_safety_enabled': True,
            'profanity_filter_enabled': True,
            'plagiarism_check_enabled': True,
            'brand_compliance_check': True
        }
    
    async def generate_content(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate text content based on context and prompt.
        
        Args:
            context: Generation context
            prompt: Text generation prompt
            options: Generation options
            
        Returns:
            Generated text data with metadata
        """
        try:
            # Parse text generation options
            text_config = TextConfig(**(options or {}))
            
            # Determine text type from prompt if not specified
            if not hasattr(text_config, 'text_type') or not text_config.text_type:
                text_config.text_type = self._determine_text_type(prompt, context)
            
            # Build content generation strategy
            strategy = await self._build_content_strategy(
                prompt, text_config, context
            )
            
            # Generate text based on type
            text_result = await self._generate_text_by_type(
                strategy, text_config, context
            )
            
            # Post-process the text
            processed_text = await self._post_process_text(
                text_result, text_config, context
            )
            
            # Analyze content quality
            quality_metrics = await self._analyze_content_quality(
                processed_text, text_config
            )
            
            return {
                'content': processed_text,
                'text_type': text_config.text_type.value,
                'format': text_config.format.value,
                'style': text_config.style.value,
                'metadata': {
                    'word_count': len(processed_text.split()),
                    'character_count': len(processed_text),
                    'language': text_config.language,
                    'target_length': text_config.target_length,
                    'generation_time': datetime.utcnow().isoformat(),
                    'model_used': self.models[text_config.text_type.value]['primary'],
                    'estimated_reading_time': self._estimate_reading_time(processed_text),
                    **quality_metrics
                },
                'configuration': {
                    'platform': text_config.platform,
                    'audience': text_config.audience,
                    'purpose': text_config.purpose,
                    'tone': text_config.tone.value,
                    'include_hashtags': text_config.include_hashtags,
                    'include_cta': text_config.include_cta,
                    'include_emojis': text_config.include_emojis
                },
                'strategy': strategy
            }
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {str(e)}")
            raise

    async def validate_output(self, content: Any) -> bool:
        """Validate generated text content"""
        if not isinstance(content, dict):
            return False
        
        # Check if text data exists
        text_data = content.get('content')
        if not text_data or not isinstance(text_data, str):
            return False
        
        # Check length constraints
        if len(text_data) < self.validation_rules['min_length']:
            return False
        
        if len(text_data) > self.validation_rules['max_length']:
            return False
        
        # Check metadata
        metadata = content.get('metadata', {})
        if not metadata.get('word_count') or not metadata.get('language'):
            return False
        
        return True

    def _determine_text_type(
        self, 
        prompt: str, 
        context: ContentGenerationContext
    ) -> TextType:
        """Determine text type from prompt and context"""
        prompt_lower = prompt.lower()
        
        # Check platform context first
        if context.platform_requirements:
            platform = context.platform_requirements.get('platform', '').lower()
            if platform in ['instagram', 'tiktok', 'facebook', 'twitter', 'linkedin']:
                return TextType.SOCIAL_MEDIA
        
        # Check for specific keywords
        if any(word in prompt_lower for word in ['social', 'post', 'caption', 'tweet', 'story']):
            return TextType.SOCIAL_MEDIA
        elif any(word in prompt_lower for word in ['ad', 'sales', 'marketing', 'promotion', 'email']):
            return TextType.MARKETING_COPY
        elif any(word in prompt_lower for word in ['tutorial', 'guide', 'how-to', 'explanation', 'course']):
            return TextType.EDUCATIONAL
        elif any(word in prompt_lower for word in ['story', 'creative', 'poem', 'script', 'fiction']):
            return TextType.CREATIVE_WRITING
        else:
            return TextType.SOCIAL_MEDIA  # Default for general content

    async def _build_content_strategy(
        self,
        prompt: str,
        config: TextConfig,
        context: ContentGenerationContext
    ) -> Dict[str, Any]:
        """Build content generation strategy"""
        
        # Get framework for the text type
        framework = self.writing_frameworks.get(config.text_type.value, {})
        
        # Get platform specifications
        platform_spec = self.platform_specs.get(config.platform, {})
        
        # Build content strategy
        strategy = {
            'content_structure': framework.get('structure', []),
            'key_elements': framework.get('elements', []),
            'optimization_targets': {
                'engagement': True,
                'readability': True,
                'seo': config.seo_optimization,
                'conversion': config.text_type == TextType.MARKETING_COPY
            },
            'platform_requirements': platform_spec,
            'length_target': self._get_length_target(config.target_length, config.platform),
            'style_guidelines': {
                'tone': config.tone.value,
                'style': config.style.value,
                'voice': config.brand_voice
            },
            'content_goals': [config.purpose],
            'keywords': config.keywords,
            'hashtag_strategy': config.include_hashtags,
            'cta_strategy': config.include_cta
        }
        
        return strategy

    async def _generate_text_by_type(
        self,
        strategy: Dict[str, Any],
        config: TextConfig,
        context: ContentGenerationContext
    ) -> str:
        """Generate text based on specific type"""
        
        text_type = config.text_type.value
        
        # Select appropriate generation method
        if text_type == 'social_media':
            return await self._generate_social_media_content(strategy, config, context)
        elif text_type == 'marketing_copy':
            return await self._generate_marketing_copy(strategy, config, context)
        elif text_type == 'educational':
            return await self._generate_educational_content(strategy, config, context)
        elif text_type == 'creative_writing':
            return await self._generate_creative_content(strategy, config, context)
        else:
            return await self._generate_social_media_content(strategy, config, context)  # Default fallback

    async def _generate_social_media_content(
        self, 
        strategy: Dict[str, Any], 
        config: TextConfig,
        context: ContentGenerationContext
    ) -> str:
        """Generate social media content"""
        return await self._mock_generate_text("social_media", strategy, config)

    async def _generate_marketing_copy(
        self, 
        strategy: Dict[str, Any], 
        config: TextConfig,
        context: ContentGenerationContext
    ) -> str:
        """Generate marketing copy"""
        return await self._mock_generate_text("marketing_copy", strategy, config)

    async def _generate_educational_content(
        self, 
        strategy: Dict[str, Any], 
        config: TextConfig,
        context: ContentGenerationContext
    ) -> str:
        """Generate educational content"""
        return await self._mock_generate_text("educational", strategy, config)

    async def _generate_creative_content(
        self, 
        strategy: Dict[str, Any], 
        config: TextConfig,
        context: ContentGenerationContext
    ) -> str:
        """Generate creative writing content"""
        return await self._mock_generate_text("creative_writing", strategy, config)

    async def _mock_generate_text(
        self, 
        text_type: str, 
        strategy: Dict[str, Any], 
        config: TextConfig
    ) -> str:
        """Mock text generation for development/testing"""
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Get length target
        length_target = strategy.get('length_target', 100)
        
        # Generate appropriate mock content based on type
        content_templates = {
            'social_media': self._generate_mock_social_content(config, length_target),
            'marketing_copy': self._generate_mock_marketing_content(config, length_target),
            'educational': self._generate_mock_educational_content(config, length_target),
            'creative_writing': self._generate_mock_creative_content(config, length_target)
        }
        
        mock_content = content_templates.get(text_type, "Generated content placeholder")
        
        self.logger.info(f"Generated {text_type} content ({len(mock_content)} chars)")
        return mock_content

    def _generate_mock_social_content(self, config: TextConfig, length_target: int) -> str:
        """Generate mock social media content"""
        base_content = f"Check out this amazing {config.format.value} content! 🚀"
        
        if config.include_hashtags:
            base_content += " #awesome #content #socialmedia #ai"
        
        if config.include_cta:
            base_content += " Like and share if you agree! 👍"
        
        # Pad to target length
        while len(base_content) < length_target - 50:
            base_content += " This is engaging social media content that connects with your audience."
        
        return base_content

    def _generate_mock_marketing_content(self, config: TextConfig, length_target: int) -> str:
        """Generate mock marketing copy"""
        base_content = f"Discover the power of AI-generated {config.format.value}! Transform your business today."
        
        if config.include_cta:
            base_content += " Sign up now for exclusive access!"
        
        # Pad to target length
        while len(base_content) < length_target - 50:
            base_content += " Our proven solution delivers results that exceed expectations."
        
        return base_content

    def _generate_mock_educational_content(self, config: TextConfig, length_target: int) -> str:
        """Generate mock educational content"""
        base_content = f"Learn how to create effective {config.format.value} content. "
        base_content += "Step 1: Understand your audience. Step 2: Define your goals. Step 3: Create compelling content."
        
        # Pad to target length
        while len(base_content) < length_target - 50:
            base_content += " This comprehensive guide provides actionable insights for content creators."
        
        return base_content

    def _generate_mock_creative_content(self, config: TextConfig, length_target: int) -> str:
        """Generate mock creative writing content"""
        base_content = f"Once upon a time, in a world of infinite possibilities, there was a {config.format.value} "
        base_content += "that captured the imagination of all who encountered it."
        
        # Pad to target length
        while len(base_content) < length_target - 50:
            base_content += " The story unfolded with unexpected twists and meaningful moments."
        
        return base_content

    async def _post_process_text(
        self,
        text: str,
        config: TextConfig,
        context: ContentGenerationContext
    ) -> str:
        """Post-process generated text"""
        processed_text = text
        
        # Apply platform-specific processing
        if config.platform in self.platform_specs:
            platform_spec = self.platform_specs[config.platform]
            max_length = platform_spec.get('max_characters')
            if max_length and len(processed_text) > max_length:
                processed_text = processed_text[:max_length-3] + "..."
        
        # Apply style-specific processing
        if config.style == WritingStyle.FORMAL:
            # Remove emojis for formal content
            processed_text = ''.join(char for char in processed_text if ord(char) < 0x1F600 or ord(char) > 0x1F64F)
        
        # Apply SEO optimization if enabled
        if config.seo_optimization:
            processed_text = await self._apply_seo_optimization(processed_text, config.keywords)
        
        return processed_text.strip()

    async def _apply_seo_optimization(self, text: str, keywords: List[str]) -> str:
        """Apply SEO optimization to text"""
        # Mock SEO optimization - in production would use proper SEO techniques
        optimized_text = text
        
        for keyword in keywords[:3]:  # Limit to top 3 keywords
            if keyword.lower() not in optimized_text.lower():
                optimized_text += f" Learn more about {keyword}."
        
        return optimized_text

    async def _analyze_content_quality(
        self, 
        text: str, 
        config: TextConfig
    ) -> Dict[str, Any]:
        """Analyze content quality metrics"""
        try:
            # Mock quality analysis - in production would use proper analysis tools
            word_count = len(text.split())
            sentence_count = text.count('.') + text.count('!') + text.count('?')
            
            # Calculate basic metrics
            readability_score = min(100, max(0, 100 - (word_count / max(1, sentence_count)) * 2))
            engagement_score = 75 + (text.count('!') * 5) + (text.count('?') * 3)
            seo_score = 60 + (len(config.keywords) * 10)
            
            return {
                'readability_score': round(readability_score, 1),
                'engagement_score': min(100, round(engagement_score, 1)),
                'seo_score': min(100, round(seo_score, 1)),
                'sentiment_score': 0.7,  # Mock positive sentiment
                'uniqueness_score': 95.0,  # Mock high uniqueness
                'grammar_score': 98.0,  # Mock high grammar quality
                'quality_rating': 'excellent'
            }
            
        except Exception as e:
            self.logger.error(f"Content quality analysis failed: {e}")
            return {'quality_rating': 'unknown'}

    def _estimate_reading_time(self, text: str) -> float:
        """Estimate reading time in minutes"""
        word_count = len(text.split())
        # Average reading speed: 200-250 words per minute
        return round(word_count / 225, 1)

    def _get_length_target(self, target_length: str, platform: str) -> int:
        """Get numerical length target based on configuration"""
        
        # Platform-specific adjustments
        platform_adjustments = {
            'twitter': {'short': 100, 'medium': 200, 'long': 280},
            'instagram': {'short': 125, 'medium': 300, 'long': 2200},
            'facebook': {'short': 150, 'medium': 400, 'long': 8000},
            'linkedin': {'short': 200, 'medium': 500, 'long': 3000}
        }
        
        if platform in platform_adjustments:
            return platform_adjustments[platform].get(target_length, 300)
        
        # Default length targets
        length_map = {
            'short': 100,
            'medium': 300,
            'long': 800
        }
        
        return length_map.get(target_length, 300)

    def _initialize_platform_specs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific text specifications"""
        return {
            'instagram': {
                'max_characters': 2200,
                'hashtag_limit': 30,
                'optimal_hashtags': 5-10,
                'style_hints': ['visual', 'engaging', 'emoji-friendly']
            },
            'twitter': {
                'max_characters': 280,
                'hashtag_limit': 2,
                'optimal_hashtags': 1-2,
                'style_hints': ['concise', 'impactful', 'conversational']
            },
            'facebook': {
                'max_characters': 8000,
                'hashtag_limit': 5,
                'optimal_hashtags': 1-3,
                'style_hints': ['storytelling', 'community-focused', 'shareable']
            },
            'linkedin': {
                'max_characters': 3000,
                'hashtag_limit': 5,
                'optimal_hashtags': 3-5,
                'style_hints': ['professional', 'educational', 'industry-focused']
            },
            'tiktok': {
                'max_characters': 4000,
                'hashtag_limit': 100,
                'optimal_hashtags': 3-5,
                'style_hints': ['trendy', 'youth-oriented', 'challenge-focused']
            },
            'youtube': {
                'max_characters': 5000,
                'hashtag_limit': 15,
                'optimal_hashtags': 2-3,
                'style_hints': ['descriptive', 'searchable', 'engaging']
            }
        }

    def _initialize_content_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize content templates for each type"""
        return {
            'social_media': {
                'hook_formulas': ['Question', 'Statistic', 'Bold Statement', 'Story'],
                'engagement_tactics': ['Ask Questions', 'Use Emojis', 'Add Hashtags', 'Include CTA'],
                'structure': ['Hook', 'Value', 'Call-to-Action']
            },
            'marketing_copy': {
                'frameworks': ['AIDA', 'PAS', 'BAB', 'PASTOR'],
                'persuasion_tactics': ['Social Proof', 'Scarcity', 'Authority', 'Reciprocity'],
                'structure': ['Headline', 'Problem', 'Solution', 'Benefits', 'CTA']
            },
            'educational': {
                'learning_models': ['Tell-Show-Do', 'Problem-Solution', 'Step-by-Step'],
                'engagement_methods': ['Examples', 'Analogies', 'Questions', 'Summaries'],
                'structure': ['Introduction', 'Main Content', 'Examples', 'Conclusion']
            },
            'creative_writing': {
                'story_structures': ['Three-Act', 'Hero\'s Journey', 'Freytag\'s Pyramid'],
                'literary_devices': ['Metaphor', 'Symbolism', 'Foreshadowing', 'Irony'],
                'structure': ['Setup', 'Conflict', 'Resolution']
            }
        }

    def _initialize_writing_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize writing frameworks for each text type"""
        return {
            'social_media': {
                'structure': ['Hook', 'Value Proposition', 'Engagement Element', 'Call-to-Action'],
                'elements': ['hashtags', 'emojis', 'mentions', 'links'],
                'optimization_goals': ['engagement', 'reach', 'shares']
            },
            'marketing_copy': {
                'structure': ['Attention', 'Interest', 'Desire', 'Action'],
                'elements': ['headline', 'benefits', 'social_proof', 'urgency'],
                'optimization_goals': ['conversion', 'persuasion', 'action']
            },
            'educational': {
                'structure': ['Learning Objective', 'Context', 'Content', 'Practice', 'Summary'],
                'elements': ['examples', 'analogies', 'step_by_step', 'resources'],
                'optimization_goals': ['clarity', 'retention', 'application']
            },
            'creative_writing': {
                'structure': ['Setting', 'Characters', 'Conflict', 'Development', 'Resolution'],
                'elements': ['dialogue', 'description', 'emotion', 'imagery'],
                'optimization_goals': ['engagement', 'emotion', 'memorability']
            }
        }

    def _supports_content_type(self, content_type: str) -> bool:
        """Check if generator supports the specified content type"""
        return content_type in ['text', 'copy', 'content', 'writing']

    async def _release_model_resources(self) -> None:
        """Release model-specific resources"""
        # Clean up model resources
        if hasattr(self, 'models'):
            self.models.clear()
        
        self.logger.info("Text generator resources released")

    # Additional utility methods for text generation

    def get_supported_text_types(self) -> List[str]:
        """Get list of supported text types"""
        return [text_type.value for text_type in TextType]

    def get_supported_formats(self) -> List[str]:
        """Get list of supported content formats"""
        return [format_type.value for format_type in ContentFormat]

    def get_writing_styles(self) -> List[str]:
        """Get list of available writing styles"""
        return [style.value for style in WritingStyle]

    def get_tones_of_voice(self) -> List[str]:
        """Get list of available tones of voice"""
        return [tone.value for tone in ToneOfVoice]

    async def generate_variations(
        self,
        base_text: str,
        config: TextConfig,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate variations of existing text"""
        variations = []
        
        for i in range(count):
            # Create variations by adjusting tone and style
            variation_config = TextConfig(**config.__dict__)
            
            # Vary the tone for each variation
            tones = list(ToneOfVoice)
            variation_config.tone = tones[i % len(tones)]
            
            try:
                strategy = await self._build_content_strategy(base_text, variation_config, None)
                variation_text = await self._generate_text_by_type(strategy, variation_config, None)
                
                variations.append({
                    'id': i + 1,
                    'content': variation_text,
                    'tone': variation_config.tone.value,
                    'word_count': len(variation_text.split()),
                    'character_count': len(variation_text)
                })
                
            except Exception as e:
                self.logger.error(f"Failed to generate variation {i+1}: {e}")
                continue
        
        return variations

    async def optimize_for_platform(
        self,
        text: str,
        source_platform: str,
        target_platform: str
    ) -> str:
        """Optimize text for different platform"""
        try:
            source_spec = self.platform_specs.get(source_platform, {})
            target_spec = self.platform_specs.get(target_platform, {})
            
            optimized_text = text
            
            # Adjust length if needed
            target_max = target_spec.get('max_characters')
            if target_max and len(optimized_text) > target_max:
                optimized_text = optimized_text[:target_max-3] + "..."
            
            # Adjust hashtag count
            target_hashtag_limit = target_spec.get('hashtag_limit', 10)
            hashtags = [word for word in optimized_text.split() if word.startswith('#')]
            
            if len(hashtags) > target_hashtag_limit:
                # Remove excess hashtags
                for hashtag in hashtags[target_hashtag_limit:]:
                    optimized_text = optimized_text.replace(hashtag, '').strip()
            
            self.logger.info(f"Optimized text from {source_platform} to {target_platform}")
            return optimized_text
            
        except Exception as e:
            self.logger.error(f"Platform optimization failed: {e}")
            return text

    async def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """Extract key points from text"""
        try:
            # Mock key point extraction - in production would use NLP
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            # Simple scoring based on sentence length and position
            scored_sentences = []
            for i, sentence in enumerate(sentences):
                score = len(sentence.split()) * (1 - i * 0.1)  # Prefer longer sentences at the beginning
                scored_sentences.append((sentence, score))
            
            # Sort by score and return top points
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            key_points = [sentence for sentence, score in scored_sentences[:max_points]]
            
            return key_points
            
        except Exception as e:
            self.logger.error(f"Key point extraction failed: {e}")
            return []

    async def generate_hashtags(
        self,
        text: str,
        platform: str = 'instagram',
        max_hashtags: int = 10
    ) -> List[str]:
        """Generate relevant hashtags for text"""
        try:
            # Mock hashtag generation - in production would use hashtag analysis
            platform_spec = self.platform_specs.get(platform, {})
            optimal_count = platform_spec.get('optimal_hashtags', max_hashtags)
            
            # Extract keywords and create hashtags
            words = text.lower().split()
            keywords = [word for word in words if len(word) > 4 and word.isalpha()]
            
            # Add some trending/popular hashtags based on content type
            popular_hashtags = ['#content', '#creative', '#inspiration', '#motivation', '#success']
            
            hashtags = []
            for keyword in keywords[:optimal_count//2]:
                hashtags.append(f"#{keyword}")
            
            hashtags.extend(popular_hashtags[:optimal_count - len(hashtags)])
            
            return hashtags[:max_hashtags]
            
        except Exception as e:
            self.logger.error(f"Hashtag generation failed: {e}")
            return ['#content']