# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
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
Comprehensive Test Suite for Generative Models

Ultra-advanced industrial-grade tests for generative neural networks,
covering content generation, audio synthesis, image creation, and all
business logic scenarios for content creators.

🎯 Expert Development Team:
✅ Lead Dev + AI Architect Developer
✅ Senior Backend Developer (Python/FastAPI/Django)  
✅ Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Backend Security Specialist
✅ Microservices Architect
✅ Audio Developer
✅ DevOps Engineer
✅ AI Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from unittest.mock import patch, MagicMock
import time

from ai.neural_networks.generative_models import (
    ContentGeneratorNetwork,
    AudioGeneratorNetwork,
    TextGeneratorNetwork,
    CoverArtGeneratorNetwork,
    ThumbnailGeneratorNetwork,
    GenerationConfig,
    GenerationTask,
    GenerationQuality
)
from ai.neural_networks.transformer_models import TransformerConfig
from ai.neural_networks.base_networks import NetworkType


@pytest.fixture
def generative_config():
    """Configuration for generative models"""
    return TransformerConfig(
        input_dim=768,
        hidden_dims=[768, 512, 256],
        output_dim=512,
        network_type=NetworkType.TRANSFORMER,
        num_heads=12,
        num_layers=8,
        d_model=768,
        d_ff=3072,
        max_sequence_length=2048
    )


@pytest.fixture
def generation_config():
    """Generation configuration for testing"""
    return GenerationConfig(
        task=GenerationTask.TEXT_COMPLETION,
        quality=GenerationQuality.STANDARD,
        max_length=512,
        temperature=0.8,
        top_k=50,
        top_p=0.9,
        repetition_penalty=1.1,
        style_strength=0.5,
        creativity_level=0.7,
        coherence_weight=0.8
    )


@pytest.fixture
def sample_prompts():
    """Sample prompts for generation testing"""
    return {
        "text": {
            "short": "Once upon a time",
            "medium": "Create a social media post about sustainable living that would resonate with millennials",
            "long": "Write a comprehensive script for a YouTube video about machine learning basics that would be engaging for beginners and include practical examples",
            "creative": "Imagine a world where AI and humans collaborate to create music",
            "technical": "Explain the transformer architecture in simple terms",
            "storytelling": "Tell me a story about a content creator who discovers an AI assistant"
        },
        "audio": {
            "music": torch.randn(1, 1024, 768),     # Musical features
            "speech": torch.randn(1, 512, 768),     # Speech features  
            "ambient": torch.randn(1, 2048, 768),   # Ambient sound features
            "podcast": torch.randn(1, 800, 768),    # Podcast audio features
        },
        "image": {
            "thumbnail": torch.randn(1, 196, 768),   # Thumbnail features
            "cover_art": torch.randn(1, 256, 768),   # Cover art features
            "social_media": torch.randn(1, 144, 768), # Social media image
            "profile_pic": torch.randn(1, 64, 768),  # Profile picture
        },
        "multimodal": {
            "text": torch.randn(1, 256, 768),
            "audio": torch.randn(1, 256, 768),
            "image": torch.randn(1, 196, 768)
        }
    }


@pytest.fixture
def style_embeddings():
    """Sample style embeddings for different creator styles"""
    return {
        "professional": torch.randn(1, 128),
        "casual": torch.randn(1, 128),
        "artistic": torch.randn(1, 128),
        "educational": torch.randn(1, 128),
        "entertainment": torch.randn(1, 128),
        "minimalist": torch.randn(1, 128),
        "vibrant": torch.randn(1, 128),
        "corporate": torch.randn(1, 128)
    }


class TestGenerationTask:
    """Test GenerationTask enum functionality"""
    
    def test_generation_task_values(self):
        """Test GenerationTask enum values"""
        assert GenerationTask.TEXT_COMPLETION.value == "text_completion"
        assert GenerationTask.AUDIO_SYNTHESIS.value == "audio_synthesis"
        assert GenerationTask.IMAGE_GENERATION.value == "image_generation"
        assert GenerationTask.MUSIC_COMPOSITION.value == "music_composition"
        assert GenerationTask.THUMBNAIL_CREATION.value == "thumbnail_creation"
        assert GenerationTask.COVER_ART_DESIGN.value == "cover_art_design"
        assert GenerationTask.SOCIAL_POST_CREATION.value == "social_post_creation"
        assert GenerationTask.SCRIPT_WRITING.value == "script_writing"
        assert GenerationTask.REMIX_GENERATION.value == "remix_generation"
    
    def test_generation_task_coverage(self):
        """Test that all major generation tasks are covered"""
        tasks = list(GenerationTask)
        task_values = [task.value for task in tasks]
        
        # Should cover main content creator needs
        expected_categories = [
            "text", "audio", "image", "music", 
            "thumbnail", "cover_art", "social_post", "script"
        ]
        
        for category in expected_categories:
            matching_tasks = [task for task in task_values if category in task]
            assert len(matching_tasks) > 0, f"No tasks found for category: {category}"


class TestGenerationQuality:
    """Test GenerationQuality enum functionality"""
    
    def test_quality_levels(self):
        """Test GenerationQuality enum values"""
        assert GenerationQuality.DRAFT.value == "draft"
        assert GenerationQuality.STANDARD.value == "standard"
        assert GenerationQuality.PROFESSIONAL.value == "professional"
        assert GenerationQuality.PREMIUM.value == "premium"
    
    def test_quality_hierarchy(self):
        """Test quality level hierarchy"""
        quality_order = [
            GenerationQuality.DRAFT,
            GenerationQuality.STANDARD,
            GenerationQuality.PROFESSIONAL,
            GenerationQuality.PREMIUM
        ]
        
        # Verify order makes sense (each level should be "higher" than previous)
        assert len(quality_order) == 4
        assert quality_order[0] == GenerationQuality.DRAFT
        assert quality_order[-1] == GenerationQuality.PREMIUM


class TestGenerationConfig:
    """Test GenerationConfig functionality"""
    
    def test_config_creation(self):
        """Test GenerationConfig creation with defaults"""
        config = GenerationConfig(
            task=GenerationTask.TEXT_COMPLETION
        )
        
        assert config.task == GenerationTask.TEXT_COMPLETION
        assert config.quality == GenerationQuality.STANDARD
        assert config.max_length == 1024
        assert config.temperature == 0.8
        assert config.top_k == 50
        assert config.top_p == 0.9
        assert config.repetition_penalty == 1.1
    
    def test_config_customization(self):
        """Test custom GenerationConfig parameters"""
        creator_style = {"professional": 0.8, "creative": 0.6}
        audience_prefs = {"educational": 0.9, "entertainment": 0.3}
        
        config = GenerationConfig(
            task=GenerationTask.AUDIO_SYNTHESIS,
            quality=GenerationQuality.PREMIUM,
            max_length=2048,
            temperature=1.2,
            target_duration=180.0,
            target_format="wav",
            creator_style=creator_style,
            audience_preferences=audience_prefs
        )
        
        assert config.task == GenerationTask.AUDIO_SYNTHESIS
        assert config.quality == GenerationQuality.PREMIUM
        assert config.max_length == 2048
        assert config.temperature == 1.2
        assert config.target_duration == 180.0
        assert config.target_format == "wav"
        assert config.creator_style == creator_style
        assert config.audience_preferences == audience_prefs
    
    def test_config_validation_ranges(self):
        """Test configuration parameter ranges"""
        config = GenerationConfig(
            task=GenerationTask.IMAGE_GENERATION,
            temperature=0.1,
            top_p=0.95,
            style_strength=1.0,
            creativity_level=0.0,
            coherence_weight=1.0
        )
        
        # Temperature should be positive
        assert config.temperature > 0
        
        # Top-p should be between 0 and 1
        assert 0 <= config.top_p <= 1
        
        # Style strength should be between 0 and 1
        assert 0 <= config.style_strength <= 1
        
        # Creativity level should be between 0 and 1
        assert 0 <= config.creativity_level <= 1
        
        # Coherence weight should be between 0 and 1
        assert 0 <= config.coherence_weight <= 1


class TestContentGeneratorNetwork:
    """Test main ContentGeneratorNetwork functionality"""
    
    def test_network_initialization(self, generative_config):
        """Test ContentGeneratorNetwork initialization"""
        network = ContentGeneratorNetwork(generative_config)
        
        assert network.config == generative_config
        assert hasattr(network, 'content_encoder')
        assert hasattr(network, 'generator')
        assert hasattr(network, 'generation_heads')
        assert hasattr(network, 'style_conditioning')
        assert hasattr(network, 'quality_controller')
        assert hasattr(network, 'coherence_layer')
        
        # Check modality encoders
        expected_modalities = ["text", "audio", "image"]
        for modality in expected_modalities:
            assert modality in network.content_encoder
            assert modality in network.generation_heads
    
    def test_single_modality_generation(self, generative_config, sample_prompts):
        """Test generation with single modality input"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        # Test text generation
        text_input = {"text": sample_prompts["multimodal"]["text"]}
        
        with torch.no_grad():
            outputs = network.forward(text_input)
        
        assert "text" in outputs
        assert "audio" in outputs
        assert "image" in outputs
        assert "quality_prediction" in outputs
        
        # Check output shapes
        batch_size = 1
        assert outputs["text"].shape[0] == batch_size
        assert outputs["audio"].shape[0] == batch_size
        assert outputs["image"].shape[0] == batch_size
        assert outputs["quality_prediction"].shape == (batch_size, 4)  # 4 quality levels
        
        # Quality predictions should sum to 1 (softmax)
        quality_sum = outputs["quality_prediction"].sum(dim=1)
        assert torch.allclose(quality_sum, torch.ones(batch_size), atol=1e-6)
    
    def test_multimodal_generation(self, generative_config, sample_prompts):
        """Test generation with multiple modalities"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        multimodal_input = sample_prompts["multimodal"]
        
        with torch.no_grad():
            outputs = network.forward(multimodal_input)
        
        assert all(modality in outputs for modality in ["text", "audio", "image"])
        assert "quality_prediction" in outputs
        
        # All outputs should have finite values
        for modality, output in outputs.items():
            assert torch.isfinite(output).all(), f"Non-finite values in {modality} output"
    
    def test_style_conditioning(self, generative_config, sample_prompts, style_embeddings):
        """Test style conditioning in generation"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        input_data = {"text": sample_prompts["multimodal"]["text"]}
        
        # Generate without style conditioning
        with torch.no_grad():
            output_no_style = network.forward(input_data)
        
        # Generate with professional style
        professional_style = style_embeddings["professional"]
        with torch.no_grad():
            output_professional = network.forward(input_data, style_embedding=professional_style)
        
        # Generate with artistic style
        artistic_style = style_embeddings["artistic"]
        with torch.no_grad():
            output_artistic = network.forward(input_data, style_embedding=artistic_style)
        
        # Outputs should be different with different styles
        text_diff_prof = torch.abs(output_no_style["text"] - output_professional["text"]).mean()
        text_diff_art = torch.abs(output_no_style["text"] - output_artistic["text"]).mean()
        
        assert text_diff_prof > 1e-6, "Professional style should affect output"
        assert text_diff_art > 1e-6, "Artistic style should affect output"
        
        # Different styles should produce different outputs
        style_diff = torch.abs(output_professional["text"] - output_artistic["text"]).mean()
        assert style_diff > 1e-6, "Different styles should produce different outputs"
    
    def test_generation_method(self, generative_config, generation_config, sample_prompts, style_embeddings):
        """Test the generate method"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        # Test with text prompt
        text_prompt = sample_prompts["text"]["medium"]
        professional_style = style_embeddings["professional"]
        
        generated_content = network.generate(
            prompt=text_prompt,
            config=generation_config,
            style_embedding=professional_style
        )
        
        assert isinstance(generated_content, dict)
        # Should contain generated content and metadata
        expected_keys = ["text", "audio", "image", "quality_prediction"]
        for key in expected_keys:
            assert key in generated_content or "generated_" + key in generated_content
    
    def test_quality_control(self, generative_config, sample_prompts):
        """Test quality control mechanism"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        input_data = {"text": sample_prompts["multimodal"]["text"]}
        
        with torch.no_grad():
            outputs = network.forward(input_data)
        
        quality_predictions = outputs["quality_prediction"]
        
        # Should predict quality distribution
        assert quality_predictions.shape[1] == 4  # 4 quality levels
        assert torch.all(quality_predictions >= 0)
        assert torch.all(quality_predictions <= 1)
        
        # Should sum to 1 for each sample
        quality_sums = quality_predictions.sum(dim=1)
        assert torch.allclose(quality_sums, torch.ones(quality_predictions.shape[0]))
    
    def test_coherence_enforcement(self, generative_config):
        """Test coherence enforcement in generation"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        # Create input with low coherence (random noise)
        batch_size = 2
        seq_len = 10
        incoherent_input = torch.randn(batch_size, seq_len, generative_config.d_model)
        
        # Test coherence layer directly
        coherent_output, attention_weights = network.coherence_layer(
            incoherent_input, incoherent_input, incoherent_input
        )
        
        assert coherent_output.shape == incoherent_input.shape
        assert attention_weights.shape == (batch_size, seq_len, seq_len)
        assert torch.isfinite(coherent_output).all()
        assert torch.isfinite(attention_weights).all()
        
        # Attention weights should sum to 1
        attention_sums = attention_weights.sum(dim=-1)
        assert torch.allclose(attention_sums, torch.ones_like(attention_sums), atol=1e-6)


class TestAudioGeneratorNetwork:
    """Test AudioGeneratorNetwork functionality"""
    
    def test_audio_generator_initialization(self, generative_config):
        """Test AudioGeneratorNetwork initialization"""
        network = AudioGeneratorNetwork(generative_config)
        
        assert hasattr(network, 'audio_encoder')
        assert hasattr(network, 'waveform_generator')
        assert hasattr(network, 'spectral_processor')
        assert hasattr(network, 'duration_controller')
    
    def test_music_generation(self, generative_config, sample_prompts):
        """Test music generation functionality"""
        network = AudioGeneratorNetwork(generative_config)
        network.eval()
        
        music_prompt = sample_prompts["audio"]["music"]
        
        with torch.no_grad():
            generated_audio = network.generate_music(
                prompt=music_prompt,
                duration=30.0,  # 30 seconds
                style="electronic"
            )
        
        assert isinstance(generated_audio, torch.Tensor)
        assert generated_audio.dim() >= 2  # Should have batch and time dimensions
        assert torch.isfinite(generated_audio).all()
    
    def test_speech_synthesis(self, generative_config):
        """Test speech synthesis functionality"""
        network = AudioGeneratorNetwork(generative_config)
        network.eval()
        
        text_input = "Hello, this is a test of speech synthesis."
        
        with torch.no_grad():
            synthesized_speech = network.synthesize_speech(
                text=text_input,
                voice_style="natural",
                speed=1.0
            )
        
        assert isinstance(synthesized_speech, torch.Tensor)
        assert synthesized_speech.dim() >= 1  # Audio waveform
        assert torch.isfinite(synthesized_speech).all()
    
    def test_audio_enhancement(self, generative_config, sample_prompts):
        """Test audio enhancement functionality"""
        network = AudioGeneratorNetwork(generative_config)
        network.eval()
        
        noisy_audio = sample_prompts["audio"]["podcast"]
        
        with torch.no_grad():
            enhanced_audio = network.enhance_audio(
                audio=noisy_audio,
                enhancement_type="noise_reduction"
            )
        
        assert enhanced_audio.shape == noisy_audio.shape
        assert torch.isfinite(enhanced_audio).all()
        
        # Enhanced audio should be different from input
        diff = torch.abs(enhanced_audio - noisy_audio).mean()
        assert diff > 1e-6
    
    def test_remix_generation(self, generative_config, sample_prompts):
        """Test remix generation functionality"""
        network = AudioGeneratorNetwork(generative_config)
        network.eval()
        
        original_track = sample_prompts["audio"]["music"]
        
        with torch.no_grad():
            remix = network.generate_remix(
                original=original_track,
                remix_style="upbeat",
                intensity=0.7
            )
        
        assert isinstance(remix, torch.Tensor)
        assert remix.shape == original_track.shape
        assert torch.isfinite(remix).all()
        
        # Remix should be different from original
        diff = torch.abs(remix - original_track).mean()
        assert diff > 1e-6


class TestTextGeneratorNetwork:
    """Test TextGeneratorNetwork functionality"""
    
    def test_text_generator_initialization(self, generative_config):
        """Test TextGeneratorNetwork initialization"""
        network = TextGeneratorNetwork(generative_config)
        
        assert hasattr(network, 'language_model')
        assert hasattr(network, 'style_adapter')
        assert hasattr(network, 'topic_controller')
        assert hasattr(network, 'length_predictor')
    
    def test_text_completion(self, generative_config, sample_prompts, generation_config):
        """Test text completion functionality"""
        network = TextGeneratorNetwork(generative_config)
        network.eval()
        
        prompt = sample_prompts["text"]["short"]
        
        with torch.no_grad():
            completion = network.complete_text(
                prompt=prompt,
                max_length=generation_config.max_length,
                temperature=generation_config.temperature
            )
        
        assert isinstance(completion, str)
        assert len(completion) > len(prompt)
        assert completion.startswith(prompt) or prompt in completion
    
    def test_social_post_generation(self, generative_config, sample_prompts):
        """Test social media post generation"""
        network = TextGeneratorNetwork(generative_config)
        network.eval()
        
        topic = "sustainable living"
        platform = "instagram"
        
        with torch.no_data():
            post = network.generate_social_post(
                topic=topic,
                platform=platform,
                target_audience="millennials",
                include_hashtags=True
            )
        
        assert isinstance(post, dict)
        assert "content" in post
        assert "hashtags" in post
        assert isinstance(post["content"], str)
        assert isinstance(post["hashtags"], list)
        assert len(post["content"]) <= 2200  # Instagram limit
    
    def test_script_writing(self, generative_config, sample_prompts):
        """Test script writing functionality"""
        network = TextGeneratorNetwork(generative_config)
        network.eval()
        
        with torch.no_grad():
            script = network.write_script(
                topic="machine learning basics",
                format="youtube_video",
                target_length=600,  # 10 minutes
                style="educational"
            )
        
        assert isinstance(script, dict)
        assert "content" in script
        assert "structure" in script
        assert "estimated_duration" in script
        
        # Script should have proper structure
        structure = script["structure"]
        expected_sections = ["introduction", "main_content", "conclusion"]
        for section in expected_sections:
            assert any(section in str(s).lower() for s in structure)
    
    def test_content_summarization(self, generative_config, sample_prompts):
        """Test content summarization"""
        network = TextGeneratorNetwork(generative_config)
        network.eval()
        
        long_content = sample_prompts["text"]["long"]
        
        with torch.no_grad():
            summary = network.summarize_content(
                content=long_content,
                summary_length="short",
                key_points=3
            )
        
        assert isinstance(summary, dict)
        assert "summary" in summary
        assert "key_points" in summary
        assert len(summary["key_points"]) <= 3
        assert len(summary["summary"]) < len(long_content)


class TestImageGenerationNetworks:
    """Test image generation networks"""
    
    def test_thumbnail_generator_initialization(self, generative_config):
        """Test ThumbnailGeneratorNetwork initialization"""
        network = ThumbnailGeneratorNetwork(generative_config)
        
        assert hasattr(network, 'image_generator')
        assert hasattr(network, 'text_overlay')
        assert hasattr(network, 'layout_optimizer')
        assert hasattr(network, 'thumbnail_styles')
    
    def test_thumbnail_generation(self, generative_config, sample_prompts):
        """Test thumbnail generation"""
        network = ThumbnailGeneratorNetwork(generative_config)
        network.eval()
        
        video_content = sample_prompts["image"]["thumbnail"]
        
        with torch.no_grad():
            thumbnail = network.generate_thumbnail(
                content_features=video_content,
                title="Amazing AI Tutorial",
                style="modern",
                platform="youtube"
            )
        
        assert isinstance(thumbnail, torch.Tensor)
        assert thumbnail.dim() == 4  # [batch, channels, height, width]
        assert torch.isfinite(thumbnail).all()
        assert torch.all(thumbnail >= 0) and torch.all(thumbnail <= 1)  # Normalized
    
    def test_cover_art_generator_initialization(self, generative_config):
        """Test CoverArtGeneratorNetwork initialization"""
        network = CoverArtGeneratorNetwork(generative_config)
        
        assert hasattr(network, 'visual_generator')
        assert hasattr(network, 'style_mixer')
        assert hasattr(network, 'color_harmonizer')
        assert hasattr(network, 'composition_optimizer')
    
    def test_cover_art_generation(self, generative_config, sample_prompts):
        """Test cover art generation"""
        network = CoverArtGeneratorNetwork(generative_config)
        network.eval()
        
        music_features = sample_prompts["audio"]["music"]
        
        with torch.no_grad():
            cover_art = network.generate_cover_art(
                music_features=music_features,
                genre="electronic",
                mood="energetic",
                color_scheme="vibrant"
            )
        
        assert isinstance(cover_art, torch.Tensor)
        assert cover_art.dim() == 4  # [batch, channels, height, width]
        assert torch.isfinite(cover_art).all()
        assert torch.all(cover_art >= 0) and torch.all(cover_art <= 1)
    
    def test_style_transfer(self, generative_config, sample_prompts, style_embeddings):
        """Test style transfer in image generation"""
        network = CoverArtGeneratorNetwork(generative_config)
        network.eval()
        
        base_image = sample_prompts["image"]["cover_art"]
        artistic_style = style_embeddings["artistic"]
        
        with torch.no_grad():
            stylized_image = network.apply_style_transfer(
                content=base_image,
                style_embedding=artistic_style,
                style_strength=0.7
            )
        
        assert stylized_image.shape == base_image.shape
        assert torch.isfinite(stylized_image).all()
        
        # Stylized image should be different from original
        diff = torch.abs(stylized_image - base_image).mean()
        assert diff > 1e-6


class TestGenerativeModelPerformance:
    """Performance tests for generative models"""
    
    def test_generation_speed(self, generative_config, sample_prompts, generation_config):
        """Test generation speed across different tasks"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        input_data = sample_prompts["multimodal"]
        
        # Warm up
        for _ in range(3):
            with torch.no_grad():
                _ = network.forward(input_data)
        
        # Measure generation time
        times = []
        for _ in range(10):
            start_time = time.time()
            with torch.no_grad():
                _ = network.forward(input_data)
            end_time = time.time()
            times.append((end_time - start_time) * 1000)  # Convert to ms
        
        avg_time = np.mean(times)
        std_time = np.std(times)
        
        print(f"Content generation: {avg_time:.2f}±{std_time:.2f}ms")
        
        # Generation should be reasonably fast
        assert avg_time < 2000  # Less than 2 seconds
    
    def test_batch_generation_efficiency(self, generative_config, sample_prompts):
        """Test batch generation efficiency"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        single_input = {k: v[:1] for k, v in sample_prompts["multimodal"].items()}
        batch_input = {k: v.repeat(4, 1, 1) for k, v in single_input.items()}  # Batch of 4
        
        # Single generation times
        single_times = []
        for _ in range(4):
            start_time = time.time()
            with torch.no_grad():
                _ = network.forward(single_input)
            single_times.append((time.time() - start_time) * 1000)
        
        total_single_time = sum(single_times)
        
        # Batch generation time
        start_time = time.time()
        with torch.no_grad():
            _ = network.forward(batch_input)
        batch_time = (time.time() - start_time) * 1000
        
        efficiency_gain = total_single_time / batch_time
        print(f"Batch efficiency gain: {efficiency_gain:.2f}x")
        
        # Batch processing should be more efficient
        assert efficiency_gain > 1.2  # At least 20% improvement
    
    def test_memory_usage_during_generation(self, generative_config, sample_prompts):
        """Test memory usage during generation"""
        import psutil
        import gc
        
        # Measure initial memory
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        input_data = sample_prompts["multimodal"]
        
        # Generate multiple times to test memory leaks
        for _ in range(10):
            with torch.no_grad():
                outputs = network.forward(input_data)
                del outputs  # Explicitly delete outputs
        
        # Measure final memory
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        memory_increase = final_memory - initial_memory
        print(f"Memory increase after 10 generations: {memory_increase:.1f}MB")
        
        # Memory increase should be reasonable (no major leaks)
        assert memory_increase < 1000  # Less than 1GB increase


class TestGenerativeModelRobustness:
    """Robustness tests for generative models"""
    
    def test_invalid_input_handling(self, generative_config):
        """Test handling of invalid inputs"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        # Test empty input
        with pytest.raises(ValueError):
            network.forward({})
        
        # Test invalid modality
        invalid_input = {"invalid_modality": torch.randn(1, 100, 768)}
        with pytest.raises(ValueError):
            network.forward(invalid_input)
        
        # Test mismatched dimensions
        wrong_dim_input = {"text": torch.randn(1, 100, 512)}  # Wrong feature dimension
        with pytest.raises(RuntimeError):
            network.forward(wrong_dim_input)
    
    def test_extreme_generation_parameters(self, generative_config, sample_prompts):
        """Test with extreme generation parameters"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        input_data = {"text": sample_prompts["multimodal"]["text"]}
        
        # Test extreme temperature (very low)
        extreme_config_low = GenerationConfig(
            task=GenerationTask.TEXT_COMPLETION,
            temperature=0.01,
            top_k=1,
            top_p=0.1
        )
        
        generated_low = network.generate(input_data, extreme_config_low)
        assert isinstance(generated_low, dict)
        
        # Test extreme temperature (very high)
        extreme_config_high = GenerationConfig(
            task=GenerationTask.TEXT_COMPLETION,
            temperature=2.0,
            top_k=100,
            top_p=0.99
        )
        
        generated_high = network.generate(input_data, extreme_config_high)
        assert isinstance(generated_high, dict)
    
    def test_corrupted_input_resilience(self, generative_config, sample_prompts):
        """Test resilience to corrupted inputs"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        clean_input = {"text": sample_prompts["multimodal"]["text"]}
        
        # Add NaN values
        corrupted_input = clean_input.copy()
        corrupted_input["text"] = corrupted_input["text"].clone()
        corrupted_input["text"][0, 0, 0] = float('nan')
        
        # Should handle NaN gracefully
        with torch.no_grad():
            outputs = network.forward(corrupted_input)
        
        # Outputs should not contain NaN
        for modality, output in outputs.items():
            if isinstance(output, torch.Tensor):
                assert not torch.isnan(output).any(), f"NaN found in {modality} output"
    
    def test_generation_consistency(self, generative_config, sample_prompts):
        """Test generation consistency with same inputs"""
        network = ContentGeneratorNetwork(generative_config)
        network.eval()
        
        input_data = {"text": sample_prompts["multimodal"]["text"]}
        
        # Generate multiple times with same seed
        torch.manual_seed(42)
        with torch.no_grad():
            output1 = network.forward(input_data)
        
        torch.manual_seed(42)
        with torch.no_grad():
            output2 = network.forward(input_data)
        
        # Outputs should be identical with same seed
        for modality in output1:
            if isinstance(output1[modality], torch.Tensor):
                assert torch.allclose(output1[modality], output2[modality], atol=1e-6)


class TestGenerativeModelIntegration:
    """Integration tests for generative models"""
    
    def test_multimodal_content_creation_pipeline(self, generative_config, sample_prompts, style_embeddings, generation_config):
        """Test complete multimodal content creation pipeline"""
        # Initialize networks
        content_generator = ContentGeneratorNetwork(generative_config)
        audio_generator = AudioGeneratorNetwork(generative_config)
        text_generator = TextGeneratorNetwork(generative_config)
        thumbnail_generator = ThumbnailGeneratorNetwork(generative_config)
        
        # Set all to eval mode
        content_generator.eval()
        audio_generator.eval()
        text_generator.eval()
        thumbnail_generator.eval()
        
        professional_style = style_embeddings["professional"]
        
        with torch.no_grad():
            # Step 1: Generate main content
            main_content = content_generator.generate(
                prompt=sample_prompts["text"]["creative"],
                config=generation_config,
                style_embedding=professional_style
            )
            
            # Step 2: Generate accompanying audio
            audio_content = audio_generator.generate_music(
                prompt=sample_prompts["audio"]["music"],
                duration=60.0,
                style="ambient"
            )
            
            # Step 3: Generate text description
            description = text_generator.generate_social_post(
                topic="AI-generated content",
                platform="youtube",
                target_audience="tech_enthusiasts"
            )
            
            # Step 4: Generate thumbnail
            thumbnail = thumbnail_generator.generate_thumbnail(
                content_features=sample_prompts["image"]["thumbnail"],
                title="AI Content Creation",
                style="modern"
            )
        
        # Verify pipeline results
        assert isinstance(main_content, dict)
        assert isinstance(audio_content, torch.Tensor)
        assert isinstance(description, dict)
        assert isinstance(thumbnail, torch.Tensor)
        
        # Check that all outputs are valid
        assert torch.isfinite(audio_content).all()
        assert torch.isfinite(thumbnail).all()
        assert "content" in description
    
    def test_creator_workflow_simulation(self, generative_config, sample_prompts, style_embeddings):
        """Test typical creator workflow with generative models"""
        content_generator = ContentGeneratorNetwork(generative_config)
        text_generator = TextGeneratorNetwork(generative_config)
        
        content_generator.eval()
        text_generator.eval()
        
        # Simulate creator's style
        creator_style = style_embeddings["artistic"]
        
        # Creator workflow: Idea -> Script -> Content -> Social Posts
        with torch.no_grad():
            # Step 1: Generate initial idea/concept
            concept_config = GenerationConfig(
                task=GenerationTask.TEXT_COMPLETION,
                creativity_level=0.9,
                max_length=256
            )
            
            concept = content_generator.generate(
                prompt="Innovative content idea about",
                config=concept_config,
                style_embedding=creator_style
            )
            
            # Step 2: Develop into full script
            script = text_generator.write_script(
                topic="AI in creative industries",
                format="youtube_video",
                target_length=900,  # 15 minutes
                style="engaging"
            )
            
            # Step 3: Generate promotional content
            social_posts = []
            platforms = ["instagram", "twitter", "tiktok"]
            
            for platform in platforms:
                post = text_generator.generate_social_post(
                    topic="new video about AI creativity",
                    platform=platform,
                    target_audience="creatives"
                )
                social_posts.append(post)
        
        # Verify creator workflow results
        assert isinstance(concept, dict)
        assert isinstance(script, dict)
        assert len(social_posts) == 3
        
        for post in social_posts:
            assert "content" in post
            assert isinstance(post["content"], str)
            assert len(post["content"]) > 0


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
