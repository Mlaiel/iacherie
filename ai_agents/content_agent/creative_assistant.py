"""
Creative Assistant - Advanced AI-Powered Creative Ideation and Content Enhancement

Ultra-advanced creative assistance system providing intelligent ideation, brainstorming,
and creative enhancement for all content types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
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
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import random
import uuid
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
import aiohttp
import requests
from transformers import (
    pipeline, AutoTokenizer, AutoModel,
    GPT2LMHeadModel, GPT2Tokenizer,
    T5ForConditionalGeneration, T5Tokenizer
)
import torch
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import openai
from openai import AsyncOpenAI
import anthropic
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, and_, or_, func
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException

from ...core.database import get_async_session
from ...core.config import get_settings
from ...models.users import User, UserProfile, CreatorProfile
from ...models.content import Content, ContentType, ContentIdea, CreativeSession
from ...ai.ml_models import AdvancedMLPipeline
from ...ai.llm_engine import UnifiedLLMEngine

logger = logging.getLogger(__name__)
settings = get_settings()


class IdeationType(str, Enum):
    """Types of creative ideas to generate"""
    CONTENT_CONCEPT = "content_concept"
    STORY_IDEA = "story_idea"
    MARKETING_ANGLE = "marketing_angle"
    VISUAL_CONCEPT = "visual_concept"
    TITLE_SUGGESTION = "title_suggestion"
    HOOK_IDEA = "hook_idea"
    CALL_TO_ACTION = "call_to_action"
    HASHTAG_SUGGESTION = "hashtag_suggestion"
    SERIES_CONCEPT = "series_concept"
    COLLABORATION_IDEA = "collaboration_idea"
    TREND_ADAPTATION = "trend_adaptation"
    PROBLEM_SOLUTION = "problem_solution"


class CreativeMethod(str, Enum):
    """Creative thinking methods"""
    BRAINSTORMING = "brainstorming"
    MIND_MAPPING = "mind_mapping"
    SCAMPER = "scamper"  # Substitute, Combine, Adapt, Modify, Put to another use, Eliminate, Reverse
    SIX_THINKING_HATS = "six_thinking_hats"
    RANDOM_WORD = "random_word"
    ANALOGICAL_THINKING = "analogical_thinking"
    REVERSE_THINKING = "reverse_thinking"
    WHAT_IF_SCENARIOS = "what_if_scenarios"
    CONSTRAINT_BASED = "constraint_based"
    TREND_ANALYSIS = "trend_analysis"


class CreativeDirection(str, Enum):
    """Creative directions for idea development"""
    INNOVATIVE = "innovative"
    TRENDING = "trending"
    CONTROVERSIAL = "controversial"
    EMOTIONAL = "emotional"
    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    INSPIRATIONAL = "inspirational"
    PRACTICAL = "practical"
    ARTISTIC = "artistic"
    COMMERCIAL = "commercial"


@dataclass
class CreativePrompt:
    """Structure for creative prompts and constraints"""
    topic: str
    context: Optional[str] = None
    target_audience: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    avoid_topics: List[str] = field(default_factory=list)
    creativity_level: float = 0.8
    quantity: int = 5
    method: Optional[CreativeMethod] = None
    direction: Optional[CreativeDirection] = None
    inspiration_sources: List[str] = field(default_factory=list)
    format_requirements: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class CreativeIdea:
    """Structure for generated creative ideas"""
    idea_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    concept: str = ""
    implementation_steps: List[str] = field(default_factory=list)
    target_audience: Optional[str] = None
    estimated_effort: str = "medium"  # low, medium, high
    potential_impact: float = 0.5  # 0-1 scale
    creativity_score: float = 0.5  # 0-1 scale
    feasibility_score: float = 0.5  # 0-1 scale
    originality_score: float = 0.5  # 0-1 scale
    tags: List[str] = field(default_factory=list)
    related_trends: List[str] = field(default_factory=list)
    inspiration_source: Optional[str] = None
    variations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    method_used: Optional[str] = None


@dataclass
class BrainstormingSession:
    """Structure for creative brainstorming sessions"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    topic: str = ""
    method: CreativeMethod = CreativeMethod.BRAINSTORMING
    ideas_generated: List[CreativeIdea] = field(default_factory=list)
    session_duration: Optional[float] = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    session_notes: str = ""
    constraints: List[str] = field(default_factory=list)
    quality_threshold: float = 0.6


class CreativeAssistant:
    """Advanced AI-powered creative assistant for content ideation"""
    
    def __init__(self):
        # Initialize AI clients
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Load ML models
        self.ml_pipeline = AdvancedMLPipeline()
        self.llm_engine = UnifiedLLMEngine()
        
        # Load specialized models
        self._load_creative_models()
        
        # Creative databases and patterns
        self.creative_patterns = self._load_creative_patterns()
        self.inspiration_databases = self._load_inspiration_databases()
        self.trend_tracker = self._initialize_trend_tracker()
        
        # Active sessions
        self.active_sessions = {}
        
        logger.info("CreativeAssistant initialized with AI engines")

    def _load_creative_models(self):
        """Load specialized models for creative tasks"""
        try:
            # Sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # GPT-2 for creative text generation
            self.gpt2_model = GPT2LMHeadModel.from_pretrained('gpt2-medium')
            self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')
            self.gpt2_tokenizer.pad_token = self.gpt2_tokenizer.eos_token
            
            # T5 for idea transformation
            self.t5_model = T5ForConditionalGeneration.from_pretrained('t5-base')
            self.t5_tokenizer = T5Tokenizer.from_pretrained('t5-base')
            
            # Creativity evaluation pipeline
            self.creativity_evaluator = pipeline(
                "text-classification", 
                model="microsoft/DialoGPT-medium"
            )
            
            logger.info("Creative models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading creative models: {e}")
            self.use_cloud_only = True

    def _load_creative_patterns(self) -> Dict[str, List[str]]:
        """Load creative thinking patterns and templates"""
        return {
            "story_structures": [
                "Hero's Journey", "Three-Act Structure", "Problem-Solution", 
                "Before-After", "Question-Answer", "List Format",
                "Case Study", "Personal Story", "How-To Guide"
            ],
            "hook_templates": [
                "What if I told you...", "The secret that changed...", 
                "Everyone thinks... but actually...", "The mistake I made...",
                "Why most people fail at...", "The surprising truth about...",
                "How to... in X minutes", "The one thing that..."
            ],
            "content_angles": [
                "Behind-the-scenes", "Day in the life", "Mistakes and lessons",
                "Predictions and trends", "Comparison and contrast", 
                "Tutorial and education", "Personal transformation",
                "Industry secrets", "Myth busting", "Q&A format"
            ],
            "creative_constraints": [
                "Use only 3 colors", "Tell story in reverse", "No adjectives allowed",
                "Under 100 words", "Use metaphors only", "Write as a conversation",
                "Include 5 specific words", "Set in unusual location"
            ],
            "trend_adaptation_methods": [
                "Apply to different industry", "Reverse the concept", 
                "Combine with personal experience", "Scale up/down dramatically",
                "Change the target audience", "Update with new technology",
                "Add educational element", "Make it interactive"
            ]
        }

    def _load_inspiration_databases(self) -> Dict[str, List[Dict]]:
        """Load databases of inspiration sources"""
        return {
            "creative_prompts": [
                {"prompt": "What would happen if gravity stopped working for 24 hours?", "category": "sci-fi"},
                {"prompt": "Describe a world where colors have sounds", "category": "fantasy"},
                {"prompt": "The last person on Earth finds a diary", "category": "post-apocalyptic"},
                {"prompt": "A child discovers their imaginary friend is real", "category": "magical-realism"}
            ],
            "random_words": [
                "serendipity", "metamorphosis", "wanderlust", "ephemeral", "cascade",
                "symphony", "kaleidoscope", "paradox", "renaissance", "infinity"
            ],
            "emotion_triggers": [
                {"emotion": "nostalgia", "triggers": ["childhood memories", "old photographs", "familiar scents"]},
                {"emotion": "curiosity", "triggers": ["mysteries", "unexpected results", "hidden truths"]},
                {"emotion": "hope", "triggers": ["new beginnings", "success stories", "possibility"]}
            ],
            "trend_categories": [
                "technology", "lifestyle", "social media", "entertainment", 
                "business", "health", "environment", "education", "travel"
            ]
        }

    def _initialize_trend_tracker(self):
        """Initialize trend tracking system"""
        return {
            "current_trends": [],
            "emerging_trends": [],
            "declining_trends": [],
            "last_updated": datetime.now(timezone.utc)
        }

    async def generate_ideas(self, prompt: CreativePrompt) -> List[CreativeIdea]:
        """Generate creative ideas based on prompt and method"""
        try:
            # Start brainstorming session
            session = BrainstormingSession(
                user_id=prompt.user_id,
                topic=prompt.topic,
                method=prompt.method or CreativeMethod.BRAINSTORMING,
                constraints=prompt.constraints,
                quality_threshold=0.6
            )
            
            self.active_sessions[session.session_id] = session
            
            # Generate ideas using specified method
            if prompt.method == CreativeMethod.BRAINSTORMING:
                ideas = await self._brainstorming_method(prompt)
            elif prompt.method == CreativeMethod.MIND_MAPPING:
                ideas = await self._mind_mapping_method(prompt)
            elif prompt.method == CreativeMethod.SCAMPER:
                ideas = await self._scamper_method(prompt)
            elif prompt.method == CreativeMethod.RANDOM_WORD:
                ideas = await self._random_word_method(prompt)
            elif prompt.method == CreativeMethod.ANALOGICAL_THINKING:
                ideas = await self._analogical_thinking_method(prompt)
            elif prompt.method == CreativeMethod.WHAT_IF_SCENARIOS:
                ideas = await self._what_if_scenarios_method(prompt)
            elif prompt.method == CreativeMethod.TREND_ANALYSIS:
                ideas = await self._trend_analysis_method(prompt)
            else:
                ideas = await self._brainstorming_method(prompt)  # Default
            
            # Evaluate and rank ideas
            ranked_ideas = await self._evaluate_and_rank_ideas(ideas, prompt)
            
            # Update session
            session.ideas_generated = ranked_ideas
            session.completed_at = datetime.now(timezone.utc)
            session.session_duration = (session.completed_at - session.started_at).total_seconds()
            
            # Store session
            await self._store_creative_session(session)
            
            logger.info(f"Generated {len(ranked_ideas)} creative ideas using {prompt.method}")
            return ranked_ideas[:prompt.quantity]
            
        except Exception as e:
            logger.error(f"Idea generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Idea generation failed: {str(e)}")

    async def _brainstorming_method(self, prompt: CreativePrompt) -> List[CreativeIdea]:
        """Generate ideas using AI-powered brainstorming"""
        brainstorm_prompt = f"""
        Generate creative ideas for: {prompt.topic}
        
        Context: {prompt.context or 'General creative content'}
        Target audience: {prompt.target_audience or 'General audience'}
        Keywords to include: {', '.join(prompt.keywords) if prompt.keywords else 'None'}
        Avoid topics: {', '.join(prompt.avoid_topics) if prompt.avoid_topics else 'None'}
        Creativity level: {'High' if prompt.creativity_level > 0.7 else 'Moderate'}
        
        Generate {prompt.quantity * 2} diverse, creative, and actionable ideas. 
        For each idea, provide:
        1. A catchy title
        2. A detailed description
        3. Core concept
        4. Why it would be engaging
        5. Implementation approach
        
        Be innovative, think outside the box, and consider current trends.
        """
        
        try:
            # Use OpenAI for brainstorming
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert creative strategist and idea generator."},
                    {"role": "user", "content": brainstorm_prompt}
                ],
                temperature=prompt.creativity_level,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            ideas = self._parse_brainstorming_response(content, CreativeMethod.BRAINSTORMING)
            
            return ideas
            
        except Exception as e:
            logger.error(f"Brainstorming method failed: {e}")
            return self._generate_fallback_ideas(prompt)

    async def _mind_mapping_method(self, prompt: CreativePrompt) -> List[CreativeIdea]:
        """Generate ideas using mind mapping technique"""
        # Create central concept and branches
        central_concept = prompt.topic
        
        # Generate related concepts
        association_prompt = f"""
        Create a mind map for: {central_concept}
        
        Generate 8 main branches (related concepts) and for each branch, 
        provide 3-4 sub-concepts. Then create content ideas from these connections.
        
        Format as: Branch -> Sub-concepts -> Content idea
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a creative mind mapping expert."},
                    {"role": "user", "content": association_prompt}
                ],
                temperature=prompt.creativity_level,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            ideas = self._parse_mind_map_response(content, CreativeMethod.MIND_MAPPING)
            
            return ideas
            
        except Exception as e:
            logger.error(f"Mind mapping method failed: {e}")
            return self._generate_fallback_ideas(prompt)

    async def _scamper_method(self, prompt: CreativePrompt) -> List[CreativeIdea]:
        """Generate ideas using SCAMPER technique"""
        scamper_questions = {
            "Substitute": f"What can be substituted in {prompt.topic}?",
            "Combine": f"What can be combined with {prompt.topic}?",
            "Adapt": f"How can {prompt.topic} be adapted for different uses?",
            "Modify": f"What can be modified or magnified in {prompt.topic}?",
            "Put to other use": f"How else can {prompt.topic} be used?",
            "Eliminate": f"What can be eliminated or minimized from {prompt.topic}?",
            "Reverse": f"What if {prompt.topic} was reversed or rearranged?"
        }
        
        ideas = []
        
        for technique, question in scamper_questions.items():
            scamper_prompt = f"""
            Using the SCAMPER technique - {technique}:
            
            Question: {question}
            Context: {prompt.context or 'Creative content development'}
            
            Generate 2 creative content ideas that answer this question.
            Each idea should be unique, actionable, and engaging.
            """
            
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a SCAMPER technique expert for creative ideation."},
                        {"role": "user", "content": scamper_prompt}
                    ],
                    temperature=prompt.creativity_level,
                    max_tokens=800
                )
                
                content = response.choices[0].message.content
                technique_ideas = self._parse_scamper_response(content, technique)
                ideas.extend(technique_ideas)
                
            except Exception as e:
                logger.error(f"SCAMPER {technique} failed: {e}")
        
        return ideas[:prompt.quantity * 2]

    async def _random_word_method(self, prompt: CreativePrompt) -> List[CreativeIdea]:
        """Generate ideas using random word association"""
        random_words = random.sample(self.inspiration_databases["random_words"], 5)
        
        ideas = []
        
        for word in random_words:
            association_prompt = f"""
            Create content ideas by connecting: {prompt.topic} with the random word "{word}"
            
            Find creative connections, analogies, or metaphors between these concepts.
            Generate 2 unique content ideas from this connection.
            
            Context: {prompt.context or 'Creative content'}
            Target audience: {prompt.target_audience or 'General'}
            """
            
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert at random word association for creativity."},
                        {"role": "user", "content": association_prompt}
                    ],
                    temperature=prompt.creativity_level,
                    max_tokens=600
                )
                
                content = response.choices[0].message.content
                word_ideas = self._parse_random_word_response(content, word)
                ideas.extend(word_ideas)
                
            except Exception as e:
                logger.error(f"Random word method failed for {word}: {e}")
        
        return ideas

    async def _analogical_thinking_method(self, prompt: CreativePrompt) -> List[CreativeIdea]:
        """Generate ideas using analogical thinking"""
        analogical_prompt = f"""
        Use analogical thinking to generate content ideas for: {prompt.topic}
        
        Think of analogies from these domains:
        1. Nature (animals, plants, natural phenomena)
        2. Sports and games
        3. Cooking and food
        4. Travel and exploration
        5. Architecture and construction
        
        For each domain, find an analogy to {prompt.topic} and create a content idea based on that analogy.
        
        Context: {prompt.context or 'Creative content'}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at analogical thinking for creative ideation."},
                    {"role": "user", "content": analogical_prompt}
                ],
                temperature=prompt.creativity_level,
                max_tokens=1200
            )
            
            content = response.choices[0].message.content
            ideas = self._parse_analogical_response(content, CreativeMethod.ANALOGICAL_THINKING)
            
            return ideas
            
        except Exception as e:
            logger.error(f"Analogical thinking method failed: {e}")
            return self._generate_fallback_ideas(prompt)

    async def _what_if_scenarios_method(self, prompt: CreativePrompt) -> List[CreativeIdea]:
        """Generate ideas using what-if scenarios"""
        scenarios = [
            f"What if {prompt.topic} was completely banned tomorrow?",
            f"What if {prompt.topic} could only be done by children?",
            f"What if {prompt.topic} was the most expensive thing in the world?",
            f"What if {prompt.topic} was discovered on Mars?",
            f"What if {prompt.topic} could talk?",
            f"What if {prompt.topic} existed in medieval times?",
            f"What if {prompt.topic} was invisible?",
            f"What if everyone had to do {prompt.topic} every day?"
        ]
        
        selected_scenarios = random.sample(scenarios, min(5, len(scenarios)))
        ideas = []
        
        for scenario in selected_scenarios:
            scenario_prompt = f"""
            Explore this hypothetical scenario: {scenario}
            
            Generate 2 creative content ideas based on this scenario.
            Think about the implications, consequences, and interesting angles.
            
            Context: {prompt.context or 'Creative exploration'}
            Make the ideas engaging and thought-provoking.
            """
            
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert at hypothetical scenario exploration."},
                        {"role": "user", "content": scenario_prompt}
                    ],
                    temperature=prompt.creativity_level,
                    max_tokens=700
                )
                
                content = response.choices[0].message.content
                scenario_ideas = self._parse_scenario_response(content, scenario)
                ideas.extend(scenario_ideas)
                
            except Exception as e:
                logger.error(f"What-if scenario failed for {scenario}: {e}")
        
        return ideas

    async def _trend_analysis_method(self, prompt: CreativePrompt) -> List[CreativeIdea]:
        """Generate ideas based on current trends analysis"""
        # Update trends if needed
        await self._update_trends_if_needed()
        
        trend_prompt = f"""
        Generate content ideas for: {prompt.topic}
        Based on current trends analysis.
        
        Current trending topics: {', '.join(self.trend_tracker.get('current_trends', [])[:5])}
        Emerging trends: {', '.join(self.trend_tracker.get('emerging_trends', [])[:3])}
        
        Create content ideas that:
        1. Incorporate trending elements
        2. Are timely and relevant
        3. Can capitalize on current interest
        4. Offer unique perspective on trends
        
        Generate {prompt.quantity} trend-based ideas.
        Context: {prompt.context or 'Trend-focused content'}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a trend analysis expert for content creation."},
                    {"role": "user", "content": trend_prompt}
                ],
                temperature=prompt.creativity_level,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            ideas = self._parse_trend_response(content, CreativeMethod.TREND_ANALYSIS)
            
            return ideas
            
        except Exception as e:
            logger.error(f"Trend analysis method failed: {e}")
            return self._generate_fallback_ideas(prompt)

    def _parse_brainstorming_response(self, content: str, method: CreativeMethod) -> List[CreativeIdea]:
        """Parse brainstorming response into structured ideas"""
        ideas = []
        
        # Split by numbered items or bullet points
        sections = re.split(r'\n\s*[\d\.\-\*]+\s*', content)
        
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            if len(section.strip()) < 20:  # Skip very short sections
                continue
            
            lines = section.strip().split('\n')
            
            # Extract title (first line)
            title = lines[0].strip().rstrip(':').strip('"\'')
            
            # Extract description (remaining lines)
            description_lines = [line.strip() for line in lines[1:] if line.strip()]
            description = ' '.join(description_lines)
            
            idea = CreativeIdea(
                title=title[:100],  # Limit title length
                description=description[:500],  # Limit description
                concept=title,
                creativity_score=random.uniform(0.6, 0.9),
                feasibility_score=random.uniform(0.5, 0.8),
                originality_score=random.uniform(0.6, 0.9),
                method_used=method.value,
                tags=['brainstorming', 'ai-generated']
            )
            
            ideas.append(idea)
        
        return ideas

    def _parse_mind_map_response(self, content: str, method: CreativeMethod) -> List[CreativeIdea]:
        """Parse mind map response into ideas"""
        # Similar parsing logic adapted for mind map structure
        return self._parse_brainstorming_response(content, method)

    def _parse_scamper_response(self, content: str, technique: str) -> List[CreativeIdea]:
        """Parse SCAMPER response into ideas"""
        ideas = []
        sections = content.split('\n\n')
        
        for section in sections:
            if len(section.strip()) < 30:
                continue
            
            lines = section.strip().split('\n')
            title = lines[0].strip().rstrip(':').strip('"\'')
            description = ' '.join(lines[1:])
            
            idea = CreativeIdea(
                title=title[:100],
                description=description[:500],
                concept=f"SCAMPER - {technique}",
                creativity_score=random.uniform(0.7, 0.95),
                originality_score=random.uniform(0.6, 0.9),
                method_used=f"scamper_{technique.lower()}",
                tags=['scamper', technique.lower(), 'systematic']
            )
            
            ideas.append(idea)
        
        return ideas

    def _parse_random_word_response(self, content: str, word: str) -> List[CreativeIdea]:
        """Parse random word association response"""
        ideas = self._parse_brainstorming_response(content, CreativeMethod.RANDOM_WORD)
        
        # Add random word context
        for idea in ideas:
            idea.inspiration_source = f"Random word: {word}"
            idea.tags.extend(['random-word', word])
            idea.creativity_score = min(1.0, idea.creativity_score + 0.1)  # Boost creativity score
        
        return ideas

    def _parse_analogical_response(self, content: str, method: CreativeMethod) -> List[CreativeIdea]:
        """Parse analogical thinking response"""
        ideas = self._parse_brainstorming_response(content, method)
        
        # Add analogical thinking context
        for idea in ideas:
            idea.tags.extend(['analogical', 'metaphor'])
            idea.creativity_score = min(1.0, idea.creativity_score + 0.15)
        
        return ideas

    def _parse_scenario_response(self, content: str, scenario: str) -> List[CreativeIdea]:
        """Parse what-if scenario response"""
        ideas = self._parse_brainstorming_response(content, CreativeMethod.WHAT_IF_SCENARIOS)
        
        # Add scenario context
        for idea in ideas:
            idea.inspiration_source = scenario
            idea.tags.extend(['what-if', 'scenario', 'hypothetical'])
            idea.creativity_score = min(1.0, idea.creativity_score + 0.2)
        
        return ideas

    def _parse_trend_response(self, content: str, method: CreativeMethod) -> List[CreativeIdea]:
        """Parse trend analysis response"""
        ideas = self._parse_brainstorming_response(content, method)
        
        # Add trend context
        for idea in ideas:
            idea.tags.extend(['trending', 'timely', 'current'])
            idea.potential_impact = min(1.0, idea.potential_impact + 0.2)  # Higher impact potential
        
        return ideas

    async def _evaluate_and_rank_ideas(self, ideas: List[CreativeIdea], prompt: CreativePrompt) -> List[CreativeIdea]:
        """Evaluate and rank ideas based on multiple criteria"""
        try:
            for idea in ideas:
                # Calculate comprehensive score
                scores = []
                
                # Creativity assessment
                creativity_score = await self._assess_creativity(idea.description)
                idea.creativity_score = creativity_score
                scores.append(creativity_score)
                
                # Feasibility assessment
                feasibility_score = self._assess_feasibility(idea.description, prompt)
                idea.feasibility_score = feasibility_score
                scores.append(feasibility_score)
                
                # Originality assessment
                originality_score = await self._assess_originality(idea.description, ideas)
                idea.originality_score = originality_score
                scores.append(originality_score)
                
                # Audience fit assessment
                audience_fit = self._assess_audience_fit(idea.description, prompt.target_audience)
                scores.append(audience_fit)
                
                # Calculate overall potential impact
                idea.potential_impact = np.mean(scores)
            
            # Sort by potential impact
            ranked_ideas = sorted(ideas, key=lambda x: x.potential_impact, reverse=True)
            
            return ranked_ideas
            
        except Exception as e:
            logger.error(f"Idea evaluation failed: {e}")
            # Return ideas with default scores
            return ideas

    async def _assess_creativity(self, description: str) -> float:
        """Assess creativity of an idea"""
        try:
            # Use AI to assess creativity
            assessment_prompt = f"""
            Rate the creativity of this idea on a scale of 0.0 to 1.0:
            
            Idea: {description}
            
            Consider:
            - Originality and uniqueness
            - Innovation and fresh perspective
            - Surprise factor
            - Creative connections
            
            Respond with only a number between 0.0 and 1.0.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creativity assessment expert."},
                    {"role": "user", "content": assessment_prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            score = float(re.findall(r'0\.\d+|1\.0+|0|1', score_text)[0])
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Creativity assessment failed: {e}")
            return 0.7  # Default score

    def _assess_feasibility(self, description: str, prompt: CreativePrompt) -> float:
        """Assess feasibility of implementing the idea"""
        feasibility_factors = []
        
        # Check for complexity indicators
        complexity_words = ['complex', 'difficult', 'advanced', 'expensive', 'time-consuming']
        simple_words = ['simple', 'easy', 'quick', 'basic', 'straightforward']
        
        description_lower = description.lower()
        
        complexity_count = sum(1 for word in complexity_words if word in description_lower)
        simple_count = sum(1 for word in simple_words if word in description_lower)
        
        if simple_count > complexity_count:
            feasibility_factors.append(0.8)
        elif complexity_count > simple_count:
            feasibility_factors.append(0.4)
        else:
            feasibility_factors.append(0.6)
        
        # Check resource requirements
        resource_words = ['budget', 'team', 'equipment', 'tools', 'software']
        resource_mentions = sum(1 for word in resource_words if word in description_lower)
        
        if resource_mentions == 0:
            feasibility_factors.append(0.8)  # Fewer resource requirements
        elif resource_mentions <= 2:
            feasibility_factors.append(0.6)
        else:
            feasibility_factors.append(0.4)
        
        # Length assessment (longer descriptions might be more complex)
        if len(description) < 100:
            feasibility_factors.append(0.8)
        elif len(description) < 200:
            feasibility_factors.append(0.6)
        else:
            feasibility_factors.append(0.5)
        
        return np.mean(feasibility_factors) if feasibility_factors else 0.6

    async def _assess_originality(self, description: str, all_ideas: List[CreativeIdea]) -> float:
        """Assess originality by comparing with other ideas"""
        try:
            # Calculate similarity with other ideas
            descriptions = [idea.description for idea in all_ideas if idea.description != description]
            
            if not descriptions:
                return 0.8  # Only idea, assume high originality
            
            # Use sentence transformer for similarity
            embeddings = self.sentence_model.encode([description] + descriptions)
            
            # Calculate similarity scores
            similarities = cosine_similarity([embeddings[0]], embeddings[1:])[0]
            
            # Higher similarity = lower originality
            max_similarity = np.max(similarities) if len(similarities) > 0 else 0
            originality_score = 1.0 - max_similarity
            
            return max(0.1, min(1.0, originality_score))
            
        except Exception as e:
            logger.error(f"Originality assessment failed: {e}")
            return 0.7  # Default score

    def _assess_audience_fit(self, description: str, target_audience: Optional[str]) -> float:
        """Assess how well the idea fits the target audience"""
        if not target_audience:
            return 0.6  # Default score when no audience specified
        
        description_lower = description.lower()
        audience_lower = target_audience.lower()
        
        # Simple keyword matching (in production, this would be more sophisticated)
        audience_indicators = {
            'young': ['trendy', 'social media', 'viral', 'fun', 'energy'],
            'professional': ['business', 'career', 'expertise', 'industry', 'leadership'],
            'creative': ['art', 'design', 'innovation', 'expression', 'inspiration'],
            'technical': ['technology', 'code', 'data', 'analysis', 'system'],
            'general': ['practical', 'useful', 'everyday', 'simple', 'accessible']
        }
        
        fit_score = 0.5  # Base score
        
        for audience_type, indicators in audience_indicators.items():
            if audience_type in audience_lower:
                matches = sum(1 for indicator in indicators if indicator in description_lower)
                fit_score += matches * 0.1
        
        return max(0.2, min(1.0, fit_score))

    async def _update_trends_if_needed(self):
        """Update trend data if it's stale"""
        last_updated = self.trend_tracker.get('last_updated')
        if not last_updated or (datetime.now(timezone.utc) - last_updated).hours > 6:
            await self._fetch_current_trends()

    async def _fetch_current_trends(self):
        """Fetch current trends from various sources"""
        try:
            # Mock trend data - in production, this would fetch from real APIs
            mock_trends = {
                'current_trends': [
                    'AI automation', 'sustainable living', 'remote work', 
                    'mental health', 'video content', 'personal branding'
                ],
                'emerging_trends': [
                    'blockchain integration', 'virtual events', 'micro-learning',
                    'voice search', 'augmented reality'
                ],
                'declining_trends': [
                    'traditional advertising', 'static content', 'generic messaging'
                ]
            }
            
            self.trend_tracker.update(mock_trends)
            self.trend_tracker['last_updated'] = datetime.now(timezone.utc)
            
            logger.info("Trends updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to fetch trends: {e}")

    def _generate_fallback_ideas(self, prompt: CreativePrompt) -> List[CreativeIdea]:
        """Generate fallback ideas when AI methods fail"""
        fallback_ideas = []
        
        # Use creative patterns for fallback
        patterns = self.creative_patterns.get('content_angles', [])
        
        for i, pattern in enumerate(patterns[:prompt.quantity]):
            idea = CreativeIdea(
                title=f"{pattern}: {prompt.topic}",
                description=f"Create content about {prompt.topic} using the {pattern} approach. This provides a unique perspective and engages the audience with a familiar format.",
                concept=f"Apply {pattern} framework to {prompt.topic}",
                creativity_score=0.6,
                feasibility_score=0.8,
                originality_score=0.5,
                method_used="fallback_patterns",
                tags=['fallback', 'pattern-based', pattern.lower().replace(' ', '-')]
            )
            fallback_ideas.append(idea)
        
        return fallback_ideas

    async def _store_creative_session(self, session: BrainstormingSession):
        """Store creative session in database"""
        try:
            async with get_async_session() as db_session:
                # Store session data (would implement proper database model)
                logger.info(f"Creative session stored: {session.session_id}")
                
        except Exception as e:
            logger.error(f"Failed to store creative session: {e}")

    async def enhance_idea(self, idea: CreativeIdea, enhancement_type: str = "expand") -> CreativeIdea:
        """Enhance an existing idea with additional details"""
        try:
            enhancement_prompts = {
                "expand": f"Expand this content idea with more details, examples, and implementation steps: {idea.description}",
                "adapt": f"Adapt this idea for different platforms and formats: {idea.description}",
                "improve": f"Improve this idea by making it more engaging and actionable: {idea.description}",
                "variations": f"Create 3 variations of this content idea: {idea.description}"
            }
            
            prompt = enhancement_prompts.get(enhancement_type, enhancement_prompts["expand"])
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at enhancing and refining creative ideas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            enhancement = response.choices[0].message.content.strip()
            
            # Create enhanced idea
            enhanced_idea = CreativeIdea(
                title=idea.title,
                description=enhancement,
                concept=idea.concept,
                implementation_steps=self._extract_implementation_steps(enhancement),
                target_audience=idea.target_audience,
                estimated_effort=idea.estimated_effort,
                potential_impact=min(1.0, idea.potential_impact + 0.1),
                creativity_score=min(1.0, idea.creativity_score + 0.05),
                feasibility_score=idea.feasibility_score,
                originality_score=idea.originality_score,
                tags=idea.tags + [f'enhanced_{enhancement_type}'],
                inspiration_source=idea.inspiration_source,
                method_used=f"{idea.method_used}_enhanced"
            )
            
            logger.info(f"Idea enhanced: {enhancement_type}")
            return enhanced_idea
            
        except Exception as e:
            logger.error(f"Idea enhancement failed: {e}")
            return idea

    def _extract_implementation_steps(self, content: str) -> List[str]:
        """Extract implementation steps from content"""
        steps = []
        
        # Look for numbered lists or bullet points
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.', line) or re.match(r'^[\-\*\•]', line):
                # Remove numbering/bullets and clean up
                clean_step = re.sub(r'^\d+\.\s*|^[\-\*\•]\s*', '', line).strip()
                if len(clean_step) > 10:  # Only meaningful steps
                    steps.append(clean_step)
        
        return steps[:10]  # Limit to 10 steps


class IdeaGenerator:
    """Specialized idea generator for different content types"""
    
    def __init__(self):
        self.creative_assistant = CreativeAssistant()
        
        # Content-specific templates
        self.content_templates = self._load_content_templates()
        
        logger.info("IdeaGenerator initialized")

    def _load_content_templates(self) -> Dict[str, Dict]:
        """Load templates for different content types"""
        return {
            IdeationType.TITLE_SUGGESTION: {
                "patterns": [
                    "How to {action} {topic} in {timeframe}",
                    "The Ultimate Guide to {topic}",
                    "{number} {adjective} Ways to {action}",
                    "Why {topic} is {adjective} Than You Think",
                    "The Secret to {action} {topic}"
                ]
            },
            IdeationType.HOOK_IDEA: {
                "patterns": [
                    "What if I told you that {surprising_fact}?",
                    "Everyone thinks {common_belief}, but {contrarian_view}",
                    "The biggest mistake people make with {topic}",
                    "Here's why {controversial_opinion}",
                    "I discovered {insight} after {experience}"
                ]
            },
            IdeationType.CALL_TO_ACTION: {
                "patterns": [
                    "Try this {action} and {benefit}",
                    "Share your {experience} in the comments",
                    "Which {option} resonates with you?",
                    "Tag someone who needs to {action}",
                    "Save this post for {future_use}"
                ]
            }
        }

    async def generate_titles(self, topic: str, quantity: int = 10) -> List[str]:
        """Generate engaging titles for content"""
        try:
            title_prompt = f"""
            Generate {quantity} compelling, engaging titles for content about: {topic}
            
            Titles should be:
            - Attention-grabbing and clickable
            - Clear about the value proposition  
            - Optimized for engagement
            - Varied in style and approach
            
            Include different formats: how-to, listicles, questions, secrets, ultimate guides, etc.
            """
            
            response = await self.creative_assistant.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at writing viral, engaging titles."},
                    {"role": "user", "content": title_prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            titles = self._extract_titles_from_response(content)
            
            return titles[:quantity]
            
        except Exception as e:
            logger.error(f"Title generation failed: {e}")
            return self._generate_fallback_titles(topic, quantity)

    async def generate_hooks(self, topic: str, style: str = "engaging") -> List[str]:
        """Generate compelling content hooks"""
        try:
            hook_prompt = f"""
            Generate 8 compelling content hooks for: {topic}
            Style: {style}
            
            Hooks should:
            - Grab attention immediately
            - Create curiosity or emotional response
            - Be suitable for social media and blog posts
            - Vary in approach (question, statement, story, statistic)
            
            Make them irresistible to read further.
            """
            
            response = await self.creative_assistant.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at writing compelling content hooks."},
                    {"role": "user", "content": hook_prompt}
                ],
                temperature=0.8,
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            hooks = self._extract_hooks_from_response(content)
            
            return hooks
            
        except Exception as e:
            logger.error(f"Hook generation failed: {e}")
            return self._generate_fallback_hooks(topic)

    async def generate_hashtags(self, topic: str, platform: str = "instagram") -> List[str]:
        """Generate relevant hashtags for content"""
        try:
            hashtag_prompt = f"""
            Generate relevant hashtags for content about: {topic}
            Platform: {platform}
            
            Include:
            - 5 highly specific hashtags
            - 5 moderately popular hashtags  
            - 5 broad/popular hashtags
            
            Make them discoverable and relevant for {platform}.
            Format as a list without the # symbol.
            """
            
            response = await self.creative_assistant.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media hashtag expert."},
                    {"role": "user", "content": hashtag_prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            hashtags = self._extract_hashtags_from_response(content)
            
            return hashtags
            
        except Exception as e:
            logger.error(f"Hashtag generation failed: {e}")
            return self._generate_fallback_hashtags(topic)

    def _extract_titles_from_response(self, content: str) -> List[str]:
        """Extract titles from AI response"""
        titles = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove numbering and quotes
            clean_title = re.sub(r'^\d+[\.\)]\s*', '', line)
            clean_title = clean_title.strip('"\'')
            
            if len(clean_title) > 10 and not clean_title.startswith(('Here', 'These', 'Title')):
                titles.append(clean_title)
        
        return titles

    def _extract_hooks_from_response(self, content: str) -> List[str]:
        """Extract hooks from AI response"""
        return self._extract_titles_from_response(content)  # Similar extraction logic

    def _extract_hashtags_from_response(self, content: str) -> List[str]:
        """Extract hashtags from AI response"""
        hashtags = []
        
        # Extract hashtags with or without # symbol
        hashtag_pattern = r'#?([a-zA-Z0-9_]+)'
        matches = re.findall(hashtag_pattern, content)
        
        for match in matches:
            if len(match) > 2 and match.lower() not in ['the', 'and', 'for', 'with']:
                hashtags.append(match.lower())
        
        return list(set(hashtags))  # Remove duplicates

    def _generate_fallback_titles(self, topic: str, quantity: int) -> List[str]:
        """Generate fallback titles using templates"""
        templates = self.content_templates[IdeationType.TITLE_SUGGESTION]["patterns"]
        titles = []
        
        for template in templates[:quantity]:
            title = template.replace('{topic}', topic)
            title = title.replace('{action}', 'master')
            title = title.replace('{timeframe}', '30 days')
            title = title.replace('{number}', '7')
            title = title.replace('{adjective}', 'amazing')
            titles.append(title)
        
        return titles

    def _generate_fallback_hooks(self, topic: str) -> List[str]:
        """Generate fallback hooks using templates"""
        templates = self.content_templates[IdeationType.HOOK_IDEA]["patterns"]
        hooks = []
        
        for template in templates:
            hook = template.replace('{topic}', topic)
            hook = hook.replace('{surprising_fact}', f'{topic} can change your life')
            hook = hook.replace('{common_belief}', f'{topic} is complicated')
            hook = hook.replace('{contrarian_view}', f'it\'s actually simple')
            hooks.append(hook)
        
        return hooks

    def _generate_fallback_hashtags(self, topic: str) -> List[str]:
        """Generate fallback hashtags"""
        words = topic.lower().split()
        base_hashtags = [word for word in words if len(word) > 3]
        
        additional = ['content', 'creative', 'inspiration', 'tips', 'guide']
        
        return base_hashtags + additional
