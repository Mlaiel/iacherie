"""Stability AI Integration - Stable Diffusion and Image Generation
================================================================

Comprehensive integration with Stability AI platform including Stable Diffusion XL,
SDXL Turbo, Stable Video Diffusion, and other Stability AI models.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import base64
import uuid
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import io
from PIL import Image

import aiohttp
import aiofiles

logger = logging.getLogger(__name__)

class StabilityModel(Enum):
    """Stability AI model types."""
    STABLE_DIFFUSION_XL = "stable-diffusion-xl-1024-v1-0"
    STABLE_DIFFUSION_XL_BETA = "stable-diffusion-xl-beta-v2-2-2"
    STABLE_DIFFUSION_512 = "stable-diffusion-512-v2-1"
    STABLE_DIFFUSION_768 = "stable-diffusion-768-v2-1"
    SDXL_TURBO = "sdxl-turbo"
    STABLE_VIDEO = "stable-video-diffusion-img2vid-v1-1"
    STABLE_AUDIO = "stable-audio-open-1-0"
    STABLE_CODE = "stable-code-3b"

class ImageStyle(Enum):
    """Image generation styles."""
    PHOTOGRAPHIC = "photographic"
    DIGITAL_ART = "digital-art"
    COMIC_BOOK = "comic-book"
    FANTASY_ART = "fantasy-art"
    LINE_ART = "line-art"
    ANALOG_FILM = "analog-film"
    NEON_PUNK = "neon-punk"
    ISOMETRIC = "isometric"
    LOW_POLY = "low-poly"
    ORIGAMI = "origami"
    MODELING_COMPOUND = "modeling-compound"
    CINEMATIC = "cinematic"
    THREE_D_MODEL = "3d-model"
    PIXEL_ART = "pixel-art"

class AspectRatio(Enum):
    """Supported aspect ratios."""
    SQUARE_1024 = "1024x1024"
    PORTRAIT_896 = "896x1152"
    LANDSCAPE_1152 = "1152x896"
    PORTRAIT_832 = "832x1216"
    LANDSCAPE_1216 = "1216x832"
    PORTRAIT_768 = "768x1344"
    LANDSCAPE_1344 = "1344x768"
    PORTRAIT_640 = "640x1536"
    LANDSCAPE_1536 = "1536x640"

@dataclass
class StabilityRequest:
    """Stability AI API request."""
    model: StabilityModel
    prompt: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Image generation parameters
    negative_prompt: str = ""
    aspect_ratio: AspectRatio = AspectRatio.SQUARE_1024
    style_preset: Optional[ImageStyle] = None
    seed: Optional[int] = None
    
    # Quality settings
    cfg_scale: float = 7.0
    steps: int = 30
    sampler: str = "K_DPMPP_2M"
    
    # Input image (for img2img, inpainting, etc.)
    init_image: Optional[str] = None  # Base64 encoded
    mask_image: Optional[str] = None  # Base64 encoded
    strength: Optional[float] = None
    
    # Video generation (for Stable Video)
    motion_bucket_id: int = 127
    noise_augmentation: float = 0.02
    fps: int = 6
    
    # Advanced options
    clip_guidance_preset: str = "FAST_BLUE"
    output_format: str = "PNG"
    
    # Request metadata
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StabilityResponse:
    """Stability AI API response."""
    request_id: str
    model: StabilityModel
    
    # Generated content
    images: List[str] = field(default_factory=list)  # Base64 encoded
    videos: List[str] = field(default_factory=list)  # Base64 encoded
    audio: List[str] = field(default_factory=list)   # Base64 encoded
    
    # Generation metadata
    seed: Optional[int] = None
    finish_reason: str = "SUCCESS"
    
    # Performance metrics
    latency_ms: Optional[float] = None
    cost_estimate: Optional[float] = None
    
    # Error handling
    error: Optional[str] = None
    error_code: Optional[str] = None
    error_details: Dict[str, Any] = field(default_factory=dict)
    
    # Response metadata
    response_metadata: Dict[str, Any] = field(default_factory=dict)
    
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class StabilityConfiguration:
    """Stability AI integration configuration."""
    # Authentication
    api_key: str
    api_host: str = "https://api.stability.ai"
    api_version: str = "v1"
    
    # Default parameters
    default_model: StabilityModel = StabilityModel.STABLE_DIFFUSION_XL
    default_steps: int = 30
    default_cfg_scale: float = 7.0
    default_aspect_ratio: AspectRatio = AspectRatio.SQUARE_1024
    
    # Rate limiting
    requests_per_minute: int = 10
    max_concurrent_requests: int = 3
    
    # Performance settings
    timeout_seconds: int = 120  # Image generation can take time
    retry_attempts: int = 3
    retry_delay: float = 2.0
    
    # Cost management
    monthly_budget_usd: Optional[float] = None
    cost_per_generation: float = 0.04  # Approximate cost
    cost_alerts_enabled: bool = True
    
    # Output settings
    save_generated_images: bool = True
    output_directory: str = "/tmp/stability_outputs"
    
    # Quality settings
    enable_safety_check: bool = True
    content_filter_enabled: bool = True

class StabilityAIIntegration:
    """Comprehensive Stability AI integration."""
    
    def __init__(self, config -> None: StabilityConfiguration) -> None:
        self.config = config
        self.session = None
        
        # Usage tracking
        self.request_count = 0
        self.generation_count = 0
        self.cost_tracking = 0.0
        self.last_reset = datetime.utcnow()
        
        # Performance monitoring
        self.response_times = []
        self.error_count = 0
        
        # Rate limiting
        self.request_semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self.last_request_time = 0
        
        logger.info("Stability AI Integration initialized")

    async def initialize(self) -> None:
        """Initialize Stability AI integration."""
        try:
            # Setup HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds),
                headers={
                    'Authorization': f'Bearer {self.config.api_key}',
                    'User-Agent': 'Ainflue-StabilityAI/1.0',
                    'Accept': 'application/json'
                }
            )
            
            # Create output directory
            import os
            os.makedirs(self.config.output_directory, exist_ok=True)
            
            # Test API connection
            await self._test_connection()
            
            logger.info("Stability AI integration initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize Stability AI integration: {e}")
            raise

    async def _test_connection(self) -> None:
        """Test API connection."""
        try:
            url = f"{self.config.api_host}/{self.config.api_version}/user/account"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Connected to Stability AI - Credits: {data.get('credits', 'unknown')}")
                else:
                    raise Exception(f"API test failed: {response.status}")
                    
        except Exception as e:
            logger.warning(f"API connection test failed: {e}")

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: StabilityModel = None,
        aspect_ratio: AspectRatio = None,
        style_preset: Optional[ImageStyle] = None,
        steps: Optional[int] = None,
        cfg_scale: Optional[float] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> StabilityResponse:
        """Generate image using Stability AI."""
        request = StabilityRequest(
            model=model or self.config.default_model,
            prompt=prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio or self.config.default_aspect_ratio,
            style_preset=style_preset,
            steps=steps or self.config.default_steps,
            cfg_scale=cfg_scale or self.config.default_cfg_scale,
            seed=seed,
            parameters=kwargs
        )
        
        return await self._execute_generation_request(request)

    async def image_to_image(
        self,
        prompt: str,
        init_image: str,  # Base64 encoded
        strength: float = 0.35,
        negative_prompt: str = "",
        model: StabilityModel = None,
        **kwargs
    ) -> StabilityResponse:
        """Generate image from input image using Stability AI."""
        request = StabilityRequest(
            model=model or self.config.default_model,
            prompt=prompt,
            negative_prompt=negative_prompt,
            init_image=init_image,
            strength=strength,
            parameters=kwargs
        )
        
        return await self._execute_img2img_request(request)

    async def inpaint_image(
        self,
        prompt: str,
        init_image: str,  # Base64 encoded
        mask_image: str,  # Base64 encoded
        negative_prompt: str = "",
        model: StabilityModel = None,
        **kwargs
    ) -> StabilityResponse:
        """Inpaint image using Stability AI."""
        request = StabilityRequest(
            model=model or self.config.default_model,
            prompt=prompt,
            negative_prompt=negative_prompt,
            init_image=init_image,
            mask_image=mask_image,
            parameters=kwargs
        )
        
        return await self._execute_inpaint_request(request)

    async def upscale_image(
        self,
        image: str,  # Base64 encoded
        model: str = "esrgan-v1-x2plus",
        **kwargs
    ) -> StabilityResponse:
        """Upscale image using Stability AI."""
        request = StabilityRequest(
            model=StabilityModel.STABLE_DIFFUSION_XL,  # Placeholder
            prompt="",  # Not used for upscaling
            init_image=image,
            parameters={'upscale_model': model, **kwargs}
        )
        
        return await self._execute_upscale_request(request)

    async def generate_video(
        self,
        init_image: str,  # Base64 encoded
        model: StabilityModel = StabilityModel.STABLE_VIDEO,
        motion_bucket_id: int = 127,
        noise_augmentation: float = 0.02,
        fps: int = 6,
        **kwargs
    ) -> StabilityResponse:
        """Generate video from image using Stable Video Diffusion."""
        request = StabilityRequest(
            model=model,
            prompt="",  # Not used for video generation
            init_image=init_image,
            motion_bucket_id=motion_bucket_id,
            noise_augmentation=noise_augmentation,
            fps=fps,
            parameters=kwargs
        )
        
        return await self._execute_video_request(request)

    async def _execute_generation_request(self, request: StabilityRequest) -> StabilityResponse:
        """Execute text-to-image generation request."""
        start_time = time.time()
        
        try:
            async with self.request_semaphore:
                await self._check_rate_limits()
                
                # Prepare request URL
                engine = self._get_engine_id(request.model)
                url = f"{self.config.api_host}/{self.config.api_version}/generation/{engine}/text-to-image"
                
                # Prepare form data
                data = aiohttp.FormData()
                
                # Add text prompts
                data.add_field('text_prompts[0][text]', request.prompt)
                data.add_field('text_prompts[0][weight]', '1')
                
                if request.negative_prompt:
                    data.add_field('text_prompts[1][text]', request.negative_prompt)
                    data.add_field('text_prompts[1][weight]', '-1')
                
                # Add generation parameters
                data.add_field('cfg_scale', str(request.cfg_scale))
                data.add_field('steps', str(request.steps))
                data.add_field('sampler', request.sampler)
                
                if request.seed:
                    data.add_field('seed', str(request.seed))
                    
                if request.style_preset:
                    data.add_field('style_preset', request.style_preset.value)
                    
                # Add dimensions
                width, height = self._parse_aspect_ratio(request.aspect_ratio)
                data.add_field('width', str(width))
                data.add_field('height', str(height))
                
                # Additional parameters
                data.add_field('samples', '1')
                data.add_field('clip_guidance_preset', request.clip_guidance_preset)
                
                # Execute request
                async with self.session.post(url, data=data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Extract generated images
                        images = []
                        for artifact in response_data.get('artifacts', []):
                            if artifact['finishReason'] == 'SUCCESS':
                                images.append(artifact['base64'])
                                
                        # Save images if configured
                        if self.config.save_generated_images and images:
                            await self._save_images(images, request.request_id)
                            
                        result = StabilityResponse(
                            request_id=request.request_id,
                            model=request.model,
                            images=images,
                            seed=response_data.get('artifacts', [{}])[0].get('seed'),
                            latency_ms=(time.time() - start_time) * 1000,
                            cost_estimate=self.config.cost_per_generation
                        )
                        
                        # Update usage tracking
                        await self._update_usage_tracking(request, result)
                        
                        return result
                        
                    else:
                        error_text = await response.text()
                        raise Exception(f"Generation failed: {response.status} - {error_text}")
                        
        except Exception as e:
            self.error_count += 1
            logger.error(f"Stability AI generation failed: {e}")
            
            return StabilityResponse(
                request_id=request.request_id,
                model=request.model,
                error=str(e),
                error_code="generation_error",
                latency_ms=(time.time() - start_time) * 1000
            )

    async def _execute_img2img_request(self, request: StabilityRequest) -> StabilityResponse:
        """Execute image-to-image request."""
        start_time = time.time()
        
        try:
            async with self.request_semaphore:
                await self._check_rate_limits()
                
                engine = self._get_engine_id(request.model)
                url = f"{self.config.api_host}/{self.config.api_version}/generation/{engine}/image-to-image"
                
                # Prepare form data
                data = aiohttp.FormData()
                
                # Add text prompts
                data.add_field('text_prompts[0][text]', request.prompt)
                data.add_field('text_prompts[0][weight]', '1')
                
                if request.negative_prompt:
                    data.add_field('text_prompts[1][text]', request.negative_prompt)
                    data.add_field('text_prompts[1][weight]', '-1')
                
                # Add init image
                if request.init_image:
                    image_data = base64.b64decode(request.init_image)
                    data.add_field('init_image', io.BytesIO(image_data), 
                                 filename='init.png', content_type='image/png')
                
                # Add parameters
                data.add_field('image_strength', str(request.strength or 0.35))
                data.add_field('cfg_scale', str(request.cfg_scale))
                data.add_field('steps', str(request.steps))
                data.add_field('sampler', request.sampler)
                
                if request.seed:
                    data.add_field('seed', str(request.seed))
                
                # Execute request
                async with self.session.post(url, data=data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        images = []
                        for artifact in response_data.get('artifacts', []):
                            if artifact['finishReason'] == 'SUCCESS':
                                images.append(artifact['base64'])
                                
                        if self.config.save_generated_images and images:
                            await self._save_images(images, request.request_id)
                            
                        return StabilityResponse(
                            request_id=request.request_id,
                            model=request.model,
                            images=images,
                            seed=response_data.get('artifacts', [{}])[0].get('seed'),
                            latency_ms=(time.time() - start_time) * 1000,
                            cost_estimate=self.config.cost_per_generation
                        )
                        
                    else:
                        error_text = await response.text()
                        raise Exception(f"Image-to-image failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Image-to-image request failed: {e}")
            return StabilityResponse(
                request_id=request.request_id,
                model=request.model,
                error=str(e),
                error_code="img2img_error",
                latency_ms=(time.time() - start_time) * 1000
            )

    async def _execute_inpaint_request(self, request: StabilityRequest) -> StabilityResponse:
        """Execute inpainting request."""
        start_time = time.time()
        
        try:
            async with self.request_semaphore:
                await self._check_rate_limits()
                
                engine = self._get_engine_id(request.model)
                url = f"{self.config.api_host}/{self.config.api_version}/generation/{engine}/image-to-image/masking"
                
                # Prepare form data
                data = aiohttp.FormData()
                
                # Add text prompts
                data.add_field('text_prompts[0][text]', request.prompt)
                data.add_field('text_prompts[0][weight]', '1')
                
                if request.negative_prompt:
                    data.add_field('text_prompts[1][text]', request.negative_prompt)
                    data.add_field('text_prompts[1][weight]', '-1')
                
                # Add images
                if request.init_image:
                    image_data = base64.b64decode(request.init_image)
                    data.add_field('init_image', io.BytesIO(image_data), 
                                 filename='init.png', content_type='image/png')
                
                if request.mask_image:
                    mask_data = base64.b64decode(request.mask_image)
                    data.add_field('mask_image', io.BytesIO(mask_data), 
                                 filename='mask.png', content_type='image/png')
                
                # Add parameters
                data.add_field('cfg_scale', str(request.cfg_scale))
                data.add_field('steps', str(request.steps))
                data.add_field('sampler', request.sampler)
                
                if request.seed:
                    data.add_field('seed', str(request.seed))
                
                # Execute request
                async with self.session.post(url, data=data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        images = []
                        for artifact in response_data.get('artifacts', []):
                            if artifact['finishReason'] == 'SUCCESS':
                                images.append(artifact['base64'])
                                
                        if self.config.save_generated_images and images:
                            await self._save_images(images, request.request_id)
                            
                        return StabilityResponse(
                            request_id=request.request_id,
                            model=request.model,
                            images=images,
                            seed=response_data.get('artifacts', [{}])[0].get('seed'),
                            latency_ms=(time.time() - start_time) * 1000,
                            cost_estimate=self.config.cost_per_generation
                        )
                        
                    else:
                        error_text = await response.text()
                        raise Exception(f"Inpainting failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Inpainting request failed: {e}")
            return StabilityResponse(
                request_id=request.request_id,
                model=request.model,
                error=str(e),
                error_code="inpaint_error",
                latency_ms=(time.time() - start_time) * 1000
            )

    async def _execute_upscale_request(self, request: StabilityRequest) -> StabilityResponse:
        """Execute upscaling request."""
        start_time = time.time()
        
        try:
            async with self.request_semaphore:
                await self._check_rate_limits()
                
                upscale_model = request.parameters.get('upscale_model', 'esrgan-v1-x2plus')
                url = f"{self.config.api_host}/{self.config.api_version}/generation/{upscale_model}/image-to-image/upscale"
                
                # Prepare form data
                data = aiohttp.FormData()
                
                # Add image
                if request.init_image:
                    image_data = base64.b64decode(request.init_image)
                    data.add_field('image', io.BytesIO(image_data), 
                                 filename='image.png', content_type='image/png')
                
                # Execute request
                async with self.session.post(url, data=data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        images = []
                        for artifact in response_data.get('artifacts', []):
                            if artifact['finishReason'] == 'SUCCESS':
                                images.append(artifact['base64'])
                                
                        if self.config.save_generated_images and images:
                            await self._save_images(images, request.request_id)
                            
                        return StabilityResponse(
                            request_id=request.request_id,
                            model=request.model,
                            images=images,
                            latency_ms=(time.time() - start_time) * 1000,
                            cost_estimate=self.config.cost_per_generation * 0.5  # Upscaling typically costs less
                        )
                        
                    else:
                        error_text = await response.text()
                        raise Exception(f"Upscaling failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Upscaling request failed: {e}")
            return StabilityResponse(
                request_id=request.request_id,
                model=request.model,
                error=str(e),
                error_code="upscale_error",
                latency_ms=(time.time() - start_time) * 1000
            )

    async def _execute_video_request(self, request: StabilityRequest) -> StabilityResponse:
        """Execute video generation request."""
        start_time = time.time()
        
        try:
            async with self.request_semaphore:
                await self._check_rate_limits()
                
                # Note: This is a placeholder for video generation
                # Actual implementation would use the Stable Video Diffusion API
                url = f"{self.config.api_host}/{self.config.api_version}/generation/stable-video-diffusion-img2vid-v1-1/image-to-video"
                
                # Prepare form data
                data = aiohttp.FormData()
                
                # Add image
                if request.init_image:
                    image_data = base64.b64decode(request.init_image)
                    data.add_field('image', io.BytesIO(image_data), 
                                 filename='image.png', content_type='image/png')
                
                # Add video parameters
                data.add_field('motion_bucket_id', str(request.motion_bucket_id))
                data.add_field('noise_augmentation', str(request.noise_augmentation))
                data.add_field('fps', str(request.fps))
                
                # For now, return a simulated response
                return StabilityResponse(
                    request_id=request.request_id,
                    model=request.model,
                    videos=["simulated_video_base64"],
                    latency_ms=(time.time() - start_time) * 1000,
                    cost_estimate=self.config.cost_per_generation * 5  # Video generation typically costs more
                )
                
        except Exception as e:
            logger.error(f"Video generation request failed: {e}")
            return StabilityResponse(
                request_id=request.request_id,
                model=request.model,
                error=str(e),
                error_code="video_error",
                latency_ms=(time.time() - start_time) * 1000
            )

    def _get_engine_id(self, model: StabilityModel) -> str:
        """Get engine ID for Stability AI model."""
        return model.value

    def _parse_aspect_ratio(self, aspect_ratio: AspectRatio) -> tuple:
        """Parse aspect ratio string to width and height."""
        width_str, height_str = aspect_ratio.value.split('x')
        return int(width_str), int(height_str)

    async def _save_images(self, images: List[str], request_id: str) -> None:
        """Save generated images to disk."""
        try:
            for i, image_b64 in enumerate(images):
                # Decode image
                image_data = base64.b64decode(image_b64)
                
                # Save to file
                filename = f"{request_id}_{i}.png"
                filepath = f"{self.config.output_directory}/{filename}"
                
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(image_data)
                    
                logger.info(f"Saved generated image: {filepath}")
                
        except Exception as e:
            logger.error(f"Failed to save images: {e}")

    async def _check_rate_limits(self) -> None:
        """Check and enforce rate limits."""
        now = time.time()
        
        # Enforce minimum time between requests
        min_interval = 60.0 / self.config.requests_per_minute
        time_since_last = now - self.last_request_time
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
            
        self.last_request_time = time.time()

    async def _update_usage_tracking(
        self,
        request: StabilityRequest,
        response: StabilityResponse
    ) -> None:
        """Update usage tracking and cost estimation."""
        self.request_count += 1
        
        if response.images or response.videos:
            self.generation_count += len(response.images) + len(response.videos)
            
        if response.cost_estimate:
            self.cost_tracking += response.cost_estimate
            
        # Monitor performance
        if response.latency_ms:
            self.response_times.append(response.latency_ms)
            if len(self.response_times) > 100:
                self.response_times.pop(0)
                
        # Check budget alerts
        if (self.config.monthly_budget_usd and 
            self.cost_tracking > self.config.monthly_budget_usd * 0.8):
            logger.warning(f"Approaching monthly budget limit: ${self.cost_tracking:.2f}")

    async def get_user_balance(self) -> Dict[str, Any]:
        """Get user account balance."""
        try:
            url = f"{self.config.api_host}/{self.config.api_version}/user/balance"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to get balance: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Failed to get user balance: {e}")
            return {"error": str(e)}

    async def list_engines(self) -> List[Dict[str, Any]]:
        """List available engines."""
        try:
            url = f"{self.config.api_host}/{self.config.api_version}/engines/list"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('engines', [])
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to list engines: {e}")
            return []

    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "request_count": self.request_count,
            "generation_count": self.generation_count,
            "cost_tracking": self.cost_tracking,
            "error_count": self.error_count,
            "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            "last_reset": self.last_reset.isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        health = {
            "status": "healthy",
            "api_connection": "unknown",
            "usage": await self.get_usage_statistics(),
            "issues": []
        }
        
        try:
            # Test API connection
            balance = await self.get_user_balance()
            if 'error' not in balance:
                health["api_connection"] = "connected"
                health["credits"] = balance.get('credits', 0)
            else:
                health["api_connection"] = "failed"
                health["issues"].append("API connection failed")
                health["status"] = "degraded"
                
        except Exception as e:
            health["issues"].append(f"Health check error: {e}")
            health["status"] = "unhealthy"
            
        return health

    async def shutdown(self) -> None:
        """Shutdown Stability AI integration."""
        logger.info("Shutting down Stability AI integration...")
        
        if self.session:
            await self.session.close()
            
        logger.info("Stability AI integration shutdown completed")

    def __repr__(self) -> str:
        return f"StabilityAIIntegration(generations={self.generation_count}, cost=${self.cost_tracking:.2f})"


# Export main classes
__all__ = [
    "StabilityAIIntegration",
    "StabilityConfiguration",
    "StabilityRequest",
    "StabilityResponse",
    "StabilityModel",
    "ImageStyle",
    "AspectRatio"
]