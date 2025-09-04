"""Media Video Generator - Consolidated Video Generation System

Handles all 7 types of video generation:
1. Short-form videos (TikTok, Instagram Reels, YouTube Shorts)
2. Long-form content (YouTube videos, educational content)
3. Marketing videos (ads, promotional content, commercials)
4. Product demonstrations (tutorials, reviews, showcases)
5. Animation and motion graphics (2D/3D animations, explainers)
6. Live streaming content (overlays, scenes, effects)
7. Video editing and enhancement (cuts, transitions, effects)

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import io
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import base64

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_engine.content_generation.base_generator import BaseContentGenerator, ContentGenerationContext


class VideoType(Enum):
    """Video generation types"""
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"
    MARKETING = "marketing"
    PRODUCT_DEMO = "product_demo"
    ANIMATION = "animation"
    LIVE_STREAMING = "live_streaming"
    VIDEO_EDITING = "video_editing"


class VideoFormat(Enum):
    """Supported video formats"""
    MP4 = "mp4"
    WEBM = "webm"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    FLV = "flv"
    GIF = "gif"


class VideoQuality(Enum):
    """Video quality levels"""
    LOW = "480p"        # 854x480
    MEDIUM = "720p"     # 1280x720
    HIGH = "1080p"      # 1920x1080
    ULTRA = "4K"        # 3840x2160


class VideoStyle(Enum):
    """Video style options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    CINEMATIC = "cinematic"
    DYNAMIC = "dynamic"
    MINIMAL = "minimal"
    ENERGETIC = "energetic"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"


class VideoConfig:
    """Configuration for video generation"""
    
    def __init__(self, **kwargs):
        self.video_type = kwargs.get('video_type', VideoType.SHORT_FORM)
        self.format = kwargs.get('format', VideoFormat.MP4)
        self.quality = kwargs.get('quality', VideoQuality.HIGH)
        self.style = kwargs.get('style', VideoStyle.PROFESSIONAL)
        self.duration = kwargs.get('duration', 30)  # seconds
        self.aspect_ratio = kwargs.get('aspect_ratio', '16:9')
        self.frame_rate = kwargs.get('frame_rate', 30)  # fps
        self.platform = kwargs.get('platform', 'youtube')
        self.include_audio = kwargs.get('include_audio', True)
        self.include_subtitles = kwargs.get('include_subtitles', False)
        self.transition_style = kwargs.get('transition_style', 'smooth')
        self.color_scheme = kwargs.get('color_scheme', 'vibrant')
        self.mood = kwargs.get('mood', 'upbeat')
        self.language = kwargs.get('language', 'en')
        self.brand_elements = kwargs.get('brand_elements', {})
        self.music_style = kwargs.get('music_style', 'background')


class VideoScene:
    """Individual video scene configuration"""
    
    def __init__(self, **kwargs):
        self.duration = kwargs.get('duration', 5)  # seconds
        self.scene_type = kwargs.get('scene_type', 'talking_head')
        self.text_overlay = kwargs.get('text_overlay', '')
        self.visual_elements = kwargs.get('visual_elements', [])
        self.audio_track = kwargs.get('audio_track', None)
        self.effects = kwargs.get('effects', [])


class MediaVideoGenerator(BaseContentGenerator):
    """
    Comprehensive video generator supporting 7 different video generation types
    with advanced AI-powered video creation capabilities.
    """
    
    def _setup_models(self) -> None:
        """Setup AI models for video generation"""
        try:
            # Initialize AI models for different video types
            self.models = {}
            
            # Short-form video models
            self.models['short_form'] = {
                'primary': 'runway-gen3',
                'fallback': 'stable-video-diffusion',
                'editing': 'auto-edit-ai'
            }
            
            # Long-form content models
            self.models['long_form'] = {
                'primary': 'long-form-ai',
                'fallback': 'educational-video-ai',
                'structure': 'content-structuring-ai'
            }
            
            # Marketing video models
            self.models['marketing'] = {
                'primary': 'commercial-video-ai',
                'fallback': 'promo-creator',
                'conversion': 'ad-optimizer-ai'
            }
            
            # Product demonstration models
            self.models['product_demo'] = {
                'primary': 'product-showcase-ai',
                'fallback': 'demo-creator',
                'tutorial': 'tutorial-generator'
            }
            
            # Animation models
            self.models['animation'] = {
                'primary': 'animation-diffusion',
                'fallback': 'motion-graphics-ai',
                '3d_engine': 'blender-ai'
            }
            
            # Live streaming models
            self.models['live_streaming'] = {
                'primary': 'obs-ai-assistant',
                'fallback': 'streaming-enhancer',
                'overlay_generator': 'dynamic-overlays'
            }
            
            # Video editing models
            self.models['video_editing'] = {
                'primary': 'premiere-ai',
                'fallback': 'auto-editor',
                'enhancement': 'video-upscaler'
            }
            
            # Platform-specific configurations
            self.platform_specs = self._initialize_platform_specs()
            
            # Video templates and presets
            self.video_templates = self._initialize_video_templates()
            
            self.logger.info("Video generator models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize video models: {str(e)}")
            raise
    
    def _setup_resources(self) -> None:
        """Setup computational resources for video generation"""
        self.max_concurrent_generations = self.config.get('max_concurrent_generations', 2)
        self.generation_timeout = self.config.get('generation_timeout', 1800)  # 30 minutes
        self.max_duration_seconds = self.config.get('max_duration_seconds', 600)  # 10 minutes
        self.max_file_size_gb = self.config.get('max_file_size_gb', 5)
        
        # Video processing settings
        self.supported_formats = ['mp4', 'webm', 'avi', 'mov', 'mkv', 'flv', 'gif']
        self.gpu_acceleration = self.config.get('gpu_acceleration', True)
        self.encoding_preset = self.config.get('encoding_preset', 'medium')
    
    def _setup_validation_rules(self) -> None:
        """Setup video validation rules"""
        self.validation_rules = {
            'min_duration_seconds': 1,
            'max_duration_seconds': 600,
            'max_file_size_gb': 5,
            'supported_formats': self.supported_formats,
            'content_safety_enabled': True,
            'copyright_check_enabled': True,
            'audio_quality_check': True
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
            context: Generation context
            prompt: Video description prompt
            options: Generation options
            
        Returns:
            Generated video data with metadata
        """
        try:
            # Parse video generation options
            video_config = VideoConfig(**(options or {}))
            
            # Determine video type from prompt if not specified
            if not hasattr(video_config, 'video_type') or not video_config.video_type:
                video_config.video_type = self._determine_video_type(prompt, context)
            
            # Build video generation plan
            video_plan = await self._build_video_plan(
                prompt, video_config, context
            )
            
            # Generate video based on type
            video_result = await self._generate_video_by_type(
                video_plan, video_config, context
            )
            
            # Post-process the video
            processed_video = await self._post_process_video(
                video_result, video_config
            )
            
            # Get video metadata
            video_metadata = await self._extract_video_metadata(processed_video)
            
            return {
                'content': processed_video,
                'video_type': video_config.video_type.value,
                'format': video_config.format.value,
                'quality': video_config.quality.value,
                'metadata': {
                    'duration_seconds': video_config.duration,
                    'aspect_ratio': video_config.aspect_ratio,
                    'frame_rate': video_config.frame_rate,
                    'resolution': self._get_resolution_from_quality(video_config.quality),
                    'generation_time': datetime.utcnow().isoformat(),
                    'model_used': self.models[video_config.video_type.value]['primary'],
                    'file_size_bytes': len(processed_video) if isinstance(processed_video, bytes) else 0,
                    'has_audio': video_config.include_audio,
                    'has_subtitles': video_config.include_subtitles,
                    **video_metadata
                },
                'configuration': {
                    'platform': video_config.platform,
                    'style': video_config.style.value,
                    'mood': video_config.mood,
                    'color_scheme': video_config.color_scheme,
                    'transition_style': video_config.transition_style,
                    'language': video_config.language
                },
                'scenes': video_plan.get('scenes', [])
            }
            
        except Exception as e:
            self.logger.error(f"Video generation failed: {str(e)}")
            raise

    async def validate_output(self, content: Any) -> bool:
        """Validate generated video content"""
        if not isinstance(content, dict):
            return False
        
        # Check if video data exists
        video_data = content.get('content')
        if not video_data:
            return False
        
        # Check metadata
        metadata = content.get('metadata', {})
        duration = metadata.get('duration_seconds', 0)
        
        # Validate duration
        if duration <= 0 or duration > self.max_duration_seconds:
            return False
        
        # Check format
        format_type = content.get('format')
        if format_type not in self.supported_formats:
            return False
        
        # Check file size
        file_size_bytes = metadata.get('file_size_bytes', 0)
        if file_size_bytes > self.max_file_size_gb * 1024 * 1024 * 1024:
            return False
        
        return True

    def _determine_video_type(
        self, 
        prompt: str, 
        context: ContentGenerationContext
    ) -> VideoType:
        """Determine video type from prompt and context"""
        prompt_lower = prompt.lower()
        
        # Check platform context first
        if context.platform_requirements:
            platform = context.platform_requirements.get('platform', '').lower()
            if platform in ['tiktok', 'instagram', 'reels', 'shorts']:
                return VideoType.SHORT_FORM
            elif platform in ['youtube', 'vimeo']:
                # Could be short or long form, check duration or other hints
                if any(word in prompt_lower for word in ['short', 'quick', 'brief']):
                    return VideoType.SHORT_FORM
                else:
                    return VideoType.LONG_FORM
        
        # Check for specific keywords
        if any(word in prompt_lower for word in ['short', 'reel', 'tiktok', 'quick']):
            return VideoType.SHORT_FORM
        elif any(word in prompt_lower for word in ['tutorial', 'course', 'explanation', 'documentary']):
            return VideoType.LONG_FORM
        elif any(word in prompt_lower for word in ['ad', 'commercial', 'promotion', 'marketing']):
            return VideoType.MARKETING
        elif any(word in prompt_lower for word in ['demo', 'product', 'review', 'showcase']):
            return VideoType.PRODUCT_DEMO
        elif any(word in prompt_lower for word in ['animation', 'cartoon', 'motion graphics']):
            return VideoType.ANIMATION
        elif any(word in prompt_lower for word in ['live', 'stream', 'broadcast']):
            return VideoType.LIVE_STREAMING
        elif any(word in prompt_lower for word in ['edit', 'cut', 'montage', 'compilation']):
            return VideoType.VIDEO_EDITING
        else:
            return VideoType.SHORT_FORM  # Default for general content

    async def _build_video_plan(
        self,
        prompt: str,
        config: VideoConfig,
        context: ContentGenerationContext
    ) -> Dict[str, Any]:
        """Build a structured plan for video generation"""
        
        # Get template for the video type
        template = self.video_templates.get(config.video_type.value, {})
        
        # Calculate scene breakdown
        total_duration = config.duration
        scene_duration = template.get('scene_duration', 5)
        num_scenes = max(1, total_duration // scene_duration)
        
        # Build scenes
        scenes = []
        for i in range(num_scenes):
            scene = VideoScene(
                duration=scene_duration if i < num_scenes - 1 else total_duration - (i * scene_duration),
                scene_type=template.get('default_scene_type', 'main_content'),
                text_overlay=f"Scene {i+1}",
                visual_elements=template.get('visual_elements', []),
                effects=template.get('effects', [])
            )
            scenes.append(scene.__dict__)
        
        # Build video plan
        video_plan = {
            'title': self._generate_video_title(prompt, config),
            'description': prompt,
            'total_duration': total_duration,
            'num_scenes': num_scenes,
            'scenes': scenes,
            'audio_track': config.music_style if config.include_audio else None,
            'style_guide': {
                'color_palette': config.color_scheme,
                'mood': config.mood,
                'transitions': config.transition_style
            },
            'platform_optimization': self.platform_specs.get(config.platform, {})
        }
        
        return video_plan

    async def _generate_video_by_type(
        self,
        video_plan: Dict[str, Any],
        config: VideoConfig,
        context: ContentGenerationContext
    ) -> bytes:
        """Generate video based on specific type"""
        
        video_type = config.video_type.value
        
        # Select appropriate generation method
        if video_type == 'short_form':
            return await self._generate_short_form_video(video_plan, config)
        elif video_type == 'long_form':
            return await self._generate_long_form_video(video_plan, config)
        elif video_type == 'marketing':
            return await self._generate_marketing_video(video_plan, config)
        elif video_type == 'product_demo':
            return await self._generate_product_demo(video_plan, config)
        elif video_type == 'animation':
            return await self._generate_animation(video_plan, config)
        elif video_type == 'live_streaming':
            return await self._generate_streaming_content(video_plan, config)
        elif video_type == 'video_editing':
            return await self._edit_video(video_plan, config, context)
        else:
            return await self._generate_short_form_video(video_plan, config)  # Default fallback

    async def _generate_short_form_video(self, video_plan: Dict[str, Any], config: VideoConfig) -> bytes:
        """Generate short-form vertical video"""
        return await self._mock_generate_video(video_plan, "short_form", config)

    async def _generate_long_form_video(self, video_plan: Dict[str, Any], config: VideoConfig) -> bytes:
        """Generate long-form horizontal video"""
        return await self._mock_generate_video(video_plan, "long_form", config)

    async def _generate_marketing_video(self, video_plan: Dict[str, Any], config: VideoConfig) -> bytes:
        """Generate marketing/promotional video"""
        return await self._mock_generate_video(video_plan, "marketing", config)

    async def _generate_product_demo(self, video_plan: Dict[str, Any], config: VideoConfig) -> bytes:
        """Generate product demonstration video"""
        return await self._mock_generate_video(video_plan, "product_demo", config)

    async def _generate_animation(self, video_plan: Dict[str, Any], config: VideoConfig) -> bytes:
        """Generate animated video"""
        return await self._mock_generate_video(video_plan, "animation", config)

    async def _generate_streaming_content(self, video_plan: Dict[str, Any], config: VideoConfig) -> bytes:
        """Generate live streaming overlays/content"""
        return await self._mock_generate_video(video_plan, "live_streaming", config)

    async def _edit_video(self, video_plan: Dict[str, Any], config: VideoConfig, context: ContentGenerationContext) -> bytes:
        """Edit existing video content"""
        return await self._mock_generate_video(video_plan, "video_editing", config)

    async def _mock_generate_video(
        self, 
        video_plan: Dict[str, Any], 
        video_type: str, 
        config: VideoConfig
    ) -> bytes:
        """Mock video generation for development/testing"""
        # Simulate processing time based on duration
        processing_time = min(config.duration * 0.1, 5.0)  # Max 5 seconds for testing
        await asyncio.sleep(processing_time)
        
        # Create mock video metadata as bytes
        mock_video_data = {
            'type': video_type,
            'duration': config.duration,
            'quality': config.quality.value,
            'format': config.format.value,
            'scenes': len(video_plan.get('scenes', [])),
            'generated_at': datetime.utcnow().isoformat(),
            'title': video_plan.get('title', 'Generated Video'),
            'file_size_estimate': config.duration * 1024 * 1024  # ~1MB per second estimate
        }
        
        # Convert to bytes (mock video file)
        mock_video_bytes = json.dumps(mock_video_data).encode('utf-8')
        
        # Pad with additional data to simulate realistic file size
        padding_size = max(0, mock_video_data['file_size_estimate'] - len(mock_video_bytes))
        mock_video_bytes += b'0' * min(padding_size, 10000)  # Limit padding for testing
        
        self.logger.info(f"Generated {video_type} video ({len(mock_video_bytes)} bytes) - Duration: {config.duration}s")
        return mock_video_bytes

    async def _post_process_video(
        self,
        video_data: bytes,
        config: VideoConfig
    ) -> bytes:
        """Post-process generated video"""
        # In production, this would apply compression, encoding optimization, etc.
        processed_data = video_data
        
        # Mock post-processing based on configuration
        if config.platform in self.platform_specs:
            # Would apply platform-specific optimizations
            pass
        
        if config.include_subtitles:
            # Would add subtitle tracks
            pass
        
        self.logger.info(f"Post-processed video ({len(processed_data)} bytes)")
        return processed_data

    async def _extract_video_metadata(self, video_data: bytes) -> Dict[str, Any]:
        """Extract metadata from video"""
        try:
            # Mock metadata extraction - in production would use FFprobe or similar
            return {
                'codec': 'h264',
                'bitrate': '2000kbps',
                'color_space': 'yuv420p',
                'audio_codec': 'aac',
                'audio_bitrate': '128kbps',
                'thumbnail_count': 3,
                'encoding_time_seconds': 1.5
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract video metadata: {e}")
            return {}

    def _generate_video_title(self, prompt: str, config: VideoConfig) -> str:
        """Generate appropriate title for video"""
        # Simple title generation based on prompt and type
        type_prefixes = {
            'short_form': 'Quick',
            'long_form': 'Complete Guide:',
            'marketing': 'Discover',
            'product_demo': 'How to use',
            'animation': 'Animated',
            'live_streaming': 'Live',
            'video_editing': 'Edited'
        }
        
        prefix = type_prefixes.get(config.video_type.value, '')
        title = f"{prefix} {prompt}".strip()
        
        # Limit title length
        return title[:60] + '...' if len(title) > 60 else title

    def _get_resolution_from_quality(self, quality: VideoQuality) -> str:
        """Get resolution string from quality enum"""
        quality_map = {
            VideoQuality.LOW: '854x480',
            VideoQuality.MEDIUM: '1280x720',
            VideoQuality.HIGH: '1920x1080',
            VideoQuality.ULTRA: '3840x2160'
        }
        return quality_map.get(quality, '1920x1080')

    def _initialize_platform_specs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific video specifications"""
        return {
            'tiktok': {
                'aspect_ratio': '9:16',
                'max_duration': 180,
                'recommended_fps': 30,
                'format': 'mp4',
                'style_hints': ['vertical', 'engaging', 'quick cuts']
            },
            'instagram': {
                'reels': {
                    'aspect_ratio': '9:16',
                    'max_duration': 90,
                    'recommended_fps': 30
                },
                'feed': {
                    'aspect_ratio': '1:1',
                    'max_duration': 60,
                    'recommended_fps': 30
                }
            },
            'youtube': {
                'shorts': {
                    'aspect_ratio': '9:16',
                    'max_duration': 60,
                    'recommended_fps': 30
                },
                'regular': {
                    'aspect_ratio': '16:9',
                    'max_duration': 43200,  # 12 hours
                    'recommended_fps': 60
                }
            },
            'facebook': {
                'aspect_ratio': '16:9',
                'max_duration': 7200,  # 2 hours
                'recommended_fps': 30,
                'format': 'mp4'
            },
            'linkedin': {
                'aspect_ratio': '16:9',
                'max_duration': 600,  # 10 minutes
                'recommended_fps': 30,
                'style_hints': ['professional', 'educational']
            },
            'twitter': {
                'aspect_ratio': '16:9',
                'max_duration': 140,
                'recommended_fps': 30,
                'format': 'mp4'
            }
        }

    def _initialize_video_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize video templates for each type"""
        return {
            'short_form': {
                'scene_duration': 3,
                'default_scene_type': 'quick_cut',
                'visual_elements': ['dynamic_text', 'transitions', 'effects'],
                'effects': ['zoom', 'fade', 'slide']
            },
            'long_form': {
                'scene_duration': 10,
                'default_scene_type': 'talking_head',
                'visual_elements': ['title_card', 'b_roll', 'graphics'],
                'effects': ['fade', 'cut', 'wipe']
            },
            'marketing': {
                'scene_duration': 5,
                'default_scene_type': 'product_focus',
                'visual_elements': ['call_to_action', 'brand_logo', 'product_shots'],
                'effects': ['zoom', 'highlight', 'glow']
            },
            'product_demo': {
                'scene_duration': 8,
                'default_scene_type': 'demonstration',
                'visual_elements': ['step_by_step', 'annotations', 'close_ups'],
                'effects': ['highlight', 'zoom', 'callout']
            },
            'animation': {
                'scene_duration': 4,
                'default_scene_type': 'animated_sequence',
                'visual_elements': ['characters', 'motion_graphics', 'effects'],
                'effects': ['morph', 'scale', 'rotate']
            },
            'live_streaming': {
                'scene_duration': 60,
                'default_scene_type': 'live_feed',
                'visual_elements': ['overlays', 'chat_display', 'alerts'],
                'effects': ['fade_in', 'slide_in', 'pulse']
            },
            'video_editing': {
                'scene_duration': 6,
                'default_scene_type': 'edited_sequence',
                'visual_elements': ['cuts', 'transitions', 'color_grading'],
                'effects': ['cut', 'fade', 'dissolve']
            }
        }

    def _supports_content_type(self, content_type: str) -> bool:
        """Check if generator supports the specified content type"""
        return content_type in ['video', 'visual', 'motion', 'animation']

    async def _release_model_resources(self) -> None:
        """Release model-specific resources"""
        # Clean up model resources
        if hasattr(self, 'models'):
            self.models.clear()
        
        self.logger.info("Video generator resources released")

    # Additional utility methods for video generation

    def get_supported_video_types(self) -> List[str]:
        """Get list of supported video types"""
        return [video_type.value for video_type in VideoType]

    def get_supported_formats(self) -> List[str]:
        """Get list of supported video formats"""
        return self.supported_formats

    def get_platform_specifications(self) -> Dict[str, Dict[str, Any]]:
        """Get platform-specific video specifications"""
        return self.platform_specs

    async def create_video_thumbnail(
        self,
        video_data: bytes,
        timestamp_seconds: float = 1.0
    ) -> bytes:
        """Extract thumbnail from video at specified timestamp"""
        try:
            # Mock thumbnail creation - in production would use FFmpeg
            await asyncio.sleep(0.1)
            
            # Return mock image data (1x1 pixel PNG)
            mock_thumbnail = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            )
            
            self.logger.info(f"Created thumbnail at {timestamp_seconds}s")
            return mock_thumbnail
            
        except Exception as e:
            self.logger.error(f"Thumbnail creation failed: {e}")
            raise

    async def add_subtitles(
        self,
        video_data: bytes,
        subtitle_text: str,
        language: str = 'en'
    ) -> bytes:
        """Add subtitles to video"""
        try:
            # Mock subtitle addition - in production would embed SRT/VTT
            await asyncio.sleep(0.2)
            
            self.logger.info(f"Added {language} subtitles to video")
            return video_data  # Mock - return same data
            
        except Exception as e:
            self.logger.error(f"Subtitle addition failed: {e}")
            raise

    async def compress_video(
        self,
        video_data: bytes,
        target_size_mb: float
    ) -> bytes:
        """Compress video to target file size"""
        try:
            # Mock compression - in production would use FFmpeg with appropriate settings
            await asyncio.sleep(0.3)
            
            compression_ratio = target_size_mb / (len(video_data) / (1024 * 1024))
            compressed_size = int(len(video_data) * min(compression_ratio, 1.0))
            
            # Simulate compression by truncating data (mock)
            compressed_data = video_data[:compressed_size]
            
            self.logger.info(f"Compressed video to {target_size_mb}MB")
            return compressed_data
            
        except Exception as e:
            self.logger.error(f"Video compression failed: {e}")
            raise

    async def merge_videos(
        self,
        video_list: List[bytes],
        transition_style: str = 'cut'
    ) -> bytes:
        """Merge multiple videos into one"""
        try:
            # Mock video merging - in production would use FFmpeg
            await asyncio.sleep(0.5)
            
            # Simple concatenation for mock
            merged_data = b''.join(video_list)
            
            self.logger.info(f"Merged {len(video_list)} videos with {transition_style} transitions")
            return merged_data
            
        except Exception as e:
            self.logger.error(f"Video merging failed: {e}")
            raise

    async def extract_audio(self, video_data: bytes) -> bytes:
        """Extract audio track from video"""
        try:
            # Mock audio extraction - in production would use FFmpeg
            await asyncio.sleep(0.1)
            
            # Return mock audio data (simplified WAV header)
            mock_audio = b'RIFF\x24\x00\x00\x00WAVEfmt '
            
            self.logger.info("Extracted audio from video")
            return mock_audio
            
        except Exception as e:
            self.logger.error(f"Audio extraction failed: {e}")
            raise

    async def batch_generate_videos(
        self,
        prompts: List[str],
        config: VideoConfig
    ) -> List[Dict[str, Any]]:
        """Generate multiple videos in batch"""
        results = []
        
        # Process in batches to avoid overwhelming the system
        batch_size = min(self.max_concurrent_generations, len(prompts))
        
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i + batch_size]
            
            # Generate batch concurrently
            tasks = []
            for prompt in batch_prompts:
                video_plan = await self._build_video_plan(prompt, config, None)
                tasks.append(self._generate_video_by_type(video_plan, config, None))
            
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Batch generation failed for prompt {i+j}: {result}")
                        continue
                    
                    metadata = await self._extract_video_metadata(result)
                    
                    results.append({
                        'id': i + j,
                        'data': result,
                        'prompt': batch_prompts[j],
                        'success': True,
                        'duration': config.duration,
                        'metadata': metadata
                    })
                    
            except Exception as e:
                self.logger.error(f"Batch processing failed: {e}")
        
        return results