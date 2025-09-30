"""
Cohere API Integration Module
=============================

Enterprise-grade integration with Cohere language models
Specialized for advanced NLP tasks and creator content workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Role Applied: Lead Dev IA + IA Prompt Engineer + ML Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Generator
from dataclasses import dataclass, field
from enum import Enum
import json

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class CohereModel(Enum):
    """Cohere model types for different use cases."""
    COMMAND = "command"
    COMMAND_LIGHT = "command-light"
    COMMAND_NIGHTLY = "command-nightly"
    EMBED_ENGLISH = "embed-english-v3.0"
    EMBED_MULTILINGUAL = "embed-multilingual-v3.0"
    RERANK_ENGLISH = "rerank-english-v3.0"
    RERANK_MULTILINGUAL = "rerank-multilingual-v3.0"


class CohereTaskType(Enum):
    """Task types for Cohere API optimization."""
    SEARCH_DOCUMENT = "search_document"
    SEARCH_QUERY = "search_query"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    CONTENT_GENERATION = "content_generation"
    SUMMARIZATION = "summarization"
    REWRITING = "rewriting"
    TRANSLATION = "translation"
    Q_AND_A = "question_answering"
    CREATIVE_WRITING = "creative_writing"


@dataclass
class CohereGenerationRequest:
    """Cohere text generation request configuration."""
    prompt: str
    model: CohereModel = CohereModel.COMMAND
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    return_likelihoods: str = "NONE"  # NONE, GENERATION, ALL
    truncate: str = "END"  # START, END
    creator_context: Dict[str, Any] = field(default_factory=dict)
    business_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CohereEmbeddingRequest:
    """Cohere embedding request configuration."""
    texts: List[str]
    model: CohereModel = CohereModel.EMBED_ENGLISH
    input_type: str = "search_document"  # search_document, search_query, classification, clustering
    embedding_types: List[str] = field(default_factory=lambda: ["float"])
    truncate: str = "END"


@dataclass
class CohereRerankRequest:
    """Cohere rerank request configuration."""
    query: str
    documents: List[str]
    model: CohereModel = CohereModel.RERANK_ENGLISH
    top_n: Optional[int] = None
    return_documents: bool = True


@dataclass
class CohereResponse:
    """Cohere API response with business context."""
    id: str = ""
    text: str = ""
    embeddings: List[List[float]] = field(default_factory=list)
    rankings: List[Dict[str, Any]] = field(default_factory=list)
    tokens: int = 0
    finish_reason: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    model_used: str = ""
    creator_context: Dict[str, Any] = field(default_factory=dict)
    business_metadata: Dict[str, Any] = field(default_factory=dict)
    cost_estimate: float = 0.0


class CohereEnterpriseClient:
    """
    Enterprise Cohere API client with creator workflow integration.
    
    Specialized for Ainflue platform business logic:
    - Advanced NLP for creator content
    - Multi-language support for global creators
    - Cost-effective model selection
    - Creator-specific prompt optimization
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.cohere.ai/v1",
        timeout: int = 120,
        max_retries: int = 3,
        enable_prompt_optimization: bool = True,
        enable_cost_optimization: bool = True
    ):
        """Initialize Cohere client with enterprise configuration."""
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_prompt_optimization = enable_prompt_optimization
        self.enable_cost_optimization = enable_cost_optimization
        
        # Enterprise session configuration
        self.session = None
        if httpx:
            self.session = httpx.AsyncClient(
                timeout=httpx.Timeout(timeout),
                headers=self._get_headers()
            )
        
        # Creator workflow templates
        self.creator_templates = self._initialize_creator_templates()
        self.prompt_optimizations = self._initialize_prompt_optimizations()
        
        # Cost tracking
        self.usage_tracking = {
            "total_tokens": 0,
            "total_requests": 0,
            "total_cost": 0.0,
            "cost_per_model": {}
        }
        
        # Model pricing (approximate)
        self.model_pricing = {
            CohereModel.COMMAND: {"input": 0.0015, "output": 0.002},
            CohereModel.COMMAND_LIGHT: {"input": 0.0003, "output": 0.0006},
            CohereModel.COMMAND_NIGHTLY: {"input": 0.0015, "output": 0.002},
            CohereModel.EMBED_ENGLISH: {"input": 0.0001, "output": 0.0},
            CohereModel.EMBED_MULTILINGUAL: {"input": 0.0001, "output": 0.0},
            CohereModel.RERANK_ENGLISH: {"input": 0.0001, "output": 0.0},
            CohereModel.RERANK_MULTILINGUAL: {"input": 0.0001, "output": 0.0}
        }
        
        logger.info("✅ Cohere Enterprise Client initialized")

    def _get_headers(self) -> Dict[str, str]:
        """Generate request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Ainflue-Cohere-Integration/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers

    def _initialize_creator_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize creator-specific prompt templates."""
        return {
            "musician": {
                "song_lyrics": """Write song lyrics for a {genre} song about {topic}.
                Style: {style}
                Mood: {mood}
                Target audience: {audience}
                
                Structure:
                - Verse 1
                - Chorus
                - Verse 2
                - Chorus
                - Bridge
                - Chorus (outro)
                
                Make it catchy and memorable with strong emotional impact.""",
                
                "album_description": """Create a compelling album description for '{album_name}' by {artist_name}.
                Genre: {genre}
                Key themes: {themes}
                Target audience: {audience}
                
                Include:
                - Brief artistic vision
                - Track highlights
                - Musical influences
                - Emotional journey""",
                
                "social_media_post": """Create an engaging social media post for musician {artist_name}.
                Context: {context}
                Platform: {platform}
                Goal: {goal}
                
                Make it authentic, engaging, and encourage fan interaction."""
            },
            
            "blogger": {
                "blog_post": """Write a comprehensive blog post about: {topic}
                Target audience: {audience}
                Tone: {tone}
                Word count: {word_count}
                SEO keywords: {keywords}
                
                Structure:
                - Compelling introduction
                - Main content with subheadings
                - Actionable insights
                - Strong conclusion with call-to-action""",
                
                "headline_generation": """Generate 10 compelling headlines for a blog post about: {topic}
                Target audience: {audience}
                Content type: {content_type}
                
                Make them click-worthy, SEO-friendly, and accurate to the content.""",
                
                "content_summary": """Create a compelling summary for this content:
                {content}
                
                Target length: {summary_length}
                Purpose: {purpose}
                Audience: {audience}"""
            },
            
            "photographer": {
                "portfolio_description": """Write a compelling description for photographer {photographer_name}'s portfolio.
                Photography style: {style}
                Specialization: {specialization}
                Experience: {experience}
                Target clients: {target_clients}
                
                Highlight artistic vision, technical expertise, and unique value proposition.""",
                
                "project_description": """Create a detailed description for photography project: {project_name}
                Client: {client}
                Concept: {concept}
                Style: {style}
                Location: {location}
                
                Include creative vision, technical approach, and expected outcomes.""",
                
                "social_caption": """Write an engaging Instagram caption for this photography post:
                Image description: {image_description}
                Photography style: {style}
                Location: {location}
                Mood: {mood}
                
                Include relevant hashtags and encourage engagement."""
            },
            
            "influencer": {
                "brand_collaboration": """Create content for a brand collaboration post:
                Brand: {brand_name}
                Product/Service: {product}
                Platform: {platform}
                Audience: {audience}
                Collaboration type: {collab_type}
                
                Make it authentic, engaging, and compliant with disclosure requirements.""",
                
                "content_script": """Write a script for {content_type} content:
                Topic: {topic}
                Platform: {platform}
                Duration: {duration}
                Audience: {audience}
                Goal: {goal}
                
                Include hooks, main content, and strong call-to-action.""",
                
                "audience_engagement": """Create engaging content to boost audience interaction:
                Topic: {topic}
                Platform: {platform}
                Content type: {content_type}
                Goal: {engagement_goal}
                
                Make it conversation-starting and shareable."""
            },
            
            "comedian": {
                "comedy_routine": """Write a comedy routine about: {topic}
                Style: {comedy_style}
                Length: {duration}
                Audience: {audience}
                Setting: {setting}
                
                Include setup, punchlines, and callbacks. Keep it appropriate and relatable.""",
                
                "social_content": """Create funny social media content:
                Topic: {topic}
                Platform: {platform}
                Style: {humor_style}
                Current events: {context}
                
                Make it shareable, relatable, and on-brand.""",
                
                "joke_writing": """Write {joke_count} jokes about: {topic}
                Style: {style}
                Audience: {audience}
                Format: {format}
                
                Ensure they're original, punchy, and appropriate for the audience."""
            }
        }

    def _initialize_prompt_optimizations(self) -> Dict[str, List[str]]:
        """Initialize prompt optimization techniques for different use cases."""
        return {
            "creativity_boosters": [
                "Think creatively and originally",
                "Use vivid, descriptive language",
                "Include unexpected angles or perspectives",
                "Make it memorable and engaging"
            ],
            "clarity_enhancers": [
                "Be clear and concise",
                "Use simple, accessible language",
                "Structure information logically",
                "Include specific examples"
            ],
            "engagement_drivers": [
                "Create emotional connection",
                "Use conversational tone",
                "Include relatable scenarios",
                "Encourage interaction"
            ],
            "seo_optimizers": [
                "Include relevant keywords naturally",
                "Structure with clear headings",
                "Create scannable content",
                "Include actionable insights"
            ],
            "brand_voice_enhancers": [
                "Maintain consistent tone",
                "Reflect brand personality",
                "Use brand-appropriate language",
                "Align with brand values"
            ]
        }

    async def generate_text(
        self,
        request: CohereGenerationRequest,
        stream: bool = False
    ) -> CohereResponse:
        """
        Generate text using Cohere models with creator workflow optimization.
        
        Args:
            request: Generation request configuration
            stream: Whether to stream the response
            
        Returns:
            CohereResponse with generated text and metadata
        """
        try:
            # Apply prompt optimization if enabled
            if self.enable_prompt_optimization:
                request = await self._optimize_prompt(request)
            
            # Apply cost optimization if enabled
            if self.enable_cost_optimization:
                request = await self._optimize_for_cost(request)
            
            # Prepare request payload
            payload = {
                "prompt": request.prompt,
                "model": request.model.value,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "p": request.top_p,
                "k": request.top_k,
                "frequency_penalty": request.frequency_penalty,
                "presence_penalty": request.presence_penalty,
                "return_likelihoods": request.return_likelihoods,
                "truncate": request.truncate,
                "stream": stream
            }
            
            if request.stop_sequences:
                payload["stop_sequences"] = request.stop_sequences
            
            # Submit request
            if not self.session:
                raise Exception("HTTP session not initialized")
                
            response = await self.session.post(
                f"{self.base_url}/generate",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Process response
            result = CohereResponse(
                id=data.get("id", ""),
                text=data.get("generations", [{}])[0].get("text", ""),
                tokens=data.get("meta", {}).get("tokens", {}).get("total_tokens", 0),
                finish_reason=data.get("generations", [{}])[0].get("finish_reason", ""),
                model_used=request.model.value,
                creator_context=request.creator_context,
                business_metadata=request.business_metadata
            )
            
            # Calculate cost estimate
            result.cost_estimate = self._calculate_cost(request.model, result.tokens, len(request.prompt))
            
            # Track usage
            self._track_usage(request.model, result.tokens, result.cost_estimate)
            
            logger.info(f"✅ Cohere text generation completed: {result.tokens} tokens")
            return result
            
        except Exception as e:
            logger.error(f"❌ Cohere text generation failed: {e}")
            raise

    async def create_embeddings(self, request: CohereEmbeddingRequest) -> CohereResponse:
        """Create embeddings for text analysis and search."""
        try:
            payload = {
                "texts": request.texts,
                "model": request.model.value,
                "input_type": request.input_type,
                "embedding_types": request.embedding_types,
                "truncate": request.truncate
            }
            
            if not self.session:
                raise Exception("HTTP session not initialized")
                
            response = await self.session.post(
                f"{self.base_url}/embed",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            result = CohereResponse(
                id=data.get("id", ""),
                embeddings=data.get("embeddings", []),
                tokens=len(" ".join(request.texts).split()),  # Approximate
                model_used=request.model.value
            )
            
            # Calculate cost estimate
            result.cost_estimate = self._calculate_cost(request.model, result.tokens, 0)
            
            # Track usage
            self._track_usage(request.model, result.tokens, result.cost_estimate)
            
            logger.info(f"✅ Cohere embeddings created for {len(request.texts)} texts")
            return result
            
        except Exception as e:
            logger.error(f"❌ Cohere embeddings failed: {e}")
            raise

    async def rerank_documents(self, request: CohereRerankRequest) -> CohereResponse:
        """Rerank documents based on relevance to query."""
        try:
            payload = {
                "query": request.query,
                "documents": request.documents,
                "model": request.model.value,
                "return_documents": request.return_documents
            }
            
            if request.top_n:
                payload["top_n"] = request.top_n
            
            if not self.session:
                raise Exception("HTTP session not initialized")
                
            response = await self.session.post(
                f"{self.base_url}/rerank",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            result = CohereResponse(
                id=data.get("id", ""),
                rankings=data.get("results", []),
                tokens=len((request.query + " ".join(request.documents)).split()),  # Approximate
                model_used=request.model.value
            )
            
            # Calculate cost estimate
            result.cost_estimate = self._calculate_cost(request.model, result.tokens, 0)
            
            # Track usage
            self._track_usage(request.model, result.tokens, result.cost_estimate)
            
            logger.info(f"✅ Cohere reranking completed for {len(request.documents)} documents")
            return result
            
        except Exception as e:
            logger.error(f"❌ Cohere reranking failed: {e}")
            raise

    async def generate_creator_content(
        self,
        creator_type: str,
        content_type: str,
        template_data: Dict[str, Any],
        custom_instructions: Optional[str] = None
    ) -> CohereResponse:
        """Generate content using creator-specific templates."""
        if creator_type not in self.creator_templates:
            raise ValueError(f"Creator type '{creator_type}' not supported")
        
        if content_type not in self.creator_templates[creator_type]:
            raise ValueError(f"Content type '{content_type}' not available for '{creator_type}'")
        
        # Get template
        template = self.creator_templates[creator_type][content_type]
        
        # Format template with provided data
        try:
            prompt = template.format(**template_data)
        except KeyError as e:
            raise ValueError(f"Missing template data: {e}")
        
        # Add custom instructions if provided
        if custom_instructions:
            prompt += f"\n\nAdditional instructions: {custom_instructions}"
        
        # Create generation request
        request = CohereGenerationRequest(
            prompt=prompt,
            model=CohereModel.COMMAND,
            max_tokens=self._get_optimal_max_tokens(content_type),
            temperature=self._get_optimal_temperature(content_type),
            creator_context={
                "creator_type": creator_type,
                "content_type": content_type,
                "template_used": f"{creator_type}.{content_type}"
            },
            business_metadata=template_data
        )
        
        return await self.generate_text(request)

    async def _optimize_prompt(self, request: CohereGenerationRequest) -> CohereGenerationRequest:
        """Apply prompt optimization techniques based on creator context."""
        creator_type = request.creator_context.get("creator_type")
        content_type = request.creator_context.get("content_type")
        
        optimizations = []
        
        # Apply content-type specific optimizations
        if content_type:
            if "creative" in content_type or "song" in content_type or "comedy" in content_type:
                optimizations.extend(self.prompt_optimizations["creativity_boosters"])
            elif "blog" in content_type or "description" in content_type:
                optimizations.extend(self.prompt_optimizations["clarity_enhancers"])
                optimizations.extend(self.prompt_optimizations["seo_optimizers"])
            elif "social" in content_type or "post" in content_type:
                optimizations.extend(self.prompt_optimizations["engagement_drivers"])
        
        # Apply creator-type specific optimizations
        if creator_type:
            optimizations.extend(self.prompt_optimizations["brand_voice_enhancers"])
        
        # Add optimizations to prompt
        if optimizations:
            optimization_text = "\n".join(f"- {opt}" for opt in optimizations[:3])  # Limit to top 3
            request.prompt += f"\n\nPlease ensure the content:\n{optimization_text}"
        
        return request

    async def _optimize_for_cost(self, request: CohereGenerationRequest) -> CohereGenerationRequest:
        """Optimize request parameters for cost efficiency."""
        content_type = request.creator_context.get("content_type", "")
        
        # Use lighter model for simple tasks
        if any(simple_task in content_type for simple_task in ["caption", "headline", "summary"]):
            if request.model == CohereModel.COMMAND:
                request.model = CohereModel.COMMAND_LIGHT
                logger.info("🔄 Optimized to use command-light for simple task")
        
        # Adjust max_tokens based on content type
        if "headline" in content_type:
            request.max_tokens = min(request.max_tokens, 100)
        elif "caption" in content_type:
            request.max_tokens = min(request.max_tokens, 200)
        elif "summary" in content_type:
            request.max_tokens = min(request.max_tokens, 500)
        
        return request

    def _get_optimal_max_tokens(self, content_type: str) -> int:
        """Get optimal max_tokens for different content types."""
        token_mapping = {
            "headline": 100,
            "caption": 200,
            "summary": 500,
            "post": 800,
            "description": 600,
            "lyrics": 1000,
            "routine": 1500,
            "blog_post": 2000,
            "script": 1200
        }
        
        for key, tokens in token_mapping.items():
            if key in content_type:
                return tokens
        
        return 1000  # Default

    def _get_optimal_temperature(self, content_type: str) -> float:
        """Get optimal temperature for different content types."""
        temperature_mapping = {
            "creative": 0.8,
            "lyrics": 0.9,
            "comedy": 0.85,
            "routine": 0.8,
            "blog": 0.7,
            "description": 0.6,
            "summary": 0.5,
            "professional": 0.5
        }
        
        for key, temp in temperature_mapping.items():
            if key in content_type:
                return temp
        
        return 0.7  # Default

    def _calculate_cost(self, model: CohereModel, output_tokens: int, input_chars: int) -> float:
        """Calculate cost estimate for API call."""
        if model not in self.model_pricing:
            return 0.0
        
        pricing = self.model_pricing[model]
        
        # Estimate input tokens (approximately 4 characters per token)
        input_tokens = input_chars // 4
        
        input_cost = input_tokens * pricing["input"] / 1000
        output_cost = output_tokens * pricing["output"] / 1000
        
        return input_cost + output_cost

    def _track_usage(self, model: CohereModel, tokens: int, cost: float) -> None:
        """Track usage statistics for analytics."""
        self.usage_tracking["total_tokens"] += tokens
        self.usage_tracking["total_requests"] += 1
        self.usage_tracking["total_cost"] += cost
        
        model_name = model.value
        if model_name not in self.usage_tracking["cost_per_model"]:
            self.usage_tracking["cost_per_model"][model_name] = 0.0
        self.usage_tracking["cost_per_model"][model_name] += cost

    async def get_usage_analytics(self) -> Dict[str, Any]:
        """Get usage analytics and cost breakdown."""
        avg_cost_per_request = (
            self.usage_tracking["total_cost"] / max(self.usage_tracking["total_requests"], 1)
        )
        
        return {
            "usage_summary": self.usage_tracking,
            "avg_cost_per_request": avg_cost_per_request,
            "most_used_model": max(
                self.usage_tracking["cost_per_model"].items(),
                key=lambda x: x[1],
                default=("none", 0)
            )[0],
            "cost_optimization_suggestions": await self._generate_cost_suggestions()
        }

    async def _generate_cost_suggestions(self) -> List[str]:
        """Generate cost optimization suggestions."""
        suggestions = []
        
        if self.usage_tracking["total_cost"] > 10.0:
            suggestions.append("Consider using command-light model for simple tasks")
        
        # Check if command model is overused for simple tasks
        command_cost = self.usage_tracking["cost_per_model"].get("command", 0)
        light_cost = self.usage_tracking["cost_per_model"].get("command-light", 0)
        
        if command_cost > light_cost * 3:
            suggestions.append("Review task complexity - many could use the lighter model")
        
        if len(suggestions) == 0:
            suggestions.append("Usage patterns look optimized!")
        
        return suggestions

    async def close(self) -> None:
        """Clean up resources and close connections."""
        if self.session:
            await self.session.aclose()
            self.session = None
            
        logger.info("✅ Cohere client closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Factory function for easy instantiation
def create_cohere_client(
    api_key: Optional[str] = None,
    enable_prompt_optimization: bool = True,
    enable_cost_optimization: bool = True
) -> CohereEnterpriseClient:
    """
    Factory function to create Cohere client with enterprise configuration.
    
    Args:
        api_key: Cohere API key
        enable_prompt_optimization: Enable prompt optimization features
        enable_cost_optimization: Enable cost optimization features
        
    Returns:
        Configured CohereEnterpriseClient instance
    """
    return CohereEnterpriseClient(
        api_key=api_key,
        enable_prompt_optimization=enable_prompt_optimization,
        enable_cost_optimization=enable_cost_optimization
    )


# Example usage for creator workflows
async def example_creator_content_generation():
    """Example of creator-specific content generation."""
    try:
        client = create_cohere_client(api_key="your-api-key")
        
        # Generate song lyrics for a musician
        lyrics_response = await client.generate_creator_content(
            creator_type="musician",
            content_type="song_lyrics",
            template_data={
                "genre": "pop",
                "topic": "overcoming challenges",
                "style": "uplifting and motivational",
                "mood": "inspiring",
                "audience": "young adults"
            },
            custom_instructions="Make it radio-friendly with a memorable hook"
        )
        
        print(f"🎵 Generated lyrics:\n{lyrics_response.text}")
        print(f"💰 Cost: ${lyrics_response.cost_estimate:.4f}")
        
        # Generate blog post for a blogger
        blog_response = await client.generate_creator_content(
            creator_type="blogger",
            content_type="blog_post",
            template_data={
                "topic": "sustainable living tips",
                "audience": "environmentally conscious millennials",
                "tone": "friendly and informative",
                "word_count": "1000-1200 words",
                "keywords": "sustainable living, eco-friendly, green lifestyle"
            }
        )
        
        print(f"📝 Generated blog post preview:\n{blog_response.text[:200]}...")
        print(f"💰 Cost: ${blog_response.cost_estimate:.4f}")
        
        # Get usage analytics
        analytics = await client.get_usage_analytics()
        print(f"📊 Total requests: {analytics['usage_summary']['total_requests']}")
        print(f"💸 Total cost: ${analytics['usage_summary']['total_cost']:.4f}")
        print(f"💡 Suggestions: {analytics['cost_optimization_suggestions']}")
        
        await client.close()
        
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_creator_content_generation())