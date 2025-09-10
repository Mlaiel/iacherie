"""Anthropic Claude API Integration
=================================

Integration with Anthropic's Claude AI models for advanced text generation,
analysis, and conversation capabilities with focus on safety and reliability.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import aiohttp
from datetime import datetime


class ClaudeModel(Enum):
    """Claude model enumeration"""
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"  
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_2_1 = "claude-2.1"
    CLAUDE_2 = "claude-2.0"
    CLAUDE_INSTANT = "claude-instant-1.2"


@dataclass
class AnthropicConfig:
    """Anthropic configuration"""
    api_key: str
    base_url: str = "https://api.anthropic.com"
    version: str = "2023-06-01"
    timeout: int = 60
    max_retries: int = 3


@dataclass
class ClaudeMessage:
    """Claude message structure"""
    role: str  # "user", "assistant"
    content: Union[str, List[Dict[str, Any]]]


@dataclass
class ClaudeToolDefinition:
    """Claude tool definition for function calling"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class AnthropicIntegration:
    """Anthropic Claude API integration"""
    
    def __init__(self, config: AnthropicConfig, rate_limiter=None, cache_manager=None):
        """Initialize Anthropic integration
        
        Args:
            config: Anthropic configuration
            rate_limiter: Rate limiter instance
            cache_manager: Cache manager instance
        """
        self.config = config
        self.rate_limiter = rate_limiter
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
        
        # Session for HTTP requests
        self.session = None
        
        # Usage tracking
        self.usage_stats = {
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "requests_count": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    async def initialize(self):
        """Initialize the integration"""
        try:
            # Create HTTP session
            headers = {
                "x-api-key": self.config.api_key,
                "anthropic-version": self.config.version,
                "Content-Type": "application/json",
                "User-Agent": "Ainflue-Anthropic-Integration/1.0"
            }
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
            
            # Test connection
            await self._test_connection()
            
            self.logger.info("Anthropic integration initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic integration: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the integration"""
        if self.session:
            await self.session.close()
        self.logger.info("Anthropic integration shutdown complete")
    
    async def _test_connection(self):
        """Test Anthropic API connection"""
        try:
            # Create a simple test message
            test_response = await self.create_message(
                model=ClaudeModel.CLAUDE_3_HAIKU,
                messages=[ClaudeMessage(role="user", content="Hello")],
                max_tokens=10
            )
            
            if test_response:
                self.logger.info("Anthropic API connection test successful")
            else:
                raise Exception("API test failed - no response")
                
        except Exception as e:
            self.logger.error(f"Anthropic API connection test failed: {e}")
            raise
    
    async def create_message(self, model: ClaudeModel, messages: List[ClaudeMessage],
                           max_tokens: int = 4096,
                           temperature: float = 0.7,
                           system: Optional[str] = None,
                           tools: Optional[List[ClaudeToolDefinition]] = None,
                           tool_choice: Optional[Dict[str, Any]] = None,
                           stream: bool = False,
                           **kwargs) -> Union[Dict[str, Any], AsyncGenerator]:
        """Create message with Claude
        
        Args:
            model: Claude model to use
            messages: List of messages
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system: System prompt
            tools: Available tools for function calling
            tool_choice: Tool choice configuration
            stream: Whether to stream response
            **kwargs: Additional parameters
            
        Returns:
            Union[Dict[str, Any], AsyncGenerator]: Response or stream
        """
        try:
            # Check rate limits
            if self.rate_limiter:
                allowed = await self.rate_limiter.allow_request("anthropic", rule_name="claude_requests")
                if not allowed:
                    raise Exception("Rate limit exceeded")
            
            # Prepare request
            request_data = {
                "model": model.value,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content
                    } for msg in messages
                ],
                "stream": stream
            }
            
            if system:
                request_data["system"] = system
            
            if tools:
                request_data["tools"] = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.input_schema
                    } for tool in tools
                ]
            
            if tool_choice:
                request_data["tool_choice"] = tool_choice
            
            # Add additional parameters
            request_data.update(kwargs)
            
            # Check cache for non-streaming requests
            cache_key = None
            if not stream and self.cache_manager:
                cache_key = f"anthropic:message:{hash(json.dumps(request_data, sort_keys=True))}"
                cached_response = await self.cache_manager.get(cache_key)
                if cached_response:
                    self.usage_stats["cache_hits"] += 1
                    return cached_response
                else:
                    self.usage_stats["cache_misses"] += 1
            
            # Make request
            url = f"{self.config.base_url}/v1/messages"
            
            if stream:
                return self._stream_message(url, request_data)
            else:
                async with self.session.post(url, json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Update usage stats
                        if "usage" in result:
                            usage = result["usage"]
                            self.usage_stats["input_tokens"] += usage.get("input_tokens", 0)
                            self.usage_stats["output_tokens"] += usage.get("output_tokens", 0)
                            self.usage_stats["total_tokens"] += usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                        
                        self.usage_stats["requests_count"] += 1
                        
                        # Cache response
                        if cache_key and self.cache_manager:
                            await self.cache_manager.set(cache_key, result, ttl=300)
                        
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(f"Anthropic API error: {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"Message creation error: {e}")
            raise
    
    async def _stream_message(self, url: str, request_data: Dict[str, Any]) -> AsyncGenerator:
        """Stream message response
        
        Args:
            url: API URL
            request_data: Request data
            
        Yields:
            Dict[str, Any]: Streaming response chunks
        """
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error: {response.status} - {error_text}")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            self.logger.error(f"Streaming message error: {e}")
            raise
    
    async def analyze_text(self, text: str, analysis_type: str = "general",
                         model: ClaudeModel = ClaudeModel.CLAUDE_3_SONNET) -> Dict[str, Any]:
        """Analyze text with Claude
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis
            model: Claude model to use
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        try:
            # Define analysis prompts
            analysis_prompts = {
                "general": "Please analyze this text and provide insights about its content, tone, structure, and key themes.",
                "sentiment": "Analyze the sentiment of this text. Identify emotions, mood, and overall sentiment polarity.",
                "summary": "Provide a concise summary of this text, highlighting the main points and key information.",
                "toxicity": "Analyze this text for any toxic, harmful, or inappropriate content. Provide a safety assessment.",
                "keywords": "Extract the most important keywords and key phrases from this text.",
                "readability": "Analyze the readability and writing quality of this text, including complexity and clarity.",
                "fact_check": "Identify factual claims in this text and assess their verifiability.",
                "structure": "Analyze the structure and organization of this text, including flow and coherence."
            }
            
            prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
            
            # Create system prompt
            system_prompt = f"""You are an expert text analyst. Your task is to {prompt}
            
Please provide your analysis in a structured format with clear sections and insights."""
            
            # Create message
            message = ClaudeMessage(
                role="user",
                content=f"Text to analyze:\n\n{text}"
            )
            
            # Get analysis
            response = await self.create_message(
                model=model,
                messages=[message],
                system=system_prompt,
                max_tokens=2048,
                temperature=0.3
            )
            
            return {
                "analysis_type": analysis_type,
                "text_length": len(text),
                "model_used": model.value,
                "analysis": response.get("content", [{}])[0].get("text", ""),
                "usage": response.get("usage", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Text analysis error: {e}")
            raise
    
    async def generate_content(self, prompt: str, content_type: str = "article",
                             style: str = "professional",
                             length: str = "medium",
                             model: ClaudeModel = ClaudeModel.CLAUDE_3_SONNET) -> Dict[str, Any]:
        """Generate content with Claude
        
        Args:
            prompt: Content generation prompt
            content_type: Type of content (article, blog, social, etc.)
            style: Writing style
            length: Content length
            model: Claude model to use
            
        Returns:
            Dict[str, Any]: Generated content
        """
        try:
            # Define content templates
            content_templates = {
                "article": "Write a comprehensive article",
                "blog": "Write an engaging blog post",
                "social": "Create social media content",
                "email": "Write a professional email",
                "story": "Write a creative story",
                "script": "Write a script or dialogue",
                "description": "Write a detailed description",
                "review": "Write a thorough review"
            }
            
            # Define style guidelines
            style_guidelines = {
                "professional": "professional, formal, and authoritative tone",
                "casual": "casual, friendly, and conversational tone",
                "creative": "creative, imaginative, and engaging tone",
                "technical": "technical, precise, and detailed approach",
                "persuasive": "persuasive, compelling, and convincing tone",
                "educational": "educational, informative, and clear explanations"
            }
            
            # Define length specifications
            length_specs = {
                "short": "concise and brief (200-400 words)",
                "medium": "moderate length (400-800 words)",
                "long": "comprehensive and detailed (800-1500 words)",
                "extended": "extensive and thorough (1500+ words)"
            }
            
            # Build system prompt
            content_instruction = content_templates.get(content_type, "Write content")
            style_instruction = style_guidelines.get(style, "appropriate tone")
            length_instruction = length_specs.get(length, "appropriate length")
            
            system_prompt = f"""You are an expert content writer. Your task is to {content_instruction} with a {style_instruction}. 
            
The content should be {length_instruction}.

Guidelines:
- Create engaging, high-quality content
- Ensure proper structure and flow
- Use appropriate formatting
- Include relevant details and examples
- Maintain consistency throughout"""
            
            # Create message
            message = ClaudeMessage(
                role="user",
                content=prompt
            )
            
            # Generate content
            response = await self.create_message(
                model=model,
                messages=[message],
                system=system_prompt,
                max_tokens=3000,
                temperature=0.7
            )
            
            generated_content = response.get("content", [{}])[0].get("text", "")
            
            return {
                "content_type": content_type,
                "style": style,
                "length": length,
                "prompt": prompt,
                "generated_content": generated_content,
                "model_used": model.value,
                "word_count": len(generated_content.split()),
                "character_count": len(generated_content),
                "usage": response.get("usage", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Content generation error: {e}")
            raise
    
    async def translate_text(self, text: str, target_language: str,
                           source_language: str = "auto",
                           model: ClaudeModel = ClaudeModel.CLAUDE_3_SONNET) -> Dict[str, Any]:
        """Translate text using Claude
        
        Args:
            text: Text to translate
            target_language: Target language
            source_language: Source language (auto-detect if "auto")
            model: Claude model to use
            
        Returns:
            Dict[str, Any]: Translation result
        """
        try:
            # Build translation prompt
            if source_language == "auto":
                system_prompt = f"""You are an expert translator. Please translate the following text to {target_language}.
                
First, detect the source language, then provide an accurate and natural translation that preserves the meaning, tone, and context."""
            else:
                system_prompt = f"""You are an expert translator. Please translate the following text from {source_language} to {target_language}.
                
Provide an accurate and natural translation that preserves the meaning, tone, and context."""
            
            # Create message
            message = ClaudeMessage(
                role="user",
                content=f"Text to translate:\n\n{text}"
            )
            
            # Get translation
            response = await self.create_message(
                model=model,
                messages=[message],
                system=system_prompt,
                max_tokens=2048,
                temperature=0.3
            )
            
            return {
                "source_language": source_language,
                "target_language": target_language,
                "original_text": text,
                "translated_text": response.get("content", [{}])[0].get("text", ""),
                "model_used": model.value,
                "usage": response.get("usage", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            raise
    
    async def code_analysis(self, code: str, language: str = "auto",
                          analysis_type: str = "review",
                          model: ClaudeModel = ClaudeModel.CLAUDE_3_SONNET) -> Dict[str, Any]:
        """Analyze code with Claude
        
        Args:
            code: Code to analyze
            language: Programming language
            analysis_type: Type of analysis
            model: Claude model to use
            
        Returns:
            Dict[str, Any]: Code analysis result
        """
        try:
            # Define analysis types
            analysis_types = {
                "review": "Provide a comprehensive code review with suggestions for improvement",
                "security": "Analyze the code for security vulnerabilities and best practices",
                "performance": "Analyze the code for performance optimization opportunities",
                "documentation": "Generate documentation for this code",
                "refactor": "Suggest refactoring improvements for better code quality",
                "bugs": "Identify potential bugs and issues in the code",
                "explain": "Explain what this code does in detail"
            }
            
            analysis_instruction = analysis_types.get(analysis_type, analysis_types["review"])
            
            # Build system prompt
            if language == "auto":
                system_prompt = f"""You are an expert software engineer and code reviewer. 
                
First, identify the programming language, then {analysis_instruction}.

Provide specific, actionable feedback with explanations."""
            else:
                system_prompt = f"""You are an expert {language} developer and code reviewer. 
                
{analysis_instruction}

Provide specific, actionable feedback with explanations."""
            
            # Create message
            message = ClaudeMessage(
                role="user",
                content=f"Code to analyze:\n\n```{language if language != 'auto' else ''}\n{code}\n```"
            )
            
            # Get analysis
            response = await self.create_message(
                model=model,
                messages=[message],
                system=system_prompt,
                max_tokens=3000,
                temperature=0.2
            )
            
            return {
                "language": language,
                "analysis_type": analysis_type,
                "code_length": len(code),
                "analysis": response.get("content", [{}])[0].get("text", ""),
                "model_used": model.value,
                "usage": response.get("usage", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Code analysis error: {e}")
            raise
    
    async def creative_writing(self, prompt: str, genre: str = "general",
                             length: str = "medium", style: str = "creative",
                             model: ClaudeModel = ClaudeModel.CLAUDE_3_OPUS) -> Dict[str, Any]:
        """Creative writing with Claude
        
        Args:
            prompt: Creative prompt
            genre: Writing genre
            length: Content length
            style: Writing style
            model: Claude model to use
            
        Returns:
            Dict[str, Any]: Creative writing result
        """
        try:
            # Define genres
            genre_styles = {
                "general": "engaging and creative",
                "fiction": "imaginative fictional narrative",
                "poetry": "poetic and lyrical",
                "screenplay": "screenplay format with dialogue and action",
                "comedy": "humorous and entertaining",
                "drama": "dramatic and emotionally engaging",
                "mystery": "mysterious and suspenseful",
                "scifi": "science fiction with futuristic elements",
                "fantasy": "fantasy with magical elements",
                "romance": "romantic and emotional"
            }
            
            genre_style = genre_styles.get(genre, "creative")
            
            # Build system prompt
            system_prompt = f"""You are a talented creative writer specializing in {genre} writing. 
            
Create {genre_style} content that is compelling, well-structured, and engaging.

Focus on:
- Strong character development (if applicable)
- Vivid descriptions and imagery
- Engaging dialogue (if applicable)
- Proper pacing and flow
- Emotional resonance
- Creative and original ideas"""
            
            # Create message
            message = ClaudeMessage(
                role="user",
                content=prompt
            )
            
            # Generate creative content
            response = await self.create_message(
                model=model,
                messages=[message],
                system=system_prompt,
                max_tokens=4000,
                temperature=0.8
            )
            
            generated_content = response.get("content", [{}])[0].get("text", "")
            
            return {
                "genre": genre,
                "style": style,
                "length": length,
                "prompt": prompt,
                "creative_content": generated_content,
                "model_used": model.value,
                "word_count": len(generated_content.split()),
                "usage": response.get("usage", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Creative writing error: {e}")
            raise
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics
        
        Returns:
            Dict[str, Any]: Usage statistics
        """
        stats = self.usage_stats.copy()
        stats["timestamp"] = datetime.utcnow().isoformat()
        
        # Calculate cache hit rate
        total_cache_requests = stats["cache_hits"] + stats["cache_misses"]
        if total_cache_requests > 0:
            stats["cache_hit_rate"] = stats["cache_hits"] / total_cache_requests
        else:
            stats["cache_hit_rate"] = 0.0
            
        return stats
    
    async def estimate_cost(self, model: ClaudeModel, input_tokens: int = 0, 
                          output_tokens: int = 0) -> Dict[str, float]:
        """Estimate cost for usage
        
        Args:
            model: Claude model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Dict[str, float]: Cost estimates
        """
        # Cost per 1M tokens (approximate, as of 2024)
        pricing = {
            ClaudeModel.CLAUDE_3_OPUS: {"input": 15.0, "output": 75.0},
            ClaudeModel.CLAUDE_3_SONNET: {"input": 3.0, "output": 15.0},
            ClaudeModel.CLAUDE_3_HAIKU: {"input": 0.25, "output": 1.25},
            ClaudeModel.CLAUDE_2_1: {"input": 8.0, "output": 24.0},
            ClaudeModel.CLAUDE_2: {"input": 8.0, "output": 24.0},
            ClaudeModel.CLAUDE_INSTANT: {"input": 0.8, "output": 2.4}
        }
        
        cost_estimate = {
            "total_cost": 0.0,
            "breakdown": {}
        }
        
        if model in pricing:
            prices = pricing[model]
            
            input_cost = (input_tokens / 1_000_000) * prices["input"]
            output_cost = (output_tokens / 1_000_000) * prices["output"]
            
            cost_estimate["breakdown"]["input_tokens"] = input_cost
            cost_estimate["breakdown"]["output_tokens"] = output_cost
            cost_estimate["total_cost"] = input_cost + output_cost
        
        return cost_estimate


# Integration factory function
def create_anthropic_integration(api_key: str, rate_limiter=None, 
                               cache_manager=None) -> AnthropicIntegration:
    """Create Anthropic integration instance
    
    Args:
        api_key: Anthropic API key
        rate_limiter: Rate limiter instance
        cache_manager: Cache manager instance
        
    Returns:
        AnthropicIntegration: Integration instance
    """
    config = AnthropicConfig(api_key=api_key)
    return AnthropicIntegration(config, rate_limiter, cache_manager)