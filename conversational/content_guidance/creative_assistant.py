"""Creative Assistant - AI-Powered Content Creation and Ideation System
==================================================================

This module provides comprehensive creative assistance, content ideation,
and AI-powered creation tools for content creators across all formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import random
import re
from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
import torch
import transformers
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
import cv2
from PIL import Image, ImageDraw, ImageFont
import librosa
import requests
from textblob import TextBlob

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.ai.content_generation import ContentGenerationEngine
from backend.ai.ml.creativity_analyzer import CreativityAnalysisEngine
from backend.integrations.platform_apis import PlatformAPIManager
from backend.utils.image_processing import ImageProcessor
from backend.utils.audio_processing import AudioProcessor

logger = get_logger(__name__)
settings = get_settings()


class ContentType(Enum):
    """
Types of content that can be created."""

    TEXT_POST = "text_post"
    IMAGE_POST = "image_post"
    VIDEO_POST = "video_post"
    STORY = "story"
    REEL = "reel"
    TIKTOK_VIDEO = "tiktok_video"
    YOUTUBE_VIDEO = "youtube_video"
    PODCAST = "podcast"
    MUSIC_TRACK = "music_track"
    BLOG_POST = "blog_post"
    CAROUSEL = "carousel"
    LIVE_STREAM = "live_stream"


class CreativeStyle(Enum):
    """Creative styles for content generation."""

    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    INSPIRATIONAL = "inspirational"
    PROMOTIONAL = "promotional"
    BEHIND_SCENES = "behind_scenes"
    TUTORIAL = "tutorial"
    STORYTELLING = "storytelling"
    HUMOROUS = "humorous"
    EMOTIONAL = "emotional"
    MINIMALIST = "minimalist"
    BOLD = "bold"
    ARTISTIC = "artistic"


class IdeationType(Enum):
    """Types of content ideas."""

    TRENDING_TOPIC = "trending_topic"
    SEASONAL_CONTENT = "seasonal_content"
    USER_GENERATED = "user_generated"
    COLLABORATION = "collaboration"
    SERIES_CONCEPT = "series_concept"
    INTERACTIVE = "interactive"
    EDUCATIONAL_SERIES = "educational_series"
    CHALLENGE = "challenge"
    BEHIND_SCENES = "behind_scenes"
    PRODUCT_SHOWCASE = "product_showcase"


class CreativityLevel(Enum):
    """Levels of creativity for content generation."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    CREATIVE = "creative"
    EXPERIMENTAL = "experimental"
    AVANT_GARDE = "avant_garde"


@dataclass
class ContentIdea:
    """Content idea with detailed information."""
    idea_id: str
    title: str
    description: str
    content_type: ContentType
    creative_style: CreativeStyle
    ideation_type: IdeationType
    target_platforms: List[str]
    estimated_engagement: float
    difficulty_level: str
    time_to_create: int  # minutes
    required_resources: List[str]
    hashtag_suggestions: List[str]
    content_outline: List[str]
    visual_suggestions: List[str]
    audio_suggestions: List[str]
    call_to_action: str
    variations: List[str]
    trending_score: float
    originality_score: float
    viral_potential: float
    generated_at: datetime


@dataclass
class CreativeTemplate:
    """
Template for content creation."""
    template_id: str
    name: str
    content_type: ContentType
    style: CreativeStyle
    structure: List[str]
    placeholders: Dict[str, str]
    visual_guidelines: Dict[str, Any]
    text_guidelines: Dict[str, Any]
    audio_guidelines: Dict[str, Any]
    example_content: List[str]
    customization_options: List[str]
    success_rate: float


@dataclass
class ContentScript:
    """
Script for video or audio content."""
    script_id: str
    title: str
    content_type: ContentType
    duration: int  # seconds
    scenes: List[Dict[str, Any]]
    dialogue: List[str]
    visual_cues: List[str]
    audio_cues: List[str]
    props_needed: List[str]
    location_requirements: List[str]
    technical_notes: List[str]
    estimated_production_time: int
    difficulty_rating: float


@dataclass
class VisualConcept:
    """
Visual concept for content creation."""
    concept_id: str
    title: str
    description: str
    visual_style: str
    color_palette: List[str]
    composition_guidelines: List[str]
    lighting_suggestions: List[str]
    prop_suggestions: List[str]
    technical_specs: Dict[str, Any]
    inspiration_references: List[str]
    mood_board: List[str]
    adaptations: Dict[str, Any]


@dataclass
class AudioConcept:
    """
Audio concept for content creation."""
    concept_id: str
    title: str
    description: str
    genre: str
    mood: str
    tempo: int
    key: str
    instruments: List[str]
    sound_effects: List[str]
    vocal_style: str
    production_notes: List[str]
    reference_tracks: List[str]
    technical_requirements: Dict[str, Any]


@dataclass
class CreativeBrief:
    """
Comprehensive creative brief for content."""
    brief_id: str
    project_title: str
    objectives: List[str]
    target_audience: Dict[str, Any]
    key_messages: List[str]
    brand_guidelines: Dict[str, Any]
    content_ideas: List[ContentIdea]
    templates: List[CreativeTemplate]
    scripts: List[ContentScript]
    visual_concepts: List[VisualConcept]
    audio_concepts: List[AudioConcept]
    timeline: Dict[str, datetime]
    budget_considerations: List[str]
    success_metrics: List[str]
    approval_process: List[str]
    deliverables: List[str]
    created_at: datetime


class ContentIdeationEngine:
    """
    Advanced AI-powered content ideation engine that generates creative
    ideas based on trends, audience preferences, and performance data.
    """
    
    def __init__(self):
        """
Initialize the content ideation engine."""
        self.creativity_analyzer = CreativityAnalysisEngine()
        self.platform_manager = PlatformAPIManager()
        
        # AI models for text generation
        self.text_generator = pipeline(
            'text-generation',
            model='gpt2',
            tokenizer='gpt2'
        )
        
        # Topic modeling for trend analysis
        self.topic_modeler = LatentDirichletAllocation(
            n_components=20,
            random_state=42
        )
        
        # Text analysis tools
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english'
        )
        
        # Creative databases
        self.trending_topics = self._load_trending_topics()
        self.creative_prompts = self._load_creative_prompts()
        self.content_templates = self._load_content_templates()
        
        logger.info("Content ideation engine initialized successfully")
    
    def _load_trending_topics(self) -> Dict[str, List[str]]:
        """Load trending topics by category."""
        
        return {
            'technology': [
                'AI and machine learning', 'Virtual reality', 'Sustainable tech',
                'Blockchain innovations', 'IoT devices', 'Cybersecurity',
                'Remote work tools', 'Digital wellness'
            ],
            'lifestyle': [
                'Minimalism', 'Wellness routines', 'Sustainable living',
                'Plant-based nutrition', 'Mental health awareness',
                'Work-life balance', 'Self-care practices'
            ],
            'entertainment': [
                'Streaming platforms', 'Gaming culture', 'Pop culture trends',
                'Celebrity news', 'Movie reviews', 'Music discoveries',
                'Books and reading', 'Art and creativity'
            ],
            'business': [
                'Entrepreneurship', 'Digital marketing', 'E-commerce trends',
                'Personal branding', 'Leadership skills', 'Innovation',
                'Startup culture', 'Investment strategies'
            ],
            'education': [
                'Online learning', 'Skill development', 'Career advice',
                'Language learning', 'Professional development',
                'Study techniques', 'Educational technology'
            ]
        }
    
    def _load_creative_prompts(self) -> Dict[CreativeStyle, List[str]]:
        """
Load creative prompts by style."""
        
        return {
            CreativeStyle.EDUCATIONAL: [
                "Break down a complex topic into simple steps",
                "Share a surprising fact about your industry",
                "Explain common misconceptions in your field",
                "Create a beginner's guide to your expertise",
                "Share the evolution of trends in your niche"
            ],
            CreativeStyle.ENTERTAINING: [
                "Create a funny scenario related to your niche",
                "Share an embarrassing moment that taught you something",
                "Do a humorous take on industry stereotypes",
                "Create entertaining comparisons or analogies",
                "Share behind-the-scenes bloopers"
            ],
            CreativeStyle.INSPIRATIONAL: [
                "Share a personal transformation story",
                "Highlight someone who inspires you",
                "Discuss overcoming a major challenge",
                "Share motivational quotes with personal context",
                "Create content about pursuing dreams"
            ],
            CreativeStyle.STORYTELLING: [
                "Tell the origin story of your passion",
                "Share a day-in-the-life narrative",
                "Create a mini-documentary style post",
                "Tell the story behind a favorite project",
                "Share customer or fan success stories"
            ]
        }
    
    def _load_content_templates(self) -> Dict[ContentType, List[CreativeTemplate]]:
        """Load content templates by type."""
        
        templates = {}
        
        # Text post templates
        templates[ContentType.TEXT_POST] = [
            CreativeTemplate(
                template_id="tip_list",
                name="Tip List Template",
                content_type=ContentType.TEXT_POST,
                style=CreativeStyle.EDUCATIONAL,
                structure=[
                    "Hook question or statement",
                    "Introduction to topic",
                    "List of 3-5 tips",
                    "Call to action",
                    "Relevant hashtags"
                ],
                placeholders={
                    "topic": "Your expertise area",
                    "tips": "Actionable advice points",
                    "cta": "Engagement question"
                },
                visual_guidelines={},
                text_guidelines={
                    "tone": "Helpful and friendly",
                    "length": "150-300 words"
                },
                audio_guidelines={},
                example_content=[
                    "Want to improve your photography? Here are 5 game-changing tips:",
                    "Struggling with productivity? Try these proven methods:"
                ],
                customization_options=[
                    "Number of tips", "Formatting style", "Emoji usage"
                ],
                success_rate=0.75
            )
        ]
        
        # Video templates
        templates[ContentType.VIDEO_POST] = [
            CreativeTemplate(
                template_id="tutorial_video",
                name="Tutorial Video Template",
                content_type=ContentType.VIDEO_POST,
                style=CreativeStyle.EDUCATIONAL,
                structure=[
                    "Hook (first 3 seconds)",
                    "Problem introduction",
                    "Step-by-step solution",
                    "Results demonstration",
                    "Call to action"
                ],
                placeholders={
                    "problem": "Common issue in your niche",
                    "solution": "Your method or approach",
                    "result": "Expected outcome"
                },
                visual_guidelines={
                    "duration": "60-90 seconds",
                    "text_overlay": "Key points highlighted",
                    "transitions": "Quick cuts between steps"
                },
                text_guidelines={
                    "script_length": "150-200 words",
                    "speaking_pace": "Conversational"
                },
                audio_guidelines={
                    "background_music": "Upbeat and motivational",
                    "volume": "Background at 20% of voice"
                },
                example_content=[
                    "Stop making this common mistake!",
                    "Here's the right way to do it..."
                ],
                customization_options=[
                    "Video length", "Music style", "Text animation"
                ],
                success_rate=0.82
            )
        ]
        
        return templates
    
    async def generate_content_ideas(
        self,
        creator_profile: Dict[str, Any],
        target_platforms: List[str],
        creativity_level: CreativityLevel = CreativityLevel.MODERATE,
        idea_count: int = 10
    ) -> List[ContentIdea]:
        """
        Generate creative content ideas based on creator profile and preferences.
        
        Args:
            creator_profile: Creator's profile and preferences
            target_platforms: Platforms to create content for
            creativity_level: Level of creativity to apply
            idea_count: Number of ideas to generate
            
        Returns:
            List of content ideas
        """
        
        try:
            ideas = []
            
            # Analyze creator's niche and interests
            niche = creator_profile.get('niche', 'general')
            interests = creator_profile.get('interests', [])
            content_types = creator_profile.get('preferred_content_types', [])
            
            # Generate ideas using different approaches
            trend_ideas = await self._generate_trend_based_ideas(
                niche, target_platforms, idea_count // 3
            )
            ideas.extend(trend_ideas)
            
            # Generate creative prompt ideas
            prompt_ideas = await self._generate_prompt_based_ideas(
                interests, content_types, creativity_level, idea_count // 3
            )
            ideas.extend(prompt_ideas)
            
            # Generate audience-based ideas
            audience_ideas = await self._generate_audience_based_ideas(
                creator_profile, target_platforms, idea_count // 3
            )
            ideas.extend(audience_ideas)
            
            # Score and rank ideas
            scored_ideas = await self._score_and_rank_ideas(
                ideas, creator_profile, target_platforms
            )
            
            logger.info(f"Generated {len(scored_ideas)} content ideas")
            return scored_ideas[:idea_count]
            
        except Exception as e:
            logger.error(f"Failed to generate content ideas: {e}")
            return []
    
    async def _generate_trend_based_ideas(
        self,
        niche: str,
        platforms: List[str],
        count: int
    ) -> List[ContentIdea]:
        """Generate ideas based on trending topics."""
        
        ideas = []
        trending_topics = self.trending_topics.get(niche, self.trending_topics['lifestyle'])
        
        for i in range(count):
            topic = random.choice(trending_topics)
            content_type = random.choice(list(ContentType))
            style = random.choice(list(CreativeStyle))
            
            # Generate idea based on topic
            idea_title = f"{style.value.title()} content about {topic}"
            description = await self._generate_idea_description(topic, content_type, style)
            
            idea = ContentIdea(
                idea_id=f"trend_idea_{i}_{int(datetime.now().timestamp())}",
                title=idea_title,
                description=description,
                content_type=content_type,
                creative_style=style,
                ideation_type=IdeationType.TRENDING_TOPIC,
                target_platforms=platforms,
                estimated_engagement=random.uniform(0.04, 0.12),
                difficulty_level=random.choice(['Easy', 'Medium', 'Hard']),
                time_to_create=random.randint(30, 180),
                required_resources=self._generate_required_resources(content_type),
                hashtag_suggestions=self._generate_hashtags(topic, niche),
                content_outline=self._generate_content_outline(content_type, topic),
                visual_suggestions=self._generate_visual_suggestions(content_type),
                audio_suggestions=self._generate_audio_suggestions(content_type),
                call_to_action=self._generate_call_to_action(style),
                variations=self._generate_variations(topic, content_type),
                trending_score=random.uniform(0.6, 0.95),
                originality_score=random.uniform(0.4, 0.8),
                viral_potential=random.uniform(0.3, 0.9),
                generated_at=datetime.now(timezone.utc)
            )
            ideas.append(idea)
        
        return ideas
    
    async def _generate_prompt_based_ideas(
        self,
        interests: List[str],
        content_types: List[str],
        creativity_level: CreativityLevel,
        count: int
    ) -> List[ContentIdea]:
        """Generate ideas based on creative prompts."""
        
        ideas = []
        
        for i in range(count):
            style = random.choice(list(CreativeStyle))
            prompts = self.creative_prompts.get(style, [])
            
            if prompts:
                prompt = random.choice(prompts)
                interest = random.choice(interests) if interests else "general content"
                content_type = ContentType(random.choice(content_types)) if content_types else random.choice(list(ContentType))
                
                # Adapt creativity based on level
                creativity_multiplier = {
                    CreativityLevel.CONSERVATIVE: 0.6,
                    CreativityLevel.MODERATE: 0.8,
                    CreativityLevel.CREATIVE: 1.0,
                    CreativityLevel.EXPERIMENTAL: 1.2,
                    CreativityLevel.AVANT_GARDE: 1.5
                }[creativity_level]
                
                idea_title = f"{prompt} - {interest} edition"
                description = await self._generate_creative_description(
                    prompt, interest, content_type, creativity_multiplier
                )
                
                idea = ContentIdea(
                    idea_id=f"prompt_idea_{i}_{int(datetime.now().timestamp())}",
                    title=idea_title,
                    description=description,
                    content_type=content_type,
                    creative_style=style,
                    ideation_type=IdeationType.USER_GENERATED,
                    target_platforms=['instagram', 'tiktok'],
                    estimated_engagement=random.uniform(0.03, 0.10) * creativity_multiplier,
                    difficulty_level=self._determine_difficulty(creativity_level),
                    time_to_create=random.randint(45, 240),
                    required_resources=self._generate_required_resources(content_type),
                    hashtag_suggestions=self._generate_hashtags(interest, 'creative'),
                    content_outline=self._generate_creative_outline(prompt, interest),
                    visual_suggestions=self._generate_visual_suggestions(content_type),
                    audio_suggestions=self._generate_audio_suggestions(content_type),
                    call_to_action=self._generate_call_to_action(style),
                    variations=self._generate_creative_variations(prompt, interest),
                    trending_score=random.uniform(0.4, 0.8),
                    originality_score=random.uniform(0.6, 0.95) * creativity_multiplier,
                    viral_potential=random.uniform(0.4, 0.8) * creativity_multiplier,
                    generated_at=datetime.now(timezone.utc)
                )
                ideas.append(idea)
        
        return ideas
    
    async def _generate_audience_based_ideas(
        self,
        creator_profile: Dict[str, Any],
        platforms: List[str],
        count: int
    ) -> List[ContentIdea]:
        """Generate ideas based on audience preferences and data."""
        
        ideas = []
        audience_data = creator_profile.get('audience_insights', {})
        
        # Audience preferences
        preferred_content = audience_data.get('preferred_content_types', ['educational', 'entertaining'])
        demographics = audience_data.get('demographics', {})
        engagement_patterns = audience_data.get('engagement_patterns', {})
        
        for i in range(count):
            # Choose content type based on audience preferences
            content_preference = random.choice(preferred_content)
            content_type = self._map_preference_to_content_type(content_preference)
            style = self._map_preference_to_style(content_preference)
            
            # Generate audience-focused idea
            idea_title = f"Audience-requested: {content_preference} content"
            description = await self._generate_audience_focused_description(
                content_preference, demographics, content_type
            )
            
            idea = ContentIdea(
                idea_id=f"audience_idea_{i}_{int(datetime.now().timestamp())}",
                title=idea_title,
                description=description,
                content_type=content_type,
                creative_style=style,
                ideation_type=IdeationType.USER_GENERATED,
                target_platforms=platforms,
                estimated_engagement=random.uniform(0.05, 0.15),  # Higher for audience-focused
                difficulty_level=random.choice(['Easy', 'Medium']),
                time_to_create=random.randint(30, 120),
                required_resources=self._generate_required_resources(content_type),
                hashtag_suggestions=self._generate_audience_hashtags(demographics),
                content_outline=self._generate_audience_outline(content_preference),
                visual_suggestions=self._generate_visual_suggestions(content_type),
                audio_suggestions=self._generate_audio_suggestions(content_type),
                call_to_action=self._generate_audience_cta(engagement_patterns),
                variations=self._generate_audience_variations(content_preference),
                trending_score=random.uniform(0.5, 0.8),
                originality_score=random.uniform(0.3, 0.7),
                viral_potential=random.uniform(0.6, 0.9),  # Higher for audience-focused
                generated_at=datetime.now(timezone.utc)
            )
            ideas.append(idea)
        
        return ideas
    
    async def _generate_idea_description(
        self, topic: str, content_type: ContentType, style: CreativeStyle
    ) -> str:
        """Generate detailed description for a content idea."""
        
        # Create contextual prompt for text generation
        prompt = f"Create {style.value} {content_type.value} about {topic}:"
        
        try:
            # Generate description using AI
            generated = self.text_generator(
                prompt,
                max_length=100,
                num_return_sequences=1,
                temperature=0.8,
                do_sample=True
            )
            
            description = generated[0]['generated_text'].replace(prompt, '').strip()
            
            # Clean and enhance the description
            description = self._enhance_description(description, topic, content_type, style)
            
        except Exception as e:
            logger.warning(f"AI generation failed, using template: {e}")
            description = self._generate_template_description(topic, content_type, style)
        
        return description
    
    def _enhance_description(
        self, description: str, topic: str, content_type: ContentType, style: CreativeStyle
    ) -> str:
        """Enhance and refine the generated description."""
        
        # Add specific elements based on content type
        if content_type in [ContentType.VIDEO_POST, ContentType.REEL, ContentType.TIKTOK_VIDEO]:
            description += f" This {content_type.value} will feature dynamic visuals and engaging transitions."
        
        elif content_type == ContentType.TEXT_POST:
            description += f" The post will include actionable insights and encourage community discussion."
        
        elif content_type == ContentType.PODCAST:
            description += f" This episode will include expert interviews and practical takeaways."
        
        # Add style-specific elements
        if style == CreativeStyle.EDUCATIONAL:
            description += " Designed to inform and educate the audience with clear explanations."
        elif style == CreativeStyle.ENTERTAINING:
            description += " Created to entertain and engage with humor and relatability."
        elif style == CreativeStyle.INSPIRATIONAL:
            description += " Aimed at motivating and inspiring positive action."
        
        return description
    
    def _generate_template_description(
        self, topic: str, content_type: ContentType, style: CreativeStyle
    ) -> str:
        """Generate description using templates as fallback."""
        
        templates = {
            CreativeStyle.EDUCATIONAL: f"An informative {content_type.value} that breaks down {topic} in an easy-to-understand way.",
            CreativeStyle.ENTERTAINING: f"A fun and engaging {content_type.value} that puts an entertaining spin on {topic}.",
            CreativeStyle.INSPIRATIONAL: f"An uplifting {content_type.value} that uses {topic} to inspire and motivate your audience.",
            CreativeStyle.TUTORIAL: f"A step-by-step {content_type.value} tutorial covering the essentials of {topic}.",
            CreativeStyle.STORYTELLING: f"A compelling {content_type.value} that tells a story related to {topic}."
        }
        
        return templates.get(style, f"Creative {content_type.value} content about {topic}")
    
    def _generate_required_resources(self, content_type: ContentType) -> List[str]:
        """Generate list of required resources for content creation."""
        
        resource_map = {
            ContentType.TEXT_POST: ['Smartphone', 'Basic editing app'],
            ContentType.IMAGE_POST: ['Camera/smartphone', 'Photo editing software', 'Props'],
            ContentType.VIDEO_POST: ['Camera', 'Video editing software', 'Tripod', 'Lighting'],
            ContentType.REEL: ['Smartphone', 'Video editing app', 'Props', 'Music'],
            ContentType.TIKTOK_VIDEO: ['Smartphone', 'TikTok app', 'Props', 'Trending audio'],
            ContentType.YOUTUBE_VIDEO: ['Camera', 'Professional editing software', 'Microphone', 'Lighting kit'],
            ContentType.PODCAST: ['Microphone', 'Audio editing software', 'Quiet recording space'],
            ContentType.MUSIC_TRACK: ['Instruments', 'Audio recording software', 'Studio time']
        }
        
        return resource_map.get(content_type, ['Basic equipment'])
    
    def _generate_hashtags(self, topic: str, niche: str) -> List[str]:
        """
Generate relevant hashtags for the content."""
        
        # Extract keywords from topic
        keywords = topic.lower().split()
        
        hashtags = []
        
        # Add topic-specific hashtags
        for keyword in keywords:
            hashtags.append(f"#{keyword}")
        
        # Add niche-specific hashtags
        niche_hashtags = {
            'technology': ['#tech', '#innovation', '#digital', '#future'],
            'lifestyle': ['#lifestyle', '#wellness', '#selfcare', '#mindfulness'],
            'business': ['#entrepreneur', '#business', '#success', '#growth'],
            'education': ['#learning', '#education', '#skills', '#knowledge'],
            'creative': ['#creative', '#art', '#inspiration', '#design']
        }
        
        hashtags.extend(niche_hashtags.get(niche, ['#content', '#creator']))
        
        # Add popular general hashtags
        hashtags.extend(['#viral', '#trending', '#fyp', '#explore'])
        
        return hashtags[:15]  # Limit to 15 hashtags
    
    def _generate_content_outline(self, content_type: ContentType, topic: str) -> List[str]:
        """Generate content outline based on type and topic."""
        
        outlines = {
            ContentType.TEXT_POST: [
                f"Hook: Attention-grabbing statement about {topic}",
                f"Main content: Key insights about {topic}",
                f"Value proposition: Why this matters to audience",
                "Call to action: Engagement question or request"
            ],
            ContentType.VIDEO_POST: [
                "Hook (0-3 seconds): Visual or verbal attention grabber",
                f"Introduction (3-10 seconds): Introduce {topic}",
                f"Main content (10-45 seconds): Demonstrate or explain {topic}",
                "Call to action (45-60 seconds): Ask for engagement"
            ],
            ContentType.YOUTUBE_VIDEO: [
                f"Introduction: Welcome and topic introduction ({topic})",
                f"Main segments: Deep dive into {topic}",
                "Practical examples or demonstrations",
                "Summary and key takeaways",
                "Call to action: Subscribe, comment, or next steps"
            ]
        }
        
        return outlines.get(content_type, [f"Create engaging content about {topic}"])
    
    def _generate_visual_suggestions(self, content_type: ContentType) -> List[str]:
        """Generate visual suggestions for content."""
        
        visual_suggestions = {
            ContentType.TEXT_POST: [
                "Colorful background with contrasting text",
                "Branded template with consistent fonts",
                "Relevant stock photos or graphics"
            ],
            ContentType.IMAGE_POST: [
                "High-quality, well-lit photography",
                "Consistent color palette",
                "Clear focal point and composition"
            ],
            ContentType.VIDEO_POST: [
                "Dynamic camera movements",
                "Text overlays for key points",
                "Consistent visual branding",
                "Good lighting throughout"
            ],
            ContentType.REEL: [
                "Quick cuts and transitions",
                "Trending visual effects",
                "Eye-catching thumbnails",
                "Vertical orientation optimization"
            ]
        }
        
        return visual_suggestions.get(content_type, ["Focus on visual appeal and brand consistency"])
    
    def _generate_audio_suggestions(self, content_type: ContentType) -> List[str]:
        """Generate audio suggestions for content."""
        
        audio_suggestions = {
            ContentType.VIDEO_POST: [
                "Clear, crisp voice recording",
                "Background music at 20% volume",
                "Sound effects for emphasis"
            ],
            ContentType.REEL: [
                "Trending audio or music",
                "Sync movements to beat",
                "Clear voice-over if speaking"
            ],
            ContentType.TIKTOK_VIDEO: [
                "Popular TikTok sounds",
                "Original audio for unique content",
                "Music that matches content mood"
            ],
            ContentType.PODCAST: [
                "Professional microphone quality",
                "Consistent audio levels",
                "Minimal background noise",
                "Intro and outro music"
            ]
        }
        
        return audio_suggestions.get(content_type, ["Focus on clear, quality audio"])
    
    def _generate_call_to_action(self, style: CreativeStyle) -> str:
        """Generate appropriate call to action based on style."""
        
        cta_templates = {
            CreativeStyle.EDUCATIONAL: "What questions do you have about this topic? Ask in the comments!",
            CreativeStyle.ENTERTAINING: "Tag someone who needs to see this! What's your take?",
            CreativeStyle.INSPIRATIONAL: "Share your own experience in the comments - let's inspire each other!",
            CreativeStyle.TUTORIAL: "Try this technique and let me know how it worked for you!",
            CreativeStyle.STORYTELLING: "What's your story? Share it in the comments below!"
        }
        
        return cta_templates.get(style, "What do you think? Let me know in the comments!")
    
    def _generate_variations(self, topic: str, content_type: ContentType) -> List[str]:
        """Generate content variations."""
        
        variations = [
            f"Beginner's guide to {topic}",
            f"Advanced tips for {topic}",
            f"Common mistakes in {topic}",
            f"Behind the scenes of {topic}",
            f"{topic} vs alternatives comparison"
        ]
        
        # Add content-type specific variations
        if content_type in [ContentType.VIDEO_POST, ContentType.REEL]:
            variations.extend([
                f"Time-lapse version of {topic}",
                f"Before and after {topic}",
                f"Quick tips for {topic}"
            ])
        
        return variations[:5]
    
    async def _score_and_rank_ideas(
        self,
        ideas: List[ContentIdea],
        creator_profile: Dict[str, Any],
        platforms: List[str]
    ) -> List[ContentIdea]:
        """Score and rank content ideas based on various factors."""
        
        for idea in ideas:
            score = 0
            
            # Platform alignment score
            platform_match = len(set(idea.target_platforms) & set(platforms)) / len(platforms)
            score += platform_match * 0.2
            
            # Trending score
            score += idea.trending_score * 0.3
            
            # Originality score
            score += idea.originality_score * 0.2
            
            # Viral potential
            score += idea.viral_potential * 0.2
            
            # Creator niche alignment
            niche = creator_profile.get('niche', '')
            if niche.lower() in idea.description.lower():
                score += 0.1
            
            # Update the idea with calculated score
            idea.estimated_engagement = min(1.0, score)
        
        # Sort by estimated engagement (which now includes our scoring)
        return sorted(ideas, key=lambda x: x.estimated_engagement, reverse=True)
    
    def _map_preference_to_content_type(self, preference: str) -> ContentType:
        """
Map audience preference to content type."""
        
        mapping = {
            'educational': ContentType.TEXT_POST,
            'entertaining': ContentType.REEL,
            'tutorial': ContentType.VIDEO_POST,
            'behind_scenes': ContentType.STORY,
            'music': ContentType.MUSIC_TRACK,
            'podcast': ContentType.PODCAST
        }
        
        return mapping.get(preference, ContentType.TEXT_POST)
    
    def _map_preference_to_style(self, preference: str) -> CreativeStyle:
        """
Map audience preference to creative style."""
        
        mapping = {
            'educational': CreativeStyle.EDUCATIONAL,
            'entertaining': CreativeStyle.ENTERTAINING,
            'tutorial': CreativeStyle.TUTORIAL,
            'inspirational': CreativeStyle.INSPIRATIONAL,
            'humorous': CreativeStyle.HUMOROUS
        }
        
        return mapping.get(preference, CreativeStyle.EDUCATIONAL)
    
    def _determine_difficulty(self, creativity_level: CreativityLevel) -> str:
        """
Determine difficulty based on creativity level."""
        
        difficulty_map = {
            CreativityLevel.CONSERVATIVE: 'Easy',
            CreativityLevel.MODERATE: 'Medium',
            CreativityLevel.CREATIVE: 'Medium',
            CreativityLevel.EXPERIMENTAL: 'Hard',
            CreativityLevel.AVANT_GARDE: 'Expert'
        }
        
        return difficulty_map.get(creativity_level, 'Medium')


class CreativeAssistant:
    """
    Comprehensive creative assistance system that provides content creators
    with AI-powered ideation, templates, and creative guidance.
    """
    
    def __init__(self):
        """
Initialize the creative assistant."""
        self.ideation_engine = ContentIdeationEngine()
        self.content_generator = ContentGenerationEngine()
        
        # Creative databases
        self.template_library = self._build_template_library()
        self.inspiration_sources = self._load_inspiration_sources()
        
        logger.info("Creative assistant initialized successfully")
    
    def _build_template_library(self) -> Dict[str, List[CreativeTemplate]]:
        """Build comprehensive template library."""
        
        library = {}
        
        # Social media templates
        library['social_media'] = [
            CreativeTemplate(
                template_id="quote_template",
                name="Inspirational Quote Template",
                content_type=ContentType.IMAGE_POST,
                style=CreativeStyle.INSPIRATIONAL,
                structure=[
                    "Background image or solid color",
                    "Quote text in readable font",
                    "Attribution if applicable",
                    "Personal reflection or question",
                    "Call to action"
                ],
                placeholders={
                    "quote": "Inspirational quote text",
                    "reflection": "Your personal take",
                    "question": "Engagement question"
                },
                visual_guidelines={
                    "font_size": "Large and readable",
                    "contrast": "High contrast for readability",
                    "brand_colors": "Use consistent brand palette"
                },
                text_guidelines={
                    "quote_length": "Under 100 characters",
                    "reflection_length": "50-150 words"
                },
                audio_guidelines={},
                example_content=[
                    "'Success is not final, failure is not fatal...'",
                    "'The only way to do great work is to love what you do'"
                ],
                customization_options=[
                    "Background style", "Font choice", "Color scheme"
                ],
                success_rate=0.78
            )
        ]
        
        # Video content templates
        library['video_content'] = [
            CreativeTemplate(
                template_id="before_after",
                name="Before and After Template",
                content_type=ContentType.VIDEO_POST,
                style=CreativeStyle.EDUCATIONAL,
                structure=[
                    "Hook: 'Watch this transformation'",
                    "Show 'before' state clearly",
                    "Quick transition or montage",
                    "Reveal 'after' result",
                    "Explain the process briefly",
                    "Call to action"
                ],
                placeholders={
                    "transformation": "What changed",
                    "process": "How it was done",
                    "timeframe": "How long it took"
                },
                visual_guidelines={
                    "duration": "30-60 seconds",
                    "split_screen": "Consider side-by-side comparison",
                    "transitions": "Clean cuts or wipes"
                },
                text_guidelines={
                    "narration": "Clear and concise explanation",
                    "text_overlay": "Highlight key points"
                },
                audio_guidelines={
                    "background_music": "Upbeat and motivational",
                    "voice_over": "Clear narration throughout"
                },
                example_content=[
                    "Room makeover in 30 seconds",
                    "Makeup transformation tutorial",
                    "Before/after workout results"
                ],
                customization_options=[
                    "Transition style", "Music choice", "Text placement"
                ],
                success_rate=0.85
            )
        ]
        
        return library
    
    def _load_inspiration_sources(self) -> Dict[str, List[str]]:
        """Load inspiration sources for creative content."""
        
        return {
            'visual_inspiration': [
                'Nature photography',
                'Architecture and design',
                'Street art and murals',
                'Fashion and style',
                'Food and culinary arts',
                'Travel destinations',
                'Abstract and geometric patterns'
            ],
            'audio_inspiration': [
                'Ambient and atmospheric sounds',
                'Classical and orchestral music',
                'Electronic and synthesized music',
                'World music and cultural sounds',
                'Nature sounds and field recordings',
                'Urban soundscapes',
                'Vintage and retro audio'
            ],
            'content_inspiration': [
                'Personal growth and development',
                'Technology and innovation',
                'Art and creativity',
                'Science and discovery',
                'Culture and society',
                'Health and wellness',
                'Environmental awareness'
            ]
        }
    
    async def create_creative_brief(
        self,
        project_requirements: Dict[str, Any],
        creator_profile: Dict[str, Any]
    ) -> CreativeBrief:
        """
        Create comprehensive creative brief for content project.
        
        Args:
            project_requirements: Project specifications and goals
            creator_profile: Creator's profile and preferences
            
        Returns:
            Detailed creative brief
        """
        
        try:
            # Extract project details
            project_title = project_requirements.get('title', 'Content Creation Project')
            objectives = project_requirements.get('objectives', [])
            target_audience = project_requirements.get('target_audience', {})
            timeline = project_requirements.get('timeline', {})
            
            # Generate content ideas
            content_ideas = await self.ideation_engine.generate_content_ideas(
                creator_profile=creator_profile,
                target_platforms=project_requirements.get('platforms', ['instagram']),
                creativity_level=CreativityLevel.CREATIVE,
                idea_count=10
            )
            
            # Select appropriate templates
            templates = self._select_templates_for_brief(content_ideas)
            
            # Generate scripts for video content
            scripts = await self._generate_scripts_for_brief(content_ideas)
            
            # Create visual and audio concepts
            visual_concepts = self._generate_visual_concepts(content_ideas)
            audio_concepts = self._generate_audio_concepts(content_ideas)
            
            brief = CreativeBrief(
                brief_id=f"brief_{int(datetime.now().timestamp())}",
                project_title=project_title,
                objectives=objectives,
                target_audience=target_audience,
                key_messages=project_requirements.get('key_messages', []),
                brand_guidelines=creator_profile.get('brand_guidelines', {}),
                content_ideas=content_ideas,
                templates=templates,
                scripts=scripts,
                visual_concepts=visual_concepts,
                audio_concepts=audio_concepts,
                timeline=timeline,
                budget_considerations=project_requirements.get('budget_notes', []),
                success_metrics=project_requirements.get('success_metrics', []),
                approval_process=project_requirements.get('approval_process', []),
                deliverables=project_requirements.get('deliverables', []),
                created_at=datetime.now(timezone.utc)
            )
            
            logger.info(f"Creative brief created: {brief.brief_id}")
            return brief
            
        except Exception as e:
            logger.error(f"Failed to create creative brief: {e}")
            raise
    
    def _select_templates_for_brief(self, content_ideas: List[ContentIdea]) -> List[CreativeTemplate]:
        """Select appropriate templates based on content ideas."""
        
        templates = []
        
        for idea in content_ideas[:5]:  # Top 5 ideas
            # Find matching templates
            for category, template_list in self.template_library.items():
                for template in template_list:
                    if (template.content_type == idea.content_type and 
                        template.style == idea.creative_style):
                        templates.append(template)
                        break
        
        return templates
    
    async def _generate_scripts_for_brief(self, content_ideas: List[ContentIdea]) -> List[ContentScript]:
        """
Generate scripts for video content in the brief."""
        
        scripts = []
        
        video_ideas = [
            idea for idea in content_ideas 
            if idea.content_type in [
                ContentType.VIDEO_POST, ContentType.REEL, 
                ContentType.TIKTOK_VIDEO, ContentType.YOUTUBE_VIDEO
            ]
        ]
        
        for idea in video_ideas[:3]:  # Generate scripts for top 3 video ideas
            script = await self._generate_content_script(idea)
            scripts.append(script)
        
        return scripts
    
    async def _generate_content_script(self, idea: ContentIdea) -> ContentScript:
        """
Generate detailed script for video content."""
        
        # Determine video duration based on content type
        duration_map = {
            ContentType.REEL: 30,
            ContentType.TIKTOK_VIDEO: 60,
            ContentType.VIDEO_POST: 90,
            ContentType.YOUTUBE_VIDEO: 300
        }
        
        duration = duration_map.get(idea.content_type, 60)
        
        # Generate scenes based on content outline
        scenes = []
        for i, outline_item in enumerate(idea.content_outline):
            scene = {
                'scene_number': i + 1,
                'duration': duration // len(idea.content_outline),
                'description': outline_item,
                'shot_type': random.choice(['Close-up', 'Medium shot', 'Wide shot']),
                'camera_movement': random.choice(['Static', 'Pan', 'Zoom', 'Tilt'])
            }
            scenes.append(scene)
        
        # Generate dialogue/narration
        dialogue = [
            f"Scene {i+1}: {scene['description']}" 
            for i, scene in enumerate(scenes)
        ]
        
        script = ContentScript(
            script_id=f"script_{idea.idea_id}",
            title=f"Script for {idea.title}",
            content_type=idea.content_type,
            duration=duration,
            scenes=scenes,
            dialogue=dialogue,
            visual_cues=idea.visual_suggestions,
            audio_cues=idea.audio_suggestions,
            props_needed=['Basic props', 'Lighting equipment'],
            location_requirements=['Well-lit indoor space'],
            technical_notes=['Ensure good audio quality', 'Maintain consistent lighting'],
            estimated_production_time=idea.time_to_create,
            difficulty_rating=0.7 if idea.difficulty_level == 'Medium' else 0.5
        )
        
        return script
    
    def _generate_visual_concepts(self, content_ideas: List[ContentIdea]) -> List[VisualConcept]:
        """Generate visual concepts for the content ideas."""
        
        visual_concepts = []
        
        # Generate concepts for top visual content ideas
        visual_ideas = [
            idea for idea in content_ideas 
            if idea.content_type in [
                ContentType.IMAGE_POST, ContentType.VIDEO_POST, 
                ContentType.CAROUSEL, ContentType.REEL
            ]
        ]
        
        for idea in visual_ideas[:3]:
            concept = VisualConcept(
                concept_id=f"visual_{idea.idea_id}",
                title=f"Visual concept for {idea.title}",
                description=f"Visual approach for {idea.content_type.value} content",
                visual_style=idea.creative_style.value,
                color_palette=self._generate_color_palette(idea.creative_style),
                composition_guidelines=[
                    'Rule of thirds composition',
                    'Leading lines for visual flow',
                    'Balanced element placement'
                ],
                lighting_suggestions=[
                    'Soft, even lighting',
                    'Avoid harsh shadows',
                    'Consider golden hour for warmth'
                ],
                prop_suggestions=idea.required_resources,
                technical_specs={
                    'resolution': '1080x1080' if 'instagram' in idea.target_platforms else '1080x1920',
                    'aspect_ratio': '1:1' if 'instagram' in idea.target_platforms else '9:16',
                    'file_format': 'MP4' if idea.content_type in [ContentType.VIDEO_POST, ContentType.REEL] else 'JPG'
                },
                inspiration_references=self.inspiration_sources['visual_inspiration'][:3],
                mood_board=['Energetic', 'Professional', 'Approachable'],
                adaptations={
                    'instagram': 'Square format with bold text',
                    'tiktok': 'Vertical format with dynamic elements',
                    'youtube': 'Thumbnail-optimized version'
                }
            )
            visual_concepts.append(concept)
        
        return visual_concepts
    
    def _generate_audio_concepts(self, content_ideas: List[ContentIdea]) -> List[AudioConcept]:
        """Generate audio concepts for content ideas."""
        
        audio_concepts = []
        
        # Generate concepts for audio-focused content
        audio_ideas = [
            idea for idea in content_ideas 
            if idea.content_type in [
                ContentType.VIDEO_POST, ContentType.REEL, 
                ContentType.TIKTOK_VIDEO, ContentType.PODCAST, ContentType.MUSIC_TRACK
            ]
        ]
        
        for idea in audio_ideas[:2]:
            concept = AudioConcept(
                concept_id=f"audio_{idea.idea_id}",
                title=f"Audio concept for {idea.title}",
                description=f"Audio approach for {idea.content_type.value}",
                genre=self._determine_audio_genre(idea.creative_style),
                mood=self._determine_audio_mood(idea.creative_style),
                tempo=self._determine_tempo(idea.content_type),
                key='C Major',  # Default key
                instruments=self._suggest_instruments(idea.content_type),
                sound_effects=self._suggest_sound_effects(idea.content_type),
                vocal_style='Conversational and clear',
                production_notes=[
                    'Maintain consistent volume levels',
                    'Use compression for voice clarity',
                    'Add subtle reverb for warmth'
                ],
                reference_tracks=self.inspiration_sources['audio_inspiration'][:2],
                technical_requirements={
                    'sample_rate': '44.1kHz',
                    'bit_depth': '24-bit',
                    'format': 'WAV for production, MP3 for delivery'
                }
            )
            audio_concepts.append(concept)
        
        return audio_concepts
    
    def _generate_color_palette(self, style: CreativeStyle) -> List[str]:
        """Generate color palette based on creative style."""
        
        palettes = {
            CreativeStyle.MINIMALIST: ['#FFFFFF', '#F5F5F5', '#333333', '#007ACC'],
            CreativeStyle.BOLD: ['#FF4757', '#FF6B35', '#F7931E', '#FFD23F'],
            CreativeStyle.EDUCATIONAL: ['#4A90E2', '#7ED321', '#F5A623', '#B8E986'],
            CreativeStyle.ENTERTAINING: ['#FF5733', '#C70039', '#900C3F', '#571845'],
            CreativeStyle.INSPIRATIONAL: ['#6C5CE7', '#A29BFE', '#FD79A8', '#FDCB6E'],
            CreativeStyle.ARTISTIC: ['#2D3436', '#636E72', '#DDD', '#E17055']
        }
        
        return palettes.get(style, ['#333333', '#666666', '#999999', '#CCCCCC'])
    
    def _determine_audio_genre(self, style: CreativeStyle) -> str:
        """
Determine audio genre based on creative style."""
        
        genre_map = {
            CreativeStyle.EDUCATIONAL: 'Corporate/Ambient',
            CreativeStyle.ENTERTAINING: 'Pop/Upbeat',
            CreativeStyle.INSPIRATIONAL: 'Cinematic/Orchestral',
            CreativeStyle.MINIMALIST: 'Ambient/Electronic',
            CreativeStyle.BOLD: 'Electronic/Dance'
        }
        
        return genre_map.get(style, 'Ambient')
    
    def _determine_audio_mood(self, style: CreativeStyle) -> str:
        """
Determine audio mood based on creative style."""
        
        mood_map = {
            CreativeStyle.EDUCATIONAL: 'Professional and clear',
            CreativeStyle.ENTERTAINING: 'Upbeat and energetic',
            CreativeStyle.INSPIRATIONAL: 'Uplifting and emotional',
            CreativeStyle.MINIMALIST: 'Calm and focused',
            CreativeStyle.BOLD: 'Dynamic and powerful'
        }
        
        return mood_map.get(style, 'Neutral')
    
    def _determine_tempo(self, content_type: ContentType) -> int:
        """
Determine appropriate tempo for content type."""
        
        tempo_map = {
            ContentType.REEL: 120,  # Upbeat
            ContentType.TIKTOK_VIDEO: 128,  # Dance tempo
            ContentType.VIDEO_POST: 100,  # Moderate
            ContentType.PODCAST: 80,  # Relaxed
            ContentType.MUSIC_TRACK: 110  # Versatile
        }
        
        return tempo_map.get(content_type, 100)
    
    def _suggest_instruments(self, content_type: ContentType) -> List[str]:
        """
Suggest instruments based on content type."""
        
        instrument_map = {
            ContentType.PODCAST: ['Voice', 'Subtle piano', 'Ambient pads'],
            ContentType.MUSIC_TRACK: ['Piano', 'Guitar', 'Strings', 'Drums'],
            ContentType.VIDEO_POST: ['Synth', 'Acoustic guitar', 'Light percussion'],
            ContentType.REEL: ['Electronic beats', 'Bass', 'Synth leads']
        }
        
        return instrument_map.get(content_type, ['Voice', 'Background music'])
    
    def _suggest_sound_effects(self, content_type: ContentType) -> List[str]:
        """
Suggest sound effects based on content type."""
        
        effects_map = {
            ContentType.VIDEO_POST: ['Transition whooshes', 'Button clicks', 'Success chimes'],
            ContentType.REEL: ['Pop sounds', 'Swoosh effects', 'Beat drops'],
            ContentType.TIKTOK_VIDEO: ['Viral sound effects', 'Comedy timing sounds'],
            ContentType.PODCAST: ['Intro/outro stingers', 'Transition music']
        }
        
        return effects_map.get(content_type, ['Subtle background elements'])
    
    async def generate_personalized_templates(
        self,
        creator_profile: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> List[CreativeTemplate]:
        """
        Generate personalized templates based on creator's style and performance.
        
        Args:
            creator_profile: Creator's profile and preferences
            performance_data: Historical performance data
            
        Returns:
            List of personalized templates
        """
        
        try:
            templates = []
            
            # Analyze successful content patterns
            successful_patterns = self._analyze_successful_patterns(performance_data)
            
            # Generate templates based on patterns
            for pattern in successful_patterns:
                template = self._create_template_from_pattern(pattern, creator_profile)
                templates.append(template)
            
            logger.info(f"Generated {len(templates)} personalized templates")
            return templates
            
        except Exception as e:
            logger.error(f"Failed to generate personalized templates: {e}")
            return []
    
    def _analyze_successful_patterns(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns from successful content."""
        
        # This would analyze actual performance data
        # For now, return sample patterns
        
        return [
            {
                'content_type': ContentType.REEL,
                'style': CreativeStyle.EDUCATIONAL,
                'avg_engagement': 0.08,
                'common_elements': ['Step-by-step format', 'Clear text overlays', 'Upbeat music']
            },
            {
                'content_type': ContentType.TEXT_POST,
                'style': CreativeStyle.INSPIRATIONAL,
                'avg_engagement': 0.06,
                'common_elements': ['Personal stories', 'Actionable advice', 'Questions for engagement']
            }
        ]
    
    def _create_template_from_pattern(
        self, pattern: Dict[str, Any], creator_profile: Dict[str, Any]
    ) -> CreativeTemplate:
        """
Create template based on successful pattern."""
        
        template = CreativeTemplate(
            template_id=f"personalized_{int(datetime.now().timestamp())}",
            name=f"Your High-Performing {pattern['content_type'].value} Template",
            content_type=pattern['content_type'],
            style=pattern['style'],
            structure=self._generate_structure_from_pattern(pattern),
            placeholders=self._generate_placeholders_from_pattern(pattern),
            visual_guidelines=self._generate_visual_guidelines_from_pattern(pattern),
            text_guidelines=self._generate_text_guidelines_from_pattern(pattern),
            audio_guidelines=self._generate_audio_guidelines_from_pattern(pattern),
            example_content=pattern.get('common_elements', []),
            customization_options=self._generate_customization_options(pattern),
            success_rate=pattern.get('avg_engagement', 0.05)
        )
        
        return template
    
    def _generate_structure_from_pattern(self, pattern: Dict[str, Any]) -> List[str]:
        """Generate template structure from successful pattern."""
        
        # Based on content type and style
        if pattern['content_type'] == ContentType.REEL and pattern['style'] == CreativeStyle.EDUCATIONAL:
            return [
                "Hook: Attention-grabbing question or statement",
                "Problem: What challenge are you solving?",
                "Solution: Step-by-step demonstration",
                "Result: Show the outcome",
                "Call to action: Encourage tries or questions"
            ]
        
        return [
            "Opening hook",
            "Main content delivery",
            "Value reinforcement", 
            "Engagement call to action"
        ]
    
    def _generate_placeholders_from_pattern(self, pattern: Dict[str, Any]) -> Dict[str, str]:
        """Generate template placeholders from pattern."""
        
        return {
            'hook': 'Attention-grabbing opener',
            'main_content': 'Core message or demonstration',
            'cta': 'Engagement question or request'
        }
    
    def _generate_visual_guidelines_from_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
Generate visual guidelines from pattern."""
        
        return {
            'duration': '30-60 seconds' if 'reel' in str(pattern['content_type']).lower() else 'N/A',
            'text_style': 'Clear, readable fonts',
            'branding': 'Consistent with creator style'
        }
    
    def _generate_text_guidelines_from_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
Generate text guidelines from pattern."""
        
        return {
            'tone': 'Conversational and helpful',
            'length': '100-200 words for captions'
        }
    
    def _generate_audio_guidelines_from_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
Generate audio guidelines from pattern."""
        
        return {
            'music_style': 'Upbeat and engaging',
            'voice_over': 'Clear and enthusiastic'
        }
    
    def _generate_customization_options(self, pattern: Dict[str, Any]) -> List[str]:
        """
Generate customization options for template."""
        
        return [
            'Color scheme adjustment',
            'Music selection',
            'Text animation style',
            'Duration modification'
        ]
