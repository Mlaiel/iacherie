#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DALL-E Client for Advanced Image Generation

Professional DALL-E integration for high-quality image generation,
editing, and variation creation for content creators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import os
import base64
import io
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    import openai
    from PIL import Image
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

logger = logging.getLogger(__name__)


class DALLEClient:
    """
    Advanced DALL-E client for professional image generation
    with support for multiple models and image editing capabilities.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize DALL-E client with configuration."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.default_model = "dall-e-3"
        self.max_retries = 3
        
        # Supported image sizes by model
        self.model_sizes = {
            "dall-e-3": ["1024x1024", "1792x1024", "1024x1792"],
            "dall-e-2": ["256x256", "512x512", "1024x1024"]
        }
        
        # Quality settings
        self.quality_settings = {
            "standard": "standard",
            "hd": "hd"
        }
        
        # Style presets
        self.style_presets = {
            "photorealistic": "photorealistic, high quality, professional photography",
            "artistic": "artistic, creative, expressive, stylized",
            "digital_art": "digital art, modern, clean, vector-style",
            "painting": "oil painting, canvas, artistic brushstrokes",
            "sketch": "pencil sketch, hand-drawn, artistic lines",
            "cartoon": "cartoon style, animated, colorful, fun",
            "vintage": "vintage style, retro, aged, classic",
            "minimalist": "minimalist, clean, simple, modern",
            "fantasy": "fantasy, magical, mystical, otherworldly",
            "sci_fi": "science fiction, futuristic, technological"
        }
        
        if DEPENDENCIES_AVAILABLE and self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("DALL-E client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DALL-E client: {e}")
                self.client = None
        else:
            logger.warning("DALL-E dependencies not available or API key not provided")

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "natural",
        model: str = "dall-e-3",
        n_images: int = 1
    ) -> Dict[str, Any]:
        """
        Generate high-quality images with DALL-E.
        
        Args:
            prompt: Detailed description of the desired image
            size: Image dimensions (1024x1024, 1792x1024, 1024x1792)
            quality: Image quality (standard, hd)
            style: Generation style (natural, vivid)
            model: DALL-E model to use (dall-e-3, dall-e-2)
            n_images: Number of images to generate
            
        Returns:
            Dictionary with generated images and metadata
        """
        if not self.client:
            return {
                "success": False,
                "error": "DALL-E client not available",
                "images": [],
                "metadata": {}
            }

        try:
            # Validate size for the model
            if size not in self.model_sizes.get(model, []):
                size = "1024x1024"  # Default fallback
            
            # Enhance prompt for better results
            enhanced_prompt = self._enhance_image_prompt(prompt)
            
            logger.info(f"Generating {n_images} image(s) with DALL-E {model}")
            
            # Create image generation request
            request_params = {
                "model": model,
                "prompt": enhanced_prompt,
                "size": size,
                "n": min(n_images, 4),  # DALL-E-3 supports max 1, DALL-E-2 supports max 4
                "response_format": "url"
            }
            
            # Add quality and style for DALL-E-3
            if model == "dall-e-3":
                request_params["quality"] = quality
                request_params["style"] = style
                request_params["n"] = 1  # DALL-E-3 only supports 1 image at a time
            
            response = await asyncio.to_thread(
                self.client.images.generate,
                **request_params
            )
            
            images = []
            for image_data in response.data:
                images.append({
                    "url": image_data.url,
                    "revised_prompt": getattr(image_data, 'revised_prompt', enhanced_prompt)
                })
            
            return {
                "success": True,
                "images": images,
                "metadata": {
                    "model": model,
                    "size": size,
                    "quality": quality,
                    "style": style,
                    "original_prompt": prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "images_generated": len(images),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "images": [],
                "metadata": {}
            }

    async def generate_image_variations(
        self,
        image_path: str,
        n_variations: int = 3,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """
        Generate variations of an existing image.
        
        Args:
            image_path: Path to the source image
            n_variations: Number of variations to generate
            size: Size of generated variations
            
        Returns:
            Dictionary with image variations and metadata
        """
        if not self.client:
            return {
                "success": False,
                "error": "DALL-E client not available",
                "variations": [],
                "metadata": {}
            }

        try:
            # Validate and process the image
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": "Source image file not found",
                    "variations": [],
                    "metadata": {}
                }
            
            logger.info(f"Generating {n_variations} variations from {image_path}")
            
            with open(image_path, "rb") as image_file:
                response = await asyncio.to_thread(
                    self.client.images.create_variation,
                    image=image_file,
                    n=min(n_variations, 4),
                    size=size,
                    response_format="url"
                )
            
            variations = []
            for image_data in response.data:
                variations.append({
                    "url": image_data.url
                })
            
            return {
                "success": True,
                "variations": variations,
                "metadata": {
                    "source_image": image_path,
                    "size": size,
                    "variations_generated": len(variations),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Image variation generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "variations": [],
                "metadata": {}
            }

    async def edit_image(
        self,
        image_path: str,
        mask_path: str,
        prompt: str,
        size: str = "1024x1024",
        n_images: int = 1
    ) -> Dict[str, Any]:
        """
        Edit an image using DALL-E's inpainting capabilities.
        
        Args:
            image_path: Path to the source image
            mask_path: Path to the mask image (transparent areas will be edited)
            prompt: Description of the desired edits
            size: Size of the edited image
            n_images: Number of edited versions to generate
            
        Returns:
            Dictionary with edited images and metadata
        """
        if not self.client:
            return {
                "success": False,
                "error": "DALL-E client not available",
                "edited_images": [],
                "metadata": {}
            }

        try:
            # Validate files exist
            if not os.path.exists(image_path):
                return {"success": False, "error": "Source image not found", "edited_images": [], "metadata": {}}
            
            if not os.path.exists(mask_path):
                return {"success": False, "error": "Mask image not found", "edited_images": [], "metadata": {}}
            
            logger.info(f"Editing image {image_path} with mask {mask_path}")
            
            with open(image_path, "rb") as image_file, open(mask_path, "rb") as mask_file:
                response = await asyncio.to_thread(
                    self.client.images.edit,
                    image=image_file,
                    mask=mask_file,
                    prompt=prompt,
                    n=min(n_images, 4),
                    size=size,
                    response_format="url"
                )
            
            edited_images = []
            for image_data in response.data:
                edited_images.append({
                    "url": image_data.url
                })
            
            return {
                "success": True,
                "edited_images": edited_images,
                "metadata": {
                    "source_image": image_path,
                    "mask_image": mask_path,
                    "edit_prompt": prompt,
                    "size": size,
                    "images_generated": len(edited_images),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Image editing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "edited_images": [],
                "metadata": {}
            }

    async def generate_with_style_preset(
        self,
        prompt: str,
        style_preset: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate image using predefined style presets.
        
        Args:
            prompt: Base description of the desired image
            style_preset: Predefined style (photorealistic, artistic, digital_art, etc.)
            size: Image dimensions
            quality: Image quality
            
        Returns:
            Dictionary with generated image and metadata
        """
        if style_preset not in self.style_presets:
            return {
                "success": False,
                "error": f"Unknown style preset: {style_preset}",
                "images": [],
                "metadata": {}
            }
        
        # Combine prompt with style preset
        style_guidance = self.style_presets[style_preset]
        enhanced_prompt = f"{prompt}, {style_guidance}"
        
        return await self.generate_image(
            prompt=enhanced_prompt,
            size=size,
            quality=quality,
            model="dall-e-3"
        )

    def _enhance_image_prompt(self, prompt: str) -> str:
        """Enhance the prompt for better DALL-E results."""
        # Add quality modifiers if not present
        quality_terms = ["high quality", "professional", "detailed", "crisp", "clear"]
        has_quality = any(term in prompt.lower() for term in quality_terms)
        
        if not has_quality:
            prompt += ", high quality, professional, detailed"
        
        # Ensure prompt doesn't exceed DALL-E limits
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."
        
        return prompt

    async def download_image(self, image_url: str, save_path: str) -> Dict[str, Any]:
        """
        Download generated image from URL to local file.
        
        Args:
            image_url: URL of the generated image
            save_path: Local path to save the image
            
        Returns:
            Dictionary with download status and metadata
        """
        try:
            import requests
            
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # Get image info
            with Image.open(save_path) as img:
                width, height = img.size
                format_name = img.format
            
            return {
                "success": True,
                "saved_path": save_path,
                "metadata": {
                    "width": width,
                    "height": height,
                    "format": format_name,
                    "file_size": len(response.content),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Image download failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "saved_path": "",
                "metadata": {}
            }

    def is_available(self) -> bool:
        """Check if DALL-E client is available and configured."""
        return self.client is not None

    def get_supported_sizes(self, model: str = "dall-e-3") -> List[str]:
        """Get supported image sizes for the specified model."""
        return self.model_sizes.get(model, [])

    def get_style_presets(self) -> List[str]:
        """Get available style presets."""
        return list(self.style_presets.keys())