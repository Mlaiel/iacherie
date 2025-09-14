"""
GPT SEO Optimizer for Ainflue Platform
======================================

Advanced GPT-powered SEO optimization and content generation.
Leverages large language models for intelligent SEO strategies and content optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import openai
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
from datetime import datetime
import re
import tiktoken
import time

logger = logging.getLogger(__name__)

class GPTModel(Enum):
    """Supported GPT models."""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4_VISION = "gpt-4-vision-preview"

class OptimizationType(Enum):
    """Types of GPT SEO optimization."""
    CONTENT_OPTIMIZATION = "content_optimization"
    META_GENERATION = "meta_generation"
    TITLE_OPTIMIZATION = "title_optimization"
    KEYWORD_INTEGRATION = "keyword_integration"
    SCHEMA_GENERATION = "schema_generation"
    FAQ_GENERATION = "faq_generation"
    CONTENT_EXPANSION = "content_expansion"
    REWRITING = "rewriting"

class ContentFormat(Enum):
    """Content format types."""
    BLOG_POST = "blog_post"
    PRODUCT_DESCRIPTION = "product_description"
    SOCIAL_MEDIA = "social_media"
    EMAIL_MARKETING = "email_marketing"
    VIDEO_DESCRIPTION = "video_description"
    LANDING_PAGE = "landing_page"
    AD_COPY = "ad_copy"

@dataclass
class GPTOptimizationRequest:
    """GPT optimization request configuration."""
    request_id: str
    content_id: str
    optimization_type: OptimizationType
    target_keywords: List[str]
    target_audience: str
    content_format: ContentFormat
    language: str
    tone: str
    length_target: int
    seo_goals: List[str]
    constraints: Dict[str, Any]
    created_at: datetime

@dataclass
class GPTOptimizationResult:
    """GPT optimization result."""
    result_id: str
    request_id: str
    optimization_type: OptimizationType
    original_content: str
    optimized_content: str
    generated_meta: Dict[str, str]
    keyword_integration: Dict[str, Any]
    seo_improvements: List[str]
    readability_score: float
    keyword_density: Dict[str, float]
    estimated_impact: Dict[str, float]
    confidence_score: float
    model_used: GPTModel
    tokens_used: int
    processing_time_ms: int
    created_at: datetime

@dataclass
class ContentSuggestion:
    """AI-generated content suggestion."""
    suggestion_id: str
    content_type: str
    title: str
    outline: List[str]
    target_keywords: List[str]
    estimated_length: int
    difficulty: str
    potential_ranking: int
    search_volume: int
    competition_level: str
    content_angle: str
    created_at: datetime

class GPTSEOOptimizer:
    """
    Advanced GPT SEO Optimizer
    
    Features:
    - Intelligent content optimization
    - SEO-focused content generation
    - Meta tags and descriptions generation
    - Keyword integration optimization
    - Schema markup generation
    - FAQ and Q&A generation
    - Content rewriting and expansion
    - Multi-language SEO optimization
    """
    
    def __init__(self, db_pool -> None: asyncpg.Pool, openai_api_key -> None: str) -> None:
        self.db_pool = db_pool
        openai.api_key = openai_api_key
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # SEO optimization prompts
        self.prompts = {
            'content_optimization': self._load_content_optimization_prompt(),
            'meta_generation': self._load_meta_generation_prompt(),
            'title_optimization': self._load_title_optimization_prompt(),
            'keyword_integration': self._load_keyword_integration_prompt(),
            'schema_generation': self._load_schema_generation_prompt(),
            'faq_generation': self._load_faq_generation_prompt(),
            'content_expansion': self._load_content_expansion_prompt(),
            'rewriting': self._load_rewriting_prompt()
        }
    
    async def optimize_content(
        self,
        content_id: str,
        original_content: str,
        optimization_request: GPTOptimizationRequest
    ) -> GPTOptimizationResult:
        """
        Optimize content using GPT for better SEO performance.
        
        Args:
            content_id: Content identifier
            original_content: Original content text
            optimization_request: Optimization configuration
            
        Returns:
            GPTOptimizationResult object
        """
        try:
            start_time = datetime.utcnow()
            result_id = f"gpt_opt_{content_id}_{int(start_time.timestamp())}"
            
            # Select appropriate model
            model = self._select_optimal_model(optimization_request)
            
            # Prepare optimization prompt
            prompt = await self._prepare_optimization_prompt(
                original_content, optimization_request
            )
            
            # Call GPT API
            gpt_response = await self._call_gpt_api(prompt, model)
            
            # Parse optimization results
            optimized_content, meta_data, improvements = await self._parse_optimization_response(
                gpt_response, optimization_request
            )
            
            # Analyze keyword integration
            keyword_integration = await self._analyze_keyword_integration(
                optimized_content, optimization_request.target_keywords
            )
            
            # Calculate metrics
            readability_score = self._calculate_readability_score(optimized_content)
            keyword_density = self._calculate_keyword_density(
                optimized_content, optimization_request.target_keywords
            )
            
            # Estimate SEO impact
            estimated_impact = await self._estimate_seo_impact(
                original_content, optimized_content, optimization_request
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_optimization_confidence(
                gpt_response, keyword_integration, estimated_impact
            )
            
            # Calculate processing metrics
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            tokens_used = len(self.encoding.encode(prompt + gpt_response))
            
            result = GPTOptimizationResult(
                result_id=result_id,
                request_id=optimization_request.request_id,
                optimization_type=optimization_request.optimization_type,
                original_content=original_content,
                optimized_content=optimized_content,
                generated_meta=meta_data,
                keyword_integration=keyword_integration,
                seo_improvements=improvements,
                readability_score=readability_score,
                keyword_density=keyword_density,
                estimated_impact=estimated_impact,
                confidence_score=confidence_score,
                model_used=model,
                tokens_used=tokens_used,
                processing_time_ms=processing_time_ms,
                created_at=datetime.utcnow()
            )
            
            # Store result
            await self._store_optimization_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing content with GPT: {e}")
            raise
    
    async def generate_seo_content(
        self,
        topic: str,
        target_keywords: List[str],
        content_format: ContentFormat,
        target_audience: str,
        length_target: int = 1000,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate SEO-optimized content from scratch using GPT.
        
        Args:
            topic: Content topic
            target_keywords: Keywords to target
            content_format: Format of content to generate
            target_audience: Target audience description
            length_target: Target word count
            language: Content language
            
        Returns:
            Generated content with SEO optimization
        """
        try:
            # Prepare content generation prompt
            prompt = await self._prepare_content_generation_prompt(
                topic, target_keywords, content_format, target_audience, 
                length_target, language
            )
            
            # Generate content
            model = GPTModel.GPT_4_TURBO
            gpt_response = await self._call_gpt_api(prompt, model)
            
            # Parse generated content
            parsed_content = await self._parse_generated_content(gpt_response)
            
            # Add SEO enhancements
            seo_enhanced_content = await self._enhance_content_for_seo(
                parsed_content, target_keywords
            )
            
            return {
                'generated_content': seo_enhanced_content,
                'meta_data': parsed_content.get('meta_data', {}),
                'seo_score': self._calculate_content_seo_score(seo_enhanced_content, target_keywords),
                'generation_timestamp': datetime.utcnow().isoformat(),
                'model_used': model.value,
                'target_keywords': target_keywords
            }
            
        except Exception as e:
            logger.error(f"Error generating SEO content: {e}")
            return {}
    
    async def generate_meta_tags(
        self,
        content: str,
        target_keywords: List[str],
        page_type: str = "article"
    ) -> Dict[str, str]:
        """
        Generate optimized meta tags using GPT.
        
        Args:
            content: Content text
            target_keywords: Target keywords
            page_type: Type of page (article, product, etc.)
            
        Returns:
            Generated meta tags
        """
        try:
            prompt = f"""
            Generate SEO-optimized meta tags for the following content:

            Content: {content[:1000]}...
            Target Keywords: {', '.join(target_keywords)}
            Page Type: {page_type}

            Generate the following meta tags:
            1. Title tag (50-60 characters, include primary keyword)
            2. Meta description (150-160 characters, compelling and keyword-rich)
            3. Meta keywords (comma-separated, relevant keywords)
            4. Open Graph title
            5. Open Graph description
            6. Twitter card title
            7. Twitter card description

            Format as JSON with keys: title, description, keywords, og_title, og_description, twitter_title, twitter_description
            """
            
            response = await self._call_gpt_api(prompt, GPTModel.GPT_3_5_TURBO)
            
            try:
                meta_tags = json.loads(response)
                return meta_tags
            except json.JSONDecodeError:
                # Fallback parsing
                return self._parse_meta_tags_fallback(response)
                
        except Exception as e:
            logger.error(f"Error generating meta tags: {e}")
            return {}
    
    async def generate_schema_markup(
        self,
        content: str,
        content_type: str,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate schema.org markup using GPT.
        
        Args:
            content: Content text
            content_type: Type of content (Article, Product, etc.)
            additional_data: Additional structured data
            
        Returns:
            Generated schema markup
        """
        try:
            prompt = f"""
            Generate schema.org JSON-LD markup for the following content:

            Content Type: {content_type}
            Content: {content[:800]}...
            Additional Data: {json.dumps(additional_data or {})}

            Generate appropriate schema.org markup including:
            - @context and @type
            - Relevant properties for the content type
            - Structured data that enhances SEO
            - Proper nesting for complex types

            Return only valid JSON-LD format.
            """
            
            response = await self._call_gpt_api(prompt, GPTModel.GPT_4)
            
            try:
                schema_markup = json.loads(response)
                return schema_markup
            except json.JSONDecodeError:
                logger.error("Failed to parse schema markup JSON")
                return {}
                
        except Exception as e:
            logger.error(f"Error generating schema markup: {e}")
            return {}
    
    async def generate_faq_content(
        self,
        main_content: str,
        target_keywords: List[str],
        num_questions: int = 5
    ) -> List[Dict[str, str]]:
        """
        Generate FAQ content using GPT for SEO enhancement.
        
        Args:
            main_content: Main content text
            target_keywords: Target keywords
            num_questions: Number of FAQ items to generate
            
        Returns:
            List of Q&A pairs
        """
        try:
            prompt = f"""
            Based on the following content, generate {num_questions} FAQ questions and answers that would help with SEO:

            Content: {main_content[:1200]}...
            Target Keywords: {', '.join(target_keywords)}

            Generate questions that:
            1. People commonly search for related to this topic
            2. Include variations of the target keywords
            3. Address user intent and concerns
            4. Are specific and actionable

            Format as JSON array with objects containing "question" and "answer" keys.
            """
            
            response = await self._call_gpt_api(prompt, GPTModel.GPT_4)
            
            try:
                faq_items = json.loads(response)
                return faq_items if isinstance(faq_items, list) else []
            except json.JSONDecodeError:
                return self._parse_faq_fallback(response)
                
        except Exception as e:
            logger.error(f"Error generating FAQ content: {e}")
            return []
    
    async def suggest_content_ideas(
        self,
        industry: str,
        target_keywords: List[str],
        competitor_content: List[str],
        num_suggestions: int = 10
    ) -> List[ContentSuggestion]:
        """
        Generate content ideas using GPT for SEO strategy.
        
        Args:
            industry: Industry or niche
            target_keywords: Target keywords
            competitor_content: Examples of competitor content
            num_suggestions: Number of suggestions to generate
            
        Returns:
            List of ContentSuggestion objects
        """
        try:
            prompt = f"""
            Generate {num_suggestions} content ideas for SEO in the {industry} industry:

            Target Keywords: {', '.join(target_keywords)}
            Competitor Content Examples: {'; '.join(competitor_content[:3])}

            For each content idea, provide:
            1. Compelling title
            2. Content outline (5-7 main points)
            3. Target keywords for the piece
            4. Estimated word count
            5. Content difficulty (easy/medium/hard)
            6. Unique angle or perspective
            7. Potential search volume estimate
            8. Competition level estimate

            Focus on content gaps and opportunities that competitors might be missing.
            Format as JSON array.
            """
            
            response = await self._call_gpt_api(prompt, GPTModel.GPT_4)
            
            suggestions = []
            try:
                parsed_suggestions = json.loads(response)
                
                for i, suggestion in enumerate(parsed_suggestions):
                    content_suggestion = ContentSuggestion(
                        suggestion_id=f"content_idea_{int(datetime.utcnow().timestamp())}_{i}",
                        content_type=suggestion.get('type', 'article'),
                        title=suggestion.get('title', ''),
                        outline=suggestion.get('outline', []),
                        target_keywords=suggestion.get('target_keywords', []),
                        estimated_length=suggestion.get('estimated_length', 1000),
                        difficulty=suggestion.get('difficulty', 'medium'),
                        potential_ranking=suggestion.get('potential_ranking', 10),
                        search_volume=suggestion.get('search_volume', 100),
                        competition_level=suggestion.get('competition_level', 'medium'),
                        content_angle=suggestion.get('content_angle', ''),
                        created_at=datetime.utcnow()
                    )
                    suggestions.append(content_suggestion)
                
                return suggestions
                
            except json.JSONDecodeError:
                logger.error("Failed to parse content suggestions")
                return []
                
        except Exception as e:
            logger.error(f"Error generating content suggestions: {e}")
            return []
    
    def _select_optimal_model(self, request: GPTOptimizationRequest) -> GPTModel:
        """Select the most appropriate GPT model for the task."""
        if request.optimization_type in [OptimizationType.SCHEMA_GENERATION, OptimizationType.FAQ_GENERATION]:
            return GPTModel.GPT_4
        elif request.content_format in [ContentFormat.BLOG_POST, ContentFormat.LANDING_PAGE]:
            return GPTModel.GPT_4_TURBO
        else:
            return GPTModel.GPT_3_5_TURBO
    
    async def _prepare_optimization_prompt(
        self,
        content: str,
        request: GPTOptimizationRequest
    ) -> str:
        """Prepare the optimization prompt for GPT."""
        base_prompt = self.prompts.get(request.optimization_type.value, "")
        
        # Customize prompt based on request
        prompt = base_prompt.format(
            content=content[:3000],  # Limit content length
            target_keywords=', '.join(request.target_keywords),
            target_audience=request.target_audience,
            content_format=request.content_format.value,
            tone=request.tone,
            length_target=request.length_target,
            seo_goals=', '.join(request.seo_goals),
            language=request.language
        )
        
        return prompt
    
    async def _call_gpt_api(self, prompt: str, model: GPTModel) -> str:
        """Call GPT API with error handling and retries."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = await openai.ChatCompletion.acreate(
                    model=model.value,
                    messages=[
                        {"role": "system", "content": "You are an expert SEO content optimizer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"GPT API attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                else:
                    raise
    
    async def _parse_optimization_response(
        self,
        response: str,
        request: GPTOptimizationRequest
    ) -> Tuple[str, Dict[str, str], List[str]]:
        """Parse GPT optimization response."""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                parsed = json.loads(response)
                return (
                    parsed.get('optimized_content', response),
                    parsed.get('meta_data', {}),
                    parsed.get('improvements', [])
                )
            else:
                # Fallback: extract content sections
                sections = response.split('\n\n')
                optimized_content = sections[0] if sections else response
                
                return optimized_content, {}, ["Content optimized using GPT"]
                
        except Exception as e:
            logger.error(f"Error parsing optimization response: {e}")
            return response, {}, []
    
    def _load_content_optimization_prompt(self) -> str:
        """Load content optimization prompt template."""
        return """
        Optimize the following content for SEO while maintaining quality and readability:

        Original Content: {content}
        Target Keywords: {target_keywords}
        Target Audience: {target_audience}
        Content Format: {content_format}
        Tone: {tone}
        Target Length: {length_target} words
        SEO Goals: {seo_goals}
        Language: {language}

        Please:
        1. Naturally integrate target keywords
        2. Improve content structure and headings
        3. Enhance readability and flow
        4. Add relevant semantic keywords
        5. Optimize for user intent
        6. Maintain the original tone and style

        Return the optimized content with clear improvements noted.
        """
    
    def _load_meta_generation_prompt(self) -> str:
        """Load meta tag generation prompt template."""
        return """
        Generate SEO-optimized meta tags for this content:

        Content: {content}
        Target Keywords: {target_keywords}
        Content Format: {content_format}

        Generate:
        1. Title tag (50-60 chars, keyword-optimized)
        2. Meta description (150-160 chars, compelling)
        3. Relevant meta keywords

        Return as JSON format.
        """
    
    def _load_title_optimization_prompt(self) -> str:
        """Load title optimization prompt template."""
        return """
        Create 5 SEO-optimized title variations for this content:

        Content: {content}
        Target Keywords: {target_keywords}
        Target Audience: {target_audience}

        Each title should:
        - Include primary keyword
        - Be 50-60 characters
        - Be compelling and clickable
        - Match search intent

        Return as numbered list.
        """
    
    def _load_keyword_integration_prompt(self) -> str:
        """Load keyword integration prompt template."""
        return """
        Optimize keyword integration in this content:

        Content: {content}
        Target Keywords: {target_keywords}

        Improve:
        1. Natural keyword placement
        2. Semantic keyword variations
        3. Keyword density optimization
        4. Long-tail keyword inclusion

        Return optimized content with keyword placement notes.
        """
    
    def _load_schema_generation_prompt(self) -> str:
        """Load schema markup generation prompt template."""
        return """
        Generate schema.org JSON-LD markup for:

        Content: {content}
        Content Type: {content_format}

        Include appropriate schema properties for SEO enhancement.
        Return valid JSON-LD format only.
        """
    
    def _load_faq_generation_prompt(self) -> str:
        """Load FAQ generation prompt template."""
        return """
        Generate FAQ content based on:

        Main Content: {content}
        Target Keywords: {target_keywords}

        Create 5-7 questions that:
        - Address common user queries
        - Include keyword variations
        - Provide valuable answers
        - Enhance SEO potential

        Return as JSON array of Q&A objects.
        """
    
    def _load_content_expansion_prompt(self) -> str:
        """Load content expansion prompt template."""
        return """
        Expand this content for better SEO coverage:

        Original Content: {content}
        Target Keywords: {target_keywords}
        Target Length: {length_target} words

        Add:
        - Related subtopics
        - Supporting details
        - Examples and use cases
        - Semantic keyword variations

        Maintain quality and relevance.
        """
    
    def _load_rewriting_prompt(self) -> str:
        """Load content rewriting prompt template."""
        return """
        Rewrite this content for better SEO performance:

        Original: {content}
        Target Keywords: {target_keywords}
        Tone: {tone}
        Audience: {target_audience}

        Improve:
        - Keyword optimization
        - Content structure
        - Readability
        - User engagement

        Keep the core message intact.
        """

# Export classes
__all__ = [
    'GPTSEOOptimizer',
    'GPTOptimizationRequest',
    'GPTOptimizationResult', 
    'ContentSuggestion',
    'GPTModel',
    'OptimizationType',
    'ContentFormat'
]