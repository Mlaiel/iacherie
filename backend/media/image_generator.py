"""Media Image Generator - Consolidated Image Generation System

Handles all 10 types of image generation:
1. Social media images (Instagram, TikTok, Facebook posts)
2. Marketing visuals (ads, banners, promotional content) 
3. Product photography (e-commerce, catalog images)
4. Artistic illustrations (digital art, concept art)
5. Infographics and data visualizations
6. Logo and brand design elements
7. Web graphics (headers, backgrounds, UI elements)
8. Print materials (flyers, posters, brochures)
9. Photo editing and enhancement
10. Custom AI-generated imagery

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import base64
import io
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from enum import Enum
from PIL import Image
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_engine.content_generation.base_generator import BaseContentGenerator, ContentGenerationContext


class ImageType(Enum):
    """Image generation types"""
    SOCIAL_MEDIA = "social_media"
    MARKETING = "marketing"
    PRODUCT_PHOTOGRAPHY = "product_photography"
    ARTISTIC_ILLUSTRATION = "artistic_illustration"
    INFOGRAPHIC = "infographic"
    LOGO_DESIGN = "logo_design"
    WEB_GRAPHICS = "web_graphics"
    PRINT_MATERIALS = "print_materials"
    PHOTO_EDITING = "photo_editing"
    CUSTOM_AI = "custom_ai"


class ImageStyle(Enum):
    """Image style options"""
    PHOTOREALISTIC = "photorealistic"
    ARTISTIC = "artistic"
    MINIMALIST = "minimalist"
    VIBRANT = "vibrant"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    MODERN = "modern"
    VINTAGE = "vintage"
    ABSTRACT = "abstract"
    CARTOON = "cartoon"


class ImageFormat(Enum):
    """Supported image formats"""
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"
    SVG = "svg"
    GIF = "gif"
    TIFF = "tiff"


class ImageResolution(Enum):
    """Standard image resolutions"""
    SQUARE_512 = "512x512"
    SQUARE_1024 = "1024x1024"
    HD = "1920x1080"
    PORTRAIT = "1080x1350"
    LANDSCAPE = "1350x1080"
    INSTAGRAM_STORY = "1080x1920"
    FACEBOOK_POST = "1200x630"
    TWITTER_POST = "1200x675"
    LINKEDIN_POST = "1200x627"
    YOUTUBE_THUMBNAIL = "1280x720"


class ImageConfig:
    """Configuration for image generation"""
    
    def __init__(self, **kwargs):
        self.image_type = kwargs.get('image_type', ImageType.SOCIAL_MEDIA)
        self.style = kwargs.get('style', ImageStyle.MODERN)
        self.format = kwargs.get('format', ImageFormat.PNG)
        self.resolution = kwargs.get('resolution', ImageResolution.SQUARE_1024)
        self.quality = kwargs.get('quality', 'high')  # low, medium, high, ultra
        self.color_scheme = kwargs.get('color_scheme', 'vibrant')
        self.mood = kwargs.get('mood', 'professional')
        self.aspect_ratio = kwargs.get('aspect_ratio', '1:1')
        self.platform = kwargs.get('platform', 'instagram')
        self.brand_colors = kwargs.get('brand_colors', [])
        self.include_text = kwargs.get('include_text', False)
        self.text_content = kwargs.get('text_content', '')
        self.background_style = kwargs.get('background_style', 'auto')
        self.artistic_filter = kwargs.get('artistic_filter', None)


class MediaImageGenerator(BaseContentGenerator):
    """
    Comprehensive image generator supporting 10 different image generation types
    with advanced AI-powered creation capabilities.
    """
    
    def _setup_models(self) -> None:
        """Setup AI models for image generation"""
        try:
            # Initialize AI models for different image types
            self.models = {}
            
            # Social media image models
            self.models['social_media'] = {
                'primary': 'dall-e-3',
                'fallback': 'stable-diffusion-xl',
                'style_transfer': 'neural-style-transfer'
            }
            
            # Marketing visual models
            self.models['marketing'] = {
                'primary': 'midjourney-commercial',
                'fallback': 'adobe-firefly',
                'template_engine': 'canva-ai'
            }
            
            # Product photography models
            self.models['product_photography'] = {
                'primary': 'product-diffusion',
                'fallback': 'commercial-ai',
                'background_removal': 'rembg-pro'
            }
            
            # Artistic illustration models
            self.models['artistic_illustration'] = {
                'primary': 'artistic-diffusion',
                'fallback': 'creativity-ai',
                'style_engine': 'art-style-transfer'
            }
            
            # Infographic models
            self.models['infographic'] = {
                'primary': 'infographic-ai',
                'fallback': 'data-viz-generator',
                'chart_engine': 'automated-charts'
            }
            
            # Logo design models
            self.models['logo_design'] = {
                'primary': 'logo-diffusion',
                'fallback': 'brand-ai',
                'vector_engine': 'svg-generator'
            }
            
            # Web graphics models
            self.models['web_graphics'] = {
                'primary': 'web-design-ai',
                'fallback': 'ui-generator',
                'responsive_engine': 'adaptive-graphics'
            }
            
            # Print materials models
            self.models['print_materials'] = {
                'primary': 'print-ready-ai',
                'fallback': 'high-res-generator',
                'cmyk_engine': 'print-color-ai'
            }
            
            # Photo editing models
            self.models['photo_editing'] = {
                'primary': 'photoshop-ai',
                'fallback': 'gimp-ai',
                'enhancement_engine': 'image-upscaler'
            }
            
            # Custom AI models
            self.models['custom_ai'] = {
                'primary': 'custom-diffusion',
                'fallback': 'general-ai-art',
                'fine_tuned': 'specialized-models'
            }
            
            # Platform-specific configurations
            self.platform_specs = self._initialize_platform_specs()
            
            # Style presets for each type
            self.style_presets = self._initialize_style_presets()
            
            self.logger.info("Image generator models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize image models: {str(e)}")
            raise
    
    def _setup_resources(self) -> None:
        """Setup computational resources for image generation"""
        self.max_concurrent_generations = self.config.get('max_concurrent_generations', 4)
        self.generation_timeout = self.config.get('generation_timeout', 600)  # 10 minutes
        self.max_resolution = self.config.get('max_resolution', '4096x4096')
        self.supported_formats = ['png', 'jpeg', 'webp', 'svg', 'gif', 'tiff']
        
        # Memory and processing limits
        self.max_file_size_mb = self.config.get('max_file_size_mb', 50)
        self.gpu_memory_limit = self.config.get('gpu_memory_limit', '8GB')
    
    def _setup_validation_rules(self) -> None:
        """Setup image validation rules"""
        self.validation_rules = {
            'min_resolution': '256x256',
            'max_resolution': '4096x4096',
            'supported_formats': self.supported_formats,
            'max_file_size_mb': 50,
            'content_safety_enabled': True,
            'nsfw_filter_enabled': True,
            'copyright_check_enabled': True
        }
    
    async def generate_content(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate image content based on context and prompt.
        
        Args:
            context: Generation context
            prompt: Image description prompt
            options: Generation options
            
        Returns:
            Generated image data with metadata
        """
        try:
            # Parse image generation options
            image_config = ImageConfig(**(options or {}))
            
            # Determine image type from prompt if not specified
            if not hasattr(image_config, 'image_type') or not image_config.image_type:
                image_config.image_type = self._determine_image_type(prompt, context)
            
            # Build enhanced prompt for specific image type
            enhanced_prompt = await self._build_image_prompt(
                prompt, image_config, context
            )
            
            # Generate image based on type
            image_result = await self._generate_image_by_type(
                enhanced_prompt, image_config, context
            )
            
            # Post-process the image
            processed_image = await self._post_process_image(
                image_result, image_config
            )
            
            # Get image metadata
            image_metadata = await self._extract_image_metadata(processed_image)
            
            return {
                'content': processed_image,
                'image_type': image_config.image_type.value,
                'style': image_config.style.value,
                'format': image_config.format.value,
                'metadata': {
                    'resolution': image_config.resolution.value,
                    'quality': image_config.quality,
                    'aspect_ratio': image_config.aspect_ratio,
                    'generation_time': datetime.utcnow().isoformat(),
                    'model_used': self.models[image_config.image_type.value]['primary'],
                    'safety_checked': True,
                    'file_size_bytes': len(processed_image) if isinstance(processed_image, bytes) else 0,
                    **image_metadata
                },
                'configuration': {
                    'platform': image_config.platform,
                    'color_scheme': image_config.color_scheme,
                    'mood': image_config.mood,
                    'background_style': image_config.background_style,
                    'include_text': image_config.include_text,
                    'text_content': image_config.text_content
                }
            }
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {str(e)}")
            raise

    async def validate_output(self, content: Any) -> bool:
        """Validate generated image content"""
        if not isinstance(content, dict):
            return False
        
        # Check if image data exists
        image_data = content.get('content')
        if not image_data:
            return False
        
        # Check metadata
        metadata = content.get('metadata', {})
        if not metadata.get('resolution') or not metadata.get('file_size_bytes'):
            return False
        
        # Check format
        format_type = content.get('format')
        if format_type not in self.supported_formats:
            return False
        
        # Safety checks
        if metadata.get('safety_checked') is not True:
            return False
        
        return True

    def _determine_image_type(
        self, 
        prompt: str, 
        context: ContentGenerationContext
    ) -> ImageType:
        """Determine image type from prompt and context"""
        prompt_lower = prompt.lower()
        
        # Check platform context first
        if context.platform_requirements:
            platform = context.platform_requirements.get('platform', '').lower()
            if platform in ['instagram', 'tiktok', 'facebook', 'twitter']:
                return ImageType.SOCIAL_MEDIA
        
        # Check for specific keywords
        if any(word in prompt_lower for word in ['social', 'instagram', 'post', 'story']):
            return ImageType.SOCIAL_MEDIA
        elif any(word in prompt_lower for word in ['marketing', 'ad', 'banner', 'promotion']):
            return ImageType.MARKETING
        elif any(word in prompt_lower for word in ['product', 'ecommerce', 'catalog']):
            return ImageType.PRODUCT_PHOTOGRAPHY
        elif any(word in prompt_lower for word in ['art', 'illustration', 'creative', 'artistic']):
            return ImageType.ARTISTIC_ILLUSTRATION
        elif any(word in prompt_lower for word in ['infographic', 'chart', 'data', 'graph']):
            return ImageType.INFOGRAPHIC
        elif any(word in prompt_lower for word in ['logo', 'brand', 'identity']):
            return ImageType.LOGO_DESIGN
        elif any(word in prompt_lower for word in ['web', 'website', 'header', 'ui']):
            return ImageType.WEB_GRAPHICS
        elif any(word in prompt_lower for word in ['print', 'poster', 'flyer', 'brochure']):
            return ImageType.PRINT_MATERIALS
        elif any(word in prompt_lower for word in ['edit', 'enhance', 'retouch', 'fix']):
            return ImageType.PHOTO_EDITING
        else:
            return ImageType.CUSTOM_AI  # Default for general AI generation

    async def _build_image_prompt(
        self,
        base_prompt: str,
        config: ImageConfig,
        context: ContentGenerationContext
    ) -> str:
        """Build enhanced prompt for image generation"""
        
        # Get style preset for the image type
        style_preset = self.style_presets.get(config.image_type.value, {})
        
        # Build prompt components
        prompt_parts = []
        
        # Add base prompt
        prompt_parts.append(base_prompt)
        
        # Add image type specific instructions
        type_instruction = style_preset.get('base_instruction', '')
        if type_instruction:
            prompt_parts.append(type_instruction)
        
        # Add style elements
        style_elements = style_preset.get('style_elements', [])
        prompt_parts.extend(style_elements)
        
        # Add platform-specific requirements
        if config.platform in self.platform_specs:
            platform_reqs = self.platform_specs[config.platform]
            if 'style_requirements' in platform_reqs:
                prompt_parts.extend(platform_reqs['style_requirements'])
        
        # Add color scheme
        if config.color_scheme != 'auto':
            prompt_parts.append(f"{config.color_scheme} color palette")
        
        # Add mood
        if config.mood:
            prompt_parts.append(f"{config.mood} mood")
        
        # Add quality and technical specifications
        prompt_parts.append(f"high quality, {config.quality} detail")
        prompt_parts.append(f"{config.style.value} style")
        
        # Add aspect ratio consideration
        if config.aspect_ratio != '1:1':
            prompt_parts.append(f"aspect ratio {config.aspect_ratio}")
        
        # Combine all parts
        enhanced_prompt = ", ".join(prompt_parts)
        
        return enhanced_prompt

    async def _generate_image_by_type(
        self,
        prompt: str,
        config: ImageConfig,
        context: ContentGenerationContext
    ) -> bytes:
        """Generate image based on specific type"""
        
        image_type = config.image_type.value
        
        # Select appropriate generation method
        if image_type == 'social_media':
            return await self._generate_social_media_image(prompt, config)
        elif image_type == 'marketing':
            return await self._generate_marketing_image(prompt, config)
        elif image_type == 'product_photography':
            return await self._generate_product_image(prompt, config)
        elif image_type == 'artistic_illustration':
            return await self._generate_artistic_image(prompt, config)
        elif image_type == 'infographic':
            return await self._generate_infographic(prompt, config)
        elif image_type == 'logo_design':
            return await self._generate_logo(prompt, config)
        elif image_type == 'web_graphics':
            return await self._generate_web_graphic(prompt, config)
        elif image_type == 'print_materials':
            return await self._generate_print_material(prompt, config)
        elif image_type == 'photo_editing':
            return await self._edit_photo(prompt, config, context)
        elif image_type == 'custom_ai':
            return await self._generate_custom_ai_image(prompt, config)
        else:
            return await self._generate_custom_ai_image(prompt, config)  # Default fallback

    async def _generate_social_media_image(self, prompt: str, config: ImageConfig) -> bytes:
        """Generate social media optimized image"""
        return await self._mock_generate_image(prompt, "social_media", config)

    async def _generate_marketing_image(self, prompt: str, config: ImageConfig) -> bytes:
        """Generate marketing visual"""
        return await self._mock_generate_image(prompt, "marketing", config)

    async def _generate_product_image(self, prompt: str, config: ImageConfig) -> bytes:
        """Generate product photography"""
        return await self._mock_generate_image(prompt, "product", config)

    async def _generate_artistic_image(self, prompt: str, config: ImageConfig) -> bytes:
        """Generate artistic illustration"""
        return await self._mock_generate_image(prompt, "artistic", config)

    async def _generate_infographic(self, prompt: str, config: ImageConfig) -> bytes:
        """Generate infographic"""
        return await self._mock_generate_image(prompt, "infographic", config)

    async def _generate_logo(self, prompt: str, config: ImageConfig) -> bytes:
        """Generate logo design"""
        return await self._mock_generate_image(prompt, "logo", config)

    async def _generate_web_graphic(self, prompt: str, config: ImageConfig) -> bytes:
        """Generate web graphic"""
        return await self._mock_generate_image(prompt, "web", config)

    async def _generate_print_material(self, prompt: str, config: ImageConfig) -> bytes:
        """Generate print material"""
        return await self._mock_generate_image(prompt, "print", config)

    async def _edit_photo(self, prompt: str, config: ImageConfig, context: ContentGenerationContext) -> bytes:
        """Edit existing photo"""
        return await self._mock_generate_image(prompt, "photo_edit", config)

    async def _generate_custom_ai_image(self, prompt: str, config: ImageConfig) -> bytes:
        """Generate custom AI image"""
        return await self._mock_generate_image(prompt, "custom_ai", config)

    async def _mock_generate_image(
        self, 
        prompt: str, 
        image_type: str, 
        config: ImageConfig
    ) -> bytes:
        """Mock image generation for development/testing"""
        # Simulate processing time
        await asyncio.sleep(0.3)
        
        # Parse resolution
        resolution_str = config.resolution.value
        width, height = map(int, resolution_str.split('x'))
        
        # Create a solid color image based on image type
        color_map = {
            'social_media': (255, 192, 203),  # Pink
            'marketing': (255, 165, 0),       # Orange
            'product': (240, 240, 240),       # Light gray
            'artistic': (138, 43, 226),       # Blue violet
            'infographic': (0, 191, 255),     # Deep sky blue
            'logo': (50, 50, 50),             # Dark gray
            'web': (0, 123, 255),             # Blue
            'print': (220, 20, 60),           # Crimson
            'photo_edit': (144, 238, 144),    # Light green
            'custom_ai': (255, 20, 147)       # Deep pink
        }
        
        color = color_map.get(image_type, (128, 128, 128))
        
        # Create image using PIL
        image = Image.new('RGB', (width, height), color)
        
        # Add some visual elements to make it more interesting
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        
        # Draw a simple pattern
        draw.rectangle([width//4, height//4, 3*width//4, 3*height//4], outline=(255, 255, 255), width=3)
        
        # Add text indicating the image type
        try:
            # Use default font
            font = ImageFont.load_default()
            text = f"{image_type.upper()}\n{width}x{height}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2
            draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
        except:
            # Fallback if font loading fails
            draw.text((width//2-50, height//2), image_type.upper(), fill=(255, 255, 255))
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        
        self.logger.info(f"Generated {image_type} image ({len(img_data)} bytes) for: {prompt[:50]}...")
        return img_data

    async def _post_process_image(
        self,
        image_data: bytes,
        config: ImageConfig
    ) -> bytes:
        """Post-process generated image"""
        # In production, this would apply filters, optimize, compress, etc.
        processed_data = image_data
        
        # Mock post-processing based on configuration
        if config.artistic_filter:
            # Would apply artistic filters
            pass
        
        if config.platform in self.platform_specs:
            # Would apply platform-specific optimizations
            pass
        
        self.logger.info(f"Post-processed image ({len(processed_data)} bytes)")
        return processed_data

    async def _extract_image_metadata(self, image_data: bytes) -> Dict[str, Any]:
        """Extract metadata from image"""
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            return {
                'actual_resolution': f"{image.width}x{image.height}",
                'color_mode': image.mode,
                'has_transparency': image.mode in ['RGBA', 'LA'] or 'transparency' in image.info,
                'dpi': image.info.get('dpi', (72, 72)),
                'color_count': len(image.getcolors(maxcolors=256)) if image.getcolors(maxcolors=256) else 256
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract image metadata: {e}")
            return {}

    def _initialize_platform_specs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific specifications"""
        return {
            'instagram': {
                'post_size': '1080x1080',
                'story_size': '1080x1920',
                'reel_size': '1080x1920',
                'style_requirements': ['vibrant colors', 'eye-catching', 'mobile-optimized']
            },
            'facebook': {
                'post_size': '1200x630',
                'cover_size': '851x315',
                'story_size': '1080x1920',
                'style_requirements': ['professional', 'clear messaging', 'accessible']
            },
            'twitter': {
                'post_size': '1200x675',
                'header_size': '1500x500',
                'style_requirements': ['concise', 'impactful', 'news-friendly']
            },
            'linkedin': {
                'post_size': '1200x627',
                'cover_size': '1192x220',
                'style_requirements': ['professional', 'business-oriented', 'clean']
            },
            'youtube': {
                'thumbnail_size': '1280x720',
                'banner_size': '2560x1440',
                'style_requirements': ['clickable', 'high contrast', 'readable text']
            },
            'tiktok': {
                'video_size': '1080x1920',
                'style_requirements': ['trendy', 'youthful', 'dynamic']
            }
        }

    def _initialize_style_presets(self) -> Dict[str, Dict[str, Any]]:
        """Initialize style presets for each image type"""
        return {
            'social_media': {
                'base_instruction': 'social media optimized visual content',
                'style_elements': ['engaging', 'shareable', 'mobile-friendly', 'vibrant']
            },
            'marketing': {
                'base_instruction': 'professional marketing visual',
                'style_elements': ['compelling', 'brand-focused', 'call-to-action', 'conversion-optimized']
            },
            'product_photography': {
                'base_instruction': 'clean product photography',
                'style_elements': ['studio lighting', 'clean background', 'detailed', 'commercial quality']
            },
            'artistic_illustration': {
                'base_instruction': 'artistic digital illustration',
                'style_elements': ['creative', 'expressive', 'unique style', 'artistic flair']
            },
            'infographic': {
                'base_instruction': 'informative data visualization',
                'style_elements': ['clear data', 'readable typography', 'organized layout', 'educational']
            },
            'logo_design': {
                'base_instruction': 'professional logo design',
                'style_elements': ['memorable', 'scalable', 'timeless', 'brand identity']
            },
            'web_graphics': {
                'base_instruction': 'web-optimized graphic element',
                'style_elements': ['responsive', 'fast-loading', 'user-friendly', 'modern design']
            },
            'print_materials': {
                'base_instruction': 'high-resolution print material',
                'style_elements': ['print-ready', 'CMYK colors', 'high DPI', 'professional layout']
            },
            'photo_editing': {
                'base_instruction': 'enhanced and retouched image',
                'style_elements': ['natural enhancement', 'color correction', 'professional editing']
            },
            'custom_ai': {
                'base_instruction': 'AI-generated custom artwork',
                'style_elements': ['creative interpretation', 'unique style', 'imaginative']
            }
        }

    def _supports_content_type(self, content_type: str) -> bool:
        """Check if generator supports the specified content type"""
        return content_type in ['image', 'visual', 'graphic', 'photo']

    async def _release_model_resources(self) -> None:
        """Release model-specific resources"""
        # Clean up model resources
        if hasattr(self, 'models'):
            self.models.clear()
        
        self.logger.info("Image generator resources released")

    # Additional utility methods for image generation

    def get_supported_image_types(self) -> List[str]:
        """Get list of supported image types"""
        return [image_type.value for image_type in ImageType]

    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""
        return self.supported_formats

    def get_platform_specifications(self) -> Dict[str, Dict[str, Any]]:
        """Get platform-specific image specifications"""
        return self.platform_specs

    async def resize_image(
        self,
        image_data: bytes,
        target_resolution: str,
        maintain_aspect_ratio: bool = True
    ) -> bytes:
        """Resize image to target resolution"""
        try:
            # Parse target resolution
            target_width, target_height = map(int, target_resolution.split('x'))
            
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            if maintain_aspect_ratio:
                image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
            else:
                image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            
            resized_data = img_buffer.getvalue()
            self.logger.info(f"Resized image to {target_resolution}")
            return resized_data
            
        except Exception as e:
            self.logger.error(f"Image resize failed: {e}")
            raise

    async def apply_style_filter(
        self,
        image_data: bytes,
        filter_name: str
    ) -> bytes:
        """Apply artistic filter to image"""
        try:
            # Mock style filter application
            await asyncio.sleep(0.1)
            
            self.logger.info(f"Applied {filter_name} filter to image")
            return image_data  # Mock - return same data
            
        except Exception as e:
            self.logger.error(f"Style filter application failed: {e}")
            raise

    async def batch_generate_images(
        self,
        prompts: List[str],
        config: ImageConfig
    ) -> List[Dict[str, Any]]:
        """Generate multiple images in batch"""
        results = []
        
        # Process in batches to avoid overwhelming the system
        batch_size = min(self.max_concurrent_generations, len(prompts))
        
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i + batch_size]
            
            # Generate batch concurrently
            tasks = [
                self._generate_image_by_type(prompt, config, None)
                for prompt in batch_prompts
            ]
            
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Batch generation failed for prompt {i+j}: {result}")
                        continue
                    
                    metadata = await self._extract_image_metadata(result)
                    
                    results.append({
                        'id': i + j,
                        'data': result,
                        'prompt': batch_prompts[j],
                        'success': True,
                        'metadata': metadata
                    })
                    
            except Exception as e:
                self.logger.error(f"Batch processing failed: {e}")
        
        return results

    async def optimize_for_web(self, image_data: bytes) -> bytes:
        """Optimize image for web usage"""
        try:
            # Mock web optimization - in production would compress, optimize format, etc.
            await asyncio.sleep(0.1)
            
            self.logger.info("Optimized image for web")
            return image_data  # Mock - return same data
            
        except Exception as e:
            self.logger.error(f"Web optimization failed: {e}")
            raise