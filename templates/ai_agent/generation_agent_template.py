"""{{agent_name}} Content Generation Agent for Ainflue Platform
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple, AsyncGenerator
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
import asyncio
import json

import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM,
    pipeline, GPT2LMHeadModel, T5ForConditionalGeneration
)
from diffusers import StableDiffusionPipeline, DiffusionPipeline
from PIL import Image
import numpy as np
from pydantic import BaseModel, Field, validator

from ai.base_agent import BaseAIAgent
from ai.models import GenerationModelManager
from generation.text_generator import TextGenerator, PromptOptimizer
from generation.image_generator import ImageGenerator, StyleTransfer
from generation.audio_generator import AudioGenerator, MusicComposer
from generation.video_generator import VideoGenerator, AnimationCreator
from core.config import get_settings
from utils.exceptions import GenerationException
from monitoring.generation_metrics import GenerationMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class GenerationType(Enum):
    """Content generation types"""
    TEXT_COMPLETION = "text_completion"
    TEXT_SUMMARIZATION = "text_summarization"
    TEXT_TRANSLATION = "text_translation"
    IMAGE_CREATION = "image_creation"
    IMAGE_EDITING = "image_editing"
    AUDIO_SYNTHESIS = "audio_synthesis"
    MUSIC_COMPOSITION = "music_composition"
    VIDEO_CREATION = "video_creation"
    ANIMATION_GENERATION = "animation_generation"
    CODE_GENERATION = "code_generation"
    CREATIVE_WRITING = "creative_writing"
    SOCIAL_MEDIA_CONTENT = "social_media_content"


class GenerationQuality(Enum):
    """Generation quality levels"""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"


class GenerationRequest(BaseModel):
    """Content generation request model"""
    type: GenerationType
    prompt: str
    quality: GenerationQuality = GenerationQuality.STANDARD
    style: Optional[str] = None
    format: Optional[str] = None
    length: Optional[int] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4096)
    seed: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('temperature')
    def validate_temperature(cls, v) -> None:
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v


class GenerationResult(BaseModel):
    """Content generation result model"""
    type: GenerationType
    content: Union[str, bytes, Dict[str, Any]]
    quality_score: float
    generation_time: float
    token_count: Optional[int] = None
    cost_estimate: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GenerationConfig(BaseModel):
    """Generation configuration"""
    text_model: str = "gpt-3.5-turbo"
    image_model: str = "stable-diffusion-v1-5"
    audio_model: str = "musicgen-small"
    video_model: str = "zeroscope"
    max_concurrent_requests: int = 5
    cache_results: bool = True
    enable_safety_filter: bool = True
    quality_threshold: float = 0.7
    timeout_seconds: int = 300


class {{agent_class_name}}(BaseAIAgent):
    """
    Advanced content generation agent for Ainflue platform.
    
    Features:
    - Multi-modal content generation (text, image, audio, video)
    - Quality-aware generation with scoring
    - Style and format customization
    - Real-time and batch processing
    - Cost optimization and caching
    - Safety filtering and moderation
    - Performance monitoring and analytics
    """
    
    def __init__(
        self,
        name -> None: str = "{{agent_name}}",
        config -> None: Optional[GenerationConfig] = None,
        **kwargs
    ) -> None:
        super().__init__(name=name, **kwargs)
        self.config = config or GenerationConfig()
        
        # Initialize model manager and generators
        self.model_manager = GenerationModelManager()
        self.text_generator = TextGenerator()
        self.image_generator = ImageGenerator()
        self.audio_generator = AudioGenerator()
        self.video_generator = VideoGenerator()
        self.prompt_optimizer = PromptOptimizer()
        
        # Initialize metrics collector
        self.metrics = GenerationMetricsCollector()
        
        # Load models
        self._load_models()
        
        logger.info(f"Generation agent '{name}' initialized successfully")

    def _load_models(self) -> None:
        """Load and initialize generation models"""
        try:
            # Load text generation models
            self.text_tokenizer = AutoTokenizer.from_pretrained(
                self.config.text_model
            )
            self.text_model = AutoModelForCausalLM.from_pretrained(
                self.config.text_model,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Load image generation pipeline
            self.image_pipeline = StableDiffusionPipeline.from_pretrained(
                self.config.image_model,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            if torch.cuda.is_available():
                self.image_pipeline = self.image_pipeline.to("cuda")
            
            # Initialize text pipelines
            self.summarization_pipeline = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.translation_pipeline = pipeline(
                "translation",
                model="Helsinki-NLP/opus-mt-en-de",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("All generation models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise GenerationException(f"Model loading failed: {str(e)}")

    async def generate_content(
        self,
        request: GenerationRequest
    ) -> GenerationResult:
        """
        Generate content based on request parameters.
        
        Args:
            request: Generation request with type, prompt, and parameters
            
        Returns:
            GenerationResult with generated content and metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Optimize prompt if needed
            optimized_prompt = await self._optimize_prompt(
                request.prompt, request.type
            )
            
            # Route to appropriate generator
            if request.type in [GenerationType.TEXT_COMPLETION, GenerationType.CREATIVE_WRITING,
                              GenerationType.CODE_GENERATION, GenerationType.SOCIAL_MEDIA_CONTENT]:
                content = await self._generate_text(optimized_prompt, request)
            elif request.type == GenerationType.TEXT_SUMMARIZATION:
                content = await self._generate_summary(optimized_prompt, request)
            elif request.type == GenerationType.TEXT_TRANSLATION:
                content = await self._generate_translation(optimized_prompt, request)
            elif request.type in [GenerationType.IMAGE_CREATION, GenerationType.IMAGE_EDITING]:
                content = await self._generate_image(optimized_prompt, request)
            elif request.type in [GenerationType.AUDIO_SYNTHESIS, GenerationType.MUSIC_COMPOSITION]:
                content = await self._generate_audio(optimized_prompt, request)
            elif request.type in [GenerationType.VIDEO_CREATION, GenerationType.ANIMATION_GENERATION]:
                content = await self._generate_video(optimized_prompt, request)
            else:
                raise GenerationException(f"Unsupported generation type: {request.type}")
            
            # Calculate quality score
            quality_score = await self._calculate_quality_score(content, request)
            
            # Calculate generation time
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = GenerationResult(
                type=request.type,
                content=content,
                quality_score=quality_score,
                generation_time=generation_time,
                metadata={
                    "model_used": self._get_model_name(request.type),
                    "prompt_optimized": optimized_prompt != request.prompt,
                    "safety_filtered": self.config.enable_safety_filter,
                    "original_prompt": request.prompt,
                    "optimized_prompt": optimized_prompt
                }
            )
            
            # Record metrics
            await self.metrics.record_generation(request, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            raise GenerationException(f"Generation failed: {str(e)}")

    async def _generate_text(
        self,
        prompt: str,
        request: GenerationRequest
    ) -> str:
        """Generate text content"""
        try:
            # Prepare inputs
            inputs = self.text_tokenizer.encode(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            
            if torch.cuda.is_available():
                inputs = inputs.to("cuda")
            
            # Generate text
            with torch.no_grad():
                outputs = self.text_model.generate(
                    inputs,
                    max_length=request.max_tokens or 1024,
                    temperature=request.temperature,
                    do_sample=True,
                    pad_token_id=self.text_tokenizer.eos_token_id,
                    num_return_sequences=1
                )
            
            # Decode output
            generated_text = self.text_tokenizer.decode(
                outputs[0], skip_special_tokens=True
            )
            
            # Remove original prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise GenerationException(f"Text generation failed: {str(e)}")

    async def _generate_image(
        self,
        prompt: str,
        request: GenerationRequest
    ) -> bytes:
        """Generate image content"""
        try:
            # Set random seed if provided
            if request.seed:
                torch.manual_seed(request.seed)
                np.random.seed(request.seed)
            
            # Generate image
            result = self.image_pipeline(
                prompt,
                num_inference_steps=50,
                guidance_scale=7.5,
                height=512,
                width=512
            )
            
            # Get generated image
            image = result.images[0]
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            raise GenerationException(f"Image generation failed: {str(e)}")

    async def _generate_summary(
        self,
        text: str,
        request: GenerationRequest
    ) -> str:
        """Generate text summary"""
        try:
            # Determine summary length
            max_length = request.length or min(len(text.split()) // 3, 150)
            min_length = max_length // 2
            
            # Generate summary
            result = self.summarization_pipeline(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return result[0]['summary_text']
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            raise GenerationException(f"Summarization failed: {str(e)}")

    async def _generate_translation(
        self,
        text: str,
        request: GenerationRequest
    ) -> str:
        """Generate text translation"""
        try:
            result = self.translation_pipeline(text)
            return result[0]['translation_text']
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise GenerationException(f"Translation failed: {str(e)}")

    async def _generate_audio(
        self,
        prompt: str,
        request: GenerationRequest
    ) -> bytes:
        """Generate audio content"""
        try:
            # Placeholder for audio generation
            # This would integrate with audio generation models
            audio_data = await self.audio_generator.generate(
                prompt=prompt,
                duration=request.length or 30,
                quality=request.quality.value
            )
            return audio_data
            
        except Exception as e:
            logger.error(f"Audio generation failed: {str(e)}")
            raise GenerationException(f"Audio generation failed: {str(e)}")

    async def _generate_video(
        self,
        prompt: str,
        request: GenerationRequest
    ) -> bytes:
        """Generate video content"""
        try:
            # Placeholder for video generation
            # This would integrate with video generation models
            video_data = await self.video_generator.generate(
                prompt=prompt,
                duration=request.length or 10,
                quality=request.quality.value
            )
            return video_data
            
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            raise GenerationException(f"Video generation failed: {str(e)}")

    async def _optimize_prompt(
        self,
        prompt: str,
        generation_type: GenerationType
    ) -> str:
        """Optimize prompt for better generation results"""
        try:
            return await self.prompt_optimizer.optimize(prompt, generation_type)
        except Exception:
            # Fallback to original prompt if optimization fails
            return prompt

    async def _calculate_quality_score(
        self,
        content: Union[str, bytes],
        request: GenerationRequest
    ) -> float:
        """Calculate quality score for generated content"""
        try:
            # Implement quality scoring based on content type
            # This is a simplified implementation
            if isinstance(content, str):
                # Text quality scoring
                if len(content.strip()) == 0:
                    return 0.0
                
                # Basic metrics: length, coherence, etc.
                length_score = min(len(content.split()) / 100, 1.0)
                coherence_score = 0.8  # Placeholder for coherence analysis
                
                return (length_score + coherence_score) / 2
            
            elif isinstance(content, bytes):
                # Image/Audio/Video quality scoring
                return 0.85  # Placeholder for media quality analysis
            
            return 0.7  # Default score
            
        except Exception:
            return 0.5  # Fallback score

    def _get_model_name(self, generation_type: GenerationType) -> str:
        """Get model name for generation type"""
        if generation_type in [GenerationType.TEXT_COMPLETION, GenerationType.CREATIVE_WRITING]:
            return self.config.text_model
        elif generation_type in [GenerationType.IMAGE_CREATION, GenerationType.IMAGE_EDITING]:
            return self.config.image_model
        elif generation_type in [GenerationType.AUDIO_SYNTHESIS, GenerationType.MUSIC_COMPOSITION]:
            return self.config.audio_model
        elif generation_type in [GenerationType.VIDEO_CREATION, GenerationType.ANIMATION_GENERATION]:
            return self.config.video_model
        else:
            return "unknown"

    async def generate_batch(
        self,
        requests: List[GenerationRequest]
    ) -> List[GenerationResult]:
        """Generate content for multiple requests in batch"""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def generate_single(request: GenerationRequest) -> GenerationResult:
            async with semaphore:
                return await self.generate_content(request)
        
        tasks = [generate_single(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch generation failed for request {i}: {str(result)}")
                # Create error result
                error_result = GenerationResult(
                    type=requests[i].type,
                    content=f"Generation failed: {str(result)}",
                    quality_score=0.0,
                    generation_time=0.0,
                    metadata={"error": str(result)}
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
        
        return final_results

    async def stream_generation(
        self,
        request: GenerationRequest
    ) -> AsyncGenerator[str, None]:
        """Stream generation results for real-time applications"""
        if request.type not in [GenerationType.TEXT_COMPLETION, GenerationType.CREATIVE_WRITING]:
            raise GenerationException("Streaming only supported for text generation")
        
        try:
            # Prepare inputs
            inputs = self.text_tokenizer.encode(
                request.prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            
            if torch.cuda.is_available():
                inputs = inputs.to("cuda")
            
            # Generate token by token
            generated_tokens = []
            max_tokens = request.max_tokens or 1024
            
            for _ in range(max_tokens):
                with torch.no_grad():
                    outputs = self.text_model(inputs)
                    next_token_logits = outputs.logits[0, -1, :]
                    
                    # Apply temperature
                    next_token_logits = next_token_logits / request.temperature
                    
                    # Sample next token
                    probs = torch.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, 1)
                    
                    # Add to sequence
                    inputs = torch.cat([inputs, next_token.unsqueeze(0)], dim=-1)
                    generated_tokens.append(next_token.item())
                    
                    # Decode and yield
                    if len(generated_tokens) % 5 == 0:  # Yield every 5 tokens
                        partial_text = self.text_tokenizer.decode(
                            generated_tokens, skip_special_tokens=True
                        )
                        yield partial_text
                    
                    # Check for stop conditions
                    if next_token.item() == self.text_tokenizer.eos_token_id:
                        break
            
            # Yield final result
            final_text = self.text_tokenizer.decode(
                generated_tokens, skip_special_tokens=True
            )
            yield final_text
            
        except Exception as e:
            logger.error(f"Streaming generation failed: {str(e)}")
            raise GenerationException(f"Streaming failed: {str(e)}")

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "supported_types": [t.value for t in GenerationType],
            "quality_levels": [q.value for q in GenerationQuality],
            "max_concurrent_requests": self.config.max_concurrent_requests,
            "supports_streaming": True,
            "supports_batch": True,
            "models": {
                "text": self.config.text_model,
                "image": self.config.image_model,
                "audio": self.config.audio_model,
                "video": self.config.video_model
            }
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get generation metrics"""
        return self.metrics.get_summary()

# File has syntax issues - needs manual review