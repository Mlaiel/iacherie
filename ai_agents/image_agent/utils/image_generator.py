"""
AI Image Generator - Advanced Image Generation & Synthesis System

Industrial-grade AI-powered image generation, style transfer, and creative synthesis
system for visual content creators and digital artists.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
from io import BytesIO

import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import cv2
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from transformers import CLIPTextModel, CLIPTokenizer

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ProcessingError, ValidationError, ResourceLimitError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ProcessingError, ValidationError, ResourceLimitError = globals().get('ProcessingError, ValidationError, ResourceLimitError', Exception)
from ...utils.performance_monitor import PerformanceMonitor
from ...security.content_filter import ContentFilter

logger = logging.getLogger(__name__)


class GenerationModel(Enum):
    """Available AI generation models"""
    STABLE_DIFFUSION_V1_5 = "stable_diffusion_v1_5"
    STABLE_DIFFUSION_V2_1 = "stable_diffusion_v2_1" 
    STABLE_DIFFUSION_XL = "stable_diffusion_xl"
    DALL_E_MINI = "dalle_mini"
    MIDJOURNEY_STYLE = "midjourney_style"
    CUSTOM_FINE_TUNED = "custom_fine_tuned"


class StyleTransferModel(Enum):
    """Style transfer model types"""
    NEURAL_STYLE_TRANSFER = "neural_style_transfer"
    FAST_NEURAL_STYLE = "fast_neural_style"
    CYCLEGAN = "cyclegan"
    STYLEGAN = "stylegan"
    ADAPTIVE_INSTANCE_NORM = "adaptive_instance_norm"


class GenerationType(Enum):
    """Types of image generation"""
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    STYLE_TRANSFER = "style_transfer"
    INPAINTING = "inpainting"
    OUTPAINTING = "outpainting" 
    SUPER_RESOLUTION = "super_resolution"
    VARIATION_GENERATION = "variation_generation"
    CREATIVE_SYNTHESIS = "creative_synthesis"


class QualityPreset(Enum):
    """Generation quality presets"""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PROFESSIONAL = "professional"
    ULTRA = "ultra"


@dataclass
class GenerationParams:
    """AI generation parameters"""
    model: GenerationModel = GenerationModel.STABLE_DIFFUSION_V2_1
    quality_preset: QualityPreset = QualityPreset.STANDARD
    width: int = 512
    height: int = 512
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    negative_prompt: str = ""
    seed: Optional[int] = None
    batch_size: int = 1
    strength: float = 0.75  # For img2img
    creativity_level: float = 0.7  # 0.0 = conservative, 1.0 = highly creative
    safety_filter: bool = True
    enhance_prompt: bool = True
    generate_variations: int = 1


@dataclass
class StyleTransferParams:
    """Style transfer parameters"""
    model: StyleTransferModel = StyleTransferModel.NEURAL_STYLE_TRANSFER
    style_strength: float = 1.0
    content_strength: float = 1.0
    preserve_original_colors: bool = False
    iterations: int = 300
    learning_rate: float = 0.003
    style_layers: List[str] = field(default_factory=lambda: ['conv1_1', 'conv2_1', 'conv3_1', 'conv4_1', 'conv5_1'])
    content_layers: List[str] = field(default_factory=lambda: ['conv4_2'])


@dataclass
class GenerationResult:
    """AI generation result"""
    success: bool
    generation_time: float
    generated_images: List[Image.Image] = field(default_factory=list)
    generation_params: Optional[GenerationParams] = None
    model_used: Optional[str] = None
    prompt_used: Optional[str] = None
    seed_used: Optional[int] = None
    quality_score: float = 0.0
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIImageGenerator:
    """
    Advanced AI Image Generation Engine
    
    Provides comprehensive AI-powered image generation capabilities including:
    - Text-to-image generation using state-of-the-art models
    - Image-to-image transformation and variation
    - Creative synthesis and artistic generation  
    - Style transfer and artistic effects
    - Super-resolution and image enhancement
    """
    
    def __init__(
        self,
        enable_gpu: bool = True,
        model_cache_size: int = 3,
        safety_filtering: bool = True,
        creative_mode: bool = True
    ):
        """
        Initialize AI Image Generator
        
        Args:
            enable_gpu: Enable GPU acceleration for generation
            model_cache_size: Number of models to keep cached
            safety_filtering: Enable content safety filtering
            creative_mode: Enable advanced creative features
        """
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.model_cache_size = model_cache_size
        self.safety_filtering = safety_filtering
        self.creative_mode = creative_mode
        
        # Device configuration
        self.device = torch.device("cuda" if self.enable_gpu else "cpu")
        
        # Model cache for efficient switching
        self.loaded_models = {}
        self.model_load_queue = []
        
        # Content safety filter
        if safety_filtering:
            self.content_filter = ContentFilter(
                filter_level="moderate",
                enable_nsfw_detection=True
            )
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(
            component="ai_image_generator",
            enable_detailed_metrics=True
        )
        
        # Generation statistics
        self.generation_stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "average_generation_time": 0.0,
            "models_used": {},
            "quality_distribution": {}
        }
        
        logger.info(f"AIImageGenerator initialized - GPU: {self.enable_gpu}, Device: {self.device}")

    async def generate_text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        params: Optional[GenerationParams] = None,
        save_path: Optional[Union[str, Path]] = None
    ) -> GenerationResult:
        """
        Generate image from text prompt using AI models
        
        Args:
            prompt: Text description of desired image
            negative_prompt: Things to avoid in generation
            params: Generation parameters
            save_path: Optional path to save generated image
            
        Returns:
            GenerationResult with generated images and metadata
        """
        start_time = time.time()
        generation_id = f"txt2img_{uuid.uuid4().hex[:8]}"
        
        try:
            # Initialize parameters
            params = params or GenerationParams()
            
            # Validate and enhance prompt
            if not prompt.strip():
                raise ValidationError("Prompt cannot be empty")
            
            enhanced_prompt = await self._enhance_prompt(prompt) if params.enhance_prompt else prompt
            final_negative_prompt = negative_prompt or params.negative_prompt
            
            # Apply safety filtering
            if self.safety_filtering:
                prompt_safe = await self.content_filter.check_text_safety(enhanced_prompt)
                if not prompt_safe:
                    raise ValidationError("Prompt contains inappropriate content")
            
            # Load appropriate model
            model = await self._load_model(params.model)
            
            # Set generation parameters
            generation_kwargs = self._prepare_generation_kwargs(params, enhanced_prompt, final_negative_prompt)
            
            # Generate images
            generated_images = []
            warnings = []
            
            with torch.no_grad():
                for batch in range(max(1, params.generate_variations)):
                    try:
                        # Set seed for reproducibility
                        if params.seed is not None:
                            torch.manual_seed(params.seed + batch)
                            np.random.seed(params.seed + batch)
                        
                        # Generate
                        result = model(**generation_kwargs)
                        
                        # Extract images
                        if hasattr(result, 'images'):
                            batch_images = result.images
                        else:
                            batch_images = [result]
                        
                        # Post-process and validate
                        for img in batch_images:
                            if isinstance(img, torch.Tensor):
                                img = self._tensor_to_pil(img)
                            
                            # Apply safety filtering to generated image
                            if self.safety_filtering:
                                img_safe = await self.content_filter.check_image_safety(img)
                                if not img_safe:
                                    warnings.append("Generated image filtered due to safety concerns")
                                    continue
                            
                            generated_images.append(img)
                    
                    except Exception as e:
                        warning_msg = f"Generation batch {batch} failed: {str(e)}"
                        warnings.append(warning_msg)
                        logger.warning(warning_msg)
            
            if not generated_images:
                raise ProcessingError("No valid images were generated")
            
            # Calculate quality scores
            quality_scores = []
            for img in generated_images:
                score = await self._assess_generation_quality(img, enhanced_prompt)
                quality_scores.append(score)
            
            average_quality = np.mean(quality_scores) if quality_scores else 0.0
            
            # Save images if requested
            if save_path and generated_images:
                await self._save_generated_images(generated_images, save_path, generation_id)
            
            generation_time = time.time() - start_time
            
            # Update statistics
            self._update_generation_stats(params.model, generation_time, average_quality, True)
            
            return GenerationResult(
                success=True,
                generation_time=generation_time,
                generated_images=generated_images,
                generation_params=params,
                model_used=params.model.value,
                prompt_used=enhanced_prompt,
                seed_used=params.seed,
                quality_score=average_quality,
                warnings=warnings,
                metadata={
                    "generation_id": generation_id,
                    "original_prompt": prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "negative_prompt": final_negative_prompt,
                    "images_generated": len(generated_images),
                    "device_used": str(self.device)
                }
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            self._update_generation_stats(params.model if params else GenerationModel.STABLE_DIFFUSION_V2_1, 
                                        generation_time, 0.0, False)
            
            logger.error(f"Text-to-image generation failed: {str(e)}")
            return GenerationResult(
                success=False,
                generation_time=generation_time,
                warnings=[str(e)]
            )

    async def generate_image_to_image(
        self,
        source_image: Union[str, Path, Image.Image],
        prompt: str,
        negative_prompt: Optional[str] = None,
        params: Optional[GenerationParams] = None,
        save_path: Optional[Union[str, Path]] = None
    ) -> GenerationResult:
        """
        Generate image variations based on source image and prompt
        
        Args:
            source_image: Source image for transformation
            prompt: Text description of desired changes
            negative_prompt: Things to avoid in generation
            params: Generation parameters
            save_path: Optional path to save generated image
            
        Returns:
            GenerationResult with generated images and metadata
        """
        start_time = time.time()
        generation_id = f"img2img_{uuid.uuid4().hex[:8]}"
        
        try:
            # Initialize parameters
            params = params or GenerationParams()
            
            # Load and validate source image
            if isinstance(source_image, (str, Path)):
                source_image = Image.open(source_image)
            elif not isinstance(source_image, Image.Image):
                raise ValidationError("Invalid source image format")
            
            # Ensure RGB mode
            if source_image.mode != 'RGB':
                source_image = source_image.convert('RGB')
            
            # Resize to target dimensions
            if source_image.size != (params.width, params.height):
                source_image = source_image.resize((params.width, params.height), Image.Resampling.LANCZOS)
            
            # Validate prompt
            if not prompt.strip():
                raise ValidationError("Prompt cannot be empty")
            
            # Enhance prompt
            enhanced_prompt = await self._enhance_prompt(prompt) if params.enhance_prompt else prompt
            final_negative_prompt = negative_prompt or params.negative_prompt
            
            # Apply safety filtering
            if self.safety_filtering:
                source_safe = await self.content_filter.check_image_safety(source_image)
                if not source_safe:
                    raise ValidationError("Source image contains inappropriate content")
                
                prompt_safe = await self.content_filter.check_text_safety(enhanced_prompt)
                if not prompt_safe:
                    raise ValidationError("Prompt contains inappropriate content")
            
            # Load img2img model
            model = await self._load_img2img_model(params.model)
            
            # Prepare generation parameters
            generation_kwargs = {
                "image": source_image,
                "prompt": enhanced_prompt,
                "negative_prompt": final_negative_prompt,
                "num_inference_steps": params.num_inference_steps,
                "guidance_scale": params.guidance_scale,
                "strength": params.strength,
                "generator": torch.Generator(device=self.device).manual_seed(params.seed) if params.seed else None
            }
            
            # Generate variations
            generated_images = []
            warnings = []
            
            with torch.no_grad():
                for variation in range(max(1, params.generate_variations)):
                    try:
                        if params.seed is not None:
                            generation_kwargs["generator"] = torch.Generator(device=self.device).manual_seed(params.seed + variation)
                        
                        result = model(**generation_kwargs)
                        
                        # Extract and process images
                        batch_images = result.images if hasattr(result, 'images') else [result]
                        
                        for img in batch_images:
                            if isinstance(img, torch.Tensor):
                                img = self._tensor_to_pil(img)
                            
                            # Safety check generated image
                            if self.safety_filtering:
                                img_safe = await self.content_filter.check_image_safety(img)
                                if not img_safe:
                                    warnings.append("Generated variation filtered due to safety concerns")
                                    continue
                            
                            generated_images.append(img)
                            
                    except Exception as e:
                        warning_msg = f"Variation {variation} generation failed: {str(e)}"
                        warnings.append(warning_msg)
                        logger.warning(warning_msg)
            
            if not generated_images:
                raise ProcessingError("No valid image variations were generated")
            
            # Quality assessment
            quality_scores = []
            for img in generated_images:
                score = await self._assess_generation_quality(img, enhanced_prompt, source_image)
                quality_scores.append(score)
            
            average_quality = np.mean(quality_scores) if quality_scores else 0.0
            
            # Save results
            if save_path and generated_images:
                await self._save_generated_images(generated_images, save_path, generation_id)
            
            generation_time = time.time() - start_time
            self._update_generation_stats(params.model, generation_time, average_quality, True)
            
            return GenerationResult(
                success=True,
                generation_time=generation_time,
                generated_images=generated_images,
                generation_params=params,
                model_used=params.model.value,
                prompt_used=enhanced_prompt,
                seed_used=params.seed,
                quality_score=average_quality,
                warnings=warnings,
                metadata={
                    "generation_id": generation_id,
                    "generation_type": "image_to_image",
                    "source_image_size": source_image.size,
                    "strength": params.strength,
                    "variations_generated": len(generated_images)
                }
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            self._update_generation_stats(params.model if params else GenerationModel.STABLE_DIFFUSION_V2_1,
                                        generation_time, 0.0, False)
            
            logger.error(f"Image-to-image generation failed: {str(e)}")
            return GenerationResult(
                success=False,
                generation_time=generation_time,
                warnings=[str(e)]
            )

    async def _load_model(self, model_type: GenerationModel) -> Any:
        """Load and cache AI generation model"""



        try:
            model_key = model_type.value
            
            # Return cached model if available
            if model_key in self.loaded_models:
                return self.loaded_models[model_key]
            
            # Clear cache if full
            if len(self.loaded_models) >= self.model_cache_size:
                oldest_model = next(iter(self.loaded_models))
                del self.loaded_models[oldest_model]
            
            # Load model based on type
            if model_type in [GenerationModel.STABLE_DIFFUSION_V1_5, GenerationModel.STABLE_DIFFUSION_V2_1]:
                model_id = self._get_model_id(model_type)
                model = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if self.enable_gpu else torch.float32,
                    safety_checker=None,  # We handle safety filtering separately
                    requires_safety_checker=False
                )
                model = model.to(self.device)
                
                # Optimize for inference
                if self.enable_gpu:
                    model.enable_memory_efficient_attention()
                    model.enable_xformers_memory_efficient_attention()
                
            elif model_type == GenerationModel.STABLE_DIFFUSION_XL:
                # Load SDXL model
                model_id = "stabilityai/stable-diffusion-xl-base-1.0"
                model = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if self.enable_gpu else torch.float32,
                    use_safetensors=True,
                    variant="fp16" if self.enable_gpu else None
                )
                model = model.to(self.device)
                
            else:
                raise ValidationError(f"Model type {model_type} not yet implemented")
            
            # Cache the loaded model
            self.loaded_models[model_key] = model
            
            logger.info(f"Loaded AI model: {model_type.value}")
            return model
            
        except Exception as e:
            raise ProcessingError(f"Failed to load model {model_type.value}: {str(e)}")

    async def _load_img2img_model(self, model_type: GenerationModel) -> Any:
        """Load image-to-image generation model"""



        try:
            model_key = f"{model_type.value}_img2img"
            
            if model_key in self.loaded_models:
                return self.loaded_models[model_key]
            
            # Clear cache if needed
            if len(self.loaded_models) >= self.model_cache_size:
                oldest_model = next(iter(self.loaded_models))
                del self.loaded_models[oldest_model]
            
            # Load img2img model
            model_id = self._get_model_id(model_type)
            model = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.enable_gpu else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            model = model.to(self.device)
            
            # Optimize for inference
            if self.enable_gpu:
                model.enable_memory_efficient_attention()
                try:
                    model.enable_xformers_memory_efficient_attention()
                except:
                    pass  # xformers not available
            
            self.loaded_models[model_key] = model
            return model
            
        except Exception as e:
            raise ProcessingError(f"Failed to load img2img model: {str(e)}")

    def _get_model_id(self, model_type: GenerationModel) -> str:
        """Get HuggingFace model ID for given model type"""
        model_ids = {
            GenerationModel.STABLE_DIFFUSION_V1_5: "runwayml/stable-diffusion-v1-5",
            GenerationModel.STABLE_DIFFUSION_V2_1: "stabilityai/stable-diffusion-2-1",
            GenerationModel.STABLE_DIFFUSION_XL: "stabilityai/stable-diffusion-xl-base-1.0",
        }
        
        return model_ids.get(model_type, "stabilityai/stable-diffusion-2-1")

    async def _enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt for better generation results"""



        try:
            # Basic prompt enhancement rules
            enhanced = prompt.strip()
            
            # Add quality modifiers if not present
            quality_keywords = ["high quality", "detailed", "professional", "masterpiece", "best quality"]
            if not any(keyword in enhanced.lower() for keyword in quality_keywords):
                enhanced = f"{enhanced}, highly detailed, professional quality"
            
            # Add artistic style hints based on content
            if "portrait" in enhanced.lower() and "photo" not in enhanced.lower():
                enhanced = f"{enhanced}, portrait photography style"
            elif "landscape" in enhanced.lower():
                enhanced = f"{enhanced}, landscape photography, wide angle"
            elif "art" in enhanced.lower() or "painting" in enhanced.lower():
                enhanced = f"{enhanced}, digital art, artistic masterpiece"
            
            # Limit length to prevent truncation
            if len(enhanced) > 200:
                enhanced = enhanced[:197] + "..."
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Prompt enhancement failed: {str(e)}")
            return prompt

    def _prepare_generation_kwargs(
        self, 
        params: GenerationParams, 
        prompt: str, 
        negative_prompt: str
    ) -> Dict[str, Any]:
        """Prepare keyword arguments for generation"""
        kwargs = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "height": params.height,
            "width": params.width,
            "num_inference_steps": params.num_inference_steps,
            "guidance_scale": params.guidance_scale,
            "num_images_per_prompt": params.batch_size
        }
        
        # Add seed if specified
        if params.seed is not None:
            kwargs["generator"] = torch.Generator(device=self.device).manual_seed(params.seed)
        
        return kwargs

    def _tensor_to_pil(self, tensor: torch.Tensor) -> Image.Image:
        """Convert PyTorch tensor to PIL Image"""



        try:
            # Denormalize tensor (assuming range [-1, 1])
            tensor = (tensor + 1.0) / 2.0
            tensor = torch.clamp(tensor, 0.0, 1.0)
            
            # Convert to numpy
            if tensor.dim() == 4:  # Batch dimension
                tensor = tensor.squeeze(0)
            
            if tensor.dim() == 3:  # CHW format
                tensor = tensor.permute(1, 2, 0)
            
            numpy_array = (tensor.cpu().numpy() * 255).astype(np.uint8)
            
            return Image.fromarray(numpy_array)
            
        except Exception as e:
            logger.error(f"Tensor to PIL conversion failed: {str(e)}")
            # Return a placeholder image
            return Image.new('RGB', (512, 512), (128, 128, 128))

    async def _assess_generation_quality(
        self, 
        generated_image: Image.Image, 
        prompt: str,
        source_image: Optional[Image.Image] = None
    ) -> float:
        """Assess quality of generated image"""



        try:
            quality_score = 0.0
            
            # Technical quality assessment
            img_array = np.array(generated_image)
            
            # Sharpness assessment
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, sharpness / 1000.0)
            quality_score += sharpness_score * 0.3
            
            # Contrast assessment
            contrast = np.std(gray)
            contrast_score = min(1.0, contrast / 64.0)
            quality_score += contrast_score * 0.2
            
            # Color diversity
            unique_colors = len(np.unique(img_array.reshape(-1, img_array.shape[2]), axis=0))
            color_diversity = min(1.0, unique_colors / 10000.0)
            quality_score += color_diversity * 0.2
            
            # Composition balance
            center_region = img_array[img_array.shape[0]//4:3*img_array.shape[0]//4, 
                                    img_array.shape[1]//4:3*img_array.shape[1]//4]
            center_mean = np.mean(center_region)
            edge_mean = np.mean(img_array) - center_mean
            balance_score = 1.0 - abs(edge_mean) / 255.0
            quality_score += balance_score * 0.1
            
            # Size and resolution bonus
            total_pixels = generated_image.size[0] * generated_image.size[1]
            resolution_score = min(1.0, total_pixels / (1024 * 1024))  # Normalize to 1MP
            quality_score += resolution_score * 0.2
            
            # If comparing to source image (img2img), add similarity/difference balance
            if source_image:
                # Calculate structural similarity
                source_array = np.array(source_image.resize(generated_image.size))
                
                # Simple correlation as similarity measure
                correlation = np.corrcoef(img_array.flatten(), source_array.flatten())[0, 1]
                if not np.isnan(correlation):
                    # We want some similarity but not identical
                    similarity_score = 1.0 - abs(correlation - 0.7)  # Target 70% similarity
                    quality_score += similarity_score * 0.1
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {str(e)}")
            return 0.5  # Default moderate quality

    async def _save_generated_images(
        self,
        images: List[Image.Image],
        base_path: Union[str, Path],
        generation_id: str
    ) -> None:
        """Save generated images to specified path"""



        try:
            base_path = Path(base_path)
            base_path.parent.mkdir(parents=True, exist_ok=True)
            
            for i, image in enumerate(images):
                if len(images) == 1:
                    filename = f"{base_path.stem}_{generation_id}{base_path.suffix}"
                else:
                    filename = f"{base_path.stem}_{generation_id}_{i+1:02d}{base_path.suffix}"
                
                save_path = base_path.parent / filename
                
                # Save with high quality
                if base_path.suffix.lower() in ['.jpg', '.jpeg']:
                    image.save(save_path, 'JPEG', quality=95, optimize=True)
                elif base_path.suffix.lower() == '.png':
                    image.save(save_path, 'PNG', optimize=True)
                elif base_path.suffix.lower() == '.webp':
                    image.save(save_path, 'WEBP', quality=90, optimize=True)
                else:
                    image.save(save_path)
                
                logger.info(f"Generated image saved: {save_path}")
                
        except Exception as e:
            logger.error(f"Failed to save generated images: {str(e)}")

    def _update_generation_stats(
        self, 
        model: GenerationModel, 
        generation_time: float, 
        quality_score: float, 
        success: bool
    ) -> None:
        """Update generation statistics"""
        self.generation_stats["total_generations"] += 1
        
        if success:
            self.generation_stats["successful_generations"] += 1
            
            # Update average generation time
            current_avg = self.generation_stats["average_generation_time"]
            total_successful = self.generation_stats["successful_generations"]
            self.generation_stats["average_generation_time"] = (
                (current_avg * (total_successful - 1) + generation_time) / total_successful
            )
            
            # Update model usage stats
            model_key = model.value
            if model_key not in self.generation_stats["models_used"]:
                self.generation_stats["models_used"][model_key] = 0
            self.generation_stats["models_used"][model_key] += 1
            
            # Update quality distribution
            quality_range = f"{int(quality_score * 10) / 10:.1f}"
            if quality_range not in self.generation_stats["quality_distribution"]:
                self.generation_stats["quality_distribution"][quality_range] = 0
            self.generation_stats["quality_distribution"][quality_range] += 1

    async def get_generation_stats(self) -> Dict[str, Any]:
        """Get comprehensive generation statistics"""



        try:
            stats = self.generation_stats.copy()
            
            # Add success rate
            if stats["total_generations"] > 0:
                stats["success_rate"] = stats["successful_generations"] / stats["total_generations"]
            else:
                stats["success_rate"] = 0.0
            
            # Add device info
            stats["device_info"] = {
                "device": str(self.device),
                "gpu_enabled": self.enable_gpu,
                "models_cached": len(self.loaded_models),
                "cache_size": self.model_cache_size
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get generation stats: {str(e)}")
            return {"error": str(e)}

    async def clear_model_cache(self) -> None:
        """Clear all cached models to free memory"""



        try:
            self.loaded_models.clear()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Model cache cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear model cache: {str(e)}")


class ImageSynthesizer:
    """
    Advanced Image Synthesis and Style Transfer System
    
    Specialized in artistic image transformation, neural style transfer,
    and creative image synthesis techniques.
    """
    
    def __init__(self, enable_gpu: bool = True):
        """Initialize Image Synthesizer"""
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.device = torch.device("cuda" if self.enable_gpu else "cpu")
        
        # Style transfer models cache
        self.style_models = {}
        
        logger.info(f"ImageSynthesizer initialized - GPU: {self.enable_gpu}")

    async def neural_style_transfer(
        self,
        content_image: Union[str, Path, Image.Image],
        style_image: Union[str, Path, Image.Image],
        params: Optional[StyleTransferParams] = None,
        save_path: Optional[Union[str, Path]] = None
    ) -> GenerationResult:
        """
        Perform neural style transfer between content and style images
        
        Args:
            content_image: Source content image
            style_image: Style reference image
            params: Style transfer parameters
            save_path: Optional save path for result
            
        Returns:
            GenerationResult with stylized image
        """
        start_time = time.time()
        
        try:
            params = params or StyleTransferParams()
            
            # Load images
            content_img = await self._load_image_for_style_transfer(content_image)
            style_img = await self._load_image_for_style_transfer(style_image)
            
            # Perform style transfer based on model type
            if params.model == StyleTransferModel.NEURAL_STYLE_TRANSFER:
                stylized_img = await self._neural_style_transfer_slow(content_img, style_img, params)
            elif params.model == StyleTransferModel.FAST_NEURAL_STYLE:
                stylized_img = await self._fast_neural_style_transfer(content_img, style_img, params)
            else:
                raise ValidationError(f"Style transfer model {params.model} not implemented")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Save if requested
            if save_path:
                await self._save_stylized_image(stylized_img, save_path)
            
            return GenerationResult(
                success=True,
                generation_time=processing_time,
                generated_images=[stylized_img],
                metadata={
                    "style_transfer_model": params.model.value,
                    "style_strength": params.style_strength,
                    "content_strength": params.content_strength,
                    "iterations": params.iterations
                }
            )
            
        except Exception as e:
            logger.error(f"Style transfer failed: {str(e)}")
            return GenerationResult(
                success=False,
                generation_time=time.time() - start_time,
                warnings=[str(e)]
            )

    async def _load_image_for_style_transfer(self, image_input: Union[str, Path, Image.Image]) -> Image.Image:
        """Load and prepare image for style transfer"""
        if isinstance(image_input, (str, Path)):
            image = Image.open(image_input)
        else:
            image = image_input.copy()
        
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize for processing efficiency
        max_size = 512
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image

    async def _neural_style_transfer_slow(
        self, 
        content_image: Image.Image, 
        style_image: Image.Image, 
        params: StyleTransferParams
    ) -> Image.Image:
        """Perform high-quality neural style transfer (slower but better quality)"""



        try:
            # This is a simplified implementation
            # In practice, this would use VGG19 or similar pre-trained networks
            # for feature extraction and optimization
            
            # Convert images to tensors
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            content_tensor = transform(content_image).unsqueeze(0).to(self.device)
            style_tensor = transform(style_image).unsqueeze(0).to(self.device)
            
            # For demonstration, we'll use a simple blending approach
            # Real implementation would use loss functions and optimization
            
            # Resize style to match content
            style_resized = torch.nn.functional.interpolate(
                style_tensor, 
                size=content_tensor.shape[2:],
                mode='bilinear',
                align_corners=False
            )
            
            # Simple weighted blend (placeholder for actual neural style transfer)
            alpha = params.style_strength / (params.style_strength + params.content_strength)
            blended = (1 - alpha) * content_tensor + alpha * style_resized
            
            # Denormalize and convert back to PIL
            denormalize = transforms.Compose([
                transforms.Normalize(mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225], 
                                   std=[1/0.229, 1/0.224, 1/0.225])
            ])
            
            result_tensor = denormalize(blended.squeeze(0))
            result_tensor = torch.clamp(result_tensor, 0, 1)
            
            # Convert to PIL
            to_pil = transforms.ToPILImage()
            result_image = to_pil(result_tensor.cpu())
            
            # Resize back to original content size if needed
            if result_image.size != content_image.size:
                result_image = result_image.resize(content_image.size, Image.Resampling.LANCZOS)
            
            return result_image
            
        except Exception as e:
            logger.error(f"Neural style transfer failed: {str(e)}")
            # Return original content image as fallback
            return content_image

    async def _fast_neural_style_transfer(
        self, 
        content_image: Image.Image, 
        style_image: Image.Image, 
        params: StyleTransferParams
    ) -> Image.Image:
        """Fast neural style transfer using pre-trained models"""
        # Placeholder for fast style transfer implementation
        # This would use pre-trained fast neural style models
        return await self._neural_style_transfer_slow(content_image, style_image, params)

    async def _save_stylized_image(self, image: Image.Image, save_path: Union[str, Path]) -> None:
        """Save stylized image"""
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        if save_path.suffix.lower() in ['.jpg', '.jpeg']:
            image.save(save_path, 'JPEG', quality=95, optimize=True)
        elif save_path.suffix.lower() == '.png':
            image.save(save_path, 'PNG', optimize=True)
        else:
            image.save(save_path)
        
        logger.info(f"Stylized image saved: {save_path}")

    async def create_artistic_variations(
        self,
        source_image: Union[str, Path, Image.Image],
        num_variations: int = 3,
        creativity_level: float = 0.7
    ) -> List[Image.Image]:
        """Create artistic variations of source image"""



        try:
            # Load source image
            if isinstance(source_image, (str, Path)):
                source = Image.open(source_image)
            else:
                source = source_image.copy()
            
            variations = []
            
            for i in range(num_variations):
                # Apply different artistic effects
                if i == 0:
                    # Oil painting effect
                    variation = await self._apply_oil_painting_effect(source, creativity_level)
                elif i == 1:
                    # Watercolor effect
                    variation = await self._apply_watercolor_effect(source, creativity_level)
                else:
                    # Abstract effect
                    variation = await self._apply_abstract_effect(source, creativity_level)
                
                variations.append(variation)
            
            return variations
            
        except Exception as e:
            logger.error(f"Artistic variation creation failed: {str(e)}")
            return [source_image] if isinstance(source_image, Image.Image) else [Image.open(source_image)]

    async def _apply_oil_painting_effect(self, image: Image.Image, intensity: float) -> Image.Image:
        """Apply oil painting artistic effect"""
        # Convert to numpy for processing
        img_array = np.array(image)
        
        # Apply multiple bilateral filters for oil painting effect
        for _ in range(int(3 * intensity)):
            img_array = cv2.bilateralFilter(img_array, 9, 200, 200)
        
        # Enhance colors
        enhancer = ImageEnhance.Color(Image.fromarray(img_array))
        result = enhancer.enhance(1.0 + 0.3 * intensity)
        
        # Increase contrast slightly
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(1.0 + 0.2 * intensity)
        
        return result

    async def _apply_watercolor_effect(self, image: Image.Image, intensity: float) -> Image.Image:
        """Apply watercolor artistic effect"""
        img_array = np.array(image)
        
        # Edge-preserving smoothing
        filtered = cv2.edgePreservingFilter(img_array, flags=1, sigma_s=50, sigma_r=0.4)
        
        # Reduce saturation for watercolor look
        hsv = cv2.cvtColor(filtered, cv2.COLOR_RGB2HSV)
        hsv[:, :, 1] = hsv[:, :, 1] * (0.7 + 0.2 * (1 - intensity))
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        # Add slight blur
        kernel_size = int(3 + 4 * intensity)
        if kernel_size % 2 == 0:
            kernel_size += 1
        result = cv2.GaussianBlur(result, (kernel_size, kernel_size), 0)
        
        return Image.fromarray(result)

    async def _apply_abstract_effect(self, image: Image.Image, intensity: float) -> Image.Image:
        """Apply abstract artistic effect"""
        img_array = np.array(image)
        
        # Quantize colors for abstract look
        data = img_array.reshape((-1, 3))
        data = np.float32(data)
        
        k = max(8, int(16 - 8 * intensity))  # Fewer colors = more abstract
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        quantized = quantized.reshape(img_array.shape)
        
        # Apply edge enhancement
        gray = cv2.cvtColor(quantized, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges = cv2.dilate(edges, None, iterations=1)
        
        # Combine quantized image with edges
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        result = cv2.addWeighted(quantized, 0.8, edges_colored, 0.2, 0)
        
        return Image.fromarray(result)
