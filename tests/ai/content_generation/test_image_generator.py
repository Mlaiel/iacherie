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
Image Generator Tests

Comprehensive tests for the ImageGenerator class that handles
AI-powered image creation and optimization.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

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

from ai.content_generation.image_generator import (
    ImageContentGenerator, 
    ImageConfig, 
    ImageFormat, 
    ImageQuality, 
    ImageStyle
)
from ai.content_generation.content_models import ContentType, Platform


class TestImageGenerator:
    """Test suite for ImageGenerator"""
    
    @pytest.fixture
    def generator(self):
        """Create an image generator instance"""
        config = {'test': 'value'}  # Minimal config for testing
        return ImageContentGenerator(config)
    
    @pytest.fixture
    def sample_prompt(self):
        """Create sample image generation prompt"""
        return "A futuristic cityscape with flying cars, neon lights, and holographic advertisements, cyberpunk style, high detail, 4k resolution"
    
    @pytest.fixture
    def image_config(self):
        """Create sample image configuration"""
        return ImageConfig(
            width=1024,
            height=1024,
            quality=ImageQuality.HIGH,
            format=ImageFormat.PNG,
            style=ImageStyle.REALISTIC,
            art_style=ArtStyle.DIGITAL_ART,
            seed=42
        )
    
    def test_generator_initialization(self, generator):
        """Test image generator initialization"""
        assert generator is not None
        assert hasattr(generator, 'image_models')
        assert hasattr(generator, 'supported_formats')
        assert hasattr(generator, 'supported_resolutions')
        assert hasattr(generator, 'quality_presets')
    
    @pytest.mark.asyncio
    async def test_basic_image_generation(self, generator, sample_prompt, image_config):
        """Test basic AI image generation"""
        with patch.object(generator, '_generate_with_ai') as mock_generation:
            mock_generation.return_value = {
                "success": True,
                "image_path": "/tmp/generated_image.png",
                "image_data": b"mock_image_data",
                "generation_time": 15.3,
                "provider": "stable_diffusion",
                "model_version": "xl_1.0",
                "seed_used": 42
            }
            
            result = await generator.generate_image(
                prompt=sample_prompt,
                config=image_config,
                provider=GenerationProvider.STABLE_DIFFUSION
            )
            
            assert result["success"] is True
            assert result["generation_time"] == 15.3
            assert result["provider"] == "stable_diffusion"
            assert "image_path" in result
    
    @pytest.mark.asyncio
    async def test_style_transfer(self, generator):
        """Test style transfer functionality"""
        source_image = "/tmp/source_photo.jpg"
        style_reference = "/tmp/style_reference.jpg"
        
        with patch.object(generator, '_apply_style_transfer') as mock_transfer:
            mock_transfer.return_value = {
                "success": True,
                "styled_image": "/tmp/styled_image.jpg",
                "style_strength": 0.8,
                "content_preservation": 0.9,
                "processing_time": 8.5
            }
            
            result = await generator.apply_style_transfer(
                source_image=source_image,
                style_reference=style_reference,
                style_strength=0.8,
                preserve_content=True
            )
            
            assert result["success"] is True
            assert result["style_strength"] == 0.8
            assert result["content_preservation"] == 0.9
    
    @pytest.mark.asyncio
    async def test_image_upscaling(self, generator):
        """Test AI-powered image upscaling"""
        low_res_image = "/tmp/low_res_image.jpg"
        
        with patch.object(generator, '_upscale_image') as mock_upscale:
            mock_upscale.return_value = {
                "success": True,
                "upscaled_image": "/tmp/upscaled_image.jpg",
                "original_resolution": "512x512",
                "new_resolution": "2048x2048",
                "upscale_factor": 4,
                "quality_improvement": 85.2
            }
            
            result = await generator.upscale_image(
                image_path=low_res_image,
                upscale_factor=4,
                enhance_quality=True,
                preserve_details=True
            )
            
            assert result["success"] is True
            assert result["upscale_factor"] == 4
            assert result["quality_improvement"] == 85.2
    
    @pytest.mark.asyncio
    async def test_batch_image_generation(self, generator, image_config):
        """Test batch image generation"""
        prompts = [
            "A serene mountain landscape at sunset",
            "A bustling marketplace in Morocco",
            "A space station orbiting Earth"
        ]
        
        with patch.object(generator, '_generate_with_ai') as mock_generation:
            mock_generation.return_value = {
                "success": True,
                "image_path": "/tmp/batch_image.png",
                "generation_time": 12.0
            }
            
            results = await generator.generate_batch(
                prompts=prompts,
                config=image_config,
                parallel_processing=True,
                max_concurrent=2
            )
            
            assert len(results) == 3
            for result in results:
                assert result["success"] is True
                assert "image_path" in result
    
    @pytest.mark.asyncio
    async def test_image_editing_inpainting(self, generator):
        """Test image inpainting for editing"""
        base_image = "/tmp/base_image.jpg"
        mask_image = "/tmp/mask.png"
        edit_prompt = "Replace the sky with a dramatic sunset"
        
        with patch.object(generator, '_inpaint_image') as mock_inpaint:
            mock_inpaint.return_value = {
                "success": True,
                "edited_image": "/tmp/inpainted_image.jpg",
                "edit_quality": 92.5,
                "blend_seamlessness": 88.7,
                "processing_time": 18.2
            }
            
            result = await generator.edit_with_inpainting(
                base_image=base_image,
                mask=mask_image,
                prompt=edit_prompt,
                blend_strength=0.9
            )
            
            assert result["success"] is True
            assert result["edit_quality"] == 92.5
            assert result["blend_seamlessness"] == 88.7
    
    @pytest.mark.asyncio
    async def test_background_removal(self, generator):
        """Test background removal functionality"""
        source_image = "/tmp/portrait.jpg"
        
        with patch.object(generator, '_remove_background') as mock_removal:
            mock_removal.return_value = {
                "success": True,
                "result_image": "/tmp/no_background.png",
                "mask_quality": 95.8,
                "edge_smoothness": 92.3,
                "processing_time": 5.2
            }
            
            result = await generator.remove_background(
                image_path=source_image,
                refine_edges=True,
                feather_amount=2.0
            )
            
            assert result["success"] is True
            assert result["mask_quality"] == 95.8
            assert result["edge_smoothness"] == 92.3
    
    @pytest.mark.asyncio
    async def test_logo_and_brand_generation(self, generator):
        """Test logo and brand image generation"""
        brand_info = {
            "company_name": "TechFlow AI",
            "industry": "Technology",
            "style_preference": "modern minimalist",
            "colors": ["#2563EB", "#F59E0B"],
            "keywords": ["innovation", "artificial intelligence", "flow"]
        }
        
        with patch.object(generator, '_generate_logo') as mock_logo:
            mock_logo.return_value = {
                "success": True,
                "logo_variations": [
                    {"path": "/tmp/logo_v1.svg", "style": "icon_only"},
                    {"path": "/tmp/logo_v2.svg", "style": "text_and_icon"},
                    {"path": "/tmp/logo_v3.svg", "style": "text_only"}
                ],
                "brand_colors": ["#2563EB", "#F59E0B"],
                "style_consistency": 94.5
            }
            
            result = await generator.generate_brand_assets(
                brand_info=brand_info,
                asset_types=["logo", "icon", "wordmark"],
                format=ImageFormat.SVG
            )
            
            assert result["success"] is True
            assert len(result["logo_variations"]) == 3
            assert result["style_consistency"] == 94.5
    
    @pytest.mark.asyncio
    async def test_social_media_image_creation(self, generator):
        """Test social media optimized image creation"""
        content_data = {
            "title": "5 AI Trends in 2025",
            "subtitle": "Revolutionary Technologies",
            "author": "Fahed Mlaiel",
            "background_style": "gradient_tech",
            "brand_colors": ["#FF6B35", "#F7931E"]
        }
        
        platforms = [Platform.INSTAGRAM, Platform.LINKEDIN, Platform.TWITTER]
        
        with patch.object(generator, '_create_social_image') as mock_social:
            def platform_image(data, platform, template):
                dimensions = {
                    Platform.INSTAGRAM: "1080x1080",
                    Platform.LINKEDIN: "1200x628",
                    Platform.TWITTER: "1200x675"
                }
                return {
                    "success": True,
                    "image_path": f"/tmp/{platform.value}_post.jpg",
                    "dimensions": dimensions[platform],
                    "platform": platform.value
                }
            
            mock_social.side_effect = platform_image
            
            results = await generator.create_social_media_images(
                content_data=content_data,
                platforms=platforms,
                template_style="professional"
            )
            
            assert len(results) == 3
            for platform, result in results.items():
                assert result["success"] is True
                assert result["platform"] == platform
    
    @pytest.mark.asyncio
    async def test_product_mockup_generation(self, generator):
        """Test product mockup generation"""
        product_info = {
            "type": "mobile_app",
            "screenshots": ["/tmp/screen1.png", "/tmp/screen2.png"],
            "device": "iphone_15_pro",
            "environment": "modern_office"
        }
        
        with patch.object(generator, '_create_mockup') as mock_mockup:
            mock_mockup.return_value = {
                "success": True,
                "mockup_image": "/tmp/product_mockup.jpg",
                "device_model": "iphone_15_pro",
                "environment_style": "modern_office",
                "realism_score": 96.8
            }
            
            result = await generator.create_product_mockup(
                product_info=product_info,
                lighting="natural",
                perspective="three_quarter"
            )
            
            assert result["success"] is True
            assert result["device_model"] == "iphone_15_pro"
            assert result["realism_score"] == 96.8
    
    @pytest.mark.asyncio
    async def test_ai_model_comparison(self, generator, sample_prompt, image_config):
        """Test comparison across different AI models"""
        providers = [
            GenerationProvider.DALLE,
            GenerationProvider.MIDJOURNEY,
            GenerationProvider.STABLE_DIFFUSION
        ]
        
        with patch.object(generator, '_generate_with_ai') as mock_generation:
            def provider_generation(prompt, config, provider):
                return {
                    "success": True,
                    "image_path": f"/tmp/{provider.value}_result.jpg",
                    "provider": provider.value,
                    "generation_time": 10 + hash(provider.value) % 10,
                    "quality_score": 85 + hash(provider.value) % 15
                }
            
            mock_generation.side_effect = provider_generation
            
            results = await generator.compare_providers(
                prompt=sample_prompt,
                config=image_config,
                providers=providers,
                include_metrics=True
            )
            
            assert len(results) == 3
            for provider, result in results.items():
                assert result["success"] is True
                assert result["provider"] == provider
                assert "quality_score" in result
    
    @pytest.mark.asyncio
    async def test_image_variation_generation(self, generator):
        """Test generating variations of an existing image"""
        source_image = "/tmp/original_image.jpg"
        
        with patch.object(generator, '_generate_variations') as mock_variations:
            mock_variations.return_value = {
                "success": True,
                "variations": [
                    {"path": "/tmp/var_1.jpg", "similarity": 0.85, "variation_type": "color"},
                    {"path": "/tmp/var_2.jpg", "similarity": 0.78, "variation_type": "style"},
                    {"path": "/tmp/var_3.jpg", "similarity": 0.82, "variation_type": "composition"}
                ],
                "generation_time": 22.5
            }
            
            result = await generator.generate_variations(
                source_image=source_image,
                variation_count=3,
                variation_strength=0.7,
                maintain_subject=True
            )
            
            assert result["success"] is True
            assert len(result["variations"]) == 3
            assert result["variations"][0]["similarity"] == 0.85
    
    @pytest.mark.asyncio
    async def test_image_quality_enhancement(self, generator):
        """Test image quality enhancement and restoration"""
        damaged_image = "/tmp/low_quality_image.jpg"
        
        with patch.object(generator, '_enhance_quality') as mock_enhance:
            mock_enhance.return_value = {
                "success": True,
                "enhanced_image": "/tmp/enhanced_image.jpg",
                "improvements": {
                    "sharpness": 85.2,
                    "noise_reduction": 92.8,
                    "color_correction": 78.5,
                    "detail_enhancement": 88.9
                },
                "overall_improvement": 86.4
            }
            
            result = await generator.enhance_image_quality(
                image_path=damaged_image,
                enhancement_type="comprehensive",
                preserve_original_style=True
            )
            
            assert result["success"] is True
            assert result["overall_improvement"] == 86.4
            assert result["improvements"]["noise_reduction"] == 92.8
    
    @pytest.mark.asyncio
    async def test_copyright_safe_generation(self, generator, sample_prompt, image_config):
        """Test copyright-safe image generation"""
        with patch.object(generator, '_check_copyright_safety') as mock_safety:
            mock_safety.return_value = {
                "safe_to_use": True,
                "similarity_to_existing": 0.15,
                "copyright_risk": "low",
                "modifications_suggested": []
            }
            
            with patch.object(generator, '_generate_with_ai') as mock_generation:
                mock_generation.return_value = {
                    "success": True,
                    "image_path": "/tmp/safe_image.jpg",
                    "copyright_checked": True,
                    "commercial_usage": "approved"
                }
                
                result = await generator.generate_copyright_safe(
                    prompt=sample_prompt,
                    config=image_config,
                    check_similarity=True,
                    commercial_use=True
                )
                
                assert result["success"] is True
                assert result["copyright_checked"] is True
                assert result["commercial_usage"] == "approved"
    
    @pytest.mark.asyncio
    async def test_image_format_conversion(self, generator):
        """Test image format conversion and optimization"""
        source_image = "/tmp/source.png"
        target_formats = [ImageFormat.JPEG, ImageFormat.WEBP, ImageFormat.AVIF]
        
        with patch.object(generator, '_convert_format') as mock_convert:
            def format_conversion(image_path, target_format, quality):
                return {
                    "success": True,
                    "converted_image": f"/tmp/converted.{target_format.value}",
                    "original_size": 2048000,
                    "new_size": 1024000 if target_format == ImageFormat.WEBP else 1536000,
                    "compression_ratio": 0.5 if target_format == ImageFormat.WEBP else 0.75,
                    "format": target_format.value
                }
            
            mock_convert.side_effect = format_conversion
            
            results = await generator.convert_to_formats(
                image_path=source_image,
                target_formats=target_formats,
                optimization_level="high"
            )
            
            assert len(results) == 3
            for format_name, result in results.items():
                assert result["success"] is True
                assert result["format"] == format_name
    
    @pytest.mark.asyncio
    async def test_image_metadata_management(self, generator):
        """Test image metadata handling"""
        image_path = "/tmp/metadata_image.jpg"
        
        metadata = {
            "creator": "Fahed Mlaiel",
            "copyright": "© 2025 Fahed Mlaiel",
            "description": "AI-generated technology illustration",
            "keywords": ["AI", "technology", "illustration"],
            "creation_date": datetime.now().isoformat()
        }
        
        with patch.object(generator, '_manage_metadata') as mock_metadata:
            mock_metadata.return_value = {
                "success": True,
                "metadata_embedded": True,
                "metadata_fields": len(metadata),
                "exif_data_preserved": True
            }
            
            result = await generator.embed_metadata(
                image_path=image_path,
                metadata=metadata,
                preserve_existing=True
            )
            
            assert result["success"] is True
            assert result["metadata_embedded"] is True
            assert result["metadata_fields"] == len(metadata)
    
    @pytest.mark.asyncio
    async def test_real_time_image_streaming(self, generator):
        """Test real-time image generation streaming"""
        prompt = "Progressive AI artwork creation"
        
        with patch.object(generator, '_stream_generation') as mock_stream:
            async def mock_stream_generator():
                stages = ["sketch", "base_colors", "details", "final"]
                for i, stage in enumerate(stages):
                    yield {
                        "stage": stage,
                        "progress": (i + 1) / len(stages),
                        "preview_image": f"/tmp/preview_{stage}.jpg",
                        "is_final": i == len(stages) - 1
                    }
            
            mock_stream.return_value = mock_stream_generator()
            
            stages = []
            async for stage in generator.stream_generation(
                prompt=prompt,
                show_progress=True
            ):
                stages.append(stage)
            
            assert len(stages) == 4
            assert stages[-1]["is_final"] is True
            assert stages[-1]["progress"] == 1.0
    
    @pytest.mark.asyncio
    async def test_error_handling_and_fallbacks(self, generator, sample_prompt, image_config):
        """Test error handling and provider fallbacks"""
        with patch.object(generator, '_generate_with_ai') as mock_generation:
            # First provider fails, second succeeds
            mock_generation.side_effect = [
                Exception("Primary provider failed"),
                {
                    "success": True,
                    "image_path": "/tmp/fallback_image.jpg",
                    "provider": "fallback_provider"
                }
            ]
            
            result = await generator.generate_image(
                prompt=sample_prompt,
                config=image_config,
                enable_fallback=True,
                fallback_providers=[GenerationProvider.STABLE_DIFFUSION]
            )
            
            assert result["success"] is True
            assert result["provider"] == "fallback_provider"
    
    @pytest.mark.asyncio
    async def test_performance_optimization(self, generator, image_config):
        """Test performance optimization features"""
        prompts = ["Fast generation test"] * 10
        
        with patch.object(generator, '_generate_with_ai') as mock_generation:
            mock_generation.return_value = {
                "success": True,
                "image_path": "/tmp/optimized_image.jpg",
                "generation_time": 8.5,
                "memory_usage": 256.7,
                "gpu_utilization": 85.2
            }
            
            start_time = datetime.now()
            
            results = await generator.generate_batch(
                prompts=prompts,
                config=image_config,
                parallel_processing=True,
                max_concurrent=4,
                optimize_performance=True
            )
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            assert len(results) == 10
            assert total_time < 30  # Should be faster with optimization


class TestImageConfig:
    """Test suite for ImageConfig model"""
    
    def test_image_config_creation(self):
        """Test image configuration creation"""
        config = ImageConfig(
            width=1024,
            height=768,
            quality=ImageQuality.HIGH,
            format=ImageFormat.PNG,
            style=ImageStyle.ARTISTIC,
            art_style=ArtStyle.IMPRESSIONIST,
            seed=123
        )
        
        assert config.width == 1024
        assert config.height == 768
        assert config.quality == ImageQuality.HIGH
        assert config.format == ImageFormat.PNG
        assert config.style == ImageStyle.ARTISTIC
        assert config.seed == 123
    
    def test_image_config_validation(self):
        """Test image configuration validation"""
        # Test invalid dimensions
        with pytest.raises(Exception):  # Adjust based on actual validation
            ImageConfig(
                width=0,  # Invalid
                height=1024,
                quality=ImageQuality.HIGH,
                format=ImageFormat.PNG
            )


class TestImageEnums:
    """Test suite for image-related enums"""
    
    def test_image_format_enum(self):
        """Test ImageFormat enum values"""
        assert ImageFormat.PNG.value == "png"
        assert ImageFormat.JPEG.value == "jpeg"
        assert ImageFormat.WEBP.value == "webp"
        assert ImageFormat.SVG.value == "svg"
    
    def test_image_quality_enum(self):
        """Test ImageQuality enum values"""
        assert ImageQuality.LOW.value == "low"
        assert ImageQuality.MEDIUM.value == "medium"
        assert ImageQuality.HIGH.value == "high"
        assert ImageQuality.ULTRA.value == "ultra"
    
    def test_image_style_enum(self):
        """Test ImageStyle enum values"""
        assert ImageStyle.REALISTIC.value == "realistic"
        assert ImageStyle.ARTISTIC.value == "artistic"
        assert ImageStyle.CARTOON.value == "cartoon"
        assert ImageStyle.ABSTRACT.value == "abstract"


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
