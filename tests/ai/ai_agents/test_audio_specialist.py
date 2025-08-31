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

"""Comprehensive Tests for AudioSpecialistAgent

Industrial-grade testing for audio processing, voice synthesis, music generation,
audio enhancement, and podcast production capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import logging
import numpy as np
import io
from pathlib import Path

from ai.ai_agents import (
    AudioSpecialistAgent,
    AgentConfiguration,
    AgentCapability
)

logger = logging.getLogger(__name__)


class TestableAudioSpecialistAgent(AudioSpecialistAgent):
    """Extended audio specialist agent for testing"""
    
    async def generate_synthetic_audio(self, duration: float, format: str = "wav") -> bytes:
        """Generate synthetic audio for testing"""
        sample_rate = 44100
        samples = int(duration * sample_rate)
        audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples))
        return audio_data.astype(np.float32).tobytes()
    
    async def create_test_voice_sample(self, text: str, voice_type: str = "natural") -> Dict[str, Any]:
        """Create test voice sample"""
        audio_data = await self.generate_synthetic_audio(len(text) * 0.1)
        return {
            "audio_data": audio_data,
            "format": "wav",
            "sample_rate": 44100,
            "duration": len(text) * 0.1,
            "voice_characteristics": {
                "gender": "neutral",
                "age": "adult",
                "accent": "neutral",
                "emotion": "neutral"
            }
        }


class TestAudioSpecialistAgent:
    """Comprehensive test suite for AudioSpecialistAgent"""
    
    @pytest.fixture
    def audio_config(self) -> AgentConfiguration:
        """Audio specialist agent configuration"""
        return AgentConfiguration(
            agent_id="audio_specialist_test",
            agent_name="Test Audio Specialist Agent",
            capabilities={
                AgentCapability.audio_processing,
                AgentCapability.voice_synthesis,
                AgentCapability.music_generation,
                AgentCapability.audio_enhancement,
                AgentCapability.podcast_production,
                AgentCapability.sound_design,
                AgentCapability.audio_transcription,
                AgentCapability.audio_analysis
            },
            max_concurrent_tasks=5,
            default_timeout=120,
            custom_settings={
                "high_quality_processing": True,
                "real_time_capabilities": True,
                "multi_format_support": True,
                "ai_voice_synthesis": True,
                "advanced_audio_effects": True,
                "noise_reduction": True,
                "audio_mastering": True,
                "voice_cloning": True,
                "spatial_audio": True
            }
        )
    
    @pytest.fixture
    async def audio_agent(self, audio_config) -> TestableAudioSpecialistAgent:
        """Initialized audio specialist agent"""
        agent = TestableAudioSpecialistAgent(audio_config)
        await agent.initialize()
        
        yield agent
        
        await agent.shutdown()
    
    async def test_agent_initialization(self, audio_config):
        """Test audio specialist agent initialization"""
        agent = TestableAudioSpecialistAgent(audio_config)
        
        # Before initialization
        assert not agent.initialized
        assert agent.status.name == "CREATED"
        
        # Initialize
        result = await agent.initialize()
        
        # After initialization
        assert result is True
        assert agent.initialized
        assert agent.status.name == "READY"
        
        # Verify capabilities
        assert agent.has_capability(AgentCapability.audio_processing)
        assert agent.has_capability(AgentCapability.voice_synthesis)
        assert agent.has_capability(AgentCapability.music_generation)
        assert agent.has_capability(AgentCapability.audio_enhancement)
        
        # Verify settings
        assert agent.get_setting("high_quality_processing") is True
        assert agent.get_setting("ai_voice_synthesis") is True
        assert agent.get_setting("voice_cloning") is True
        
        await agent.shutdown()
    
    async def test_voice_synthesis(self, audio_agent):
        """Test AI voice synthesis capabilities"""
        synthesis_request = {
            "task_type": "voice_synthesis",
            "text": "Welcome to our AI influencer platform. This is a test of our voice synthesis technology.",
            "voice_settings": {
                "voice_type": "natural_female",
                "age": "young_adult",
                "emotion": "enthusiastic",
                "speaking_rate": 1.0,
                "pitch": 0.0,
                "accent": "american"
            },
            "output_format": {
                "format": "wav",
                "sample_rate": 44100,
                "bit_depth": 16,
                "quality": "high"
            },
            "advanced_options": {
                "add_breathing": True,
                "natural_pauses": True,
                "emotional_inflection": True,
                "prosody_control": True
            }
        }
        
        result = await audio_agent.process_task(synthesis_request)
        
        # Verify successful synthesis
        assert result["success"] is True
        assert "audio_output" in result
        
        audio_output = result["audio_output"]
        assert "audio_data" in audio_output
        assert "metadata" in audio_output
        assert "quality_metrics" in audio_output
        
        # Verify metadata
        metadata = audio_output["metadata"]
        assert "duration" in metadata
        assert "file_size" in metadata
        assert "format" in metadata
        assert "sample_rate" in metadata
        assert "voice_characteristics" in metadata
        
        # Verify quality metrics
        quality = audio_output["quality_metrics"]
        assert "clarity_score" in quality
        assert "naturalness_score" in quality
        assert "intelligibility" in quality
        assert "emotional_accuracy" in quality
        
        # Verify voice characteristics
        voice_chars = metadata["voice_characteristics"]
        assert voice_chars["voice_type"] == "natural_female"
        assert voice_chars["emotion"] == "enthusiastic"
    
    async def test_voice_cloning(self, audio_agent):
        """Test voice cloning capabilities"""
        cloning_request = {
            "task_type": "voice_cloning",
            "target_voice_samples": [
                {
                    "audio_data": await audio_agent.generate_synthetic_audio(5.0),
                    "transcript": "This is a sample of the target voice for cloning."
                },
                {
                    "audio_data": await audio_agent.generate_synthetic_audio(4.0),
                    "transcript": "Another sample to improve cloning accuracy."
                }
            ],
            "text_to_synthesize": "This is new content using the cloned voice.",
            "cloning_settings": {
                "quality_level": "high",
                "preservation_accuracy": 0.95,
                "include_speech_patterns": True,
                "maintain_emotional_range": True
            }
        }
        
        result = await audio_agent.process_task(cloning_request)
        
        # Verify successful voice cloning
        assert result["success"] is True
        assert "cloned_audio" in result
        assert "cloning_analysis" in result
        
        cloned_audio = result["cloned_audio"]
        assert "audio_data" in cloned_audio
        assert "similarity_score" in cloned_audio
        assert "voice_profile" in cloned_audio
        
        # Verify cloning analysis
        analysis = result["cloning_analysis"]
        assert "voice_characteristics" in analysis
        assert "cloning_quality" in analysis
        assert "recommendations" in analysis
        
        # Verify similarity score is high
        assert cloned_audio["similarity_score"] >= 0.8
    
    async def test_music_generation(self, audio_agent):
        """Test AI music generation capabilities"""
        music_request = {
            "task_type": "music_generation",
            "music_style": "electronic_ambient",
            "duration": 30.0,  # 30 seconds
            "parameters": {
                "tempo": 120,
                "key": "C_major",
                "mood": "uplifting",
                "energy_level": "medium",
                "instruments": ["synthesizer", "pad", "bass", "drums"]
            },
            "structure": {
                "intro": 4,
                "verse": 8,
                "chorus": 8,
                "bridge": 4,
                "outro": 6
            },
            "output_format": {
                "format": "wav",
                "quality": "studio",
                "stems_included": True
            }
        }
        
        result = await audio_agent.process_task(music_request)
        
        # Verify successful music generation
        assert result["success"] is True
        assert "music_output" in result
        
        music_output = result["music_output"]
        assert "master_track" in music_output
        assert "stems" in music_output
        assert "composition_data" in music_output
        assert "analysis" in music_output
        
        # Verify master track
        master = music_output["master_track"]
        assert "audio_data" in master
        assert "duration" in master
        assert master["duration"] >= 29.0  # Allow slight variance
        
        # Verify stems
        stems = music_output["stems"]
        assert "synthesizer" in stems
        assert "bass" in stems
        assert "drums" in stems
        
        # Verify composition data
        composition = music_output["composition_data"]
        assert "chord_progression" in composition
        assert "melody_structure" in composition
        assert "rhythm_pattern" in composition
        
        # Verify analysis
        analysis = music_output["analysis"]
        assert "tempo_detected" in analysis
        assert "key_detected" in analysis
        assert "mood_analysis" in analysis
    
    async def test_podcast_production(self, audio_agent):
        """Test podcast production capabilities"""
        podcast_request = {
            "task_type": "podcast_production",
            "segments": [
                {
                    "type": "intro",
                    "voice_content": "Welcome to the AI Influencer Podcast",
                    "voice_settings": {"voice_type": "professional_male"},
                    "background_music": "upbeat_intro",
                    "duration": 10
                },
                {
                    "type": "content",
                    "voice_content": "Today we're discussing the future of AI content creation",
                    "voice_settings": {"voice_type": "conversational_female"},
                    "effects": ["noise_reduction", "EQ"],
                    "duration": 60
                },
                {
                    "type": "outro",
                    "voice_content": "Thanks for listening, subscribe for more content",
                    "voice_settings": {"voice_type": "professional_male"},
                    "background_music": "fade_out",
                    "duration": 8
                }
            ],
            "production_settings": {
                "target_loudness": -16,  # LUFS
                "normalize_levels": True,
                "add_compression": True,
                "crossfade_segments": True,
                "noise_gate": True
            },
            "output_format": {
                "format": "mp3",
                "bitrate": 320,
                "include_chapters": True
            }
        }
        
        result = await audio_agent.process_task(podcast_request)
        
        # Verify successful podcast production
        assert result["success"] is True
        assert "podcast_output" in result
        
        podcast_output = result["podcast_output"]
        assert "final_audio" in podcast_output
        assert "segments_data" in podcast_output
        assert "production_report" in podcast_output
        assert "chapters" in podcast_output
        
        # Verify final audio
        final_audio = podcast_output["final_audio"]
        assert "audio_data" in final_audio
        assert "total_duration" in final_audio
        assert final_audio["total_duration"] >= 75  # Sum of segments
        
        # Verify segments data
        segments = podcast_output["segments_data"]
        assert len(segments) == 3
        for segment in segments:
            assert "start_time" in segment
            assert "end_time" in segment
            assert "type" in segment
            assert "processing_applied" in segment
        
        # Verify production report
        report = podcast_output["production_report"]
        assert "loudness_analysis" in report
        assert "dynamic_range" in report
        assert "frequency_analysis" in report
        assert "quality_score" in report
        
        # Verify chapters
        chapters = podcast_output["chapters"]
        assert len(chapters) == 3
        for chapter in chapters:
            assert "title" in chapter
            assert "start_time" in chapter
            assert "duration" in chapter
    
    async def test_audio_enhancement(self, audio_agent):
        """Test audio enhancement and restoration"""
        enhancement_request = {
            "task_type": "audio_enhancement",
            "input_audio": await audio_agent.generate_synthetic_audio(10.0),
            "enhancement_types": [
                "noise_reduction",
                "voice_clarity",
                "dynamic_range_compression",
                "EQ_optimization",
                "stereo_widening"
            ],
            "quality_settings": {
                "noise_reduction_strength": 0.8,
                "clarity_enhancement": 0.7,
                "compression_ratio": 3.0,
                "eq_preset": "voice_optimized",
                "stereo_width": 1.2
            },
            "preserve_original": True
        }
        
        result = await audio_agent.process_task(enhancement_request)
        
        # Verify successful enhancement
        assert result["success"] is True
        assert "enhanced_audio" in result
        assert "enhancement_report" in result
        
        enhanced_audio = result["enhanced_audio"]
        assert "audio_data" in enhanced_audio
        assert "before_after_comparison" in enhanced_audio
        
        # Verify enhancement report
        report = result["enhancement_report"]
        assert "improvements_made" in report
        assert "quality_metrics" in report
        assert "processing_chain" in report
        
        # Verify quality metrics
        quality = report["quality_metrics"]
        assert "noise_reduction_db" in quality
        assert "clarity_improvement" in quality
        assert "dynamic_range_change" in quality
        assert "overall_quality_score" in quality
        
        # Verify improvements
        improvements = report["improvements_made"]
        assert len(improvements) >= 3  # Multiple enhancements applied
    
    async def test_sound_design(self, audio_agent):
        """Test sound design and effects creation"""
        sound_design_request = {
            "task_type": "sound_design",
            "sound_type": "ambient_atmosphere",
            "description": "Futuristic tech environment with subtle AI processing sounds",
            "duration": 20.0,
            "parameters": {
                "base_frequency": 440,
                "texture": "smooth_digital",
                "spatial_positioning": "surround",
                "evolution": "gradual_build",
                "mood": "mysterious_tech"
            },
            "layers": [
                {"type": "background_hum", "volume": 0.3},
                {"type": "digital_artifacts", "volume": 0.2},
                {"type": "processing_sounds", "volume": 0.4},
                {"type": "ambient_texture", "volume": 0.5}
            ]
        }
        
        result = await audio_agent.process_task(sound_design_request)
        
        # Verify successful sound design
        assert result["success"] is True
        assert "sound_output" in result
        
        sound_output = result["sound_output"]
        assert "composite_audio" in sound_output
        assert "individual_layers" in sound_output
        assert "design_breakdown" in sound_output
        
        # Verify individual layers
        layers = sound_output["individual_layers"]
        assert len(layers) == 4
        for layer in layers:
            assert "audio_data" in layer
            assert "layer_type" in layer
            assert "volume_level" in layer
        
        # Verify design breakdown
        breakdown = sound_output["design_breakdown"]
        assert "frequency_analysis" in breakdown
        assert "spatial_mapping" in breakdown
        assert "evolution_timeline" in breakdown
    
    async def test_audio_transcription(self, audio_agent):
        """Test audio transcription capabilities"""
        transcription_request = {
            "task_type": "audio_transcription",
            "audio_data": await audio_agent.generate_synthetic_audio(15.0),
            "transcription_settings": {
                "language": "en-US",
                "include_timestamps": True,
                "speaker_diarization": True,
                "punctuation": True,
                "formatting": "professional"
            },
            "advanced_features": {
                "emotion_detection": True,
                "confidence_scores": True,
                "word_level_timing": True,
                "noise_filtering": True
            }
        }
        
        result = await audio_agent.process_task(transcription_request)
        
        # Verify successful transcription
        assert result["success"] is True
        assert "transcription" in result
        
        transcription = result["transcription"]
        assert "text" in transcription
        assert "timestamps" in transcription
        assert "confidence_score" in transcription
        assert "metadata" in transcription
        
        # Verify timestamps
        timestamps = transcription["timestamps"]
        assert isinstance(timestamps, list)
        for timestamp in timestamps:
            assert "word" in timestamp
            assert "start_time" in timestamp
            assert "end_time" in timestamp
            assert "confidence" in timestamp
        
        # Verify metadata
        metadata = transcription["metadata"]
        assert "language_detected" in metadata
        assert "audio_quality" in metadata
        assert "speaker_count" in metadata
    
    async def test_spatial_audio_processing(self, audio_agent):
        """Test spatial audio and 3D audio processing"""
        spatial_request = {
            "task_type": "spatial_audio_processing",
            "input_audio": await audio_agent.generate_synthetic_audio(8.0),
            "spatial_config": {
                "output_format": "5.1_surround",
                "listener_position": {"x": 0, "y": 0, "z": 0},
                "audio_sources": [
                    {"position": {"x": -1, "y": 0, "z": 1}, "type": "dialogue"},
                    {"position": {"x": 1, "y": 0, "z": 1}, "type": "effects"},
                    {"position": {"x": 0, "y": 0, "z": -1}, "type": "ambient"}
                ],
                "room_simulation": {
                    "room_size": "medium",
                    "reverb_time": 1.2,
                    "absorption": 0.3
                }
            }
        }
        
        result = await audio_agent.process_task(spatial_request)
        
        # Verify successful spatial processing
        assert result["success"] is True
        assert "spatial_audio" in result
        
        spatial_audio = result["spatial_audio"]
        assert "surround_channels" in spatial_audio
        assert "binaural_output" in spatial_audio
        assert "spatial_metadata" in spatial_audio
        
        # Verify surround channels
        channels = spatial_audio["surround_channels"]
        assert "front_left" in channels
        assert "front_right" in channels
        assert "center" in channels
        assert "rear_left" in channels
        assert "rear_right" in channels
        assert "lfe" in channels
        
        # Verify spatial metadata
        metadata = spatial_audio["spatial_metadata"]
        assert "source_positions" in metadata
        assert "room_characteristics" in metadata
        assert "processing_applied" in metadata
    
    async def test_real_time_audio_processing(self, audio_agent):
        """Test real-time audio processing capabilities"""
        realtime_request = {
            "task_type": "real_time_processing",
            "processing_chain": [
                {"effect": "noise_gate", "threshold": -40},
                {"effect": "compressor", "ratio": 4.0, "attack": 3.0},
                {"effect": "equalizer", "preset": "vocal_enhance"},
                {"effect": "reverb", "room_size": 0.3, "wetness": 0.2}
            ],
            "latency_target": 10,  # milliseconds
            "buffer_size": 256,
            "sample_rate": 48000
        }
        
        result = await audio_agent.process_task(realtime_request)
        
        # Verify successful real-time setup
        assert result["success"] is True
        assert "processing_session" in result
        
        session = result["processing_session"]
        assert "session_id" in session
        assert "latency_achieved" in session
        assert "processing_chain" in session
        assert "performance_metrics" in session
        
        # Verify latency
        assert session["latency_achieved"] <= 15  # Should be close to target
        
        # Verify performance metrics
        metrics = session["performance_metrics"]
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "throughput" in metrics
    
    async def test_audio_analysis(self, audio_agent):
        """Test comprehensive audio analysis"""
        analysis_request = {
            "task_type": "audio_analysis",
            "audio_data": await audio_agent.generate_synthetic_audio(12.0),
            "analysis_types": [
                "spectral_analysis",
                "loudness_analysis",
                "voice_characteristics",
                "quality_assessment",
                "content_detection"
            ],
            "detailed_output": True
        }
        
        result = await audio_agent.process_task(analysis_request)
        
        # Verify successful analysis
        assert result["success"] is True
        assert "analysis_results" in result
        
        analysis = result["analysis_results"]
        assert "spectral_data" in analysis
        assert "loudness_metrics" in analysis
        assert "voice_analysis" in analysis
        assert "quality_scores" in analysis
        
        # Verify spectral data
        spectral = analysis["spectral_data"]
        assert "frequency_spectrum" in spectral
        assert "dominant_frequencies" in spectral
        assert "harmonic_content" in spectral
        
        # Verify loudness metrics
        loudness = analysis["loudness_metrics"]
        assert "peak_level" in loudness
        assert "rms_level" in loudness
        assert "lufs_integrated" in loudness
        assert "dynamic_range" in loudness
        
        # Verify voice analysis
        voice = analysis["voice_analysis"]
        assert "fundamental_frequency" in voice
        assert "formant_frequencies" in voice
        assert "voice_quality" in voice
        
        # Verify quality scores
        quality = analysis["quality_scores"]
        assert "overall_quality" in quality
        assert "clarity_score" in quality
        assert "naturalness_score" in quality
    
    async def test_batch_audio_processing(self, audio_agent):
        """Test batch processing of multiple audio files"""
        batch_request = {
            "task_type": "batch_processing",
            "audio_files": [
                {
                    "id": "file_1",
                    "audio_data": await audio_agent.generate_synthetic_audio(5.0),
                    "processing": ["noise_reduction", "normalize"]
                },
                {
                    "id": "file_2", 
                    "audio_data": await audio_agent.generate_synthetic_audio(7.0),
                    "processing": ["voice_enhance", "compress"]
                },
                {
                    "id": "file_3",
                    "audio_data": await audio_agent.generate_synthetic_audio(6.0),
                    "processing": ["eq_optimize", "reverb"]
                }
            ],
            "output_format": "wav",
            "quality": "high",
            "parallel_processing": True
        }
        
        result = await audio_agent.process_task(batch_request)
        
        # Verify successful batch processing
        assert result["success"] is True
        assert "processed_files" in result
        
        processed = result["processed_files"]
        assert len(processed) == 3
        
        for file_result in processed:
            assert "id" in file_result
            assert "processed_audio" in file_result
            assert "processing_report" in file_result
            assert file_result["success"] is True
    
    async def test_concurrent_audio_tasks(self, audio_agent):
        """Test concurrent audio processing"""
        tasks = [
            {
                "task_type": "voice_synthesis",
                "text": "Test voice synthesis",
                "voice_settings": {"voice_type": "natural"}
            },
            {
                "task_type": "music_generation",
                "music_style": "ambient",
                "duration": 10.0
            },
            {
                "task_type": "audio_enhancement",
                "input_audio": await audio_agent.generate_synthetic_audio(5.0),
                "enhancement_types": ["noise_reduction"]
            }
        ]
        
        # Execute tasks concurrently
        results = await asyncio.gather(*[
            audio_agent.process_task(task) for task in tasks
        ])
        
        # Verify all tasks completed successfully
        assert len(results) == 3
        for result in results:
            assert result["success"] is True
    
    @pytest.mark.performance
    async def test_audio_performance(self, audio_agent, assert_performance):
        """Test audio processing performance"""
        # Test voice synthesis speed
        voice_task = {
            "task_type": "voice_synthesis",
            "text": "Performance test for voice synthesis functionality",
            "voice_settings": {"voice_type": "natural"}
        }
        
        result = await audio_agent.process_task(voice_task)
        assert_performance("voice_synthesis", max_time=30.0)
        assert result["success"] is True
        
        # Test audio enhancement speed
        enhancement_task = {
            "task_type": "audio_enhancement",
            "input_audio": await audio_agent.generate_synthetic_audio(10.0),
            "enhancement_types": ["noise_reduction", "voice_clarity"]
        }
        
        result = await audio_agent.process_task(enhancement_task)
        assert_performance("audio_enhancement", max_time=25.0)
        assert result["success"] is True
    
    async def test_error_handling(self, audio_agent):
        """Test error handling in audio processing"""
        # Test invalid audio format
        invalid_format_task = {
            "task_type": "voice_synthesis",
            "text": "Test",
            "output_format": {"format": "invalid_format"}
        }
        
        result = await audio_agent.process_task(invalid_format_task)
        assert result["success"] is False
        assert "error" in result
        
        # Test empty audio data
        empty_audio_task = {
            "task_type": "audio_enhancement",
            "input_audio": b"",
            "enhancement_types": ["noise_reduction"]
        }
        
        result = await audio_agent.process_task(empty_audio_task)
        assert result["success"] is False
        assert "error" in result
        
        # Agent should remain functional
        valid_task = {
            "task_type": "voice_synthesis",
            "text": "Valid test",
            "voice_settings": {"voice_type": "natural"}
        }
        
        result = await audio_agent.process_task(valid_task)
        assert result["success"] is True
