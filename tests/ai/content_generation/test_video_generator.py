# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Video Generator Tests

Comprehensive tests for the VideoGenerator class that handles
AI-powered video content creation and editing.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
import tempfile
import os

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.video_generator import (
    VideoContentGenerator, 
    VideoConfig, 
    VideoFormat, 
    VideoQuality, 
    VideoStyle
)
from ai.content_generation.content_models import ContentType, Platform


class TestVideoGenerator:
    """Test suite for VideoGenerator"""
    
    @pytest.fixture
    def generator(self):
        """
Create a video generator instance"""
        config = {'test': 'value'}  # Minimal config for testing
        return VideoContentGenerator(config)
    
    @pytest.fixture
    def sample_script(self):
        """
Create sample video script"""
        return {
            "title": "AI Technology Explained",
            "duration": 60,
            "scenes": [
                {
                    "id": "intro",
                    "duration": 10,
                    "text": "Welcome to AI Technology Explained",
                    "visuals": ["title_card", "tech_background"],
                    "audio": "intro_music.mp3"
                },
                {
                    "id": "main_content",
                    "duration": 40,
                    "text": "Artificial Intelligence is transforming our world...",
                    "visuals": ["ai_animation", "data_visualization"],
                    "audio": "narrator_voice.wav"
                },
                {
                    "id": "conclusion",
                    "duration": 10,
                    "text": "Thank you for watching",
                    "visuals": ["outro_card", "subscribe_animation"],
                    "audio": "outro_music.mp3"
                }
            ]
        }
    
    @pytest.fixture
    def video_config(self):
        """Create sample video configuration"""
        return VideoConfig(
            resolution="1920x1080",
            fps=30,
            quality=VideoQuality.HIGH,
            format=VideoFormat.MP4,
            style=VideoStyle.PROFESSIONAL,
            duration=60,
            aspect_ratio="16:9"
        )
    
    def test_generator_initialization(self, generator):
        """Test video generator initialization"""
        assert generator is not None
        assert hasattr(generator, 'supported_formats')
        assert hasattr(generator, 'supported_resolutions')
        assert hasattr(generator, 'max_duration')
        assert hasattr(generator, 'video_models')
    
    @pytest.mark.asyncio
    async def test_script_to_video_generation(self, generator, sample_script, video_config):
        """
Test generating video from script"""
        with patch.object(generator, '_render_video') as mock_render:
            mock_render.return_value = {
                "success": True,
                "video_path": "/tmp/generated_video.mp4",
                "duration": 60.0,
                "file_size": 15728640,  # 15MB
                "resolution": "1920x1080",
                "fps": 30
            }
            
            result = await generator.generate_from_script(
                script=sample_script,
                config=video_config,
                auto_generate_visuals=True
            )
            
            assert result["success"] is True
            assert result["duration"] == 60.0
            assert result["resolution"] == "1920x1080"
            assert "video_path" in result
    
    @pytest.mark.asyncio
    async def test_ai_visual_generation(self, generator):
        """Test AI-powered visual generation"""
        scene_description = "A futuristic cityscape with flying cars and neon lights"
        
        with patch.object(generator, '_generate_ai_visuals') as mock_visuals:
            mock_visuals.return_value = {
                "success": True,
                "generated_images": [
                    {"id": "img_001", "path": "/tmp/cityscape_001.jpg", "style": "futuristic"},
                    {"id": "img_002", "path": "/tmp/cityscape_002.jpg", "style": "futuristic"}
                ],
                "animation_frames": 120,
                "generation_time": 45.2
            }
            
            result = await generator.generate_scene_visuals(
                description=scene_description,
                style=VideoStyle.FUTURISTIC,
                duration=4.0,
                animation_type="smooth_pan"
            )
            
            assert result["success"] is True
            assert len(result["generated_images"]) == 2
            assert result["animation_frames"] == 120
    
    @pytest.mark.asyncio
    async def test_template_based_video_creation(self, generator):
        """Test template-based video creation"""
        template_id = "social_media_promo"
        content_data = {
            "title": "New Product Launch",
            "subtitle": "Revolutionary AI Technology",
            "description": "Transform your workflow with our AI solution",
            "logo": "/assets/company_logo.png",
            "colors": {"primary": "#FF6B35", "secondary": "#F7931E"}
        }
        
        with patch.object(generator, '_apply_template') as mock_template:
            mock_template.return_value = {
                "success": True,
                "video_path": "/tmp/templated_video.mp4",
                "template_applied": template_id,
                "customizations": len(content_data),
                "render_time": 23.5
            }
            
            result = await generator.create_from_template(
                template_id=template_id,
                content_data=content_data,
                platform=Platform.INSTAGRAM,
                custom_duration=15
            )
            
            assert result["success"] is True
            assert result["template_applied"] == template_id
            assert result["customizations"] == len(content_data)
    
    @pytest.mark.asyncio
    async def test_multi_platform_optimization(self, generator, video_config):
        """Test multi-platform video optimization"""
        base_video = "/tmp/master_video.mp4"
        platforms = [Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK, Platform.LINKEDIN]
        
        with patch.object(generator, '_optimize_for_platform') as mock_optimize:
            def platform_optimization(video_path, platform, config):
                platform_specs = {
                    Platform.YOUTUBE: {"resolution": "1920x1080", "max_duration": 600},
                    Platform.INSTAGRAM: {"resolution": "1080x1080", "max_duration": 60},
                    Platform.TIKTOK: {"resolution": "1080x1920", "max_duration": 60},
                    Platform.LINKEDIN: {"resolution": "1920x1080", "max_duration": 600}
                }
                spec = platform_specs[platform]
                return {
                    "success": True,
                    "optimized_video": f"/tmp/{platform.value}_optimized.mp4",
                    "resolution": spec["resolution"],
                    "max_duration": spec["max_duration"],
                    "platform": platform.value
                }
            
            mock_optimize.side_effect = platform_optimization
            
            results = await generator.optimize_for_platforms(
                video_path=base_video,
                platforms=platforms,
                config=video_config
            )
            
            assert len(results) == 4
            for platform, result in results.items():
                assert result["success"] is True
                assert result["platform"] == platform
    
    @pytest.mark.asyncio
    async def test_real_time_video_effects(self, generator):
        """Test real-time video effects application"""
        video_path = "/tmp/source_video.mp4"
        effects = [
            {"type": "color_grading", "intensity": 0.7, "style": "cinematic"},
            {"type": "motion_blur", "strength": 0.5},
            {"type": "particle_system", "effect": "floating_particles"},
            {"type": "text_overlay", "text": "AI Generated", "position": "bottom_right"}
        ]
        
        with patch.object(generator, '_apply_effects') as mock_effects:
            mock_effects.return_value = {
                "success": True,
                "processed_video": "/tmp/effects_video.mp4",
                "effects_applied": len(effects),
                "processing_time": 34.8,
                "quality_enhancement": 15.2
            }
            
            result = await generator.apply_real_time_effects(
                video_path=video_path,
                effects=effects,
                preview_mode=False
            )
            
            assert result["success"] is True
            assert result["effects_applied"] == 4
            assert result["quality_enhancement"] == 15.2
    
    @pytest.mark.asyncio
    async def test_automatic_scene_detection(self, generator):
        """Test automatic scene detection and segmentation"""
        video_path = "/tmp/long_video.mp4"
        
        with patch.object(generator, '_detect_scenes') as mock_detection:
            mock_detection.return_value = {
                "success": True,
                "scenes": [
                    {"start": 0.0, "end": 15.5, "type": "intro", "confidence": 0.92},
                    {"start": 15.5, "end": 45.2, "type": "main_content", "confidence": 0.89},
                    {"start": 45.2, "end": 60.0, "type": "conclusion", "confidence": 0.94}
                ],
                "total_scenes": 3,
                "detection_confidence": 0.92
            }
            
            result = await generator.detect_and_segment_scenes(
                video_path=video_path,
                min_scene_duration=5.0,
                confidence_threshold=0.8
            )
            
            assert result["success"] is True
            assert result["total_scenes"] == 3
            assert result["detection_confidence"] == 0.92
    
    @pytest.mark.asyncio
    async def test_audio_video_synchronization(self, generator):
        """Test audio-video synchronization"""
        video_path = "/tmp/video_track.mp4"
        audio_path = "/tmp/audio_track.wav"
        
        with patch.object(generator, '_synchronize_audio') as mock_sync:
            mock_sync.return_value = {
                "success": True,
                "synchronized_video": "/tmp/synced_video.mp4",
                "sync_offset": 0.025,  # 25ms offset correction
                "sync_quality": 0.98,
                "audio_enhanced": True
            }
            
            result = await generator.synchronize_audio_video(
                video_path=video_path,
                audio_path=audio_path,
                auto_sync=True,
                enhance_audio=True
            )
            
            assert result["success"] is True
            assert result["sync_quality"] == 0.98
            assert result["audio_enhanced"] is True
    
    @pytest.mark.asyncio
    async def test_batch_video_processing(self, generator, video_config):
        """Test batch video processing"""
        video_jobs = [
            {"id": "job_001", "script": {"title": "Video 1"}, "template": "template_a"},
            {"id": "job_002", "script": {"title": "Video 2"}, "template": "template_b"},
            {"id": "job_003", "script": {"title": "Video 3"}, "template": "template_c"}
        ]
        
        with patch.object(generator, '_process_video_job') as mock_process:
            mock_process.return_value = {
                "success": True,
                "video_path": "/tmp/batch_video.mp4",
                "processing_time": 15.3
            }
            
            results = await generator.process_batch(
                jobs=video_jobs,
                config=video_config,
                parallel_processing=True,
                max_concurrent=2
            )
            
            assert len(results) == 3
            for result in results:
                assert result["success"] is True
                assert "video_path" in result
    
    @pytest.mark.asyncio
    async def test_live_streaming_preparation(self, generator):
        """Test live streaming preparation"""
        video_content = {
            "intro_video": "/tmp/intro.mp4",
            "main_content": "/tmp/presentation.mp4",
            "outro_video": "/tmp/outro.mp4",
            "overlay_graphics": ["/tmp/logo.png", "/tmp/watermark.png"]
        }
        
        stream_config = {
            "resolution": "1920x1080",
            "bitrate": 4000,
            "fps": 30,
            "codec": "h264",
            "streaming_protocol": "RTMP"
        }
        
        with patch.object(generator, '_prepare_live_stream') as mock_stream:
            mock_stream.return_value = {
                "success": True,
                "stream_ready": True,
                "stream_url": "rtmp://stream.example.com/live",
                "stream_key": "sk_abc123xyz",
                "estimated_bitrate": 4200
            }
            
            result = await generator.prepare_live_stream(
                content=video_content,
                stream_config=stream_config,
                test_connection=True
            )
            
            assert result["success"] is True
            assert result["stream_ready"] is True
            assert "stream_url" in result
    
    @pytest.mark.asyncio
    async def test_ai_content_analysis(self, generator):
        """Test AI-powered content analysis"""
        video_path = "/tmp/analysis_video.mp4"
        
        with patch.object(generator, '_analyze_content') as mock_analysis:
            mock_analysis.return_value = {
                "success": True,
                "content_summary": "Technology presentation about AI",
                "detected_objects": ["laptop", "charts", "person"],
                "scene_types": ["presentation", "talking_head"],
                "engagement_score": 8.5,
                "quality_metrics": {
                    "visual_quality": 9.2,
                    "audio_quality": 8.8,
                    "content_relevance": 9.0
                },
                "suggested_improvements": [
                    "Add more visual transitions",
                    "Improve audio levels"
                ]
            }
            
            result = await generator.analyze_video_content(
                video_path=video_path,
                analysis_type="comprehensive",
                include_suggestions=True
            )
            
            assert result["success"] is True
            assert result["engagement_score"] == 8.5
            assert len(result["suggested_improvements"]) == 2
    
    @pytest.mark.asyncio
    async def test_subtitle_generation(self, generator):
        """Test automatic subtitle generation"""
        video_path = "/tmp/subtitle_video.mp4"
        
        with patch.object(generator, '_generate_subtitles') as mock_subtitles:
            mock_subtitles.return_value = {
                "success": True,
                "subtitles": [
                    {"start": 0.0, "end": 3.5, "text": "Welcome to our AI presentation"},
                    {"start": 3.5, "end": 7.2, "text": "Today we'll explore machine learning"},
                    {"start": 7.2, "end": 11.0, "text": "And its applications in modern technology"}
                ],
                "subtitle_file": "/tmp/subtitles.srt",
                "languages": ["en", "es", "fr"],
                "accuracy": 0.94
            }
            
            result = await generator.generate_subtitles(
                video_path=video_path,
                languages=["en", "es", "fr"],
                auto_translate=True,
                format="srt"
            )
            
            assert result["success"] is True
            assert len(result["subtitles"]) == 3
            assert len(result["languages"]) == 3
            assert result["accuracy"] == 0.94
    
    @pytest.mark.asyncio
    async def test_thumbnail_generation(self, generator):
        """Test automatic thumbnail generation"""
        video_path = "/tmp/thumbnail_video.mp4"
        
        with patch.object(generator, '_generate_thumbnails') as mock_thumbnails:
            mock_thumbnails.return_value = {
                "success": True,
                "thumbnails": [
                    {"timestamp": 5.0, "path": "/tmp/thumb_1.jpg", "score": 9.2},
                    {"timestamp": 15.5, "path": "/tmp/thumb_2.jpg", "score": 8.8},
                    {"timestamp": 25.0, "path": "/tmp/thumb_3.jpg", "score": 9.5}
                ],
                "best_thumbnail": "/tmp/thumb_3.jpg",
                "selection_criteria": "highest_engagement_potential"
            }
            
            result = await generator.generate_thumbnails(
                video_path=video_path,
                count=3,
                selection_method="ai_powered",
                custom_text="AI Technology"
            )
            
            assert result["success"] is True
            assert len(result["thumbnails"]) == 3
            assert result["best_thumbnail"] == "/tmp/thumb_3.jpg"
    
    @pytest.mark.asyncio
    async def test_video_compression_optimization(self, generator):
        """Test intelligent video compression"""
        video_path = "/tmp/large_video.mp4"
        
        with patch.object(generator, '_optimize_compression') as mock_compression:
            mock_compression.return_value = {
                "success": True,
                "compressed_video": "/tmp/compressed_video.mp4",
                "original_size": 104857600,  # 100MB
                "compressed_size": 31457280,  # 30MB
                "compression_ratio": 0.3,
                "quality_retained": 0.95,
                "processing_time": 45.2
            }
            
            result = await generator.optimize_compression(
                video_path=video_path,
                target_size="30MB",
                quality_threshold=0.9,
                adaptive_bitrate=True
            )
            
            assert result["success"] is True
            assert result["compression_ratio"] == 0.3
            assert result["quality_retained"] == 0.95
    
    @pytest.mark.asyncio
    async def test_interactive_video_elements(self, generator):
        """Test interactive video elements creation"""
        video_path = "/tmp/interactive_video.mp4"
        
        interactive_elements = [
            {
                "type": "clickable_button",
                "timestamp": 10.0,
                "position": {"x": 100, "y": 200},
                "action": "open_link",
                "data": "https://example.com"
            },
            {
                "type": "quiz_question",
                "timestamp": 30.0,
                "question": "What is AI?",
                "options": ["Artificial Intelligence", "Advanced Internet", "Automated Interface"],
                "correct_answer": 0
            }
        ]
        
        with patch.object(generator, '_add_interactive_elements') as mock_interactive:
            mock_interactive.return_value = {
                "success": True,
                "interactive_video": "/tmp/interactive_output.mp4",
                "elements_added": len(interactive_elements),
                "engagement_features": ["clickable_buttons", "quiz_questions"],
                "metadata_file": "/tmp/interactive_metadata.json"
            }
            
            result = await generator.add_interactive_elements(
                video_path=video_path,
                elements=interactive_elements,
                platform_compatibility="web"
            )
            
            assert result["success"] is True
            assert result["elements_added"] == 2
            assert "quiz_questions" in result["engagement_features"]
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, generator, video_config):
        """Test error handling and recovery mechanisms"""
        invalid_script = {"title": "Test", "scenes": []}  # Invalid empty scenes
        
        with patch.object(generator, '_render_video') as mock_render:
            # Test rendering failure with recovery
            mock_render.side_effect = [
                Exception("Rendering failed: insufficient memory"),
                {
                    "success": True,
                    "video_path": "/tmp/recovered_video.mp4",
                    "recovery_method": "reduced_quality_fallback"
                }
            ]
            
            result = await generator.generate_from_script(
                script=invalid_script,
                config=video_config,
                enable_recovery=True,
                fallback_quality=VideoQuality.MEDIUM
            )
            
            # Should succeed with fallback
            assert result["success"] is True
            assert result["recovery_method"] == "reduced_quality_fallback"
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, generator, video_config):
        """Test performance monitoring and optimization"""
        script = {"title": "Performance Test", "scenes": [{"id": "test", "duration": 10}]}
        
        with patch.object(generator, '_render_video') as mock_render:
            mock_render.return_value = {
                "success": True,
                "video_path": "/tmp/performance_video.mp4",
                "performance_metrics": {
                    "render_time": 23.5,
                    "memory_peak": 512.7,
                    "cpu_usage": 85.2,
                    "gpu_usage": 92.1,
                    "frames_per_second": 28.5
                }
            }
            
            result = await generator.generate_from_script(
                script=script,
                config=video_config,
                monitor_performance=True
            )
            
            assert result["success"] is True
            assert "performance_metrics" in result
            assert result["performance_metrics"]["render_time"] == 23.5


class TestVideoConfig:
    """Test suite for VideoConfig model"""
    
    def test_video_config_creation(self):
        """
Test video configuration creation"""
        config = VideoConfig(
            resolution="1920x1080",
            fps=30,
            quality=VideoQuality.HIGH,
            format=VideoFormat.MP4,
            style=VideoStyle.CINEMATIC,
            duration=120,
            aspect_ratio="16:9"
        )
        
        assert config.resolution == "1920x1080"
        assert config.fps == 30
        assert config.quality == VideoQuality.HIGH
        assert config.format == VideoFormat.MP4
        assert config.style == VideoStyle.CINEMATIC
        assert config.duration == 120
        assert config.aspect_ratio == "16:9"
    
    def test_video_config_validation(self):
        """Test video configuration validation"""
        # Test invalid resolution
        with pytest.raises(Exception):  # Adjust based on actual validation
            VideoConfig(
                resolution="invalid_resolution",
                fps=30,
                quality=VideoQuality.HIGH,
                format=VideoFormat.MP4
            )


class TestVideoEnums:
    """Test suite for video-related enums"""
    
    def test_video_format_enum(self):
        """
Test VideoFormat enum values"""
        assert VideoFormat.MP4.value == "mp4"
        assert VideoFormat.AVI.value == "avi"
        assert VideoFormat.MOV.value == "mov"
        assert VideoFormat.WEBM.value == "webm"
    
    def test_video_quality_enum(self):
        """Test VideoQuality enum values"""
        assert VideoQuality.LOW.value == "low"
        assert VideoQuality.MEDIUM.value == "medium"
        assert VideoQuality.HIGH.value == "high"
        assert VideoQuality.ULTRA.value == "ultra"
    
    def test_video_style_enum(self):
        """Test VideoStyle enum values"""
        assert VideoStyle.PROFESSIONAL.value == "professional"
        assert VideoStyle.CASUAL.value == "casual"
        assert VideoStyle.CINEMATIC.value == "cinematic"
        assert VideoStyle.ANIMATED.value == "animated"


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
