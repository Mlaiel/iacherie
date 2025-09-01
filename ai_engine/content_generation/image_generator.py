"""Image Content Generator - Advanced AI image generation engine

Professional image content generator for influencers and content creators
supporting image synthesis, editing, and enhancement.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tempfile
import os
import io
import base64

from .base_generator import BaseContentGenerator, ContentGenerationContext


class ImageConfig:
    """
Configuration for image generation settings"""
    
    def __init__(self, **kwargs):
        self.width = kwargs.get('width', 1024)
        self.height = kwargs.get('height', 1024)
        self.format = kwargs.get('format', 'png')
        self.quality = kwargs.get('quality', 95)
        self.style = kwargs.get('style', 'photorealistic')
        self.model = kwargs.get('model', 'dalle-3')


class ImageFormat:
    """
Image format enumeration"""

    PNG = "png"
    JPG = "jpg"
    WEBP = "webp"
    GIF = "gif"
    SVG = "svg"


class ImageQuality:
    """Image quality enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class ImageStyle:
    """Image style enumeration"""

    PHOTOREALISTIC = "photorealistic"
    ARTISTIC = "artistic"
    CARTOON = "cartoon"
    ABSTRACT = "abstract"
    VINTAGE = "vintage"


class ImageGenerationOptions:
    """Configuration options for image generation"""
    
    def __init__(self, **kwargs):
        self.resolution = kwargs.get('resolution', '1024x1024')
        self.format = kwargs.get('format', 'png')
        self.quality = kwargs.get('quality', 'high')
        self.style = kwargs.get('style', 'photorealistic')
        self.mood = kwargs.get('mood', 'neutral')
        self.color_palette = kwargs.get('color_palette', 'vibrant')
        self.aspect_ratio = kwargs.get('aspect_ratio', '1:1')
        self.lighting = kwargs.get('lighting', 'natural')
        self.composition = kwargs.get('composition', 'centered')
        self.effects = kwargs.get('effects', [])
        self.model_name = kwargs.get('model_name', 'dalle-3')
        self.negative_prompt = kwargs.get('negative_prompt', '')
        self.steps = kwargs.get('steps', 50)
        self.guidance_scale = kwargs.get('guidance_scale', 7.5)
        self.seed = kwargs.get('seed', None)


class ImageContentGenerator(BaseContentGenerator):
    """
    Advanced image content generator that creates high-quality images
    for various purposes including:
    - Social media posts and stories
    - Product photography and showcases
    - Marketing materials and advertisements
    - Profile pictures and avatars
    - Logos and branding elements
    - Thumbnails and cover images
    - Artistic and creative content
    - Educational and informational graphics
    """
    
    def _setup_models(self) -> None:
        """
Setup AI models and dependencies"""
        try:
            # Initialize image generation models
            self._initialize_image_models()
            self._initialize_image_effects()
            self._initialize_image_processing()
            
            # Image specifications
            self.supported_resolutions = {
                'square': (1024, 1024),
                'portrait': (768, 1024),
                'landscape': (1024, 768),
                'instagram': (1080, 1080),
                'story': (1080, 1920),
                'cover': (1200, 630),
                'thumbnail': (1280, 720),
                '4k': (3840, 2160)
            }
            
            # Supported image formats
            self.supported_formats = {
                'photo', 'illustration', 'digital_art', 'logo', 
                'infographic', 'thumbnail', 'avatar', 'product'
            }
            
            # Quality presets
            self.quality_presets = {
                'draft': {'steps': 20, 'guidance': 5.0},
                'standard': {'steps': 50, 'guidance': 7.5},
                'high': {'steps': 100, 'guidance': 10.0},
                'ultra': {'steps': 150, 'guidance': 12.0}
            }
            
            self.logger.info("Image generator models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize image models: {str(e)}")
            raise
    
    def _initialize_image_models(self) -> None:
        """Initialize image generation models"""
        # In a real implementation, this would load models like:
        # - DALL-E 3 for high-quality image generation
        # - Stable Diffusion for open-source generation
        # - Midjourney API for artistic generation
        # - Adobe Firefly for commercial use
        self.image_models = {
            'dalle-3': {'type': 'text-to-image', 'quality': 'ultra', 'speed': 'medium'},
            'stable-diffusion': {'type': 'text-to-image', 'quality': 'high', 'speed': 'fast'},
            'midjourney': {'type': 'text-to-image', 'quality': 'artistic', 'speed': 'slow'},
            'firefly': {'type': 'text-to-image', 'quality': 'commercial', 'speed': 'medium'}
        }
        
        self.current_image_model = 'dalle-3'
    
    def _initialize_image_effects(self) -> None:
        """
Initialize image effects and filters"""
        self.available_effects = {
            'blur': {'intensity': [1, 10], 'type': 'filter'},
            'sharpen': {'intensity': [1, 5], 'type': 'filter'},
            'brightness': {'level': [-50, 50], 'type': 'adjustment'},
            'contrast': {'level': [-50, 50], 'type': 'adjustment'},
            'saturation': {'level': [-100, 100], 'type': 'adjustment'},
            'vintage': {'strength': [0.1, 1.0], 'type': 'artistic'},
            'sepia': {'strength': [0.1, 1.0], 'type': 'artistic'},
            'vignette': {'intensity': [0.1, 1.0], 'type': 'artistic'},
            'glow': {'radius': [5, 50], 'type': 'artistic'},
            'shadow': {'offset': [2, 20], 'type': 'depth'}
        }
    
    def _initialize_image_processing(self) -> None:
        """
Initialize image processing capabilities"""
        # Create temporary directory for image processing
        self.temp_dir = tempfile.mkdtemp(prefix='image_gen_')
        
        # Image processing settings
        self.max_image_size = (4096, 4096)
        self.default_dpi = 300
        
    def _setup_resources(self) -> None:
        """
Setup computational resources"""
        # Image generation resource settings
        self.max_concurrent_requests = self.config.get('max_concurrent_requests', 3)
        self.request_timeout = self.config.get('request_timeout', 180)  # 3 minutes
        
        # Memory management
        self.max_memory_usage = self.config.get('max_memory_mb', 4096)
        
        # GPU acceleration
        self.use_gpu = self.config.get('use_gpu', True)
    
    def _setup_validation_rules(self) -> None:
        """
Setup image validation rules"""
        self.validation_rules = {
            'min_resolution': (256, 256),
            'max_resolution': (4096, 4096),
            'supported_formats': ['png', 'jpg', 'jpeg', 'webp'],
            'max_file_size_mb': 50,
            'min_quality_score': 0.7
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
            context: Generation context with user and platform information
            prompt: Image generation prompt
            options: Additional generation options
            
        Returns:
            Generated image content with metadata
        """
        try:
            # Parse options
            gen_options = ImageGenerationOptions(**(options or {}))
            
            # Determine image type
            image_type = self._determine_image_type(context, prompt, gen_options)
            
            # Build enhanced prompt
            enhanced_prompt = await self._build_enhanced_prompt(
                prompt, context, gen_options, image_type
            )
            
            # Generate image based on type
            if image_type == 'photo':
                image, metadata = await self._generate_photo(
                    enhanced_prompt, context, gen_options
                )
            elif image_type == 'illustration':
                image, metadata = await self._generate_illustration(
                    enhanced_prompt, context, gen_options
                )
            elif image_type == 'logo':
                image, metadata = await self._generate_logo(
                    enhanced_prompt, context, gen_options
                )
            elif image_type == 'infographic':
                image, metadata = await self._generate_infographic(
                    enhanced_prompt, context, gen_options
                )
            else:
                image, metadata = await self._generate_general_image(
                    enhanced_prompt, context, gen_options
                )
            
            # Apply post-processing
            processed_image = await self._post_process_image(
                image, gen_options, image_type
            )
            
            # Save image file
            image_file_path = await self._save_image_file(
                processed_image, gen_options, context.user_id
            )
            
            # Analyze image properties
            image_analysis = await self._analyze_image(processed_image)
            
            # Convert image to base64 for API response
            image_base64 = await self._image_to_base64(processed_image, gen_options.format)
            
            return {
                'image_file': image_file_path,
                'image_data': image_base64,
                'format': gen_options.format,
                'resolution': gen_options.resolution,
                'metadata': {
                    **metadata,
                    'image_type': image_type,
                    'file_size_mb': os.path.getsize(image_file_path) / (1024 * 1024),
                    'analysis': image_analysis
                },
                'generation_info': {
                    'model_used': gen_options.model_name,
                    'processing_time': metadata.get('processing_time', 0),
                    'quality_preset': gen_options.quality,
                    'steps': gen_options.steps,
                    'guidance_scale': gen_options.guidance_scale
                }
            }
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {str(e)}")
            raise
    
    async def validate_output(self, content: Any) -> bool:
        """
        Validate generated image content.
        
        Args:
            content: Generated image content to validate
            
        Returns:
            True if content meets quality standards
        """
        if not isinstance(content, dict):
            return False
        
        # Check required fields
        required_fields = ['image_file', 'format', 'resolution']
        for field in required_fields:
            if field not in content:
                return False
        
        # Check file exists
        image_file = content.get('image_file')
        if not image_file or not os.path.exists(image_file):
            return False
        
        # Check file size
        file_size_mb = os.path.getsize(image_file) / (1024 * 1024)
        if file_size_mb > self.validation_rules['max_file_size_mb']:
            return False
        
        # Validate image properties
        try:
            with Image.open(image_file) as img:
                width, height = img.size
                
                # Check resolution constraints
                if (width, height) < self.validation_rules['min_resolution']:
                    return False
                
                if (width, height) > self.validation_rules['max_resolution']:
                    return False
                
                # Check if image has content (not completely black or white)
                if await self._is_valid_image_content(img):
                    return True
                
        except Exception as e:
            self.logger.error(f"Image validation failed: {str(e)}")
            return False
        
        return False
    
    def _determine_image_type(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: ImageGenerationOptions
    ) -> str:
        """Determine the type of image to generate"""
        prompt_lower = prompt.lower()
        
        # Check for explicit type in prompt
        if any(word in prompt_lower for word in ['photo', 'photograph', 'realistic']):
            return 'photo'
        elif any(word in prompt_lower for word in ['illustration', 'drawing', 'artwork']):
            return 'illustration'
        elif any(word in prompt_lower for word in ['logo', 'brand', 'icon']):
            return 'logo'
        elif any(word in prompt_lower for word in ['infographic', 'chart', 'diagram']):
            return 'infographic'
        elif any(word in prompt_lower for word in ['avatar', 'profile', 'character']):
            return 'avatar'
        elif any(word in prompt_lower for word in ['product', 'showcase', 'commercial']):
            return 'product'
        
        # Check platform requirements
        if context.platform_requirements:
            platform = context.platform_requirements.get('platform', '').lower()
            if 'instagram' in platform:
                return 'photo'
            elif 'linkedin' in platform:
                return 'professional'
            elif 'logo' in platform:
                return 'logo'
        
        # Check style preference
        if options.style in ['photorealistic', 'realistic']:
            return 'photo'
        elif options.style in ['artistic', 'creative', 'abstract']:
            return 'illustration'
        
        return 'photo'  # Default
    
    async def _build_enhanced_prompt(
        self,
        base_prompt: str,
        context: ContentGenerationContext,
        options: ImageGenerationOptions,
        image_type: str
    ) -> str:
        """
Build enhanced prompt with style and quality modifiers"""
        prompt_parts = [base_prompt]
        
        # Add style specifications
        style_modifiers = []
        if options.style:
            style_modifiers.append(f"in {options.style} style")
        
        if options.lighting and options.lighting != 'natural':
            style_modifiers.append(f"with {options.lighting} lighting")
        
        if options.mood and options.mood != 'neutral':
            style_modifiers.append(f"{options.mood} mood")
        
        if options.color_palette and options.color_palette != 'natural':
            style_modifiers.append(f"{options.color_palette} color palette")
        
        if style_modifiers:
            prompt_parts.append(", ".join(style_modifiers))
        
        # Add quality and technical specifications
        quality_specs = []
        if image_type == 'photo':
            quality_specs.extend([
                "high resolution",
                "professional photography",
                "sharp focus",
                "detailed"
            ])
        elif image_type == 'illustration':
            quality_specs.extend([
                "digital art",
                "detailed illustration",
                "vibrant colors"
            ])
        elif image_type == 'logo':
            quality_specs.extend([
                "clean design",
                "professional logo",
                "minimalist",
                "vector style"
            ])
        
        if quality_specs:
            prompt_parts.append(", ".join(quality_specs))
        
        # Add composition specifications
        if options.composition and options.composition != 'natural':
            prompt_parts.append(f"{options.composition} composition")
        
        # Build final prompt
        enhanced_prompt = ", ".join(prompt_parts)
        
        # Add negative prompt if specified
        if options.negative_prompt:
            enhanced_prompt += f" | Negative: {options.negative_prompt}"
        
        return enhanced_prompt
    
    async def _generate_photo(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: ImageGenerationOptions
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """Generate photorealistic image"""
        start_time = datetime.now()
        
        # Enhanced prompt for photorealism
        photo_prompt = f"{prompt}, photorealistic, high quality, professional photography, 8k resolution"
        
        # Generate image using AI model (mock implementation)
        image = await self._mock_image_generation(photo_prompt, options, 'photo')
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'prompt': photo_prompt,
            'style': 'photorealistic',
            'processing_time': processing_time,
            'model_used': options.model_name
        }
        
        return image, metadata
    
    async def _generate_illustration(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: ImageGenerationOptions
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """Generate illustration/artwork"""
        start_time = datetime.now()
        
        # Enhanced prompt for illustration
        illustration_prompt = f"{prompt}, digital illustration, artwork, detailed, vibrant colors"
        
        # Generate image
        image = await self._mock_image_generation(illustration_prompt, options, 'illustration')
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'prompt': illustration_prompt,
            'style': 'illustration',
            'processing_time': processing_time
        }
        
        return image, metadata
    
    async def _generate_logo(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: ImageGenerationOptions
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """Generate logo design"""
        start_time = datetime.now()
        
        # Create logo using simple graphics (mock implementation)
        image = await self._create_simple_logo(prompt, options)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'prompt': prompt,
            'style': 'logo',
            'processing_time': processing_time,
            'design_type': 'minimalist'
        }
        
        return image, metadata
    
    async def _generate_infographic(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: ImageGenerationOptions
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
Generate infographic"""
        start_time = datetime.now()
        
        # Create infographic layout
        image = await self._create_infographic_layout(prompt, options)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'prompt': prompt,
            'style': 'infographic',
            'processing_time': processing_time,
            'layout_type': 'structured'
        }
        
        return image, metadata
    
    async def _generate_general_image(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: ImageGenerationOptions
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
Generate general image"""
        start_time = datetime.now()
        
        # Generate using default settings
        image = await self._mock_image_generation(prompt, options, 'general')
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'prompt': prompt,
            'style': options.style,
            'processing_time': processing_time
        }
        
        return image, metadata
    
    async def _mock_image_generation(
        self,
        prompt: str,
        options: ImageGenerationOptions,
        image_type: str
    ) -> Image.Image:
        """
Mock image generation (replace with actual AI model)"""
        # Parse resolution
        width, height = self._parse_resolution(options.resolution)
        
        # Create base image
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Generate base colors based on mood and palette
        base_colors = self._get_color_palette(options.color_palette, options.mood)
        
        # Create gradient background
        self._create_gradient_background(draw, width, height, base_colors)
        
        # Add content based on image type
        if image_type == 'photo':
            self._add_photorealistic_elements(draw, width, height, prompt)
        elif image_type == 'illustration':
            self._add_artistic_elements(draw, width, height, prompt)
        else:
            self._add_general_elements(draw, width, height, prompt)
        
        # Add text if mentioned in prompt
        if any(word in prompt.lower() for word in ['text', 'title', 'caption']):
            self._add_text_to_image(draw, prompt, width, height)
        
        return image
    
    async def _create_simple_logo(self, prompt: str, options: ImageGenerationOptions) -> Image.Image:
        """
Create a simple logo design"""
        width, height = self._parse_resolution(options.resolution)
        
        # Create image with transparent background for logo
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # Extract text from prompt
        logo_text = self._extract_logo_text(prompt)
        
        # Create simple logo design
        center_x, center_y = width // 2, height // 2
        
        # Add geometric shape
        shape_size = min(width, height) // 4
        shape_color = (50, 100, 200, 255)  # Blue color
        
        # Draw circle or square based on style
        if 'modern' in prompt.lower() or 'circle' in prompt.lower():
            # Modern circular logo
            draw.ellipse(
                [center_x - shape_size, center_y - shape_size, 
                 center_x + shape_size, center_y + shape_size],
                fill=shape_color
            )
        else:
            # Square/rectangular logo
            draw.rectangle(
                [center_x - shape_size, center_y - shape_size,
                 center_x + shape_size, center_y + shape_size],
                fill=shape_color
            )
        
        # Add text
        if logo_text:
            try:
                # Try to use a nice font
                font_size = shape_size // 2
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            text_bbox = draw.textbbox((0, 0), logo_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = center_x - text_width // 2
            text_y = center_y + shape_size + 20
            
            draw.text((text_x, text_y), logo_text, fill=(50, 50, 50, 255), font=font)
        
        return image
    
    async def _create_infographic_layout(self, prompt: str, options: ImageGenerationOptions) -> Image.Image:
        """Create an infographic layout"""
        width, height = self._parse_resolution(options.resolution)
        
        image = Image.new('RGB', (width, height), (240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        # Parse infographic content
        sections = self._parse_infographic_content(prompt)
        
        # Create layout sections
        section_height = height // len(sections)
        
        colors = [(50, 100, 200), (200, 100, 50), (50, 200, 100), (200, 50, 100)]
        
        for i, section in enumerate(sections):
            y_start = i * section_height
            y_end = (i + 1) * section_height
            
            # Section background
            color = colors[i % len(colors)]
            draw.rectangle([0, y_start, width, y_end], fill=color + (100,))
            
            # Section content
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            text_x = 50
            text_y = y_start + section_height // 2
            
            draw.text((text_x, text_y), section[:50], fill=(255, 255, 255), font=font)
        
        return image
    
    def _parse_resolution(self, resolution_str: str) -> Tuple[int, int]:
        """Parse resolution string to width, height tuple"""
        if 'x' in resolution_str:
            width, height = map(int, resolution_str.split('x'))
            return width, height
        elif resolution_str in self.supported_resolutions:
            return self.supported_resolutions[resolution_str]
        else:
            return 1024, 1024  # Default
    
    def _get_color_palette(self, palette_name: str, mood: str) -> List[Tuple[int, int, int]]:
        """
Get color palette based on name and mood"""
        palettes = {
            'vibrant': [(255, 100, 100), (100, 255, 100), (100, 100, 255)],
            'pastel': [(255, 200, 200), (200, 255, 200), (200, 200, 255)],
            'monochrome': [(100, 100, 100), (150, 150, 150), (200, 200, 200)],
            'warm': [(255, 150, 100), (255, 200, 150), (200, 100, 50)],
            'cool': [(100, 150, 255), (150, 200, 255), (50, 100, 200)]
        }
        
        base_palette = palettes.get(palette_name, palettes['vibrant'])
        
        # Adjust based on mood
        if mood == 'dark':
            return [(r//2, g//2, b//2) for r, g, b in base_palette]
        elif mood == 'bright':
            return [(min(255, r+50), min(255, g+50), min(255, b+50)) for r, g, b in base_palette]
        
        return base_palette
    
    def _create_gradient_background(self, draw: ImageDraw.Draw, width: int, height: int, colors: List[Tuple[int, int, int]]) -> None:
        """
Create gradient background"""
        if len(colors) < 2:
            colors = [(100, 100, 100), (200, 200, 200)]
        
        start_color = colors[0]
        end_color = colors[1]
        
        for y in range(height):
            t = y / height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    def _add_photorealistic_elements(self, draw: ImageDraw.Draw, width: int, height: int, prompt: str) -> None:
        """
Add photorealistic elements to image"""
        # Add some geometric shapes to simulate photorealistic content
        center_x, center_y = width // 2, height // 2
        
        # Add main subject (simplified)
        if 'portrait' in prompt.lower():
            # Simulate portrait with ellipse
            draw.ellipse([center_x-100, center_y-150, center_x+100, center_y+150], 
                        fill=(220, 180, 140), outline=(100, 100, 100))
        elif 'landscape' in prompt.lower():
            # Simulate landscape elements
            draw.rectangle([0, height//2, width, height], fill=(100, 150, 100))  # Ground
            draw.ellipse([width//4, height//4, 3*width//4, height//2], fill=(200, 200, 100))  # Sun/sky
    
    def _add_artistic_elements(self, draw: ImageDraw.Draw, width: int, height: int, prompt: str) -> None:
        """
Add artistic elements to image"""
        # Add abstract artistic elements
        import random
        
        for _ in range(10):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(20, 100)
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            
            if random.choice([True, False]):
                draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=color)
            else:
                draw.rectangle([x-size//2, y-size//2, x+size//2, y+size//2], fill=color)
    
    def _add_general_elements(self, draw: ImageDraw.Draw, width: int, height: int, prompt: str) -> None:
        """
Add general elements to image"""
        # Add some basic geometric elements
        center_x, center_y = width // 2, height // 2
        
        # Add central focus element
        draw.ellipse([center_x-50, center_y-50, center_x+50, center_y+50], 
                    fill=(255, 255, 255), outline=(100, 100, 100))
    
    def _add_text_to_image(self, draw: ImageDraw.Draw, prompt: str, width: int, height: int) -> None:
        """
Add text to image based on prompt"""
        text = self._extract_text_from_prompt(prompt)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Center the text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = height - text_height - 50  # Bottom of image
        
        # Add text with shadow
        draw.text((x+2, y+2), text, fill=(0, 0, 0), font=font)  # Shadow
        draw.text((x, y), text, fill=(255, 255, 255), font=font)  # Main text
    
    def _extract_logo_text(self, prompt: str) -> str:
        """Extract logo text from prompt"""
        # Look for quoted text
        if '"' in prompt:
            parts = prompt.split('"')
            if len(parts) >= 3:
                return parts[1].upper()
        
        # Extract company/brand name
        words = prompt.split()
        for i, word in enumerate(words):
            if word.lower() in ['logo', 'brand'] and i + 1 < len(words):
                return words[i + 1].upper()
        
        return "LOGO"
    
    def _extract_text_from_prompt(self, prompt: str) -> str:
        """Extract text content from prompt"""
        # Look for quoted text
        if '"' in prompt:
            parts = prompt.split('"')
            if len(parts) >= 3:
                return parts[1]
        
        # Extract key words
        words = prompt.split()
        important_words = [word for word in words if len(word) > 3]
        return ' '.join(important_words[:3])  # First 3 important words
    
    def _parse_infographic_content(self, prompt: str) -> List[str]:
        """Parse infographic content from prompt"""
        # Split by common delimiters
        sections = []
        
        if '1.' in prompt or '2.' in prompt:
            # Numbered list
            parts = prompt.split('.')
            sections = [part.strip() for part in parts if part.strip() and not part.strip().isdigit()]
        elif ',' in prompt:
            # Comma-separated
            sections = [part.strip() for part in prompt.split(',')]
        else:
            # Split by sentences
            sections = [part.strip() for part in prompt.split('.') if part.strip()]
        
        return sections[:4] if sections else ["Section 1", "Section 2", "Section 3"]
    
    async def _post_process_image(
        self,
        image: Image.Image,
        options: ImageGenerationOptions,
        image_type: str
    ) -> Image.Image:
        """Apply post-processing effects to image"""
        processed_image = image.copy()
        
        # Apply requested effects
        for effect in options.effects:
            if effect in self.available_effects:
                processed_image = await self._apply_image_effect(processed_image, effect)
        
        # Apply quality-based enhancements
        if options.quality == 'high':
            processed_image = self._enhance_image_quality(processed_image)
        
        return processed_image
    
    async def _apply_image_effect(self, image: Image.Image, effect_name: str) -> Image.Image:
        """
Apply specific image effect"""
        if effect_name == 'blur':
            return image.filter(ImageFilter.GaussianBlur(radius=2))
        elif effect_name == 'sharpen':
            return image.filter(ImageFilter.SHARPEN)
        elif effect_name == 'brightness':
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(1.2)
        elif effect_name == 'contrast':
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(1.1)
        elif effect_name == 'saturation':
            enhancer = ImageEnhance.Color(image)
            return enhancer.enhance(1.2)
        elif effect_name == 'vintage':
            return self._apply_vintage_effect(image)
        elif effect_name == 'sepia':
            return self._apply_sepia_effect(image)
        else:
            return image
    
    def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """
Enhance image quality"""
        # Apply sharpening
        enhanced = image.filter(ImageFilter.SHARPEN)
        
        # Slight contrast enhancement
        enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = enhancer.enhance(1.05)
        
        return enhanced
    
    def _apply_vintage_effect(self, image: Image.Image) -> Image.Image:
        """
Apply vintage effect"""
        # Convert to sepia tones and add vignette
        sepia_image = self._apply_sepia_effect(image)
        
        # Add slight blur for vintage feel
        vintage_image = sepia_image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return vintage_image
    
    def _apply_sepia_effect(self, image: Image.Image) -> Image.Image:
        """
Apply sepia effect"""
        # Convert to grayscale then tint
        grayscale = image.convert('L')
        sepia = Image.new('RGB', image.size)
        
        pixels = grayscale.load()
        sepia_pixels = sepia.load()
        
        for x in range(image.width):
            for y in range(image.height):
                gray = pixels[x, y]
                # Sepia formula
                r = min(255, int(gray * 1.2))
                g = min(255, int(gray * 1.0))
                b = min(255, int(gray * 0.8))
                sepia_pixels[x, y] = (r, g, b)
        
        return sepia
    
    async def _save_image_file(
        self,
        image: Image.Image,
        options: ImageGenerationOptions,
        user_id: str
    ) -> str:
        """
Save image to file and return path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{user_id}_{timestamp}.{options.format}"
        filepath = os.path.join(self.temp_dir, filename)
        
        # Save with appropriate quality
        save_kwargs = {}
        if options.format.lower() in ['jpg', 'jpeg']:
            save_kwargs['quality'] = 95
            save_kwargs['optimize'] = True
        elif options.format.lower() == 'png':
            save_kwargs['optimize'] = True
        
        image.save(filepath, format=options.format.upper(), **save_kwargs)
        
        return filepath
    
    async def _image_to_base64(self, image: Image.Image, format: str) -> str:
        """Convert image to base64 string"""
        buffer = io.BytesIO()
        image.save(buffer, format=format.upper())
        image_bytes = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(image_bytes).decode('utf-8')
    
    async def _analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """
Analyze image properties"""
        width, height = image.size
        
        # Convert to array for analysis
        img_array = np.array(image)
        
        # Basic statistics
        mean_brightness = np.mean(img_array)
        contrast = np.std(img_array)
        
        # Color analysis
        if len(img_array.shape) == 3:
            r_mean = np.mean(img_array[:, :, 0])
            g_mean = np.mean(img_array[:, :, 1])
            b_mean = np.mean(img_array[:, :, 2])
            color_balance = {'r': float(r_mean), 'g': float(g_mean), 'b': float(b_mean)}
        else:
            color_balance = {'grayscale': float(mean_brightness)}
        
        return {
            'dimensions': {'width': width, 'height': height},
            'aspect_ratio': width / height,
            'mean_brightness': float(mean_brightness),
            'contrast': float(contrast),
            'color_balance': color_balance,
            'file_format': image.format or 'Unknown'
        }
    
    async def _is_valid_image_content(self, image: Image.Image) -> bool:
        """
Check if image has valid content"""
        # Convert to array
        img_array = np.array(image)
        
        # Check if image is not completely black or white
        mean_value = np.mean(img_array)
        std_value = np.std(img_array)
        
        # Image should have some variation (not solid color)
        if std_value < 5:  # Very low variation
            return False
        
        # Check if image is not extremely dark or bright
        if mean_value < 10 or mean_value > 245:
            return False
        
        return True
    
    def _supports_content_type(self, content_type: str) -> bool:
        """
Check if generator supports the specified content type"""
        return content_type == 'image'
    
    async def generate_brand_assets(self, brand_info: Dict[str, Any], asset_types: List[str] = None, format: str = "png") -> Dict[str, Any]:
        """Generate brand assets like logos, icons, and brand imagery"""
        brand_name = brand_info.get('company_name', brand_info.get('brand_name', 'Brand'))
        brand_colors = brand_info.get('colors', ['#000000', '#FFFFFF'])
        style = brand_info.get('style_preference', brand_info.get('style', 'modern'))
        
        if asset_types is None:
            asset_types = ['logo', 'icon']
        
        # Mock implementation - in real system would generate actual brand assets
        assets = {
            'logo_variations': [
                {
                    'type': 'primary_logo',
                    'size': '512x512',
                    'format': 'png',
                    'url': f"/generated/logo_{brand_name.lower()}_primary.png",
                    'description': f"Primary logo for {brand_name}"
                },
                {
                    'type': 'icon',
                    'size': '256x256', 
                    'format': 'png',
                    'url': f"/generated/icon_{brand_name.lower()}.png",
                    'description': f"Icon version for {brand_name}"
                },
                {
                    'type': 'horizontal_logo',
                    'size': '800x200',
                    'format': 'png', 
                    'url': f"/generated/logo_{brand_name.lower()}_horizontal.png",
                    'description': f"Horizontal logo for {brand_name}"
                }
            ],
            'brand_colors': brand_colors,
            'style_guide': {
                'primary_font': 'Roboto',
                'secondary_font': 'Arial',
                'logo_usage': 'Maintain minimum clear space of 1x logo height',
                'color_variations': brand_colors
            },
            'generation_metadata': {
                'brand_name': brand_name,
                'style': style,
                'generated_at': datetime.now().isoformat(),
                'assets_count': 3
            }
        }
        
        return assets
    
    async def generate_social_media_templates(self, platform: str, content_type: str) -> Dict[str, Any]:
        """Generate social media image templates"""
        platform_sizes = {
            'instagram': {'post': '1080x1080', 'story': '1080x1920'},
            'twitter': {'post': '1200x675', 'header': '1500x500'},
            'linkedin': {'post': '1200x627', 'banner': '1584x396'},
            'facebook': {'post': '1200x630', 'cover': '820x312'}
        }
        
        size = platform_sizes.get(platform, {}).get(content_type, '1080x1080')
        
        return {
            'template_id': f"{platform}_{content_type}_{int(datetime.now().timestamp())}",
            'platform': platform,
            'content_type': content_type,
            'dimensions': size,
            'template_url': f"/templates/{platform}_{content_type}_template.png",
            'customization_options': {
                'text_areas': 2,
                'image_slots': 1,
                'color_schemes': 5,
                'font_options': 10
            }
        }
    
    def get_style_presets(self) -> List[str]:
        """Get available image style presets"""
        return [
            "photorealistic", "artistic", "cartoon", "sketch",
            "oil_painting", "watercolor", "digital_art", "vintage",
            "modern", "minimalist", "abstract", "surreal",
            "cyberpunk", "fantasy", "sci_fi", "nature"
        ]
    
    def get_color_palettes(self) -> List[Dict[str, Any]]:
        """Get available color palettes"""
        return [
            {
                "name": "vibrant",
                "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
                "description": "Bright and energetic colors"
            },
            {
                "name": "pastel",
                "colors": ["#FFB3BA", "#BFBFBF", "#BFFFBF", "#B3B3FF"],
                "description": "Soft and gentle tones"
            },
            {
                "name": "monochrome",
                "colors": ["#000000", "#404040", "#808080", "#FFFFFF"],
                "description": "Classic black and white"
            },
            {
                "name": "earth",
                "colors": ["#8B4513", "#DEB887", "#D2691E", "#F4A460"],
                "description": "Natural earth tones"
            }
        ]
    
    async def apply_filter(self, image_path: str, filter_name: str) -> str:
        """Apply filter to an image"""
        try:
            # Load image
            with Image.open(image_path) as img:
                # Apply different filters based on name
                if filter_name == "blur":
                    filtered_img = img.filter(ImageFilter.BLUR)
                elif filter_name == "sharpen":
                    filtered_img = img.filter(ImageFilter.SHARPEN)
                elif filter_name == "emboss":
                    filtered_img = img.filter(ImageFilter.EMBOSS)
                elif filter_name == "edge_enhance":
                    filtered_img = img.filter(ImageFilter.EDGE_ENHANCE)
                elif filter_name == "sepia":
                    # Convert to sepia
                    grayscale = img.convert('L')
                    filtered_img = Image.merge('RGB', (grayscale, grayscale, grayscale))
                    enhancer = ImageEnhance.Color(filtered_img)
                    filtered_img = enhancer.enhance(0.8)
                elif filter_name == "vintage":
                    # Apply vintage effect
                    enhancer = ImageEnhance.Contrast(img)
                    filtered_img = enhancer.enhance(0.8)
                    enhancer = ImageEnhance.Color(filtered_img)
                    filtered_img = enhancer.enhance(0.9)
                else:
                    filtered_img = img.copy()
                
                # Save filtered image
                filtered_path = os.path.join(self.temp_dir, f"filtered_{filter_name}_{os.path.basename(image_path)}")
                filtered_img.save(filtered_path)
                return filtered_path
                
        except Exception as e:
            self.logger.error(f"Filter application failed: {str(e)}")
            return image_path
    
    async def resize_image(self, image_path: str, new_size: Tuple[int, int]) -> str:
        """Resize an image to new dimensions"""
        try:
            with Image.open(image_path) as img:
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                resized_path = os.path.join(self.temp_dir, f"resized_{new_size[0]}x{new_size[1]}_{os.path.basename(image_path)}")
                resized_img.save(resized_path)
                return resized_path
                
        except Exception as e:
            self.logger.error(f"Image resizing failed: {str(e)}")
            return image_path
    
    async def crop_image(self, image_path: str, crop_box: Tuple[int, int, int, int]) -> str:
        """Crop an image using the specified crop box (left, top, right, bottom)"""
        try:
            with Image.open(image_path) as img:
                cropped_img = img.crop(crop_box)
                
                cropped_path = os.path.join(self.temp_dir, f"cropped_{os.path.basename(image_path)}")
                cropped_img.save(cropped_path)
                return cropped_path
                
        except Exception as e:
            self.logger.error(f"Image cropping failed: {str(e)}")
            return image_path
    
    async def add_watermark(self, image_path: str, watermark_text: str, position: str = "bottom_right") -> str:
        """Add watermark text to an image"""
        try:
            with Image.open(image_path) as img:
                # Create drawing context
                draw = ImageDraw.Draw(img)
                
                # Calculate position based on parameter
                img_width, img_height = img.size
                try:
                    font = ImageFont.truetype("arial.ttf", 36)
                except OSError:
                    font = ImageFont.load_default()
                
                # Get text dimensions
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Calculate position
                if position == "bottom_right":
                    x = img_width - text_width - 20
                    y = img_height - text_height - 20
                elif position == "bottom_left":
                    x = 20
                    y = img_height - text_height - 20
                elif position == "top_right":
                    x = img_width - text_width - 20
                    y = 20
                elif position == "top_left":
                    x = 20
                    y = 20
                else:  # center
                    x = (img_width - text_width) // 2
                    y = (img_height - text_height) // 2
                
                # Draw watermark with semi-transparency
                watermark_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
                watermark_draw = ImageDraw.Draw(watermark_img)
                watermark_draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
                
                # Composite watermark onto original image
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                watermarked_img = Image.alpha_composite(img, watermark_img)
                
                # Save watermarked image
                watermarked_path = os.path.join(self.temp_dir, f"watermarked_{os.path.basename(image_path)}")
                watermarked_img = watermarked_img.convert('RGB')  # Convert back to RGB for JPEG
                watermarked_img.save(watermarked_path)
                return watermarked_path
                
        except Exception as e:
            self.logger.error(f"Watermark addition failed: {str(e)}")
            return image_path
    
    async def enhance_image(self, image_path: str, enhancement_settings: Dict[str, float]) -> str:
        """Enhance image with various adjustments"""
        try:
            with Image.open(image_path) as img:
                enhanced_img = img.copy()
                
                # Apply brightness enhancement
                if 'brightness' in enhancement_settings:
                    enhancer = ImageEnhance.Brightness(enhanced_img)
                    enhanced_img = enhancer.enhance(enhancement_settings['brightness'])
                
                # Apply contrast enhancement
                if 'contrast' in enhancement_settings:
                    enhancer = ImageEnhance.Contrast(enhanced_img)
                    enhanced_img = enhancer.enhance(enhancement_settings['contrast'])
                
                # Apply color enhancement
                if 'color' in enhancement_settings:
                    enhancer = ImageEnhance.Color(enhanced_img)
                    enhanced_img = enhancer.enhance(enhancement_settings['color'])
                
                # Apply sharpness enhancement
                if 'sharpness' in enhancement_settings:
                    enhancer = ImageEnhance.Sharpness(enhanced_img)
                    enhanced_img = enhancer.enhance(enhancement_settings['sharpness'])
                
                # Save enhanced image
                enhanced_path = os.path.join(self.temp_dir, f"enhanced_{os.path.basename(image_path)}")
                enhanced_img.save(enhanced_path)
                return enhanced_path
                
        except Exception as e:
            self.logger.error(f"Image enhancement failed: {str(e)}")
            return image_path
    
    def _apply_artistic_style(self, img: Image.Image, style: str) -> Image.Image:
        """Apply artistic style to image"""
        if style == "oil_painting":
            # Simulate oil painting effect
            return img.filter(ImageFilter.SMOOTH_MORE)
        elif style == "watercolor":
            # Simulate watercolor effect
            return img.filter(ImageFilter.BLUR)
        elif style == "sketch":
            # Convert to sketch-like effect
            gray = img.convert('L')
            return gray.convert('RGB')
        elif style == "vintage":
            # Apply vintage effect
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(0.7)
        else:
            return img
    
    def _add_text_overlay(self, img: Image.Image, text: str, font_size: int = 48) -> Image.Image:
        """Add text overlay to image"""
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
        
        # Draw text with outline for better visibility
        draw.text((x-2, y-2), text, font=font, fill=(0, 0, 0))
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0))
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        return img
    
    async def _release_model_resources(self) -> None:
        """Release model-specific resources"""
        # Clean up temporary files
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
        
        self.logger.info("Image generator resources released")
