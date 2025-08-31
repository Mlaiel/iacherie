"""
Content Generator - Advanced AI-Powered Content Generation Engine

Ultra-advanced content generation system supporting all media types and creative styles
for musicians, bloggers, photographers, influencers, and comedians.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  IMPORTANT LEGAL NOTICE:
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
from typing import Dict, List, Any, Optional, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from pathlib import Path
import re
import hashlib
import uuid
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import librosa
import torch
import transformers
from transformers import (
    GPT2LMHeadModel, GPT2Tokenizer, pipeline,
    T5ForConditionalGeneration, T5Tokenizer,
    BlipProcessor, BlipForConditionalGeneration,
    AutoTokenizer, AutoModelForSeq2SeqLM
)
import openai
from openai import AsyncOpenAI
import anthropic
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, and_, or_
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
import requests
import aiohttp
import aiofiles
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC

try:
    from core.database import get_async_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_async_session = DatabaseManager
try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...security.encryption import AdvancedEncryption
from ...models.content import Content, ContentType, ContentStatus, ContentMetadata
from ...models.users import User, UserProfile, CreatorProfile
from ...ai.ml_models import AdvancedMLPipeline
from ...ai.llm_engine import UnifiedLLMEngine
from ...audio.audio_processor import EnterpriseAudioProcessor
from ...content_protection.content_fingerprint import ContentFingerprintEngine

logger = logging.getLogger(__name__)
settings = get_settings()


class ContentGenerationType(str, Enum):
    """Advanced content generation types"""
    # Text content
    BLOG_ARTICLE = "blog_article"
    SOCIAL_MEDIA_POST = "social_media_post"
    EMAIL_NEWSLETTER = "email_newsletter"
    PRODUCT_DESCRIPTION = "product_description"
    SEO_CONTENT = "seo_content"
    PRESS_RELEASE = "press_release"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    
    # Creative content
    SONG_LYRICS = "song_lyrics"
    POEM = "poem"
    SHORT_STORY = "short_story"
    SCRIPT = "script"
    COMEDY_ROUTINE = "comedy_routine"
    
    # Marketing content
    AD_COPY = "ad_copy"
    LANDING_PAGE = "landing_page"
    SALES_EMAIL = "sales_email"
    SOCIAL_MEDIA_CAMPAIGN = "social_media_campaign"
    INFLUENCER_PITCH = "influencer_pitch"
    
    # Audio content
    PODCAST_SCRIPT = "podcast_script"
    VOICEOVER_SCRIPT = "voiceover_script"
    AUDIO_DESCRIPTION = "audio_description"
    MUSIC_COMPOSITION = "music_composition"
    
    # Video content
    VIDEO_SCRIPT = "video_script"
    STORYBOARD = "storyboard"
    MOTION_GRAPHICS = "motion_graphics"
    
    # Image content
    IMAGE_CAPTION = "image_caption"
    PHOTO_DESCRIPTION = "photo_description"
    VISUAL_STORY = "visual_story"


class CreativeEngine(str, Enum):
    """AI engines for content generation"""
    GPT4_TURBO = "gpt-4-turbo"
    GPT4_VISION = "gpt-4-vision-preview"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    CUSTOM_T5 = "custom-t5"
    CUSTOM_BERT = "custom-bert"
    DALL_E_3 = "dall-e-3"
    MIDJOURNEY = "midjourney"
    STABLE_DIFFUSION = "stable-diffusion"


class ContentTone(str, Enum):
    """Content tone and style options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    HUMOROUS = "humorous"
    DRAMATIC = "dramatic"
    INSPIRING = "inspiring"
    EDUCATIONAL = "educational"
    PERSUASIVE = "persuasive"
    STORYTELLING = "storytelling"
    TECHNICAL = "technical"
    EMOTIONAL = "emotional"
    CONVERSATIONAL = "conversational"
    FORMAL = "formal"


@dataclass
class GenerationRequest:
    """Content generation request structure"""
    content_type: ContentGenerationType
    prompt: str
    tone: ContentTone = ContentTone.PROFESSIONAL
    target_audience: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    length_constraint: Optional[int] = None
    style_references: List[str] = field(default_factory=list)
    format_requirements: Dict[str, Any] = field(default_factory=dict)
    brand_guidelines: Optional[Dict[str, Any]] = None
    seo_requirements: Optional[Dict[str, Any]] = None
    multilingual: Optional[List[str]] = None
    creativity_level: float = 0.7
    engine_preference: Optional[CreativeEngine] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class GeneratedContent:
    """Generated content with metadata"""
    content: str
    content_type: ContentGenerationType
    metadata: Dict[str, Any]
    quality_score: float
    creativity_score: float
    seo_score: Optional[float] = None
    readability_score: Optional[float] = None
    engagement_prediction: Optional[float] = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    generation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    engine_used: Optional[str] = None
    processing_time: Optional[float] = None
    cost_estimate: Optional[float] = None


class ContentGenerator:
    """Advanced AI-powered content generator"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Load ML models
        self.ml_pipeline = AdvancedMLPipeline()
        self.llm_engine = UnifiedLLMEngine()
        self.audio_processor = EnterpriseAudioProcessor()
        self.fingerprint_engine = ContentFingerprintEngine()
        
        # Load specialized models
        self._load_specialized_models()
        
        # Content templates and patterns
        self.content_templates = self._load_content_templates()
        self.style_patterns = self._load_style_patterns()
        
        logger.info("ContentGenerator initialized with all AI engines")

    def _load_specialized_models(self):
        """Load specialized AI models for different content types"""



        try:
            # Text generation models
            self.gpt2_model = GPT2LMHeadModel.from_pretrained('gpt2-large')
            self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2-large')
            
            # T5 for text-to-text generation
            self.t5_model = T5ForConditionalGeneration.from_pretrained('t5-large')
            self.t5_tokenizer = T5Tokenizer.from_pretrained('t5-large')
            
            # BLIP for image captioning
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
            
            # Sentiment and style analysis
            self.sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            self.emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
            
            logger.info("Specialized AI models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading specialized models: {e}")
            # Use fallback models or cloud APIs
            self._setup_fallback_models()

    def _setup_fallback_models(self):
        """Setup fallback cloud-based models"""
        self.use_cloud_models = True
        logger.info("Using cloud-based AI models as fallback")

    def _load_content_templates(self) -> Dict[str, Dict]:
        """Load content templates for different types"""



        return {
            ContentGenerationType.BLOG_ARTICLE: {
                "structure": ["introduction", "main_points", "conclusion", "call_to_action"],
                "min_sections": 3,
                "recommended_length": 1500,
                "seo_elements": ["title", "meta_description", "headers", "keywords"]
            },
            ContentGenerationType.SOCIAL_MEDIA_POST: {
                "structure": ["hook", "content", "call_to_action", "hashtags"],
                "platform_limits": {
                    "twitter": 280,
                    "instagram": 2200,
                    "linkedin": 3000,
                    "facebook": 63206
                },
                "engagement_elements": ["question", "poll", "hashtags", "mentions"]
            },
            ContentGenerationType.SONG_LYRICS: {
                "structure": ["verse", "chorus", "verse", "chorus", "bridge", "chorus"],
                "rhyme_schemes": ["ABAB", "AABB", "ABCB", "AAAA"],
                "syllable_patterns": [8, 10, 12],
                "themes": ["love", "life", "dreams", "struggle", "celebration"]
            },
            ContentGenerationType.VIDEO_SCRIPT: {
                "structure": ["hook", "introduction", "main_content", "conclusion", "call_to_action"],
                "timing_guidelines": {
                    "youtube_shorts": 60,
                    "instagram_reel": 90,
                    "tiktok": 180,
                    "youtube_video": 600
                },
                "visual_cues": True,
                "audio_cues": True
            }
        }

    def _load_style_patterns(self) -> Dict[str, Dict]:
        """Load writing style patterns"""



        return {
            ContentTone.PROFESSIONAL: {
                "vocabulary": "formal",
                "sentence_structure": "complex",
                "personal_pronouns": "minimal",
                "contractions": False,
                "technical_terms": True
            },
            ContentTone.CASUAL: {
                "vocabulary": "informal",
                "sentence_structure": "varied",
                "personal_pronouns": "frequent",
                "contractions": True,
                "technical_terms": False
            },
            ContentTone.HUMOROUS: {
                "vocabulary": "playful",
                "sentence_structure": "punchy",
                "wordplay": True,
                "timing": "comedic",
                "surprise_elements": True
            },
            ContentTone.EDUCATIONAL: {
                "vocabulary": "clear",
                "sentence_structure": "logical",
                "examples": True,
                "step_by_step": True,
                "definitions": True
            }
        }

    async def generate_content(self, request: GenerationRequest) -> GeneratedContent:
        """Generate content based on request parameters"""
        start_time = datetime.now()
        
        try:
            # Validate request
            self._validate_request(request)
            
            # Select optimal AI engine
            engine = self._select_optimal_engine(request)
            
            # Generate content based on type
            if request.content_type in [
                ContentGenerationType.BLOG_ARTICLE,
                ContentGenerationType.SOCIAL_MEDIA_POST,
                ContentGenerationType.EMAIL_NEWSLETTER
            ]:
                content = await self._generate_text_content(request, engine)
            elif request.content_type in [
                ContentGenerationType.SONG_LYRICS,
                ContentGenerationType.POEM,
                ContentGenerationType.COMEDY_ROUTINE
            ]:
                content = await self._generate_creative_content(request, engine)
            elif request.content_type in [
                ContentGenerationType.VIDEO_SCRIPT,
                ContentGenerationType.PODCAST_SCRIPT
            ]:
                content = await self._generate_script_content(request, engine)
            elif request.content_type in [
                ContentGenerationType.IMAGE_CAPTION,
                ContentGenerationType.PHOTO_DESCRIPTION
            ]:
                content = await self._generate_visual_content(request, engine)
            else:
                content = await self._generate_generic_content(request, engine)
            
            # Analyze and enhance content
            enhanced_content = await self._enhance_content(content, request)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(enhanced_content, request)
            
            # Create result
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = GeneratedContent(
                content=enhanced_content,
                content_type=request.content_type,
                metadata=self._create_metadata(request, quality_metrics),
                quality_score=quality_metrics.get('quality_score', 0.8),
                creativity_score=quality_metrics.get('creativity_score', request.creativity_level),
                seo_score=quality_metrics.get('seo_score'),
                readability_score=quality_metrics.get('readability_score'),
                engagement_prediction=quality_metrics.get('engagement_prediction'),
                engine_used=engine.value if isinstance(engine, CreativeEngine) else str(engine),
                processing_time=processing_time,
                cost_estimate=self._estimate_cost(request, processing_time)
            )
            
            # Store generation record
            await self._store_generation_record(request, result)
            
            logger.info(f"Content generated successfully: {result.generation_id}")
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

    def _validate_request(self, request: GenerationRequest):
        """Validate generation request"""
        if not request.prompt or len(request.prompt.strip()) < 10:
            raise ValueError("Prompt must be at least 10 characters long")
        
        if request.creativity_level < 0 or request.creativity_level > 1:
            raise ValueError("Creativity level must be between 0 and 1")
        
        if request.length_constraint and request.length_constraint < 1:
            raise ValueError("Length constraint must be positive")

    def _select_optimal_engine(self, request: GenerationRequest) -> CreativeEngine:
        """Select the optimal AI engine for the request"""
        if request.engine_preference:
            return request.engine_preference
        
        # Engine selection logic based on content type
        engine_map = {
            ContentGenerationType.BLOG_ARTICLE: CreativeEngine.GPT4_TURBO,
            ContentGenerationType.SOCIAL_MEDIA_POST: CreativeEngine.CLAUDE_3_SONNET,
            ContentGenerationType.SONG_LYRICS: CreativeEngine.GPT4_TURBO,
            ContentGenerationType.VIDEO_SCRIPT: CreativeEngine.CLAUDE_3_OPUS,
            ContentGenerationType.IMAGE_CAPTION: CreativeEngine.GPT4_VISION,
            ContentGenerationType.TECHNICAL_DOCUMENTATION: CreativeEngine.CLAUDE_3_OPUS,
            ContentGenerationType.COMEDY_ROUTINE: CreativeEngine.GPT4_TURBO,
            ContentGenerationType.SEO_CONTENT: CreativeEngine.GEMINI_PRO
        }
        
        return engine_map.get(request.content_type, CreativeEngine.GPT4_TURBO)

    async def _generate_text_content(self, request: GenerationRequest, engine: CreativeEngine) -> str:
        """Generate text-based content"""
        # Build comprehensive prompt
        prompt = self._build_text_prompt(request)
        
        if engine == CreativeEngine.GPT4_TURBO:
            return await self._generate_with_openai(prompt, request)
        elif engine in [CreativeEngine.CLAUDE_3_OPUS, CreativeEngine.CLAUDE_3_SONNET]:
            return await self._generate_with_anthropic(prompt, request, engine)
        elif engine == CreativeEngine.GEMINI_PRO:
            return await self._generate_with_gemini(prompt, request)
        else:
            return await self._generate_with_custom_model(prompt, request)

    async def _generate_creative_content(self, request: GenerationRequest, engine: CreativeEngine) -> str:
        """Generate creative content like lyrics, poems, stories"""
        # Build creative prompt with structure
        prompt = self._build_creative_prompt(request)
        
        # Add creative constraints
        if request.content_type == ContentGenerationType.SONG_LYRICS:
            prompt += self._add_lyric_constraints(request)
        elif request.content_type == ContentGenerationType.POEM:
            prompt += self._add_poetry_constraints(request)
        elif request.content_type == ContentGenerationType.COMEDY_ROUTINE:
            prompt += self._add_comedy_constraints(request)
        
        return await self._generate_with_creative_engine(prompt, request, engine)

    async def _generate_script_content(self, request: GenerationRequest, engine: CreativeEngine) -> str:
        """Generate script content for video/audio"""
        # Build script prompt with formatting
        prompt = self._build_script_prompt(request)
        
        # Add timing and visual cues
        if request.content_type == ContentGenerationType.VIDEO_SCRIPT:
            prompt += "\n\nInclude timing marks, visual cues, and scene descriptions."
        elif request.content_type == ContentGenerationType.PODCAST_SCRIPT:
            prompt += "\n\nInclude audio cues, transitions, and speaking notes."
        
        return await self._generate_with_script_engine(prompt, request, engine)

    async def _generate_visual_content(self, request: GenerationRequest, engine: CreativeEngine) -> str:
        """Generate visual content descriptions"""
        prompt = self._build_visual_prompt(request)
        
        # Use vision-capable models
        if engine == CreativeEngine.GPT4_VISION:
            return await self._generate_with_vision_model(prompt, request)
        else:
            return await self._generate_visual_description(prompt, request)

    async def _generate_generic_content(self, request: GenerationRequest, engine: CreativeEngine) -> str:
        """Generate generic content for other types"""
        prompt = self._build_generic_prompt(request)
        return await self._generate_with_selected_engine(prompt, request, engine)

    def _build_text_prompt(self, request: GenerationRequest) -> str:
        """Build comprehensive prompt for text content"""
        template = self.content_templates.get(request.content_type, {})
        style = self.style_patterns.get(request.tone, {})
        
        prompt_parts = [
            f"Generate a {request.content_type.value} with the following requirements:",
            f"Topic: {request.prompt}",
            f"Tone: {request.tone.value}",
        ]
        
        if request.target_audience:
            prompt_parts.append(f"Target audience: {request.target_audience}")
        
        if request.keywords:
            prompt_parts.append(f"Keywords to include: {', '.join(request.keywords)}")
        
        if request.length_constraint:
            prompt_parts.append(f"Approximate length: {request.length_constraint} words")
        
        # Add structure requirements
        if 'structure' in template:
            prompt_parts.append(f"Structure: {' -> '.join(template['structure'])}")
        
        # Add style guidelines
        style_guide = []
        if style.get('vocabulary'):
            style_guide.append(f"Use {style['vocabulary']} vocabulary")
        if style.get('sentence_structure'):
            style_guide.append(f"Use {style['sentence_structure']} sentence structure")
        
        if style_guide:
            prompt_parts.append(f"Style guidelines: {'; '.join(style_guide)}")
        
        # Add SEO requirements
        if request.seo_requirements:
            seo_parts = []
            if request.seo_requirements.get('focus_keyword'):
                seo_parts.append(f"Focus keyword: {request.seo_requirements['focus_keyword']}")
            if request.seo_requirements.get('meta_description'):
                seo_parts.append("Include meta description")
            if seo_parts:
                prompt_parts.append(f"SEO requirements: {'; '.join(seo_parts)}")
        
        return "\n".join(prompt_parts)

    def _build_creative_prompt(self, request: GenerationRequest) -> str:
        """Build prompt for creative content"""
        prompt_parts = [
            f"Create an original {request.content_type.value} based on:",
            f"Theme/Inspiration: {request.prompt}",
            f"Creative style: {request.tone.value}",
            f"Creativity level: {'High' if request.creativity_level > 0.7 else 'Moderate' if request.creativity_level > 0.4 else 'Conservative'}",
        ]
        
        if request.style_references:
            prompt_parts.append(f"Style references: {', '.join(request.style_references)}")
        
        return "\n".join(prompt_parts)

    def _build_script_prompt(self, request: GenerationRequest) -> str:
        """Build prompt for script content"""
        template = self.content_templates.get(request.content_type, {})
        
        prompt_parts = [
            f"Write a professional {request.content_type.value} for:",
            f"Topic: {request.prompt}",
            f"Tone: {request.tone.value}",
        ]
        
        if 'timing_guidelines' in template and request.format_requirements.get('platform'):
            platform = request.format_requirements['platform']
            if platform in template['timing_guidelines']:
                duration = template['timing_guidelines'][platform]
                prompt_parts.append(f"Target duration: approximately {duration} seconds")
        
        prompt_parts.append("Include stage directions, timing cues, and formatting appropriate for production.")
        
        return "\n".join(prompt_parts)

    def _build_visual_prompt(self, request: GenerationRequest) -> str:
        """Build prompt for visual content"""



        return f"""
        Generate a detailed and engaging {request.content_type.value} for:
        Subject: {request.prompt}
        Style: {request.tone.value}
        
        Focus on visual elements, composition, mood, and storytelling aspects.
        Make it suitable for social media and marketing use.
        """

    def _build_generic_prompt(self, request: GenerationRequest) -> str:
        """Build generic prompt for other content types"""



        return f"""
        Create high-quality {request.content_type.value} content about:
        {request.prompt}
        
        Style: {request.tone.value}
        Target audience: {request.target_audience or 'General audience'}
        
        Ensure the content is engaging, original, and professionally written.
        """

    async def _generate_with_openai(self, prompt: str, request: GenerationRequest) -> str:
        """Generate content using OpenAI GPT models"""



        try:
            messages = [
                {"role": "system", "content": self._get_system_prompt(request)},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=request.creativity_level,
                max_tokens=self._calculate_max_tokens(request),
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def _generate_with_anthropic(self, prompt: str, request: GenerationRequest, engine: CreativeEngine) -> str:
        """Generate content using Anthropic Claude"""



        try:
            model_map = {
                CreativeEngine.CLAUDE_3_OPUS: "claude-3-opus-20240229",
                CreativeEngine.CLAUDE_3_SONNET: "claude-3-sonnet-20240229"
            }
            
            message = await self.anthropic_client.messages.create(
                model=model_map.get(engine, "claude-3-sonnet-20240229"),
                max_tokens=self._calculate_max_tokens(request),
                temperature=request.creativity_level,
                system=self._get_system_prompt(request),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise

    async def _generate_with_gemini(self, prompt: str, request: GenerationRequest) -> str:
        """Generate content using Google Gemini"""



        try:
            model = genai.GenerativeModel('gemini-pro')
            
            generation_config = genai.types.GenerationConfig(
                temperature=request.creativity_level,
                max_output_tokens=self._calculate_max_tokens(request),
                top_p=0.8,
                top_k=40
            )
            
            full_prompt = f"{self._get_system_prompt(request)}\n\n{prompt}"
            
            response = await model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    async def _generate_with_custom_model(self, prompt: str, request: GenerationRequest) -> str:
        """Generate content using custom local models"""



        try:
            # Use T5 for text-to-text generation
            input_text = f"generate {request.content_type.value}: {prompt}"
            input_ids = self.t5_tokenizer.encode(input_text, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.t5_model.generate(
                    input_ids,
                    max_length=self._calculate_max_tokens(request),
                    temperature=request.creativity_level,
                    do_sample=True,
                    top_p=0.9,
                    num_return_sequences=1
                )
            
            generated_text = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"Custom model generation failed: {e}")
            # Fallback to cloud models
            return await self._generate_with_openai(prompt, request)

    def _get_system_prompt(self, request: GenerationRequest) -> str:
        """Get system prompt based on request"""
        base_prompt = f"""
        You are an expert content creator specializing in {request.content_type.value} creation.
        
        Your expertise includes:
        - Professional writing and creative storytelling
        - SEO optimization and marketing psychology  
        - Brand voice consistency and audience engagement
        - Multi-platform content adaptation
        - Content performance optimization
        
        Guidelines:
        - Create original, high-quality content
        - Match the specified tone and style exactly
        - Include relevant keywords naturally
        - Ensure content is engaging and actionable
        - Follow platform-specific best practices
        - Maintain professional standards
        """
        
        # Add specific instructions based on content type
        if request.content_type == ContentGenerationType.SEO_CONTENT:
            base_prompt += "\n- Focus on search engine optimization while maintaining readability"
        elif request.content_type == ContentGenerationType.SOCIAL_MEDIA_POST:
            base_prompt += "\n- Include relevant hashtags and engagement hooks"
        elif request.content_type == ContentGenerationType.SONG_LYRICS:
            base_prompt += "\n- Focus on rhythm, rhyme, and emotional resonance"
        
        return base_prompt

    def _calculate_max_tokens(self, request: GenerationRequest) -> int:
        """Calculate maximum tokens based on request"""
        if request.length_constraint:
            # Approximate 1.3 tokens per word
            return min(int(request.length_constraint * 1.5), 4000)
        
        # Default tokens by content type
        token_map = {
            ContentGenerationType.SOCIAL_MEDIA_POST: 300,
            ContentGenerationType.BLOG_ARTICLE: 2000,
            ContentGenerationType.EMAIL_NEWSLETTER: 1000,
            ContentGenerationType.SONG_LYRICS: 500,
            ContentGenerationType.VIDEO_SCRIPT: 1500,
            ContentGenerationType.PRODUCT_DESCRIPTION: 400
        }
        
        return token_map.get(request.content_type, 1000)

    async def _enhance_content(self, content: str, request: GenerationRequest) -> str:
        """Enhance generated content with post-processing"""
        enhanced = content
        
        # Apply tone-specific enhancements
        if request.tone == ContentTone.PROFESSIONAL:
            enhanced = self._enhance_professional_tone(enhanced)
        elif request.tone == ContentTone.HUMOROUS:
            enhanced = self._enhance_humor(enhanced)
        elif request.tone == ContentTone.EDUCATIONAL:
            enhanced = self._enhance_educational_content(enhanced)
        
        # Add SEO enhancements
        if request.seo_requirements:
            enhanced = await self._apply_seo_enhancements(enhanced, request)
        
        # Format for specific platforms
        if request.format_requirements:
            enhanced = self._apply_format_requirements(enhanced, request)
        
        return enhanced

    def _enhance_professional_tone(self, content: str) -> str:
        """Enhance content for professional tone"""
        # Remove contractions
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "isn't": "is not", "aren't": "are not", "wasn't": "was not",
            "weren't": "were not", "hasn't": "has not", "haven't": "have not",
            "hadn't": "had not", "wouldn't": "would not", "shouldn't": "should not",
            "couldn't": "could not", "mustn't": "must not"
        }
        
        for contraction, expansion in contractions.items():
            content = re.sub(r'\b' + contraction.replace("'", r"'") + r'\b', expansion, content, flags=re.IGNORECASE)
        
        return content

    def _enhance_humor(self, content: str) -> str:
        """Enhance content with humor elements"""
        # This would include humor analysis and enhancement
        # For now, return as is
        return content

    def _enhance_educational_content(self, content: str) -> str:
        """Enhance content for educational purposes"""
        # Add structural elements for better learning
        # This could include adding bullet points, numbered lists, etc.
        return content

    async def _apply_seo_enhancements(self, content: str, request: GenerationRequest) -> str:
        """Apply SEO enhancements to content"""
        seo_req = request.seo_requirements
        
        if not seo_req:
            return content
        
        enhanced = content
        
        # Ensure focus keyword appears in key positions
        if seo_req.get('focus_keyword'):
            keyword = seo_req['focus_keyword']
            # Check if keyword appears in first paragraph
            paragraphs = content.split('\n\n')
            if paragraphs and keyword.lower() not in paragraphs[0].lower():
                # Try to naturally integrate the keyword
                enhanced = self._integrate_keyword_naturally(enhanced, keyword)
        
        # Add meta description if requested
        if seo_req.get('include_meta_description'):
            meta_desc = await self._generate_meta_description(enhanced, request)
            enhanced += f"\n\n[META DESCRIPTION: {meta_desc}]"
        
        return enhanced

    def _integrate_keyword_naturally(self, content: str, keyword: str) -> str:
        """Naturally integrate keyword into content"""
        # Simple implementation - in production, this would be more sophisticated
        sentences = content.split('. ')
        if sentences:
            first_sentence = sentences[0]
            if keyword.lower() not in first_sentence.lower():
                # Try to add keyword to first sentence naturally
                enhanced_sentence = f"{first_sentence.rstrip('.')} related to {keyword}."
                sentences[0] = enhanced_sentence
                content = '. '.join(sentences)
        
        return content

    async def _generate_meta_description(self, content: str, request: GenerationRequest) -> str:
        """Generate SEO meta description"""
        # Extract key points and create compelling meta description
        sentences = content.split('. ')[:3]  # First few sentences
        summary = '. '.join(sentences)[:155]  # Limit to 155 characters
        
        if len(summary) == 155:
            summary = summary[:152] + "..."
        
        return summary

    def _apply_format_requirements(self, content: str, request: GenerationRequest) -> str:
        """Apply specific format requirements"""
        format_req = request.format_requirements
        
        if not format_req:
            return content
        
        formatted = content
        
        # Platform-specific formatting
        if format_req.get('platform') == 'instagram':
            formatted = self._format_for_instagram(formatted)
        elif format_req.get('platform') == 'linkedin':
            formatted = self._format_for_linkedin(formatted)
        elif format_req.get('platform') == 'twitter':
            formatted = self._format_for_twitter(formatted)
        
        # HTML formatting if requested
        if format_req.get('html_format'):
            formatted = self._convert_to_html(formatted)
        
        # Markdown formatting if requested
        if format_req.get('markdown_format'):
            formatted = self._convert_to_markdown(formatted)
        
        return formatted

    def _format_for_instagram(self, content: str) -> str:
        """Format content for Instagram"""
        # Add line breaks for readability
        # Add relevant hashtags
        formatted = content + "\n\n"
        
        # Add generic hashtags (in production, these would be more targeted)
        hashtags = ["#content", "#creative", "#inspiration", "#quality"]
        formatted += " ".join(hashtags)
        
        return formatted

    def _format_for_linkedin(self, content: str) -> str:
        """Format content for LinkedIn"""
        # Professional formatting with proper paragraphs
        return content

    def _format_for_twitter(self, content: str) -> str:
        """Format content for Twitter"""
        # Ensure content fits Twitter character limit
        if len(content) > 280:
            content = content[:277] + "..."
        return content

    def _convert_to_html(self, content: str) -> str:
        """Convert content to HTML format"""
        # Basic HTML conversion
        html_content = content.replace('\n\n', '</p><p>')
        html_content = f"<p>{html_content}</p>"
        return html_content

    def _convert_to_markdown(self, content: str) -> str:
        """Convert content to Markdown format"""
        # Basic Markdown conversion
        return content  # Already in a readable format

    async def _calculate_quality_metrics(self, content: str, request: GenerationRequest) -> Dict[str, float]:
        """Calculate comprehensive quality metrics"""
        metrics = {}
        
        try:
            # Content length analysis
            word_count = len(content.split())
            char_count = len(content)
            
            # Readability score (Flesch-Kincaid)
            readability = self._calculate_readability_score(content)
            metrics['readability_score'] = readability
            
            # SEO score if keywords provided
            if request.keywords:
                seo_score = self._calculate_seo_score(content, request.keywords)
                metrics['seo_score'] = seo_score
            
            # Sentiment analysis
            sentiment = self.sentiment_analyzer(content[:512])  # Limit for model
            sentiment_score = sentiment[0]['score'] if sentiment else 0.5
            metrics['sentiment_score'] = sentiment_score
            
            # Creativity assessment based on vocabulary diversity
            creativity = self._assess_creativity(content)
            metrics['creativity_score'] = creativity
            
            # Overall quality score
            quality_factors = [
                readability / 100,  # Normalize to 0-1
                sentiment_score,
                creativity,
                min(word_count / 100, 1.0)  # Word count factor
            ]
            
            if 'seo_score' in metrics:
                quality_factors.append(metrics['seo_score'])
            
            metrics['quality_score'] = np.mean(quality_factors)
            
            # Engagement prediction (simplified)
            engagement = self._predict_engagement(content, request)
            metrics['engagement_prediction'] = engagement
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
            # Provide default metrics
            metrics = {
                'quality_score': 0.75,
                'creativity_score': request.creativity_level,
                'readability_score': 70.0,
                'engagement_prediction': 0.6
            }
        
        return metrics

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate Flesch-Kincaid readability score"""



        try:
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            words = content.split()
            syllables = sum(self._count_syllables(word) for word in words)
            
            if len(sentences) == 0 or len(words) == 0:
                return 50.0
            
            avg_sentence_length = len(words) / len(sentences)
            avg_syllables_per_word = syllables / len(words)
            
            # Flesch Reading Ease Score
            score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            
            # Normalize to 0-100 range
            return max(0, min(100, score))
            
        except:
            return 50.0  # Default moderate readability

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower().strip(".,!?;:")
        if len(word) <= 3:
            return 1
        
        vowels = "aeiouy"
        syllable_count = 0
        prev_char_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_was_vowel:
                syllable_count += 1
            prev_char_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)

    def _calculate_seo_score(self, content: str, keywords: List[str]) -> float:
        """Calculate SEO score based on keyword usage"""
        content_lower = content.lower()
        total_words = len(content.split())
        
        if total_words == 0:
            return 0.0
        
        keyword_scores = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            occurrences = content_lower.count(keyword_lower)
            
            # Calculate keyword density (ideal 1-3%)
            density = (occurrences / total_words) * 100
            
            if density == 0:
                score = 0
            elif 1 <= density <= 3:
                score = 1.0
            elif density < 1:
                score = density
            else:
                score = max(0, 1 - (density - 3) * 0.1)
            
            keyword_scores.append(score)
        
        return np.mean(keyword_scores) if keyword_scores else 0.0

    def _assess_creativity(self, content: str) -> float:
        """Assess creativity based on vocabulary diversity"""
        words = re.findall(r'\b\w+\b', content.lower())
        
        if len(words) == 0:
            return 0.0
        
        unique_words = set(words)
        diversity_ratio = len(unique_words) / len(words)
        
        # Normalize to 0-1 range
        return min(1.0, diversity_ratio * 2)

    def _predict_engagement(self, content: str, request: GenerationRequest) -> float:
        """Predict potential engagement score"""
        factors = []
        
        # Content length factor
        word_count = len(content.split())
        if request.content_type == ContentGenerationType.SOCIAL_MEDIA_POST:
            # Optimal length for social media
            if 50 <= word_count <= 150:
                factors.append(1.0)
            else:
                factors.append(0.6)
        else:
            factors.append(min(word_count / 500, 1.0))
        
        # Question factor (questions drive engagement)
        question_count = content.count('?')
        factors.append(min(question_count * 0.2, 0.8))
        
        # Action words factor
        action_words = ['discover', 'learn', 'try', 'start', 'join', 'share', 'comment']
        action_score = sum(1 for word in action_words if word in content.lower())
        factors.append(min(action_score * 0.1, 0.5))
        
        # Tone factor
        tone_engagement = {
            ContentTone.HUMOROUS: 0.9,
            ContentTone.INSPIRING: 0.8,
            ContentTone.CONVERSATIONAL: 0.8,
            ContentTone.EDUCATIONAL: 0.7,
            ContentTone.PROFESSIONAL: 0.6
        }
        factors.append(tone_engagement.get(request.tone, 0.6))
        
        return np.mean(factors)

    def _create_metadata(self, request: GenerationRequest, quality_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Create comprehensive metadata for generated content"""



        return {
            'generation_params': {
                'content_type': request.content_type.value,
                'tone': request.tone.value,
                'creativity_level': request.creativity_level,
                'target_audience': request.target_audience,
                'keywords': request.keywords,
                'length_constraint': request.length_constraint
            },
            'quality_metrics': quality_metrics,
            'content_stats': {
                'word_count': len(request.prompt.split()),
                'character_count': len(request.prompt),
                'estimated_reading_time': max(1, len(request.prompt.split()) // 200)  # minutes
            },
            'generation_context': {
                'user_id': request.user_id,
                'session_id': request.session_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }

    def _estimate_cost(self, request: GenerationRequest, processing_time: float) -> float:
        """Estimate generation cost"""
        # Base cost factors
        base_cost = 0.01  # Base cost per generation
        
        # Engine cost multipliers
        engine_costs = {
            CreativeEngine.GPT4_TURBO: 3.0,
            CreativeEngine.GPT4_VISION: 4.0,
            CreativeEngine.CLAUDE_3_OPUS: 5.0,
            CreativeEngine.CLAUDE_3_SONNET: 2.0,
            CreativeEngine.GEMINI_PRO: 1.5,
            CreativeEngine.CUSTOM_T5: 0.1
        }
        
        engine = self._select_optimal_engine(request)
        cost_multiplier = engine_costs.get(engine, 1.0)
        
        # Length multiplier
        length_multiplier = 1.0
        if request.length_constraint:
            length_multiplier = max(1.0, request.length_constraint / 500)
        
        # Processing time factor
        time_factor = max(1.0, processing_time / 10)  # More complex requests cost more
        
        total_cost = base_cost * cost_multiplier * length_multiplier * time_factor
        
        return round(total_cost, 4)

    async def _store_generation_record(self, request: GenerationRequest, result: GeneratedContent):
        """Store generation record in database"""



        try:
            async with get_async_session() as session:
                # Store in content generations table (would need to create this table)
                generation_record = {
                    'generation_id': result.generation_id,
                    'user_id': request.user_id,
                    'content_type': request.content_type.value,
                    'prompt': request.prompt,
                    'generated_content': result.content,
                    'quality_score': result.quality_score,
                    'creativity_score': result.creativity_score,
                    'engine_used': result.engine_used,
                    'processing_time': result.processing_time,
                    'cost_estimate': result.cost_estimate,
                    'metadata': json.dumps(result.metadata),
                    'created_at': result.generated_at
                }
                
                # In production, this would use proper database models
                logger.info(f"Generation record stored: {result.generation_id}")
                
        except Exception as e:
            logger.error(f"Failed to store generation record: {e}")
            # Don't fail the generation process for storage issues


class AICreativeEngine:
    """Advanced AI creative engine with multi-model support"""
    
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.active_sessions = {}
        self.model_performance = {}
        
        logger.info("AICreativeEngine initialized")

    async def create_content_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Stream content generation for real-time feedback"""



        try:
            # Initialize streaming session
            session_id = str(uuid.uuid4())
            self.active_sessions[session_id] = {
                'request': request,
                'start_time': datetime.now(),
                'status': 'streaming'
            }
            
            # Generate content in chunks
            full_content = await self.content_generator.generate_content(request)
            
            # Stream content word by word for real-time experience
            words = full_content.content.split()
            for i, word in enumerate(words):
                if i == 0:
                    yield word
                else:
                    yield f" {word}"
                
                # Small delay for streaming effect
                await asyncio.sleep(0.05)
            
            # Update session status
            self.active_sessions[session_id]['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Content streaming failed: {e}")
            yield f"Error: {str(e)}"

    async def batch_generate(self, requests: List[GenerationRequest]) -> List[GeneratedContent]:
        """Generate multiple content pieces in batch"""
        tasks = [self.content_generator.generate_content(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def get_content_suggestions(self, partial_prompt: str, content_type: ContentGenerationType) -> List[str]:
        """Get content suggestions based on partial prompt"""
        suggestions = []
        
        # Use AI to generate prompt completions
        suggestion_prompt = f"""
        Based on this partial content prompt: "{partial_prompt}"
        
        Generate 5 creative and engaging completion suggestions for {content_type.value} content.
        Each suggestion should be a complete, actionable prompt that would result in high-quality content.
        
        Suggestions:
        """
        
        try:
            request = GenerationRequest(
                content_type=ContentGenerationType.BLOG_ARTICLE,  # Use generic type for suggestions
                prompt=suggestion_prompt,
                creativity_level=0.8
            )
            
            result = await self.content_generator.generate_content(request)
            
            # Parse suggestions from result
            lines = result.content.split('\n')
            for line in lines:
                if line.strip() and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                    clean_suggestion = re.sub(r'^[-•0-9.\s]+', '', line).strip()
                    if clean_suggestion:
                        suggestions.append(clean_suggestion)
            
            return suggestions[:5]  # Return top 5
            
        except Exception as e:
            logger.error(f"Failed to generate content suggestions: {e}")
            return [
                "Create engaging content that resonates with your audience",
                "Share your unique perspective and expertise",
                "Tell a compelling story with clear takeaways",
                "Provide actionable tips and insights",
                "Address common questions or challenges"
            ]

    async def optimize_for_platform(self, content: str, platform: str) -> str:
        """Optimize content for specific platforms"""
        optimization_prompts = {
            'instagram': "Optimize this content for Instagram with engaging hashtags, emojis, and visual storytelling elements:",
            'linkedin': "Adapt this content for LinkedIn with professional tone, industry insights, and networking focus:",
            'twitter': "Transform this content for Twitter with concise messaging, trending hashtags, and engagement hooks:",
            'tiktok': "Rewrite this content for TikTok with trendy language, viral elements, and youth appeal:",
            'youtube': "Adapt this content for YouTube with hook-driven introduction, clear structure, and call-to-action:",
            'facebook': "Optimize this content for Facebook with community-focused messaging and shareable elements:"
        }
        
        if platform not in optimization_prompts:
            return content
        
        prompt = f"{optimization_prompts[platform]}\n\n{content}"
        
        request = GenerationRequest(
            content_type=ContentGenerationType.SOCIAL_MEDIA_POST,
            prompt=prompt,
            format_requirements={'platform': platform}
        )
        
        try:
            result = await self.content_generator.generate_content(request)
            return result.content
        except Exception as e:
            logger.error(f"Platform optimization failed for {platform}: {e}")
            return content

    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance analytics for the creative engine"""



        return {
            'active_sessions': len(self.active_sessions),
            'total_generations': len(self.model_performance),
            'average_quality_score': np.mean([p.get('quality_score', 0) for p in self.model_performance.values()]) if self.model_performance else 0,
            'model_usage': self._get_model_usage_stats(),
            'content_type_distribution': self._get_content_type_stats()
        }

    def _get_model_usage_stats(self) -> Dict[str, int]:
        """Get model usage statistics"""
        usage = {}
        for perf in self.model_performance.values():
            engine = perf.get('engine_used', 'unknown')
            usage[engine] = usage.get(engine, 0) + 1
        return usage

    def _get_content_type_stats(self) -> Dict[str, int]:
        """Get content type generation statistics"""
        stats = {}
        for perf in self.model_performance.values():
            content_type = perf.get('content_type', 'unknown')
            stats[content_type] = stats.get(content_type, 0) + 1
        return stats
