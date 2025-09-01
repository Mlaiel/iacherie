#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenAI GPT-4 Client for Advanced Text Generation

Enhanced OpenAI client with GPT-4 integration for professional content creation
with multilingual support, tone adaptation, and creative assistance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Advanced OpenAI GPT-4 client for professional content generation
    with multilingual support and cultural adaptation.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client with configuration."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.default_model = "gpt-4-turbo-preview"
        self.max_retries = 3
        
        # Supported languages for multilingual content
        self.supported_languages = {
            'en': 'English',
            'fr': 'French', 
            'es': 'Spanish',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic'
        }
        
        if OPENAI_AVAILABLE and self.api_key:
            try:
                openai.api_key = self.api_key
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("OpenAI not available or API key not provided")

    def _count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Count tokens in text for the specified model."""
        if not TIKTOKEN_AVAILABLE:
            # Rough estimation: 1 token ≈ 4 characters
            return len(text) // 4
        
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback estimation
            return len(text) // 4

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        language: str = 'en',
        tone: str = 'professional',
        style: str = 'creative',
        audience: str = 'general'
    ) -> Dict[str, Any]:
        """
        Generate high-quality text content with GPT-4.
        
        Args:
            prompt: Input prompt for generation
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0-1.0)
            language: Target language code
            tone: Content tone (professional, casual, formal, friendly)
            style: Writing style (creative, technical, marketing, blog)
            audience: Target audience (general, expert, youth, business)
            
        Returns:
            Dictionary with generated content and metadata
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI client not available",
                "content": "",
                "metadata": {}
            }

        try:
            # Enhance prompt with language and style guidance
            enhanced_prompt = self._enhance_prompt(prompt, language, tone, style, audience)
            
            logger.info(f"Generating text with GPT-4 in {language} with {tone} tone")
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional content creator specialized in {style} writing with a {tone} tone for {audience} audience. Write in {self.supported_languages.get(language, language)}."
                    },
                    {
                        "role": "user", 
                        "content": enhanced_prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            content = response.choices[0].message.content
            
            return {
                "success": True,
                "content": content,
                "metadata": {
                    "model": self.default_model,
                    "language": language,
                    "tone": tone,
                    "style": style,
                    "audience": audience,
                    "tokens_used": response.usage.total_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "metadata": {}
            }

    def _enhance_prompt(self, prompt: str, language: str, tone: str, style: str, audience: str) -> str:
        """Enhance the base prompt with language and style context."""
        enhancements = []
        
        # Language-specific guidance
        if language != 'en':
            lang_name = self.supported_languages.get(language, language)
            enhancements.append(f"Write the response in {lang_name}.")
        
        # Style-specific guidance
        style_guides = {
            'creative': "Use vivid imagery, engaging metaphors, and captivating storytelling techniques.",
            'technical': "Use precise terminology, clear explanations, and logical structure.",
            'marketing': "Use persuasive language, compelling calls-to-action, and benefit-focused messaging.",
            'blog': "Use conversational tone, engaging headlines, and reader-friendly formatting.",
            'social': "Use concise, engaging language optimized for social media platforms.",
            'email': "Use clear subject lines, scannable content, and strong calls-to-action."
        }
        
        if style in style_guides:
            enhancements.append(style_guides[style])
        
        # Tone-specific guidance
        tone_guides = {
            'professional': "Maintain a formal, authoritative, and respectful tone.",
            'casual': "Use relaxed, conversational, and approachable language.",
            'friendly': "Be warm, welcoming, and personable in your communication.",
            'formal': "Use proper grammar, sophisticated vocabulary, and structured presentation.",
            'excited': "Show enthusiasm, energy, and positive emotion.",
            'empathetic': "Demonstrate understanding, compassion, and emotional intelligence."
        }
        
        if tone in tone_guides:
            enhancements.append(tone_guides[tone])
        
        # Audience-specific guidance
        audience_guides = {
            'expert': "Use technical terminology and assume advanced knowledge of the subject.",
            'beginner': "Explain concepts clearly and avoid jargon.",
            'youth': "Use modern, energetic language that resonates with younger audiences.",
            'business': "Focus on ROI, efficiency, and professional outcomes.",
            'creative': "Appeal to artistic sensibilities and innovative thinking."
        }
        
        if audience in audience_guides:
            enhancements.append(audience_guides[audience])
        
        # Combine prompt with enhancements
        if enhancements:
            enhancement_text = " ".join(enhancements)
            return f"{prompt}\n\nStyle guidance: {enhancement_text}"
        
        return prompt

    async def translate_content(
        self,
        content: str,
        target_language: str,
        source_language: str = 'auto',
        preserve_style: bool = True
    ) -> Dict[str, Any]:
        """
        Translate content while preserving style and cultural context.
        
        Args:
            content: Content to translate
            target_language: Target language code
            source_language: Source language code ('auto' for detection)
            preserve_style: Whether to maintain original style and tone
            
        Returns:
            Dictionary with translated content and metadata
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI client not available",
                "translated_content": "",
                "metadata": {}
            }

        try:
            target_lang_name = self.supported_languages.get(target_language, target_language)
            
            style_instruction = ""
            if preserve_style:
                style_instruction = "Preserve the original tone, style, and cultural context while adapting appropriately for the target culture."
            
            prompt = f"""
            Translate the following content to {target_lang_name}.
            {style_instruction}
            
            Content to translate:
            {content}
            """
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator with expertise in cultural adaptation and style preservation. Translate content to {target_lang_name} while maintaining the original intent and emotional impact."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=len(content) * 2,  # Allow for expansion
                temperature=0.3  # Lower temperature for more consistent translations
            )
            
            translated_content = response.choices[0].message.content
            
            return {
                "success": True,
                "translated_content": translated_content,
                "metadata": {
                    "model": self.default_model,
                    "source_language": source_language,
                    "target_language": target_language,
                    "preserve_style": preserve_style,
                    "tokens_used": response.usage.total_tokens,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "translated_content": "",
                "metadata": {}
            }

    async def adapt_content_culturally(
        self,
        content: str,
        target_culture: str,
        content_type: str = 'general'
    ) -> Dict[str, Any]:
        """
        Adapt content for specific cultural context and local preferences.
        
        Args:
            content: Content to adapt
            target_culture: Target culture/region (e.g., 'US', 'UK', 'JP', 'FR')
            content_type: Type of content (marketing, social, blog, email)
            
        Returns:
            Dictionary with culturally adapted content
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI client not available",
                "adapted_content": "",
                "metadata": {}
            }

        try:
            prompt = f"""
            Adapt the following {content_type} content for {target_culture} culture.
            Consider local customs, preferences, communication styles, and cultural sensitivities.
            Maintain the core message while making it culturally appropriate and engaging.
            
            Original content:
            {content}
            """
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a cultural adaptation specialist with deep knowledge of {target_culture} culture, customs, and communication preferences. Adapt content to be culturally appropriate and engaging for this audience."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=len(content) * 2,
                temperature=0.7
            )
            
            adapted_content = response.choices[0].message.content
            
            return {
                "success": True,
                "adapted_content": adapted_content,
                "metadata": {
                    "model": self.default_model,
                    "target_culture": target_culture,
                    "content_type": content_type,
                    "tokens_used": response.usage.total_tokens,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Cultural adaptation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "adapted_content": "",
                "metadata": {}
            }

    async def check_content_quality(self, content: str) -> Dict[str, Any]:
        """
        Analyze content quality and provide improvement suggestions.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with quality analysis and suggestions
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI client not available",
                "analysis": {},
                "suggestions": []
            }

        try:
            prompt = f"""
            Analyze the following content for quality, clarity, engagement, and effectiveness.
            Provide scores (1-10) for:
            - Clarity and readability
            - Engagement and interest
            - Grammar and style
            - Structure and flow
            - Overall effectiveness
            
            Also provide specific improvement suggestions.
            
            Content to analyze:
            {content}
            """
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional content editor and quality analyst. Provide detailed, actionable feedback on content quality."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": {
                    "raw_analysis": analysis_text,
                    "content_length": len(content),
                    "estimated_reading_time": len(content.split()) / 200  # Words per minute
                },
                "suggestions": [],  # Could parse structured suggestions from response
                "metadata": {
                    "model": self.default_model,
                    "tokens_used": response.usage.total_tokens,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Content quality check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {},
                "suggestions": []
            }

    def is_available(self) -> bool:
        """Check if OpenAI client is available and configured."""
        return self.client is not None

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return list(self.supported_languages.keys())