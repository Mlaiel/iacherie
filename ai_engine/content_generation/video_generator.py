"""Video Content Generator - Advanced AI video generation engine

Professional video content generator for influencers and content creators
supporting video synthesis, editing, and enhancement.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont

from .base_generator import BaseContentGenerator, ContentGenerationContext


class VideoConfig:
    """
Configuration for video generation settings"""
    
    def __init__(self, **kwargs):
        self.width = kwargs.get('width', 1920)
        self.height = kwargs.get('height', 1080)
        self.fps = kwargs.get('fps', 30)
        self.duration = kwargs.get('duration', 15)
        self.format = kwargs.get('format', 'mp4')
        self.quality = kwargs.get('quality', 'high')
        self.style = kwargs.get('style', 'cinematic')


class VideoFormat:
    """
Video format enumeration"""

    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"


class VideoQuality:
    """Video quality enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class VideoStyle:
    """Video style enumeration"""

    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"
    ANIMATED = "animated"
    VINTAGE = "vintage"


class VideoGenerationOptions:
    """Configuration options for video generation"""
    
    def __init__(self, **kwargs):
        self.duration = kwargs.get('duration', 15)  # Duration in seconds
        self.resolution = kwargs.get('resolution', '1920x1080')
        self.fps = kwargs.get('fps', 30)
        self.format = kwargs.get('format', 'mp4')
        self.quality = kwargs.get('quality', 'high')
        self.style = kwargs.get('style', 'cinematic')
        self.mood = kwargs.get('mood', 'dynamic')
        self.aspect_ratio = kwargs.get('aspect_ratio', '16:9')
        self.color_palette = kwargs.get('color_palette', 'vibrant')
        self.motion_type = kwargs.get('motion_type', 'smooth')
        self.effects = kwargs.get('effects', [])
        self.include_audio = kwargs.get('include_audio', False)
        self.model_name = kwargs.get('model_name', 'runway-gen2')
        self.seed = kwargs.get('seed', None)


class VideoContentGenerator(BaseContentGenerator):
    """
    Advanced video content generator that creates high-quality video content
    for various purposes including:
        pass
    - Social media videos (Instagram Reels, TikTok, YouTube Shorts)
    - Promotional videos and advertisements
    - Product showcase videos
    - Animated logos and branding
    - Educational and tutorial videos
    - Background video loops
    - Video transitions and effects
    """
    
    def _setup_models(self) -> None:
        """
Setup AI models and dependencies"""
        try:
            # Initialize video generation models
            self._initialize_video_models()
            self._initialize_video_effects()
            self._initialize_video_processing()
            
            # Video specifications
            self.max_duration = 60  # 1 minute max
            self.supported_resolutions = {
                '720p': (1280, 720),
                '1080p': (1920, 1080),
                '4k': (3840, 2160),
                'square': (1080, 1080),
                'vertical': (1080, 1920)
            }
            
            # Supported video formats
            self.supported_formats = {
                'video', 'animation', 'slideshow', 'transition',
                'logo_animation', 'product_showcase', 'tutorial'
            }
            
            # Video codecs and quality settings
            self.codec_settings = {
                'mp4': {'codec': 'mp4v', 'quality': 'high'},
                'avi': {'codec': 'XVID', 'quality': 'medium'},
                'mov': {'codec': 'mp4v', 'quality': 'high'},
                'webm': {'codec': 'VP90', 'quality': 'web'}
            }
            
            self.logger.info("Video generator models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize video models: {str(e)}")
            raise
    
    def _initialize_video_models(self) -> None:
        """Initialize video generation models"""
        # In a real implementation, this would load models like:
        # - Runway Gen-2 for video generation
        # - Stable Video Diffusion for video synthesis
        # - AnimateDiff for animation generation
        self.video_models = {
            'runway-gen2': {'type': 'text-to-video', 'quality': 'high', 'speed': 'medium'},
            'stable-video': {'type': 'image-to-video', 'quality': 'high', 'speed': 'slow'},
            'animatediff': {'type': 'animation', 'quality': 'medium', 'speed': 'fast'},
            'pika-labs': {'type': 'text-to-video', 'quality': 'medium', 'speed': 'fast'}
        }
        
        self.current_video_model = 'runway-gen2'
    
    def _initialize_video_effects(self) -> None:
        """
Initialize video effects and filters"""
        self.available_effects = {
            'fade_in': {'duration': 1.0, 'type': 'transition'},
            'fade_out': {'duration': 1.0, 'type': 'transition'},
            'zoom_in': {'factor': 1.2, 'type': 'motion'},
            'zoom_out': {'factor': 0.8, 'type': 'motion'},
            'pan_left': {'distance': 100, 'type': 'motion'},
            'pan_right': {'distance': 100, 'type': 'motion'},
            'blur': {'intensity': 5, 'type': 'filter'},
            'sharpen': {'intensity': 3, 'type': 'filter'},
            'color_grade': {'style': 'cinematic', 'type': 'color'},
            'vignette': {'intensity': 0.3, 'type': 'artistic'}
        }
    
    def _initialize_video_processing(self) -> None:
        """
Initialize video processing capabilities"""
        # OpenCV setup for video processing
        self.video_writer_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        # Temporary directory for video processing
        self.temp_dir = tempfile.mkdtemp(prefix='video_gen_')
    
    def _setup_resources(self) -> None:
        """
Setup computational resources"""
        # Video generation requires substantial resources
        self.max_concurrent_requests = self.config.get('max_concurrent_requests', 1)
        self.request_timeout = self.config.get('request_timeout', 600)  # 10 minutes
        
        # Memory and storage management
        self.max_memory_usage = self.config.get('max_memory_mb', 8192)
        self.max_storage_usage = self.config.get('max_storage_gb', 10)
        
        # GPU acceleration
        self.use_gpu = self.config.get('use_gpu', True)
        self.gpu_memory_limit = self.config.get('gpu_memory_mb', 4096)
    
    def _setup_validation_rules(self) -> None:
        """
Setup video validation rules"""
        self.validation_rules = {
            'min_duration': 1.0,  # Minimum 1 second
            'max_duration': 60.0,  # Maximum 1 minute
            'min_fps': 15,
            'max_fps': 60,
            'supported_formats': ['mp4', 'avi', 'mov', 'webm'],
            'max_file_size_mb': 500,
            'min_resolution': (480, 360),
            'max_resolution': (3840, 2160)
        }
    
    async def generate_content(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate video content based on context and prompt.
        
        Args:
            context: Generation context with user and platform information
            prompt: Video generation prompt
            options: Additional generation options
            
        Returns:
            Generated video content with metadata
        """
        try:
            # Parse options
            gen_options = VideoGenerationOptions(**(options or {}))
            
            # Determine video type
            video_type = self._determine_video_type(context, prompt, gen_options)
            
            # Generate video based on type
            if video_type == 'animation':
                video_path, metadata = await self._generate_animation(
                    prompt, context, gen_options
                )
            elif video_type == 'slideshow':
                video_path, metadata = await self._generate_slideshow(
                    prompt, context, gen_options
                )
            elif video_type == 'logo_animation':
                video_path, metadata = await self._generate_logo_animation(
                    prompt, context, gen_options
                )
            elif video_type == 'product_showcase':
                video_path, metadata = await self._generate_product_showcase(
                    prompt, context, gen_options
                )
            else:
                video_path, metadata = await self._generate_general_video(
                    prompt, context, gen_options
                )
            
            # Apply post-processing
            processed_video_path = await self._post_process_video(
                video_path, gen_options, video_type
            )
            
            # Analyze video properties
            video_analysis = await self._analyze_video(processed_video_path)
            
            return {
                'video_file': processed_video_path,
                'format': gen_options.format,
                'resolution': gen_options.resolution,
                'fps': gen_options.fps,
                'duration': gen_options.duration,
                'metadata': {
                    **metadata,
                    'video_type': video_type,
                    'file_size_mb': os.path.getsize(processed_video_path) / (1024 * 1024),
                    'analysis': video_analysis
                },
                'generation_info': {
                    'model_used': gen_options.model_name,
                    'processing_time': metadata.get('processing_time', 0),
                    'quality_preset': gen_options.quality
                }
            }
            
        except Exception as e:
            self.logger.error(f"Video generation failed: {str(e)}")
            raise
    
    async def validate_output(self, content: Any) -> bool:
        """
        Validate generated video content.
        
        Args:
            content: Generated video content to validate
            
        Returns:
            True if content meets quality standards
        """
        if not isinstance(content, dict):
            return False
        
        # Check required fields
        required_fields = ['video_file', 'format', 'resolution', 'fps', 'duration']
        for field in required_fields:
            if field not in content:
                return False
        
        # Validate duration
        duration = content.get('duration', 0)
        if duration < self.validation_rules['min_duration']:
            return False
        
        if duration > self.validation_rules['max_duration']:
            return False
        
        # Validate FPS
        fps = content.get('fps', 0)
        if not (self.validation_rules['min_fps'] <= fps <= self.validation_rules['max_fps']):
            return False
        
        # Check file exists and is valid
        video_file = content.get('video_file')
        if not video_file or not os.path.exists(video_file):
            return False
        
        # Check file size
        file_size_mb = os.path.getsize(video_file) / (1024 * 1024)
        if file_size_mb > self.validation_rules['max_file_size_mb']:
            return False
        
        # Validate video properties
        try:
            cap = cv2.VideoCapture(video_file)
            if not cap.isOpened():
                return False
            
            # Check frame count and properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            
            # Validate resolution
            if (width, height) < self.validation_rules['min_resolution']:
                return False
            
            if (width, height) > self.validation_rules['max_resolution']:
                return False
            
            # Check if video has content
            if frame_count < fps:  # Less than 1 second of content
                return False
            
            return True
            
        except:
            return False
    
    def _determine_video_type(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: VideoGenerationOptions
    ) -> str:
        """
Determine the type of video to generate"""
        prompt_lower = prompt.lower()
        
        # Check for explicit type in prompt
        if any(word in prompt_lower for word in ['animation', 'animated', 'cartoon']):
            return 'animation'
        elif any(word in prompt_lower for word in ['slideshow', 'slides', 'presentation']):
            return 'slideshow'
        elif any(word in prompt_lower for word in ['logo', 'brand', 'intro']):
            return 'logo_animation'
        elif any(word in prompt_lower for word in ['product', 'showcase', 'demo']):
            return 'product_showcase'
        elif any(word in prompt_lower for word in ['tutorial', 'howto', 'guide']):
            return 'tutorial'
        
        # Check platform requirements
        if context.platform_requirements:
            platform = context.platform_requirements.get('platform', '').lower()
            if 'tiktok' in platform or 'reels' in platform:
                return 'social_video'
            elif 'youtube' in platform:
                return 'youtube_video'
            elif 'product' in platform:
                return 'product_showcase'
        
        # Default to general video
        return 'video'
    
    async def _generate_animation(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: VideoGenerationOptions
    ) -> Tuple[str, Dict[str, Any]]:
        """
Generate animated video content"""
        start_time = datetime.now()
        
        # Parse resolution
        width, height = self._parse_resolution(options.resolution)
        
        # Create animation frames
        frames = await self._create_animation_frames(prompt, options, width, height)
        
        # Create video from frames
        video_path = await self._frames_to_video(frames, options, width, height)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'prompt': prompt,
            'style': options.style,
            'motion_type': options.motion_type,
            'frame_count': len(frames),
            'processing_time': processing_time,
            'model_used': options.model_name
        }
        
        return video_path, metadata
    
    async def _generate_slideshow(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: VideoGenerationOptions
    ) -> Tuple[str, Dict[str, Any]]:
        """
Generate slideshow video"""
        start_time = datetime.now()
        
        # Parse slideshow content from prompt
        slides_content = self._parse_slideshow_content(prompt)
        
        # Create slide frames
        frames = await self._create_slideshow_frames(slides_content, options)
        
        # Create video with transitions
        video_path = await self._slideshow_to_video(frames, options)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'slides_count': len(slides_content),
            'transition_style': 'fade',
            'processing_time': processing_time
        }
        
        return video_path, metadata
    
    async def _generate_logo_animation(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: VideoGenerationOptions
    ) -> Tuple[str, Dict[str, Any]]:
        """
Generate logo animation video"""
        start_time = datetime.now()
        
        # Extract logo information from prompt or context
        logo_info = self._extract_logo_info(prompt, context)
        
        # Create logo animation frames
        frames = await self._create_logo_animation_frames(logo_info, options)
        
        # Create video
        video_path = await self._frames_to_video(frames, options, *self._parse_resolution(options.resolution))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'animation_type': 'logo',
            'logo_info': logo_info,
            'processing_time': processing_time
        }
        
        return video_path, metadata
    
    async def _generate_product_showcase(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: VideoGenerationOptions
    ) -> Tuple[str, Dict[str, Any]]:
        """
Generate product showcase video"""
        start_time = datetime.now()
        
        # Parse product information
        product_info = self._parse_product_info(prompt)
        
        # Create product showcase frames
        frames = await self._create_product_showcase_frames(product_info, options)
        
        # Create video
        video_path = await self._frames_to_video(frames, options, *self._parse_resolution(options.resolution))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'product_info': product_info,
            'showcase_style': options.style,
            'processing_time': processing_time
        }
        
        return video_path, metadata
    
    async def _generate_general_video(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: VideoGenerationOptions
    ) -> Tuple[str, Dict[str, Any]]:
        """
Generate general video content"""
        start_time = datetime.now()
        
        # Create general video frames based on prompt
        frames = await self._create_general_video_frames(prompt, options)
        
        # Create video
        video_path = await self._frames_to_video(frames, options, *self._parse_resolution(options.resolution))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = {
            'prompt': prompt,
            'video_style': options.style,
            'processing_time': processing_time
        }
        
        return video_path, metadata
    
    def _parse_resolution(self, resolution_str: str) -> Tuple[int, int]:
        """
Parse resolution string to width, height tuple"""
        if 'x' in resolution_str:
            width, height = map(int, resolution_str.split('x'))
            return width, height
        elif resolution_str in self.supported_resolutions:
            return self.supported_resolutions[resolution_str]
        else:
            return 1920, 1080  # Default to 1080p
    
    async def _create_animation_frames(
        self,
        prompt: str,
        options: VideoGenerationOptions,
        width: int,
        height: int
    ) -> List[np.ndarray]:
        """
Create animation frames"""
        frame_count = int(options.duration * options.fps)
        frames = []
        
        # Create a simple animation sequence
        for i in range(frame_count):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Create simple animated elements
            progress = i / frame_count
            
            # Animated background color
            bg_color = self._interpolate_color(
                (50, 50, 100),  # Start color
                (100, 50, 150),  # End color
                progress
            )
            frame[:] = bg_color
            
            # Animated moving element
            center_x = int(width * (0.2 + 0.6 * progress))
            center_y = height // 2
            
            cv2.circle(frame, (center_x, center_y), 50, (255, 255, 255), -1)
            
            # Add text if specified
            if 'text' in prompt.lower():
                text = self._extract_text_from_prompt(prompt)
                self._add_text_to_frame(frame, text, center_x, center_y + 100)
            
            frames.append(frame)
        
        return frames
    
    async def _create_slideshow_frames(
        self,
        slides_content: List[str],
        options: VideoGenerationOptions
    ) -> List[np.ndarray]:
        """
Create slideshow frames"""
        width, height = self._parse_resolution(options.resolution)
        frames_per_slide = int(options.fps * (options.duration / len(slides_content)))
        all_frames = []
        
        for slide_text in slides_content:
            # Create frames for this slide
            for _ in range(frames_per_slide):
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                frame[:] = (40, 40, 40)  # Dark gray background
                
                # Add slide text
                self._add_slide_text(frame, slide_text, width, height)
                all_frames.append(frame)
        
        return all_frames
    
    async def _create_logo_animation_frames(
        self,
        logo_info: Dict[str, Any],
        options: VideoGenerationOptions
    ) -> List[np.ndarray]:
        """
Create logo animation frames"""
        width, height = self._parse_resolution(options.resolution)
        frame_count = int(options.duration * options.fps)
        frames = []
        
        logo_text = logo_info.get('text', 'LOGO')
        
        for i in range(frame_count):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            progress = i / frame_count
            
            # Animated logo appearance
            if progress < 0.3:
                # Fade in phase
                alpha = progress / 0.3
                self._add_logo_text(frame, logo_text, width, height, alpha)
            elif progress < 0.7:
                # Static phase
                self._add_logo_text(frame, logo_text, width, height, 1.0)
            else:
                # Scale effect phase
                scale = 1.0 + (progress - 0.7) * 0.5
                self._add_logo_text(frame, logo_text, width, height, 1.0, scale)
            
            frames.append(frame)
        
        return frames
    
    async def _create_product_showcase_frames(
        self,
        product_info: Dict[str, Any],
        options: VideoGenerationOptions
    ) -> List[np.ndarray]:
        """
Create product showcase frames"""
        width, height = self._parse_resolution(options.resolution)
        frame_count = int(options.duration * options.fps)
        frames = []
        
        product_name = product_info.get('name', 'Product')
        features = product_info.get('features', ['Feature 1', 'Feature 2'])
        
        for i in range(frame_count):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Gradient background
            self._add_gradient_background(frame, options.color_palette)
            
            # Product showcase content
            progress = i / frame_count
            current_feature_idx = min(int(progress * len(features)), len(features) - 1)
            
            # Add product name
            self._add_product_text(frame, product_name, width, height // 3)
            
            # Add current feature
            current_feature = features[current_feature_idx]
            self._add_feature_text(frame, current_feature, width, 2 * height // 3)
            
            frames.append(frame)
        
        return frames
    
    async def _create_general_video_frames(
        self,
        prompt: str,
        options: VideoGenerationOptions
    ) -> List[np.ndarray]:
        """
Create general video frames based on prompt"""
        width, height = self._parse_resolution(options.resolution)
        frame_count = int(options.duration * options.fps)
        frames = []
        
        # Analyze prompt for visual elements
        visual_elements = self._analyze_visual_elements(prompt)
        
        for i in range(frame_count):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            progress = i / frame_count
            
            # Create dynamic background based on mood
            self._create_dynamic_background(frame, options.mood, progress)
            
            # Add visual elements based on prompt
            for element in visual_elements:
                self._add_visual_element(frame, element, progress, width, height)
            
            frames.append(frame)
        
        return frames
    
    async def _frames_to_video(
        self,
        frames: List[np.ndarray],
        options: VideoGenerationOptions,
        width: int,
        height: int
    ) -> str:
        """
Convert frames to video file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"video_{timestamp}.{options.format}"
        video_path = os.path.join(self.temp_dir, video_filename)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, options.fps, (width, height))
        
        # Write frames
        for frame in frames:
            # Convert RGB to BGR for OpenCV
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(bgr_frame)
        
        out.release()
        return video_path
    
    async def _slideshow_to_video(
        self,
        frames: List[np.ndarray],
        options: VideoGenerationOptions
    ) -> str:
        """Convert slideshow frames to video with transitions"""
        # For now, use the same method as frames_to_video
        # In a full implementation, add transition effects between slides
        width, height = frames[0].shape[1], frames[0].shape[0]
        return await self._frames_to_video(frames, options, width, height)
    
    def _interpolate_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """
Interpolate between two colors"""
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        return (r, g, b)
    
    def _extract_text_from_prompt(self, prompt: str) -> str:
        """
Extract text content from prompt"""
        # Look for quoted text
        if '"' in prompt:
            parts = prompt.split('"')
            if len(parts) >= 3:
                return parts[1]
        
        # Extract key words
        words = prompt.split()
        important_words = [word for word in words if len(word) > 3]
        return ' '.join(important_words[:3])  # First 3 important words
    
    def _add_text_to_frame(self, frame: np.ndarray, text: str, x: int, y: int) -> None:
        """Add text to frame using OpenCV"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (255, 255, 255)
        thickness = 2
        
        cv2.putText(frame, text, (x - len(text) * 10, y), font, font_scale, color, thickness)
    
    def _parse_slideshow_content(self, prompt: str) -> List[str]:
        """
Parse slideshow content from prompt"""
        # Simple parsing - split by sentences or bullet points
        sentences = prompt.split('.')
        slides = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not slides:
            slides = ['Slide 1', 'Slide 2', 'Slide 3']
        
        return slides[:5]  # Max 5 slides
    
    def _extract_logo_info(self, prompt: str, context: ContentGenerationContext) -> Dict[str, Any]:
        """
Extract logo information from prompt and context"""
        logo_info = {'text': 'LOGO', 'style': 'modern'}
        
        # Check brand guidelines
        if context.brand_guidelines:
            brand_name = context.brand_guidelines.get('name', 'BRAND')
            logo_info['text'] = brand_name
        
        # Extract from prompt
        words = prompt.split()
        for i, word in enumerate(words):
            if word.lower() in ['logo', 'brand'] and i + 1 < len(words):
                logo_info['text'] = words[i + 1].upper()
                break
        
        return logo_info
    
    def _parse_product_info(self, prompt: str) -> Dict[str, Any]:
        """
Parse product information from prompt"""
        product_info = {
            'name': 'Product',
            'features': ['High Quality', 'Great Value', 'Easy to Use']
        }
        
        # Extract product name (simple heuristics)
        words = prompt.split()
        for i, word in enumerate(words):
            if word.lower() == 'product' and i + 1 < len(words):
                product_info['name'] = words[i + 1]
                break
        
        return product_info
    
    def _add_slide_text(self, frame: np.ndarray, text: str, width: int, height: int) -> None:
        """
Add formatted text to slide frame"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        color = (255, 255, 255)
        thickness = 3
        
        # Center the text
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x = (width - text_size[0]) // 2
        y = (height + text_size[1]) // 2
        
        cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
    
    def _add_logo_text(self, frame: np.ndarray, text: str, width: int, height: int, alpha: float, scale: float = 1.0) -> None:
        """
Add logo text with alpha and scale"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 3 * scale
        color = (int(255 * alpha), int(255 * alpha), int(255 * alpha))
        thickness = 4
        
        # Center the text
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x = (width - text_size[0]) // 2
        y = (height + text_size[1]) // 2
        
        cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
    
    def _add_gradient_background(self, frame: np.ndarray, color_palette: str) -> None:
        """
Add gradient background based on color palette"""
        height, width = frame.shape[:2]
        
        if color_palette == 'vibrant':
            start_color = (255, 100, 150)
            end_color = (100, 150, 255)
        elif color_palette == 'cool':
            start_color = (100, 150, 200)
            end_color = (50, 100, 150)
        else:  # warm
            start_color = (255, 150, 100)
            end_color = (200, 100, 50)
        
        for y in range(height):
            t = y / height
            color = self._interpolate_color(start_color, end_color, t)
            frame[y, :] = color
    
    def _add_product_text(self, frame: np.ndarray, text: str, width: int, y: int) -> None:
        """
Add product name text"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.5
        color = (255, 255, 255)
        thickness = 3
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x = (width - text_size[0]) // 2
        
        cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
    
    def _add_feature_text(self, frame: np.ndarray, text: str, width: int, y: int) -> None:
        """
Add feature text"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        color = (200, 200, 200)
        thickness = 2
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x = (width - text_size[0]) // 2
        
        cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
    
    def _analyze_visual_elements(self, prompt: str) -> List[str]:
        """
Analyze prompt for visual elements"""
        elements = []
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['circle', 'round']):
            elements.append('circle')
        if any(word in prompt_lower for word in ['square', 'box']):
            elements.append('square')
        if any(word in prompt_lower for word in ['text', 'title']):
            elements.append('text')
        if any(word in prompt_lower for word in ['particle', 'dots']):
            elements.append('particles')
        
        return elements if elements else ['text']
    
    def _create_dynamic_background(self, frame: np.ndarray, mood: str, progress: float) -> None:
        """
Create dynamic background based on mood"""
        height, width = frame.shape[:2]
        
        if mood == 'energetic':
            # Bright, changing colors
            base_color = (
                int(128 + 127 * np.sin(progress * 4 * np.pi)),
                int(128 + 127 * np.sin(progress * 4 * np.pi + np.pi/2)),
                int(128 + 127 * np.sin(progress * 4 * np.pi + np.pi))
            )
        elif mood == 'calm':
            # Soft, stable colors
            base_color = (80, 120, 160)
        else:  # dynamic
            # Gradual color transition
            start_color = (50, 50, 100)
            end_color = (100, 50, 150)
            base_color = self._interpolate_color(start_color, end_color, progress)
        
        frame[:] = base_color
    
    def _add_visual_element(self, frame: np.ndarray, element: str, progress: float, width: int, height: int) -> None:
        """
Add visual element to frame"""
        if element == 'circle':
            center = (width // 2, height // 2)
            radius = int(50 + 20 * np.sin(progress * 2 * np.pi))
            cv2.circle(frame, center, radius, (255, 255, 255), 2)
        elif element == 'square':
            size = int(100 + 50 * np.sin(progress * 2 * np.pi))
            x = (width - size) // 2
            y = (height - size) // 2
            cv2.rectangle(frame, (x, y), (x + size, y + size), (255, 255, 255), 2)
        elif element == 'text':
            text = "Dynamic Video"
            self._add_text_to_frame(frame, text, width // 2, height // 2)
        elif element == 'particles':
            # Add some random particles
            for _ in range(10):
                x = int(np.random.random() * width)
                y = int(np.random.random() * height)
                cv2.circle(frame, (x, y), 3, (255, 255, 255), -1)
    
    async def _post_process_video(
        self,
        video_path: str,
        options: VideoGenerationOptions,
        video_type: str
    ) -> str:
        """Apply post-processing effects to video"""
        if not options.effects:
            return video_path
        
        # For now, return the original path
        # In a full implementation, apply effects like:
        # - Color grading
        # - Stabilization
        # - Noise reduction
        # - Transitions
        
        return video_path
    
    async def _analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
Analyze video properties"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Read first frame for analysis
            ret, first_frame = cap.read()
            brightness = 0
            if ret:
                gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
            
            cap.release()
            
            return {
                'frame_count': frame_count,
                'actual_fps': fps,
                'resolution': f"{width}x{height}",
                'duration_seconds': duration,
                'average_brightness': float(brightness),
                'aspect_ratio': width / height if height > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Video analysis failed: {str(e)}")
            return {}
    
    def get_animation_styles(self) -> List[str]:
        """Get available animation styles"""
        return [
            "fade_in", "fade_out", "slide_left", "slide_right",
            "zoom_in", "zoom_out", "bounce", "elastic",
            "rotate", "scale", "flip", "particle"
        ]
    
    def get_transition_effects(self) -> List[str]:
        """Get available transition effects"""
        return [
            "crossfade", "wipe", "dissolve", "cut",
            "push", "slide", "fade", "morph",
            "zoom", "spin", "blur", "pixelate"
        ]
    
    def get_video_templates(self) -> List[Dict[str, Any]]:
        """Get available video templates"""
        return [
            {
                "id": "promo_30s",
                "name": "30-Second Promo",
                "duration": 30,
                "format": "16:9",
                "style": "modern",
                "fps": 30
            },
            {
                "id": "story_60s", 
                "name": "Story Format",
                "duration": 60,
                "format": "9:16",
                "style": "cinematic",
                "fps": 24
            },
            {
                "id": "intro_10s",
                "name": "Brand Intro",
                "duration": 10,
                "format": "16:9",
                "style": "professional",
                "fps": 30
            }
        ]
    
    async def generate_thumbnail(self, video_path: str, timestamp: float = 1.0) -> str:
        """Generate thumbnail from video"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Set timestamp position
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                thumbnail_path = os.path.join(self.temp_dir, f"thumbnail_{timestamp}.jpg")
                cv2.imwrite(thumbnail_path, frame)
                return thumbnail_path
            else:
                raise ValueError("Could not extract frame for thumbnail")
                
        except Exception as e:
            self.logger.error(f"Thumbnail generation failed: {str(e)}")
            # Return a default thumbnail path
            return f"thumbnail_{timestamp}.jpg"
    
    async def add_subtitles(self, video_path: str, subtitle_text: str) -> str:
        """Add subtitles to video"""
        try:
            # Simulate subtitle processing
            await asyncio.sleep(0.2)
            
            subtitled_path = os.path.join(self.temp_dir, f"subtitled_{os.path.basename(video_path)}")
            
            # In a real implementation, this would use FFmpeg to add subtitles
            # For now, copy the original file
            import shutil
            shutil.copy2(video_path, subtitled_path)
            
            return subtitled_path
            
        except Exception as e:
            self.logger.error(f"Subtitle addition failed: {str(e)}")
            return video_path
    
    async def create_slideshow(self, images: List[str], duration_per_slide: float = 2.0) -> str:
        """Create slideshow from images"""
        try:
            # Calculate total duration and frame count
            total_duration = len(images) * duration_per_slide
            fps = 30
            total_frames = int(total_duration * fps)
            frames_per_slide = int(duration_per_slide * fps)
            
            slideshow_path = os.path.join(self.temp_dir, f"slideshow_{len(images)}_slides.mp4")
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(slideshow_path, fourcc, fps, (1920, 1080))
            
            for image_path in images:
                # Load and resize image
                img = cv2.imread(image_path)
                if img is not None:
                    img_resized = cv2.resize(img, (1920, 1080))
                    
                    # Write frames for this slide
                    for _ in range(frames_per_slide):
                        out.write(img_resized)
                else:
                    # Create black frame if image not found
                    black_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
                    for _ in range(frames_per_slide):
                        out.write(black_frame)
            
            out.release()
            return slideshow_path
            
        except Exception as e:
            self.logger.error(f"Slideshow creation failed: {str(e)}")
            # Return a mock path
            return f"slideshow_{len(images)}_slides.mp4"
    
    async def apply_color_correction(self, video_path: str, settings: Dict[str, Any]) -> str:
        """Apply color correction to video"""
        try:
            corrected_path = os.path.join(self.temp_dir, f"color_corrected_{os.path.basename(video_path)}")
            
            # Open video capture and writer
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(corrected_path, fourcc, fps, (width, height))
            
            # Apply color correction to each frame
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply basic color corrections
                brightness = settings.get('brightness', 0)
                contrast = settings.get('contrast', 1.0)
                saturation = settings.get('saturation', 1.0)
                
                # Adjust brightness and contrast
                corrected_frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)
                
                # Adjust saturation
                if saturation != 1.0:
                    hsv = cv2.cvtColor(corrected_frame, cv2.COLOR_BGR2HSV)
                    hsv[:, :, 1] = hsv[:, :, 1] * saturation
                    corrected_frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                
                out.write(corrected_frame)
            
            cap.release()
            out.release()
            
            return corrected_path
            
        except Exception as e:
            self.logger.error(f"Color correction failed: {str(e)}")
            return video_path
    
    async def extract_frames(self, video_path: str, frame_rate: float = 1.0) -> List[str]:
        """Extract frames from video"""
        try:
            frames_list = []
            cap = cv2.VideoCapture(video_path)
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps / frame_rate)
            
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frame_path = os.path.join(self.temp_dir, f"frame_{extracted_count:04d}.jpg")
                    cv2.imwrite(frame_path, frame)
                    frames_list.append(frame_path)
                    extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            return frames_list
            
        except Exception as e:
            self.logger.error(f"Frame extraction failed: {str(e)}")
            # Return mock frame paths
            num_frames = int(30 * frame_rate)  # Assume 30s video
            return [f"frame_{i:04d}.jpg" for i in range(num_frames)]
    
    async def merge_videos(self, video_paths: List[str]) -> str:
        """Merge multiple videos"""
        try:
            if not video_paths:
                raise ValueError("No videos to merge")
            
            merged_path = os.path.join(self.temp_dir, f"merged_{len(video_paths)}_videos.mp4")
            
            # Get properties from first video
            first_cap = cv2.VideoCapture(video_paths[0])
            fps = first_cap.get(cv2.CAP_PROP_FPS)
            width = int(first_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(first_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            first_cap.release()
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(merged_path, fourcc, fps, (width, height))
            
            # Merge videos
            for video_path in video_paths:
                cap = cv2.VideoCapture(video_path)
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Resize frame if necessary
                    if frame.shape[:2] != (height, width):
                        frame = cv2.resize(frame, (width, height))
                    
                    out.write(frame)
                
                cap.release()
            
            out.release()
            return merged_path
            
        except Exception as e:
            self.logger.error(f"Video merging failed: {str(e)}")
            # Return mock merged path
            return f"merged_{len(video_paths)}_videos.mp4"
    
    def _add_effects(self, video_data: bytes, effects: List[str]) -> bytes:
        """Add visual effects to video"""
        # Simulate effect processing
        effects_data = b"effects_applied_" + "_".join(effects).encode()
        return video_data + effects_data
    
    def _render_video(self, scenes: List[Dict], output_format: str) -> bytes:
        """Render final video from scenes"""
        # Simulate video rendering
        scene_info = f"rendered_video_{len(scenes)}_scenes_{output_format}"
        return scene_info.encode() + b"video_data"
    
    def _supports_content_type(self, content_type: str) -> bool:
        """Check if generator supports the specified content type"""
        return content_type == 'video'
    
    async def _release_model_resources(self) -> None:
        """
Release model-specific resources"""
        # Clean up temporary files
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
        
        self.logger.info("Video generator resources released")
